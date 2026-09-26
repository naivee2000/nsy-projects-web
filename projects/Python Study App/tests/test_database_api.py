from datetime import datetime, timezone

from fastapi.testclient import TestClient

from code_practice import database
from code_practice.app import app
from code_practice.catalog import get_catalog, refresh_catalog
from code_practice.database import (
    connect,
    get_draft,
    list_attempts,
    save_attempt,
    save_daily_assignment,
    save_variant,
)
from code_practice.schemas import AttemptCreate


def test_health_problem_detail_separates_examples_from_hidden_tests():
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["mode"] == "local-only"
        assert health.json()["problemCount"] == len(get_catalog())

        listing = client.get("/api/problems").json()
        assert listing["total"] == len(get_catalog())
        assert len(listing["items"]) == 30
        detail = client.get("/api/problems/pair-sum-indices").json()
        assert len(detail["tests"]) == 2
        assert all(test["visible"] and test["arguments"] is not None for test in detail["tests"])
        assert "reference_solution" not in detail
        package = client.post("/api/problems/pair-sum-indices/submission-package").json()
        assert len(package["tests"]) == 12
        assert all(not test["visible"] and test["arguments"] is not None for test in package["tests"])

        linked_detail = client.get("/api/problems/merge-sorted-linked-lists").json()
        assert [parameter["adapter"] for parameter in linked_detail["signature"]["parameters"]] == ["listnode", "listnode"]
        assert linked_detail["signature"]["return_adapter"] == "listnode"
        assert len(linked_detail["tests"]) == 2
        linked_package = client.post("/api/problems/merge-sorted-linked-lists/submission-package").json()
        assert len(linked_package["tests"]) == 12


def test_existing_node_draft_receives_the_visible_support_class():
    database.save_draft("reverse-linked-list", "def reverse_linked_list(head):\n    return head\n")
    with TestClient(app) as client:
        detail = client.get("/api/problems/reverse-linked-list").json()
    assert detail["savedDraft"].startswith("# Data structure supplied to this problem.\nclass ListNode:")
    assert detail["savedDraft"].count("class ListNode:") == 1
    assert "def reverse_linked_list(head):" in detail["savedDraft"]


def test_schema_migration_is_versioned_and_idempotent():
    from code_practice.database import initialize_database
    initialize_database()
    initialize_database()
    with connect() as connection:
        versions = connection.execute("SELECT version FROM schema_migrations").fetchall()
    assert [row["version"] for row in versions] == [1, 2, 3]


def test_progress_seed_installs_once_and_never_overwrites_runtime(tmp_path, monkeypatch):
    seed_dir = tmp_path / "seed"
    seed_db = seed_dir / "initial_progress.db"
    monkeypatch.setattr(database, "DATA_DIR", seed_dir)
    monkeypatch.setattr(database, "DB_PATH", seed_db)
    monkeypatch.setattr(database, "SEED_DB_PATH", None)
    database.initialize_database()
    database.save_draft("pair-sum-indices", "seed draft")

    runtime_dir = tmp_path / "persistent-runtime"
    runtime_db = runtime_dir / "code_practice.db"
    monkeypatch.setattr(database, "DATA_DIR", runtime_dir)
    monkeypatch.setattr(database, "DB_PATH", runtime_db)
    monkeypatch.setattr(database, "SEED_DB_PATH", seed_db)

    assert database.install_seed_database() is True
    assert database.get_draft("pair-sum-indices") == "seed draft"
    database.save_draft("pair-sum-indices", "online progress")

    assert database.install_seed_database() is False
    database.initialize_database()
    assert database.get_draft("pair-sum-indices") == "online progress"


