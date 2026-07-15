from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from car_compare.codex_cli import codex_login_status
from car_compare.collector import (
    CollectionManager,
    CollectorConfig,
    DEFAULT_FALLBACK_LEASE_SECONDS,
    MAX_MSRP_PRICE,
    MIN_MSRP_PRICE,
    _msrp_matches_request,
    listings_from_result,
    msrp_from_result,
)
from car_compare.depreciation import build_report
from car_compare.generation_impact import GenerationResearchConfig, GenerationResearchManager, normalize_generation_impact
from car_compare.models import Listing, MSRP
from car_compare.parser import parse_vehicle_query
from car_compare.sample_data import default_msrp_for, sample_listings_for
from car_compare.shared_auth import SharedSessionAuth
from car_compare.sources.browser_capture import parse_visible_listing_text
from car_compare.sources.source_plan import build_collection_plan
from car_compare.sources.site_status import SITE_STATUS


MAX_AGE_LIMIT = 20
MAX_REQUEST_BODY_BYTES = 4 * 1024 * 1024
ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
AUTH = SharedSessionAuth.from_environment()
SAMPLE_MODE_ENABLED = os.environ.get("CAR_COMPARE_SAMPLE_MODE", "").lower() in {"1", "true", "yes"}


def _environment_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


def _environment_bool(name: str, default: bool = True) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


COLLECTION_REQUEST_KEYS: dict[str, str] = {}
GENERATION_REQUEST_KEYS: dict[str, str] = {}
COLLECTOR = CollectionManager(
    CollectorConfig(
        root=ROOT,
        codex_path=os.environ.get("CODEX_BIN", "").strip(),
        dry_run=os.environ.get("CAR_COMPARE_COLLECTOR_DRY_RUN", "").lower() in {"1", "true", "yes"},
        use_visor_facets=os.environ.get("CAR_COMPARE_VISOR_FACETS", "1").lower() not in {"0", "false", "no"},
        cache_enabled=_environment_bool("CAR_COMPARE_CACHE_ENABLED"),
        cache_dir=(Path(os.environ["CAR_COMPARE_CACHE_DIR"]).expanduser() if os.environ.get("CAR_COMPARE_CACHE_DIR") else None),
        recent_cache_ttl_seconds=_environment_int("CAR_COMPARE_RECENT_CACHE_TTL_SECONDS", 3 * 24 * 60 * 60),
        older_cache_ttl_seconds=_environment_int("CAR_COMPARE_OLDER_CACHE_TTL_SECONDS", 3 * 24 * 60 * 60),
        collector_review_cache_ttl_seconds=_environment_int("CAR_COMPARE_REVIEW_CACHE_TTL_SECONDS", 3 * 24 * 60 * 60),
        marketplace_concurrency=_environment_int("CAR_COMPARE_MARKETPLACE_CONCURRENCY", 2),
        codex_search_workers=_environment_int("CAR_COMPARE_CODEX_SEARCH_WORKERS", 3),
        codex_search_batch_size=_environment_int("CAR_COMPARE_CODEX_SEARCH_BATCH_SIZE", 5),
        background_mode=_environment_bool("CAR_COMPARE_BACKGROUND_MODE"),
        fallback_lease_seconds=_environment_int(
            "CAR_COMPARE_FALLBACK_LEASE_SECONDS", DEFAULT_FALLBACK_LEASE_SECONDS
        ),
    )
)
GENERATION_RESEARCH = GenerationResearchManager(
    GenerationResearchConfig(
        root=ROOT,
        codex_path=os.environ.get("CODEX_BIN", "").strip(),
        dry_run=os.environ.get("CAR_COMPARE_GENERATION_DRY_RUN", "").lower() in {"1", "true", "yes"},
        cache_enabled=_environment_bool("CAR_COMPARE_CACHE_ENABLED"),
        cache_dir=(Path(os.environ["CAR_COMPARE_CACHE_DIR"]).expanduser() if os.environ.get("CAR_COMPARE_CACHE_DIR") else None),
        cache_ttl_seconds=_environment_int("CAR_COMPARE_GENERATION_CACHE_TTL_SECONDS", 3 * 24 * 60 * 60),
    )
)


