from __future__ import annotations

import json
import math
import os
import platform
import re
import shutil
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from car_compare.sources.request_budget import run_bounded


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
    deadline_at: float | None = None,
    max_pages: int | None = None,
    requested_scope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return raw evidence, never a verified scope. Callers must validate every page.

    max_pages is the remaining page budget, inclusive of the initial page.
    deadline_at is an absolute UNIX timestamp shared with the collection job.
    """
    deadline = time.time() + max(0, min(600, float(timeout_seconds)))
    if deadline_at is not None:
        if not math.isfinite(float(deadline_at)):
            raise ValueError("deadline_at must be finite UNIX seconds")
        deadline = min(deadline, float(deadline_at))

    def remaining() -> float:
        seconds = deadline - time.time()
        if seconds <= 0:
            raise TimeoutError("deadline_exceeded")
        return seconds

    remaining()
    page_limit = min(20, int(max_pages)) if max_pages is not None else max(0, min(10, int(max_clicks))) + 1
    if page_limit <= 0:
        raise ValueError("max_pages remaining budget is exhausted")
    expected_host = SOURCE_HOSTS.get(source)
    if not expected_host:
        raise ValueError("Unsupported host Chrome source")
    _validate_source_url(url, expected_host)
    status = host_chrome_status(script_path)
    if not status["ready"]:
        raise RuntimeError(str(status["error"] or status["mode"]))

    use_background = background_mode_enabled() if background_mode is None else bool(background_mode)
    # Share the exact DOM evidence reader with the worker; no browser is launched.
    reader = run_bounded(
        [shutil.which("node") or "node", str(script_path.with_name("car_compare_browser_mcp.mjs")), "--scope-dom-script"],
        text=True, capture_output=True, deadline_at=deadline, timeout=remaining(), check=False,
    )
    if reader.returncode or not reader.stdout.strip():
        raise RuntimeError("Unable to load the host Chrome scope evidence reader")
    completed = run_bounded(
        [
            shutil.which("osascript") or "osascript",
            str(script_path),
            url,
            str(max(1_000, min(250_000, int(max_characters)))),
            str(min(max(0, min(10, int(max_clicks))), page_limit - 1)),
            "1" if use_background else "0",
            str(deadline),
            str(page_limit),
            reader.stdout.strip(),
        ],
        text=True,
        capture_output=True,
        timeout=remaining(),
        deadline_at=deadline,
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
    valid_cards = []
    for card in capture.get("cards") or []:
        if not isinstance(card, dict):
            continue
        card_url = str(card.get("url") or "")
        card_text = str(card.get("text") or "")
        try:
            _validate_source_url(card_url, expected_host)
        except ValueError:
            continue
        if card_text.strip():
            valid_cards.append({"url": card_url, "text": card_text})
    capture["cards"] = valid_cards
    capture["source"] = source
    capture["requestedUrl"] = url
    capture["browserMode"] = status["mode"]
    capture["backgroundMode"] = bool(capture.get("backgroundMode", use_background))
    capture["requested_scope"] = requested_scope
    capture["deadline_at"] = deadline
    capture["max_pages"] = page_limit
    capture["validation_revision"] = 3
    capture["validation_status"] = "unverified"
    capture["requires_independent_scope_validation"] = True
    return capture


def capture_is_access_wall(capture: dict[str, Any]) -> bool:
    lead = f"{capture.get('title') or ''} {(capture.get('text') or '')[:2000]}"
    return bool(ACCESS_WALL_RE.search(lead))


def validate_host_scope(capture: dict[str, Any], requested_scope: dict[str, Any]) -> dict[str, Any]:
    """Independently validate raw selected controls and refresh evidence on every page.

    Returns scope, evidence, status. The caller attaches its own query_key only
    after checking scope.validation_status == 'verified'. No marketplace access.
    """
    worker = Path(__file__).resolve().parents[2] / "scripts" / "car_compare_browser_mcp.mjs"
    remaining = min(10.0, float(capture.get("deadline_at") or time.time() + 10) - time.time())
    if remaining <= 0:
        return {"status": "loading", "scope": {"validation_revision": 3, "validation_status": "unverified", "geography": "unknown", "complete": False}, "evidence": {"reason": "deadline_exceeded", "result_refresh_confirmed": False}}
    completed = run_bounded(
        [shutil.which("node") or "node", str(worker), "--validate-host-scope-json"],
        input=json.dumps({"capture": capture, "requested_scope": requested_scope}),
        text=True, capture_output=True, deadline_at=capture.get("deadline_at"), timeout=remaining, check=False,
    )
    if completed.returncode:
        raise RuntimeError("Host Chrome scope validation failed")
    result = json.loads(completed.stdout)
    if not isinstance(result, dict) or not isinstance(result.get("scope"), dict):
        raise RuntimeError("Host Chrome scope validation returned invalid evidence")
    return result


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
