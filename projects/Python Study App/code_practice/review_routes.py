"""Private account-local review workspace and score inspection endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from typing import Literal

from . import database, review_v2
from .catalog import get_catalog
from .starter_code import with_support_classes

router = APIRouter(prefix="/api/reviews")


def require_review_access(request: Request) -> None:
    if not request.state.user:
        raise HTTPException(401, "Authentication required.")
    if not review_v2.enabled():
        raise HTTPException(404, "Review scoring v2 is disabled.")


def context_row(con, context_id: int):
    row = con.execute("SELECT * FROM review_contexts WHERE id=?", (context_id,)).fetchone()
    if not row or row["event_date"] != str(review_v2.local_day()):
        raise HTTPException(409, "This review session has expired. Reopen the problem.")
    return row


def validate_context(context_id: int, problem_id: str) -> None:
    with database.db_session() as con:
        row = context_row(con, context_id)
        if row["problem_id"] != problem_id:
            raise HTTPException(409, "Review session does not match this problem.")


@router.get("/priorities")
def priority_list(request: Request, search: str = "", status: str = "all",
                  page: int = Query(1, ge=1), page_size: int = Query(30, ge=1, le=100)):
    require_review_access(request)
    with database.db_session() as con:
        rows = review_v2.priorities(con, get_catalog().metadata)
    if search.strip():
        needle = search.strip().casefold()
        rows = [r for r in rows if needle in r["title"].casefold() or needle in r["id"]]
    if status != "all":
        if status not in {"eligible", "retry", "not_due", "cooldown", "unlearned", "assigned"}:
            raise HTTPException(422, "Unknown review status.")
        rows = [r for r in rows if r["assignedToday"]] if status == "assigned" else [r for r in rows if r["status"] == status]
    return {"items": rows[(page-1)*page_size:page*page_size], "total": len(rows), "page": page,
            "asOf": datetime.now(timezone.utc).isoformat()}


@router.post("/{problem_id}/session")
def start_review(problem_id: str, request: Request):
    require_review_access(request)
    problem = get_catalog().get(problem_id)
    if not problem:
        raise HTTPException(404, "Problem not found.")
    day = str(review_v2.local_day())
    with database.db_session() as con:
        con.execute("BEGIN IMMEDIATE")
        previous = con.execute("SELECT source_code FROM attempts WHERE problem_id=? AND result='accepted' ORDER BY created_at DESC,id DESC LIMIT 1", (problem_id,)).fetchone()
        if not previous:
            raise HTTPException(409, "Pass this problem once before starting a review.")
        adapters = [p.adapter for p in problem.signature.parameters] + [problem.signature.return_adapter]
        starter = with_support_classes(problem.starter_code, adapters)
        con.execute("INSERT OR IGNORE INTO review_contexts(problem_id,event_date,source_code,previous_source) VALUES(?,?,?,?)",
                    (problem_id, day, starter, previous[0]))
        row = con.execute("SELECT * FROM review_contexts WHERE problem_id=? AND event_date=?", (problem_id, day)).fetchone()
        hints = [{"level": level, "label": ["Concept", "Strategy", "Pseudocode", "Editorial"][level-1],
                  "content": problem.editorial if level == 4 else problem.hints[level-1]}
                 for level in range(1, row["hint_level"]+1)]
        return {"id": row["id"], "source": row["source_code"], "hints": hints,
                "event": review_v2.event_payload(con, problem_id), "hasPreviousSolution": bool(row["previous_source"])}


class Draft(BaseModel):
    source_code: str = Field(max_length=200_000)


@router.put("/sessions/{context_id}/draft")
def save_review_draft(context_id: int, payload: Draft, request: Request):
    require_review_access(request)
    with database.db_session() as con:
        con.execute("BEGIN IMMEDIATE")
        context_row(con, context_id)
        con.execute("UPDATE review_contexts SET source_code=? WHERE id=?", (payload.source_code, context_id))
    return {"saved": True}


class Help(BaseModel):
    kind: Literal["hint", "coach", "debugging", "solution"]
    level: int | None = Field(None, ge=1, le=4)


@router.post("/sessions/{context_id}/help")
def help_review(context_id: int, payload: Help, request: Request):
    require_review_access(request)
    with database.db_session() as con:
        con.execute("BEGIN IMMEDIATE")
        row = context_row(con, context_id)
        reply = {}
        if payload.kind == "solution":
            con.execute("UPDATE review_contexts SET source_viewed=1 WHERE id=?", (context_id,))
            reply["source"] = row["previous_source"] or ""
        elif payload.kind in {"coach", "debugging"}:
            con.execute("UPDATE review_contexts SET assisted=1 WHERE id=?", (context_id,))
        else:
            level = payload.level
            if level is None or level > row["hint_level"] + 1:
                raise HTTPException(409, "Reveal hints in order.")
            problem = get_catalog()[row["problem_id"]]
            con.execute("UPDATE review_contexts SET hint_level=MAX(hint_level,?),source_viewed=MAX(source_viewed,?) WHERE id=?",
                        (level, int(level == 4), context_id))
            reply.update(level=level, label=["Concept", "Strategy", "Pseudocode", "Editorial"][level-1],
                         content=problem.editorial if level == 4 else problem.hints[level-1])
        category = ("solution" if payload.kind == "solution" or payload.level == 4 else
                    "debugging" if payload.kind == "debugging" else "algorithm")
        record_help(con, row, category)
        review_v2.sync_problem(con, row["problem_id"])
        reply["event"] = review_v2.event_payload(con, row["problem_id"])
        return reply


class Feedback(BaseModel):
    grade: Literal["again", "hard", "good", "easy"] | None = None
    correction_answer: Literal["implementation", "approach"] | None = None


@router.put("/events/{event_id}/feedback")
def feedback(event_id: int, payload: Feedback, request: Request):
    require_review_access(request)
    with database.db_session() as con:
        con.execute("BEGIN IMMEDIATE")
        event = con.execute("SELECT * FROM review_events WHERE id=?", (event_id,)).fetchone()
        if not event or event["event_date"] != str(review_v2.local_day()):
            raise HTTPException(409, "Only today's review feedback can be edited.")
        if event["latest_result"] != "accepted":
            raise HTTPException(409, "Pass the problem before rating the review.")
        if "grade" in payload.model_fields_set:
            con.execute("UPDATE review_events SET manual_grade=? WHERE id=?", (payload.grade, event_id))
        if "correction_answer" in payload.model_fields_set:
            con.execute("UPDATE review_events SET correction_answer=? WHERE id=?", (payload.correction_answer, event_id))
        review_v2.sync_problem(con, event["problem_id"])
        return review_v2.event_payload(con, event["problem_id"])


def record_help(con, context, category: str) -> None:
    con.execute("INSERT INTO review_help_events(problem_id,event_date,category,created_at) VALUES(?,?,?,?)",
                (context["problem_id"], context["event_date"], category, datetime.now(timezone.utc).isoformat()))


def record_coaching(context_id: int | None, problem_id: str, mode: str) -> None:
    if context_id is None:
        return
    if not review_v2.enabled():
        raise HTTPException(403, "Review context is unavailable for this account.")
    with database.db_session() as con:
        row = context_row(con, context_id)
        if row["problem_id"] != problem_id:
            raise HTTPException(409, "Review session does not match this problem.")
        record_help(con, row, "debugging" if mode == "debug" else "algorithm")
