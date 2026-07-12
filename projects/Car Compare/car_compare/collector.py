from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from car_compare.models import Listing, MSRP, VehicleQuery
from car_compare.parser import parse_vehicle_query
from car_compare.codex_cli import codex_environment, codex_login_status, find_codex_cli
from car_compare.sources.visor_facets import collect_visor_public_facets
from car_compare.sources.source_plan import build_collection_plan
from car_compare.vehicle_match import vehicle_text_match_score


CODEX_TIMEOUT_SECONDS = 900
MIN_MODEL_YEAR = 1980
MAX_SCHEMA_MODEL_YEAR = 2100
MIN_LISTING_PRICE = 500
MAX_LISTING_PRICE = 10_000_000
MIN_MSRP_PRICE = 5_000
MAX_MSRP_PRICE = 10_000_000
# Backward-compatible listing bounds for callers migrating to the split names.
MIN_VEHICLE_PRICE = MIN_LISTING_PRICE
MAX_VEHICLE_PRICE = MAX_LISTING_PRICE
MAX_MILEAGE = 1_000_000
BROWSER_SOURCE_NAMES = {"autotrader_browser", "edmunds_browser"}


@dataclass
class CollectionJob:
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

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["createdAt"] = self.created_at
        data["updatedAt"] = self.updated_at
        if self.started_at:
            data["elapsedSeconds"] = max(0, int(time.time() - self.started_at))
        else:
            data["elapsedSeconds"] = 0
        return data


@dataclass
class CollectorConfig:
    root: Path
    codex_path: str = ""
    dry_run: bool = False
    timeout_seconds: int = CODEX_TIMEOUT_SECONDS
    use_visor_facets: bool = True
    jobs_dir: Path = field(init=False)
    schema_path: Path = field(init=False)
    browser_server_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.jobs_dir = self.root / "data" / "collector_jobs"
        self.schema_path = self.root / "car_compare" / "collector_schema.json"
        self.browser_server_path = self.root / "scripts" / "car_compare_browser_mcp.mjs"