class CarCompareHandler(BaseHTTPRequestHandler):
    server_version = "CarCompare/0.1"

    def do_GET(self) -> None:
        if not self._require_auth():
            return
        if self.path == "/" or self.path.startswith("/?"):
            self._send_file(STATIC / "index.html")
            return
        if self.path == "/codex-action" or self.path.startswith("/codex-action?"):
            self._send_file(STATIC / "codex-action.html")
            return
        if self.path == "/api/site-status":
            collector = COLLECTOR.availability()
            self._send_json(
                {
                    "sources": SITE_STATUS,
                    "collector": collector,
                    "generationResearch": GENERATION_RESEARCH.availability(),
                    "sampleMode": SAMPLE_MODE_ENABLED,
                }
            )
            return
        if self.path == "/api/health":
            self._send_json({"status": "ok", "app": "car-compare"})
            return
        if self.path == "/api/setup":
            codex = codex_login_status(os.environ.get("CODEX_BIN", ""))
            skill_path = ROOT / "skills" / "generation-impact-research" / "SKILL.md"
            collector = COLLECTOR.availability()
            self._send_json(
                {
                    "status": (
                        "ready"
                        if codex["available"]
                        and codex["authenticated"]
                        and skill_path.is_file()
                        and collector["browserWorkerAvailable"]
                        and collector["persistentBrowserReady"]
                        else "not-ready"
                    ),
                    "app": "car-compare",
                    "codex": codex,
                    "generationSkill": {
                        "ok": skill_path.is_file(),
                        "path": str(skill_path.parent),
                    },
                    "browserWorker": {
                        "ok": collector["browserWorkerAvailable"],
                        "persistentBrowserConfigured": collector["persistentBrowserConfigured"],
                        "persistentBrowserReady": collector["persistentBrowserReady"],
                        "persistentBrowserMode": collector["persistentBrowserMode"],
                        "persistentBrowserBackground": collector["persistentBrowserBackground"],
                        "persistentBrowserName": collector["persistentBrowserName"],
                        "hostChromeFallbackReady": collector["hostChromeFallbackReady"],
                        "hostChromeBackground": collector["hostChromeBackground"],
                        "backgroundMode": collector["backgroundMode"],
                        "path": str(ROOT / "scripts" / "car_compare_browser_mcp.mjs"),
                    },
                    "runtimeRoot": str(ROOT),
                }
            )
            return
        if self.path == "/api/codex-browser-actions":
            self._send_json({"actions": COLLECTOR.browser_actions()})
            return
        if self.path.startswith("/api/collect/"):
            job_id = self.path.removeprefix("/api/collect/").split("?", 1)[0]
            payload = COLLECTOR.job_payload(job_id)
            if not payload:
                self._send_error(404, "Collection job not found")
                return
            self._send_json(payload)
            return
        if self.path.startswith("/api/generation-impact/"):
            job_id = self.path.removeprefix("/api/generation-impact/").split("?", 1)[0]
            job = GENERATION_RESEARCH.get(job_id)
            if not job:
                self._send_error(404, "Generation research job not found")
                return
            self._send_json(job.to_dict())
            return
        if self.path.startswith("/static/"):
            rel = unquote(self.path.removeprefix("/static/").split("?", 1)[0])
            target = (STATIC / rel).resolve()
            if not str(target).startswith(str(STATIC.resolve())):
                self._send_error(403, "Forbidden")
                return
            self._send_file(target)
            return
        self._send_error(404, "Not found")

    def do_POST(self) -> None:
        if not self._require_auth():
            return
        known_paths = {
            "/api/research",
            "/api/collect",
            "/api/generation-impact",
            "/api/collection-plan",
            "/api/parse-visible-text",
            "/api/codex-browser-capture",
        }
        if self.path not in known_paths:
            self._send_error(404, "Not found")
            return
        try:
            body = self._read_json()
        except RequestBodyError as exc:
            self._send_error(exc.status, str(exc))
            return

        if self.path == "/api/research":
            query_text = str(body.get("query") or "").strip()
            if not query_text:
                self._send_error(400, "Missing query")
                return

            request = parse_vehicle_query(query_text)
            if not _has_vehicle_identity(request):
                self._send_error(400, "Query must resolve to a make and model")
                return
            request.max_age = _max_age_from_body(body, request.max_age)
            listings = _initial_listings(request)

            capture_text = str(body.get("captureText") or "").strip()
            capture_source = str(body.get("captureSource") or "manual").strip() or "manual"
            capture_url = str(body.get("captureUrl") or "").strip()
            if capture_text:
                listings.extend(
                    parse_visible_listing_text(
                        source=capture_source,
                        url=capture_url,
                        text=capture_text,
                        request=request,
                    )
                )

            msrp = _initial_msrp(request)
            job_id = str(body.get("jobId") or "").strip()
            job_result: dict[str, Any] | None = None
            if job_id:
                job = COLLECTOR.get(job_id)
                if not job:
                    self._send_error(404, "Collection job not found")
                    return
                job_request = parse_vehicle_query(job.query)
                job_request.max_age = job.max_age
                expected_request_key = COLLECTION_REQUEST_KEYS.get(job_id) or _request_key(job_request)
                if expected_request_key != _request_key(request):
                    self._send_error(409, "Collection job does not match this vehicle query and horizon")
                    return
                if job.result:
                    job_result = job.result
                listings.extend(COLLECTOR.listings_from_job(job_id))
                job_msrp = COLLECTOR.msrp_from_job(job_id)
                if job_msrp:
                    msrp = job_msrp

            collected_listings = body.get("collectedListings")
            if isinstance(collected_listings, list):
                listings.extend(_listings_from_payload(collected_listings))
            collected_msrp = body.get("collectedMsrp")
            if isinstance(collected_msrp, dict):
                payload_msrp = msrp_from_result({"msrp": collected_msrp})
                if payload_msrp and _msrp_matches_request(payload_msrp, request):
                    msrp = payload_msrp

            override_msrp = body.get("msrpPrice")
            if override_msrp not in (None, ""):
                try:
                    msrp.price = _validated_vehicle_price(override_msrp)
                    msrp.label = "User supplied MSRP"
                    msrp.source = "manual"
                    msrp.url = str(body.get("msrpUrl") or msrp.url)
                    msrp.year = request.target_year or datetime.now(timezone.utc).year
                except (OverflowError, TypeError, ValueError):
                    self._send_error(
                        400,
                        f"MSRP price must be between ${MIN_MSRP_PRICE:,.0f} and ${MAX_MSRP_PRICE:,.0f}",
                    )
                    return

            generation_impact = _generation_impact_from_body(body)
            generation_job_id = str(body.get("generationJobId") or "").strip()
            if generation_job_id:
                generation_job = GENERATION_RESEARCH.get(generation_job_id)
                if not generation_job:
                    self._send_error(404, "Generation job not found")
                    return
                if GENERATION_REQUEST_KEYS.get(generation_job_id) != _request_key(request):
                    self._send_error(409, "Generation job does not match this vehicle query and horizon")
                    return
                generation_impact = GENERATION_RESEARCH.impact_from_job(generation_job_id) or generation_impact

            report = build_report(request=request, listings=listings, msrp=msrp, generation_impact=generation_impact)
            report["collectionPlan"] = build_collection_plan(request)
            _attach_collector_evidence(report, job_result)
            _attach_report_metadata(report)
            self._send_json(report)
            return

        if self.path == "/api/collect":
            query_text = str(body.get("query") or "").strip()
            if not query_text:
                self._send_error(400, "Missing query")
                return
            max_age = _max_age_from_body(body)
            request = parse_vehicle_query(query_text)
            if not _has_vehicle_identity(request):
                self._send_error(400, "Query must resolve to a make and model")
                return
            request.max_age = max_age
            job = COLLECTOR.start(query_text, max_age)
            COLLECTION_REQUEST_KEYS[job.id] = _request_key(request)
            self._send_json(job.to_dict(), status=202)
            return

        if self.path == "/api/generation-impact":
            query_text = str(body.get("query") or "").strip()
            if not query_text:
                self._send_error(400, "Missing query")
                return
            max_age = _max_age_from_body(body)
            request = parse_vehicle_query(query_text)
            if not _has_vehicle_identity(request):
                self._send_error(400, "Query must resolve to a make and model")
                return
            request.max_age = max_age
            job = GENERATION_RESEARCH.start(query_text, max_age)
            GENERATION_REQUEST_KEYS[job.id] = _request_key(request)
            self._send_json(job.to_dict(), status=202)
            return

        if self.path == "/api/collection-plan":
            request = parse_vehicle_query(str(body.get("query") or ""))
            if not _has_vehicle_identity(request):
                self._send_error(400, "Query must resolve to a make and model")
                return
            request.max_age = _max_age_from_body(body, request.max_age)
            self._send_json(build_collection_plan(request))
            return

        if self.path == "/api/parse-visible-text":
            request = parse_vehicle_query(str(body.get("query") or ""))
            if not _has_vehicle_identity(request):
                self._send_error(400, "Query must resolve to a make and model")
                return
            listings = parse_visible_listing_text(
                source=str(body.get("source") or "manual"),
                url=str(body.get("url") or ""),
                text=str(body.get("text") or ""),
                request=request,
            )
            self._send_json({"listings": [item.to_dict() for item in listings]})
            return

        if self.path == "/api/codex-browser-capture":
            try:
                result = COLLECTOR.import_codex_browser_capture(
                    str(body.get("jobId") or "").strip(),
                    source=str(body.get("source") or "").strip(),
                    url=str(body.get("url") or "").strip(),
                    visible_text=str(body.get("visibleText") or ""),
                    pages_examined=int(body.get("pagesExamined") or 1),
                    cards_examined=int(body.get("cardsExamined") or 0),
                    load_more_clicked=int(body.get("loadMoreClicked") or 0),
                )
            except KeyError as exc:
                self._send_error(404, str(exc))
                return
            except RuntimeError as exc:
                self._send_error(409, str(exc))
                return
            except (TypeError, ValueError) as exc:
                self._send_error(400, str(exc))
                return
            self._send_json(result)
            return

    def log_message(self, fmt: str, *args: Any) -> None:
        print("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), fmt % args))

    def _require_auth(self) -> bool:
        if not AUTH.enabled or self.path.split("?", 1)[0] == "/api/health":
            return True
        if AUTH.valid_cookie_header(self.headers.get("Cookie")):
            return True
        request_path = self.path.split("?", 1)[0]
        if self.command == "GET" and not request_path.startswith("/api/"):
            self.send_response(303)
            self.send_header("Location", AUTH.login_redirect(self.path))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            self._send_json({"error": "authentication_required"}, status=401)
        return False

    def _read_json(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError as exc:
            raise RequestBodyError(400, "Invalid Content-Length") from exc
        if length < 0:
            raise RequestBodyError(400, "Invalid Content-Length")
        if length > MAX_REQUEST_BODY_BYTES:
            raise RequestBodyError(413, "Request body is too large")
        try:
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        except UnicodeDecodeError as exc:
            raise RequestBodyError(400, "Request body must be UTF-8 JSON") from exc
        if not raw.strip():
            return {}
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RequestBodyError(400, "Request body contains invalid JSON") from exc
        if not isinstance(payload, dict):
            raise RequestBodyError(400, "Request body must be a JSON object")
        return payload

    def _send_json(self, payload: Any, status: int = 200) -> None:
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self._send_error(404, "Not found")
            return
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def _send_error(self, status: int, message: str) -> None:
        self._send_json({"error": message}, status=status)


def _listings_from_payload(items: list[object]) -> list[Listing]:
    return listings_from_result({"listings": items})


def _initial_listings(request: Any) -> list[Listing]:
    return sample_listings_for(request) if SAMPLE_MODE_ENABLED else []


def _initial_msrp(request: Any) -> MSRP:
    if SAMPLE_MODE_ENABLED:
        return default_msrp_for(request)
    return MSRP(
        price=0,
        label="Needs verified MSRP capture",
        source="needs_manufacturer_capture",
        url="",
        year=request.target_year,
    )


def _attach_collector_evidence(report: dict[str, Any], job_result: dict[str, Any] | None) -> None:
    evidence = report.setdefault("evidence", {})
    if not job_result:
        evidence.setdefault("collectorSources", [])
        evidence.setdefault("facets", [])
        evidence.setdefault("collectorNotes", [])
        evidence.setdefault("collectionQuality", {})
        return
    evidence["collectorSources"] = job_result.get("sources") or []
    evidence["facets"] = job_result.get("evidence") or []
    evidence["collectorNotes"] = job_result.get("notes") or []
    evidence["collectionQuality"] = job_result.get("collectionQuality") or {}


class RequestBodyError(ValueError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def _request_key(request: Any) -> str:
    return json.dumps(
        {
            "make": request.make,
            "model": request.model,
            "trim": request.trim,
            "startYear": request.start_year,
            "targetYear": request.target_year,
            "maxAge": request.max_age,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def _attach_report_metadata(report: dict[str, Any]) -> None:
    summary = report.setdefault("summary", {})
    listing_count = max(0, int(summary.get("listingCount") or 0))
    sources = summary.get("sources") or {}
    sample_count = sum(int(count) for source, count in sources.items() if "sample" in source.lower())
    aggregate_points = sum(
        int(count)
        for source, count in sources.items()
        if "facet" in source.lower() or "aggregate" in source.lower()
    )
    aggregate_population = 0
    accepted_aggregate_keys = {
        (str(item.get("source") or "").lower(), int(item.get("year") or 0))
        for item in report.get("evidence", {}).get("listings", [])
        if "facet" in str(item.get("source") or "").lower()
        or "aggregate" in str(item.get("source") or "").lower()
    }
    for facet in report.get("evidence", {}).get("facets", []):
        facet_key = (str(facet.get("source") or "").lower(), int(facet.get("year") or 0))
        if facet_key not in accepted_aggregate_keys:
            continue
        bins = facet.get("price_bins") or []
        if bins:
            aggregate_population += sum(max(0, int(item.get("count") or 0)) for item in bins)
        else:
            aggregate_population += max(0, int((facet.get("price_stats") or {}).get("count") or 0))
    if SAMPLE_MODE_ENABLED:
        sample_count = listing_count
        aggregate_points = 0
        aggregate_population = 0
    individual_rows = max(0, listing_count - sample_count - aggregate_points)
    dealer_rows = 0
    for item in report.get("evidence", {}).get("listings", []):
        source = str(item.get("source") or "").lower()
        if "sample" in source or "facet" in source or "aggregate" in source:
            continue
        if str(item.get("dealer") or "").strip():
            dealer_rows += 1
    summary["sampleMode"] = SAMPLE_MODE_ENABLED
    summary["sampleRows"] = sample_count
    summary["aggregateObservationPoints"] = aggregate_points
    summary["aggregateMarketCount"] = (aggregate_population or aggregate_points) if aggregate_points else 0
    summary["individualListingRows"] = individual_rows
    summary["dealerListings"] = min(individual_rows, dealer_rows)
    summary["generatedAt"] = datetime.now(timezone.utc).isoformat()


def _generation_impact_from_body(body: dict[str, Any]) -> dict[str, Any] | None:
    item = body.get("generationImpact")
    if not isinstance(item, dict):
        return None
    return normalize_generation_impact(item)


def _max_age_from_body(body: dict[str, Any], default: int = 10) -> int:
    raw = body.get("maxAge", body.get("max_age", default))
    try:
        value = int(float(raw))
    except (TypeError, ValueError):
        value = default
    return max(1, min(MAX_AGE_LIMIT, value))


def _validated_vehicle_price(value: object) -> float:
    normalized = str(value).strip().replace("$", "").replace(",", "")
    price = float(normalized)
    if not math.isfinite(price) or not MIN_MSRP_PRICE <= price <= MAX_MSRP_PRICE:
        raise ValueError("vehicle price is outside the accepted range")
    return price


def _has_vehicle_identity(request: Any) -> bool:
    return bool(str(request.make or "").strip() and str(request.model or "").strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8787, type=int)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), CarCompareHandler)
    print(f"Car Compare running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Car Compare")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
