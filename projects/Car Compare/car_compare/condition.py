from __future__ import annotations

from datetime import datetime, timezone
import re


NEW_OLD_STOCK_RE = re.compile(r"\b(?:new old stock|nos vehicle)\b", re.I)
NEW_RE = re.compile(r"^(?:brand new|new vehicle|new)\b", re.I)
USED_RE = re.compile(r"^(?:used|pre[- ]?owned)\b", re.I)
CPO_RE = re.compile(r"^(?:certified(?:\s+pre[- ]?owned)?|cpo)\b", re.I)


def sanitize_listing_condition(
    declared: str,
    title: str,
    year: int,
    *,
    current_year: int | None = None,
    verified_new: bool = False,
) -> str:
    """Normalize condition evidence without relabeling unsold older inventory."""

    current_year = current_year if current_year is not None else datetime.now(timezone.utc).year
    normalized = (declared or "unknown").strip().lower()
    normalized = {"certified": "cpo", "certified pre-owned": "cpo"}.get(normalized, normalized)
    if normalized not in {"new", "used", "cpo", "unknown"}:
        normalized = "unknown"

    clean_title = (title or "").strip()
    if clean_title.lower().startswith("new arrival"):
        normalized = "used"
    elif CPO_RE.match(clean_title):
        normalized = "cpo"
    elif USED_RE.match(clean_title):
        normalized = "used"
    elif NEW_RE.match(clean_title):
        normalized = "new"

    if not verified_new and is_implausible_new(normalized, clean_title, year, current_year):
        return "unknown"
    return normalized


def is_implausible_new(condition: str, title: str, year: int, current_year: int) -> bool:
    return (
        (condition or "").lower() == "new"
        and year < current_year - 1
        and not NEW_OLD_STOCK_RE.search(title or "")
    )
