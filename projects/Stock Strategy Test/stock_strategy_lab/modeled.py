from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from bisect import bisect_right
import csv
from io import StringIO
import math
from pathlib import Path
import ssl
import statistics
import threading
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import certifi

from .calendar import is_us_trading_day
from .models import OptionQuote, OptionRule, StockBar
from .providers import ProviderError
from .reference_data import FreeReferenceData, interpolate_term

try:
    import numpy as np
except ImportError:  # pragma: no cover - requirements install supplies it
    np = None  # type: ignore[assignment]


FRED_SERIES = {
    "SPY": "VIXCLS",
    "QQQ": "VXNCLS",
    "rate": "DGS1",
}
FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
CONTRACT_MULTIPLIER = 100


@dataclass(frozen=True)
class ModeledContract:
    option_symbol: str
    underlying: str
    side: str
    base_strike: float
    expiration: str
    is_monthly: bool
    opened_on: str


class FredDailySeries:
    """Small, keyless FRED reader with a machine-local CSV cache."""

    def __init__(self, data_dir: Path, timeout: int = 4, allow_network: bool = False):
        self.cache_dir = data_dir / "free_model"
        self.timeout = timeout
        self.allow_network = allow_network
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._memory: dict[str, dict[str, float]] = {}
        self._lock = threading.RLock()

    def values(self, series: str) -> dict[str, float]:
        with self._lock:
            if series in self._memory:
                return self._memory[series]
        cached = self._read_cache(series)
        if cached:
            with self._lock:
                self._memory[series] = cached
            return cached
        if not self.allow_network:
            with self._lock:
                self._memory[series] = {}
            return {}
        downloaded = self._download(series)
        if downloaded:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            target = self.cache_dir / f"{series}.csv"
            target.write_text(downloaded, encoding="utf-8")
            parsed = self._parse(downloaded)
            with self._lock:
                self._memory[series] = parsed
            return parsed
        # A temporary source outage must not make every modeled quote retry the
        # same network request. The model has documented local fallbacks.
        with self._lock:
            self._memory[series] = {}
        return {}

    def _read_cache(self, series: str) -> dict[str, float]:
        target = self.cache_dir / f"{series}.csv"
        if not target.is_file():
            return {}
        try:
            return self._parse(target.read_text(encoding="utf-8"))
        except OSError:
            return {}

    def _download(self, series: str) -> str:
        request = Request(
            FRED_CSV_URL.format(series=series),
            headers={"Accept": "text/csv", "User-Agent": "NSY-Portfolio-Lab/1.0"},
        )
        try:
            with urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
                return response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError, UnicodeDecodeError):
            return ""

    @staticmethod
    def _parse(raw: str) -> dict[str, float]:
        output: dict[str, float] = {}
        for row in csv.DictReader(StringIO(raw)):
            market_date = str(row.get("DATE") or row.get("observation_date") or "")[:10]
            raw_value = next(
                (
                    value
                    for key, value in row.items()
                    if key not in {"DATE", "observation_date"} and value not in {None, "", "."}
                ),
                None,
            )
            if not market_date or raw_value is None:
                continue
            try:
                output[market_date] = float(raw_value)
            except ValueError:
                continue
        return output


