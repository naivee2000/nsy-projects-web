# DEM Claim Excel App

FastAPI wrapper for the `dem-claim-excel` Codex skill.

This app is part of the project at `projects/dem-claim/`. Start with `../README.md` when you need the project-level overview.

## Entrypoints

- `app.py` - local no-login DEM app.
- `app_zh.py` - Chinese UI wrapper for the local app routes.
- `auth_gate.py` - session-cookie login gate for public deployment.
- `app_zh_secure.py` - Chinese app plus `auth_gate.py`, used for `https://dem.nsyprojects.com/`.

Keep auth out of `app.py` so local installs can open directly without login.

## Local Run

```bash
cd /path/to/nsy-projects-web/projects/dem-claim
./run_local_app_mac.sh
```

Open:

```text
http://127.0.0.1:8000
```

## Public/Secure Run

```bash
cd /path/to/nsy-projects-web/projects/dem-claim/app
DEM_SKILL_ROOT="$HOME/.codex/skills/dem-claim-excel" \
DEM_JOB_ROOT="$PWD/web_outputs" \
CODEX_BIN="/Applications/Codex.app/Contents/Resources/codex" \
DEM_AUTH_USERNAME="admin" \
DEM_AUTH_PASSWORD_HASH="pbkdf2_sha256$..." \
DEM_SESSION_SECRET="replace-with-a-long-random-secret" \
./.venv/bin/python -m uvicorn app_zh_secure:app --host 127.0.0.1 --port 8000
```

For HTTPS public use, keep `DEM_COOKIE_SECURE=1` or omit it. For localhost-only secure testing, set `DEM_COOKIE_SECURE=0`.

## Flow

1. Upload loading files and discharge files in workbook order.
2. The app runs deterministic Python OCR first.
3. If OCR misses required fields, the app renders PDFs to PNG when needed and calls local `codex exec` with this Mac's saved Codex login.
4. Codex returns extraction JSON.
5. The skill's Python writer builds the fixed-format Excel workbook.

Laytime to commence is formula-driven in the workbook: each load/discharge block compares `NOR tendered + 6 hours` with the relevant load/discharge commence time and uses the earlier value.

No `OPENAI_API_KEY` is required for the default fallback path. Fallback requires this machine's Codex CLI to be installed, logged in, and within usage limits.

The `dem-claim-excel` skill is not shipped as a zip artifact in this Git repo. Keep it installed under `~/.codex/skills/dem-claim-excel` on each computer that runs the app.

## Important Codex Fallback Detail

`run_command()` must start subprocesses with:

```python
stdin=asyncio.subprocess.DEVNULL,
```

This prevents `codex exec` from waiting for inherited stdin. Real Chrome testing on 2026-06-17 showed fallback could look stuck without this line.

## Backend Data Retention

Uploaded source files and generated outputs are automatically expired after 24 hours by default.

- Active job state is stored in memory in `jobs`.
- Uploaded files, OCR debug output, JSON, and generated Excel files stay under `web_outputs/<job_id>/` while the job is active.
- The cleanup task runs once at startup and then every hour by default.
- Jobs and orphaned job folders older than `DEM_JOB_RETENTION_HOURS` are deleted. Default: `24`.
- Change the scan interval with `DEM_JOB_CLEANUP_INTERVAL_SECONDS`. Default: `3600`.
- Restarting the app clears the in-memory task list but leaves `web_outputs/` on disk.
- The UI `删除` action removes/cancels a task and deletes its job folder immediately.
- `Download All` creates a temporary zip and deletes that zip after the download response.

## Verification

Use the files under `Test Load:Discharge Documents/`.

- OCR-only: `Load1.png` plus `Discharge1.png`.
- Codex fallback: `Load3.png` plus `Discharge3.png`.

Expected real Chrome results from 2026-06-17:

- OCR-only completed in about 25 seconds.
- Codex fallback completed in about 35 seconds after the stdin fix.
- Both produced valid `.xlsx` files.
