from __future__ import annotations

from datetime import date
import math
from pathlib import Path
import tempfile
import unittest

from stock_strategy_lab.calendar import trading_dates
from stock_strategy_lab.modeled import FreeModeledProvider, american_option_price, black_scholes_price
from stock_strategy_lab.models import OptionRule, StockBar
from stock_strategy_lab.unified import InstrumentHolding


class FakeFred:
    def values(self, series: str) -> dict[str, float]:
        return {
            "2020-01-02": 20.0 if series in {"VIXCLS", "VXNCLS"} else 1.5,
            "2024-01-02": 18.0 if series in {"VIXCLS", "VXNCLS"} else 4.0,
        }


class FakeStocks:
    def __init__(self, crash_after: str | None = None):
        self.crash_after = crash_after

    def stock_bars(self, symbol: str, start: str, end: str) -> list[StockBar]:
        bars = []
        for index, market_day in enumerate(
            trading_dates(date.fromisoformat(start), date.fromisoformat(end))
        ):
            price = 100 * math.exp(index * 0.00035)
            if self.crash_after and market_day.isoformat() > self.crash_after:
                price *= 0.55
            bars.append(
                StockBar(
                    market_date=market_day.isoformat(),
                    open=price,
                    high=price,
                    low=price,
                    close=price,
                    adjusted_close=price,
                )
            )
        return bars


