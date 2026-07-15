# Always-Awake Mac Handoff

This guide moves Car Compare to the Mac that stays awake. The current design performs marketplace collection without a user click and without a recurring Codex monitor.

## Zero-Click Flow

```text
Collect & Research starts
-> fresh verified SQLite cache rows load
-> Visor public facets run
-> the project Playwright profile opens Autotrader and Edmunds range pages concurrently in a headless browser
-> combined year coverage is calculated across cache, facets, and both marketplaces
-> only genuinely sparse years enter bounded follow-up queues
-> a blocked or empty source is retried once in a minimized regular-Chrome worker window
-> Chrome scrolls and clicks recognized result pagination controls
-> rendered text returns directly to Car Compare
-> if the host network still refuses an official source page, Codex native web search opens only sparse indexed year pages in small parallel batches
-> Codex returns verbatim listing blocks under a fixed schema
-> Car Compare parses, filters, and audits rows deterministically
-> Codex reviews the completed coverage and generation forecast
-> the minimized Chrome worker window closes
```

The host-Chrome retry is event driven. It starts only inside an active collection job, immediately minimizes its private window, restores the app that was previously focused, performs no model call, and exits when that source finishes or shows an access refusal. Host-Chrome retries are serialized so two worker windows cannot compete for focus. If the refusal leaves a source empty, the same active job can invoke `codex --search` once. That stage spends Codex usage, but it is never run while the app is idle. There is no five-minute task.

`scripts/chrome_host_capture.applescript` is the browser bridge. `car_compare/sources/chrome_host.py` restricts it to configured Autotrader, Edmunds, or Porsche Finder HTTPS hosts. Porsche Finder is enabled only for Porsche queries and carries an explicit nationwide radius in its planned URL. The bridge reads public rendered page text only. It does not read cookies, local storage, passwords, history, or profile files.

The indexed-source stage is defined by `car_compare/web_search_capture_schema.json`. Codex may return only official Edmunds page URLs and verbatim page text. The app rejects another host, an out-of-range year, empty evidence, and every row the deterministic vehicle parser cannot recover. Search prose alone never becomes a listing.

The older `Open Codex + Chrome` lease remains a manual recovery path only when host Chrome automation is unavailable. A completed automatic host-Chrome attempt does not ask the operator to click the same blocked source again.

## Persistent Cache

Set `CAR_COMPARE_CACHE_DIR` to a directory that survives service restarts. The default is `data/cache` inside the project, which is suitable for the always-awake Mac. A container or hosted Linux service should mount a persistent volume at the configured location.

```bash
export CAR_COMPARE_CACHE_DIR="/persistent/car-compare-cache"
export CAR_COMPARE_CACHE_ENABLED=1
export CAR_COMPARE_RECENT_CACHE_TTL_SECONDS=259200
export CAR_COMPARE_OLDER_CACHE_TTL_SECONDS=259200
export CAR_COMPARE_GENERATION_CACHE_TTL_SECONDS=259200
export CAR_COMPARE_REVIEW_CACHE_TTL_SECONDS=259200
export CAR_COMPARE_MARKETPLACE_CONCURRENCY=2
export CAR_COMPARE_CODEX_SEARCH_WORKERS=3
export CAR_COMPARE_CODEX_SEARCH_BATCH_SIZE=5
export CAR_COMPARE_BACKGROUND_MODE=1
```

The SQLite file is `collector_cache.sqlite3`. WAL mode and atomic upserts support concurrent job threads. Cache keys isolate make, model, trim scope, source, and year. Every row is deterministically revalidated when read. Marketplace rows, Visor facet snapshots, validated collection reviews, and generation research can remain fresh for at most three days. Larger environment values are clamped to that limit.

## Requirements

- macOS with a logged-in graphical user session
- Google Chrome installed in `/Applications`
- Chrome allowed to run JavaScript from Apple Events
- Node.js and the project npm packages
- Playwright Chromium
- Codex CLI installed and logged in for research/review
- Codex CLI version that exposes the native `--search` option
- ChatGPT or Codex Desktop open when using its bundled Codex CLI

The Chrome extension is useful for supervised recovery but is not required for the automatic AppleScript capture itself.

## Install

Copy or clone the complete `Car Compare` folder. Keep these paths together:

