from datetime import datetime, timezone

from fastapi.testclient import TestClient

from code_practice.app import app
from code_practice.catalog import get_catalog, refresh_catalog
from code_practice.database import connect, get_draft, list_attempts, save_attempt, save_variant
from code_practice.schemas import AttemptCreate


def test_health_problem_detail_and_hidden_boundary():
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["mode"] == "local-only"
        assert health.json()["problemCount"] == 100

        listing = client.get("/api/problems").json()
        assert len(listing) == 100
        detail = client.get("/api/problems/pair-sum-indices").json()
        assert len(detail["tests"]) == 2
        assert "reference_solution" not in detail
        package = client.post("/api/problems/pair-sum-indices/submission-package").json()
        assert len(package["tests"]) == 12


def test_schema_migration_is_versioned_and_idempotent():
    from code_practice.database import initialize_database
    initialize_database()
    initialize_database()
    with connect() as connection:
        versions = connection.execute("SELECT version FROM schema_migrations").fetchall()
    assert [row["version"] for row in versions] == [1, 2, 3]


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
        listing = client.get("/api/problems").json()
        assert next(item for item in listing if item["id"] == "pair-sum-indices")["solved"] is True
        progress = client.get("/api/progress").json()
        assert progress["solvedCount"] == 1
        assert progress["mastery"]["arrays"] == 60.0


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
        ids = {item["id"] for item in client.get("/api/problems").json()}
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


def test_dashboard_caps_primary_at_four_when_medium_is_included_and_reviews_at_five():
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
        assert len(payload["recommendations"]) == 4
        assert any(4 <= problem["difficulty"] <= 7 for problem in payload["recommendations"])
        assert all(not problem["solved"] for problem in payload["recommendations"])
        assert len(payload["reviewRecommendations"]) == 5
        assert all(problem["solved"] for problem in payload["reviewRecommendations"])


def test_dashboard_caps_primary_at_three_when_hard_is_included():
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
        assert len(payload["recommendations"]) == 3
        assert any(problem["difficulty"] >= 8 for problem in payload["recommendations"])
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
