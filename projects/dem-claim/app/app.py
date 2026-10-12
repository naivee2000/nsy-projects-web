#!/usr/bin/env python3
"""Local DEM claim upload site with Python OCR and Codex fallback."""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Any
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from starlette.background import BackgroundTask

try:
    import fitz  # PyMuPDF
except ModuleNotFoundError:  # pragma: no cover - setup endpoint reports this clearly
    fitz = None

try:
    from PIL import Image
except ModuleNotFoundError:  # pragma: no cover - setup endpoint reports this clearly
    Image = None


BASE_DIR = Path(__file__).resolve().parent
PROJECT_NAME = "装卸时间计算表"
DEFAULT_SKILL_ROOT = Path.home() / ".codex" / "skills" / "dem-claim-excel"
SKILL_ROOT = Path(os.environ.get("DEM_SKILL_ROOT", DEFAULT_SKILL_ROOT)).expanduser().resolve()
CODEX_CONFIGURED_BIN = os.environ.get("CODEX_BIN", "").strip()
CODEX_APP_BIN_CANDIDATES = (
    "/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex",
    "/Applications/Codex.app/Contents/Resources/codex-cli/bin/codex",
    "/Applications/ChatGPT.app/Contents/Resources/codex",
    "/Applications/Codex.app/Contents/Resources/codex",
)


def resolve_codex_bin() -> str:
    """Prefer a usable configured CLI, then recover from stale app-bundle paths."""
    candidates = (CODEX_CONFIGURED_BIN, *CODEX_APP_BIN_CANDIDATES, shutil.which("codex"))
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return CODEX_CONFIGURED_BIN or "codex"


CODEX_BIN = resolve_codex_bin()
CODEX_FALLBACK_MODEL = os.environ.get("CODEX_FALLBACK_MODEL", "gpt-5.6-terra")
CODEX_FALLBACK_REASONING_EFFORT = os.environ.get("CODEX_FALLBACK_REASONING_EFFORT", "medium")
CODEX_FALLBACK_CLEAN_CONFIG = os.environ.get("CODEX_FALLBACK_CLEAN_CONFIG", "1").lower() not in {"0", "false", "no"}
JOB_ROOT = Path(os.environ.get("DEM_JOB_ROOT", BASE_DIR / "web_outputs")).expanduser().resolve()
JOB_RETENTION_HOURS = float(os.environ.get("DEM_JOB_RETENTION_HOURS", "24"))
JOB_CLEANUP_INTERVAL_SECONDS = int(os.environ.get("DEM_JOB_CLEANUP_INTERVAL_SECONDS", "3600"))
ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".pdf", ".tif", ".tiff"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
CONVERTIBLE_IMAGE_SUFFIXES = {".tif", ".tiff"}
REQUIRED_LOAD_EVENTS = ("nor_tendered", "all_fast", "hose_on", "load_commence", "load_complete", "hose_off")
REQUIRED_DISCHARGE_EVENTS = (
    "nor_tendered",
    "anchor_up",
    "all_fast",
    "hose_on",
    "disch_commence",
    "disch_complete",
    "hose_off",
)

app = FastAPI(title=PROJECT_NAME)
jobs: dict[str, dict[str, Any]] = {}
job_tasks: dict[str, asyncio.Task[Any]] = {}
cleanup_task: asyncio.Task[Any] | None = None


