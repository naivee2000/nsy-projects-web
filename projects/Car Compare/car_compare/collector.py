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
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from car_compare.models import Listing, MSRP, VehicleQuery
from car_compare.parser import parse_vehicle_query
from car_compare.browser_runtime import browser_cdp_status
from car_compare.capture_cache import CaptureCache, ResearchResultCache
from car_compare.codex_cli import codex_environment, codex_login_status, find_codex_cli
from car_compare.sources.browser_capture import listing_year_in_scope, parse_visible_listing_text
from car_compare.sources.chrome_host import (
    capture_access_message,
    capture_is_access_wall,
    capture_with_host_chrome,
    host_chrome_status,
)
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
MAX_MARKET_WEIGHT = 1_000_000
BROWSER_SOURCE_NAMES = {"autotrader_browser", "edmunds_browser", "porsche_finder_browser"}
BROWSER_SOURCE_HOSTS = {
    "autotrader_browser": "autotrader.com",
    "edmunds_browser": "edmunds.com",
    "porsche_finder_browser": "finder.porsche.com",
}
DEFAULT_FALLBACK_LEASE_SECONDS = 20 * 60
MIN_FALLBACK_LEASE_SECONDS = 5 * 60
MAX_FALLBACK_LEASE_SECONDS = 60 * 60


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
    max_age: int = 10
    fallback_status: str = ""
    fallback_created_at: float = 0
    fallback_expires_at: float = 0
    fallback_sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["createdAt"] = self.created_at
        data["updatedAt"] = self.updated_at
        if self.started_at:
            data["elapsedSeconds"] = max(0, int(time.time() - self.started_at))
        else:
            data["elapsedSeconds"] = 0
        if self.fallback_status:
            data["fallback"] = {
                "status": self.fallback_status,
                "createdAt": self.fallback_created_at,
                "expiresAt": self.fallback_expires_at,
                "remainingSeconds": (
                    max(0, int(self.fallback_expires_at - time.time()))
                    if self.fallback_status == "pending"
                    else 0
                ),
                "sources": list(self.fallback_sources),
            }
        else:
            data["fallback"] = None
        return data


@dataclass
class CollectorConfig:
    root: Path
    codex_path: str = ""
    dry_run: bool = False
    timeout_seconds: int = CODEX_TIMEOUT_SECONDS
    fallback_lease_seconds: int = DEFAULT_FALLBACK_LEASE_SECONDS
    use_visor_facets: bool = True
    cache_enabled: bool = True
    cache_dir: Path | None = None
    recent_cache_ttl_seconds: int = 3 * 24 * 60 * 60
    older_cache_ttl_seconds: int = 3 * 24 * 60 * 60
    collector_review_cache_ttl_seconds: int = 3 * 24 * 60 * 60
    marketplace_concurrency: int = 2
    codex_search_workers: int = 3
    codex_search_batch_size: int = 5
    background_mode: bool = True
    jobs_dir: Path = field(init=False)
    cache_path: Path = field(init=False)
    schema_path: Path = field(init=False)
    web_search_schema_path: Path = field(init=False)
    browser_server_path: Path = field(init=False)
    chrome_host_script_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.fallback_lease_seconds = max(
            MIN_FALLBACK_LEASE_SECONDS,
            min(MAX_FALLBACK_LEASE_SECONDS, int(self.fallback_lease_seconds)),
        )
        self.marketplace_concurrency = max(1, min(4, int(self.marketplace_concurrency)))
        self.codex_search_workers = max(1, min(4, int(self.codex_search_workers)))
        self.codex_search_batch_size = max(1, min(8, int(self.codex_search_batch_size)))
        self.jobs_dir = self.root / "data" / "collector_jobs"
        resolved_cache_dir = self.cache_dir or (self.root / "data" / "cache")
        self.cache_path = resolved_cache_dir / "collector_cache.sqlite3"
        self.schema_path = self.root / "car_compare" / "collector_schema.json"
        self.web_search_schema_path = self.root / "car_compare" / "web_search_capture_schema.json"
        self.browser_server_path = self.root / "scripts" / "car_compare_browser_mcp.mjs"
        self.chrome_host_script_path = self.root / "scripts" / "chrome_host_capture.applescript"


