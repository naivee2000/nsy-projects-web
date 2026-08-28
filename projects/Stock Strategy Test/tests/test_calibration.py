from __future__ import annotations

from datetime import date
from pathlib import Path
import tempfile
import unittest

from stock_strategy_lab.calibration import (
    AccuracyCalibration,
    DAILY_BUDGET_SETTING,
    SSVIParameters,
    VALIDATION_SETTING,
)
from stock_strategy_lab.models import OptionQuote, OptionRule
from stock_strategy_lab.storage import AppStore, MarketVault
from stock_strategy_lab.unified import InstrumentHolding


class FakeReference:
    def values(self, series: str) -> dict[str, float]:
        return {"2020-01-02": 4.0 if series.startswith("UST") else 20.0}


class FakeExactProvider:
    available = False

    def __init__(self, vault: MarketVault | None = None) -> None:
        self.vault = vault
        self.chain_calls = 0

    def history_window_start(self, as_of: date | None = None) -> date:
        current = as_of or date.today()
        return current.replace(year=current.year - 1)

    def capture_accuracy_chain(self, symbol: str, market_date: str, side: str, target_dte: int):  # type: ignore[no-untyped-def]
        self.chain_calls += 1
        return []


def surface_rows(market_date: str, volatility: float, symbol: str = "SPY") -> list[OptionQuote]:
    expiration = "2026-06-26"
    output = []
    for strike in (80.0, 90.0, 100.0, 110.0, 120.0):
        output.append(
            OptionQuote(
                market_date=market_date,
                option_symbol=f"{symbol}-{market_date}-{strike}",
                underlying=symbol,
                expiration=expiration,
                side="call",
                strike=strike,
                bid=9.8,
                ask=10.2,
                iv=volatility,
                open_interest=1_000,
                volume=100,
                underlying_price=100.0,
                pricing_source="exact",
            )
        )
    return output


class CalibrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = Path(tempfile.mkdtemp())
        self.vault = MarketVault(self.directory)
        self.store = AppStore(self.directory)
        self.exact = FakeExactProvider(self.vault)
        self.calibration = AccuracyCalibration(
            self.vault, self.store, self.exact, FakeReference()
        )

    def test_essvi_parameters_obey_static_arbitrage_constraint(self) -> None:
        params = self.calibration._fit_essvi(surface_rows("2025-01-02", 0.24), 100.0, 540)
        self.assertIsInstance(params, SSVIParameters)
        assert params is not None
        self.assertLessEqual(params.theta * params.phi * (1 + abs(params.rho)), 4.0)
        for moneyness in (-0.7, -0.3, 0.0, 0.3, 0.7):
            self.assertGreater(params.volatility(moneyness, 540 / 365.25), 0)

    def test_surface_never_uses_a_future_snapshot(self) -> None:
        self.vault.save_option_quotes("marketdata", surface_rows("2025-01-02", 0.20))
        self.vault.save_option_quotes("marketdata", surface_rows("2025-01-09", 0.80))
        estimate = self.calibration.estimate(
            "SPY", "2025-01-08", "call", 100.0, 534, 100.0, 0.35
        )
        self.assertEqual(estimate.source, "calibrated")
        self.assertLess(estimate.volatility, 0.30)

    def test_strict_badge_requires_saved_every_portfolio_validation(self) -> None:
        holding = InstrumentHolding("SPY", "call", 20)
        rule = OptionRule("call", target_dte=540, roll_dte=180)
        self.store.save_setting(
            VALIDATION_SETTING,
            {
                "status": "passed",
                "worstEndingErrorPct": 0.8,
                "referenceStart": "2025-01-01",
                "referenceEnd": "2025-12-31",
                "validatedAt": "2026-01-02T10:00:00-05:00",
            },
        )
        result = self.calibration.pricing_accuracy(
            "2025-03-01", [holding], {holding.key: rule}, {"calibrated": 100}, 0.5
        )
        self.assertEqual(result["label"], "Validated within 1%")
        uncertain = self.calibration.pricing_accuracy(
            "2025-03-01", [holding], {holding.key: rule}, {"calibrated": 100}, 1.01
        )
        self.assertEqual(uncertain["level"], "assignment-uncertain")

    def test_exact_quotes_receive_the_exact_label_without_model_validation(self) -> None:
        holding = InstrumentHolding("QQQ", "put", 20)
        result = self.calibration.pricing_accuracy(
            "2025-03-01",
            [holding],
            {holding.key: OptionRule("put", target_dte=45, roll_dte=21)},
            {"exact": 250, "missing": 0},
        )
        self.assertEqual(result["label"], "Exact historical quotes")

    def test_validation_reports_all_ninety_grid_cells_plus_default_mix(self) -> None:
        self.assertIsNone(self.calibration.uncertainty_pct())
        report = self.calibration.validate()
        self.assertEqual(report["requiredPortfolios"], 91)
        self.assertEqual(report["missingPortfolios"], 91)
        self.assertEqual(report["badge"], "Insufficient evidence")
        self.assertTrue(report["strictEveryPortfolioGate"])

    def test_sync_stops_at_the_thirty_credit_reserve(self) -> None:
        self.exact.available = True
        self.store.record_quota("test", 1, 30, 100, None)
        result = self.calibration.sync(max_symbol_days=1)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(self.exact.chain_calls, 0)

    def test_sync_never_starts_a_batch_that_would_cross_seventy_daily_credits(self) -> None:
        self.exact.available = True
        self.store.record_quota("test", 1, 100, 100, None)
        self.store.save_setting(
            DAILY_BUDGET_SETTING,
            {"date": date.today().isoformat(), "consumed": 60},
        )
        result = self.calibration.sync(max_symbol_days=1)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(self.exact.chain_calls, 0)
        self.assertEqual(result["quota"]["remaining"], 100)

    def test_market_data_purge_clears_validation_and_in_process_surface(self) -> None:
        self.vault.save_option_quotes("marketdata", surface_rows("2025-01-02", 0.20))
        calibrated = self.calibration.estimate(
            "SPY", "2025-01-08", "call", 100.0, 534, 100.0, 0.35
        )
        self.assertEqual(calibrated.source, "calibrated")
        self.store.save_setting(VALIDATION_SETTING, {"status": "passed"})
        self.vault.purge("marketdata")
        self.store.purge_marketdata_metadata()
        self.calibration.invalidate()
        after = self.calibration.estimate(
            "SPY", "2025-01-08", "call", 100.0, 534, 100.0, 0.35
        )
        self.assertEqual(after.source, "uncalibrated")
        self.assertIsNone(self.store.get_setting(VALIDATION_SETTING))


if __name__ == "__main__":
    unittest.main()