CODEX_EXTRACTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "metadata": {
            "type": "object",
            "properties": {
                "charterer": {"type": ["string", "null"]},
                "charterer_ref": {"type": ["string", "null"]},
                "owner": {"type": ["string", "null"]},
                "owner_ref": {"type": ["string", "null"]},
                "broker": {"type": ["string", "null"]},
                "vessel": {"type": ["string", "null"]},
                "cp_date": {"type": ["string", "null"]},
                "demurrage_rate": {"type": ["number", "null"]},
                "total_cargo_quantity": {"type": ["number", "null"]},
                "currency": {"type": ["string", "null"]},
                "laycan_start": {"type": ["string", "null"]},
                "laycan_end": {"type": ["string", "null"]},
                "doc_date": {"type": ["string", "null"]},
            },
            "required": [
                "charterer",
                "charterer_ref",
                "owner",
                "owner_ref",
                "broker",
                "vessel",
                "cp_date",
                "demurrage_rate",
                "total_cargo_quantity",
                "currency",
                "laycan_start",
                "laycan_end",
                "doc_date",
            ],
            "additionalProperties": False,
        },
        "load": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "port": {"type": ["string", "null"]},
                    "berth": {"type": ["string", "null"]},
                    "terminal": {"type": ["string", "null"]},
                    "allowed_hours": {"type": ["number", "null"]},
                    "document_onboard_hours": {"type": ["number", "null"]},
                    "events": {
                        "type": "object",
                        "properties": {
                            "nor_tendered": {"type": ["string", "null"]},
                            "anchor_up": {"type": ["string", "null"]},
                            "all_fast": {"type": ["string", "null"]},
                            "hose_on": {"type": ["string", "null"]},
                            "load_commence": {"type": ["string", "null"]},
                            "load_complete": {"type": ["string", "null"]},
                            "hose_off": {"type": ["string", "null"]},
                        },
                        "required": [
                            "nor_tendered",
                            "anchor_up",
                            "all_fast",
                            "hose_on",
                            "load_commence",
                            "load_complete",
                            "hose_off",
                        ],
                        "additionalProperties": False,
                    },
                },
                "required": ["port", "berth", "terminal", "allowed_hours", "document_onboard_hours", "events"],
                "additionalProperties": False,
            },
        },
        "discharge": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "port": {"type": ["string", "null"]},
                    "berth": {"type": ["string", "null"]},
                    "quantity": {"type": ["number", "null"]},
                    "rate": {"type": ["number", "null"]},
                    "allowed_hours": {"type": ["number", "null"]},
                    "events": {
                        "type": "object",
                        "properties": {
                            "nor_tendered": {"type": ["string", "null"]},
                            "anchor_up": {"type": ["string", "null"]},
                            "all_fast": {"type": ["string", "null"]},
                            "hose_on": {"type": ["string", "null"]},
                            "disch_commence": {"type": ["string", "null"]},
                            "disch_complete": {"type": ["string", "null"]},
                            "hose_off": {"type": ["string", "null"]},
                        },
                        "required": [
                            "nor_tendered",
                            "anchor_up",
                            "all_fast",
                            "hose_on",
                            "disch_commence",
                            "disch_complete",
                            "hose_off",
                        ],
                        "additionalProperties": False,
                    },
                    "deductions": {
                        "type": "object",
                        "properties": {
                            "shifting_hours": {"type": ["number", "null"]},
                            "rate_difference_hours": {"type": ["number", "null"]},
                            "night_navigation_hours": {"type": ["number", "null"]},
                            "document_onboard_hours": {"type": ["number", "null"]},
                        },
                        "required": [
                            "shifting_hours",
                            "rate_difference_hours",
                            "night_navigation_hours",
                            "document_onboard_hours",
                        ],
                        "additionalProperties": False,
                    },
                },
                "required": ["port", "berth", "quantity", "rate", "allowed_hours", "events", "deductions"],
                "additionalProperties": False,
            },
        },
        "confidence_notes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["field", "note"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["metadata", "load", "discharge", "confidence_notes"],
    "additionalProperties": False,
}


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>装卸时间计算表</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f4f6f8;
      --surface: #ffffff;
      --surface-soft: #f9fafb;
      --ink: #182230;
      --muted: #667085;
      --subtle: #98a2b3;
      --line: #d0d5dd;
      --line-strong: #b8c0cc;
      --primary: #175cd3;
      --primary-strong: #1849a9;
      --primary-soft: #eff4ff;
      --green: #067647;
      --green-soft: #ecfdf3;
      --amber: #b54708;
      --amber-soft: #fffaeb;
      --red: #b42318;
      --red-soft: #fef3f2;
      --log: #111827;
      --shadow: 0 20px 48px rgba(16, 24, 40, 0.10);
    }
    * { box-sizing: border-box; }
    html { min-width: 320px; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        linear-gradient(180deg, #eef2f6 0, var(--bg) 280px),
        var(--bg);
      color: var(--ink);
      letter-spacing: 0;
    }
    button,
    input {
      font: inherit;
      letter-spacing: 0;
    }
    main {
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }
    .app-header {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 18px;
      align-items: end;
      margin-bottom: 18px;
    }
    .eyebrow {
      margin: 0 0 8px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
    }
    h1 {
      margin: 0;
      font-size: clamp(30px, 4vw, 44px);
      line-height: 1.02;
      letter-spacing: 0;
    }
    h2,
    h3,
    p {
      letter-spacing: 0;
    }
    .setup-summary {
      min-width: 230px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.86);
      padding: 12px 14px;
      box-shadow: 0 8px 22px rgba(16, 24, 40, 0.06);
    }
    .summary-label {
      display: block;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }
    .summary-value {
      display: block;
      margin-top: 4px;
      color: var(--ink);
      font-size: 16px;
      font-weight: 800;
      overflow-wrap: anywhere;
    }
    .summary-value.ok { color: var(--green); }
    .summary-value.warn { color: var(--amber); }
    .summary-value.fail { color: var(--red); }
    .workspace {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 16px;
    }
    .surface {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .setup-panel {
      padding: 16px;
      display: grid;
      grid-template-columns: auto minmax(0, 1fr);
      gap: 14px;
      align-items: start;
    }
    .setup-dot {
      width: 12px;
      height: 12px;
      margin-top: 4px;
      border-radius: 999px;
      background: var(--subtle);
      box-shadow: 0 0 0 4px #eef2f6;
    }
    .setup-dot.ok { background: var(--green); box-shadow: 0 0 0 4px var(--green-soft); }
    .setup-dot.warn { background: var(--amber); box-shadow: 0 0 0 4px var(--amber-soft); }
    .setup-dot.fail { background: var(--red); box-shadow: 0 0 0 4px var(--red-soft); }
    .setup-copy,
    .queue-head,
    .task-head,
    .progress-head {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: start;
    }
    .setup-copy h2,
    .queue-head h2,
    .task-title h3,
    .progress-head h3,
    .log-title {
      margin: 0;
      font-size: 17px;
      line-height: 1.2;
    }
    .setup-copy p,
    .queue-head p,
    .task-title p,
    .progress-head p {
      margin: 4px 0 0;
      color: var(--muted);
      line-height: 1.45;
    }
    .setup-copy { margin-bottom: 12px; }
    .setup-grid {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 8px;
    }
    .check {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface-soft);
      padding: 10px;
    }
    .check strong,
    .check span {
      display: block;
      overflow-wrap: anywhere;
    }
    .check strong {
      font-size: 13px;
      line-height: 1.2;
    }
    .check span {
      margin-top: 4px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.3;
    }
    .check.ok { border-color: #abefc6; background: var(--green-soft); }
    .check.warn { border-color: #fedf89; background: var(--amber-soft); }
    .check.fail { border-color: #fecdca; background: var(--red-soft); }
    .queue {
      display: grid;
      gap: 14px;
      padding: 16px;
      background: #fcfcfd;
    }
    .queue-actions {
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 8px;
      align-items: center;
    }
    .stats {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .stat {
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #ffffff;
      color: var(--muted);
      padding: 7px 10px;
      font-size: 12px;
      font-weight: 800;
      white-space: nowrap;
    }
    .task-list {
      display: grid;
      gap: 12px;
    }
    .queue-footer {
      display: flex;
      justify-content: center;
      padding-top: 2px;
    }
    .queue-footer button {
      min-width: 150px;
    }
    .task-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      overflow: hidden;
      box-shadow: 0 10px 24px rgba(16, 24, 40, 0.05);
    }
    .task-card.running { border-color: #b2ccff; }
    .task-card.completed { border-color: #abefc6; }
    .task-card.failed { border-color: #fecdca; }
    .task-card.fallback { border-color: #fedf89; }
    .task-head {
      padding: 14px;
      border-bottom: 1px solid var(--line);
      background: #ffffff;
    }
    .task-title {
      min-width: 0;
      display: flex;
      gap: 10px;
      align-items: start;
    }
    .task-number {
      width: 30px;
      height: 30px;
      border-radius: 999px;
      background: var(--primary-soft);
      color: var(--primary-strong);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
      font-weight: 900;
      flex: 0 0 auto;
    }
    .task-title h3 {
      overflow-wrap: anywhere;
    }
    .task-tools {
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 8px;
      align-items: center;
    }
    .task-body {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(300px, 0.72fr);
      gap: 14px;
      padding: 14px;
      background: var(--surface-soft);
    }
    .pair-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    .upload-panel {
      min-width: 0;
      border: 1px dashed var(--line-strong);
      border-radius: 8px;
      background: #ffffff;
      padding: 12px;
      display: grid;
      grid-template-rows: auto auto minmax(86px, auto);
      gap: 10px;
      transition: border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
    }
    .upload-panel.ready {
      border-style: solid;
      background: #ffffff;
    }
    .upload-panel.dragging,
    .upload-panel:focus-within {
      border-color: var(--primary);
      box-shadow: 0 0 0 4px rgba(23, 92, 211, 0.12);
      background: #ffffff;
    }
    .upload-panel.locked {
      border-style: solid;
      background: #f8fafc;
    }
    .upload-head,
    .choose-row,
    .result-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }
    .upload-title {
      min-width: 0;
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .step {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 26px;
      height: 26px;
      border-radius: 999px;
      background: var(--primary-soft);
      color: var(--primary-strong);
      font-size: 12px;
      font-weight: 900;
      flex: 0 0 auto;
    }
    .upload-title h4 {
      margin: 0;
      font-size: 15px;
      line-height: 1.2;
      overflow-wrap: anywhere;
    }
    .count,
    .tag {
      border-radius: 999px;
      padding: 6px 10px;
      background: var(--primary-soft);
      color: var(--primary-strong);
      font-size: 12px;
      font-weight: 800;
      line-height: 1;
      max-width: 100%;
      overflow-wrap: anywhere;
      white-space: nowrap;
    }
    .count {
      border: 1px solid var(--line);
      background: #ffffff;
      color: var(--muted);
    }
    .tag.ok { background: var(--green-soft); color: var(--green); }
    .tag.warn { background: var(--amber-soft); color: var(--amber); }
    .tag.fail { background: var(--red-soft); color: var(--red); }
    .choose,
    button,
    .download {
      min-height: 38px;
      border-radius: 6px;
      padding: 0 13px;
      font-weight: 800;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      white-space: nowrap;
    }
    button,
    .download {
      border: 0;
      background: var(--primary);
      color: #ffffff;
    }
    button:hover,
    .download:hover {
      background: var(--primary-strong);
    }
    button:disabled {
      opacity: 0.52;
      cursor: not-allowed;
    }
    .choose,
    .ghost {
      border: 1px solid var(--line);
      background: #ffffff;
      color: var(--ink);
    }
    .choose:hover,
    .ghost:hover {
      border-color: var(--primary);
      color: var(--primary-strong);
      background: #ffffff;
    }
    .danger:hover {
      border-color: #fecdca;
      color: var(--red);
    }
    .file-input {
      position: absolute;
      inline-size: 1px;
      block-size: 1px;
      opacity: 0;
      pointer-events: none;
    }
    .format-note {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }
    .files {
      margin: 0;
      padding: 0;
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 7px;
      min-height: 86px;
      max-height: 168px;
      overflow: auto;
    }
    .files li {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #ffffff;
      padding: 8px 9px;
      font-size: 13px;
    }
    .file-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
    }
    .file-name {
      min-width: 0;
      overflow-wrap: anywhere;
      line-height: 1.32;
      font-weight: 650;
    }
    .file-size {
      color: var(--muted);
      white-space: nowrap;
      font-size: 12px;
      font-weight: 700;
    }
    .empty {
      color: var(--muted);
      display: grid;
      min-height: 72px;
      place-items: center;
      text-align: center;
      line-height: 1.35;
      background: #ffffff;
    }
    .task-side {
      min-width: 0;
      display: grid;
      gap: 10px;
    }
    .progress-panel {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      padding: 12px;
    }
    .progress-head {
      margin-bottom: 10px;
    }
    .state {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      justify-content: flex-end;
    }
    .message {
      margin: 0;
      color: var(--muted);
      line-height: 1.45;
      overflow-wrap: anywhere;
    }
    .message.fail { color: var(--red); font-weight: 700; }
    .message.ok { color: var(--green); font-weight: 700; }
    .timeline {
      margin: 0;
      padding: 0;
      list-style: none;
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 6px;
    }
    .timeline li {
      min-width: 0;
      display: grid;
      gap: 6px;
      align-content: start;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      line-height: 1.25;
    }
    .marker {
      width: 24px;
      height: 24px;
      border-radius: 999px;
      border: 2px solid var(--line-strong);
      background: #ffffff;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      color: var(--subtle);
      font-size: 11px;
      font-weight: 900;
    }
    .timeline span:last-child {
      overflow-wrap: anywhere;
    }
    .timeline li.done { color: var(--green); }
    .timeline li.done .marker {
      border-color: var(--green);
      background: var(--green-soft);
      color: var(--green);
    }
    .timeline li.active { color: var(--primary-strong); }
    .timeline li.active .marker {
      border-color: var(--primary);
      background: var(--primary-soft);
      color: var(--primary-strong);
    }
    .timeline li.warn { color: var(--amber); }
    .timeline li.warn .marker {
      border-color: var(--amber);
      background: var(--amber-soft);
      color: var(--amber);
    }
    .timeline li.fail { color: var(--red); }
    .timeline li.fail .marker {
      border-color: var(--red);
      background: var(--red-soft);
      color: var(--red);
    }
    .result-row {
      min-height: 38px;
      border-top: 1px solid var(--line);
      padding-top: 10px;
    }
    details.log {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      overflow: hidden;
    }
    details.log summary {
      min-height: 40px;
      padding: 10px 12px;
      cursor: pointer;
      font-weight: 800;
      color: var(--ink);
      list-style-position: inside;
    }
    .log-body {
      background: var(--log);
      color: #e5e7eb;
      max-height: 260px;
      overflow: auto;
      padding: 12px;
      border-top: 1px solid #1f2937;
    }
    pre {
      margin: 0;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      color: #d1d5db;
      font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }
    .empty-log pre {
      color: #9ca3af;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
    }
    @media (max-width: 1060px) {
      .task-body { grid-template-columns: 1fr; }
      .setup-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    }
    @media (max-width: 780px) {
      main {
        width: min(100vw - 24px, 1180px);
        padding-top: 18px;
      }
      .app-header,
      .queue-head,
      .task-head,
      .progress-head {
        display: grid;
        grid-template-columns: 1fr;
      }
      .app-header {
        align-items: stretch;
      }
      .setup-summary {
        min-width: 0;
      }
      .setup-panel {
        grid-template-columns: 1fr;
      }
      .setup-dot {
        display: none;
      }
      .setup-grid,
      .pair-grid {
        grid-template-columns: 1fr;
      }
      .task-tools,
      .queue-actions,
      .state {
        justify-content: stretch;
      }
      .task-tools {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        width: 100%;
      }
      .queue-footer {
        display: grid;
      }
      .queue-actions > *,
      .choose,
      button,
      .download {
        width: 100%;
      }
      .upload-panel {
        padding: 10px;
        gap: 8px;
      }
      .files {
        min-height: 56px;
        max-height: 124px;
      }
      .empty {
        min-height: 48px;
      }
      .upload-head,
      .choose-row,
      .result-row {
        align-items: stretch;
        flex-direction: column;
      }
      .count {
        width: 100%;
        text-align: center;
      }
      .file-row {
        grid-template-columns: 1fr;
        gap: 4px;
      }
      .file-size {
        white-space: normal;
      }
      h1 {
        font-size: 32px;
      }
    }
  </style>
</head>
<body>
  <main>
    <header class="app-header">
      <div>
        <p class="eyebrow">Local workbook builder</p>
        <h1>装卸时间计算表</h1>
      </div>
      <div class="setup-summary" aria-live="polite">
        <span class="summary-label">Setup</span>
        <span id="setupSummary" class="summary-value">Checking...</span>
      </div>
    </header>

    <div class="workspace">
      <section class="surface setup-panel" aria-labelledby="setupTitle">
        <div id="setupDot" class="setup-dot" aria-hidden="true"></div>
        <div>
          <div class="setup-copy">
            <div>
              <h2 id="setupTitle">Local Setup</h2>
              <p id="setupMessage">Checking local tools...</p>
            </div>
          </div>
          <div id="setupChecks" class="setup-grid" aria-live="polite"></div>
        </div>
      </section>

      <section class="surface queue" aria-labelledby="queueTitle">
        <div class="queue-head">
          <div>
            <h2 id="queueTitle">Task Queue</h2>
            <p>Each task keeps its own matched loading and discharge files.</p>
          </div>
          <div class="queue-actions">
            <div id="queueStats" class="stats" aria-live="polite"></div>
            <button id="startAllBtn" class="ghost" type="button" disabled>Start All</button>
            <button id="downloadAllBtn" class="ghost" type="button" disabled>Download All</button>
            <button id="addTaskBtn" type="button" disabled>Add Task</button>
          </div>
        </div>
        <div id="taskList" class="task-list" aria-live="polite"></div>
        <div class="queue-footer">
          <button id="addTaskBottomBtn" class="ghost" type="button" disabled>Add Task</button>
        </div>
      </section>
    </div>
  </main>

  <template id="taskTemplate">
    <article class="task-card">
      <div class="task-head">
        <div class="task-title">
          <span class="task-number"></span>
          <div>
            <h3></h3>
            <p class="task-subtitle">Select matching files, then start this task.</p>
          </div>
        </div>
        <div class="task-tools">
          <button class="start-task" type="button" disabled>Start Task</button>
          <button class="ghost danger remove-task" type="button">Remove</button>
        </div>
      </div>
      <div class="task-body">
        <div class="pair-grid">
          <div class="upload-panel" data-kind="load">
            <div class="upload-head">
              <div class="upload-title">
                <span class="step">L</span>
                <h4>Loading Files</h4>
              </div>
              <span class="count">No files</span>
            </div>
            <div class="choose-row">
              <label class="choose">Choose Files</label>
              <span class="format-note">PDF, PNG, JPG, TIFF</span>
              <input class="file-input load-input" name="load_files" type="file" accept=".png,.jpg,.jpeg,.pdf,.tif,.tiff" multiple>
            </div>
            <ul class="files"><li class="empty">No loading files selected</li></ul>
          </div>
          <div class="upload-panel" data-kind="discharge">
            <div class="upload-head">
              <div class="upload-title">
                <span class="step">D</span>
                <h4>Discharge Files</h4>
              </div>
              <span class="count">No files</span>
            </div>
            <div class="choose-row">
              <label class="choose">Choose Files</label>
              <span class="format-note">PDF, PNG, JPG, TIFF</span>
              <input class="file-input discharge-input" name="discharge_files" type="file" accept=".png,.jpg,.jpeg,.pdf,.tif,.tiff" multiple>
            </div>
            <ul class="files"><li class="empty">No discharge files selected</li></ul>
          </div>
        </div>
        <div class="task-side">
          <section class="progress-panel">
            <div class="progress-head">
              <div>
                <h3>Job Status</h3>
                <p class="message">Waiting for matching files.</p>
              </div>
              <div class="state">
                <span class="tag">draft</span>
              </div>
            </div>
            <ol class="timeline" aria-label="Job progress"></ol>
            <div class="result-row">
              <span class="format-note job-id"></span>
              <span class="download-slot"></span>
            </div>
          </section>
          <details class="log empty-log">
            <summary>Log</summary>
            <div class="log-body"><pre>No log output yet.</pre></div>
          </details>
        </div>
      </div>
    </article>
  </template>

  <script>
    const setupSummary = document.getElementById("setupSummary");
    const setupMessage = document.getElementById("setupMessage");
    const setupChecks = document.getElementById("setupChecks");
    const setupDot = document.getElementById("setupDot");
    const startAllBtn = document.getElementById("startAllBtn");
    const downloadAllBtn = document.getElementById("downloadAllBtn");
    const addTaskBtn = document.getElementById("addTaskBtn");
    const addTaskBottomBtn = document.getElementById("addTaskBottomBtn");
    const taskList = document.getElementById("taskList");
    const taskTemplate = document.getElementById("taskTemplate");
    const queueStats = document.getElementById("queueStats");
    const tasks = new Map();
    let nextTaskId = 1;

    const stages = [
      { key: "queued", label: "Queued" },
      { key: "python-ocr", label: "Python OCR" },
      { key: "codex", label: "Codex Fallback" },
      { key: "excel-build", label: "Excel Build" },
      { key: "complete", label: "Ready" }
    ];

    function formatBytes(bytes) {
      if (!bytes) return "0 KB";
      if (bytes < 1024 * 1024) return `${Math.max(1, Math.ceil(bytes / 1024))} KB`;
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }

    function fileWord(count) {
      return count === 1 ? "file" : "files";
    }

    function phaseKey(job) {
      const status = job.status || "idle";
      const phase = job.phase || "idle";
      if (status === "completed" || phase === "complete") return "complete";
      if (status === "failed" || phase === "failed") return "failed";
      if (phase === "excel-build") return "excel-build";
      if (phase === "codex-fallback" || phase === "codex-reading" || status === "fallback") return "codex";
      if (phase === "python-ocr" || status === "processing") return "python-ocr";
      if (phase === "queued" || status === "queued") return "queued";
      return "idle";
    }

    function toneForJob(job) {
      const status = job.status || "draft";
      const phase = job.phase || "draft";
      if (status === "completed" || status === "ready") return "ok";
      if (status === "failed") return "fail";
      if (status === "fallback" || phase.indexOf("codex") === 0) return "warn";
      return "";
    }

    function isFinal(job) {
      return job && (job.status === "completed" || job.status === "failed");
    }

    function isTaskDownloadable(task) {
      return Boolean(task.job && task.job.status === "completed" && task.job.download_ready);
    }

    function downloadUrl(task) {
      return `/api/jobs/${task.job.job_id}/download?task=${encodeURIComponent(task.number)}`;
    }

    function renderDownloadSlot(task) {
      if (isTaskDownloadable(task)) {
        task.downloadSlot.innerHTML = `<a class="download" href="${downloadUrl(task)}">Download Excel</a>`;
      } else {
        task.downloadSlot.innerHTML = "";
      }
    }

    function downloadAllItems() {
      return Array.from(tasks.values())
        .filter(isTaskDownloadable)
        .map(task => `${task.job.job_id}:${task.number}`);
    }

    function updateQueueStats() {
      const values = Array.from(tasks.values());
      const counts = {
        draft: 0,
        startable: 0,
        running: 0,
        completed: 0,
        failed: 0
      };
      values.forEach(task => {
        if (!task.job && isTaskStartable(task)) counts.startable += 1;
        else if (!task.job) counts.draft += 1;
        else if (task.job.status === "completed") counts.completed += 1;
        else if (task.job.status === "failed") counts.failed += 1;
        else counts.running += 1;
      });
      queueStats.innerHTML = "";
      [
        ["Tasks", values.length],
        ["Draft", counts.draft],
        ["Ready", counts.startable],
        ["Running", counts.running],
        ["Completed", counts.completed],
        ["Failed", counts.failed]
      ].forEach(([label, value]) => {
        const item = document.createElement("span");
        item.className = "stat";
        item.textContent = `${label}: ${value}`;
        queueStats.appendChild(item);
      });
      startAllBtn.disabled = counts.startable === 0;
      startAllBtn.textContent = counts.startable ? `Start All (${counts.startable})` : "Start All";
      const downloadable = downloadAllItems().length;
      downloadAllBtn.disabled = downloadable === 0;
      downloadAllBtn.textContent = downloadable ? `Download All (${downloadable})` : "Download All";
    }

    function renderTimeline(target, job = { status: "draft", phase: "draft" }) {
      const key = phaseKey(job);
      const activeIndex = stages.findIndex(stage => stage.key === key);
      target.innerHTML = "";
      stages.forEach((stage, index) => {
        const item = document.createElement("li");
        const marker = document.createElement("span");
        const label = document.createElement("span");
        marker.className = "marker";
        marker.textContent = String(index + 1);
        label.textContent = stage.label;
        if (key === "failed") {
          const failIndex = activeIndex >= 0 ? activeIndex : 0;
          if (index < failIndex) item.className = "done";
          if (index === failIndex) item.className = "fail";
        } else if (key === "complete") {
          item.className = "done";
        } else if (index < activeIndex) {
          item.className = "done";
        } else if (index === activeIndex) {
          item.className = stage.key === "codex" ? "warn" : "active";
        }
        item.append(marker, label);
        target.appendChild(item);
      });
    }

    function renderTags(target, job = { status: "draft", phase: "waiting", method: "pending" }) {
      const tone = toneForJob(job);
      target.innerHTML = "";
      [
        { value: job.status || "draft", tone },
        { value: job.phase || "waiting", tone: "" },
        { value: job.method || "pending", tone: "" }
      ].forEach(item => {
        const tag = document.createElement("span");
        tag.className = `tag ${item.tone}`.trim();
        tag.textContent = item.value;
        target.appendChild(tag);
      });
    }

    function setLog(task, text) {
      const clean = text || "";
      task.log.classList.toggle("empty-log", !clean);
      task.logText.textContent = clean || "No log output yet.";
    }

    function compactMessage(text) {
      const clean = (text || "").replace(/\s+/g, " ").trim();
      if (clean.length <= 220) return clean;
      return `${clean.slice(0, 220)}... Open the log for full detail.`;
    }

    function setTaskCardState(task, job) {
      task.root.classList.remove("running", "completed", "failed", "fallback");
      if (!job) return;
      if (job.status === "completed") task.root.classList.add("completed");
      else if (job.status === "failed") task.root.classList.add("failed");
      else if (job.status === "fallback") task.root.classList.add("fallback");
      else task.root.classList.add("running");
    }

    function renderJob(task, job) {
      task.job = job;
      renderTags(task.state, job);
      renderTimeline(task.timeline, job);
      task.message.className = "message";
      if (job.status === "completed") task.message.classList.add("ok");
      if (job.status === "failed") task.message.classList.add("fail");
      task.message.textContent = compactMessage(job.message || "");
      task.message.title = job.message || "";
      task.jobId.textContent = job.job_id ? `Job ${job.job_id}` : "";
      setLog(task, job.log || "");
      setTaskCardState(task, job);
      renderDownloadSlot(task);
      updateQueueStats();
    }

    function filesFor(task, kind) {
      return Array.from(task.inputs[kind].files || []);
    }

    function isTaskStartable(task) {
      return !task.job && !task.isBusy && filesFor(task, "load").length > 0 && filesFor(task, "discharge").length > 0;
    }

    function updateTaskReady(task) {
      const hasLoad = filesFor(task, "load").length > 0;
      const hasDischarge = filesFor(task, "discharge").length > 0;
      const readyToStart = hasLoad && hasDischarge;
      const locked = task.isBusy || Boolean(task.job);
      task.startBtn.disabled = locked || !readyToStart;
      task.startBtn.textContent = task.isBusy ? "Working..." : "Start Task";
      if (!task.job) {
        const loadText = hasLoad ? `${filesFor(task, "load").length} loading ${fileWord(filesFor(task, "load").length)}` : "loading files";
        const disText = hasDischarge ? `${filesFor(task, "discharge").length} discharge ${fileWord(filesFor(task, "discharge").length)}` : "discharge files";
        task.subtitle.textContent = readyToStart
          ? `${loadText} and ${disText} selected.`
          : `Select matching ${loadText} and ${disText}.`;
        task.message.className = "message";
        task.message.title = "";
        if (readyToStart) {
          task.message.classList.add("ok");
          task.message.textContent = "Ready to start.";
          renderTags(task.state, { status: "ready", phase: "waiting", method: "not started" });
        } else {
          task.message.textContent = "Waiting for matching files.";
          renderTags(task.state, { status: "draft", phase: "waiting", method: "pending" });
        }
      }
      updateQueueStats();
    }

    function renderFileList(task, kind, emptyText) {
      const input = task.inputs[kind];
      const panel = task.panels[kind];
      const list = panel.querySelector(".files");
      const count = panel.querySelector(".count");
      const meta = panel.querySelector(".format-note");
      const files = filesFor(task, kind);
      const totalBytes = files.reduce((sum, file) => sum + file.size, 0);
      list.innerHTML = "";
      panel.classList.toggle("ready", files.length > 0);
      count.textContent = files.length ? `${files.length} ${fileWord(files.length)}` : "No files";
      meta.textContent = files.length ? `${formatBytes(totalBytes)} total` : "PDF, PNG, JPG, TIFF";
      if (!files.length) {
        const item = document.createElement("li");
        item.className = "empty";
        item.textContent = emptyText;
        list.appendChild(item);
        updateTaskReady(task);
        return;
      }
      files.forEach((file, index) => {
        const item = document.createElement("li");
        const row = document.createElement("div");
        const name = document.createElement("span");
        const size = document.createElement("span");
        row.className = "file-row";
        name.className = "file-name";
        size.className = "file-size";
        name.textContent = `${index + 1}. ${file.name}`;
        size.textContent = formatBytes(file.size);
        row.append(name, size);
        item.appendChild(row);
        list.appendChild(item);
      });
      updateTaskReady(task);
    }

    function lockInputs(task) {
      Object.values(task.inputs).forEach(input => input.disabled = true);
      Object.values(task.panels).forEach(panel => panel.classList.add("locked"));
    }

    async function pollTask(task) {
      if (task.removed || !task.jobIdValue) return;
      const res = await fetch(`/api/jobs/${task.jobIdValue}`);
      const job = await res.json();
      if (task.removed) return;
      renderJob(task, job);
      if (isFinal(job)) {
        task.isBusy = false;
        updateTaskReady(task);
        clearInterval(task.pollTimer);
        task.pollTimer = null;
      }
    }

    async function startTask(task) {
      if (task.startBtn.disabled) return;
      task.isBusy = true;
      lockInputs(task);
      updateTaskReady(task);
      task.message.className = "message";
      task.message.textContent = "Uploading files...";
      setLog(task, "");
      task.downloadSlot.innerHTML = "";
      renderTags(task.state, { status: "queued", phase: "queued", method: "pending" });
      renderTimeline(task.timeline, { status: "queued", phase: "queued" });
      setTaskCardState(task, { status: "queued" });
      updateQueueStats();

      const data = new FormData();
      filesFor(task, "load").forEach(file => data.append("load_files", file));
      filesFor(task, "discharge").forEach(file => data.append("discharge_files", file));
      data.append("task_number", String(task.number));
      try {
        const res = await fetch("/api/jobs", { method: "POST", body: data });
        const body = await res.json();
        if (!res.ok) throw new Error(body.detail || "Upload failed");
        if (task.removed) {
          await fetch(`/api/jobs/${body.job_id}`, { method: "DELETE" });
          return;
        }
        task.jobIdValue = body.job_id;
        renderJob(task, body);
        task.pollTimer = setInterval(() => pollTask(task), 1600);
        await pollTask(task);
      } catch (error) {
        if (task.removed) return;
        task.isBusy = false;
        task.job = { status: "failed", phase: "failed", method: "upload" };
        renderTags(task.state, task.job);
        renderTimeline(task.timeline, task.job);
        task.message.className = "message fail";
        task.message.textContent = compactMessage(error.message || "Upload failed");
        task.message.title = error.message || "Upload failed";
        setTaskCardState(task, task.job);
        updateQueueStats();
      }
    }

    function startAllReadyTasks() {
      const readyTasks = Array.from(tasks.values()).filter(isTaskStartable);
      startAllBtn.disabled = true;
      readyTasks.forEach(task => {
        startTask(task);
      });
    }

    function downloadAllReadyTasks() {
      const items = downloadAllItems();
      if (!items.length) return;
      window.location.href = `/api/jobs/download-all?items=${encodeURIComponent(items.join(","))}`;
    }

    function addTaskAndShow() {
      const task = createTask();
      task.root.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function wireDropPanel(task, kind, emptyText) {
      const panel = task.panels[kind];
      const input = task.inputs[kind];
      const label = panel.querySelector(".choose");
      label.setAttribute("for", input.id);
      input.addEventListener("change", () => renderFileList(task, kind, emptyText));
      panel.addEventListener("dragover", event => {
        event.preventDefault();
        if (input.disabled) return;
        panel.classList.add("dragging");
      });
      panel.addEventListener("dragleave", () => panel.classList.remove("dragging"));
      panel.addEventListener("drop", event => {
        event.preventDefault();
        panel.classList.remove("dragging");
        if (input.disabled) return;
        input.files = event.dataTransfer.files;
        input.dispatchEvent(new Event("change"));
      });
    }

    function renumberTasks() {
      Array.from(tasks.values()).forEach((task, index) => {
        const number = index + 1;
        task.number = number;
        task.numberLabel.textContent = number;
        task.title.textContent = `Task ${number}`;
        renderDownloadSlot(task);
      });
    }

    async function removeTask(task) {
      task.removed = true;
      if (task.pollTimer) {
        clearInterval(task.pollTimer);
        task.pollTimer = null;
      }
      if (task.jobIdValue) {
        try {
          await fetch(`/api/jobs/${task.jobIdValue}`, { method: "DELETE" });
        } catch (error) {
          console.warn("Could not cancel removed task", error);
        }
      }
      tasks.delete(task.id);
      task.root.remove();
      if (!tasks.size) {
        createTask();
        return;
      }
      renumberTasks();
      updateQueueStats();
    }

    function createTask(existingJob = null) {
      const fragment = taskTemplate.content.cloneNode(true);
      const root = fragment.querySelector(".task-card");
      const id = `task-${nextTaskId++}-${Math.random().toString(16).slice(2)}`;
      const task = {
        id,
        number: 0,
        root,
        isBusy: false,
        removed: false,
        job: null,
        jobIdValue: "",
        pollTimer: null,
        title: root.querySelector(".task-title h3"),
        subtitle: root.querySelector(".task-subtitle"),
        startBtn: root.querySelector(".start-task"),
        removeBtn: root.querySelector(".remove-task"),
        message: root.querySelector(".message"),
        state: root.querySelector(".state"),
        timeline: root.querySelector(".timeline"),
        downloadSlot: root.querySelector(".download-slot"),
        jobId: root.querySelector(".job-id"),
        log: root.querySelector(".log"),
        logText: root.querySelector("pre"),
        numberLabel: root.querySelector(".task-number"),
        inputs: {
          load: root.querySelector(".load-input"),
          discharge: root.querySelector(".discharge-input")
        },
        panels: {
          load: root.querySelector('[data-kind="load"]'),
          discharge: root.querySelector('[data-kind="discharge"]')
        }
      };
      root.dataset.taskId = id;
      task.inputs.load.id = `${id}-load`;
      task.inputs.discharge.id = `${id}-discharge`;
      wireDropPanel(task, "load", "No loading files selected");
      wireDropPanel(task, "discharge", "No discharge files selected");
      task.startBtn.addEventListener("click", () => startTask(task));
      task.removeBtn.addEventListener("click", () => removeTask(task));
      renderTags(task.state);
      renderTimeline(task.timeline);
      taskList.appendChild(fragment);
      tasks.set(id, task);
      renumberTasks();
      if (existingJob) {
        task.subtitle.textContent = `${existingJob.load_files.length} loading ${fileWord(existingJob.load_files.length)} and ${existingJob.discharge_files.length} discharge ${fileWord(existingJob.discharge_files.length)} from this server session.`;
        task.inputs.load.disabled = true;
        task.inputs.discharge.disabled = true;
        renderServerFileList(task, "load", existingJob.load_files);
        renderServerFileList(task, "discharge", existingJob.discharge_files);
        task.jobIdValue = existingJob.job_id;
        renderJob(task, existingJob);
        if (!isFinal(existingJob)) {
          task.isBusy = true;
          task.pollTimer = setInterval(() => pollTask(task), 1600);
        }
      } else {
        updateTaskReady(task);
      }
      updateQueueStats();
      return task;
    }

    function renderServerFileList(task, kind, names) {
      const panel = task.panels[kind];
      const list = panel.querySelector(".files");
      const count = panel.querySelector(".count");
      const meta = panel.querySelector(".format-note");
      list.innerHTML = "";
      panel.classList.add("ready", "locked");
      count.textContent = `${names.length} ${fileWord(names.length)}`;
      meta.textContent = "Server session";
      names.forEach((filename, index) => {
        const item = document.createElement("li");
        const row = document.createElement("div");
        const name = document.createElement("span");
        const size = document.createElement("span");
        row.className = "file-row";
        name.className = "file-name";
        size.className = "file-size";
        name.textContent = `${index + 1}. ${filename}`;
        size.textContent = "saved";
        row.append(name, size);
        item.appendChild(row);
        list.appendChild(item);
      });
    }

    function addSetupCheck(label, ok, detail) {
      const item = document.createElement("div");
      const title = document.createElement("strong");
      const meta = document.createElement("span");
      item.className = `check ${ok ? "ok" : "warn"}`;
      title.textContent = label;
      meta.textContent = ok ? "Ready" : detail;
      item.append(title, meta);
      setupChecks.appendChild(item);
    }

    async function checkSetup() {
      try {
        const res = await fetch("/api/setup");
        const data = await res.json();
        const ok = data.skill_root_ok && data.codex_ok && data.codex_auth_ok && data.tesseract_ok && data.packages_ok;
        setupSummary.textContent = ok ? "Ready" : "Needs attention";
        setupSummary.className = `summary-value ${ok ? "ok" : "warn"}`;
        setupDot.className = `setup-dot ${ok ? "ok" : "warn"}`;
        setupMessage.textContent = ok ? "All local checks passed." : "One or more local checks need attention.";
        setupChecks.innerHTML = "";
        addSetupCheck("Skill Scripts", data.skill_root_ok, data.skill_root || "Missing");
        addSetupCheck("Codex CLI", data.codex_ok, data.codex_bin || "Missing");
        addSetupCheck("Codex Login", data.codex_auth_ok, "Not authenticated");
        addSetupCheck("Tesseract OCR", data.tesseract_ok, "Not on PATH");
        const missingPackages = Object.entries(data.packages || {})
          .filter(([_name, ready]) => !ready)
          .map(([name]) => name)
          .join(", ");
        addSetupCheck("Python Packages", data.packages_ok, missingPackages || "Missing");
      } catch (error) {
        setupSummary.textContent = "Check failed";
        setupSummary.className = "summary-value fail";
        setupDot.className = "setup-dot fail";
        setupMessage.textContent = "Setup check failed.";
        setupChecks.innerHTML = "";
        const item = document.createElement("div");
        const title = document.createElement("strong");
        const meta = document.createElement("span");
        item.className = "check fail";
        title.textContent = "Setup API";
        meta.textContent = error.message || "Unavailable";
        item.append(title, meta);
        setupChecks.appendChild(item);
      }
    }

    async function loadExistingJobs() {
      try {
        const res = await fetch("/api/jobs");
        if (!res.ok) throw new Error("Could not load jobs");
        const data = await res.json();
        if (Array.isArray(data.jobs) && data.jobs.length) {
          data.jobs.forEach(job => createTask(job));
        } else {
          createTask();
        }
      } catch (error) {
        createTask();
      } finally {
        addTaskBtn.disabled = false;
        addTaskBottomBtn.disabled = false;
      }
    }

    startAllBtn.addEventListener("click", startAllReadyTasks);
    downloadAllBtn.addEventListener("click", downloadAllReadyTasks);
    addTaskBtn.addEventListener("click", addTaskAndShow);
    addTaskBottomBtn.addEventListener("click", addTaskAndShow);
    checkSetup();
    loadExistingJobs();
  </script>
</body>
</html>
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def public_job(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "job_id": job["job_id"],
        "task_number": job.get("task_number"),
        "status": job["status"],
        "phase": job["phase"],
        "method": job["method"],
        "message": job["message"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
        "load_files": [path.name for path in job["load_files"]],
        "discharge_files": [path.name for path in job["discharge_files"]],
        "download_ready": bool(job.get("output_path") and Path(job["output_path"]).exists()),
        "report_path": str(job.get("report_path") or ""),
        "extraction_path": str(job.get("extraction_path") or ""),
        "log": job.get("log", "")[-12000:],
    }


def normalize_task_number(value: Any) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def task_excel_filename(task_number: Any = None) -> str:
    number = normalize_task_number(task_number)
    if number is None:
        return "task_excel.xlsx"
    return f"task_{number}_excel.xlsx"


def parse_download_items(items: str) -> list[tuple[str, int | None]]:
    parsed: list[tuple[str, int | None]] = []
    for item in (items or "").split(","):
        clean = item.strip()
        if not clean:
            continue
        if ":" in clean:
            job_id, task_number = clean.split(":", 1)
        else:
            job_id, task_number = clean, None
        if re.fullmatch(r"[0-9a-f]{12}", job_id):
            parsed.append((job_id, normalize_task_number(task_number)))
    return parsed


def unique_archive_name(name: str, used: set[str]) -> str:
    if name not in used:
        used.add(name)
        return name
    path = Path(name)
    for index in range(2, 1000):
        candidate = f"{path.stem}_{index}{path.suffix}"
        if candidate not in used:
            used.add(candidate)
            return candidate
    raise RuntimeError(f"Could not create a unique filename for {name}")


def job_cutoff() -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=max(JOB_RETENTION_HOURS, 0))


def parse_job_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    with contextlib.suppress(ValueError):
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return None


def path_is_expired(path: Path, cutoff: datetime) -> bool:
    with contextlib.suppress(FileNotFoundError):
        modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        return modified < cutoff
    return False


def remove_path(path: Path) -> None:
    with contextlib.suppress(FileNotFoundError):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def safe_job_dir(value: Any) -> Path | None:
    if not value:
        return None
    with contextlib.suppress(Exception):
        path = Path(str(value)).expanduser().resolve()
        path.relative_to(JOB_ROOT)
        return path
    return None


async def remove_job(job_id: str, *, delete_files: bool) -> bool:
    job = jobs.pop(job_id, None)
    task = job_tasks.pop(job_id, None)
    if task and not task.done():
        task.cancel()
    if job:
        await stop_process(job.get("current_process"))
        if delete_files:
            job_dir = safe_job_dir(job.get("job_dir"))
            if job_dir:
                remove_path(job_dir)
    return bool(job)


async def cleanup_expired_jobs_once() -> dict[str, int]:
    if JOB_RETENTION_HOURS <= 0:
        return {"jobs": 0, "job_dirs": 0, "zips": 0}

    cutoff = job_cutoff()
    removed_jobs = 0
    removed_dirs = 0
    removed_zips = 0

    for job_id, job in list(jobs.items()):
        created_at = parse_job_time(job.get("created_at"))
        job_dir = safe_job_dir(job.get("job_dir"))
        expired = bool(created_at and created_at < cutoff)
        if not expired and job_dir and job_dir.exists():
            expired = path_is_expired(job_dir, cutoff)
        if expired:
            if await remove_job(job_id, delete_files=True):
                removed_jobs += 1

    if JOB_ROOT.exists():
        active_job_dirs = {
            job_dir for job in jobs.values() if (job_dir := safe_job_dir(job.get("job_dir"))) is not None
        }
        for path in JOB_ROOT.iterdir():
            if path in active_job_dirs:
                continue
            if path.is_dir() and re.fullmatch(r"[0-9a-f]{12}", path.name) and path_is_expired(path, cutoff):
                remove_path(path)
                removed_dirs += 1
            elif path.is_file() and path.name.startswith("all_task_excels_") and path.suffix == ".zip" and path_is_expired(path, cutoff):
                remove_path(path)
                removed_zips += 1

    return {"jobs": removed_jobs, "job_dirs": removed_dirs, "zips": removed_zips}


async def cleanup_loop() -> None:
    while True:
        with contextlib.suppress(Exception):
            await cleanup_expired_jobs_once()
        await asyncio.sleep(max(JOB_CLEANUP_INTERVAL_SECONDS, 60))


async def start_cleanup_loop() -> None:
    global cleanup_task
    await cleanup_expired_jobs_once()
    if JOB_RETENTION_HOURS > 0 and (cleanup_task is None or cleanup_task.done()):
        cleanup_task = asyncio.create_task(cleanup_loop())


async def stop_cleanup_loop() -> None:
    global cleanup_task
    if cleanup_task and not cleanup_task.done():
        cleanup_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await cleanup_task
    cleanup_task = None


def update_job(job: dict[str, Any], **changes: Any) -> None:
    job.update(changes)
    job["updated_at"] = now_iso()


def append_log(job: dict[str, Any], title: str, text: str) -> None:
    clean = text.strip()
    if not clean:
        return
    previous = job.get("log", "")
    job["log"] = (previous + f"\n\n[{title}]\n{clean}").strip()
    job["updated_at"] = now_iso()


def extraction_missing_required(extraction: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for index, section in enumerate(extraction.get("load") or [], start=1):
        events = section.get("events", {}) if isinstance(section, dict) else {}
        for key in REQUIRED_LOAD_EVENTS:
            if not events.get(key):
                missing.append(f"LOAD {index} {key.replace('_', ' ').upper()}")
    for index, section in enumerate(extraction.get("discharge") or [], start=1):
        events = section.get("events", {}) if isinstance(section, dict) else {}
        for key in REQUIRED_DISCHARGE_EVENTS:
            if not events.get(key):
                missing.append(f"DISCHARGE {index} {key.replace('_', ' ').upper()}")
    return missing


def partial_records(partial: dict[str, Any], section: str | None = None) -> list[dict[str, Any]]:
    sections = (section,) if section else ("load", "discharge")
    records: list[dict[str, Any]] = []
    for name in sections:
        for record in partial.get(name) or []:
            if isinstance(record, dict):
                records.append(record)
    return records


def records_needing_codex(partial: dict[str, Any]) -> list[dict[str, Any]]:
    return [record for record in partial_records(partial) if not record.get("ok")]


def clean_python_section(record: dict[str, Any]) -> dict[str, Any]:
    item = {
        key: value
        for key, value in record.items()
        if key not in {"ok", "missing", "error", "source_path", "section", "index"}
    }
    item["method"] = "python_ocr"
    return item


def empty_codex_section(section: str, record: dict[str, Any]) -> dict[str, Any]:
    if section == "load":
        base: dict[str, Any] = {
            "port": None,
            "berth": None,
            "terminal": None,
            "allowed_hours": None,
            "document_onboard_hours": None,
            "events": {},
        }
    else:
        base = {
            "port": None,
            "berth": None,
            "quantity": None,
            "rate": None,
            "allowed_hours": None,
            "events": {},
            "deductions": {
                "shifting_hours": None,
                "rate_difference_hours": None,
                "night_navigation_hours": None,
                "document_onboard_hours": None,
            },
        }
    base.update({"source": record.get("source"), "original_index": record.get("index"), "method": "codex_missing"})
    return base


def normalize_confidence_notes(value: Any) -> list[dict[str, str]]:
    if isinstance(value, list):
        return [
            {"field": str(item.get("field", "")), "note": str(item.get("note", ""))}
            for item in value
            if isinstance(item, dict)
        ]
    if isinstance(value, dict):
        return [{"field": str(field), "note": str(note)} for field, note in value.items()]
    return []


def merge_hybrid_extraction(partial: dict[str, Any], codex: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {
        "metadata": codex.get("metadata") if isinstance(codex.get("metadata"), dict) else partial.get("metadata", {}),
        "load": [],
        "discharge": [],
        "confidence_notes": normalize_confidence_notes(codex.get("confidence_notes")),
    }
    for section in ("load", "discharge"):
        codex_sections = [item for item in codex.get(section) or [] if isinstance(item, dict)]
        codex_index = 0
        for record in partial.get(section) or []:
            if not isinstance(record, dict):
                continue
            if record.get("ok"):
                merged[section].append(clean_python_section(record))
                continue
            if codex_index < len(codex_sections):
                item = dict(codex_sections[codex_index])
                codex_index += 1
            else:
                item = empty_codex_section(section, record)
                merged["confidence_notes"].append(
                    {
                        "field": f"{section}.{record.get('index')}",
                        "note": "Codex did not return a section for this source; workbook was built with blanks for review.",
                    }
                )
            item.setdefault("source", record.get("source"))
            item.setdefault("original_index", record.get("index"))
            item["method"] = "codex"
            merged[section].append(item)
        for extra in codex_sections[codex_index:]:
            item = dict(extra)
            item["method"] = "codex_extra"
            merged[section].append(item)
            merged["confidence_notes"].append(
                {
                    "field": section,
                    "note": "Codex returned an extra section beyond the files marked unreadable by Python.",
                }
            )
    return merged


def safe_filename(name: str, index: int) -> str:
    suffix = Path(name).suffix.lower()
    stem = Path(name).stem
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-") or "upload"
    return f"{index:02d}_{stem}{suffix}"


async def save_uploads(job_dir: Path, section: str, uploads: list[UploadFile]) -> list[Path]:
    target_dir = job_dir / "uploads" / section
    target_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for index, upload in enumerate(uploads, start=1):
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {upload.filename}")
        path = target_dir / safe_filename(upload.filename or f"{section}_{index}{suffix}", index)
        content = await upload.read()
        if not content:
            raise HTTPException(status_code=400, detail=f"Empty upload: {upload.filename}")
        path.write_bytes(content)
        saved.append(path)
    return saved


async def run_command(
    cmd: list[str],
    *,
    cwd: Path,
    timeout: int,
    job: dict[str, Any] | None = None,
) -> tuple[int, str, str]:
    env = os.environ.copy()
    env.setdefault("TERM", "xterm-256color")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(cwd),
        env=env,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    if job is not None:
        job["current_process"] = proc
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        if proc.returncode is None:
            proc.kill()
        await proc.wait()
        return 124, "", f"Command timed out after {timeout} seconds"
    except asyncio.CancelledError:
        if proc.returncode is None:
            proc.terminate()
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(proc.wait(), timeout=3)
        if proc.returncode is None:
            proc.kill()
            await proc.wait()
        raise
    finally:
        if job is not None and job.get("current_process") is proc:
            job.pop("current_process", None)
    return (
        proc.returncode or 0,
        stdout.decode("utf-8", errors="replace"),
        stderr.decode("utf-8", errors="replace"),
    )


def check_paths() -> None:
    if not SKILL_ROOT.exists():
        raise RuntimeError(f"DEM skill root does not exist: {SKILL_ROOT}")
    partial = SKILL_ROOT / "scripts" / "dem_claim_extract_partial.py"
    from_json = SKILL_ROOT / "scripts" / "dem_claim_from_json.py"
    if not partial.exists() or not from_json.exists():
        raise RuntimeError(f"DEM skill scripts are missing under: {SKILL_ROOT}")
    if not Path(CODEX_BIN).is_file() and not shutil.which(CODEX_BIN):
        raise RuntimeError(f"Codex CLI was not found: {CODEX_BIN}")


async def build_workbook_from_extraction(
    job: dict[str, Any],
    extraction: dict[str, Any],
    extraction_path: Path,
    *,
    method: str,
    ready_message: str,
) -> None:
    output = Path(job["job_dir"]) / "dem_claim.xlsx"
    report_path = Path(job["job_dir"]) / "dem_claim.report.json"
    cmd = [
        sys.executable,
        str(SKILL_ROOT / "scripts" / "dem_claim_from_json.py"),
        "--json",
        str(extraction_path),
        "--output",
        str(output),
        "--report",
        str(report_path),
        "--allow-missing",
    ]
    missing_required = extraction_missing_required(extraction)
    if missing_required:
        job["warnings"] = [f"Required field needs review: {', '.join(missing_required)}"]

    update_job(job, phase="excel-build", message="Building workbook from extracted values...")
    code, stdout, stderr = await run_command(cmd, cwd=SKILL_ROOT, timeout=180, job=job)
    append_log(job, "JSON workbook stdout", stdout)
    append_log(job, "JSON workbook stderr", stderr)
    if code != 0 or not output.exists():
        raise RuntimeError(f"Workbook build from extraction JSON failed with exit code {code}")

    message = ready_message
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        warnings = [item for item in report.get("messages", []) if str(item).startswith("WARNING")]
        if warnings:
            job["warnings"] = warnings
            message = f"Workbook generated with {len(warnings)} warning(s)."
    except Exception:
        pass

    update_job(
        job,
        status="completed",
        phase="complete",
        method=method,
        message=message,
        output_path=str(output),
        extraction_path=str(extraction_path),
        report_path=str(report_path),
    )


async def run_deterministic(job: dict[str, Any]) -> bool:
    job_dir = Path(job["job_dir"])
    debug_dir = job_dir / "debug_ocr"
    partial_path = job_dir / "python_partial_extraction.json"
    cmd = [
        sys.executable,
        str(SKILL_ROOT / "scripts" / "dem_claim_extract_partial.py"),
        "--json-output",
        str(partial_path),
        "--debug-dir",
        str(debug_dir),
    ]
    if job["load_files"]:
        cmd.append("--load-source")
        cmd.extend(str(path) for path in job["load_files"])
    if job["discharge_files"]:
        cmd.append("--discharge-source")
        cmd.extend(str(path) for path in job["discharge_files"])

    update_job(job, status="processing", phase="python-ocr", method="Python OCR", message="Running deterministic OCR...")
    code, stdout, stderr = await run_command(cmd, cwd=SKILL_ROOT, timeout=300, job=job)
    append_log(job, "Python OCR stdout", stdout)
    append_log(job, "Python OCR stderr", stderr)
    if code != 0 or not partial_path.exists():
        update_job(
            job,
            status="fallback",
            phase="codex-fallback",
            method="Codex fallback",
            message="Python OCR could not complete. Starting Codex for all uploaded files...",
        )
        return False

    partial = json.loads(partial_path.read_text(encoding="utf-8"))
    job["partial_extraction_path"] = str(partial_path)
    job["hybrid_summary"] = partial.get("summary", {})
    needs_codex = records_needing_codex(partial)
    total = len(partial_records(partial))
    python_count = total - len(needs_codex)
    if not needs_codex:
        await build_workbook_from_extraction(
            job,
            partial,
            partial_path,
            method="Python OCR",
            ready_message="Workbook generated by deterministic Python OCR.",
        )
        return True

    update_job(
        job,
        status="fallback",
        phase="codex-fallback",
        method="Hybrid OCR",
        message=f"Python OCR read {python_count}/{total} source(s). Starting Codex for only {len(needs_codex)} unreadable source(s)...",
    )
    return False


def render_pdf(path: Path, target_dir: Path, prefix: str) -> list[Path]:
    if fitz is None:
        raise RuntimeError("PyMuPDF is not installed. Install requirements.txt before PDF fallback.")
    rendered: list[Path] = []
    doc = fitz.open(path)
    try:
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), alpha=False)
            out = target_dir / f"{prefix}_page_{page_index + 1:02d}.png"
            pix.save(out)
            rendered.append(out)
    finally:
        doc.close()
    return rendered


def convert_image(path: Path, target_dir: Path, prefix: str) -> Path:
    if Image is None:
        raise RuntimeError("Pillow is not installed. Install requirements.txt before image fallback.")
    out = target_dir / f"{prefix}.png"
    with Image.open(path) as image:
        image.convert("RGB").save(out)
    return out


def prepare_codex_images(job: dict[str, Any], targets: list[dict[str, Any]] | None = None) -> list[tuple[str, Path]]:
    image_dir = Path(job["job_dir"]) / "codex_images"
    image_dir.mkdir(parents=True, exist_ok=True)
    prepared: list[tuple[str, Path]] = []
    if targets is None:
        targets = []
        for section in ("load", "discharge"):
            source_key = "load_files" if section == "load" else "discharge_files"
            for index, source in enumerate(job[source_key], start=1):
                targets.append({"section": section, "index": index, "source_path": str(source), "source": source.name})
    for target in targets:
        section = str(target.get("section") or "")
        index = int(target.get("index") or 0)
        source = Path(str(target.get("source_path") or ""))
        suffix = source.suffix.lower()
        prefix = f"{section}_{index:02d}_{source.stem}"
        label_base = f"{section} file {index}: {source.name}"
        if suffix == ".pdf":
            for page_number, page_path in enumerate(render_pdf(source, image_dir, prefix), start=1):
                prepared.append((f"{label_base} page {page_number}", page_path))
        elif suffix in IMAGE_SUFFIXES:
            prepared.append((label_base, source))
        elif suffix in CONVERTIBLE_IMAGE_SUFFIXES:
            prepared.append((label_base, convert_image(source, image_dir, prefix)))
        else:
            raise RuntimeError(f"Unsupported fallback file type: {source.name}")
    return prepared


def codex_prompt(job: dict[str, Any], images: list[tuple[str, Path]], targets: list[dict[str, Any]] | None = None) -> str:
    image_list = "\n".join(f"- {label}" for label, _path in images)
    if targets:
        load_targets = [target for target in targets if target.get("section") == "load"]
        discharge_targets = [target for target in targets if target.get("section") == "discharge"]
        scope_note = textwrap.dedent(
            f"""
            Python OCR already read the other uploaded files. Only extract the attached unreadable files.
            Return the load array with exactly {len(load_targets)} item(s), in the attached loading-file order.
            Return the discharge array with exactly {len(discharge_targets)} item(s), in the attached discharge-file order.
            Do not create placeholder sections for files that were already handled by Python OCR.
            """
        ).strip()
    else:
        scope_note = "The first group is loading files, in upload order. The second group is discharge files, in upload order."
    return textwrap.dedent(
        f"""
        You are a visual extraction worker for DEM claim Excel generation.
        Do not inspect local files, search the repository, run shell commands, browse the web, or use tools.
        Use only the attached images and the rules in this prompt.

        Use the DEM claim Excel extraction rules.

        Read the attached SOF/time-sheet images and return extraction JSON only.
        {scope_note}

        Attached files:
        {image_list}

        Required load events: NOR tendered, all fast, hose on, load commence, load complete, hose off.
        Anchor up is useful and should be extracted when present.
        Required discharge events: NOR tendered, anchor up, all fast, hose on, discharge commence, discharge complete, hose off.

        Event row mapping:
        - load nor_tendered: NOR tendered / NOR notice row.
        - load all_fast: all fast / alongside at berth row.
        - load hose_on: completed hose connecting / hose on row.
        - load load_commence: commenced loading row.
        - load load_complete: completed loading row.
        - load hose_off: completed disconnecting / hose off row.
        - discharge nor_tendered: NOR tendered / NOR notice row.
        - discharge anchor_up: anchor up shifting to berth row; use null if the row is blank or crossed out.
        - discharge all_fast: all fast / alongside at berth row.
        - discharge hose_on: completed hose connecting / hose on row.
        - discharge disch_commence: commenced loading/discharging row.
        - discharge disch_complete: completed loading/discharging row.
        - discharge hose_off: completed disconnecting / hose off row.

        Use YYYY-MM-DD HH:MM for event values and YYYY-MM-DD for date-only metadata.
        Preserve leading zero hours such as 06:30.
        Convert handwritten compact times like 0630 to 06:30.
        Use null for any value you cannot read confidently.
        Put uncertainty in confidence_notes as field/note objects.
        Do not invent missing values.
        Before finalizing, re-check each required event against its original row.
        For handwritten times, inspect each digit carefully; do not round or infer a cleaner value from nearby rows.
        Pay special attention to ambiguous 0/2/5/7 digits.

        Build the JSON shape expected by dem_claim_from_json.py:
        metadata, load array, discharge array, confidence_notes array.
        """
    ).strip()


async def run_codex_fallback(job: dict[str, Any]) -> None:
    partial_path_value = job.get("partial_extraction_path")
    partial = json.loads(Path(partial_path_value).read_text(encoding="utf-8")) if partial_path_value else None
    targets = records_needing_codex(partial) if isinstance(partial, dict) else None
    prepared = prepare_codex_images(job, targets)
    if not prepared:
        raise RuntimeError("No images were available for Codex fallback.")

    job_dir = Path(job["job_dir"])
    schema_path = job_dir / "codex_extraction_schema.json"
    codex_extraction_path = job_dir / "codex_extraction.json"
    extraction_path = job_dir / "extraction.json"
    schema_path.write_text(json.dumps(CODEX_EXTRACTION_SCHEMA, indent=2), encoding="utf-8")

    prompt = codex_prompt(job, prepared, targets)
    cmd = [
        CODEX_BIN,
        "exec",
        "--ephemeral",
        "--ignore-rules",
        "--skip-git-repo-check",
        "-m",
        CODEX_FALLBACK_MODEL,
        "-c",
        f'model_reasoning_effort="{CODEX_FALLBACK_REASONING_EFFORT}"',
        "--sandbox",
        "read-only",
        "--output-schema",
        str(schema_path),
        "-o",
        str(codex_extraction_path),
        prompt,
    ]
    if CODEX_FALLBACK_CLEAN_CONFIG:
        cmd.insert(2, "--ignore-user-config")
    for _label, path in prepared:
        cmd.extend(["--image", str(path)])

    update_job(
        job,
        status="fallback",
        phase="codex-reading",
        method="Hybrid OCR" if partial else "Codex fallback",
        message=(
            f"Codex is reading {len(targets)} unreadable source(s)..."
            if targets is not None
            else "Codex is reading the uploaded files..."
        ),
    )
    code, stdout, stderr = await run_command(cmd, cwd=job_dir, timeout=900, job=job)
    append_log(job, "Codex stdout", stdout)
    append_log(job, "Codex stderr", stderr)
    if code != 0:
        detail = (stderr or stdout).strip()
        detail_tail = detail[-1400:] if detail else "No Codex error detail was returned."
        if "usage limit" in detail.lower():
            raise RuntimeError(f"Codex fallback hit the current account usage limit. {detail_tail}")
        raise RuntimeError(f"Codex fallback failed with exit code {code}. {detail_tail}")
    if not codex_extraction_path.exists():
        codex_extraction_path.write_text(stdout.strip(), encoding="utf-8")

    codex_extraction = json.loads(codex_extraction_path.read_text(encoding="utf-8"))
    extraction = merge_hybrid_extraction(partial, codex_extraction) if isinstance(partial, dict) else codex_extraction
    extraction["confidence_notes"] = normalize_confidence_notes(extraction.get("confidence_notes"))
    extraction_path.write_text(json.dumps(extraction, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = job.get("hybrid_summary") or {}
    method = "Hybrid OCR" if isinstance(partial, dict) else "Codex fallback"
    ready_message = (
        f"Workbook generated by hybrid OCR: Python read {summary.get('python_complete', 0)} source(s); "
        f"Codex read {summary.get('needs_codex', len(targets or []))} source(s)."
        if isinstance(partial, dict)
        else "Workbook generated by Codex fallback."
    )
    await build_workbook_from_extraction(
        job,
        extraction,
        extraction_path,
        method=method,
        ready_message=ready_message,
    )


async def process_job(job_id: str) -> None:
    job = jobs.get(job_id)
    if not job:
        return
    try:
        check_paths()
        deterministic_ok = await run_deterministic(job)
        if deterministic_ok:
            return
        await run_codex_fallback(job)
    except asyncio.CancelledError:
        if job_id in jobs:
            append_log(job, "Canceled", "Task was removed by the user.")
            update_job(job, status="failed", phase="failed", message="Task canceled.")
        raise
    except Exception as exc:
        append_log(job, "Error", str(exc))
        update_job(job, status="failed", phase="failed", message=str(exc))
    finally:
        job_tasks.pop(job_id, None)


def package_ok(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False


def codex_auth_ok() -> bool:
    try:
        result = subprocess.run(
            [CODEX_BIN, "login", "status"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


async def stop_process(proc: Any) -> None:
    if not proc or proc.returncode is not None:
        return
    with contextlib.suppress(ProcessLookupError):
        proc.terminate()
    with contextlib.suppress(asyncio.TimeoutError):
        await asyncio.wait_for(proc.wait(), timeout=3)
    if proc.returncode is None:
        with contextlib.suppress(ProcessLookupError):
            proc.kill()
        await proc.wait()


@app.on_event("startup")
async def app_startup() -> None:
    await start_cleanup_loop()


@app.on_event("shutdown")
async def app_shutdown() -> None:
    await stop_cleanup_loop()


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return HTML


@app.get("/api/setup")
async def setup_status() -> JSONResponse:
    skill_root_ok = SKILL_ROOT.exists()
    scripts_ok = all(
        (SKILL_ROOT / "scripts" / name).exists()
        for name in ("dem_claim_extract_partial.py", "dem_claim_from_json.py")
    )
    codex_ok = bool(Path(CODEX_BIN).is_file() or shutil.which(CODEX_BIN))
    tesseract_ok = bool(shutil.which("tesseract"))
    package_status = {
        "fastapi": package_ok("fastapi"),
        "openpyxl": package_ok("openpyxl"),
        "PIL": package_ok("PIL"),
        "pypdf": package_ok("pypdf"),
        "fitz": package_ok("fitz"),
    }
    return JSONResponse(
        {
            "skill_root": str(SKILL_ROOT),
            "skill_root_ok": skill_root_ok and scripts_ok,
            "codex_bin": CODEX_BIN,
            "codex_configured_bin": CODEX_CONFIGURED_BIN or None,
            "codex_ok": codex_ok,
            "codex_auth_ok": await asyncio.to_thread(codex_auth_ok),
            "tesseract_ok": tesseract_ok,
            "packages": package_status,
            "packages_ok": all(package_status.values()),
            "job_retention_hours": JOB_RETENTION_HOURS,
            "job_cleanup_interval_seconds": JOB_CLEANUP_INTERVAL_SECONDS,
        }
    )


@app.post("/api/jobs", status_code=202)
async def create_job(
    load_files: Annotated[list[UploadFile], File()],
    discharge_files: Annotated[list[UploadFile], File()],
    task_number: Annotated[str | None, Form()] = None,
) -> JSONResponse:
    if not load_files:
        raise HTTPException(status_code=400, detail="At least one loading file is required.")
    if not discharge_files:
        raise HTTPException(status_code=400, detail="At least one discharge file is required.")

    JOB_ROOT.mkdir(parents=True, exist_ok=True)
    job_id = uuid.uuid4().hex[:12]
    job_dir = JOB_ROOT / job_id
    job_dir.mkdir(parents=True, exist_ok=False)
    saved_load = await save_uploads(job_dir, "load", load_files)
    saved_discharge = await save_uploads(job_dir, "discharge", discharge_files)

    job = {
        "job_id": job_id,
        "task_number": normalize_task_number(task_number),
        "job_dir": str(job_dir),
        "status": "queued",
        "phase": "queued",
        "method": "pending",
        "message": "Job queued.",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "load_files": saved_load,
        "discharge_files": saved_discharge,
        "log": "",
    }
    jobs[job_id] = job
    job_tasks[job_id] = asyncio.create_task(process_job(job_id))
    return JSONResponse(public_job(job), status_code=202)


@app.get("/api/jobs")
async def list_jobs() -> JSONResponse:
    ordered = sorted(jobs.values(), key=lambda job: job.get("created_at", ""), reverse=True)
    return JSONResponse({"jobs": [public_job(job) for job in ordered]})


@app.get("/api/jobs/download-all")
async def download_all_jobs(items: str = "") -> FileResponse:
    parsed = parse_download_items(items)
    if not parsed:
        completed = [
            job
            for job in sorted(jobs.values(), key=lambda item: item.get("created_at", ""))
            if job.get("status") == "completed"
        ]
        parsed = [(job["job_id"], normalize_task_number(job.get("task_number"))) for job in completed]

    zip_path = JOB_ROOT / f"all_task_excels_{uuid.uuid4().hex[:8]}.zip"
    used_names: set[str] = set()
    count = 0
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        for job_id, task_number in parsed:
            job = jobs.get(job_id)
            output_value = job.get("output_path") if job else None
            output = Path(output_value) if output_value else None
            if not job or job.get("status") != "completed" or not output or not output.exists():
                continue
            filename = task_excel_filename(task_number or job.get("task_number"))
            archive.write(output, unique_archive_name(filename, used_names))
            count += 1
    if count == 0:
        zip_path.unlink(missing_ok=True)
        raise HTTPException(status_code=404, detail="No completed workbooks are ready to download.")
    return FileResponse(
        zip_path,
        filename="all_task_excels.zip",
        media_type="application/zip",
        background=BackgroundTask(lambda: zip_path.unlink(missing_ok=True)),
    )


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str) -> JSONResponse:
    deleted = await remove_job(job_id, delete_files=True)
    if not deleted and re.fullmatch(r"[0-9a-f]{12}", job_id):
        orphan_dir = (JOB_ROOT / job_id).resolve()
        with contextlib.suppress(ValueError):
            orphan_dir.relative_to(JOB_ROOT)
            if orphan_dir.exists():
                remove_path(orphan_dir)
                deleted = True
    return JSONResponse({"deleted": deleted, "job_id": job_id})


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str) -> JSONResponse:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return JSONResponse(public_job(job))


@app.get("/api/jobs/{job_id}/download")
async def download_job(job_id: str, task: int | None = None) -> FileResponse:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    output = job.get("output_path")
    if job.get("status") != "completed" or not output or not Path(output).exists():
        raise HTTPException(status_code=404, detail="Workbook is not ready.")
    return FileResponse(
        output,
        filename=task_excel_filename(task or job.get("task_number")),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=int(os.environ.get("PORT", "8000")), reload=False)
