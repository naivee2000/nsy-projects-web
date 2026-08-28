from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
import math
from typing import Any, Literal, Protocol

from .models import ROBINHOOD_OPTION_FEE_PER_CONTRACT, OptionQuote, OptionRule, StockBar


InstrumentKind = Literal["stock", "call", "put", "short_put"]
MISSING_RETRY_GAP_SESSIONS = 5
MAX_MISSING_RETRIES_PER_CYCLE = 1
MAX_PARALLEL_PROVIDER_REQUESTS = 4


class UnifiedDataProvider(Protocol):
    name: str

    def stock_bars(self, symbol: str, start: str, end: str) -> list[StockBar]: ...

    def option_chain(self, symbol: str, market_date: str, rule: OptionRule) -> list[OptionQuote]: ...

    def option_quote_series(self, option_symbol: str, start: str, end: str) -> list[OptionQuote]: ...


@dataclass(frozen=True)
class InstrumentHolding:
    symbol: str
    kind: InstrumentKind
    weight: float

    @property
    def key(self) -> str:
        return f"{self.symbol.upper()}:{self.kind}"

    @property
    def label(self) -> str:
        labels = {
            "stock": "shares",
            "call": "long call",
            "put": "long put",
            "short_put": "cash-secured short put",
        }
        return f"{self.symbol.upper()} {labels[self.kind]}"


@dataclass
class UnifiedOptionPosition:
    holding: InstrumentHolding
    quote: OptionQuote
    quantity: int
    series: dict[str, OptionQuote]
    last_quote: OptionQuote | None = None
    missing_sessions: int = 0
    collateral: float = 0.0
    last_valuation_date: str = ""
    last_mark_price: float = 0.0
    last_mark_multiplier: float = 100.0
    assigned_units: float = 0.0
    assigned_on: str = ""


class HybridMarketProvider:
    """Uses one provider for shares and another for exact historical options."""

    name = "tiingo+marketdata"

    def __init__(self, stock_provider: Any, option_provider: Any):
        self.stock_provider = stock_provider
        self.option_provider = option_provider

    def stock_bars(self, symbol: str, start: str, end: str) -> list[StockBar]:
        return self.stock_provider.stock_bars(symbol, start, end)

    def option_chain(self, symbol: str, market_date: str, rule: OptionRule) -> list[OptionQuote]:
        return self.option_provider.option_chain(symbol, market_date, rule)

    def option_quote_series(self, option_symbol: str, start: str, end: str) -> list[OptionQuote]:
        return self.option_provider.option_quote_series(option_symbol, start, end)


