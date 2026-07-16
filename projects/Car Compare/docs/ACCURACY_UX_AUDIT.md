# Accuracy and UX Audit

Verified on 2026-07-11. This document records the seven search-accuracy changes and seven user-experience changes delivered for the Car Depreciation Research Tool.

## Seven search-accuracy fixes

1. **Catalog-backed query correction without guessing.** Make, model, and trim typos are corrected only when the catalog match is strong; ambiguous input is left unchanged. Common aliases and attached model tokens such as `Mercedes`, `Chevy`, `VW`, `C300`, and `F150` are normalized so valid rows are not lost.
2. **Exact vehicle and trim boundaries.** Whole-token model checks prevent near-model contamination such as M4 versus M440. Exact trims reject catalog sibling trims and drivetrain variants when they identify a different configured trim, while genuinely unspecified body, drivetrain, and powertrain filters retain their documented inclusive behavior.
3. **Exact year, condition, and age semantics.** A requested model year is enforced in the source URLs, source responses, and final report. Age 0 separates new vehicles, current-model-year used vehicles, and an MSRP reference; current-year used samples remain represented without being labeled as new. The runtime year is calculated dynamically rather than being fixed to 2026.
4. **Verified source filters.** Autotrader, Edmunds, and Visor targets carry the requested year. Visor data is accepted only when structured page evidence confirms the make/model and applied year/trim/version filters; a title string or global histogram alone is not sufficient.
5. **Sale-price and ingest validation.** Visible-text parsing accepts ordinary four-digit through high-end vehicle prices, extracts the sale price even when payment text is nearby, and rejects MSRP, discount, savings, down-payment, and monthly-payment amounts. Collector JSON schema and ingest code also enforce plausible price and year ranges.
6. **Identity-aware, deterministic deduplication.** Different VINs never merge. Matching VINs, normalized detail URLs, or stock identities merge across sources; CPO and used representations of the same car are compatible. Same-source rows with distinct detail URLs remain separate. VIN/no-VIN matching is input-order independent.
7. **Representative sampling and provenance.** Aggregate price-bin samples preserve the source-bin population ratio while retaining at least one observation from every non-empty bin. Synthetic aggregate observations are labeled separately from individual listing rows, and bundled sample data is disabled in production unless explicit demo mode is enabled.

## Seven user-experience fixes

1. **Resolve before collecting.** `/api/collection-plan` runs before the long job, shows the canonical vehicle and any spelling correction immediately, and stops low-confidence queries with an inline, focusable error.
2. **One immutable run at a time.** Query, horizon, capture text, MSRP, and canonical key are snapshotted for each run. Inputs are locked during collection, job IDs are bound to that canonical request, old callbacks cannot overwrite a newer run, and market/generation report updates are serialized with a market-only fallback.
3. **Visible progress and timing.** A top-level live run panel shows the current stage, resolved vehicle, source message, elapsed time, success state, or error state instead of hiding progress in the sidebar.
4. **Recoverable network and job errors.** JSON requests have timeouts, structured HTTP/auth/network handling, `try/catch/finally` cleanup, a retry action, and a sign-in-again path. Buttons and inputs are always restored after a terminal success or failure.
5. **Honest zero/partial results.** The report distinguishes individual listing rows, the identifiable dealer subset, aggregate market population, aggregate sample points, and demo rows. Zero and partial states explain what was accepted and provide Retry Sources and Import Listing Text actions instead of presenting an empty chart as success.
6. **Graceful capability fallback.** Visor and Codex website collection are reported separately. Visor remains usable when Codex is offline, and Analyze Imported Data remains available even when every automatic collector is offline.
7. **Responsive and accessible results.** The product name and NSY return link are consistent; charts and tables scroll on small screens with a sticky Age column; tables have captions and scoped headers; charts have accessible titles/descriptions and keyboard-focusable data points with visible focus; status/error regions announce changes.

## Verification

Run the regression suite and static checks from this folder:

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile app.py car_compare/*.py car_compare/sources/*.py
node --check static/app.js
python3 scripts/deploy_preflight.py
git diff --check
```

Browser verification covers typo correction (`BMW M4 Cometition`), both depreciation charts, immutable disabled inputs while collecting, offline manual import, zero-data recovery actions, and terminal input/button recovery.

## 2026-07-15 market-integrity follow-up

- Zero-result marketplace pages, search-result headings, and ZIP/postal values can no longer become vehicle listings or prices. Host-Chrome accepted rows cannot exceed its reported card count, and the marketplace cache version was advanced so contaminated captures are not reused.
- Age 0 weighted statistics preserve each price/market-weight pair. A single age-bucket row remains visible as evidence but does not define an observed trend.
- Curated U.S. model-year lifecycle bounds stop generic BMW M4 collection at model-year 2015 and exclude prelaunch rows from observed report data while retaining long-range age projections.
- Value movement is signed: positive values are appreciation and negative values are depreciation. Broad all-trim queries are labeled as current cross-sectional market mix rather than same-trim longitudinal depreciation.
- Generation-impact adjustments apply only to predicted forecast buckets. Observed medians, quartiles, and whiskers remain factual market summaries.
- Box-plot low/high values use IQR whiskers when supported. Extreme rows remain in source evidence and are counted in `outlier_count` instead of stretching the chart.

For a second computer or production host, continue with [DEPLOYMENT.md](DEPLOYMENT.md). It adds Codex login, Playwright, host-Chrome, shared-auth, persistent-cache, PM2, and Cloudflare verification to this code-level audit.

## 2026-07-16 accuracy and runtime acceptance

The portable 60-label fixture now passes 60/60 across BMW M4 Competition, Porsche 911 Carrera, Honda Civic EX, Ford Mustang GT, Mercedes-Benz C-Class C300, Toyota Camry XSE, and Tesla Model 3 Long Range AWD. That is a 36.37% relative improvement over the recorded 44/60 baseline. The same cold BMW browser workflow fell from 13:58 to 2:36, an 81.4% reduction. Seven user-like browser runs, exact commands, job behavior, and bounded crawl budgets are recorded in [PERFORMANCE_ACCURACY_BENCHMARK.md](PERFORMANCE_ACCURACY_BENCHMARK.md).
