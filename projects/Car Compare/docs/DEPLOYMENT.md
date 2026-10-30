# Car Compare Website Deployment

Before deploying the October 2026 changes, read [Verified Market Migration](VERIFIED_MARKET_MIGRATION.md). It records the new pricing/cache contract and outstanding live release checks; do not treat the historical validation below as fresh evidence.

Last updated: 2026-10-29 (local migration; not released)

## Current Release Hold

Do not run the production restart steps below for this migration yet. The October 29 full-job smoke checks encountered Visor rate limiting and no verified individual browser rows. The twenty-query live comparison and live fallback acceptance gates remain incomplete. Local offline tests are not evidence of marketplace reachability.

All workers on one host must use the same `CAR_COMPARE_REQUEST_BUDGET_DB` path (default `/tmp/car-compare-budget-<uid>/budget.sqlite3`). It coordinates at most two operations per source and shared Retry-After cooldowns across processes. Multiple hosts do not share this local limiter: use one collection host until a distributed coordinator exists. Preserve the three-day cache directory, but do not relabel old evidence as revision 3.

This is the canonical clean-install guide for deploying Car Compare from GitHub to the always-awake Mac that serves `https://carcompare.nsyprojects.com/`. For detailed browser recovery and evidence files, continue with [ALWAYS_AWAKE_HANDOFF.md](ALWAYS_AWAKE_HANDOFF.md).

## Production Shape

```text
authenticated browser
-> https://carcompare.nsyprojects.com
-> Cloudflare Tunnel
-> http://127.0.0.1:8787
-> PM2: python3 app.py
-> SQLite cache + Playwright + host Chrome + local Codex CLI
```

- PM2 keeps only the Python backend running.
- Playwright and regular-Chrome workers start only during an active collection.
- Codex runs on the deployment Mac. Website visitors do not install Codex or supply their own Codex account.
- The app reuses the signed session issued by `https://dem.nsyprojects.com/login`.
- Autotrader and Edmunds are general marketplace sources. Porsche queries also use official Porsche Finder.
- Marketplace rows, Visor facet snapshots, collection reviews, and generation research expire after at most three days.
- Deterministic marketplace audits finalize collection by default. The separate generation-impact researcher remains automatic.
- There is no recurring five-minute Codex task.

## GitHub Versus Machine-Local State

GitHub carries the app, tests, schemas, project skills, safe templates, and documentation. Do not commit:

- Codex login or `~/.codex/`
- Chrome/Playwright profiles or browser cookies
- `CAR_COMPARE_SESSION_SECRET` or other credentials
- the private PM2 config
- Cloudflare tunnel credentials or config
- `data/cache/`, collector jobs, generation jobs, or logs

The root `.gitignore` already excludes the standard local paths. Keep the deploy Mac's cache directory on persistent storage; deleting it removes the three-day reuse benefit.

## 1. Clone And Install

Install Git, Python 3, Node.js 20 or newer, Google Chrome, PM2, Cloudflare Tunnel, and ChatGPT or Codex Desktop. Homebrew can provide the command-line dependencies:

```bash
brew install git python node cloudflared
npm install --global pm2
```

Then clone the project:

```bash
git clone https://github.com/naivee2000/nsy-projects-web.git
cd "nsy-projects-web/projects/Car Compare"
npm install
npm exec playwright install chromium
./scripts/install_project_skills.sh
```

The Python backend currently uses the standard library and does not require a virtual environment. Re-run `npm install` after pulling a changed `package-lock.json`.

## 2. Prepare Codex And Chrome

Use the same logged-in macOS user for Codex Desktop, Chrome automation, PM2, and the backend.

1. Open ChatGPT or Codex Desktop and log in to Codex.
2. In Codex Desktop, install the Chrome plugin and complete its Chrome extension setup. The automatic AppleScript path does not require the extension, but supervised `Repair Missing Source` recovery and the complete desktop preflight do.
3. Confirm the CLI path and login:

   ```bash
   "/Applications/ChatGPT.app/Contents/Resources/codex" --version
   "/Applications/ChatGPT.app/Contents/Resources/codex" login status
   ```

   If the standalone Codex app is installed instead, use `/Applications/Codex.app/Contents/Resources/codex`.
