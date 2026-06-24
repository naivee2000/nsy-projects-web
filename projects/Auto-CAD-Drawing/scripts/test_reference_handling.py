#!/usr/bin/env python3
"""Check that every reference PDF is classified and routed safely."""

from __future__ import annotations

from pathlib import Path

from generator_registry import analyze_uploads
from scan_reference_pdfs import ROOT, scan


def main() -> int:
    items = scan()
    if len(items) < 8:
        print(f"FAIL: expected at least 8 reference PDFs, found {len(items)}")
        return 1

    by_project = {item.get("project_id"): item for item in items if item.get("project_id")}
    for required in ("CPX26051", "CPX25034", "CPX25063"):
        if required not in by_project:
            print(f"FAIL: missing detected project {required}")
            return 1

    cpx26051_path = ROOT / by_project["CPX26051"]["path"]
    cpx26051_result = analyze_uploads([cpx26051_path])
    if cpx26051_result["status"] != "supported" or cpx26051_result["generator"] != "level_sensor":
        print("FAIL: CPX26051 did not route to the reusable level_sensor generator")
        return 1

    cpx25034_final = next(
        (item for item in items if item.get("project_id") == "CPX25034" and item.get("kind") == "cargo-safety"),
        None,
    )
    if not cpx25034_final:
        print("FAIL: missing CPX25034 cargo-safety final drawing")
        return 1
    cpx25034_result = analyze_uploads([ROOT / cpx25034_final["path"]])
    if cpx25034_result["status"] != "supported" or cpx25034_result["generator"] != "level_sensor":
        print("FAIL: CPX25034 final drawing did not route to the reusable level_sensor generator")
        return 1

    cpx25034_reference_only = next(
        (item for item in items if item.get("project_id") == "CPX25034" and item.get("kind") == "unknown"),
        None,
    )
    if cpx25034_reference_only:
        result = analyze_uploads([ROOT / cpx25034_reference_only["path"]])
        if result["status"] != "unsupported":
            print("FAIL: CPX25034 reference-only PDF should not generate by itself")
            return 1

    path = ROOT / by_project["CPX25063"]["path"]
    result = analyze_uploads([path])
    if result["status"] != "unsupported":
        print("FAIL: CPX25063 should be unsupported until a generator is implemented")
        return 1

    print("OK: reference scan covers all PDFs")
    print("OK: CPX26051 routes to the reusable level_sensor generator")
    print("OK: CPX25034 final drawing routes to the reusable level_sensor generator")
    print("OK: CPX25034 reference-only PDFs and CPX25063 are safely blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
