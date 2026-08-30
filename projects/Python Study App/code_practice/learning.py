from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Iterable

from .schemas import Attempt, ProblemDefinition


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

