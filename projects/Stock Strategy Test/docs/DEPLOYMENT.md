# Stock Strategy Lab Deployment

Last updated: 2026-07-17

This is the production runbook for `https://strategy.nsyprojects.com/` on the always-on NSY Mac.

## Production Shape

```text
authenticated browser
-> strategy.nsyprojects.com
-> Cloudflare Tunnel
-> 127.0.0.1:8790
-> PM2: nsy-stock-strategy
-> Python app + DuckDB vault + SQLite metadata
```

The service binds only to localhost. The app reuses the HMAC session issued by `dem.nsyprojects.com`; only `/api/health` is public. Provider credentials, market history, quota records, saved runs, logs, Cloudflare credentials, and the private PM2 file remain on the deployment machine.

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
- Set `MARKETDATA_API_TOKEN` to the personal account token.
- Put `STOCK_STRATEGY_DATA_DIR` on persistent writable storage.
- Use the same username, HMAC secret, and cookie name as the NSY login service.
- Keep `STOCK_STRATEGY_PUBLIC_ORIGIN=https://strategy.nsyprojects.com`.

Start and persist it:

```bash
pm2 start ops/pm2-stock-strategy.config.cjs
pm2 save
pm2 status nsy-stock-strategy
curl -fsS http://127.0.0.1:8790/api/health
```

Expected health payload: `{"status":"ok","app":"stock-strategy-lab"}`.

## 3. Add the Cloudflare Route

Insert before the tunnel's final catch-all, preserving all existing hostnames:

```yaml
ingress:
  - hostname: strategy.nsyprojects.com
    service: http://127.0.0.1:8790
  - service: http_status:404
```

Restart the existing tunnel. Confirm an unauthenticated page request redirects to NSY login, an unauthenticated API request returns 401, and a signed-in user can open the lab.

## 4. Controlled Real-Data Smoke Test

Real smoke tests consume provider credits and are intentionally not part of automated tests. In the authenticated UI:

1. Add one modest symbol with **Only Contracts Used** or **Balanced Monthly**.
2. Note the displayed credits before sync.
3. Run **Sync safely now** once.
4. Confirm the coverage dates, contract count, and updated remaining-credit header value.
5. Run the same short backtest twice. The second run should reuse vault records and not repeat covered calls.

Do not test `Full` collection first on a large ETF. Historical chains may be billed by returned contract count, and unexpectedly large chains can consume multiple credits.

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
- [ ] Private PM2 config uses the shared NSY session secret
- [ ] Backend listens only on `127.0.0.1:8790`
- [ ] Cloudflare hostname routes through the existing tunnel
- [ ] Public health works and every other surface requires the shared session
- [ ] One disclosed-credit real-data smoke test succeeds
- [ ] Repeated covered backtest does not refetch the same records
- [ ] Data directory, secrets, private ops config, and logs are ignored by Git
- [ ] Account owner understands the provider-deletion obligation
