# NSY Projects DEM App Handoff

Last updated: 2026-06-19

This bundle is for installing, running, testing, and later redeploying the NSY Projects DEM claim Excel app.

## Current Status

- Local app folder: `projects/dem-claim/app/`
- Public site folder: `web_ui/`
- Public site: `https://nsyprojects.com/`
- DEM app URL: `https://dem.nsyprojects.com/`
- Current backend entrypoint for public use: `projects/dem-claim/app/app_zh_secure.py`
- Current unauthenticated local entrypoint: `projects/dem-claim/app/app.py`
- Current PM2 apps on this Mac: `nsy-dem-app` and `nsy-dem-tunnel`
- Current tunnel target: `http://127.0.0.1:8000`
- Backend upload/output retention: 24 hours by default

The DEM app is served from this always-on Mac through Cloudflare Tunnel. Do not publish the raw local app without an auth layer.

## Cleaned Folder Layout

- `web_ui/` - static NSY Projects website files for Cloudflare Pages. Do not put backend app code here.
- `web_ui/projects/<slug>/` - stable public website project entry pages. The DEM page redirects to `https://dem.nsyprojects.com/`.
- `projects/` - local/backend project apps. Add future apps here as `projects/<new-project>/`.
- `projects/dem-claim/app/` - FastAPI DEM upload app, Chinese wrapper, auth wrapper, OCR/workbook bridge code, test files, `.venv/`, and runtime `web_outputs/`.
- `projects/dem-claim/dem-claim-excel-portable.zip` - portable Codex skill package required by the DEM app.
- `projects/dem-claim/run_local_app_mac.sh` - local no-login runner for the DEM app.
- `ops/` - PM2/Cloudflare Tunnel notes and templates.
- `HANDOFF_INSTALL.md` and `PROMPT_FOR_OTHER_CODEX.md` - transfer/install instructions.

## What Is Included

- `projects/dem-claim/app/` - FastAPI DEM upload app, Chinese wrapper, auth wrapper, OCR/workbook bridge code, and test files.
- `web_ui/` - static NSY Projects website for Cloudflare Pages.
- `projects/dem-claim/dem-claim-excel-portable.zip` - Codex skill package required by the app.
- `projects/dem-claim/run_local_app_mac.sh` - convenience script for unauthenticated local testing.
- `PROMPT_FOR_OTHER_CODEX.md` - copy/paste prompt for another Codex instance.
- `ops/README.md` and example files - deployment notes and safe templates.

## What Is Not Included In The Zip

The handoff zip intentionally excludes local-only, generated, or sensitive artifacts:

- Python virtual environments such as `.venv/`
- `__pycache__/`
- generated `web_outputs/`
- `.DS_Store`
- `.wrangler/` caches
- local `.pem` files
- live PM2 config containing auth secrets
- Cloudflare tunnel credentials JSON
- logs under `ops/logs/`
- nested `.zip` upload/build artifacts from `web_ui/`

## Install On Another Mac

Unzip this handoff package, then run:

```bash
cd /path/to/unzipped/nsy-dem-app-handoff
mkdir -p "$HOME/.codex/skills"
unzip -o projects/dem-claim/dem-claim-excel-portable.zip -d "$HOME/.codex/skills"
cd projects/dem-claim/app
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

Install Tesseract:

```bash
brew install tesseract
```

Install and log in to Codex on that computer. The fallback path uses local `codex exec` and the local Codex login, not an OpenAI API key.

## Verify The Skill

```bash
cd "$HOME/.codex/skills/dem-claim-excel"
python3 scripts/dem_claim_setup_check.py
```

## Run Local App Without Login

```bash
cd /path/to/unzipped/nsy-dem-app-handoff/projects/dem-claim
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
cd /path/to/unzipped/nsy-dem-app-handoff/projects/dem-claim/app
DEM_SKILL_ROOT="$HOME/.codex/skills/dem-claim-excel" \
DEM_JOB_ROOT="$PWD/web_outputs" \
CODEX_BIN="/Applications/Codex.app/Contents/Resources/codex" \
DEM_AUTH_USERNAME="admin" \
DEM_AUTH_PASSWORD_HASH="pbkdf2_sha256$..." \
DEM_SESSION_SECRET="replace-with-a-long-random-secret" \
DEM_COOKIE_SECURE=0 \
./.venv/bin/python -m uvicorn app_zh_secure:app --host 127.0.0.1 --port 8000
```

Do not store the raw password in handoff docs. Generate a PBKDF2 hash and put that hash in the runtime environment.

## Public Deployment Pattern

Current production-style setup:

- Static website: Cloudflare Pages project `nsy-projects`
- Static domain: `https://nsyprojects.com/`
- Backend domain: `https://dem.nsyprojects.com/`
- Backend process: PM2 app `nsy-dem-app`
- Tunnel process: PM2 app `nsy-dem-tunnel`
- Backend entrypoint: `app_zh_secure:app`
- Tunnel service target: `http://127.0.0.1:8000`

