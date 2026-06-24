#!/usr/bin/env python3
"""Scan Auto-CAD-Drawing reference PDFs and summarize likely generator candidates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]

PROJECT_ALIASES = {
    "SZ600HG01-TA-E002": "CPX26051",
    "600吨起重船液位测量设备技术协议": "CPX26051",
    "7300液货": "CPX25034",
    "岽俊液货安全设备技术协议": "CPX25034",
    "7300吨取样式可燃气体": "CPX25034",
    "6250DWT（2#）阀门遥控系统技术协议": "CPX25063",
}


def classify_text(text: str) -> str:
    if "DJC-L型液位遥测系统" in text or "液位测量设备技术协议" in text:
        return "level-measuring"
    if "DJC-L型压力" in text or "可燃气体" in text or "液货" in text:
        return "cargo-safety"
    if "DJC-VK" in text or "阀门遥控" in text:
        return "valve-remote"
    return "unknown"


def detect_project_id(path: Path, text: str) -> str | None:
    relative = str(path.relative_to(ROOT)) if path.is_absolute() and ROOT in path.parents else str(path)
    haystack = f"{relative} {path.name} {text}"
    for project_id in ("CPX26051", "CPX25034", "CPX25063"):
        if project_id in haystack:
            return project_id
    for marker, project_id in PROJECT_ALIASES.items():
        if marker in haystack:
            return project_id
    return None


def summarize_pdf(path: Path) -> dict[str, Any]:
    item: dict[str, Any] = {
        "path": str(path.relative_to(ROOT)),
        "size_mb": round(path.stat().st_size / 1024 / 1024, 2),
        "pages": None,
        "kind": "unknown",
        "project_id": None,
        "sample": "",
        "error": None,
    }
    try:
        with pdfplumber.open(path) as pdf:
            item["pages"] = len(pdf.pages)
            samples = []
            for page_number in [1, 3, 9]:
                if page_number <= len(pdf.pages):
                    text = pdf.pages[page_number - 1].extract_text(x_tolerance=1, y_tolerance=3) or ""
                    samples.append(" ".join(text.split()))
            sample = " ".join(samples)
            item["sample"] = sample[:700]
            item["kind"] = classify_text(sample)
            item["project_id"] = detect_project_id(path, sample)
    except Exception as exc:
        item["error"] = f"{type(exc).__name__}: {exc}"
    return item


def scan() -> list[dict[str, Any]]:
    return [summarize_pdf(path) for path in sorted(ROOT.glob("*/*.pdf"))]


def main() -> None:
    print(json.dumps(scan(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
