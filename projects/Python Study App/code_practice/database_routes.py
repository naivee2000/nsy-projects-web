from __future__ import annotations

from datetime import date
import json
from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from . import database_track as track
from . import review_v2
from .database import db_session
from .database_catalog import CATALOG, INVENTORY, pandas_starter, public_case, summary
from .database_judge import Unavailable, matches, evaluate_mysql


router = APIRouter(prefix="/api/database")
Language = Literal["mysql", "pandas"]


def item(problem_id):
    if problem_id not in INVENTORY:
        raise HTTPException(404, "Database problem not found.")
    return INVENTORY[problem_id]


def runnable(problem_id):
    item(problem_id)
    if problem_id not in CATALOG:
        raise HTTPException(409, "This problem is awaiting local judge verification.")
    return CATALOG[problem_id]


def context(con, problem_id, review_day):
    if not review_day:
        return "practice"
    if review_day != review_v2.local_day():
        raise HTTPException(409, "This review belongs to a different study day. Open today's Review.")
    assignment = con.execute("SELECT review_ids FROM db_track_assignments WHERE day=?",
                             (str(review_day),)).fetchone()
    if not assignment or problem_id not in json.loads(assignment[0]):
        raise HTTPException(404, "Review assignment not found.")
    return f"review:{review_day}"


@router.get("/problems")
def problems(search: str = Query("", max_length=160),
             difficulty: Literal["all", "Easy", "Medium", "Hard"] = "all",
             playable: bool = False, page: int = Query(1, ge=1)):
    with db_session() as con:
        passed = track.completion(con)
    query = search.strip().casefold()
    rows = [summary(p, sorted(passed.get(p["id"], ()))) for p in INVENTORY.values()
            if (query in p["title"].casefold() or query == str(p["id"]))
            and (difficulty == "all" or p["difficulty"] == difficulty)
            and (not playable or p["id"] in CATALOG)]
    return {"items": rows[(page - 1) * 30:page * 30], "total": len(rows), "pageSize": 30}


@router.get("/problems/{problem_id}")
def problem_detail(problem_id: int, review_day: date | None = None):
    inventory = item(problem_id)
    problem = CATALOG.get(problem_id)
    with db_session() as con:
        draft_context = context(con, problem_id, review_day)
        passed = track.completion(con)
        drafts = {r["language"]: r["source"] for r in con.execute(
            "SELECT language,source FROM db_track_drafts WHERE problem_id=? AND context=?",
            (problem_id, draft_context))}
    payload = {**summary(inventory, sorted(passed.get(problem_id, ()))), "summary": inventory["summary"],
               "sourceExample": inventory["example"], "officialLanguages": inventory["language"]}
    if problem:
        payload.update({"examples": [public_case(problem, c) for c in problem["cases"][:2]],
                        "schema": problem["schema"], "advice": problem["advice"],
                        "starters": {"mysql": "-- Write your MySQL solution here.\n", "pandas": pandas_starter(problem)},
                        "drafts": drafts})
    return payload


class Draft(BaseModel):
    source: str = Field(max_length=50_000)
    review_day: date | None = None


@router.put("/problems/{problem_id}/draft/{language}")
def save_draft(problem_id: int, language: Language, payload: Draft):
    runnable(problem_id)
    with db_session() as con:
        draft_context = context(con, problem_id, payload.review_day)
        con.execute("""INSERT INTO db_track_drafts VALUES (?,?,?,?)
                       ON CONFLICT(problem_id,language,context) DO UPDATE SET source=excluded.source""",
                    (problem_id, language, draft_context, payload.source))
    return {"saved": True}


@router.get("/problems/{problem_id}/pandas-cases")
def pandas_cases(problem_id: int, examples: bool = False):
    problem = runnable(problem_id)
    cases = problem["cases"][:2] if examples else problem["cases"]
    return {"schema": problem["schema"], "runner": problem["runner"],
            "inputs": [{key: value for key, value in public_case(problem, case).items() if key != "expected"} for case in cases]}


