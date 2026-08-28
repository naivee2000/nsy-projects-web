from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date
import hashlib
import json
import math
import ssl
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi

from .calendar import is_us_trading_day
from .models import OptionRule
from .providers import ProviderError
from .unified import HybridMarketProvider, InstrumentHolding, run_unified_backtest


class OnclickBacktestProvider:
    """Experimental adapter for OnclickMedia's free derived backtest API.

    This source returns backtest rows rather than redistributable raw chains, so
    it intentionally remains separate from the app's audited Market Data engine.
    """

    name = "onclick-experimental"
    base_url = "https://backtest.onclickmedia.com/"

    def __init__(
        self,
        stock_provider: Any,
        timeout: int = 60,
        strict_quality: bool = False,
        quote_provider: Any | None = None,
        verified_engine: bool = False,
    ):
        self.stock_provider = stock_provider
        self.timeout = timeout
        self.strict_quality = strict_quality
        self.quote_provider = quote_provider
        self.verified_engine = verified_engine
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._availability_cache: dict[str, list[str]] = {}
        self._result_cache: dict[str, list[dict[str, Any]]] = {}

    def availability(self, symbol: str) -> list[str]:
        symbol = symbol.upper()
        if symbol not in self._availability_cache:
            payload = self._request_json(
                "GET",
                f"{self.base_url}?{urlencode({'ticker': symbol, 'list': 'date'})}",
            )
            if not isinstance(payload, list):
                raise ProviderError("The experimental options archive returned an invalid availability response")
            self._availability_cache[symbol] = sorted(
                {
                    str(value)[:10]
                    for value in payload
                    if isinstance(value, str) and len(value) >= 10
                }
            )
        return list(self._availability_cache[symbol])

    def run_portfolio_backtest(
        self,
        holdings: list[InstrumentHolding],
        start: str,
        end: str,
        initial_capital: float,
        rebalance: str,
        call_rule: OptionRule,
        put_rule: OptionRule,
        option_rules: dict[str, OptionRule] | None = None,
        cash_weight: float = 0,
        option_commission: float = 0.04,
    ) -> dict[str, Any]:
        options = [item for item in holdings if item.kind != "stock" and item.weight > 0]
        stocks = [item for item in holdings if item.kind == "stock" and item.weight > 0]
        if not options:
            raise ValueError("Experimental long-history options needs at least one positive call or put row")
        if rebalance != "none":
            raise ValueError(
                "Choose Never — buy and hold for experimental long-history options. "
                "The option will still be replaced at its roll threshold."
            )

        rules = {
            item.key: (option_rules or {}).get(
                item.key,
                call_rule if item.kind == "call" else put_rule,
            )
            for item in options
        }
        if not self.verified_engine:
            unsupported = [
                item.label
                for item in options
                if rules[item.key].strike_mode in {"dollar_below", "dollar_above", "delta"}
            ]
            if unsupported:
                raise ValueError(
                    f"Experimental long-history options cannot calculate the strike rule for {', '.join(unsupported)}. "
                    "Use at-the-money or percentage-based strikes, or choose another price source for fixed-dollar or delta rules."
                )

        def run_sleeve(item: InstrumentHolding) -> tuple[str, dict[str, Any]]:
            sleeve_capital = initial_capital * item.weight / 100
            return item.key, self._run_option_sleeve(
                item,
                rules[item.key],
                start,
                end,
                sleeve_capital,
                option_commission,
            )

        with ThreadPoolExecutor(
            max_workers=min(4, len(options)),
            thread_name_prefix="onclick-sleeve",
        ) as executor:
            sleeves = dict(executor.map(run_sleeve, options))

        stock_symbols = list(dict.fromkeys([item.symbol.upper() for item in stocks] + ["SPY", "QQQ"]))

        def load_stock(symbol: str) -> tuple[str, dict[str, float]]:
            bars = self.stock_provider.stock_bars(symbol, start, end)
            return symbol, {
                bar.market_date: float(bar.adjusted_close or bar.close)
                for bar in bars
                if (bar.adjusted_close or bar.close) > 0
            }

        with ThreadPoolExecutor(
            max_workers=min(4, len(stock_symbols)),
            thread_name_prefix="onclick-stock",
        ) as executor:
            stock_histories = dict(executor.map(load_stock, stock_symbols))
        missing_stocks = [symbol for symbol, values in stock_histories.items() if len(values) < 2]
        if missing_stocks:
            raise ProviderError(
                f"Tiingo did not return enough share history for {', '.join(missing_stocks)} in this period"
            )

        date_sets = [set(item["values"]) for item in sleeves.values()]
        date_sets.extend(set(values) for values in stock_histories.values())
        common_dates = sorted(set.intersection(*date_sets))
        if len(common_dates) < 2:
            raise ProviderError(
                "The experimental option sleeves, selected shares, and Tiingo benchmarks do not share enough dates"
            )
        actual_start, actual_end = common_dates[0], common_dates[-1]
        benchmark_units = {
            symbol: initial_capital / stock_histories[symbol][actual_start]
            for symbol in ("SPY", "QQQ")
        }
        stock_units = {
            item.key: (initial_capital * item.weight / 100) / stock_histories[item.symbol.upper()][actual_start]
            for item in stocks
        }
        explicit_cash = initial_capital * cash_weight / 100
        timeline = [
            {
                "date": market_date,
                "strategy": round(
                    explicit_cash
                    + sum(
                        stock_units[item.key] * stock_histories[item.symbol.upper()][market_date]
                        for item in stocks
                    )
                    + sum(sleeves[item.key]["values"][market_date] for item in options),
                    2,
                ),
                "spy": round(benchmark_units["SPY"] * stock_histories["SPY"][market_date], 2),
                "qqq": round(benchmark_units["QQQ"] * stock_histories["QQQ"][market_date], 2),
            }
            for market_date in common_dates
        ]
        metrics = {
            key: _metrics([float(point[key]) for point in timeline], actual_start, actual_end, initial_capital)
            for key in ("strategy", "spy", "qqq")
        }
        ending_total = float(timeline[-1]["strategy"])
        breakdown = [
            _breakdown(
                item.label,
                item.kind,
                item.weight,
                stock_units[item.key] * stock_histories[item.symbol.upper()][actual_end],
                ending_total,
            )
            for item in stocks
        ]
        breakdown.extend(
            _breakdown(
                item.label,
                item.kind,
                item.weight,
                sleeves[item.key]["values"][actual_end],
                ending_total,
            )
            for item in options
        )
        if cash_weight > 0:
            breakdown.append(_breakdown("Cash", "cash", cash_weight, explicit_cash, ending_total))
        fees = sum(float(item["fees"]) for item in sleeves.values())
        replacement_count = sum(
            max(0, int(item["openingCount"]) - 1)
            for item in sleeves.values()
        )
        row_errors = sum(
            int(item["quality"]["tradingErrorRows"]) if self.strict_quality else len(item["errors"])
            for item in sleeves.values()
        )
        checked_rows = sum(int(item["quality"]["checkedTradingRows"]) for item in sleeves.values())
        repriced_contracts = sum(int(item["quality"]["repricedContracts"]) for item in sleeves.values())
        repriced_quotes = sum(int(item["quality"]["repricedQuotes"]) for item in sleeves.values())
        selection_miss_rows = sum(int(item["quality"]["selectionMissRows"]) for item in sleeves.values())
        contract_audit = [
            {"holding": item.label, **audit}
            for item in options
            for audit in sleeves[item.key]["quality"]["contractAudit"]
        ]
        chain_audit = [
            {"holding": item.label, **audit}
            for item in options
            for audit in sleeves[item.key]["quality"].get("chainAudit", [])
        ]
        source_warnings = [
            (
                "Verified beta calculation: the app selected every option contract and roll locally from Market Data "
                "historical chains, then used Market Data asks for purchases and bids for values and sales. "
                "Missing required quote evidence rejects the run."
            ),
            (
                "No OnclickMedia contract schedule, option price, or portfolio total was used in this result. "
                "Tiingo supplied adjusted share and benchmark history."
            ),
        ] if self.verified_engine else [
            "Experimental source: this result was calculated by OnclickMedia's external beta engine, not the app's "
            "audited local option simulator. Use it for rough screening, then verify important findings with a paid source.",
            "OnclickMedia says its historical options archive aggregates public sources, including Yahoo Finance and "
            "community channels, and may contain gaps or inconsistencies.",
        ]
        warnings = source_warnings + [
            "Each option row was calculated as an independently funded sleeve and then combined with the selected "
            "share and cash sleeves into the single strategy line. Money is not moved between sleeves after the start.",
        ]
        if not self.verified_engine:
            warnings.append(
                "The experimental engine selects each option row's nearest strike using that row's at-the-money or "
                "percentage rule. Delta, open-interest, monthly-expiration, and bid/ask-spread filters in Advanced "
                "settings are not applied."
            )
        for item in options:
            for warning in sleeves[item.key].get("warnings") or []:
                warnings.append(f"{item.label}: {warning}")
        for item in options:
            rule = rules[item.key]
            replacement_days = sleeves[item.key]["externalRebalanceDays"]
            if self.verified_engine:
                warnings.append(
                    f"{item.label} targets approximately {rule.target_dte} days until expiration and is replaced when "
                    f"{rule.roll_dte} or fewer calendar days remain."
                )
            elif replacement_days is not None:
                warnings.append(
                    f"For {item.label}, replacing near {rule.roll_dte} days remaining is approximated by a "
                    f"{replacement_days}-calendar-day replacement interval "
                    f"({rule.target_dte} target DTE minus {rule.roll_dte} roll DTE)."
                )
            else:
                warnings.append(
                    f"{item.label} has a zero-day replacement threshold, so the experimental sleeve "
                    "holds each option until expiration before purchasing the next one."
                )
        if actual_start > start or actual_end < end:
            warnings.append(
                f"The requested {start} to {end} period was limited to {actual_start} to {actual_end}, "
                "where every option sleeve, selected share, and Tiingo benchmark overlaps."
            )
        if row_errors:
            warnings.append(
                f"The external engine reported {row_errors} row-level warning"
                f"{'s' if row_errors != 1 else ''}. Those rows still contained finite portfolio values and remain "
                "on the chart, but the affected option sleeve may have been temporarily unable to open a replacement contract."
            )
        if selection_miss_rows:
            warnings.append(
                f"No qualifying contract was available on {selection_miss_rows} trading session"
                f"{'s' if selection_miss_rows != 1 else ''}. Those sleeves remained in cash on those dates; "
                "no unverified option value was inserted."
            )
        return {
            "provider": self.name,
            "requestedStartDate": start,
            "requestedEndDate": end,
            "startDate": actual_start,
            "endDate": actual_end,
            "initialCapital": initial_capital,
            "rebalance": rebalance,
            "rebalanceCount": replacement_count,
            "holdings": [
                {"symbol": item.symbol.upper(), "kind": item.kind, "weight": item.weight}
                for item in holdings
            ],
            "cashWeight": cash_weight,
            "optionCount": len(options),
            "optionRetryCount": 0,
            "optionRules": {
                item.key: {
                    "side": item.kind,
                    "targetDte": rules[item.key].target_dte,
                    "rollDte": rules[item.key].roll_dte,
                    "externalRebalanceDays": sleeves[item.key]["externalRebalanceDays"],
                    "strikeMode": rules[item.key].strike_mode,
                    "strikeValue": rules[item.key].strike_value,
                    "externalPercentItm": sleeves[item.key]["externalPercentItm"],
                }
                for item in options
            },
            "fees": round(fees, 2),
            "dataQuality": {
                "status": (
                    "verified-independent-sleeves"
                    if self.verified_engine
                    else "verified-reference-priced"
                    if self.quote_provider is not None
                    else ("strict-integrity-checked" if self.strict_quality else "experimental")
                ),
                "checkedTradingRows": checked_rows,
                "externalErrorRows": row_errors,
                "selectionMissRows": selection_miss_rows,
                "checks": [
                    "locally selected historical contract chains",
                    "observed bid and ask for every held trading session",
                    "ask-priced purchases and bid-priced values and sales",
                    "whole 100-share contracts",
                    "SHA-256 checksums for chain and contract evidence",
                ],
                "independentlyRepriced": self.quote_provider is not None,
                "locallySelectedContracts": self.verified_engine,
                "referenceProvider": getattr(self.quote_provider, "name", None),
                "repricedContracts": repriced_contracts,
                "repricedQuotes": repriced_quotes,
                "contractAudit": contract_audit,
                "chainAudit": chain_audit,
            },
            "coverage": (
                [
                    {
                        "symbol": item.symbol.upper(),
                        "kind": item.kind,
                        "startDate": sleeves[item.key]["start"],
                        "endDate": sleeves[item.key]["end"],
                    }
                    for item in options
                ]
                + [
                    {
                        "symbol": symbol,
                        "kind": "stock",
                        "startDate": min(stock_histories[symbol]),
                        "endDate": max(stock_histories[symbol]),
                    }
                    for symbol in stock_symbols
                ]
            ),
            "timeline": timeline,
            "metrics": metrics,
            "breakdown": breakdown,
            "summary": _summary(metrics, fees, self.verified_engine),
            "warnings": warnings,
            "assumptions": [
                "Every option row begins with its requested percentage of the starting money and is run independently. "
                "Its value includes any cash that its whole-contract purchases could not invest.",
                "The combined strategy is buy-and-hold between sleeves. Option replacement occurs inside each option sleeve, "
                "but the app does not transfer gains or losses between SPY, QQQ, calls, puts, shares, or cash.",
                (
                    "Market Data historical end-of-day asks determine option purchases and bids determine daily values "
                    "and sales; option quantities are whole 100-share contracts."
                    if self.quote_provider is not None
                    else "The external engine uses historical end-of-day option bids and asks and whole 100-share contracts."
                ),
                f"Estimated Robinhood stock/ETF option fees are ${option_commission:.2f} per contract per side.",
                "Selected shares and the SPY and QQQ comparisons use adjusted Tiingo daily closes over shared usable dates.",
                (
                    "Cash earns no interest. Verified beta is an independent-sleeve model; all contract selection and "
                    "pricing are calculated locally, and missing required quote evidence stops the run."
                    if self.verified_engine
                    else "Cash earns no interest. The contract schedule remains a beta model even though all prices are "
                    "independently sourced and missing evidence stops the run."
                    if self.quote_provider is not None
                    else "Cash earns no interest. The experimental source is free, unaudited, and unsuitable for live trading decisions."
                ),
            ],
        }

    def _run_option_sleeve(
        self,
        option: InstrumentHolding,
        rule: OptionRule,
        start: str,
        end: str,
        sleeve_capital: float,
        option_commission: float,
    ) -> dict[str, Any]:
        if self.verified_engine:
            return self._run_verified_option_sleeve(
                option,
                rule,
                start,
                end,
                sleeve_capital,
                option_commission,
            )
        available = self.availability(option.symbol)
        usable_dates = [value for value in available if start <= value <= end]
        if len(usable_dates) < 2:
            first = available[0] if available else "unknown"
            last = available[-1] if available else "unknown"
            raise ProviderError(
                f"The experimental archive has no usable {option.label} period inside {start} to {end}. "
                f"Its reported availability is {first} to {last}."
            )
        option_start, option_end = usable_dates[0], usable_dates[-1]
        percent_itm = 0.0
        if rule.strike_mode == "percent_below":
            percent_itm = rule.strike_value if option.kind == "call" else -rule.strike_value
        elif rule.strike_mode == "percent_above":
            percent_itm = -rule.strike_value if option.kind == "call" else rule.strike_value
        external_rebalance_days = (
            rule.target_dte - rule.roll_dte
            if rule.roll_dte > 0
            else None
        )
        payload: dict[str, Any] = {
            "ticker": option.symbol.upper(),
            "portfolio_start": sleeve_capital,
            "start_date": option_start,
            "end_date": option_end,
            "real": True,
            "percent_per_trade": 1,
            "max_invested": 1,
            "distribution": "equal_amount",
            "legs": [
                {
                    "ticker": option.symbol.upper(),
                    "type": option.kind,
                    "direction": "long",
                    "percent_itm": percent_itm / 100,
                    "days_till_expiration": rule.target_dte,
                    "rebalance_period": external_rebalance_days,
                    "fee_per_trade": 0,
                    "fee_per_contract": option_commission,
                    "prime": True,
                    "stop_loss": None,
                    "stop_profit": None,
                    "stop_at_midpoint": False,
                }
            ],
            "stock": None,
        }
        cache_key = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        if cache_key not in self._result_cache:
            response = self._request_json(
                "POST",
                f"{self.base_url}?data=all&output=json",
                payload,
            )
            if not isinstance(response, list):
                raise ProviderError("The experimental options archive returned an invalid backtest response")
            self._result_cache[cache_key] = [dict(item) for item in response if isinstance(item, dict)]
        rows = self._result_cache[cache_key]
        errors = [str(item.get("error") or "").strip() for item in rows if str(item.get("error") or "").strip()]
        usable_rows = [
            item
            for item in rows
            if _finite_number(item.get("total_value"))
            and isinstance(item.get("date"), str)
        ]
        quality: dict[str, Any] = self._validate_row_quality(option, usable_rows) if self.strict_quality else {
            "checkedTradingRows": 0,
            "tradingErrorRows": 0,
            "selectionMissRows": 0,
        }
        if self.quote_provider is not None:
            repriced = self._reprice_with_reference(
                option,
                usable_rows,
                sleeve_capital,
                option_commission,
            )
            values = repriced["values"]
            fees = repriced["fees"]
            opening_count = repriced["openingCount"]
            quality.update(
                {
                    "repricedContracts": repriced["contractCount"],
                    "repricedQuotes": repriced["quoteCount"],
                    "contractAudit": repriced["contractAudit"],
                }
            )
        else:
            values = {str(item["date"])[:10]: float(item["total_value"]) for item in usable_rows}
            final_row = max(usable_rows, key=lambda item: str(item["date"])[:10])
            fees = float(final_row.get("total_fees") or 0)
            opening_count = sum(
                bool(str(item.get("leg1_open_transact") or "").strip())
                for item in usable_rows
            )
            quality.update({"repricedContracts": 0, "repricedQuotes": 0, "contractAudit": []})
        if len(values) < 2:
            detail = errors[0] if errors else "no usable portfolio rows"
            raise ProviderError(f"The experimental archive could not complete {option.label}: {detail}")
        return {
            "values": values,
            "start": min(values),
            "end": max(values),
            "fees": fees,
            "openingCount": opening_count,
            "errors": errors,
            "quality": quality,
            "externalRebalanceDays": external_rebalance_days,
            "externalPercentItm": percent_itm,
        }

    def _run_verified_option_sleeve(
        self,
        option: InstrumentHolding,
        rule: OptionRule,
        start: str,
        end: str,
        sleeve_capital: float,
        option_commission: float,
    ) -> dict[str, Any]:
        contract_quotes: dict[str, dict[str, Any]] = {}
        contract_open_dates: dict[str, str] = {}
        chain_audit: list[dict[str, Any]] = []

        class AuditedHybridProvider(HybridMarketProvider):
            def option_chain(inner_self, symbol: str, market_date: str, selected_rule: OptionRule):  # type: ignore[no-untyped-def]
                chain = super(AuditedHybridProvider, inner_self).option_chain(
                    symbol,
                    market_date,
                    selected_rule,
                )
                checksum_payload = [
                    [
                        quote.option_symbol,
                        quote.expiration,
                        round(float(quote.strike), 8),
                        round(float(quote.bid), 8),
                        round(float(quote.ask), 8),
                        int(quote.open_interest),
                    ]
                    for quote in sorted(chain, key=lambda value: value.option_symbol)
                ]
                chain_audit.append(
                    {
                        "symbol": symbol.upper(),
                        "marketDate": market_date,
                        "contracts": len(chain),
                        "sha256": hashlib.sha256(
                            json.dumps(checksum_payload, separators=(",", ":")).encode("utf-8")
                        ).hexdigest(),
                    }
                )
                return chain

            def option_quote_series(inner_self, option_symbol: str, series_start: str, series_end: str):  # type: ignore[no-untyped-def]
                quotes = super(AuditedHybridProvider, inner_self).option_quote_series(
                    option_symbol,
                    series_start,
                    series_end,
                )
                contract_open_dates.setdefault(option_symbol, series_start)
                contract_quotes.setdefault(option_symbol, {}).update(
                    {quote.market_date: quote for quote in quotes}
                )
                return quotes

        audited_provider = AuditedHybridProvider(self.stock_provider, self.quote_provider)
        call_rule = rule if option.kind == "call" else OptionRule("call", 540, 180)
        put_rule = rule if option.kind == "put" else OptionRule("put", 45, 21)
        result = run_unified_backtest(
            audited_provider,
            holdings=[InstrumentHolding(option.symbol, option.kind, 100)],
            start=start,
            end=end,
            initial_capital=sleeve_capital,
            rebalance="none",
            call_rule=call_rule,
            put_rule=put_rule,
            option_rules={option.key: rule},
            cash_weight=0,
            option_commission=option_commission,
        )
        unreliable_warnings = [
            warning
            for warning in result.get("warnings") or []
            if any(
                phrase in warning.lower()
                for phrase in (
                    "missing daily",
                    "prior session's bid",
                    "no usable bid",
                    "intrinsic value",
                    "no bid on a rebalance",
                )
            )
        ]
        if unreliable_warnings:
            raise ProviderError(
                f"Verified beta rejected {option.label}: {unreliable_warnings[0]} "
                "A reliable result requires an observed Market Data quote for every valuation and transaction."
            )

        timeline_dates = [str(item["date"]) for item in result["timeline"]]
        for option_symbol, open_date in contract_open_dates.items():
            quotes_by_date = contract_quotes.get(option_symbol, {})
            if not quotes_by_date:
                raise ProviderError(
                    f"Verified beta rejected {option.label}: Market Data returned no quote history for {option_symbol}."
                )
            opening_quote = min(quotes_by_date.values(), key=lambda value: value.market_date)
            roll_date = next(
                (
                    market_date
                    for market_date in timeline_dates
                    if market_date >= open_date
                    and (
                        date.fromisoformat(opening_quote.expiration) - date.fromisoformat(market_date)
                    ).days <= rule.roll_dte
                ),
                None,
            )
            required_end = roll_date or min(end, opening_quote.expiration)
            required_dates = [
                market_date
                for market_date in timeline_dates
                if open_date <= market_date <= required_end
                and market_date < opening_quote.expiration
            ]
            missing_dates = [
                market_date
                for market_date in required_dates
                if market_date not in quotes_by_date
                or float(quotes_by_date[market_date].bid) <= 0
                or float(quotes_by_date[market_date].ask) <= 0
            ]
            if missing_dates:
                raise ProviderError(
                    f"Verified beta rejected {option.label}: Market Data had no complete bid/ask quote for "
                    f"{option_symbol} on {missing_dates[0]}. A verified result never carries or invents that value."
                )

        contract_audit: list[dict[str, Any]] = []
        for option_symbol, by_date in sorted(contract_quotes.items()):
            quotes = sorted(by_date.values(), key=lambda value: value.market_date)
            checksum_payload = [
                [
                    quote.market_date,
                    round(float(quote.bid), 8),
                    round(float(quote.ask), 8),
                    round(float(quote.last), 8),
                ]
                for quote in quotes
            ]
            contract_audit.append(
                {
                    "optionSymbol": option_symbol,
                    "startDate": quotes[0].market_date,
                    "endDate": quotes[-1].market_date,
                    "referenceQuotes": len(quotes),
                    "sha256": hashlib.sha256(
                        json.dumps(checksum_payload, separators=(",", ":")).encode("utf-8")
                    ).hexdigest(),
                }
            )
        values = {
            str(item["date"]): float(item["strategy"])
            for item in result["timeline"]
        }
        selection_misses = [
            warning
            for warning in result.get("warnings") or []
            if "remained in cash" in warning.lower() or "could not buy one whole contract" in warning.lower()
        ]
        return {
            "values": values,
            "start": result["startDate"],
            "end": result["endDate"],
            "fees": float(result["fees"]),
            "openingCount": max(1, int(result["rebalanceCount"]) + 1),
            "errors": [],
            "warnings": list(result.get("warnings") or []),
            "quality": {
                "checkedTradingRows": len(values),
                "tradingErrorRows": 0,
                "selectionMissRows": len(selection_misses),
                "repricedContracts": len(contract_audit),
                "repricedQuotes": sum(item["referenceQuotes"] for item in contract_audit),
                "contractAudit": contract_audit,
                "chainAudit": chain_audit,
            },
            "externalRebalanceDays": None,
            "externalPercentItm": None,
        }

    @staticmethod
    def _validate_row_quality(option: InstrumentHolding, rows: list[dict[str, Any]]) -> dict[str, int]:
        trading_rows = [
            item
            for item in rows
            if _is_trading_date(str(item.get("date") or "")[:10])
        ]
        fatal_error_rows: list[tuple[str, str]] = []
        selection_miss_rows: list[str] = []
        for item in trading_rows:
            code = str(item.get("error") or "").strip()
            if not code:
                continue
            market_date = str(item.get("date") or "")[:10]
            empty_e2 = (
                code == "E2"
                and (_number_or_none(item.get("leg1_value")) or 0) == 0
                and (_number_or_none(item.get("leg1_contracts")) or 0) == 0
                and (_number_or_none(item.get("leg1_bid")) or 0) == 0
                and (_number_or_none(item.get("leg1_ask")) or 0) == 0
                and not str(item.get("leg1_expiry") or "").strip()
            )
            if empty_e2:
                selection_miss_rows.append(market_date)
            else:
                fatal_error_rows.append((market_date, code))
        if fatal_error_rows:
            codes = sorted({code for _, code in fatal_error_rows})
            preview = ", ".join(day for day, _ in fatal_error_rows[:3])
            raise ProviderError(
                f"Verified beta rejected {option.label}: the external source reported "
                f"{', '.join(codes)} on {len(fatal_error_rows)} trading session"
                f"{'s' if len(fatal_error_rows) != 1 else ''}, including {preview}. "
                "Those rows cannot be treated as reliable market history."
            )

        issues: list[str] = []
        for item in trading_rows:
            market_date = str(item.get("date") or "")[:10]
            cash = _number_or_none(item.get("cash"))
            option_value = _number_or_none(item.get("leg1_value"))
            total = _number_or_none(item.get("total_value"))
            if cash is not None and option_value is not None and total is not None:
                tolerance = max(0.02, abs(total) * 1e-8)
                if abs(cash + option_value - total) > tolerance:
                    issues.append(f"{market_date} portfolio total did not reconcile")

            bid = _number_or_none(item.get("leg1_bid"))
            ask = _number_or_none(item.get("leg1_ask"))
            if bid is None and ask is None:
                continue
            if bid is None or ask is None:
                issues.append(f"{market_date} had only one side of the option quote")
                continue
            if bid < 0 or ask < 0:
                issues.append(f"{market_date} had a negative option quote")
            elif bid > ask:
                issues.append(f"{market_date} had a bid above its ask")

        if issues:
            raise ProviderError(
                f"Verified beta rejected {option.label}: {issues[0]}. "
                f"{len(issues)} inconsistent trading row{'s were' if len(issues) != 1 else ' was'} found."
            )
        return {
            "checkedTradingRows": len(trading_rows),
            "tradingErrorRows": 0,
            "selectionMissRows": len(selection_miss_rows),
        }

    def _reprice_with_reference(
        self,
        option: InstrumentHolding,
        rows: list[dict[str, Any]],
        sleeve_capital: float,
        option_commission: float,
    ) -> dict[str, Any]:
        trading_rows = sorted(
            (
                item
                for item in rows
                if _is_trading_date(str(item.get("date") or "")[:10])
            ),
            key=lambda item: str(item.get("date") or "")[:10],
        )
        contract_dates: dict[str, list[str]] = {}
        previous_contract: str | None = None
        for item in trading_rows:
            market_date = str(item["date"])[:10]
            contract = _contract_symbol(option, item)
            if contract:
                contract_dates.setdefault(contract, []).append(market_date)
            if previous_contract and (
                bool(str(item.get("leg1_close_transact") or "").strip())
                or (contract and contract != previous_contract)
            ):
                contract_dates.setdefault(previous_contract, []).append(market_date)
            if bool(str(item.get("leg1_open_transact") or "").strip()):
                previous_contract = contract
        if not contract_dates:
            raise ProviderError(
                f"Verified beta rejected {option.label}: the external source did not identify any option contracts."
            )

        reference: dict[str, dict[str, Any]] = {}
        contract_audit: list[dict[str, Any]] = []
        for contract, dates in contract_dates.items():
            try:
                series = self.quote_provider.option_quote_series(contract, min(dates), max(dates))
            except Exception as exc:
                raise ProviderError(
                    f"Verified beta could not independently price {option.label} contract {contract}: {exc}"
                ) from exc
            scoped = [
                quote
                for quote in series
                if min(dates) <= quote.market_date <= max(dates)
            ]
            reference[contract] = {quote.market_date: quote for quote in scoped}
            checksum_payload = [
                [
                    quote.market_date,
                    round(float(quote.bid), 8),
                    round(float(quote.ask), 8),
                    round(float(quote.last), 8),
                ]
                for quote in sorted(scoped, key=lambda value: value.market_date)
            ]
            contract_audit.append(
                {
                    "optionSymbol": contract,
                    "startDate": min(dates),
                    "endDate": max(dates),
                    "referenceQuotes": len(scoped),
                    "sha256": hashlib.sha256(
                        json.dumps(checksum_payload, separators=(",", ":")).encode("utf-8")
                    ).hexdigest(),
                }
            )

        cash = float(sleeve_capital)
        held_contract: str | None = None
        held_quantity = 0
        selected_contract: str | None = None
        fees = 0.0
        opening_count = 0
        quote_count = 0
        values: dict[str, float] = {}
        for item in trading_rows:
            market_date = str(item["date"])[:10]
            contract = _contract_symbol(option, item)
            close_event = bool(str(item.get("leg1_close_transact") or "").strip())
            open_event = bool(str(item.get("leg1_open_transact") or "").strip())

            if held_contract and (close_event or (contract and contract != selected_contract)):
                quote = reference.get(held_contract, {}).get(market_date)
                if quote is None:
                    raise ProviderError(
                        f"Verified beta rejected {option.label}: Market Data had no closing quote "
                        f"for {held_contract} on {market_date}."
                    )
                cash += max(0.0, float(quote.bid)) * 100 * held_quantity
                close_fee = option_commission * held_quantity
                cash -= close_fee
                fees += close_fee
                quote_count += 1
                held_contract = None
                held_quantity = 0

            if open_event:
                opening_count += 1
                selected_contract = contract
                if not contract:
                    raise ProviderError(
                        f"Verified beta rejected {option.label}: an opening on {market_date} "
                        "did not include a valid strike and expiration."
                    )
                quote = reference.get(contract, {}).get(market_date)
                if quote is None or float(quote.ask) <= 0:
                    raise ProviderError(
                        f"Verified beta rejected {option.label}: Market Data had no usable opening ask "
                        f"for {contract} on {market_date}."
                    )
                unit_cost = float(quote.ask) * 100 + option_commission
                quantity = math.floor(cash / unit_cost)
                quote_count += 1
                if quantity > 0:
                    open_fee = option_commission * quantity
                    cash -= float(quote.ask) * 100 * quantity + open_fee
                    fees += open_fee
                    held_contract = contract
                    held_quantity = quantity

            if held_contract:
                quote = reference.get(held_contract, {}).get(market_date)
                if quote is None:
                    raise ProviderError(
                        f"Verified beta rejected {option.label}: Market Data had no valuation quote "
                        f"for {held_contract} on {market_date}."
                    )
                option_value = max(0.0, float(quote.bid)) * 100 * held_quantity
                quote_count += 1
            else:
                option_value = 0.0
            values[market_date] = round(cash + option_value, 4)

        return {
            "values": values,
            "fees": round(fees, 4),
            "openingCount": opening_count,
            "contractCount": len(reference),
            "quoteCount": quote_count,
            "contractAudit": contract_audit,
        }

    def _request_json(self, method: str, url: str, payload: dict[str, Any] | None = None) -> Any:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            url,
            data=body,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "NSY-Portfolio-Lab/1.0",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw)
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            raise ProviderError(f"The experimental options archive rejected the request ({exc.code}): {raw[:160]}") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProviderError(f"The experimental options archive could not be reached: {exc}") from exc