4. Open Google Chrome and enable `View > Developer > Allow JavaScript from Apple Events`.
5. Approve the macOS Automation prompt when the terminal or service user first controls Chrome.
6. Keep the macOS graphical user logged in. The display may sleep, but Chrome automation cannot run from a logged-out session.

Run the no-model preflight:

```bash
python3 scripts/deploy_preflight.py --smoke-browser --desktop-fallback
```

This checks Codex login, native web-search support, project skills and schemas, Node/Playwright, the persistent browser, Desktop/Chrome integration, and a minimized host-Chrome capture. Add `--smoke-codex` only when a small Codex usage charge is acceptable:

```bash
python3 scripts/deploy_preflight.py --smoke-codex --smoke-browser --desktop-fallback
```

## 3. Configure The Private PM2 Service

Create a machine-local config whose filename is ignored by Git:

```bash
cp ops/pm2-car-compare.example.cjs ops/pm2-car-compare.config.cjs
mkdir -p ops/logs
```

Edit `ops/pm2-car-compare.config.cjs` and set:

- `repoRoot` to the checkout root, not the `Car Compare` folder.
- `script` to the host's `python3` path from `command -v python3`.
- `CODEX_BIN` to the installed bundled or standalone Codex executable.
- `CAR_COMPARE_AUTH_USERNAME` to the same username configured by the NSY login service.
- `CAR_COMPARE_SESSION_SECRET` to the exact same long secret used by the NSY login service.
- `CAR_COMPARE_PUBLIC_ORIGIN` to `https://carcompare.nsyprojects.com`.
- `CAR_COMPARE_CACHE_DIR` to a persistent writable directory.

Keep `CAR_COMPARE_BROWSER_CDP_URL: ""` for the default app-managed browser.
PM2 merges environment settings on restart, so deleting this key from the file
does not clear an old override such as `http://127.0.0.1:9222`. Set it explicitly
to an empty string, restart using the config with `--update-env`, verify
`/api/setup` and `scripts/deploy_preflight.py --smoke-browser`, then run `pm2 save`.

Keep these production values:

```text
CAR_COMPARE_CACHE_ENABLED=1
CAR_COMPARE_RECENT_CACHE_TTL_SECONDS=259200
CAR_COMPARE_OLDER_CACHE_TTL_SECONDS=259200
CAR_COMPARE_GENERATION_CACHE_TTL_SECONDS=259200
CAR_COMPARE_REVIEW_CACHE_TTL_SECONDS=259200
CAR_COMPARE_CODEX_COLLECTION_REVIEW=0
CAR_COMPARE_CODEX_COLLECTION_REASONING_EFFORT=low
CAR_COMPARE_CODEX_GENERATION_REASONING_EFFORT=high
CAR_COMPARE_BACKGROUND_MODE=1
CAR_COMPARE_HOST_CHROME_FALLBACK=1
CAR_COMPARE_CODEX_SEARCH_FALLBACK=1
```

The four TTL values are hard-capped at 259,200 seconds, or three days, even if a larger value is configured.

Start and persist the backend:

```bash
pm2 start ops/pm2-car-compare.config.cjs
pm2 save
pm2 startup
pm2 status nsy-car-compare
```

Run the command printed by `pm2 startup` if macOS requests it. Then verify the local health endpoint:

```bash
curl -fsS http://127.0.0.1:8787/api/health
```

Expected response:

```json
{"status":"ok","app":"car-compare"}
```

## 4. Add The Cloudflare Route

Add this hostname before the tunnel configuration's final catch-all rule. Preserve every existing hostname:

```yaml
ingress:
  - hostname: carcompare.nsyprojects.com
    service: http://127.0.0.1:8787
  - service: http_status:404
```

The live tunnel configuration and credentials stay on the deployment Mac. Restart the existing tunnel process after editing it, then confirm that unauthenticated access redirects to the NSY login page and an authenticated session reaches Car Compare.

Do not route port 8787 directly to the internet. The backend should remain bound to `127.0.0.1` and be reached through the authenticated hostname.

