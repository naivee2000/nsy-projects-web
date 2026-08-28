from __future__ import annotations

from collections import Counter
from datetime import date
import threading
import time
import unittest

from stock_strategy_lab.calendar import trading_dates
from stock_strategy_lab.models import (
    ROBINHOOD_OPTION_FEE_PER_CONTRACT,
    OptionQuote,
    OptionRule,
    StockBar,
    StrategyDefinition,
)
from stock_strategy_lab.providers import FixtureProvider
from stock_strategy_lab.unified import HybridMarketProvider, InstrumentHolding, _select_contract, run_unified_backtest


class UnifiedPortfolioTests(unittest.TestCase):
    @staticmethod
    def _strike_chain() -> list[OptionQuote]:
        return [
            OptionQuote(
                market_date="2025-01-02",
                option_symbol=f"SPY-{strike}",
                underlying="SPY",
                expiration="2025-12-19",
                side="call",
                strike=float(strike),
                bid=10,
                ask=10.5,
                delta=delta,
                open_interest=1_000,
                underlying_price=100,
            )
            for strike, delta in ((90, 0.80), (95, 0.65), (100, 0.50), (105, 0.35), (110, 0.20))
        ]

    def test_strike_rules_use_current_stock_price_at_each_purchase(self) -> None:
        chain = self._strike_chain()
        above = _select_contract(
            chain,
            OptionRule("call", strike_mode="percent_above", strike_value=10),
            100,
        )
        below = _select_contract(
            chain,
            OptionRule("call", strike_mode="dollar_below", strike_value=5),
            100,
        )
        delta = _select_contract(
            chain,
            OptionRule("call", target_delta=0.35, strike_mode="delta"),
            100,
        )
        self.assertEqual(above.strike, 110)
        self.assertEqual(below.strike, 95)
        self.assertEqual(delta.strike, 105)

    def test_each_option_holding_can_use_its_own_rule(self) -> None:
        class RuleCaptureProvider(FixtureProvider):
            def __init__(self) -> None:
                super().__init__()
                self.rules: list[tuple[str, str]] = []

            def option_chain(self, symbol, market_date, rule):  # type: ignore[no-untyped-def]
                self.rules.append((symbol, rule.strike_mode))
                return super().option_chain(symbol, market_date, rule)

        provider = RuleCaptureProvider()
        result = run_unified_backtest(
            provider,
            [
                InstrumentHolding("SPY", "call", 50),
                InstrumentHolding("QQQ", "call", 50),
            ],
            "2025-01-02",
            "2025-02-28",
            100_000,
            "none",
            OptionRule("call", 365, 0),
            OptionRule("put", 45, 21),
            option_rules={
                "SPY:call": OptionRule(
                    "call", 365, 0,
                    strike_mode="percent_above", strike_value=10,
                ),
                "QQQ:call": OptionRule(
                    "call", 365, 0,
                    strike_mode="percent_below", strike_value=5,
                ),
            },
        )
        self.assertIn(("SPY", "percent_above"), provider.rules)
        self.assertIn(("QQQ", "percent_below"), provider.rules)
        self.assertEqual(result["optionRules"]["SPY:call"]["strike_value"], 10)
        self.assertEqual(result["optionRules"]["QQQ:call"]["strike_value"], 5)

    def test_robinhood_option_fee_is_the_engine_default(self) -> None:
        strategy = StrategyDefinition("SPY", "2025-01-02", "2025-12-31")
        self.assertEqual(strategy.option_commission, ROBINHOOD_OPTION_FEE_PER_CONTRACT)
        self.assertEqual(ROBINHOOD_OPTION_FEE_PER_CONTRACT, 0.04)

    def test_same_ticker_can_have_shares_call_and_put_rows(self) -> None:
        result = run_unified_backtest(
            FixtureProvider(),
            [
                InstrumentHolding("SPY", "stock", 40),
                InstrumentHolding("SPY", "call", 30),
                InstrumentHolding("SPY", "put", 20),
            ],
            "2025-01-02",
            "2025-12-31",
            100_000,
            "quarterly",
            OptionRule("call", 365, 120),
            OptionRule("put", 45, 21),
            cash_weight=10,
        )
        labels = {item["symbol"] for item in result["breakdown"]}
        self.assertIn("SPY shares", labels)
        self.assertIn("SPY long call", labels)
        self.assertIn("SPY long put", labels)
        self.assertIn("Cash", labels)
        self.assertEqual(result["optionCount"], 2)
        self.assertGreater(result["rebalanceCount"], 0)
        # Buying at the ask and immediately valuing at the bid makes the first
        # marked value lower than starting cash; the spread is intentionally visible.
        self.assertLess(result["timeline"][0]["strategy"], 100_000)
        self.assertGreater(result["timeline"][0]["strategy"], 90_000)

    def test_multiple_underlyings_and_benchmarks_share_one_timeline(self) -> None:
        result = run_unified_backtest(
            FixtureProvider(),
            [InstrumentHolding("SPY", "call", 25), InstrumentHolding("QQQ", "stock", 75)],
            "2025-01-02",
            "2025-09-30",
            50_000,
            "monthly",
            OptionRule("call", 365, 120),
            OptionRule("put", 45, 21),
        )
        self.assertGreater(len(result["timeline"]), 100)
        self.assertTrue(all({"strategy", "spy", "qqq"} <= set(point) for point in result["timeline"]))
        self.assertEqual({item["symbol"] for item in result["coverage"]}, {"SPY", "QQQ"})

    def test_missing_leg_retries_once_without_retrading_healthy_leg(self) -> None:
        class SelectiveProvider(FixtureProvider):
            def __init__(self) -> None:
                super().__init__()
                self.chain_calls: Counter[tuple[str, str]] = Counter()

            def option_chain(self, symbol, market_date, rule):  # type: ignore[no-untyped-def]
                self.chain_calls[(symbol, rule.side)] += 1
                if symbol == "QQQ":
                    return []
                return super().option_chain(symbol, market_date, rule)

        provider = SelectiveProvider()
        result = run_unified_backtest(
            provider,
            [InstrumentHolding("SPY", "call", 50), InstrumentHolding("QQQ", "put", 50)],
            "2025-01-02",
            "2025-02-28",
            100_000,
            "none",
            OptionRule("call", 365, 0),
            OptionRule("put", 365, 0),
        )
        self.assertEqual(provider.chain_calls[("SPY", "call")], 1)
        self.assertEqual(provider.chain_calls[("QQQ", "put")], 2)
        self.assertEqual(result["optionRetryCount"], 1)
        self.assertEqual(result["rebalanceCount"], 0)
        self.assertTrue(any("limited retry" in warning for warning in result["warnings"]))

    def test_zero_weight_option_is_not_downloaded_or_retried(self) -> None:
        class CountingProvider(FixtureProvider):
            def __init__(self) -> None:
                super().__init__()
                self.chain_calls = 0

            def option_chain(self, symbol, market_date, rule):  # type: ignore[no-untyped-def]
                self.chain_calls += 1
                return super().option_chain(symbol, market_date, rule)

        provider = CountingProvider()
        result = run_unified_backtest(
            provider,
            [InstrumentHolding("SPY", "stock", 100), InstrumentHolding("QQQ", "put", 0)],
            "2025-01-02",
            "2025-02-28",
            100_000,
            "none",
            OptionRule("call", 365, 0),
            OptionRule("put", 45, 21),
        )
        self.assertEqual(provider.chain_calls, 0)
        self.assertEqual(result["optionRetryCount"], 0)

    def test_short_put_roll_does_not_replace_long_call(self) -> None:
        class CountingProvider(FixtureProvider):
            def __init__(self) -> None:
                super().__init__()
                self.chain_calls: Counter[str] = Counter()

            def option_chain(self, symbol, market_date, rule):  # type: ignore[no-untyped-def]
                self.chain_calls[rule.side] += 1
                return super().option_chain(symbol, market_date, rule)

        provider = CountingProvider()
        result = run_unified_backtest(
            provider,
            [InstrumentHolding("SPY", "call", 50), InstrumentHolding("SPY", "short_put", 50)],
            "2025-01-02",
            "2025-06-30",
            1_000_000,
            "none",
            OptionRule("call", 365, 0),
            OptionRule("put", 45, 21),
        )
        self.assertEqual(provider.chain_calls["call"], 1)
        self.assertGreater(provider.chain_calls["put"], 1)
        self.assertGreater(result["rollCount"], 0)
        self.assertIn("Rolling a short-dated put does not replace", result["assumptions"][2])

    def test_deep_itm_short_put_reports_rational_assignment(self) -> None:
        class AssignmentProvider:
            name = "assignment-fixture"

            def stock_bars(self, symbol, start, end):  # type: ignore[no-untyped-def]
                return [
                    StockBar(
                        session.isoformat(),
                        100 if session < date(2025, 1, 15) else 70,
                        100 if session < date(2025, 1, 15) else 70,
                        100 if session < date(2025, 1, 15) else 70,
                        100 if session < date(2025, 1, 15) else 70,
                        100 if session < date(2025, 1, 15) else 70,
                    )
                    for session in trading_dates(date.fromisoformat(start), date.fromisoformat(end))
                ]

            def option_chain(self, symbol, market_date, rule):  # type: ignore[no-untyped-def]
                return [
                    OptionQuote(
                        market_date,
                        "SPY250321P00100000",
                        "SPY",
                        "2025-03-21",
                        "put",
                        100,
                        5.0,
                        5.1,
                        open_interest=10_000,
                        underlying_price=100,
                    )
                ]

            def option_quote_series(self, option_symbol, start, end):  # type: ignore[no-untyped-def]
                rows = []
                for session in trading_dates(date.fromisoformat(start), date.fromisoformat(end)):
                    crashed = session >= date(2025, 1, 15)
                    rows.append(
                        OptionQuote(
                            session.isoformat(), option_symbol, "SPY", "2025-03-21", "put", 100,
                            29.98 if crashed else 5.0,
                            30.04 if crashed else 5.1,
                            open_interest=10_000,
                            underlying_price=70 if crashed else 100,
                        )
                    )
                return rows

        request = dict(
            provider=AssignmentProvider(),
            holdings=[InstrumentHolding("SPY", "short_put", 100)],
            start="2025-01-02",
            end="2025-02-28",
            initial_capital=100_000,
            rebalance="none",
            call_rule=OptionRule("call", 365, 120),
            put_rule=OptionRule("put", 45, 0, min_open_interest=0, max_spread_pct=1),
        )
        assigned = run_unified_backtest(**request)
        unassigned = run_unified_backtest(**request, assignment_mode="none")
        self.assertEqual(assigned["assignmentCount"], 1)
        self.assertEqual(unassigned["assignmentCount"], 0)
        self.assertTrue(any("rational-assignment" in warning for warning in assigned["warnings"]))

    def test_option_strike_selection_uses_raw_not_adjusted_close(self) -> None:
        class RawAdjustedProvider(FixtureProvider):
            selected_symbol = ""

            def stock_bars(self, symbol, start, end):  # type: ignore[no-untyped-def]
                return [
                    type(bar)(
                        market_date=bar.market_date,
                        open=100,
                        high=100,
                        low=100,
                        close=100,
                        adjusted_close=50,
                    )
                    for bar in super().stock_bars(symbol, start, end)
                ]

            def option_chain(self, symbol, market_date, rule):  # type: ignore[no-untyped-def]
                return [
                    OptionQuote(
                        market_date=market_date,
                        option_symbol=f"RAW-{strike}",
                        underlying=symbol,
                        expiration="2025-12-19",
                        side="call",
                        strike=strike,
                        bid=10,
                        ask=10.1,
                        open_interest=1_000,
                    )
                    for strike in (50.0, 100.0)
                ]

            def option_quote_series(self, option_symbol, start, end):  # type: ignore[no-untyped-def]
                self.selected_symbol = option_symbol
                strike = float(option_symbol.removeprefix("RAW-"))
                return [
                    OptionQuote(
                        market_date=bar.market_date,
                        option_symbol=option_symbol,
                        underlying="SPY",
                        expiration="2025-12-19",
                        side="call",
                        strike=strike,
                        bid=10,
                        ask=10.1,
                        open_interest=1_000,
                    )
                    for bar in self.stock_bars("SPY", start, end)
                ]

        provider = RawAdjustedProvider()
        run_unified_backtest(
            provider,
            [InstrumentHolding("SPY", "call", 100)],
            "2025-01-02",
            "2025-02-28",
            100_000,
            "none",
            OptionRule("call", 365, 0, min_open_interest=0, max_spread_pct=1),
            OptionRule("put", 45, 21),
        )
        self.assertEqual(provider.selected_symbol, "RAW-100.0")

    def test_duplicate_symbol_and_kind_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "only once"):
            run_unified_backtest(
                FixtureProvider(),
                [InstrumentHolding("SPY", "stock", 50), InstrumentHolding("SPY", "stock", 50)],
                "2025-01-02",
                "2025-12-31",
                10_000,
                "annual",
                OptionRule("call"),
                OptionRule("put"),
            )

    def test_hybrid_provider_routes_shares_and_options_separately(self) -> None:
        class Stub:
            def __init__(self) -> None:
                self.calls: list[tuple[str, ...]] = []

            def stock_bars(self, *args):  # type: ignore[no-untyped-def]
                self.calls.append(("stock", *args))
                return ["stock-bars"]

            def option_chain(self, *args):  # type: ignore[no-untyped-def]
                self.calls.append(("chain", str(args[0])))
                return ["chain"]

            def option_quote_series(self, *args):  # type: ignore[no-untyped-def]
                self.calls.append(("series", *args))
                return ["series"]

        stocks, options = Stub(), Stub()
        provider = HybridMarketProvider(stocks, options)
        self.assertEqual(provider.stock_bars("SPY", "a", "b"), ["stock-bars"])
        self.assertEqual(provider.option_chain("SPY", "a", OptionRule("call")), ["chain"])
        self.assertEqual(provider.option_quote_series("contract", "a", "b"), ["series"])
        self.assertEqual(stocks.calls[0][0], "stock")
        self.assertEqual([item[0] for item in options.calls], ["chain", "series"])

    def test_independent_provider_reads_run_in_parallel(self) -> None:
        class DelayedProvider(FixtureProvider):
            def __init__(self) -> None:
                super().__init__()
                self.lock = threading.Lock()
                self.active = Counter()
                self.maximum = Counter()

            def _enter(self, kind: str) -> None:
                with self.lock:
                    self.active[kind] += 1
                    self.maximum[kind] = max(self.maximum[kind], self.active[kind])

            def _leave(self, kind: str) -> None:
                with self.lock:
                    self.active[kind] -= 1

            def stock_bars(self, *args):  # type: ignore[no-untyped-def]
                self._enter("stock")
                try:
                    time.sleep(0.03)
                    return super().stock_bars(*args)
                finally:
                    self._leave("stock")

            def option_chain(self, *args):  # type: ignore[no-untyped-def]
                self._enter("chain")
                try:
                    time.sleep(0.03)
                    return super().option_chain(*args)
                finally:
                    self._leave("chain")

            def option_quote_series(self, *args):  # type: ignore[no-untyped-def]
                self._enter("series")
                try:
                    time.sleep(0.03)
                    return super().option_quote_series(*args)
                finally:
                    self._leave("series")

        provider = DelayedProvider()
        run_unified_backtest(
            provider,
            [
                InstrumentHolding("SPY", "call", 25),
                InstrumentHolding("SPY", "put", 25),
                InstrumentHolding("QQQ", "call", 25),
                InstrumentHolding("QQQ", "put", 25),
            ],
            "2025-01-02",
            "2025-02-28",
            1_000_000,
            "none",
            OptionRule("call", 365, 120),
            OptionRule("put", 45, 21),
        )
        self.assertGreaterEqual(provider.maximum["stock"], 2)
        self.assertGreaterEqual(provider.maximum["chain"], 2)
        self.assertGreaterEqual(provider.maximum["series"], 2)


if __name__ == "__main__":
    unittest.main()