def _finite_number(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _number_or_none(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _is_trading_date(value: str) -> bool:
    try:
        return is_us_trading_day(date.fromisoformat(value))
    except ValueError:
        return False


def _contract_symbol(option: InstrumentHolding, row: dict[str, Any]) -> str | None:
    expiration = str(row.get("leg1_expiry") or "")[:10]
    strike = _number_or_none(row.get("leg1_strike"))
    try:
        expiry = date.fromisoformat(expiration)
    except ValueError:
        return None
    if strike is None or strike <= 0:
        return None
    side = "C" if option.kind == "call" else "P"
    root = option.symbol.upper()
    return f"{root}{expiry:%y%m%d}{side}{int(round(strike * 1000)):08d}"


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


def _breakdown(label: str, kind: str, target: float, value: float, ending_total: float) -> dict[str, Any]:
    return {
        "symbol": label,
        "targetWeight": target,
        "endingWeight": value / ending_total * 100 if ending_total else 0,
        "endingValue": value,
        "kind": kind,
    }


def _summary(metrics: dict[str, dict[str, float]], fees: float, verified: bool = False) -> str:
    strategy = metrics["strategy"]
    best = "QQQ" if metrics["qqq"]["endingValue"] >= metrics["spy"]["endingValue"] else "SPY"
    difference = strategy["endingValue"] - metrics[best.lower()]["endingValue"]
    strategy_label = "verified strategy" if verified else "experimental strategy"
    fee_source = "the local calculation included" if verified else "the external engine reported"
    return (
        f"The {strategy_label} finished at ${strategy['endingValue']:,.0f}, ${abs(difference):,.0f} "
        f"{'above' if difference >= 0 else 'below'} putting all starting money in {best}. "
        f"Its largest temporary decline was {abs(strategy['maxDrawdown']) * 100:.1f}%, "
        f"and {fee_source} ${fees:,.2f} in option fees."
    )
