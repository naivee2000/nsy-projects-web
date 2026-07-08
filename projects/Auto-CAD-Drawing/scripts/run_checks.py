#!/usr/bin/env python3
"""Run local regression checks for the Auto CAD Drawing project."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(command: list[str]) -> None:
    printable = " ".join(command)
    print(f"\n$ {printable}")
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=None,
        help="When provided, also run API smoke tests against this running server.",
    )
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Skip regenerating baseline CPX26051 outputs before verification.",
    )
    args = parser.parse_args()

    py_files = [
        "app.py",
        "scripts/check_deploy_package.py",
        "scripts/clean_runtime.py",
        "scripts/generate_cpx26051.py",
        "scripts/generate_level_sensor_project.py",
        "scripts/generator_registry.py",
        "scripts/level_sensor_generator.py",
        "scripts/run_checks.py",
        "scripts/scan_reference_pdfs.py",
        "scripts/screen_sensor_models.py",
        "scripts/smoke_test_app.py",
        "scripts/test_reference_handling.py",
        "scripts/verify_level_sensor_project.py",
        "scripts/verify_cpx26051.py",
        "web/app.py",
    ]
    run([PYTHON, "-m", "py_compile", *py_files])
    run([PYTHON, "scripts/test_reference_handling.py"])
    run([PYTHON, "scripts/verify_level_sensor_project.py"])
    run([PYTHON, "scripts/verify_level_sensor_project.py", "--data", "data/cpx25034_stk333_ar2_sensors.json"])
    if not args.skip_generate:
        run([PYTHON, "scripts/generate_cpx26051.py"])
        run([PYTHON, "scripts/generate_level_sensor_project.py", "CPX25034"])
    run([PYTHON, "scripts/verify_cpx26051.py", "--require-proofs"])
    run(
        [
            PYTHON,
            "scripts/verify_level_sensor_project.py",
            "--data",
            "data/cpx25034_stk333_ar2_sensors.json",
            "--output-dir",
            "output/cpx25034",
            "--require-proofs",
        ]
    )
    run([PYTHON, "scripts/check_deploy_package.py"])
    if args.base_url:
        run([PYTHON, "scripts/smoke_test_app.py", "--base-url", args.base_url])
    print("\nOK: all requested checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
