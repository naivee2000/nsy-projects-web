# Verified Market Migration

Local implementation checkpoint: October 30, 2026. This supersedes the pricing proposals in the October 28 audit. Changes remain local and are not approved for production. Live source acceptance and the full twenty-query comparison are still blocked/incomplete.

## Revision Contract

| Boundary | Required revision |
| --- | --- |
| Collection scope validation | 3 |
| Report analysis | 3 |
| Marketplace capture cache schema | 6 |
| Research cache schema | 5 |

Build scope fixtures with `car_compare.collection_scope.verified_scope`; do not duplicate an older revision literal in fixtures. A verified scope binds evidence to the canonical query key and nationwide geography, carries the original capture timestamp, and identifies its validation revision and status. Aggregate pricing additionally requires `scope.complete` to be exactly `true`.

Old cache files may be retained, but must not be relabeled as newly verified evidence or copied into the new schema. Cache replay must preserve capture age and enforce scope/query compatibility. Report producers, summaries, comparisons and cache consumers must agree on analysis revision 3 before release; the version table is a requirement, not proof that all integration paths have been checked.

## Partition Contract

`scope.partition_manifest` is a list of entries with `id`, `year`, `condition` and `status`. Each nonempty aggregate snapshot carries its own `scope.partition_key`, matching the entry's `id`. Identity is the tuple of year, condition and partition key, not the key alone. `certified` is normalized to `cpo` for matching.

- `successful`: verified nonempty partition; its aggregate snapshot must be present.
- `verified_empty`: verified zero inventory; no price snapshot is required and no synthetic zero-price observation is created.
- `failed`: attempted collection without acceptable evidence; blocks the affected combined population.
- `unattempted`: not collected, including deadline exhaustion; also blocks the affected combined population.

The manifest covers the whole population being priced. Used and certified partitions for a model year belong to the same completeness decision. A failed or unattempted certified partition cannot silently leave a used-only aggregate labeled complete. New inventory completeness spans all included model years and source model partitions, including next-model-year inventory.

Every successful manifest identity must have a corresponding snapshot, and every accepted snapshot identity must be declared successful. A missing successful partition, wrong year/condition/key, or `scope.complete: false` excludes that aggregate population. A verified-empty companion partition is not missing data: one remaining successful partition can retain its exact source median. Duplicate copies of the same partition must not increase counts.

## Pricing Contract

- Age 0 requires verified new inventory, not simply inventory whose model year equals the current year. Verified new inventory can span model years. Current-year used/CPO inventory is disclosed separately. MSRP is reference-only, never an inferred baseline.
- Without new inventory, baseline-relative fields are null. Observed used prices, adjacent-year changes and supported forecasts remain available.
- One complete verified nonempty aggregate partition uses its exact median. Multiple disjoint partitions require complete compatible histograms: identical bin boundaries, no overlapping bins within a histogram, and bin counts matching the partition's price count. Their pooled median is explicitly a `pooled_histogram_estimate`, not an exact median or a count-weighted average of source medians.
- Missing or incompatible histograms exclude aggregate pricing. Independently acceptable individual samples may still support a sample median; unavailable aggregate evidence must not be repaired by averaging medians or inventing histogram detail.
- Separate marketplaces can overlap, so their aggregate populations are alternatives, not additive counts. Repeated partitions and overlapping version populations must not be double counted.
- Synthetic aggregate rows remain evidence, not individual listings or an extra population to blend with listings. Tiny samples cannot normalize aggregate medians.
- Verified aggregate medians remain authoritative through report construction: MSRP, tiny individual samples and curve normalization must not move them. Baseline-relative changes use the verified new-inventory median.
- Charts must use backend signed change fields. Comparison reports must reject mixed analysis revisions; those integration paths remain release checks below.

## Collection And Cache

The Visor discovery contract is the union of matching source model names from new, used and certified catalogs, deduplicated across catalogs. Tests mock all three responses with structured `queryHash` state. Titles, arbitrary links and facet option lists alone are not proof of an applied make/model/condition selection.

Trim resolution must preserve the requested population. In particular, Porsche 911 Carrera S under the source model `911 Carrera` must select trim `S`, not `4S` and not the unfiltered Carrera model. Source-specific aliases, parent counts, filtered counts and discovered new model years still require broader integration verification.

Browser and manual-repair producers must prove nationwide scope, applied filters and refreshed results before evidence is accepted. Legacy or unverified captures must fail closed. These are requirements for the independently edited browser/runtime and collector paths, not behavior certified by the focused Python tests.

The collection deadline starts at job creation and is shared by discovery, browser queue waits, primary work and automatic fallbacks. Owned subprocess groups are terminated on timeout or cancellation. Verified page checkpoints are written atomically and recovered after a worker timeout; older captures cannot masquerade as the current worker's checkpoint. An optional Codex review has no browser MCP attached and is review-only.

`CAR_COMPARE_REQUEST_BUDGET_DB` coordinates two active operations per source across jobs/processes on one host and shares Retry-After cooldowns. All service workers must use the same path. This is not a distributed multi-host coordinator. The browser worker caps initial searches at five pages and targeted searches at two pages, with four targeted searches per job. Host-Chrome and indexed fallback use the remaining allowance instead of resetting it. Indexed candidates remain discovery-only.

The report exposes `partitionManifest`, `aggregateCoverage`, and per-snapshot `pricingStatus`/`pricingReason`. `aggregateMarketCount` is the population actually selected for pricing, not the sum of raw snapshots or synthetic observation rows. `rawAggregatePopulationCount` is an audit-only raw sum and is not a unique-car total. Browser sample counts remain separate.

