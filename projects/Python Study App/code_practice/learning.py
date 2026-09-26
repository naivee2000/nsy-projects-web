from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import random
from typing import Iterable

from .schemas import Attempt, ProblemDefinition, ReviewState


REVIEW_INTERVALS = (1, 3, 7, 14, 30, 60)
HINT_SCORES = {0: 1.0, 1: 0.8, 2: 0.6, 3: 0.4, 4: 0.2}

# Personal review preferences. These are intentionally separate from canonical
# difficulty: they change what this one-user app reviews, not how a problem is
# rated in the library.
REVIEW_FOCUS_WEIGHTS = {
    "linked-lists": 60.0,
    "recursion": 50.0,
    "binary-search": 60.0,
}
GRID_RECURSION_BONUS = 80.0
TREE_FOCUS_BONUS = 60.0
LINKED_LIST_FOCUS_BONUS = 60.0
GRAPH_TRAVERSAL_FOCUS_BONUS = 60.0


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


def normalized_topics(problem: ProblemDefinition) -> set[str]:
    return {"-".join(topic.lower().replace("_", " ").split()) for topic in problem.topics}


def topic_progression_met(
    problem: ProblemDefinition,
    introductory_topics: set[str],
    passed_introductory_topics: set[str],
) -> bool:
    """Keep new Medium/Hard work behind an Easy introduction when one exists."""
    if problem.difficulty <= 3:
        return True
    required_topics = normalized_topics(problem) & introductory_topics
    return required_topics <= passed_introductory_topics


def choose_daily_session(candidates: Iterable[ProblemDefinition]) -> list[ProblemDefinition]:
    """Build one workload-capped session from candidates in priority order."""
    ordered: list[ProblemDefinition] = []
    seen: set[str] = set()
    for problem in candidates:
        if problem.id not in seen:
            ordered.append(problem)
            seen.add(problem.id)
    if not ordered:
        return []

    anchor = ordered[0]
    easy = [problem for problem in ordered if problem.difficulty <= 3]
    medium = [problem for problem in ordered if 4 <= problem.difficulty <= 7]
    hard = [problem for problem in ordered if problem.difficulty >= 8]

    if anchor.difficulty >= 8:
        # A hard problem is the main workload. Pair it with no more than one
        # medium problem, and do not pad the day with extra easy work.
        return [hard[0], *medium[:1]]

    if anchor.difficulty >= 4:
        # Prefer two medium patterns plus one easy reinforcement. If there is
        # no easy work left, a third medium is the absolute daily maximum.
        if easy:
            return [*medium[:2], easy[0]]
        return medium[:3]

    return easy[:5]


def is_grid_recursion_problem(problem: ProblemDefinition) -> bool:
    """Include explicitly recursive grids and DFS grid/field traversal."""
    topics = normalized_topics(problem)
    return bool({"matrix", "matrices"} & topics) and bool(
        {"recursion", "depth-first-search", "dfs"} & topics
    )


def is_tree_problem(problem: ProblemDefinition) -> bool:
    topics = normalized_topics(problem)
    return bool(
        {
            "trees",
            "binary-trees",
            "binary-search-trees",
            "tree-dp",
            "tree-dynamic-programming",
            "subtree-sizes",
        }
        & topics
    )


def is_linked_list_problem(problem: ProblemDefinition) -> bool:
    return bool({"linked-list", "linked-lists"} & normalized_topics(problem))


def is_graph_traversal_problem(problem: ProblemDefinition) -> bool:
    topics = normalized_topics(problem)
    return not is_grid_recursion_problem(problem) and any("graph" in topic for topic in topics)


def is_review_focus_problem(problem: ProblemDefinition) -> bool:
    return (
        is_grid_recursion_problem(problem)
        or is_tree_problem(problem)
        or is_linked_list_problem(problem)
        or is_graph_traversal_problem(problem)
    )


def review_focus_boost(problem: ProblemDefinition) -> float:
    """Return the owner's personal weak-topic priority boost."""
    topics = normalized_topics(problem)
    boost = sum(weight for topic, weight in REVIEW_FOCUS_WEIGHTS.items() if topic in topics)
    if is_grid_recursion_problem(problem):
        boost += GRID_RECURSION_BONUS
    if is_tree_problem(problem):
        boost += TREE_FOCUS_BONUS
    if is_linked_list_problem(problem) and "linked-lists" not in topics:
        boost += LINKED_LIST_FOCUS_BONUS
    if is_graph_traversal_problem(problem):
        boost += GRAPH_TRAVERSAL_FOCUS_BONUS
    return boost


def _stable_review_rng(seed: str, label: str) -> random.Random:
    digest = hashlib.sha256(f"{seed}:{label}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


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
        + review_focus_boost(problem)
        + min(review_failures, 3) * 30.0
        + study_load * 15.0
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
    selection_seed: str | None = None,
) -> list[ProblemDefinition]:
    """Choose three focused reviews plus two daily-stable random reviews."""
    now = now or datetime.now(timezone.utc)
    seed = selection_seed or now.date().isoformat()
    histories: dict[str, list[Attempt]] = defaultdict(list)
    for attempt in attempts:
        histories[attempt.problem_id].append(attempt)
    states = {review.problem_id: review for review in reviews}
    candidates = [
        catalog[problem_id]
        for problem_id in solved_ids
        if problem_id in catalog
        and problem_id in states
        and states[problem_id].latest_result == "accepted"
    ]
    ranked = sorted(
        candidates,
        key=lambda problem: (
            -review_priority_score(problem, histories[problem.id], states.get(problem.id), now),
            -problem.difficulty,
            problem.id,
        ),
    )
    # Reserve one slot each for matrix/grid recursion, trees, and either linked
    # lists or directed/undirected graph traversal. The structure/graph lane
    # alternates deterministically by day when both pools are available.
    focus_limit = min(3, limit)

    selected: list[ProblemDefinition] = []
    selected_ids: set[str] = set()

    def add(problem: ProblemDefinition) -> None:
        if problem.id not in selected_ids and len(selected) < limit:
            selected.append(problem)
            selected_ids.add(problem.id)

    grid = [problem for problem in ranked if is_grid_recursion_problem(problem)]
    trees = [problem for problem in ranked if is_tree_problem(problem)]
    linked = [problem for problem in ranked if is_linked_list_problem(problem)]
    graph = [problem for problem in ranked if is_graph_traversal_problem(problem)]

    for pool in (grid, trees):
        if pool and len(selected) < focus_limit:
            add(pool[0])

    structure_pools = [linked, graph]
    _stable_review_rng(seed, "structure-lane").shuffle(structure_pools)
    for pool in structure_pools:
        if pool and len(selected) < focus_limit:
            add(pool[0])
            break

    # If a requested focus category is not yet represented in completed work,
    # retain the highest-priority review candidates rather than returning fewer
    # than three core reviews.
    for problem in ranked:
        if len(selected) >= focus_limit:
            break
        add(problem)

    remaining = [problem for problem in ranked if problem.id not in selected_ids]
    general = [problem for problem in remaining if not is_review_focus_problem(problem)]
    random_needed = max(0, limit - len(selected))
    random_pool = general if len(general) >= random_needed else remaining
    _stable_review_rng(seed, "random-slots").shuffle(random_pool)
    for problem in random_pool:
        add(problem)

    for problem in ranked:
        add(problem)
    return selected[:limit]
