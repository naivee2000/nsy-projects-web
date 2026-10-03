from __future__ import annotations

from contextlib import asynccontextmanager
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .catalog import get_catalog, problem_summary, public_problem
from .coach import build_coaching
from .interview_plan import InterviewPlan
from .codex_coach import codex_status, request_codex_coaching
from .database import (
    get_daily_assignment,
    get_daily_review_assignment,
    get_draft,
    highest_hint,
    list_attempts,
    learning_attempts,
    recent_daily_review_problem_ids,
    solved_problem_ids,
    list_review_states,
    record_hint,
    remove_daily_assignment_problems,
    save_attempt,
    save_daily_assignment,
    save_daily_review_assignment,
    save_draft,
)
from .learning import (
    choose_daily_session,
    normalized_topics,
    prioritized_review_problems,
    topic_mastery,
    topic_progression_met,
)
from .schemas import AttemptCreate, ProblemDefinition
from .shared_auth import SharedSessionAuth
from .starter_code import with_support_classes
from . import accounts
from .account_routes import router as account_router
from .database import profile_scope


APP_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIST = APP_ROOT / "frontend" / "dist"
AUTH = SharedSessionAuth.from_environment()

@asynccontextmanager
async def lifespan(_app: FastAPI):
    accounts.initialize(AUTH.username or "admin")
    yield


app = FastAPI(title="Code Practice Lab", version="0.1.0", lifespan=lifespan)
app.include_router(account_router)


def login_required() -> bool:
    return AUTH.enabled or os.environ.get("CODE_PRACTICE_REQUIRE_LOGIN", "").lower() in {"1", "true", "yes"}


@app.middleware("http")
async def require_online_auth(request: Request, call_next: Any) -> Response:
    path = request.url.path
    required = login_required()
    token = request.cookies.get(accounts.COOKIE)
    user = accounts.session_user(token) if token else None
    if token is None and (not required or AUTH.valid_token(request.cookies.get(AUTH.cookie_name))):
        user = accounts.get_user("owner")
    request.state.user = user
    request.state.shared_auth = AUTH
    request.state.login_required = required
    request.state.secure_cookie = AUTH.public_origin.startswith("https://")
    public = path in {"/api/health", "/api/auth/me", "/api/auth/login", "/api/auth/logout", "/api/auth/owner", "/login"}
    public = public or path.startswith(("/assets/", "/pyodide/", "/monaco/")) or path == "/judge-worker.js"
    unsafe = request.method not in {"GET", "HEAD", "OPTIONS"}
    if unsafe and (required or path.startswith(("/api/auth/", "/api/admin/"))):
        origin = request.headers.get("origin")
        if (request.headers.get("x-requested-with") != "CodePractice"
                or (origin and origin.rstrip("/") not in {AUTH.public_origin, str(request.base_url).rstrip("/")})):
            return JSONResponse({"detail": "Request must come from the study app."}, status_code=403)
    if not public and not user:
        if path.startswith("/api/"):
            return JSONResponse({"detail": "Authentication required."}, status_code=401)
        return RedirectResponse("/login", status_code=303)
    if user and not public:
        profile = request.headers.get("x-study-profile")
        if ((profile and profile != user["id"]) or (unsafe and required and not profile)):
            return JSONResponse({"detail": "Account changed. Reload before continuing.", "code": "profile_changed"}, status_code=409)
        if user["must_change_password"] and path != "/api/auth/password" and path.startswith("/api/"):
            return JSONResponse({"detail": "Change your temporary password first.", "code": "password_change_required"}, status_code=403)
        if user["role"] != "admin" and (path.endswith("/codex-coach") or path == "/api/coach/codex-status"):
            return JSONResponse({"detail": "Codex coaching is available to the owner only."}, status_code=403)
    with profile_scope(user["id"] if user else "owner"):
        response = await call_next(request)
    if path.startswith("/api/") or path in {"/", "/login"}:
        response.headers["Cache-Control"] = "no-store"
    return response


class DraftPayload(BaseModel):
    source_code: str = Field(max_length=200_000)


class AttemptSubmission(AttemptCreate):
    entry_point: Literal["daily", "review", "challenge", "library"] = "library"


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
        "mode": "authenticated-website" if login_required() else "local-only",
        "authEnabled": login_required(),
        "problemCount": len(get_catalog()),
        "time": datetime.now(timezone.utc).isoformat(),
    }


def _solved_ids() -> set[str]:
    return solved_problem_ids()


@app.get("/api/problems")
def problems(
    topic: str | None = None,
    difficulty_min: int = Query(default=1, ge=1, le=10),
    difficulty_max: int = Query(default=10, ge=1, le=10),
    search: str | None = None,
    completion: Literal["all", "passed", "unsolved"] = "all",
    study_list: Literal["all", "interview-picks", "hot-100", "interview-150"] = "all",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=30, ge=1, le=100),
) -> dict[str, Any]:
    catalog = get_catalog()
    return catalog.search(solved=_solved_ids(), search=search or "", topic=topic,
                          difficulty_min=difficulty_min, difficulty_max=difficulty_max,
                          completion=completion, study_list=study_list, page=page, page_size=page_size)


