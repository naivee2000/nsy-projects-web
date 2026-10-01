from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from code_practice import database, interview_plan
from code_practice.app import app
from code_practice.catalog import get_catalog, refresh_catalog
from code_practice.interview_plan import InterviewPlan
from code_practice.learning import choose_daily_session
from code_practice.schemas import AttemptCreate
from code_practice.study_lists import study_list_badges


NOW = datetime(2026, 9, 30, tzinfo=timezone.utc)


def problem(key, difficulty, topics, prerequisites=()):
    return SimpleNamespace(id=key, title=key, difficulty=difficulty, topics=topics, prerequisites=prerequisites)


def attempt(key, result="accepted", minutes=0):
    return SimpleNamespace(problem_id=key, result=result, hint_level=0, created_at=NOW + timedelta(minutes=minutes))


def plan_for(monkeypatch, problems, targets, attempts=()):
    monkeypatch.setattr(interview_plan, "study_list_badges", lambda key: [{}] if key in targets else [])
    return InterviewPlan({p.id: p for p in problems}, attempts, [], NOW, "2026-09-30")


def test_unseen_interval_target_gets_related_easy_preparation_not_unrelated_work(monkeypatch):
    problems = [problem("target", 5, ["intervals", "arrays"]),
                problem("intro", 3, ["intervals", "arrays"]),
                problem("unrelated", 2, ["trees"])]
    plan = plan_for(monkeypatch, problems, {"target"})
    assert [p.id for p in plan.ordered] == ["intro"]
    assert "target" in plan.reason("intro")
    ready = plan_for(monkeypatch, problems, {"target"}, [attempt("intro")])
    assert [p.id for p in ready.ordered] == ["target"]


def test_hard_requires_two_distinct_related_medium_successes_and_mastery(monkeypatch):
    problems = [problem("target", 8, ["intervals"]), problem("easy", 3, ["intervals"]),
                problem("medium1", 4, ["intervals"]), problem("medium2", 5, ["intervals"])]
    history = [attempt("easy"), attempt("medium1", minutes=1), attempt("medium1", minutes=2)]
    plan = plan_for(monkeypatch, problems, {"target"}, history)
    assert [p.id for p in plan.ordered] == ["medium2"]
    history.append(attempt("medium2", minutes=3))
    assert "target" in plan_for(monkeypatch, problems, {"target"}, history).ready_targets
    history.extend(attempt("medium2", "wrong_answer", minutes=4+i) for i in range(4))
    assert "target" not in plan_for(monkeypatch, problems, {"target"}, history).ready_targets


def test_upper_medium_requires_a_lower_medium_and_topic_aliases_match(monkeypatch):
    problems = [problem("target", 6, ["binary search"]), problem("easy", 3, ["binary-search"]),
                problem("middle", 4, ["binary_search"])]
    plan = plan_for(monkeypatch, problems, {"target"}, [attempt("easy")])
    assert [p.id for p in plan.ordered] == ["middle"]
    assert "target" in plan_for(monkeypatch, problems, {"target"}, [attempt("easy"), attempt("middle")]).ready_targets


def test_repeated_failure_takes_an_easier_detour_before_retry(monkeypatch):
    problems = [problem("target", 5, ["intervals"]), problem("easy", 3, ["intervals"]),
                problem("reinforcement", 3, ["intervals"])]
    history = [attempt("easy"), attempt("target", "wrong_answer", 1), attempt("target", "runtime_error", 2)]
    plan = plan_for(monkeypatch, problems, {"target"}, history)
    assert [p.id for p in plan.ordered] == ["reinforcement"]
    assert "target" not in plan.ready_targets
    history.append(attempt("reinforcement", minutes=3))
    assert "target" in plan_for(monkeypatch, problems, {"target"}, history).ready_targets


def test_prerequisite_cycle_stops_without_selecting_locked_or_unrelated_work(monkeypatch):
    problems = [problem("target", 5, ["intervals"], ["intervals"]),
                problem("intro", 3, ["intervals"], ["intervals"]),
                problem("unrelated", 2, ["trees"])]
    assert plan_for(monkeypatch, problems, {"target"}).ordered == []


def test_published_curriculum_can_reach_all_targets_without_unrelated_filler():
    catalog = get_catalog().metadata
    attempts = []
    seen = set()
    for day in range(200):
        plan = InterviewPlan(catalog, attempts, [], NOW + timedelta(days=day), str(day))
        if not plan.remaining:
            break
        selection = choose_daily_session(plan.ordered)
        assert selection, f"Blocked targets: {sorted(plan.remaining)}"
        for p in selection:
            assert p.id not in seen
            assert p.id in plan.targets or plan.reason(p.id)
            assert not plan.blockers(p)
            seen.add(p.id)
            attempts.append(attempt(p.id, minutes=day * 24 * 60))
    assert not plan.remaining
    assert plan.targets <= seen
    assert plan.ordered == []


def test_dashboard_reports_progress_and_keeps_saved_day_on_restart():
    today = datetime.now().astimezone().date().isoformat()
    # Existing assignment survives the switch to the interview curriculum.
    database.save_daily_assignment(today, ["pair-sum-indices"])
    with TestClient(app) as client:
        first = client.get("/api/dashboard").json()
    refresh_catalog()
    with TestClient(app) as client:
        second = client.get("/api/dashboard").json()
    assert [p["id"] for p in second["recommendations"]] == ["pair-sum-indices"]
    assert second["interviewProgress"] == first["interviewProgress"]
    expected = {key for key in get_catalog().metadata if study_list_badges(key)}
    assert second["interviewProgress"]["available"] == len(expected)
    assert second["interviewProgress"]["solved"] == 0
    assert [p["available"] for p in second["interviewProgress"]["lists"]] == [89, 132]
    database.save_attempt(AttemptCreate(
        problem_id="pair-sum-indices", problem_version=1, source_code="saved solution",
        result="accepted", runtime_ms=1, tests_passed=12, tests_total=12,
        elapsed_study_seconds=60, hint_level=0,
    ))
    refresh_catalog()
    with TestClient(app) as client:
        finished = client.get("/api/dashboard").json()
    assert finished["dailyComplete"]
    assert finished["recommendations"] == []
    assert finished["interviewProgress"]["solved"] == 1
    assert [p["solved"] for p in finished["interviewProgress"]["lists"]] == [1, 1]
