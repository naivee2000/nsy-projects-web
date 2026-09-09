from datetime import datetime, timedelta, timezone

from code_practice.content import PROBLEMS
from code_practice.learning import (
    REVIEW_INTERVALS,
    attempt_score,
    choose_daily_session,
    next_review,
    prioritized_review_problems,
    review_focus_boost,
    review_priority_score,
    topic_mastery,
)
from code_practice.schemas import Attempt, ReviewState


def make_attempt(problem_id="pair-sum-indices", result="accepted", hint=0, attempt_id=1):
    return Attempt(
        id=attempt_id,
        problem_id=problem_id,
        problem_version=1,
        source_code="pass",
        result=result,
        runtime_ms=1,
        tests_passed=1 if result == "accepted" else 0,
        tests_total=1,
        elapsed_study_seconds=10,
        hint_level=hint,
        created_at=datetime.now(timezone.utc),
    )


def test_hint_scores_are_exact():
    assert [attempt_score(make_attempt(hint=level)) for level in range(5)] == [1.0, 0.8, 0.6, 0.4, 0.2]
    assert attempt_score(make_attempt(result="wrong_answer")) == 0


def test_topic_mastery_uses_latest_ten(get_catalog_fixture=None):
    from code_practice.content import PROBLEMS
    catalog = {problem.id: problem for problem in PROBLEMS}
    attempts = [make_attempt(hint=index % 5, attempt_id=index) for index in range(12)]
    mastery = topic_mastery(attempts, catalog)
    assert mastery["arrays"] == 60.0
    assert mastery["hash-maps"] == 60.0


def test_review_intervals_advance_and_failure_resets():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    index = None
    for expected_index, days in enumerate(REVIEW_INTERVALS):
        index, due = next_review(index, True, now)
        assert index == expected_index
        assert (due - now).days == days
    index, due = next_review(5, False, now)
    assert index == 0
    assert (due - now).days == 1


def test_daily_session_uses_workload_based_difficulty_mixes():
    easy = [problem for problem in PROBLEMS if problem.difficulty <= 3][:6]
    medium = [problem for problem in PROBLEMS if 4 <= problem.difficulty <= 7][:4]
    hard = [problem for problem in PROBLEMS if problem.difficulty >= 8][:2]

    assert choose_daily_session(easy) == easy[:5]
    assert choose_daily_session([*medium[:3], easy[0]]) == [medium[0], medium[1], easy[0]]
    assert choose_daily_session(medium[:4]) == medium[:3]
    assert choose_daily_session([*hard, medium[0], easy[0]]) == [hard[0], medium[0]]


