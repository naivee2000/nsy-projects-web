from __future__ import annotations

import re
from typing import Any

from car_compare.models import VehicleQuery
from car_compare.trim_match import is_bmw_m4_competition_family
from car_compare.vehicle_catalog import MAKE_ALIASES, MODEL_CATALOG, source_model_profile, trim_candidates


BODY_STYLE_TERMS = {
    "coupe": "Coupe",
    "convertible": "Convertible",
    "cabriolet": "Convertible",
    "sedan": "Sedan",
    "suv": "SUV",
    "wagon": "Wagon",
    "hatchback": "Hatchback",
    "truck": "Truck",
    "pickup": "Truck",
    "van": "Van",
    "minivan": "Minivan",
    "roadster": "Roadster",
    "spyder": "Spyder",
}

DRIVETRAIN_TERMS = {
    "awd": "AWD",
    "4wd": "4WD",
    "fwd": "FWD",
    "rwd": "RWD",
    "xdrive": "xDrive",
    "4matic": "4MATIC",
    "quattro": "quattro",
}

POWERTRAIN_TERMS = {
    "hybrid": "Hybrid",
    "phev": "PHEV",
    "plug-in": "Plug-in Hybrid",
    "plugin": "Plug-in Hybrid",
    "electric": "Electric",
    "ev": "EV",
    "diesel": "Diesel",
}


def resolve_vehicle_query(request: VehicleQuery) -> dict[str, Any]:
    raw_tokens = _tokens(request.raw)
    trim_tokens = _tokens(request.trim)
    profile = source_model_profile(request.make, request.model, request.trim, "matching")

    body_style = _first_match(raw_tokens + trim_tokens, BODY_STYLE_TERMS)
    drivetrain = _first_match(raw_tokens + trim_tokens, DRIVETRAIN_TERMS)
    powertrain = _first_match(raw_tokens + trim_tokens, POWERTRAIN_TERMS)
    trim_drivetrain_siblings = _trim_drivetrain_siblings(request)
    drivetrain_mode = "exact" if drivetrain else "constrained" if trim_drivetrain_siblings else "all"
    drivetrain_value = drivetrain or (
        "Constrained by exact trim" if trim_drivetrain_siblings else "All drivetrains"
    )

    chips = [
        _chip("make", "Make", request.make or "Unknown", "exact" if request.make else "unknown", _corrected_confidence(request, "make", _make_confidence(request.make))),
        _chip("model", "Model", request.model or "Unknown", "exact" if request.model else "unknown", _corrected_confidence(request, "model", _model_confidence(request))),
        _chip("trim", "Trim", request.trim or "All trims", "exact" if request.trim else "all", _corrected_confidence(request, "trim", "high" if request.trim else "broad")),
        _chip("year", "Years", _year_label(request), _year_mode(request), "high" if (request.start_year or request.target_year) else "broad"),
        _chip("body_style", "Body", body_style or "All body styles", "exact" if body_style else "all", "medium" if body_style else "broad"),
        _chip(
            "drivetrain",
            "Drivetrain",
            drivetrain_value,
            drivetrain_mode,
            "high" if trim_drivetrain_siblings else "medium" if drivetrain else "broad",
        ),
        _chip("powertrain", "Powertrain", powertrain or "All powertrains", "exact" if powertrain else "all", "medium" if powertrain else "broad"),
    ]

    include_all = [chip["key"] for chip in chips if chip["mode"] == "all"]
    exact = {chip["key"]: chip["value"] for chip in chips if chip["mode"] in {"exact", "range"}}
    warnings = _warnings(request, include_all, trim_drivetrain_siblings)

    confidence = _overall_confidence(chips, warnings)
    return {
        "canonical": request.display_name,
        "confidence": confidence,
        "corrections": list(request.corrections),
        "chips": chips,
        "include_all": include_all,
        "exact": exact,
        "matching": {
            "required_keywords": profile["required_keywords"],
            "exclude_keywords": profile["exclude_keywords"],
            "model_aliases": profile["model_aliases"],
            "rule": "Exact chips restrict collection. All chips are intentionally broad and must not be used to reject rows.",
        },
        "website_rules": [
            "If trim/body/drivetrain/powertrain is All, include every visible variant that passes make/model matching.",
            "If a chip is Exact, require visible listing text or detail-page evidence for that value before collecting the row.",
            "If drivetrain is Constrained by exact trim, reject the named drivetrain sibling variants listed in warnings.",
            "Never infer a missing trim/body/drivetrain from the website filter alone; verify it on the listing row or detail page.",
            "Reject rows with excluded sibling-model tokens even when a website returns them from a broad make page.",
        ],
        "warnings": warnings,
    }


