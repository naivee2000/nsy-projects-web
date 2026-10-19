from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
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


def test_dp_beginner_gets_two_easy_and_three_normal_credits(monkeypatch):
    dp = [problem(f"dp{i}", 3, ["dynamic programming"]) for i in range(4)]
    normal = [problem(f"normal{i}", 3, ["trees"]) for i in range(5)]
    plan = plan_for(monkeypatch, dp + normal, {p.id for p in normal})
    selected = plan.daily_session()
    assert len(selected) == 5
    assert sum(p.id.startswith("dp") for p in selected) == 2
    assert len({p.id for p in selected}) == 5
    assert plan.daily_session() == selected


def test_dp_progression_needs_two_distinct_easy_passes_and_recent_mastery(monkeypatch):
    dp = [problem(f"dp{i}", 3, ["dynamic-programming"]) for i in range(5)]
    medium = problem("dp-medium", 4, ["dynamic-programming"])
    normal = [problem(f"normal{i}", 3, ["trees"]) for i in range(4)]
    problems = dp + [medium] + normal
    targets = {p.id for p in normal} | {medium.id}
    for history, expect_medium in [
        ([attempt("dp0"), attempt("dp0", minutes=1)], False),
        ([attempt("dp0"), attempt("dp1", minutes=1)], True),
        ([attempt("dp0"), attempt("dp1", minutes=1), attempt("dp-medium", "wrong_answer", 2)], False),
    ]:
        plan = plan_for(monkeypatch, problems, targets, history)
        selected = plan.daily_session()
        assert ("dp-medium" in {p.id for p in selected}) == expect_medium
        assert sum(plan._credits(p) for p in selected) == 5
        assert not ({"dp0", "dp1"} & {p.id for p in selected} & plan.solved)
        assert sum(p.id.startswith("normal") for p in selected) == 3


def test_dp_medium_gates_and_remaining_interview_medium_budget(monkeypatch):
    problems = [problem("dp0", 3, ["dynamic-programming"]),
                problem("dp1", 3, ["dynamic-programming"]),
                problem("dp2", 3, ["dynamic-programming"]),
                problem("dp3", 3, ["dynamic-programming"]),
                problem("dp-locked", 4, ["dynamic-programming", "intervals"]),
                problem("interval-intro", 3, ["intervals"]),
                problem("tree-intro", 3, ["trees"]),
                problem("tree-medium", 4, ["trees"])]
    plan = plan_for(monkeypatch, problems, {"tree-medium", "dp-locked"},
                    [attempt("dp0"), attempt("dp1"), attempt("tree-intro")])
    selected = plan.daily_session()
    assert {p.id for p in selected} == {"dp2", "dp3", "tree-medium", "interval-intro"}
    assert sum(plan._credits(p) for p in selected) == 5
    assert all(not plan.blockers(p) for p in selected)


def test_dp_shortage_returns_unused_credits_and_does_not_bypass_mastery(monkeypatch):
    problems = [problem("dp0", 3, ["dynamic-programming"]),
                problem("dp-medium", 4, ["dynamic-programming"]),
                *[problem(f"normal{i}", 3, ["trees"]) for i in range(5)]]
    targets = {p.id for p in problems}
    plan = plan_for(monkeypatch, problems, targets)
    selected = plan.daily_session()
    assert len(selected) == 5 and sum(p.id == "dp0" for p in selected) == 1
    plan = plan_for(monkeypatch, problems, targets, [attempt("dp0")])
    assert {p.id for p in plan.daily_session()} == {f"normal{i}" for i in range(5)}


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


@pytest.mark.parametrize("use_daily_session", [False, True])
def test_published_curriculum_can_reach_all_targets(use_daily_session):
    catalog = get_catalog().metadata
    attempts = []
    seen = set()
    for day in range(200):
        plan = InterviewPlan(catalog, attempts, [], NOW + timedelta(days=day), str(day))
        if not plan.remaining:
            break
        selection = plan.daily_session() if use_daily_session else choose_daily_session(plan.ordered)
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


def test_short_easy_day_adds_unsolved_diverse_practice(monkeypatch):
    targets = [problem(f"target{i}", 3, ["trees"]) for i in range(3)]
    extras = [problem("same-topic", 2, ["trees"]), problem("grid", 3, ["matrix"]),
              problem("lists", 3, ["linked-lists"]), problem("passed", 1, ["stacks"]),
              problem("locked", 1, ["graphs"], ["advanced"])]
    plan = plan_for(monkeypatch, targets + extras, {p.id for p in targets}, [attempt("passed")])
    selected = plan.daily_session()
    assert {p.id for p in selected[:3]} == {p.id for p in targets}
    assert {p.id for p in selected[3:]} == {"grid", "lists"}
    assert all(p.difficulty <= 3 for p in selected)
    assert plan.daily_session() == selected
    assert "Extra practice" in plan.reason("grid")
    assert len(plan.ordered) == 3  # Roadmap and interview progress are unchanged.


