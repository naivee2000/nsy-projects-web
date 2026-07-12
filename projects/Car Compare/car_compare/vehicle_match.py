from __future__ import annotations

import re

from car_compare.models import VehicleQuery
from car_compare.trim_match import has_conflicting_trim_variant, trim_tokens
from car_compare.vehicle_catalog import MODEL_CATALOG, make_aliases, source_model_profile


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
    haystack = f"{title} {trim}"
    tokens = set(_tokens(haystack))
    canonical_make_tokens = set(_tokens(request.make))
    make_groups = [set(_tokens(alias)) for alias in make_aliases(request.make)]
    make_matched = any(group and group <= tokens for group in make_groups)

    profile = source_model_profile(request.make, request.model, request.trim, "matching")
    required = [
        token
        for token in _tokens(" ".join(profile["required_keywords"]))
        if token not in canonical_make_tokens
    ]
    if _bmw_family_trim_identifies_model(request, tokens):
        family_tokens = set(_tokens(request.model))
        required = [token for token in required if token not in family_tokens]
    exclude = set(_tokens(" ".join(profile["exclude_keywords"])))
    missing_make = [] if make_matched else sorted(canonical_make_tokens)
    missing_required = [token for token in required if token not in tokens]
    excluded = sorted(tokens & exclude)
    missing = sorted(set(missing_make + missing_required))
    model_conflict = _has_conflicting_model_variant(request, haystack)
    trim_conflict = request.trim and has_conflicting_trim_variant(request, haystack)
    accepted = not missing and not excluded and not model_conflict and not trim_conflict
    matched_count = max(0, len(required) - len(set(missing_required)))
    denominator = max(1, len(required))
    score = matched_count / denominator
    if excluded:
        score = min(score, 0.2)
    if model_conflict:
        score = min(score, 0.2)
    if missing_make:
        score = min(score, 0.4)

    if not accepted:
        confidence = (
            "rejected_model_variant"
            if model_conflict
            else "rejected_trim_variant"
            if trim_conflict
            else "rejected_excluded"
            if excluded
            else "rejected_missing_tokens"
        )
    elif request.trim:
        confidence = "exact_model_trim"
    else:
        confidence = "exact_model_all_trims"

    return {
        "accepted": accepted,
        "confidence": confidence,
        "score": round(score, 3),
        "missing": missing,
        "excluded": sorted(
            [
                *excluded,
                *(["model_variant"] if model_conflict else []),
                *(["trim_variant"] if trim_conflict else []),
            ]
        ),
    }


def _has_conflicting_model_variant(request: VehicleQuery, value: str) -> bool:
    requested_tokens = _tokens(request.model)
    requested = set(requested_tokens)
    observed = _tokens(value)
    if not requested or not observed:
        return False
    for sibling in MODEL_CATALOG.get(request.make, []):
        sibling_sequence = _tokens(sibling)
        sibling_tokens = set(sibling_sequence)
        index = _sequence_index(observed, sibling_sequence)
        if not requested < sibling_tokens or index < 0:
            continue
        if requested < sibling_tokens:
            return True
    return False


def _bmw_family_trim_identifies_model(request: VehicleQuery, observed: set[str]) -> bool:
    if request.make != "BMW" or request.model not in {"3 Series", "4 Series"}:
        return False
    requested_trim = set(_tokens(request.trim))
    if not requested_trim or not requested_trim <= observed:
        return False
    primary = next(iter(_tokens(request.trim)), "")
    return bool(re.fullmatch(r"m?[34]\d{2}[ie]?", primary))


def _contains_token_sequence(haystack: list[str], needle: list[str]) -> bool:
    if not needle or len(needle) > len(haystack):
        return False
    return any(haystack[index : index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1))


def _sequence_index(haystack: list[str], needle: list[str]) -> int:
    if not needle or len(needle) > len(haystack):
        return -1
    for index in range(len(haystack) - len(needle) + 1):
        if haystack[index : index + len(needle)] == needle:
            return index
    return -1


def _tokens(value: str) -> list[str]:
    return trim_tokens(_split_attached_terms((value or "").lower()))


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
        r"\b(gl[abces])\s*(\d{2,3})\b": r"\1 \2",
        r"\b(cla|cle)\s*(\d{2,3})\b": r"\1 \2",
        r"\b([cesg])\s*(\d{2,3})\b": r"\1 \2",
        r"\b(gt)(c)\b": r"\1c",
    }
    result = value
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result)
    return result
