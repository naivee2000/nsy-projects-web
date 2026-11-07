from datetime import date, datetime, timedelta, timezone
import json
from types import SimpleNamespace

from fastapi.testclient import TestClient
import pytest

from code_practice import accounts, database, review_v2
from code_practice.app import app
from code_practice.catalog import get_catalog
from code_practice.schemas import AttemptCreate


@pytest.fixture
def v2(monkeypatch):
    monkeypatch.setenv("CODE_PRACTICE_REVIEW_V2", "1")
    database.initialize_database()


def insert_attempt(con, key, day, result="accepted", minute=0):
    stamp = review_v2.midnight(day) + timedelta(hours=12, minutes=minute)
    con.execute("""INSERT INTO attempts(problem_id,problem_version,source_code,result,runtime_ms,
                tests_passed,tests_total,created_at) VALUES(?,1,'saved original',?,1,1,1,?)""",
                (key,result,stamp.isoformat()))


def exercise_clean_review_grading():
    key = "leetcode-62"
    today = review_v2.local_day()
    with database.db_session() as con:
        for i, ago in enumerate((70, 69, 66, 59)):
            insert_attempt(con, key, today-timedelta(days=ago))
            if i:
                con.execute("INSERT INTO attempt_contexts VALUES(last_insert_rowid(),'review')")
        review_v2.sync_problem(con, key)
        event = review_v2.event_payload(con, key, str(today-timedelta(days=59)))
        assert event["automaticGrade"] == "easy" and event["cleanStreak"] == 3
        review_v2.sync_problem(con, key)
        assert review_v2.event_payload(con, key, event["date"]) == event
        insert_attempt(con, key, today, "syntax_error")
        insert_attempt(con, key, today, minute=1)
        con.execute("INSERT INTO attempt_contexts VALUES(last_insert_rowid(),'review')")
        review_v2.sync_problem(con, key)
        current = review_v2.event_payload(con, key)
        assert current["cleanStreak"] == 0
        assert current["automaticGrade"] == "hard"


def test_three_due_clean_reviews_and_same_day_replay(v2):
    exercise_clean_review_grading()


def test_corrections_help_timing_and_restart(v2):
    key = "pair-sum-indices"
    with database.db_session() as con:
        insert_attempt(con, key, review_v2.local_day()-timedelta(days=5))
        review_v2.sync_problem(con, key)
    with TestClient(app) as client:
        cid = client.post(f"/api/reviews/{key}/session").json()["id"]
        payload = dict(problem_id=key, problem_version=1, source_code="x", result="syntax_error",
                       runtime_ms=1, tests_passed=0, tests_total=12, entry_point="review", review_context_id=cid)
        client.post('/api/attempts', json=payload)
        # Explicit debugging help is permitted, but does not make a clean review.
        coach = dict(source_code="x", status="syntax_error", message="syntax", mode="debug", review_context_id=cid)
        assert client.post(f"/api/problems/{key}/coach", json=coach).status_code == 200
        payload.update(result="accepted", tests_passed=12)
        event = client.post('/api/attempts', json=payload).json()["reviewEvent"]
        url = f"/api/reviews/events/{event['id']}/feedback"
        assert event["automaticGrade"] == "hard" and event["needsCorrectionAnswer"]
        event = client.put(url, json={"correction_answer":"implementation"}).json()
        assert event["automaticGrade"] == "good" and event["cleanStreak"] == 0
        assert client.put(url, json={"correction_answer":"approach"}).json()["automaticGrade"] == "hard"
        client.put(url, json={"correction_answer":"implementation"})
        # Post-pass study cannot undo the result or its due date.
        after = client.post(f"/api/reviews/sessions/{cid}/help", json={"kind":"solution"}).json()["event"]
        assert after["automaticGrade"] == "good" and after["dueDate"] == event["dueDate"]
        # A new submission incorporates that help.
        event = client.post('/api/attempts', json=payload).json()["reviewEvent"]
        assert event["automaticGrade"] == "again"
        manual = client.put(url, json={"grade":"easy"}).json()
        assert manual["effectiveGrade"] == "easy" and manual["cleanStreak"] == 0
        # Correction changes must not clear an independent manual override.
        assert client.put(url, json={"correction_answer":None}).json()["manualGrade"] == "easy"
    database.initialize_database()
    with TestClient(app) as client:
        restored = client.post(f"/api/reviews/{key}/session").json()["event"]
        assert restored["effectiveGrade"] == "easy" and restored["cleanStreak"] == 0


