from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import math
import statistics
from typing import Any
import uuid

from .models import BacktestResult, OptionQuote, OptionRule, StockBar, StrategyDefinition, TradeEvent
from .providers import CachedProvider, DataProvider


CONTRACT_MULTIPLIER = 100


@dataclass
class OptionPosition:
    side: str
    quote: OptionQuote
    quantity: int
    series: dict[str, OptionQuote]
    last_quote: OptionQuote | None = None
    missing_sessions: int = 0


class BacktestEngine:
    def run(self, strategy: StrategyDefinition, provider: DataProvider, include_sweep: bool = False) -> BacktestResult:
        strategy.validate()
        provider = provider if isinstance(provider, CachedProvider) else CachedProvider(provider)
        bars = provider.stock_bars(strategy.ticker, strategy.start_date, strategy.end_date)
        if len(bars) < 2:
            raise ValueError("There are not enough trading days in this date range")
        if any(bar.split_detected for bar in bars):
            raise ValueError(
                "This period crosses a stock split that may have changed option contracts. "
                "Choose a period on one side of the split so the app does not show a misleading result."
            )
        run_id = uuid.uuid4().hex
        main = self._simulate(strategy, provider, bars)
        sweep_rows: list[dict[str, Any]] = []
        if include_sweep:
            for stock, call, put in allocation_grid(strategy.sweep_step_pct):
                candidate = strategy.with_weights(stock, call, put)
                result = self._simulate(candidate, provider, bars, compact=True)
                sweep_rows.append(
                    {
                        "stockPct": stock,
                        "callPct": call,
                        "putPct": put,
                        "endingValue": result["metrics"]["endingValue"],
                        "totalReturnPct": result["metrics"]["totalReturnPct"],
                        "maxDrawdownPct": result["metrics"]["maxDrawdownPct"],
                        "sharpeRatio": result["metrics"]["sharpeRatio"],
                        "warnings": len(result["warnings"]),
                    }
                )
            sweep_rows.sort(key=lambda item: (item["endingValue"], -item["maxDrawdownPct"]), reverse=True)
        summary = {
            "ticker": strategy.ticker.upper(),
            "period": f"{bars[0].market_date} to {bars[-1].market_date}",
            "startingValue": strategy.initial_capital,
            "endingValue": main["metrics"]["endingValue"],
            "gainLoss": main["metrics"]["endingValue"] - strategy.initial_capital,
            "benchmarkEndingValue": main["metrics"]["benchmarkEndingValue"],
            "versusBenchmark": main["metrics"]["endingValue"] - main["metrics"]["benchmarkEndingValue"],
            "plainStrategy": strategy.plain_summary(),
            "sweepCount": len(sweep_rows),
        }
        return BacktestResult(
            run_id=run_id,
            strategy=strategy.to_dict(),
            status="complete",
            summary=summary,
            explanation=self._explain(strategy, main),
            metrics=main["metrics"],
            daily_equity=main["dailyEquity"],
            benchmark_equity=main["benchmarkEquity"],
            attribution=main["attribution"],
            trades=main["trades"],
            warnings=main["warnings"],
            audit={
                "engineVersion": "1.0",
                "provider": provider.name,
                "stockSessions": len(bars),
                "optionMultiplier": CONTRACT_MULTIPLIER,
                "fillRules": {
                    "stock": "closing price plus/minus configured slippage",
                    "optionBuy": "ask",
                    "optionSell": "bid",
                    "missingBid": "one-session carry, then intrinsic value",
                },
                "dataStart": bars[0].market_date,
                "dataEnd": bars[-1].market_date,
                "calculatedAt": datetime.now(timezone.utc).isoformat(),
            },
            created_at=datetime.now(timezone.utc).isoformat(),
            sweep=sweep_rows,
        )

    def _simulate(
        self,
        strategy: StrategyDefinition,
        provider: DataProvider,
        bars: list[StockBar],
        compact: bool = False,
    ) -> dict[str, Any]:
        cash = strategy.initial_capital
        stock_shares = 0
        option_positions: dict[str, OptionPosition | None] = {"call": None, "put": None}
        warnings: list[str] = []
        warning_keys: set[str] = set()
        trades: list[TradeEvent] = []
        daily_equity: list[dict[str, Any]] = []
        contributions = {"stock": 0.0, "call": 0.0, "put": 0.0}
        total_fees = 0.0
        turnover = 0.0
        roll_count = 0
        previous_bar: StockBar | None = None
        next_retry_index = 5

        benchmark_buy = bars[0].close * (1 + strategy.stock_slippage_bps / 10_000)
        benchmark_shares = math.floor(strategy.initial_capital / max(benchmark_buy, 0.01))
        benchmark_cash = strategy.initial_capital - benchmark_shares * benchmark_buy - strategy.stock_commission
        benchmark_equity: list[dict[str, Any]] = []

        cash, stock_shares, total_fees, turnover = self._allocate(
            strategy,
            provider,
            bars[0],
            cash,
            stock_shares,
            option_positions,
            contributions,
            trades,
            warnings,
            warning_keys,
            total_fees,
            turnover,
            "initial allocation",
        )

        for index, bar in enumerate(bars):
            current_day = date.fromisoformat(bar.market_date)
            if previous_bar:
                dividend = self._dividend_per_share(previous_bar, bar)
                if dividend > 0 and stock_shares:
                    amount = dividend * stock_shares
                    cash += amount
                    contributions["stock"] += amount
                    if not compact:
                        trades.append(
                            TradeEvent(bar.market_date, "stock", "dividend", strategy.ticker.upper(), stock_shares, dividend, amount, 0, "cash dividend")
                        )
                benchmark_cash += dividend * benchmark_shares

            for side, position in list(option_positions.items()):
                if position and current_day >= date.fromisoformat(position.quote.expiration):
                    intrinsic = position.quote.intrinsic_value(bar.close)
                    proceeds = intrinsic * CONTRACT_MULTIPLIER * position.quantity
                    cash += proceeds
                    contributions[side] += proceeds
                    turnover += proceeds
                    if not compact:
                        trades.append(
                            TradeEvent(
                                bar.market_date,
                                side,
                                "expire",
                                position.quote.option_symbol,
                                position.quantity,
                                intrinsic,
                                proceeds,
                                0,
                                "cash value at expiration",
                            )
                        )
                    option_positions[side] = None

            should_roll = False
            for side, position in option_positions.items():
                if not position:
                    continue
                rule = strategy.call_rule if side == "call" else strategy.put_rule
                remaining = (date.fromisoformat(position.quote.expiration) - current_day).days
                if remaining <= rule.roll_dte:
                    should_roll = True
            missing_weighted_leg = (
                (strategy.call_pct > 0 and option_positions["call"] is None)
                or (strategy.put_pct > 0 and option_positions["put"] is None)
            )
            if index >= next_retry_index and missing_weighted_leg:
                should_roll = True
                next_retry_index = index + 5
            if index > 0 and should_roll:
                cash, stock_shares, total_fees, turnover = self._liquidate(
                    strategy,
                    bar,
                    cash,
                    stock_shares,
                    option_positions,
                    contributions,
                    trades,
                    warnings,
                    warning_keys,
                    total_fees,
                    turnover,
                    "scheduled rebalance",
                    compact,
                )
                cash, stock_shares, total_fees, turnover = self._allocate(
                    strategy,
                    provider,
                    bar,
                    cash,
                    stock_shares,
                    option_positions,
                    contributions,
                    trades,
                    warnings,
                    warning_keys,
                    total_fees,
                    turnover,
                    "scheduled rebalance",
                    compact,
                )
                roll_count += 1

            stock_value = stock_shares * bar.close
            call_value = self._position_value(option_positions["call"], bar, warnings, warning_keys)
            put_value = self._position_value(option_positions["put"], bar, warnings, warning_keys)
            equity = cash + stock_value + call_value + put_value
            daily_equity.append(
                {
                    "date": bar.market_date,
                    "value": round(equity, 2),
                    "stock": round(stock_value, 2),
                    "call": round(call_value, 2),
                    "put": round(put_value, 2),
                    "cash": round(cash, 2),
                }
            )
            benchmark_equity.append(
                {"date": bar.market_date, "value": round(benchmark_cash + benchmark_shares * bar.close, 2)}
            )
            previous_bar = bar

        cash, stock_shares, total_fees, turnover = self._liquidate(
            strategy,
            bars[-1],
            cash,
            stock_shares,
            option_positions,
            contributions,
            trades,
            warnings,
            warning_keys,
            total_fees,
            turnover,
            "end of test",
            compact,
        )
        daily_equity[-1]["value"] = round(cash, 2)
        daily_equity[-1].update({"stock": 0.0, "call": 0.0, "put": 0.0, "cash": round(cash, 2)})
        benchmark_sell = bars[-1].close * (1 - strategy.stock_slippage_bps / 10_000)
        benchmark_final = benchmark_cash + benchmark_shares * benchmark_sell - strategy.stock_commission
        benchmark_equity[-1]["value"] = round(benchmark_final, 2)
        metrics = self._metrics(
            strategy,
            daily_equity,
            benchmark_final,
            total_fees,
            turnover,
            roll_count,
        )
        return {
            "metrics": metrics,
            "dailyEquity": [] if compact else daily_equity,
            "benchmarkEquity": [] if compact else benchmark_equity,
            "attribution": {key: round(value, 2) for key, value in contributions.items()},
            "trades": [] if compact else [trade.to_dict() for trade in trades],
            "warnings": warnings,
        }

    def _allocate(
        self,
        strategy: StrategyDefinition,
        provider: DataProvider,
        bar: StockBar,
        cash: float,
        stock_shares: int,
        option_positions: dict[str, OptionPosition | None],
        contributions: dict[str, float],
        trades: list[TradeEvent],
        warnings: list[str],
        warning_keys: set[str],
        total_fees: float,
        turnover: float,
        reason: str,
        compact: bool = False,
    ) -> tuple[float, int, float, float]:
        available = cash
        stock_target = available * strategy.stock_pct / 100
        stock_price = bar.close * (1 + strategy.stock_slippage_bps / 10_000)
        shares = math.floor(max(0.0, stock_target - strategy.stock_commission) / max(stock_price, 0.01))
        if shares:
            notional = shares * stock_price
            fee = strategy.stock_commission
            cash -= notional + fee
            stock_shares += shares
            contributions["stock"] -= notional + fee
            total_fees += fee
            turnover += notional
            if not compact:
                trades.append(TradeEvent(bar.market_date, "stock", "buy", strategy.ticker.upper(), shares, stock_price, -(notional + fee), fee, reason))
        elif strategy.stock_pct > 0:
            self._warn(
                warnings,
                warning_keys,
                "stock-too-small",
                "The stock allocation was too small to buy one whole share, so that portion remained in cash.",
            )

        for side, pct, rule in (
            ("call", strategy.call_pct, strategy.call_rule),
            ("put", strategy.put_pct, strategy.put_rule),
        ):
            if pct <= 0:
                option_positions[side] = None
                continue
            target = available * pct / 100
            chain = provider.option_chain(strategy.ticker, bar.market_date, rule)
            selected = self._select_contract(chain, rule, bar.close)
            if not selected:
                self._warn(
                    warnings,
                    warning_keys,
                    f"no-{side}-{bar.market_date}",
                    f"No {side} met the expiration, liquidity, and spread rules on {bar.market_date}. "
                    "That allocation stayed in cash, so the result has less option exposure than requested.",
                )
                option_positions[side] = None
                continue
            unit_cost = selected.ask * CONTRACT_MULTIPLIER + strategy.option_commission
            quantity = math.floor(target / max(unit_cost, 0.01))
            if quantity <= 0:
                self._warn(
                    warnings,
                    warning_keys,
                    f"small-{side}",
                    f"The {side} allocation could not buy one whole contract, so that money remained in cash.",
                )
                option_positions[side] = None
                continue
            premium = quantity * selected.ask * CONTRACT_MULTIPLIER
            fees = quantity * strategy.option_commission
            cash -= premium + fees
            contributions[side] -= premium + fees
            total_fees += fees
            turnover += premium
            series = provider.option_quote_series(selected.option_symbol, bar.market_date, strategy.end_date)
            option_positions[side] = OptionPosition(side, selected, quantity, {item.market_date: item for item in series})
            if not compact:
                trades.append(
                    TradeEvent(
                        bar.market_date,
                        side,
                        "buy",
                        selected.option_symbol,
                        quantity,
                        selected.ask,
                        -(premium + fees),
                        fees,
                        reason,
                    )
                )
        return cash, stock_shares, total_fees, turnover

    def _liquidate(
        self,
        strategy: StrategyDefinition,
        bar: StockBar,
        cash: float,
        stock_shares: int,
        option_positions: dict[str, OptionPosition | None],
        contributions: dict[str, float],
        trades: list[TradeEvent],
        warnings: list[str],
        warning_keys: set[str],
        total_fees: float,
        turnover: float,
        reason: str,
        compact: bool,
    ) -> tuple[float, int, float, float]:
        if stock_shares:
            price = bar.close * (1 - strategy.stock_slippage_bps / 10_000)
            proceeds = stock_shares * price
            fee = strategy.stock_commission
            cash += proceeds - fee
            contributions["stock"] += proceeds - fee
            turnover += proceeds
            total_fees += fee
            if not compact:
                trades.append(TradeEvent(bar.market_date, "stock", "sell", strategy.ticker.upper(), stock_shares, price, proceeds - fee, fee, reason))
            stock_shares = 0
        for side, position in list(option_positions.items()):
            if not position:
                continue
            quote = self._quote_for_day(position, bar)
            carried = bool(not quote and position.last_quote and position.missing_sessions < 1)
            price = quote.bid if quote else (position.last_quote.bid if carried and position.last_quote else position.quote.intrinsic_value(bar.close))
            if not quote:
                if carried:
                    self._warn(
                        warnings,
                        warning_keys,
                        f"carried-exit-{position.quote.option_symbol}",
                        "An option had no bid on its sale date, so the previous trading session's bid was used once. "
                        "The result is marked as degraded because that sale price was not observed on the simulated date.",
                    )
                else:
                    self._warn(
                        warnings,
                        warning_keys,
                        f"intrinsic-exit-{position.quote.option_symbol}",
                        "An option had no usable closing bid for more than one session, so the app used only its intrinsic value. "
                        "The result is conservative and may understate what a sale could have received.",
                    )
            proceeds = price * CONTRACT_MULTIPLIER * position.quantity
            fees = position.quantity * strategy.option_commission
            cash += proceeds - fees
            contributions[side] += proceeds - fees
            turnover += proceeds
            total_fees += fees
            if not compact:
                trades.append(
                    TradeEvent(
                        bar.market_date,
                        side,
                        "sell",
                        position.quote.option_symbol,
                        position.quantity,
                        price,
                        proceeds - fees,
                        fees,
                        reason,
                    )
                )
            option_positions[side] = None
        return cash, stock_shares, total_fees, turnover

    @staticmethod
    def _select_contract(chain: list[OptionQuote], rule: OptionRule, stock_price: float) -> OptionQuote | None:
        eligible = [
            item
            for item in chain
            if item.ask > 0
            and item.open_interest >= rule.min_open_interest
            and item.spread_pct <= rule.max_spread_pct
            and not item.is_nonstandard
            and (rule.expiration_type != "monthly" or item.is_monthly)
        ]
        if not eligible:
            return None
        dated = date.fromisoformat(eligible[0].market_date)
        expiration = min(
            {item.expiration for item in eligible},
            key=lambda value: abs((date.fromisoformat(value) - dated).days - rule.target_dte),
        )
        eligible = [item for item in eligible if item.expiration == expiration]
        target_strike = rule.target_strike(stock_price)
        if target_strike is None:
            with_delta = [item for item in eligible if item.delta is not None]
            if with_delta:
                return min(with_delta, key=lambda item: abs(abs(item.delta or 0) - abs(rule.target_delta)))
            target_strike = stock_price
        return min(eligible, key=lambda item: abs(item.strike - target_strike))

    def _position_value(
        self,
        position: OptionPosition | None,
        bar: StockBar,
        warnings: list[str],
        warning_keys: set[str],
    ) -> float:
        if not position:
            return 0.0
        quote = self._quote_for_day(position, bar)
        if quote:
            position.last_quote = quote
            position.missing_sessions = 0
            return max(0.0, quote.bid) * CONTRACT_MULTIPLIER * position.quantity
        position.missing_sessions += 1
        if position.last_quote and position.missing_sessions <= 1:
            return max(0.0, position.last_quote.bid) * CONTRACT_MULTIPLIER * position.quantity
        self._warn(
            warnings,
            warning_keys,
            f"missing-series-{position.quote.option_symbol}",
            "An option was missing daily bids for more than one session. Its value was reduced to intrinsic value, "
            "so the equity curve is conservative and marked as degraded.",
        )
        return position.quote.intrinsic_value(bar.close) * CONTRACT_MULTIPLIER * position.quantity

    @staticmethod
    def _quote_for_day(position: OptionPosition, bar: StockBar) -> OptionQuote | None:
        return position.series.get(bar.market_date)

    @staticmethod
    def _dividend_per_share(previous: StockBar, current: StockBar) -> float:
        if previous.close <= 0 or previous.adjusted_close <= 0:
            return 0.0
        raw_return = current.close / previous.close
        adjusted_return = current.adjusted_close / previous.adjusted_close
        return max(0.0, (adjusted_return - raw_return) * previous.close)

    @staticmethod
    def _metrics(
        strategy: StrategyDefinition,
        equity: list[dict[str, Any]],
        benchmark_final: float,
        total_fees: float,
        turnover: float,
        roll_count: int,
    ) -> dict[str, Any]:
        values = [float(item["value"]) for item in equity]
        returns = [values[index] / values[index - 1] - 1 for index in range(1, len(values)) if values[index - 1] > 0]
        ending = values[-1]
        total_return = ending / strategy.initial_capital - 1
        days = max(1, (date.fromisoformat(equity[-1]["date"]) - date.fromisoformat(equity[0]["date"])).days)
        annualized = (ending / strategy.initial_capital) ** (365 / days) - 1 if ending > 0 else -1.0
        volatility = statistics.stdev(returns) * math.sqrt(252) if len(returns) > 1 else 0.0
        daily_rf = strategy.risk_free_rate / 252
        excess = [item - daily_rf for item in returns]
        sharpe = (statistics.mean(excess) / statistics.stdev(excess) * math.sqrt(252)) if len(excess) > 1 and statistics.stdev(excess) else 0.0
        peak = values[0]
        max_drawdown = 0.0
        for value in values:
            peak = max(peak, value)
            max_drawdown = min(max_drawdown, value / peak - 1 if peak else 0)
        average_cash = statistics.mean(float(item["cash"]) for item in equity)
        return {
            "endingValue": round(ending, 2),
            "gainLoss": round(ending - strategy.initial_capital, 2),
            "totalReturnPct": round(total_return * 100, 3),
            "annualizedReturnPct": round(annualized * 100, 3),
            "maxDrawdownPct": round(max_drawdown * 100, 3),
            "annualizedVolatilityPct": round(volatility * 100, 3),
            "sharpeRatio": round(sharpe, 3),
            "fees": round(total_fees, 2),
            "turnover": round(turnover, 2),
            "cashDragPct": round(average_cash / strategy.initial_capital * 100, 3),
            "rollCount": roll_count,
            "benchmarkEndingValue": round(benchmark_final, 2),
            "benchmarkReturnPct": round((benchmark_final / strategy.initial_capital - 1) * 100, 3),
            "versusBenchmark": round(ending - benchmark_final, 2),
            "tradingSessions": len(values),
        }

    @staticmethod
    def _explain(strategy: StrategyDefinition, result: dict[str, Any]) -> list[str]:
        metrics = result["metrics"]
        direction = "grew" if metrics["gainLoss"] >= 0 else "fell"
        comparison = "finished above" if metrics["versusBenchmark"] >= 0 else "finished below"
        explanations = [
            f"The ${strategy.initial_capital:,.0f} test {direction} to ${metrics['endingValue']:,.0f}.",
            f"It {comparison} simply owning {strategy.ticker.upper()} by ${abs(metrics['versusBenchmark']):,.0f}.",
            f"Its largest peak-to-trough decline was {abs(metrics['maxDrawdownPct']):.1f}%.",
        ]
        attribution = result["attribution"]
        leader = max(attribution, key=attribution.get)
        laggard = min(attribution, key=attribution.get)
        explanations.append(
            f"The {leader} leg contributed the most ({attribution[leader]:+,.0f}), while the {laggard} leg contributed the least ({attribution[laggard]:+,.0f})."
        )
        if result["warnings"]:
            explanations.append("Some requested exposure could not be reproduced exactly; review the warnings before relying on the comparison.")
        return explanations

    @staticmethod
    def _warn(warnings: list[str], keys: set[str], key: str, message: str) -> None:
        if key not in keys:
            keys.add(key)
            warnings.append(message)


def allocation_grid(step: int = 10) -> list[tuple[int, int, int]]:
    if step <= 0 or 100 % step:
        raise ValueError("Allocation step must divide 100 evenly")
    output: list[tuple[int, int, int]] = []
    for stock in range(0, 101, step):
        for call in range(0, 101 - stock, step):
            put = 100 - stock - call
            output.append((stock, call, put))
    return output
