from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Literal


OptionSide = Literal["call", "put"]
StrikeMode = Literal[
    "atm",
    "percent_below",
    "percent_above",
    "dollar_below",
    "dollar_above",
    "delta",
]
ROBINHOOD_OPTION_FEE_PER_CONTRACT = 0.04


def _iso(value: date | datetime | str) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


@dataclass(frozen=True)
class OptionRule:
    side: OptionSide
    target_dte: int = 45
    roll_dte: int = 21
    target_delta: float = 0.50
    fallback_moneyness_pct: float = 0.0
    expiration_type: str = "monthly"
    min_open_interest: int = 100
    max_spread_pct: float = 0.20
    strike_mode: StrikeMode = "atm"
    strike_value: float = 0.0

    def validate(self) -> None:
        if self.side not in {"call", "put"}:
            raise ValueError("Option side must be call or put")
        if not 1 <= self.target_dte <= 730:
            raise ValueError("Days until expiration must be between 1 and 730")
        if not 0 <= self.roll_dte < self.target_dte:
            raise ValueError("Roll days must be zero or more and below the target expiration days")
        if not 0.01 <= abs(self.target_delta) <= 0.99:
            raise ValueError("Option sensitivity must be between 0.01 and 0.99")
        if self.expiration_type not in {"monthly", "any"}:
            raise ValueError("Expiration type must be monthly or any")
        if self.min_open_interest < 0:
            raise ValueError("Minimum open interest cannot be negative")
        if not 0 <= self.max_spread_pct <= 5:
            raise ValueError("Maximum spread must be between 0% and 500%")
        if self.strike_mode not in {
            "atm",
            "percent_below",
            "percent_above",
            "dollar_below",
            "dollar_above",
            "delta",
        }:
            raise ValueError("Choose a valid strike-price rule")
        if self.strike_value < 0:
            raise ValueError("Strike distance cannot be negative")
        if self.strike_mode.startswith("percent_") and self.strike_value >= 100:
            raise ValueError("Strike percentage must be below 100%")
        if self.strike_mode.startswith("dollar_") and self.strike_value > 1_000_000:
            raise ValueError("Strike dollar distance must be $1,000,000 or less")

    def target_strike(self, stock_price: float) -> float | None:
        """Return an absolute target strike, or None when delta should decide."""
        if self.strike_mode == "delta":
            return None
        if self.strike_mode == "percent_below":
            return max(0.01, stock_price * (1 - self.strike_value / 100))
        if self.strike_mode == "percent_above":
            return stock_price * (1 + self.strike_value / 100)
        if self.strike_mode == "dollar_below":
            return max(0.01, stock_price - self.strike_value)
        if self.strike_mode == "dollar_above":
            return stock_price + self.strike_value
        return stock_price

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StrategyDefinition:
    ticker: str
    start_date: str
    end_date: str
    initial_capital: float = 100_000.0
    stock_pct: int = 60
    call_pct: int = 20
    put_pct: int = 20
    call_rule: OptionRule = field(default_factory=lambda: OptionRule("call"))
    put_rule: OptionRule = field(default_factory=lambda: OptionRule("put"))
    stock_slippage_bps: float = 5.0
    stock_commission: float = 0.0
    option_commission: float = ROBINHOOD_OPTION_FEE_PER_CONTRACT
    sweep_step_pct: int = 10
    risk_free_rate: float = 0.0
    name: str = "Untitled experiment"

    def validate(self) -> None:
        ticker = self.ticker.strip().upper()
        if not ticker or len(ticker) > 12 or not all(ch.isalnum() or ch in {".", "-"} for ch in ticker):
            raise ValueError("Enter a valid U.S. stock or ETF ticker")
        start = date.fromisoformat(self.start_date)
        end = date.fromisoformat(self.end_date)
        if start >= end:
            raise ValueError("The end date must be after the start date")
        if not 100 <= self.initial_capital <= 1_000_000_000:
            raise ValueError("Starting money must be between $100 and $1 billion")
        weights = (self.stock_pct, self.call_pct, self.put_pct)
        if any(weight < 0 or weight > 100 for weight in weights) or sum(weights) != 100:
            raise ValueError("Stock, call, and put percentages must add up to 100%")
        if self.sweep_step_pct not in {5, 10, 20, 25}:
            raise ValueError("Allocation step must be 5%, 10%, 20%, or 25%")
        if min(self.stock_slippage_bps, self.stock_commission, self.option_commission) < 0:
            raise ValueError("Trading costs cannot be negative")
        self.call_rule.validate()
        self.put_rule.validate()

    def with_weights(self, stock: int, call: int, put: int) -> "StrategyDefinition":
        payload = self.to_dict()
        payload.update({"stock_pct": stock, "call_pct": call, "put_pct": put})
        payload["call_rule"] = self.call_rule
        payload["put_rule"] = self.put_rule
        return StrategyDefinition(**payload)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["ticker"] = self.ticker.strip().upper()
        return payload

    def plain_summary(self) -> str:
        capital = f"${self.initial_capital:,.0f}"
        return (
            f"This test starts with {capital}: about {self.stock_pct}% in shares, "
            f"{self.call_pct}% in calls, and {self.put_pct}% in puts. "
            f"Options are replaced near {self.call_rule.roll_dte} days remaining and "
            "the target mix is restored at each replacement."
        )