Manual repair is a separately authorized, expiring lease after an automatic job finishes. Revision 3 imports bind `requested_scope`, `query_key`, `result_refresh_confirmed`, `verification_method: supervised_visible_controls`, and the original capture time to that lease. This is supervised attestation, not automatic machine proof. Do not use it to label indexed snippets verified.

## Verification And Remaining Work

Focused offline verification on October 29, 2026:

```sh
python3 -m unittest discover -s tests -p test_partition_integrity.py -v
```

Result: **25 tests passed** against the current in-progress local code. The test module mocks marketplace fetches and rejects socket connections. Fixtures use the rev3 `verified_scope` helper. Coverage includes trim separation, three-condition catalog union, structured scope rejection, manifest identity/completeness, verified-empty partitions, failed/unattempted CPO, missing successful partitions, compatible histogram pooling, duplicate/overlap prevention, sample fallback and new-baseline median invariants.

Integrated checks on October 30: **246 Python tests passed**, **11 browser-scope JavaScript tests passed**, browser worker self-test passed, and the host-Chrome AppleScript compiled against the installed Chrome dictionary. Process tests include cancellation, expired deadlines, shared cooldowns, another process respecting the two-operation cap, and monotonic-clock behavior. Visor HTTP captures now run in owned, cancellable subprocesses with a total request timeout and response-size limit, so slow streaming cannot extend the collection deadline. Python subprocess cleanup tests require normal local process permissions; the restricted runner can reject process-group probes. The portable skill was reviewed and updated, but its optional frontmatter validator could not run because PyYAML is absent from both available Python environments.

The October 29 isolated full-job smoke attempt produced:

| Query | Runtime | Outcome |
| --- | --- | --- |
| BMW M4 Competition | 102.11 s | Blocked; zero verified individual rows |
| Porsche 911 Carrera S | 165.62 s | Partial; three raw aggregate snapshots, zero verified individual rows |
| Toyota Camry XSE | 60.76 s | Blocked; zero verified individual rows |

Visor returned a rate limit; the harness stopped further Visor calls for that session. Browser/fallback paths did not establish accepted individual evidence. Porsche's 40 raw synthetic aggregate observation rows are **not 40 individual listings** and do not establish complete-population pricing. The smoke evidence also exposed duplicate fallback accounting and lost failure diagnostics, fixed locally afterward; those fixes are offline-tested, not certified by that earlier live run.

Evidence was saved outside the checkout under the temporary directory `car-compare-full-smoke-slmy7tvd`. The portable runner is `scripts/smoke_collection_jobs.py`; it creates fresh temporary storage, disables cache reuse, stops affected-source testing after rate limits, and never claims an independent benchmark pass.

The read-only twenty-query inventory inspection on October 30 found 18 saved results and two without saved results. This is **not** twenty completed fresh comparisons. Remaining live queries and same-session independent source comparisons were not completed. No production deployment or recurring monitor was created.

UI checks use explicitly synthetic data. `tests/ui_fixture_server.py --port 8793` serves an isolated offline preview with a verified fixture baseline for BMW and a missing baseline for Toyota; it makes no marketplace or model calls. Never use this server as production. Single-report missing-baseline display and mobile overflow were checked; comparison values and chart labels were checked against the synthetic table. Desktop and 390px mobile comparison screenshots were inspected; the document stayed 390px wide while charts scrolled within their containers. Comparison charts contained 41 and 52 rendered marks. Missing-baseline wording and individual-count labels were corrected during this check. Synthetic values are not market observations.

Release gates still outstanding:

- Rerun the offline checks after any further code changes; retain the current results above as a checkpoint, not blanket release approval.
- Verify analysis revision 3 consistently at every report boundary, comparison path and cache consumer; verify schema 6/5 cache invalidation and original capture timestamps without upgrading stale evidence in place.
- Verify parent-collector propagation of complete manifests, condition normalization and failed/unattempted statuses into reports, including missing and zero-count new model years.
- Exercise browser, manual repair and all legacy host-Chrome/search fallbacks for nationwide scope proof, deadline propagation, host limits and rate-limit handling.
- Perform fresh multi-brand, full-job validation on the deployment host, including source-specific trim aliases, numeric trims and all twenty audit queries. Retain blocked, incomplete and unattempted outcomes rather than labeling the run successful.
- Inspect desktop/mobile reports and comparison mode for signed changes, missing-baseline states, immutable aggregate medians and histogram fallback. Offline helper tests do not establish UI correctness or real-source histogram compatibility.

## Portable Handoff

Keep the project source, package lock, tests, docs and bundled skills together. Follow `DEPLOYMENT.md` and `ALWAYS_AWAKE_HANDOFF.md` for the existing host, authentication and persistent profile setup. A repository edit does not automatically update a globally installed skill. This checkpoint creates no scheduled task and does not restart services.

Additional release checks to run from the Car Compare directory, not checks claimed complete here:

```sh
python3 -m unittest discover -s tests -q
npm run browser:self-test
node --test tests/browser_scope.test.mjs
python3 scripts/audit_twenty_queries.py --output /tmp/car-compare-audit.json
```

The audit is read-only by default; `--live` opts into bounded requests and requires a separately reviewed validation run. Keep blocked, rate-limited and incomplete results explicit. Do not restart the production service until release gates have been reviewed.
