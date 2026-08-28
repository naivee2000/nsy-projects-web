# Projects

Each project gets exactly one top-level folder here:

```text
projects/<project-slug>/
```

Put that project's app code, docs, local runner scripts, test files, and deployment templates inside its own folder. This keeps the repo easy to scan as more projects are added.

Current projects:

- `dem-claim/` - DEM claim Excel workflow for turning load/discharge documents into fixed-format claim workbooks.
- `Car Compare/` - authenticated vehicle depreciation research workspace served at `carcompare.nsyprojects.com`. Start with `Car Compare/docs/DEPLOYMENT.md` on a website host, `Car Compare/docs/CODEX_CONTEXT.md` for a new Codex task, and `Car Compare/docs/PERFORMANCE_ACCURACY_BENCHMARK.md` for the portable acceptance gate.
- `Stock Strategy Test/` - private stock, call, and put allocation lab served at `strategy.nsyprojects.com`. It includes fixture-mode backtests, a quota-aware personal history vault, and deployment/licensing guidance in `Stock Strategy Test/docs/DEPLOYMENT.md`.
