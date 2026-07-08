#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize a Car Compare generation-impact JSON file.")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    data = normalize(json.loads(args.input.read_text(encoding="utf-8")))
    payload = json.dumps(data, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


def normalize(data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(data)
    normalized["status"] = str(normalized.get("status") or "blocked")
    normalized["query"] = str(normalized.get("query") or "")
    normalized["notes"] = [str(item) for item in normalized.get("notes") or [] if str(item).strip()]
    normalized["adjustments"] = normalize_adjustments(normalized.get("adjustments") or [])
    return normalized


def normalize_adjustments(items: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            age = int(item.get("age"))
            extra_pct = float(item.get("extra_depreciation_pct"))
        except (TypeError, ValueError):
            continue
        if age <= 0 or not (0 < extra_pct < 0.5):
            continue
        rows.append(
            {
                "age": age,
                "calendar_year": optional_int(item.get("calendar_year")),
                "extra_depreciation_pct": round(max(0.0, min(0.35, extra_pct)), 4),
                "label": str(item.get("label") or "Generation adjustment"),
                "basis": str(item.get("basis") or item.get("rationale") or ""),
            }
        )
    return sorted(rows, key=lambda row: row["age"])


def optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    main()
