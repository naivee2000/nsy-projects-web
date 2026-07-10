from __future__ import annotations

import asyncio
import json
import importlib.util
import shutil
import sys
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from generator_registry import (  # noqa: E402
    KNOWN_UNSUPPORTED,
    SUPPORTED_GENERATORS,
    SUPPORTED_PROJECTS,
    analyze_uploads,
    project_requirement_message,
)
from codex_advisory import advisory_enabled, advisory_status, analyze_rejected_upload  # noqa: E402
from level_sensor_generator import (  # noqa: E402
    generate as generate_level_sensor,
    load_data as load_level_sensor_data,
    load_device_models,
    validate_level_sensor_project,
)
from scan_reference_pdfs import scan as scan_reference_pdfs  # noqa: E402
from verify_cpx26051 import load_data as load_cpx26051_data, verify_data as verify_cpx26051_data  # noqa: E402
from verify_level_sensor_project import verify_outputs as verify_level_sensor_outputs  # noqa: E402


APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
JOBS_DIR = ROOT / "output" / "web_jobs"
REQUIRED_STATIC_FILES = ("index.html", "styles.css", "app.js")
REQUIRED_DEPENDENCIES = ("ezdxf", "pdfplumber", "PIL", "matplotlib", "fastapi", "uvicorn")

app = FastAPI(title="Auto CAD Drawing")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def safe_job_dir() -> Path:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = str(time.time_ns())[-6:]
    return JOBS_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}-{suffix}"