def test_algorithm_help_precedes_correction_confirmation(v2):
    key = "pair-sum-indices"
    with database.db_session() as con:
        insert_attempt(con, key, review_v2.local_day()-timedelta(days=5))
        review_v2.sync_problem(con, key)
    with TestClient(app) as client:
        cid = client.post(f"/api/reviews/{key}/session").json()["id"]
        client.post(f"/api/reviews/sessions/{cid}/help", json={"kind":"hint","level":1})
        payload = dict(problem_id=key,problem_version=1,source_code="x",result="accepted",runtime_ms=1,
                       tests_passed=12,tests_total=12,entry_point="review",review_context_id=cid)
        event = client.post('/api/attempts',json=payload).json()["reviewEvent"]
        event = client.put(f"/api/reviews/events/{event['id']}/feedback",json={"correction_answer":"implementation"}).json()
        assert event["automaticGrade"] == "hard" and event["cleanStreak"] == 0


@pytest.mark.parametrize("kind,expected", [("debugging","good"),("coach","hard"),("solution","again")])
def test_requested_help_before_first_pass_is_not_clean(v2, kind, expected):
    key = "pair-sum-indices"
    with database.db_session() as con:
        insert_attempt(con, key, review_v2.local_day()-timedelta(days=5))
        review_v2.sync_problem(con, key)
    with TestClient(app) as client:
        cid = client.post(f"/api/reviews/{key}/session").json()["id"]
        assert client.post(f"/api/reviews/sessions/{cid}/help", json={"kind":kind}).status_code == 200
        payload = dict(problem_id=key,problem_version=1,source_code="x",result="accepted",runtime_ms=1,
                       tests_passed=12,tests_total=12,entry_point="review",review_context_id=cid)
        event = client.post('/api/attempts',json=payload).json()["reviewEvent"]
        assert event["automaticGrade"] == expected and event["cleanStreak"] == 0


def test_upgrade_preserves_legacy_schedule_and_assignments(tmp_path, monkeypatch):
    import sqlite3
    path = tmp_path / "old.db"
    day = str(review_v2.local_day()-timedelta(days=5))
    stamp = review_v2.midnight(date.fromisoformat(day)).isoformat()
    state = dict(index=3, intervalDays=14, anchorDay=day,
                 dueDay=str(date.fromisoformat(day)+timedelta(days=14)), recovery=False,
                 latestResult="accepted", lastEventDay=day)
    with sqlite3.connect(path) as con:
        con.execute("CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)")
        for version in range(1, 5):
            for statement in database.MIGRATIONS[version]:
                con.execute(statement)
            con.execute("INSERT INTO schema_migrations VALUES(?,?)", (version,stamp))
        con.execute("INSERT INTO attempts(problem_id,problem_version,source_code,result,runtime_ms,tests_passed,tests_total,created_at) VALUES('leetcode-62',1,'old source','accepted',1,12,12,?)", (stamp,))
        con.execute("INSERT INTO review_events(problem_id,event_date,automatic_grade,manual_grade,latest_result,first_at,last_at,inferred,counted,final_state) VALUES('leetcode-62',?,'good','easy','accepted',?,?,0,1,?)", (day,stamp,stamp,json.dumps(state)))
        con.execute("INSERT INTO review_schedules_v2 VALUES('leetcode-62',?)", (json.dumps(state),))
        con.execute("INSERT INTO review_v2_meta VALUES('replayed-v1',?)", (stamp,))
        con.execute("INSERT INTO daily_review_sessions VALUES(?,?)", (day,stamp))
        con.execute("INSERT INTO daily_review_problems VALUES(?,0,'leetcode-62')", (day,))
    monkeypatch.setattr(database, "DB_PATH", path)
    monkeypatch.setenv("CODE_PRACTICE_REVIEW_V2", "1")
    database.initialize_database()
    database.initialize_database()
    with database.db_session() as con:
        review_v2.sync_problem(con,"leetcode-62")
        row = con.execute("SELECT * FROM review_events").fetchone()
        assert row["manual_grade"] == "easy" and row["policy_version"] == 1
        assert row["clean_streak"] == 0
        assert json.loads(row["final_state"]) == state
        assert json.loads(con.execute("SELECT state_json FROM review_schedules_v2").fetchone()[0]) == state
        assert con.execute("SELECT problem_id FROM daily_review_problems").fetchone()[0] == "leetcode-62"


def test_same_day_replay_is_one_event_and_preserves_raw_attempts(v2):
    day = date(2026, 10, 1)
    with database.db_session() as con:
        for minute in range(5):
            insert_attempt(con,"leetcode-62",day,minute=minute)
        review_v2.sync_problem(con,"leetcode-62")
        state = json.loads(con.execute("SELECT state_json FROM review_schedules_v2").fetchone()[0])
        assert state["dueDay"] == "2026-10-02"
        assert con.execute("SELECT COUNT(*) FROM attempts").fetchone()[0] == 5
        assert con.execute("SELECT COUNT(*) FROM review_events").fetchone()[0] == 1


