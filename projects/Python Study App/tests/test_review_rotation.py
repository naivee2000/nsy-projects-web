from datetime import date, datetime, timedelta, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import random
import sqlite3
import subprocess
import sys
from types import SimpleNamespace

from fastapi.testclient import TestClient
import pytest

from code_practice import accounts, database, review_v2
from code_practice.app import app
from code_practice.catalog import get_catalog


DAY = date(2026, 11, 17)
NOW = review_v2.midnight(DAY) + timedelta(hours=12)


def candidate(key, *, days=10, score=60, recovery=False, difficulty=5, topic="trees", due_days=20):
    last_day = str(DAY - timedelta(days=days))
    return dict(id=key, title=key, status="eligible", score=score, difficulty=difficulty,
                lastActivityDate=last_day, daysSinceLastActivity=days, lastSubmissionDate=last_day,
                lastAssignmentDate=None, dueDate=str(DAY - timedelta(days=due_days)),
                olderReviewEligible=days >= 14, recentRecovery=recovery and days <= 7, topic=topic)


def catalog_for(rows):
    return {r["id"]: SimpleNamespace(id=r["id"], difficulty=r["difficulty"],
                                    topics=["matrices", "recursion"] if r["topic"] == "grid" else [r["topic"]])
            for r in rows}


@pytest.fixture
def listed(monkeypatch):
    monkeypatch.setattr(review_v2, "study_list_badges", lambda key: [{"id": "hot-100"}])


@pytest.fixture
def v2(monkeypatch):
    monkeypatch.setenv("CODE_PRACTICE_REVIEW_V2", "1")
    database.initialize_database()


def store_history(con, key, *, ago=30, assigned_ago=None, recovery=False):
    submitted = review_v2.midnight(DAY - timedelta(days=ago)) + timedelta(hours=12)
    con.execute("""INSERT INTO attempts(problem_id,problem_version,source_code,result,runtime_ms,
                   tests_passed,tests_total,created_at) VALUES(?,1,'original','accepted',1,12,12,?)""",
                (key, submitted.isoformat()))
    review_v2.sync_problem(con, key)
    state = dict(index=0, intervalDays=1, anchorDay=str(DAY-timedelta(days=ago)),
                 dueDay=str(DAY-timedelta(days=1)), recovery=recovery,
                 latestResult="accepted", lastEventDay=str(DAY-timedelta(days=ago)))
    con.execute("UPDATE review_schedules_v2 SET state_json=? WHERE problem_id=?", (json.dumps(state), key))
    if assigned_ago is not None:
        day = str(DAY - timedelta(days=assigned_ago))
        con.execute("INSERT OR IGNORE INTO daily_review_sessions VALUES(?,?)", (day, submitted.isoformat()))
        position = con.execute("SELECT count(*) FROM daily_review_problems WHERE assignment_date=?", (day,)).fetchone()[0]
        con.execute("INSERT INTO daily_review_problems VALUES(?,?,?)", (day, position, key))


@pytest.mark.parametrize("ago,older,recent", [(0, False, True), (7, False, True),
                                            (8, False, False), (13, False, False),
                                            (14, True, False), (15, True, False)])
def test_calendar_boundaries_for_full_submissions(v2, ago, older, recent):
    key = "leetcode-62"
    with database.db_session() as con:
        store_history(con, key, ago=ago, recovery=True)
        row = next(r for r in review_v2.priorities(con, get_catalog().metadata, NOW) if r["id"] == key)
        assert row["lastSubmissionDate"] == str(DAY - timedelta(days=ago))
        assert row["daysSinceLastActivity"] == ago
        assert row["olderReviewEligible"] == older
        assert row["recentRecovery"] == recent


