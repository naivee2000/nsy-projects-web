from datetime import datetime, timedelta, timezone

from code_practice.catalog import get_catalog
from code_practice.content import PROBLEMS
from code_practice.learning import (
    REVIEW_INTERVALS,
    attempt_score,
    choose_daily_session,
    is_graph_traversal_problem,
    is_grid_recursion_problem,
    is_linked_list_problem,
    is_review_focus_problem,
    is_tree_problem,
    next_review,
    prioritized_review_problems,
    review_focus_boost,
    review_priority_score,
    topic_mastery,
    topic_progression_met,
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


def test_medium_topic_requires_a_passed_easy_introduction():
    catalog = get_catalog()
    medium_interval = catalog["leetcode-57"]
    easy_interval = catalog["leetcode-1450"]
    introductory_topics = {
        "-".join(topic.lower().replace("_", " ").split())
        for problem in catalog.values()
        if problem.difficulty <= 3
        for topic in problem.topics
    }

    assert not topic_progression_met(medium_interval, introductory_topics, set())
    assert topic_progression_met(
        medium_interval,
        introductory_topics,
        {"-".join(topic.lower().replace("_", " ").split()) for topic in easy_interval.topics},
    )


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
    assert len(balanced) == 5


def test_review_priority_ignores_hint_usage_but_boosts_personal_weak_topics():
    now = datetime(2026, 9, 8, 12, tzinfo=timezone.utc)
    catalog = {problem.id: problem for problem in PROBLEMS}
    plain = catalog["pair-sum-indices"]
    linked = catalog["reverse-linked-list"]
    binary = catalog["binary-search-index"]
    recursive = catalog["recursive-digit-sum"]
    grid_recursive = catalog["flood-fill-region"]
    dfs_grid = catalog["largest-land-region"]
    tree = catalog["tree-max-depth"]
    graph = catalog["directed-cycle-check"]

    assert review_focus_boost(plain) == 0
    assert review_focus_boost(linked) == 60
    assert review_focus_boost(binary) == 60
    assert review_focus_boost(recursive) == 50
    assert review_focus_boost(grid_recursive) == 130
    assert review_focus_boost(dfs_grid) == 80
    assert review_focus_boost(tree) == 110
    assert review_focus_boost(graph) == 110

    review = ReviewState(problem_id=plain.id, interval_index=0, due_at=now, latest_result="accepted")
    no_hint = make_attempt(plain.id, hint=0).model_copy(update={"created_at": now})
    editorial = make_attempt(plain.id, hint=4).model_copy(update={"created_at": now})
    assert review_priority_score(plain, [no_hint], review, now) == review_priority_score(
        plain, [editorial], review, now
    )


def test_review_set_uses_three_category_slots_with_two_daily_random_slots():
    now = datetime(2026, 9, 8, 12, tzinfo=timezone.utc)
    catalog = {problem.id: problem for problem in PROBLEMS}
    chosen = [
        catalog["largest-land-region"],
        catalog["tree-max-depth"],
        catalog["linked-odd-even-order"],
        catalog["directed-cycle-check"],
        catalog["undirected-component-count"],
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
        selection_seed="2026-09-08",
    )

    assert is_grid_recursion_problem(ranked[0])
    assert is_tree_problem(ranked[1])
    assert is_linked_list_problem(ranked[2]) or is_graph_traversal_problem(ranked[2])
    assert all(not is_review_focus_problem(problem) for problem in ranked[3:5])
    assert ranked == prioritized_review_problems(
        catalog,
        attempts,
        reviews,
        {problem.id for problem in chosen},
        now,
        selection_seed="2026-09-08",
    )

    tails = {
        tuple(
            problem.id
            for problem in prioritized_review_problems(
                catalog,
                attempts,
                reviews,
                {problem.id for problem in chosen},
                now,
                selection_seed=f"2026-09-{day:02d}",
            )[3:]
        )
        for day in range(8, 15)
    }
    assert len(tails) > 1


def test_review_set_uses_fresh_category_alternatives_before_recent_repeats():
    now = datetime(2026, 9, 30, 12, tzinfo=timezone.utc)
    catalog = {problem.id: problem for problem in PROBLEMS}
    chosen = [
        catalog["largest-land-region"],
        catalog["flood-fill-region"],
        catalog["tree-max-depth"],
        catalog["recursive-leaf-count"],
        catalog["linked-odd-even-order"],
        catalog["reverse-linked-list"],
        catalog["minimum-window"],
        catalog["merge-intervals"],
        catalog["pair-sum-indices"],
    ]
    attempts = [make_attempt(problem.id, attempt_id=300 + index) for index, problem in enumerate(chosen)]
    reviews = [
        ReviewState(problem_id=problem.id, interval_index=0, due_at=now, latest_result="accepted")
        for problem in chosen
    ]
    recent_ids = {
        "largest-land-region",
        "tree-max-depth",
        "linked-odd-even-order",
        "minimum-window",
    }

    selected = prioritized_review_problems(
        catalog,
        attempts,
        reviews,
        {problem.id for problem in chosen},
        now,
        selection_seed="2026-09-30",
        recently_assigned_ids=recent_ids,
    )

    assert len(selected) == 5
    assert recent_ids.isdisjoint(problem.id for problem in selected)
    assert selected[0].id == "flood-fill-region"
    assert selected[1].id == "recursive-leaf-count"
    assert selected[2].id == "reverse-linked-list"

    fallback = prioritized_review_problems(
        catalog,
        attempts,
        reviews,
        {problem.id for problem in chosen},
        now,
        selection_seed="2026-09-30",
        recently_assigned_ids={problem.id for problem in chosen},
    )
    assert len(fallback) == 5
    assert len({problem.id for problem in fallback}) == 5


def test_review_set_falls_back_when_focus_categories_are_missing():
    now = datetime(2026, 9, 8, 12, tzinfo=timezone.utc)
    catalog = {problem.id: problem for problem in PROBLEMS}
    chosen = [
        catalog["largest-land-region"],
        catalog["linked-odd-even-order"],
        catalog["rotated-array-search"],
        catalog["recursive-digit-sum"],
        catalog["binary-search-index"],
        catalog["merge-intervals"],
    ]
    attempts = [make_attempt(problem.id, attempt_id=200 + index) for index, problem in enumerate(chosen)]
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
        selection_seed="2026-09-08",
    )

    assert len(ranked) == 5
    assert is_grid_recursion_problem(ranked[0])
    assert any(is_linked_list_problem(problem) for problem in ranked[:3])
    assert len({problem.id for problem in ranked}) == 5