def test_recovery_early_success_and_manual_regrading_are_idempotent(v2):
    today = review_v2.local_day()
    with database.db_session() as con:
        insert_attempt(con,"leetcode-62",today-timedelta(days=9))
        insert_attempt(con,"leetcode-62",today-timedelta(days=8))
        insert_attempt(con,"leetcode-62",today-timedelta(days=5))
        insert_attempt(con,"leetcode-62",today,"wrong_answer")
        insert_attempt(con,"leetcode-62",today,minute=1)
        review_v2.sync_problem(con,"leetcode-62")
        event = review_v2.event_payload(con,"leetcode-62")
        assert event["automaticGrade"] == "hard"
        event_id = event["id"]
    with TestClient(app) as client:
        first = client.put(f"/api/reviews/events/{event_id}/feedback",json={"grade":"easy"}).json()
        second = client.put(f"/api/reviews/events/{event_id}/feedback",json={"grade":"easy"}).json()
        assert first["dueDate"] == second["dueDate"]
        again = client.put(f"/api/reviews/events/{event_id}/feedback",json={"grade":"again"}).json()
        assert again["dueDate"] == str(today+timedelta(days=1))
        cleared = client.put(f"/api/reviews/events/{event_id}/feedback",json={"grade":None}).json()
        assert cleared["effectiveGrade"] == "hard"


def test_early_clean_practice_cannot_postpone_due():
    previous = {"index":3,"intervalDays":14,"anchorDay":"2026-10-01","dueDay":"2026-10-15","recovery":False}
    for grade in ("good","easy"):
        state,counted = review_v2.advance(previous,date(2026,10,3),grade)
        assert state == previous and not counted
    state,counted = review_v2.advance(previous,date(2026,10,14),"hard")
    assert state["dueDay"] == "2026-10-15" and counted


def test_recent_struggle_fades_and_future_scores_do_not_enable_early_reviews(v2):
    today = review_v2.local_day()
    key="leetcode-62"
    with database.db_session() as con:
        insert_attempt(con,key,today-timedelta(days=30),"wrong_answer")
        insert_attempt(con,key,today-timedelta(days=30),minute=1)
        for ago in (29,26,19):
            insert_attempt(con,key,today-timedelta(days=ago))
        review_v2.sync_problem(con,key)
        row = next(r for r in review_v2.priorities(con,get_catalog().metadata) if r["id"]==key)
        assert row["recentStruggle"] == 0
        assert 0 <= row["score"] <= 100
        con.execute("UPDATE attempts SET elapsed_study_seconds=999999,hint_level=4")
        again = next(r for r in review_v2.priorities(con,get_catalog().metadata) if r["id"]==key)
        assert row["score"] == again["score"]


def test_selector_medium_dp_uniqueness_and_shortages(monkeypatch):
    catalog={}
    rows=[]
    for i in range(7):
        key=f"q{i}"
        catalog[key]=SimpleNamespace(id=key,difficulty=5 if i<4 else 3,topics=["dynamic-programming"] if i==4 else ["trees"])
        rows.append({"id":key,"difficulty":catalog[key].difficulty,"score":100-i,"status":"eligible"})
    monkeypatch.setattr(review_v2,"study_list_badges",lambda key:[{"id":"hot-100"}])
    chosen,notes=review_v2.choose(rows,catalog,"2026-11-03")
    assert len(chosen)==5 and len({r['id'] for r in chosen})==5
    assert sum(r["difficulty"]==5 for r in chosen)==4
    assert "q4" in {r["id"] for r in chosen}
    assert review_v2.choose(rows,catalog,"2026-11-03")== (chosen,notes)
    rows[0]["status"]="not_due"
    chosen,notes=review_v2.choose(rows,catalog,"2026-11-03")
    assert "q0" not in {r["id"] for r in chosen}
    assert sum(r["difficulty"]==5 for r in chosen)==3
    assert any("four" in n for n in notes)


