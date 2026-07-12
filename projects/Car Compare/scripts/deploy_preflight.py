#!/usr/bin/env python3
"""Verify that this checkout can use Codex on its deployment host."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
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
    parser.add_argument("--smoke-browser", action="store_true", help="verify the persistent collection browser endpoint")
    args = parser.parse_args()

    status = codex_login_status()
    skill = ROOT / "skills" / "generation-impact-research" / "SKILL.md"
    schema_files = (
        ROOT / "car_compare" / "collector_schema.json",
        ROOT / "car_compare" / "generation_impact_schema.json",
    )
    browser_server = ROOT / "scripts" / "car_compare_browser_mcp.mjs"
    browser_dependencies = (
        ROOT / "node_modules" / "playwright",
        ROOT / "node_modules" / "@modelcontextprotocol" / "sdk",
    )

    passed = True
    passed &= report("Codex CLI", status["available"], status["codexPath"] or status["message"])
    passed &= report("Codex login", status["authenticated"], status["authMethod"] or status["message"])
    passed &= report("project skill", skill.is_file(), str(skill.parent))
    passed &= report("output schemas", all(path.is_file() for path in schema_files), ", ".join(path.name for path in schema_files))
    passed &= report("Node.js", bool(shutil.which("node")), shutil.which("node") or "Install Node.js 20+")
    passed &= report("browser MCP", browser_server.is_file(), str(browser_server))
    passed &= report(
        "browser packages",
        all(path.exists() for path in browser_dependencies),
        "installed" if all(path.exists() for path in browser_dependencies) else "Run npm install in the Car Compare folder",
    )

    if args.smoke_browser and passed:
        cdp_url = os.environ.get("CAR_COMPARE_BROWSER_CDP_URL", "").rstrip("/")
        if not cdp_url:
            passed = report("browser endpoint", False, "Set CAR_COMPARE_BROWSER_CDP_URL after starting scripts/start_collection_browser.sh") and passed
        else:
            try:
                with urllib.request.urlopen(f"{cdp_url}/json/version", timeout=5) as response:
                    browser_info = json.loads(response.read().decode("utf-8"))
            except Exception as exc:
                passed = report("browser endpoint", False, str(exc)) and passed
            else:
                passed &= report("browser endpoint", bool(browser_info.get("Browser")), browser_info.get("Browser", "No browser identity"))

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
