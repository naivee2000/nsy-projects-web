from __future__ import annotations

import json
import os
from typing import Any, Mapping
from urllib.parse import urlparse
from urllib.request import ProxyHandler, build_opener


DEFAULT_BROWSER_DEBUG_PORT = 9222
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def browser_cdp_url(environ: Mapping[str, str] | None = None) -> tuple[str, bool]:
    env = os.environ if environ is None else environ
    configured = str(env.get("CAR_COMPARE_BROWSER_CDP_URL") or "").strip().rstrip("/")
    if configured:
        return configured, True
    raw_port = str(env.get("CAR_COMPARE_BROWSER_DEBUG_PORT") or DEFAULT_BROWSER_DEBUG_PORT).strip()
    try:
        port = int(raw_port)
    except ValueError:
        port = DEFAULT_BROWSER_DEBUG_PORT
    if not 1 <= port <= 65535:
        port = DEFAULT_BROWSER_DEBUG_PORT
    return f"http://127.0.0.1:{port}", False


def browser_cdp_status(
    environ: Mapping[str, str] | None = None,
    *,
    timeout: float = 0.75,
) -> dict[str, Any]:
    url, explicitly_configured = browser_cdp_url(environ)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in LOOPBACK_HOSTS:
        return {
            "url": url,
            "configured": explicitly_configured,
            "ready": False,
            "mode": "invalid",
            "browser": "",
            "error": "The collection browser endpoint must use localhost.",
        }
    try:
        opener = build_opener(ProxyHandler({}))
        with opener.open(f"{url}/json/version", timeout=timeout) as response:
            info = json.loads(response.read().decode("utf-8"))
        browser = str(info.get("Browser") or "").strip()
        ready = bool(browser and info.get("webSocketDebuggerUrl"))
        error = "" if ready else "The endpoint did not report a debuggable browser."
    except Exception as exc:
        browser = ""
        ready = False
        error = str(exc)
    return {
        "url": url,
        "configured": explicitly_configured,
        "ready": ready,
        "mode": "configured" if explicitly_configured else ("auto-detected" if ready else "unavailable"),
        "browser": browser,
        "error": error,
    }
