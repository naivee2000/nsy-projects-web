from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import hashlib
import math
from typing import Any, Protocol

from .calendar import trading_dates
from .models import StockBar


class StockHistoryProvider(Protocol):
    name: str

    def stock_bars(self, symbol: str, start: str, end: str) -> list[StockBar]: ...


class DemoPortfolioProvider:
    """Deterministic, symbol-specific stock paths for learning without an account."""

    name = "demo"

    def stock_bars(self, symbol: str, start: str, end: str) -> list[StockBar]:
        symbol = symbol.upper()
        seed = int(hashlib.sha256(symbol.encode()).hexdigest()[:8], 16)
        sessions = trading_dates(date.fromisoformat(start), date.fromisoformat(end))
        price = 70.0 + seed % 90
        drift = 0.00022 + (seed % 19) / 100_000
        phase = (seed % 628) / 100
        output: list[StockBar] = []
        for index, session in enumerate(sessions):
            cycle = math.sin(index / 19 + phase) * 0.0045 + math.sin(index / 83 + phase / 2) * 0.002
            shock = -0.055 if (index + seed) % 613 == 0 else 0.0
            change = drift + cycle + shock
            open_price = price
            price = max(2.0, price * (1 + change))
            output.append(
                StockBar(
                    market_date=session.isoformat(),
                    open=round(open_price, 4),
                    high=round(max(open_price, price) * 1.003, 4),
                    low=round(min(open_price, price) * 0.997, 4),
                    close=round(price, 4),
                    adjusted_close=round(price, 4),
                    volume=1_000_000 + (seed % 500_000),
                )
            )
        return output


@dataclass(frozen=True)
class Holding:
    symbol: str
    weight: float


def run_portfolio_backtest(
    provider: StockHistoryProvider,
    holdings: list[Holding],
    start: str,
    end: str,
    initial_capital: float,
    rebalance: str,
    cash_weight: float = 0,
) -> dict[str, Any]:
    if not holdings:
        raise ValueError("Add at least one stock or ETF")
    if rebalance not in {"none", "monthly", "quarterly", "annual"}:
        raise ValueError("Rebalancing must be buy-and-hold, monthly, quarterly, or annual")
    if not 100 <= initial_capital <= 1_000_000_000:
        raise ValueError("Starting money must be between $100 and $1 billion")
    if date.fromisoformat(start) >= date.fromisoformat(end):
        raise ValueError("The end date must be after the start date")
    total_weight = sum(item.weight for item in holdings) + cash_weight
    if abs(total_weight - 100) > 0.05 or cash_weight < 0 or any(item.weight < 0 for item in holdings):
        raise ValueError("Portfolio allocations must add up to 100%")

    requested = list(dict.fromkeys([item.symbol.upper() for item in holdings] + ["SPY", "QQQ"]))
    histories: dict[str, dict[str, float]] = {}
    first_dates: dict[str, str] = {}
    last_dates: dict[str, str] = {}
    for symbol in requested:
        bars = provider.stock_bars(symbol, start, end)
        prices = {bar.market_date: float(bar.adjusted_close or bar.close) for bar in bars if (bar.adjusted_close or bar.close) > 0}
        if not prices:
            raise ValueError(f"No daily price history was available for {symbol} in this period")
        histories[symbol] = prices
        first_dates[symbol] = min(prices)
        last_dates[symbol] = max(prices)

    common_dates = sorted(set.intersection(*(set(values) for values in histories.values())))
    if len(common_dates) < 2:
        raise ValueError("The selected holdings do not share enough trading dates for a comparison")
    actual_start, actual_end = common_dates[0], common_dates[-1]
    warnings: list[str] = []
    if actual_start > start:
        latest_first_date = max(first_dates.values())
        limiting_symbols = [symbol for symbol in requested if first_dates[symbol] == latest_first_date]
        if latest_first_date > start:
            names = ", ".join(limiting_symbols)
            verb = "has" if len(limiting_symbols) == 1 else "have"
            warnings.append(
                f"The chart begins on {actual_start} because {names} {verb} no usable price before "
                f"{latest_first_date}. A portfolio comparison can only begin when every selected holding "
                "and both benchmarks have prices."
            )
        else:
            warnings.append(
                f"The comparison begins on {actual_start}, the first trading date with a usable price for every holding and benchmark."
            )
    if actual_end < end:
        warnings.append(f"The comparison ends on {actual_end}, the latest completed date shared by every symbol.")

    target_weights = {item.symbol.upper(): item.weight / 100 for item in holdings}
    shares = {symbol: initial_capital * weight / histories[symbol][actual_start] for symbol, weight in target_weights.items()}
    target_cash_weight = cash_weight / 100
    cash_value = initial_capital * target_cash_weight
    benchmark_shares = {symbol: initial_capital / histories[symbol][actual_start] for symbol in ("SPY", "QQQ")}
    rebalance_dates = _rebalance_dates(common_dates, rebalance)
    timeline: list[dict[str, Any]] = []
    rebalance_count = 0
    for market_date in common_dates:
        if market_date in rebalance_dates and market_date != actual_start:
            value = cash_value + sum(shares[symbol] * histories[symbol][market_date] for symbol in shares)
            shares = {
                symbol: value * target_weights[symbol] / histories[symbol][market_date]
                for symbol in target_weights
            }
            cash_value = value * target_cash_weight
            rebalance_count += 1
        strategy_value = cash_value + sum(shares[symbol] * histories[symbol][market_date] for symbol in shares)
        timeline.append(
            {
                "date": market_date,
                "strategy": strategy_value,
                "spy": benchmark_shares["SPY"] * histories["SPY"][market_date],
                "qqq": benchmark_shares["QQQ"] * histories["QQQ"][market_date],
            }
        )

    metrics = {
        key: _metrics([float(point[key]) for point in timeline], actual_start, actual_end, initial_capital)
        for key in ("strategy", "spy", "qqq")
    }
    ending_total = timeline[-1]["strategy"]
    breakdown = []
    for item in holdings:
        symbol = item.symbol.upper()
        value = shares[symbol] * histories[symbol][actual_end]
        breakdown.append(
            {
                "symbol": symbol,
                "targetWeight": item.weight,
                "endingWeight": value / ending_total * 100 if ending_total else 0,
                "endingValue": value,
            }
        )
    if cash_weight > 0:
        breakdown.append(
            {
                "symbol": "CASH",
                "targetWeight": cash_weight,
                "endingWeight": cash_value / ending_total * 100 if ending_total else 0,
                "endingValue": cash_value,
            }
        )
    summary = _summary(metrics)
    return {
        "provider": provider.name,
        "requestedStartDate": start,
        "requestedEndDate": end,
        "startDate": actual_start,
        "endDate": actual_end,
        "initialCapital": initial_capital,
        "rebalance": rebalance,
        "rebalanceCount": rebalance_count,
        "holdings": [{"symbol": item.symbol.upper(), "weight": item.weight} for item in holdings],
        "cashWeight": cash_weight,
        "coverage": [
            {"symbol": symbol, "startDate": first_dates[symbol], "endDate": last_dates[symbol]}
            for symbol in requested
        ],
        "timeline": timeline,
        "metrics": metrics,
        "breakdown": breakdown,
        "summary": summary,
        "warnings": warnings,
        "assumptions": [
            "Adjusted daily closing prices are used, including the provider's split and distribution adjustments.",
            "Fractional shares are used so target percentages can be restored exactly.",
            "Cash earns no interest in this version.",
            "Taxes, commissions, bid/ask spreads, and market impact are not included.",
        ],
    }