def test_draft_attempt_hint_and_progress_persist():
    with TestClient(app) as client:
        response = client.put(
            "/api/problems/pair-sum-indices/draft",
            json={"source_code": "def pair_sum_indices(nums, target):\n    return [0, 1]"},
        )
        assert response.status_code == 200
        assert get_draft("pair-sum-indices").startswith("def pair_sum_indices")

        assert client.post("/api/problems/pair-sum-indices/hints/2").status_code == 409
        assert client.post("/api/problems/pair-sum-indices/hints/1").status_code == 200
        assert client.post("/api/problems/pair-sum-indices/hints/2").status_code == 200

        attempt = {
            "problem_id": "pair-sum-indices",
            "problem_version": 1,
            "source_code": "def pair_sum_indices(nums, target): return [0, 1]",
            "result": "accepted",
            "runtime_ms": 2.5,
            "tests_passed": 12,
            "tests_total": 12,
            "elapsed_study_seconds": 30,
            "hint_level": 2,
        }
        assert client.post("/api/attempts", json=attempt).status_code == 200
        assert len(list_attempts()) == 1
        detail = client.get("/api/problems/pair-sum-indices").json()
        assert detail["solved"] is True
        listing = client.get("/api/problems?search=Pair%20Sum%20Indices").json()["items"]
        assert next(item for item in listing if item["id"] == "pair-sum-indices")["solved"] is True
        progress = client.get("/api/progress").json()
        assert progress["solvedCount"] == 1
        assert progress["mastery"]["arrays"] == 60.0


def test_unpassed_challenge_does_not_create_attempt_or_review_progress():
    problem = next(problem for problem in get_catalog().values() if problem.difficulty >= 8)
    submission = {
        "problem_id": problem.id,
        "problem_version": problem.version,
        "source_code": problem.starter_code,
        "result": "wrong_answer",
        "runtime_ms": 2.5,
        "tests_passed": 3,
        "tests_total": 12,
        "elapsed_study_seconds": 120,
        "hint_level": 0,
        "entry_point": "challenge",
    }
    with TestClient(app) as client:
        response = client.post("/api/attempts", json=submission)
        assert response.status_code == 200
        assert response.json() == {
            "recorded": False,
            "reason": "Unpassed challenge attempts do not affect progress.",
        }
        assert database.list_attempts() == []
        assert database.list_review_states() == []
        assert client.get("/api/dashboard").json()["attemptCount"] == 0

        passed = {**submission, "result": "accepted", "source_code": problem.reference_solution,
                  "tests_passed": 12}
        accepted = client.post("/api/attempts", json=passed)
        assert accepted.status_code == 200
        assert accepted.json()["recorded"] is True
        assert len(database.list_attempts()) == 1
        assert database.list_review_states()[0].latest_result == "accepted"
        assert client.get(f"/api/problems/{problem.id}").json()["solved"] is True


def test_failed_daily_submission_is_still_recorded_for_future_retry():
    problem = get_catalog()["pair-sum-indices"]
    payload = {
        "problem_id": problem.id,
        "problem_version": problem.version,
        "source_code": problem.starter_code,
        "result": "wrong_answer",
        "runtime_ms": 1,
        "tests_passed": 0,
        "tests_total": 12,
        "entry_point": "daily",
    }
    with TestClient(app) as client:
        response = client.post("/api/attempts", json=payload)
    assert response.status_code == 200
    assert response.json()["recorded"] is True
    assert len(database.list_attempts()) == 1
    assert database.list_review_states()[0].latest_result == "wrong_answer"


def test_rejected_variant_never_appears_in_library():
    from code_practice.content import PROBLEMS
    variant = PROBLEMS[0].model_copy(deep=True)
    variant.id = "rejected-private-draft"
    variant.title = "Rejected private draft"
    variant.status = "draft"
    variant.seed_problem_id = PROBLEMS[0].id
    variant.variation_dimensions = ["operation", "constraints"]
    save_variant(variant.model_dump(mode="json"), PROBLEMS[0].id, status="rejected", validation={"valid": False})
    refresh_catalog()
    with TestClient(app) as client:
        ids = {item["id"] for item in client.get("/api/problems?search=Rejected").json()["items"]}
        assert variant.id not in ids
        assert client.get(f"/api/problems/{variant.id}").status_code == 404


