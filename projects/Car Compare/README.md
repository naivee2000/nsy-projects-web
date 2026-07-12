# Car Depreciation Research Tool

Local car depreciation research workstation. This folder is intended to be moved into:

```text
/Users/shaoyangni/Desktop/Python Files/nsy-dem-app-handoff/projects/
```

For the next Codex chat, start with [docs/CODEX_CONTEXT.md](docs/CODEX_CONTEXT.md). It explains the current architecture, source-collection behavior, tested cases, known limitations, and the fastest verification commands.

It accepts natural vehicle queries such as `BMW M4 Competition after 2021`, normalizes market listings into age buckets, and returns:

- age 0 MSRP plus actual new-car market samples when sources expose them
- observed market values by vehicle age
- average, median, Q1, Q3, min, max
- yearly depreciation in dollars and percent
- projected values out to the selected horizon, up to 20 years, when data is thin
- optional Codex generation-impact research for future new-generation depreciation shocks
- source feasibility status for Edmunds, Autotrader, Visor, and manufacturer MSRP
- cross-source deduplication so the same VIN/listing is counted once

Obvious catalog-backed spelling mistakes are corrected conservatively before collection. For example, `BMW M4 Cometition` resolves to `BMW M4 Competition`, and the Parsed Vehicle panel discloses the correction. Unknown or ambiguous trim names are left unchanged. When verified new-market samples are unavailable, the official MSRP reference is used as the Age 0 depreciation baseline and remains labeled `MSRP Ref` rather than being presented as an observed listing.

The completed seven-point search-accuracy audit and seven-point UX audit are documented in [docs/ACCURACY_UX_AUDIT.md](docs/ACCURACY_UX_AUDIT.md).

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

## Data Collection Modes

1. **Explicit demo mode**
   Setting `CAR_COMPARE_SAMPLE_MODE=1` enables a small BMW M4 Competition dataset for interface testing. Bundled rows are never injected in the default production mode.

2. **Visible-text import**
   Codex can open a normal website page, collect visible page text, and send it to `/api/parse-visible-text` or the app's capture import box. This is useful for Edmunds and Autotrader pages that expose listing rows in normal browser views.

3. **Automatic collection**
   The app's `Collect` button checks Visor public market facets, then runs the audited browser worker against Autotrader and Edmunds year by year. The worker records pages/cards examined, accepted rows, rejection reasons, detail-page checks, pagination, stop reasons, and sparse years. Codex reviews the resulting coverage and handles additional research when usage is available. Browser rows without a worker audit are discarded.

4. **Codex website collection review**
   If Codex is installed/logged in on the same computer, the app registers the same project-local browser worker as an MCP tool and starts a fixed-schema review job. If Codex fails, times out, or reaches a usage limit, audited browser rows and Visor facets remain available as a completed partial result.

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

3. Start the persistent collection browser and expose only its localhost endpoint to the backend:

   ```bash
   scripts/start_collection_browser.sh
   export CAR_COMPARE_BROWSER_CDP_URL="http://127.0.0.1:9222"
   ```

   On Linux without a graphical session, install `xvfb` first.
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

For a deployment host, verify both CLI discovery and the saved/keyring login with:

```bash
python3 scripts/deploy_preflight.py --smoke-codex --smoke-browser
```

The app binds to `127.0.0.1` by default. Keep it local unless you intentionally add authentication, because automatic collection can spend Codex usage.

The public route is `https://carcompare.nsyprojects.com/`. The deployment reuses the signed NSY session issued by `dem.nsyprojects.com/login`, so unauthenticated visitors are redirected to the existing NSY sign-in page. Browser visitors use the deployment host's Codex account and do not install or log in to Codex themselves. `GET /api/health` remains public for health checks; all other pages and APIs require the shared session when `CAR_COMPARE_AUTH_USERNAME` and `CAR_COMPARE_SESSION_SECRET` are configured.

The PM2 template is `ops/pm2-car-compare.example.cjs`. The live Cloudflare tunnel should route `carcompare.nsyprojects.com` to `http://127.0.0.1:8787` before its final 404 ingress rule.

The first page intentionally opens empty. It should not auto-run a default BMW query anymore.

## Generation Impact Research

The `Generation Forecast` panel runs automatically for the current vehicle when research or collection is started. It uses Codex to estimate whether a coming replacement generation should add an extra depreciation shock to predicted rows. The project-local skill lives at:

```text
skills/generation-impact-research
```

On another computer, the app can use the skill directly from the project folder. To also install it into that computer's Codex skill folder:

```bash
scripts/install_project_skills.sh
```

The app stores generation research runs under `data/generation_research_jobs/`. These are local generated outputs, while the reusable skill and schema are part of the project folder.

## Deduplication

The normalization layer deduplicates before calculating statistics:

1. Same VIN is always one vehicle observation.
2. Without VIN, likely duplicates are matched by year, title/trim, price, mileage, and dealer when available.
3. Duplicate sightings keep combined source names, but count as one price observation.

## Current Verification Snapshot

Last verified in browser on 2026-07-08:

- The initial page opens blank and does not call `/api/research` until a user searches.
- The user-supplied 23 make/model/trim CSV parsed correctly in the UI.
- Representative `Collect` browser tests completed for `Mercedes-Benz C-Class C300`, `Honda Civic EX`, `Ford Mustang GT`, `Porsche 911 Carrera`, and `Porsche 911 Carrera S`.
- Exact-trim guardrails separate `Civic EX` from `EX-L/EX-T`, `Mustang GT` from Shelby `GT500`, and `Porsche 911 Carrera` from `Carrera S/GTS`. `BMW M4 Competition` is deliberately a family rule: all Competition body/drivetrain variants qualify, as do verified 2016-2020 factory ZCP Competition Package cars; Base, CS, CSL, and GTS do not.

Quick checks:

```bash
python3 -m unittest discover -s tests
python3 -m py_compile app.py car_compare/*.py car_compare/sources/*.py
node --check static/app.js
```
