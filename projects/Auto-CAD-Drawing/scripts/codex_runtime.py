#!/usr/bin/env python3
"""Portable Codex CLI discovery and authentication checks for this app."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser().resolve()


def executable_path(candidate: str | Path | None) -> str:
    if not candidate:
        return ""
    value = os.path.expandvars(str(candidate).strip())
    if not value:
        return ""
    path = Path(value).expanduser()
    if path.is_file() and os.access(path, os.X_OK):
        return str(path.resolve())
    return shutil.which(value) or ""


def candidate_paths() -> tuple[str | Path | None, ...]:
    executable = "codex.exe" if os.name == "nt" else "codex"
    install_dir = os.environ.get("CODEX_INSTALL_DIR", "").strip()
    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    common: list[str | Path | None] = [
        os.environ.get("CODEX_BIN", "").strip(),
        shutil.which("codex"),
        Path(install_dir).expanduser() / executable if install_dir else None,
        Path.home() / ".local" / "bin" / executable,
        Path(local_app_data) / "Programs" / "OpenAI" / "Codex" / "bin" / "codex.exe" if local_app_data else None,
        "/Applications/ChatGPT.app/Contents/Resources/codex",
        "/Applications/Codex.app/Contents/Resources/codex",
        Path.home() / "Applications/ChatGPT.app/Contents/Resources/codex",
        Path.home() / "Applications/Codex.app/Contents/Resources/codex",
    ]
    if sys.platform != "win32":
        common.extend(("/usr/local/bin/codex", "/opt/homebrew/bin/codex"))
    return tuple(common)


def resolve_codex_bin() -> str:
    configured = os.environ.get("CODEX_BIN", "").strip()
    if configured:
        return executable_path(configured) or configured
    for candidate in candidate_paths():
        path = executable_path(candidate)
        if path:
            return path
    return "codex"


def codex_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home())
    env.setdefault("TERM", "xterm-256color")
    return env


def codex_login_status(timeout: int = 15) -> dict[str, Any]:
    codex_bin = resolve_codex_bin()
    available = bool(executable_path(codex_bin))
    result: dict[str, Any] = {
        "available": available,
        "authenticated": False,
        "codex_bin": codex_bin,
        "codex_home": str(codex_home()),
        "auth_method": "",
        "message": "Codex CLI not found. Install Codex or set CODEX_BIN.",
    }
    if not available:
        return result
    try:
        completed = subprocess.run(
            [codex_bin, "login", "status"],
            env=codex_environment(),
            stdin=subprocess.DEVNULL,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        result["message"] = f"Codex login check failed: {exc}"
        return result

    output = " ".join((completed.stdout, completed.stderr)).strip()
    lower = output.lower()
    authenticated = completed.returncode == 0 and "not logged in" not in lower and "not authenticated" not in lower
    if "chatgpt" in lower:
        auth_method = "chatgpt"
    elif "api key" in lower or "api-key" in lower:
        auth_method = "api-key"
    elif "access token" in lower:
        auth_method = "access-token"
    else:
        auth_method = "saved-login" if authenticated else ""
    result.update(
        {
            "authenticated": authenticated,
            "auth_method": auth_method,
            "message": output[-400:] if output else ("Codex login is ready." if authenticated else "Codex is not logged in."),
        }
    )
    return result
