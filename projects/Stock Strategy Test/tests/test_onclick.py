from __future__ import annotations

import unittest

from stock_strategy_lab.models import OptionQuote, OptionRule
from stock_strategy_lab.onclick import OnclickBacktestProvider
from stock_strategy_lab.providers import FixtureProvider
from stock_strategy_lab.unified import InstrumentHolding


class FakeOnclickProvider(OnclickBacktestProvider):
    last_payload = None

    def availability(self, symbol: str) -> list[str]:
        return [
            "2025-01-02",
            "2025-01-03",
            "2025-01-06",
            "2025-01-07",
            "2025-01-08",
            "2025-01-09",
            "2025-01-10",
        ]

    def _request_json(self, method, url, payload=None):  # type: ignore[no-untyped-def]
        if method != "POST":
            return self.availability("SPY")
        self.last_payload = payload
        scale = float(payload["portfolio_start"]) / 100_000
        return [
            {
                "date": market_date,
                "cash": 20_000 * scale,
                "stock_value": 0,
                "leg1_value": (49_000 + index * 180) * scale,
                "leg1_mtm": (49_000 + index * 180) * scale,
                "leg1_open_transact": "10.0" if index == 0 else "",
                "total_fees": 0.4 * scale,
                "total_value": (99_000 + index * 300) * scale,
                "error": "",
            }
            for index, market_date in enumerate(self.availability("SPY"))
        ]


