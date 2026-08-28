# DEM Claim Deployment

Last updated: 2026-06-20

This document explains how the DEM claim app is expected to run from a Git checkout.

## Current Shape

- Repo root: `nsy-projects-web`
- Public site folder: `web_ui/`
- DEM project folder: `projects/dem-claim/`
- DEM app folder: `projects/dem-claim/app/`
- Public site: `https://nsyprojects.com/`
- DEM app URL: `https://dem.nsyprojects.com/`
- Public backend entrypoint: `projects/dem-claim/app/app_zh_secure.py`
- Local no-login entrypoint: `projects/dem-claim/app/app.py`
- Backend upload/output retention: 24 hours by default

The DEM app is served from an always-on Mac through Cloudflare Tunnel. Do not publish the raw local app without an auth layer.

## GitHub Versus Local Runtime

GitHub carries the shared source code and docs. Each computer keeps its own private runtime setup outside the repo:

- Codex login and `~/.codex/auth.json`
- `~/.codex/skills/dem-claim-excel`
- Tesseract
- `app/.venv/`
- generated `app/web_outputs/`
- PM2 secrets
- Cloudflare tunnel credentials

The app's fallback path calls local `codex exec`, so fallback uses the Codex account on the computer that is running the backend.

## Install From Git On Another Mac

```bash
git clone https://github.com/naivee2000/nsy-projects-web.git
cd nsy-projects-web/projects/dem-claim/app
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

Install Tesseract if it is not already installed:

```bash
brew install tesseract
```

Make sure Codex is installed and logged in on that computer. The fallback path uses local `codex exec`; it does not use a committed API key.

## Verify Local Dependencies

```bash
cd "$HOME/.codex/skills/dem-claim-excel"
python3 scripts/dem_claim_setup_check.py
```

From the app venv, `/api/setup` should report:

- `skill_root_ok`
- `codex_ok`
- `codex_auth_ok`
- `tesseract_ok`
- `packages_ok`

## Run Local App Without Login

```bash
cd /path/to/nsy-projects-web/projects/dem-claim
./run_local_app_mac.sh
```

Open:

```text
http://127.0.0.1:8000
```

The app should open directly as `装卸时间计算表`. There should be no local login gate when using `app.py`.

## Run Secure Chinese App Locally

Use this when testing the public-auth version locally:

```bash
cd /path/to/nsy-projects-web/projects/dem-claim/app
DEM_SKILL_ROOT="$HOME/.codex/skills/dem-claim-excel" \
DEM_JOB_ROOT="$PWD/web_outputs" \
CODEX_BIN="/Applications/Codex.app/Contents/Resources/codex" \
DEM_AUTH_USERNAME="admin" \
DEM_AUTH_PASSWORD_HASH="pbkdf2_sha256$..." \
DEM_SESSION_SECRET="replace-with-a-long-random-secret" \
DEM_COOKIE_SECURE=0 \
./.venv/bin/python -m uvicorn app_zh_secure:app --host 127.0.0.1 --port 8000
```

Do not store the raw password, password hash, or session secret in GitHub. Put them in the deploy computer's private PM2/env config.

## Public Deployment Pattern

- Static website: Cloudflare Pages project `nsy-projects`
- Static domain: `https://nsyprojects.com/`
- Backend domain: `https://dem.nsyprojects.com/`
- Backend process: PM2 app `nsy-dem-app`
- Tunnel process: PM2 app `nsy-dem-tunnel`
- Backend entrypoint: `app_zh_secure:app`
- Tunnel service target: `http://127.0.0.1:8000`

Use `projects/dem-claim/ops/` for safe templates. The live PM2 config and Cloudflare tunnel credentials should stay private on the deploy computer.

Useful checks:

```bash
pm2 status nsy-dem-app nsy-dem-tunnel
curl -I https://dem.nsyprojects.com/
curl -s https://nsyprojects.com/projects | head
```

For `/api/setup` on the public backend, authenticate first or use a browser session.

## Verification Checklist

- `GET /` returns app HTML.
- `GET /api/setup` returns healthy setup JSON.
- Local unauthenticated mode does not include `/login` or `/projects`.
- Secure public mode redirects unauthenticated users to `/login`.
- Uploading a loading file and discharge file creates a task and eventually produces an Excel download.

Test files live under `app/Test Load:Discharge Documents/`:

- OCR-only: `Load1.png` plus `Discharge1.png`.
- Codex fallback: `Load3.png` plus `Discharge3.png`.

## Backend Data Retention

- Uploaded files, OCR debug output, extraction JSON, and generated Excel files live under `app/web_outputs/<job_id>/` while active.
- Cleanup runs once at backend startup and then every hour by default.
- Jobs and orphaned job folders older than `DEM_JOB_RETENTION_HOURS` are deleted. Default: `24`.
- Change the scan interval with `DEM_JOB_CLEANUP_INTERVAL_SECONDS`. Default: `3600`.
- The UI `删除` action deletes the job folder immediately.
- `Download All` temporary zip files are deleted after the response.

## Important Fallback Fix

Do not remove this line in `app/app.py` inside `run_command()`:

```python
stdin=asyncio.subprocess.DEVNULL,
```

It prevents `codex exec` from waiting for inherited stdin. If fallback hangs:

1. Check for stuck Codex child processes:

```bash
ps -axo pid,etime,command | rg "codex exec"
```

2. Confirm the job is stuck in `codex-reading` and has no `codex_extraction.json`.
3. Confirm `stdin=asyncio.subprocess.DEVNULL` is still present.
4. Run a tiny Codex CLI smoke:

```bash
"/Applications/ChatGPT.app/Contents/Resources/codex" exec \
  --ignore-user-config --ephemeral --ignore-rules --skip-git-repo-check \
  -m gpt-5.6-terra -c model_reasoning_effort="medium" \
  --sandbox read-only 'Return exactly OK.'
```

## Boundaries

- Keep the DEM project under `projects/dem-claim/`.
- Keep the static website under `web_ui/`.
- Keep auth/session logic in `app/auth_gate.py` and `app/app_zh_secure.py`; do not put website auth into `app/app.py`.
- Static website cookies are display state only. Backend session cookies enforce real DEM access.
- Do not expose the local app publicly unless the secure wrapper or another real auth layer is enabled.
