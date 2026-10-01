import json
from pathlib import Path

from fastapi.testclient import TestClient

from code_practice.app import app
from code_practice.catalog import Catalog, get_catalog
from code_practice.database import save_attempt
from code_practice.schemas import AttemptCreate
from code_practice.study_lists import study_list_badges, study_list_snapshot


def test_official_snapshot_is_complete_and_uses_source_ids_and_verified_equivalents():
    root = Path(__file__).resolve().parent.parent
    sources = {r["source_id"]: r for r in map(json.loads, (root / "catalog_import/sources.jsonl").read_text().splitlines())}
    records = {r["source_id"]: r for r in json.loads((root / "catalog_import/ledger.json").read_text())["records"]}
    for plan, expected_count in zip(study_list_snapshot()["lists"], (100, 150)):
        assert len(plan["problems"]) == expected_count
        assert len({p["source_id"] for p in plan["problems"]}) == expected_count
        for member in plan["problems"]:
            assert member["slug"] == sources[member["source_id"]]["slug"]
            record = records[member["source_id"]]
            expected = record["existing_id"] if record["status"] == "overlap" else record.get("problem_id") or f"leetcode-{member['source_id']}"
            assert member["problem_id"] == expected
    assert {b["id"] for b in study_list_badges("pair-sum-indices")} == {"hot-100", "interview-150"}


def test_study_list_filter_paginates_without_loading_problem_details(monkeypatch):
    def forbidden(*args):
        raise AssertionError("Study-list search loaded full problem content")
    monkeypatch.setattr(Catalog, "_load_detail", forbidden)
    catalog = get_catalog()
    with TestClient(app) as client:
        sets = []
        for key in ("hot-100", "interview-150", "interview-picks"):
            expected = {p for p in catalog if any(key == "interview-picks" or b["id"] == key for b in study_list_badges(p))}
            ids = []
            page = 1
            while len(ids) < len(expected):
                response = client.get(f"/api/problems?study_list={key}&page_size=30&page={page}")
                assert response.status_code == 200
                payload = response.json()
                assert payload["total"] == len(expected)
                assert payload["items"]
                ids.extend(p["id"] for p in payload["items"])
                page += 1
            assert len(ids) == len(set(ids))
            assert set(ids) == expected
            sets.append(expected)
        assert sets[2] == sets[0] | sets[1]
        assert "leetcode-146" not in sets[2]  # Excluded LRU Cache is not published.
        assert client.get("/api/problems?study_list=unknown").status_code == 422


def test_study_lists_combine_with_existing_filters_and_preserve_passed_status():
    problem = get_catalog()["pair-sum-indices"]
    save_attempt(AttemptCreate(
        problem_id=problem.id, problem_version=problem.version,
        source_code=problem.reference_solution, result="accepted", runtime_ms=1,
        tests_passed=12, tests_total=12, elapsed_study_seconds=30, hint_level=0,
    ))
    with TestClient(app) as client:
        response = client.get("/api/problems?study_list=hot-100&completion=passed&topic=arrays&difficulty_max=3&search=Pair")
        assert [p["id"] for p in response.json()["items"]] == [problem.id]
        assert response.json()["items"][0]["solved"]
        assert client.get("/api/problems?study_list=hot-100&completion=unsolved&search=Pair%20Sum%20Indices").json()["total"] == 0
        detail = client.get(f"/api/problems/{problem.id}").json()
        assert detail["studyLists"] == response.json()["items"][0]["studyLists"]
        assert all(b["match"] == "equivalent" for b in detail["studyLists"])
        assert all(b["sourceTitle"] == "Two Sum" for b in detail["studyLists"])
