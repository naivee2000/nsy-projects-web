# Auto CAD Drawing

Local CAD-generation workspace for DONJUN-style PDF-to-CAD workflows.

## Current State

- `STK333-AR2` level-sensor drawings are implemented as a reusable Python + `ezdxf` generator.
- `CPX26051` and the CPX25034 page-171 STK333-AR2 tank-level sheet are normalized project configurations using that reusable level-sensor generator.
- The generator creates editable DXF files plus PNG/PDF proof renders.
- Other STK333-AR2 occurrences are screened and only routed when they match a supported level-sensor fixture. Pressure-sensor STK333-AR2 pages are intentionally not handled by the level-sensor generator.

## Key Files

- `data/cpx26051_sensors.json` - normalized CPX26051 sensor/channel input.
- `data/cpx25034_stk333_ar2_sensors.json` - normalized CPX25034 STK333-AR2 tank-level sheet input.
- `data/device_models.json` - reusable sensor model library, currently including `STK333-AR2`.
- `scripts/level_sensor_generator.py` - reusable level-sensor DXF/proof generator.
- `scripts/generate_level_sensor_project.py` - generates any registered level-sensor project.
- `scripts/generate_cpx26051.py` - CPX26051 compatibility wrapper around the reusable generator.
- `scripts/verify_level_sensor_project.py` - validates reusable level-sensor project data.
- `scripts/verify_cpx26051.py` - validates counts, LT ranges, terminal sequence, and generated files.
- `scripts/scan_reference_pdfs.py` - summarizes PDFs under this project folder.
- `scripts/screen_sensor_models.py` - screens all project PDFs for sensor model hits and page context.
- `scripts/generator_registry.py` - routes analyzed PDFs to supported generators.
- `scripts/test_reference_handling.py` - checks that known sample PDFs are detected safely.
- `scripts/check_deploy_package.py` - checks deployable folder structure, dependencies, and readiness.
- `scripts/smoke_test_app.py` - checks a running local/deployed API.
- `scripts/run_checks.py` - runs the local regression suite.
- `scripts/clean_runtime.py` - removes caches and ignored runtime job output.
- `app.py` - local launcher; run this directly for browser use.
- `web/app.py` - local FastAPI UI for upload/generate/download.
- `GET /api/readiness` reports deploy readiness checks for data, dependencies, registry, UI files, and baseline outputs.
- `GET /api/setup` reports whether the optional deployment-host Codex advisory is enabled, installed, and logged in.
- `GET /api/jobs` and `GET /api/jobs/{job}/manifest` expose runtime job history.
- `Dockerfile` - deployable container entrypoint.
- `docs/deployment.md` - deployment and API integration notes.
- `output/cpx26051/` - checked CPX26051 baseline outputs.
- `output/cpx25034/` - checked CPX25034 STK333-AR2 baseline outputs.
- `output/web_jobs/` - local runtime jobs, ignored by git.

## Commands

```bash
python3 -m pip install -r requirements.txt
python3 scripts/generate_cpx26051.py
python3 scripts/generate_level_sensor_project.py CPX25034
python3 scripts/verify_level_sensor_project.py
python3 scripts/verify_level_sensor_project.py --data data/cpx25034_stk333_ar2_sensors.json --output-dir output/cpx25034 --require-proofs
python3 scripts/verify_cpx26051.py --require-proofs
python3 scripts/scan_reference_pdfs.py
python3 scripts/screen_sensor_models.py --term STK333-AR2
python3 scripts/test_reference_handling.py
python3 scripts/check_deploy_package.py
python3 scripts/deploy_preflight.py --require-codex
python3 scripts/run_checks.py
python3 app.py
python3 scripts/smoke_test_app.py --base-url http://127.0.0.1:8008
python3 scripts/run_checks.py --base-url http://127.0.0.1:8008
python3 scripts/clean_runtime.py
```

Then open `http://127.0.0.1:8008`.

If you want the old explicit server command, this is equivalent:

```bash
python3 -m uvicorn web.app:app --host 127.0.0.1 --port 8008
```

## Boundary

Keep all CAD app work inside this `projects/Auto-CAD-Drawing` folder. Do not edit sibling project folders when extending this workflow.

The local UI classifies uploads before generation. `CPX26051` and the CPX25034 cargo-safety final drawing are currently supported through the reusable `level_sensor` generator and `STK333-AR2` model library. CPX25034 supplement/agreement PDFs are reference-only unless uploaded with the recognized final drawing package. `CPX25063` is detected but intentionally blocked until a dedicated template is implemented.

For the `cad.nsyprojects.com` deployment, set `AUTO_CAD_CODEX_ADVISORY=1`. When the deterministic router rejects an upload, Codex can return a read-only explanation and recommended next step. That advisory never unlocks a generator or substitutes one project's drawings for another.
