from __future__ import annotations

import json
import subprocess
from unittest.mock import patch
from pathlib import Path

from code_practice.codex_coach import codex_status, request_codex_coaching, resolve_codex_cli
from code_practice.content import PROBLEMS


PROBLEM = next(problem for problem in PROBLEMS if problem.id == "pair-sum-indices")
CASES = [
    {"id": "case-1", "visible": True, "passed": False, "arguments": [[3, 2, 4], 6], "expected": [1, 2], "actual": []},
    {"id": "case-2", "visible": False, "passed": False, "arguments": [[1, 8, 2, 7], 9], "expected": [0, 1], "actual": []},
]


def fake_runner_with(payload: dict[str, str], captured: dict[str, object]):
    def run(command, **kwargs):
        captured["command"] = command
        captured["prompt"] = kwargs["input"]
        output_path = Path(command[command.index("--output-last-message") + 1])
        output_path.write_text(json.dumps(payload), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
    return run


def test_codex_coach_uses_ephemeral_read_only_structured_run_with_test_evidence():
    captured: dict[str, object] = {}
    response = request_codex_coaching(
        PROBLEM,
        "def pair_sum_indices(nums, target):\n    return []",
        "wrong_answer",
        "A test produced an unexpected result.",
        CASES,
        runner=fake_runner_with(
            {
                "title": "Check the loop boundary",
                "explanation": "The final candidate is not considered by the current loop boundary.",
                "nudge": "Trace the highest index reached by each loop.",
                "question": "Can either loop ever visit the final list position?",
            },
            captured,
        ),
        executable="/fake/codex",
    )
    assert response["source"] == "codex-cli"
    assert response["fallbackReason"] is None
    command = captured["command"]
    assert "--ephemeral" in command
    assert command[command.index("--sandbox") + 1] == "read-only"
    assert "--output-schema" in command
    prompt = str(captured["prompt"])
    assert "[[1, 8, 2, 7], 9]" in prompt
    assert "seen[partner]" not in prompt
    assert "Never provide a complete solution" in prompt


def test_codex_coach_withholds_answer_like_output_and_falls_back_offline():
    response = request_codex_coaching(
        PROBLEM,
        "def pair_sum_indices(nums, target):\n    return []",
        "wrong_answer",
        "wrong",
        CASES,
        runner=fake_runner_with(
            {
                "title": "Complete solution",
                "explanation": "Here is the code:\n```python\ndef pair_sum_indices(nums, target): return [0, 1]\n```",
                "nudge": "Copy and paste it.",
                "question": "Done?",
            },
            {},
        ),
        executable="/fake/codex",
    )
    assert response["source"] == "offline-static-coach"
    assert "withheld" in response["fallbackReason"]
    assert "def pair_sum_indices" not in str(response)


def test_codex_coach_unavailable_keeps_offline_feedback(monkeypatch):
    monkeypatch.setattr("code_practice.codex_coach.shutil.which", lambda _name: None)
    response = request_codex_coaching(PROBLEM, "pass", "syntax_error", "invalid syntax", [], executable=None)
    assert response["source"] == "offline-static-coach"
    assert "not installed" in response["fallbackReason"]


def test_configured_cli_is_used_by_status_and_generation(monkeypatch):
    monkeypatch.setenv("CODEX_BIN", "/custom/codex")
    monkeypatch.setattr("code_practice.codex_coach.shutil.which", lambda name: "/custom/codex" if name == "/custom/codex" else "/old/codex")
    assert resolve_codex_cli() == "/custom/codex"
    with patch("code_practice.codex_coach.subprocess.run", return_value=subprocess.CompletedProcess([], 0)) as run:
        assert codex_status()["authenticated"]
        assert run.call_args.args[0][0] == "/custom/codex"
    captured = {}
    request_codex_coaching(PROBLEM, "pass", "wrong_answer", "wrong", [], runner=fake_runner_with(
        {"title": "Trace", "explanation": "No result is returned.", "nudge": "Inspect the return value.", "question": "What does pass return?"}, captured))
    assert captured["command"][0] == "/custom/codex"


def test_stale_configured_cli_recovers_to_current_bundle_before_path(monkeypatch):
    bundle = "/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"
    monkeypatch.setenv("CODEX_BIN", "/missing/old/codex")
    monkeypatch.setattr("code_practice.codex_coach.shutil.which", lambda name: bundle if name == bundle else "/old/codex" if name == "codex" else None)
    assert resolve_codex_cli() == bundle
