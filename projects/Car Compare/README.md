# Car Depreciation Research Tool

Local car depreciation research workstation. This folder is intended to be moved into:

```text
/Users/shaoyangni/Desktop/Python Files/nsy-dem-app-handoff/projects/
```

For the next Codex chat, start with [docs/CODEX_CONTEXT.md](docs/CODEX_CONTEXT.md). It explains the current architecture, source-collection behavior, tested cases, known limitations, and the fastest verification commands.

For a clean website deployment on the Mac that stays online, start with [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). The deeper [docs/ALWAYS_AWAKE_HANDOFF.md](docs/ALWAYS_AWAKE_HANDOFF.md) runbook covers browser evidence, recovery, and host troubleshooting.

It accepts natural vehicle queries such as `BMW M4 Competition after 2021`, normalizes market listings into age buckets, and returns:

- age 0 MSRP plus actual new-car market samples when sources expose them
- observed market values by vehicle age
- average, median, Q1, Q3, IQR whiskers, and retained outlier evidence
- signed yearly value movement and cumulative change, including appreciation
- projected values out to the selected horizon, up to 20 years, when data is thin
- optional Codex generation-impact research for future new-generation depreciation shocks
- source feasibility status for Edmunds, Autotrader, Visor, and manufacturer MSRP
- cross-source deduplication so the same VIN/listing is counted once
- optional two-car comparison with aligned median-value curves, grouped YoY dollar-loss bars, labeled cumulative depreciation percentages, and a shared age-by-age table

Obvious catalog-backed spelling mistakes are corrected conservatively before collection. For example, `BMW M4 Cometition` resolves to `BMW M4 Competition`, and the Parsed Vehicle panel discloses the correction. Unknown or ambiguous trim names are left unchanged. When verified new-market samples are unavailable, the official MSRP reference is used as the Age 0 depreciation baseline and remains labeled `MSRP Ref` rather than being presented as an observed listing.

The completed seven-point search-accuracy audit and seven-point UX audit are documented in [docs/ACCURACY_UX_AUDIT.md](docs/ACCURACY_UX_AUDIT.md).
The current 60-label accuracy gate, seven live browser samples, and runtime acceptance record are in [docs/PERFORMANCE_ACCURACY_BENCHMARK.md](docs/PERFORMANCE_ACCURACY_BENCHMARK.md).

## Run

```bash
cd "/Users/shaoyangni/Desktop/Python Files/nsy-dem-app-handoff/projects/Car Compare"
python3 app.py --host 127.0.0.1 --port 8787
```

Then open:

```text
http://127.0.0.1:8787
```

If the folder is renamed during the move, use that actual path instead. The Python app has no required virtualenv. Audited marketplace collection additionally uses the project-local Node/Playwright worker described below.

## Current Shape

The first version is intentionally adapter-based:

```text
App button / Codex browser research / APIs / pasted captures
-> source adapters
-> normalized listings
-> VIN/listing deduplication
-> depreciation engine
-> local web dashboard
```

This makes it easier to add more websites later. Each source can be tested and fixed independently without rewriting the chart or depreciation model.

## Single And Compare Modes

`Single Car` preserves the original one-vehicle report. `Compare Cars` accepts Car A and Car B with one shared horizon and one `Compare & Research` action. Both vehicle jobs and generation researchers start together; the backend browser lock coordinates each vehicle's audited browser stage while Visor, cache, and generation work can overlap. Each vehicle still receives its own normal depreciation report and generation-impact result, aligned by vehicle age without changing the depreciation formula.

In comparison results, vehicle color stays consistent across charts. Solid line segments are observed, dashed segments are predicted, grouped bars are signed year-over-year value movement, and the labeled percentage dots show signed change from each vehicle's own Age 0 market baseline. Source evidence and collection plans remain separate under Car A and Car B tabs.

## Data Collection Modes

1. **Explicit demo mode**
   Setting `CAR_COMPARE_SAMPLE_MODE=1` enables a small BMW M4 Competition dataset for interface testing. Bundled rows are never injected in the default production mode.

2. **Visible-text import**
   Codex can open a normal website page, collect visible page text, and send it to `/api/parse-visible-text` or the app's capture import box. This is useful for Edmunds and Autotrader pages that expose listing rows in normal browser views.

3. **Automatic collection**
   `Collect & Research` first loads fresh source-year cache entries. It collects only missing or expired Visor facets, Autotrader, Edmunds, and, for Porsche queries, official Porsche Finder. Missing browser sources start with the full requested year range, expand visible results, and use bounded single-year follow-ups only where evidence remains sparse. If both browser profiles are refused, native Codex web search can collect verbatim blocks from indexed official Edmunds year pages. Every cache, browser, or search row is revalidated by the deterministic parser. Unverified Codex prose is discarded.

4. **Deterministic collection finalization**
   Browser, cache, and indexed-source rows are accepted only after the same deterministic matcher validates them. The redundant post-collection Codex review is disabled by default with `CAR_COMPARE_CODEX_COLLECTION_REVIEW=0`. Generation-impact research remains automatic and separate.

