#!/usr/bin/env python3
"""Remove runtime-only files from the Auto CAD Drawing project."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIRS = [
    ROOT / "output" / "web_jobs",
    ROOT / "tmp" / "pdfs",
]


def remove_pycache() -> list[Path]:
    removed: list[Path] = []
    for path in ROOT.rglob("__pycache__"):
        if path.is_dir():
            shutil.rmtree(path)
            removed.append(path)
    for path in ROOT.rglob("*.pyc"):
        if path.is_file():
            path.unlink()
            removed.append(path)
    return removed


def remove_ds_store() -> list[Path]:
    removed: list[Path] = []
    for path in ROOT.rglob(".DS_Store"):
        if path.is_file():
            path.unlink()
            removed.append(path)
    return removed


def remove_runtime_jobs() -> list[Path]:
    removed: list[Path] = []
    for path in RUNTIME_DIRS:
        if path.exists():
            shutil.rmtree(path)
            removed.append(path)
        path.mkdir(parents=True, exist_ok=True)
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep-jobs", action="store_true", help="Leave output/web_jobs in place.")
    args = parser.parse_args()

    removed = []
    removed.extend(remove_pycache())
    removed.extend(remove_ds_store())
    if not args.keep_jobs:
        removed.extend(remove_runtime_jobs())

    for path in removed:
        print(f"removed {path.relative_to(ROOT)}")
    if not removed:
        print("nothing to clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
