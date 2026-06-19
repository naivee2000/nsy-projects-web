# Prompt For The Other Codex

You are helping install and test a transferred NSY Projects DEM claim Excel app from a handoff zip.

The user has unzipped a package named something like `nsy-dem-app-handoff.zip`. Your job is to install it on this computer and verify that the local app runs. Do not deploy it to the internet unless the user explicitly asks.

## Package Layout

Expected files/folders:

- `projects/dem-claim/app/` - FastAPI DEM app. Local `app.py` should open directly with no login.
- `web_ui/` - static NSY Projects website/front-page design for Cloudflare Pages.
- `projects/dem-claim/dem-claim-excel-portable.zip` - Codex skill package required by the app.
- `HANDOFF_INSTALL.md` - install and deployment guide.
- `projects/dem-claim/run_local_app_mac.sh` - convenience script for macOS local mode.
- `ops/` - safe deployment notes/templates. Do not expect live secrets in the zip.

## Install Steps

1. Confirm package contents:

```bash
ls -la
ls -la projects/dem-claim/app
```

2. Install the skill:

```bash
mkdir -p "$HOME/.codex/skills"
unzip -o projects/dem-claim/dem-claim-excel-portable.zip -d "$HOME/.codex/skills"
```

3. Create the app virtual environment:

```bash
cd projects/dem-claim/app
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

4. Make sure Tesseract is installed. On macOS:

```bash
brew install tesseract
```

5. Make sure Codex is installed and logged in on this computer. The fallback path uses local `codex exec`, not an OpenAI API key.

6. Verify the DEM skill:

```bash
cd "$HOME/.codex/skills/dem-claim-excel"
python3 scripts/dem_claim_setup_check.py
```

7. Run the local no-login app:

```bash
cd /path/to/unzipped/nsy-dem-app-handoff/projects/dem-claim
./run_local_app_mac.sh
```

8. Open:

```text
http://127.0.0.1:8000
```

The page should open directly as `装卸时间计算表`. There should be no local login gate.

## Verification Checklist

- `GET /` returns the app HTML.
- `GET /api/setup` returns JSON with `skill_root_ok`, `codex_ok`, `codex_auth_ok`, `tesseract_ok`, and `packages_ok`.
- Local `app.py` does not add `/login` or website project routes.
- Uploading a loading file and discharge file creates a task and produces an Excel download.
- Test deterministic OCR with `Load1.png` plus `Discharge1.png`.
- Test Codex fallback with `Load3.png` plus `Discharge3.png`; Python OCR should miss required fields and fallback should produce a workbook.
- Confirm the downloaded `.xlsx` opens with `openpyxl`.

## Known Important Fix

Do not remove this line in `projects/dem-claim/app/app.py` inside `run_command()`:

```python
stdin=asyncio.subprocess.DEVNULL,
```

It prevents `codex exec` from waiting forever for inherited stdin. Without it, Codex fallback can look stuck in the browser.

## Backend Data Retention

Uploaded files and generated workbooks are automatically expired after 24 hours by default.

- Uploaded files and generated workbooks remain under `projects/dem-claim/app/web_outputs/<job_id>/` while active.
- Cleanup runs once at startup and then every hour by default.
- `DEM_JOB_RETENTION_HOURS` defaults to `24`.
- `DEM_JOB_CLEANUP_INTERVAL_SECONDS` defaults to `3600`.
- Restarting the app clears the in-memory task list; orphaned job folders are still removed once they are older than the retention window.
- Clicking `删除` cancels/removes the task and deletes its job folder immediately.
- `Download All` temporary zip files are deleted after the response.

## Public Deployment Boundaries

- Keep the local DEM app separate from `web_ui/`.
- Keep auth/session code in `auth_gate.py` and `app_zh_secure.py`; do not put website auth into `projects/dem-claim/app/app.py`.
- Do not expose local `app.py` publicly.
- For public use, run `app_zh_secure:app` behind an auth layer or Cloudflare Access.
- If something fails, inspect `/api/setup` first, then job logs, then stuck `codex exec` processes.
