from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .catalog import get_catalog, problem_summary, public_problem
from .coach import build_coaching
from .codex_coach import codex_status, request_codex_coaching
from .database import (
    get_draft,
    highest_hint,
    initialize_database,
    list_attempts,
    list_review_states,
    record_hint,
    save_attempt,
    save_draft,
)
from .learning import prerequisites_met, topic_mastery
from .schemas import AttemptCreate, ProblemDefinition


APP_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIST = APP_ROOT / "frontend" / "dist"

@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Code Practice Lab", version="0.1.0", lifespan=lifespan)


class DraftPayload(BaseModel):
    source_code: str = Field(max_length=200_000)


class CoachCase(BaseModel):
    id: str
    passed: bool
    actual: Any | None = None
    expected: Any | None = None
    error: str | None = None
    visible: bool = False
    arguments: list[Any] | None = None


class CoachPayload(BaseModel):
    source_code: str = Field(max_length=200_000)
    status: str
    message: str = Field(max_length=4_000)
    cases: list[CoachCase] = Field(default_factory=list, max_length=100)
    step: int = Field(default=1, ge=1, le=3)


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "mode": "local-only",
        "problemCount": len(get_catalog()),
        "time": datetime.now(timezone.utc).isoformat(),
    }


def _solved_ids() -> set[str]:
    return {attempt.problem_id for attempt in list_attempts() if attempt.result == "accepted"}


@app.get("/api/problems")
def problems(
    topic: str | None = None,
    difficulty_min: int = Query(default=1, ge=1, le=10),
    difficulty_max: int = Query(default=10, ge=1, le=10),
    search: str | None = None,
) -> list[dict[str, Any]]:
    catalog = get_catalog()
    solved = _solved_ids()
    query = (search or "").strip().lower()
    selected = []
    for problem in catalog.values():
        if problem.status != "approved" or not difficulty_min <= problem.difficulty <= difficulty_max:
            continue
        if topic and topic not in problem.topics:
            continue
        if query and query not in f"{problem.title} {problem.summary} {' '.join(problem.topics)}".lower():
            continue
        selected.append(problem_summary(problem, solved))
    return sorted(selected, key=lambda item: (item["difficulty"], item["title"]))


@app.get("/api/problems/{problem_id}")
def problem_detail(problem_id: str) -> dict[str, Any]:
    problem = get_catalog().get(problem_id)
    if not problem or problem.status != "approved":
        raise HTTPException(404, "Problem not found")
    payload = public_problem(problem)
    payload["solved"] = problem_id in _solved_ids()
    payload["savedDraft"] = get_draft(problem_id) or problem.starter_code
    revealed = highest_hint(problem_id)
    payload["revealedHintLevel"] = revealed
    payload["revealedHints"] = [
        {
            "level": level,
            "label": ["Concept", "Strategy", "Pseudocode", "Editorial"][level - 1],
            "content": problem.editorial if level == 4 else problem.hints[level - 1],
        }
        for level in range(1, revealed + 1)
    ]
    return payload


@app.post("/api/problems/{problem_id}/submission-package")
def submission_package(problem_id: str) -> dict[str, Any]:
    problem = get_catalog().get(problem_id)
    if not problem or problem.status != "approved":
        raise HTTPException(404, "Problem not found")
    return {
        "problemId": problem.id,
        "version": problem.version,
        "signature": problem.signature.model_dump(mode="json"),
        "tests": [test.model_dump(mode="json") for test in problem.tests if not test.visible],
        "timeoutMs": 3000,
    }


@app.post("/api/problems/{problem_id}/coach")
def coach(problem_id: str, payload: CoachPayload) -> dict[str, Any]:
    problem = get_catalog().get(problem_id)
    if not problem or problem.status != "approved":
        raise HTTPException(404, "Problem not found")
    if payload.status == "accepted":
        raise HTTPException(409, "Coaching is only generated for an unresolved run")
    # build_coaching parses source text for structure but never compiles or executes it.
    reply = build_coaching(
        problem,
        payload.source_code,
        payload.status,
        payload.message,
        [case.model_dump(mode="json") for case in payload.cases],
        payload.step,
    )
    return reply.as_dict()


@app.get("/api/coach/codex-status")
def coach_codex_status() -> dict[str, Any]:
    return codex_status()


@app.post("/api/problems/{problem_id}/codex-coach")
def codex_coach(problem_id: str, payload: CoachPayload) -> dict[str, Any]:
    problem = get_catalog().get(problem_id)
    if not problem or problem.status != "approved":
        raise HTTPException(404, "Problem not found")
    if payload.status == "accepted":
        raise HTTPException(409, "Coaching is only generated for an unresolved run")
    return request_codex_coaching(
        problem,
        payload.source_code,
        payload.status,
        payload.message,
        [case.model_dump(mode="json") for case in payload.cases],
    )


