from datetime import datetime, timezone

from code_practice.learning import REVIEW_INTERVALS, attempt_score, next_review, topic_mastery
from code_practice.schemas import Attempt


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