def test_review_priority_prefers_harder_and_observed_struggle():
    now = datetime(2026, 9, 7, 12, tzinfo=timezone.utc)
    catalog = {problem.id: problem for problem in PROBLEMS}
    easy = catalog["pair-sum-indices"]
    medium = catalog["merge-intervals"]
    hard = catalog["minimum-window"]

    attempts = [
        make_attempt(easy.id, attempt_id=1),
        make_attempt(medium.id, attempt_id=2),
        make_attempt(hard.id, attempt_id=3),
    ]
    attempts = [attempt.model_copy(update={"created_at": now - timedelta(days=5)}) for attempt in attempts]
    reviews = [
        ReviewState(
            problem_id=problem.id,
            interval_index=0,
            due_at=now - timedelta(days=1),
            latest_result="accepted",
        )
        for problem in (easy, medium, hard)
    ]
    ranked = prioritized_review_problems(catalog, attempts, reviews, {easy.id, medium.id, hard.id}, now)
    assert [problem.id for problem in ranked] == [hard.id, medium.id, easy.id]

    equally_difficult = [problem for problem in PROBLEMS if problem.difficulty == 5][:2]
    steady, struggled = equally_difficult
    steady_history = [make_attempt(steady.id, attempt_id=10).model_copy(update={"created_at": now - timedelta(days=5)})]
    struggled_history = [
        make_attempt(struggled.id, attempt_id=11).model_copy(update={"created_at": now - timedelta(days=5)}),
        make_attempt(struggled.id, result="wrong_answer", hint=3, attempt_id=12).model_copy(
            update={"created_at": now - timedelta(days=1), "elapsed_study_seconds": struggled.estimated_minutes * 120}
        ),
    ]
    steady_review = ReviewState(problem_id=steady.id, interval_index=0, due_at=now, latest_result="accepted")
    struggled_review = ReviewState(problem_id=struggled.id, interval_index=0, due_at=now, latest_result="wrong_answer")
    assert review_priority_score(struggled, struggled_history, struggled_review, now) > review_priority_score(
        steady, steady_history, steady_review, now
    )

    challenging = [problem for problem in PROBLEMS if 4 <= problem.difficulty <= 7][:4]
    mixed = [easy, *challenging]
    mixed_attempts = [
        make_attempt(problem.id, attempt_id=20 + index).model_copy(update={"created_at": now - timedelta(days=5)})
        for index, problem in enumerate(mixed)
    ]
    mixed_reviews = [
        ReviewState(
            problem_id=problem.id,
            interval_index=0,
            due_at=now - timedelta(days=100) if problem.id == easy.id else now + timedelta(days=1),
            latest_result="accepted",
        )
        for problem in mixed
    ]
    balanced = prioritized_review_problems(
        catalog,
        mixed_attempts,
        mixed_reviews,
        {problem.id for problem in mixed},
        now,
    )
    assert all(problem.difficulty >= 4 for problem in balanced[:4])


def test_review_priority_ignores_hint_usage_but_boosts_personal_weak_topics():
    now = datetime(2026, 9, 8, 12, tzinfo=timezone.utc)
    catalog = {problem.id: problem for problem in PROBLEMS}
    plain = catalog["pair-sum-indices"]
    linked = catalog["reverse-linked-list"]
    binary = catalog["binary-search-index"]
    recursive = catalog["recursive-digit-sum"]
    grid_recursive = catalog["flood-fill-region"]
    dfs_grid = catalog["largest-land-region"]

    assert review_focus_boost(plain) == 0
    assert review_focus_boost(linked) == 60
    assert review_focus_boost(binary) == 60
    assert review_focus_boost(recursive) == 50
    assert review_focus_boost(grid_recursive) == 130
    assert review_focus_boost(dfs_grid) == 80

    review = ReviewState(problem_id=plain.id, interval_index=0, due_at=now, latest_result="accepted")
    no_hint = make_attempt(plain.id, hint=0).model_copy(update={"created_at": now})
    editorial = make_attempt(plain.id, hint=4).model_copy(update={"created_at": now})
    assert review_priority_score(plain, [no_hint], review, now) == review_priority_score(
        plain, [editorial], review, now
    )


def test_review_set_reserves_weak_topic_and_grid_recursion_slots():
    now = datetime(2026, 9, 8, 12, tzinfo=timezone.utc)
    catalog = {problem.id: problem for problem in PROBLEMS}
    chosen = [
        catalog["largest-land-region"],
        catalog["linked-odd-even-order"],
        catalog["rotated-array-search"],
        catalog["minimum-window"],
        catalog["merge-intervals"],
        catalog["pair-sum-indices"],
    ]
    attempts = [
        make_attempt(problem.id, attempt_id=100 + index).model_copy(update={"created_at": now - timedelta(days=5)})
        for index, problem in enumerate(chosen)
    ]
    reviews = [
        ReviewState(problem_id=problem.id, interval_index=0, due_at=now, latest_result="accepted")
        for problem in chosen
    ]

    ranked = prioritized_review_problems(
        catalog,
        attempts,
        reviews,
        {problem.id for problem in chosen},
        now,
    )

    assert ranked[0].id == "largest-land-region"
    assert {problem.id for problem in ranked[:3]} >= {
        "largest-land-region",
        "linked-odd-even-order",
        "rotated-array-search",
    }
    assert all(problem.difficulty >= 4 for problem in ranked[:4])
