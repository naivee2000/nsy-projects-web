import subprocess
import unittest
from unittest.mock import patch

import app


class CodexRuntimeTests(unittest.TestCase):
    def test_stale_bundle_recovers_before_path_cli(self):
        bundle = app.CODEX_APP_BIN_CANDIDATES[0]
        with (
            patch.object(app, "CODEX_CONFIGURED_BIN", "/missing/codex"),
            patch.object(app.Path, "is_file", lambda path: str(path) == bundle),
            patch.object(app.os, "access", return_value=True),
            patch.object(app.shutil, "which", side_effect=lambda value: "/old/codex" if value == "codex" else None),
        ):
            self.assertEqual(app.resolve_codex_bin(), bundle)

    def test_login_failure_is_not_reported_as_ready(self):
        with patch.object(app.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)) as run:
            self.assertFalse(app.codex_auth_ok())
            self.assertEqual(run.call_args.args[0], [app.CODEX_BIN, "login", "status"])

    def test_login_timeout_is_not_reported_as_ready(self):
        with patch.object(app.subprocess, "run", side_effect=subprocess.TimeoutExpired("codex", 10)):
            self.assertFalse(app.codex_auth_ok())


if __name__ == "__main__":
    unittest.main()
