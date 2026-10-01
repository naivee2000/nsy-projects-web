"""Offline study-plan metadata; source IDs and approved equivalents preserve progress IDs."""
from functools import lru_cache
import json
from pathlib import Path


@lru_cache(maxsize=1)
def study_list_snapshot() -> dict:
    return json.loads(Path(__file__).with_name("study_lists.json").read_text())


@lru_cache(maxsize=1)
def _memberships() -> dict[str, list[dict]]:
    memberships: dict[str, list[dict]] = {}
    for plan in study_list_snapshot()["lists"]:
        for member in plan["problems"]:
            memberships.setdefault(member["problem_id"], []).append({
                "id": plan["id"], "label": plan["label"], "url": plan["url"],
                "sourceTitle": member["title"], "match": member["match"],
            })
    return memberships


def study_list_badges(problem_id: str) -> list[dict]:
    return _memberships().get(problem_id, [])


def study_list_options(available_ids: set[str]) -> list[dict]:
    return [
        {
            "id": plan["id"], "label": plan["label"], "url": plan["url"],
            "available": len({p["problem_id"] for p in plan["problems"]} & available_ids),
            "total": len(plan["problems"]),
        }
        for plan in study_list_snapshot()["lists"]
    ]
