#!/usr/bin/env python3
"""Verify a normalized level-sensor project data file."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from level_sensor_generator import DEFAULT_DATA_PATH, load_data, load_device_models, validate_level_sensor_project


def fail(message: str) -> None:
    raise AssertionError(message)


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
        required_text = [sheet["drawing_no"], sheet["current_page"], sheet.get("terminal_strip", "TB1")]
        for required in required_text:
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
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--require-proofs", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        data = load_data(args.data)
        messages = validate_level_sensor_project(data, load_device_models())
        if args.output_dir:
            messages.extend(verify_outputs(data, args.output_dir, require_proofs=args.require_proofs))
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1

    for message in messages:
        print(f"OK: {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
