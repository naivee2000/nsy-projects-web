from __future__ import annotations

import json
import subprocess
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from car_compare.models import VehicleQuery
from car_compare.parser import parse_vehicle_query
from car_compare.codex_cli import (
    codex_environment,
    codex_login_status,
    codex_reasoning_config_args,
    find_codex_cli,
    normalize_codex_reasoning_effort,
)
from car_compare.capture_cache import ResearchResultCache


GENERATION_RESEARCH_TIMEOUT_SECONDS = 900


@dataclass
class GenerationResearchJob:
    id: str
    query: str
    status: str
    created_at: float
    updated_at: float
    message: str = ""
    result: dict[str, Any] | None = None
    error: str = ""
    codex_path: str = ""
    process_id: int = 0
    started_at: float = 0
    cache_hit: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["createdAt"] = self.created_at
        data["updatedAt"] = self.updated_at
        data["elapsedSeconds"] = max(0, int(time.time() - self.started_at)) if self.started_at else 0
        return data


@dataclass
class GenerationResearchConfig:
    root: Path
    codex_path: str = ""
    codex_reasoning_effort: str = "high"
    dry_run: bool = False
    timeout_seconds: int = GENERATION_RESEARCH_TIMEOUT_SECONDS
    cache_enabled: bool = True
    cache_dir: Path | None = None
    cache_ttl_seconds: int = 3 * 24 * 60 * 60
    jobs_dir: Path = field(init=False)
    cache_path: Path = field(init=False)
    schema_path: Path = field(init=False)
    skill_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.codex_reasoning_effort = normalize_codex_reasoning_effort(
            self.codex_reasoning_effort,
            "high",
        )
        self.jobs_dir = self.root / "data" / "generation_research_jobs"
        self.cache_path = (self.cache_dir or (self.root / "data" / "cache")) / "collector_cache.sqlite3"
        self.schema_path = self.root / "car_compare" / "generation_impact_schema.json"
        self.skill_path = self.root / "skills" / "generation-impact-research"


