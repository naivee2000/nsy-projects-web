#!/usr/bin/env python3
"""Optional Codex advisory for uploads the deterministic CAD router rejects."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from codex_runtime import codex_environment, codex_login_status


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "codex_advisory_schema.json"


def advisory_enabled() -> bool:
    return os.environ.get("AUTO_CAD_CODEX_ADVISORY", "0").lower() in {"1", "true", "yes"}


def advisory_status() -> dict[str, Any]:
    status = codex_login_status()
    enabled = advisory_enabled()
    schema_ok = SCHEMA_PATH.is_file()
    return {
        "enabled": enabled,
        "ready": bool(enabled and schema_ok and status["available"] and status["authenticated"]),
        "schema_ok": schema_ok,
        **status,
    }


def analyze_rejected_upload(analysis: dict[str, Any], job_dir: Path, timeout: int = 180) -> dict[str, Any]:
    """Return a non-authoritative explanation; never unlock a generator."""
    status = advisory_status()
    if not status["ready"]:
        return {
            "status": "unavailable",
            "summary": "Codex advisory is not ready on this deployment host.",
            "detected_project_ids": [],
            "drawing_kinds": [],
            "sensor_models": [],
            "recommended_next_step": status["message"],
            "notes": [],
        }

    output_path = job_dir / "codex-advisory.json"
    prompt = f"""
You are the read-only advisory step for the Auto CAD Drawing app.

The deterministic router rejected an uploaded PDF set. Review only the supplied
router summary. Explain what project/drawing type appears to be present and the
next safe implementation step. Do not claim that a CAD generator exists. Do not
override the deterministic decision, edit files, or run commands.

Supported deterministic projects: CPX26051 and CPX25034.
Known unsupported project: CPX25063.

Router summary:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

Return only JSON matching the provided schema.
""".strip()
    command = [
        status["codex_bin"],
        "--ask-for-approval",
        "never",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--output-schema",
        str(SCHEMA_PATH),
        "-o",
        str(output_path),
        "-C",
        str(ROOT),
        prompt,
    ]
    try:
        completed = subprocess.run(
            command,
            env=codex_environment(),
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _failure(f"Codex advisory could not run: {exc}")
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip().replace("\n", " ")[-800:]
        return _failure(f"Codex advisory failed: {detail or 'no error detail'}")
    try:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _failure(f"Codex advisory returned invalid JSON: {exc}")
    payload["status"] = "analyzed"
    return payload


def _failure(message: str) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "summary": message,
        "detected_project_ids": [],
        "drawing_kinds": [],
        "sensor_models": [],
        "recommended_next_step": "Use the deterministic router result and review the upload manually.",
        "notes": [],
    }