def test_review_set_excludes_a_previously_passed_problem_after_latest_failure():
    now = datetime(2026, 9, 21, 12, tzinfo=timezone.utc)
    catalog = {problem.id: problem for problem in PROBLEMS}
    chosen = [
        catalog["largest-land-region"],
        catalog["tree-max-depth"],
        catalog["linked-odd-even-order"],
        catalog["minimum-window"],
        catalog["merge-intervals"],
        catalog["pair-sum-indices"],
    ]
    failed = chosen[0]
    attempts = [
        make_attempt(problem.id, attempt_id=300 + index).model_copy(
            update={"created_at": now - timedelta(days=2)}
        )
        for index, problem in enumerate(chosen)
    ]
    attempts.append(
        make_attempt(failed.id, result="timeout", attempt_id=400).model_copy(
            update={"created_at": now - timedelta(hours=1)}
        )
    )
    reviews = [
        ReviewState(
            problem_id=problem.id,
            interval_index=0,
            due_at=now,
            latest_result="timeout" if problem.id == failed.id else "accepted",
        )
        for problem in chosen
    ]

    ranked = prioritized_review_problems(
        catalog,
        attempts,
        reviews,
        {problem.id for problem in chosen},
        now,
        selection_seed="2026-09-21",
    )

    assert failed.id not in {problem.id for problem in ranked}
    assert len(ranked) == 5
