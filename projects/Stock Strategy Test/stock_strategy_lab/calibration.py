from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from bisect import bisect_right
import hashlib
import math
import statistics
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from .calendar import trading_dates
from .models import OptionQuote, OptionRule
from .reference_data import interpolate_term
from .storage import AppStore, MarketVault


EASTERN = ZoneInfo("America/New_York")
SUPPORTED_SYMBOLS = ("SPY", "QQQ")
SUPPORTED_MONEYNESS = (0.50, 0.75, 1.00, 1.25, 1.50)
CALL_DTES = (365, 540, 730)
PUT_DTES = (30, 45, 60)
CALIBRATION_PROFILE = "option-accuracy-v1"
VALIDATION_SETTING = "option_pricing_validation_v1"
DAILY_BUDGET_SETTING = "option_pricing_calibration_daily_budget_v1"
RESERVE_CREDITS = 30
MAX_DAILY_CALIBRATION_CREDITS = 70


@dataclass(frozen=True)
class SurfaceEstimate:
    volatility: float
    half_spread_pct: float
    source: str
    sample_count: int
    dividend_yield: float | None = None


@dataclass(frozen=True)
class SSVIParameters:
    theta: float
    rho: float
    phi: float
    samples: int

    def volatility(self, log_forward_moneyness: float, years: float) -> float:
        x = self.phi * log_forward_moneyness
        variance = 0.5 * self.theta * (
            1 + self.rho * x + math.sqrt((x + self.rho) ** 2 + 1 - self.rho**2)
        )
        return math.sqrt(max(variance, 1e-8) / max(years, 1 / 365.25))


