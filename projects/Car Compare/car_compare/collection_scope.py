"""Versioned evidence contract shared by collectors, caches and reports."""
from __future__ import annotations

import time
import json
import math
from pathlib import Path
from typing import Any

from car_compare.models import VehicleQuery

REVISIONS = json.loads(Path(__file__).with_name("revisions.json").read_text())
VALIDATION_REVISION = REVISIONS["validation"]
ANALYSIS_REVISION = REVISIONS["analysis"]
COLLECTION_SECONDS = 12 * 60


def query_key(request: VehicleQuery) -> list[Any]:
    return [request.make, request.model, request.trim, request.target_year, request.start_year, request.max_age]


def requested_scope(request: VehicleQuery, years: list[int], conditions: list[str]) -> dict[str, Any]:
    from car_compare.resolver import resolve_vehicle_query
    resolution = resolve_vehicle_query(request)
    chips = {item["key"]: item for item in resolution["chips"]}
    def exact(name: str) -> str:
        item = chips.get(name, {})
        return str(item.get("value") or "") if item.get("mode") == "exact" else ""
    return {"make": request.make, "model": request.model, "trim": request.trim,
            "trim_mode": chips.get("trim", {}).get("mode", "exact"),
            "years": years, "conditions": conditions, "body": exact("body_style"), "drivetrain": exact("drivetrain")}


def verified_scope(request: VehicleQuery, **fields: Any) -> dict[str, Any]:
    return {
        "validation_revision": VALIDATION_REVISION,
        "validation_status": "verified",
        "query_key": query_key(request),
        "geography": "nationwide",
        "captured_at": time.time(),
        "complete": True,
        **fields,
    }


def scope_is_verified(scope: Any, request: VehicleQuery | None = None) -> bool:
    if not isinstance(scope, dict):
        return False
    captured = scope.get("captured_at")
    if not isinstance(captured, (int, float)) or not math.isfinite(captured):
        return False
    if not time.time() - 259200 <= captured <= time.time() + 5:
        return False
    return (
        scope.get("validation_revision") == VALIDATION_REVISION
        and scope.get("validation_status") == "verified"
        and scope.get("geography") == "nationwide"
        and (request is None or scope.get("query_key") == query_key(request))
    )