class CollectionManager:
    def __init__(self, config: CollectorConfig):
        self.config = config
        self.config.jobs_dir.mkdir(parents=True, exist_ok=True)
        self._capture_cache = CaptureCache(
            self.config.cache_path,
            enabled=self.config.cache_enabled,
            recent_ttl_seconds=self.config.recent_cache_ttl_seconds,
            older_ttl_seconds=self.config.older_cache_ttl_seconds,
        )
        self._result_cache = ResearchResultCache(
            self.config.cache_path,
            enabled=self.config.cache_enabled,
            ttl_seconds=self.config.collector_review_cache_ttl_seconds,
        )
        self._jobs: dict[str, CollectionJob] = {}
        self._lock = threading.Lock()
        self._browser_lock = threading.Lock()
        self._restore_finished_jobs()

    def _restore_finished_jobs(self) -> None:
        result_paths = sorted(
            self.config.jobs_dir.glob("*/collector_result.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )[:50]
        for result_path in result_paths:
            try:
                result = json.loads(result_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            query = str(result.get("query") or "").strip()
            if not query:
                continue
            modified = result_path.stat().st_mtime
            status = "completed" if str(result.get("status") or "") in {"success", "partial"} else "blocked"
            job = CollectionJob(
                id=result_path.parent.name,
                query=query,
                status=status,
                created_at=modified,
                updated_at=modified,
                message="Restored finished collection",
                result=result,
                codex_path=self._codex_path(),
                max_age=_infer_result_max_age(result),
            )
            self._restore_fallback_lease(job)
            self._jobs[job.id] = job

    def availability(self) -> dict[str, Any]:
        path = self._codex_path()
        status = codex_login_status(path) if path else codex_login_status(self.config.codex_path)
        website_available = bool(path and status["authenticated"])
        visor_available = bool(self.config.use_visor_facets)
        browser_worker_available = self._browser_worker_available()
        host_chrome = host_chrome_status(self.config.chrome_host_script_path)
        codex_search_fallback_ready = bool(
            website_available
            and self.config.web_search_schema_path.is_file()
            and os.environ.get("CAR_COMPARE_CODEX_SEARCH_FALLBACK", "1").strip().lower()
            not in {"0", "false", "no", "off"}
        )
        explicit_cdp = bool(os.environ.get("CAR_COMPARE_BROWSER_CDP_URL", "").strip())
        persistent_browser = browser_cdp_status() if explicit_cdp else self._browser_runtime_status()
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
            "hostChromeFallbackReady": bool(host_chrome["ready"]),
            "hostChromeFallbackMode": str(host_chrome["mode"]),
            "hostChromeBackground": bool(host_chrome.get("background")),
            "hostChromeFallbackError": str(host_chrome["error"]),
            "codexSearchFallbackReady": codex_search_fallback_ready,
            "persistentBrowserConfigured": bool(explicit_cdp or persistent_browser["ready"]),
            "persistentBrowserReady": persistent_browser["ready"],
            "persistentBrowserMode": persistent_browser["mode"],
            "persistentBrowserUrl": persistent_browser["url"],
            "persistentBrowserName": persistent_browser["browser"],
            "persistentBrowserBackground": bool(persistent_browser.get("background")),
            "persistentBrowserError": persistent_browser["error"],
            "auditedWebsiteCollectorAvailable": bool(
                website_available and browser_worker_available and persistent_browser["ready"]
            ),
            "codexPath": path,
            "codexHome": status["codexHome"],
            "authenticated": status["authenticated"],
            "authMethod": status["authMethod"],
            "dryRun": self.config.dry_run,
            "captureCache": self._capture_cache.status(),
            "collectorReviewCache": self._result_cache.status(),
            "marketplaceConcurrency": self.config.marketplace_concurrency,
            "codexSearchWorkers": self.config.codex_search_workers,
            "backgroundMode": self.config.background_mode,
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
            max_age=request.max_age,
        )
        with self._lock:
            self._jobs[job.id] = job
        thread = threading.Thread(target=self._run_job, args=(job.id, request), daemon=True)
        thread.start()
        return job

    def get(self, job_id: str) -> CollectionJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def job_payload(self, job_id: str) -> dict[str, Any] | None:
        self._expire_fallback_lease(job_id)
        job = self.get(job_id)
        if not job:
            return None
        payload = job.to_dict()
        if payload.get("fallback"):
            payload["fallback"]["projectPath"] = str(self.config.root)
        return payload

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

    def browser_actions(self) -> list[dict[str, Any]]:
        with self._lock:
            jobs = list(self._jobs.values())
        actions: list[dict[str, Any]] = []
        for job in sorted(jobs, key=lambda item: item.updated_at, reverse=True):
            self._expire_fallback_lease(job.id)
            job = self.get(job.id) or job
            if job.fallback_status != "pending":
                continue
            if job.status not in {"completed", "blocked"} or not job.result:
                continue
            request = parse_vehicle_query(job.query)
            request.max_age = job.max_age
            targets = {
                item["source"]: item
                for item in build_collection_plan(request)["targets"]
                if item["source"] in BROWSER_SOURCE_NAMES
            }
            source_rows = {
                str(item.get("source") or ""): item
                for item in job.result.get("sources") or []
                if str(item.get("source") or "") in BROWSER_SOURCE_NAMES
            }
            needed = []
            for source in sorted(job.fallback_sources):
                row = source_rows.get(source) or {}
                target = targets.get(source) or {}
                needed.append(
                    {
                        "source": source,
                        "url": str(target.get("url") or row.get("url") or ""),
                        "status": str(row.get("status") or "unavailable"),
                    }
                )
            if needed:
                actions.append(
                    {
                        "jobId": job.id,
                        "query": job.query,
                        "maxAge": job.max_age,
                        "createdAt": job.created_at,
                        "updatedAt": job.updated_at,
                        "fallbackCreatedAt": job.fallback_created_at,
                        "fallbackExpiresAt": job.fallback_expires_at,
                        "fallbackRemainingSeconds": max(0, int(job.fallback_expires_at - time.time())),
                        "projectPath": str(self.config.root),
                        "sources": needed,
                    }
                )
        return actions[:10]

    def import_codex_browser_capture(
        self,
        job_id: str,
        *,
        source: str,
        url: str,
        visible_text: str,
        pages_examined: int = 1,
        cards_examined: int = 0,
        load_more_clicked: int = 0,
    ) -> dict[str, Any]:
        job = self.get(job_id)
        if not job:
            raise KeyError("Collection job not found")
        if job.status not in {"completed", "blocked"} or not job.result:
            raise RuntimeError("Collection job must be finished before importing a Codex Chrome capture")
        self._expire_fallback_lease(job_id)
        job = self.get(job_id) or job
        if job.fallback_status != "pending" or time.time() >= job.fallback_expires_at:
            raise RuntimeError("The temporary Codex Chrome fallback lease is not active")
        if source not in BROWSER_SOURCE_NAMES:
            raise ValueError("Unsupported browser source")
        if source not in job.fallback_sources:
            raise RuntimeError("This marketplace no longer needs a fallback capture")
        parsed_url = urlparse(url)
        expected_host = BROWSER_SOURCE_HOSTS[source]
        if (
            parsed_url.scheme != "https"
            or not parsed_url.hostname
            or not (parsed_url.hostname == expected_host or parsed_url.hostname.endswith(f".{expected_host}"))
        ):
            raise ValueError(f"Capture URL must use {expected_host}")
        if not visible_text.strip():
            raise ValueError("Visible page text is required")

        request = parse_vehicle_query(job.query)
        request.max_age = job.max_age
        listings = [
            listing
            for listing in parse_visible_listing_text(source, url, visible_text, request)
            if listing_year_in_scope(listing.year, request)
        ]
        quota = _browser_year_quota(listings, request)
        safe_pages = max(1, min(100, int(pages_examined or 1)))
        safe_cards = max(len(listings), min(5_000, max(0, int(cards_examined or 0))))
        safe_clicks = min(100, max(0, int(load_more_clicked or 0)))
        audit = {
            "version": 1,
            "source": source,
            "url": url,
            "browser_mode": "codex_browser_action",
            "browser_verified": True,
            "status": "collected" if listings else "unavailable",
            "pages_examined": safe_pages,
            "cards_examined": safe_cards,
            "accepted": len(listings),
            "rejected_by_reason": {},
            "load_more_clicked": safe_clicks,
            "detail_pages_opened": 0,
            "stop_reason": "codex_browser_action_capture",
            "access_message": "",
            "year_quota": quota,
            "page_records": [
                {
                    "page": 1,
                    "url": url,
                    "cards_examined": safe_cards,
                    "accepted_new": len(listings),
                    "detail_pages_opened": 0,
                    "search_scope": "codex_browser_action",
                }
            ],
            "requested_year_searches": 0,
            "attempted_year_searches": 0,
            "avoided_year_searches": 0,
            "skipped_year_searches": 0,
            "listings": [item.to_dict() for item in listings],
        }
        job_dir = self.config.jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        capture_path = job_dir / f"browser_capture_{source}.json"
        capture_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
        refreshed = _apply_browser_captures(job.result, job_dir, request)
        self._write_job_result(job_id, refreshed)
        self._update(
            job_id,
            status="completed",
            message=f"Codex Chrome action imported {len(listings)} {source.replace('_browser', '')} rows",
            result=refreshed,
            error="",
        )
        return {
            "jobId": job_id,
            "source": source,
            "status": audit["status"],
            "accepted": len(listings),
            "cardsExamined": safe_cards,
            "listingCount": len(refreshed.get("listings") or []),
        }

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
            facet_identity = _collector_review_cache_identity(request)
            facet_result = self._result_cache.load("visor_facets", facet_identity)
            if facet_result:
                self._update(job_id, status="running", message="Reusing cached Visor public market facets")
            else:
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
                    self._result_cache.store("visor_facets", facet_identity, facet_result)
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
            self._update(job_id, status="running", message="Checking the verified marketplace cache")
            with self._browser_lock:
                self._update(
                    job_id,
                    status="running",
                    message="Reusing cached marketplaces and collecting only missing or expired sources",
                )
                browser_result = self._run_browser_sources(request, job_dir, facet_result)
            facet_result = _merge_collector_results(facet_result, browser_result, request)
        cached_review = self._result_cache.load("collector_review", _collector_review_cache_identity(request))
        if cached_review:
            result = _merge_collector_results(facet_result, cached_review, request)
            result = _apply_browser_captures(result, job_dir, request)
            result.setdefault("notes", []).append("Reused a fresh validated Codex collection review from the persistent cache.")
            self._write_job_result(job_id, result)
            final_status = "completed" if result.get("status") in {"success", "partial"} else "blocked"
            self._update(
                job_id,
                status=final_status,
                message=f"Collection {result.get('status', 'finished')} from verified cache",
                result=result,
            )
            return
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

        if result.get("status") in {"success", "partial"}:
            self._result_cache.store("collector_review", _collector_review_cache_identity(request), result)
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

    def _browser_runtime_status(self) -> dict[str, Any]:
        if not self._browser_worker_available():
            return {
                "ready": False,
                "mode": "missing-worker",
                "url": "",
                "browser": "",
                "error": "Install Node.js and run npm install.",
                "background": False,
            }
        try:
            env = os.environ.copy()
            env["CAR_COMPARE_BACKGROUND_MODE"] = "1" if self.config.background_mode else "0"
            completed = subprocess.run(
                [shutil.which("node") or "node", str(self.config.browser_server_path), "--runtime-status"],
                env=env,
                text=True,
                capture_output=True,
                timeout=5,
                check=False,
            )
            result = (
                json.loads(completed.stdout)
                if completed.returncode == 0
                else {"ready": False, "error": _cap_error(completed.stderr or completed.stdout)}
            )
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            result = {"ready": False, "error": str(exc)}
        return {
            "ready": bool(result.get("ready")),
            "configured": bool(result.get("ready")),
            "mode": str(result.get("mode") or "missing-browser"),
            "url": "",
            "browser": Path(str(result.get("executable_path") or "")).name,
            "error": str(result.get("error") or ""),
            "background": bool(result.get("background_mode")),
        }

    def _run_browser_sources(
        self,
        request: VehicleQuery,
        job_dir: Path,
        baseline_result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        plan = build_collection_plan(request)
        targets = [item for item in plan["targets"] if item["source"] in BROWSER_SOURCE_NAMES]
        current_year = _runtime_current_year()
        start_year = request.target_year or max(current_year - request.max_age, request.start_year or current_year - request.max_age)
        end_year = request.target_year or current_year
        payloads = [
            {
                "source": target["source"],
                "url": target["url"],
                "required_keywords": target["required_keywords"],
                "exclude_keywords": target["exclude_keywords"],
                "start_year": start_year,
                "end_year": end_year,
                "current_year": current_year,
                "max_pages": 3,
                "split_by_year": False,
                "skip_persist": True,
            }
            for target in targets
        ]
        years = list(range(start_year, end_year + 1))
        cached = self._cached_browser_audits(request, payloads, years)
        audits = list(cached)
        requested_years = set(years)
        fully_cached_sources = {
            str(audit.get("source") or "")
            for audit in cached
            if requested_years.issubset({int(year) for year in audit.get("cache_years") or []})
        }
        range_payloads = [
            payload for payload in payloads if str(payload["source"]) not in fully_cached_sources
        ]
        refreshable_sources = {str(payload["source"]) for payload in range_payloads}
        if range_payloads:
            range_audits = self._run_browser_batch(range_payloads, job_dir, timeout=300)
            for audit in range_audits:
                self._store_audit_cache(request, audit, current_year)
            audits = _merge_audits_by_source(request, payloads, [*audits, *range_audits])

            for _round in range(2):
                coverage = _combined_year_coverage(request, baseline_result, audits)
                followups = _plan_browser_followups(request, range_payloads, audits, coverage["sparse_years"])
                if not followups:
                    break
                targeted_audits = self._run_browser_batch(followups, job_dir, timeout=420)
                for audit in targeted_audits:
                    self._store_audit_cache(request, audit, current_year)
                audits = _merge_audits_by_source(request, payloads, [*audits, *targeted_audits])
                if _combined_year_coverage(request, baseline_result, audits)["met"]:
                    break
        else:
            audits = _merge_audits_by_source(request, payloads, audits)

        coverage = _combined_year_coverage(request, baseline_result, audits)
        if coverage["sparse_years"]:
            fallback_payloads = [
                {**payload, "target_years": list(coverage["sparse_years"])}
                for payload in payloads
                if str(payload["source"]) in refreshable_sources
            ]
            if fallback_payloads:
                fallback_audits = self._run_host_chrome_fallbacks(
                    request, fallback_payloads, audits, job_dir
                )
                audits = _merge_audits_by_source(request, payloads, [*audits, *fallback_audits])

        coverage = _combined_year_coverage(request, baseline_result, audits)
        if coverage["sparse_years"]:
            search_payloads = [
                {**payload, "target_years": list(coverage["sparse_years"])}
                for payload in payloads
                if str(payload["source"]) in refreshable_sources
            ]
            if search_payloads:
                search_audits = self._run_codex_search_fallbacks(
                    request, search_payloads, audits, job_dir
                )
                audits = _merge_audits_by_source(request, payloads, [*audits, *search_audits])

        final_coverage = _combined_year_coverage(request, baseline_result, audits)
        for audit in audits:
            audit["combined_year_coverage"] = final_coverage
            source = str(audit.get("source") or "")
            if source in BROWSER_SOURCE_NAMES:
                (job_dir / f"browser_capture_{source}.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

        sources = []
        listings = []
        notes = []
        summary = []
        for audit in sorted(audits, key=lambda item: str(item.get("source") or "")):
            source = str(audit.get("source") or "")
            accepted = len(audit.get("listings") or [])
            error = str(audit.get("error") or "")
            stop_reason = str(audit.get("stop_reason") or "worker_error")
            browser_mode = str(audit.get("browser_mode") or "unknown")
            range_search = audit.get("range_search") if isinstance(audit.get("range_search"), dict) else {}
            targeted_year_searches = int(audit.get("attempted_year_searches") or 0)
            avoided_year_searches = int(audit.get("avoided_year_searches") or 0)
            note = (
                f"Audited browser examined {int(audit.get('cards_examined') or 0)} cards across "
                f"{int(audit.get('pages_examined') or 0)} page(s), accepted {accepted}, "
                f"browser={browser_mode}, stop={stop_reason}."
            )
            cache_hits = int(audit.get("cache_entries") or 0)
            if cache_hits:
                note += f" Reused {cache_hits} fresh cached year capture(s)."
            if final_coverage.get("met"):
                note += " Combined cross-source year coverage met."
            elif final_coverage.get("sparse_years"):
                note += " Combined sparse years: " + ", ".join(str(year) for year in final_coverage["sparse_years"]) + "."
            if range_search:
                note += (
                    f" Range-first pass accepted {int(range_search.get('accepted') or 0)}; "
                    f"targeted {targeted_year_searches} sparse year(s)."
                )
            if error:
                note += f" Error: {error}"
            sources.append(
                {
                    "source": source,
                    "url": str(audit.get("url") or ""),
                    "status": str(audit.get("status") or "unavailable"),
                    "accepted": accepted,
                    "load_more_clicked": int(audit.get("load_more_clicked") or 0),
                    "browser_mode": browser_mode,
                    "host_chrome_attempted": bool(audit.get("host_chrome_attempted")),
                    "codex_search_attempted": bool(audit.get("codex_search_attempted")),
                    "search_verified": bool(audit.get("search_verified")),
                    "background_mode": bool(audit.get("background_mode")),
                    "cache_entries": cache_hits,
                    "stop_reason": stop_reason,
                    "notes": note,
                }
            )
            listings.extend(audit.get("listings") or [])
            notes.append(f"{source}: {note}")
            summary.append(
                {
                    "source": source,
                    "status": audit.get("status"),
                    "accepted": accepted,
                    "rangeAccepted": int(range_search.get("accepted") or 0) if range_search else 0,
                    "targetedYearSearches": targeted_year_searches,
                    "avoidedYearSearches": avoided_year_searches,
                    "stopReason": stop_reason,
                    "hostChromeAttempted": bool(audit.get("host_chrome_attempted")),
                    "codexSearchAttempted": bool(audit.get("codex_search_attempted")),
                    "searchVerified": bool(audit.get("search_verified")),
                    "backgroundMode": bool(audit.get("background_mode")),
                    "cacheEntries": cache_hits,
                }
            )
        return {
            "query": request.raw,
            "status": "partial" if listings else "blocked",
            "notes": notes,
            "msrp": None,
            "sources": sources,
            "listings": listings,
            "collectionSummary": summary,
            "combinedYearCoverage": final_coverage,
        }

    def _run_browser_batch(
        self,
        payloads: list[dict[str, Any]],
        job_dir: Path,
        *,
        timeout: int,
    ) -> list[dict[str, Any]]:
        if not payloads:
            return []
        env = os.environ.copy()
        env["CAR_COMPARE_BROWSER_AUDIT_DIR"] = str(job_dir)
        env["CAR_COMPARE_BACKGROUND_MODE"] = "1" if self.config.background_mode else "0"
        node_path = shutil.which("node") or "node"
        completed: subprocess.CompletedProcess[str] | None = None
        try:
            completed = subprocess.run(
                [node_path, str(self.config.browser_server_path), "--collect-batch-json"],
                input=json.dumps(
                    {
                        "targets": payloads,
                        "max_concurrency": self.config.marketplace_concurrency,
                    }
                ),
                env=env,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
            audits = json.loads(completed.stdout) if completed.returncode == 0 else []
            if not isinstance(audits, list):
                raise json.JSONDecodeError("Expected a browser audit list", completed.stdout, 0)
            return [item for item in audits if isinstance(item, dict)]
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            error = str(exc)
        if completed is not None and completed.returncode != 0:
            error = _cap_error(completed.stderr or completed.stdout)
        return [
            {
                "source": str(payload.get("source") or ""),
                "url": str(payload.get("url") or ""),
                "status": "unavailable",
                "error": error,
                "listings": [],
                "background_mode": self.config.background_mode,
            }
            for payload in payloads
        ]

    def _cached_browser_audits(
        self,
        request: VehicleQuery,
        payloads: list[dict[str, Any]],
        years: list[int],
    ) -> list[dict[str, Any]]:
        audits: list[dict[str, Any]] = []
        for payload in payloads:
            source = str(payload["source"])
            entries = self._capture_cache.load(request, source, years)
            if entries:
                audits.append(_audit_from_cache_entries(request, payload, entries))
        return audits

    def _store_audit_cache(self, request: VehicleQuery, audit: dict[str, Any], current_year: int) -> None:
        source = str(audit.get("source") or "")
        deterministic_verified = bool(
            audit.get("browser_verified") is True
            or (audit.get("search_verified") is True and audit.get("deterministic_verified") is True)
        )
        if source not in BROWSER_SOURCE_NAMES or not deterministic_verified:
            return
        rows_by_year: dict[int, list[dict[str, Any]]] = {}
        for listing in _verified_audit_listings(request, audit):
            rows_by_year.setdefault(listing.year, []).append(listing.to_dict())
        if not rows_by_year:
            quota_targets = (audit.get("year_quota") or {}).get("targets") or {}
            attempted_years = {
                int(year)
                for year in quota_targets
                if str(year).isdigit()
            }
            if not attempted_years:
                if request.target_year:
                    attempted_years = {request.target_year}
                else:
                    first_year = max(
                        current_year - request.max_age,
                        request.start_year or current_year - request.max_age,
                    )
                    attempted_years = set(range(first_year, current_year + 1))
            rows_by_year = {year: [] for year in attempted_years}
        for year, rows in rows_by_year.items():
            self._capture_cache.store_year(
                request,
                source,
                year,
                {
                    "version": 1,
                    "source": source,
                    "url": str(audit.get("url") or ""),
                    "browser_mode": str(audit.get("browser_mode") or "unknown"),
                    "browser_verified": bool(audit.get("browser_verified")),
                    "search_verified": bool(audit.get("search_verified")),
                    "deterministic_verified": deterministic_verified,
                    "background_mode": bool(audit.get("background_mode")),
                    "stop_reason": str(audit.get("stop_reason") or ""),
                    "listings": rows,
                },
                current_year=current_year,
                overwrite_existing=bool(rows),
            )

    def _run_host_chrome_fallbacks(
        self,
        request: VehicleQuery,
        payloads: list[dict[str, Any]],
        audits: list[dict[str, Any]],
        job_dir: Path,
    ) -> list[dict[str, Any]]:
        status = host_chrome_status(self.config.chrome_host_script_path)
        if not status["ready"]:
            return audits
        by_source = {
            str(audit.get("source") or ""): audit
            for audit in audits
            if isinstance(audit, dict)
        }
        eligible: list[dict[str, Any]] = []
        for payload in payloads:
            source = str(payload.get("source") or "")
            existing = by_source.get(source) or {}
            existing_status = str(existing.get("status") or "unavailable")
            if (
                not payload.get("target_years")
                and existing_status not in {"blocked", "unavailable"}
                and existing.get("listings")
            ):
                continue
            if payload.get("target_years") == []:
                continue
            eligible.append(payload)
        host_workers = 1 if self.config.background_mode else self.config.marketplace_concurrency
        with ThreadPoolExecutor(max_workers=min(host_workers, len(eligible) or 1)) as pool:
            future_map = {
                pool.submit(self._collect_host_chrome_source, request, payload, job_dir): payload
                for payload in eligible
            }
            for future in as_completed(future_map):
                payload = future_map[future]
                source = str(payload.get("source") or "")
                existing = by_source.get(source) or {}
                existing_status = str(existing.get("status") or "unavailable")
                try:
                    live_audit = future.result()
                    self._store_audit_cache(request, live_audit, _runtime_current_year())
                    by_source[source] = _merge_browser_audits(
                        request,
                        source,
                        str(payload.get("url") or ""),
                        [existing, live_audit],
                    )
                except Exception as exc:
                    replacement = dict(existing)
                    replacement.update(
                        {
                            "source": source,
                            "url": str(payload.get("url") or ""),
                            "status": existing_status,
                            "browser_mode": str(status["mode"]),
                            "browser_verified": bool(existing.get("browser_verified")),
                            "background_mode": bool(existing.get("background_mode", self.config.background_mode)),
                            "host_chrome_attempted": True,
                            "error": _cap_error(str(exc)),
                            "listings": list(existing.get("listings") or []),
                        }
                    )
                    by_source[source] = replacement
        return [by_source.get(str(payload.get("source") or ""), {}) for payload in payloads]

    def _run_codex_search_fallbacks(
        self,
        request: VehicleQuery,
        payloads: list[dict[str, Any]],
        audits: list[dict[str, Any]],
        job_dir: Path,
    ) -> list[dict[str, Any]]:
        if os.environ.get("CAR_COMPARE_CODEX_SEARCH_FALLBACK", "1").strip().lower() in {
            "0",
            "false",
            "no",
            "off",
        }:
            return audits
        if not self.config.web_search_schema_path.is_file():
            return audits
        codex_path = self._codex_path()
        login = codex_login_status(codex_path) if codex_path else {"authenticated": False}
        if not codex_path or not login.get("authenticated"):
            return audits

        by_source = {
            str(audit.get("source") or ""): audit
            for audit in audits
            if isinstance(audit, dict)
        }
        for payload in payloads:
            source = str(payload.get("source") or "")
            if source != "edmunds_browser":
                continue
            existing = by_source.get(source) or {}
            target_years = [int(year) for year in payload.get("target_years") or []]
            if payload.get("target_years") == []:
                continue
            if (
                not target_years
                and existing.get("listings")
                and str(existing.get("status") or "") not in {"blocked", "unavailable"}
            ):
                continue
            try:
                search_audit = self._collect_codex_web_search_source(
                    request,
                    payload,
                    job_dir,
                    codex_path=codex_path,
                    host_chrome_attempted=bool(existing.get("host_chrome_attempted")),
                )
            except Exception as exc:
                replacement = dict(existing)
                replacement["codex_search_attempted"] = True
                replacement["search_verified"] = False
                replacement["error"] = " | ".join(
                    item for item in [str(existing.get("error") or ""), _cap_error(str(exc))] if item
                )
                by_source[source] = replacement
                capture_path = job_dir / f"browser_capture_{source}.json"
                if capture_path.is_file():
                    capture_path.write_text(json.dumps(replacement, indent=2), encoding="utf-8")
                continue
            self._store_audit_cache(request, search_audit, _runtime_current_year())
            by_source[source] = _merge_browser_audits(
                request,
                source,
                str(payload.get("url") or ""),
                [existing, search_audit],
            )
        return [by_source.get(str(payload.get("source") or ""), {}) for payload in payloads]

    def _collect_codex_web_search_source(
        self,
        request: VehicleQuery,
        payload: dict[str, Any],
        job_dir: Path,
        *,
        codex_path: str,
        host_chrome_attempted: bool,
    ) -> dict[str, Any]:
        source = str(payload["source"])
        if source != "edmunds_browser":
            raise ValueError("Codex web-search capture currently supports Edmunds only")
        years = sorted(
            {
                int(year)
                for year in (
                    payload.get("target_years")
                    or range(int(payload["start_year"]), int(payload["end_year"]) + 1)
                )
            }
        )
        if not years:
            raise ValueError("Codex web-search fallback received no target years")
        raw_output_path = job_dir / f"codex_web_search_{source}.json"
        stdout_path = job_dir / f"codex_web_search_{source}.stdout.log"
        stderr_path = job_dir / f"codex_web_search_{source}.stderr.log"
        batches = [
            years[index : index + self.config.codex_search_batch_size]
            for index in range(0, len(years), self.config.codex_search_batch_size)
        ]

        def run_batch(batch_index: int, batch_years: list[int]) -> tuple[dict[str, Any], str, str]:
            batch_output = job_dir / f"codex_web_search_{source}_batch_{batch_index}.json"
            command = build_codex_web_search_command(
                codex_path=codex_path,
                root=self.config.root,
                schema_path=self.config.web_search_schema_path,
                output_path=batch_output,
            )
            page_urls = [_edmunds_search_page_url(request, year) for year in batch_years]
            completed = subprocess.run(
                command,
                input=build_codex_web_search_prompt(request, batch_years, page_urls),
                env=codex_environment(),
                text=True,
                capture_output=True,
                timeout=min(900, max(120, self.config.timeout_seconds)),
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(clean_codex_error(completed.stderr or completed.stdout))
            try:
                batch_result = json.loads(batch_output.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"Codex web search did not return valid JSON: {exc}") from exc
            if batch_result.get("source") != source:
                raise RuntimeError("Codex web-search source did not match the requested marketplace")
            return batch_result, completed.stdout or "", completed.stderr or ""

        batch_results: list[dict[str, Any]] = []
        batch_errors: list[str] = []
        stdout_parts: list[str] = []
        stderr_parts: list[str] = []
        with ThreadPoolExecutor(max_workers=min(self.config.codex_search_workers, len(batches))) as pool:
            future_map = {
                pool.submit(run_batch, batch_index, batch_years): batch_years
                for batch_index, batch_years in enumerate(batches)
            }
            for future in as_completed(future_map):
                batch_years = future_map[future]
                try:
                    batch_result, batch_stdout, batch_stderr = future.result()
                    batch_results.append(batch_result)
                    stdout_parts.append(batch_stdout)
                    stderr_parts.append(batch_stderr)
                except Exception as exc:
                    batch_errors.append(f"Years {batch_years}: {_cap_error(str(exc))}")
        stdout_path.write_text("\n".join(stdout_parts), encoding="utf-8")
        stderr_path.write_text("\n".join([*stderr_parts, *batch_errors]), encoding="utf-8")
        if not batch_results:
            raise RuntimeError("; ".join(batch_errors) or "Codex web search returned no batches")
        result = {
            "source": source,
            "status": "partial" if batch_errors else "success",
            "pages": [page for item in batch_results for page in item.get("pages") or []],
            "notes": [
                *[str(note) for item in batch_results for note in item.get("notes") or []],
                *batch_errors,
            ],
        }
        raw_output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

        listings: list[Listing] = []
        seen: set[tuple[Any, ...]] = set()
        accepted_pages: list[dict[str, Any]] = []
        rejected_pages = 0
        cards_examined = 0
        for page in result.get("pages") or []:
            if not isinstance(page, dict):
                rejected_pages += 1
                continue
            url = str(page.get("url") or "")
            try:
                _validate_marketplace_url(source, url)
            except ValueError:
                rejected_pages += 1
                continue
            try:
                model_year = int(page.get("model_year") or 0)
            except (TypeError, ValueError):
                rejected_pages += 1
                continue
            if model_year not in years:
                rejected_pages += 1
                continue
            visible_text = str(page.get("visible_text") or "")[:250_000]
            if not visible_text.strip():
                rejected_pages += 1
                continue
            page_cards = len(
                re.findall(r"(?m)^\s*(?:(?:used|new|certified)\s+)?(?:19|20)\d{2}\s+", visible_text, re.I)
            )
            cards_examined += page_cards
            accepted_before = len(listings)
            for listing in parse_visible_listing_text(source, url, visible_text, request):
                if not listing_year_in_scope(listing.year, request):
                    continue
                identity = (
                    listing.vin,
                    listing.year,
                    round(listing.price),
                    listing.mileage,
                    listing.title.lower(),
                )
                if identity in seen:
                    continue
                seen.add(identity)
                listings.append(listing)
            accepted_pages.append(
                {
                    "page": len(accepted_pages) + 1,
                    "url": url,
                    "cards_examined": page_cards,
                    "accepted_new": len(listings) - accepted_before,
                    "detail_pages_opened": 0,
                    "search_scope": "codex_web_search",
                    "search_year": model_year,
                }
            )

        quota = _browser_year_quota(listings, request)
        audit = {
            "version": 1,
            "source": source,
            "url": str(payload["url"]),
            "browser_mode": "codex_web_search",
            "background_mode": True,
            "browser_verified": False,
            "search_verified": True,
            "deterministic_verified": True,
            "host_chrome_attempted": host_chrome_attempted,
            "codex_search_attempted": True,
            "status": "collected" if listings and quota["met"] else "partial" if listings else "unavailable",
            "pages_examined": len(accepted_pages),
            "cards_examined": max(cards_examined, len(listings)),
            "accepted": len(listings),
            "rejected_by_reason": {"invalid_search_page": rejected_pages} if rejected_pages else {},
            "load_more_clicked": 0,
            "detail_pages_opened": 0,
            "stop_reason": "codex_web_search_complete" if listings else "codex_web_search_no_rows",
            "access_message": "",
            "year_quota": quota,
            "page_records": accepted_pages,
            "requested_year_searches": len(years),
            "attempted_year_searches": len(accepted_pages),
            "avoided_year_searches": max(0, len(years) - len(accepted_pages)),
            "skipped_year_searches": 0,
            "search_notes": [str(item)[:1000] for item in result.get("notes") or []],
            "search_batches": len(batches),
            "search_workers": min(self.config.codex_search_workers, len(batches)),
            "listings": [item.to_dict() for item in listings],
        }
        (job_dir / f"browser_capture_{source}.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
        return audit

    def _collect_host_chrome_source(
        self,
        request: VehicleQuery,
        payload: dict[str, Any],
        job_dir: Path,
    ) -> dict[str, Any]:
        source = str(payload["source"])
        requested_url = str(payload["url"])
        searches: list[tuple[str, int | None]] = [(requested_url, None)]
        captures: list[dict[str, Any]] = []
        listings: list[Listing] = []
        seen: set[tuple[Any, ...]] = set()
        access_message = ""
        access_blocked = False

        search_index = 0
        while search_index < len(searches):
            search_url, search_year = searches[search_index]
            capture = capture_with_host_chrome(
                source=source,
                url=search_url,
                script_path=self.config.chrome_host_script_path,
                background_mode=self.config.background_mode,
            )
            capture["searchYear"] = search_year
            captures.append(capture)
            accepted_before = len(listings)
            if capture_is_access_wall(capture):
                access_blocked = True
                access_message = capture_access_message(capture)
                capture["acceptedNew"] = 0
                raw_path = job_dir / f"host_chrome_{source}_{search_index}.json"
                raw_path.write_text(json.dumps(capture, indent=2), encoding="utf-8")
                break
            for listing in parse_visible_listing_text(source, search_url, str(capture.get("text") or ""), request):
                if not listing_year_in_scope(listing.year, request):
                    continue
                identity = (
                    listing.vin,
                    listing.year,
                    round(listing.price),
                    listing.mileage,
                    listing.title.lower(),
                )
                if identity in seen:
                    continue
                seen.add(identity)
                listings.append(listing)
            capture["acceptedNew"] = len(listings) - accepted_before
            raw_path = job_dir / f"host_chrome_{source}_{search_index}.json"
            raw_path.write_text(json.dumps(capture, indent=2), encoding="utf-8")

            if search_index == 0:
                sparse_years = sorted(_browser_year_quota(listings, request)["sparse_years"], reverse=True)
                target_years = {int(year) for year in payload.get("target_years") or sparse_years}
                sparse_years = [year for year in sparse_years if year in target_years]
                searches.extend((_browser_url_for_year(requested_url, source, year), year) for year in sparse_years)
            search_index += 1

        quota = _browser_year_quota(listings, request)
        pages_examined = sum(int(item.get("pagesExamined") or 0) for item in captures)
        cards_examined = sum(int(item.get("cardsExamined") or 0) for item in captures)
        load_more_clicked = sum(int(item.get("loadMoreClicked") or 0) for item in captures)
        attempted_year_searches = sum(1 for item in captures if item.get("searchYear") is not None)
        planned_year_searches = max(0, len(searches) - 1)
        audit = {
            "version": 1,
            "source": source,
            "url": requested_url,
            "browser_mode": "system_chrome_applescript",
            "background_mode": all(bool(item.get("backgroundMode")) for item in captures) if captures else self.config.background_mode,
            "browser_verified": True,
            "host_chrome_attempted": True,
            "status": (
                "collected"
                if listings and quota["met"]
                else "partial"
                if listings
                else "blocked"
                if access_blocked
                else "unavailable"
            ),
            "pages_examined": pages_examined,
            "cards_examined": max(cards_examined, len(listings)),
            "accepted": len(listings),
            "rejected_by_reason": {},
            "load_more_clicked": load_more_clicked,
            "detail_pages_opened": 0,
            "stop_reason": (
                "host_chrome_access_wall"
                if access_blocked
                else "year_targets_met"
                if quota["met"]
                else "host_chrome_searches_complete"
            ),
            "access_message": access_message,
            "year_quota": quota,
            "page_records": [
                {
                    "page": index + 1,
                    "url": str(item.get("requestedUrl") or item.get("url") or ""),
                    "cards_examined": int(item.get("cardsExamined") or 0),
                    "accepted_new": int(item.get("acceptedNew") or 0),
                    "detail_pages_opened": 0,
                    "search_scope": "year" if item.get("searchYear") is not None else "range",
                    "search_year": item.get("searchYear"),
                }
                for index, item in enumerate(captures)
            ],
            "requested_year_searches": int(payload["end_year"]) - int(payload["start_year"]) + 1,
            "range_search": {
                "status": "blocked" if access_blocked and len(captures) == 1 else "collected",
                "pages_examined": int(captures[0].get("pagesExamined") or 0) if captures else 0,
                "cards_examined": int(captures[0].get("cardsExamined") or 0) if captures else 0,
                "accepted": int(captures[0].get("acceptedNew") or 0) if captures else 0,
                "load_more_clicked": int(captures[0].get("loadMoreClicked") or 0) if captures else 0,
                "stop_reason": "access_wall" if access_blocked and len(captures) == 1 else "range_search_complete",
            },
            "attempted_year_searches": attempted_year_searches,
            "avoided_year_searches": max(0, int(payload["end_year"]) - int(payload["start_year"]) + 1 - planned_year_searches),
            "skipped_year_searches": max(0, planned_year_searches - attempted_year_searches) if access_blocked else 0,
            "listings": [item.to_dict() for item in listings],
        }
        (job_dir / f"browser_capture_{source}.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
        return audit

    def _update(self, job_id: str, **updates: Any) -> None:
        sync_fallback = bool(
            updates.get("result") is not None and updates.get("status") in {"completed", "blocked"}
        )
        with self._lock:
            job = self._jobs[job_id]
            for key, value in updates.items():
                setattr(job, key, value)
            job.updated_at = time.time()
        if sync_fallback:
            self._sync_fallback_lease(job_id)

    def _write_job_result(self, job_id: str, result: dict[str, Any]) -> None:
        job_dir = self.config.jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        (job_dir / "collector_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    def _restore_fallback_lease(self, job: CollectionJob) -> None:
        path = self.config.jobs_dir / job.id / "fallback_lease.json"
        try:
            lease = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        job.fallback_status = str(lease.get("status") or "")
        job.fallback_created_at = float(lease.get("createdAt") or 0)
        job.fallback_expires_at = float(lease.get("expiresAt") or 0)
        job.fallback_sources = [
            str(source) for source in lease.get("sources") or [] if str(source) in BROWSER_SOURCE_NAMES
        ]
        if job.fallback_status == "pending" and time.time() >= job.fallback_expires_at:
            job.fallback_status = "expired"
            job.fallback_sources = []
            self._write_fallback_lease(job)

    def _sync_fallback_lease(self, job_id: str) -> None:
        now = time.time()
        with self._lock:
            job = self._jobs[job_id]
            needed = _browser_sources_needing_fallback(job.result)
            if not needed:
                if job.fallback_status:
                    job.fallback_status = "completed"
                    job.fallback_sources = []
                else:
                    return
            elif job.fallback_status == "pending" and now < job.fallback_expires_at:
                job.fallback_sources = needed
                job.fallback_expires_at = now + self.config.fallback_lease_seconds
            elif not job.fallback_status:
                job.fallback_status = "pending"
                job.fallback_created_at = now
                job.fallback_expires_at = now + self.config.fallback_lease_seconds
                job.fallback_sources = needed
            else:
                return
            snapshot = CollectionJob(**asdict(job))
        self._write_fallback_lease(snapshot)

    def _expire_fallback_lease(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job.fallback_status != "pending" or time.time() < job.fallback_expires_at:
                return
            job.fallback_status = "expired"
            job.fallback_sources = []
            snapshot = CollectionJob(**asdict(job))
        self._write_fallback_lease(snapshot)

    def _write_fallback_lease(self, job: CollectionJob) -> None:
        job_dir = self.config.jobs_dir / job.id
        job_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "jobId": job.id,
            "status": job.fallback_status,
            "createdAt": job.fallback_created_at,
            "expiresAt": job.fallback_expires_at,
            "sources": list(job.fallback_sources),
        }
        (job_dir / "fallback_lease.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _browser_sources_needing_fallback(result: dict[str, Any] | None) -> list[str]:
    if not result:
        return []
    rows = {
        str(item.get("source") or ""): item
        for item in result.get("sources") or []
        if str(item.get("source") or "") in BROWSER_SOURCE_NAMES
    }
    listing_counts = {source: 0 for source in rows}
    for listing in result.get("listings") or []:
        listing_sources = set(str(listing.get("source") or "").split("+"))
        for source in listing_counts:
            if source in listing_sources:
                listing_counts[source] += 1

    needed = []
    for source in sorted(rows):
        row = rows.get(source) or {}
        status = str(row.get("status") or "unavailable")
        accepted = int(row.get("accepted") or listing_counts[source])
        if row.get("codex_search_attempted") and str(row.get("stop_reason") or "").startswith(
            "codex_web_search"
        ):
            continue
        if row.get("host_chrome_attempted") and str(row.get("stop_reason") or "").startswith(
            ("host_chrome_", "year_targets_met")
        ):
            continue
        if status in {"blocked", "unavailable"} or accepted <= 0:
            needed.append(source)
    return needed


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
- A project-local MCP tool named collect_vehicle_source is the authoritative browser collector. The app already ran the complete marketplace pass before this review. Do not call the tool again in this job; review its coverage, preserve sparse/blocked disclosures, and use non-marketplace research only where useful.
- Pass each target's source, URL, required_keywords, and exclude_keywords to that tool. Use the requested year range, current year, and max_pages=20.
- The tool persists deterministic listing cards and page audits for the app. Do not retype, alter, or invent its listing rows.
- A browser source may be called collected only when collect_vehicle_source returns browser_verified=true. Search snippets and cached page summaries are not browser evidence.
- If you are running inside Codex desktop and can show/use the browser, make website operation visible.
- Open the target URLs, confirm the visible page matches the requested vehicle, scroll results, and click visible Load More / See More Results / Next controls when available.
- After clicking a load-more control, verify that listing count, visible listing text, or page height changed. If it does not change, record that in source notes and continue.
- Stop on CAPTCHA, login-only wall, paywall, or access refusal. Do not bypass restrictions.
- Each target includes required_keywords, exclude_keywords, model_aliases, and location_policy. Treat those as binding collection rules.
- The resolver includes chips with mode="exact", mode="family", mode="range", mode="constrained", or mode="all". Exact/range chips restrict collection; family chips require the named family while allowing its configured descendants; constrained chips inherit named sibling exclusions from the exact trim; all chips mean include every visible variant for that dimension.
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


def build_codex_web_search_command(
    *,
    codex_path: str,
    root: Path,
    schema_path: Path,
    output_path: Path,
) -> list[str]:
    return [
        codex_path,
        "--search",
        "--ask-for-approval",
        "never",
        "exec",
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


def build_codex_web_search_prompt(
    request: VehicleQuery,
    years: list[int],
    page_urls: list[str],
) -> str:
    plan = build_collection_plan(request)
    matching = plan["matching"]
    current_year = _runtime_current_year()
    targets = {
        year: 15 if year >= current_year - 5 else 8
        for year in years
    }
    return f"""
Use the native live web-search tool to collect public sale-listing evidence from official Edmunds pages.

Requested vehicle: {request.raw}
Canonical vehicle: {request.display_name}
Years: {json.dumps(years)}
Target listing blocks per year: {json.dumps(targets)}
Required whole-token matching: {json.dumps(matching["required_keywords"])}
Excluded variants: {json.dumps(matching["exclude_keywords"])}
Trim scope: {json.dumps(matching["trim_scope"])}

Open each exact official page with web search:
{json.dumps(page_urls, indent=2)}

Return source=edmunds_browser. Create at most one pages[] item per model year, using the official Edmunds URL that supplied the text.
For each page, copy as many complete sale-listing blocks as the search result exposes, up to that year's target.
The visible_text must be verbatim source evidence, not a summary. Preserve one block after another with these fields when shown:
- listing title containing year, make, model, and trim
- asking price
- mileage
- VIN

Include only active for-sale inventory blocks. Omit appraisal values, trade-in/private-party estimates, editorial text, aggregate averages, advertisements for other models, and any block whose title/price/mileage cannot be copied from the official page. Never infer, calculate, rewrite, or manufacture a field. Do not use snippets or facts from any non-Edmunds host. If a year exposes no complete blocks, omit that page and explain it briefly in notes.

For BMW M4 Competition, 2021+ Competition Coupe/Convertible and RWD/xDrive qualify; Base, CS, CSL, and GTS do not. For 2016-2020, include only text that explicitly verifies the factory ZCP/Competition Package.
""".strip()


def _edmunds_search_page_url(request: VehicleQuery, year: int) -> str:
    make_slug = re.sub(r"[^a-z0-9]+", "-", request.make.lower()).strip("-")
    model_slug = re.sub(r"[^a-z0-9]+", "-", request.model.lower()).strip("-")
    return f"https://www.edmunds.com/{make_slug}/{model_slug}/{year}/for-sale/"


def _validate_marketplace_url(source: str, url: str) -> None:
    expected_host = BROWSER_SOURCE_HOSTS.get(source)
    if not expected_host:
        raise ValueError("Unsupported marketplace source")
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not (
        hostname == expected_host or hostname.endswith(f".{expected_host}")
    ):
        raise ValueError(f"Capture URL must use {expected_host}")


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
    expected_browser_sources = {
        str(target["source"])
        for target in build_collection_plan(request)["targets"]
        if str(target.get("source") or "") in BROWSER_SOURCE_NAMES
    }
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
    combined_year_coverage: dict[str, Any] = {}

    for capture_path in sorted(job_dir.glob("browser_capture_*.json")):
        try:
            audit = json.loads(capture_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        source = str(audit.get("source") or "")
        deterministic_verified = bool(
            audit.get("browser_verified") is True
            or (audit.get("search_verified") is True and audit.get("deterministic_verified") is True)
        )
        if source not in expected_browser_sources or not deterministic_verified:
            continue
        audited_sources.add(source)
        if isinstance(audit.get("combined_year_coverage"), dict):
            combined_year_coverage = dict(audit["combined_year_coverage"])
        accepted_rows: list[dict[str, Any]] = []
        accepted_listings: list[Listing] = []
        outside_year_window = 0
        for item in audit.get("listings") or []:
            parsed = listings_from_result({"listings": [item]})
            if not parsed:
                continue
            listing = parsed[0]
            if not listing_year_in_scope(listing.year, request):
                outside_year_window += 1
                continue
            match = vehicle_text_match_score(request, listing.title, listing.trim, source)
            if not match["accepted"]:
                continue
            accepted_listings.append(listing)
            accepted_rows.append(listing.to_dict())
        merged["listings"].extend(accepted_rows)
        rejected = dict(audit.get("rejected_by_reason") or {})
        if outside_year_window:
            rejected["outside_year_window"] = int(rejected.get("outside_year_window") or 0) + outside_year_window
        year_quota = _browser_year_quota(accepted_listings, request)
        sparse_years = year_quota.get("sparse_years") or []
        combined_coverage = audit.get("combined_year_coverage") if isinstance(audit.get("combined_year_coverage"), dict) else {}
        skipped_year_searches = int(audit.get("skipped_year_searches") or 0)
        verification_label = "Codex web search + deterministic parser" if audit.get("search_verified") else "Browser"
        if audit.get("cache_verified"):
            verification_label += " + verified cache"
        diagnostics = (
            f"{verification_label} verified {int(audit.get('pages_examined') or 0)} page(s), examined "
            f"{int(audit.get('cards_examined') or 0)} cards, and accepted {len(accepted_rows)} exact rows. "
            f"Browser: {audit.get('browser_mode') or 'unknown'}. Stop: {audit.get('stop_reason') or 'unknown'}."
        )
        if skipped_year_searches:
            diagnostics += f" Skipped {skipped_year_searches} remaining year search(es) after the access wall."
        if sparse_years and combined_coverage.get("met"):
            diagnostics += " Source-local quota was not required because combined cross-source coverage met."
        elif sparse_years:
            diagnostics += " Sparse years: " + ", ".join(str(year) for year in sparse_years) + "."
        source_rows.append(
            {
                "source": source,
                "url": str(audit.get("url") or ""),
                "status": str(audit.get("status") or "partial"),
                "load_more_clicked": int(audit.get("load_more_clicked") or 0),
                "notes": diagnostics,
                "browser_verified": bool(audit.get("browser_verified")),
                "search_verified": bool(audit.get("search_verified")),
                "deterministic_verified": deterministic_verified,
                "pages_examined": int(audit.get("pages_examined") or 0),
                "cards_examined": int(audit.get("cards_examined") or 0),
                "detail_pages_opened": int(audit.get("detail_pages_opened") or 0),
                "browser_mode": str(audit.get("browser_mode") or "unknown"),
                "background_mode": bool(audit.get("background_mode")),
                "cache_verified": bool(audit.get("cache_verified")),
                "cache_entries": int(audit.get("cache_entries") or 0),
                "cache_years": list(audit.get("cache_years") or []),
                "host_chrome_attempted": bool(audit.get("host_chrome_attempted")),
                "codex_search_attempted": bool(audit.get("codex_search_attempted")),
                "accepted": len(accepted_rows),
                "rejected_by_reason": rejected,
                "stop_reason": str(audit.get("stop_reason") or ""),
                "year_quota": year_quota,
                "attempted_year_searches": int(audit.get("attempted_year_searches") or 0),
                "skipped_year_searches": skipped_year_searches,
            }
        )
        quality_sources.append(source_rows[-1])

    for source in sorted(expected_browser_sources - audited_sources):
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
        "searchAudited": any(item.get("search_verified") for item in quality_sources),
        "deterministicAudited": bool(quality_sources),
        "individualRows": individual_count,
        "combinedYearCoverage": combined_year_coverage,
        "sources": quality_sources,
    }
    if combined_year_coverage:
        merged["combinedYearCoverage"] = combined_year_coverage
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
    legacy_weights = _legacy_aggregate_weights(result)
    for item_index, item in enumerate(result.get("listings") or []):
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
            try:
                market_weight = float(item.get("market_weight", legacy_weights.get(item_index, 1.0)))
            except (TypeError, ValueError):
                market_weight = 1.0
            if not math.isfinite(market_weight) or not 0 < market_weight <= MAX_MARKET_WEIGHT:
                market_weight = 1.0
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
                    market_weight=market_weight,
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return rows


def _legacy_aggregate_weights(result: dict[str, Any]) -> dict[int, float]:
    items = result.get("listings") or []
    evidence = result.get("evidence") or []
    if not isinstance(evidence, list):
        return {}

    item_keys: dict[int, tuple[str, int, str, int]] = {}
    samples_per_bin: dict[tuple[str, int, str, int], int] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict) or item.get("market_weight") not in (None, ""):
            continue
        source = str(item.get("source") or "").lower()
        if "facet" not in source and "aggregate" not in source:
            continue
        match = re.search(r"\baggregate bin (\d+) sample\b", str(item.get("title") or ""), re.I)
        if not match:
            continue
        try:
            key = (source, int(item.get("year") or 0), str(item.get("url") or ""), int(match.group(1)) - 1)
        except (TypeError, ValueError):
            continue
        item_keys[index] = key
        samples_per_bin[key] = samples_per_bin.get(key, 0) + 1

    represented_per_bin: dict[tuple[str, int, str, int], float] = {}
    for facet in evidence:
        if not isinstance(facet, dict):
            continue
        source = str(facet.get("source") or "").lower()
        try:
            year = int(facet.get("year") or 0)
        except (TypeError, ValueError):
            continue
        url = str(facet.get("url") or "")
        for bin_index, item in enumerate(facet.get("price_bins") or []):
            try:
                count = float(item.get("count") or 0)
            except (TypeError, ValueError):
                continue
            if count > 0:
                represented_per_bin[(source, year, url, bin_index)] = count

    return {
        index: represented_per_bin[key] / samples_per_bin[key]
        for index, key in item_keys.items()
        if represented_per_bin.get(key, 0) > 0 and samples_per_bin.get(key, 0) > 0
    }


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


def _browser_year_quota(listings: list[Listing], request: VehicleQuery) -> dict[str, Any]:
    current_year = _runtime_current_year()
    start_year = request.target_year or max(
        current_year - request.max_age,
        request.start_year or current_year - request.max_age,
    )
    end_year = request.target_year or current_year
    counts: dict[int, int] = {}
    for listing in listings:
        counts[listing.year] = counts.get(listing.year, 0) + 1
    targets = {
        year: 15 if year >= current_year - 5 else 8
        for year in range(start_year, end_year + 1)
    }
    sparse_years = [year for year, target in targets.items() if counts.get(year, 0) < target]
    return {
        "counts": counts,
        "targets": targets,
        "sparse_years": sparse_years,
        "met": not sparse_years,
    }


def _verified_audit_listings(request: VehicleQuery, audit: dict[str, Any]) -> list[Listing]:
    source = str(audit.get("source") or "")
    rows: list[Listing] = []
    seen: set[tuple[Any, ...]] = set()
    for listing in listings_from_result({"listings": audit.get("listings") or []}):
        if source in BROWSER_SOURCE_NAMES and listing.source != source:
            continue
        if not listing_year_in_scope(listing.year, request):
            continue
        if not vehicle_text_match_score(request, listing.title, listing.trim, source)["accepted"]:
            continue
        identity = _listing_identity(listing)
        if identity in seen:
            continue
        seen.add(identity)
        rows.append(listing)
    return rows


def _listing_identity(listing: Listing) -> tuple[Any, ...]:
    if listing.vin:
        return ("vin", listing.vin.upper())
    return (
        "row",
        listing.year,
        round(listing.price),
        listing.mileage,
        listing.title.casefold(),
        listing.dealer.casefold(),
    )


def _audit_from_cache_entries(
    request: VehicleQuery,
    payload: dict[str, Any],
    entries: list[Any],
) -> dict[str, Any]:
    source = str(payload["source"])
    listings: list[Listing] = []
    seen: set[tuple[Any, ...]] = set()
    browser_verified = False
    search_verified = False
    background_modes: list[bool] = []
    modes: set[str] = set()
    for entry in entries:
        item = dict(entry.payload)
        item["source"] = source
        browser_verified = browser_verified or bool(item.get("browser_verified"))
        search_verified = search_verified or bool(item.get("search_verified"))
        background_modes.append(bool(item.get("background_mode")))
        if item.get("browser_mode"):
            modes.add(str(item["browser_mode"]))
        for listing in _verified_audit_listings(request, item):
            if listing.year != int(entry.model_year):
                continue
            identity = _listing_identity(listing)
            if identity in seen:
                continue
            seen.add(identity)
            listings.append(listing)
    quota = _browser_year_quota(listings, request)
    return {
        "version": 1,
        "source": source,
        "url": str(payload.get("url") or ""),
        "browser_mode": "verified_cache" + (f"({'+'.join(sorted(modes))})" if modes else ""),
        "browser_verified": browser_verified,
        "search_verified": search_verified,
        "deterministic_verified": True,
        "background_mode": all(background_modes) if background_modes else False,
        "cache_verified": True,
        "cache_entries": len(entries),
        "cache_years": sorted({int(entry.model_year) for entry in entries}),
        "cache_oldest_at": min((float(entry.captured_at) for entry in entries), default=0),
        "cache_newest_at": max((float(entry.captured_at) for entry in entries), default=0),
        "status": "collected" if listings and quota["met"] else "partial" if listings else "unavailable",
        "pages_examined": 0,
        "cards_examined": 0,
        "accepted": len(listings),
        "rejected_by_reason": {},
        "load_more_clicked": 0,
        "detail_pages_opened": 0,
        "stop_reason": "fresh_cache_hit" if listings else "cache_empty",
        "access_message": "",
        "year_quota": quota,
        "page_records": [],
        "requested_year_searches": 0,
        "attempted_year_searches": 0,
        "avoided_year_searches": len(entries),
        "skipped_year_searches": 0,
        "listings": [listing.to_dict() for listing in listings],
    }


def _merge_browser_audits(
    request: VehicleQuery,
    source: str,
    url: str,
    audits: list[dict[str, Any]],
) -> dict[str, Any]:
    usable = [audit for audit in audits if isinstance(audit, dict) and str(audit.get("source") or source) == source]
    listings: list[Listing] = []
    seen: set[tuple[Any, ...]] = set()
    rejected: dict[str, int] = {}
    page_records: list[dict[str, Any]] = []
    modes: list[str] = []
    errors: list[str] = []
    for audit in usable:
        for reason, count in (audit.get("rejected_by_reason") or {}).items():
            rejected[str(reason)] = rejected.get(str(reason), 0) + int(count or 0)
        for listing in _verified_audit_listings(request, {**audit, "source": source}):
            identity = _listing_identity(listing)
            if identity in seen:
                continue
            seen.add(identity)
            listings.append(listing)
        page_records.extend(item for item in audit.get("page_records") or [] if isinstance(item, dict))
        mode = str(audit.get("browser_mode") or "")
        if mode and mode not in modes:
            modes.append(mode)
        error = str(audit.get("error") or "").strip()
        if error and error not in errors:
            errors.append(error)
    quota = _browser_year_quota(listings, request)
    any_blocked = any(str(audit.get("status") or "") == "blocked" for audit in usable)
    deterministic_verified = any(
        audit.get("browser_verified") is True
        or (audit.get("search_verified") is True and audit.get("deterministic_verified") is True)
        for audit in usable
    )
    status = (
        "collected"
        if listings and quota["met"]
        else "partial"
        if listings
        else "blocked"
        if any_blocked
        else "unavailable"
    )
    return {
        "version": 1,
        "source": source,
        "url": url,
        "browser_mode": "+".join(modes) or "unknown",
        "browser_verified": any(bool(audit.get("browser_verified")) for audit in usable),
        "search_verified": any(bool(audit.get("search_verified")) for audit in usable),
        "deterministic_verified": deterministic_verified,
        "background_mode": all(bool(audit.get("background_mode")) for audit in usable) if usable else False,
        "cache_verified": any(bool(audit.get("cache_verified")) for audit in usable),
        "cache_entries": sum(int(audit.get("cache_entries") or 0) for audit in usable),
        "cache_years": sorted(
            {
                int(year)
                for audit in usable
                for year in audit.get("cache_years") or []
            }
        ),
        "host_chrome_attempted": any(bool(audit.get("host_chrome_attempted")) for audit in usable),
        "codex_search_attempted": any(bool(audit.get("codex_search_attempted")) for audit in usable),
        "status": status,
        "pages_examined": sum(int(audit.get("pages_examined") or 0) for audit in usable),
        "cards_examined": sum(int(audit.get("cards_examined") or 0) for audit in usable),
        "accepted": len(listings),
        "rejected_by_reason": rejected,
        "load_more_clicked": sum(int(audit.get("load_more_clicked") or 0) for audit in usable),
        "detail_pages_opened": sum(int(audit.get("detail_pages_opened") or 0) for audit in usable),
        "stop_reason": "year_targets_met" if quota["met"] else "combined_capture_complete" if listings else "access_wall" if any_blocked else "no_rows",
        "access_message": " | ".join(
            str(audit.get("access_message") or "").strip()
            for audit in usable
            if str(audit.get("access_message") or "").strip()
        )[:1000],
        "error": " | ".join(errors)[:1000],
        "year_quota": quota,
        "page_records": page_records,
        "range_search": next((audit.get("range_search") for audit in usable if audit.get("range_search")), None),
        "requested_year_searches": max((int(audit.get("requested_year_searches") or 0) for audit in usable), default=0),
        "attempted_year_searches": sum(int(audit.get("attempted_year_searches") or 0) for audit in usable),
        "avoided_year_searches": max((int(audit.get("avoided_year_searches") or 0) for audit in usable), default=0),
        "skipped_year_searches": sum(int(audit.get("skipped_year_searches") or 0) for audit in usable),
        "listings": [listing.to_dict() for listing in listings],
    }


def _merge_audits_by_source(
    request: VehicleQuery,
    payloads: list[dict[str, Any]],
    audits: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        _merge_browser_audits(
            request,
            str(payload["source"]),
            str(payload.get("url") or ""),
            audits,
        )
        for payload in payloads
    ]


def _combined_year_coverage(
    request: VehicleQuery,
    baseline_result: dict[str, Any] | None,
    audits: list[dict[str, Any]],
) -> dict[str, Any]:
    targets = _browser_year_quota([], request)["targets"]
    aggregate_years: set[int] = set()
    for item in (baseline_result or {}).get("evidence") or []:
        if not isinstance(item, dict):
            continue
        source = str(item.get("source") or "").casefold()
        try:
            year = int(item.get("year") or 0)
        except (TypeError, ValueError):
            continue
        if year in targets and ("facet" in source or "aggregate" in source):
            aggregate_years.add(year)

    identities_by_year: dict[int, set[tuple[Any, ...]]] = {year: set() for year in targets}
    sources_by_year: dict[int, dict[str, int]] = {year: {} for year in targets}
    for audit in audits:
        source = str(audit.get("source") or "")
        if source not in BROWSER_SOURCE_NAMES:
            continue
        for listing in _verified_audit_listings(request, audit):
            if listing.year not in targets:
                continue
            identities_by_year[listing.year].add(_listing_identity(listing))
            source_counts = sources_by_year[listing.year]
            source_counts[source] = source_counts.get(source, 0) + 1

    years: dict[int, dict[str, Any]] = {}
    sparse_years: list[int] = []
    for year, target in targets.items():
        unique_rows = len(identities_by_year[year])
        source_counts = sources_by_year[year]
        independent_support = year in aggregate_years or len(source_counts) >= 2
        met = unique_rows >= int(target) and independent_support
        if not met:
            sparse_years.append(year)
        years[year] = {
            "target": int(target),
            "individual_rows": unique_rows,
            "individual_sources": source_counts,
            "aggregate_support": year in aggregate_years,
            "independent_support": independent_support,
            "met": met,
        }
    return {
        "years": years,
        "sparse_years": sparse_years,
        "met": not sparse_years,
    }


def _plan_browser_followups(
    request: VehicleQuery,
    payloads: list[dict[str, Any]],
    audits: list[dict[str, Any]],
    sparse_years: list[int],
) -> list[dict[str, Any]]:
    by_source = {str(audit.get("source") or ""): audit for audit in audits}
    payload_by_source = {str(payload["source"]): payload for payload in payloads}
    counts: dict[str, dict[int, int]] = {}
    for source, audit in by_source.items():
        source_counts: dict[int, int] = {}
        for listing in _verified_audit_listings(request, audit):
            source_counts[listing.year] = source_counts.get(listing.year, 0) + 1
        counts[source] = source_counts

    followups: list[dict[str, Any]] = []
    for year in sorted({int(item) for item in sparse_years}, reverse=True):
        candidates = []
        for source in sorted(BROWSER_SOURCE_NAMES):
            audit = by_source.get(source) or {}
            blocked = str(audit.get("status") or "") == "blocked" or "access_wall" in str(audit.get("stop_reason") or "")
            if not blocked and source in payload_by_source:
                candidates.append(source)
        if not candidates:
            continue
        source = min(candidates, key=lambda item: (counts.get(item, {}).get(year, 0), item != "autotrader_browser"))
        base = payload_by_source[source]
        followups.append(
            {
                **base,
                "url": _browser_url_for_year(str(base["url"]), source, year),
                "start_year": year,
                "end_year": year,
                "max_pages": 2,
                "split_by_year": False,
                "search_year": year,
            }
        )
    return followups


def _browser_url_for_year(raw_url: str, source: str, year: int) -> str:
    parsed = urlparse(raw_url)
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key not in {"pagenumber", "page", "startYear", "endYear", "year", "minimum-model-year", "maximum-model-year"}
    ]
    if source == "autotrader_browser":
        query.extend([("startYear", str(year)), ("endYear", str(year))])
    elif source == "edmunds_browser":
        query.append(("year", str(year)))
    elif source == "porsche_finder_browser":
        query.extend([("minimum-model-year", str(year)), ("maximum-model-year", str(year))])
    else:
        raise ValueError("Unsupported browser source")
    return urlunparse(parsed._replace(query=urlencode(query)))


def _infer_result_max_age(result: dict[str, Any]) -> int:
    years: list[int] = []
    for source in result.get("sources") or []:
        targets = (source.get("year_quota") or {}).get("targets") or {}
        for year in targets:
            try:
                years.append(int(year))
            except (TypeError, ValueError):
                continue
    if years:
        return max(1, min(20, max(years) - min(years)))
    return 10


def _collector_review_cache_identity(request: VehicleQuery) -> dict[str, Any]:
    return {
        "make": request.make.strip().casefold(),
        "model": request.model.strip().casefold(),
        "trim": request.trim.strip().casefold(),
        "start_year": request.start_year,
        "target_year": request.target_year,
        "max_age": int(request.max_age),
    }


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