class AccuracyCalibration:
    """Local SPY/QQQ quote calibration and evidence gate.

    Exact provider rows remain in the licensed local vault. The pricing model
    receives only fitted parameters and residual summaries; it never exposes a
    bulk raw-chain API.
    """

    def __init__(
        self,
        vault: MarketVault,
        store: AppStore,
        exact_provider: Any,
        reference: Any,
        reserve_credits: int = RESERVE_CREDITS,
    ):
        self.vault = vault
        self.store = store
        self.exact_provider = exact_provider
        self.reference = reference
        self.reserve_credits = reserve_credits
        self._quotes: list[OptionQuote] = []
        self._by_symbol_date: dict[str, dict[str, list[OptionQuote]]] = {}
        self._dates: dict[str, list[str]] = {}
        self._surface_cache: dict[tuple[str, str, str, str, str], tuple[SSVIParameters | None, float | None, float]] = {}
        self._prepared_end = ""

    def invalidate(self) -> None:
        """Remove all in-process views derived from licensed quote rows."""
        self._quotes = []
        self._by_symbol_date = {}
        self._dates = {}
        self._surface_cache.clear()
        self._prepared_end = ""

    def prepare(self, start: str, end: str) -> None:
        if self._prepared_end >= end:
            return
        quotes = self.vault.calibration_quotes(SUPPORTED_SYMBOLS, end=end)
        by_symbol_date: dict[str, dict[str, list[OptionQuote]]] = {
            symbol: defaultdict(list) for symbol in SUPPORTED_SYMBOLS
        }
        for quote in quotes:
            if quote.underlying in by_symbol_date and not quote.is_nonstandard:
                by_symbol_date[quote.underlying][quote.market_date].append(quote)
        self._quotes = quotes
        self._by_symbol_date = {symbol: dict(values) for symbol, values in by_symbol_date.items()}
        self._dates = {symbol: sorted(values) for symbol, values in self._by_symbol_date.items()}
        self._surface_cache.clear()
        self._prepared_end = end

    def exact_chain(self, symbol: str, market_date: str, rule: OptionRule, download: bool = True) -> list[OptionQuote]:
        symbol = symbol.upper()
        if symbol not in SUPPORTED_SYMBOLS:
            return []
        cached = self._eligible_exact_chain(
            self.vault.option_chain("marketdata", symbol, market_date, side=rule.side), market_date, rule
        )
        if cached:
            return cached
        if not download or not self._can_download(market_date):
            return []
        try:
            quotes = self.exact_provider.capture_accuracy_chain(symbol, market_date, rule.side, rule.target_dte)
        except Exception:
            return []
        self._prepared_end = ""
        return self._eligible_exact_chain(quotes, market_date, rule)

    def exact_series(self, option_symbol: str, start: str, end: str, download: bool = True) -> list[OptionQuote]:
        cached = self.vault.option_series("marketdata", option_symbol, start, end)
        if self._series_has_endpoints(cached, start, end):
            return cached
        if not download or not self._has_budget():
            return cached
        try:
            fetched = self.exact_provider.option_quote_series(option_symbol, start, end)
        except Exception:
            return cached
        self._prepared_end = ""
        return fetched or cached

    def estimate(
        self,
        symbol: str,
        market_date: str,
        side: str,
        strike: float,
        dte: int,
        stock_price: float,
        base_volatility: float,
        exclude_symbol: str = "",
    ) -> SurfaceEstimate:
        symbol = symbol.upper()
        if symbol not in SUPPORTED_SYMBOLS or stock_price <= 0:
            return SurfaceEstimate(base_volatility, self._fallback_half_spread(side, dte, strike / max(stock_price, 0.01)), "uncalibrated", 0)
        moneyness = strike / stock_price
        premium_ratio = self._premium_proxy(side, dte, moneyness, base_volatility)
        self.prepare("1900-01-01", market_date)
        snapshot_date = self._latest_date(symbol, market_date, max_age_days=14)
        if snapshot_date:
            rows = [
                item for item in self._by_symbol_date.get(symbol, {}).get(snapshot_date, [])
                if item.option_symbol != exclude_symbol
            ]
            params, dividend_yield, forward = self._surface(
                rows, snapshot_date, side, dte, cache_tag=exclude_symbol
            )
            if params:
                years = max(dte / 365.25, 1 / 365.25)
                log_moneyness = math.log(max(strike, 0.01) / max(forward or stock_price, 0.01))
                volatility = params.volatility(log_moneyness, years)
                spread = self._calibrated_half_spread(
                    rows, side, dte, moneyness, premium_ratio, volatility
                )
                return SurfaceEstimate(
                    min(2.0, max(0.03, volatility)), spread, "calibrated", params.samples, dividend_yield
                )
        multiplier, spread, samples = self._pooled_adjustment(
            symbol,
            side,
            dte,
            moneyness,
            premium_ratio,
            base_volatility,
            exclude_symbol=exclude_symbol,
        )
        source = "extrapolated" if samples else "uncalibrated"
        return SurfaceEstimate(
            min(2.0, max(0.03, base_volatility * multiplier)),
            spread,
            source,
            samples,
        )

    def uncertainty_pct(self) -> float | None:
        validation = self.store.get_setting(VALIDATION_SETTING) or {}
        measured = validation.get("worstEndingErrorPct")
        if isinstance(measured, (int, float)) and measured >= 0:
            return min(75.0, max(1.0, float(measured)))
        return None

    def status(self) -> dict[str, Any]:
        today = datetime.now(EASTERN).date()
        self.prepare("1900-01-01", today.isoformat())
        coverage = {}
        for symbol in SUPPORTED_SYMBOLS:
            dates = self._dates.get(symbol, [])
            rows = [item for item in self._quotes if item.underlying == symbol]
            coverage[symbol] = {
                "firstDate": dates[0] if dates else None,
                "lastDate": dates[-1] if dates else None,
                "anchorDates": len(dates),
                "quotes": len(rows),
                "contractSeries": len({item.option_symbol for item in rows}),
            }
        anchors = self._anchor_dates()
        completed = sum(
            1 for symbol in SUPPORTED_SYMBOLS for market_date in anchors
            if market_date in self.store.collection_dates(symbol, CALIBRATION_PROFILE)
        )
        total = len(anchors) * len(SUPPORTED_SYMBOLS)
        local_quotes = sum(int(item["quotes"]) for item in coverage.values())
        credits_used_today = self._collection_credits_today()
        affordable_batches = max(0, (MAX_DAILY_CALIBRATION_CREDITS - credits_used_today) // 12)
        validation = self.store.get_setting(VALIDATION_SETTING) or {
            "status": "not-run",
            "badge": "Insufficient evidence",
            "reason": "Run calibration and validation before relying on a measured error.",
        }
        quota = self.store.quota_status()
        return {
            "available": bool(getattr(self.exact_provider, "available", False)),
            "scope": {
                "symbols": list(SUPPORTED_SYMBOLS),
                "moneyness": [0.50, 1.50],
                "callDte": [365, 730],
                "putDte": [30, 60],
            },
            "coverage": coverage,
            "anchorSymbolDays": total,
            "completedAnchorSymbolDays": completed,
            "remainingAnchorSymbolDays": max(0, total - completed),
            "estimatedRemainingCredits": max(0, total - completed) * 12,
            "estimatedNextBatchCredits": min(4, max(0, total - completed), affordable_batches) * 12,
            "calibrationCreditsUsedToday": credits_used_today,
            "calibrationCreditsRemainingToday": max(0, MAX_DAILY_CALIBRATION_CREDITS - credits_used_today),
            "maxDailyCalibrationCredits": MAX_DAILY_CALIBRATION_CREDITS,
            "localQuotes": local_quotes,
            "dailyReserve": self.reserve_credits,
            "quota": quota,
            "validation": validation,
        }

    def sync(self, max_symbol_days: int = 4) -> dict[str, Any]:
        if not getattr(self.exact_provider, "available", False):
            raise RuntimeError("Save a Market Data token before improving option accuracy")
        anchors = self._anchor_dates()
        missing = [
            (market_date, symbol)
            for market_date in anchors
            for symbol in SUPPORTED_SYMBOLS
            if market_date not in self.store.collection_dates(symbol, CALIBRATION_PROFILE)
        ]
        result: dict[str, Any] = {
            "status": "complete",
            "symbolDaysCompleted": 0,
            "chainsStored": 0,
            "seriesStored": 0,
            "errors": [],
        }
        for market_date, symbol in missing[: max(1, min(max_symbol_days, 4))]:
            if not self._has_budget() or self._collection_credits_today() + 12 > MAX_DAILY_CALIBRATION_CREDITS:
                result["status"] = "partial"
                break
            before = self.store.quota_status().get("remaining")
            request_count = 0
            fingerprints: list[str] = []
            complete = True
            for side, targets in (("call", CALL_DTES), ("put", PUT_DTES)):
                for target in targets:
                    if not self._has_budget():
                        complete = False
                        break
                    try:
                        request_count += 1
                        chain = self.exact_provider.capture_accuracy_chain(symbol, market_date, side, target)
                        result["chainsStored"] += len(chain)
                        fingerprints.extend(item.option_symbol for item in chain)
                        selected = self._rotating_heldout(chain, market_date)
                        if not selected:
                            complete = False
                            result["errors"].append(
                                f"{symbol} {market_date} {side} {target}: no eligible held-out contract was returned"
                            )
                        elif self._has_budget():
                            end = min(date.fromisoformat(selected.expiration), datetime.now(EASTERN).date() - timedelta(days=1))
                            request_count += 1
                            series = self.exact_provider.option_quote_series(selected.option_symbol, market_date, end.isoformat())
                            result["seriesStored"] += len(series)
                            if len(series) < 2:
                                complete = False
                                result["errors"].append(
                                    f"{symbol} {market_date} {side} {target}: held-out history had fewer than two quotes"
                                )
                        else:
                            complete = False
                            result["errors"].append(
                                f"{symbol} {market_date} {side} {target}: stopped at the 30-credit reserve"
                            )
                    except Exception as exc:
                        complete = False
                        result["errors"].append(f"{symbol} {market_date} {side} {target}: {exc}")
                if not complete:
                    break
            after = self.store.quota_status().get("remaining")
            credits = max(0, int(before) - int(after)) if before is not None and after is not None else request_count
            self._record_collection_credits(max(credits, 0))
            checksum = hashlib.sha256("\n".join(sorted(set(fingerprints))).encode()).hexdigest()
            self.store.mark_collection(
                symbol, market_date, CALIBRATION_PROFILE,
                "complete" if complete else "partial", len(set(fingerprints)), credits,
                "; ".join(result["errors"][-2:]) if not complete else "", checksum,
            )
            if complete:
                result["symbolDaysCompleted"] += 1
        self._prepared_end = ""
        current = self.status()
        result["remainingAnchorSymbolDays"] = current["remainingAnchorSymbolDays"]
        result["quota"] = current["quota"]
        if result["errors"]:
            result["status"] = "partial"
        result["message"] = (
            f"Saved {result['symbolDaysCompleted']} SPY/QQQ calibration batch(es). "
            f"{result['remainingAnchorSymbolDays']} weekly symbol-date batch(es) remain."
        )
        return result

    def validate(self) -> dict[str, Any]:
        today = datetime.now(EASTERN).date().isoformat()
        self.prepare("1900-01-01", today)
        series: dict[str, list[OptionQuote]] = defaultdict(list)
        for quote in self._quotes:
            if quote.bid >= 0 and quote.ask > 0 and quote.underlying_price > 0:
                series[quote.option_symbol].append(quote)
        cases: dict[tuple[str, str, int, float], float] = {}
        runnable_portfolios = 0
        quote_errors: list[float] = []
        for option_symbol, rows in series.items():
            ordered = sorted(rows, key=lambda item: item.market_date)
            if len(ordered) < 2:
                continue
            opening, closing = ordered[0], ordered[-1]
            open_dte = (date.fromisoformat(opening.expiration) - date.fromisoformat(opening.market_date)).days
            target_dtes = CALL_DTES if opening.side == "call" else PUT_DTES
            target_dte = min(target_dtes, key=lambda value: abs(value - open_dte))
            if abs(target_dte - open_dte) > (90 if opening.side == "call" else 15):
                continue
            ratio = opening.strike / opening.underlying_price
            target_ratio = min(SUPPORTED_MONEYNESS, key=lambda value: abs(value - ratio))
            if abs(target_ratio - ratio) > 0.08:
                continue
            estimated_open = self._estimate_quote(opening, exclude_symbol=option_symbol)
            estimated_close = self._estimate_quote(closing, exclude_symbol=option_symbol)
            if not estimated_open or not estimated_close:
                continue
            for kind in (["call"] if opening.side == "call" else ["put", "short_put"]):
                exact_ending = self._one_leg_ending(opening, closing, kind, opening.ask, opening.bid, closing.bid, closing.ask)
                modeled_ending = self._one_leg_ending(
                    opening, closing, kind,
                    estimated_open["ask"], estimated_open["bid"], estimated_close["bid"], estimated_close["ask"],
                )
                error = abs(modeled_ending / exact_ending - 1) * 100 if exact_ending > 0 else 100.0
                key = (opening.underlying, kind, target_dte, target_ratio)
                # The badge is an every-portfolio gate. Keep the worst held-out
                # result in each evidence cell; a good contract must never hide
                # a failed contract in the same bucket.
                cases[key] = max(error, cases.get(key, 0.0))
                runnable_portfolios += 1
            quote_errors.extend([
                abs(estimated_open["mid"] / max(opening.midpoint, 0.01) - 1) * 100,
                abs(estimated_close["mid"] / max(closing.midpoint, 0.01) - 1) * 100,
            ])
        required = {
            (symbol, kind, dte, ratio)
            for symbol in SUPPORTED_SYMBOLS
            for kind in ("call", "put", "short_put")
            for dte in (CALL_DTES if kind == "call" else PUT_DTES)
            for ratio in SUPPORTED_MONEYNESS
        }
        missing = sorted(required - set(cases))
        mixed_errors = self._default_mixed_errors(series)
        mixed_worst = max(mixed_errors, default=None)
        worst_values = [*cases.values(), *mixed_errors]
        worst = max(worst_values, default=None)
        missing_count = len(missing) + (0 if mixed_errors else 1)
        passed = missing_count == 0 and worst is not None and worst <= 1.0
        report = {
            "status": "passed" if passed else ("failed" if missing_count == 0 else "insufficient-evidence"),
            "badge": "Validated within 1%" if passed else (f"Estimated, measured error {worst:.2f}%" if worst is not None and missing_count == 0 else "Insufficient evidence"),
            "reason": (
                "Every required held-out SPY/QQQ portfolio finished within 1%."
                if passed else
                (f"{missing_count} of {len(required) + 1} required evidence cells still need held-out contract histories."
                 if missing_count else "At least one held-out portfolio finished more than 1% from the exact-quote reference.")
            ),
            "validatedAt": datetime.now(EASTERN).isoformat(),
            "referenceStart": min((item.market_date for item in self._quotes), default=None),
            "referenceEnd": max((item.market_date for item in self._quotes), default=None),
            "requiredPortfolios": len(required) + 1,
            "validatedPortfolios": len(cases) + (1 if mixed_errors else 0),
            "runnableHeldOutPortfolios": runnable_portfolios + len(mixed_errors),
            "missingPortfolios": missing_count,
            "worstEndingErrorPct": round(worst, 4) if worst is not None else None,
            "defaultMixedWorstEndingErrorPct": round(mixed_worst, 4) if mixed_worst is not None else None,
            "medianQuoteErrorPct": round(statistics.median(quote_errors), 4) if quote_errors else None,
            "strictEveryPortfolioGate": True,
        }
        self.store.save_setting(VALIDATION_SETTING, report)
        return report

    def pricing_accuracy(
        self,
        start: str,
        holdings: Iterable[Any],
        option_rules: dict[str, OptionRule],
        source_counts: dict[str, int],
        assignment_uncertainty_pct: float = 0.0,
    ) -> dict[str, Any]:
        total = sum(source_counts.values())
        percentages = {
            key: round(source_counts.get(key, 0) / total * 100, 2) if total else 0.0
            for key in ("exact", "calibrated", "extrapolated", "uncalibrated", "missing")
        }
        validation = self.store.get_setting(VALIDATION_SETTING) or {}
        eligible = True
        reasons: list[str] = []
        for item in holdings:
            if getattr(item, "kind", "stock") == "stock" or float(getattr(item, "weight", 0)) <= 0:
                continue
            if str(getattr(item, "symbol", "")).upper() not in SUPPORTED_SYMBOLS:
                eligible = False
                reasons.append("Only SPY and QQQ are inside the strict calibration scope.")
                continue
            rule = option_rules.get(getattr(item, "key", ""))
            if not rule:
                continue
            valid_dte = 365 <= rule.target_dte <= 730 if rule.side == "call" else 30 <= rule.target_dte <= 60
            if not valid_dte:
                eligible = False
                reasons.append("An option expiration is outside the supported call or put range.")
        earliest = min((item.market_date for item in self._quotes), default=None)
        extrapolated = percentages["extrapolated"] > 0 or percentages["uncalibrated"] > 0 or bool(earliest and start < earliest)
        if percentages["exact"] >= 99.999 and percentages["missing"] == 0:
            label, level = "Exact historical quotes", "exact"
            reason = "Required option marks came from retained historical bid/ask quotes."
        elif (
            eligible and not extrapolated and assignment_uncertainty_pct <= 1
            and validation.get("status") == "passed" and percentages["missing"] == 0
        ):
            label, level = "Validated within 1%", "validated"
            reason = "Every applicable held-out portfolio passed the strict ending-value gate."
        elif extrapolated:
            label, level = "Extrapolated historical estimate", "extrapolated"
            reason = "Part of this test predates locally retained exact calibration evidence."
        elif validation.get("worstEndingErrorPct") is not None:
            measured = float(validation["worstEndingErrorPct"])
            label, level = f"Estimated, measured error {measured:.2f}%", "measured"
            reason = str(validation.get("reason") or "The strict 1% gate did not pass.")
        else:
            label, level = "Insufficient evidence", "insufficient"
            reason = "More held-out SPY/QQQ contract histories are needed before assigning a measured accuracy margin."
        if assignment_uncertainty_pct > 1:
            label, level = "Assignment outcome is uncertain", "assignment-uncertain"
            reason = "Early assignment could move the ending value by more than 1%, so the strict badge is unavailable."
        return {
            "label": label,
            "level": level,
            "reason": reason,
            "sourcePercentages": percentages,
            "supportedScope": {
                "symbols": list(SUPPORTED_SYMBOLS), "strikeRatio": [0.50, 1.50],
                "callDte": [365, 730], "putDte": [30, 60],
            },
            "eligible": eligible,
            "scopeWarnings": list(dict.fromkeys(reasons)),
            "worstHeldOutEndingErrorPct": validation.get("worstEndingErrorPct"),
            "referenceStart": validation.get("referenceStart"),
            "referenceEnd": validation.get("referenceEnd"),
            "validatedAt": validation.get("validatedAt"),
            "assignmentUncertaintyPct": round(max(0.0, assignment_uncertainty_pct), 4),
            "strictEveryPortfolioGate": True,
        }

    def _surface(
        self,
        rows: list[OptionQuote],
        snapshot_date: str,
        side: str,
        target_dte: int,
        cache_tag: str = "",
    ) -> tuple[SSVIParameters | None, float | None, float]:
        expirations = sorted({item.expiration for item in rows if item.side == side})
        if not expirations:
            return None, None, 0.0
        expiration = min(
            expirations,
            key=lambda value: abs((date.fromisoformat(value) - date.fromisoformat(snapshot_date)).days - target_dte),
        )
        key = (rows[0].underlying if rows else "", snapshot_date, expiration, side, cache_tag)
        if key in self._surface_cache:
            return self._surface_cache[key]
        selected = [item for item in rows if item.side == side and item.expiration == expiration]
        spot = statistics.median([item.underlying_price for item in selected if item.underlying_price > 0]) if any(item.underlying_price > 0 for item in selected) else 0.0
        dte = max(1, (date.fromisoformat(expiration) - date.fromisoformat(snapshot_date)).days)
        rate = self._risk_free_rate(snapshot_date, dte)
        forward = self._infer_forward(rows, expiration, spot, rate, dte)
        dividend_yield = None
        if spot > 0 and forward > 0:
            dividend_yield = min(0.20, max(-0.05, rate - math.log(forward / spot) / (dte / 365.25)))
        # Prefer the liquid out-of-the-money side at each strike. This lets an
        # OTM put inform a deep-ITM call (and vice versa) without fitting the
        # early-exercise-distorted midpoint of the less liquid contract.
        fit_rows = [
            item for item in rows
            if item.expiration == expiration and item.underlying_price > 0
            and (
                (item.side == "call" and item.strike >= item.underlying_price * 0.95)
                or (item.side == "put" and item.strike <= item.underlying_price * 1.05)
            )
        ]
        params = self._fit_essvi(fit_rows if len(fit_rows) >= 5 else selected, forward or spot, dte)
        result = (params, dividend_yield, forward or spot)
        self._surface_cache[key] = result
        return result

    @staticmethod
    def _fit_essvi(rows: list[OptionQuote], forward: float, dte: int) -> SSVIParameters | None:
        years = max(dte / 365.25, 1 / 365.25)
        points = [
            (math.log(item.strike / forward), float(item.iv) ** 2 * years)
            for item in rows
            if forward > 0 and item.strike > 0 and item.iv is not None and 0.03 <= item.iv <= 3.0
        ]
        if len(points) < 5:
            return None
        near = [variance for k, variance in points if abs(k) <= 0.08]
        theta = statistics.median(near or [variance for _, variance in points])
        best: tuple[float, float, float] | None = None
        for rho in (-0.9, -0.75, -0.6, -0.45, -0.3, -0.15, 0.0, 0.15, 0.3):
            for phi in (0.10, 0.20, 0.35, 0.50, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0):
                if theta * phi * (1 + abs(rho)) > 4.0:
                    continue
                error = 0.0
                for k, observed in points:
                    x = phi * k
                    predicted = 0.5 * theta * (1 + rho * x + math.sqrt((x + rho) ** 2 + 1 - rho**2))
                    error += (predicted - observed) ** 2
                if best is None or error < best[0]:
                    best = (error, rho, phi)
        return SSVIParameters(theta, best[1], best[2], len(points)) if best else None

    @staticmethod
    def _infer_forward(rows: list[OptionQuote], expiration: str, spot: float, rate: float, dte: int) -> float:
        paired: dict[float, dict[str, float]] = defaultdict(dict)
        for item in rows:
            if item.expiration == expiration and item.midpoint > 0 and item.strike > 0:
                paired[item.strike][item.side] = item.midpoint
        forwards = [
            (values["call"] - values["put"]) * math.exp(rate * dte / 365.25) + strike
            for strike, values in paired.items()
            if {"call", "put"} <= set(values) and (not spot or abs(strike / spot - 1) <= 0.15)
        ]
        return statistics.median(forwards) if forwards else spot

    def _pooled_adjustment(
        self,
        symbol: str,
        side: str,
        dte: int,
        moneyness: float,
        premium_ratio: float,
        target_iv: float,
        exclude_symbol: str = "",
    ) -> tuple[float, float, int]:
        dte_bucket = min((CALL_DTES if side == "call" else PUT_DTES), key=lambda value: abs(value - dte))
        money_bucket = min(SUPPORTED_MONEYNESS, key=lambda value: abs(value - moneyness))
        ratios: list[float] = []
        spread_rows: list[OptionQuote] = []
        for market_date, rows in self._by_symbol_date.get(symbol, {}).items():
            candidates = [
                item for item in rows
                if item.option_symbol != exclude_symbol
                and item.side == side and item.iv is not None and item.underlying_price > 0
                and abs((date.fromisoformat(item.expiration) - date.fromisoformat(market_date)).days - dte_bucket) <= (90 if side == "call" else 15)
                and abs(item.strike / item.underlying_price - money_bucket) <= 0.08
            ]
            if not candidates:
                continue
            atm = [
                item.iv for item in rows
                if item.option_symbol != exclude_symbol and item.side == side and item.iv
                and item.underlying_price > 0 and abs(item.strike / item.underlying_price - 1) <= 0.05
            ]
            atm_iv = statistics.median(atm) if atm else None
            for item in candidates:
                if atm_iv:
                    ratios.append(float(item.iv) / atm_iv)
                if math.isfinite(item.spread_pct):
                    spread_rows.append(item)
        return (
            min(2.0, max(0.5, statistics.median(ratios))) if ratios else 1.0,
            self._calibrated_half_spread(
                spread_rows, side, dte, moneyness, premium_ratio, target_iv
            ) if spread_rows else self._fallback_half_spread(side, dte, moneyness),
            len(ratios),
        )

    def _default_mixed_errors(self, series: dict[str, list[OptionQuote]]) -> list[float]:
        """Validate the app's default SPY/QQQ mix on common exact dates."""
        candidates: dict[tuple[str, str, str], tuple[OptionQuote, list[OptionQuote]]] = {}
        for rows in series.values():
            ordered = sorted(rows, key=lambda item: item.market_date)
            if len(ordered) < 2:
                continue
            opening = ordered[0]
            if opening.underlying not in SUPPORTED_SYMBOLS or opening.underlying_price <= 0:
                continue
            dte = (date.fromisoformat(opening.expiration) - date.fromisoformat(opening.market_date)).days
            target = 540 if opening.side == "call" else 45
            tolerance = 90 if opening.side == "call" else 15
            ratio = opening.strike / opening.underlying_price
            if abs(dte - target) > tolerance or abs(ratio - 1.0) > 0.08:
                continue
            key = (opening.market_date, opening.underlying, opening.side)
            previous = candidates.get(key)
            score = abs(dte - target) + abs(ratio - 1.0) * 100
            if previous is None:
                candidates[key] = (opening, ordered)
                continue
            old = previous[0]
            old_dte = (date.fromisoformat(old.expiration) - date.fromisoformat(old.market_date)).days
            old_score = abs(old_dte - target) + abs(old.strike / old.underlying_price - 1.0) * 100
            if score < old_score:
                candidates[key] = (opening, ordered)

        errors: list[float] = []
        opening_dates = sorted({key[0] for key in candidates})
        for opening_date in opening_dates:
            keys = [
                (opening_date, "SPY", "call"),
                (opening_date, "QQQ", "call"),
                (opening_date, "SPY", "put"),
                (opening_date, "QQQ", "put"),
            ]
            if any(key not in candidates for key in keys):
                continue
            rows_by_key = {key: {item.market_date: item for item in candidates[key][1]} for key in keys}
            common = set.intersection(*(set(values) for values in rows_by_key.values()))
            minimum_close = (date.fromisoformat(opening_date) + timedelta(days=14)).isoformat()
            close_dates = sorted(value for value in common if value >= minimum_close)
            if not close_dates:
                continue
            target_close = (date.fromisoformat(opening_date) + timedelta(days=21)).isoformat()
            close_date = min(close_dates, key=lambda value: abs((date.fromisoformat(value) - date.fromisoformat(target_close)).days))
            exact_total = 25_000.0
            modeled_total = 25_000.0
            valid = True
            for key in keys:
                opening = candidates[key][0]
                closing = rows_by_key[key][close_date]
                estimated_open = self._estimate_quote(opening, exclude_symbol=opening.option_symbol)
                estimated_close = self._estimate_quote(closing, exclude_symbol=opening.option_symbol)
                if not estimated_open or not estimated_close or opening.ask <= 0 or closing.bid < 0:
                    valid = False
                    break
                weight = 8_000.0 if opening.side == "call" else 2_000.0
                multiplier = max(1.0, opening.contract_multiplier)
                exact_quantity = int(weight // max(opening.ask * multiplier, 0.01))
                modeled_quantity = int(weight // max(estimated_open["ask"] * multiplier, 0.01))
                exact_total += weight - exact_quantity * opening.ask * multiplier + exact_quantity * closing.bid * multiplier
                modeled_total += weight - modeled_quantity * estimated_open["ask"] * multiplier + modeled_quantity * estimated_close["bid"] * multiplier
            if not valid:
                continue
            for symbol in SUPPORTED_SYMBOLS:
                opening = candidates[(opening_date, symbol, "call")][0]
                closing = rows_by_key[(opening_date, symbol, "call")][close_date]
                share_budget = 27_500.0
                share_ending = share_budget / opening.underlying_price * closing.underlying_price
                exact_total += share_ending
                modeled_total += share_ending
            errors.append(abs(modeled_total / max(exact_total, 0.01) - 1) * 100)
        return errors

    @staticmethod
    def _calibrated_half_spread(
        rows: list[OptionQuote],
        side: str,
        dte: int,
        moneyness: float,
        premium_ratio: float,
        target_iv: float,
    ) -> float:
        candidates = [
            item for item in rows
            if item.side == side and math.isfinite(item.spread_pct)
            and item.underlying_price > 0 and item.midpoint >= 0
        ]
        if not candidates:
            return AccuracyCalibration._fallback_half_spread(side, dte, moneyness)
        liquidities = sorted(math.log1p(max(0, item.open_interest) + max(0, item.volume)) for item in candidates)
        target_liquidity = statistics.median(liquidities)

        def distance(item: OptionQuote) -> float:
            observed_dte = max(1, (date.fromisoformat(item.expiration) - date.fromisoformat(item.market_date)).days)
            observed_money = item.strike / item.underlying_price
            observed_premium = max(item.midpoint / item.underlying_price, 1e-5)
            observed_iv = float(item.iv or target_iv)
            liquidity = math.log1p(max(0, item.open_interest) + max(0, item.volume))
            return (
                abs(math.log(observed_dte / max(dte, 1)))
                + 2.0 * abs(math.log(max(observed_money, 0.01) / max(moneyness, 0.01)))
                + abs(math.log(observed_premium / max(premium_ratio, 1e-5)))
                + 0.5 * abs(observed_iv - target_iv) / max(target_iv, 0.05)
                + 0.12 * abs(liquidity - target_liquidity)
            )

        nearest = sorted(candidates, key=distance)[: min(60, len(candidates))]
        spreads = [max(0.001, item.spread_pct / 2) for item in nearest]
        return min(0.50, max(0.001, statistics.median(spreads)))

    @staticmethod
    def _premium_proxy(side: str, dte: int, moneyness: float, volatility: float) -> float:
        intrinsic = max(0.0, 1 - moneyness) if side == "call" else max(0.0, moneyness - 1)
        distance = abs(math.log(max(moneyness, 0.01)))
        time_value = volatility * math.sqrt(max(dte, 1) / 365.25) * 0.40 * math.exp(-2.0 * distance)
        return max(1e-5, intrinsic + time_value)

    @staticmethod
    def _fallback_half_spread(side: str, dte: int, moneyness: float) -> float:
        distance = abs(math.log(max(moneyness, 0.01)))
        return min(0.50, 0.012 + distance * (0.08 if side == "put" else 0.06) + (0.01 if dte < 90 else 0.0))

    def _estimate_quote(self, quote: OptionQuote, exclude_symbol: str) -> dict[str, float] | None:
        dte = max(1, (date.fromisoformat(quote.expiration) - date.fromisoformat(quote.market_date)).days)
        estimate = self.estimate(
            quote.underlying, quote.market_date, quote.side, quote.strike, dte,
            quote.underlying_price, float(quote.iv or 0.22), exclude_symbol,
        )
        if estimate.source == "uncalibrated":
            return None
        from .modeled import american_option_price
        years = dte / 365.25
        rate = self._risk_free_rate(quote.market_date, dte)
        dividend_yield = estimate.dividend_yield if estimate.dividend_yield is not None else 0.015
        mid, _ = american_option_price(
            quote.underlying_price, quote.strike, years, rate, dividend_yield,
            estimate.volatility, quote.side,
        )
        intrinsic = quote.intrinsic_value(quote.underlying_price)
        mid = max(intrinsic, mid, 0.0)
        half = max(0.005, mid * estimate.half_spread_pct)
        return {
            "mid": mid,
            "bid": max(intrinsic, mid - half, 0.0),
            "ask": max(mid + half, 0.01),
        }

    @staticmethod
    def _one_leg_ending(
        opening: OptionQuote, closing: OptionQuote, kind: str,
        open_ask: float, open_bid: float, close_bid: float, close_ask: float,
    ) -> float:
        initial = 100_000.0
        share_budget, option_budget = 80_000.0, 20_000.0
        shares = share_budget / opening.underlying_price
        share_value = shares * closing.underlying_price
        multiplier = max(1.0, opening.contract_multiplier)
        if kind == "short_put":
            quantity = int(option_budget // (opening.strike * multiplier))
            unused = option_budget - quantity * opening.strike * multiplier
            return share_value + unused + quantity * (
                opening.strike * multiplier + open_bid * multiplier - close_ask * multiplier
            )
        quantity = int(option_budget // max(open_ask * multiplier, 0.01))
        unused = option_budget - quantity * open_ask * multiplier
        return share_value + unused + quantity * close_bid * multiplier

    def _latest_date(self, symbol: str, market_date: str, max_age_days: int) -> str | None:
        dates = self._dates.get(symbol, [])
        index = bisect_right(dates, market_date) - 1
        if index < 0:
            return None
        selected = dates[index]
        return selected if (date.fromisoformat(market_date) - date.fromisoformat(selected)).days <= max_age_days else None

    @staticmethod
    def _eligible_exact_chain(quotes: list[OptionQuote], market_date: str, rule: OptionRule) -> list[OptionQuote]:
        current = date.fromisoformat(market_date)
        eligible = [
            item for item in quotes
            if item.side == rule.side and not item.is_nonstandard
            and (date.fromisoformat(item.expiration) - current).days > rule.roll_dte
            and item.ask > 0
        ]
        if not eligible:
            return []
        expiration = min(
            {item.expiration for item in eligible},
            key=lambda value: abs((date.fromisoformat(value) - current).days - rule.target_dte),
        )
        selected = [item for item in eligible if item.expiration == expiration]
        return selected if len(selected) >= 5 else []

    @staticmethod
    def _series_has_endpoints(quotes: list[OptionQuote], start: str, end: str) -> bool:
        if not quotes:
            return False
        expiration = date.fromisoformat(quotes[0].expiration)
        required_end = min(expiration, date.fromisoformat(end))
        return date.fromisoformat(quotes[0].market_date) <= date.fromisoformat(start) + timedelta(days=7) and date.fromisoformat(quotes[-1].market_date) >= required_end - timedelta(days=7)

    def _can_download(self, market_date: str) -> bool:
        if not getattr(self.exact_provider, "available", False) or not self._has_budget():
            return False
        start = self.exact_provider.history_window_start()
        return start is None or date.fromisoformat(market_date) >= start

    def _has_budget(self) -> bool:
        remaining = self.store.quota_status().get("remaining")
        return remaining is None or int(remaining) > self.reserve_credits

    def _collection_credits_today(self) -> int:
        stored = self.store.get_setting(DAILY_BUDGET_SETTING) or {}
        today = datetime.now(EASTERN).date().isoformat()
        return max(0, int(stored.get("consumed") or 0)) if stored.get("date") == today else 0

    def _record_collection_credits(self, credits: int) -> None:
        self.store.save_setting(
            DAILY_BUDGET_SETTING,
            {
                "date": datetime.now(EASTERN).date().isoformat(),
                "consumed": self._collection_credits_today() + max(0, int(credits)),
            },
        )

    def _anchor_dates(self) -> list[str]:
        today = datetime.now(EASTERN).date()
        start = self.exact_provider.history_window_start(today) if getattr(self.exact_provider, "available", False) else today - timedelta(days=365)
        sessions = trading_dates(start or today - timedelta(days=365), today - timedelta(days=1))
        by_week: dict[tuple[int, int], date] = {}
        for session in sessions:
            iso = session.isocalendar()
            by_week[(iso.year, iso.week)] = session
        return [item.isoformat() for item in sorted(by_week.values())]

    @staticmethod
    def _rotating_heldout(chain: list[OptionQuote], market_date: str) -> OptionQuote | None:
        if not chain:
            return None
        spot = next((item.underlying_price for item in chain if item.underlying_price > 0), 0.0)
        if spot <= 0:
            return None
        week = date.fromisoformat(market_date).isocalendar().week
        ratio = SUPPORTED_MONEYNESS[week % len(SUPPORTED_MONEYNESS)]
        return min(chain, key=lambda item: abs(item.strike / spot - ratio))

    def _risk_free_rate(self, market_date: str, dte: int) -> float:
        points = []
        for days, series in (
            (30, "UST1MO"), (60, "UST2MO"), (91, "UST3MO"), (122, "UST4MO"),
            (182, "UST6MO"), (365, "UST1Y"), (730, "UST2Y"),
        ):
            values = self.reference.values(series)
            dates = sorted(values)
            index = bisect_right(dates, market_date) - 1
            if index >= 0:
                points.append((days, values[dates[index]] / 100))
        return interpolate_term(points, dte) or 0.025
