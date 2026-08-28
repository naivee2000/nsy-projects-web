# NSY Projects Web

This repository holds the public NSY Projects website and the backend project apps that sit behind it.

## Layout

- `web_ui/` - static website files for Cloudflare Pages at `https://nsyprojects.com/`.
- `projects/` - one folder per backend or tool project.
- `projects/dem-claim/` - DEM claim Excel workflow, including its FastAPI app, local runner, deployment notes, ops templates, and test files.
- `projects/Car Compare/` - authenticated vehicle depreciation research app for `https://carcompare.nsyprojects.com/`, including its browser workers, project skills, cache layer, deployment guide, and tests.
- `projects/Stock Strategy Test/` - public Long-Term Stock Allocation Lab for `https://strategy.nsyprojects.com/`, including safe public backtests, fixture data, an owner-only Market Data history vault, deployment guide, and tests.

Future projects should be added as `projects/<project-slug>/` so each project keeps its own app code, docs, tests, and deployment notes in one place.

## Important Runtime Boundary

GitHub stores the shared project code. Each computer still keeps its own private runtime setup outside Git:

- Codex app/CLI login and `~/.codex/auth.json`
- installed project Codex skills under `~/.codex/skills/`
- Car Compare Chrome/Playwright profile and Apple Events permission
- Tesseract install
- Python virtual environments
- PM2 secrets, Cloudflare tunnel credentials, caches, logs, uploads, collector evidence, and generated outputs

Both backend projects run local Codex processes on the computer that deploys or tests the app. That is intentional. Do not commit Codex credentials, shared session secrets, browser state, or Cloudflare credentials to this repo.

## Working Across Computers

Before editing on either computer:

```bash
git pull
```

After editing:

```bash
git add .
git commit -m "Describe the change"
git push
```

On the deploy computer, pull the latest code and restart the backend process that changed:

```bash
git pull
# Run the command for the backend that changed:
pm2 restart nsy-dem-app
pm2 restart nsy-car-compare --update-env
pm2 restart nsy-stock-strategy --update-env
```

Deployment entrypoints:

- `projects/dem-claim/docs/DEPLOYMENT.md`
- `projects/Car Compare/docs/DEPLOYMENT.md`
- `projects/Stock Strategy Test/docs/DEPLOYMENT.md`

For Car Compare, the deploy computer should also run `python3 scripts/benchmark_search_accuracy.py` from `projects/Car Compare`. The current acceptance record, seven browser samples, and runtime limits are in `projects/Car Compare/docs/PERFORMANCE_ACCURACY_BENCHMARK.md`. Production should keep `CAR_COMPARE_CODEX_COLLECTION_REVIEW=0`; deterministic collection remains enabled and automatic generation-impact research is unaffected.