5. **API/source adapters**
   Visor should still be treated as API/MCP-first when an API key is available. Public facets are good for depreciation trends; the listings API is the cleaner path for listing-level VIN/dealer data.

See [docs/CODEX_COLLECTION_WORKFLOW.md](docs/CODEX_COLLECTION_WORKFLOW.md) for the browser collection workflow, including scrolling and clicking visible load-more controls.

## Tests

```bash
python3 -m unittest discover -s tests
```

## Important Boundary

This project is a research assistant. It should use normal public website UI, official APIs, manual import, or user-authorized accounts/API keys. If a source blocks access, requires CAPTCHA, or restricts data, use another source or manual capture rather than trying to bypass the site.

## Automatic Collection Setup

On another computer:

1. Install and log into Codex.
2. Install Node.js 20 or newer and the project browser packages:

   ```bash
   npm install
   npm exec playwright install chromium
   npm run browser:self-test
   ```

3. Verify the version-matched persistent browser profile:

   ```bash
   python3 scripts/deploy_preflight.py --smoke-browser
   ```

   The worker launches Playwright's version-matched browser headlessly by default and stores its reusable machine-local session under `~/.car-compare/browser-profile`. No separate Chrome process, visible window, or CDP port is required. Keep `CAR_COMPARE_BACKGROUND_MODE=1` in normal operation. Set it to `0` only while diagnosing a browser problem.
4. Make sure the CLI works:

   ```bash
   codex --version
   ```

5. The app automatically checks `PATH`, official standalone install locations on macOS/Linux/Windows, and macOS ChatGPT/Codex desktop bundles. If it still cannot find the CLI, set `CODEX_BIN` to the executable on that computer, for example:

   ```bash
   export CODEX_BIN="/Applications/ChatGPT.app/Contents/Resources/codex"
   ```

   On Windows, a standard standalone install is discovered under `%LOCALAPPDATA%\Programs\OpenAI\Codex\bin\codex.exe`.

6. Run the app:

   ```bash
   cd "/path/to/Car Compare"
   python3 app.py --port 8787
   ```

7. Open `http://127.0.0.1:8787`, enter a vehicle, and click `Collect & Research`.

For a deployment host, follow [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md), then verify both CLI discovery and the saved/keyring login with:

```bash
python3 scripts/deploy_preflight.py --smoke-codex --smoke-browser
```

The app binds to `127.0.0.1` by default. Keep that bind address in production and route the authenticated hostname through Cloudflare Tunnel, because automatic collection can spend the deployment account's Codex usage.

The public route is `https://carcompare.nsyprojects.com/`. The deployment reuses the signed NSY session issued by `dem.nsyprojects.com/login`, so unauthenticated visitors are redirected to the existing NSY sign-in page. Browser visitors use the deployment host's Codex account and do not install or log in to Codex themselves. `GET /api/health` remains public for health checks; all other pages and APIs require the shared session when `CAR_COMPARE_AUTH_USERNAME` and `CAR_COMPARE_SESSION_SECRET` are configured.

The PM2 template is `ops/pm2-car-compare.example.cjs`. The worker is started by the backend for each collection pass and reuses its project-local browser profile, so PM2 only needs to manage the Car Compare backend. The live Cloudflare tunnel should route `carcompare.nsyprojects.com` to `http://127.0.0.1:8787` before its final 404 ingress rule.

Autotrader and Edmunds open their broad year-range pages concurrently inside one shared browser session when their cache is missing or expired. Porsche queries add official Porsche Finder with an explicit nationwide radius; its 911 URL categories distinguish all trims, Carrera family, Base, and known exact trims before deterministic card validation. Each source examines at most five broad pages, followed by one round of at most four sparse year pages. A fresh completed source-year set suppresses recollection for that source for three days even when its row count is below the preferred sample target. Newly added or expired sources collect independently.

When the backend browser profile is refused or returns no rows, the app automatically retries that source in the host Mac's regular Google Chrome. The project AppleScript worker creates and immediately minimizes its own temporary window, restores the app the user was working in, scrolls rendered results, clicks recognized load-more or next-page controls, and returns public listing-card text plus same-site detail URLs to the deterministic parser. Whole-page visible text remains a compatibility fallback. The worker then closes its own window. It runs only during the active collection and does not invoke a model or require an operator click. A short-lived `Repair Missing Source` action remains only as a manual recovery path when host Chrome automation is unavailable. No recurring Codex scheduled task is required.

When the host network still blocks an official Edmunds result page, the active job can invoke `codex --search` for at most four critical years with fewer than two individual rows and no aggregate support. Codex returns only official Edmunds URLs and verbatim listing blocks under `car_compare/web_search_capture_schema.json`; the app then validates the host and reruns deterministic year/model/trim parsing. This fallback consumes Codex usage only for that active job and never polls while idle. Set `CAR_COMPARE_CODEX_SEARCH_FALLBACK=0` to disable it.

## Persistent Cache And Concurrency

Verified marketplace captures and generation-impact results are stored in SQLite at `data/cache/collector_cache.sqlite3` by default. Production should set `CAR_COMPARE_CACHE_DIR` to a persistent disk or mounted volume; ephemeral container storage removes the performance benefit after a restart. SQLite WAL mode and atomic upserts make the cache safe for concurrent job threads and portable across macOS and Linux deployment hosts.

