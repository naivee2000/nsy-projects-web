#!/usr/bin/env python3
"""Verify that this checkout can use Codex on its deployment host."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from car_compare.codex_cli import codex_environment, codex_login_status  # noqa: E402


def report(name: str, ok: bool, detail: str) -> bool:
    state = "OK" if ok else ("LIMITED" if "usage limit" in detail.lower() else "MISSING")
    print(f"{state:7} {name}: {detail}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-codex", action="store_true", help="run a small authenticated codex exec request")
    args = parser.parse_args()

    status = codex_login_status()
    skill = ROOT / "skills" / "generation-impact-research" / "SKILL.md"
    schema_files = (
        ROOT / "car_compare" / "collector_schema.json",
        ROOT / "car_compare" / "generation_impact_schema.json",
    )

    passed = True
    passed &= report("Codex CLI", status["available"], status["codexPath"] or status["message"])
    passed &= report("Codex login", status["authenticated"], status["authMethod"] or status["message"])
    passed &= report("project skill", skill.is_file(), str(skill.parent))
    passed &= report("output schemas", all(path.is_file() for path in schema_files), ", ".join(path.name for path in schema_files))

    if args.smoke_codex and passed:
        command = [
            status["codexPath"],
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
    print("\nCar Compare is ready to use the deployment host's Codex account.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
