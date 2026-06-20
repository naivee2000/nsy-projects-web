# DEM Claim Project

This folder contains the DEM claim Excel workflow. It is the single home for this project inside the repo.

## What It Does

The app accepts matching loading and discharge documents, reads laytime event dates/times with deterministic OCR first, falls back to local Codex vision when needed, and generates fixed-format Excel claim workbooks.

## Folder Map

- `app/` - FastAPI backend, embedded UI, Chinese wrapper, auth wrapper, OCR bridge code, workbook template, requirements, and test documents.
- `run_local_app_mac.sh` - local no-login runner for development on macOS.
- `ops/` - PM2 and Cloudflare Tunnel notes/templates for public deployment.
- `docs/` - deployment notes and context for another Codex working on this repo.

## Computer-Local Requirements

These are intentionally not stored in Git:

- Codex app/CLI installed and logged in on the computer running the app.
- `dem-claim-excel` skill installed at `~/.codex/skills/dem-claim-excel`.
- Tesseract installed.
- Python virtual environment under `app/.venv/`.
- PM2 auth/session secrets and Cloudflare tunnel credentials.

The app uses the deploy computer's Codex login when fallback OCR calls `codex exec`. GitHub only syncs the code.

## Local Development

```bash
cd projects/dem-claim/app
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
cd ..
./run_local_app_mac.sh
```

Open:

```text
http://127.0.0.1:8000
```

The local runner uses `app.py` and should open directly without a login gate.

## Public Deployment

Public deployment should run `app/app_zh_secure.py` with real environment variables for:

- `DEM_AUTH_USERNAME`
- `DEM_AUTH_PASSWORD_HASH`
- `DEM_SESSION_SECRET`
- `DEM_SKILL_ROOT`
- `DEM_JOB_ROOT`
- `CODEX_BIN`

If the auth variables are missing, `auth_gate.py` intentionally leaves auth disabled. Do not expose the public backend without those variables or another real auth layer.

See `ops/README.md` and `docs/DEPLOYMENT.md` for deploy checks.
