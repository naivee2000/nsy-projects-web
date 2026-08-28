# Codex Context: Stock & Options Strategy Lab

This folder is a self-contained private research app under `projects/Stock Strategy Test`.

## Product Boundary

- Beginner-first allocations among shares, long calls, long puts, cash-secured short puts, and cash across verified U.S. stocks/ETFs.
- Fixture mode must always work without a token.
- Market Data is a replaceable provider and must remain vault-first and quota-aware.
- No raw licensed-data export or unauthenticated data routes.
- Cash-secured short puts are the only short option. Rational early assignment and an unassigned comparison are modeled; margin, brokerage execution, and public advice remain excluded.
- Historical option runs crossing a detected adjusting split are rejected.

## Important Files

- `app.py`: HTTP routes, shared-auth gate, static serving, and runtime wiring.
- `stock_strategy_lab/models.py`: strategy/data/result contracts.
- `stock_strategy_lab/engine.py`: deterministic simulation and allocation sweeps.
- `stock_strategy_lab/providers.py`: fixtures and Market Data adapter.
- `stock_strategy_lab/calibration.py`: SPY/QQQ exact-first hierarchy, local eSSVI calibration, credit-safe sync, strict held-out badge gate.
- `stock_strategy_lab/modeled.py`: calibrated hybrid pricing and adaptive American solver.
- `stock_strategy_lab/unified.py`: multi-instrument portfolio accounting, exercise floors, rolling, and assignment scenarios.
- `stock_strategy_lab/storage.py`: DuckDB vault and SQLite app store.
- `stock_strategy_lab/credentials.py`: owner-only machine-local Market Data token storage used by the local UI.
- `stock_strategy_lab/collector.py`: quota-aware T+1 favorite collection and scheduler.
- `static/`: beginner interface.
- `tests/`: fixture-only acceptance coverage.
- `docs/DEPLOYMENT.md`: deployment and licensed-data deletion runbook.

## Verification

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
.venv/bin/python -m py_compile app.py stock_strategy_lab/*.py
node --check static/app.js
.venv/bin/python scripts/deploy_preflight.py
```

Keep `data/`, credentials, logs, private PM2/Cloudflare files, raw provider responses, and virtual environments out of Git. Production is `nsy-stock-strategy` on `127.0.0.1:8790` behind `strategy.nsyprojects.com`, reusing the NSY session.
