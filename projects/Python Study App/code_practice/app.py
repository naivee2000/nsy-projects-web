from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .catalog import get_catalog, problem_summary, public_problem
from .coach import build_coaching
from .codex_coach import codex_status, request_codex_coaching
from .database import (
    get_daily_assignment,
    get_daily_review_assignment,
    get_draft,
    highest_hint,
    initialize_database,
    list_attempts,
    list_review_states,
    record_hint,
    save_attempt,
    save_daily_assignment,
    save_daily_review_assignment,
    save_draft,
)
from .learning import prerequisites_met, topic_mastery
from .schemas import AttemptCreate, ProblemDefinition
from .shared_auth import SharedSessionAuth


APP_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIST = APP_ROOT / "frontend" / "dist"
AUTH = SharedSessionAuth.from_environment()

@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Code Practice Lab", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def require_online_auth(request: Request, call_next: Any) -> Response:
    if request.url.path == "/api/health" or not AUTH.enabled:
        return await call_next(request)
    if AUTH.valid_token(request.cookies.get(AUTH.cookie_name)):
        return await call_next(request)
    if request.url.path.startswith("/api/"):
        return JSONResponse({"detail": "Authentication required."}, status_code=401)
    target = request.url.path
    if request.url.query:
        target = f"{target}?{request.url.query}"
    return RedirectResponse(AUTH.login_redirect(target), status_code=303)


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
        "mode": "authenticated-website" if AUTH.enabled else "local-only",
        "authEnabled": AUTH.enabled,
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
    today_key = datetime.now().astimezone().date().isoformat()
    daily_ids = get_daily_assignment(today_key)
    if daily_ids is None:
        due_ids = [
            review.problem_id
            for review in reviews
            if review.due_at <= now and review.problem_id in catalog and review.problem_id not in solved
        ]
        selected: list[ProblemDefinition] = []

        def recommendation_limit(items: list[ProblemDefinition]) -> int:
            if any(problem.difficulty >= 8 for problem in items):
                return 3
            if any(4 <= problem.difficulty <= 7 for problem in items):
                return 4
            return 5

        def at_capacity() -> bool:
            return len(selected) >= recommendation_limit(selected)

        def add_recommendation(problem: ProblemDefinition) -> bool:
            if problem.id in solved or problem in selected or not prerequisites_met(problem, mastery):
                return False
            proposed = [*selected, problem]
            if len(proposed) > recommendation_limit(proposed):
                return False
            selected.append(problem)
            return True

        for problem_id in due_ids:
            if at_capacity():
                break
            add_recommendation(catalog[problem_id])

        weak_topics = [topic for topic, _score in sorted(mastery.items(), key=lambda item: item[1])]
        for topic in weak_topics:
            candidate = next(
                (
                    problem for problem in catalog.values()
                    if topic in problem.topics and problem.id not in solved and problem not in selected
                ),
                None,
            )
            if candidate and add_recommendation(candidate):
                break
            if at_capacity():
                break

        for problem in sorted(catalog.values(), key=lambda item: item.difficulty):
            if at_capacity():
                break
            add_recommendation(problem)

        daily_ids = save_daily_assignment(today_key, [problem.id for problem in selected])

    assigned = [catalog[problem_id] for problem_id in daily_ids if problem_id in catalog]
    recommendations = [problem for problem in assigned if problem.id not in solved]
    daily_complete = not recommendations

    daily_review = get_daily_review_assignment(today_key)
    if daily_review is None:
        review_ids = [
            review.problem_id
            for review in reviews
            if review.problem_id in solved and review.problem_id in catalog
        ]
        review_ids.extend(sorted(solved.difference(review_ids)))
        daily_review = save_daily_review_assignment(today_key, review_ids[:5])
    review_assigned_at, assigned_review_ids = daily_review
    reviewed_today = {
        attempt.problem_id
        for attempt in attempts
        if attempt.result == "accepted" and attempt.created_at > review_assigned_at
    }
    remaining_review_ids = [problem_id for problem_id in assigned_review_ids if problem_id not in reviewed_today]
    review_recommendations = [catalog[problem_id] for problem_id in remaining_review_ids if problem_id in catalog]
    review_complete = bool(assigned_review_ids) and not review_recommendations

    challenge = next(
        (
            problem for problem in sorted(catalog.values(), key=lambda item: item.difficulty)
            if problem.id not in solved and problem.difficulty >= 8 and prerequisites_met(problem, mastery)
        ),
        None,
    )
    return {
        "recommendations": [problem_summary(problem, solved) for problem in recommendations],
        "dailyComplete": daily_complete,
        "dailyAssignedCount": len(assigned),
        "dailyRemainingCount": len(recommendations),
        "reviewRecommendations": [problem_summary(problem, solved) for problem in review_recommendations],
        "reviewComplete": review_complete,
        "reviewAssignedCount": len(assigned_review_ids),
        "reviewRemainingCount": len(review_recommendations),
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
