from __future__ import annotations

import re
from typing import Any

from car_compare.models import VehicleQuery
from car_compare.vehicle_catalog import MAKE_ALIASES, MODEL_CATALOG, source_model_profile


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

    chips = [
        _chip("make", "Make", request.make or "Unknown", "exact" if request.make else "unknown", _make_confidence(request.make)),
        _chip("model", "Model", request.model or "Unknown", "exact" if request.model else "unknown", _model_confidence(request)),
        _chip("trim", "Trim", request.trim or "All trims", "exact" if request.trim else "all", "high" if request.trim else "broad"),
        _chip("year", "Years", _year_label(request), _year_mode(request), "high" if (request.start_year or request.target_year) else "broad"),
        _chip("body_style", "Body", body_style or "All body styles", "exact" if body_style else "all", "medium" if body_style else "broad"),
        _chip("drivetrain", "Drivetrain", drivetrain or "All drivetrains", "exact" if drivetrain else "all", "medium" if drivetrain else "broad"),
        _chip("powertrain", "Powertrain", powertrain or "All powertrains", "exact" if powertrain else "all", "medium" if powertrain else "broad"),
    ]

    include_all = [chip["key"] for chip in chips if chip["mode"] == "all"]
    exact = {chip["key"]: chip["value"] for chip in chips if chip["mode"] in {"exact", "range"}}
    warnings = _warnings(request, include_all)

    confidence = _overall_confidence(chips, warnings)
    return {
        "canonical": request.display_name,
        "confidence": confidence,
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


def _warnings(request: VehicleQuery, include_all: list[str]) -> list[str]:
    warnings: list[str] = []
    if not request.make or not request.model:
        warnings.append("Make or model was not confidently resolved.")
    if "trim" in include_all:
        warnings.append("No trim was specified, so all trims under the resolved model are included.")
    if "body_style" in include_all:
        warnings.append("No body style was specified, so coupe/sedan/SUV/convertible variants are included when the model matches.")
    if "drivetrain" in include_all:
        warnings.append("No drivetrain was specified, so AWD/RWD/FWD/4WD variants are included when the model matches.")
    return warnings


def _overall_confidence(chips: list[dict[str, str]], warnings: list[str]) -> str:
    if any(chip["mode"] == "unknown" for chip in chips[:2]):
        return "low"
    if warnings and any("not confidently" in warning for warning in warnings):
        return "low"
    exact_count = sum(1 for chip in chips if chip["mode"] in {"exact", "range"})
    return "high" if exact_count >= 3 else "medium"


def _first_match(tokens: list[str], mapping: dict[str, str]) -> str:
    token_set = set(tokens)
    for token, display in mapping.items():
        if token in token_set:
            return display
    return ""


def _tokens(value: str) -> list[str]:
    normalized = (value or "").lower()
    normalized = re.sub(r"\bx\s+drive\b", "xdrive", normalized)
    normalized = re.sub(r"\b4\s*matic\b", "4matic", normalized)
    normalized = re.sub(r"\bplug\s*-?\s*in\b", "plug-in", normalized)
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", normalized)
