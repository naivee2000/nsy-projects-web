from __future__ import annotations

import re

from car_compare.models import VehicleQuery


TOKEN_RE = re.compile(r"[a-z0-9]+")


def trim_value_matches_request(request: VehicleQuery, value: str) -> bool:
    requested = set(trim_tokens(request.trim))
    if not requested:
        return False
    observed = set(trim_tokens(value))
    if not requested <= observed:
        return False
    return not has_conflicting_trim_variant(request, value)


def has_conflicting_trim_variant(request: VehicleQuery, value: str) -> bool:
    requested = set(trim_tokens(request.trim))
    observed = set(trim_tokens(value))
    if not requested or not observed:
        return False

    if request.make == "Honda" and request.model == "Civic" and requested == {"ex"}:
        return bool(observed & {"exl", "ext"})

    if request.make == "Ford" and request.model == "Mustang" and "gt" in requested:
        if requested & {"gt350", "gt500", "shelby"}:
            return False
        return bool(observed & {"gt350", "gt500", "shelby"})

    if request.make == "Porsche" and request.model == "911" and requested == {"carrera"}:
        return bool(observed & {"4", "4s", "s", "gts", "t", "turbo"})

    if request.make == "BMW" and request.model in {"M3", "M4"} and requested == {"competition"}:
        return "xdrive" in observed

    return False


def trim_tokens(value: str) -> list[str]:
    normalized = (value or "").lower()
    replacements = {
        r"\bx\s+drive\b": "xdrive",
        r"\bxdrive\s*(\d{2,3}i?)\b": r"xdrive \1",
        r"\b4\s*matic\b": "4matic",
        r"\ball\s*[- ]?\s*wheel\s*drive\b": "awd",
        r"\bex\s*[- ]?\s*l\b": "exl",
        r"\bex\s*[- ]?\s*t\b": "ext",
        r"\b(gt)\s*[- ]?\s*(350|500)\b": r"\1\2",
        r"\b(gl[abces])\s*(\d{2,3})\b": r"\1 \2",
        r"\b([cesg])\s*(\d{2,3})\b": r"\1 \2",
        r"\b(lc|ls|lx|rx|gx|nx|tx|is|es|rc)\s*(\d{3}h?)\b": r"\1 \2",
        r"\b(m[2345])competition\b": r"\1 competition",
        r"\b(m[2345])comp\b": r"\1 competition",
    }
    for pattern, replacement in replacements.items():
        normalized = re.sub(pattern, replacement, normalized)
    return TOKEN_RE.findall(normalized)
