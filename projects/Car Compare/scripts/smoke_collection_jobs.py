#!/usr/bin/env python3
"""Opt-in full collection jobs in temporary storage; not a benchmark pass."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import json
import sys
import tempfile
import threading
import time
import os
import hashlib
from types import SimpleNamespace
from audit_twenty_queries import sanitize_text, snapshot_oracle, compare_oracle
from unittest.mock import patch
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from car_compare import collector
from car_compare.parser import parse_vehicle_query
from car_compare.sources import visor_facets, request_budget
from car_compare.depreciation import build_report
from car_compare.models import MSRP


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument("--query", action="append", default=[])
    parser.add_argument("--matrix", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--request-spacing", type=float, default=1.5, help="Additional conservative validation pacing, in seconds per host")
    args = parser.parse_args()
    directory = Path(tempfile.mkdtemp(prefix="car-compare-full-smoke-"))
    if args.matrix:
        matrix = json.loads((ROOT / "tests/fixtures/twenty_vehicle_queries.json").read_text())
        args.query.extend(row["query"] for row in matrix["queries"])
        args.query.append("Lexus NX")
    if not args.query:
        parser.error("--query or --matrix required")
    os.environ["CAR_COMPARE_BROWSER_PROFILE"] = str(directory / "browser-profile")
    os.environ["CAR_COMPARE_CDP_URL"] = ""
    config = collector.CollectorConfig(root=ROOT, cache_enabled=False, cache_dir=directory / "cache")
    config.jobs_dir = directory / "jobs"
    manager = collector.CollectionManager(config)
    stopped_hosts = set()
    lock = threading.Lock()
    source_captures = {}
    pacing_lock = threading.Lock()
    next_request = {}
    original_fetch = visor_facets._fetch_text
    evidence_dir = directory / "source-evidence"
    evidence_dir.mkdir()

    def capture_fetch(url, **kwargs):
        text = original_fetch(url, **kwargs)
        clean = sanitize_text(text)
        key = hashlib.sha256((url + clean).encode()).hexdigest()
        (evidence_dir / f"{key}.txt").write_text(clean)
        with lock:
            source_captures.setdefault(url, []).append({"captured_at":time.time(), "path":str(evidence_dir / f"{key}.txt"), "oracle":snapshot_oracle(clean)})
        return text

    @contextmanager
    def guarded_slot(url, deadline=None, **kwargs):
        host = request_budget._host(url)
        with lock:
            stopped = host in stopped_hosts
        if stopped:
            raise RuntimeError("Live smoke stopped this source after a rate limit; no retry")
        with pacing_lock:
            wait = max(0, next_request.get(host, 0) - time.monotonic())
            next_request[host] = time.monotonic() + wait + max(0, args.request_spacing)
        if deadline and time.time() + wait >= deadline:
            raise TimeoutError("Collection deadline reached during validation pacing")
        if wait:
            time.sleep(wait)
        with request_budget.host_slot(url, deadline, **kwargs):
            yield

    def stop_source(url, retry_after=None):
        with lock:
            stopped_hosts.add(request_budget._host(url))
        request_budget.rate_limited(url, retry_after)

    def run(index_query):
        index, query = index_query
        request = parse_vehicle_query(query)
        job = collector.CollectionJob(id=f"smoke-{index}", query=query, status="queued", created_at=time.time(), updated_at=time.time())
        manager._jobs[job.id] = job
        started = time.monotonic()
        try:
            manager._run_job(job.id, request)
            result = manager.get(job.id).result or {}
            analysis = build_report(request, collector.listings_from_result(result), MSRP(0, "Reference unavailable", "reference", ""), aggregate_snapshots=result.get("evidence", []))
            comparisons = []
            for item in result.get("evidence", []):
                captures = source_captures.get(item.get("url"), [])
                if not captures:
                    comparisons.append({"status":"inconclusive", "url":item.get("url")})
                    continue
                capture = min(captures, key=lambda capture:abs(capture["captured_at"] - item.get("scope",{}).get("captured_at",0)))
                comparison = compare_oracle(SimpleNamespace(num_found=item.get("num_found"),price_stats=item.get("price_stats",{})),capture["oracle"])
                comparisons.append({**comparison,"url":item.get("url"),"year":item.get("year"),"condition":item.get("condition"),"capture":capture["path"],"selected_filters":item.get("scope",{}).get("selected_filters")})
            (config.jobs_dir / job.id / "source-comparison.json").write_text(json.dumps(comparisons, indent=2))
            (config.jobs_dir / job.id / "analysis.json").write_text(json.dumps(analysis, indent=2))
            row = {"query": query, "job_id": job.id, "status": manager.get(job.id).status,
                    "elapsed_seconds": round(time.monotonic() - started, 2),
                    "sources": result.get("sources", []), "partitions": result.get("partition_manifest", []),
                    "raw_rows": len(result.get("listings", [])),
                    "readiness": analysis["summary"]["readiness"],
                    "priced_year_count": analysis["summary"]["pricedYearCount"],
                    "baseline_year": analysis["summary"]["baselineModelYear"],
                    "baseline_price": analysis["buckets"][0]["market_median"],
                    "independent_source_comparison": "matched" if comparisons and all(item["status"]=="matched" for item in comparisons) else "requires_review", "benchmark_pass": False}
            print(json.dumps({"finished": query, "status": row["status"], "readiness": row["readiness"], "priced_year_count": row["priced_year_count"]}), flush=True)
            return row
        except Exception as exc:
            return {"query": query, "status": "error", "error": str(exc), "benchmark_pass": False}

    print(json.dumps({"output_directory": str(directory), "queries": args.query}), flush=True)
    with patch.object(visor_facets, "_fetch_text", capture_fetch), patch.object(collector, "host_slot", guarded_slot), patch.object(visor_facets, "host_slot", guarded_slot), patch.object(collector, "rate_limited", stop_source), patch.object(visor_facets, "rate_limited", stop_source):
        with ThreadPoolExecutor(max_workers=max(1,min(args.workers,3,len(args.query)))) as pool:
            rows = list(pool.map(run, enumerate(args.query, 1)))
    report = {"jobs": rows, "rate_limited_hosts_stopped": sorted(stopped_hosts), "full_benchmark_pass": False}
    (directory / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
