from __future__ import annotations

import re

from car_compare.models import VehicleQuery
from car_compare.trim_match import has_conflicting_trim_variant, trim_tokens
from car_compare.vehicle_catalog import source_model_profile


TOKEN_RE = re.compile(r"[a-z0-9]+")


def matches_vehicle_text(request: VehicleQuery, title: str, trim: str = "", source: str = "") -> bool:
    return vehicle_text_match_score(request, title, trim, source)["accepted"]


def vehicle_text_match_score(request: VehicleQuery, title: str, trim: str = "", source: str = "") -> dict[str, object]:
    if not request.make and not request.model:
        return {
            "accepted": True,
            "confidence": "unrestricted",
            "score": 1.0,
            "missing": [],
            "excluded": [],
        }
    if source == "sample":
        return {
            "accepted": True,
            "confidence": "sample",
            "score": 1.0,
            "missing": [],
            "excluded": [],
        }

    haystack = f"{title} {trim}"
    tokens = set(_tokens(haystack))
    make_tokens = _tokens(request.make)

    profile = source_model_profile(request.make, request.model, request.trim, "matching")
    required = _tokens(" ".join(profile["required_keywords"]))
    exclude = set(_tokens(" ".join(profile["exclude_keywords"])))
    missing_make = [token for token in make_tokens if token not in tokens]
    missing_required = [token for token in required if token not in tokens]
    excluded = sorted(tokens & exclude)
    missing = sorted(set(missing_make + missing_required))
    trim_conflict = request.trim and has_conflicting_trim_variant(request, haystack)
    accepted = not missing and not excluded and not trim_conflict
    matched_count = max(0, len(required) - len(set(missing_required)))
    denominator = max(1, len(required))
    score = matched_count / denominator
    if excluded:
        score = min(score, 0.2)
    if missing_make:
        score = min(score, 0.4)

    if not accepted:
        confidence = "rejected_trim_variant" if trim_conflict else "rejected_excluded" if excluded else "rejected_missing_tokens"
    elif request.trim:
        confidence = "exact_model_trim"
    else:
        confidence = "exact_model_all_trims"

    return {
        "accepted": accepted,
        "confidence": confidence,
        "score": round(score, 3),
        "missing": missing,
        "excluded": sorted([*excluded, *(["trim_variant"] if trim_conflict else [])]),
    }


def _tokens(value: str) -> list[str]:
    return trim_tokens(value)


def _split_attached_terms(value: str) -> str:
    replacements = {
        r"\b(m[2345])competition\b": r"\1 competition",
        r"\b(m[2345])comp\b": r"\1 competition",
        r"\bf\s*[- ]?\s*(150|250|350)\b": r"f \1",
        r"\b(cr|hr)\s*-?\s*v\b": r"\1 v",
        r"\b(cx)\s*-?\s*(30|5|50|70|90)\b": r"\1 \2",
        r"\bmodel\s*([s3xy])\b": r"model \1",
        r"\bcyber\s*truck\b": "cybertruck",
        r"\bioniq\s*([569])\b": r"ioniq \1",
        r"\bid\s*\.?\s*4\b": "id 4",
        r"\b(lc|ls|lx|rx|gx|nx|tx|is|es|rc)(\d{3}h?)\b": r"\1 \2",
        r"\b(gt)(c)\b": r"\1c",
    }
    result = value
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result)
    return result
