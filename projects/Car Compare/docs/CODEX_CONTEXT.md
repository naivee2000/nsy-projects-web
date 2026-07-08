# Codex Context: Car Compare

This is the handoff entrypoint for another Codex chat after the folder is moved into:

```text
/Users/shaoyangni/Desktop/Python Files/nsy-dem-app-handoff/projects/
```

The user wants this project to stay self-contained as one project folder under `projects/`. Shared code and docs can live in Git; machine-local Codex auth, browser state, API keys, generated collector jobs, caches, and screenshots should stay local unless the user explicitly asks to preserve them.

## What This App Does

Car Compare is a local web app for researching vehicle depreciation.

User flow:

```text
user enters vehicle query
-> parser resolves make/model/trim/year horizon
-> Collect pulls market data from public source adapters and local Codex website collection
-> Research builds age buckets and graph
-> app shows box-plot trend, source evidence, and collection plan
```

The target behavior:

- Age 0 is MSRP plus actual new-car market samples when available.
- Age 1+ is current market value of matching used examples by model year.
- The graph shows median, average, Q1, Q3, low, high, yearly depreciation, and projection.
- The user can choose a horizon up to 20 years.
- Rows are deduplicated by VIN first, then likely same listing fields.
- The first page opens empty. No default BMW query should run on load.

## How To Run

From this project folder:

```bash
python3 app.py --host 127.0.0.1 --port 8787
```

Open:

```text
http://127.0.0.1:8787
```

If port 8787 is busy:

```bash
lsof -nP -iTCP:8787 -sTCP:LISTEN
```

Stop the old app process only if it is this Car Compare server and the user is okay with restarting it.

## Important Files

- `app.py`: local HTTP server and API routes.
- `static/index.html`, `static/app.js`, `static/styles.css`: web UI.
- `car_compare/parser.py`: natural vehicle query parsing.
- `car_compare/vehicle_catalog.py`: make/model catalog, aliases, source model mapping.
- `car_compare/trim_match.py`: exact-trim conflict rules.
- `car_compare/sources/source_plan.py`: source URLs, Codex workflow instructions, manufacturer URLs.
- `car_compare/sources/visor_facets.py`: public Visor aggregate facet collector.
- `car_compare/sources/browser_capture.py`: visible listing text parser.
- `car_compare/collector.py`: background collection jobs and Codex CLI bridge.
- `car_compare/depreciation.py`: dedupe, statistics, projections, report assembly.
- `tests/test_core.py`: regression suite.

Docs:

- `README.md`: user-facing overview and run instructions.
- `docs/AUTOMATIC_CODEX_COLLECTION.md`: how the Collect button bridges to Codex.
- `docs/CODEX_COLLECTION_WORKFLOW.md`: how Codex should operate websites.
- `docs/WEBSITE_RESEARCH.md`: original source feasibility notes.

## Current Source Strategy

The app uses two layers:

1. Public adapters, especially Visor public facets.
   These give aggregate market observations and are useful for nationwide trend buckets. They are not individual dealer VIN rows.

2. Local Codex website collection.
   The app starts the Codex CLI on the same computer, passes a fixed collection plan and JSON schema, and expects structured listings/MSRP back. Codex should use visible website UI, official APIs, or user-authorized accounts/API keys. Do not bypass CAPTCHAs, login walls, paywalls, or site restrictions.

The collection job currently checks Visor facets first. If Codex is available, the job can continue into website collection afterward. If Codex fails after Visor returned rows, the app keeps the Visor data as a completed partial result.

## Vehicle Matching Rules Already Fixed

These are important because wrong trim grouping changes the depreciation graph:

- `Mercedes-Benz C-Class C300` maps to Visor model `C-Class`, not `C`.
- `Mercedes-Benz GLC300` style variants match `GLC300` and `GLC 300`.
- Lexus repeated/numeric inputs such as `Lexus RX RX 350` normalize to `Lexus RX 350`.
- `Honda Civic EX` excludes `EX-L` and `EX-T`.
- `Ford Mustang GT` excludes Shelby `GT500`.
- `Porsche 911 Carrera` excludes `Carrera S`, `Carrera GTS`, `Carrera 4S`, etc.
- `Porsche 911 Carrera S` stays separate from base `Carrera`.
- `BMW M4 Competition` excludes xDrive unless the user asks for xDrive.
- `BMW X5 xDrive40i`, `BMW 3 Series 330i`, and similar attached names parse cleanly.

## Verified Test Matrix

The user supplied this CSV and asked that app parsing and source alias behavior be checked:

```csv
Make,Model,Trim
Toyota,Camry,LE
Toyota,Camry,XSE
Toyota,RAV4,Limited
Honda,Civic,EX
Honda,Accord,Touring
Ford,F-150,Lariat
Ford,Mustang,GT
Chevrolet,Silverado 1500,LT
BMW,3 Series,330i
BMW,X5,xDrive40i
Mercedes-Benz,C-Class,C300
Mercedes-Benz,GLE,350 4MATIC
Audi,Q5,Premium Plus
Lexus,RX,RX 350
Tesla,Model 3,Long Range AWD
Tesla,Model Y,Performance
Jeep,Wrangler,Rubicon
Subaru,Outback,Touring XT
Hyundai,Tucson,SEL
Kia,Telluride,SX
Porsche,911,Carrera
Porsche,911,Carrera S
Porsche,Cayenne,Base
```

As of 2026-07-08, all 23 parse correctly in the UI.

Representative browser `Collect` runs were verified:

- `Mercedes-Benz C-Class C300`: collected Visor facet rows.
- `Honda Civic EX`: collected with a realistic multi-year horizon; a 1-year horizon may be too narrow because Visor may have no usable 2025/2026 EX rows.
- `Ford Mustang GT`: collected and excluded Shelby variants.
- `Porsche 911 Carrera`: collected and separated from Carrera S/GTS.
- `Porsche 911 Carrera S`: collected separately.

## Current UI State

The opening page should be blank:

- Vehicle input is empty.
- No `/api/research` call happens on load.
- Chart, resolver, metrics, source evidence, and collection plan are blank.
- Source/collector status still loads.

Clicking `Research` or `Collect` with an empty vehicle should leave the empty state in place.

## Verification Commands

Use these after edits:

```bash
python3 -m unittest discover -s tests
python3 -m py_compile app.py car_compare/*.py car_compare/sources/*.py
node --check static/app.js
```

For browser verification, use the actual local app at `http://127.0.0.1:8787`. At minimum check:

- Initial page is empty and does not call `/api/research`.
- A normal query such as `Toyota Camry XSE` renders parsed chips and a collection plan.
- For source matching changes, test both backend unit tests and browser flow.

## Known Limitations And Next Good Improvements

- Visor public facets are aggregate data, not individual listing URLs/VINs.
- Autotrader and Edmunds collection depends on what a normal browser can see.
- Codex website collection can consume usage and may fail from usage limits, site walls, or browser availability.
- Manufacturer MSRP/new inventory collection is planned through source plan instructions, but true listing-level official adapters can still be improved.
- Some trims have sparse data for very new model years; a longer horizon can be necessary.
- Generated evidence screenshots and collector jobs under `data/` are useful locally but should not be treated as core source code.

## Boundary

Keep this app local-first. Do not add login/auth/public deployment behavior unless the user explicitly asks. If deployment is discussed later, preserve the boundary between shared project code and machine-local Codex/runtime/secrets.
