"""Account-local review scheduling with optional owner topic quotas.

Raw attempts and the legacy scheduler remain available for rollback. This
module never executes student code and never changes historical submissions.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
import hashlib
from itertools import combinations
import json
import os
from zoneinfo import ZoneInfo

from . import database
from .learning import (is_dynamic_programming_problem, is_graph_traversal_problem,
                       is_grid_recursion_problem, is_linked_list_problem, is_tree_problem)
from .study_lists import study_list_badges

TZ = ZoneInfo("America/New_York")
INTERVALS = (1, 3, 7, 14, 30, 60)
GRADES = ("again", "hard", "good", "easy")
LABELS = {"again": "Need more review", "hard": "Hard to finish", "good": "Finished independently", "easy": "Very easy"}
GROUPS = (("trees", is_tree_problem), ("linked lists", is_linked_list_problem),
          ("graphs", is_graph_traversal_problem), ("grid recursion", is_grid_recursion_problem))


def enabled() -> bool:
    return os.environ.get("CODE_PRACTICE_REVIEW_V2", "1").lower() not in {"0", "false", "off"}


def local_day(now: datetime | None = None) -> date:
    return (now or datetime.now(timezone.utc)).astimezone(TZ).date()


def midnight(day: date) -> datetime:
    return datetime.combine(day, time(), TZ).astimezone(timezone.utc)


def effective_grade(event) -> str:
    if event["latest_result"] != "accepted":
        return "again"
    return event["manual_grade"] or event["automatic_grade"]


def advance(previous: dict | None, day: date, grade: str) -> tuple[dict, bool]:
    """Recompute from the day's frozen prior state; early passes cannot defer due."""
    if previous is None:
        index = 1 if grade == "easy" else 0
    else:
        early = day < date.fromisoformat(previous["dueDay"])
        if early and grade in {"good", "easy"}:
            return dict(previous), False
        old_index = previous["index"]
        index = (0 if grade == "again" else max(0, min(old_index - 1, 2)) if grade == "hard"
                 else min(old_index + (2 if grade == "easy" else 1), len(INTERVALS) - 1))
        if early and day + timedelta(days=INTERVALS[index]) >= date.fromisoformat(previous["dueDay"]):
            return {**previous, "recovery": True}, True
    return {"index": index, "anchorDay": str(day), "dueDay": str(day + timedelta(days=INTERVALS[index])),
            "intervalDays": INTERVALS[index], "recovery": grade in {"again", "hard"}}, True


def initialize(con) -> None:
    if con.execute("SELECT 1 FROM review_v2_meta WHERE key='replayed-v1'").fetchone():
        return
    for row in con.execute("SELECT DISTINCT problem_id FROM attempts").fetchall():
        sync_problem(con, row[0], legacy_backfill=True)
    con.execute("INSERT INTO review_v2_meta VALUES('replayed-v1',?)", (datetime.now(timezone.utc).isoformat(),))


