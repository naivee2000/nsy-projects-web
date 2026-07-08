# Car Compare

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

## Run

```bash
cd "/Users/shaoyangni/Desktop/Python Files/nsy-dem-app-handoff/projects/Car Compare"
python3 app.py --host 127.0.0.1 --port 8787
```

Then open:

```text
http://127.0.0.1:8787
```

If the folder is renamed during the move, use that actual path instead. The app has no build step and no required virtualenv for the current standard-library path.

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

1. **Sample mode**
   Uses a small BMW M4 Competition dataset captured from the feasibility pass, plus BMW MSRP metadata.

2. **Visible-text import**
   Codex can open a normal website page, collect visible page text, and send it to `/api/parse-visible-text` or the app's capture import box. This is useful for Edmunds and Autotrader pages that expose listing rows in normal browser views.

3. **Automatic collection**
   The app's `Collect` button first checks Visor public market facets by model year. It collects used-market facets for age 1+ and new-car facets for age 0 when available. New observations are labeled `condition=new`, the age-0 row displays as `New Market`, and MSRP is shown only as a reference value. If Codex is available, the job can continue into Codex website collection after Visor so individual website rows can be added later.

4. **Codex website collection fallback**
   If Codex is installed/logged in on the same computer, the app starts a local Codex CLI job using a fixed prompt and JSON schema. If Codex fails, times out, or hits a usage limit after Visor succeeded, the app preserves the Visor facet data as a completed partial result instead of throwing it away. The source plan includes official manufacturer pages for MSRP/new inventory when practical.

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
2. Make sure the CLI works:

   ```bash
   codex --version
   ```

3. If `codex` is not on PATH, set:

   ```bash
   export CODEX_BIN="/Applications/Codex.app/Contents/Resources/codex"
   ```

4. Run the app:

   ```bash
   cd "/path/to/Car Compare"
   python3 app.py --port 8787
   ```

5. Open `http://127.0.0.1:8787`, enter a vehicle, and click `Collect`.

The app binds to `127.0.0.1` by default. Keep it local unless you intentionally add authentication, because automatic collection can spend Codex usage.

The first page intentionally opens empty. It should not auto-run a default BMW query anymore.

## Generation Impact Research

The `Generation Forecast` panel can start a Codex research job that estimates whether a coming replacement generation should add an extra depreciation shock to predicted rows. The project-local skill lives at:

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
- Exact-trim guardrails separate `Civic EX` from `EX-L/EX-T`, `Mustang GT` from Shelby `GT500`, `Porsche 911 Carrera` from `Carrera S/GTS`, and non-xDrive BMW Competition from xDrive.

Quick checks:

```bash
python3 -m unittest discover -s tests
python3 -m py_compile app.py car_compare/*.py car_compare/sources/*.py
node --check static/app.js
```
