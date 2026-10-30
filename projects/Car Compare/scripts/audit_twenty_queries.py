#!/usr/bin/env python3
"""Read-only local audit; opt-in bounded live Visor diagnostics, never collection jobs."""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import hashlib
import html
import json
import math
from pathlib import Path
import re
import sys
import tempfile
import time
from unittest.mock import patch
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MANIFEST = ROOT / "tests/fixtures/twenty_vehicle_queries.json"
VALIDATION_REVISION = 3
MAX_TTL_SECONDS = 259200
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
PUBLIC_PARAMETERS = {
    "make", "model", "model_family", "model_family_member", "trim", "version",
    "year", "car_type", "state", "radius", "distance",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")


def load_manifest(path: Path = MANIFEST) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    rows = value["queries"]
    if len(rows) != 20 or len({row["id"] for row in rows}) != 20 or len({row["query"] for row in rows}) != 20:
        raise ValueError("Expected exactly twenty distinct query IDs and queries")
    if value["probe_year"] != 2023 or value["probe_condition"] != "used":
        raise ValueError("This diagnostic is scoped to used 2023 inventory")
    return value


def select_queries(manifest: dict, selectors: list[str]) -> list[dict]:
    if not selectors:
        return manifest["queries"]
    chosen = set()
    for selector in selectors:
        matches = [row for row in manifest["queries"]
                   if selector.casefold() in {row["id"], row["query"].casefold(), str(int(row["id"]))}]
        if not matches:
            raise ValueError(f"Unknown query ID or exact query: {selector}")
        chosen.update(row["id"] for row in matches)
    return [row for row in manifest["queries"] if row["id"] in chosen]


def output_directory(output: str | None) -> tuple[Path, Path]:
    path = Path(output).expanduser().resolve() if output else Path(tempfile.mkdtemp(prefix="car-compare-audit-")) / "report.json"
    checkout = next((parent for parent in [ROOT, *ROOT.parents] if (parent / ".git").exists()), ROOT)
    if path.is_relative_to(checkout):
        raise ValueError("Audit output must be outside the checkout, including data/ and tests/fixtures/")
    if path.exists():
        raise ValueError("Choose a new output JSON path; prior audit evidence is never overwritten")
    path.parent.mkdir(parents=True, exist_ok=True)
    artifacts = path.parent / (path.stem + "_snapshots")
    artifacts.mkdir(exist_ok=False)
    return path, artifacts


def numeric(value: object) -> float | None:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


def timestamp(value: object) -> float | None:
    number = numeric(value)
    if number is not None:
        return number
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.timestamp() if parsed.tzinfo else None
        except ValueError:
            pass
    return None


def inspect_local(queries: list[dict], jobs_dir: Path, now: float | None = None) -> tuple[list[dict], list[dict]]:
    """Inspect files without constructing CollectionManager or opening any cache."""
    now = time.time() if now is None else now
    latest: dict[str, tuple[Path, dict]] = {}
    errors = []
    paths = sorted(jobs_dir.glob("*/collector_result.json"), key=lambda p: (p.stat().st_mtime, str(p)), reverse=True)
    for path in paths:
        try:
            result = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(result, dict) or not isinstance(result.get("query"), str):
                raise ValueError("invalid result shape")
            key = " ".join(result["query"].casefold().split())
            latest.setdefault(key, (path, result))
        except (OSError, ValueError) as exc:
            errors.append({"job_id": path.parent.name, "error_type": type(exc).__name__})
    rows = []
    for query in queries:
        row = {**query, "status": "no_saved_result", "end_to_end": "not_run"}
        entry = latest.get(" ".join(query["query"].casefold().split()))
        if entry:
            path, result = entry
            evidence = [item for item in result.get("evidence", []) if isinstance(item, dict)] if isinstance(result.get("evidence"), list) else []
            facets = [item for item in evidence if item.get("kind") == "visor_public_facets"]
            revision = numeric(result.get("validation_revision"))
            capture = timestamp(result.get("captured_at"))
            signatures = Counter(json.dumps({key: item.get(key) for key in ("num_found", "price_stats", "price_bins")}, sort_keys=True) for item in facets)
            listings = result.get("listings") if isinstance(result.get("listings"), list) else []
            sources = result.get("sources") if isinstance(result.get("sources"), list) else []
            row.update({
                "status": "saved_result_inspected", "job_id": path.parent.name,
                "saved_status": result.get("status"), "validation_revision": revision,
                "validation": "current_revision_requires_scope_review" if revision == VALIDATION_REVISION else "legacy_quarantined",
                "selected_by": "file_mtime_not_capture_time", "file_mtime": path.stat().st_mtime,
                "capture_time": capture,
                "freshness": "unknown" if capture is None else "future_timestamp_unverified" if capture > now else "within_max_ttl_not_cache_certification" if now - capture < MAX_TTL_SECONDS else "expired",
                "raw_listing_rows": len(listings), "facet_partitions": len(facets),
                "visor_reported_partition_sum_not_unique_cars": sum(numeric(item.get("num_found")) or 0 for item in facets),
                "repeated_facet_payloads_require_review": sum(count - 1 for count in signatures.values() if count > 1),
                "source_statuses": [{key: item.get(key) for key in ("source", "status")} for item in sources if isinstance(item, dict)],
                "report_replay": "not_run_historical_scope_not_revalidated",
            })
        rows.append(row)
    return rows, errors


def sanitize_text(text: str) -> str:
    """Redact identifiers from public unauthenticated HTML; save as inert text."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", "[REDACTED_EMAIL]", text)
    text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[REDACTED_IP]", text)
    text = re.sub(r"(?i)\b[A-HJ-NPR-Z0-9]{17}\b", "[REDACTED_ID]", text)
    text = re.sub(r"(?<!\d)(?:\+1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)", "[REDACTED_PHONE]", text)
    text = re.sub(r'''(?i)((?:["']?)(?:authorization|cookie|set-cookie|access_token|refresh_token|csrf_token|session_id|api_key|password)(?:["']?)\s*[:=]\s*)(?:"[^"\n]*"|'[^'\n]*'|[^\s<>&,;}]+)''', r'\1"[REDACTED]"', text)
    return text


def safe_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    params = [(key, value) for key, value in urllib.parse.parse_qsl(parts.query) if key in PUBLIC_PARAMETERS]
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(params), ""))


def snapshot_oracle(text: str) -> dict:
    """Independent small reader: ambiguous/missing fields stay unknown, never zero."""
    counts = {int(value) for value in re.findall(r"\bnum_found\s*:\s*(\d+)", text)}
    blocks = re.findall(r'\bprice\s*:\s*\$R\[\d+\]\s*=\s*\{([^{}]*)\}', text)
    stats = []
    for block in blocks:
        fields = {}
        for key, value in re.findall(r'\b(min|max|count|missing|mean|median|stddev)\s*:\s*(-?\d+(?:\.\d+)?)(?=\s*[,} ]|$)', block):
            fields[key] = float(value)
        if "median" in fields and "count" in fields:
            stats.append(fields)
    distinct = {json.dumps(item, sort_keys=True): item for item in stats}
    visible = html.unescape(re.sub(r"<[^>]*>", " ", re.sub(r"<script\b.*?</script>", " ", text, flags=re.I | re.S)))
    sale_counts = sorted({int(value.replace(",", "")) for value in re.findall(r"([\d,]+)\s+(?:cars|vehicles)\s+for\s+sale", visible, re.I)})
    return {
        "num_found": next(iter(counts)) if len(counts) == 1 else None,
        "price_stats": next(iter(distinct.values())) if len(distinct) == 1 else None,
        "visible_sale_counts": sale_counts,
        "scope_authority": "none_numeric_oracle_only",
    }


class AuditLimit(RuntimeError):
    pass


class StopRedirects(urllib.request.HTTPRedirectHandler):
    def __init__(self, session):
        self.session = session

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parts = urllib.parse.urlsplit(newurl)
        if parts.scheme != "https" or parts.netloc != "visor.vin" or parts.path != "/search/filters":
            raise AuditLimit("redirect_not_followed")
        if self.session.calls >= self.session.max_calls or time.monotonic() >= self.session.deadline:
            raise AuditLimit("redirect_call_limit")
        self.session.calls += 1
        self.session.total_calls += 1
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class CaptureSession:
    def __init__(self, directory: Path, max_calls: int = 3, deadline_seconds: float = 720, timeout: float = 18):
        self.directory = directory
        self.max_calls = max_calls
        self.deadline = time.monotonic() + deadline_seconds
        self.timeout = timeout
        self.total_calls = 0
        self.calls = 0
        self.cache: dict[str, str] = {}
        self.snapshots: list[dict] = []
        self.query_id = ""
        self.stop_reason = ""
        self.last_error = ""
        self.opener = urllib.request.build_opener(StopRedirects(self))

    def begin(self, query_id: str) -> None:
        self.query_id = query_id
        self.calls = 0
        self.cache = {}
        self.snapshots = []
        self.last_error = ""

    def fetch(self, url: str, *, deadline_at: float | None = None) -> str:
        if url in self.cache:
            return self.cache[url]
        remaining = self.deadline - time.monotonic()
        if self.stop_reason or remaining <= 0 or self.calls >= self.max_calls:
            self.last_error = self.stop_reason or ("deadline_exhausted" if remaining <= 0 else "query_call_limit")
            raise AuditLimit(self.last_error)
        parts = urllib.parse.urlsplit(url)
        if parts.scheme != "https" or parts.netloc != "visor.vin" or parts.path != "/search/filters":
            self.last_error = "source_url_not_allowlisted"
            raise AuditLimit(self.last_error)
        self.calls += 1
        self.total_calls += 1
        started = time.monotonic()
        record = {"url": safe_url(url), "captured_at": utc_now(), "status": "requested"}
        self.snapshots.append(record)
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149 Safari/537.36", "Accept": "text/html"})
            with self.opener.open(request, timeout=min(self.timeout, remaining)) as response:
                # Read in chunks so a slow response cannot silently outlive the shared deadline.
                chunks = []
                size = 0
                while True:
                    if time.monotonic() >= self.deadline:
                        raise AuditLimit("deadline_exhausted")
                    chunk = response.read(min(65536, MAX_RESPONSE_BYTES + 1 - size))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    size += len(chunk)
                    if size > MAX_RESPONSE_BYTES:
                        raise AuditLimit("response_size_limit")
                raw = b"".join(chunks)
                record["http_status"] = response.status
            text = raw.replace(b"\x00", b"").decode("utf-8", "replace")
            clean = sanitize_text(text)
            filename = f"{self.query_id}-{self.calls:02d}.source.txt"
            (self.directory / filename).write_text(clean, encoding="utf-8")
            record.update({"status": "captured", "file": filename, "raw_sha256": digest(raw),
                           "sanitized_sha256": digest(clean.encode()), "bytes": len(raw),
                           "oracle": snapshot_oracle(clean)})
            self.cache[url] = clean
            return clean
        except urllib.error.HTTPError as exc:
            record.update({"status": "http_error", "http_status": exc.code})
            self.last_error = "rate_limited" if exc.code == 429 else "source_http_error"
            if exc.code == 429:
                self.stop_reason = "rate_limited_run_stopped_no_retry"
            raise
        except Exception as exc:
            self.last_error = str(exc) if isinstance(exc, AuditLimit) else type(exc).__name__
            record.update({"status": "capture_failed", "error_type": type(exc).__name__})
            raise
        finally:
            record["elapsed_seconds"] = round(time.monotonic() - started, 3)


def compare_oracle(data: object, oracle: dict) -> dict:
    checks = {}
    if oracle.get("num_found") is not None:
        checks["num_found"] = data.num_found == oracle["num_found"]
    if oracle.get("price_stats"):
        checks.update({"price_" + key: numeric(data.price_stats.get(key)) == value for key, value in oracle["price_stats"].items()})
    return {"status": "mismatch" if False in checks.values() else "matched" if "num_found" in checks and "price_median" in checks else "inconclusive", "checks": checks}


def report_snapshot(request, data, adapter, current_year: int) -> dict:
    from car_compare.depreciation import build_report
    from car_compare.models import MSRP

    listings = adapter._listings_from_years(request, [data], current_year)
    actual = build_report(request, listings, MSRP(0, "No baseline captured in used-only diagnostic", "none", ""), current_year=current_year, aggregate_snapshots=adapter._facet_evidence([data]))
    age_zero = next((bucket for bucket in actual["buckets"] if bucket["age"] == 0), {})
    return {
        "kind": "actual_build_report_from_same_captured_slice_not_http_end_to_end",
        "source_evidence": adapter._facet_evidence([data]),
        "actual_report": actual,
        "baseline_policy_check": "violation_used_only_probe_has_baseline" if age_zero.get("median") is not None else "no_baseline_as_expected",
        "median_comparison": "source_exact_median_and_report_histogram_estimate_are_different_statistics",
    }


def live_probe(query: dict, manifest: dict, session: CaptureSession) -> dict:
    from car_compare.parser import parse_vehicle_query
    from car_compare.sources import visor_facets as adapter

    session.begin(query["id"])
    started = time.monotonic()
    request = parse_vehicle_query(query["query"])
    row = {**query, "status": "not_run", "end_to_end": "not_run",
           "requested_scope": {"vehicle": request.to_dict(), "year": 2023, "condition": "used", "geography": "source_default_not_independently_verified"},
           "scope_verification": "adapter_validation_only_not_independent_membership_proof",
           "full_query_coverage": False}
    try:
        with patch.object(adapter, "_fetch_text", session.fetch):
            models = adapter._resolve_source_models(request)
            model = models[0]
            base = session.fetch(adapter._visor_url(request, car_type="used", model_value=model))
            specs = adapter._specs_from_html(request, base, model)
            if request.trim and not specs:
                row["status"] = "unresolved_scope"
                return row
            urls = [(adapter._visor_url(request, 2023, "used", spec["name"], spec["value"], model_value=model), spec["name"], spec["value"]) for spec in (specs or [{"name": "", "value": ""}])]
            row["resolved_partitions"] = len(urls)
            row["unexamined_partitions"] = max(0, len(urls) - 1)
            if not urls:
                row["status"] = "unresolved_scope"
                return row
            url, name, value = urls[0]
            row["probed_partition"] = {"url": safe_url(url), "filter_name": name, "filter_value": value}
            years = {str(item["value"]): item["count"] for item in adapter._parse_facet_items(base, "year")}
            data = adapter._fetch_visor_facets(request, 2023, "used", url, name, value, min(adapter._parse_num_found(base), years.get("2023", 0)))
        if data is None:
            row["status"] = session.last_error or "adapter_rejected_or_empty_unverified"
            return row
        captured = session.cache.get(data.url)
        if captured is None:
            row["status"] = "adapter_result_without_captured_snapshot"
            return row
        row["adapter_result"] = asdict(data) if is_dataclass(data) else vars(data)
        oracle = snapshot_oracle(captured)
        row["same_snapshot_comparison"] = compare_oracle(data, oracle)
        row["status"] = "accepted_slice_diagnostic"
        if row["same_snapshot_comparison"]["status"] != "matched":
            row["status"] = "oracle_" + row["same_snapshot_comparison"]["status"]
        report = report_snapshot(request, data, adapter, manifest["current_year"])
        filename = query["id"] + ".app-report.json"
        write_json(session.directory / filename, report)
        row["app_report_file"] = filename
        row["baseline_policy_check"] = report["baseline_policy_check"]
        if report["baseline_policy_check"].startswith("violation"):
            row["status"] = "report_policy_violation"
        if session.last_error:
            row["resolution_warning"] = session.last_error
    except Exception as exc:
        row["status"] = session.last_error or "adapter_or_report_error"
        row["error_type"] = type(exc).__name__
    finally:
        row["source_calls"] = session.calls
        row["snapshots"] = session.snapshots
        row["elapsed_seconds"] = round(time.monotonic() - started, 3)
    return row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Opt into bounded public Visor requests; never starts full jobs")
    parser.add_argument("--query", action="append", default=[], help="Repeat an exact query or manifest ID (1-20)")
    parser.add_argument("--output", help="New JSON file outside the checkout; default is a temporary directory")
    parser.add_argument("--jobs-dir", type=Path, default=ROOT / "data/collector_jobs")
    parser.add_argument("--max-source-calls", type=int, choices=range(1, 9), default=6, help="Per query, including three-condition discovery and redirects; default 6, maximum 8")
    parser.add_argument("--deadline-seconds", type=float, default=720, help="Shared live diagnostic deadline, capped at 720 seconds")
    args = parser.parse_args(argv)
    if not math.isfinite(args.deadline_seconds) or not 0 < args.deadline_seconds <= 720:
        parser.error("deadline must be greater than zero and at most 720 seconds")
    try:
        manifest = load_manifest()
        queries = select_queries(manifest, args.query)
        path, directory = output_directory(args.output)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    local, errors = inspect_local(queries, args.jobs_dir)
    report = {
        "schema_version": 1, "started_at": utc_now(), "mode": "live_diagnostic" if args.live else "offline_inventory",
        "manifest_sha256": digest(MANIFEST.read_bytes()), "current_year": manifest["current_year"],
        "source_module_sha256": digest((ROOT / "car_compare/sources/visor_facets.py").read_bytes()),
        "limits": {"per_query_source_calls": args.max_source_calls, "total_source_calls_max": len(queries) * args.max_source_calls, "shared_seconds": args.deadline_seconds, "retries": 0},
        "local_results": local, "local_read_errors": errors, "live_results": [],
        "end_to_end": "not_run", "hosted_deployment": "not_checked_or_updated",
        "limitations": ["No full collection jobs, browser marketplace checks, HTTP app calls, or generation research.",
                        "First resolved partition only; used 2023 is not all years/conditions or all aliases.",
                        "Adapter scope validation is not independent proof of model membership or nationwide scope.",
                        "The oracle checks numbers from the identical sanitized capture, not market completeness.",
                        "No historical-versus-live recall calculation. No fabricated source fixtures.",
                        "Sanitized source text is inert; review it before sharing outside the machine."],
    }
    write_json(path, report)
    if args.live:
        session = CaptureSession(directory, args.max_source_calls, args.deadline_seconds)
        for query in queries:
            report["live_results"].append(live_probe(query, manifest, session))
            write_json(path, report)
        report["source_calls"] = session.total_calls
    report["finished_at"] = utc_now()
    report["outcomes"] = dict(Counter(row["status"] for row in report["live_results"] or local))
    report["full_success_claimed"] = False
    write_json(path, report)
    print(json.dumps({"report": str(path), "snapshots": str(directory), "outcomes": report["outcomes"], "end_to_end": "not_run"}, indent=2))
    # Inconclusive live cases must not become a green acceptance gate.
    if args.live and any(row["status"] != "accepted_slice_diagnostic" for row in report["live_results"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
