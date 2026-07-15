# Automatic Codex Collection

The app starts marketplace collection and Codex research from the single `Collect & Research` action.

## How It Works

```text
User enters car query
-> app parses make/model/trim
-> app builds source plan
-> app loads fresh completed source-year cache entries
-> app collects only missing or expired Visor facets
-> app can continue into a local Codex CLI job for website collection when Codex is available
-> Codex calls the project-local browser MCP worker for missing Autotrader and Edmunds coverage
-> Porsche queries also add missing official Porsche Finder coverage
-> the worker flips pages and persists deterministic card/audit JSON beside the job
-> the app accepts browser rows only from that audit
-> if a marketplace is blocked or empty, the app retries once in the host Mac's regular Chrome
-> if the network still refuses an official Edmunds page, native Codex web search captures indexed official listing blocks
-> only a host-automation failure opens the short-lived manual Codex Desktop fallback lease
-> app deduplicates listings and graphs depreciation
```

The bridge is server-side. The website does not talk to a model API directly; it starts a process on the computer running the backend. After deployment, visitors on other computers use that host connection and do not provide their own Codex login.

For sources like Visor, the app can use public market-facet pages directly. These are aggregate observations, not individual VIN/dealer listings. Used-market rows are labeled `visor_public_facets`; new-car age-0 rows are labeled `visor_public_facets_new` with `condition=new`.

If Codex fails after Visor returned usable rows, the job should complete with a partial result and preserve the Visor observations.

## How To Know It Is Running

After you click `Collect & Research`, the Collector panel should move through these states:

- `queued`: the app accepted the job.
- `running: Codex process started (PID ...)`: the local Codex process is alive.
- `running: Codex is still running for ... (PID ...)`: the app is still polling and the child process has not exited.
- `completed`: Codex returned structured JSON and the app will rerun the graph.
- `failed` or `blocked`: Codex exited, timed out, hit a usage limit, or could not access the requested data.

While the job is running, the app checks the Codex process about once per second and the browser polls the app every few seconds. Long website research can still take several minutes, but the elapsed-time/PID line means the app has not frozen.

## Requirements On Another Computer

- Codex installed.
- Codex logged in.
- `codex` available on PATH, or `CODEX_BIN` set to the executable path.
- Node.js 20 or newer.
- The project browser dependencies installed with `npm install`.
- The app running locally on `127.0.0.1`.

Install and test the project-local browser worker:

```bash
npm install
npm exec playwright install chromium
npm run browser:self-test
```

Verify that the worker can launch its persistent browser profile:

```bash
python3 scripts/deploy_preflight.py --smoke-browser
```

The worker owns Playwright's version-matched browser, runs it headlessly by default, and persists its session under `~/.car-compare/browser-profile`. This machine-local path avoids checking browser state into Git and works even when the project path contains spaces. No separate visible Chrome process, debug port, or machine-specific browser path is required. An explicitly configured localhost `CAR_COMPARE_BROWSER_CDP_URL` remains supported as an advanced override, but is reported as non-background because its window state is externally managed.

The collection pass opens missing Autotrader and Edmunds broad year-range pages concurrently in separate pages of one shared browser session. Porsche queries also open missing official Porsche Finder coverage. Concurrent vehicle jobs still wait for the browser lock. A fresh completed source-year set suppresses that source for three days even when its sample is below the preferred row target. After the range pass, the backend merges marketplaces with cache and Visor aggregate support; only sparse missing evidence enters a bounded follow-up queue. Confirmed access walls remain recorded and never trigger identity rotation or CAPTCHA bypasses.

Porsche Finder always receives an explicit nationwide position radius (`-1`) because the site can restore a local radius when position is omitted. It uses `minimum-model-year` / `maximum-model-year`, repeated `category` filters for supported 911 trim scopes, `/details/` card links, and `page` pagination. The app still runs every card through deterministic year/model/trim matching.

For `carcompare.nsyprojects.com`, use `ops/pm2-car-compare.example.cjs`. PM2 runs the backend with `CAR_COMPARE_BACKGROUND_MODE=1`; the backend launches one shared headless persistent-profile browser session with a configurable two-page worker pool. `python3 scripts/deploy_preflight.py --smoke-browser` verifies both a real browser launch and background mode.

