from __future__ import annotations

import base64
from dataclasses import replace
from datetime import date, timedelta
import hashlib
import hmac
from pathlib import Path
import ssl
import tempfile
import time
import unittest
from unittest.mock import patch

from stock_strategy_lab.calendar import trading_dates
from stock_strategy_lab.credentials import LocalTokenStore
from stock_strategy_lab.models import OptionQuote, OptionRule, StockBar
from stock_strategy_lab.providers import ApiResponse, HistoryAccessError, MarketDataProvider, ProviderError
from stock_strategy_lab.shared_auth import SharedSessionAuth, valid_shared_session_token
from stock_strategy_lab.storage import AppStore, MarketVault
from stock_strategy_lab.tiingo import TiingoProvider


def session_token(username: str, secret: str, expires: int | None = None) -> str:
    payload = f"{username}|{expires or int(time.time()) + 3600}|test-nonce"
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}|{signature}".encode()).decode().rstrip("=")


class ProviderAndAuthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        path = Path(self.temporary.name)
        self.vault = MarketVault(path)
        self.store = AppStore(path)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_valid_shared_session_and_cookie(self) -> None:
        token = session_token("admin", "secret")
        self.assertTrue(valid_shared_session_token(token, "admin", "secret"))
        self.assertFalse(valid_shared_session_token(token, "other", "secret"))
        expired = session_token("admin", "secret", int(time.time()) - 5)
        self.assertFalse(valid_shared_session_token(expired, "admin", "secret"))
        auth = SharedSessionAuth("admin", "secret", "dem_session", "https://dem.example/login", "https://strategy.example")
        self.assertTrue(auth.valid_cookie_header(f"other=x; dem_session={token}"))
        self.assertIn("next=https%3A%2F%2Fstrategy.example%2Flibrary", auth.login_redirect("/library"))

    def test_local_token_store_is_owner_only_and_deletable(self) -> None:
        store = LocalTokenStore(Path(self.temporary.name))
        store.save("test-token-123")
        self.assertEqual(store.load(), "test-token-123")
        restarted_store = LocalTokenStore(Path(self.temporary.name))
        self.assertEqual(restarted_store.load(), "test-token-123")
        self.assertEqual(store.path.stat().st_mode & 0o777, 0o600)
        with self.assertRaisesRegex(ValueError, "whitespace"):
            store.save("bad token")
        store.delete()
        self.assertFalse(store.exists)
        self.assertEqual(store.load(), "")

    def test_cached_stock_bars_need_no_token_or_provider_call(self) -> None:
        start, end = "2025-01-02", "2025-01-10"
        bars = [StockBar(day.isoformat(), 100, 101, 99, 100, 100, 1000) for day in trading_dates(date.fromisoformat(start), date.fromisoformat(end))]
        self.vault.save_stock_bars("marketdata", "SPY", bars)
        provider = MarketDataProvider(self.vault, self.store, token="")
        self.assertEqual(len(provider.stock_bars("SPY", start, end)), len(bars))

    def test_replacing_token_clears_request_caches_and_validation(self) -> None:
        provider = MarketDataProvider(self.vault, self.store, token="old-token")
        provider._chain_cache[("SPY", "2025-01-02", "rule")] = []
        provider._series_cache[("contract", "2025-01-02", "2025-02-01")] = []
        provider.token_validated = True
        provider.set_token("new-token")
        self.assertEqual(provider.token, "new-token")
        self.assertFalse(provider.token_validated)
        self.assertFalse(provider._chain_cache)
        self.assertFalse(provider._series_cache)

    def test_provider_uses_a_verified_certificate_context(self) -> None:
        class FakeResponse:
            status = 200
            headers: dict[str, str] = {}

            def __enter__(self):  # type: ignore[no-untyped-def]
                return self

            def __exit__(self, *args):  # type: ignore[no-untyped-def]
                return False

            @staticmethod
            def read() -> bytes:
                return b'{"s":"ok"}'

        provider = MarketDataProvider(self.vault, self.store, token="token")
        with patch("stock_strategy_lab.providers.urlopen", return_value=FakeResponse()) as mocked:
            provider._request("/test/", {})
        context = mocked.call_args.kwargs["context"]
        self.assertIs(context, provider.ssl_context)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)
        self.assertTrue(context.get_ca_certs())

    def test_tiingo_rows_are_transient_and_preserve_corporate_actions(self) -> None:
        class FakeResponse:
            def __enter__(self):  # type: ignore[no-untyped-def]
                return self

            def __exit__(self, *args):  # type: ignore[no-untyped-def]
                return False

            @staticmethod
            def read() -> bytes:
                return (
                    b'[{"date":"2025-01-02T00:00:00Z","open":100,"high":101,"low":99,'
                    b'"close":100,"adjClose":50,"volume":1000,"divCash":0.5,"splitFactor":1},'
                    b'{"date":"2025-01-03T00:00:00Z","open":50,"high":51,"low":49,'
                    b'"close":50,"adjClose":50,"volume":2000,"divCash":0,"splitFactor":2}]'
                )

        provider = TiingoProvider(self.vault, self.store, token="token")
        with patch("stock_strategy_lab.tiingo.urlopen", return_value=FakeResponse()):
            bars = provider.stock_bars("SPY", "2025-01-02", "2025-01-03")
        self.assertEqual(bars[0].dividend_cash, 0.5)
        self.assertEqual(bars[1].split_factor, 2)
        self.assertTrue(bars[1].split_detected)
        self.assertEqual(self.vault.stock_bars("tiingo", "SPY", "2025-01-02", "2025-01-03"), [])
        provider.clear_transient()
        self.assertFalse(provider._transient_bars)

    def test_missing_stock_session_is_detected(self) -> None:
        start, end = "2025-01-02", "2025-01-10"
        sessions = trading_dates(date.fromisoformat(start), date.fromisoformat(end))
        bars = [StockBar(day.isoformat(), 100, 101, 99, 100, 100, 1000) for day in sessions if day != sessions[2]]
        self.assertFalse(MarketDataProvider._covers(bars, start, end))
        self.assertEqual(MarketDataProvider._missing_stock_sessions(bars, start, end), [sessions[2].isoformat()])

    def test_old_missing_option_history_is_explicitly_permanent(self) -> None:
        provider = MarketDataProvider(self.vault, self.store, token="")
        old = (date.today() - timedelta(days=500)).isoformat()
        with self.assertRaisesRegex(ProviderError, "permanently unavailable"):
            provider.option_chain("SPY", old, OptionRule("call"))

    def test_five_year_access_requires_an_old_date_probe_not_a_large_quota(self) -> None:
        provider = MarketDataProvider(self.vault, self.store, token="token")
        self.store.record_quota("/test", 1, 9_999, 10_000, None)
        self.assertEqual(provider.history_years, 1)
        with patch.object(provider, "_request", return_value=ApiResponse({"s": "ok", "t": [1], "c": [100]}, {}, 200)):
            result = provider.verify_five_year_access()
        self.assertTrue(result["verified"])
        self.assertEqual(provider.history_years, 5)
        self.assertEqual(provider.history_window_start(date.today()).year, date.today().year - 5)

        provider.set_token("different-token")
        self.assertEqual(provider.history_years, 1)

    def test_five_year_probe_records_one_year_plan_rejection(self) -> None:
        provider = MarketDataProvider(self.vault, self.store, token="token")
        with patch.object(provider, "_request", side_effect=HistoryAccessError("upgrade required")):
            result = provider.verify_five_year_access()
        self.assertFalse(result["verified"])
        self.assertEqual(result["status"], "one_year_only")
        self.assertEqual(provider.history_years, 1)

    def test_rate_limit_headers_are_recorded_exactly(self) -> None:
        provider = MarketDataProvider(self.vault, self.store, token="token")
        provider._record_quota(
            "/options/chain/SPY/",
            {
                "x-api-ratelimit-consumed": "7",
                "x-api-ratelimit-remaining": "42",
                "x-api-ratelimit-limit": "100",
                "x-api-ratelimit-reset": "123456",
            },
        )
        status = self.store.quota_status()
        self.assertEqual(status["consumed"], 7)
        self.assertEqual(status["remaining"], 42)
        self.assertEqual(status["limit"], 100)
        self.assertEqual(status["resetAt"], 123456)

    def test_sparse_option_series_fetch_is_cached_across_provider_instances(self) -> None:
        option_symbol = "SPY270115C00100000"
        payload = {
            "s": "ok",
            "optionSymbol": [option_symbol],
            "updated": ["2026-01-02 16:00:00 -05:00"],
            "expiration": ["2027-01-15 16:00:00 -05:00"],
            "side": ["call"],
            "strike": [100],
            "bid": [2.0],
            "ask": [2.2],
            "openInterest": [1000],
            "underlyingPrice": [100],
        }

        class StubProvider(MarketDataProvider):
            calls = 0

            def _request(self, path, params):  # type: ignore[no-untyped-def]
                StubProvider.calls += 1
                return ApiResponse(payload, {}, 200)

        first = StubProvider(self.vault, self.store, token="token")
        fetched = first.option_quote_series(option_symbol, "2026-01-02", "2026-02-27")
        self.assertEqual(len(fetched), 1)
        second = StubProvider(self.vault, self.store, token="token")
        cached = second.option_quote_series(option_symbol, "2026-01-02", "2026-02-27")
        self.assertEqual(len(cached), 1)
        self.assertEqual(StubProvider.calls, 1)

    def test_scalar_contract_symbol_expands_across_daily_quote_arrays(self) -> None:
        option_symbol = "QQQ270617C00620000"
        payload = {
            "s": "ok",
            "optionSymbol": option_symbol,
            "updated": [
                "2026-01-16 16:00:00 -05:00",
                "2026-01-20 16:00:00 -05:00",
                "2026-01-21 16:00:00 -05:00",
            ],
            "expiration": "2027-06-17 16:00:00 -04:00",
            "side": "call",
            "strike": 620,
            "bid": [79.09, 74.5, 76.25],
            "ask": [83.5, 78.0, 79.1],
            "last": [81.37, 76.0, 78.0],
            "openInterest": [1000, 1010, 1020],
            "underlyingPrice": [619.8, 610.0, 614.0],
        }
        provider = MarketDataProvider(self.vault, self.store, token="token")
        parsed = provider._parse_option_quotes(payload, "QQQ", "2026-01-16")
        self.assertEqual(len(parsed), 3)
        self.assertEqual([item.market_date for item in parsed], ["2026-01-16", "2026-01-20", "2026-01-21"])
        self.assertTrue(all(item.option_symbol == option_symbol for item in parsed))
        self.assertEqual([item.ask for item in parsed], [83.5, 78.0, 79.1])

    def test_token_enabled_run_repairs_a_sparse_completed_series_manifest(self) -> None:
        option_symbol = "SPY250221C00100000"
        self.vault.save_option_quotes(
            "marketdata",
            [
                OptionQuote(
                    market_date="2025-01-02",
                    option_symbol=option_symbol,
                    underlying="SPY",
                    expiration="2025-02-21",
                    side="call",
                    strike=100,
                    bid=2,
                    ask=2.2,
                    last=2.1,
                    delta=None,
                    gamma=None,
                    theta=None,
                    vega=None,
                    iv=None,
                    open_interest=1000,
                    volume=100,
                    underlying_price=100,
                    is_monthly=True,
                    is_nonstandard=False,
                )
            ],
        )
        self.store.mark_provider_fetch(
            f"option-series:{option_symbol}",
            "marketdata",
            "option-series",
            "2025-01-02",
            "2025-02-21",
        )
        payload = {
            "s": "ok",
            "optionSymbol": option_symbol,
            "updated": [
                "2025-01-02 16:00:00 -05:00",
                "2025-01-20 16:00:00 -05:00",
                "2025-02-20 16:00:00 -05:00",
            ],
            "expiration": "2025-02-21 16:00:00 -05:00",
            "side": "call",
            "strike": 100,
            "bid": [2, 3, 4],
            "ask": [2.2, 3.2, 4.2],
            "last": [2.1, 3.1, 4.1],
            "openInterest": [1000, 1100, 1200],
            "underlyingPrice": [100, 101, 102],
        }

        class RepairProvider(MarketDataProvider):
            calls = 0

            def _request(self, path, params):  # type: ignore[no-untyped-def]
                RepairProvider.calls += 1
                return ApiResponse(payload, {}, 200)

        provider = RepairProvider(self.vault, self.store, token="token")
        repaired = provider.option_quote_series(option_symbol, "2025-01-02", "2025-02-21")
        self.assertEqual(RepairProvider.calls, 1)
        self.assertEqual(len(repaired), 3)
        self.assertEqual(repaired[-1].market_date, "2025-02-20")

    def test_monthly_filtered_chain_trusts_holiday_adjusted_provider_expiration(self) -> None:
        option_symbol = "SPY270617C00700000"
        payload = {
            "s": "ok",
            "optionSymbol": [option_symbol],
            "updated": ["2026-06-18 16:00:00 -04:00"],
            "expiration": ["2027-06-17 16:00:00 -04:00"],
            "side": ["call"],
            "strike": [700],
            "bid": [40],
            "ask": [41],
            "openInterest": [1000],
            "underlyingPrice": [700],
        }

        class StubProvider(MarketDataProvider):
            calls = 0

            def _request(self, path, params):  # type: ignore[no-untyped-def]
                StubProvider.calls += 1
                self.assert_monthly = params.get("monthly")
                return ApiResponse(payload, {}, 200)

        rule = OptionRule("call", target_dte=365, roll_dte=180, expiration_type="monthly")
        first = StubProvider(self.vault, self.store, token="token")
        fetched = first.option_chain("SPY", "2026-06-18", rule)
        self.assertEqual(len(fetched), 1)
        self.assertTrue(fetched[0].is_monthly)
        self.assertEqual(first.assert_monthly, "true")

        # A later contract-series download for the same market date must not
        # become part of this cached chain on the next run.
        self.vault.save_option_quotes(
            "marketdata",
            [
                replace(
                    fetched[0],
                    option_symbol="SPY270716C00700000",
                    expiration="2027-07-16",
                    strike=710,
                )
            ],
        )
        restarted = StubProvider(self.vault, self.store, token="")
        cached = restarted.option_chain("SPY", "2026-06-18", rule)
        self.assertEqual(len(cached), 1)
        self.assertEqual(cached[0].option_symbol, option_symbol)
        self.assertTrue(cached[0].is_monthly)
        self.assertEqual(StubProvider.calls, 1)

    def test_sparse_contract_history_is_never_treated_as_a_complete_chain(self) -> None:
        # Fixed so the target expiration remains near 365 DTE as the wall clock advances.
        market_date = "2026-01-15"
        sparse = OptionQuote(
            market_date=market_date,
            option_symbol="SPY270115C00700000",
            underlying="SPY",
            expiration="2027-01-15",
            side="call",
            strike=700,
            bid=20,
            ask=21,
            last=20.5,
            delta=0.5,
            gamma=None,
            theta=None,
            vega=None,
            iv=None,
            open_interest=1000,
            volume=100,
            underlying_price=700,
            is_monthly=True,
            is_nonstandard=False,
        )
        self.vault.save_option_quotes("marketdata", [sparse])
        full_symbol = "SPY270115C00690000"
        payload = {
            "s": "ok",
            "optionSymbol": [full_symbol],
            "updated": [f"{market_date} 16:00:00 -04:00"],
            "expiration": ["2027-01-15 16:00:00 -05:00"],
            "side": ["call"],
            "strike": [690],
            "bid": [25],
            "ask": [26],
            "openInterest": [2000],
            "underlyingPrice": [700],
        }

        class StubProvider(MarketDataProvider):
            calls = 0

            def _request(self, path, params):  # type: ignore[no-untyped-def]
                StubProvider.calls += 1
                return ApiResponse(payload, {}, 200)

        provider = StubProvider(self.vault, self.store, token="token")
        chain = provider.option_chain(
            "SPY",
            market_date,
            OptionRule(
                "call",
                target_dte=365,
                roll_dte=180,
                expiration_type="monthly",
                min_open_interest=0,
                max_spread_pct=1,
            ),
        )
        self.assertEqual(StubProvider.calls, 1)
        self.assertEqual([item.option_symbol for item in chain], [full_symbol])

    def test_split_detection_from_adjustment_ratio_change(self) -> None:
        provider = MarketDataProvider(self.vault, self.store, token="token")
        stamps = [int(time.mktime(time.strptime(day, "%Y-%m-%d"))) for day in ["2025-01-02", "2025-01-03", "2025-01-06"]]
        raw = {"t": stamps, "o": [100, 50, 51], "h": [101, 51, 52], "l": [99, 49, 50], "c": [100, 50, 51], "v": [1, 1, 1]}
        adjusted = {"t": stamps, "c": [50, 50, 51]}
        bars = provider._parse_stock_bars(raw, adjusted)
        self.assertTrue(any(item.split_detected for item in bars))


if __name__ == "__main__":
    unittest.main()