@app.get("/api/problems/{problem_id}")
def problem_detail(problem_id: str) -> dict[str, Any]:
    problem = get_catalog().get(problem_id)
    if not problem or problem.status != "approved":
        raise HTTPException(404, "Problem not found")
    payload = public_problem(problem)
    payload["solved"] = problem_id in _solved_ids()
    saved_source = get_draft(problem_id) or problem.starter_code
    adapters = [parameter.adapter for parameter in problem.signature.parameters]
    adapters.append(problem.signature.return_adapter)
    payload["savedDraft"] = with_support_classes(saved_source, adapters)
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
def attempts(payload: AttemptSubmission) -> dict[str, Any]:
    problem = get_catalog().get(payload.problem_id)
    if not problem or problem.status != "approved":
        raise HTTPException(404, "Problem not found")
    if payload.problem_version != problem.version:
        raise HTTPException(409, "Problem version changed; reload before submitting")
    if payload.entry_point == "challenge" and payload.result != "accepted":
        return {"recorded": False, "reason": "Unpassed challenge attempts do not affect progress."}
    attempt = save_attempt(AttemptCreate.model_validate(payload.model_dump(exclude={"entry_point"})))
    return {**attempt.model_dump(mode="json"), "recorded": True}


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
    attempts = learning_attempts()
    catalog = get_catalog().metadata
    mastery = topic_mastery(attempts, catalog)
    reviews = list_review_states()
    solved = {attempt.problem_id for attempt in attempts if attempt.result == "accepted"}
    return {
        "attempts": [attempt.model_dump(mode="json") for attempt in list_attempts(limit=50)],
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
    catalog = get_catalog().metadata
    attempts = learning_attempts()
    mastery = topic_mastery(attempts, catalog)
    reviews = list_review_states()
    solved = {attempt.problem_id for attempt in attempts if attempt.result == "accepted"}
    introductory_topics = {
        topic
        for problem in catalog.values()
        if problem.difficulty <= 3
        for topic in normalized_topics(problem)
    }
    passed_introductory_topics = {
        topic
        for problem_id in solved
        if (problem := catalog.get(problem_id)) is not None and problem.difficulty <= 3
        for topic in normalized_topics(problem)
    }

    now = datetime.now(timezone.utc)
    today_key = datetime.now().astimezone().date().isoformat()
    interview_plan = InterviewPlan(catalog, attempts, reviews, now, today_key)
    daily_ids = get_daily_assignment(today_key)
    if daily_ids is not None:
        newly_locked_ids = [
            problem_id
            for problem_id in daily_ids
            if problem_id in catalog
            and problem_id not in solved
            and not topic_progression_met(
                catalog[problem_id],
                introductory_topics,
                passed_introductory_topics,
            )
        ]
        if newly_locked_ids:
            daily_ids = remove_daily_assignment_problems(today_key, newly_locked_ids)
    if daily_ids is None:
        selected = choose_daily_session(interview_plan.ordered)
        daily_ids = save_daily_assignment(today_key, [problem.id for problem in selected])

    assigned = [catalog[problem_id] for problem_id in daily_ids if problem_id in catalog]
    recommendations = [problem for problem in assigned if problem.id not in solved]
    daily_complete = bool(assigned) and not recommendations

    daily_review = get_daily_review_assignment(today_key)
    if daily_review is None:
        recent_review_ids = recent_daily_review_problem_ids(today_key, lookback_days=3)
        review_problems = prioritized_review_problems(
            catalog,
            attempts,
            reviews,
            solved,
            now,
            limit=5,
            selection_seed=today_key,
            recently_assigned_ids=recent_review_ids,
        )
        daily_review = save_daily_review_assignment(today_key, [problem.id for problem in review_problems])
    review_assigned_at, assigned_review_ids = daily_review
    current_passed_review_ids = {
        review.problem_id for review in reviews if review.latest_result == "accepted"
    }
    eligible_assigned_review_ids = [
        problem_id for problem_id in assigned_review_ids if problem_id in current_passed_review_ids
    ]
    reviewed_today = {
        attempt.problem_id
        for attempt in attempts
        if attempt.result == "accepted" and attempt.created_at > review_assigned_at
    }
    remaining_review_ids = [
        problem_id for problem_id in eligible_assigned_review_ids if problem_id not in reviewed_today
    ]
    review_recommendations = [catalog[problem_id] for problem_id in remaining_review_ids if problem_id in catalog]
    review_complete = bool(eligible_assigned_review_ids) and not review_recommendations

    challenge = next(
        (
            problem for problem in interview_plan.ordered
            if problem.id in interview_plan.ready_targets and problem.difficulty >= 8
        ),
        None,
    )
    return {
        "recommendations": [
            {**problem_summary(problem, solved), "preparationReason": interview_plan.reason(problem.id)}
            for problem in recommendations
        ],
        "interviewProgress": interview_plan.progress(),
        "dailyComplete": daily_complete,
        "dailyAssignedCount": len(assigned),
        "dailyRemainingCount": len(recommendations),
        "reviewRecommendations": [problem_summary(problem, solved) for problem in review_recommendations],
        "reviewComplete": review_complete,
        "reviewAssignedCount": len(eligible_assigned_review_ids),
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
    if (FRONTEND_DIST / "monaco").exists():
        app.mount("/monaco", StaticFiles(directory=FRONTEND_DIST / "monaco"), name="monaco")

    @app.get("/{full_path:path}")
    def frontend(full_path: str) -> FileResponse:
        candidate = (FRONTEND_DIST / full_path).resolve()
        if candidate.is_relative_to(FRONTEND_DIST.resolve()) and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
