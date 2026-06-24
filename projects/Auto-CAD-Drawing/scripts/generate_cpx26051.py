#!/usr/bin/env python3
"""Generate the CPX26051 level-sensor CAD sheets.

This is a compatibility wrapper around the reusable level-sensor generator.
Keep project-specific defaults here; keep STK333-AR2 drawing logic in
level_sensor_generator.py.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from level_sensor_generator import DEFAULT_DATA_PATH, OUTPUT_DIR, generate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        action="append",
        help="Generate only this output stem, e.g. DJC-26051-04-01-page-15. Can be passed more than once.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory for generated DXF and proof files.",
    )
    parser.add_argument("--no-proof", action="store_true", help="Skip PNG/PDF proof rendering.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected = set(args.only) if args.only else None
    generate(selected=selected, proof=not args.no_proof, output_dir=args.output_dir, data_path=DEFAULT_DATA_PATH)


if __name__ == "__main__":
    main()