class FreeModeledProvider:
    """Real share history plus transparent, deterministic option estimates.

    Stock observations are deliberately kept in memory only. The provider uses
    raw closes for option terms and adjusted closes for total-return share
    performance. Official Cboe and Treasury reference files provide historical
    volatility/rates without requiring another account.
    """

    name = "free-modeled"
    supports_option_split_adjustment = True

    def __init__(
        self,
        stock_provider: Any,
        data_dir: Path,
        fred: Any | None = None,
        calibration: Any | None = None,
    ):
        self.stock_provider = stock_provider
        self.reference = fred or FreeReferenceData(data_dir)
        # Keep this public alias for older local tests and integrations.
        self.fred = self.reference
        self.calibration = calibration
        self._bars: dict[str, list[StockBar]] = {}
        self._bar_dates: dict[str, list[str]] = {}
        self._bar_prices: dict[str, list[float]] = {}
        self._bar_return_prices: dict[str, list[float]] = {}
        self._contracts: dict[str, ModeledContract] = {}
        self._base_quote_cache: dict[tuple[str, str], tuple[float, float, float, float, float, str, float]] = {}
        self._realized_cache: dict[tuple[str, str], tuple[float, float]] = {}
        self._fred_value_cache: dict[tuple[str, str], float | None] = {}
        self._fred_dates: dict[str, list[str]] = {}
        self._lock = threading.RLock()
        self.modeled_quote_count = 0
        self.used_volatility_indices: set[str] = set()
        self.used_rate_history = False
        self.volatility_multiplier = 1.0
        self.spread_multiplier = 1.0
        self.model_price_multiplier = 1.0
        self.source_counts: dict[str, int] = {
            "exact": 0, "calibrated": 0, "extrapolated": 0,
            "uncalibrated": 0, "missing": 0,
        }
        self.assignment_uncertainty_pct = 0.0

    def stock_bars(self, symbol: str, start: str, end: str) -> list[StockBar]:
        warmup_start = (date.fromisoformat(start) - timedelta(days=370)).isoformat()
        symbol = symbol.upper()
        with self._lock:
            cached = list(self._bars.get(symbol, []))
        if cached and cached[0].market_date <= warmup_start and cached[-1].market_date >= end:
            bars = cached
        else:
            bars = self.stock_provider.stock_bars(symbol, warmup_start, end)
        with self._lock:
            self._bars[symbol] = list(bars)
            self._bar_dates[symbol] = [bar.market_date for bar in bars]
            # Option strikes, intrinsic value, and volatility must use the raw
            # contemporaneous underlying price, never a split-adjusted price.
            self._bar_prices[symbol] = [float(bar.close) for bar in bars]
            # Realized returns must use the adjusted series so a split is not
            # mistaken for an enormous one-day volatility event.
            self._bar_return_prices[symbol] = [float(bar.adjusted_close or bar.close) for bar in bars]
            self._realized_cache = {
                key: value for key, value in self._realized_cache.items() if key[0] != symbol
            }
        return [bar for bar in bars if start <= bar.market_date <= end]

    def option_chain(self, symbol: str, market_date: str, rule: OptionRule) -> list[OptionQuote]:
        symbol = symbol.upper()
        stock_price = self._stock_price(symbol, market_date)
        if self.calibration is not None:
            exact = self.calibration.exact_chain(symbol, market_date, rule, download=True)
            if exact:
                for quote in exact:
                    with self._lock:
                        self._contracts[quote.option_symbol] = ModeledContract(
                            option_symbol=quote.option_symbol,
                            underlying=symbol,
                            side=quote.side,
                            base_strike=quote.strike,
                            expiration=quote.expiration,
                            is_monthly=quote.is_monthly,
                            opened_on=market_date,
                        )
                return exact
        expiration, is_monthly = self._target_expiration(
            date.fromisoformat(market_date),
            rule.target_dte,
            rule.expiration_type == "monthly",
        )
        strikes = self._candidate_strikes(stock_price, rule)
        output: list[OptionQuote] = []
        for strike in strikes:
            option_symbol = (
                f"MODEL:{symbol}:{expiration.isoformat()}:{rule.side.upper()}:{strike:.4f}"
            )
            contract = ModeledContract(
                option_symbol=option_symbol,
                underlying=symbol,
                side=rule.side,
                base_strike=strike,
                expiration=expiration.isoformat(),
                is_monthly=is_monthly,
                opened_on=market_date,
            )
            with self._lock:
                self._contracts[option_symbol] = contract
            output.append(self._quote(contract, market_date, stock_price))
        return output

    def option_quote_series(self, option_symbol: str, start: str, end: str) -> list[OptionQuote]:
        with self._lock:
            contract = self._contracts.get(option_symbol)
            bars = list(self._bars.get(contract.underlying, [])) if contract else []
        if not contract:
            raise ProviderError("The free option model could not find the selected contract")
        expiration = date.fromisoformat(contract.expiration)
        exact_by_date: dict[str, OptionQuote] = {}
        if self.calibration is not None and not option_symbol.startswith("MODEL:"):
            exact_by_date = {
                item.market_date: item
                for item in self.calibration.exact_series(option_symbol, start, end, download=True)
            }
        output: list[OptionQuote] = []
        for bar in bars:
            market_date = bar.market_date
            if market_date < start or market_date > end or date.fromisoformat(market_date) > expiration:
                continue
            if market_date in exact_by_date:
                quote = exact_by_date[market_date]
                output.append(quote)
                with self._lock:
                    self.source_counts["exact"] += 1
                    self.modeled_quote_count += 1
                continue
            stock_price = float(bar.close)
            output.append(self._quote(contract, market_date, stock_price))
        if not output:
            with self._lock:
                self.source_counts["missing"] += 1
        return output

    def run_portfolio_backtest(self, **request: Any) -> dict[str, Any]:
        # Imported here to avoid a module cycle: unified defines the shared
        # simulator and only treats this object as a provider.
        from .unified import run_unified_backtest

        start, end = str(request["start"]), str(request["end"])
        prepare_start = (date.fromisoformat(start) - timedelta(days=370)).isoformat()
        if hasattr(self.stock_provider, "begin_run"):
            self.stock_provider.begin_run()
        if hasattr(self.reference, "prepare"):
            self.reference.prepare(prepare_start, end)
        if self.calibration is not None:
            self.calibration.prepare(prepare_start, end)
        self.modeled_quote_count = 0
        self.used_volatility_indices.clear()
        self.used_rate_history = False
        self.source_counts = {key: 0 for key in self.source_counts}
        self.assignment_uncertainty_pct = 0.0
        try:
            self._set_scenario(1.0, 1.0, 1.0)
            result = run_unified_backtest(self, **request)
            base_quote_count = self.modeled_quote_count
            base_source_counts = dict(self.source_counts)
            residual_pct = self.calibration.uncertainty_pct() if self.calibration is not None else None
            if result.get("optionCount") and residual_pct is not None:
                residual = residual_pct / 100
                self.source_counts = {key: 0 for key in self.source_counts}
                self._set_scenario(1.0, 1.0, max(0.05, 1 - residual))
                conservative_low = run_unified_backtest(self, **request)
                self.source_counts = {key: 0 for key in self.source_counts}
                self._set_scenario(1.0, 1.0, 1 + residual)
                conservative_high = run_unified_backtest(self, **request)
                low_by_date = {row["date"]: row["strategy"] for row in conservative_low["timeline"]}
                high_by_date = {row["date"]: row["strategy"] for row in conservative_high["timeline"]}
                for row in result["timeline"]:
                    alternatives = [
                        float(row["strategy"]),
                        float(low_by_date.get(row["date"], row["strategy"])),
                        float(high_by_date.get(row["date"], row["strategy"])),
                    ]
                    row["strategyLow"] = round(min(alternatives), 2)
                    row["strategyHigh"] = round(max(alternatives), 2)
                endings = [
                    float(result["metrics"]["strategy"]["endingValue"]),
                    float(conservative_low["metrics"]["strategy"]["endingValue"]),
                    float(conservative_high["metrics"]["strategy"]["endingValue"]),
                ]
                result["pricingSensitivity"] = {
                    "lowEndingValue": round(min(endings), 2),
                    "baseEndingValue": round(endings[0], 2),
                    "highEndingValue": round(max(endings), 2),
                        "description": (
                        "The shaded range replays the measured calibration residual around modeled time value. "
                        "It is an evidence-based sensitivity range, not a statistical confidence interval."
                    ),
                }
            if any(
                getattr(item, "kind", "") == "short_put" and float(getattr(item, "weight", 0)) > 0
                for item in request.get("holdings") or []
            ):
                self._set_scenario(1.0, 1.0, 1.0)
                self.source_counts = {key: 0 for key in self.source_counts}
                unassigned_request = dict(request)
                unassigned_request["assignment_mode"] = "none"
                unassigned = run_unified_backtest(self, **unassigned_request)
                assigned_ending = float(result["metrics"]["strategy"]["endingValue"])
                unassigned_ending = float(unassigned["metrics"]["strategy"]["endingValue"])
                self.assignment_uncertainty_pct = (
                    abs(unassigned_ending - assigned_ending) / max(abs(assigned_ending), 0.01) * 100
                )
                result["assignmentSensitivity"] = {
                    "assignedEndingValue": round(assigned_ending, 2),
                    "unassignedEndingValue": round(unassigned_ending, 2),
                    "differencePct": round(self.assignment_uncertainty_pct, 4),
                    "description": (
                        "The base path applies a rational deep-ITM assignment rule; the alternative leaves the short put open. "
                        "Actual assignment timing cannot be reconstructed from closing quotes."
                    ),
                }
                if result.get("pricingSensitivity"):
                    result["pricingSensitivity"]["lowEndingValue"] = round(
                        min(float(result["pricingSensitivity"]["lowEndingValue"]), unassigned_ending), 2
                    )
                    result["pricingSensitivity"]["highEndingValue"] = round(
                        max(float(result["pricingSensitivity"]["highEndingValue"]), unassigned_ending), 2
                    )
                unassigned_by_date = {row["date"]: float(row["strategy"]) for row in unassigned["timeline"]}
                for row in result["timeline"]:
                    alternative = unassigned_by_date.get(row["date"])
                    if alternative is None:
                        continue
                    row["strategyLow"] = round(min(float(row.get("strategyLow", row["strategy"])), alternative), 2)
                    row["strategyHigh"] = round(max(float(row.get("strategyHigh", row["strategy"])), alternative), 2)
            result["pricingMode"] = "modeled"
            result["modelVersion"] = "calibrated-american-v3"
            result["pricingCoverage"] = {
                "realStockPrices": 100,
                "realOptionQuotes": round(base_source_counts.get("exact", 0) / max(1, sum(base_source_counts.values())) * 100, 2),
                "modeledOptionQuotes": round((sum(base_source_counts.values()) - base_source_counts.get("exact", 0)) / max(1, sum(base_source_counts.values())) * 100, 2) if result.get("optionCount") else 0,
                "modeledQuoteCount": base_quote_count,
            }
            model_warning = (
                "Modeled option prices use a hybrid hierarchy: locally retained historical bid/ask quotes are used first. Remaining calls and puts "
                "use calibrated or explicitly labeled extrapolated estimates, so older option profits can still differ materially."
            )
            result["warnings"] = [model_warning, *(result.get("warnings") or [])]
            volatility_note = (
                "SPY volatility uses the historical Cboe VIX term structure; QQQ uses VXN plus the contemporaneous "
                "VIX term slope. Longer expirations are blended with trailing realized volatility."
                if self.used_volatility_indices
                else "Historical volatility-index observations were unavailable, so only trailing returns were used."
            )
            rate_note = (
                "Risk-free rates are interpolated from the historical U.S. Treasury curve for each option's term."
                if self.used_rate_history
                else "A documented 2.5% rate fallback was used where Treasury history was unavailable."
            )
            result["assumptions"] = [
                "Deep in-the-money options use an adaptive American-option lattice; other daily marks use the faster continuation value with the same arbitrage checks and exercise floor.",
                volatility_note,
                rate_note,
                "Trailing cash dividends inform dividend yield; raw closes determine option strikes and intrinsic value, while adjusted closes determine share total returns.",
                (
                    "The sensitivity band applies the locally measured calibration residual to modeled time value; exact retained quotes are not shocked."
                    if residual_pct is not None
                    else "No sensitivity band is shown until local held-out tests provide a measured portfolio-pricing residual."
                ),
                *(result.get("assumptions") or []),
            ]
            reference_status = self.reference.status() if hasattr(self.reference, "status") else {}
            result["dataQuality"] = {
                "level": "modeled-options" if result.get("optionCount") else "real-shares",
                "label": "Real shares + modeled options" if result.get("optionCount") else "Real share prices",
                "stockHistory": "Real daily provider prices; imported files are used when available.",
                "optionHistory": (
                    "Retained exact bid/ask quotes are used first; remaining values are tagged as calibrated, extrapolated, or uncalibrated."
                    if result.get("optionCount") else "No options were used."
                ),
                "lookAhead": (
                    "No future stock prices, rates, dividends, or daily volatility observations are used. Older periods may use "
                    "a retrospectively learned calibration shape and are labeled extrapolated."
                ),
                "referenceSources": reference_status.get("sources", []),
            }
            result["validation"] = {
                "status": "reference-backed-model",
                "note": (
                    "Cboe volatility and strategy-index history is used as a model reference, not as proof that a "
                    "custom option portfolio would have received those fills."
                ),
                "referenceCoverage": reference_status.get("coverage", {}),
            }
            if self.calibration is not None and result.get("optionCount"):
                resolved_rules = request.get("option_rules") or {}
                result["pricingAccuracy"] = self.calibration.pricing_accuracy(
                    start,
                    request.get("holdings") or [],
                    resolved_rules,
                    base_source_counts,
                    self.assignment_uncertainty_pct,
                )
                accuracy = result["pricingAccuracy"]
                result["validation"]["status"] = accuracy["level"]
                result["validation"]["note"] = accuracy["reason"]
            return result
        finally:
            self._set_scenario(1.0, 1.0, 1.0)
            with self._lock:
                self._bars.clear()
                self._bar_dates.clear()
                self._bar_prices.clear()
                self._bar_return_prices.clear()
                self._contracts.clear()
                self._base_quote_cache.clear()
                self._realized_cache.clear()
            if hasattr(self.stock_provider, "clear_transient"):
                self.stock_provider.clear_transient()

    def _set_scenario(
        self, volatility_multiplier: float, spread_multiplier: float, model_price_multiplier: float = 1.0
    ) -> None:
        self.volatility_multiplier = volatility_multiplier
        self.spread_multiplier = spread_multiplier
        self.model_price_multiplier = model_price_multiplier

    def _quote(self, contract: ModeledContract, market_date: str, stock_price: float) -> OptionQuote:
        current = date.fromisoformat(market_date)
        expiration = date.fromisoformat(contract.expiration)
        years = max((expiration - current).days / 365.25, 0.0)
        strike, multiplier = self._contract_terms(contract, market_date)
        dte = max((expiration - current).days, 1)
        cache_key = (contract.option_symbol, market_date)
        with self._lock:
            cached = self._base_quote_cache.get(cache_key) if self.volatility_multiplier == 1.0 else None
        if cached:
            theoretical, delta, intrinsic, volatility, base_half_spread, pricing_source, multiplier = cached
        else:
            base_volatility = self._volatility(
                contract.underlying,
                market_date,
                stock_price,
                strike,
                contract.side,
                dte,
            )
            calibration = None
            if self.calibration is not None:
                calibration = self.calibration.estimate(
                    contract.underlying, market_date, contract.side, strike, dte,
                    stock_price, base_volatility,
                )
            volatility = (
                calibration.volatility if calibration is not None else base_volatility
            ) * self.volatility_multiplier
            rate = self._risk_free_rate(market_date, dte)
            dividend_yield = (
                calibration.dividend_yield
                if calibration is not None and calibration.dividend_yield is not None
                else self._trailing_dividend_yield(contract.underlying, market_date, stock_price)
            )
            # Early exercise is economically material mainly for sufficiently
            # deep-in-the-money American contracts. Use the converged lattice
            # there and the closed-form continuation value elsewhere so a
            # ten-year daily mark-to-market run remains interactive.
            deep_itm = (
                contract.side == "call" and stock_price >= strike * 1.15
            ) or (
                contract.side == "put" and strike >= stock_price * 1.15
            )
            pricing_function = american_option_price if deep_itm else black_scholes_price
            theoretical, delta = pricing_function(
                stock_price,
                strike,
                years,
                rate,
                dividend_yield,
                volatility,
                contract.side,
            )
            intrinsic = max(
                0.0,
                stock_price - strike
                if contract.side == "call"
                else strike - stock_price,
            )
            unshocked_midpoint = max(theoretical, intrinsic, 0.0)
            if calibration is not None:
                base_half_spread = max(0.005, unshocked_midpoint * calibration.half_spread_pct)
                pricing_source = calibration.source
            else:
                base_half_spread = max(0.005, min(max(unshocked_midpoint, 0.01) * 0.08, 0.01 + max(unshocked_midpoint, 0.01) * 0.008 + stock_price * 0.00002))
                pricing_source = "uncalibrated"
            if self.volatility_multiplier == 1.0:
                with self._lock:
                    self._base_quote_cache[cache_key] = (
                        theoretical, delta, intrinsic, volatility, base_half_spread, pricing_source, multiplier
                    )
        time_value = max(0.0, theoretical - intrinsic) * self.model_price_multiplier
        upper_bound = stock_price if contract.side == "call" else strike
        midpoint = min(upper_bound, max(intrinsic + time_value, intrinsic, 0.0))
        half_spread = base_half_spread * self.spread_multiplier
        # A deep OTM option may genuinely have no executable bid. Do not create
        # a one-cent sale value that was never supported by market evidence.
        bid = max(intrinsic, midpoint - half_spread, 0.0)
        if intrinsic == 0 and midpoint <= half_spread:
            bid = 0.0
        ask = min(upper_bound, max(midpoint + half_spread, min(0.01, upper_bound)))
        with self._lock:
            self.modeled_quote_count += 1
            self.source_counts[pricing_source if pricing_source in self.source_counts else "uncalibrated"] += 1
        return OptionQuote(
            market_date=market_date,
            option_symbol=contract.option_symbol,
            underlying=contract.underlying,
            expiration=contract.expiration,
            side=contract.side,  # type: ignore[arg-type]
            strike=strike,
            bid=round(bid, 4),
            ask=round(ask, 4),
            last=round(midpoint, 4),
            delta=delta,
            iv=volatility,
            open_interest=1_000_000,
            volume=1_000_000,
            underlying_price=stock_price,
            is_monthly=contract.is_monthly,
            contract_multiplier=multiplier,
            pricing_source=pricing_source,
        )

    def _contract_terms(self, contract: ModeledContract, market_date: str) -> tuple[float, float]:
        with self._lock:
            bars = list(self._bars.get(contract.underlying, []))
        split_product = 1.0
        for bar in bars:
            if contract.opened_on < bar.market_date <= market_date and bar.split_factor > 0:
                split_product *= bar.split_factor
        return contract.base_strike / split_product, CONTRACT_MULTIPLIER * split_product

    def _trailing_dividend_yield(self, symbol: str, market_date: str, stock_price: float) -> float:
        cutoff = (date.fromisoformat(market_date) - timedelta(days=365)).isoformat()
        with self._lock:
            bars = list(self._bars.get(symbol, []))
        dividends = sum(
            max(0.0, bar.dividend_cash)
            for bar in bars
            if cutoff < bar.market_date <= market_date
        )
        return min(0.20, dividends / max(stock_price, 0.01))

    def _stock_price(self, symbol: str, market_date: str) -> float:
        with self._lock:
            dates = self._bar_dates.get(symbol, [])
            prices = self._bar_prices.get(symbol, [])
        index = bisect_right(dates, market_date) - 1
        if index < 0 or not prices:
            raise ProviderError(f"The free option model has no share price for {symbol} on {market_date}")
        return prices[index]

    def _volatility(
        self,
        symbol: str,
        market_date: str,
        stock_price: float,
        strike: float,
        side: str,
        dte: int,
    ) -> float:
        cache_key = (symbol, market_date)
        with self._lock:
            realized_pair = self._realized_cache.get(cache_key)
            dates = self._bar_dates.get(symbol, [])
            prices = self._bar_return_prices.get(symbol, [])
        if realized_pair is None:
            index = bisect_right(dates, market_date)
            window = prices[max(0, index - 253):index]
            returns = [
                math.log(current / previous)
                for previous, current in zip(window, window[1:])
                if previous > 0 and current > 0
            ]
            long_realized = _annualized_volatility(returns, fallback=0.22)
            short_realized = _annualized_volatility(returns[-21:], fallback=long_realized)
            with self._lock:
                self._realized_cache[cache_key] = (long_realized, short_realized)
        else:
            long_realized, short_realized = realized_pair
        realized = max(long_realized, short_realized * 0.85)

        spy_points = [
            (9, self._reference_value("VIX9D", market_date)),
            (30, self._reference_value("VIXCLS", market_date)),
            (93, self._reference_value("VIX3M", market_date)),
            (186, self._reference_value("VIX6M", market_date)),
            (365, self._reference_value("VIX1Y", market_date)),
        ]
        if symbol == "SPY":
            term_value = interpolate_term(
                [(days, value / 100) for days, value in spy_points if value is not None and value >= 5],
                dte,
            )
            if term_value:
                self.used_volatility_indices.update(
                    series for series, (_, value) in zip(
                        ("VIX9D", "VIXCLS", "VIX3M", "VIX6M", "VIX1Y"), spy_points
                    ) if value is not None and value >= 5
                )
        elif symbol == "QQQ":
            vxn = self._reference_value("VXNCLS", market_date)
            vix30 = self._reference_value("VIXCLS", market_date)
            spx_term = interpolate_term(
                [(days, value / 100) for days, value in spy_points if value is not None and value >= 5],
                dte,
            )
            if vxn is not None and vxn >= 5:
                term_value = vxn / 100
                if spx_term and vix30 and vix30 >= 5:
                    term_value *= spx_term / (vix30 / 100)
                self.used_volatility_indices.add("VXNCLS")
            else:
                term_value = None
        else:
            term_value = None
        market_iv = term_value if term_value else realized * 1.12
        term_weight = min(0.90, max(0.40, math.sqrt(180 / max(dte, 180))))
        volatility = term_weight * market_iv + (1 - term_weight) * max(long_realized * 1.10, 0.10)

        log_moneyness = math.log(max(strike, 0.01) / max(stock_price, 0.01))
        if side == "put" and strike < stock_price:
            volatility += min(0.18, abs(log_moneyness) * 0.45 + 0.015)
        elif side == "call" and strike > stock_price:
            volatility += min(0.08, abs(log_moneyness) * 0.18)
        return min(1.50, max(0.08, volatility))

    def _risk_free_rate(self, market_date: str, dte: int) -> float:
        tenors = [
            (30, "UST1MO"), (60, "UST2MO"), (91, "UST3MO"), (122, "UST4MO"),
            (182, "UST6MO"), (365, "UST1Y"), (730, "UST2Y"),
        ]
        value = interpolate_term(
            [
                (days, observed / 100)
                for days, series in tenors
                if (observed := self._reference_value(series, market_date)) is not None and observed >= 0
            ],
            dte,
        )
        if value is not None and value >= 0:
            self.used_rate_history = True
            return value
        return 0.025

    def _reference_value(self, series: str, market_date: str) -> float | None:
        cache_key = (series, market_date)
        with self._lock:
            if cache_key in self._fred_value_cache:
                return self._fred_value_cache[cache_key]
        values = self.reference.values(series)
        with self._lock:
            dates = self._fred_dates.get(series)
            if dates is None:
                dates = sorted(values)
                self._fred_dates[series] = dates
        index = bisect_right(dates, market_date) - 1
        value = values[dates[index]] if index >= 0 else None
        with self._lock:
            self._fred_value_cache[cache_key] = value
        return value

    @staticmethod
    def _target_expiration(current: date, target_dte: int, monthly: bool) -> tuple[date, bool]:
        target = current + timedelta(days=target_dte)
        if not monthly:
            expiration = target
            while not is_us_trading_day(expiration):
                expiration -= timedelta(days=1)
            return expiration, False
        candidates = []
        for offset in range(-2, 4):
            month_index = target.year * 12 + target.month - 1 + offset
            year, month_zero = divmod(month_index, 12)
            month = month_zero + 1
            first = date(year, month, 1)
            third_friday = first + timedelta(days=(4 - first.weekday()) % 7 + 14)
            expiration = third_friday
            while not is_us_trading_day(expiration):
                expiration -= timedelta(days=1)
            if expiration > current:
                candidates.append(expiration)
        if not candidates:
            raise ProviderError("The free option model could not construct a future expiration")
        return min(candidates, key=lambda item: abs((item - current).days - target_dte)), True

    @staticmethod
    def _candidate_strikes(stock_price: float, rule: OptionRule) -> list[float]:
        increment = 1.0 if stock_price < 50 else (2.5 if stock_price < 250 else 5.0)
        target = rule.target_strike(stock_price)
        if target is None:
            low, high = stock_price * 0.55, stock_price * 1.45
            start = math.floor(low / increment) * increment
            count = int(math.ceil((high - start) / increment))
            return [round(max(increment, start + index * increment), 4) for index in range(count + 1)]
        center = round(target / increment) * increment
        return [
            round(max(increment, center + offset * increment), 4)
            for offset in range(-4, 5)
        ]


