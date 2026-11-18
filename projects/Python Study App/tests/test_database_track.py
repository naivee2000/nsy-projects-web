from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from code_practice import accounts, app as app_module, database, database_track, review_v2
from code_practice.database_catalog import CATALOG
from code_practice.database_judge import matches
from test_accounts import create, online, sign_in


def answer(key=175, *, examples=False, correct=True):
    cases = CATALOG[key]["cases"]
    return {"language": "pandas", "source": "test simulated Worker results",
            "examples": examples, "request_id": str(uuid4()),
            "results": [{"actual": c["expected"] if correct else None} for c in (cases[:2] if examples else cases)]}


def test_two_tabs_get_same_sets_and_example_does_not_record():
    with TestClient(app_module.app) as client:
        with ThreadPoolExecutor(max_workers=2) as executor:
            left, right = list(executor.map(lambda _: client.get("/api/dashboard").json(), range(2)))
        assert left["database"] == right["database"]
        assert left["reviewRecommendations"] == right["reviewRecommendations"]
        assert len(left["database"]["newProblems"]) == 5
        assert left["database"]["dailyAssignment"] == left["database"]["newProblems"]
        assert all(not item["completedToday"] for item in left["database"]["dailyAssignment"])
        assert left["database"]["reviews"] == []
        assert client.get("/api/database/problems").json()["total"] == 323
        result = client.post("/api/database/problems/175/judge", json=answer(examples=True)).json()
        assert result["accepted"]
        assert client.get("/api/dashboard").json()["database"]["solved"] == 0


def test_database_profile_drafts_submissions_and_algorithm_isolation(online):
    user = create(online)
    with TestClient(app_module.app) as member:
        sign_in(member, "learner")
        initial = member.get("/api/dashboard").json()["database"]
        item = initial["newProblems"][0]
        key = item["id"]
        for language in ("mysql", "pandas"):
            response = member.put(f"/api/database/problems/{key}/draft/{language}", json={"source": language})
            assert response.status_code == 200
        submission = answer(key)
        reply = member.post(f"/api/database/problems/{key}/judge", json=submission).json()
        assert reply["accepted"]
        assert member.post(f"/api/database/problems/{key}/judge", json=submission).json() == reply
        assert member.get(f"/api/database/problems/{key}").json()["drafts"] == {"mysql": "mysql", "pandas": "pandas"}
        state = member.get("/api/dashboard").json()
        assert state["solvedCount"] == 0 and state["database"]["solved"] == 1
        assert len(state["database"]["newProblems"]) == 4
        assert [p["id"] for p in state["database"]["dailyAssignment"]] == [p["id"] for p in initial["dailyAssignment"]]
        assert [p["id"] for p in state["database"]["dailyAssignment"] if p["completedToday"]] == [key]
        library = member.get("/api/database/problems", params={"completion":"passed","topic":item["topic"]}).json()
        assert [p["id"] for p in library["items"]] == [key]
        assert library["items"][0]["prompt"] and item["topic"] in library["topics"]
        assert online.get("/api/database/problems?completion=passed").json()["total"] == 0
    with database.profile_scope(user["id"]), database.db_session() as con:
        assert con.execute("SELECT count(*) FROM db_track_attempts").fetchone()[0] == 1
        assert con.execute("SELECT count(*) FROM db_track_events").fetchone()[0] == 1
    assert online.get(f"/api/database/problems/{key}").json()["drafts"] == {}
    assert online.get("/api/dashboard").json()["database"]["solved"] == 0