class FreeModeledProviderTests(unittest.TestCase):
    def provider(self, crash_after: str | None = None) -> FreeModeledProvider:
        return FreeModeledProvider(
            FakeStocks(crash_after),
            Path(tempfile.mkdtemp()),
            fred=FakeFred(),  # type: ignore[arg-type]
        )

    def test_black_scholes_respects_call_put_parity(self) -> None:
        call, _ = black_scholes_price(100, 100, 1, 0.04, 0.01, 0.22, "call")
        put, _ = black_scholes_price(100, 100, 1, 0.04, 0.01, 0.22, "put")
        parity = 100 * math.exp(-0.01) - 100 * math.exp(-0.04)
        self.assertAlmostEqual(call - put, parity, places=8)

    def test_american_put_includes_early_exercise_value(self) -> None:
        european, _ = black_scholes_price(70, 100, 1, 0.06, 0.0, 0.20, "put")
        american, delta = american_option_price(70, 100, 1, 0.06, 0.0, 0.20, "put", steps=96)
        self.assertGreaterEqual(american, european)
        self.assertLess(delta, 0)

    def test_adaptive_lattice_converges_to_the_high_step_reference(self) -> None:
        adaptive, _ = american_option_price(65, 100, 0.75, 0.05, 0.01, 0.28, "put")
        reference, _ = american_option_price(65, 100, 0.75, 0.05, 0.01, 0.28, "put", steps=1024)
        self.assertLessEqual(abs(adaptive - reference), max(0.01, reference * 0.001))

    def test_deep_out_of_money_contract_can_have_a_zero_bid(self) -> None:
        provider = self.provider()
        provider.stock_bars("SPY", "2024-01-02", "2024-06-30")
        chain = provider.option_chain(
            "SPY",
            "2024-03-01",
            OptionRule(
                "call",
                target_dte=30,
                roll_dte=5,
                strike_mode="percent_above",
                strike_value=50,
            ),
        )
        quote = min(chain, key=lambda item: abs(item.strike / item.underlying_price - 1.5))
        self.assertEqual(quote.bid, 0)
        self.assertLessEqual(quote.ask, quote.underlying_price)

    def test_option_opening_quote_does_not_look_at_future_prices(self) -> None:
        stable = self.provider()
        crashed = self.provider("2024-03-01")
        for provider in (stable, crashed):
            provider.stock_bars("SPY", "2023-01-03", "2024-12-31")
        rule = OptionRule("call", target_dte=365, roll_dte=120)
        stable_quote = stable.option_chain("SPY", "2024-02-01", rule)[4]
        crashed_quote = crashed.option_chain("SPY", "2024-02-01", rule)[4]
        self.assertEqual(stable_quote.bid, crashed_quote.bid)
        self.assertEqual(stable_quote.ask, crashed_quote.ask)
        self.assertEqual(stable_quote.iv, crashed_quote.iv)

    def test_split_adjusts_modeled_contract_terms_but_not_realized_returns(self) -> None:
        class SplitStocks:
            def stock_bars(self, symbol, start, end):  # type: ignore[no-untyped-def]
                rows = [
                    ("2024-01-02", 100, 50, 1),
                    ("2024-01-03", 100, 50, 1),
                    ("2024-01-04", 100, 50, 1),
                    ("2024-01-05", 100, 50, 1),
                    ("2024-01-08", 50, 50, 2),
                    ("2024-01-09", 50, 50, 1),
                    ("2024-01-10", 50, 50, 1),
                ]
                return [
                    StockBar(day, raw, raw, raw, raw, adjusted, split_detected=split != 1, split_factor=split)
                    for day, raw, adjusted, split in rows
                    if start <= day <= end
                ]

        provider = FreeModeledProvider(SplitStocks(), Path(tempfile.mkdtemp()), fred=FakeFred())  # type: ignore[arg-type]
        provider.stock_bars("SPY", "2024-01-02", "2024-01-10")
        chain = provider.option_chain("SPY", "2024-01-05", OptionRule("call", 45, 21))
        opening = min(chain, key=lambda quote: abs(quote.strike - 100))
        series = provider.option_quote_series(opening.option_symbol, "2024-01-05", "2024-01-10")
        after = next(quote for quote in series if quote.market_date == "2024-01-08")
        self.assertEqual(after.underlying_price, 50)
        self.assertEqual(after.strike, 50)
        self.assertEqual(after.contract_multiplier, 200)
        self.assertLess(after.iv or 0, 0.5)

    def test_free_mode_returns_one_automatic_combined_result(self) -> None:
        provider = self.provider()
        result = provider.run_portfolio_backtest(
            holdings=[
                InstrumentHolding("SPY", "stock", 40),
                InstrumentHolding("QQQ", "stock", 30),
                InstrumentHolding("SPY", "call", 15),
                InstrumentHolding("QQQ", "put", 15),
            ],
            start="2020-01-02",
            end="2024-12-31",
            initial_capital=100_000,
            rebalance="quarterly",
            call_rule=OptionRule("call", target_dte=540, roll_dte=180),
            put_rule=OptionRule("put", target_dte=45, roll_dte=21),
            cash_weight=0,
        )
        self.assertEqual(result["provider"], "free-modeled")
        self.assertEqual(result["pricingMode"], "modeled")
        self.assertEqual(result["pricingCoverage"]["realOptionQuotes"], 0)
        self.assertGreater(result["pricingCoverage"]["modeledQuoteCount"], 100)
        self.assertGreater(len(result["timeline"]), 1_000)
        self.assertIn("Modeled option prices", result["warnings"][0])
        self.assertTrue(all({"strategy", "spy", "qqq"} <= set(row) for row in result["timeline"]))

    def test_cash_secured_short_put_reserves_collateral_and_can_finish(self) -> None:
        provider = self.provider("2024-06-01")
        result = provider.run_portfolio_backtest(
            holdings=[InstrumentHolding("SPY", "short_put", 100)],
            start="2024-01-02",
            end="2024-12-31",
            initial_capital=100_000,
            rebalance="none",
            call_rule=OptionRule("call", target_dte=365, roll_dte=120),
            put_rule=OptionRule("put", target_dte=45, roll_dte=21),
            cash_weight=0,
        )
        self.assertGreater(result["timeline"][-1]["strategy"], 0)
        self.assertLess(result["timeline"][-1]["strategy"], 100_000)
        self.assertEqual(result["breakdown"][0]["kind"], "short_put")


if __name__ == "__main__":
    unittest.main()
