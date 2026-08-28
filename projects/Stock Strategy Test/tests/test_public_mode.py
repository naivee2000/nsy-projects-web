from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import app
from stock_strategy_lab.modeled import FreeModeledProvider
from stock_strategy_lab.models import OptionRule


class RecordingCalibration:
    def __init__(self) -> None:
        self.download_values: list[bool] = []

    def exact_chain(self, symbol, market_date, rule, download=True):  # type: ignore[no-untyped-def]
        self.download_values.append(bool(download))
        return []


class PublicModeTests(unittest.TestCase):
    def test_public_route_allowlist_keeps_owner_controls_closed(self) -> None:
        self.assertTrue(app.public_route_allowed("GET", "/"))
        self.assertTrue(app.public_route_allowed("GET", "/static/app.js"))
        self.assertTrue(app.public_route_allowed("GET", "/api/portfolio/search"))
        self.assertTrue(app.public_route_allowed("GET", "/api/backtests/unguessable-id"))
        self.assertTrue(app.public_route_allowed("POST", "/api/portfolio/backtests"))
        for method, path in (
            ("POST", "/api/settings/tiingo-token"),
            ("POST", "/api/settings/marketdata-token"),
            ("POST", "/api/data/import-stock-csv"),
            ("POST", "/api/vault/purge"),
            ("GET", "/api/runs"),
            ("DELETE", "/api/runs/example"),
        ):
            self.assertFalse(app.public_route_allowed(method, path), path)

    def test_public_backtest_limit_resets_after_window(self) -> None:
        limiter = app.PublicBacktestLimiter(limit=2, window_seconds=10)
        self.assertTrue(limiter.allow("visitor", now=1))
        self.assertTrue(limiter.allow("visitor", now=2))
        self.assertFalse(limiter.allow("visitor", now=3))
        self.assertTrue(limiter.allow("visitor", now=12))

    def test_public_mode_can_reuse_exact_evidence_without_downloading(self) -> None:
        calibration = RecordingCalibration()
        with tempfile.TemporaryDirectory(prefix="stock-public-mode-") as directory:
            provider = FreeModeledProvider(
                object(),
                Path(directory),
                fred=object(),
                calibration=calibration,
                allow_exact_downloads=False,
            )
            provider._bar_dates["SPY"] = ["2025-01-02"]
            provider._bar_prices["SPY"] = [100.0]
            with patch.object(provider, "_quote", return_value=object()):
                provider.option_chain("SPY", "2025-01-02", OptionRule("call"))
        self.assertEqual(calibration.download_values, [False])


if __name__ == "__main__":
    unittest.main()
