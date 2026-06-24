#!/usr/bin/env python3
"""Generate a registered level-sensor project."""

from __future__ import annotations

import argparse
from pathlib import Path

from generator_registry import SUPPORTED_PROJECTS
from level_sensor_generator import generate


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_id", choices=sorted(SUPPORTED_PROJECTS))
    parser.add_argument("--no-proof", action="store_true", help="Skip PNG/PDF proof rendering.")
    parser.add_argument("--output-dir", type=Path, help="Override the registered output directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = SUPPORTED_PROJECTS[args.project_id]
    if config["generator"] != "level_sensor":
        raise SystemExit(f"{args.project_id} does not use the level_sensor generator")
    data_path = ROOT / config["data_file"]
    output_dir = args.output_dir or (ROOT / config["output_dir"])
    generate(proof=not args.no_proof, output_dir=output_dir, data_path=data_path)


if __name__ == "__main__":
    main()