@dataclass(frozen=True)
class StockBar:
    market_date: str
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float
    volume: float = 0.0
    split_detected: bool = False
    dividend_cash: float = 0.0
    split_factor: float = 1.0
    source_timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OptionQuote:
    market_date: str
    option_symbol: str
    underlying: str
    expiration: str
    side: OptionSide
    strike: float
    bid: float
    ask: float
    last: float = 0.0
    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None
    iv: float | None = None
    open_interest: int = 0
    volume: int = 0
    underlying_price: float = 0.0
    is_monthly: bool = True
    is_nonstandard: bool = False
    contract_multiplier: float = 100.0
    bid_size: int = 0
    ask_size: int = 0
    source_timestamp: str = ""
    pricing_source: str = "unknown"

    @property
    def midpoint(self) -> float:
        if self.bid > 0 and self.ask > 0:
            return (self.bid + self.ask) / 2
        return max(self.bid, self.ask, self.last, 0.0)

    @property
    def spread_pct(self) -> float:
        mid = self.midpoint
        return (self.ask - self.bid) / mid if mid > 0 and self.ask >= self.bid else float("inf")

    def intrinsic_value(self, stock_price: float) -> float:
        if self.side == "call":
            return max(0.0, stock_price - self.strike)
        return max(0.0, self.strike - stock_price)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FavoriteSymbol:
    symbol: str
    capture_profile: str = "balanced"
    active: bool = True
    estimated_daily_credits: int = 7


@dataclass(frozen=True)
class CaptureProfile:
    key: str
    label: str
    max_dte: int
    monthly_only: bool
    estimated_daily_credits: int


@dataclass(frozen=True)
class CoverageManifest:
    symbol: str
    state: str
    stock_start: str | None = None
    stock_end: str | None = None
    option_start: str | None = None
    option_end: str | None = None
    message: str = ""


@dataclass
class MarketTape:
    """Per-run cache shared by the selected mix and every sweep candidate."""

    stock: dict[tuple[str, str, str], list[StockBar]] = field(default_factory=dict)
    chains: dict[tuple[str, str, str], list[OptionQuote]] = field(default_factory=dict)
    series: dict[tuple[str, str, str], list[OptionQuote]] = field(default_factory=dict)


@dataclass
class TradeEvent:
    market_date: str
    leg: str
    action: str
    symbol: str
    quantity: int
    price: float
    cash_flow: float
    fees: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BacktestResult:
    run_id: str
    strategy: dict[str, Any]
    status: str
    summary: dict[str, Any]
    explanation: list[str]
    metrics: dict[str, Any]
    daily_equity: list[dict[str, Any]]
    benchmark_equity: list[dict[str, Any]]
    attribution: dict[str, float]
    trades: list[dict[str, Any]]
    warnings: list[str]
    audit: dict[str, Any]
    created_at: str
    sweep: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def strategy_from_dict(payload: dict[str, Any]) -> StrategyDefinition:
    call_payload = dict(payload.get("call_rule") or payload.get("callRule") or {})
    put_payload = dict(payload.get("put_rule") or payload.get("putRule") or {})
    call_payload["side"] = "call"
    put_payload["side"] = "put"
    aliases = {
        "startDate": "start_date",
        "endDate": "end_date",
        "initialCapital": "initial_capital",
        "stockPct": "stock_pct",
        "callPct": "call_pct",
        "putPct": "put_pct",
        "stockSlippageBps": "stock_slippage_bps",
        "stockCommission": "stock_commission",
        "optionCommission": "option_commission",
        "sweepStepPct": "sweep_step_pct",
        "riskFreeRate": "risk_free_rate",
    }
    normalized: dict[str, Any] = {}
    allowed = set(StrategyDefinition.__dataclass_fields__)
    for key, value in payload.items():
        target = aliases.get(key, key)
        if target in allowed and target not in {"call_rule", "put_rule"}:
            normalized[target] = value
    normalized["call_rule"] = _rule_from_dict(call_payload)
    normalized["put_rule"] = _rule_from_dict(put_payload)
    strategy = StrategyDefinition(**normalized)
    strategy.validate()
    return strategy


def _rule_from_dict(payload: dict[str, Any]) -> OptionRule:
    aliases = {
        "targetDte": "target_dte",
        "rollDte": "roll_dte",
        "targetDelta": "target_delta",
        "fallbackMoneynessPct": "fallback_moneyness_pct",
        "expirationType": "expiration_type",
        "minOpenInterest": "min_open_interest",
        "maxSpreadPct": "max_spread_pct",
        "strikeMode": "strike_mode",
        "strikeValue": "strike_value",
    }
    allowed = set(OptionRule.__dataclass_fields__)
    normalized = {aliases.get(key, key): value for key, value in payload.items() if aliases.get(key, key) in allowed}
    return OptionRule(**normalized)


def dated_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: _iso(value) if isinstance(value, (date, datetime)) else value for key, value in payload.items()}
