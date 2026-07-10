#!/usr/bin/env python3
"""Check Auto CAD Drawing and its optional server-side Codex advisory."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from codex_advisory import SCHEMA_PATH, advisory_status
from codex_runtime import codex_environment


ROOT = Path(__file__).resolve().parents[1]


def report(name: str, ok: bool, detail: str) -> bool:
    state = "OK" if ok else ("LIMITED" if "usage limit" in detail.lower() else "MISSING")
    print(f"{state:7} {name}: {detail}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-codex", action="store_true", help="require the deployment Codex advisory to be ready")
    parser.add_argument("--smoke-codex", action="store_true", help="run a small authenticated codex exec request")
    args = parser.parse_args()

    if args.require_codex or args.smoke_codex:
        os.environ["AUTO_CAD_CODEX_ADVISORY"] = "1"
    status = advisory_status()

    passed = True
    passed &= report("advisory schema", SCHEMA_PATH.is_file(), str(SCHEMA_PATH))
    if args.require_codex or args.smoke_codex:
        passed &= report("Codex CLI", status["available"], status["codex_bin"] or status["message"])
        passed &= report("Codex login", status["authenticated"], status["auth_method"] or status["message"])

    if args.smoke_codex and passed:
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
            "-C",
            str(ROOT),
            "Return exactly OK.",
        ]
        try:
            completed = subprocess.run(
                command,
                env=codex_environment(),
                stdin=subprocess.DEVNULL,
                text=True,
                capture_output=True,
                timeout=120,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            passed = report("Codex smoke", False, str(exc)) and passed
        else:
            detail = (completed.stdout or completed.stderr).strip().replace("\n", " ")[-300:]
            passed = report("Codex smoke", completed.returncode == 0, detail or "Codex completed") and passed

    if not passed:
        print("\nIf login is missing, run Codex login as the service user. If the smoke is LIMITED, wait for the account reset and retry.")
        return 1
    print("\nAuto CAD Drawing deployment checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
