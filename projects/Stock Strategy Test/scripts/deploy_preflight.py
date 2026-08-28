#!/usr/bin/env python3
"""Check the local runtime without consuming Market Data credits."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from stock_strategy_lab.models import StrategyDefinition  # noqa: E402
from stock_strategy_lab.providers import FixtureProvider  # noqa: E402
from stock_strategy_lab.engine import BacktestEngine  # noqa: E402
from stock_strategy_lab.storage import AppStore, MarketVault  # noqa: E402


def report(name: str, okay: bool, detail: str) -> bool:
    print(f"{'OK' if okay else 'MISSING':7} {name}: {detail}")
    return okay


def main() -> int:
    passed = True
    passed &= report("Python", sys.version_info >= (3, 11), sys.version.split()[0])
    with tempfile.TemporaryDirectory(prefix="stock-strategy-preflight-") as directory:
        try:
            vault = MarketVault(Path(directory))
            store = AppStore(Path(directory))
            storage_ok = vault.coverage("fixture", "SPY")["stockDays"] == 0 and not store.list_favorites()
            storage_detail = "DuckDB and SQLite initialized in a temporary directory"
        except Exception as exc:
            storage_ok = False
            storage_detail = str(exc)
        passed &= report("local storage", storage_ok, storage_detail)

    try:
        strategy = StrategyDefinition("SPY", "2025-01-02", "2025-04-30", stock_pct=60, call_pct=20, put_pct=20)
        result = BacktestEngine().run(strategy, FixtureProvider("wave"))
        fixture_ok = result.status == "complete" and bool(result.daily_equity)
        fixture_detail = f"{result.metrics['tradingSessions']} sessions, ending {result.metrics['endingValue']:.2f}"
    except Exception as exc:
        fixture_ok = False
        fixture_detail = str(exc)
    passed &= report("fixture backtest", fixture_ok, fixture_detail)

    token = os.environ.get("MARKETDATA_API_TOKEN", "").strip()
    report("Market Data token", bool(token), "configured (not called)" if token else "optional; fixture mode remains available")
    data_dir = Path(os.environ.get("STOCK_STRATEGY_DATA_DIR", ROOT / "data")).expanduser()
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        writable = os.access(data_dir, os.W_OK)
    except OSError:
        writable = False
    passed &= report("persistent data path", writable, str(data_dir))
    print(json.dumps({"ready": passed, "providerTokenConfigured": bool(token)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
