# Twenty-Query Collection Audit

Audit date: 2026-10-28. Local code: commit `1e80c587e`.

## Executive Summary

The collector has reproducible source-resolution and validation problems. More browser retries alone will not fix them. The highest priorities are adapting to Visor's changed vehicle catalog, validating actual selected filters instead of page titles or echoed URLs, and enforcing nationwide scope in the executable Edmunds worker.

No collector, pricing, cache, or deployment code was changed during this audit. No production collection jobs were started. This document is the audit deliverable and proposed implementation plan.

## Method And Limits

- Inspected the latest locally saved result for each of 18 valid vehicle queries; added Porsche 911 base and BMW M3 as boundary cases without saved results. Latest means file modification order, not a verified source-capture timestamp.
- Made read-only live Visor requests for all 20 queries, independently read the server-rendered sale-count text, and compared it with the app's parser. Then exercised the current alias resolver and facet validator using a 2023 used-car slice. For queries with multiple resolved versions, the live validation probe tested the first version, not their complete union.
- Checked the rendered Visor UI to resolve BMW's changed model names and confirm Porsche's catalog migration. Opened the app-generated BMW M4 searches on Edmunds and Autotrader. Clicked Autotrader's See More Results and confirmed additional cards loaded.
- Replayed the 18 saved result payloads through the current report builder in memory, with current year fixed to 2026 and each result's inferred horizon. This excludes any separately supplied generation-research payload or manual MSRP override.
- Ran `python3 -m unittest discover -s tests -q`: **199 tests passed**.
- Most saved results are from July 2026. Live October counts must NOT be subtracted from these and presented as a collection recall/error percentage. Conditions, model years, source scope, and timestamps differ.
- This is a 20-query diagnostic audit, NOT 20 new end-to-end collections or a complete listing-by-listing census across all marketplaces. Live browser spot-checks covered Visor, Edmunds, and Autotrader; Porsche Finder was not live-audited. The deployed website's database was not inspected.
- One final Visor probe received HTTP 429. Browser control later became unavailable, preventing completion of the Edmunds nationwide-refresh/pagination check and further interactive verification. Neither is evidence of zero inventory.

## Twenty-Query Matrix

The saved count is the sum of Visor `num_found` entries in the latest local result, across its captured years, conditions, and version partitions. It is NOT the number of individual listing rows or a guaranteed unique-car total. The live count is the visible count for the 2023 used-car probe, except where explicitly stated. These columns describe different scopes and are not an apples-to-apples numerical comparison.

| # | Query | Saved Visor reported total | Live probe count | Current facet-validator outcome / diagnosis |
|---|---|---:|---:|---|
| 1 | 2023 BMW M4 Competition | 40 | 0 | Old `model=M4` path has no results; current Coupe/Convertible catalog has matching cars. |
| 2 | BMW M4 | 795 | 0 | Same model-name problem. Browser-selected M4 Coupe + Convertible shows 86 used 2023 cars. |
| 3 | BMW M4 Competition | 428 | 0 | Same model-name problem; Competition and Competition xDrive must both be included. |
| 4 | BMW M4 Competition xDrive | 0 | 0 | Same model-name problem; the manual 2023 combined-body-style page exposes 53 Competition xDrive cars. |
| 5 | Porsche 911 | 2,443 | 155 | Valid data parsed, but rejected because the title is now generic. |
| 6 | Porsche 911 Carrera | 1,095 | 0 | Generic-title gate prevents alias discovery; Carrera is now also a model-family member, not simply an old trim string. |
| 7 | Porsche 911 Carrera S | 162 | 0 | Same title/model-plus-trim resolution problem. |
| 8 | Bentley Continental GT | 572 | 29 | Probe accepted; source median $215,795. No parser discrepancy found in this slice; completeness unproven. |
| 9 | Bentley Continental GT Speed | 0 | 7 | Probe for `version=Speed` accepted, median $229,900. Current alias resolution works for this slice; old zero result is not evidence of no supply. |
| 10 | Ford Mustang GT | 5,987 | 49 | First resolved GT Premium version accepted, median $39,778; fixed alias cap remains a coverage risk. |
| 11 | Honda Civic | 32,062 | 1,464 | Valid data rejected by generic-title gate; median $24,280 is present in source data. |
| 12 | Honda Civic EX | 1,848 | 140 | Same title-gate rejection; source median $23,777. |
| 13 | Mercedes-Benz C-Class C300 | 5,755 | 5,808,332 | Numeric trim request returns an unrelated broad-market payload. Current title guard rejects it; must not loosen that guard without replacing its safety checks. |
| 14 | Toyota Camry | 55,007 | 2,094 | Probe accepted; source median $24,667. No parser discrepancy found in this slice; completeness unproven. |
| 15 | Toyota Camry XSE | 9,893 | 286 | Valid `XSE FWD 2.5L I4` version rejected by decimal-token validation bug; source median $27,213. |
| 16 | Tesla Model 3 Long Range AWD | 229 | 0 | Resolver chooses `Long Range AWD`, but the 2023 version slice is empty. Saved Visor coverage is only 2024-2025 while saved Edmunds rows include 2023. Older-year trim/drivetrain mapping needs verification; do not call this zero market supply. |
| 17 | Lexus LC 500 | 60,109,836 | 5,808,332 | Historical result is contaminated by repeated broad-market payloads. Current probe is rejected; numeric version request still produces the unrelated payload. |
| 18 | Porsche Cayenne GTS | 422 | 24 | `version=GTS` probe accepted; source median $84,795. No parser discrepancy found in this slice; completeness unproven. |
| 19 | Porsche 911 base | No saved result | 21 | Generic-title rejection. `Base` applied across all expanded 911 models is not proof of base Carrera-only scope. Exact membership was not verified. |
| 20 | BMW M3 | No saved result | 845, all used years | Broad live page parsed successfully; follow-up 2023 validation was rate-limited. Year-specific outcome is inconclusive. |

