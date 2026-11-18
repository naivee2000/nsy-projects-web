"""Persistence and scheduling for Database, scoped by the existing account middleware."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
import json

from .database import db_session
from .database_catalog import CATALOG, CREDITS, INVENTORY, PREREQUISITES, summary
from . import review_v2



def completion(con):
    result = defaultdict(set)
    for row in con.execute("SELECT DISTINCT problem_id,language FROM db_track_attempts WHERE accepted=1"):
        result[row[0]].add(row[1])
    return result


def latest_events(con):
    history = defaultdict(list)
    for row in con.execute("SELECT * FROM db_track_events ORDER BY day DESC"):
        history[row["problem_id"]].append(row)
    return history


def choose_new(day, passed, attempts):
    passed_topics = defaultdict(set)
    recent = defaultdict(list)
    for row in attempts:
        topic = CATALOG.get(row["problem_id"], {}).get("topic")
        if topic and len(recent[topic]) < 10:
            recent[topic].append(row["accepted"])
    for key in passed:
        if key in CATALOG:
            passed_topics[CATALOG[key]["topic"]].add(key)
    suitable = []
    for key, problem in CATALOG.items():
        if key in passed:
            continue
        topic = problem["topic"]
        difficulty = INVENTORY[key]["difficulty"]
        foundation = PREREQUISITES.get(topic, topic)
        lower = {p for p, item in CATALOG.items() if item["topic"] == foundation
                 and INVENTORY[p]["difficulty"] == "Easy"}
        if difficulty != "Easy" and lower and not (lower & passed_topics[foundation]):
            continue
        if difficulty == "Hard":
            mediums = {p for p, item in CATALOG.items() if item["topic"] == foundation
                       and INVENTORY[p]["difficulty"] == "Medium"}
            scores = recent[foundation]
            if len(mediums & passed_topics[foundation]) < min(2, len(mediums)):
                continue
            if not scores or sum(scores) / len(scores) < .7:
                continue
        suitable.append(key)
    picked, topics, budget = [], set(), 5
    while available := [key for key in suitable if key not in picked and CREDITS[INVENTORY[key]["difficulty"]] <= budget]:
        key = min(available, key=lambda key: (
            CATALOG[key]["topic"] in topics,
            -CREDITS[INVENTORY[key]["difficulty"]],
            sha256(f"{day}:{key}".encode()).digest(),
        ))
        picked.append(key)
        topics.add(CATALOG[key]["topic"])
        budget -= CREDITS[INVENTORY[key]["difficulty"]]
    return picked, budget


def choose_review(day, now, history, assignments):
    last_assigned = {}
    for assignment in assignments:
        for key in json.loads(assignment["review_ids"]):
            last_assigned.setdefault(key, assignment["day"])
    candidates = []
    for key, events in history.items():
        if key not in CATALOG or not events[0]["latest"]:
            continue
        state = json.loads(events[0]["state"])
        if state["dueDay"] > str(day):
            continue
        last = max(last_assigned.get(key, ""), next(
            (e["day"] for e in events if e["counted"] and e["base"]), ""))
        if last and (day - date.fromisoformat(last)).days <= 3 and not state["recovery"]:
            continue
        unseen = (day - date.fromisoformat(max(events[0]["day"], last))).days
        grades = [e["manual"] or e["grade"] for e in events if e["counted"]][:3]
        weights = (4, 2, 1)[:len(grades)]
        struggle = 30 * sum(w * {"again": 1, "hard": .5, "good": 0, "easy": 0}[g]
                            for w, g in zip(weights, grades)) / max(1, sum(weights))
        elapsed = max(0, (now - review_v2.midnight(date.fromisoformat(state["anchorDay"]))).total_seconds() / 86400)
        candidates.append((key, INVENTORY[key]["difficulty"] == "Medium", state["recovery"] and unseen <= 7,
                           unseen, state["dueDay"], min(70, 35 * elapsed / state["intervalDays"]) + struggle))
    # Group by topic to keep the search bounded; a five-slot DP retains the
    # best score for each combination of Mediums, recoveries and older coverage.
    by_topic = defaultdict(list)
    for candidate in candidates:
        by_topic[CATALOG[candidate[0]]["topic"]].append(candidate)
    def compare(choice):
        unseen, due, score, ids = choice
        return unseen, -date.fromisoformat(due).toordinal() if due else 0, score, ids

    plans = {(0, 0, 0, 0, False): (0, "", 0.0, ())}
    for _, group in sorted(by_topic.items()):
        topic_plans = {(*key, False): value for key, value in plans.items()}
        for key, medium, recovery, unseen, due, score in group:
            for (size, mids, rec, topics, older, used), value in list(topic_plans.items()):
                if size == 5:
                    continue
                for designate in ((False, True) if unseen >= 14 and not older else (False,)):
                    next_key = (size + 1, min(4, mids + int(medium)), rec + int(recovery),
                                topics + int(not used), older or designate, True)
                    choice = (unseen if designate else value[0], due if designate else value[1],
                              value[2] + score, (*value[3], key))
                    if next_key not in topic_plans or compare(choice) > compare(topic_plans[next_key]):
                        topic_plans[next_key] = choice
        plans = {}
        for key, value in topic_plans.items():
            if key[:-1] not in plans or compare(value) > compare(plans[key[:-1]]):
                plans[key[:-1]] = value
    key, choice = max(plans.items(), key=lambda entry: (
        entry[0][0], entry[0][1], -max(0, entry[0][2] - 2), entry[0][4], entry[1][0],
        -date.fromisoformat(entry[1][1]).toordinal() if entry[1][1] else 0, entry[0][3], entry[1][2], entry[1][3]))
    size, mids, rec, _, older = key
    notes = []
    if size < 5:
        notes.append("Fewer than five due Database reviews are eligible.")
    if mids < 4:
        notes.append("Fewer than four eligible Medium reviews are available.")
    if rec > 2:
        notes.append(f"{rec} recent recoveries were needed to fill today's review set.")
    if not older:
        notes.append("No eligible older review could be included.")
    return choice[3], notes


def dashboard(now=None):
    now = now or now_utc()
    day = review_v2.local_day(now)
    with db_session() as con:
        con.execute("BEGIN IMMEDIATE")
        saved = con.execute("SELECT * FROM db_track_assignments WHERE day=?", (str(day),)).fetchone()
        passed = completion(con)
        if saved:
            new_ids, review_ids, notes = (json.loads(saved[column]) for column in ("new_ids", "review_ids", "notes"))
        else:
            attempts = con.execute("SELECT problem_id,accepted FROM db_track_attempts ORDER BY rowid DESC").fetchall()
            older_sets = con.execute("SELECT day,review_ids FROM db_track_assignments WHERE day<? ORDER BY day DESC",
                                     (str(day),)).fetchall()
            new_ids, budget = choose_new(day, passed, attempts)
            review_ids, notes = choose_review(day, now, latest_events(con), older_sets)
            if budget:
                notes.append(f"{budget} new-problem credits had no eligible Database problem.")
            con.execute("INSERT INTO db_track_assignments VALUES (?,?,?,?)",
                        (str(day), json.dumps(new_ids), json.dumps(review_ids), json.dumps(notes)))
        completed_reviews = {row[0] for row in con.execute(
            "SELECT DISTINCT problem_id FROM db_track_attempts WHERE day=? AND context=? AND accepted=1",
            (str(day), f"review:{day}"))}
        return {"day": str(day), "solved": len(passed), "runnable": len(CATALOG), "total": len(INVENTORY),
                "newProblems": [summary(INVENTORY[k], sorted(passed[k])) for k in new_ids if k not in passed],
                "reviews": [summary(INVENTORY[k], sorted(passed[k])) for k in review_ids if k not in completed_reviews],
                "notes": notes}


def save_event(con, problem_id, day):
    old = con.execute("SELECT * FROM db_track_events WHERE problem_id=? AND day=?", (problem_id, str(day))).fetchone()
    prior = con.execute("SELECT state FROM db_track_events WHERE problem_id=? AND day<? ORDER BY day DESC LIMIT 1",
                        (problem_id, str(day))).fetchone()
    base = json.loads(old["base"]) if old and old["base"] else json.loads(prior[0]) if prior else None
    records = con.execute(
        "SELECT accepted,context FROM db_track_attempts WHERE problem_id=? AND day=? ORDER BY rowid",
        (problem_id, str(day))).fetchall()
    accepted = records[-1]["accepted"]
    if not base and not any(row["accepted"] for row in records):
        return None
    failed = any(not row["accepted"] for row in records)
    reviewed = any(row["context"] == f"review:{day}" for row in records)
    grade = "again" if not accepted else "hard" if failed else "good"
    manual = old["manual"] if accepted and old else None
    streak = base.get("cleanStreak", 0) if base else 0
    if reviewed and base and str(day) >= base["dueDay"]:
        streak = streak + 1 if accepted and not failed else 0
        if streak >= 3:
            grade = "easy"
    if base and accepted and grade == "good" and not reviewed and not manual:
        state, counted = dict(base), False
    else:
        state, counted = review_v2.advance(base, day, manual or grade)
    state["cleanStreak"] = streak
    con.execute("""INSERT INTO db_track_events VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(problem_id,day) DO UPDATE SET state=excluded.state,grade=excluded.grade,
        latest=excluded.latest,manual=excluded.manual,counted=excluded.counted""",
        (problem_id, str(day), json.dumps(base) if base else None, json.dumps(state), grade, manual, counted, accepted))
    return {"grade": manual or grade, "due": state["dueDay"]}


def now_utc():
    return datetime.now(timezone.utc)