class ExperimentalOnclickTests(unittest.TestCase):
    @staticmethod
    def _strict_rows(rows):  # type: ignore[no-untyped-def]
        for row in rows:
            row["leg1_bid"] = 10.0
            row["leg1_ask"] = 10.1
            row["total_value"] = float(row["cash"]) + float(row["leg1_value"])
        return rows

    @staticmethod
    def _contract_rows(rows):  # type: ignore[no-untyped-def]
        rows = ExperimentalOnclickTests._strict_rows(rows)
        for row in rows:
            row["leg1_expiry"] = "2025-02-21"
            row["leg1_strike"] = 100.0
            row["leg1_type"] = "call"
            row["leg1_contracts"] = 100.0
            row["leg1_close_transact"] = ""
        return rows

    def test_single_option_and_same_ticker_stock_are_normalized(self) -> None:
        provider = FakeOnclickProvider(FixtureProvider())
        result = provider.run_portfolio_backtest(
            holdings=[
                InstrumentHolding("SPY", "stock", 30),
                InstrumentHolding("SPY", "call", 50),
            ],
            start="2025-01-02",
            end="2025-01-10",
            initial_capital=100_000,
            rebalance="none",
            call_rule=OptionRule("call", 365, 180),
            put_rule=OptionRule("put", 45, 21),
            cash_weight=20,
        )
        self.assertEqual(result["provider"], "onclick-experimental")
        self.assertEqual(result["optionCount"], 1)
        # 2025-01-09 was an official U.S. market closure.
        self.assertEqual(len(result["timeline"]), 6)
        self.assertEqual({item["symbol"] for item in result["breakdown"]}, {"SPY shares", "SPY long call", "Cash"})
        self.assertTrue(any("Experimental source" in item for item in result["warnings"]))
        self.assertTrue(any("not applied" in item for item in result["warnings"]))
        self.assertEqual(provider.last_payload["legs"][0]["rebalance_period"], 185)
        self.assertEqual(
            result["optionRules"]["SPY:call"],
            {
                "side": "call",
                "targetDte": 365,
                "rollDte": 180,
                "externalRebalanceDays": 185,
                "strikeMode": "atm",
                "strikeValue": 0.0,
                "externalPercentItm": 0.0,
            },
        )
        self.assertEqual(provider.last_payload["portfolio_start"], 50_000)
        self.assertEqual(provider.last_payload["percent_per_trade"], 1)
        self.assertIsNone(provider.last_payload["stock"])
        self.assertTrue(any("185-calendar-day replacement interval" in item for item in result["warnings"]))

    def test_long_call_roll_threshold_is_converted_to_elapsed_days(self) -> None:
        provider = FakeOnclickProvider(FixtureProvider())
        provider.run_portfolio_backtest(
            holdings=[InstrumentHolding("SPY", "call", 100)],
            start="2025-01-02",
            end="2025-01-10",
            initial_capital=100_000,
            rebalance="none",
            call_rule=OptionRule("call", 540, 180),
            put_rule=OptionRule("put", 45, 21),
        )
        self.assertEqual(provider.last_payload["legs"][0]["rebalance_period"], 360)

    def test_percentage_strike_rule_maps_to_provider_moneyness(self) -> None:
        provider = FakeOnclickProvider(FixtureProvider())
        result = provider.run_portfolio_backtest(
            holdings=[InstrumentHolding("SPY", "call", 100)],
            start="2025-01-02",
            end="2025-01-10",
            initial_capital=100_000,
            rebalance="none",
            call_rule=OptionRule(
                "call",
                540,
                180,
                strike_mode="percent_above",
                strike_value=10,
            ),
            put_rule=OptionRule("put", 45, 21),
        )
        self.assertEqual(provider.last_payload["legs"][0]["percent_itm"], -0.10)
        self.assertEqual(result["optionRules"]["SPY:call"]["strikeMode"], "percent_above")
        self.assertEqual(result["optionRules"]["SPY:call"]["strikeValue"], 10)

    def test_fixed_dollar_strikes_are_rejected_by_experimental_provider(self) -> None:
        provider = FakeOnclickProvider(FixtureProvider())
        with self.assertRaisesRegex(ValueError, "fixed-dollar"):
            provider.run_portfolio_backtest(
                holdings=[InstrumentHolding("SPY", "call", 100)],
                start="2025-01-02",
                end="2025-01-10",
                initial_capital=100_000,
                rebalance="none",
                call_rule=OptionRule(
                    "call",
                    540,
                    180,
                    strike_mode="dollar_above",
                    strike_value=25,
                ),
                put_rule=OptionRule("put", 45, 21),
            )

    def test_zero_roll_threshold_holds_until_expiration(self) -> None:
        provider = FakeOnclickProvider(FixtureProvider())
        result = provider.run_portfolio_backtest(
            holdings=[InstrumentHolding("SPY", "put", 100)],
            start="2025-01-02",
            end="2025-01-10",
            initial_capital=100_000,
            rebalance="none",
            call_rule=OptionRule("call", 540, 180),
            put_rule=OptionRule("put", 45, 0),
        )
        self.assertIsNone(provider.last_payload["legs"][0]["rebalance_period"])
        self.assertIsNone(result["optionRules"]["SPY:put"]["externalRebalanceDays"])
        self.assertTrue(any("holds each option until expiration" in item for item in result["warnings"]))

    def test_warned_rows_with_finite_values_remain_on_the_chart(self) -> None:
        class WarnedProvider(FakeOnclickProvider):
            def _request_json(self, method, url, payload=None):  # type: ignore[no-untyped-def]
                rows = super()._request_json(method, url, payload)
                if method == "POST":
                    rows[2]["error"] = "E2"
                return rows

        provider = WarnedProvider(FixtureProvider())
        result = provider.run_portfolio_backtest(
            holdings=[InstrumentHolding("SPY", "put", 100)],
            start="2025-01-02",
            end="2025-01-10",
            initial_capital=100_000,
            rebalance="none",
            call_rule=OptionRule("call", 540, 180),
            put_rule=OptionRule("put", 45, 21),
        )
        self.assertEqual(len(result["timeline"]), 6)
        self.assertTrue(any("remain on the chart" in item for item in result["warnings"]))

    def test_strict_quality_rejects_provider_error_rows(self) -> None:
        class WarnedStrictProvider(FakeOnclickProvider):
            def _request_json(self, method, url, payload=None):  # type: ignore[no-untyped-def]
                rows = super()._request_json(method, url, payload)
                if method == "POST":
                    rows = ExperimentalOnclickTests._strict_rows(rows)
                    rows[2]["error"] = "E2"
                return rows

        provider = WarnedStrictProvider(FixtureProvider(), strict_quality=True)
        with self.assertRaisesRegex(RuntimeError, "Verified beta rejected SPY long put.*E2"):
            provider.run_portfolio_backtest(
                holdings=[InstrumentHolding("SPY", "put", 100)],
                start="2025-01-02",
                end="2025-01-10",
                initial_capital=100_000,
                rebalance="none",
                call_rule=OptionRule("call", 540, 180),
                put_rule=OptionRule("put", 45, 21),
            )

    def test_strict_quality_rejects_crossed_option_market(self) -> None:
        class CrossedMarketProvider(FakeOnclickProvider):
            def _request_json(self, method, url, payload=None):  # type: ignore[no-untyped-def]
                rows = super()._request_json(method, url, payload)
                if method == "POST":
                    rows = ExperimentalOnclickTests._strict_rows(rows)
                    rows[3]["leg1_bid"] = 10.2
                return rows

        provider = CrossedMarketProvider(FixtureProvider(), strict_quality=True)
        with self.assertRaisesRegex(RuntimeError, "bid above its ask"):
            provider.run_portfolio_backtest(
                holdings=[InstrumentHolding("SPY", "call", 100)],
                start="2025-01-02",
                end="2025-01-10",
                initial_capital=100_000,
                rebalance="none",
                call_rule=OptionRule("call", 540, 180),
                put_rule=OptionRule("put", 45, 21),
            )

    def test_strict_quality_reports_reconciled_trading_rows(self) -> None:
        class CleanStrictProvider(FakeOnclickProvider):
            def _request_json(self, method, url, payload=None):  # type: ignore[no-untyped-def]
                rows = super()._request_json(method, url, payload)
                return ExperimentalOnclickTests._strict_rows(rows) if method == "POST" else rows

        provider = CleanStrictProvider(FixtureProvider(), strict_quality=True)
        result = provider.run_portfolio_backtest(
            holdings=[InstrumentHolding("SPY", "call", 100)],
            start="2025-01-02",
            end="2025-01-10",
            initial_capital=100_000,
            rebalance="none",
            call_rule=OptionRule("call", 540, 180),
            put_rule=OptionRule("put", 45, 21),
        )
        self.assertEqual(result["dataQuality"]["status"], "strict-integrity-checked")
        self.assertEqual(result["dataQuality"]["checkedTradingRows"], 6)
        self.assertEqual(result["dataQuality"]["externalErrorRows"], 0)
        self.assertFalse(result["dataQuality"]["independentlyRepriced"])

    def test_reference_quotes_replace_external_option_prices(self) -> None:
        class ContractProvider(FakeOnclickProvider):
            def _request_json(self, method, url, payload=None):  # type: ignore[no-untyped-def]
                rows = super()._request_json(method, url, payload)
                return ExperimentalOnclickTests._contract_rows(rows) if method == "POST" else rows

        class ReferenceQuotes:
            name = "marketdata-fixture"

            def option_quote_series(self, option_symbol, start, end):  # type: ignore[no-untyped-def]
                self.last_symbol = option_symbol
                return [
                    OptionQuote(
                        market_date=market_date,
                        option_symbol=option_symbol,
                        underlying="SPY",
                        expiration="2025-02-21",
                        side="call",
                        strike=100,
                        bid=9,
                        ask=10,
                        last=9.5,
                        delta=0.5,
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
                    for market_date in FakeOnclickProvider(FixtureProvider()).availability("SPY")
                    if start <= market_date <= end
                ]

        reference = ReferenceQuotes()
        provider = ContractProvider(
            FixtureProvider(),
            strict_quality=True,
            quote_provider=reference,
        )
        result = provider.run_portfolio_backtest(
            holdings=[InstrumentHolding("SPY", "call", 100)],
            start="2025-01-02",
            end="2025-01-10",
            initial_capital=100_000,
            rebalance="none",
            call_rule=OptionRule("call", 540, 180),
            put_rule=OptionRule("put", 45, 21),
        )
        self.assertEqual(reference.last_symbol, "SPY250221C00100000")
        self.assertAlmostEqual(result["metrics"]["strategy"]["endingValue"], 90_096.04, places=2)
        self.assertAlmostEqual(result["fees"], 3.96, places=2)
        self.assertTrue(result["dataQuality"]["independentlyRepriced"])
        self.assertEqual(result["dataQuality"]["referenceProvider"], "marketdata-fixture")
        self.assertEqual(result["dataQuality"]["repricedContracts"], 1)
        self.assertGreaterEqual(result["dataQuality"]["repricedQuotes"], 7)
        self.assertEqual(result["dataQuality"]["contractAudit"][0]["optionSymbol"], "SPY250221C00100000")
        self.assertEqual(result["dataQuality"]["contractAudit"][0]["referenceQuotes"], 7)
        self.assertEqual(len(result["dataQuality"]["contractAudit"][0]["sha256"]), 64)

    def test_reference_repricing_rejects_a_missing_daily_quote(self) -> None:
        class ContractProvider(FakeOnclickProvider):
            def _request_json(self, method, url, payload=None):  # type: ignore[no-untyped-def]
                rows = super()._request_json(method, url, payload)
                return ExperimentalOnclickTests._contract_rows(rows) if method == "POST" else rows

        class MissingReference:
            name = "marketdata-fixture"

            def option_quote_series(self, option_symbol, start, end):  # type: ignore[no-untyped-def]
                return []

        provider = ContractProvider(
            FixtureProvider(),
            strict_quality=True,
            quote_provider=MissingReference(),
        )
        with self.assertRaisesRegex(RuntimeError, "no usable opening ask"):
            provider.run_portfolio_backtest(
                holdings=[InstrumentHolding("SPY", "call", 100)],
                start="2025-01-02",
                end="2025-01-10",
                initial_capital=100_000,
                rebalance="none",
                call_rule=OptionRule("call", 540, 180),
                put_rule=OptionRule("put", 45, 21),
            )

    def test_empty_e2_selection_row_stays_in_cash_without_using_a_price(self) -> None:
        class DelayedContractProvider(FakeOnclickProvider):
            def _request_json(self, method, url, payload=None):  # type: ignore[no-untyped-def]
                rows = super()._request_json(method, url, payload)
                if method != "POST":
                    return rows
                rows = ExperimentalOnclickTests._contract_rows(rows)
                rows[0].update(
                    {
                        "error": "E2",
                        "leg1_bid": 0,
                        "leg1_ask": 0,
                        "leg1_value": 0,
                        "leg1_contracts": 0,
                        "leg1_expiry": "",
                        "leg1_strike": 0,
                        "leg1_open_transact": "",
                        "cash": 100_000,
                        "total_value": 100_000,
                    }
                )
                rows[1]["leg1_open_transact"] = 10
                return rows

        class ReferenceQuotes:
            name = "marketdata-fixture"

            def option_quote_series(self, option_symbol, start, end):  # type: ignore[no-untyped-def]
                return [
                    OptionQuote(
                        market_date=market_date,
                        option_symbol=option_symbol,
                        underlying="SPY",
                        expiration="2025-02-21",
                        side="call",
                        strike=100,
                        bid=9,
                        ask=10,
                        last=9.5,
                        delta=0.5,
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
                    for market_date in FakeOnclickProvider(FixtureProvider()).availability("SPY")
                    if start <= market_date <= end
                ]

        provider = DelayedContractProvider(
            FixtureProvider(),
            strict_quality=True,
            quote_provider=ReferenceQuotes(),
        )
        result = provider.run_portfolio_backtest(
            holdings=[InstrumentHolding("SPY", "call", 100)],
            start="2025-01-02",
            end="2025-01-10",
            initial_capital=100_000,
            rebalance="none",
            call_rule=OptionRule("call", 540, 180),
            put_rule=OptionRule("put", 45, 21),
        )
        self.assertEqual(result["dataQuality"]["selectionMissRows"], 1)
        self.assertEqual(result["timeline"][0]["strategy"], 100_000)
        self.assertTrue(any("remained in cash" in item for item in result["warnings"]))

    def test_multiple_option_rows_are_combined_into_one_strategy_timeline(self) -> None:
        provider = FakeOnclickProvider(FixtureProvider())
        result = provider.run_portfolio_backtest(
            holdings=[
                InstrumentHolding("SPY", "stock", 30),
                InstrumentHolding("SPY", "call", 25),
                InstrumentHolding("QQQ", "call", 25),
                InstrumentHolding("SPY", "put", 10),
            ],
            start="2025-01-02",
            end="2025-01-10",
            initial_capital=100_000,
            rebalance="none",
            call_rule=OptionRule("call", 365, 180),
            put_rule=OptionRule("put", 45, 21),
            option_rules={
                "SPY:call": OptionRule("call", 540, 180, strike_mode="percent_above", strike_value=10),
                "QQQ:call": OptionRule("call", 365, 90, strike_mode="percent_below", strike_value=5),
                "SPY:put": OptionRule("put", 45, 21),
            },
            cash_weight=10,
        )
        self.assertEqual(result["optionCount"], 3)
        self.assertEqual(len(result["timeline"]), 6)
        self.assertEqual(
            {item["symbol"] for item in result["breakdown"]},
            {"SPY shares", "SPY long call", "QQQ long call", "SPY long put", "Cash"},
        )
        self.assertEqual(set(result["optionRules"]), {"SPY:call", "QQQ:call", "SPY:put"})
        self.assertEqual(result["optionRules"]["SPY:call"]["strikeValue"], 10)
        self.assertEqual(result["optionRules"]["QQQ:call"]["strikeValue"], 5)
        self.assertTrue(all({"strategy", "spy", "qqq"} <= set(point) for point in result["timeline"]))
        self.assertTrue(any("single strategy line" in warning for warning in result["warnings"]))

    def test_verified_engine_selects_and_prices_locally_without_external_schedule(self) -> None:
        class NoExternalCalls(OnclickBacktestProvider):
            def _request_json(self, method, url, payload=None):  # type: ignore[no-untyped-def]
                raise AssertionError("Verified engine must not call the external beta archive")

        fixture = FixtureProvider("wave")
        provider = NoExternalCalls(
            fixture,
            strict_quality=True,
            quote_provider=fixture,
            verified_engine=True,
        )
        result = provider.run_portfolio_backtest(
            holdings=[InstrumentHolding("SPY", "call", 100)],
            start="2025-01-02",
            end="2025-03-31",
            initial_capital=100_000,
            rebalance="none",
            call_rule=OptionRule(
                "call",
                45,
                21,
                min_open_interest=0,
                max_spread_pct=1,
            ),
            put_rule=OptionRule(
                "put",
                45,
                21,
                min_open_interest=0,
                max_spread_pct=1,
            ),
        )
        quality = result["dataQuality"]
        self.assertEqual(quality["status"], "verified-independent-sleeves")
        self.assertTrue(quality["locallySelectedContracts"])
        self.assertGreater(quality["repricedContracts"], 0)
        self.assertGreater(quality["repricedQuotes"], 0)
        self.assertTrue(quality["chainAudit"])
        self.assertTrue(all(len(item["sha256"]) == 64 for item in quality["chainAudit"]))
        self.assertTrue(all(len(item["sha256"]) == 64 for item in quality["contractAudit"]))
        self.assertTrue(any("No OnclickMedia" in warning for warning in result["warnings"]))
        self.assertIn("The verified strategy finished", result["summary"])
        self.assertNotIn("external engine", result["summary"])


if __name__ == "__main__":
    unittest.main()