def test_review_uses_ny_day_and_is_separate_from_original_draft(monkeypatch, tmp_path):
    clock = [datetime(2026, 11, 18, 4, 30, tzinfo=timezone.utc)]
    local_day = review_v2.local_day
    dashboard = database_track.dashboard
    monkeypatch.setattr(database_track, "dashboard", lambda now=None: dashboard(clock[0]))
    monkeypatch.setattr(review_v2, "local_day", lambda now=None: local_day(now or clock[0]))
    with TestClient(app_module.app) as client:
        client.get("/api/dashboard")
        endpoint = "/api/database/problems/175"
        client.put(endpoint + "/draft/pandas", json={"source": "original"})
        assert not client.post(endpoint + "/judge", json=answer(correct=False)).json()["accepted"]
        assert client.post(endpoint + "/judge", json=answer()).json()["accepted"]
        clock[0] = datetime(2026, 11, 18, 5, 30, tzinfo=timezone.utc)
        state = client.get("/api/dashboard").json()["database"]
        assert state["day"] == "2026-11-18" and [p["id"] for p in state["reviews"]] == [175]
        assert state["reviewAssignment"][0]["passedLanguages"] == ["pandas"]
        assert not state["reviewAssignment"][0]["completedToday"]
        assert client.get(endpoint + "?review_day=2026-11-18").json()["drafts"] == {}
        assert client.post(endpoint + "/judge", json={**answer(examples=True), "review_day": state["day"]}).json()["accepted"]
        assert not client.get("/api/dashboard").json()["database"]["reviewAssignment"][0]["completedToday"]
        assert client.post(endpoint + "/judge", json={**answer(), "review_day": state["day"]}).json()["accepted"]
        assert client.get("/api/dashboard").json()["database"]["reviews"] == []
        assert [(p["id"],p["completedToday"]) for p in client.get("/api/dashboard").json()["database"]["reviewAssignment"]] == [(175,True)]
        assert client.put(endpoint + "/rating", json={"grade":"hard"}).json()["manualGrade"] == "hard"
        assert client.get(endpoint).json()["reviewFeedback"]["manualGrade"] == "hard"
        assert client.get(endpoint).json()["drafts"] == {"pandas": "original"}
    backup = tmp_path / "backup"
    accounts.backup_all(backup)
    with database.db_session() as con:
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    with TestClient(app_module.app) as restarted:
        assert restarted.get(endpoint).json()["passedLanguages"] == ["pandas"]
        assert restarted.get("/api/dashboard").json()["database"]["reviewAssignment"][0]["completedToday"]


def test_table_comparison_respects_column_aliases_nulls_and_duplicate_rows():
    expected = {"columns": ["result"], "rows": [[None], [2], [2]]}
    assert matches(expected, ["result"], [[2], [None], [2]])
    assert not matches(expected, ["result"], [[2], [None], [2]], ordered=True)
    assert not matches(expected, ["result"], [[2], [None]])
    assert not matches(expected, ["result"], [[2], ["NULL"], [2]])
    assert not matches({"columns": ["x"], "rows": []}, ["y"], [])


def test_mysql_setup_timeout_keeps_draft_and_does_not_record_an_attempt(monkeypatch):
    import subprocess
    from code_practice import database_judge

    def unavailable(*args, **kwargs):
        raise subprocess.TimeoutExpired("mysql", 5)

    monkeypatch.setattr(database_judge, "client", unavailable)
    endpoint = "/api/database/problems/175"
    with TestClient(app_module.app) as client:
        assert client.put(endpoint + "/draft/mysql", json={"source": "SELECT 1"}).is_success
        response = client.post(endpoint + "/judge", json={
            "language": "mysql", "source": "SELECT 1", "request_id": str(uuid4()),
        })
        assert response.status_code == 503
        assert client.get(endpoint).json()["drafts"] == {"mysql": "SELECT 1"}
        with database.db_session() as con:
            for table in ("db_track_attempts", "db_track_events"):
                assert con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0


def test_additive_upgrade_and_restored_backup_keep_old_progress(tmp_path, monkeypatch):
    import sqlite3

    member = "a" * 32
    profile_db = database.profile_database_path(member)
    profile_db.parent.mkdir(parents=True)
    with sqlite3.connect(profile_db) as old:
        old.execute("CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)")
        for version in range(1, 6):
            for sql in database.MIGRATIONS[version]:
                old.execute(sql)
            old.execute("INSERT INTO schema_migrations VALUES(?,?)", (version, "prior"))
        old.execute("INSERT INTO drafts VALUES(?,?,?)", ("pair-sum-indices", "# existing", "prior"))
    with database.profile_scope(member):
        database.initialize_database()
        assert database.get_draft("pair-sum-indices") == "# existing"
        with database.db_session() as con:
            con.execute("INSERT INTO db_track_drafts VALUES(?,?,?,?)", (175, "mysql", "practice", "-- saved"))
            assert con.execute("PRAGMA foreign_key_check").fetchall() == []
    restored_root = tmp_path / "restored"
    restored_db = restored_root / "profiles" / member / "code_practice.db"
    restored_db.parent.mkdir(parents=True)
    with sqlite3.connect(profile_db) as source, sqlite3.connect(restored_db) as backup:
        source.backup(backup)
    monkeypatch.setattr(database, "DATA_DIR", restored_root)
    with database.profile_scope(member):
        database.initialize_database()
        assert database.get_draft("pair-sum-indices") == "# existing"
        with database.db_session() as con:
            assert con.execute("SELECT source FROM db_track_drafts").fetchone()[0] == "-- saved"