Cache keys include canonical make, model, trim scope, marketplace, and model year. Cached rows are revalidated through the deterministic year/model/trim matcher on every read. Marketplace rows, Visor facet snapshots, validated collection reviews, and generation research all expire within three days. This is a hard maximum in code even when a larger environment value is supplied.

Deployment controls:

```text
CAR_COMPARE_CACHE_DIR=/persistent/path/car-compare-cache
CAR_COMPARE_CACHE_ENABLED=1
CAR_COMPARE_RECENT_CACHE_TTL_SECONDS=259200
CAR_COMPARE_OLDER_CACHE_TTL_SECONDS=259200
CAR_COMPARE_GENERATION_CACHE_TTL_SECONDS=259200
CAR_COMPARE_REVIEW_CACHE_TTL_SECONDS=259200
CAR_COMPARE_CODEX_COLLECTION_REVIEW=0
CAR_COMPARE_MARKETPLACE_CONCURRENCY=2
CAR_COMPARE_CODEX_SEARCH_WORKERS=3
CAR_COMPARE_CODEX_SEARCH_BATCH_SIZE=5
```

An optional Codex collection review can still be enabled for diagnosis and is cached for up to three days, but production leaves it disabled. A repeat run revalidates fresh cached marketplace and Visor rows and skips complete source-year captures. An empty or blocked attempt cannot overwrite a richer accepted cache entry. Comparison mode starts both vehicles' collection and generation work together. The backend browser lock still serializes ownership between vehicle jobs, while cache reads, generation research, and the other vehicle's non-browser work can overlap safely.

The first page intentionally opens empty. It should not auto-run a default BMW query anymore.

## Generation Impact Research

The `Generation Forecast` panel runs automatically for the current vehicle when research or collection is started. It uses Codex to estimate whether a coming replacement generation should add an extra depreciation shock to predicted rows. The project-local skill lives at:

```text
skills/generation-impact-research
skills/collect-car-marketplaces
```

On another computer, the app can use the skill directly from the project folder. To also install it into that computer's Codex skill folder:

```bash
scripts/install_project_skills.sh
```

The app stores generation research runs under `data/generation_research_jobs/` and reuses successful research from the persistent cache for at most three days. Job outputs are local generated artifacts, while both reusable skills and the generation schema are part of the project folder.

## Deduplication

The normalization layer deduplicates before calculating statistics:

1. Same VIN is always one vehicle observation.
2. Without VIN, likely duplicates are matched by year, title/trim, price, mileage, and dealer when available.
3. Duplicate sightings keep combined source names, but count as one price observation.

## Current Verification Snapshot

Last verified locally on 2026-07-16:

- The portable seven-vehicle fixture passed 60/60 classifications, up from the recorded 44/60 baseline: a 36.37% relative accuracy improvement.
- The same cold `BMW M4 Competition` browser workflow fell from 13:58 to 2:36, an 81.4% runtime reduction.
- Seven normal UI runs covered BMW M4 Competition, Porsche 911 Carrera, Honda Civic EX, Ford Mustang GT, Mercedes-Benz C-Class C300, Toyota Camry XSE, and Tesla Model 3 Long Range AWD.
- The seven-run median was 2:21. Porsche Carrera was slowest at 5:57 because it intentionally resolves a broad trim family; Ford Mustang GT was fastest at 1:22.
- The corrected Tesla run retained 28 report rows plus 221 aggregate vehicles after preserving AWD evidence from the same listing block.
- All 196 regression tests passed, the browser worker self-test passed, Python compilation passed, and the deterministic benchmark had zero false positives and zero false negatives.
- Detailed rows, commands, and acceptance thresholds are in [docs/PERFORMANCE_ACCURACY_BENCHMARK.md](docs/PERFORMANCE_ACCURACY_BENCHMARK.md).

Previously verified interface and resolver behavior:

- The initial page opens blank and does not call `/api/research` until a user searches.
- The user-supplied 23 make/model/trim CSV parsed correctly in the UI.
- Representative `Collect` browser tests completed for `Mercedes-Benz C-Class C300`, `Honda Civic EX`, `Ford Mustang GT`, `Porsche 911 Carrera`, and `Porsche 911 Carrera S`.
- Trim scopes are model-wide, configured family, base, or exact. `Porsche 911` includes every 911 trim, `Porsche 911 Carrera` includes the Carrera family, and `Porsche 911 Base` keeps only the root Carrera Coupe/Cabriolet. Unconfigured trims remain exact, so `Civic EX` stays separate from `EX-L/EX-T` and Mustang `GT` stays separate from Shelby `GT500`. `BMW M4 Competition` remains a generation-aware family rule.

Quick checks:

```bash
python3 -m unittest discover -s tests
python3 scripts/benchmark_search_accuracy.py
python3 -m py_compile app.py car_compare/*.py car_compare/sources/*.py
node scripts/car_compare_browser_mcp.mjs --self-test
```
