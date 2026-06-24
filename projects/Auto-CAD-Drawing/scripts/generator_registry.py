#!/usr/bin/env python3
"""Route analyzed PDFs to the available CAD generators."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scan_reference_pdfs import summarize_pdf


SUPPORTED_PROJECTS = {
    "CPX26051": {
        "generator": "level_sensor",
        "data_file": "data/cpx26051_sensors.json",
        "output_dir": "output/cpx26051",
        "primary_sensor_model": "STK333-AR2",
        "required_kinds": ["level-measuring"],
        "description": "600-ton crane vessel liquid-level measuring sheets using the reusable STK333-AR2 level-sensor template",
    },
    "CPX25034": {
        "generator": "level_sensor",
        "data_file": "data/cpx25034_stk333_ar2_sensors.json",
        "output_dir": "output/cpx25034",
        "primary_sensor_model": "STK333-AR2",
        "required_kinds": ["cargo-safety"],
        "description": "7300DWT cargo-safety package STK333-AR2 tank level-sensor sheet using the reusable level-sensor template",
    }
}

SUPPORTED_GENERATORS = {
    "level_sensor": {
        "description": "DONJUN level-sensor circuit/overview drawings from normalized sensor data.",
        "supported_sensor_models": ["STK333-AR2"],
    }
}

KNOWN_UNSUPPORTED = {
    "CPX25063": "Valve remote control drawing generator is not implemented yet.",
}


def project_requirements_met(project_id: str, summaries: list[dict[str, Any]]) -> bool:
    config = SUPPORTED_PROJECTS[project_id]
    required_kinds = set(config.get("required_kinds", []))
    if not required_kinds:
        return True
    return any(item.get("project_id") == project_id and item.get("kind") in required_kinds for item in summaries)


def project_requirement_message(project_id: str) -> str:
    config = SUPPORTED_PROJECTS[project_id]
    required_kinds = ", ".join(config.get("required_kinds", []))
    if required_kinds:
        return f"{project_id} is supported when the upload includes a recognized {required_kinds} final drawing PDF."
    return f"{project_id} is supported."


def analyze_uploads(paths: list[Path]) -> dict[str, Any]:
    summaries = [summarize_pdf(path) for path in paths]
    project_ids = sorted({item.get("project_id") for item in summaries if item.get("project_id")})
    supported = [
        project_id
        for project_id in project_ids
        if project_id in SUPPORTED_PROJECTS and project_requirements_met(project_id, summaries)
    ]

    if not paths:
        return {
            "status": "unsupported",
            "generator": None,
            "project_id": None,
            "message": "Upload at least one PDF before generating CAD output.",
            "uploads": summaries,
        }

    if len(supported) == 1:
        project_id = supported[0]
        return {
            "status": "supported",
            "generator": SUPPORTED_PROJECTS[project_id]["generator"],
            "project_id": project_id,
            "message": SUPPORTED_PROJECTS[project_id]["description"],
            "uploads": summaries,
        }

    if len(supported) > 1:
        return {
            "status": "unsupported",
            "generator": None,
            "project_id": None,
            "message": f"Multiple supported projects were uploaded together: {', '.join(supported)}.",
            "uploads": summaries,
        }

    unsupported_reasons = [KNOWN_UNSUPPORTED[project_id] for project_id in project_ids if project_id in KNOWN_UNSUPPORTED]
    if unsupported_reasons:
        message = " ".join(unsupported_reasons)
    elif project_ids:
        requirement_messages = [
            project_requirement_message(project_id)
            for project_id in project_ids
            if project_id in SUPPORTED_PROJECTS and not project_requirements_met(project_id, summaries)
        ]
        if requirement_messages:
            message = " ".join(requirement_messages)
        else:
            message = f"No generator is registered for uploaded project(s): {', '.join(project_ids)}."
    else:
        kinds = sorted({item.get("kind") for item in summaries if item.get("kind")})
        message = "No supported generator matched these uploads."
        if kinds:
            message += f" Detected kind(s): {', '.join(kinds)}."

    return {
        "status": "unsupported",
        "generator": None,
        "project_id": None,
        "message": message,
        "uploads": summaries,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdfs", nargs="*", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze_uploads(args.pdfs), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