class Table(BaseModel):
    columns: list[str] = Field(max_length=128)
    rows: list[list[float | int | str | None]] = Field(max_length=5000)


class CaseResult(BaseModel):
    actual: Table | None = None
    error: str | None = Field(None, max_length=1000)


class Submission(Draft):
    language: Language
    request_id: UUID
    examples: bool = False
    results: list[CaseResult] | None = Field(None, max_length=100)


def evaluate(problem, payload):
    cases = problem["cases"][:2] if payload.examples else problem["cases"]
    if payload.language == "pandas" and (
        payload.results is None or len(payload.results) != len(cases)
    ):
        raise HTTPException(422, "Results must match the current fixture package.")
    outcomes = []
    for index, case in enumerate(cases):
        if payload.language == "mysql":
            try:
                result = evaluate_mysql(problem, case, payload.source)
            except Unavailable as error:
                raise HTTPException(503, str(error)) from error
        else:
            value = payload.results[index]
            actual = value.actual
            passed = actual is not None and matches(
                case["expected"], actual.columns, actual.rows, ordered=problem["ordered"])
            result = {"passed": passed, "actual": actual.model_dump() if actual else None, "error": value.error}
        if index < 2 or not result["passed"]:
            outcomes.append({"case": index + 1, **result, "expected": case["expected"],
                             "input": public_case(problem, case)["tables"], "parameters": case["parameters"]})
        else:
            outcomes.append({"case": index + 1, "passed": True})
    return {"accepted": all(result["passed"] for result in outcomes), "cases": outcomes}


def replay(con, request_id, problem_id, payload, draft_context):
    row = con.execute("SELECT * FROM db_track_attempts WHERE request_id=?", (request_id,)).fetchone()
    if row:
        if (row["problem_id"], row["language"], row["context"], row["source"]) != (
            problem_id, payload.language, draft_context, payload.source
        ):
            raise HTTPException(409, "This submission ID was already used for a different answer.")
        return json.loads(row["response"])
    return None


@router.post("/problems/{problem_id}/judge")
def judge(problem_id: int, payload: Submission):
    problem = runnable(problem_id)
    request_id = str(payload.request_id)
    with db_session() as con:
        draft_context = context(con, problem_id, payload.review_day)
        saved = None if payload.examples else replay(con, request_id, problem_id, payload, draft_context)
    if saved:
        return saved
    reply = evaluate(problem, payload)
    if payload.examples:
        return reply
    with db_session() as con:
        con.execute("BEGIN IMMEDIATE")
        draft_context = context(con, problem_id, payload.review_day)
        if saved := replay(con, request_id, problem_id, payload, draft_context):
            return saved
        day = review_v2.local_day()
        con.execute("INSERT INTO db_track_attempts VALUES (?,?,?,?,?,?,?,?)",
                    (request_id, problem_id, payload.language, draft_context, str(day),
                     payload.source, int(reply["accepted"]), "{}"))
        reply["review"] = track.save_event(con, problem_id, day)
        con.execute("UPDATE db_track_attempts SET response=? WHERE request_id=?", (json.dumps(reply), request_id))
    return reply


class Rating(BaseModel):
    grade: Literal["again", "hard", "good", "easy"] | None


@router.put("/problems/{problem_id}/rating")
def rate(problem_id: int, payload: Rating):
    runnable(problem_id)
    day = review_v2.local_day()
    with db_session() as con:
        con.execute("BEGIN IMMEDIATE")
        result = con.execute("UPDATE db_track_events SET manual=? WHERE problem_id=? AND day=? AND latest=1",
                             (payload.grade, problem_id, str(day)))
        if not result.rowcount:
            raise HTTPException(409, "Pass the problem today before rating the review.")
        return track.save_event(con, problem_id, day)
