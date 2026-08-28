from __future__ import annotations

import unittest

from stock_strategy_lab.portfolio import DemoPortfolioProvider, Holding, run_portfolio_backtest


class LateStartProvider(DemoPortfolioProvider):
    def stock_bars(self, symbol: str, start: str, end: str):
        bars = super().stock_bars(symbol, start, end)
        if symbol.upper() == "AAPL":
            return [bar for bar in bars if bar.market_date >= "2023-12-05"]
        return bars


class PortfolioBacktestTests(unittest.TestCase):
    def test_strategy_compares_same_starting_money_with_spy_and_qqq(self) -> None:
        result = run_portfolio_backtest(
            DemoPortfolioProvider(),
            [Holding("SPY", 60), Holding("QQQ", 40)],
            "2018-01-02",
            "2025-12-31",
            100_000,
            "quarterly",
        )
        self.assertEqual(result["initialCapital"], 100_000)
        self.assertEqual(result["timeline"][0]["strategy"], 100_000)
        self.assertEqual(result["timeline"][0]["spy"], 100_000)
        self.assertEqual(result["timeline"][0]["qqq"], 100_000)
        self.assertGreater(result["rebalanceCount"], 20)
        self.assertEqual({item["symbol"] for item in result["breakdown"]}, {"SPY", "QQQ"})

    def test_buy_and_hold_does_not_rebalance_and_weights_drift(self) -> None:
        result = run_portfolio_backtest(
            DemoPortfolioProvider(),
            [Holding("AAPL", 50), Holding("QQQ", 50)],
            "2020-01-02",
            "2025-12-31",
            50_000,
            "none",
        )
        self.assertEqual(result["rebalanceCount"], 0)
        self.assertAlmostEqual(sum(item["endingWeight"] for item in result["breakdown"]), 100, places=6)

    def test_allocations_must_total_one_hundred(self) -> None:
        with self.assertRaisesRegex(ValueError, "100%"):
            run_portfolio_backtest(
                DemoPortfolioProvider(), [Holding("SPY", 70), Holding("QQQ", 20)],
                "2020-01-02", "2021-01-04", 10_000, "annual"
            )

    def test_cash_is_included_and_does_not_need_market_data(self) -> None:
        result = run_portfolio_backtest(
            DemoPortfolioProvider(),
            [Holding("SPY", 50), Holding("QQQ", 30)],
            "2020-01-02",
            "2025-12-31",
            100_000,
            "quarterly",
            cash_weight=20,
        )
        self.assertEqual(result["cashWeight"], 20)
        self.assertEqual(result["timeline"][0]["strategy"], 100_000)
        cash = next(item for item in result["breakdown"] if item["symbol"] == "CASH")
        self.assertAlmostEqual(cash["targetWeight"], 20)
        self.assertTrue(any("Cash earns no interest" in item for item in result["assumptions"]))

    def test_cash_counts_toward_one_hundred_percent(self) -> None:
        with self.assertRaisesRegex(ValueError, "100%"):
            run_portfolio_backtest(
                DemoPortfolioProvider(), [Holding("SPY", 70)],
                "2020-01-02", "2021-01-04", 10_000, "annual", cash_weight=20
            )

    def test_late_start_symbol_explains_shorter_chart_range(self) -> None:
        result = run_portfolio_backtest(
            LateStartProvider(), [Holding("AAPL", 50), Holding("QQQ", 50)],
            "2020-01-02", "2025-12-31", 10_000, "annual"
        )
        self.assertEqual(result["startDate"], "2023-12-05")
        self.assertIn("AAPL has no usable price before 2023-12-05", result["warnings"][0])
        coverage = {item["symbol"]: item for item in result["coverage"]}
        self.assertEqual(coverage["AAPL"]["startDate"], "2023-12-05")