def run_unified_backtest(
    provider: UnifiedDataProvider,
    holdings: list[InstrumentHolding],
    start: str,
    end: str,
    initial_capital: float,
    rebalance: str,
    call_rule: OptionRule,
    put_rule: OptionRule,
    option_rules: dict[str, OptionRule] | None = None,
    cash_weight: float = 0,
    option_commission: float = ROBINHOOD_OPTION_FEE_PER_CONTRACT,
    assignment_mode: str = "rational",
) -> dict[str, Any]:
    resolved_rules = option_rules or {}
    _validate(
        holdings, start, end, initial_capital, rebalance, cash_weight,
        call_rule, put_rule, resolved_rules,
    )
    requested_symbols = list(dict.fromkeys([item.symbol.upper() for item in holdings] + ["SPY", "QQQ"]))
    adjusted_histories: dict[str, dict[str, float]] = {}
    raw_histories: dict[str, dict[str, float]] = {}
    first_dates: dict[str, str] = {}
    last_dates: dict[str, str] = {}
    split_symbols: set[str] = set()
    option_symbols = {item.symbol.upper() for item in holdings if item.kind != "stock"}

    def load_stock_history(symbol: str) -> tuple[str, list[StockBar]]:
        return symbol, provider.stock_bars(symbol, start, end)

    for symbol, bars in _parallel_map(load_stock_history, requested_symbols):
        adjusted = {
            bar.market_date: float(bar.adjusted_close or bar.close)
            for bar in bars if (bar.adjusted_close or bar.close) > 0 and bar.close > 0
        }
        raw = {bar.market_date: float(bar.close) for bar in bars if bar.close > 0}
        if not adjusted or not raw:
            raise ValueError(f"No daily price history was available for {symbol} in this period")
        if (
            symbol in option_symbols
            and any(bar.split_detected or abs(bar.split_factor - 1) > 1e-9 for bar in bars)
            and not getattr(provider, "supports_option_split_adjustment", False)
        ):
            split_symbols.add(symbol)
        adjusted_histories[symbol] = adjusted
        raw_histories[symbol] = raw
        first_dates[symbol] = min(adjusted)
        last_dates[symbol] = max(adjusted)
    if split_symbols:
        names = ", ".join(sorted(split_symbols))
        raise ValueError(
            f"This period crosses a split for {names}. This exact historical option source does not adjust "
            "contract strikes and multipliers, so choose dates on one side of the split."
        )

    common_dates = sorted(set.intersection(*(set(values) for values in adjusted_histories.values())))
    if len(common_dates) < 2:
        raise ValueError("The selected investments do not share enough trading dates for a comparison")
    actual_start, actual_end = common_dates[0], common_dates[-1]
    warnings: list[str] = []
    warning_keys: set[str] = set()
    if actual_start > start:
        limiting_date = max(first_dates.values())
        limiting = [symbol for symbol in requested_symbols if first_dates[symbol] == limiting_date]
        warnings.append(
            f"The chart begins on {actual_start} because {', '.join(limiting)} had no usable earlier price. "
            "Every selected investment and benchmark must share a date."
        )
    if actual_end < end:
        warnings.append(f"The chart ends on {actual_end}, the latest completed date shared by every selected symbol.")

    stock_units = {item.key: 0.0 for item in holdings if item.kind == "stock"}
    option_positions: dict[str, UnifiedOptionPosition | None] = {
        item.key: None for item in holdings if item.kind != "stock"
    }
    cash = initial_capital
    benchmark_units = {
        symbol: initial_capital / adjusted_histories[symbol][actual_start]
        for symbol in ("SPY", "QQQ")
    }
    scheduled = _rebalance_dates(common_dates, rebalance)
    timeline: list[dict[str, Any]] = []
    rebalance_count = 0
    roll_count = 0
    option_retry_count = 0
    assignment_count = 0
    fees = 0.0
    retry_due: dict[str, int] = {}
    retry_attempts: dict[str, int] = {}
    positive_option_keys = {
        item.key for item in holdings if item.kind != "stock" and item.weight > 0
    }

    for index, market_date in enumerate(common_dates):
        if assignment_mode == "rational":
            assignment_count += _assign_short_puts(
                option_positions, market_date, raw_histories, warnings, warning_keys
            )
        cash, expired_keys = _expire_positions(option_positions, market_date, raw_histories, cash)
        rolling_keys = {
            position.holding.key
            for position in option_positions.values()
            if position
            and (date.fromisoformat(position.quote.expiration) - date.fromisoformat(market_date)).days
            <= _rule_for(position.holding, call_rule, put_rule, resolved_rules).roll_dte
        }
        for key in sorted(rolling_keys):
            position = option_positions.get(key)
            if not position:
                continue
            cash, close_fee = _close_position(
                position, position.quantity, market_date,
                raw_histories[position.holding.symbol.upper()][market_date], cash,
                option_commission, warnings, warning_keys,
            )
            fees += close_fee
            option_positions[key] = None
            roll_count += 1

        scheduled_rebalance = market_date in scheduled and market_date != actual_start
        full_rebalance = index == 0 or scheduled_rebalance or bool(expired_keys | rolling_keys)
        if full_rebalance:
            if index > 0:
                rebalance_count += 1
            base_value = _current_value(
                holdings, stock_units, option_positions, adjusted_histories,
                raw_histories, market_date, cash, warnings, warning_keys,
            )
            cash, trade_fees = _rebalance_to_targets(
                provider, holdings, adjusted_histories, raw_histories,
                market_date, actual_end, cash, stock_units, option_positions,
                call_rule, put_rule, resolved_rules, option_commission,
                warnings, warning_keys, cash_weight, base_value,
            )
            fees += trade_fees
            missing_keys = {key for key in positive_option_keys if option_positions.get(key) is None}
            retry_due = {key: index + MISSING_RETRY_GAP_SESSIONS for key in missing_keys}
            retry_attempts = {key: 0 for key in missing_keys}
        else:
            due_keys = {key for key, due_index in retry_due.items() if index >= due_index}
            if due_keys:
                portfolio_value = _current_value(
                    holdings, stock_units, option_positions, adjusted_histories,
                    raw_histories, market_date, cash, warnings, warning_keys,
                )
                cash, retry_fees = _rebalance_to_targets(
                    provider, holdings, adjusted_histories, raw_histories,
                    market_date, actual_end, cash, stock_units, option_positions,
                    call_rule, put_rule, resolved_rules, option_commission,
                    warnings, warning_keys, cash_weight, portfolio_value,
                    only_keys=due_keys,
                )
                fees += retry_fees
                option_retry_count += len(due_keys)
                for key in due_keys:
                    retry_attempts[key] = retry_attempts.get(key, 0) + 1
                    if option_positions.get(key) is not None:
                        retry_due.pop(key, None)
                        retry_attempts.pop(key, None)
                    elif retry_attempts[key] < MAX_MISSING_RETRIES_PER_CYCLE:
                        retry_due[key] = index + MISSING_RETRY_GAP_SESSIONS
                    else:
                        retry_due.pop(key, None)
                        holding = next(item for item in holdings if item.key == key)
                        _warn(
                            warnings, warning_keys, f"retry-exhausted:{key}:{market_date}",
                            f"{holding.label} still had no usable contract after a limited retry. "
                            "Its allocation stayed in cash until the next planned portfolio event.",
                        )

        strategy_value = _current_value(
            holdings, stock_units, option_positions, adjusted_histories,
            raw_histories, market_date, cash, warnings, warning_keys,
        )
        timeline.append({
            "date": market_date,
            "strategy": round(strategy_value, 2),
            "spy": round(benchmark_units["SPY"] * adjusted_histories["SPY"][market_date], 2),
            "qqq": round(benchmark_units["QQQ"] * adjusted_histories["QQQ"][market_date], 2),
        })

    metrics = {
        key: _metrics([float(point[key]) for point in timeline], actual_start, actual_end, initial_capital)
        for key in ("strategy", "spy", "qqq")
    }
    ending_total = timeline[-1]["strategy"]
    breakdown: list[dict[str, Any]] = []
    for item in holdings:
        if item.kind == "stock":
            value = stock_units[item.key] * adjusted_histories[item.symbol.upper()][actual_end]
        else:
            value = _option_value(
                option_positions[item.key], actual_end,
                raw_histories[item.symbol.upper()][actual_end], warnings, warning_keys,
            )
        breakdown.append({
            "symbol": item.label,
            "targetWeight": item.weight,
            "endingWeight": value / ending_total * 100 if ending_total else 0,
            "endingValue": value,
            "kind": item.kind,
        })
    if cash_weight > 0 or cash > 0.01:
        breakdown.append({
            "symbol": "Cash",
            "targetWeight": cash_weight,
            "endingWeight": cash / ending_total * 100 if ending_total else 0,
            "endingValue": cash,
            "kind": "cash",
        })
    option_count = sum(item.kind != "stock" for item in holdings)
    assumptions = [
        "Adjusted daily closes are used for share and benchmark total returns; raw contemporaneous closes are used for option strikes and intrinsic value.",
        "Share allocations use fractional shares; option allocations use whole contracts and each quote's historical contract multiplier.",
        "Each option follows its own roll rule. Rolling a short-dated put does not replace an unrelated long-dated call.",
        "Long options open at ask and close at bid. Cash-secured short puts open at bid, close at ask, and reserve strike × multiplier in collateral.",
        "Strike targets are recalculated from the current raw stock price only when that option leg opens or rolls.",
        f"Estimated Robinhood stock/ETF option fees are ${option_commission:.2f} per contract per side. "
        "Minor sell-only regulatory fees, taxes, and share-trading costs are excluded.",
        "Cash and short-put collateral earn no interest in this version.",
    ]
    return {
        "provider": provider.name,
        "requestedStartDate": start,
        "requestedEndDate": end,
        "startDate": actual_start,
        "endDate": actual_end,
        "initialCapital": initial_capital,
        "rebalance": rebalance,
        "rebalanceCount": rebalance_count,
        "rollCount": roll_count,
        "holdings": [
            {"symbol": item.symbol.upper(), "kind": item.kind, "weight": item.weight}
            for item in holdings
        ],
        "cashWeight": cash_weight,
        "optionCount": option_count,
        "optionRetryCount": option_retry_count,
        "assignmentCount": assignment_count,
        "assignmentMode": assignment_mode,
        "optionRules": {
            item.key: _rule_for(item, call_rule, put_rule, resolved_rules).to_dict()
            for item in holdings if item.kind != "stock"
        },
        "fees": round(fees, 2),
        "coverage": [
            {"symbol": symbol, "startDate": first_dates[symbol], "endDate": last_dates[symbol]}
            for symbol in requested_symbols
        ],
        "timeline": timeline,
        "metrics": metrics,
        "breakdown": breakdown,
        "summary": _summary(metrics, option_count, fees),
        "warnings": warnings,
        "assumptions": assumptions,
    }


