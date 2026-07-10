# Deployment Notes

This project is deployable as a FastAPI web app from inside `projects/Auto-CAD-Drawing`.

## Runtime

- Python 3.12+
- `requirements.txt`
- Web entrypoint: `web.app:app`
- Default port: `8008`
- Public hostname: `https://cad.nsyprojects.com/`
- Local command:

```bash
python app.py
```

- Production command:

```bash
python -m uvicorn web.app:app --host 0.0.0.0 --port ${PORT:-8008}
```

## Docker

```bash
docker build -t auto-cad-drawing .
docker run --rm -p 8008:8008 auto-cad-drawing
```

Then verify:

```bash
python scripts/smoke_test_app.py --base-url http://127.0.0.1:8008
python scripts/run_checks.py --skip-generate --base-url http://127.0.0.1:8008
```

## Current Support

- Supported reusable generator: `level_sensor`.
- Supported sensor model: `STK333-AR2`.
- Supported project configurations: `CPX26051`, `CPX25034` page-171 STK333-AR2 tank-level sheet.
- CPX25034 supplement/agreement PDFs are reference-only unless the recognized cargo-safety final drawing PDF is included.
- Detected but intentionally blocked until implemented: `CPX25063`.

The app should never return one project's drawings for a different uploaded project. Upload routing must classify PDFs first and return a clear unsupported response when no normalized data/template exists.

## Website Integration Shape

- `GET /api/health` - basic health check.
- `GET /api/readiness` - deploy readiness checks for normalized data, device model library, Python dependencies, generator registry, UI files, and baseline CAD/proof outputs.
- `GET /api/setup` - deployment-host Codex CLI/login/advisory status.
- `GET /api/capabilities` - supported generators, sensor models, and known project IDs.
- `GET /api/reference-pdfs` - local reference scan, useful in development.
- `POST /api/jobs` - upload one or more PDFs and generate a ZIP when supported.
- `GET /api/jobs` - recent runtime jobs.
- `GET /api/jobs/{job}/manifest` - one job manifest.
- `GET /api/jobs/{job}/download` - download the generated ZIP.

Runtime job output lives under `output/web_jobs/` and is ignored by git.

## Codex Deployment Boundary

Set `AUTO_CAD_CODEX_ADVISORY=1` only behind authenticated access. Rejected uploads can then receive a server-side Codex explanation based on the deterministic PDF summary. Codex remains read-only and cannot override the generator registry.

The browser visitor does not need Codex. Install and log in to Codex as the operating-system account that runs the backend, then verify:

```bash
codex login status
python scripts/deploy_preflight.py --require-codex --smoke-codex
```

The runtime finds the CLI through `CODEX_BIN`, `PATH`, official standalone install locations, or supported desktop app bundles. Keep the origin on `127.0.0.1`; expose it only through the authenticated NSY Projects reverse proxy/tunnel described in `../../../ops/README.md`.

## Maintenance

Use this before committing or handing the folder to another machine:

```bash
python scripts/run_checks.py
python scripts/check_deploy_package.py
python scripts/clean_runtime.py
```

`clean_runtime.py` removes Python caches, temporary PDF renders, and `output/web_jobs/`. It does not remove checked baseline outputs in `output/cpx26051/` or `output/cpx25034/`.
