from __future__ import annotations

import json
import subprocess
from pathlib import Path

from code_practice.codex_coach import request_codex_coaching
from code_practice.content import PROBLEMS


PROBLEM = next(problem for problem in PROBLEMS if problem.id == "pair-sum-indices")
CASES = [
    {"id": "visible", "visible": True, "passed": False, "arguments": [[3, 2, 4], 6], "expected": [1, 2], "actual": []},
    {"id": "hidden", "visible": False, "passed": False, "expected": "SECRET-HIDDEN-OUTPUT", "actual": []},
]


def fake_runner_with(payload: dict[str, str], captured: dict[str, object]):
    def run(command, **kwargs):
        captured["command"] = command
        captured["prompt"] = kwargs["input"]
        output_path = Path(command[command.index("--output-last-message") + 1])
        output_path.write_text(json.dumps(payload), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
    return run


def test_codex_coach_uses_ephemeral_read_only_structured_run_without_hidden_answers():
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
    assert "SECRET-HIDDEN-OUTPUT" not in prompt
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