def _annualized_volatility(returns: list[float], fallback: float) -> float:
    if len(returns) < 5:
        return fallback
    return statistics.stdev(returns) * math.sqrt(252)


def american_option_price(
    stock_price: float,
    strike: float,
    years: float,
    rate: float,
    dividend_yield: float,
    volatility: float,
    side: str,
    steps: int | None = None,
) -> tuple[float, float]:
    """Adaptive Cox-Ross-Rubinstein American value and tree delta.

    When a step count is supplied the function remains deterministic for unit
    tests and specialized callers. Normal pricing compares 128 and 256 steps,
    then doubles up to 1,024 until the result converges within 0.1% or one cent.
    """
    if years <= 0 or volatility <= 0 or stock_price <= 0 or strike <= 0:
        intrinsic = max(0.0, stock_price - strike) if side == "call" else max(0.0, strike - stock_price)
        delta = (1.0 if stock_price > strike else 0.0) if side == "call" else (-1.0 if stock_price < strike else 0.0)
        return intrinsic, delta
    if steps is not None:
        return _american_option_price_fixed(
            stock_price, strike, years, rate, dividend_yield, volatility, side, max(4, int(steps))
        )
    previous = _american_option_price_fixed(
        stock_price, strike, years, rate, dividend_yield, volatility, side, 128
    )
    for candidate in (256, 512, 1024):
        current = _american_option_price_fixed(
            stock_price, strike, years, rate, dividend_yield, volatility, side, candidate
        )
        tolerance = max(0.01, abs(current[0]) * 0.001)
        if abs(current[0] - previous[0]) <= tolerance:
            return current
        previous = current
    return previous