def test_dashboard_adapts_daily_count_and_separates_completed_reviews():
    with TestClient(app) as client:
        accepted = {
            "problem_id": "pair-sum-indices",
            "problem_version": 1,
            "source_code": "def pair_sum_indices(nums, target): return [0, 1]",
            "result": "accepted",
            "runtime_ms": 2.5,
            "tests_passed": 12,
            "tests_total": 12,
            "elapsed_study_seconds": 30,
            "hint_level": 0,
        }
        assert client.post("/api/attempts", json=accepted).status_code == 200
        payload = client.get("/api/dashboard").json()
        assert len(payload["recommendations"]) == 5
        assert payload["dailyAssignedCount"] == 5
        assert payload["dailyComplete"] is False
        assert "pair-sum-indices" not in {problem["id"] for problem in payload["recommendations"]}
        assert all(not problem["solved"] for problem in payload["recommendations"])
        assert [problem["id"] for problem in payload["reviewRecommendations"]] == ["pair-sum-indices"]
        assert all(problem["solved"] for problem in payload["reviewRecommendations"])
        assert payload["reviewComplete"] is False
        assert payload["weeklyChallenge"] is None or not payload["weeklyChallenge"]["solved"]

        assert client.post("/api/attempts", json=accepted).status_code == 200
        reviewed = client.get("/api/dashboard").json()
        assert reviewed["reviewRecommendations"] == []
        assert reviewed["reviewComplete"] is True
        assert reviewed["reviewRemainingCount"] == 0

        for recommendation in payload["recommendations"]:
            problem = get_catalog()[recommendation["id"]]
            completed = {**accepted, "problem_id": problem.id, "problem_version": problem.version, "source_code": problem.reference_solution}
            assert client.post("/api/attempts", json=completed).status_code == 200

        finished = client.get("/api/dashboard").json()
        assert finished["recommendations"] == []
        assert finished["dailyComplete"] is True
        assert finished["dailyRemainingCount"] == 0
        assert client.get("/api/dashboard").json()["recommendations"] == []
        assert client.get("/api/dashboard").json()["reviewRecommendations"] == []


def test_dashboard_removes_stored_unseen_medium_without_refilling():
    today_key = datetime.now().astimezone().date().isoformat()
    save_daily_assignment(today_key, ["leetcode-57", "leetcode-1450"])

    with TestClient(app) as client:
        initial = client.get("/api/dashboard").json()
        assert [problem["id"] for problem in initial["recommendations"]] == ["leetcode-1450"]
        assert initial["dailyAssignedCount"] == 1

        easy = get_catalog()["leetcode-1450"]
        response = client.post(
            "/api/attempts",
            json={
                "problem_id": easy.id,
                "problem_version": easy.version,
                "source_code": easy.reference_solution,
                "result": "accepted",
                "runtime_ms": 1,
                "tests_passed": 12,
                "tests_total": 12,
                "elapsed_study_seconds": 1,
                "hint_level": 0,
            },
        )
        assert response.status_code == 200
        finished = client.get("/api/dashboard").json()
        assert finished["recommendations"] == []
        assert finished["dailyComplete"] is True


def test_dashboard_caps_primary_at_three_mediums_and_reviews_at_five():
    for problem in get_catalog().values():
        if problem.difficulty <= 3:
            save_attempt(AttemptCreate(
                problem_id=problem.id,
                problem_version=problem.version,
                source_code=problem.reference_solution,
                result="accepted",
                runtime_ms=1,
                tests_passed=12,
                tests_total=12,
                elapsed_study_seconds=1,
                hint_level=0,
            ))

    with TestClient(app) as client:
        payload = client.get("/api/dashboard").json()
        assert len(payload["recommendations"]) == 3
        assert all(4 <= problem["difficulty"] <= 7 for problem in payload["recommendations"])
        assert all(not problem["solved"] for problem in payload["recommendations"])
        assert len(payload["reviewRecommendations"]) == 5
        assert all(problem["solved"] for problem in payload["reviewRecommendations"])