def test_assignments_without_completion_and_same_day_submissions_count(v2):
    keys = ["leetcode-62", "pair-sum-indices", "matrix-spiral-order"]
    with database.db_session() as con:
        store_history(con, keys[0], assigned_ago=7, recovery=True)
        store_history(con, keys[1], assigned_ago=13)
        store_history(con, keys[2], assigned_ago=14)
        before = {r["id"]: r for r in review_v2.priorities(con, get_catalog().metadata, NOW)}
        assert before[keys[0]]["recentRecovery"] and before[keys[0]]["daysSinceLastActivity"] == 7
        # Several full submissions on one NY calendar day share the same date,
        # even though one timestamp is on the following UTC day.
        for stamp in ("2026-11-17T23:50:00-05:00", "2026-11-18T04:55:00+00:00"):
            con.execute("""INSERT INTO attempts(problem_id,problem_version,source_code,result,runtime_ms,
                           tests_passed,tests_total,created_at) VALUES(?,1,'original','accepted',1,12,12,?)""",
                        (keys[0], stamp))
        rows = {r["id"]: r for r in review_v2.priorities(con, get_catalog().metadata, NOW)}
        assert rows[keys[0]]["lastAssignmentDate"] == "2026-11-10"
        assert rows[keys[0]]["lastSubmissionDate"] == "2026-11-17"
        assert rows[keys[0]]["daysSinceLastActivity"] == 0 and rows[keys[0]]["recentRecovery"]
        assert not rows[keys[1]]["olderReviewEligible"]
        assert rows[keys[2]]["olderReviewEligible"]
        assert rows[keys[2]]["lastActivityDate"] == "2026-11-03"


@pytest.mark.parametrize("owner", [False, True])
def test_balanced_selection_preserves_size_quota_and_topic_rotation(listed, owner):
    topics = ["dynamic-programming", "trees", "linked-list", "graphs", "grid"]
    rows = [candidate(f"recovery-{i}", days=2, recovery=True, score=99-i, topic=topic)
            for i, topic in enumerate(topics)]
    rows += [candidate("oldest", days=40, score=1), candidate("old-dp", days=30, score=2, topic=topics[0])]
    rows += [candidate(f"normal-{i}", topic=topic) for i, topic in enumerate(topics)]
    catalog = catalog_for(rows)
    for offset in range(6):
        day = str(DAY + timedelta(days=offset))
        chosen, notes = review_v2.choose(rows, catalog, day, owner_focus=owner)
        keys = {r["id"] for r in chosen}
        assert len(chosen) == len(keys) == 5
        assert "oldest" in keys
        assert sum(r["recentRecovery"] for r in chosen) <= 2
        assert not any("exception:" in note for note in notes)
        assert review_v2.choose(list(reversed(rows)), catalog, day, owner_focus=owner) == (chosen, notes)
        if owner:
            pair = list(combinations(range(4), 2))[(DAY+timedelta(days=offset)).toordinal() % 6]
            reasons = [r["selectionReason"] for r in chosen]
            assert sum(4 <= r["difficulty"] <= 7 for r in chosen) >= 4
            assert any(reason.startswith("Daily DP") for reason in reasons)
            assert all(any(reason.startswith(review_v2.GROUPS[index][0]) for reason in reasons) for index in pair)


def test_member_minimum_recovery_exception_and_oldest_tiebreak(listed):
    rows = [candidate(f"recovery-{i}", days=2, recovery=True, score=100-i) for i in range(4)]
    rows += [candidate("old-later", days=30, due_days=15, score=50),
             candidate("old-earlier", days=30, due_days=25, score=1)]
    chosen, notes = review_v2.choose(rows, {}, str(DAY), owner_focus=False)
    assert sum(r["recentRecovery"] for r in chosen) == 3
    assert {"old-later", "old-earlier"} <= {r["id"] for r in chosen}
    protected = [r for r in chosen if "Older review:" in r["selectionReason"]]
    assert [r["id"] for r in protected] == ["old-earlier"]
    assert any("3 recent recovery" in n and "1 above two" in n for n in notes)


def test_existing_owner_coverage_can_require_minimum_exception(listed):
    rows = [candidate("dp", topic="dynamic-programming", days=1, recovery=True)]
    rows += [candidate(f"r{i}", days=1, recovery=True, score=99-i) for i in range(3)]
    rows += [candidate("older", days=30, difficulty=2), candidate("recent-easy", difficulty=2)]
    chosen, notes = review_v2.choose(rows, catalog_for(rows), str(DAY))
    assert len(chosen) == 5
    assert sum(r["difficulty"] == 5 for r in chosen) == 4
    assert sum(r["recentRecovery"] for r in chosen) == 4
    assert "older" in {r["id"] for r in chosen}
    assert any("2 above two" in n for n in notes)