def _rebalance_dates(dates: list[str], cadence: str) -> set[str]:
    if cadence == "none":
        return set()
    output: set[str] = set()
    previous_key: tuple[int, int] | int | None = None
    for value in dates:
        current = date.fromisoformat(value)
        if cadence == "monthly":
            key: tuple[int, int] | int = (current.year, current.month)
        elif cadence == "quarterly":
            key = (current.year, (current.month - 1) // 3)
        else:
            key = current.year
        if key != previous_key:
            output.add(value)
            previous_key = key
    return output


def _metrics(values: list[float], start: str, end: str, initial: float) -> dict[str, float]:
    ending = values[-1]
    total_return = ending / initial - 1
    years = max((date.fromisoformat(end) - date.fromisoformat(start)).days / 365.25, 1 / 365.25)
    annualized = (ending / initial) ** (1 / years) - 1 if ending > 0 else -1
    peak = values[0]
    max_drawdown = 0.0
    for value in values:
        peak = max(peak, value)
        max_drawdown = min(max_drawdown, value / peak - 1)
    return {
        "endingValue": ending,
        "totalReturn": total_return,
        "annualizedReturn": annualized,
        "maxDrawdown": max_drawdown,
    }


def _summary(metrics: dict[str, dict[str, float]]) -> str:
    strategy = metrics["strategy"]
    best_benchmark = "QQQ" if metrics["qqq"]["endingValue"] >= metrics["spy"]["endingValue"] else "SPY"
    difference = strategy["endingValue"] - metrics[best_benchmark.lower()]["endingValue"]
    direction = "more" if difference >= 0 else "less"
    return (
        f"The strategy finished at ${strategy['endingValue']:,.0f}, which was ${abs(difference):,.0f} {direction} "
        f"than putting all starting money in {best_benchmark}. Its largest temporary decline was "
        f"{abs(strategy['maxDrawdown']) * 100:.1f}%."
    )