On the always-awake Mac, the event-driven regular-Chrome fallback is also background-oriented: it creates a private worker window, minimizes it immediately, restores the previously focused app, and closes the worker when capture finishes. Fallbacks run one at a time to avoid focus races. Chrome must remain installed in a logged-in graphical session with `View > Developer > Allow JavaScript from Apple Events` enabled. The process may remain visible in Dock or Activity Monitor, but no collection page should remain on the desktop. Set `CAR_COMPARE_BACKGROUND_MODE=0` only for temporary diagnosis.

Set `CAR_COMPARE_CACHE_DIR` to a persistent disk. The SQLite cache uses WAL mode and atomic upserts, so it works for the local always-awake Mac and for a Linux deployment with a mounted volume. Marketplace rows, Visor facet snapshots, validated collection reviews, and generation research all have a maximum three-day TTL. Expired rows never satisfy coverage, every listing cache hit is passed through the deterministic matcher again, and an empty attempt cannot replace richer accepted cache data.

The app checks `CODEX_BIN`, `PATH`, official standalone install locations on macOS/Linux/Windows, and these macOS desktop locations. To override discovery manually, use the path that exists on the host:

```bash
export CODEX_BIN="/Applications/ChatGPT.app/Contents/Resources/codex"
```

The standalone Codex desktop fallback is `/Applications/Codex.app/Contents/Resources/codex`.

After moving into the NSY projects repo, a typical run path is:

```bash
cd "/Users/shaoyangni/Desktop/Python Files/nsy-dem-app-handoff/projects/Car Compare"
python3 app.py --host 127.0.0.1 --port 8787
```

## Safety

The app does not pass arbitrary shell commands from the browser. It only passes the vehicle query into a fixed Codex prompt with a fixed JSON schema.

The MCP worker accepts HTTPS URLs only from an explicit marketplace allowlist. Every worker call records pages/cards examined, accepted rows, rejection reasons, pagination count, stop reason, and per-year quota status. Codex prose or search snippets cannot create accepted Autotrader, Edmunds, or Porsche Finder rows without this audit.

A public marketplace may allow a visible browser session while refusing the deployment host's automated profile or network address. Treat that as source availability, not as permission to rotate identities or bypass a CAPTCHA/access wall. The app preserves already verified rows and Visor facets, records the refusal, and stops repeated requests for that source.

On macOS, a blocked or empty audited source is retried automatically through `scripts/chrome_host_capture.applescript`. The script immediately minimizes a temporary regular-Chrome worker window, restores the previously focused app, scrolls rendered results, clicks only recognized pagination controls, and returns public visible text. `car_compare/sources/chrome_host.py` enforces the marketplace host allowlist, and the app parses and filters the capture deterministically before replacing the blocked audit. This path runs only during the collection and spends no model usage.

If regular Chrome also receives a network refusal from Edmunds, the active job invokes native `codex --search` only for combined sparse years. Long horizons are split into small batches and up to three batches may run concurrently. The fixed `web_search_capture_schema.json` permits only official Edmunds page URLs plus verbatim visible text. The app validates every URL and runs `parse_visible_listing_text` plus the resolved trim rules before accepting a row. The search stage spends Codex usage only when needed and has no idle monitor. A temporary manual Chrome lease is retained only when automatic capture mechanisms cannot produce an authoritative result.

Do not create a recurring five-minute Codex task. While a lease is pending, the report page polls the local job endpoint every five seconds; this is ordinary local HTTP traffic and does not invoke Codex. No polling remains after completion, expiry, navigation to a new run, or an error. The backend cannot silently start a Chrome-plugin desktop task, so the operator uses `Repair Missing Source` and sends the prefilled task on the host Mac only when automatic recovery failed.

See [DEPLOYMENT.md](DEPLOYMENT.md) for clean installation and [ALWAYS_AWAKE_HANDOFF.md](ALWAYS_AWAKE_HANDOFF.md) for detailed recovery.

The backend stays bound to `127.0.0.1` and is published only through the authenticated `carcompare.nsyprojects.com` route. Normal Codex review and an operator-started Chrome fallback can consume the deployment account's Codex usage; an idle app and an expired lease do not.

## Fallback

If Codex is not installed, not logged in, or cannot operate a website, the app still supports manual capture import and Visor API-style adapters.