def sync_problem(con, problem_id: str, *, legacy_backfill: bool = False) -> None:
    rows = con.execute("""SELECT a.id,a.result,a.created_at,c.entry_point FROM attempts a
                          LEFT JOIN attempt_contexts c ON c.attempt_id=a.id
                          WHERE a.problem_id=? ORDER BY a.created_at,a.id""", (problem_id,)).fetchall()
    days = defaultdict(list)
    for row in rows:
        days[str(local_day(datetime.fromisoformat(row["created_at"])))].append(row)
    manual = {r["event_date"]: r["manual_grade"] for r in con.execute(
        "SELECT event_date,manual_grade FROM review_events WHERE problem_id=?", (problem_id,))}
    contexts = {r["event_date"]: r for r in con.execute("SELECT * FROM review_contexts WHERE problem_id=?", (problem_id,))}
    state = None
    for day, records in sorted(days.items()):
        if state is None and not any(r["result"] == "accepted" for r in records):
            continue
        existing = con.execute("SELECT * FROM review_events WHERE problem_id=? AND event_date=?", (problem_id, day)).fetchone()
        if existing and existing["policy_version"] == 1 and day != str(local_day()):
            state = json.loads(existing["final_state"])
            continue
        context = contexts.get(day)
        helped = bool(context and (context["hint_level"] or context["assisted"]))
        seen_solution = bool(context and context["source_viewed"])
        latest = records[-1]["result"]
        automatic = ("again" if latest != "accepted" or seen_solution else
                     "hard" if helped or any(r["result"] != "accepted" for r in records) else "good")
        reason = "Historical rating inferred from submissions."
        streak = 0
        policy = existing["policy_version"] if existing else (1 if legacy_backfill else 2)
        if policy == 2:
            help_rows = con.execute("SELECT category FROM review_help_events WHERE problem_id=? AND event_date=? AND created_at<=?",
                                    (problem_id, day, records[-1]["created_at"])).fetchall()
            categories = {r[0] for r in help_rows}
            failed = any(r["result"] != "accepted" for r in records)
            answer = existing["correction_answer"] if existing else None
            if latest != "accepted":
                automatic, reason = "again", "The latest full submission has not passed yet."
            elif "solution" in categories:
                automatic, reason = "again", "Viewed a solution before passing."
            elif "algorithm" in categories:
                automatic, reason = "hard", "Used help with the approach before passing."
            elif failed and answer != "implementation":
                automatic = "hard"
                reason = ("Rethought the approach before passing." if answer == "approach" else
                          "Passed after corrections; confirm what you changed.")
            else:
                automatic = "good"
                reason = ("Passed independently after correcting implementation details." if failed else
                          "Passed with debugging assistance." if categories else "Passed independently.")
            is_due_review = bool(state and day >= state["dueDay"] and any(r["entry_point"] == "review" for r in records))
            streak = state.get("cleanStreak", 0) if state else 0
            if is_due_review:
                streak = streak + 1 if latest == "accepted" and not failed and not categories else 0
                if streak >= 3 and automatic == "good":
                    automatic, reason = "easy", f"Recalled independently on {streak} consecutive clean reviews."
        chosen = manual.get(day) if latest == "accepted" else None
        base = json.dumps(state) if state else None
        inferred = all(r["entry_point"] is None for r in records)
        # Re-submitting a saved Library solution is not evidence of spaced
        # recall. Fresh review sessions provide that evidence going forward.
        saved_library_pass = (state is not None and not inferred and not chosen
                              and automatic == "good" and not any(r["entry_point"] == "review" for r in records))
        state, counted = (dict(state), False) if saved_library_pass else advance(state, date.fromisoformat(day), chosen or automatic)
        state = {**state, "latestResult": latest, "lastEventDay": day}
        if policy == 2:
            state["cleanStreak"] = streak
        con.execute("""INSERT INTO review_events(problem_id,event_date,automatic_grade,manual_grade,
                    latest_result,first_at,last_at,inferred,counted,base_state,final_state)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(problem_id,event_date) DO UPDATE SET
                    automatic_grade=excluded.automatic_grade,latest_result=excluded.latest_result,
                    last_at=excluded.last_at,inferred=excluded.inferred,counted=excluded.counted,
                    base_state=excluded.base_state,final_state=excluded.final_state""",
                    (problem_id, day, automatic, manual.get(day), latest, records[0]["created_at"], records[-1]["created_at"],
                     int(inferred), int(counted), base, json.dumps(state)))
        con.execute("UPDATE review_events SET rating_reason=?,clean_streak=?,policy_version=? WHERE problem_id=? AND event_date=?",
                    (reason, streak, policy, problem_id, day))
    if state:
        con.execute("INSERT INTO review_schedules_v2 VALUES(?,?) ON CONFLICT(problem_id) DO UPDATE SET state_json=excluded.state_json",
                    (problem_id, json.dumps(state)))


def event_payload(con, problem_id: str, day: str | None = None) -> dict | None:
    event = con.execute("SELECT * FROM review_events WHERE problem_id=? AND event_date=?", (problem_id, day or str(local_day()))).fetchone()
    if not event:
        return None
    state = json.loads(event["final_state"])
    return {"id": event["id"], "problemId": problem_id, "date": event["event_date"],
            "automaticGrade": event["automatic_grade"], "manualGrade": event["manual_grade"],
            "effectiveGrade": effective_grade(event), "latestResult": event["latest_result"],
            "dueDate": state["dueDay"], "inferred": bool(event["inferred"]),
            "ratingReason": event["rating_reason"], "cleanStreak": event["clean_streak"],
            "correctionAnswer": event["correction_answer"],
            "needsCorrectionAnswer": event["policy_version"] == 2 and event["latest_result"] == "accepted" and
                bool(con.execute("SELECT 1 FROM attempts WHERE problem_id=? AND result!='accepted' AND created_at>=? AND created_at<=?",
                                 (problem_id, event["first_at"], event["last_at"])).fetchone())}