def zip_directory(source_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path == zip_path or not path.is_file():
                continue
            archive.write(path, path.relative_to(source_dir))


def support_status(project_id: str | None, kind: str | None = None) -> dict[str, str | None]:
    if not project_id:
        return {
            "status": "unknown",
            "message": "No project ID detected.",
        }
    if project_id in SUPPORTED_PROJECTS:
        required_kinds = set(SUPPORTED_PROJECTS[project_id].get("required_kinds", []))
        if required_kinds and kind not in required_kinds:
            return {
                "status": "reference-only",
                "message": project_requirement_message(project_id),
            }
        return {
            "status": "supported",
            "message": SUPPORTED_PROJECTS[project_id]["description"],
        }
    if project_id in KNOWN_UNSUPPORTED:
        return {
            "status": "known-unsupported",
            "message": KNOWN_UNSUPPORTED[project_id],
        }
    return {
        "status": "unsupported",
        "message": "No generator is registered for this project.",
    }


def enriched_reference_scan() -> list[dict]:
    items = scan_reference_pdfs()
    for item in items:
        item["support"] = support_status(item.get("project_id"), item.get("kind"))
    return items


def check_item(name: str, ok: bool, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "ok": ok,
        "message": message,
        "details": details or {},
    }


def expected_baseline_files(data: dict[str, Any], output_dir: Path) -> list[Path]:
    files: list[Path] = []
    for sheet in data.get("sheets", []):
        stem = sheet["output_name"]
        for suffix in ("dxf", "png", "pdf"):
            files.append(output_dir / f"{stem}.{suffix}")
    return files


def build_readiness_payload() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    try:
        data = load_cpx26051_data()
        data_messages = verify_cpx26051_data(data)
        checks.append(
            check_item(
                "cpx26051_data",
                True,
                "Normalized CPX26051 sensor data is valid.",
                {"messages": data_messages},
            )
        )
    except Exception as exc:
        checks.append(check_item("cpx26051_data", False, f"CPX26051 data validation failed: {exc}"))

    project_data_messages: list[str] = []
    try:
        for project_id, config in SUPPORTED_PROJECTS.items():
            if config["generator"] != "level_sensor":
                continue
            project_data = load_level_sensor_data(ROOT / config["data_file"])
            messages = validate_level_sensor_project(project_data)
            project_data_messages.append(f"{project_id}: " + "; ".join(messages))
        checks.append(
            check_item(
                "supported_project_data",
                True,
                "Supported level-sensor project data files are valid.",
                {"messages": project_data_messages},
            )
        )
    except Exception as exc:
        checks.append(check_item("supported_project_data", False, f"Supported project data validation failed: {exc}"))

    try:
        device_models = load_device_models()
        model_ok = "STK333-AR2" in device_models
        checks.append(
            check_item(
                "device_model_library",
                model_ok,
                "STK333-AR2 level-sensor model is available."
                if model_ok
                else "STK333-AR2 level-sensor model is missing.",
                {"models": sorted(device_models)},
            )
        )
    except Exception as exc:
        checks.append(check_item("device_model_library", False, f"Device model library failed: {exc}"))

    dependency_status = {
        name: importlib.util.find_spec(name) is not None
        for name in REQUIRED_DEPENDENCIES
    }
    missing_dependencies = sorted(name for name, ok in dependency_status.items() if not ok)
    checks.append(
        check_item(
            "python_dependencies",
            not missing_dependencies,
            "Required Python packages are importable."
            if not missing_dependencies
            else f"Missing Python package(s): {', '.join(missing_dependencies)}.",
            {"dependencies": dependency_status},
        )
    )

    supported_ok = all(
        SUPPORTED_PROJECTS.get(project_id, {}).get("generator") == "level_sensor"
        for project_id in ("CPX26051", "CPX25034")
    )
    generator_ok = "level_sensor" in SUPPORTED_GENERATORS
    unsupported_ok = {"CPX25063"}.issubset(KNOWN_UNSUPPORTED)
    checks.append(
        check_item(
            "generator_registry",
            supported_ok and generator_ok and unsupported_ok,
            "Generator registry has the reusable level-sensor generator enabled and known future projects blocked."
            if supported_ok and generator_ok and unsupported_ok
            else "Generator registry is missing expected supported/blocked project entries.",
            {
                "supported_generators": sorted(SUPPORTED_GENERATORS),
                "supported_projects": sorted(SUPPORTED_PROJECTS),
                "known_unsupported_projects": sorted(KNOWN_UNSUPPORTED),
            },
        )
    )

    static_files = {name: (STATIC_DIR / name).exists() for name in REQUIRED_STATIC_FILES}
    missing_static = sorted(name for name, ok in static_files.items() if not ok)
    checks.append(
        check_item(
            "static_ui",
            not missing_static,
            "Static browser UI files are present."
            if not missing_static
            else f"Missing static UI file(s): {', '.join(missing_static)}.",
            {"files": static_files},
        )
    )

    codex = advisory_status()
    codex_ok = not codex["enabled"] or codex["ready"]
    checks.append(
        check_item(
            "codex_advisory",
            codex_ok,
            "Codex advisory is ready on this deployment host."
            if codex["ready"]
            else (
                "Codex advisory is disabled; deterministic CAD generation remains available."
                if not codex["enabled"]
                else codex["message"]
            ),
            {
                "enabled": codex["enabled"],
                "available": codex["available"],
                "authenticated": codex["authenticated"],
                "auth_method": codex["auth_method"],
                "codex_bin": codex["codex_bin"],
                "codex_home": codex["codex_home"],
                "schema_ok": codex["schema_ok"],
            },
        )
    )

    output_details: list[dict[str, Any]] = []
    output_ok = True
    output_messages: list[str] = []
    for project_id, config in SUPPORTED_PROJECTS.items():
        if config["generator"] != "level_sensor":
            continue
        project_output_dir = ROOT / config["output_dir"]
        try:
            project_data = load_level_sensor_data(ROOT / config["data_file"])
            missing_outputs = [
                str(path.relative_to(ROOT))
                for path in expected_baseline_files(project_data, project_output_dir)
                if not path.exists()
            ]
            messages = verify_level_sensor_outputs(project_data, output_dir=project_output_dir, require_proofs=True)
            project_ok = not missing_outputs
            if not project_ok:
                output_ok = False
            output_messages.extend(f"{project_id}: {message}" for message in messages)
            output_details.append(
                {
                    "project_id": project_id,
                    "output_dir": str(project_output_dir.relative_to(ROOT)),
                    "missing": missing_outputs,
                    "messages": messages,
                }
            )
        except Exception as exc:
            output_ok = False
            output_details.append(
                {
                    "project_id": project_id,
                    "output_dir": config["output_dir"],
                    "missing": [],
                    "messages": [],
                    "error": str(exc),
                }
            )
    if output_details:
        checks.append(
            check_item(
                "baseline_outputs",
                output_ok,
                "Baseline DXF/PNG/PDF outputs are present and readable for supported projects."
                if output_ok
                else "Baseline output validation failed for one or more supported projects.",
                {
                    "projects": output_details,
                    "messages": output_messages,
                },
            )
        )
    else:
        checks.append(check_item("baseline_outputs", False, "No supported project outputs could be checked."))

    ready = all(item["ok"] for item in checks)
    return {
        "status": "ready" if ready else "not-ready",
        "app": "auto-cad-drawing",
        "supported_generators": SUPPORTED_GENERATORS,
        "supported_projects": sorted(SUPPORTED_PROJECTS),
        "known_unsupported_projects": sorted(KNOWN_UNSUPPORTED),
        "output_formats": ["dxf", "pdf", "png", "zip"],
        "checks": checks,
    }


def read_manifest(job_dir: Path) -> dict | None:
    manifest_path = job_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    manifest["download_available"] = (job_dir / "cad-output.zip").exists()
    if manifest["download_available"]:
        manifest["download_url"] = f"/api/jobs/{job_dir.name}/download"
    return manifest


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/reference-pdfs")
def reference_pdfs() -> JSONResponse:
    return JSONResponse({"items": enriched_reference_scan()})


@app.get("/api/capabilities")
def capabilities() -> JSONResponse:
    return JSONResponse(
        {
            "app": "auto-cad-drawing",
            "supported_generators": SUPPORTED_GENERATORS,
            "supported_sensor_models": load_device_models(),
            "supported_projects": SUPPORTED_PROJECTS,
            "known_unsupported_projects": KNOWN_UNSUPPORTED,
            "output_format": ["dxf", "pdf", "png", "zip"],
        }
    )


@app.get("/api/readiness")
def readiness() -> JSONResponse:
    payload = build_readiness_payload()
    status_code = 200 if payload["status"] == "ready" else 503
    return JSONResponse(payload, status_code=status_code)


@app.get("/api/setup")
def setup() -> JSONResponse:
    codex = advisory_status()
    return JSONResponse(
        {
            "status": "ready" if (not codex["enabled"] or codex["ready"]) else "not-ready",
            "app": "auto-cad-drawing",
            "codex": codex,
            "runtime_root": str(ROOT),
        }
    )


@app.post("/api/jobs")
async def create_job(files: Annotated[list[UploadFile], File()] = []) -> JSONResponse:
    job_dir = safe_job_dir()
    upload_dir = job_dir / "uploads"
    generated_dir = job_dir / "generated"
    upload_dir.mkdir(parents=True, exist_ok=True)
    generated_dir.mkdir(parents=True, exist_ok=True)

    saved_uploads = []
    saved_paths = []
    for upload in files:
        filename = Path(upload.filename or "uploaded.pdf").name
        if not filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Only PDF uploads are accepted: {filename}")
        target = upload_dir / filename
        with target.open("wb") as handle:
            shutil.copyfileobj(upload.file, handle)
        saved_uploads.append(filename)
        saved_paths.append(target)

    analysis = analyze_uploads(saved_paths)
    if analysis["status"] != "supported":
        codex_advisory = None
        if advisory_enabled():
            codex_advisory = await asyncio.to_thread(analyze_rejected_upload, analysis, job_dir)
        manifest = {
            "job": job_dir.name,
            "created_at": datetime.now(UTC).isoformat(),
            "status": analysis["status"],
            "saved_uploads": saved_uploads,
            "analysis": analysis,
            "codex_advisory": codex_advisory,
            "generated_files": [],
            "verification": [],
        }
        (job_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        raise HTTPException(status_code=422, detail=manifest)

    if analysis["generator"] != "level_sensor":
        raise HTTPException(status_code=422, detail=f"Generator is registered but not wired: {analysis['generator']}")

    project_config = SUPPORTED_PROJECTS[analysis["project_id"]]
    data_path = ROOT / project_config["data_file"]
    generated = generate_level_sensor(output_dir=generated_dir, proof=True, data_path=data_path)
    data = load_level_sensor_data(data_path)
    data_messages = validate_level_sensor_project(data)
    if analysis["project_id"] == "CPX26051":
        data_messages.extend(verify_cpx26051_data(data))
    output_messages = verify_level_sensor_outputs(data, output_dir=generated_dir, require_proofs=True)

    manifest = {
        "job": job_dir.name,
        "created_at": datetime.now(UTC).isoformat(),
        "status": "complete",
        "mode": analysis["generator"],
        "project_id": analysis["project_id"],
        "generator": analysis["generator"],
        "primary_sensor_model": project_config["primary_sensor_model"],
        "template_data_file": project_config["data_file"],
        "saved_uploads": saved_uploads,
        "analysis": analysis,
        "generated_files": [path.name for path in generated_dir.iterdir() if path.is_file()],
        "verification": data_messages + output_messages,
        "note": "The reusable level-sensor generator uses normalized project data after upload classification confirms a matching source PDF.",
    }
    (job_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    zip_path = job_dir / "cad-output.zip"
    zip_directory(job_dir, zip_path)
    return JSONResponse(
        {
            "job": job_dir.name,
            "download_url": f"/api/jobs/{job_dir.name}/download",
            "manifest": manifest,
        }
    )


@app.get("/api/jobs")
def list_jobs() -> JSONResponse:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    jobs = []
    for job_dir in sorted([path for path in JOBS_DIR.iterdir() if path.is_dir()], reverse=True):
        manifest = read_manifest(job_dir)
        if manifest:
            jobs.append(manifest)
    return JSONResponse({"jobs": jobs})


@app.get("/api/jobs/{job}/manifest")
def job_manifest(job: str) -> JSONResponse:
    job_dir = JOBS_DIR / Path(job).name
    manifest = read_manifest(job_dir)
    if not manifest:
        raise HTTPException(status_code=404, detail="Job manifest not found")
    return JSONResponse(manifest)


@app.get("/api/jobs/{job}/download")
def download_job(job: str) -> FileResponse:
    job_dir = JOBS_DIR / Path(job).name
    zip_path = job_dir / "cad-output.zip"
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Job output not found")
    return FileResponse(zip_path, filename=f"{job}-cad-output.zip", media_type="application/zip")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
