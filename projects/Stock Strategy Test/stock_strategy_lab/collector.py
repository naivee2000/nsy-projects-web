from __future__ import annotations

from datetime import date, datetime, time, timedelta
import hashlib
import os
import threading
from typing import Any, Callable
from zoneinfo import ZoneInfo

from .calendar import is_us_trading_day, trading_dates
from .providers import CreditLimitError, MarketDataProvider, ProviderError, is_monthly_expiration
from .storage import CAPTURE_PROFILE_CREDITS, AppStore, MarketVault


EASTERN = ZoneInfo("America/New_York")
CAPTURE_PROFILE_BYTES = {"used": 180_000, "balanced": 520_000, "full": 1_800_000}
OPTIMIZED_SYMBOLS = ("SPY", "QQQ")
OPTIMIZED_MAX_CREDITS = 9_500
OPTIMIZED_SERIES_RESERVE = 1_000
OPTIMIZED_DOWNLOAD_CAP = OPTIMIZED_MAX_CREDITS - OPTIMIZED_SERIES_RESERVE
OPTIMIZED_BYTES_PER_SYMBOL_DAY = 250_000


class VaultCollector:
    def __init__(self, provider: MarketDataProvider, vault: MarketVault, store: AppStore):
        self.provider = provider
        self.vault = vault
        self.store = store
        self.reserve_credits = max(0, int(os.environ.get("STOCK_STRATEGY_CREDIT_RESERVE", "30")))
        self.max_backfill_sessions = max(0, int(os.environ.get("STOCK_STRATEGY_MAX_BACKFILL_SESSIONS", "8")))
        self._lock = threading.Lock()
        self._last_result: dict[str, Any] = {"status": "idle", "message": "No collection has run yet."}

    @property
    def last_result(self) -> dict[str, Any]:
        return dict(self._last_result)

    def sync(self) -> dict[str, Any]:
        if not self._lock.acquire(blocking=False):
            return {"status": "running", "message": "A history sync is already running."}
        started = datetime.now(EASTERN)
        result: dict[str, Any] = {
            "status": "running",
            "startedAt": started.isoformat(),
            "symbols": [],
            "sessionsCompleted": 0,
            "contractsStored": 0,
            "errors": [],
        }
        self._last_result = dict(result)
        try:
            if not self.provider.available:
                raise ProviderError("Add MARKETDATA_API_TOKEN to collect real historical data.")
            favorites = [item for item in self.store.list_favorites() if item["active"]]
            if not favorites:
                result.update({"status": "complete", "message": "Add a favorite stock or ETF before syncing."})
                return result

            market_calendar: dict[str, list[str]] = {}
            today = started.date()
            history_window = getattr(self.provider, "history_window_start", None)
            provider_start = history_window(today) if history_window else today - timedelta(days=365)
            start = (provider_start or (today - timedelta(days=365 * 20))).isoformat()
            end = today.isoformat()
            for favorite in favorites:
                symbol = favorite["symbol"]
                try:
                    bars = self.provider.stock_bars(symbol, start, end)
                    dates = [bar.market_date for bar in bars if date.fromisoformat(bar.market_date) < today]
                    if not dates:
                        raise ProviderError("No completed stock sessions were returned")
                    market_calendar[symbol] = dates
                    result["symbols"].append(symbol)
                except ProviderError as exc:
                    result["errors"].append(f"{symbol}: {exc}")

            # The newest missing session is captured first for immediate usability.
            for favorite in favorites:
                symbol = favorite["symbol"]
                dates = market_calendar.get(symbol) or []
                if not dates:
                    continue
                completed = self.store.collection_dates(symbol, favorite["captureProfile"])
                newest = dates[-1]
                if newest not in completed and self._has_collection_budget():
                    self._capture_session(symbol, newest, favorite["captureProfile"], result)

            # Backfill oldest accessible sessions first so the rolling one-year edge is preserved.
            sessions_attempted = 0
            progress = True
            while progress and sessions_attempted < self.max_backfill_sessions and self._has_collection_budget():
                progress = False
                for favorite in favorites:
                    if sessions_attempted >= self.max_backfill_sessions or not self._has_collection_budget():
                        break
                    symbol = favorite["symbol"]
                    profile = favorite["captureProfile"]
                    completed = self.store.collection_dates(symbol, profile)
                    missing = [item for item in market_calendar.get(symbol, []) if item not in completed]
                    if not missing:
                        continue
                    self._capture_session(symbol, missing[0], profile, result)
                    sessions_attempted += 1
                    progress = True

            result["status"] = "complete" if not result["errors"] else "partial"
            result["finishedAt"] = datetime.now(EASTERN).isoformat()
            result["quota"] = self.store.quota_status()
            result["message"] = (
                f"Stored {result['contractsStored']:,} option records across "
                f"{result['sessionsCompleted']} symbol-days."
            )
            return result
        except (ProviderError, CreditLimitError) as exc:
            result.update({"status": "failed", "message": str(exc), "finishedAt": datetime.now(EASTERN).isoformat()})
            return result
        finally:
            self._last_result = dict(result)
            self._lock.release()

    def estimate_backfill(self, symbol: str, start: str, end: str, profile: str) -> dict[str, Any]:
        if profile not in CAPTURE_PROFILE_BYTES:
            raise ValueError("Capture profile must be balanced, full, or used")
        sessions = [item.isoformat() for item in trading_dates(date.fromisoformat(start), date.fromisoformat(end))]
        complete = self.store.collection_dates(symbol, profile)
        missing = [item for item in sessions if item not in complete]
        coverage = self.vault.coverage(self.provider.name, symbol)
        stock_covered = bool(
            coverage.get("stockStart")
            and coverage.get("stockEnd")
            and str(coverage["stockStart"]) <= start
            and str(coverage["stockEnd"]) >= end
        )
        stock_credits = 0 if stock_covered else 2
        estimated_credits = stock_credits + len(missing) * CAPTURE_PROFILE_CREDITS[profile]
        quota = self.store.quota_status()
        daily_capacity = max(1, int(quota.get("limit") or 100) - self.reserve_credits)
        estimated_days = max(1, (estimated_credits + daily_capacity - 1) // daily_capacity) if estimated_credits else 0
        return {
            "symbol": symbol.upper(),
            "startDate": start,
            "endDate": end,
            "captureProfile": profile,
            "tradingSessions": len(sessions),
            "alreadyStoredSessions": len(sessions) - len(missing),
            "remainingSessions": len(missing),
            "estimatedCredits": estimated_credits,
            "estimatedStorageBytes": len(missing) * CAPTURE_PROFILE_BYTES[profile],
            "estimatedProviderDays": estimated_days,
            "stockHistoryAlreadyCovered": stock_covered,
            "quota": quota,
        }

    def backfill(
        self,
        symbol: str,
        start: str,
        end: str,
        profile: str,
        progress: Callable[[int, int, str], None] | None = None,
    ) -> dict[str, Any]:
        if not self._lock.acquire(blocking=False):
            return {"status": "failed", "message": "Another History Vault download is already running."}
        result: dict[str, Any] = {
            "status": "running",
            "symbol": symbol.upper(),
            "startDate": start,
            "endDate": end,
            "captureProfile": profile,
            "sessionsCompleted": 0,
            "contractsStored": 0,
            "errors": [],
            "startedAt": datetime.now(EASTERN).isoformat(),
        }
        self._last_result = dict(result)
        try:
            if not self.provider.available:
                raise ProviderError("Connect a Market Data token before downloading historical data.")
            bars = self.provider.stock_bars(symbol, start, end)
            available_dates = {
                bar.market_date
                for bar in bars
                if start <= bar.market_date <= end and date.fromisoformat(bar.market_date) < datetime.now(EASTERN).date()
            }
            completed = self.store.collection_dates(symbol, profile)
            missing = sorted(available_dates - completed)
            total = len(missing)
            for index, market_date in enumerate(missing, start=1):
                if not self._has_collection_budget():
                    break
                if progress:
                    progress(index - 1, total, market_date)
                error_count = len(result["errors"])
                self._capture_session(symbol, market_date, profile, result)
                if progress:
                    progress(index, total, market_date)
                if len(result["errors"]) > error_count and "429" in result["errors"][-1]:
                    break

            remaining = len(available_dates - self.store.collection_dates(symbol, profile))
            result["remainingSessions"] = remaining
            result["finishedAt"] = datetime.now(EASTERN).isoformat()
            result["quota"] = self.store.quota_status()
            if remaining == 0 and not result["errors"]:
                result["status"] = "complete"
                result["message"] = (
                    f"Historical download complete for {symbol.upper()}: "
                    f"{len(available_dates):,} trading sessions are covered locally."
                )
            else:
                result["status"] = "partial"
                reason = "The reserved-credit boundary was reached." if not self._has_collection_budget() else "Some provider requests were incomplete."
                result["message"] = (
                    f"Paused with {remaining:,} trading sessions still missing. {reason} "
                    "Click Resume historical download to continue without duplicating saved records."
                )
            return result
        except (ProviderError, CreditLimitError, ValueError) as exc:
            result.update({"status": "failed", "message": str(exc), "finishedAt": datetime.now(EASTERN).isoformat()})
            return result
        finally:
            self._last_result = dict(result)
            self._lock.release()

    @staticmethod
    def optimized_profile(call_dte: int, put_dte: int, strike_limit: int) -> str:
        return f"leaps-protection-c{call_dte}-p{put_dte}-s{strike_limit}"

    def estimate_leaps_protection(
        self,
        start: str,
        end: str,
        call_dte: int = 540,
        put_dte: int = 45,
        strike_limit: int = 40,
    ) -> dict[str, Any]:
        profile = self.optimized_profile(call_dte, put_dte, strike_limit)
        sessions = [item.isoformat() for item in trading_dates(date.fromisoformat(start), date.fromisoformat(end))]
        remaining_by_symbol: dict[str, int] = {}
        stock_credits = 0
        for symbol in OPTIMIZED_SYMBOLS:
            completed = self.store.collection_dates(symbol, profile)
            remaining_by_symbol[symbol] = len([item for item in sessions if item not in completed])
            coverage = self.vault.coverage(self.provider.name, symbol)
            covered = bool(
                coverage.get("stockStart")
                and coverage.get("stockEnd")
                and str(coverage["stockStart"]) <= start
                and str(coverage["stockEnd"]) >= end
            )
            stock_credits += 0 if covered else 2
        remaining_symbol_days = sum(remaining_by_symbol.values())
        chain_credits = remaining_symbol_days * 2
        estimated_download_credits = stock_credits + chain_credits
        projected_total = estimated_download_credits + OPTIMIZED_SERIES_RESERVE
        fits = projected_total <= OPTIMIZED_MAX_CREDITS
        verified = self.provider.history_years is None or int(self.provider.history_years) >= 5
        return {
            "symbols": list(OPTIMIZED_SYMBOLS),
            "startDate": start,
            "endDate": end,
            "callTargetDte": call_dte,
            "putTargetDte": put_dte,
            "strikeLimit": strike_limit,
            "tradingSessionsPerSymbol": len(sessions),
            "totalSymbolDays": len(sessions) * len(OPTIMIZED_SYMBOLS),
            "remainingBySymbol": remaining_by_symbol,
            "remainingSymbolDays": remaining_symbol_days,
            "alreadyStoredSymbolDays": len(sessions) * len(OPTIMIZED_SYMBOLS) - remaining_symbol_days,
            "estimatedChainCredits": chain_credits,
            "estimatedStockCredits": stock_credits,
            "estimatedDownloadCredits": estimated_download_credits,
            "reservedSeriesCredits": OPTIMIZED_SERIES_RESERVE,
            "projectedCreditBudget": projected_total,
            "maximumCredits": OPTIMIZED_MAX_CREDITS,
            "downloadCreditCap": OPTIMIZED_DOWNLOAD_CAP,
            "estimatedStorageBytes": remaining_symbol_days * OPTIMIZED_BYTES_PER_SYMBOL_DAY,
            "fitsWithinCreditCap": fits,
            "fiveYearAccessVerified": verified,
            "canStart": self.provider.available and verified and fits,
            "profile": profile,
            "quota": self.store.quota_status(),
        }

    def backfill_leaps_protection(
        self,
        start: str,
        end: str,
        call_dte: int = 540,
        put_dte: int = 45,
        strike_limit: int = 40,
        max_credits: int = OPTIMIZED_DOWNLOAD_CAP,
        progress: Callable[[int, int, str], None] | None = None,
    ) -> dict[str, Any]:
        if not self._lock.acquire(blocking=False):
            return {"status": "failed", "message": "Another History Vault download is already running."}
        profile = self.optimized_profile(call_dte, put_dte, strike_limit)
        result: dict[str, Any] = {
            "status": "running",
            "symbols": list(OPTIMIZED_SYMBOLS),
            "startDate": start,
            "endDate": end,
            "callTargetDte": call_dte,
            "putTargetDte": put_dte,
            "strikeLimit": strike_limit,
            "symbolDaysCompleted": 0,
            "contractsStored": 0,
            "creditsUsed": 0,
            "errors": [],
            "startedAt": datetime.now(EASTERN).isoformat(),
        }
        self._last_result = dict(result)
        try:
            if not self.provider.available:
                raise ProviderError("Connect a Market Data token before downloading historical data.")
            if self.provider.history_years is not None and self.provider.history_years < 5:
                raise ProviderError("Five-year access has not been verified for this Market Data token.")
            estimate = self.estimate_leaps_protection(start, end, call_dte, put_dte, strike_limit)
            if not estimate["fitsWithinCreditCap"]:
                raise ProviderError(
                    f"The projected {estimate['projectedCreditBudget']:,}-credit workload exceeds the {OPTIMIZED_MAX_CREDITS:,}-credit safety cap."
                )

            quota_before = self.store.quota_status().get("remaining")
            available_dates: dict[str, list[str]] = {}
            for symbol in OPTIMIZED_SYMBOLS:
                bars = self.provider.stock_bars(symbol, start, end)
                available_dates[symbol] = sorted(
                    bar.market_date
                    for bar in bars
                    if start <= bar.market_date <= end and date.fromisoformat(bar.market_date) < datetime.now(EASTERN).date()
                )
            quota_after_stocks = self.store.quota_status().get("remaining")
            if quota_before is not None and quota_after_stocks is not None:
                result["creditsUsed"] = max(0, int(quota_before) - int(quota_after_stocks))
            completed_by_symbol = {symbol: self.store.collection_dates(symbol, profile) for symbol in OPTIMIZED_SYMBOLS}
            tasks = [
                (symbol, market_date)
                for market_date in sorted({item for values in available_dates.values() for item in values})
                for symbol in OPTIMIZED_SYMBOLS
                if market_date in available_dates[symbol]
                and market_date not in completed_by_symbol[symbol]
            ]
            total = len(tasks)
            for index, (symbol, market_date) in enumerate(tasks, start=1):
                quota = self.store.quota_status()
                remaining = quota.get("remaining")
                if result["creditsUsed"] + 2 > max_credits or (remaining is not None and int(remaining) <= self.reserve_credits):
                    break
                if progress:
                    progress(index - 1, total, f"{symbol} {market_date}")
                before = remaining
                fingerprints: list[str] = []
                contract_count = 0
                try:
                    for side, target in (("call", call_dte), ("put", put_dte)):
                        quotes = self.provider.capture_target_chain(symbol, market_date, side, target, strike_limit)
                        contract_count += len(quotes)
                        fingerprints.extend(
                            f"{item.option_symbol}|{item.market_date}|{item.bid:.8f}|{item.ask:.8f}" for item in quotes
                        )
                    after = self.store.quota_status().get("remaining")
                    credits = max(0, int(before) - int(after)) if before is not None and after is not None else 2
                    result["creditsUsed"] += credits
                    checksum = hashlib.sha256("\n".join(sorted(fingerprints)).encode()).hexdigest()
                    self.store.mark_collection(symbol, market_date, profile, "complete", contract_count, credits, checksum=checksum)
                    result["symbolDaysCompleted"] += 1
                    result["contractsStored"] += contract_count
                except (ProviderError, CreditLimitError) as exc:
                    after = self.store.quota_status().get("remaining")
                    credits = max(0, int(before) - int(after)) if before is not None and after is not None else 0
                    result["creditsUsed"] += credits
                    self.store.mark_collection(symbol, market_date, profile, "partial", contract_count, credits, str(exc))
                    result["errors"].append(f"{symbol} {market_date}: {exc}")
                    if isinstance(exc, CreditLimitError):
                        break
                if progress:
                    progress(index, total, f"{symbol} {market_date}")

            remaining_symbol_days = sum(
                len(set(available_dates[symbol]) - self.store.collection_dates(symbol, profile)) for symbol in OPTIMIZED_SYMBOLS
            )
            if quota_before is not None:
                quota_after = self.store.quota_status().get("remaining")
                if quota_after is not None:
                    result["creditsUsed"] = max(result["creditsUsed"], int(quota_before) - int(quota_after))
            result.update(
                {
                    "remainingSymbolDays": remaining_symbol_days,
                    "finishedAt": datetime.now(EASTERN).isoformat(),
                    "quota": self.store.quota_status(),
                    "status": "complete" if remaining_symbol_days == 0 and not result["errors"] else "partial",
                }
            )
            if result["status"] == "complete":
                result["message"] = "SPY + QQQ five-year LEAPS and protective-put history is saved locally."
            else:
                result["message"] = (
                    f"Paused with {remaining_symbol_days:,} SPY/QQQ date(s) still missing. "
                    "Resume the same download later; completed dates will not use credits again."
                )
            return result
        except (ProviderError, CreditLimitError, ValueError) as exc:
            result.update({"status": "failed", "message": str(exc), "finishedAt": datetime.now(EASTERN).isoformat()})
            return result
        finally:
            self._last_result = dict(result)
            self._lock.release()

    def _capture_session(self, symbol: str, market_date: str, profile: str, result: dict[str, Any]) -> None:
        before = self.store.quota_status().get("remaining")
        contract_count = 0
        fingerprints: list[str] = []
        try:
            expirations = self.provider.option_expirations(symbol, market_date)
            chosen = self._choose_expirations(expirations, market_date, profile)
            if not chosen:
                raise ProviderError("No eligible option expirations were available")
            for expiration in chosen:
                if not self._has_collection_budget():
                    raise CreditLimitError("The collector reached the reserved interactive-credit boundary")
                quotes = self.provider.capture_expiration(symbol, market_date, expiration)
                contract_count += len(quotes)
                fingerprints.extend(
                    f"{item.option_symbol}|{item.market_date}|{item.bid:.8f}|{item.ask:.8f}"
                    for item in quotes
                )
            after = self.store.quota_status().get("remaining")
            credits = max(0, int(before) - int(after)) if before is not None and after is not None else len(chosen) + 1
            checksum = hashlib.sha256("\n".join(sorted(fingerprints)).encode()).hexdigest()
            self.store.mark_collection(symbol, market_date, profile, "complete", contract_count, credits, checksum=checksum)
            result["sessionsCompleted"] += 1
            result["contractsStored"] += contract_count
        except (ProviderError, CreditLimitError) as exc:
            after = self.store.quota_status().get("remaining")
            credits = max(0, int(before) - int(after)) if before is not None and after is not None else 0
            self.store.mark_collection(symbol, market_date, profile, "partial", contract_count, credits, str(exc))
            result["errors"].append(f"{symbol} {market_date}: {exc}")

    @staticmethod
    def _choose_expirations(expirations: list[str], market_date: str, profile: str) -> list[str]:
        current = date.fromisoformat(market_date)
        valid = []
        for value in sorted(set(expirations)):
            try:
                dte = (date.fromisoformat(value) - current).days
            except ValueError:
                continue
            if dte < 0:
                continue
            if profile == "full" and dte <= 365:
                valid.append(value)
            elif profile == "balanced" and dte <= 180 and is_monthly_expiration(value):
                valid.append(value)
            elif profile == "used" and dte <= 90 and is_monthly_expiration(value):
                valid.append(value)
        if profile == "used" and valid:
            return [min(valid, key=lambda value: abs((date.fromisoformat(value) - current).days - 45))]
        return valid

    def _has_collection_budget(self) -> bool:
        quota = self.store.quota_status()
        remaining = quota.get("remaining")
        return remaining is None or int(remaining) > self.reserve_credits


class DailyCollectorScheduler:
    """Small in-process T+1 scheduler; PM2 keeps the owning process alive."""

    def __init__(self, collector: VaultCollector):
        self.collector = collector
        self.enabled = os.environ.get("STOCK_STRATEGY_SCHEDULER_ENABLED", "1").lower() not in {"0", "false", "no"}
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_run_date: date | None = None

    def start(self) -> None:
        if not self.enabled or self._thread:
            return
        self._thread = threading.Thread(target=self._loop, name="strategy-vault-scheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _loop(self) -> None:
        while not self._stop.wait(30):
            now = datetime.now(EASTERN)
            if not is_us_trading_day(now.date()) or now.time() < time(10, 0):
                continue
            if self._last_run_date == now.date():
                continue
            self._last_run_date = now.date()
            self.collector.sync()
