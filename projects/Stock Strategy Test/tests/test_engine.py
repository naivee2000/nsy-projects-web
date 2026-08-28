from __future__ import annotations

import unittest

from stock_strategy_lab.engine import BacktestEngine, allocation_grid
from stock_strategy_lab.models import OptionRule, StockBar, StrategyDefinition, strategy_from_dict
from stock_strategy_lab.providers import FixtureProvider


START = "2025-01-02"
END = "2025-06-30"


def strategy(weights: tuple[int, int, int] = (60, 20, 20), **changes: object) -> StrategyDefinition:
    payload = {
        "ticker": "SPY",
        "start_date": START,
        "end_date": END,
        "stock_pct": weights[0],
        "call_pct": weights[1],
        "put_pct": weights[2],
    }
    payload.update(changes)
    return StrategyDefinition(**payload)


class CountingProvider:
    name = "counting-fixture"

    def __init__(self, scenario: str = "wave"):
        self.fixture = FixtureProvider(scenario)
        self.stock_calls = 0
        self.chain_calls = 0
        self.series_calls = 0
        self.chain_keys: list[tuple[str, str, str]] = []
        self.series_keys: list[tuple[str, str, str]] = []

    def stock_bars(self, symbol: str, start: str, end: str):
        self.stock_calls += 1
        return self.fixture.stock_bars(symbol, start, end)

    def option_chain(self, symbol: str, market_date: str, rule: OptionRule):
        self.chain_calls += 1
        self.chain_keys.append((symbol, market_date, rule.side))
        return self.fixture.option_chain(symbol, market_date, rule)

    def option_quote_series(self, option_symbol: str, start: str, end: str):
        self.series_calls += 1
        self.series_keys.append((option_symbol, start, end))
        return self.fixture.option_quote_series(option_symbol, start, end)


class MissingSeriesProvider(FixtureProvider):
    def option_quote_series(self, option_symbol: str, start: str, end: str):
        series = super().option_quote_series(option_symbol, start, end)
        return [item for index, item in enumerate(series) if index not in {8, 9}]


