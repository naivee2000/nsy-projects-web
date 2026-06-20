# Codex Context For DEM Claim Project

Use this when another Codex instance opens the repo on another computer.

## Goal

You are working in the `nsy-projects-web` repo. The DEM claim project lives entirely under:

```text
projects/dem-claim/
```

It is a FastAPI app that turns loading/discharge documents into fixed-format Excel claim workbooks. Deterministic OCR runs first. If required fields are missing, the backend calls local `codex exec` with image inputs and asks Codex to produce extraction JSON.

## Important Local Dependency

The app uses the Codex installation and login on the computer running the backend. GitHub does not store that login.

Before testing fallback, confirm:

```bash
cd "$HOME/.codex/skills/dem-claim-excel"
python3 scripts/dem_claim_setup_check.py
```

Then check the app's setup endpoint:

```bash
curl -s http://127.0.0.1:8000/api/setup
```

Expected fields include:

- `skill_root_ok`
- `codex_ok`
- `codex_auth_ok`
- `tesseract_ok`
- `packages_ok`

## Key Files

- `projects/dem-claim/README.md` - project overview.
- `projects/dem-claim/app/app.py` - local no-login FastAPI app and main workflow.
- `projects/dem-claim/app/app_zh.py` - Chinese UI wrapper.
- `projects/dem-claim/app/auth_gate.py` - session-cookie auth gate for public deployment.
- `projects/dem-claim/app/app_zh_secure.py` - public secure entrypoint.
- `projects/dem-claim/app/DEM_CLAIM_TEMPLATE.xlsx` - workbook template.
- `projects/dem-claim/app/Test Load:Discharge Documents/` - sample load/discharge documents.
- `projects/dem-claim/ops/` - safe PM2 and Cloudflare Tunnel templates.
- `projects/dem-claim/docs/DEPLOYMENT.md` - deployment and verification notes.
- `web_ui/` - static public website. Do not put DEM upload/OCR logic there.

## Run Local No-Login App

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

## Public Deployment Boundary

For public use, run `app_zh_secure:app` and provide private runtime environment variables on the deploy computer:

- `DEM_AUTH_USERNAME`
- `DEM_AUTH_PASSWORD_HASH`
- `DEM_SESSION_SECRET`
- `DEM_SKILL_ROOT`
- `DEM_JOB_ROOT`
- `CODEX_BIN`

If the auth variables are missing, `auth_gate.py` leaves auth disabled. Do not expose the backend in that state.

## Known Fallback Fix

Keep this in `app/app.py` inside `run_command()`:

```python
stdin=asyncio.subprocess.DEVNULL,
```

Without it, `codex exec` can wait for inherited stdin and the browser can appear stuck at the Codex reading step.

## Git Workflow

Use GitHub for shared code only:

```bash
git pull
# edit
git add .
git commit -m "Describe the change"
git push
```

Do not commit `.venv/`, `.env`, `web_outputs/`, logs, PM2 secrets, Cloudflare credentials, Codex auth files, or generated customer outputs.
