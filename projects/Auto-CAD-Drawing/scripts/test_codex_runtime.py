#!/usr/bin/env python3
"""Regression checks for portable Codex discovery and auth readiness."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from codex_advisory import SCHEMA_PATH, advisory_status
from codex_runtime import codex_environment, codex_login_status, resolve_codex_bin


def main() -> int:
    previous_bin = os.environ.get("CODEX_BIN")
    previous_home = os.environ.get("CODEX_HOME")
    previous_advisory = os.environ.get("AUTO_CAD_CODEX_ADVISORY")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake = root / ("codex.cmd" if os.name == "nt" else "codex")
            if os.name == "nt":
                fake.write_text("@echo Logged in using ChatGPT\r\n", encoding="utf-8")
            else:
                fake.write_text("#!/bin/sh\necho 'Logged in using ChatGPT'\n", encoding="utf-8")
                os.chmod(fake, 0o755)
            os.environ["CODEX_BIN"] = str(fake)
            os.environ["CODEX_HOME"] = str(root / "state")
            os.environ["AUTO_CAD_CODEX_ADVISORY"] = "1"

            assert resolve_codex_bin() == str(fake.resolve())
            assert codex_environment()["CODEX_HOME"] == str((root / "state").resolve())
            status = codex_login_status()
            assert status["available"] and status["authenticated"], status
            assert status["auth_method"] == "chatgpt", status
            advisory = advisory_status()
            assert advisory["enabled"] and advisory["ready"], advisory

        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        assert set(schema["required"]) == set(schema["properties"])
    finally:
        if previous_bin is None:
            os.environ.pop("CODEX_BIN", None)
        else:
            os.environ["CODEX_BIN"] = previous_bin
        if previous_home is None:
            os.environ.pop("CODEX_HOME", None)
        else:
            os.environ["CODEX_HOME"] = previous_home
        if previous_advisory is None:
            os.environ.pop("AUTO_CAD_CODEX_ADVISORY", None)
        else:
            os.environ["AUTO_CAD_CODEX_ADVISORY"] = previous_advisory

    print("OK: portable Codex runtime")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