def _chip(key: str, label: str, value: str, mode: str, confidence: str) -> dict[str, str]:
    return {
        "key": key,
        "label": label,
        "value": value,
        "mode": mode,
        "confidence": confidence,
    }


def _make_confidence(make: str) -> str:
    if not make:
        return "low"
    return "high" if make in set(MAKE_ALIASES.values()) else "medium"


def _model_confidence(request: VehicleQuery) -> str:
    if not request.model:
        return "low"
    known_models = set(MODEL_CATALOG.get(request.make, []))
    return "high" if request.model in known_models else "medium"


def _year_label(request: VehicleQuery) -> str:
    if request.start_year:
        return f"{request.start_year}+"
    if request.target_year:
        return str(request.target_year)
    return "All model years"


def _year_mode(request: VehicleQuery) -> str:
    if request.start_year:
        return "range"
    if request.target_year:
        return "exact"
    return "all"


def _warnings(
    request: VehicleQuery,
    include_all: list[str],
    trim_drivetrain_siblings: list[str] | None = None,
) -> list[str]:
    warnings: list[str] = []
    for correction in request.corrections:
        warnings.append(
            f'Corrected {correction["field"]} spelling from "{correction["original"]}" to "{correction["corrected"]}".'
        )
    if not request.make or not request.model:
        warnings.append("Make or model was not confidently resolved.")
    if "trim" in include_all:
        warnings.append("No trim was specified, so all trims under the resolved model are included.")
    if "body_style" in include_all:
        warnings.append("No body style was specified, so coupe/sedan/SUV/convertible variants are included when the model matches.")
    if "drivetrain" in include_all:
        warnings.append("No drivetrain was specified, so AWD/RWD/FWD/4WD variants are included when the model matches.")
    elif trim_drivetrain_siblings:
        warnings.append(
            f'Exact trim "{request.trim}" excludes named drivetrain sibling'
            f'{"s" if len(trim_drivetrain_siblings) != 1 else ""}: '
            + ", ".join(trim_drivetrain_siblings)
            + "."
        )
    if is_bmw_m4_competition_family(request):
        warnings.append(
            "M4 Competition is resolved as a generation-aware family: include G8x Competition body/drivetrain variants "
            "and F82/F83 cars with a verified factory Competition Package; exclude Base, CS, CSL, and GTS variants."
        )
    return warnings


def _overall_confidence(chips: list[dict[str, str]], warnings: list[str]) -> str:
    if any(chip["mode"] == "unknown" for chip in chips[:2]):
        return "low"
    if warnings and any("not confidently" in warning for warning in warnings):
        return "low"
    if any(warning.startswith("Corrected ") for warning in warnings):
        return "medium"
    exact_count = sum(1 for chip in chips if chip["mode"] in {"exact", "range"})
    return "high" if exact_count >= 3 else "medium"


def _corrected_confidence(request: VehicleQuery, field: str, default: str) -> str:
    return "medium" if any(item.get("field") == field for item in request.corrections) else default


def _first_match(tokens: list[str], mapping: dict[str, str]) -> str:
    token_set = set(tokens)
    for token, display in mapping.items():
        if token in token_set:
            return display
    return ""


def _trim_drivetrain_siblings(request: VehicleQuery) -> list[str]:
    if is_bmw_m4_competition_family(request):
        return []
    requested = _tokens(request.trim)
    if not requested:
        return []
    siblings: list[str] = []
    for candidate in trim_candidates(request.make, request.model):
        candidate_tokens = _tokens(candidate)
        if len(candidate_tokens) <= len(requested):
            continue
        if candidate_tokens[: len(requested)] != requested:
            continue
        added = candidate_tokens[len(requested) :]
        if any(token in DRIVETRAIN_TERMS for token in added):
            siblings.append(candidate)
    return sorted(set(siblings))


def _tokens(value: str) -> list[str]:
    normalized = (value or "").lower()
    normalized = re.sub(r"\bx\s+drive\b", "xdrive", normalized)
    normalized = re.sub(r"\b4\s*matic\b", "4matic", normalized)
    normalized = re.sub(r"\bplug\s*-?\s*in\b", "plug-in", normalized)
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", normalized)