def test_oldest_only_when_compatible_and_members_keep_their_pool(monkeypatch):
    rows = [candidate(f"m{i}", days=20+i, difficulty=5) for i in range(4)]
    rows += [candidate("dp-easy", topic="dynamic-programming", difficulty=2),
             candidate("incompatible-oldest", days=90, difficulty=2),
             candidate("future", days=100), candidate("unlisted", days=120)]
    rows[-2]["status"] = "not_due"
    rows[-1]["status"] = "retry"
    monkeypatch.setattr(review_v2, "study_list_badges", lambda key: [] if key == "unlisted" else [{"id": "hot-100"}])
    chosen, _ = review_v2.choose(rows, catalog_for(rows), str(DAY))
    assert "incompatible-oldest" not in {r["id"] for r in chosen}
    assert "m3" in {r["id"] for r in chosen}
    rows[-1]["status"] = "eligible"
    chosen, _ = review_v2.choose(rows, {}, str(DAY), owner_focus=False)
    assert "incompatible-oldest" in {r["id"] for r in chosen}
    assert "unlisted" not in {r["id"] for r in chosen}
    assert "future" not in {r["id"] for r in chosen}


def test_owner_explains_when_older_candidate_cannot_fit_existing_quotas(listed):
    rows = [candidate("dp-easy", topic="dynamic-programming", difficulty=2)]
    rows += [candidate(f"medium-{i}") for i in range(4)]
    rows += [candidate("older-easy", days=30, difficulty=2)]
    chosen, notes = review_v2.choose(rows, catalog_for(rows), str(DAY))
    assert len(chosen) == 5 and sum(r['difficulty'] == 5 for r in chosen) == 4
    assert 'dp-easy' in {r['id'] for r in chosen}
    assert 'older-easy' not in {r['id'] for r in chosen}
    assert any('No suitable older review' in note for note in notes)


def test_no_older_candidate_and_due_pool_shortage_are_explained(listed):
    rows = [candidate("only", days=2, recovery=True)]
    chosen, notes = review_v2.choose(rows, {}, str(DAY), owner_focus=False)
    assert len(chosen) == 1
    assert any("Fewer than five" in n for n in notes)
    assert any("No suitable older review" in n for n in notes)


def test_balancing_matches_exhaustive_search_on_small_member_pools(listed):
    rng = random.Random(1417)
    for _ in range(60):
        rows = [candidate(f"q{i}", days=rng.choice([2, 7, 8, 14, 30]),
                          score=rng.randrange(1, 100), recovery=bool(rng.randrange(2)),
                          due_days=rng.randrange(1, 25)) for i in range(8)]
        def quality(chosen):
            older = [r for r in chosen if r['olderReviewEligible']]
            oldest = min(((r['lastActivityDate'], r['dueDate']) for r in older), default=('9999', '9999'))
            return (max(0, sum(r['recentRecovery'] for r in chosen)-2), not bool(older),
                    oldest, -sum(r['score'] for r in chosen))
        expected = min(quality(selection) for selection in combinations(rows, 5))
        chosen, _ = review_v2.choose(rows, {}, str(DAY), owner_focus=False)
        assert quality(chosen) == expected


def test_oldest_rotation_uses_assignment_even_without_a_submission(v2):
    catalog = get_catalog().metadata
    keys = [p.id for p in catalog.values() if review_v2.study_list_badges(p.id)][:7]
    profile = "a" * 32
    with database.profile_scope(profile):
        database.initialize_database()
        with database.db_session() as con:
            for index, key in enumerate(keys):
                store_history(con, key, ago=40-index)
        with database.db_session() as con:
            first, _ = review_v2.ensure_assignment(con, catalog, NOW)
        with database.db_session() as con:
            tomorrow, _ = review_v2.ensure_assignment(con, catalog, NOW+timedelta(days=1))
            assert len(first[1]) == 5
            assert not set(first[1]) & set(tomorrow[1])
            assert keys[0] in first[1] and keys[5] in tomorrow[1]
            snapshot = con.execute("SELECT reason FROM review_assignment_details WHERE assignment_date=? AND problem_id=?", (str(DAY), keys[0])).fetchone()[0]
            assert "Older review: last practised 40 days ago" in snapshot
            assert con.execute("SELECT value FROM review_v2_meta WHERE key=?", (f"assignment-policy:{DAY}",)).fetchone()[0] == review_v2.SELECTION_POLICY_VERSION


