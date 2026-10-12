from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


# The desktop app bundles the same CLI under ChatGPT.app on current macOS installs.
MACOS_CODEX_CLI_PATHS = (
    Path("/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"),
    Path("/Applications/Codex.app/Contents/Resources/codex-cli/bin/codex"),
    Path.home() / "Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex",
    Path.home() / "Applications/Codex.app/Contents/Resources/codex-cli/bin/codex",
    Path("/Applications/ChatGPT.app/Contents/Resources/codex"),
    Path("/Applications/Codex.app/Contents/Resources/codex"),
    Path.home() / "Applications/ChatGPT.app/Contents/Resources/codex",
    Path.home() / "Applications/Codex.app/Contents/Resources/codex",
)
CODEX_REASONING_EFFORTS = frozenset({"none", "low", "medium", "high", "xhigh", "max"})


def normalize_codex_reasoning_effort(value: str, default: str) -> str:
    """Return a supported Codex reasoning effort with a safe workload default."""
    normalized_default = str(default or "").strip().lower()
    if normalized_default not in CODEX_REASONING_EFFORTS:
        raise ValueError(f"Unsupported default Codex reasoning effort: {default}")
    normalized = str(value or "").strip().lower()
    return normalized if normalized in CODEX_REASONING_EFFORTS else normalized_default


def codex_reasoning_config_args(value: str, default: str) -> list[str]:
    """Build an invocation-local override that survives ``--ignore-user-config``."""
    effort = normalize_codex_reasoning_effort(value, default)
    return ["--config", f'model_reasoning_effort="{effort}"']


def codex_home() -> Path:
    """Return the state folder used by the account running this backend."""
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser().resolve()


def _executable_path(candidate: str | Path | None) -> str:
    if not candidate:
        return ""
    value = os.path.expandvars(str(candidate).strip())
    if not value:
        return ""
    path = Path(value).expanduser()
    if path.is_file() and os.access(path, os.X_OK):
        return str(path.resolve())
    return shutil.which(value) or ""


def _standalone_codex_paths() -> tuple[Path, ...]:
    executable = "codex.exe" if os.name == "nt" else "codex"
    paths = [Path.home() / ".local" / "bin" / executable]
    install_dir = os.environ.get("CODEX_INSTALL_DIR", "").strip()
    if install_dir:
        paths.append(Path(install_dir).expanduser() / executable)
    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app_data:
        paths.append(Path(local_app_data) / "Programs" / "OpenAI" / "Codex" / "bin" / "codex.exe")
    if sys.platform != "win32":
        paths.extend((Path("/usr/local/bin/codex"), Path("/opt/homebrew/bin/codex")))
    return tuple(paths)


def find_codex_cli(configured_path: str = "") -> str:
    """Return an executable Codex CLI path available to this app process."""
    explicit_path = configured_path.strip() or os.environ.get("CODEX_BIN", "").strip()
    if explicit_path:
        return _executable_path(explicit_path)

    for candidate in (*MACOS_CODEX_CLI_PATHS, shutil.which("codex"), *_standalone_codex_paths()):
        path = _executable_path(candidate)
        if path:
            return path
    return ""


def codex_environment() -> dict[str, str]:
    """Build the environment for a server-side ``codex exec`` child."""
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home())
    env.setdefault("TERM", "xterm-256color")
    return env


def codex_login_status(configured_path: str = "", timeout: int = 15) -> dict[str, Any]:
    """Check CLI authentication without assuming credentials live in auth.json.

    Codex may store credentials in the operating-system keyring. The supported
    ``codex login status`` command is therefore a more portable readiness check
    than inspecting one file under CODEX_HOME.
    """
    path = find_codex_cli(configured_path)
    result: dict[str, Any] = {
        "available": bool(path),
        "authenticated": False,
        "codexPath": path,
        "codexHome": str(codex_home()),
        "authMethod": "",
        "message": "Codex CLI not found. Install Codex or set CODEX_BIN.",
    }
    if not path:
        return result
    try:
        completed = subprocess.run(
            [path, "login", "status"],
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
        method = "chatgpt"
    elif "api key" in lower or "api-key" in lower:
        method = "api-key"
    elif "access token" in lower:
        method = "access-token"
    else:
        method = "saved-login" if authenticated else ""
    result.update(
        {
            "authenticated": authenticated,
            "authMethod": method,
            "message": output[-400:] if output else ("Codex login is ready." if authenticated else "Codex is not logged in."),
        }
    )
    return result
