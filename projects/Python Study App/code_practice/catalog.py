from __future__ import annotations

from functools import lru_cache
from typing import Any

from .content import PROBLEMS
from .database import approved_variant_rows
from .schemas import ProblemDefinition


@lru_cache(maxsize=1)
def get_catalog() -> dict[str, ProblemDefinition]:
    problems = {problem.id: problem for problem in PROBLEMS}
    for row in approved_variant_rows():
        problem = ProblemDefinition.model_validate(row)
        if problem.status == "approved":
            problems[problem.id] = problem
    return problems


def refresh_catalog() -> None:
    get_catalog.cache_clear()


def problem_summary(problem: ProblemDefinition, solved_ids: set[str] | None = None) -> dict[str, Any]:
    solved_ids = solved_ids or set()
    return {
        "id": problem.id,
        "version": problem.version,
        "title": problem.title,
        "summary": problem.summary,
        "topics": problem.topics,
        "prerequisites": problem.prerequisites,
        "difficulty": problem.difficulty,
        "estimatedMinutes": problem.estimated_minutes,
        "solved": problem.id in solved_ids,
    }


def public_problem(problem: ProblemDefinition) -> dict[str, Any]:
    payload = problem.model_dump(mode="json")
    payload["difficulty"] = problem.difficulty
    payload["tests"] = [test.model_dump(mode="json") for test in problem.tests if test.visible]
    payload.pop("reference_solution", None)
    payload.pop("brute_force_solution", None)
    payload.pop("known_wrong_solutions", None)
    payload["hints"] = []
    payload["editorial"] = ""
    return payload