def test_saved_assignment_metadata_reload_completion_and_accounts(v2):
    key = "pair-sum-indices"
    today = review_v2.local_day()
    with database.db_session() as con:
        store_history(con, key)
    database.save_daily_assignment(str(today), [])
    with TestClient(app) as client:
        original = client.get('/api/dashboard').json()
        assert original['reviewAssignedCount'] == 1
        before = client.get('/api/reviews/priorities?status=assigned').json()
        assert before['selectionPolicyVersion'] == review_v2.SELECTION_POLICY_VERSION
        assert before['selectionExplanations'] == original['reviewSelectionNotes']
        assert 'Older review:' in before['items'][0]['assignmentReason']
        member = accounts.create_user('rotation-test', 'a-valid-test-password')
        accounts.set_password(member['id'], 'a-valid-test-password')
        token = accounts.new_session(member['id'])
        problem = get_catalog()[key]
        payload = dict(problem_id=key, problem_version=problem.version, source_code='answer',
                       result='accepted', runtime_ms=1, tests_passed=12, tests_total=12)
        assert client.post('/api/attempts', json=payload).status_code == 200
        completed = client.get('/api/dashboard').json()
        assert completed['reviewComplete'] and not completed['reviewRecommendations']
        assert completed['reviewAssignedCount'] == 1
    database.initialize_database()
    with TestClient(app) as client:
        assert client.get('/api/dashboard').json()['reviewComplete']
        after = client.get('/api/reviews/priorities?status=assigned').json()
        assert before['selectionPolicyVersion'] == after['selectionPolicyVersion']
        assert before['selectionExplanations'] == after['selectionExplanations']
        assert before['items'][0]['assignmentReason'] == after['items'][0]['assignmentReason']
    with TestClient(app, cookies={accounts.COOKIE: token}) as client:
        assert not client.get('/api/reviews/priorities?status=assigned').json()['items']
        assert client.get('/api/dashboard').json()['solvedCount'] == 0


def test_old_saved_sets_are_never_backfilled_with_new_selection_metadata(v2):
    key = "pair-sum-indices"
    day = str(review_v2.local_day())
    database.save_daily_review_assignment(day, [key])
    with database.db_session() as con:
        before = [tuple(row) for row in con.execute('SELECT * FROM daily_review_problems')]
        assignment, _ = review_v2.ensure_assignment(con, get_catalog().metadata, datetime.now(timezone.utc))
        assert assignment[1] == [key]
        assert before == [tuple(row) for row in con.execute('SELECT * FROM daily_review_problems')]
        assert not con.execute("SELECT 1 FROM review_v2_meta WHERE key=?", (f"assignment-policy:{day}",)).fetchone()


@pytest.mark.parametrize("version", [1, 3, 4, 5])
def test_preview_migrates_only_in_memory_and_supports_member_profiles(tmp_path, version):
    path = tmp_path / 'old database.db'
    with sqlite3.connect(path) as con:
        con.execute('CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)')
        for number in range(1, version+1):
            for statement in database.MIGRATIONS[number]:
                con.execute(statement)
            con.execute('INSERT INTO schema_migrations VALUES(?,?)', (number, NOW.isoformat()))
        con.execute("""INSERT INTO attempts(problem_id,problem_version,source_code,result,runtime_ms,
                       tests_passed,tests_total,created_at) VALUES('pair-sum-indices',1,'original','accepted',1,12,12,?)""",
                    ((NOW-timedelta(days=30)).isoformat(),))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    script = Path(__file__).resolve().parents[1] / 'scripts/review_v2_preview.py'
    output = subprocess.run([sys.executable, str(script), '--db', str(path), '--profile', 'member', '--now', NOW.isoformat()],
                            capture_output=True, text=True, check=True)
    preview = json.loads(output.stdout)
    assert preview['profile'] == 'member' and preview['sourceUnchanged']
    assert preview['selectionPolicyVersion'] == review_v2.SELECTION_POLICY_VERSION
    assert preview['previewSelection'][0]['id'] == 'pair-sum-indices'
    assert preview['previewSelection'][0]['olderReviewEligible']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    assert not path.with_name(path.name+'-wal').exists()
