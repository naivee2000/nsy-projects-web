from __future__ import annotations

from dataclasses import replace
from datetime import date
from pathlib import Path
import tempfile
import unittest

from stock_strategy_lab.calendar import is_us_trading_day, trading_dates
from stock_strategy_lab.collector import VaultCollector
from stock_strategy_lab.models import OptionQuote, StockBar
from stock_strategy_lab.providers import CreditLimitError
from stock_strategy_lab.storage import AppStore, MarketVault


def quote(market_date: str, symbol: str = "SPY250221C00100000", expiration: str = "2025-02-21") -> OptionQuote:
    return OptionQuote(
        market_date=market_date,
        option_symbol=symbol,
        underlying="SPY",
        expiration=expiration,
        side="call",
        strike=100,
        bid=2.0,
        ask=2.2,
        last=2.1,
        delta=0.5,
        open_interest=1000,
        volume=100,
        underlying_price=100,
        is_monthly=True,
    )


class FakeCollectorProvider:
    available = True
    name = "marketdata"
    history_years = 5

    def __init__(self, vault: MarketVault, fail_after: int | None = None):
        self.vault = vault
        self.captured: list[tuple[str, str, str]] = []
        self.targeted: list[tuple[str, str, str, int, int]] = []
        self.fail_after = fail_after

    def stock_bars(self, symbol: str, start: str, end: str):
        sessions = ["2025-01-02", "2025-01-03", "2025-01-06", "2025-01-07"]
        bars = [StockBar(day, 100, 101, 99, 100, 100, 1000) for day in sessions]
        self.vault.save_stock_bars("marketdata", symbol, bars)
        return bars

    def option_expirations(self, symbol: str, market_date: str):
        return ["2025-02-21"]

    def capture_expiration(self, symbol: str, market_date: str, expiration: str):
        if self.fail_after is not None and len(self.captured) >= self.fail_after:
            raise CreditLimitError("429 test limit")
        self.captured.append((symbol, market_date, expiration))
        item = quote(market_date, f"SPY{market_date.replace('-', '')}C", expiration)
        self.vault.save_option_quotes("marketdata", [item])
        return [item]

    def capture_target_chain(self, symbol: str, market_date: str, side: str, target_dte: int, strike_limit: int):
        self.targeted.append((symbol, market_date, side, target_dte, strike_limit))
        expiration = "2026-06-19" if side == "call" else "2025-02-21"
        item = replace(quote(market_date, f"{symbol}{market_date.replace('-', '')}{side[0].upper()}", expiration), underlying=symbol, side=side)
        self.vault.save_option_quotes("marketdata", [item])
        return [item]


class StorageAndCollectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary.name)
        self.vault = MarketVault(self.path)
        self.store = AppStore(self.path)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_vault_deduplicates_and_keeps_old_history_queryable(self) -> None:
        bars = [
            StockBar("2024-01-02", 99, 101, 98, 100, 100, 1000),
            StockBar("2024-01-03", 100, 102, 99, 101, 101, 1100),
        ]
        self.vault.save_stock_bars("marketdata", "SPY", bars)
        self.vault.save_stock_bars("marketdata", "SPY", bars)
        self.vault.save_option_quotes("marketdata", [quote("2024-01-02")])
        self.vault.save_option_quotes("marketdata", [quote("2024-01-02")])
        self.assertEqual(len(self.vault.stock_bars("marketdata", "SPY", "2024-01-01", "2024-01-31")), 2)
        self.assertEqual(len(self.vault.option_chain("marketdata", "SPY", "2024-01-02")), 1)
        coverage = self.vault.coverage("marketdata", "SPY")
        self.assertEqual(coverage["stockDays"], 2)
        self.assertEqual(coverage["optionContracts"], 1)

    def test_store_persists_favorites_strategies_runs_and_quota(self) -> None:
        favorite = self.store.save_favorite("spy", "balanced", True)
        self.assertEqual(favorite["symbol"], "SPY")
        self.assertEqual(self.store.estimated_collection_credits(), 7)
        strategy_id = self.store.save_strategy("Test", {"ticker": "SPY"})
        self.assertEqual(self.store.list_strategies()[0]["id"], strategy_id)
        self.store.save_run("run1", "Result", "SPY", "complete", {"metrics": {"endingValue": 101000}})
        self.assertEqual(self.store.get_run("run1")["metrics"]["endingValue"], 101000)
        self.store.record_quota("/test", 4, 81, 100, 12345)
        self.assertEqual(self.store.quota_status()["remaining"], 81)

    def test_free_provider_runs_persist_summaries_not_daily_price_rows(self) -> None:
        self.store.save_run(
            "free-run",
            "Free result",
            "SPY",
            "complete",
            {
                "provider": "free-modeled",
                "metrics": {"strategy": {"endingValue": 110_000}},
                "timeline": [{"date": "2025-01-02", "strategy": 100_000}],
            },
        )
        saved = self.store.get_run("free-run")
        self.assertNotIn("timeline", saved)
        self.assertTrue(saved["summaryOnly"])
        self.assertIn("not retained", saved["summaryNotice"])

    def test_jobs_persist_and_interrupted_work_becomes_an_explicit_failure(self) -> None:
        self.store.save_job(
            {
                "id": "job1",
                "kind": "backtest",
                "status": "running",
                "stage": "Pulling required market data and running the test",
                "provider": "marketdata",
                "mode": "single",
                "createdAt": "2026-07-17T07:00:00+00:00",
                "startedAt": "2026-07-17T07:00:01+00:00",
            }
        )
        reopened = AppStore(self.path)
        self.assertEqual(reopened.get_job("job1")["status"], "running")
        self.assertEqual(reopened.fail_incomplete_jobs(), 1)
        recovered = reopened.get_job("job1")
        self.assertEqual(recovered["status"], "failed")
        self.assertIn("stopped before", recovered["error"].lower())

    def test_collector_orders_newest_then_oldest_and_resumes_without_duplicates(self) -> None:
        self.store.save_favorite("SPY", "balanced", True)
        provider = FakeCollectorProvider(self.vault)
        collector = VaultCollector(provider, self.vault, self.store)  # type: ignore[arg-type]
        collector.max_backfill_sessions = 2
        first = collector.sync()
        self.assertEqual(first["status"], "complete")
        self.assertEqual([item[1] for item in provider.captured], ["2025-01-07", "2025-01-02", "2025-01-03"])
        second = collector.sync()
        self.assertEqual(second["status"], "complete")
        self.assertEqual([item[1] for item in provider.captured], ["2025-01-07", "2025-01-02", "2025-01-03", "2025-01-06"])
        self.assertEqual(len(self.store.collection_dates("SPY", "balanced")), 4)

    def test_collector_stops_at_reserved_credit_boundary(self) -> None:
        self.store.save_favorite("SPY", "balanced", True)
        self.store.record_quota("/test", 1, 30, 100, None)
        provider = FakeCollectorProvider(self.vault)
        collector = VaultCollector(provider, self.vault, self.store)  # type: ignore[arg-type]
        result = collector.sync()
        self.assertEqual(result["sessionsCompleted"], 0)
        self.assertFalse(provider.captured)

    def test_partial_429_is_recorded_and_resumable(self) -> None:
        self.store.save_favorite("SPY", "balanced", True)
        provider = FakeCollectorProvider(self.vault, fail_after=1)
        collector = VaultCollector(provider, self.vault, self.store)  # type: ignore[arg-type]
        collector.max_backfill_sessions = 1
        result = collector.sync()
        self.assertEqual(result["status"], "partial")
        self.assertTrue(any("429" in error for error in result["errors"]))

    def test_historical_backfill_estimates_saves_and_skips_duplicates(self) -> None:
        provider = FakeCollectorProvider(self.vault)
        collector = VaultCollector(provider, self.vault, self.store)  # type: ignore[arg-type]
        estimate = collector.estimate_backfill("SPY", "2025-01-02", "2025-01-07", "used")
        self.assertEqual(estimate["tradingSessions"], 4)
        self.assertEqual(estimate["remainingSessions"], 4)
        self.assertEqual(estimate["estimatedCredits"], 14)

        progress: list[tuple[int, int, str]] = []
        result = collector.backfill(
            "SPY",
            "2025-01-02",
            "2025-01-07",
            "used",
            progress=lambda completed, total, market_date: progress.append((completed, total, market_date)),
        )
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["remainingSessions"], 0)
        self.assertEqual(len(provider.captured), 4)
        self.assertTrue(progress)

        repeated = collector.backfill("SPY", "2025-01-02", "2025-01-07", "used")
        self.assertEqual(repeated["status"], "complete")
        self.assertEqual(len(provider.captured), 4)
        self.assertEqual(collector.estimate_backfill("SPY", "2025-01-02", "2025-01-07", "used")["estimatedCredits"], 0)

    def test_historical_backfill_pauses_at_reserve_and_can_resume(self) -> None:
        provider = FakeCollectorProvider(self.vault)
        collector = VaultCollector(provider, self.vault, self.store)  # type: ignore[arg-type]
        self.store.record_quota("/test", 1, 30, 10_000, None)
        paused = collector.backfill("SPY", "2025-01-02", "2025-01-07", "used")
        self.assertEqual(paused["status"], "partial")
        self.assertEqual(paused["remainingSessions"], 4)
        self.assertFalse(provider.captured)

        self.store.record_quota("/test", 1, 9_999, 10_000, None)
        resumed = collector.backfill("SPY", "2025-01-02", "2025-01-07", "used")
        self.assertEqual(resumed["status"], "complete")
        self.assertEqual(resumed["remainingSessions"], 0)

    def test_optimized_spy_qqq_estimate_fits_under_credit_cap(self) -> None:
        provider = FakeCollectorProvider(self.vault)
        collector = VaultCollector(provider, self.vault, self.store)  # type: ignore[arg-type]
        estimate = collector.estimate_leaps_protection("2025-01-02", "2025-01-07", 540, 45, 40)
        self.assertEqual(estimate["totalSymbolDays"], 8)
        self.assertEqual(estimate["estimatedDownloadCredits"], 20)
        self.assertEqual(estimate["projectedCreditBudget"], 1020)
        self.assertTrue(estimate["fitsWithinCreditCap"])
        self.assertTrue(estimate["canStart"])

    def test_optimized_spy_qqq_download_is_targeted_and_resumable(self) -> None:
        provider = FakeCollectorProvider(self.vault)
        collector = VaultCollector(provider, self.vault, self.store)  # type: ignore[arg-type]
        result = collector.backfill_leaps_protection("2025-01-02", "2025-01-07", 540, 45, 40)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["remainingSymbolDays"], 0)
        self.assertEqual(len(provider.targeted), 16)
        self.assertEqual({item[0] for item in provider.targeted}, {"SPY", "QQQ"})
        self.assertEqual({(item[2], item[3], item[4]) for item in provider.targeted}, {("call", 540, 40), ("put", 45, 40)})

        repeated = collector.backfill_leaps_protection("2025-01-02", "2025-01-07", 540, 45, 40)
        self.assertEqual(repeated["status"], "complete")
        self.assertEqual(len(provider.targeted), 16)

    def test_capture_profiles_and_market_holidays(self) -> None:
        expirations = ["2025-01-10", "2025-01-17", "2025-02-21", "2025-08-15"]
        self.assertEqual(VaultCollector._choose_expirations(expirations, "2025-01-02", "balanced"), ["2025-01-17", "2025-02-21"])
        self.assertEqual(VaultCollector._choose_expirations(expirations, "2025-01-02", "used"), ["2025-02-21"])
        self.assertFalse(is_us_trading_day(date(2025, 1, 20)))
        self.assertFalse(is_us_trading_day(date(2025, 7, 4)))
        self.assertNotIn(date(2025, 11, 27), trading_dates(date(2025, 11, 24), date(2025, 11, 28)))

    def test_delete_market_data_preserves_saved_work(self) -> None:
        self.vault.save_stock_bars("marketdata", "SPY", [StockBar("2025-01-02", 100, 100, 100, 100, 100)])
        self.store.save_strategy("Keep", {"ticker": "SPY"})
        self.store.mark_collection("SPY", "2025-01-02", "balanced", "complete", 1, 1)
        self.vault.purge("marketdata")
        self.store.purge_marketdata_metadata()
        self.assertEqual(self.vault.coverage("marketdata", "SPY")["stockDays"], 0)
        self.assertEqual(len(self.store.list_strategies()), 1)
        self.assertFalse(self.store.collection_dates("SPY", "balanced"))


if __name__ == "__main__":
    unittest.main()