def _validate(
    holdings: list[InstrumentHolding], start: str, end: str, initial_capital: float, rebalance: str,
    cash_weight: float, call_rule: OptionRule, put_rule: OptionRule,
    option_rules: dict[str, OptionRule],
) -> None:
    if not holdings:
        raise ValueError("Add at least one stock, ETF, call, or put")
    if len(holdings) > 18:
        raise ValueError("This version supports up to eighteen investment rows")
    if len({item.key for item in holdings}) != len(holdings):
        raise ValueError("Each symbol and investment type can appear only once")
    if rebalance not in {"none", "monthly", "quarterly", "annual"}:
        raise ValueError("Rebalancing must be buy-and-hold, monthly, quarterly, or annual")
    if date.fromisoformat(start) >= date.fromisoformat(end):
        raise ValueError("The end date must be after the start date")
    if not 100 <= initial_capital <= 1_000_000_000:
        raise ValueError("Starting money must be between $100 and $1 billion")
    total = sum(item.weight for item in holdings) + cash_weight
    if abs(total - 100) > 0.05 or cash_weight < 0 or any(item.weight < 0 for item in holdings):
        raise ValueError("Portfolio allocations must add up to 100%")
    call_rule.validate()
    put_rule.validate()
    for item in holdings:
        if item.kind == "stock":
            continue
        rule = _rule_for(item, call_rule, put_rule, option_rules)
        expected_side = "put" if item.kind == "short_put" else item.kind
        if rule.side != expected_side:
            raise ValueError(f"The option settings for {item.label} have the wrong call/put side")
        rule.validate()


