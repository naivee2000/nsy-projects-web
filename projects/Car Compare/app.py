from __future__ import annotations

import argparse
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from car_compare.collector import (
    CollectionManager,
    CollectorConfig,
    listings_from_result,
    msrp_from_result,
)
from car_compare.depreciation import build_report
from car_compare.models import Listing
from car_compare.parser import parse_vehicle_query
from car_compare.sample_data import default_msrp_for, sample_listings_for
from car_compare.sources.browser_capture import parse_visible_listing_text
from car_compare.sources.source_plan import build_collection_plan
from car_compare.sources.site_status import SITE_STATUS


MAX_AGE_LIMIT = 20
ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
COLLECTOR = CollectionManager(
    CollectorConfig(
        root=ROOT,
        codex_path=os.environ.get("CODEX_BIN", "").strip(),
        dry_run=os.environ.get("CAR_COMPARE_COLLECTOR_DRY_RUN", "").lower() in {"1", "true", "yes"},
        use_visor_facets=os.environ.get("CAR_COMPARE_VISOR_FACETS", "1").lower() not in {"0", "false", "no"},
    )
)


class CarCompareHandler(BaseHTTPRequestHandler):
    server_version = "CarCompare/0.1"

    def do_GET(self) -> None:
        if self.path == "/" or self.path.startswith("/?"):
            self._send_file(STATIC / "index.html")
            return
        if self.path == "/api/site-status":
            self._send_json({"sources": SITE_STATUS, "collector": COLLECTOR.availability()})
            return
        if self.path.startswith("/api/collect/"):
            job_id = self.path.removeprefix("/api/collect/").split("?", 1)[0]
            job = COLLECTOR.get(job_id)
            if not job:
                self._send_error(404, "Collection job not found")
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
        if self.path == "/api/research":
            body = self._read_json()
            query_text = str(body.get("query") or "").strip()
            if not query_text:
                self._send_error(400, "Missing query")
                return

            request = parse_vehicle_query(query_text)
            request.max_age = _max_age_from_body(body, request.max_age)
            listings = sample_listings_for(request)

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

            msrp = default_msrp_for(request)
            job_id = str(body.get("jobId") or "").strip()
            job_result: dict[str, Any] | None = None
            if job_id:
                job = COLLECTOR.get(job_id)
                if job and job.result:
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
                if payload_msrp:
                    msrp = payload_msrp

            override_msrp = body.get("msrpPrice")
            if override_msrp not in (None, ""):
                try:
                    msrp.price = float(override_msrp)
                    msrp.label = "User supplied MSRP"
                    msrp.source = "manual"
                    msrp.url = str(body.get("msrpUrl") or msrp.url)
                except (TypeError, ValueError):
                    self._send_error(400, "MSRP price must be numeric")
                    return

            report = build_report(request=request, listings=listings, msrp=msrp)
            report["collectionPlan"] = build_collection_plan(request)
            _attach_collector_evidence(report, job_result)
            self._send_json(report)
            return

        if self.path == "/api/collect":
            body = self._read_json()
            query_text = str(body.get("query") or "").strip()
            if not query_text:
                self._send_error(400, "Missing query")
                return
            job = COLLECTOR.start(query_text, _max_age_from_body(body))
            self._send_json(job.to_dict(), status=202)
            return

        if self.path == "/api/collection-plan":
            body = self._read_json()
            request = parse_vehicle_query(str(body.get("query") or ""))
            request.max_age = _max_age_from_body(body, request.max_age)
            self._send_json(build_collection_plan(request))
            return

        if self.path == "/api/parse-visible-text":
            body = self._read_json()
            request = parse_vehicle_query(str(body.get("query") or ""))
            listings = parse_visible_listing_text(
                source=str(body.get("source") or "manual"),
                url=str(body.get("url") or ""),
                text=str(body.get("text") or ""),
                request=request,
            )
            self._send_json({"listings": [item.to_dict() for item in listings]})
            return

        self._send_error(404, "Not found")

    def log_message(self, fmt: str, *args: Any) -> None:
        print("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), fmt % args))

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        if not raw.strip():
            return {}
        return json.loads(raw)

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
        self.end_headers()
        self.wfile.write(data)

    def _send_error(self, status: int, message: str) -> None:
        self._send_json({"error": message}, status=status)


def _listings_from_payload(items: list[object]) -> list[Listing]:
    return listings_from_result({"listings": items})


def _attach_collector_evidence(report: dict[str, Any], job_result: dict[str, Any] | None) -> None:
    evidence = report.setdefault("evidence", {})
    if not job_result:
        evidence.setdefault("collectorSources", [])
        evidence.setdefault("facets", [])
        evidence.setdefault("collectorNotes", [])
        return
    evidence["collectorSources"] = job_result.get("sources") or []
    evidence["facets"] = job_result.get("evidence") or []
    evidence["collectorNotes"] = job_result.get("notes") or []


def _max_age_from_body(body: dict[str, Any], default: int = 10) -> int:
    raw = body.get("maxAge", body.get("max_age", default))
    try:
        value = int(float(raw))
    except (TypeError, ValueError):
        value = default
    return max(1, min(MAX_AGE_LIMIT, value))


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
