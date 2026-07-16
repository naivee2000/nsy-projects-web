# Search Accuracy And Runtime Benchmark

Last verified: 2026-07-16

This is the acceptance record for the optimized marketplace collector. A deployment is expected to preserve the deterministic benchmark and bounded collection strategy below. Live marketplace counts can change; exact row counts are evidence from this run, not permanent quotas.

## Acceptance Targets And Results

| Measure | Baseline | Verified result | Required target |
| --- | ---: | ---: | ---: |
| Audited title classification | 44/60 (73.33%) | 60/60 (100%) | At least 88% |
| Relative accuracy improvement | - | 36.37% | At least 20% |
| Cold BMW M4 Competition browser run | 13:58 (838 s) | 2:36 (156 s) | At most 9:46 (586 s) |
| Runtime reduction | - | 81.4% | At least 30% |

The classification fixture contains 60 realistic marketplace labels across seven vehicles. It covers missing-make scoped cards, attached model terms, exact neighboring trims, Porsche Carrera aliases, M4 ZCP evidence, and Tesla Long Range AWD context.

## Seven User-Like Browser Runs

Each query was entered through the app UI at `http://127.0.0.1:8788/` with a 10-year horizon and the normal `Collect & Research` action.

| Query | UI elapsed | Individual rows in report | Aggregate vehicles represented | Audit note |
| --- | ---: | ---: | ---: | --- |
| BMW M4 Competition | 2:36 | 32 | 414 | Competition family retained; Base, CS, and GTS boundaries stayed excluded |
| Porsche 911 Carrera | 5:57 | 83 | 901 | Carrera family included S, T, 4/4S, GTS, coupe, and cabriolet variants |
| Honda Civic EX | 2:21 | 8 | 1,678 | EX rows retained without EX-L or EX-T contamination |
| Ford Mustang GT | 1:22 | 28 | 5,285 | GT and GT Premium retained; Shelby variants stayed excluded |
| Mercedes-Benz C-Class C300 | 2:13 | 30 | 5,465 | C300 retained without C300 4MATIC drift |
| Toyota Camry XSE | 1:52 | 12 | 9,376 | Every accepted individual title was XSE |
| Tesla Model 3 Long Range AWD | 3:21 | 28 | 221 | Final filter preserved AWD evidence from the same listing block |

Median end-to-end UI time was 2:21. Mean time was about 2:49. Porsche Carrera is intentionally broader than an exact trim and resolves more Visor version aliases, so it is the slowest sample.

## What Changed

- Audited marketplace pages may omit the make from each card when the page itself is make/model scoped.
- Common deterministic aliases include `Comp`, M4 `ZCP`, Porsche `C2/C2S/C4/C4S`, Tesla `LR`, and `Dual Motor`.
- A 2016-2020 M4 row needs factory ZCP/Competition Package evidence; text saying the package is merely available is rejected.
- Requested drivetrain evidence found later in the same listing block is preserved in the normalized trim before final validation.
- Same-source detail rows and broad-page summary echoes merge only when one side has a detail identity and year/title/price agree. Two different detail URLs remain separate cars.
- Autotrader and Edmunds begin with broad range pages, capped at five pages per source.
- There is one targeted follow-up round, capped at four sparse year pages.
- Regular host Chrome runs only for a blocked, unavailable, or empty source and uses one broad range capture rather than another year-by-year crawl.
- Native Codex indexed recovery is capped at four critical years with fewer than two individual rows and no aggregate support.
- The optional Codex collection review is disabled by default. Generation-impact research remains automatic and separate.

## Reproduce On Another Computer

From `projects/Car Compare`:

```bash
npm install
npm exec playwright install chromium
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/benchmark_search_accuracy.py
node scripts/car_compare_browser_mcp.mjs --self-test
python3 -m compileall -q app.py car_compare scripts
python3 scripts/deploy_preflight.py --smoke-browser --desktop-fallback
```

The benchmark command must report `accuracy: 1.0`, `relativeImprovement` of at least `0.20`, zero false positives, and zero false negatives. The full suite contained 196 passing tests at this verification point.

For a live timing comparison, use an empty temporary cache and the same query/horizon. Do not delete the production cache:

```bash
CAR_COMPARE_CACHE_DIR="$(mktemp -d /tmp/carcompare-benchmark.XXXXXX)" \
CAR_COMPARE_CODEX_COLLECTION_REVIEW=0 \
python3 app.py --host 127.0.0.1 --port 8788
```

Marketplace access is variable, so a live run may be partial. Accuracy is determined by accepted evidence and truthful source status, not by inventing rows when a site refuses access.
