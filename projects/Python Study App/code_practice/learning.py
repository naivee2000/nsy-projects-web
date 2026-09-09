from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Iterable

from .schemas import Attempt, ProblemDefinition, ReviewState


REVIEW_INTERVALS = (1, 3, 7, 14, 30, 60)
HINT_SCORES = {0: 1.0, 1: 0.8, 2: 0.6, 3: 0.4, 4: 0.2}


def attempt_score(attempt: Attempt) -> float:
    if attempt.result != "accepted":
        return 0.0
    return HINT_SCORES[attempt.hint_level]


def topic_mastery(attempts: Iterable[Attempt], catalog: dict[str, ProblemDefinition]) -> dict[str, float]:
    by_topic: dict[str, list[Attempt]] = defaultdict(list)
    for attempt in sorted(attempts, key=lambda item: item.created_at, reverse=True):
        problem = catalog.get(attempt.problem_id)
        if not problem:
            continue
        for topic in problem.topics:
            if len(by_topic[topic]) < 10:
                by_topic[topic].append(attempt)
    return {
        topic: round(sum(attempt_score(item) for item in recent) / len(recent) * 100, 1)
        for topic, recent in by_topic.items()
        if recent
    }


def next_review(current_index: int | None, accepted: bool, now: datetime | None = None) -> tuple[int, datetime]:
    now = now or datetime.now(timezone.utc)
    if accepted:
        index = 0 if current_index is None else min(current_index + 1, len(REVIEW_INTERVALS) - 1)
    else:
        index = 0
    return index, now + timedelta(days=REVIEW_INTERVALS[index])


def prerequisites_met(problem: ProblemDefinition, mastery: dict[str, float]) -> bool:
    return all(mastery.get(topic, 0.0) >= 70.0 for topic in problem.prerequisites)


def review_priority_score(
    problem: ProblemDefinition,
    attempts: Iterable[Attempt],
    review_state: ReviewState | None,
    now: datetime | None = None,
) -> float:
    """Score review value from difficulty, due date, and observed struggle."""
    now = now or datetime.now(timezone.utc)
    history = sorted(
        (attempt for attempt in attempts if attempt.problem_id == problem.id),
        key=lambda attempt: attempt.created_at,
    )
    accepted_at = next(
        (attempt.created_at for attempt in history if attempt.result == "accepted"),
        None,
    )
    review_failures = sum(
        attempt.result != "accepted" and accepted_at is not None and attempt.created_at > accepted_at
        for attempt in history
    )
    total_study_seconds = sum(attempt.elapsed_study_seconds for attempt in history)
    expected_seconds = max(1, problem.estimated_minutes * 60)
    study_load = min(total_study_seconds / expected_seconds, 3.0)
    highest_hint = max((attempt.hint_level for attempt in history), default=0)
    latest_failed = bool(history and history[-1].result != "accepted")

    due_score = 0.0
    if review_state:
        seconds_from_due = (now - review_state.due_at).total_seconds()
        if seconds_from_due >= 0:
            due_score = 120.0 + min(seconds_from_due / 86_400, 60.0)
        else:
            days_until_due = -seconds_from_due / 86_400
            due_score = -min(days_until_due * 25.0, 150.0)

    return round(
        problem.difficulty * 20.0
        + min(review_failures, 3) * 30.0
        + study_load * 15.0
        + highest_hint * 8.0
        + (25.0 if latest_failed else 0.0)
        + due_score,
        3,
    )


def prioritized_review_problems(
    catalog: dict[str, ProblemDefinition],
    attempts: Iterable[Attempt],
    reviews: Iterable[ReviewState],
    solved_ids: set[str],
    now: datetime | None = None,
    limit: int = 5,
) -> list[ProblemDefinition]:
    """Return a stable daily review order with difficult/struggling work first."""
    now = now or datetime.now(timezone.utc)
    attempt_list = list(attempts)
    states = {review.problem_id: review for review in reviews}
    candidates = [catalog[problem_id] for problem_id in solved_ids if problem_id in catalog]
    ranked = sorted(
        candidates,
        key=lambda problem: (
            -review_priority_score(problem, attempt_list, states.get(problem.id), now),
            -problem.difficulty,
            problem.id,
        ),
    )
    # Reserve most of a full review set for medium/advanced work when enough has
    # been completed. The final slot remains flexible for a highly due or
    # historically troublesome Easy problem.
    challenging = [problem for problem in ranked if problem.difficulty >= 4]
    selected = challenging[:min(4, limit)]
    selected_ids = {problem.id for problem in selected}
    selected.extend(problem for problem in ranked if problem.id not in selected_ids)
    return selected[:limit]