@app.post("/api/attempts")
def attempts(payload: AttemptCreate) -> dict[str, Any]:
    problem = get_catalog().get(payload.problem_id)
    if not problem or problem.status != "approved":
        raise HTTPException(404, "Problem not found")
    if payload.problem_version != problem.version:
        raise HTTPException(409, "Problem version changed; reload before submitting")
    return save_attempt(payload).model_dump(mode="json")


@app.put("/api/problems/{problem_id}/draft")
def draft(problem_id: str, payload: DraftPayload) -> dict[str, bool]:
    if problem_id not in get_catalog():
        raise HTTPException(404, "Problem not found")
    save_draft(problem_id, payload.source_code)
    return {"saved": True}


@app.post("/api/problems/{problem_id}/hints/{level}")
def reveal_hint(problem_id: str, level: int) -> dict[str, Any]:
    problem = get_catalog().get(problem_id)
    if not problem or problem.status != "approved":
        raise HTTPException(404, "Problem not found")
    if not 1 <= level <= 4:
        raise HTTPException(422, "Hint level must be from 1 through 4")
    current = highest_hint(problem_id)
    if level > current + 1:
        raise HTTPException(409, "Hints must be revealed in order")
    record_hint(problem_id, level)
    return {
        "level": level,
        "content": problem.editorial if level == 4 else problem.hints[level - 1],
        "label": ["Concept", "Strategy", "Pseudocode", "Editorial"][level - 1],
    }


def _progress_payload() -> dict[str, Any]:
    attempts = list_attempts()
    catalog = get_catalog()
    mastery = topic_mastery(attempts, catalog)
    reviews = list_review_states()
    solved = {attempt.problem_id for attempt in attempts if attempt.result == "accepted"}
    return {
        "attempts": [attempt.model_dump(mode="json") for attempt in attempts[:50]],
        "reviewStates": [review.model_dump(mode="json") for review in reviews],
        "mastery": mastery,
        "solvedCount": len(solved),
        "totalProblems": len(catalog),
    }


@app.get("/api/progress")
def progress() -> dict[str, Any]:
    return _progress_payload()


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    catalog = get_catalog()
    attempts = list_attempts()
    mastery = topic_mastery(attempts, catalog)
    reviews = list_review_states()
    solved = {attempt.problem_id for attempt in attempts if attempt.result == "accepted"}
    now = datetime.now(timezone.utc)
    due_ids = [
        review.problem_id
        for review in reviews
        if review.due_at <= now and review.problem_id in catalog and review.problem_id not in solved
    ]
    recommendations: list[ProblemDefinition] = []

    for problem_id in due_ids:
        if len(recommendations) == 3:
            break
        recommendations.append(catalog[problem_id])

    weak_topics = [topic for topic, _score in sorted(mastery.items(), key=lambda item: item[1])]
    for topic in weak_topics:
        candidate = next(
            (
                problem for problem in catalog.values()
                if problem.id not in solved
                and topic in problem.topics
                and problem not in recommendations
                and prerequisites_met(problem, mastery)
            ),
            None,
        )
        if candidate and len(recommendations) < 3:
            recommendations.append(candidate)
            break

    for problem in sorted(catalog.values(), key=lambda item: item.difficulty):
        if len(recommendations) == 3:
            break
        if problem.id not in solved and problem.difficulty <= 7 and problem not in recommendations and prerequisites_met(problem, mastery):
            recommendations.append(problem)

    challenge = next(
        (
            problem for problem in sorted(catalog.values(), key=lambda item: item.difficulty)
            if problem.id not in solved and problem.difficulty >= 8 and prerequisites_met(problem, mastery)
        ),
        None,
    )
    return {
        "recommendations": [problem_summary(problem, solved) for problem in recommendations[:3]],
        "weeklyChallenge": problem_summary(challenge, solved) if challenge else None,
        "mastery": mastery,
        "solvedCount": len(solved),
        "totalProblems": len(catalog),
        "attemptCount": len(attempts),
    }


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")
    if (FRONTEND_DIST / "pyodide").exists():
        app.mount("/pyodide", StaticFiles(directory=FRONTEND_DIST / "pyodide"), name="pyodide")

    @app.get("/{full_path:path}")
    def frontend(full_path: str) -> FileResponse:
        candidate = FRONTEND_DIST / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