def test_review_workspace_is_separate_assistance_and_feedback_persist(v2):
    key="pair-sum-indices"
    with database.db_session() as con:
        insert_attempt(con,key,review_v2.local_day()-timedelta(days=2))
        review_v2.sync_problem(con,key)
    database.save_draft(key,"# Original draft stays here")
    with TestClient(app) as client:
        session=client.post(f"/api/reviews/{key}/session").json()
        assert session["source"] == get_catalog()[key].starter_code
        cid=session["id"]
        assert client.put(f"/api/reviews/sessions/{cid}/draft",json={"source_code":"# review draft"}).status_code==200
        assert client.post(f"/api/reviews/{key}/session").json()["source"]=="# review draft"
        assert database.get_draft(key)=="# Original draft stays here"
        assert client.post(f"/api/reviews/sessions/{cid}/help",json={"kind":"solution"}).json()["source"]=="saved original"
        payload={"problem_id":key,"problem_version":1,"source_code":"review solution","result":"accepted",
                 "runtime_ms":1,"tests_passed":12,"tests_total":12,"entry_point":"review","review_context_id":cid}
        response=client.post('/api/attempts',json=payload)
        assert response.status_code==200
        event=response.json()["reviewEvent"]
        assert event["automaticGrade"]=="again"
        assert client.put(f"/api/reviews/events/{event['id']}/feedback",json={"grade":"good"}).json()["effectiveGrade"]=="good"
        assert client.post(f"/api/reviews/{key}/session").json()["event"]["manualGrade"]=="good"


def test_assigned_failure_stays_pending_and_scores_endpoint_is_read_only(v2):
    key="pair-sum-indices";today=str(review_v2.local_day())
    with database.db_session() as con:
        insert_attempt(con,key,review_v2.local_day()-timedelta(days=4))
        review_v2.sync_problem(con,key)
    database.save_daily_assignment(today,[])
    database.save_daily_review_assignment(today,[key])
    payload=AttemptCreate(problem_id=key,problem_version=1,source_code="x",result="wrong_answer",runtime_ms=1,tests_passed=0,tests_total=12)
    database.save_attempt(payload,entry_point="review")
    with TestClient(app) as client:
        result=client.get('/api/dashboard').json()
        assert result["reviewAssignedCount"]==1 and not result["reviewComplete"]
        assert result["reviewRecommendations"][0]["id"]==key
        response=client.get('/api/reviews/priorities?search=Pair%20Sum')
        assert response.status_code==200
        assert response.json()["items"][0]["status"]=="retry"
        assert database.get_daily_review_assignment(today)[1]==[key]


def test_member_review_grading_and_account_isolation(v2):
    with TestClient(app):
        user=accounts.create_user('member-test','valid-member-password')
        accounts.set_password(user['id'],'valid-member-password')
        token=accounts.new_session(user['id'])
    key = "leetcode-62"
    with database.db_session() as con:
        insert_attempt(con,key,review_v2.local_day()-timedelta(days=5))
        review_v2.sync_problem(con,key)
    with TestClient(app,cookies={accounts.COOKIE:token}) as client:
        assert client.get('/api/reviews/priorities').status_code==200
        assert client.post(f'/api/reviews/{key}/session',json={}).status_code==409
        assert client.get('/api/dashboard').json()['reviewV2'] is True
        assert client.get('/api/reviews/priorities',headers={"X-Study-Profile":"owner"}).status_code==409
    with database.profile_scope(user['id']):
        # The same clean-streak and grading policy runs in the member database.
        exercise_clean_review_grading()
        with database.db_session() as con:
            event = review_v2.event_payload(con,key)
            assert event["automaticGrade"] == "hard" and event["cleanStreak"] == 0
    with TestClient(app,cookies={accounts.COOKIE:token}) as client:
        session = client.post(f'/api/reviews/{key}/session',json={}).json()
        assert session["hasPreviousSolution"] and session["event"]["needsCorrectionAnswer"]
        url = f"/api/reviews/events/{session['event']['id']}/feedback"
        event = client.put(url,json={"correction_answer":"implementation"}).json()
        assert event["automaticGrade"] == "good"
        assert client.put(url,json={"grade":"easy"}).json()["manualGrade"] == "easy"
        assert client.post(f"/api/reviews/sessions/{session['id']}/help",json={"kind":"solution"}).json()["event"]["manualGrade"] == "easy"
        payload = dict(problem_id=key,problem_version=1,source_code="member source",result="accepted",runtime_ms=1,
                       tests_passed=12,tests_total=12,entry_point="review",review_context_id=session['id'])
        assert client.post('/api/attempts',json=payload).json()["reviewEvent"]["automaticGrade"] == "again"
        client.put(url,json={"grade":"easy"})
        assert client.get('/api/coach/codex-status').status_code == 403
    with TestClient(app):
        pass
    with database.profile_scope(user['id']):
        with database.db_session() as con:
            assert review_v2.event_payload(con,key)["manualGrade"] == "easy"
    with database.db_session() as con:
        assert review_v2.event_payload(con,key) is None