## 5. Verify A Real Collection

1. Sign in through `https://dem.nsyprojects.com/login`.
2. Open `https://carcompare.nsyprojects.com/`.
3. Run a normal non-Porsche query and confirm Autotrader, Edmunds, and Visor appear truthfully as accepted, cached, partial, or blocked.
4. Run a Porsche query and confirm Porsche Finder appears in the collection plan and source evidence.
5. Repeat the same query. Fresh complete source-year cache entries should skip those sources for three days, even when a source has fewer rows than the desired sample target.
6. Confirm `Repair Missing Source` appears only when automatic Playwright and host-Chrome recovery could not produce an authoritative audit.

Run the portable accuracy gate before the live source checks:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/benchmark_search_accuracy.py
node scripts/car_compare_browser_mcp.mjs --self-test
```

The benchmark must remain at or above 88% and currently verifies 60/60 labels. See [PERFORMANCE_ACCURACY_BENCHMARK.md](PERFORMANCE_ACCURACY_BENCHMARK.md) for the seven browser runs and measured runtime reduction.

Porsche Finder is only scheduled for Porsche. If existing Autotrader, Edmunds, and Visor cache entries are fresh, adding or repairing Porsche Finder should collect only that missing source instead of reopening every marketplace.

Per-job evidence is under `data/collector_jobs/<job-id>/`. The cache database is `<CAR_COMPARE_CACHE_DIR>/collector_cache.sqlite3`.

## Updating The Deployment

From the repo root:

```bash
git pull --ff-only
cd "projects/Car Compare"
npm install
npm exec playwright install chromium
./scripts/install_project_skills.sh
python3 scripts/deploy_preflight.py --smoke-browser
pm2 restart nsy-car-compare --update-env
curl -fsS http://127.0.0.1:8787/api/health
```

If `git pull --ff-only` reports local changes, inspect `git status` before doing anything destructive. Private runtime config, caches, logs, and credentials should already be ignored.

## Operations And Recovery

```bash
pm2 status nsy-car-compare
pm2 logs nsy-car-compare --lines 100
python3 scripts/deploy_preflight.py --smoke-browser --desktop-fallback
```

- `Codex login` missing: run `codex login` as the same macOS user that runs PM2.
- Browser packages missing: rerun `npm install` and `npm exec playwright install chromium`.
- Apple Events failure: re-enable Chrome's developer setting and approve macOS Automation access.
- Source access refusal: leave it truthfully unavailable or use an official API/account; do not bypass CAPTCHA or access controls.
- Manual repair shown: use `Repair Missing Source` only for the source named by the app, then inspect the imported audit.
- Cache unexpectedly recollects: confirm `CAR_COMPARE_CACHE_DIR` is unchanged, writable, and persistent, and that the prior source-year audit completed successfully.

See [ALWAYS_AWAKE_HANDOFF.md](ALWAYS_AWAKE_HANDOFF.md) for detailed audit filenames, fallback behavior, and browser troubleshooting.

## Deployment Checklist

- [ ] Latest GitHub checkout is on the deployment Mac
- [ ] Node packages and Playwright Chromium are installed
- [ ] Project skills are installed into the deployment user's `CODEX_HOME`
- [ ] Codex login and `--search` support pass preflight
- [ ] Google Chrome and Apple Events JavaScript access are ready
- [ ] Private PM2 config uses the shared NSY username and session secret
- [ ] Cache directory is persistent and all TTLs are 259200 seconds
- [ ] `CAR_COMPARE_CODEX_COLLECTION_REVIEW=0` is explicit unless a deliberate paid review experiment is being run
- [ ] Unit tests, deterministic accuracy benchmark, and browser worker self-test pass
- [ ] PM2 starts at login and local `/api/health` is healthy
- [ ] Cloudflare routes the hostname to `127.0.0.1:8787`
- [ ] Unauthenticated users redirect to NSY login
- [ ] Authenticated non-Porsche and Porsche collections complete truthfully
- [ ] A repeated query reuses fresh cache rather than recollecting every source
- [ ] No recurring Codex polling task is installed
