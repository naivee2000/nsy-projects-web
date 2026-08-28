from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from time import perf_counter
import threading
from typing import Any, Callable
import uuid

from .collector import VaultCollector
from .engine import BacktestEngine
from .models import StrategyDefinition
from .providers import DataProvider
from .storage import AppStore
from .unified import run_unified_backtest


class JobManager:
    def __init__(self, store: AppStore, collector: VaultCollector, provider_factory: Callable[[str, str], DataProvider]):
        self.store = store
        self.collector = collector
        self.provider_factory = provider_factory
        self.engine = BacktestEngine()
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="strategy-job")
        self._lock = threading.RLock()
        self._jobs: dict[str, dict[str, Any]] = {}
        self.store.fail_incomplete_jobs()

    def start_backtest(self, strategy: StrategyDefinition, provider_name: str, mode: str, scenario: str = "wave") -> dict[str, Any]:
        job_id = uuid.uuid4().hex
        job = {
            "id": job_id,
            "kind": "backtest",
            "status": "queued",
            "stage": "Waiting to start",
            "createdAt": self._now(),
            "provider": provider_name,
            "mode": mode,
        }
        with self._lock:
            self._jobs[job_id] = job
        self.store.save_job(job)
        self._executor.submit(self._run_backtest, job_id, strategy, provider_name, mode, scenario)
        return dict(job)

    def start_sync(self) -> dict[str, Any]:
        job_id = uuid.uuid4().hex
        job = {
            "id": job_id,
            "kind": "vault-sync",
            "status": "queued",
            "stage": "Waiting to sync",
            "createdAt": self._now(),
        }
        with self._lock:
            self._jobs[job_id] = job
        self.store.save_job(job)
        self._executor.submit(self._run_sync, job_id)
        return dict(job)

    def start_portfolio_backtest(
        self,
        request: dict[str, Any],
        provider: Any,
    ) -> dict[str, Any]:
        job_id = uuid.uuid4().hex
        option_count = sum(item.kind != "stock" and item.weight > 0 for item in request["holdings"])
        job = {
            "id": job_id,
            "kind": "portfolio-backtest",
            "status": "queued",
            "stage": "Waiting to load historical prices",
            "createdAt": self._now(),
            "provider": provider.name,
            "mode": "options" if option_count else "shares",
        }
        with self._lock:
            self._jobs[job_id] = job
        self.store.save_job(job)
        self._executor.submit(self._run_portfolio_backtest, job_id, request, provider, option_count)
        return dict(job)

    def start_backfill(self, symbol: str, start: str, end: str, profile: str) -> dict[str, Any]:
        job_id = uuid.uuid4().hex
        job = {
            "id": job_id,
            "kind": "historical-backfill",
            "status": "queued",
            "stage": f"Waiting to download {symbol} history",
            "createdAt": self._now(),
            "provider": "marketdata",
            "mode": profile,
        }
        with self._lock:
            self._jobs[job_id] = job
        self.store.save_job(job)
        self._executor.submit(self._run_backfill, job_id, symbol, start, end, profile)
        return dict(job)

    def start_leaps_protection_backfill(self, start: str, end: str, call_dte: int, put_dte: int, strike_limit: int) -> dict[str, Any]:
        job_id = uuid.uuid4().hex
        job = {
            "id": job_id,
            "kind": "leaps-protection-backfill",
            "status": "queued",
            "stage": "Waiting to download optimized SPY + QQQ history",
            "createdAt": self._now(),
            "provider": "marketdata",
            "mode": f"{call_dte}-day calls / {put_dte}-day puts",
        }
        with self._lock:
            self._jobs[job_id] = job
        self.store.save_job(job)
        self._executor.submit(self._run_leaps_protection_backfill, job_id, start, end, call_dte, put_dte, strike_limit)
        return dict(job)

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            payload = dict(job) if job else self.store.get_job(job_id)
        if payload and "result" not in payload and payload.get("status") == "complete" and payload.get("kind") in {
            "backtest",
            "portfolio-backtest",
        }:
            result = self.store.get_run(job_id)
            if result:
                payload["result"] = result
        return payload

    def list_recent(self, kind: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        return self.store.list_jobs(kind=kind, limit=limit)

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)

    def _run_backtest(self, job_id: str, strategy: StrategyDefinition, provider_name: str, mode: str, scenario: str) -> None:
        stage = "Pulling required market data and running the test" if provider_name == "marketdata" else "Running the learning scenario"
        self._update(job_id, status="running", stage=stage, startedAt=self._now())
        try:
            provider = self.provider_factory(provider_name, scenario)
            result = self.engine.run(strategy, provider, include_sweep=mode == "sweep")
            result.run_id = job_id
            payload = result.to_dict()
            self.store.save_run(job_id, strategy.name, strategy.ticker.upper(), "complete", payload)
            self._update(
                job_id,
                status="complete",
                stage="Complete",
                finishedAt=self._now(),
                result=payload,
            )
        except Exception as exc:
            self._update(job_id, status="failed", stage="Could not complete", finishedAt=self._now(), error=str(exc))

    def _run_sync(self, job_id: str) -> None:
        self._update(job_id, status="running", stage="Downloading missing favorite history", startedAt=self._now())
        try:
            result = self.collector.sync()
            status = "complete" if result.get("status") in {"complete", "partial"} else "failed"
            self._update(
                job_id,
                status=status,
                stage="Complete" if status == "complete" else "Could not complete",
                finishedAt=self._now(),
                result=result,
                error=result.get("message") if status == "failed" else "",
            )
        except Exception as exc:
            self._update(job_id, status="failed", stage="Could not complete", finishedAt=self._now(), error=str(exc))

    def _run_portfolio_backtest(
        self,
        job_id: str,
        request: dict[str, Any],
        provider: Any,
        option_count: int,
    ) -> None:
        stage = (
            f"Loading real share history and pricing {option_count} option allocation"
            f"{'s' if option_count != 1 else ''}; the sensitivity checks reuse this run's data"
            if option_count
            else "Loading real adjusted share history and checking date coverage"
        )
        self._update(job_id, status="running", stage=stage, startedAt=self._now())
        started = perf_counter()
        try:
            external_runner = getattr(provider, "run_portfolio_backtest", None)
            result = external_runner(**request) if callable(external_runner) else run_unified_backtest(provider, **request)
            result["runtimeSeconds"] = round(perf_counter() - started, 2)
            symbols = list(dict.fromkeys(item.symbol.upper() for item in request["holdings"]))
            ticker = ", ".join(symbols[:3]) + ("…" if len(symbols) > 3 else "")
            self.store.save_run(job_id, "Portfolio comparison", ticker, "complete", result)
            self._update(
                job_id,
                status="complete",
                stage=f"Complete in {result['runtimeSeconds']:.1f} seconds",
                finishedAt=self._now(),
                result=result,
            )
        except Exception as exc:
            self._update(job_id, status="failed", stage="Could not complete", finishedAt=self._now(), error=str(exc))

    def _run_backfill(self, job_id: str, symbol: str, start: str, end: str, profile: str) -> None:
        self._update(job_id, status="running", stage=f"Preparing {symbol} historical download", startedAt=self._now())
        try:
            def report(completed: int, total: int, market_date: str) -> None:
                self._update(
                    job_id,
                    stage=f"Downloading {symbol}: {completed:,} of {total:,} option dates saved — checking {market_date}",
                )

            result = self.collector.backfill(symbol, start, end, profile, progress=report)
            status = "complete" if result.get("status") in {"complete", "partial"} else "failed"
            remaining = int(result.get("remainingSessions") or 0)
            final_stage = "Historical download complete" if remaining == 0 and status == "complete" else "Historical download paused"
            self._update(
                job_id,
                status=status,
                stage=final_stage if status == "complete" else "Could not complete",
                finishedAt=self._now(),
                result=result,
                error=result.get("message") if status == "failed" else "",
            )
        except Exception as exc:
            self._update(job_id, status="failed", stage="Could not complete", finishedAt=self._now(), error=str(exc))

    def _run_leaps_protection_backfill(
        self, job_id: str, start: str, end: str, call_dte: int, put_dte: int, strike_limit: int
    ) -> None:
        self._update(job_id, status="running", stage="Preparing SPY + QQQ historical download", startedAt=self._now())
        try:
            def report(completed: int, total: int, label: str) -> None:
                self._update(job_id, stage=f"Downloading SPY + QQQ: {completed:,} of {total:,} dates saved — {label}")

            result = self.collector.backfill_leaps_protection(
                start, end, call_dte, put_dte, strike_limit, progress=report
            )
            status = "complete" if result.get("status") in {"complete", "partial"} else "failed"
            remaining = int(result.get("remainingSymbolDays") or 0)
            final_stage = "SPY + QQQ download complete" if remaining == 0 else "SPY + QQQ download paused"
            self._update(
                job_id,
                status=status,
                stage=final_stage if status == "complete" else "Could not complete",
                finishedAt=self._now(),
                result=result,
                error=result.get("message") if status == "failed" else "",
            )
        except Exception as exc:
            self._update(job_id, status="failed", stage="Could not complete", finishedAt=self._now(), error=str(exc))

    def _update(self, job_id: str, **changes: Any) -> None:
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(changes)
                job = dict(self._jobs[job_id])
            else:
                return
        self.store.save_job(job)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
