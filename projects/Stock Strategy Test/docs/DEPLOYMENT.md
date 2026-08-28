# Long-Term Stock Allocation Lab Deployment

Last updated: 2026-08-28

This is the production runbook for `https://strategy.nsyprojects.com/` on the always-on NSY Mac.

## Production Shape

```text
public browser (no login)
-> strategy.nsyprojects.com
-> Cloudflare Tunnel
-> 127.0.0.1:8790
-> PM2: nsy-stock-strategy
-> Python app + DuckDB vault + SQLite metadata
```

The service binds only to localhost. `STOCK_STRATEGY_PUBLIC_MODE=1` opens the simulator, search, status, and unguessable job-polling routes without login. Credential changes, CSV imports, provider collection, saved-run listings, and licensed-data controls return `403`. Public modeled runs reuse retained exact option evidence read-only and cannot trigger Market Data downloads. Provider credentials, market history, quota records, saved runs, logs, Cloudflare credentials, and the private PM2 file remain on the deployment machine.

## 1. Install

```bash
cd "projects/Stock Strategy Test"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
.venv/bin/python scripts/deploy_preflight.py
```

## 2. Configure PM2

```bash
cp ops/pm2-stock-strategy.example.cjs ops/pm2-stock-strategy.config.cjs
mkdir -p ops/logs
```

Edit the ignored config:

- Point `repoRoot` at this checkout.
- Put `STOCK_STRATEGY_DATA_DIR` on persistent writable storage.
- Set `STOCK_STRATEGY_PUBLIC_MODE=1` and keep the per-visitor public run limit enabled.
- Optionally provide `TIINGO_API_TOKEN` on the host for transient real-share history. Without it, the public app automatically uses built-in demo data.
- Do not expose a Market Data token in public mode. Retained option records are read-only and exact-option downloads stay disabled.
- Keep `STOCK_STRATEGY_PUBLIC_ORIGIN=https://strategy.nsyprojects.com`.

Start and persist it:

```bash
pm2 start ops/pm2-stock-strategy.config.cjs
pm2 save
pm2 status nsy-stock-strategy
curl -fsS http://127.0.0.1:8790/api/health
```

Expected health payload: `{"status":"ok","app":"long-term-stock-allocation-lab","publicMode":true}`.

## 3. Add the Cloudflare Route

Insert before the tunnel's final catch-all, preserving all existing hostnames:

```yaml
ingress:
  - hostname: strategy.nsyprojects.com
    service: http://127.0.0.1:8790
  - service: http_status:404
```

Restart the existing tunnel. Confirm the page opens without login, a demo backtest completes, and owner-only routes such as `POST /api/settings/tiingo-token` return `403`.

## 4. Controlled Real-Data Smoke Test

Real smoke tests consume provider allowance and are intentionally not part of automated tests. Public production must not trigger Market Data collection. If a host Tiingo token is configured, run one modest share-only Free automatic test and confirm the UI reports transient server share data. Otherwise verify Built-in demo mode only.

Owner-only provider synchronization should be performed from a separate local/private maintenance workflow, never through the public hostname.

## Collector Operation

The in-process scheduler checks every 30 seconds and runs once after 10:00 AM America/New_York on weekdays. It appends the newest available session for all active favorites, then uses remaining allowance to backfill oldest accessible dates. Writes and collection manifests are idempotent. Provider 429 responses stop the current sync; the next scheduled or manual run resumes from stored manifests.

The collector reserves 30 credits for interactive work. Adding favorites is refused when profile estimates exceed the 70-credit background budget. Estimates are guardrails, not guarantees; the collector also reads exact `X-Api-Ratelimit-*` response headers and stops when the reported remaining value reaches the reserve.

## Updating

```bash
git pull --ff-only
cd "projects/Stock Strategy Test"
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
.venv/bin/python scripts/deploy_preflight.py
pm2 restart nsy-stock-strategy --update-env
curl -fsS http://127.0.0.1:8790/api/health
```

## Licensing and Deletion Procedure

Market Data's personal/self-service license does not authorize raw-data redistribution. The app therefore exports only derived backtest results and the calculated trade ledger. Never add raw stock/chain download endpoints or serve the DuckDB file.

If the Market Data subscription or account ends:

1. Open **My Data Library → Data-license and deletion controls**.
2. Select **Delete downloaded Market Data** and confirm.
3. Confirm My Data Library reports zero downloaded history.
4. On the host, stop the service and verify/remove any backups or optional raw-response directories containing provider records.
5. Start the app again only with fixture mode or a valid continuing subscription.

This deletion preserves application code, built-in fixtures, saved strategies, and derived results. Review the current [Market Data terms](https://www.marketdata.app/terms/) with the account owner.

## Recovery

```bash
pm2 logs nsy-stock-strategy --lines 100
pm2 status nsy-stock-strategy
.venv/bin/python scripts/deploy_preflight.py
```

- Real data unavailable: verify `MARKETDATA_API_TOKEN` is visible to PM2 and restart with `--update-env`.
- Collector paused at reserve: expected; wait for provider reset or reduce/pause favorites.
- Partial coverage: inspect the favorite's coverage and collector message; do not treat missing dates as complete.
- Split rejection: choose a period that does not cross the adjusting split or wait for a future corporate-action model.
- Database lock or disk error: stop PM2, verify the persistent directory is writable and has free space, then restart. Do not delete the vault as a first response.

## Checklist

- [ ] Fixture test suite passes without a provider token
- [ ] Preflight finds DuckDB and writable persistent storage
- [ ] Private PM2 config enables public mode and a per-visitor run limit
- [ ] Backend listens only on `127.0.0.1:8790`
- [ ] Cloudflare hostname routes through the existing tunnel
- [ ] Public page and demo backtest work without login
- [ ] Credential, import, collection, saved-run listing, and purge routes return `403`
- [ ] Public modeled tests cannot download new exact-option records
- [ ] Data directory, secrets, private ops config, and logs are ignored by Git
- [ ] Account owner understands the provider-deletion obligation
