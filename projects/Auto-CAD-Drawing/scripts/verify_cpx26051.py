#!/usr/bin/env python3
"""Verify CPX26051 generated CAD data and outputs."""

from __future__ import annotations

import json
import argparse
from pathlib import Path
from typing import Any

from level_sensor_generator import validate_level_sensor_project


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "cpx26051_sensors.json"
OUTPUT_DIR = ROOT / "output" / "cpx26051"


def load_data() -> dict[str, Any]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise AssertionError(message)


def verify_data(data: dict[str, Any]) -> list[str]:
    messages: list[str] = validate_level_sensor_project(data)
    sensors = data["sensors"]
    expected = data["supply_list_expected"]
    side = [s for s in sensors if s["install_type"] == "side-mounted"]
    top = [s for s in sensors if s["install_type"] == "top-mounted"]
    draft = [s for s in sensors if s["measurement"] == "draft"]

    if len(side) != expected["side_mounted_stk333_ar2"]:
        fail(f"side-mounted count mismatch: {len(side)} != {expected['side_mounted_stk333_ar2']}")
    if len(top) != expected["top_mounted_stk333_ar2"]:
        fail(f"top-mounted count mismatch: {len(top)} != {expected['top_mounted_stk333_ar2']}")
    if len(draft) != expected["draft_stk333_ar2"]:
        fail(f"draft count mismatch: {len(draft)} != {expected['draft_stk333_ar2']}")

    messages.append("counts ok: 17 side-mounted, 3 top-mounted, 4 draft")

    tags = [s["lt_tag"] for s in sensors]
    expected_tags = [f"LT{i}" for i in range(1, 25)]
    if tags != expected_tags:
        fail(f"LT tags are not sequential LT1-LT24: {tags}")
    messages.append("LT tag sequence ok: LT1-LT24")

    terminals: list[int] = []
    for sensor in sensors:
        pair = sensor["terminal_pair"]
        if len(pair) != 2 or pair[1] != pair[0] + 1:
            fail(f"bad terminal pair for {sensor['lt_tag']}: {pair}")
        terminals.extend(pair)
    if terminals != list(range(1, 49)):
        fail(f"terminal sequence mismatch: {terminals}")
    messages.append("terminal sequence ok: TB1 1-48")

    expected_sheet_ranges = {
        "15": [f"LT{i}" for i in range(1, 10)],
        "16": [f"LT{i}" for i in range(10, 19)],
        "17": [f"LT{i}" for i in range(19, 25)],
    }
    for page, expected_tags_for_page in expected_sheet_ranges.items():
        actual = [s["lt_tag"] for s in sensors if s["sheet_current_page"] == page]
        if actual != expected_tags_for_page:
            fail(f"sheet {page} tag mismatch: {actual} != {expected_tags_for_page}")
    messages.append("sheet LT ranges ok: page 15, 16, 17")

    for sensor in side:
        if sensor["model"] != "STK333-AR2":
            fail(f"side-mounted sensor model mismatch: {sensor['lt_tag']} {sensor['model']}")
        if sensor["range"] != "0-50kPa":
            fail(f"side-mounted range mismatch: {sensor['lt_tag']} {sensor['range']}")
        if sensor["tail_cable_m"] != 5:
            fail(f"side-mounted tail cable mismatch: {sensor['lt_tag']} {sensor['tail_cable_m']}")
    messages.append("side-mounted specs ok: STK333-AR2, 0-50kPa, 5m tail cable")

    return messages


def verify_outputs(data: dict[str, Any], output_dir: Path, require_proofs: bool = False) -> list[str]:
    messages: list[str] = []
    try:
        import ezdxf
    except Exception as exc:
        fail(f"ezdxf is required to verify DXF files: {exc}")

    for sheet in data["sheets"]:
        stem = sheet["output_name"]
        dxf_path = output_dir / f"{stem}.dxf"
        if not dxf_path.exists():
            fail(f"missing DXF output: {dxf_path}")
        doc = ezdxf.readfile(dxf_path)
        text_values: list[str] = []
        for entity in doc.modelspace():
            if entity.dxftype() == "TEXT":
                text_values.append(entity.dxf.text)
            elif entity.dxftype() == "MTEXT":
                text_values.append(entity.text)
        for required in [sheet["drawing_no"], sheet["current_page"]]:
            if required and not any(required in value for value in text_values):
                fail(f"{dxf_path.name} missing expected text: {required}")
        messages.append(f"DXF ok: {dxf_path.name}")

        if require_proofs:
            for suffix in ("png", "pdf"):
                proof = output_dir / f"{stem}.{suffix}"
                if not proof.exists():
                    fail(f"missing proof output: {proof}")
            messages.append(f"proofs ok: {stem}.png/.pdf")
    return messages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--require-proofs", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_data()
    try:
        messages = verify_data(data)
        messages.extend(verify_outputs(data, output_dir=args.output_dir, require_proofs=args.require_proofs))
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        return 1
    for message in messages:
        print(f"OK: {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