class SplitProvider(FixtureProvider):
    def stock_bars(self, symbol: str, start: str, end: str):
        bars = super().stock_bars(symbol, start, end)
        changed = list(bars)
        item = changed[len(changed) // 2]
        changed[len(changed) // 2] = StockBar(
            item.market_date,
            item.open,
            item.high,
            item.low,
            item.close,
            item.adjusted_close,
            item.volume,
            True,
        )
        return changed


class EngineAcceptanceTests(unittest.TestCase):
    def test_stock_only_matches_stock_benchmark(self) -> None:
        result = BacktestEngine().run(strategy((100, 0, 0)), FixtureProvider("wave"))
        self.assertAlmostEqual(result.metrics["endingValue"], result.metrics["benchmarkEndingValue"], places=2)
        self.assertAlmostEqual(result.metrics["versusBenchmark"], 0.0, places=2)
        self.assertFalse(result.warnings)

    def test_directional_fixture_scenarios(self) -> None:
        rising_call = BacktestEngine().run(strategy((0, 100, 0)), FixtureProvider("up"))
        rising_stock = BacktestEngine().run(strategy((100, 0, 0)), FixtureProvider("up"))
        falling_put = BacktestEngine().run(strategy((0, 0, 100)), FixtureProvider("down"))
        falling_stock = BacktestEngine().run(strategy((100, 0, 0)), FixtureProvider("down"))
        self.assertGreater(rising_call.metrics["endingValue"], rising_stock.metrics["endingValue"])
        self.assertGreater(falling_put.metrics["endingValue"], falling_stock.metrics["endingValue"])

    def test_mixed_attribution_reconciles_to_gain_loss(self) -> None:
        result = BacktestEngine().run(strategy(), FixtureProvider("wave"))
        self.assertAlmostEqual(sum(result.attribution.values()), result.metrics["gainLoss"], places=2)
        self.assertEqual(set(result.attribution), {"stock", "call", "put"})
        self.assertGreaterEqual(len(result.explanation), 4)

    def test_rolls_whole_lots_fees_and_residual_cash(self) -> None:
        result = BacktestEngine().run(strategy(), FixtureProvider("wave"))
        self.assertGreater(result.metrics["rollCount"], 0)
        self.assertGreater(result.metrics["fees"], 0)
        self.assertTrue(all(isinstance(trade["quantity"], int) for trade in result.trades))
        self.assertTrue(all(day["cash"] >= -0.01 for day in result.daily_equity))
        option_trades = [trade for trade in result.trades if trade["leg"] in {"call", "put"} and trade["action"] == "buy"]
        self.assertTrue(option_trades)
        self.assertTrue(all(trade["quantity"] >= 1 for trade in option_trades))

    def test_expiration_is_cash_settled(self) -> None:
        call_rule = OptionRule("call", target_dte=10, roll_dte=0)
        result = BacktestEngine().run(
            strategy((0, 100, 0), call_rule=call_rule),
            FixtureProvider("up"),
        )
        self.assertTrue(any(trade["action"] == "expire" for trade in result.trades))
        self.assertFalse(any("physical" in trade["reason"] for trade in result.trades))

    def test_missing_quotes_are_disclosed_and_degraded(self) -> None:
        result = BacktestEngine().run(strategy((0, 100, 0)), MissingSeriesProvider("up"))
        self.assertTrue(any("intrinsic value" in warning for warning in result.warnings))

    def test_split_adjustment_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "stock split"):
            BacktestEngine().run(strategy(), SplitProvider("wave"))

    def test_default_sweep_has_66_deterministic_combinations(self) -> None:
        first = BacktestEngine().run(strategy(), FixtureProvider("wave"), include_sweep=True)
        second = BacktestEngine().run(strategy(), FixtureProvider("wave"), include_sweep=True)
        self.assertEqual(len(allocation_grid(10)), 66)
        self.assertEqual(len(first.sweep), 66)
        self.assertEqual(first.sweep, second.sweep)
        self.assertEqual(first.sweep, sorted(first.sweep, key=lambda item: (item["endingValue"], -item["maxDrawdownPct"]), reverse=True))

    def test_sweep_reuses_one_market_tape(self) -> None:
        single_provider = CountingProvider()
        BacktestEngine().run(strategy(), single_provider)
        sweep_provider = CountingProvider()
        BacktestEngine().run(strategy(), sweep_provider, include_sweep=True)
        self.assertEqual(sweep_provider.stock_calls, 1)
        self.assertEqual(sweep_provider.chain_calls, len(set(sweep_provider.chain_keys)))
        self.assertEqual(sweep_provider.series_calls, len(set(sweep_provider.series_keys)))
        self.assertLess(sweep_provider.chain_calls, single_provider.chain_calls + 10)
        self.assertLess(sweep_provider.series_calls, single_provider.series_calls + 10)

    def test_small_allocations_remain_cash_with_warning(self) -> None:
        result = BacktestEngine().run(strategy((0, 100, 0), initial_capital=100), FixtureProvider("wave"))
        self.assertTrue(any("whole contract" in warning for warning in result.warnings))
        self.assertGreaterEqual(result.metrics["endingValue"], 0)

    def test_guided_payload_maps_to_advanced_fields_and_summary(self) -> None:
        payload = {
            "ticker": "qqq",
            "startDate": START,
            "endDate": END,
            "initialCapital": 125000,
            "stockPct": 70,
            "callPct": 30,
            "putPct": 0,
            "stockSlippageBps": 7,
            "optionCommission": 0.75,
            "sweepStepPct": 10,
            "callRule": {
                "targetDte": 50,
                "rollDte": 18,
                "targetDelta": 0.45,
                "maxSpreadPct": 0.15,
                "strikeMode": "percent_above",
                "strikeValue": 10,
            },
            "putRule": {
                "targetDte": 60,
                "rollDte": 20,
                "targetDelta": 0.40,
                "maxSpreadPct": 0.25,
                "strikeMode": "dollar_below",
                "strikeValue": 5,
            },
        }
        parsed = strategy_from_dict(payload)
        self.assertEqual(parsed.ticker, "qqq")
        self.assertEqual(parsed.call_rule.target_dte, 50)
        self.assertEqual(parsed.put_rule.roll_dte, 20)
        self.assertEqual(parsed.call_rule.strike_mode, "percent_above")
        self.assertAlmostEqual(parsed.call_rule.target_strike(100) or 0, 110)
        self.assertEqual(parsed.put_rule.strike_mode, "dollar_below")
        self.assertEqual(parsed.put_rule.target_strike(100), 95)
        self.assertEqual(parsed.stock_slippage_bps, 7)
        summary = parsed.plain_summary()
        self.assertIn("$125,000", summary)
        self.assertIn("70% in shares", summary)


if __name__ == "__main__":
    unittest.main()
