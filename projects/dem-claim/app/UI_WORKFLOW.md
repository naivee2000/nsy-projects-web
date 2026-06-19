# DEM Claim Excel UI Workflow

## Design Intent

This app is an operational upload tool for building DEM claim workbooks. The UI should feel calm, direct, and easy to scan while a job is running. The first screen should make the two required inputs obvious, show local setup health, and keep job progress visible without requiring the user to read logs.

## Visual System

- Canvas: soft neutral background, white work surfaces, restrained borders, and one primary blue action.
- Type: system sans serif with compact headings and readable body text.
- Radius: 8px for panels and controls; no decorative oversized cards.
- Spacing: 8px base rhythm, with 16-24px between major regions.
- States: blue for active work, green for complete, amber for fallback or missing setup, red for failed.
- Logs: dark code surface with small monospace type and a clear empty state.

## Components

- App header: product name, current setup summary, and compact status copy.
- Setup panel: individual health chips for skill scripts, Codex CLI, Codex login, Tesseract, and Python packages.
- Task queue: stacked task cards, each representing one matched load/discharge workbook job.
- Upload workspace: each task card has two equal drop zones, one for loading files and one for discharge files, each with selected count, total size, ordered file names, and drag focus state.
- Action row: each task card has its own start button, and the queue has a Start All button for every draft task with both upload groups populated.
- Progress panel: each task card owns its own timeline for queue, Python OCR, Codex fallback, Excel build, and completion/error.
- Result panel: each task card shows final status and a download action when its workbook is ready.
- Logs: each task card keeps logs collapsed by default so several tasks can run without crowding the page.

## State Matrix

- Draft: task card exists but has not been started.
- Ready: both upload groups have at least one file selected.
- Uploading: submit is disabled and the message reads `Uploading files...`.
- Python OCR: timeline highlights deterministic extraction.
- Codex fallback: timeline highlights fallback reading/building and uses amber status.
- Complete: timeline shows complete, download button is visible.
- Failed: timeline shows failed, message is red, submit is re-enabled.

## Verification Checklist

- Start with `./.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8000`.
- Confirm `/api/setup` still returns the same backend fields.
- Browser-check desktop and mobile widths for empty, one-sided selection, both-sided selection, processing, failed, and completed/download states.
- Confirm file names wrap inside their rows and controls do not overlap at narrow widths.
- Confirm no Node, Tailwind, or external runtime dependency is required.

## Real Chrome Regression Tests

Completed on 2026-06-17 against `https://dem.nsyprojects.com/`.

- Login gate redirected unauthenticated Chrome to `/login?next=/`.
- Successful login opened the Chinese app shell with fixed links: `返回项目列表`, `返回首页`, `退出登录`.
- OCR-only task used `Load1.png` plus `Discharge1.png` and produced a downloadable Excel workbook in about 25 seconds.
- Codex fallback task used `Load3.png` plus `Discharge3.png`; Python OCR marked both files as needing Codex, then fallback produced a downloadable Excel workbook in about 35 seconds.
- Both downloaded workbooks opened successfully with `openpyxl`.

Keep `stdin=asyncio.subprocess.DEVNULL` in `app.py` subprocess calls. Without this, `codex exec` can wait for inherited stdin and the UI can appear stuck in `Codex is reading ...`.
