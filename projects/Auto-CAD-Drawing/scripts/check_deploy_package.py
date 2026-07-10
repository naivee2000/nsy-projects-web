#!/usr/bin/env python3
"""Check that the Auto CAD Drawing folder is ready to deploy or hand off."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REQUIRED_FILES = (
    ".dockerignore",
    ".gitignore",
    "Dockerfile",
    "README.md",
    "app.py",
    "requirements.txt",
    "data/cpx25034_stk333_ar2_sensors.json",
    "data/cpx26051_sensors.json",
    "data/codex_advisory_schema.json",
    "data/device_models.json",
    "docs/deployment.md",
    "docs/reference_pdf_scan.md",
    "scripts/clean_runtime.py",
    "scripts/codex_advisory.py",
    "scripts/codex_runtime.py",
    "scripts/deploy_preflight.py",
    "scripts/generate_cpx26051.py",
    "scripts/generate_level_sensor_project.py",
    "scripts/generator_registry.py",
    "scripts/level_sensor_generator.py",
    "scripts/run_checks.py",
    "scripts/scan_reference_pdfs.py",
    "scripts/screen_sensor_models.py",
    "scripts/smoke_test_app.py",
    "scripts/test_reference_handling.py",
    "scripts/test_codex_runtime.py",
    "scripts/verify_level_sensor_project.py",
    "scripts/verify_cpx26051.py",
    "web/app.py",
    "web/static/app.js",
    "web/static/index.html",
    "web/static/styles.css",
)

REQUIRED_REQUIREMENTS = (
    "ezdxf",
    "pdfplumber",
    "Pillow",
    "matplotlib",
    "fastapi",
    "uvicorn",
    "python-multipart",
)

REQUIRED_IGNORE_PATTERNS = (
    "__pycache__/",
    "*.pyc",
    ".venv/",
    "output/web_jobs/",
    "tmp/",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def check_required_files() -> list[str]:
    missing = [name for name in REQUIRED_FILES if not (ROOT / name).exists()]
    if missing:
        return [f"missing required file: {name}" for name in missing]
    return []


def check_requirements() -> list[str]:
    text = read_text(ROOT / "requirements.txt")
    normalized = text.lower()
    missing = [name for name in REQUIRED_REQUIREMENTS if name.lower() not in normalized]
    if missing:
        return [f"requirements.txt missing dependency: {name}" for name in missing]
    return []


def check_ignored_runtime() -> list[str]:
    errors: list[str] = []
    for filename in (".gitignore", ".dockerignore"):
        text = read_text(ROOT / filename)
        for pattern in REQUIRED_IGNORE_PATTERNS:
            if pattern not in text:
                errors.append(f"{filename} missing ignored runtime pattern: {pattern}")
    return errors


def check_readiness_payload() -> list[str]:
    from web.app import build_readiness_payload

    payload = build_readiness_payload()
    if payload["status"] != "ready":
        failed = [item for item in payload["checks"] if not item["ok"]]
        return [f"readiness check failed: {item['name']} - {item['message']}" for item in failed]

    expected_checks = {
        "cpx26051_data",
        "supported_project_data",
        "device_model_library",
        "python_dependencies",
        "generator_registry",
        "codex_advisory",
        "static_ui",
        "baseline_outputs",
    }
    present_checks = {item["name"] for item in payload["checks"]}
    missing_checks = sorted(expected_checks - present_checks)
    if missing_checks:
        return [f"readiness payload missing check: {name}" for name in missing_checks]
    return []


def collect_baseline_outputs() -> list[str]:
    from web.app import build_readiness_payload

    payload = build_readiness_payload()
    baseline = next(item for item in payload["checks"] if item["name"] == "baseline_outputs")
    outputs: list[str] = []
    for project in baseline["details"]["projects"]:
        output_dir = ROOT / project["output_dir"]
        if output_dir.exists():
            outputs.extend(relative(path) for path in output_dir.iterdir() if path.is_file())
    return sorted(outputs)


def main() -> int:
    checks: list[tuple[str, list[str]]] = [
        ("required files", check_required_files()),
        ("requirements", check_requirements()),
        ("runtime ignores", check_ignored_runtime()),
        ("readiness payload", check_readiness_payload()),
    ]

    errors = [message for _, messages in checks for message in messages]
    if errors:
        for message in errors:
            print(f"FAIL: {message}")
        return 1

    for name, _ in checks:
        print(f"OK: {name}")

    outputs = collect_baseline_outputs()
    print(f"OK: baseline output files: {len(outputs)}")
    for name in outputs:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