class CollectionManager:
    def __init__(self, config: CollectorConfig):
        self.config = config
        self.config.jobs_dir.mkdir(parents=True, exist_ok=True)
        self._jobs: dict[str, CollectionJob] = {}
        self._lock = threading.Lock()

    def availability(self) -> dict[str, Any]:
        path = self._codex_path()
        status = codex_login_status(path) if path else codex_login_status(self.config.codex_path)
        website_available = bool(path and status["authenticated"])
        visor_available = bool(self.config.use_visor_facets)
        browser_worker_available = self._browser_worker_available()
        persistent_browser = bool(os.environ.get("CAR_COMPARE_BROWSER_CDP_URL", "").strip())
        if website_available and visor_available:
            message = "Visor facets and Codex website collector ready"
        elif website_available:
            message = "Codex website collector ready"
        elif visor_available:
            message = f"Visor facet collector ready; {status['message']}"
        else:
            message = status["message"]
        return {
            "available": bool(visor_available or website_available),
            "visorAvailable": visor_available,
            "websiteCollectorAvailable": website_available,
            "browserWorkerAvailable": browser_worker_available,
            "persistentBrowserConfigured": persistent_browser,
            "auditedWebsiteCollectorAvailable": bool(website_available and browser_worker_available),
            "codexPath": path,
            "codexHome": status["codexHome"],
            "authenticated": status["authenticated"],
            "authMethod": status["authMethod"],
            "dryRun": self.config.dry_run,
            "message": message,
        }

    def start(self, query: str, max_age: int | None = None) -> CollectionJob:
        request = parse_vehicle_query(query)
        if max_age:
            request.max_age = max_age
        job = CollectionJob(
            id=uuid.uuid4().hex,
            query=request.raw,
            status="queued",
            created_at=time.time(),
            updated_at=time.time(),
            message="Queued website collection",
            codex_path=self._codex_path(),
        )
        with self._lock:
            self._jobs[job.id] = job
        thread = threading.Thread(target=self._run_job, args=(job.id, request), daemon=True)
        thread.start()
        return job

    def get(self, job_id: str) -> CollectionJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def listings_from_job(self, job_id: str) -> list[Listing]:
        job = self.get(job_id)
        if not job or not job.result:
            return []
        return listings_from_result(job.result)

    def msrp_from_job(self, job_id: str) -> MSRP | None:
        job = self.get(job_id)
        if not job or not job.result:
            return None
        msrp = msrp_from_result(job.result)
        request = parse_vehicle_query(job.query)
        return msrp if msrp and _msrp_matches_request(msrp, request) else None

    def _run_job(self, job_id: str, request: VehicleQuery) -> None:
        self._update(job_id, status="running", message="Starting Codex website collection", started_at=time.time())
        codex_path = self._codex_path()
        codex_status = codex_login_status(codex_path) if codex_path else codex_login_status(self.config.codex_path)
        if self.config.dry_run:
            result = _dry_run_result(request)
            self._write_job_result(job_id, result)
            self._update(job_id, status="completed", message="Dry-run collection completed", result=result)
            return
        job_dir = self.config.jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        facet_result: dict[str, Any] | None = None
        if self.config.use_visor_facets:
            self._update(job_id, status="running", message="Checking Visor public market facets")
            try:
                facet_result = collect_visor_public_facets(request)
            except Exception as exc:
                facet_result = {
                    "query": request.raw,
                    "status": "blocked",
                    "notes": [f"Visor public facets failed: {exc}"],
                    "msrp": None,
                    "sources": [],
                    "listings": [],
                }
            if facet_result.get("listings"):
                self._update(
                    job_id,
                    status="running",
                    message=(
                        f"Visor public facets collected {len(facet_result.get('listings') or [])} aggregate observations; "
                        "continuing to Codex website collection"
                    ),
                )
            else:
                self._update(job_id, status="running", message="Visor facets had no listings; starting Codex website collection")
        browser_result: dict[str, Any] | None = None
        if self._browser_worker_available():
            self._update(job_id, status="running", message="Collecting audited Autotrader and Edmunds listing cards")
            browser_result = self._run_browser_sources(request, job_dir)
            facet_result = _merge_collector_results(facet_result, browser_result, request)
        if not codex_path or not codex_status["authenticated"]:
            unavailable_note = (
                "Codex CLI was not found"
                if not codex_path
                else "Codex CLI is not logged in for the deployment user"
            )
            if facet_result and facet_result.get("listings"):
                facet_result["status"] = "partial"
                facet_result.setdefault("notes", []).append(
                    f"{unavailable_note}; verified browser-worker rows and Visor public facets were preserved."
                )
                facet_result = _apply_browser_captures(facet_result, job_dir, request)
                self._write_job_result(job_id, facet_result)
                self._update(
                    job_id,
                    status="completed",
                    message=f"Partial collection preserved {len(facet_result.get('listings') or [])} verified observations",
                    result=facet_result,
                )
                return
            self._update(
                job_id,
                status="blocked",
                message=f"{unavailable_note} and Visor public facets had no listings.",
                error="codex_not_authenticated" if codex_path else "codex_not_found",
            )
            return

        output_path = job_dir / "collector_result.json"
        stdout_path = job_dir / "codex_stdout.log"
        stderr_path = job_dir / "codex_stderr.log"
        prompt = build_codex_prompt(request, (browser_result or {}).get("collectionSummary"))
        command = build_codex_command(
            codex_path=codex_path,
            root=self.config.root,
            schema_path=self.config.schema_path,
            output_path=output_path,
            browser_server_path=self.config.browser_server_path,
        )
        start_time = time.time()
        try:
            with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open("w", encoding="utf-8") as stderr_file:
                collector_env = codex_environment()
                collector_env["CAR_COMPARE_BROWSER_AUDIT_DIR"] = str(job_dir)
                process = subprocess.Popen(
                    command,
                    env=collector_env,
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
                            message=f"Codex collection timed out after {_format_elapsed(elapsed)}",
                            error=f"Timed out after {self.config.timeout_seconds} seconds.",
                        )
                        return
                    self._update(
                        job_id,
                        status="running",
                        message=(
                            f"Codex is still running for {_format_elapsed(elapsed)} "
                            f"(PID {process.pid}). Waiting for website collection JSON."
                        ),
                    )
                    time.sleep(min(1, max(1, self.config.timeout_seconds - elapsed)))
                returncode = process.returncode
        except OSError as exc:
            if facet_result and facet_result.get("listings"):
                facet_result["status"] = "partial"
                facet_result.setdefault("notes", []).append(f"Could not launch Codex collector after Visor facets: {exc}")
                facet_result = _apply_browser_captures(facet_result, job_dir, request)
                self._write_job_result(job_id, facet_result)
                self._update(
                    job_id,
                    status="completed",
                    message=(
                        f"Visor public facets collected {len(facet_result.get('listings') or [])} aggregate observations; "
                        "Codex could not be launched"
                    ),
                    result=facet_result,
                )
                return
            self._update(
                job_id,
                status="failed",
                message="Could not launch Codex collector",
                error=str(exc),
            )
            return

        stdout_text = _read_text(stdout_path)
        stderr_text = _read_text(stderr_path)
        if returncode != 0:
            error_text = clean_codex_error(stderr_text or stdout_text)
            if facet_result and facet_result.get("listings"):
                facet_result["status"] = "partial"
                facet_result.setdefault("notes", []).append(
                    f"Codex review failed after audited browser/facet collection: {error_text}"
                )
                facet_result = _apply_browser_captures(facet_result, job_dir, request)
                self._write_job_result(job_id, facet_result)
                self._update(
                    job_id,
                    status="completed",
                    message=(
                        f"Audited browser/facet collection preserved {len(facet_result.get('listings') or [])} observations; "
                        "Codex review failed"
                    ),
                    result=facet_result,
                )
                return
            self._update(
                job_id,
                status="failed",
                message=codex_failure_message(error_text),
                error=error_text,
            )
            return

        try:
            result = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            if facet_result and facet_result.get("listings"):
                facet_result["status"] = "partial"
                facet_result.setdefault("notes", []).append(f"Codex collector did not produce valid JSON after Visor facets: {exc}")
                facet_result = _apply_browser_captures(facet_result, job_dir, request)
                self._write_job_result(job_id, facet_result)
                self._update(
                    job_id,
                    status="completed",
                    message=(
                        f"Visor public facets collected {len(facet_result.get('listings') or [])} aggregate observations; "
                        "Codex JSON was invalid"
                    ),
                    result=facet_result,
                )
                return
            self._update(
                job_id,
                status="failed",
                message="Codex collector did not produce valid JSON",
                error=str(exc),
            )
            return

        result = _merge_collector_results(facet_result, result, request)
        result = _apply_browser_captures(result, job_dir, request)
        self._write_job_result(job_id, result)
        final_status = "completed" if result.get("status") in {"success", "partial"} else "blocked"
        self._update(
            job_id,
            status=final_status,
            message=f"Collection {result.get('status', 'finished')}",
            result=result,
        )

    def _codex_path(self) -> str:
        return find_codex_cli(self.config.codex_path)

    def _browser_worker_available(self) -> bool:
        return bool(
            shutil.which("node")
            and self.config.browser_server_path.exists()
            and (self.config.root / "node_modules" / "playwright").exists()
        )

    def _run_browser_sources(self, request: VehicleQuery, job_dir: Path) -> dict[str, Any]:
        plan = build_collection_plan(request)
        targets = [item for item in plan["targets"] if item["source"] in BROWSER_SOURCE_NAMES]
        current_year = _runtime_current_year()
        start_year = request.target_year or max(current_year - request.max_age, request.start_year or current_year - request.max_age)
        end_year = request.target_year or current_year
        node_path = shutil.which("node") or "node"

        def run_target(target: dict[str, Any]) -> dict[str, Any]:
            payload = {
                "source": target["source"],
                "url": target["url"],
                "required_keywords": target["required_keywords"],
                "exclude_keywords": target["exclude_keywords"],
                "start_year": start_year,
                "end_year": end_year,
                "current_year": current_year,
                "max_pages": 3,
                "split_by_year": True,
            }
            env = os.environ.copy()
            env["CAR_COMPARE_BROWSER_AUDIT_DIR"] = str(job_dir)
            try:
                completed = subprocess.run(
                    [node_path, str(self.config.browser_server_path), "--collect-json"],
                    input=json.dumps(payload),
                    env=env,
                    text=True,
                    capture_output=True,
                    timeout=330,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                return {"source": target["source"], "status": "unavailable", "error": str(exc), "listings": []}
            if completed.returncode != 0:
                return {
                    "source": target["source"],
                    "status": "unavailable",
                    "error": _cap_error(completed.stderr or completed.stdout),
                    "listings": [],
                }
            try:
                return json.loads(completed.stdout)
            except json.JSONDecodeError as exc:
                return {"source": target["source"], "status": "unavailable", "error": str(exc), "listings": []}

        audits: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=2) as pool:
            future_map = {pool.submit(run_target, target): target for target in targets}
            for future in as_completed(future_map):
                audits.append(future.result())

        sources = []
        listings = []
        notes = []
        summary = []
        for audit in sorted(audits, key=lambda item: str(item.get("source") or "")):
            source = str(audit.get("source") or "")
            accepted = len(audit.get("listings") or [])
            error = str(audit.get("error") or "")
            stop_reason = str(audit.get("stop_reason") or "worker_error")
            note = (
                f"Audited browser examined {int(audit.get('cards_examined') or 0)} cards across "
                f"{int(audit.get('pages_examined') or 0)} page(s), accepted {accepted}, stop={stop_reason}."
            )
            if error:
                note += f" Error: {error}"
            sources.append(
                {
                    "source": source,
                    "url": str(audit.get("url") or ""),
                    "status": str(audit.get("status") or "unavailable"),
                    "load_more_clicked": int(audit.get("load_more_clicked") or 0),
                    "notes": note,
                }
            )
            listings.extend(audit.get("listings") or [])
            notes.append(f"{source}: {note}")
            summary.append({"source": source, "status": audit.get("status"), "accepted": accepted, "stopReason": stop_reason})
        return {
            "query": request.raw,
            "status": "partial" if listings else "blocked",
            "notes": notes,
            "msrp": None,
            "sources": sources,
            "listings": listings,
            "collectionSummary": summary,
        }

    def _update(self, job_id: str, **updates: Any) -> None:
        with self._lock:
            job = self._jobs[job_id]
            for key, value in updates.items():
                setattr(job, key, value)
            job.updated_at = time.time()

    def _write_job_result(self, job_id: str, result: dict[str, Any]) -> None:
        job_dir = self.config.jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        (job_dir / "collector_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


def build_codex_prompt(request: VehicleQuery, browser_summary: list[dict[str, Any]] | None = None) -> str:
    plan = build_collection_plan(request)
    browser_context = json.dumps(browser_summary or [], indent=2)
    return f"""
You are collecting public car market data for the local Car Compare app.

Vehicle query:
{request.raw}

Parsed vehicle:
make={request.make}
model={request.model}
trim={request.trim or "(none)"}
trend_horizon_years={request.max_age}

Vehicle resolver:
{json.dumps(plan["resolution"], indent=2)}

Collection targets:
{json.dumps(plan["targets"], indent=2)}

Browser worker pass already completed:
{browser_context}

Rules:
- Do not edit project files.
- Prefer normal visible website/browser interaction if browser automation is available.
- A project-local MCP tool named collect_vehicle_source is the authoritative browser collector. The app runs it once before this review. Call it again only for a browser target shown above as missing, blocked, or clearly sparse when another pass can add pages.
- Pass each target's source, URL, required_keywords, and exclude_keywords to that tool. Use the requested year range, current year, and max_pages=20.
- The tool persists deterministic listing cards and page audits for the app. Do not retype, alter, or invent its listing rows.
- A browser source may be called collected only when collect_vehicle_source returns browser_verified=true. Search snippets and cached page summaries are not browser evidence.
- If you are running inside Codex desktop and can show/use the browser, make website operation visible.
- Open the target URLs, confirm the visible page matches the requested vehicle, scroll results, and click visible Load More / See More Results / Next controls when available.
- After clicking a load-more control, verify that listing count, visible listing text, or page height changed. If it does not change, record that in source notes and continue.
- Stop on CAPTCHA, login-only wall, paywall, or access refusal. Do not bypass restrictions.
- Each target includes required_keywords, exclude_keywords, model_aliases, and location_policy. Treat those as binding collection rules.
- The resolver includes chips with mode="exact", mode="range", mode="constrained", or mode="all". Exact/range chips restrict collection; constrained chips inherit named sibling exclusions from the exact trim; all chips mean include every visible variant for that dimension.
- If trim, body_style, drivetrain, or powertrain is marked all, do not reject rows just because that field differs or is missing. Only require make/model and any exact chips.
- Extract only listings where every required keyword appears as a separate visible token in the listing row/detail page and none of the exclude keywords appear. For example, GT is not the same token as GTC.
- If a site redirects a model URL to all cars for the make, that is not automatically a failure. Continue only if visible rows can be filtered by the required/exclude rules; otherwise mark the source unavailable.
- Set or confirm the search radius/location to Nationwide, All miles, Unlimited, or the closest equivalent. If a zip is required, use it only to unlock the search and record the nationwide setting in source notes.
- If a source cannot be made nationwide/all-US, record that limitation clearly and avoid mixing it into a national depreciation trend unless no better source exists.
- Collect actual new-car examples when visible on manufacturer inventory pages, Autotrader/Edmunds new inventory, or Visor new-car results. Mark those listings with condition="new" and use a title beginning with "New ".
- Mark ordinary used examples with condition="used"; mark certified pre-owned with condition="cpo" when the page clearly says CPO/certified.
- Capture VIN and dealer when visible; if VIN is only visible on detail pages, open a small number of listing detail pages when practical.
- Deduplication happens in the app, but include VIN/dealer when possible.
- Listing price must be the vehicle asking/sale price between $500 and $10,000,000. Never use a payment, down payment, discount, fee, delivery charge, package, option, rebate, MSRP, or market-value reference as listing price.
- Continue until the tool reports its stop_reason. Its targets are 15 unique rows per year for the newest six model years and 8 per older year; sparse years must remain disclosed.
- Use manufacturer official MSRP between $5,000 and $10,000,000 when practical; never place a monthly payment in MSRP. If the manufacturer site also exposes current new inventory prices, include those as condition="new" listings. Otherwise set msrp to null.

Return only JSON matching the provided schema. Do not include Markdown.
""".strip()


def build_codex_command(
    codex_path: str,
    root: Path,
    schema_path: Path,
    output_path: Path,
    browser_server_path: Path | None = None,
) -> list[str]:
    command = [
        codex_path,
        "--ask-for-approval",
        "never",
        "exec",
    ]
    if browser_server_path and browser_server_path.exists() and shutil.which("node"):
        command.extend(
            [
                "--config",
                f"mcp_servers.car_compare_browser.command={json.dumps(shutil.which('node'))}",
                "--config",
                f"mcp_servers.car_compare_browser.args={json.dumps([str(browser_server_path)])}",
                "--config",
                "mcp_servers.car_compare_browser.startup_timeout_sec=30",
            ]
        )
    command.extend(
        [
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
    )
    return command


def _merge_collector_results(
    facet_result: dict[str, Any] | None,
    codex_result: dict[str, Any],
    request: VehicleQuery | None = None,
) -> dict[str, Any]:
    if not facet_result:
        merged = dict(codex_result)
        codex_msrp = msrp_from_result({"msrp": codex_result.get("msrp")})
        if codex_msrp and (not request or _msrp_matches_request(codex_msrp, request)):
            merged["msrp"] = codex_msrp.to_dict()
        else:
            merged["msrp"] = None
        return merged

    merged = dict(codex_result)
    merged["query"] = codex_result.get("query") or facet_result.get("query")
    merged_statuses = {str(facet_result.get("status") or ""), str(codex_result.get("status") or "")}
    if "success" in merged_statuses and not (merged_statuses - {"success", ""}):
        merged["status"] = "success"
    elif codex_result.get("listings") or facet_result.get("listings"):
        merged["status"] = "partial" if "blocked" in merged_statuses or "partial" in merged_statuses else "success"
    else:
        merged["status"] = codex_result.get("status") or facet_result.get("status") or "blocked"

    merged["notes"] = [*(facet_result.get("notes") or []), *(codex_result.get("notes") or [])]
    merged["sources"] = [*(facet_result.get("sources") or []), *(codex_result.get("sources") or [])]
    merged["evidence"] = [*(facet_result.get("evidence") or []), *(codex_result.get("evidence") or [])]
    merged["listings"] = [*(facet_result.get("listings") or []), *(codex_result.get("listings") or [])]
    codex_msrp = msrp_from_result({"msrp": codex_result.get("msrp")})
    facet_msrp = msrp_from_result({"msrp": facet_result.get("msrp")})
    if codex_msrp and request and not _msrp_matches_request(codex_msrp, request):
        codex_msrp = None
    if facet_msrp and request and not _msrp_matches_request(facet_msrp, request):
        facet_msrp = None
    selected_msrp = codex_msrp or facet_msrp
    merged["msrp"] = selected_msrp.to_dict() if selected_msrp else None
    return merged


def _apply_browser_captures(result: dict[str, Any], job_dir: Path, request: VehicleQuery) -> dict[str, Any]:
    merged = dict(result)
    merged["listings"] = [
        item
        for item in (result.get("listings") or [])
        if str(item.get("source") or "") not in BROWSER_SOURCE_NAMES
    ]
    source_rows = [
        item
        for item in (result.get("sources") or [])
        if str(item.get("source") or "") not in BROWSER_SOURCE_NAMES
    ]
    notes = list(result.get("notes") or [])
    quality_sources: list[dict[str, Any]] = []
    audited_sources: set[str] = set()

    for capture_path in sorted(job_dir.glob("browser_capture_*.json")):
        try:
            audit = json.loads(capture_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        source = str(audit.get("source") or "")
        if source not in BROWSER_SOURCE_NAMES or audit.get("browser_verified") is not True:
            continue
        audited_sources.add(source)
        accepted_rows: list[dict[str, Any]] = []
        for item in audit.get("listings") or []:
            parsed = listings_from_result({"listings": [item]})
            if not parsed:
                continue
            listing = parsed[0]
            match = vehicle_text_match_score(request, listing.title, listing.trim, source)
            if not match["accepted"]:
                continue
            accepted_rows.append(listing.to_dict())
        merged["listings"].extend(accepted_rows)
        rejected = audit.get("rejected_by_reason") or {}
        sparse_years = (audit.get("year_quota") or {}).get("sparse_years") or []
        diagnostics = (
            f"Browser verified {int(audit.get('pages_examined') or 0)} page(s), examined "
            f"{int(audit.get('cards_examined') or 0)} cards, and accepted {len(accepted_rows)} exact rows. "
            f"Stop: {audit.get('stop_reason') or 'unknown'}."
        )
        if sparse_years:
            diagnostics += " Sparse years: " + ", ".join(str(year) for year in sparse_years) + "."
        source_rows.append(
            {
                "source": source,
                "url": str(audit.get("url") or ""),
                "status": str(audit.get("status") or "partial"),
                "load_more_clicked": int(audit.get("load_more_clicked") or 0),
                "notes": diagnostics,
                "browser_verified": True,
                "pages_examined": int(audit.get("pages_examined") or 0),
                "cards_examined": int(audit.get("cards_examined") or 0),
                "detail_pages_opened": int(audit.get("detail_pages_opened") or 0),
                "accepted": len(accepted_rows),
                "rejected_by_reason": rejected,
                "stop_reason": str(audit.get("stop_reason") or ""),
                "year_quota": audit.get("year_quota") or {},
            }
        )
        quality_sources.append(source_rows[-1])

    for source in sorted(BROWSER_SOURCE_NAMES - audited_sources):
        notes.append(
            f"{source} produced no deterministic browser audit; search snippets and unverified Codex rows were not accepted."
        )
        source_rows.append(
            {
                "source": source,
                "url": "",
                "status": "unavailable",
                "load_more_clicked": 0,
                "notes": "No browser-worker audit was produced, so this source contributed zero individual rows.",
                "browser_verified": False,
            }
        )

    individual_count = sum(int(item.get("accepted") or 0) for item in quality_sources)
    merged["sources"] = source_rows
    merged["notes"] = notes
    merged["collectionQuality"] = {
        "browserAudited": bool(quality_sources),
        "individualRows": individual_count,
        "sources": quality_sources,
    }
    return merged


def _msrp_matches_request(msrp: MSRP, request: VehicleQuery) -> bool:
    if request.target_year:
        return msrp.year == request.target_year
    if msrp.year is None:
        return False
    current_year = _runtime_current_year()
    return current_year <= msrp.year <= current_year + 2


def clean_codex_error(raw: str) -> str:
    structured_message = _structured_error_message(raw)
    if structured_message:
        return _cap_error(structured_message)

    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    important = [
        line
        for line in lines
        if not line.startswith("WARN ")
        and " WARN " not in line
        and "codex_core_plugins::manifest" not in line
        and "codex_core_skills::loader" not in line
    ]
    usage_lines = [line for line in important if "usage limit" in line.lower()]
    if usage_lines:
        return _usage_limit_error("\n".join(dict.fromkeys(usage_lines)))
    error_lines = [line for line in important if line.startswith("ERROR") or " ERROR " in line]
    if error_lines:
        return _cap_error("\n".join(error_lines))
    if important:
        return _cap_error("\n".join(important))
    return _cap_error(raw.strip() or "Codex exited without an error message.")


def _structured_error_message(raw: str) -> str:
    match = re.search(r'"message"\s*:\s*"(?P<message>(?:\\"|[^"])*)"', raw, re.S)
    if not match:
        return ""
    try:
        return json.loads(f'"{match.group("message")}"')
    except json.JSONDecodeError:
        return match.group("message").replace('\\"', '"')


def codex_failure_message(error_text: str) -> str:
    lower = error_text.lower()
    if "usage limit" in lower:
        return "Codex usage limit reached"
    if "unexpected argument" in lower:
        return "Codex command option failed"
    if "invalid_json_schema" in lower or "schema" in lower:
        return "Codex collector schema failed"
    return "Codex collector failed"


def _cap_error(text: str, limit: int = 1200) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return f"{text[: limit - 1].rstrip()}..."


def _format_elapsed(seconds: int) -> str:
    seconds = max(0, int(seconds))
    minutes, secs = divmod(seconds, 60)
    hours, mins = divmod(minutes, 60)
    if hours:
        return f"{hours}h {mins}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _usage_limit_error(text: str) -> str:
    match = re.search(r"try again at ([^.]+)", text, re.I)
    retry = f" Try again at {match.group(1).strip()}." if match else ""
    return f"Codex usage limit reached.{retry}"


def listings_from_result(result: dict[str, Any]) -> list[Listing]:
    rows = []
    for item in result.get("listings") or []:
        if not isinstance(item, dict):
            continue
        try:
            year_number = float(item["year"])
            if not math.isfinite(year_number) or not year_number.is_integer():
                continue
            year = int(year_number)
            price = float(item["price"])
            mileage = _optional_int(item.get("mileage"))
            if not MIN_MODEL_YEAR <= year <= _runtime_current_year() + 2:
                continue
            if not math.isfinite(price) or not MIN_LISTING_PRICE <= price <= MAX_LISTING_PRICE:
                continue
            if mileage is not None and not 0 <= mileage <= MAX_MILEAGE:
                continue
            title_condition = _condition_from_title(item.get("title"))
            condition = title_condition or str(item.get("condition") or "unknown").lower()
            if condition not in {"new", "used", "cpo", "unknown"}:
                condition = "unknown"
            rows.append(
                Listing(
                    source=str(item.get("source") or "codex_collector"),
                    year=year,
                    price=price,
                    trim=str(item.get("trim") or ""),
                    mileage=mileage,
                    title=str(item.get("title") or ""),
                    url=str(item.get("url") or ""),
                    vin=str(item.get("vin") or ""),
                    dealer=str(item.get("dealer") or ""),
                    confidence=str(item.get("confidence") or "codex_collected"),
                    condition=condition,
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return rows


def msrp_from_result(result: dict[str, Any]) -> MSRP | None:
    item = result.get("msrp")
    if not isinstance(item, dict):
        return None
    price = item.get("price")
    if price in (None, ""):
        return None
    try:
        price_float = float(price)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(price_float) or not MIN_MSRP_PRICE <= price_float <= MAX_MSRP_PRICE:
        return None
    year = _optional_int(item.get("year"))
    if year is not None and not MIN_MODEL_YEAR <= year <= _runtime_current_year() + 2:
        return None
    return MSRP(
        price=price_float,
        label=str(item.get("label") or "Codex collected MSRP"),
        source=str(item.get("source") or "codex_collector"),
        url=str(item.get("url") or ""),
        year=year,
    )


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _runtime_current_year() -> int:
    return datetime.now(timezone.utc).year


def _condition_from_title(value: Any) -> str:
    title = str(value or "").lower().strip()
    if title.startswith("new arrival"):
        return "used"
    if re.match(r"^used\b", title):
        return "used"
    if re.match(r"^(?:certified(?:\s+pre[- ]?owned)?|cpo)\b", title):
        return "cpo"
    if re.match(r"^new\b", title):
        return "new"
    # A neutral title has no authority over structured collector evidence.
    return ""


def _dry_run_result(request: VehicleQuery) -> dict[str, Any]:
    plan = build_collection_plan(request)
    return {
        "query": request.raw,
        "status": "blocked",
        "notes": ["Dry-run mode: no websites were opened."],
        "msrp": None,
        "sources": [
            {
                "source": target["source"],
                "url": target["url"],
                "status": "unavailable",
                "load_more_clicked": 0,
                "notes": "Dry-run target only.",
            }
            for target in plan["targets"]
        ],
        "listings": [],
    }