def test_easy_preparation_and_filler_do_not_starve_ready_medium_targets(monkeypatch):
    problems = [problem("intro", 3, ["trees"]),
                problem("medium1", 4, ["trees"]), problem("medium2", 5, ["trees"]),
                problem("blocked", 5, ["intervals"]),
                *[problem(f"prep{i}", 3, ["intervals"]) for i in range(8)]]
    targets = {"medium1", "medium2", "blocked"}
    plan = plan_for(monkeypatch, problems, targets, [attempt("intro")])
    assert plan.ordered[0].id == "prep0"  # Reproduces the old all-Easy anchor.
    selected = plan.daily_session()
    assert {p.id for p in selected} == {"medium1", "medium2", "prep0"}
    assert all(not plan.blockers(p) for p in selected)
    assert plan.daily_session() == selected


def test_ready_easy_interview_targets_still_precede_mediums(monkeypatch):
    problems = [problem("intro", 3, ["trees"]), problem("easy-target", 3, ["trees"]),
                problem("medium-target", 5, ["trees"]),
                *[problem(f"practice{i}", 3, ["trees"]) for i in range(5)]]
    plan = plan_for(monkeypatch, problems, {"easy-target", "medium-target"}, [attempt("intro")])
    selected = plan.daily_session()
    assert selected[0].id == "easy-target"
    assert len(selected) == 5 and all(p.difficulty <= 3 for p in selected)


def test_preparation_remains_primary_when_no_interview_target_is_ready(monkeypatch):
    problems = [problem("blocked", 5, ["intervals"]),
                *[problem(f"prep{i}", 3, ["intervals"]) for i in range(6)]]
    plan = plan_for(monkeypatch, problems, {"blocked"})
    assert not plan.ready_targets
    assert len(plan.daily_session()) == 5
    assert all(p.difficulty <= 3 and not plan.blockers(p) for p in plan.daily_session())


def test_ready_hard_target_is_not_starved_by_other_topic_preparation(monkeypatch):
    problems = [problem("intro", 3, ["trees"]), problem("medium1", 4, ["trees"]),
                problem("medium2", 5, ["trees"]), problem("hard", 8, ["trees"]),
                problem("blocked", 5, ["intervals"]), problem("prep", 3, ["intervals"])]
    plan = plan_for(monkeypatch, problems, {"hard", "blocked"},
                    [attempt("intro"), attempt("medium1"), attempt("medium2")])
    assert [p.id for p in plan.daily_session()] == ["hard"]


def test_short_easy_day_uses_only_unlocked_medium_when_easy_pool_exhausted(monkeypatch):
    targets = [problem(f"target{i}", 3, ["trees"]) for i in range(3)]
    extras = [problem("intro", 2, ["arrays"]), problem("ready", 4, ["arrays"]),
              problem("unseen", 4, ["trees"]),
              problem("prerequisite-locked", 4, ["arrays"], ["graphs"]),
              problem("hard", 8, ["arrays"])]
    plan = plan_for(monkeypatch, targets + extras, {p.id for p in targets}, [attempt("intro")])
    selected = plan.daily_session()
    assert {p.id for p in selected} == {p.id for p in targets} | {"ready"}
    assert sum(1 if p.difficulty <= 3 else 2 for p in selected) == 5
    assert all(not plan.blockers(p) for p in selected)


def test_easy_shortage_does_not_force_locked_work_or_continue_finished_path(monkeypatch):
    targets = [problem(f"target{i}", 3, ["trees"]) for i in range(3)]
    extras = [problem("locked", 4, ["trees"])]
    plan = plan_for(monkeypatch, targets + extras, {p.id for p in targets})
    assert len(plan.daily_session()) == 3
    finished = plan_for(monkeypatch, targets + extras, {p.id for p in targets},
                        [attempt(p.id) for p in targets])
    assert finished.daily_session() == []


@pytest.mark.parametrize("dp_focus", [False, True])
def test_dashboard_persists_topped_up_day_without_refilling(monkeypatch, dp_focus):
    import importlib
    app_module = importlib.import_module("code_practice.app")
    base = get_catalog()["pair-sum-indices"]
    catalog = {f"practice-{i}": base.model_copy(update={
        "id": f"practice-{i}", "difficulty": 3, "topics": [f"topic-{i}"],
        "prerequisites": [],
    }) for i in range(7)}
    if dp_focus:
        for i in range(2):
            catalog[f"practice-{i}"].topics = ["dynamic-programming"]
    targets = {f"practice-{i}" for i in range(3)}
    monkeypatch.setattr(interview_plan, "study_list_badges", lambda key: [{}] if key in targets else [])
    monkeypatch.setattr(app_module, "get_catalog", lambda: SimpleNamespace(metadata=catalog))
    with TestClient(app) as client:
        first = client.get("/api/dashboard").json()
        ids = [p["id"] for p in first["recommendations"]]
        assert first["dailyAssignedCount"] == 5
        assert set(ids[:3]) == targets
        if dp_focus:
            assert set(ids[:2]) == {"practice-0", "practice-1"}
            assert all("Daily DP focus" in p["preparationReason"] for p in first["recommendations"][:2])
        assert all(p["preparationReason"] for p in first["recommendations"][3:])
        assert client.get("/api/dashboard").json()["recommendations"] == first["recommendations"]
        for key in ids:
            database.save_attempt(AttemptCreate(
                problem_id=key, problem_version=1, source_code="solution",
                result="accepted", runtime_ms=1, tests_passed=12, tests_total=12,
            ))
    with TestClient(app) as client:
        finished = client.get("/api/dashboard").json()
        assert finished["dailyAssignedCount"] == 5
        assert finished["dailyComplete"]
        assert finished["recommendations"] == []


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