def priorities(con, catalog, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    today = local_day(now)
    schedules = {r[0]: json.loads(r[1]) for r in con.execute("SELECT * FROM review_schedules_v2")}
    events = defaultdict(list)
    last_review = {}
    for r in con.execute("SELECT * FROM review_events ORDER BY event_date DESC"):
        events[r["problem_id"]].append(r)
        # The first learning day does not impose a review cooldown.
        if r["counted"] and r["base_state"] is not None:
            last_review.setdefault(r["problem_id"], r["event_date"])
    for r in con.execute("SELECT problem_id,MAX(assignment_date) FROM daily_review_problems WHERE assignment_date<=? GROUP BY problem_id", (str(today),)):
        last_review[r[0]] = max(last_review.get(r[0], ""), r[1])
    assigned = {r[0] for r in con.execute("SELECT problem_id FROM daily_review_problems WHERE assignment_date=?", (str(today),))}
    snapshots = {r["problem_id"]: dict(r) for r in con.execute("SELECT * FROM review_assignment_details WHERE assignment_date=?", (str(today),))}
    result = []
    for p in catalog.values():
        state = schedules.get(p.id)
        cooldown = str(date.fromisoformat(last_review[p.id]) + timedelta(days=4)) if p.id in last_review else None
        urgency = struggle = None
        recovery = False
        if state:
            elapsed = max(0.0, (now - midnight(date.fromisoformat(state["anchorDay"]))).total_seconds() / 86400)
            urgency = min(70.0, 35 * elapsed / state["intervalDays"])
            recent = [e for e in events[p.id] if e["counted"]][:3]
            weights = (4, 2, 1)[:len(recent)]
            struggle = 30 * sum(w * {"again": 1, "hard": .5, "good": 0, "easy": 0}[effective_grade(e)] for w,e in zip(weights,recent)) / sum(weights)
            due = date.fromisoformat(state["dueDay"]) <= today
            recovery = state["recovery"] and due
            status = ("retry" if state["latestResult"] != "accepted" else "not_due" if not due else
                      "cooldown" if cooldown and str(today) < cooldown and not recovery else "eligible")
        else:
            status = "unlearned"
        reason = {"unlearned": "Pass this problem before it can enter Review.",
                  "retry": "A previous pass exists; retry the unresolved attempt before normal review.",
                  "not_due": "Not due yet.", "cooldown": "Within the three-day review cooldown.",
                  "eligible": "Due and eligible for review."}[status]
        if status == "eligible" and recovery:
            reason += " Short recovery interval overrides normal cooldown."
        snapshot = snapshots.get(p.id)
        if p.id in assigned:
            reason += " In today's saved set."
        elif status == "eligible" and assigned:
            reason += " Outside today's fixed set; topic and difficulty matching determined selection."
        result.append({"id": p.id, "title": p.title, "difficulty": p.difficulty,
                       "score": round(urgency + struggle, 3) if state else None,
                       "urgency": round(urgency, 3) if state else None, "recentStruggle": round(struggle, 3) if state else None,
                       "dueDate": state["dueDay"] if state else None, "cooldownUntil": cooldown,
                       "recoveryException": bool(recovery), "status": status, "reason": reason,
                       "assignedToday": p.id in assigned, "assignmentScore": snapshot["score"] if snapshot else None,
                       "assignmentReason": snapshot["reason"] if snapshot else "Saved before scoring v2." if p.id in assigned else None,
                       "inferred": bool(events[p.id] and events[p.id][0]["inferred"])})
    return sorted(result, key=lambda r: (r["score"] is None, -(r["score"] or 0), r["id"]))


def choose(rows: list[dict], catalog, day: str, *, owner_focus: bool = True) -> tuple[list[dict], list[str]]:
    """Five-slot matching with per-question uniqueness and Medium quota."""
    candidates = sorted((r for r in rows if r["status"] == "eligible"), key=lambda r: r["id"])
    if not owner_focus:
        # Members follow their interview path without personal topic or
        # difficulty quotas. Due dates and ratings drive review priority.
        candidates = [r for r in candidates if study_list_badges(r["id"])]
        candidates.sort(key=lambda r: (-r["score"], -r["difficulty"], r["id"]))
        chosen = [{**r, "selectionReason": "Due interview practice"} for r in candidates[:5]]
        return chosen, (["Fewer than five due interview-list questions are currently eligible."] if len(chosen) < 5 else [])
    pairs = list(combinations(range(4), 2))
    offset = date.fromisoformat(day).toordinal() % len(pairs)
    pairs = pairs[offset:] + pairs[:offset]
    best = None
    for pair_rank, pair in enumerate(pairs):
        # State value: DP matches, Hot100 matches, focus matches, score, stable tie, choices.
        dp = {(0, 0): (0, 0, 0, 0.0, 0, ())}
        for row in candidates:
            p = catalog[row["id"]]
            medium = int(4 <= p.difficulty <= 7)
            hot = any(b["id"] == "hot-100" for b in study_list_badges(p.id))
            tie = -int.from_bytes(hashlib.sha256(f"{day}:{p.id}".encode()).digest()[:8], "big")
            matches = (is_dynamic_programming_problem(p), GROUPS[pair[0]][1](p), GROUPS[pair[1]][1](p), hot, hot)
            for (mask, count), value in list(dp.items()):
                for slot in range(5):
                    if mask & (1 << slot):
                        continue
                    candidate = (value[0] + int(slot == 0 and matches[slot]),
                                 value[1] + int(slot >= 3 and matches[slot]),
                                 value[2] + int(slot in (1,2) and matches[slot]),
                                 value[3] + row["score"], value[4] + tie,
                                 (*value[5], (slot, row["id"], bool(matches[slot]))))
                    key = (mask | (1 << slot), min(4, count + medium))
                    if key not in dp or candidate[:5] > dp[key][:5]:
                        dp[key] = candidate
        for (mask, medium), value in dp.items():
            quality = (mask.bit_count(), value[0], medium, value[1], value[2], -pair_rank, value[3], value[4])
            if best is None or quality > best[0]:
                best = (quality, value[5], pair)
    assert best is not None
    by_id = {r["id"]: r for r in candidates}
    names = ("Daily DP", GROUPS[best[2][0]][0], GROUPS[best[2][1]][0], "Hot 100", "Hot 100")
    chosen = [{**by_id[key], "selectionReason": names[slot] if matched else "Due-question quota fallback"}
              for slot,key,matched in sorted(best[1])]
    notes = []
    if sum(4 <= r["difficulty"] <= 7 for r in chosen) < 4:
        notes.append("Fewer than four due Mediums are available outside cooldown; no early questions were added.")
    if not any(is_dynamic_programming_problem(catalog[r["id"]]) for r in chosen):
        notes.append("No due DP question is available outside cooldown.")
    if len(chosen) < 5:
        notes.append("Fewer than five due questions are currently eligible.")
    if any(r["selectionReason"] == "Due-question quota fallback" for r in chosen):
        notes.append("Topic or Hot 100 slots were relaxed to preserve due-only and Medium priorities.")
    return chosen, notes


def ensure_assignment(con, catalog, now: datetime) -> tuple[tuple[datetime, list[str]], list[str]]:
    """Serialize first assignment and its explanatory snapshot in one transaction."""
    day = str(local_day(now))
    con.execute("BEGIN IMMEDIATE")
    saved = con.execute("SELECT assigned_at FROM daily_review_sessions WHERE assignment_date=?", (day,)).fetchone()
    notes_key = f"assignment-notes:{day}"
    if saved:
        ids = [r[0] for r in con.execute("SELECT problem_id FROM daily_review_problems WHERE assignment_date=? ORDER BY position", (day,))]
        notes = con.execute("SELECT value FROM review_v2_meta WHERE key=?", (notes_key,)).fetchone()
        return (datetime.fromisoformat(saved[0]), ids), json.loads(notes[0]) if notes else [
            "Today's existing review set is preserved; new quotas apply to the next day's set."]
    chosen, notes = choose(priorities(con, catalog, now), catalog, day,
                           owner_focus=database.current_profile() == "owner")
    con.execute("INSERT INTO daily_review_sessions VALUES(?,?)", (day, now.isoformat()))
    con.executemany("INSERT INTO daily_review_problems VALUES(?,?,?)", [(day,i,r["id"]) for i,r in enumerate(chosen)])
    con.executemany("INSERT INTO review_assignment_details VALUES(?,?,?,?)",
                    [(day,r["id"],r["score"],r["selectionReason"]) for r in chosen])
    con.execute("INSERT INTO review_v2_meta VALUES(?,?)", (notes_key,json.dumps(notes)))
    return (now,[r["id"] for r in chosen]), notes