Five representative 2023 probes were accepted, fourteen were rejected or empty, and one was rate-limited. This is a diagnostic outcome count, not an app-wide accuracy score or full-query success rate.

## Confirmed Findings

### P1: Visor Model Catalog Changed

The app emits `model=M4`. Visor's own search now returns **M4 Coupe** and **M4 Convertible**, with model-family/member identifiers. Manually selecting both produced **1,608** results across conditions, including **1,000 used**, **558 new**, and **50 certified**. Narrowing to used 2023 cars produced **86**, with visible trim options of **53 Competition xDrive** and **15 Competition**. The app-generated old-model 2023 URL returned zero.

Visor explicitly displayed a Porsche notice that its OpenSpec catalog changed model/trim names and groupings. The broad 911 query expands into nine model names. A simple global `trim=Base` or `trim=S` is therefore insufficient to distinguish Carrera from Turbo/GT variants.

Evidence: [old M4 query](https://visor.vin/search/filters?make=BMW&model=M4&car_type=used&year=2023), [current combined M4 query](https://visor.vin/search/filters?make=BMW&model_family=4_series&model_family_member=m4_coupe%2Cm4_convertible&car_type=used), [broad 911 query](https://visor.vin/search/filters?make=Porsche&model=911&car_type=used).

### P1: Validation Both Rejects Good Data And Accepts Weak Proof

In `car_compare/sources/visor_facets.py:395`, `_html_confirms_vehicle` rejects every title beginning with `Visor |`. This now rejects valid multi-model 911/Civic pages before their aliases or statistics can be used.

In the same module at line 411, `_html_confirms_applied_value` tokenizes only the expected value, then matches it against mostly raw HTML. `2.5L` becomes `2` and `5l`, but the matcher does not permit the decimal point between them. A controlled local check returned false for `version=XSE FWD 2.5L I4`, true for `version=XSE FWD`, and true for an unrelated anchor containing only `year=2023`. Thus, echoed links are currently sufficient proof, whereas some real selections fail validation.

Do not merely remove the generic-title rejection: it currently prevents the broad-market C300/LC500 responses from entering fresh collections.

### P1: Historical Invalid Results Remain Loadable

Saved Lexus job `881a794e733f482ca22f726bca8106b7` contains **12 copies** of a **5,009,153-car** payload under different years/conditions, totaling **60,109,836**. Their price statistics are identical, including a $37,896.50 median. This is not LC 500 inventory. The generated synthetic rows are nevertheless labeled as Lexus LC 500.

`car_compare/collector.py:185` restores finished result files without a collection-validation version gate. Current fresh-response checks do not retrospectively validate these historical payloads. The three-day cache expiration is separate: the presence of old job files does not prove that TTL enforcement is broken.

Evidence: `data/collector_jobs/881a794e733f482ca22f726bca8106b7/collector_result.json`.

### P1: Edmunds Nationwide Intent Is Not Enforced By The Worker

The app-generated [BMW M4 search](https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&make=bmw&model=m4&year=2015-2026) opened with **87 listings** and **Search radius 25 miles**, using the browser's local ZIP. The URL has no explicit geographic scope. `source_plan.py` describes nationwide search, but `scripts/car_compare_browser_mcp.mjs:318` opens the page and extracts cards without executing a radius-setting/verification step.

Manually selecting the slider maximum displayed Nationwide, but an updated count was not verified before browser control became unavailable. Do not treat 87 as a national count, and do not assert that earlier saved Edmunds jobs all used the same radius.

### P2: Conditions And Model Years Differ Across Sources

Visor collection requests only `used` and one calendar-year `new` slice. Its UI exposes **Certified** separately. The BMW page also exposed 2027 inventory, while `_requested_years` and the new-car request stop at 2026. This means a manually observed all-condition/all-model-year total cannot match the app's Visor scope.

The app already includes used/CPO in its Edmunds target. The Visor omission is a cross-source inconsistency, not proof that certified vehicles are absent from every app source.

### P2: Bounded Sampling And Alias Limits Can Hide Coverage Gaps

Visor's resolver prefers version aliases and truncates to eight matches for most queries or sixteen for configured families. The live Mustang GT response fills all eight version slots. This audit did not quantify the additional matching aliases beyond that cap, so the exact loss is unmeasured.

Browser collection intentionally uses five broad-range pages and at most four targeted follow-ups. Saved Mustang GT had 14 accepted Autotrader rows and 14 Edmunds rows; Camry XSE had six each. Several runs stopped with `combined_capture_complete` despite sparse source-local years. These are samples, not exhaustive inventories. Increasing retries without better scope and coverage reporting will not make them representative.

Autotrader was accessible in this audit: its app-generated BMW M4 page showed **463 Matches**. See More Results worked; afterward 36 rendered M4 listing links represented 35 unique links. This disproves a blanket claim that the site cannot currently be opened, but does not certify unattended worker access or full extraction on another host. The historical app result's 429 accepted rows cannot be used as recall against today's 463 matches.

### P2: Price Provenance And Baseline Policy Need Clear Boundaries

Synthetic histogram observations approximate a source distribution; their median is not guaranteed to equal the source's exact reported median. In a same-payload report replay, the saved 2023 Continental GT source median was **$219,993**, while the app's reconstructed median was **$220,991.50**. The saved Cayenne GTS source median was **$90,500**, versus **$91,244.50** reconstructed. These differences are explainable approximation, not fresh-market movement.

The 2023 M4 Competition replay also produced an age-zero value of **$78,600** with `confidence=msrp_reference`, despite the previous requirement that MSRP be reference-only. `_age_zero_bucket` still allows this when no age-zero rows exist. This must not be presented as an observed new-market baseline.

## Proposed Fix Plan

### 1. Replace Source Identity And Scope Validation First

- Introduce a source selection record containing requested identity, resolved model members/versions, selected years, conditions, geography, capture time, and adapter/validation revision. Pass it from planning through capture, validation, caching, and report evidence.
- Resolve current Visor model-family members from the site's public catalog/UI instead of assuming the normalized app model is the source model name. Preserve the app's existing all/family/base/exact intent. For M4 include Coupe and Convertible; for Competition include xDrive and verified historical ZCP, excluding CS/CSL/GTS. For 911 Carrera resolve Carrera model members first, then applicable trims; for 911 base restrict to base Carrera coupe/cabriolet, not Base across every 911 member.
- Validate the actual selected-filter state associated with the result payload. Generic titles may be accepted only with verified model scope. Request URLs, unrelated links, and facet-option availability alone must not validate a filter.
- Normalize both expected and observed selection values consistently. Cover decimal engines, punctuation, AWD synonyms, and numeric model/trim values. Do not stringify numeric source values with the wrong type.
- If source selection cannot be proven, report a filter mismatch/unverified source and exclude its aggregates from calculations. Preserve the evidence for diagnosis rather than treating failure as zero supply.

### 2. Align Geography, Conditions, Years, And Coverage

- Add executable source preparation before extraction: set nationwide/all-distance using observed site controls, wait for result refresh, then record and verify the actual radius. If national scope is unavailable, label the source local/partial and exclude it from the national aggregate unless the user explicitly requests local analysis.
- Collect used plus certified as disjoint used-market conditions where the source separates them. Discover available model years rather than stopping new inventory at the calendar year; retain actual year and condition on each record. Preserve explicit target-year queries. Keep future-model-year used vehicles out of age-zero new-market statistics and disclose their separate inventory count.
- Remove silent alias truncation. Prefer a verified source-side union; otherwise queue all matching disjoint aliases under the existing job budget and report unfinished partitions. Do not sum overlapping alias totals as unique cars.
- Keep the current five-page/four-follow-up default for speed, but expose total advertised, priced, examined, accepted, unique individual, and aggregate-represented counts separately. Mark incomplete sources and years explicitly. A complete combined sample is not a complete crawl.
- Apply a shared per-host concurrency limit of two, honor Retry-After, and use a 60-second cooldown when a 429 provides none. Do not cache rate limiting, filter mismatch, loading shells, or unverified zero results as successful empty inventory.

### 3. Quarantine Old Invalid Data And Separate Price Meanings

- Increment capture/research-result cache revisions when the scope/validation contract changes; retain the three-day maximum TTL. Cache by resolved scope and adapter revision, not just the user query.
- On restoring legacy jobs, preserve files but flag their validation status as legacy/unverified. Quarantine demonstrably broad or repeated-scope payloads, including the Lexus job, from pricing. Revalidate from sufficient stored evidence or recollect; never silently relabel old data as fresh.
- Preserve exact per-source medians as exact source statistics. Label histogram-pooled medians as estimates and individual-listing medians as sample medians; do not claim the pooled median equals each source median or compute an exact pooled median by averaging medians. Keep the current estimator until a separately validated statistical replacement is chosen.
- Remove MSRP as a computational fallback. Use observed age-zero new-market data; otherwise use the existing used-market-based estimate with an estimated label when support exists, or leave baseline-dependent depreciation unavailable. Keep MSRP in its separate informational field. Graphs and tables must use the same curve/baseline fields.

### 4. Regression And Deployment Acceptance

- Add captured, sanitized fixtures for all 20 queries and all confirmed source-shape failures. Include old/new BMW taxonomy, generic valid Porsche/Civic titles, numeric broad-market responses, decimal Camry versions, and legacy identical multi-year payloads.
- Unit-test that unrelated link echoes never prove selected scope; exact verified selections do. Test zero results separately from loading, blocked, schema-change, and rate-limit responses.
- Test 911 all/family/base/exact membership and M4 Competition/ZCP exclusions with positive and negative listing evidence. Verify older Tesla Long Range AWD mapping using explicit drivetrain evidence before expanding aliases.
- Browser-test fresh profiles and different host ZIPs: both must either reach the same nationwide scope or return an explicit scope failure. Verify Next/Load More adds unique records, sponsored duplicates do not inflate counts, and changing a filter invalidates prior evidence.
- Run a same-session 20-query benchmark against the actual app after implementation, using matching years/conditions/geography and one captured snapshot as the oracle. Compare every accepted card in the captured pages for year, trim, price, and identity; compare parsed aggregate counts and exact source medians to that same snapshot. Keep exhaustive-market recall separate from captured-page accuracy.
- Require the existing 199 tests plus new regressions to pass, no contaminated aggregate accepted, no unverified zero labeled successful, no MSRP-derived depreciation, and graph/table arithmetic agreement to displayed rounding precision. Network-blocked benchmark cases remain explicitly inconclusive, not passes.
- Document adapter revisions, cache invalidation, the source scope contract, fixture reproduction, and host-browser requirements in the deployment/always-awake handoff guides. Validate on the deployment host before publishing; this audit did not inspect its live database.

## Recommended Order

First fix validation and catalog resolution together, then executable nationwide scope and condition/year coverage, then legacy/cache migration and price labeling/baselines. Finally rerun the same 20-query benchmark. Do not start by raising page counts: that would collect more data under currently unreliable filters.
