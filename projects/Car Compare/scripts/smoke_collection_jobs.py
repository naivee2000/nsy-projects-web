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
from unittest.mock import patch
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from car_compare import collector
from car_compare.parser import parse_vehicle_query
from car_compare.sources import visor_facets, request_budget


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument("--query", action="append", required=True)
    args = parser.parse_args()
    directory = Path(tempfile.mkdtemp(prefix="car-compare-full-smoke-"))
    config = collector.CollectorConfig(root=ROOT, cache_enabled=False, cache_dir=directory / "cache")
    config.jobs_dir = directory / "jobs"
    manager = collector.CollectionManager(config)
    stopped_hosts = set()
    lock = threading.Lock()

    @contextmanager
    def guarded_slot(url, deadline=None, **kwargs):
        host = request_budget._host(url)
        with lock:
            stopped = host in stopped_hosts
        if stopped:
            raise RuntimeError("Live smoke stopped this source after a rate limit; no retry")
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
            return {"query": query, "job_id": job.id, "status": manager.get(job.id).status,
                    "elapsed_seconds": round(time.monotonic() - started, 2),
                    "sources": result.get("sources", []), "partitions": result.get("partition_manifest", []),
                    "raw_rows": len(result.get("listings", [])),
                    "independent_source_comparison": "not_completed", "benchmark_pass": False}
        except Exception as exc:
            return {"query": query, "status": "error", "error": str(exc), "benchmark_pass": False}

    print(json.dumps({"output_directory": str(directory), "queries": args.query}), flush=True)
    with patch.object(collector, "host_slot", guarded_slot), patch.object(visor_facets, "host_slot", guarded_slot), patch.object(collector, "rate_limited", stop_source), patch.object(visor_facets, "rate_limited", stop_source):
        with ThreadPoolExecutor(max_workers=min(3, len(args.query))) as pool:
            rows = list(pool.map(run, enumerate(args.query, 1)))
    report = {"jobs": rows, "rate_limited_hosts_stopped": sorted(stopped_hosts), "full_benchmark_pass": False}
    (directory / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
