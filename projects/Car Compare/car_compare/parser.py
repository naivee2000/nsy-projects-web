from __future__ import annotations

import re

from car_compare.models import VehicleQuery
from car_compare.vehicle_catalog import (
    MERCEDES_CLASS_LETTERS,
    MODEL_MAKE_HINTS,
    display_token,
    make_candidates,
    model_candidates,
)

RANGE_WORDS = {"after", "since", "from", "newer", "newer-than"}
STOP_WORDS = {"depreciation", "trend", "value", "values", "price", "prices"}


def parse_vehicle_query(text: str) -> VehicleQuery:
    raw = " ".join((text or "").strip().split())
    if not raw:
        return VehicleQuery(raw="", make="", model="")

    lower = raw.lower()
    start_year = _range_year(lower)
    years = [int(item) for item in re.findall(r"\b(19\d{2}|20\d{2})\b", lower)]
    target_year = None
    if years and start_year is None:
        target_year = years[-1]

    cleaned = _split_attached_terms(lower)
    cleaned = re.sub(r"\b(19\d{2}|20\d{2})\b", " ", cleaned)
    cleaned = re.sub(r"\b(after|since|from|newer than|newer-than)\b", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9+\- ]+", " ", cleaned)
    tokens = [tok for tok in cleaned.split() if tok not in STOP_WORDS]

    make = ""
    make_index = 0
    make_len = 0
    for i in range(len(tokens)):
        for alias_tokens, canonical in make_candidates():
            if tokens[i : i + len(alias_tokens)] == alias_tokens:
                make = canonical
                make_index = i
                make_len = len(alias_tokens)
                break
        if make:
            break

    if not make and tokens and tokens[0] in MODEL_MAKE_HINTS:
        make = MODEL_MAKE_HINTS[tokens[0]]
        make_index = -1
        make_len = 0
    elif not make and tokens:
        make = display_token(tokens[0])
        make_index = 0
        make_len = 1

    remainder = tokens[make_index + make_len :] if make_index >= 0 else tokens
    remainder = [tok for tok in remainder if tok not in RANGE_WORDS]

    model = ""
    model_len = 0
    for model_tokens, canonical in model_candidates(make):
        if remainder[: len(model_tokens)] == model_tokens:
            model = canonical
            model_len = len(model_tokens)
            break

    if not model and remainder:
        model = display_token(remainder[0])
        model_len = 1
    trim = " ".join(display_token(tok) for tok in remainder[model_len:] if tok not in STOP_WORDS)
    trim = _normalize_trim(make, model, trim)

    return VehicleQuery(
        raw=raw,
        make=make,
        model=model,
        trim=trim,
        start_year=start_year,
        target_year=target_year,
        max_age=10,
    )


def _range_year(lower: str) -> int | None:
    match = re.search(r"\b(after|since|from|newer than|newer-than)\s+(19\d{2}|20\d{2})\b", lower)
    if not match:
        return None
    return int(match.group(2))


def _split_attached_terms(text: str) -> str:
    replacements = {
        r"\bx\s+s\s+e\b": "xse",
        r"\bx\s+l\s+e\b": "xle",
        r"\bl\s+e\b": "le",
        r"\bs\s+e\b": "se",
        r"\bf\s*[- ]?\s*(150|250|350)\b": r"f-\1",
        r"\b(cr|hr)\s*-?\s*v\b": r"\1-v",
        r"\b(cx)\s*-?\s*(30|5|50|70|90)\b": r"\1-\2",
        r"\b(mx)\s*-?\s*5\b": r"mx-5",
        r"\bmodel\s*([s3xy])\b": r"model \1",
        r"\bcyber\s*truck\b": "cybertruck",
        r"\bioniq\s*([569])\b": r"ioniq \1",
        r"\bid\s*\.?\s*4\b": "id.4",
        r"\bxdrive\s*(\d{2,3}i?)\b": r"xdrive \1",
        r"\bamg\s+([ces])(\d{2})\b": r"\1 \2 amg",
        r"\b(m[2345])competition\b": r"\1 competition",
        r"\b(m[2345])comp\b": r"\1 competition",
        r"\b(lc|ls|lx|rx|gx|nx|tx|is|es|rc)(\d{3}h?)\b": r"\1 \2",
        r"\b(\d{3})(i|e)\b": r"\1 \2",
        r"\b([ces])(\d{2,3})\b": r"\1 \2",
        r"\b(gl[abces])(\d{2,3})\b": r"\1 \2",
        r"\b(g)(\d{3})\b": r"\1 \2",
        r"\bx\s+drive\b": "xdrive",
        r"\bxdrive\b": "xdrive",
    }
    result = text
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result)
    return result


def _normalize_trim(make: str, model: str, trim: str) -> str:
    parts = trim.split()
    if not parts:
        return trim

    model_parts = model.split()
    if model_parts and [part.lower() for part in parts[: len(model_parts)]] == [part.lower() for part in model_parts]:
        parts = parts[len(model_parts) :]

    if make == "Mercedes-Benz" and model in MERCEDES_CLASS_LETTERS and parts[:1] == [MERCEDES_CLASS_LETTERS[model]]:
        parts = parts[1:]

    if make == "BMW" and len(parts) >= 2 and parts[0].isdigit() and parts[1].lower() in {"i", "e"}:
        parts = [parts[0] + parts[1].lower(), *parts[2:]]
    if make == "BMW" and len(parts) >= 2 and parts[0].lower() == "xdrive" and re.match(r"^\d{2,3}i?$", parts[1].lower()):
        parts = ["xDrive" + parts[1].lower(), *parts[2:]]

    return " ".join(parts)