class GenerationResearchManager:
    def __init__(self, config: GenerationResearchConfig):
        self.config = config
        self.config.jobs_dir.mkdir(parents=True, exist_ok=True)
        self._cache = ResearchResultCache(
            self.config.cache_path,
            enabled=self.config.cache_enabled,
            ttl_seconds=self.config.cache_ttl_seconds,
        )
        self._jobs: dict[str, GenerationResearchJob] = {}
        self._lock = threading.Lock()

    def availability(self) -> dict[str, Any]:
        path = self._codex_path()
        status = codex_login_status(path) if path else codex_login_status(self.config.codex_path)
        skill_ready = (self.config.skill_path / "SKILL.md").exists()
        available = bool(path and status["authenticated"] and skill_ready)
        if available:
            message = "Generation impact researcher ready"
        elif not skill_ready:
            message = "Project-local generation-impact skill is missing."
        elif path and not status["authenticated"]:
            message = status["message"]
        else:
            message = "Codex CLI not found. Install Codex or set CODEX_BIN."
        return {
            "available": available,
            "codexPath": path,
            "codexHome": status["codexHome"],
            "authenticated": status["authenticated"],
            "authMethod": status["authMethod"],
            "skillPath": str(self.config.skill_path),
            "dryRun": self.config.dry_run,
            "codexReasoningEffort": self.config.codex_reasoning_effort,
            "resultCache": self._cache.status(),
            "message": message,
        }

    def start(self, query: str, max_age: int | None = None) -> GenerationResearchJob:
        request = parse_vehicle_query(query)
        if max_age:
            request.max_age = max_age
        cache_identity = _generation_cache_identity(request, self.config.codex_reasoning_effort)
        cached = None if self.config.dry_run else self._cache.load("generation_impact", cache_identity)
        job = GenerationResearchJob(
            id=uuid.uuid4().hex,
            query=request.raw,
            status="completed" if cached else "queued",
            created_at=time.time(),
            updated_at=time.time(),
            message="Reused fresh generation-impact research" if cached else "Queued generation impact research",
            result=normalize_generation_impact(cached) if cached else None,
            codex_path=self._codex_path(),
            cache_hit=bool(cached),
        )
        with self._lock:
            self._jobs[job.id] = job
        if not cached:
            thread = threading.Thread(target=self._run_job, args=(job.id, request), daemon=True)
            thread.start()
        return job

    def get(self, job_id: str) -> GenerationResearchJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def impact_from_job(self, job_id: str) -> dict[str, Any] | None:
        job = self.get(job_id)
        if not job or not job.result:
            return None
        return normalize_generation_impact(job.result)

    def _run_job(self, job_id: str, request: VehicleQuery) -> None:
        self._update(job_id, status="running", message="Starting generation impact research")
        if self.config.dry_run:
            result = _dry_run_generation_impact(request)
            self._write_job_result(job_id, result)
            self._update(job_id, status="completed", message="Dry-run generation research completed", result=result)
            return

        codex_path = self._codex_path()
        if not codex_path:
            self._update(job_id, status="blocked", message="Codex CLI not found.", error="codex_not_found")
            return
        status = codex_login_status(codex_path)
        if not status["authenticated"]:
            self._update(
                job_id,
                status="blocked",
                message="Codex CLI is not logged in for the deployment user.",
                error="codex_not_authenticated",
            )
            return
        if not (self.config.skill_path / "SKILL.md").exists():
            self._update(job_id, status="blocked", message="Project-local generation-impact skill is missing.", error="skill_not_found")
            return

        job_dir = self.config.jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        output_path = job_dir / "generation_impact.json"
        stdout_path = job_dir / "codex_stdout.log"
        stderr_path = job_dir / "codex_stderr.log"
        prompt = build_generation_research_prompt(request, self.config.skill_path)
        command = build_generation_research_command(
            codex_path=codex_path,
            root=self.config.root,
            schema_path=self.config.schema_path,
            output_path=output_path,
            reasoning_effort=self.config.codex_reasoning_effort,
        )
        start_time = time.time()
        try:
            with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open("w", encoding="utf-8") as stderr_file:
                process = subprocess.Popen(
                    command,
                    env=codex_environment(),
                    stdin=subprocess.PIPE,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    text=True,
                )
                self._update(
                    job_id,
                    status="running",
                    message=f"Codex process started (PID {process.pid}).",
                    process_id=process.pid,
                    started_at=start_time,
                )
                if process.stdin:
                    try:
                        process.stdin.write(prompt)
                        process.stdin.close()
                    except BrokenPipeError:
                        pass
                while process.poll() is None:
                    elapsed = int(time.time() - start_time)
                    if elapsed >= self.config.timeout_seconds:
                        process.kill()
                        process.wait()
                        self._update(
                            job_id,
                            status="failed",
                            message=f"Generation research timed out after {_format_elapsed(elapsed)}",
                            error=f"Timed out after {self.config.timeout_seconds} seconds.",
                        )
                        return
                    self._update(
                        job_id,
                        status="running",
                        message=f"Codex is still researching generation impact for {_format_elapsed(elapsed)}.",
                    )
                    time.sleep(min(3, max(1, self.config.timeout_seconds - elapsed)))
                returncode = process.returncode
        except OSError as exc:
            self._update(job_id, status="failed", message="Could not launch Codex generation researcher", error=str(exc))
            return

        if returncode != 0:
            error_text = _clean_error(_read_text(stderr_path) or _read_text(stdout_path))
            self._update(job_id, status="failed", message=f"Generation research failed: {error_text}", error=error_text)
            return

        try:
            result = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self._update(job_id, status="failed", message="Codex generation researcher did not produce valid JSON", error=str(exc))
            return

        result = normalize_generation_impact(result)
        if result.get("status") in {"success", "partial"}:
            self._cache.store(
                "generation_impact",
                _generation_cache_identity(request, self.config.codex_reasoning_effort),
                result,
            )
        self._write_job_result(job_id, result)
        final_status = "completed" if result.get("status") in {"success", "partial"} else "blocked"
        self._update(job_id, status=final_status, message=f"Generation research {result.get('status', 'finished')}", result=result)

    def _codex_path(self) -> str:
        return find_codex_cli(self.config.codex_path)

    def _update(self, job_id: str, **updates: Any) -> None:
        with self._lock:
            job = self._jobs[job_id]
            for key, value in updates.items():
                setattr(job, key, value)
            job.updated_at = time.time()

    def _write_job_result(self, job_id: str, result: dict[str, Any]) -> None:
        job_dir = self.config.jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        (job_dir / "generation_impact.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


def build_generation_research_prompt(request: VehicleQuery, skill_path: Path) -> str:
    return f"""
Use the project-local skill at:
{skill_path}

Read that skill's SKILL.md and follow its workflow. Research generation timing and generation-change depreciation impact for this vehicle:

query={request.raw}
make={request.make}
model={request.model}
trim={request.trim or "(none)"}
forecast_horizon_years={request.max_age}

Return only JSON matching the provided schema. Do not edit project files. Do not include Markdown.
""".strip()


def build_generation_research_command(
    codex_path: str,
    root: Path,
    schema_path: Path,
    output_path: Path,
    reasoning_effort: str = "high",
) -> list[str]:
    return [
        codex_path,
        "--ask-for-approval",
        "never",
        "exec",
        *codex_reasoning_config_args(reasoning_effort, "high"),
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--output-schema",
        str(schema_path),
        "-o",
        str(output_path),
        "-C",
        str(root),
        "-",
    ]


def _generation_cache_identity(request: VehicleQuery, reasoning_effort: str = "high") -> dict[str, Any]:
    return {
        "make": request.make.strip().casefold(),
        "model": request.model.strip().casefold(),
        "trim": request.trim.strip().casefold(),
        "max_age": int(request.max_age),
        "reasoning_effort": normalize_codex_reasoning_effort(reasoning_effort, "high"),
    }


def normalize_generation_impact(result: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(result)
    normalized["status"] = str(normalized.get("status") or "blocked")
    normalized["query"] = str(normalized.get("query") or "")
    normalized["notes"] = [str(item) for item in normalized.get("notes") or [] if str(item).strip()]
    normalized["sources"] = _normalize_sources(normalized.get("sources") or [])
    normalized["adjustments"] = _normalize_adjustments(normalized.get("adjustments") or [])
    return normalized


def _normalize_adjustments(items: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            age = int(item.get("age"))
            extra_pct = float(item.get("extra_depreciation_pct"))
        except (TypeError, ValueError):
            continue
        if age <= 0 or not (0 < extra_pct < 0.5):
            continue
        rows.append(
            {
                "age": age,
                "calendar_year": _optional_int(item.get("calendar_year")),
                "extra_depreciation_pct": round(max(0.0, min(0.35, extra_pct)), 4),
                "label": str(item.get("label") or "Generation adjustment"),
                "basis": str(item.get("basis") or item.get("rationale") or ""),
            }
        )
    return sorted(rows, key=lambda row: row["age"])


def _normalize_sources(items: list[Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "title": str(item.get("title") or item.get("source") or ""),
                "url": str(item.get("url") or ""),
                "publisher": str(item.get("publisher") or ""),
                "date": str(item.get("date") or ""),
                "notes": str(item.get("notes") or ""),
            }
        )
    return rows


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _dry_run_generation_impact(request: VehicleQuery) -> dict[str, Any]:
    return {
        "query": request.raw,
        "status": "partial",
        "vehicle": {
            "make": request.make,
            "model": request.model,
            "trim": request.trim,
        },
        "current_generation": {
            "name": "Dry-run current generation",
            "start_model_year": 2021,
            "end_model_year": None,
            "confidence": "low",
            "notes": "Dry-run placeholder for local testing.",
        },
        "next_generation": {
            "expected_model_year": 2028,
            "confidence": "low",
            "notes": "Dry-run placeholder; replace with Codex research.",
        },
        "impact_estimate": {
            "extra_drop_pct": 0.06,
            "follow_on_extra_drop_pct": 0.02,
            "confidence": "low",
            "rationale": "Dry-run placeholder adjustment.",
        },
        "adjustments": [
            {
                "age": 2,
                "calendar_year": 2028,
                "extra_depreciation_pct": 0.06,
                "label": "Dry-run new generation shock",
                "basis": "Placeholder result for integration testing.",
            },
            {
                "age": 3,
                "calendar_year": 2029,
                "extra_depreciation_pct": 0.02,
                "label": "Dry-run follow-on shock",
                "basis": "Placeholder result for integration testing.",
            },
        ],
        "historical_transitions": [],
        "sources": [],
        "notes": ["Dry-run result. Do not use for actual valuation."],
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _clean_error(raw: str) -> str:
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    return " ".join(lines[-4:])[:600] if lines else "Unknown error"


def _format_elapsed(seconds: int) -> str:
    minutes, secs = divmod(max(0, int(seconds)), 60)
    hours, mins = divmod(minutes, 60)
    if hours:
        return f"{hours}h {mins}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"