def test_dashboard_orders_daily_reviews_by_difficulty():
    catalog = get_catalog()
    reviewed = [catalog["pair-sum-indices"], catalog["merge-intervals"], catalog["minimum-window"]]
    for problem in reviewed:
        save_attempt(AttemptCreate(
            problem_id=problem.id,
            problem_version=problem.version,
            source_code=problem.reference_solution,
            result="accepted",
            runtime_ms=1,
            tests_passed=12,
            tests_total=12,
            elapsed_study_seconds=60,
            hint_level=0,
        ))

    with TestClient(app) as client:
        payload = client.get("/api/dashboard").json()
    assert [problem["id"] for problem in payload["reviewRecommendations"]] == [
        "minimum-window",
        "merge-intervals",
        "pair-sum-indices",
    ]


def test_dashboard_caps_primary_at_one_hard_when_no_medium_remains():
    for problem in get_catalog().values():
        if problem.difficulty <= 7:
            save_attempt(AttemptCreate(
                problem_id=problem.id,
                problem_version=problem.version,
                source_code=problem.reference_solution,
                result="accepted",
                runtime_ms=1,
                tests_passed=12,
                tests_total=12,
                elapsed_study_seconds=1,
                hint_level=0,
            ))

    with TestClient(app) as client:
        payload = client.get("/api/dashboard").json()
        assert len(payload["recommendations"]) == 1
        assert payload["recommendations"][0]["difficulty"] >= 8
        assert all(not problem["solved"] for problem in payload["recommendations"])


def test_wrong_answer_coach_is_progressive_and_never_returns_solution():
    source = """def pair_sum_indices(nums, target):
    result = []
    for i in range(len(nums) - 1):
        for j in range(i + 1, len(nums) - 1):
            if nums[i] + nums[j] == target:
                result.extend([i, j])
    return result
"""
    failed_case = {
        "id": "example-2",
        "passed": False,
        "actual": [],
        "expected": [1, 2],
        "visible": True,
        "arguments": [[3, 2, 4], 6],
    }
    with TestClient(app) as client:
        first = client.post(
            "/api/problems/pair-sum-indices/coach",
            json={"source_code": source, "status": "wrong_answer", "message": "wrong", "cases": [failed_case], "step": 1},
        )
        second = client.post(
            "/api/problems/pair-sum-indices/coach",
            json={"source_code": source, "status": "wrong_answer", "message": "wrong", "cases": [failed_case], "step": 2},
        )
        assert first.status_code == second.status_code == 200
        assert first.json()["step"] == 1
        assert second.json()["step"] == 2
        assert "produces []" in first.json()["observation"]
        assert first.json()["nudge"] != second.json()["nudge"]
        assert "final position" in second.json()["nudge"]
        combined = str(first.json()) + str(second.json())
        assert "seen[partner]" not in combined
        assert "return [seen" not in combined
        assert client.post(
            "/api/problems/pair-sum-indices/coach",
            json={"source_code": source, "status": "accepted", "message": "ok", "cases": [], "step": 1},
        ).status_code == 409


def test_codex_coach_api_preserves_unresolved_only_boundary(monkeypatch):
    monkeypatch.setattr(
        "code_practice.app.request_codex_coaching",
        lambda *_args, **_kwargs: {
            "step": 4, "maxSteps": 4, "title": "One issue", "observation": "A boundary is skipped.",
            "nudge": "Trace the last index.", "question": "Can it be visited?", "canContinue": False,
            "source": "codex-cli", "fallbackReason": None,
        },
    )
    payload = {"source_code": "pass", "status": "wrong_answer", "message": "wrong", "cases": [], "step": 3}
    with TestClient(app) as client:
        response = client.post("/api/problems/pair-sum-indices/codex-coach", json=payload)
        assert response.status_code == 200
        assert response.json()["source"] == "codex-cli"
        payload["status"] = "accepted"
        assert client.post("/api/problems/pair-sum-indices/codex-coach", json=payload).status_code == 409
