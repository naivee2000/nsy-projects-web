#!/usr/bin/env python3
"""Screen project PDFs for reusable sensor-model drawing candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TERMS = (
    "STK333-AR2",
    "STK333",
    "压电式液位传感器",
    "液位传感器",
    "Level Sensor",
)


def matching_lines(text: str, terms: list[str]) -> list[str]:
    lines = []
    lowered_terms = [term.lower() for term in terms]
    for line in text.splitlines():
        if any(term in line.lower() for term in lowered_terms):
            lines.append(" ".join(line.split()))
    return lines


def screen_pdf(path: Path, terms: list[str], max_context_lines: int) -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    with pdfplumber.open(path) as doc:
        for index, page in enumerate(doc.pages, start=1):
            text = page.extract_text() or ""
            found_terms = [term for term in terms if term.lower() in text.lower()]
            if not found_terms:
                continue
            lines = matching_lines(text, terms)
            hits.append(
                {
                    "page": index,
                    "terms": found_terms,
                    "context": lines[:max_context_lines],
                }
            )
    return {
        "path": str(path.relative_to(ROOT)),
        "hit_pages": len(hits),
        "hits": hits,
    }


def screen(root: Path = ROOT, terms: list[str] | None = None, max_context_lines: int = 8) -> list[dict[str, Any]]:
    active_terms = terms or list(DEFAULT_TERMS)
    results = []
    for pdf in sorted(root.rglob("*.pdf")):
        result = screen_pdf(pdf, active_terms, max_context_lines)
        if result["hit_pages"]:
            results.append(result)
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--term", action="append", help="Term to search for. Can be passed more than once.")
    parser.add_argument("--max-context-lines", type=int, default=8)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    terms = args.term if args.term else list(DEFAULT_TERMS)
    print(json.dumps(screen(terms=terms, max_context_lines=args.max_context_lines), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