```text
app.py
car_compare/
docs/
ops/
scripts/
skills/
skill_backups/
static/
package.json
package-lock.json
```

Install dependencies:

```bash
cd "/path/to/Car Compare"
npm install
npm exec playwright install chromium
scripts/install_project_skills.sh
```

Verify the Codex account used by the backend:

```bash
codex --version
codex login status
```

When `codex` is not on `PATH`, set the bundled executable that exists on the Mac:

```bash
export CODEX_BIN="/Applications/ChatGPT.app/Contents/Resources/codex"
```

or:

```bash
export CODEX_BIN="/Applications/Codex.app/Contents/Resources/codex"
```

## Enable Chrome Automation

1. Open Google Chrome.
2. In the menu bar, open `View > Developer`.
3. Enable `Allow JavaScript from Apple Events`.
4. Keep Chrome available under the same macOS user that runs Car Compare.
5. The first Apple Events request may cause a macOS Automation permission prompt. Allow the terminal or service host to control Google Chrome.

Run the complete preflight:

```bash
python3 scripts/deploy_preflight.py --smoke-browser --desktop-fallback
```

This does not invoke a model. It checks:

- Codex CLI and login
- native Codex live web search
- project skills and schemas
- Node.js, Playwright, and the browser worker
- ChatGPT/Codex Desktop installation
- regular Google Chrome
- optional Chrome plugin and extension
- the project AppleScript worker
- Apple Events JavaScript capture using a minimized temporary `example.com` window
- the headless persistent Playwright profile and its reported background state

Add `--smoke-codex` only when a small Codex usage charge is acceptable.

## PM2 Service

Create the local PM2 configuration:

```bash
cd "/path/to/Car Compare"
cp ops/pm2-car-compare.example.cjs ops/pm2-car-compare.cjs
```

Edit `repoRoot`, `CODEX_BIN`, authentication values, and `CAR_COMPARE_PUBLIC_ORIGIN`. Start and persist it:

```bash
mkdir -p ops/logs
pm2 start ops/pm2-car-compare.cjs
pm2 save
pm2 startup
```

Run the command printed by `pm2 startup` if macOS requests it. Verify:

```bash
pm2 status nsy-car-compare
curl -fsS http://127.0.0.1:8787/api/health
```

Expected response:

```json
{"status":"ok","app":"car-compare"}
```

The Cloudflare tunnel for `carcompare.nsyprojects.com` should route to `http://127.0.0.1:8787` before its final catch-all rule.

## Power Settings

In macOS System Settings:

- add ChatGPT/Codex Desktop and the PM2 launch service to the login session
- prevent system sleep while connected to power
- allow the display to sleep
- keep network access available while the display is off

Inspect settings without changing them:

```bash
pmset -g custom
```

Chrome automation requires the macOS user to remain logged in. A locked screen is normally fine; a logged-out graphical session is not.

## Verification Run

Start a collection in the app and wait for it to finish. The returned job should show:

```json
{
  "fallback": null,
  "result": {
    "sources": [
      {
        "source": "autotrader_browser",
        "browser_mode": "system_chrome_applescript",
        "background_mode": true,
        "host_chrome_attempted": true
      },
      {
        "source": "edmunds_browser",
        "browser_mode": "codex_web_search",
        "search_verified": true,
        "deterministic_verified": true
      }
    ]
  }
}
```

Inspect a job directly:

```bash
curl -s http://127.0.0.1:8787/api/collect/<job-id> | python3 -m json.tool
```

Per-job evidence is stored under:

```text
data/collector_jobs/<job-id>/collector_result.json
data/collector_jobs/<job-id>/browser_capture_autotrader_browser.json
data/collector_jobs/<job-id>/browser_capture_edmunds_browser.json
data/collector_jobs/<job-id>/host_chrome_autotrader_browser_*.json
data/collector_jobs/<job-id>/host_chrome_edmunds_browser_*.json
data/collector_jobs/<job-id>/codex_web_search_edmunds_browser.json
data/collector_jobs/<job-id>/codex_web_search_edmunds_browser.stderr.log
data/collector_jobs/<job-id>/codex_stdout.log
data/collector_jobs/<job-id>/codex_stderr.log
```

## Access Refusals

