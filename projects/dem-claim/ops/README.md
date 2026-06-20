# NSY DEM App Ops Notes

Last updated: 2026-06-20

This folder is for running the public DEM app from an always-on Mac through Cloudflare Tunnel.

## Current Live Shape

- Static website: Cloudflare Pages project `nsy-projects`
- Website domain: `https://nsyprojects.com/`
- DEM backend domain: `https://dem.nsyprojects.com/`
- Local backend target: `http://127.0.0.1:8000`
- Backend PM2 app: `nsy-dem-app`
- Tunnel PM2 app: `nsy-dem-tunnel`
- Backend entrypoint: `projects/dem-claim/app/app_zh_secure.py`
- Ops folder: `projects/dem-claim/ops/`

## Sensitive Files

Do not commit these to GitHub:

- live `pm2-nsy-dem-app.config.cjs` if it contains `DEM_SESSION_SECRET` or password hashes
- Cloudflare tunnel credentials JSON under `~/.cloudflared/`
- logs under `projects/dem-claim/ops/logs/`

Use the `.example` files in this folder as templates when rebuilding on a new Mac. Keep the real files private on that Mac.

## Run Checks

```bash
pm2 status nsy-dem-app nsy-dem-tunnel
curl -I https://dem.nsyprojects.com/
curl -s https://dem.nsyprojects.com/api/setup
```

For `/api/setup`, authenticate first or use a browser session. Expected backend checks are:

- `skill_root_ok`
- `codex_ok`
- `codex_auth_ok`
- `tesseract_ok`
- `packages_ok`

## Known Fallback Fix

The backend must close subprocess stdin:

```python
stdin=asyncio.subprocess.DEVNULL,
```

This is required because `codex exec` can wait for inherited stdin. If fallback appears stuck in `Codex is reading ...`, check for a lingering process:

```bash
ps -axo pid,etime,command | rg "codex exec"
```

## Data Retention

Uploaded source files and generated Excel files expire after 24 hours by default.

- Uploaded files and generated workbooks remain in `../app/web_outputs/<job_id>/` while active.
- Cleanup runs at backend startup and then every hour.
- Set `DEM_JOB_RETENTION_HOURS` to change the retention window. Default: `24`.
- Set `DEM_JOB_CLEANUP_INTERVAL_SECONDS` to change the scan interval. Default: `3600`.
- Restarting PM2 clears the in-memory job list; old orphaned job folders are removed once they are outside the retention window.
- The UI delete action removes/cancels active task state and deletes the job folder immediately.
- `Download All` temporary zip files are deleted after the response.
