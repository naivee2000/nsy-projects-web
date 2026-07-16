from __future__ import annotations

import re

from car_compare.models import VehicleQuery
from car_compare.vehicle_catalog import trim_candidates, trim_scope_profile


TOKEN_RE = re.compile(r"[a-z0-9]+")
BODY_STYLE_TOKENS = {"cabriolet", "convertible", "coupe", "hatchback", "roadster", "sedan", "suv", "wagon"}
M4_COMPETITION_FAMILY_EXCLUSIONS = {"cs", "csl", "gts", "gt3"}
MENTION_ONLY_TOKENS = {"available", "compatible", "option", "optional", "separately", "style", "look"}


def trim_value_matches_request(request: VehicleQuery, value: str) -> bool:
    scope = trim_scope_profile(request.make, request.model, request.trim)
    observed = set(trim_tokens(value))
    if scope["mode"] == "family":
        return set(trim_tokens(str(scope["family"]))) <= observed
    if scope["mode"] == "base":
        return _matches_base_scope(scope, observed)

    requested = set(trim_tokens(request.trim))
    if not requested:
        return False
    if not requested <= observed:
        return False
    return not has_conflicting_trim_variant(request, value)


def has_conflicting_trim_variant(request: VehicleQuery, value: str) -> bool:
    requested = set(trim_tokens(request.trim))
    observed = set(trim_tokens(value))
    if not requested or not observed:
        return False

    scope = trim_scope_profile(request.make, request.model, request.trim)
    if scope["mode"] == "family":
        return not set(trim_tokens(str(scope["family"]))) <= observed
    if scope["mode"] == "base":
        return not _matches_base_scope(scope, observed)

    if is_bmw_m4_competition_family(request):
        return bool(observed & M4_COMPETITION_FAMILY_EXCLUSIONS) or _requested_trim_is_mention_only(request, value)

    recognized = _recognized_catalog_trim(request, value)
    if recognized:
        return set(trim_tokens(recognized)) != requested

    if request.make == "Honda" and request.model == "Civic" and requested == {"ex"}:
        return bool(observed & {"exl", "ext"})

    if request.make == "Ford" and request.model == "Mustang" and "gt" in requested:
        if requested & {"gt350", "gt500", "shelby"}:
            return False
        return bool(observed & {"gt350", "gt500", "shelby"})

    if request.make == "BMW" and request.model == "M3" and requested == {"competition"}:
        return "xdrive" in observed

    return False


def _matches_base_scope(scope: dict[str, object], observed: set[str]) -> bool:
    base_tokens = set(trim_tokens(str(scope.get("base_trim") or "")))
    identifies_base = bool(base_tokens and base_tokens <= observed) or "base" in observed
    variants = {str(item).lower() for item in scope.get("base_variant_tokens") or []}
    return identifies_base and not bool(observed & variants)


def is_bmw_m4_competition_family(request: VehicleQuery) -> bool:
    return (
        request.make == "BMW"
        and request.model == "M4"
        and set(trim_tokens(request.trim)) == {"competition"}
    )


def _recognized_catalog_trim(request: VehicleQuery, value: str) -> str:
    candidates = trim_candidates(request.make, request.model)
    tokens = trim_tokens(value)
    if not candidates or not tokens:
        return ""

    model_tokens = trim_tokens(request.model)
    model_index = _sequence_index(tokens, model_tokens)
    region = tokens[model_index + len(model_tokens) :] if model_index >= 0 else tokens
    searchable = [(token, index) for index, token in enumerate(region) if token not in BODY_STYLE_TOKENS]
    search_tokens = [token for token, _ in searchable]
    requested = set(trim_tokens(request.trim))
    matches: list[tuple[int, int, str]] = []
    for candidate in candidates:
        candidate_tokens = [token for token in trim_tokens(candidate) if token not in BODY_STYLE_TOKENS]
        for index in range(len(search_tokens) - len(candidate_tokens) + 1):
            if search_tokens[index : index + len(candidate_tokens)] != candidate_tokens:
                continue
            original_start = searchable[index][1]
            original_end = searchable[index + len(candidate_tokens) - 1][1] + 1
            trailing = region[original_end : original_end + 3]
            mention_only = bool(set(trailing) & {"package", "option", "available", "separately"})
            if mention_only and set(candidate_tokens) != requested:
                continue
            matches.append((original_start, -len(candidate_tokens), candidate))
            break
    if not matches:
        return ""
    matches.sort()
    return matches[0][2]


def _requested_trim_is_mention_only(request: VehicleQuery, value: str) -> bool:
    tokens = trim_tokens(value)
    requested = trim_tokens(request.trim)
    index = _sequence_index(tokens, requested)
    if index < 0:
        return False
    trailing = set(tokens[index + len(requested) : index + len(requested) + 5])
    return bool(trailing & MENTION_ONLY_TOKENS)


def _sequence_index(haystack: list[str], needle: list[str]) -> int:
    if not needle or len(needle) > len(haystack):
        return -1
    for index in range(len(haystack) - len(needle) + 1):
        if haystack[index : index + len(needle)] == needle:
            return index
    return -1


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
        r"\bcomp\b": "competition",
        r"\bc2s\b": "carrera s",
        r"\bc4s\b": "carrera 4s",
        r"\bc2\b": "carrera",
        r"\bc4\b": "carrera 4",
        r"\bdual\s+motor\b": "awd",
        r"\blr\b": "long range",
    }
    for pattern, replacement in replacements.items():
        normalized = re.sub(pattern, replacement, normalized)
    return TOKEN_RE.findall(normalized)