def _rule_for(
    holding: InstrumentHolding,
    call_rule: OptionRule,
    put_rule: OptionRule,
    option_rules: dict[str, OptionRule],
) -> OptionRule:
    return option_rules.get(holding.key, call_rule if holding.kind == "call" else put_rule)


def _rebalance_dates(dates: list[str], cadence: str) -> set[str]:
    if cadence == "none":
        return set()
    output: set[str] = set()
    previous: tuple[int, int] | int | None = None
    for value in dates:
        current = date.fromisoformat(value)
        if cadence == "monthly":
            key: tuple[int, int] | int = (current.year, current.month)
        elif cadence == "quarterly":
            key = (current.year, (current.month - 1) // 3)
        else:
            key = current.year
        if key != previous:
            output.add(value)
            previous = key
    return output


def _expire_positions(
    positions: dict[str, UnifiedOptionPosition | None],
    market_date: str,
    raw_histories: dict[str, dict[str, float]],
    cash: float,
) -> tuple[float, set[str]]:
    current = date.fromisoformat(market_date)
    expired: set[str] = set()
    for key, position in list(positions.items()):
        if not position or current < date.fromisoformat(position.quote.expiration):
            continue
        stock_price = raw_histories[position.holding.symbol.upper()][market_date]
        if position.assigned_units > 0:
            cash += position.assigned_units * stock_price * (1 - 0.0005)
            positions[key] = None
            expired.add(key)
            continue
        terms = position.series.get(market_date) or position.last_quote or position.quote
        intrinsic = terms.intrinsic_value(stock_price) * terms.contract_multiplier * position.quantity
        if position.holding.kind == "short_put":
            cash += position.collateral - intrinsic
        else:
            cash += intrinsic
        positions[key] = None
        expired.add(key)
    return cash, expired


def _close_position(
    position: UnifiedOptionPosition,
    quantity: int,
    market_date: str,
    stock_price: float,
    cash: float,
    commission: float,
    warnings: list[str],
    warning_keys: set[str],
) -> tuple[float, float]:
    if position.assigned_units > 0:
        cash += position.assigned_units * stock_price * (1 - 0.0005)
        position.assigned_units = 0.0
        position.assigned_on = ""
        position.quantity = 0
        return cash, 0.0
    quantity = min(quantity, position.quantity)
    price, multiplier = _mark_price(position, market_date, stock_price, warnings, warning_keys)
    fee = commission * quantity
    if position.holding.kind == "short_put":
        released = position.collateral * quantity / max(position.quantity, 1)
        cash += released - price * multiplier * quantity - fee
        position.collateral -= released
    else:
        cash += price * multiplier * quantity - fee
    position.quantity -= quantity
    return cash, fee


def _current_value(
    holdings: list[InstrumentHolding],
    stock_units: dict[str, float],
    positions: dict[str, UnifiedOptionPosition | None],
    adjusted_histories: dict[str, dict[str, float]],
    raw_histories: dict[str, dict[str, float]],
    market_date: str,
    cash: float,
    warnings: list[str],
    warning_keys: set[str],
) -> float:
    value = cash
    for item in holdings:
        if item.kind == "stock":
            value += stock_units[item.key] * adjusted_histories[item.symbol.upper()][market_date]
        else:
            value += _option_value(
                positions[item.key], market_date,
                raw_histories[item.symbol.upper()][market_date], warnings, warning_keys,
            )
    return value


def _rebalance_to_targets(
    provider: UnifiedDataProvider,
    holdings: list[InstrumentHolding],
    adjusted_histories: dict[str, dict[str, float]],
    raw_histories: dict[str, dict[str, float]],
    market_date: str,
    end: str,
    cash: float,
    stock_units: dict[str, float],
    positions: dict[str, UnifiedOptionPosition | None],
    call_rule: OptionRule,
    put_rule: OptionRule,
    option_rules: dict[str, OptionRule],
    commission: float,
    warnings: list[str],
    warning_keys: set[str],
    cash_weight: float,
    target_base: float,
    only_keys: set[str] | None = None,
) -> tuple[float, float]:
    fees = 0.0
    scoped = [item for item in holdings if only_keys is None or item.key in only_keys]
    # A rational early assignment converts a cash-secured put into shares. At
    # the next portfolio event those shares are sold before the target option
    # sleeve is restored, matching the strategy's replacement instruction.
    for item in scoped:
        position = positions.get(item.key)
        if item.kind != "stock" and position and position.assigned_units > 0:
            cash += position.assigned_units * raw_histories[item.symbol.upper()][market_date] * (1 - 0.0005)
            positions[item.key] = None
    missing_options = [
        item for item in scoped
        if item.kind != "stock" and item.weight > 0 and positions.get(item.key) is None
    ]

    def select_option(item: InstrumentHolding) -> tuple[str, OptionQuote | None]:
        rule = _rule_for(item, call_rule, put_rule, option_rules)
        chain = provider.option_chain(item.symbol, market_date, rule)
        return item.key, _select_contract(chain, rule, raw_histories[item.symbol.upper()][market_date])

    selected_options = dict(_parallel_map(select_option, missing_options))

    def load_option_series(item: InstrumentHolding) -> tuple[str, list[OptionQuote]]:
        selected = selected_options[item.key]
        assert selected is not None
        return item.key, provider.option_quote_series(selected.option_symbol, market_date, end)

    series_candidates = [item for item in missing_options if selected_options.get(item.key) is not None]
    option_series = dict(_parallel_map(load_option_series, series_candidates))

    desired_stock_units: dict[str, float] = {}
    desired_option_quantity: dict[str, int] = {}
    for item in scoped:
        target = target_base * item.weight / 100
        if item.kind == "stock":
            desired_stock_units[item.key] = target / adjusted_histories[item.symbol.upper()][market_date]
            continue
        position = positions.get(item.key)
        quote = selected_options.get(item.key)
        if position:
            quote = position.series.get(market_date) or position.last_quote or position.quote
        if not quote:
            desired_option_quantity[item.key] = 0
            continue
        if item.kind == "short_put":
            unit_target = quote.strike * quote.contract_multiplier
        else:
            unit_target = quote.ask * quote.contract_multiplier + commission
        desired_option_quantity[item.key] = math.floor(target / max(unit_target, 0.01))

    if only_keys is None:
        for item in scoped:
            if item.kind == "stock":
                desired = desired_stock_units[item.key]
                if stock_units[item.key] > desired:
                    cash += (stock_units[item.key] - desired) * adjusted_histories[item.symbol.upper()][market_date]
                    stock_units[item.key] = desired
                continue
            position = positions.get(item.key)
            desired = desired_option_quantity.get(item.key, 0)
            if position and position.quantity > desired:
                cash, fee = _close_position(
                    position, position.quantity - desired, market_date,
                    raw_histories[item.symbol.upper()][market_date], cash,
                    commission, warnings, warning_keys,
                )
                fees += fee
                if position.quantity <= 0:
                    positions[item.key] = None

    reserve = target_base * cash_weight / 100
    for item in scoped:
        if item.weight <= 0:
            continue
        spendable = max(0.0, cash - reserve)
        if item.kind == "stock":
            desired = desired_stock_units[item.key]
            additional = max(0.0, desired - stock_units[item.key])
            price = adjusted_histories[item.symbol.upper()][market_date]
            purchased = min(additional, spendable / price)
            stock_units[item.key] += purchased
            cash -= purchased * price
            continue

        position = positions.get(item.key)
        desired = desired_option_quantity.get(item.key, 0)
        if not position:
            selected = selected_options.get(item.key)
            if not selected:
                _warn(
                    warnings, warning_keys, f"missing:{item.key}:{market_date}",
                    f"No {item.label} met its expiration, liquidity, and spread rules on {market_date}. "
                    "That target allocation remained in cash, so the strategy had less option exposure than requested.",
                )
                continue
            if desired <= 0:
                consequence = (
                    "A cash-secured short put must reserve strike × contract multiplier."
                    if item.kind == "short_put" else "Options trade in whole contracts."
                )
                _warn(
                    warnings, warning_keys, f"small:{item.key}",
                    f"The allocation for {item.label} could not support one contract, so it remained in cash. {consequence}",
                )
                continue
            position = UnifiedOptionPosition(
                item, selected, 0,
                {quote.market_date: quote for quote in option_series.get(item.key, [])},
            )
            positions[item.key] = position
        if desired <= position.quantity:
            continue
        quote = position.series.get(market_date) or position.last_quote or position.quote
        multiplier = quote.contract_multiplier
        if item.kind == "short_put":
            collateral_per_contract = quote.strike * multiplier
            cash_cost = max(0.01, collateral_per_contract - quote.bid * multiplier + commission)
        else:
            collateral_per_contract = 0.0
            cash_cost = quote.ask * multiplier + commission
        wanted = desired - position.quantity
        quantity = min(wanted, math.floor(spendable / max(cash_cost, 0.01)))
        if quantity <= 0:
            if position.quantity == 0:
                positions[item.key] = None
            _warn(
                warnings, warning_keys, f"cash-small:{item.key}:{market_date}",
                f"Available cash could not buy one {item.label} contract on {market_date}; that amount stayed in cash.",
            )
            continue
        fee = quantity * commission
        if item.kind == "short_put":
            collateral = quantity * collateral_per_contract
            premium_received = quantity * quote.bid * multiplier
            cash -= collateral - premium_received + fee
            position.collateral += collateral
        else:
            cash -= quantity * quote.ask * multiplier + fee
        position.quantity += quantity
        fees += fee
    return cash, fees


def _parallel_map(function: Any, items: list[Any]) -> list[Any]:
    if len(items) < 2:
        return [function(item) for item in items]
    with ThreadPoolExecutor(
        max_workers=min(MAX_PARALLEL_PROVIDER_REQUESTS, len(items)),
        thread_name_prefix="market-read",
    ) as executor:
        return list(executor.map(function, items))


def _select_contract(chain: list[OptionQuote], rule: OptionRule, stock_price: float) -> OptionQuote | None:
    eligible = [
        item for item in chain
        if item.ask > 0 and item.open_interest >= rule.min_open_interest
        and item.spread_pct <= rule.max_spread_pct and not item.is_nonstandard
        and (rule.expiration_type != "monthly" or item.is_monthly)
    ]
    if not eligible:
        return None
    current = date.fromisoformat(eligible[0].market_date)
    expiration = min(
        {item.expiration for item in eligible},
        key=lambda value: abs((date.fromisoformat(value) - current).days - rule.target_dte),
    )
    eligible = [item for item in eligible if item.expiration == expiration]
    target_strike = rule.target_strike(stock_price)
    if target_strike is None:
        with_delta = [item for item in eligible if item.delta is not None]
        if with_delta:
            return min(with_delta, key=lambda item: abs(abs(item.delta or 0) - abs(rule.target_delta)))
        target_strike = stock_price
    return min(eligible, key=lambda item: abs(item.strike - target_strike))


def _mark_price(
    position: UnifiedOptionPosition,
    market_date: str,
    stock_price: float,
    warnings: list[str],
    warning_keys: set[str],
) -> tuple[float, float]:
    if position.assigned_units > 0:
        return stock_price, 1.0
    if position.last_valuation_date == market_date:
        return position.last_mark_price, position.last_mark_multiplier
    quote = position.series.get(market_date)
    short_put = position.holding.kind == "short_put"
    observed = quote.ask if short_put and quote else (quote.bid if quote else 0.0)
    if quote and (observed > 0 or (not short_put and quote.bid == 0)):
        position.last_quote = quote
        position.missing_sessions = 0
        exercise_floor = max(0.0, quote.intrinsic_value(stock_price) - stock_price * 0.0005)
        price = observed if short_put else max(observed, exercise_floor)
        multiplier = quote.contract_multiplier
        if not short_put and exercise_floor > observed + 0.005:
            _warn(
                warnings, warning_keys, f"exercise-floor:{position.quote.option_symbol}",
                "A deep in-the-money long option was worth more through exercise than its quoted bid, so the app used "
                "intrinsic value after estimated share slippage as the realizable exit value.",
            )
    else:
        position.missing_sessions += 1
        if position.last_quote and position.missing_sessions <= 1:
            price = max(0.0, position.last_quote.ask if short_put else position.last_quote.bid)
            multiplier = position.last_quote.contract_multiplier
            _warn(
                warnings, warning_keys, f"carried:{position.quote.option_symbol}:{market_date}",
                "An option lacked a usable quote for one session, so the prior observed quote was carried forward once. "
                "The result is marked as degraded because this was not an executable same-day price.",
            )
        else:
            terms = position.last_quote or position.quote
            price = terms.intrinsic_value(stock_price)
            multiplier = terms.contract_multiplier
            _warn(
                warnings, warning_keys, f"intrinsic:{position.quote.option_symbol}",
                "An option lacked usable quotes for more than one session, so its value fell back to intrinsic value. "
                "The result may materially understate or overstate an actual historical exit.",
            )
    position.last_valuation_date = market_date
    position.last_mark_price = price
    position.last_mark_multiplier = multiplier
    return price, multiplier


def _option_value(
    position: UnifiedOptionPosition | None,
    market_date: str,
    stock_price: float,
    warnings: list[str],
    warning_keys: set[str],
) -> float:
    if not position:
        return 0.0
    if position.assigned_units > 0:
        return position.assigned_units * stock_price
    price, multiplier = _mark_price(position, market_date, stock_price, warnings, warning_keys)
    option_value = price * multiplier * position.quantity
    return position.collateral - option_value if position.holding.kind == "short_put" else option_value


def _assign_short_puts(
    positions: dict[str, UnifiedOptionPosition | None],
    market_date: str,
    raw_histories: dict[str, dict[str, float]],
    warnings: list[str],
    warning_keys: set[str],
) -> int:
    assigned = 0
    current = date.fromisoformat(market_date)
    for position in positions.values():
        if not position or position.holding.kind != "short_put" or position.assigned_units > 0 or position.quantity <= 0:
            continue
        dte = (date.fromisoformat(position.quote.expiration) - current).days
        if dte <= 0:
            continue
        quote = position.series.get(market_date)
        if not quote or quote.ask <= 0:
            continue
        stock_price = raw_histories[position.holding.symbol.upper()][market_date]
        intrinsic = quote.intrinsic_value(stock_price)
        time_value = max(0.0, quote.ask - intrinsic)
        if intrinsic <= 0 or stock_price > quote.strike * 0.90 or time_value > 0.05:
            continue
        position.assigned_units = position.quantity * quote.contract_multiplier
        position.assigned_on = market_date
        position.quantity = 0
        position.collateral = 0.0
        assigned += 1
        _warn(
            warnings, warning_keys, f"assignment:{position.quote.option_symbol}",
            f"A deep in-the-money short put had no more than $0.05 of time value on {market_date}, so the rational-assignment "
            "scenario converted it into shares. Actual assignment timing is random and can differ.",
        )
    return assigned


def _metrics(values: list[float], start: str, end: str, initial: float) -> dict[str, float]:
    ending = values[-1]
    total_return = ending / initial - 1
    years = max((date.fromisoformat(end) - date.fromisoformat(start)).days / 365.25, 1 / 365.25)
    annualized = (ending / initial) ** (1 / years) - 1 if ending > 0 else -1
    peak = values[0]
    drawdown = 0.0
    for value in values:
        peak = max(peak, value)
        drawdown = min(drawdown, value / peak - 1 if peak else 0)
    return {
        "endingValue": ending,
        "totalReturn": total_return,
        "annualizedReturn": annualized,
        "maxDrawdown": drawdown,
    }


def _summary(metrics: dict[str, dict[str, float]], option_count: int, fees: float) -> str:
    strategy = metrics["strategy"]
    best = "QQQ" if metrics["qqq"]["endingValue"] >= metrics["spy"]["endingValue"] else "SPY"
    difference = strategy["endingValue"] - metrics[best.lower()]["endingValue"]
    option_note = (
        f" It used {option_count} option allocation{'s' if option_count != 1 else ''} "
        f"and charged ${fees:,.2f} in estimated Robinhood option fees."
        if option_count else ""
    )
    return (
        f"The strategy finished at ${strategy['endingValue']:,.0f}, ${abs(difference):,.0f} "
        f"{'above' if difference >= 0 else 'below'} putting all starting money in {best}. "
        f"Its largest temporary decline was {abs(strategy['maxDrawdown']) * 100:.1f}%.{option_note}"
    )


def _warn(warnings: list[str], keys: set[str], key: str, message: str) -> None:
    if key not in keys:
        keys.add(key)
        warnings.append(message)