def _american_option_price_fixed(
    stock_price: float,
    strike: float,
    years: float,
    rate: float,
    dividend_yield: float,
    volatility: float,
    side: str,
    steps: int,
) -> tuple[float, float]:
    steps = max(4, int(steps))
    dt = years / steps
    up = math.exp(volatility * math.sqrt(dt))
    down = 1 / up
    denominator = up - down
    if abs(denominator) < 1e-12:
        return black_scholes_price(stock_price, strike, years, rate, dividend_yield, volatility, side)
    probability = (math.exp((rate - dividend_yield) * dt) - down) / denominator
    probability = min(1.0, max(0.0, probability))
    discount = math.exp(-rate * dt)

    def payoff(value: float) -> float:
        return max(0.0, value - strike) if side == "call" else max(0.0, strike - value)

    if np is not None:
        indices = np.arange(steps + 1, dtype=float)
        underlying = stock_price * np.power(down, steps - indices) * np.power(up, indices)
        values = np.maximum(underlying - strike, 0.0) if side == "call" else np.maximum(strike - underlying, 0.0)
        delta = 0.0
        for level in range(steps - 1, -1, -1):
            values = discount * (probability * values[1:] + (1 - probability) * values[:-1])
            indices = np.arange(level + 1, dtype=float)
            underlying = stock_price * np.power(down, level - indices) * np.power(up, indices)
            exercise = np.maximum(underlying - strike, 0.0) if side == "call" else np.maximum(strike - underlying, 0.0)
            values = np.maximum(values, exercise)
            if level == 1:
                delta = float((values[1] - values[0]) / max(stock_price * (up - down), 1e-12))
        return max(0.0, float(values[0])), delta

    values = [payoff(stock_price * (down ** (steps - index)) * (up ** index)) for index in range(steps + 1)]
    delta = 0.0
    for level in range(steps - 1, -1, -1):
        next_values: list[float] = []
        for index in range(level + 1):
            underlying = stock_price * (down ** (level - index)) * (up ** index)
            continuation = discount * (
                probability * values[index + 1] + (1 - probability) * values[index]
            )
            next_values.append(max(payoff(underlying), continuation))
        if level == 1:
            delta = (next_values[1] - next_values[0]) / max(stock_price * (up - down), 1e-12)
        values = next_values
    return max(0.0, values[0]), delta