Zero-click automation and marketplace reachability are separate concerns. A host-network refusal first opens the circuit breaker for direct browser requests. The app may then use native Codex web search to read indexed official sale pages without rotating the host identity. If neither direct rendering nor the official indexed page exposes complete listing blocks, that source remains unavailable.

Examples recorded as a truthful blocked source:

- `Autotrader - page unavailable` with an incident number
- `403 - Access Denied | Edmunds` with an IP address and reference ID
- CAPTCHA, human verification, login wall, or security interstitial

Do not add proxy rotation, fingerprint spoofing, CAPTCHA solving, or private endpoint scraping. Confirm that the host's normal network can open the public result page in regular Chrome. If the whole domain is refused, use a permitted network, an official API/account, or leave that source marked unavailable.

## Runtime Controls

Background mode is enabled by default and should remain explicit in PM2:

```bash
export CAR_COMPARE_BACKGROUND_MODE=1
```

In this mode, Playwright runs headlessly. The macOS regular-Chrome fallback still needs a logged-in graphical session, but its private window is minimized immediately and the user's previously focused app is restored. Chrome can still appear as a running process in the Dock or Activity Monitor. Set `CAR_COMPARE_BACKGROUND_MODE=0` only while diagnosing a browser failure. An externally managed `CAR_COMPARE_BROWSER_CDP_URL` cannot be guaranteed hidden and is reported as non-background.

Host Chrome retry is enabled by default on macOS. Disable it for diagnosis with:

```bash
export CAR_COMPARE_HOST_CHROME_FALLBACK=0
```

Indexed official-page recovery is enabled by default when Codex is authenticated. Disable it for cost control or diagnosis with:

```bash
export CAR_COMPARE_CODEX_SEARCH_FALLBACK=0
```

When disabled or unavailable, the old short-lived manual lease can still appear. Its duration remains configurable between 300 and 3,600 seconds:

```bash
export CAR_COMPARE_FALLBACK_LEASE_SECONDS=1200
```

No recurring task should poll that queue.

## Recovery

- **Host Chrome missing:** install Google Chrome in `/Applications`.
- **Apple Events error:** enable `View > Developer > Allow JavaScript from Apple Events`, then allow the macOS Automation permission.
- **Chrome worker window remains open or visible:** inspect PM2 logs and rerun preflight. The script minimizes and closes only the window it created, including on errors.
- **Marketplace access refusal:** verify the URL manually on the same network. Do not bypass the refusal.
- **Indexed recovery has no rows:** inspect the saved Codex search JSON and stderr log. The official page may not be indexed or may expose too little complete evidence.
- **Codex login missing:** run `codex login` as the backend macOS user.
- **Browser packages missing:** run `npm install` and `npm exec playwright install chromium`.
- **Backend restart:** PM2 restores the service. A new collection starts a fresh event-driven capture.
- **Manual fallback shown:** host Chrome was unavailable or failed before producing an authoritative audit. Inspect the source audit and preflight output.

## Portable Backup

The zero-click worker is ordinary project code and moves with the folder:

```text
car_compare/sources/chrome_host.py
scripts/chrome_host_capture.applescript
```

The optional supervised Codex workflow remains backed up at:

```text
skills/collect-car-marketplaces/
skill_backups/collect-car-marketplaces.zip
```

Rebuild that archive after changing the skill:

```bash
rm -f skill_backups/collect-car-marketplaces.zip
(cd skills && zip -qr ../skill_backups/collect-car-marketplaces.zip collect-car-marketplaces)
```

## Handoff Checklist

- [ ] Complete project folder copied or cloned
- [ ] Node.js packages and Playwright Chromium installed
- [ ] Codex CLI logged in as the backend user
- [ ] `codex --help` lists `--search`
- [ ] ChatGPT/Codex Desktop open in the login session
- [ ] Google Chrome installed
- [ ] `Allow JavaScript from Apple Events` enabled
- [ ] macOS Automation permission granted
- [ ] `CAR_COMPARE_BACKGROUND_MODE=1` configured in PM2
- [ ] `deploy_preflight.py --smoke-browser --desktop-fallback` passes
- [ ] PM2 service saved and healthy
- [ ] Cloudflare route reaches local port 8787
- [ ] No recurring five-minute task configured
- [ ] One unattended job produces a `system_chrome_applescript` audit
- [ ] A network-blocked official page produces a `codex_web_search` audit or remains truthfully unavailable
