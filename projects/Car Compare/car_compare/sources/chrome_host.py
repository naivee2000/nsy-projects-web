from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SOURCE_HOSTS = {
    "autotrader_browser": "autotrader.com",
    "edmunds_browser": "edmunds.com",
    "porsche_finder_browser": "finder.porsche.com",
}
ACCESS_WALL_RE = re.compile(
    r"page unavailable|access denied|verify you are human|security verification|captcha|"
    r"unusual activity|network restrictions|do not have permission",
    re.I,
)


def background_mode_enabled() -> bool:
    return os.environ.get("CAR_COMPARE_BACKGROUND_MODE", "1").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }


def host_chrome_status(script_path: Path) -> dict[str, Any]:
    background = background_mode_enabled()
    if os.environ.get("CAR_COMPARE_HOST_CHROME_FALLBACK", "1").strip().lower() in {
        "0",
        "false",
        "no",
        "off",
    }:
        return {"ready": False, "mode": "disabled", "error": "Disabled by environment.", "background": background}
    if platform.system() != "Darwin":
        return {"ready": False, "mode": "unsupported-platform", "error": "Requires macOS.", "background": background}
    if not shutil.which("osascript"):
        return {"ready": False, "mode": "missing-osascript", "error": "osascript was not found.", "background": background}
    if not Path("/Applications/Google Chrome.app").exists():
        return {"ready": False, "mode": "missing-chrome", "error": "Google Chrome was not found.", "background": background}
    if not script_path.exists():
        return {"ready": False, "mode": "missing-script", "error": f"Missing {script_path.name}.", "background": background}
    return {"ready": True, "mode": "system_chrome_applescript", "error": "", "background": background}


def capture_with_host_chrome(
    *,
    source: str,
    url: str,
    script_path: Path,
    max_characters: int = 250_000,
    max_clicks: int = 3,
    timeout_seconds: int = 180,
    background_mode: bool | None = None,
) -> dict[str, Any]:
    expected_host = SOURCE_HOSTS.get(source)
    if not expected_host:
        raise ValueError("Unsupported host Chrome source")
    _validate_source_url(url, expected_host)
    status = host_chrome_status(script_path)
    if not status["ready"]:
        raise RuntimeError(str(status["error"] or status["mode"]))

    use_background = background_mode_enabled() if background_mode is None else bool(background_mode)
    completed = subprocess.run(
        [
            shutil.which("osascript") or "osascript",
            str(script_path),
            url,
            str(max(1_000, min(250_000, int(max_characters)))),
            str(max(0, min(10, int(max_clicks)))),
            "1" if use_background else "0",
        ],
        text=True,
        capture_output=True,
        timeout=max(30, min(600, int(timeout_seconds))),
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or "Host Chrome capture failed").strip()[:1000])
    try:
        capture = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Host Chrome returned invalid JSON: {exc}") from exc
    if not isinstance(capture, dict):
        raise RuntimeError("Host Chrome returned an invalid capture")

    final_url = str(capture.get("url") or url)
    _validate_source_url(final_url, expected_host)
    for page in capture.get("pages") or []:
        if isinstance(page, dict) and page.get("url"):
            _validate_source_url(str(page["url"]), expected_host)
    capture["source"] = source
    capture["requestedUrl"] = url
    capture["browserMode"] = status["mode"]
    capture["backgroundMode"] = bool(capture.get("backgroundMode", use_background))
    return capture


def capture_is_access_wall(capture: dict[str, Any]) -> bool:
    lead = f"{capture.get('title') or ''} {(capture.get('text') or '')[:2000]}"
    return bool(ACCESS_WALL_RE.search(lead))


def capture_access_message(capture: dict[str, Any]) -> str:
    text = re.sub(r"\s+", " ", str(capture.get("text") or "")).strip()
    title = str(capture.get("title") or "").strip()
    return f"{title}: {text}".strip(": ")[:1000]


def _validate_source_url(url: str, expected_host: str) -> None:
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not (
        hostname == expected_host or hostname.endswith(f".{expected_host}")
    ):
        raise ValueError(f"Host Chrome URL must use {expected_host}")
