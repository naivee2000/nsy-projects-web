# Reliability revision 4 — validation record

Date: 2026-11-02. Release status: **deployed and public research verified**.

This supersedes the pricing and cache contracts in the historical October migration notes. Historical test results remain historical evidence, not a release approval.

## Contract

- Central versions: validation/analysis 4, marketplace cache 7, research cache 6 (`car_compare/revisions.json`). Existing SQLite files and original capture timestamps are preserved.
- A new baseline is selected per model year, newest complete eligible year first. Old stock does not invalidate another year's verified population. Historical ages use the analysis model year; forecast calendar dates use the research year.
- Exact single-population medians stay exact. Disjoint histograms are coarsened without splitting bin counts. Pooled medians are estimates with a containing interval; wide intervals have no point estimate or forecast anchor.
- A consistent combined used/CPO series is preferred; otherwise a labeled used-only or CPO-only series is selected. Three comparable observed years are required for forecasts.
- Automatic evidence must have fresh compatible scope and current validation. Manual imports are labeled samples. Synthetic observations are never counted as vehicles.
- Readiness is separate from execution completion. Generation adjustments are an optional chart overlay; market values and signed calculations stay unchanged.
- Primary and regular-Chrome paths share selected-control preparation and validation. Only independently verified pages contribute cards. Available options resolve expected groups but never prove applied filters.

## Verified checkpoints

- Saved Lexus NX replay: exact 2026 baseline **$54,623**, **eight** combined historical prices. 2019 and 2016 histogram count mismatches are disclosed. The original 795 synthetic observations are not 795 vehicles.
- Python suite: 258 tests passed. Owned-process cleanup now distinguishes a denied macOS probe from an actual termination failure using a bounded, read-only process-table check; unknown/live groups still fail closed.
- Browser scope regressions: 20 tests passed; browser worker self-test passed.
- Accuracy fixture: 60/60 labels, zero false positives/negatives. This is an offline matching benchmark, not a live collection acceptance result.
- Deployment browser preflight passed.
- Isolated synthetic desktop/mobile UI: median-only marker visible, unavailable result explicitly labeled, comparison with missing baseline, and optional generation overlay checked. Toggling the overlay did not change the market table.
- Fresh Lexus jobs recovered eight historical prices and a current baseline of **$54,713**. The different saved/current baseline values come from separate captures. Autotrader returned 42 verified NX rows in the second job. Edmunds failures remain excluded.

## Live evidence locations

Temporary directories are outside the checkout and contain no production cache reuse:

- `car-compare-full-smoke-bpt77qgc`: first fresh Lexus check.
- `car-compare-full-smoke-kh70ye9g`: repaired Autotrader NX check.
- `car-compare-full-smoke-5dn754h1`: full 20-query matrix plus Lexus. Visor returned HTTP 429; the harness stopped that host for the rest of this pass.
- `car-compare-full-smoke-78lh7vdk`: separate representative pass after cooldown, one job at a time with additional two-second per-host pacing. Saves sanitized source snapshots and independently compares source counts/price statistics.

The system temporary root is `/var/folders/tr/t5zlj5yd7rjbkh2dtygbvt_40000gn/T/`. Do not treat a `completed` job or `partial` report alone as a benchmark pass. Inspect accepted scope, prices, counts, and remaining failures before release.

## Release result and limitations

The 21-query matrix completed: **8 qualified partial reports and 13 unavailable reports**. Visor HTTP 429 caused the harness to stop that host for the rest of the pass. Unavailable cases are not represented as zero inventory or successful market research.

The separately paced representative pass produced qualified partial reports for all five required categories:

| Query | Priced historical years | Same-session price evidence |
| --- | ---: | --- |
| Lexus NX | 8 | 29/29 accepted browser prices and 25/25 aggregate partitions matched |
| Toyota Camry | 4 | 36/36 accepted browser prices matched |
| Lexus LC 500 | 5 | 17/17 aggregate partitions matched |
| Porsche 911 | 8 | 120/120 accepted browser prices matched |
| BMW M4 | 7 | 35/35 accepted browser prices matched |

`scripts/verify_saved_live_runs.py` independently checks saved card prices and reconstructs pooled intervals by merging overlapping whole bins. Every aggregate report point checked in the matrix and representative runs matched its selected evidence. Sources with access walls, unresolved filters, or missing partitions remain excluded; these checks do not certify complete marketplace coverage. Toyota/Porsche/BMW in the representative pass lacked an eligible new baseline and correctly left baseline percentages unavailable.

Production was restarted through `ops/pm2-car-compare.config.cjs` and PM2 state saved. Local and public health returned validation/analysis **4**, marketplace cache **7**, research cache **6**. Unauthenticated access still redirects to sign-in. Authenticated Chrome rendering and a fresh public Lexus run were verified:

- Collection job: `f948adcff33140398e5f5ca8f9349e78`.
- Generation job: `1fc5383b70c04f7d9b9e29ed05869860`; partial, five research sources, one optional adjustment. No automatic adjustment to the market curve.
- Repeat job: `61ebeae25ff740829f719c7a69db7ca1`; reused all 25 aggregate partitions without changing their capture times, plus 49 listings from 11 fresh Autotrader year captures. Only missing/failed portions were retried.
- Public result: 2026 baseline **$54,713**, eight historical prices, 49 individual rows, 18,418 aggregate priced vehicles, and 785 synthetic observations explicitly labeled **not vehicles**.
- Actual curve label: **All-Trim Market Mix**. Supported individual normalization diagnostics cannot label an aggregate-selected curve as normalized. The generation overlay is unchecked by default.
- The existing Projects card routes through `/projects/car-compare/` to the deployed app.

Rollback source and private PM2 settings are in `/tmp/car-compare-rollback-LfsT5n` (private directory). Prior Git revision: `27040bd5c1943d5290721d87d04e5ed812430cc1`. No runtime SQLite files were cleared or edited directly. No Git commit was created. Temporary test servers were stopped; the public result tab was retained for inspection.
