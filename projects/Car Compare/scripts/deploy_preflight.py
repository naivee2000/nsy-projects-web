#!/usr/bin/env python3
"""Verify that this checkout can use Codex on its deployment host."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from car_compare.codex_cli import codex_environment, codex_login_status  # noqa: E402
from car_compare.capture_cache import CaptureCache  # noqa: E402
from car_compare.sources.chrome_host import host_chrome_status  # noqa: E402


def report(name: str, ok: bool, detail: str) -> bool:
    state = "OK" if ok else ("LIMITED" if "usage limit" in detail.lower() else "MISSING")
    print(f"{state:7} {name}: {detail}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-codex", action="store_true", help="run a small authenticated codex exec request")
    parser.add_argument("--smoke-browser", action="store_true", help="verify the persistent collection browser endpoint")
    parser.add_argument(
        "--desktop-fallback",
        action="store_true",
        help="verify the Codex Desktop app and installed marketplace fallback skill without spending model usage",
    )
    args = parser.parse_args()

    status = codex_login_status()
    project_skills = (
        ROOT / "skills" / "generation-impact-research" / "SKILL.md",
        ROOT / "skills" / "collect-car-marketplaces" / "SKILL.md",
    )
    schema_files = (
        ROOT / "car_compare" / "collector_schema.json",
        ROOT / "car_compare" / "generation_impact_schema.json",
        ROOT / "car_compare" / "web_search_capture_schema.json",
    )
    browser_server = ROOT / "scripts" / "car_compare_browser_mcp.mjs"
    chrome_host_script = ROOT / "scripts" / "chrome_host_capture.applescript"
    browser_dependencies = (
        ROOT / "node_modules" / "playwright",
        ROOT / "node_modules" / "@modelcontextprotocol" / "sdk",
    )

    passed = True
    passed &= report("Codex CLI", status["available"], status["codexPath"] or status["message"])
    passed &= report("Codex login", status["authenticated"], status["authMethod"] or status["message"])
    search_supported = False
    search_detail = "Codex CLI with --search support is required"
    if status["available"]:
        checked = subprocess.run(
            [status["codexPath"], "--help"],
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        search_supported = checked.returncode == 0 and "--search" in checked.stdout
        if search_supported:
            search_detail = "native live web search available"
        elif (checked.stderr or checked.stdout).strip():
            search_detail = (checked.stderr or checked.stdout).strip()[-300:]
    passed &= report("Codex web search", search_supported, search_detail)
    passed &= report(
        "project skills",
        all(skill.is_file() for skill in project_skills),
        ", ".join(skill.parent.name for skill in project_skills),
    )
    passed &= report("output schemas", all(path.is_file() for path in schema_files), ", ".join(path.name for path in schema_files))
    passed &= report("Node.js", bool(shutil.which("node")), shutil.which("node") or "Install Node.js 20+")
    passed &= report("browser MCP", browser_server.is_file(), str(browser_server))
    passed &= report(
        "browser packages",
        all(path.exists() for path in browser_dependencies),
        "installed" if all(path.exists() for path in browser_dependencies) else "Run npm install in the Car Compare folder",
    )
    cache_dir = Path(os.environ.get("CAR_COMPARE_CACHE_DIR", ROOT / "data" / "cache")).expanduser()
    try:
        cache = CaptureCache(cache_dir / "collector_cache.sqlite3")
        cache_status = cache.status()
        cache_ok = bool(cache_status["ready"])
        cache_detail = f"{cache_status['path']} (all cache entries <=3d)"
    except Exception as exc:
        cache_ok = False
        cache_detail = str(exc)
    passed &= report("persistent cache", cache_ok, cache_detail)

    if shutil.which("node") and browser_server.is_file():
        checked = subprocess.run(
            [shutil.which("node") or "node", str(browser_server), "--self-test"],
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
        passed &= report(
            "browser worker self-test",
            checked.returncode == 0,
            (checked.stdout or checked.stderr).strip()[-500:],
        )

    if args.desktop_fallback:
        desktop_bundles = (Path("/Applications/ChatGPT.app"), Path("/Applications/Codex.app"))
        desktop_installed = any(path.exists() for path in desktop_bundles)
        passed &= report(
            "Codex Desktop",
            desktop_installed,
            next((str(path) for path in desktop_bundles if path.exists()), "Install ChatGPT or Codex Desktop"),
        )
        running = False
        if sys.platform == "darwin":
            process_list = subprocess.run(
                ["ps", "-axo", "args="], text=True, capture_output=True, check=False
            ).stdout
            running = any(
                f"/Applications/{app}.app/Contents/MacOS/{app}" in process_list
                for app in ("ChatGPT", "Codex")
            )
        else:
            running = desktop_installed
        passed &= report("Desktop running", running, "ChatGPT/Codex process found" if running else "Open the desktop app")
        codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
        installed_skill = codex_home / "skills" / "collect-car-marketplaces" / "SKILL.md"
        passed &= report(
            "fallback skill",
            installed_skill.is_file(),
            str(installed_skill) if installed_skill.is_file() else "Run scripts/install_project_skills.sh",
        )
        chrome_app = Path("/Applications/Google Chrome.app")
        passed &= report(
            "Google Chrome",
            chrome_app.exists(),
            str(chrome_app) if chrome_app.exists() else "Install Google Chrome",
        )
        chrome_manifests = list(
            (codex_home / "plugins" / "cache" / "openai-bundled" / "chrome").glob(
                "*/.codex-plugin/plugin.json"
            )
        )
        passed &= report(
            "Chrome plugin",
            bool(chrome_manifests),
            str(chrome_manifests[0].parent.parent) if chrome_manifests else "Install Chrome from Codex Plugins",
        )
        extension_ok = False
        extension_detail = "Complete the Chrome plugin setup in Codex Desktop"
        if chrome_manifests and shutil.which("node"):
            extension_check = chrome_manifests[0].parent.parent / "scripts" / "check-extension-installed.js"
            if extension_check.is_file():
                checked = subprocess.run(
                    [shutil.which("node") or "node", str(extension_check)],
                    text=True,
                    capture_output=True,
                    timeout=10,
                    check=False,
                )
                extension_ok = checked.returncode == 0 and "Enabled in any profile: yes" in checked.stdout
                if extension_ok:
                    extension_detail = "installed and enabled in a Chrome profile"
                elif checked.stdout.strip():
                    extension_detail = checked.stdout.strip().splitlines()[-1]
        passed &= report("Chrome extension", extension_ok, extension_detail)
        host_status = host_chrome_status(chrome_host_script)
        passed &= report(
            "zero-click host Chrome",
            bool(host_status["ready"]),
            str(host_status["mode"] if host_status["ready"] else host_status["error"]),
        )
        host_probe_ok = False
        host_probe_detail = "Enable View > Developer > Allow JavaScript from Apple Events in Chrome"
        if host_status["ready"]:
            try:
                front_before = subprocess.run(
                    [shutil.which("osascript") or "osascript", "-e", "path to frontmost application as text"],
                    text=True,
                    capture_output=True,
                    timeout=10,
                    check=False,
                ).stdout.strip()
                checked = subprocess.run(
                    [
                        shutil.which("osascript") or "osascript",
                        str(chrome_host_script),
                        "https://example.com/",
                        "2000",
                        "0",
                        "1",
                    ],
                    text=True,
                    capture_output=True,
                    timeout=60,
                    check=False,
                )
                capture = json.loads(checked.stdout) if checked.returncode == 0 else {}
                front_after = subprocess.run(
                    [shutil.which("osascript") or "osascript", "-e", "path to frontmost application as text"],
                    text=True,
                    capture_output=True,
                    timeout=10,
                    check=False,
                ).stdout.strip()
                host_probe_ok = bool(
                    capture.get("readyState") == "complete"
                    and capture.get("text")
                    and capture.get("backgroundMode") is True
                    and front_before
                    and front_before == front_after
                )
                if host_probe_ok:
                    host_probe_detail = "minimized capture succeeded and preserved the foreground app"
                elif (checked.stderr or checked.stdout).strip():
                    host_probe_detail = (checked.stderr or checked.stdout).strip()[-500:]
            except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
                host_probe_detail = str(exc)
        passed &= report("host Chrome capture", host_probe_ok, host_probe_detail)

    if args.smoke_browser and passed:
        probe_env = os.environ.copy()
        try:
            completed = subprocess.run(
                [shutil.which("node") or "node", str(browser_server), "--probe-browser"],
                env=probe_env,
                text=True,
                capture_output=True,
                timeout=45,
                check=False,
            )
            probe = json.loads(completed.stdout) if completed.returncode == 0 else {}
            mode = str(probe.get("mode") or "")
            background_required = os.environ.get("CAR_COMPARE_BACKGROUND_MODE", "1").strip().lower() not in {
                "0", "false", "no", "off"
            }
            probe_ok = (
                completed.returncode == 0
                and mode.startswith(("persistent_profile", "persistent_cdp"))
                and (not background_required or probe.get("background_mode") is True)
            )
            probe_detail = (
                f"{mode} with {probe.get('contexts', 0)} context(s), background={bool(probe.get('background_mode'))}"
                if probe_ok
                else (completed.stderr or completed.stdout or "Playwright could not launch").strip()[-500:]
            )
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            probe_ok = False
            probe_detail = str(exc)
        passed = report("browser runtime", probe_ok, probe_detail) and passed

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