def black_scholes_price(
    stock_price: float,
    strike: float,
    years: float,
    rate: float,
    dividend_yield: float,
    volatility: float,
    side: str,
) -> tuple[float, float]:
    if years <= 0 or volatility <= 0 or stock_price <= 0 or strike <= 0:
        intrinsic = max(0.0, stock_price - strike) if side == "call" else max(0.0, strike - stock_price)
        if side == "call":
            return intrinsic, 1.0 if stock_price > strike else 0.0
        return intrinsic, -1.0 if stock_price < strike else 0.0
    root_time = math.sqrt(years)
    d1 = (
        math.log(stock_price / strike)
        + (rate - dividend_yield + 0.5 * volatility * volatility) * years
    ) / (volatility * root_time)
    d2 = d1 - volatility * root_time
    discounted_stock = stock_price * math.exp(-dividend_yield * years)
    discounted_strike = strike * math.exp(-rate * years)
    if side == "call":
        price = discounted_stock * _normal_cdf(d1) - discounted_strike * _normal_cdf(d2)
        delta = math.exp(-dividend_yield * years) * _normal_cdf(d1)
    else:
        price = discounted_strike * _normal_cdf(-d2) - discounted_stock * _normal_cdf(-d1)
        delta = -math.exp(-dividend_yield * years) * _normal_cdf(-d1)
    return max(0.0, price), delta


def _normal_cdf(value: float) -> float:
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))