For the current Mac, the real config lives under `ops/`. The live PM2 config contains auth secrets and should not be published into a general handoff zip. Use the example files under `ops/` as templates when moving to a new computer.

For future apps, keep `nsyprojects.com` as the public site and project directory. Backend tools should each get a specific subdomain, for example `dem.nsyprojects.com`, `invoice.nsyprojects.com`, or `ops.nsyprojects.com`, with Cloudflare Tunnel routing each hostname to the matching local port or server. Static-only projects can remain under `nsyprojects.com/projects/<slug>/`.

Useful live checks:

```bash
pm2 status nsy-dem-app nsy-dem-tunnel
curl -I https://dem.nsyprojects.com/
curl -s https://nsyprojects.com/projects | head
```

## Verification Checklist

Basic:

- `GET /` returns app HTML.
- `GET /api/setup` returns JSON with `skill_root_ok`, `codex_ok`, `codex_auth_ok`, `tesseract_ok`, and `packages_ok`.
- Local unauthenticated mode does not include `/login` or `/projects`.
- Secure public mode redirects unauthenticated users to `/login`.
- Uploading a loading file and discharge file creates a task and eventually produces an Excel download.

Real Chrome tests completed on 2026-06-17:

- Chrome could open `https://dem.nsyprojects.com/`, log in, and show `装卸时间计算表`.
- OCR-only test: `Load1.png` plus `Discharge1.png` completed in about 25 seconds and produced a valid `.xlsx`.
- Codex fallback test: `Load3.png` plus `Discharge3.png` first failed deterministic OCR, then Codex fallback completed in about 35 seconds and produced a valid `.xlsx` with one review warning.
- The resulting workbooks opened with `openpyxl`.

## Backend Data Retention

- Uploaded files, OCR debug output, extraction JSON, and generated Excel files live under `projects/dem-claim/app/web_outputs/<job_id>/` while active.
- Cleanup runs once at backend startup and then every hour by default.
- Jobs and orphaned job folders older than `DEM_JOB_RETENTION_HOURS` are deleted. Default: `24`.
- Change the scan interval with `DEM_JOB_CLEANUP_INTERVAL_SECONDS`. Default: `3600`.
- The UI `删除` action deletes the job folder immediately.
- `Download All` temporary zip files are deleted after the response.

## Important Fallback Fix

On 2026-06-17, real Chrome testing found that Codex fallback could appear stuck. The root cause was that backend subprocesses inherited stdin, and `codex exec` can wait for additional stdin input.

The fix is in `projects/dem-claim/app/app.py`: `run_command()` passes `stdin=asyncio.subprocess.DEVNULL` to `asyncio.create_subprocess_exec(...)`.

Do not remove this line. If fallback hangs again:

1. Check for stuck Codex child processes:

```bash
ps -axo pid,etime,command | rg "codex exec"
```

2. Confirm the job is stuck in `codex-reading` and has no `codex_extraction.json`.
3. Confirm `stdin=asyncio.subprocess.DEVNULL` is still present.
4. Run a tiny Codex CLI smoke:

```bash
"/Applications/Codex.app/Contents/Resources/codex" exec \
  --ignore-user-config --ephemeral --ignore-rules --skip-git-repo-check \
  -m gpt-5.5 -c model_reasoning_effort="low" \
  --sandbox read-only 'Return exactly OK.'
```

## Boundaries

- Keep the local DEM app separate from `web_ui/`.
- Keep auth/session logic in `auth_gate.py` and `app_zh_secure.py`; do not put website auth back into `projects/dem-claim/app/app.py`.
- Static website cookies are display state only. Backend session cookies enforce real DEM access.
- Do not expose the local app publicly unless the secure wrapper or another real auth layer is enabled.