def test_member_selection_has_no_owner_topic_or_medium_quotas(monkeypatch):
    rows = [dict(id=f"easy-{i}",status="eligible",score=90-i,difficulty=2) for i in range(5)]
    rows += [dict(id="dp",status="eligible",score=30,difficulty=5),
             dict(id="unlisted",status="eligible",score=100,difficulty=7),
             dict(id="future",status="not_due",score=100,difficulty=5)]
    monkeypatch.setattr(review_v2,"study_list_badges",lambda key: [] if key=="unlisted" else [{"id":"interview-150"}])
    chosen, notes = review_v2.choose(rows,{},"2026-11-06",owner_focus=False)
    assert [r["id"] for r in chosen] == [f"easy-{i}" for i in range(5)]
    assert not notes and all(r["selectionReason"] == "Due interview practice" for r in chosen)


def test_backfill_is_idempotent_and_does_not_rewrite_legacy_progress(v2):
    with database.db_session() as con:
        insert_attempt(con,"leetcode-62",date(2026,10,1),"wrong_answer")
        insert_attempt(con,"leetcode-62",date(2026,10,1),minute=1)
        con.execute("INSERT INTO review_states VALUES('leetcode-62',5,'2027-01-01T00:00:00+00:00','accepted','original')")
        before=[tuple(r) for r in con.execute('SELECT * FROM attempts')]
        legacy=[tuple(r) for r in con.execute('SELECT * FROM review_states')]
        con.execute("DELETE FROM review_v2_meta")
        review_v2.initialize(con)
        events=[tuple(r) for r in con.execute('SELECT * FROM review_events')]
        review_v2.initialize(con)
        assert events==[tuple(r) for r in con.execute('SELECT * FROM review_events')]
        assert before==[tuple(r) for r in con.execute('SELECT * FROM attempts')]
        assert legacy==[tuple(r) for r in con.execute('SELECT * FROM review_states')]
        assert events[0][8]==1 and events[0][9]==1  # Inferred and counted, without source/timer heuristics.


def test_recovery_cooldown_and_assignment_snapshot_survive_refresh(v2):
    today=review_v2.local_day()
    with database.db_session() as con:
        insert_attempt(con,'leetcode-62',today-timedelta(days=4))
        insert_attempt(con,'leetcode-62',today-timedelta(days=1),'wrong_answer')
        insert_attempt(con,'leetcode-62',today-timedelta(days=1),minute=1)
        review_v2.sync_problem(con,'leetcode-62')
        con.execute('INSERT INTO daily_review_sessions VALUES(?,?)',(str(today-timedelta(days=1)),review_v2.midnight(today-timedelta(days=1)).isoformat()))
        con.execute('INSERT INTO daily_review_problems VALUES(?,0,?)',(str(today-timedelta(days=1)),'leetcode-62'))
        row=next(r for r in review_v2.priorities(con,get_catalog().metadata) if r['id']=='leetcode-62')
        assert row['status']=='eligible' and row['recoveryException']
    with database.db_session() as con:
        assignment,notes=review_v2.ensure_assignment(con,get_catalog().metadata,datetime.now(timezone.utc))
    with database.db_session() as con:
        again,same_notes=review_v2.ensure_assignment(con,get_catalog().metadata,datetime.now(timezone.utc))
        assert assignment==again and notes==same_notes
        assert con.execute('SELECT COUNT(*) FROM review_assignment_details').fetchone()[0]==len(assignment[1])


def test_expired_context_and_foreign_problem_context_are_rejected(v2):
    with database.db_session() as con:
        insert_attempt(con,'pair-sum-indices',review_v2.local_day()-timedelta(days=4))
        review_v2.sync_problem(con,'pair-sum-indices')
    with TestClient(app) as client:
        context=client.post('/api/reviews/pair-sum-indices/session').json()
        payload={'problem_id':'leetcode-62','problem_version':1,'source_code':'x','result':'accepted',
                 'runtime_ms':1,'tests_passed':1,'tests_total':1,'review_context_id':context['id']}
        assert client.post('/api/attempts',json=payload).status_code==409
        with database.db_session() as con:
            con.execute("UPDATE review_contexts SET event_date='2026-01-01' WHERE id=?",(context['id'],))
        assert client.put(f"/api/reviews/sessions/{context['id']}/draft",json={'source_code':'x'}).status_code==409


def test_local_calendar_day_handles_utc_boundary_and_dst():
    assert str(review_v2.local_day(datetime(2026,11,3,3,59,tzinfo=timezone.utc)))=='2026-11-02'
    assert str(review_v2.local_day(datetime(2026,11,3,5,0,tzinfo=timezone.utc)))=='2026-11-03'
