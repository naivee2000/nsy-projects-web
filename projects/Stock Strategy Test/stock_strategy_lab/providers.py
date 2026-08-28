from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
import certifi
import hashlib
import json
import math
import os
import ssl
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from .calendar import trading_dates
from .models import MarketTape, OptionQuote, OptionRule, StockBar
from .storage import AppStore, MarketVault


EASTERN = ZoneInfo("America/New_York")


class ProviderError(RuntimeError):
    pass


class CreditLimitError(ProviderError):
    pass


class HistoryAccessError(ProviderError):
    pass


class DataProvider(Protocol):
    name: str

    def stock_bars(self, symbol: str, start: str, end: str) -> list[StockBar]: ...

    def option_chain(self, symbol: str, market_date: str, rule: OptionRule) -> list[OptionQuote]: ...

    def option_quote_series(self, option_symbol: str, start: str, end: str) -> list[OptionQuote]: ...


def is_monthly_expiration(value: str) -> bool:
    day = date.fromisoformat(value)
    return day.weekday() == 4 and 15 <= day.day <= 21


class FixtureProvider:
    """Deterministic educational data; no account or internet required."""

    name = "fixture"

    def __init__(self, scenario: str = "wave"):
        self.scenario = scenario
        self._bar_cache: dict[tuple[str, str, str], list[StockBar]] = {}
        self._all_bars: dict[str, dict[str, StockBar]] = {}
        self._contracts: dict[str, dict[str, Any]] = {}

    def stock_bars(self, symbol: str, start: str, end: str) -> list[StockBar]:
        key = (symbol.upper(), start, end)
        if key in self._bar_cache:
            return list(self._bar_cache[key])
        sessions = trading_dates(date.fromisoformat(start), date.fromisoformat(end))
        price = 100.0
        bars: list[StockBar] = []
        for index, session in enumerate(sessions):
            wave = math.sin(index / 8.0) * 0.004
            if self.scenario == "up":
                change = 0.0025 + wave
            elif self.scenario == "down":
                change = -0.0022 + wave
            elif self.scenario == "flat":
                change = math.sin(index / 5.0) * 0.002
            else:
                change = 0.0005 + wave
            open_price = price
            price = max(10.0, price * (1 + change))
            high = max(open_price, price) * 1.004
            low = min(open_price, price) * 0.996
            bar = StockBar(
                market_date=session.isoformat(),
                open=round(open_price, 4),
                high=round(high, 4),
                low=round(low, 4),
                close=round(price, 4),
                adjusted_close=round(price, 4),
                volume=1_000_000 + index * 1_000,
            )
            bars.append(bar)
        self._bar_cache[key] = bars
        self._all_bars.setdefault(symbol.upper(), {}).update({bar.market_date: bar for bar in bars})
        return list(bars)

    def option_chain(self, symbol: str, market_date: str, rule: OptionRule) -> list[OptionQuote]:
        market_day = date.fromisoformat(market_date)
        stock = self._stock_price(symbol, market_date)
        expirations = self._expirations(market_day, rule.expiration_type)
        expiration = min(
            (item for item in expirations if (item - market_day).days > rule.roll_dte),
            key=lambda item: abs((item - market_day).days - rule.target_dte),
        )
        increment = 1 if stock < 80 else 5
        center = round(stock / increment) * increment
        strikes = [max(increment, center + increment * offset) for offset in range(-10, 11)]
        quotes: list[OptionQuote] = []
        for strike in strikes:
            item = self._quote(symbol, market_day, expiration, rule.side, float(strike), stock)
            self._contracts[item.option_symbol] = {
                "underlying": symbol.upper(),
                "expiration": expiration,
                "side": rule.side,
                "strike": float(strike),
            }
            quotes.append(item)
        return quotes

    def option_quote_series(self, option_symbol: str, start: str, end: str) -> list[OptionQuote]:
        contract = self._contracts.get(option_symbol)
        if not contract:
            raise ProviderError(f"Demo contract {option_symbol} is not known")
        underlying = contract["underlying"]
        expiration: date = contract["expiration"]
        output: list[OptionQuote] = []
        for market_day in trading_dates(date.fromisoformat(start), min(date.fromisoformat(end), expiration)):
            market_date = market_day.isoformat()
            try:
                stock = self._stock_price(underlying, market_date)
            except ProviderError:
                continue
            output.append(
                self._quote(
                    underlying,
                    market_day,
                    expiration,
                    contract["side"],
                    contract["strike"],
                    stock,
                )
            )
        return output

    def _stock_price(self, symbol: str, market_date: str) -> float:
        bar = self._all_bars.get(symbol.upper(), {}).get(market_date)
        if not bar:
            raise ProviderError(f"No demo stock price for {symbol} on {market_date}")
        return bar.close

    @staticmethod
    def _expirations(market_day: date, expiration_type: str) -> list[date]:
        output: list[date] = []
        current = market_day + timedelta(days=1)
        # Demo data supports the same long-dated call controls as the real app.
        limit = market_day + timedelta(days=800)
        while current <= limit:
            if current.weekday() == 4:
                if expiration_type == "any" or 15 <= current.day <= 21:
                    output.append(current)
            current += timedelta(days=1)
        return output

    @staticmethod
    def _option_symbol(symbol: str, expiration: date, side: str, strike: float) -> str:
        letter = "C" if side == "call" else "P"
        return f"{symbol.upper()}{expiration:%y%m%d}{letter}{int(round(strike * 1000)):08d}"

    def _quote(
        self,
        symbol: str,
        market_day: date,
        expiration: date,
        side: str,
        strike: float,
        stock: float,
    ) -> OptionQuote:
        dte = max(0, (expiration - market_day).days)
        intrinsic = max(0.0, stock - strike) if side == "call" else max(0.0, strike - stock)
        volatility = 0.22
        years = dte / 365
        if years > 0 and stock > 0 and strike > 0:
            denominator = volatility * math.sqrt(years)
            d1 = (math.log(stock / strike) + 0.5 * volatility**2 * years) / denominator
            d2 = d1 - denominator
            normal = lambda item: 0.5 * (1 + math.erf(item / math.sqrt(2)))
            call_fair = stock * normal(d1) - strike * normal(d2)
            put_fair = strike * normal(-d2) - stock * normal(-d1)
            fair = call_fair if side == "call" else put_fair
            call_delta = normal(d1)
        else:
            fair = intrinsic
            call_delta = 1.0 if stock > strike else 0.0
        fair = max(intrinsic, fair, 0.05 if dte > 0 else 0.0)
        spread = max(0.02, fair * 0.06)
        bid = max(0.0, fair - spread / 2)
        ask = max(bid + 0.01, fair + spread / 2)
        call_delta = min(0.98, max(0.02, call_delta))
        delta = call_delta if side == "call" else -(1 - call_delta)
        return OptionQuote(
            market_date=market_day.isoformat(),
            option_symbol=self._option_symbol(symbol, expiration, side, strike),
            underlying=symbol.upper(),
            expiration=expiration.isoformat(),
            side=side,  # type: ignore[arg-type]
            strike=strike,
            bid=round(bid, 4),
            ask=round(ask, 4),
            last=round(fair, 4),
            delta=round(delta, 4),
            gamma=0.02,
            theta=round(-(fair - intrinsic) / max(dte, 1), 4),
            vega=0.1,
            iv=0.22,
            open_interest=1_000,
            volume=250,
            underlying_price=stock,
            is_monthly=is_monthly_expiration(expiration.isoformat()),
        )


class CachedProvider:
    """Shares one market tape across the main result and allocation sweep."""

    def __init__(self, provider: DataProvider, tape: MarketTape | None = None):
        self.provider = provider
        self.name = provider.name
        self.tape = tape or MarketTape()

    def stock_bars(self, symbol: str, start: str, end: str) -> list[StockBar]:
        key = (symbol.upper(), start, end)
        if key not in self.tape.stock:
            self.tape.stock[key] = self.provider.stock_bars(symbol, start, end)
        return list(self.tape.stock[key])

    def option_chain(self, symbol: str, market_date: str, rule: OptionRule) -> list[OptionQuote]:
        key = (symbol.upper(), market_date, json.dumps(rule.to_dict(), sort_keys=True))
        if key not in self.tape.chains:
            self.tape.chains[key] = self.provider.option_chain(symbol, market_date, rule)
        return list(self.tape.chains[key])

    def option_quote_series(self, option_symbol: str, start: str, end: str) -> list[OptionQuote]:
        key = (option_symbol, start, end)
        if key not in self.tape.series:
            self.tape.series[key] = self.provider.option_quote_series(option_symbol, start, end)
        return list(self.tape.series[key])


@dataclass(frozen=True)
class ApiResponse:
    payload: dict[str, Any]
    headers: dict[str, str]
    status: int


class MarketDataProvider:
    name = "marketdata"
    base_url = "https://api.marketdata.app/v1"

    def __init__(
        self,
        vault: MarketVault,
        store: AppStore,
        token: str | None = None,
        timeout: int = 45,
        ssl_context: ssl.SSLContext | None = None,
    ):
        self.vault = vault
        self.store = store
        self.token = (token or os.environ.get("MARKETDATA_API_TOKEN", "")).strip()
        self.timeout = timeout
        self.ssl_context = ssl_context or ssl.create_default_context(cafile=certifi.where())
        self.token_validated = False
        self._chain_cache: dict[tuple[str, str, str], list[OptionQuote]] = {}
        self._series_cache: dict[tuple[str, str, str], list[OptionQuote]] = {}

    @property
    def available(self) -> bool:
        return bool(self.token)

    @property
    def history_years(self) -> int | None:
        """Use an explicit probe result; trial and paid plans can share credit limits."""
        override = os.environ.get("MARKETDATA_HISTORY_YEARS", "").strip().lower()
        if override in {"unlimited", "full", "none"}:
            return None
        if override:
            try:
                return max(1, int(override))
            except ValueError:
                pass
        verification = self.history_verification
        if verification.get("verified") is True and int(verification.get("years") or 0) >= 5:
            return 5
        return 1

    @property
    def history_verification(self) -> dict[str, Any]:
        stored = self.store.get_setting("marketdata_history_verification") or {}
        if stored.get("tokenFingerprint") != self._token_fingerprint():
            return {"verified": False, "years": 1, "status": "not_checked"}
        return stored

    def clear_history_verification(self) -> None:
        self.store.delete_setting("marketdata_history_verification")

    def verify_five_year_access(self, symbol: str = "SPY") -> dict[str, Any]:
        self._require_token()
        current = datetime.now(EASTERN).date()
        try:
            target = current.replace(year=current.year - 4)
        except ValueError:
            target = current.replace(year=current.year - 4, day=28)
        sessions = trading_dates(target, target + timedelta(days=7))
        probe_date = sessions[0] if sessions else target
        try:
            response = self._request(
                f"/stocks/candles/D/{quote(symbol.upper())}/",
                {"from": probe_date.isoformat(), "to": probe_date.isoformat(), "adjustsplits": "true", "adjustdividends": "true"},
            )
            has_data = response.payload.get("s") == "ok" and bool(response.payload.get("t") or response.payload.get("c"))
            if not has_data:
                raise ProviderError("The five-year verification request returned no historical candle")
            result = {
                "verified": True,
                "years": 5,
                "status": "verified",
                "probeSymbol": symbol.upper(),
                "probeDate": probe_date.isoformat(),
                "tokenFingerprint": self._token_fingerprint(),
                "checkedAt": datetime.now(EASTERN).isoformat(),
                "message": "Five-year Market Data access was verified successfully.",
            }
        except HistoryAccessError as exc:
            result = {
                "verified": False,
                "years": 1,
                "status": "one_year_only",
                "probeSymbol": symbol.upper(),
                "probeDate": probe_date.isoformat(),
                "tokenFingerprint": self._token_fingerprint(),
                "checkedAt": datetime.now(EASTERN).isoformat(),
                "message": f"This token is limited to one year of history: {exc}",
            }
        self.store.save_setting("marketdata_history_verification", result)
        return {key: value for key, value in result.items() if key != "tokenFingerprint"}

    def history_window_start(self, as_of: date | None = None) -> date | None:
        years = self.history_years
        if years is None:
            return None
        current = as_of or datetime.now(EASTERN).date()
        try:
            return current.replace(year=current.year - years)
        except ValueError:
            return current.replace(year=current.year - years, day=28)

    def set_token(self, token: str) -> None:
        self.token = token.strip()
        self.token_validated = False
        self.clear_cache()

    def clear_cache(self) -> None:
        self._chain_cache.clear()
        self._series_cache.clear()

    def _token_fingerprint(self) -> str:
        return hashlib.sha256(self.token.encode("utf-8")).hexdigest()[:16] if self.token else ""

    def stock_bars(self, symbol: str, start: str, end: str) -> list[StockBar]:
        symbol = symbol.upper()
        cached = self.vault.stock_bars(self.name, symbol, start, end)
        if self._covers(cached, start, end):
            return cached
        self._require_token()
        raw = self._request(
            f"/stocks/candles/D/{quote(symbol)}/",
            {"from": start, "to": end, "adjustsplits": "false", "adjustdividends": "false"},
        )
        adjusted = self._request(
            f"/stocks/candles/D/{quote(symbol)}/",
            {"from": start, "to": end, "adjustsplits": "true", "adjustdividends": "true"},
        )
        raw_rows = self._parse_stock_bars(raw.payload, adjusted.payload)
        self.vault.save_stock_bars(self.name, symbol, raw_rows)
        result = self.vault.stock_bars(self.name, symbol, start, end)
        missing = self._missing_stock_sessions(result, start, end)
        if missing:
            preview = ", ".join(missing[:3])
            raise ProviderError(
                f"Stock history is missing {len(missing)} requested trading session(s), including {preview}. "
                "The backtest stopped because filling those dates would make the comparison misleading."
            )
        return result

    def option_chain(self, symbol: str, market_date: str, rule: OptionRule) -> list[OptionQuote]:
        symbol = symbol.upper()
        key = (symbol, market_date, json.dumps(rule.to_dict(), sort_keys=True))
        fetch_key = f"option-chain:{symbol}:{market_date}:{key[2]}"
        if key in self._chain_cache:
            return list(self._chain_cache[key])
        cached = self.vault.option_chain(self.name, symbol, market_date, side=rule.side)
        if self.store.provider_fetch_covers(fetch_key, market_date, market_date):
            scoped = self._cached_chain_for_fetch(cached, fetch_key, market_date, rule)
            eligible = self._eligible_chain(scoped, market_date, rule)
            self._chain_cache[key] = eligible
            return list(eligible)
        # Individual contract-history downloads share the same option table as
        # historical chain snapshots. Without an explicit fetch manifest and
        # membership list, cached rows are not proof of a complete chain and
        # must never be used for contract selection.
        provider_window_start = self.history_window_start()
        if provider_window_start and date.fromisoformat(market_date) < provider_window_start:
            window_label = f"{self.history_years}-year" if self.history_years != 1 else "one-year"
            raise ProviderError(
                f"Option history for {market_date} is not in the local vault and is older than the detected {window_label} provider window. "
                "That gap is permanently unavailable under the current plan, so the backtest was not approximated."
            )
        self._require_token()
        params: dict[str, Any] = {
            "date": market_date,
            "dte": rule.target_dte,
            "side": rule.side,
            "strikeLimit": 40,
            "nonstandard": "false",
        }
        if rule.expiration_type == "monthly":
            params["monthly"] = "true"
        response = self._request(f"/options/chain/{quote(symbol)}/", params)
        quotes = self._parse_option_quotes(response.payload, symbol, market_date)
        if rule.expiration_type == "monthly":
            quotes = [replace(item, is_monthly=True) for item in quotes]
        self.vault.save_option_quotes(self.name, quotes)
        self._save_chain_membership(fetch_key, quotes)
        self.store.mark_provider_fetch(fetch_key, self.name, "option-chain", market_date, market_date)
        eligible = self._eligible_chain(quotes, market_date, rule)
        self._chain_cache[key] = eligible
        return list(eligible)

    def _cached_chain_for_fetch(
        self,
        cached: list[OptionQuote],
        fetch_key: str,
        market_date: str,
        rule: OptionRule,
    ) -> list[OptionQuote]:
        membership = self.store.get_setting(self._chain_membership_key(fetch_key))
        if membership is not None:
            symbols = set(membership.get("symbols") or [])
            selected = [item for item in cached if item.option_symbol in symbols]
        else:
            # Older caches predate explicit chain membership. A historical
            # strike-limited chain normally contributes many symbols for one
            # expiration, while a contract-history download contributes only
            # sparse individual symbols. Reconstruct once, then persist it.
            current = date.fromisoformat(market_date)
            candidates = [
                item for item in cached
                if item.side == rule.side
                and not item.is_nonstandard
                and (date.fromisoformat(item.expiration) - current).days > rule.roll_dte
            ]
            counts: dict[str, int] = {}
            for item in candidates:
                counts[item.expiration] = counts.get(item.expiration, 0) + 1
            largest = max(counts.values(), default=0)
            if largest < 5:
                selected = []
            else:
                expirations = [value for value, count in counts.items() if count == largest]
                expiration = min(
                    expirations,
                    key=lambda value: abs(
                        (date.fromisoformat(value) - current).days - rule.target_dte
                    ),
                )
                selected = [item for item in candidates if item.expiration == expiration]
            self._save_chain_membership(fetch_key, selected)
        if rule.expiration_type == "monthly":
            selected = [replace(item, is_monthly=True) for item in selected]
            if selected:
                self.vault.save_option_quotes(self.name, selected)
        return selected

    def _save_chain_membership(self, fetch_key: str, quotes: list[OptionQuote]) -> None:
        self.store.save_setting(
            self._chain_membership_key(fetch_key),
            {"symbols": sorted({item.option_symbol for item in quotes})},
        )

    @staticmethod
    def _chain_membership_key(fetch_key: str) -> str:
        digest = hashlib.sha256(fetch_key.encode("utf-8")).hexdigest()
        return f"marketdata_chain_membership:{digest}"

    def option_quote_series(self, option_symbol: str, start: str, end: str) -> list[OptionQuote]:
        key = (option_symbol, start, end)
        # v2 distinguishes correctly expanded vector responses from manifests
        # written by the older scalar-symbol parser.
        fetch_key = f"option-series:v2:{option_symbol}"
        if key in self._series_cache:
            return list(self._series_cache[key])
        cached = self.vault.option_series(self.name, option_symbol, start, end)
        if self._covers_quotes(cached, start, end):
            self._series_cache[key] = cached
            return list(cached)
        if self.store.provider_fetch_covers(fetch_key, start, end):
            self._series_cache[key] = cached
            return list(cached)
        self._require_token()
        response = self._request(
            f"/options/quotes/{quote(option_symbol)}/",
            {"from": start, "to": (date.fromisoformat(end) + timedelta(days=1)).isoformat()},
        )
        underlying = self._underlying_from_occ(option_symbol)
        quotes = self._parse_option_quotes(response.payload, underlying, start)
        self.vault.save_option_quotes(self.name, quotes)
        self.store.mark_provider_fetch(fetch_key, self.name, "option-series", start, end)
        result = self.vault.option_series(self.name, option_symbol, start, end)
        self._series_cache[key] = result
        return list(result)

    def option_expirations(self, symbol: str, market_date: str) -> list[str]:
        self._require_token()
        response = self._request(f"/options/expirations/{quote(symbol.upper())}/", {"date": market_date})
        values = response.payload.get("expirations") or response.payload.get("expiration") or []
        if not isinstance(values, list):
            return []
        return [self._date_value(value) for value in values]

    def capture_expiration(self, symbol: str, market_date: str, expiration: str) -> list[OptionQuote]:
        symbol = symbol.upper()
        fetch_key = f"capture-chain:{symbol}:{market_date}:{expiration}"
        cached = self.vault.option_chain(self.name, symbol, market_date, expiration=expiration)
        if self.store.provider_fetch_covers(fetch_key, market_date, market_date):
            return cached
        self._require_token()
        response = self._request(
            f"/options/chain/{quote(symbol)}/",
            {
                "date": market_date,
                "expiration": expiration,
                "nonstandard": "false",
            },
        )
        quotes = self._parse_option_quotes(response.payload, symbol, market_date)
        self.vault.save_option_quotes(self.name, quotes)
        self.store.mark_provider_fetch(fetch_key, self.name, "capture-chain", market_date, market_date)
        return quotes

    def capture_target_chain(
        self,
        symbol: str,
        market_date: str,
        side: str,
        target_dte: int,
        strike_limit: int = 40,
    ) -> list[OptionQuote]:
        symbol = symbol.upper()
        fetch_key = f"target-chain:{symbol}:{market_date}:{side}:{target_dte}:{strike_limit}:monthly"
        if self.store.provider_fetch_covers(fetch_key, market_date, market_date):
            cached = self.vault.option_chain(self.name, symbol, market_date, side=side)
            if not cached:
                return []
            current = date.fromisoformat(market_date)
            expiration = min(
                {item.expiration for item in cached},
                key=lambda value: abs((date.fromisoformat(value) - current).days - target_dte),
            )
            return [item for item in cached if item.expiration == expiration and item.side == side]
        self._require_token()
        response = self._request(
            f"/options/chain/{quote(symbol)}/",
            {
                "date": market_date,
                "dte": target_dte,
                "side": side,
                "monthly": "true",
                "strikeLimit": strike_limit,
                "nonstandard": "false",
            },
        )
        quotes = self._parse_option_quotes(response.payload, symbol, market_date)
        self.vault.save_option_quotes(self.name, quotes)
        self.store.mark_provider_fetch(fetch_key, self.name, "target-chain", market_date, market_date)
        return [item for item in quotes if item.side == side]

    def capture_accuracy_chain(
        self,
        symbol: str,
        market_date: str,
        side: str,
        target_dte: int,
    ) -> list[OptionQuote]:
        """Capture a wide, standard monthly chain for local calibration.

        Historical chains are credit-efficient, but the result is still kept
        local and tagged with an explicit fetch manifest so sparse contract
        histories can never masquerade as a complete selection chain.
        """
        symbol = symbol.upper()
        fetch_key = f"accuracy-chain:v1:{symbol}:{market_date}:{side}:{target_dte}"
        if self.store.provider_fetch_covers(fetch_key, market_date, market_date):
            cached = self.vault.option_chain(self.name, symbol, market_date, side=side)
            membership = self.store.get_setting(self._chain_membership_key(fetch_key)) or {}
            symbols = set(membership.get("symbols") or [])
            return [item for item in cached if item.option_symbol in symbols]
        self._require_token()
        response = self._request(
            f"/options/chain/{quote(symbol)}/",
            {
                "date": market_date,
                "dte": target_dte,
                "side": side,
                "monthly": "true",
                "strikeLimit": 1000,
                "nonstandard": "false",
            },
        )
        quotes = [
            replace(item, is_monthly=True, pricing_source="exact")
            for item in self._parse_option_quotes(response.payload, symbol, market_date)
            if item.side == side and not item.is_nonstandard
        ]
        if quotes:
            spot = next((item.underlying_price for item in quotes if item.underlying_price > 0), 0.0)
            if spot > 0:
                quotes = [item for item in quotes if 0.50 <= item.strike / spot <= 1.50]
        self.vault.save_option_quotes(self.name, quotes)
        self._save_chain_membership(fetch_key, quotes)
        self.store.mark_provider_fetch(fetch_key, self.name, "accuracy-chain", market_date, market_date)
        return quotes

    def _request(self, path: str, params: dict[str, Any]) -> ApiResponse:
        query_string = urlencode({key: value for key, value in params.items() if value is not None})
        url = f"{self.base_url}{path}{'?' + query_string if query_string else ''}"
        request = Request(url, headers={"Authorization": f"Bearer {self.token}", "Accept": "application/json"})
        try:
            with urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
                status = int(response.status)
                raw = response.read().decode("utf-8")
                payload = json.loads(raw) if raw.strip() else {}
                headers = {key.lower(): value for key, value in response.headers.items()}
        except HTTPError as exc:
            error_headers = {key.lower(): value for key, value in exc.headers.items()} if exc.headers else {}
            if error_headers:
                self._record_quota(path, error_headers)
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {"errmsg": raw or exc.reason}
            if exc.code == 429:
                raise CreditLimitError(payload.get("errmsg") or "Market Data daily credit limit reached") from exc
            if exc.code == 402:
                raise HistoryAccessError(payload.get("errmsg") or "The Market Data plan does not include this historical date") from exc
            if exc.code == 401:
                self.token_validated = False
            if exc.code == 404 and payload.get("s") == "no_data":
                return ApiResponse(payload, {}, exc.code)
            raise ProviderError(payload.get("errmsg") or f"Market Data request failed ({exc.code})") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            reason = getattr(exc, "reason", None)
            if isinstance(reason, ssl.SSLCertVerificationError):
                raise ProviderError(
                    "The secure Market Data connection could not verify its certificate. "
                    "Reinstall the app requirements to refresh the trusted certificate bundle."
                ) from exc
            raise ProviderError(f"Market Data could not be reached: {exc}") from exc
        if status not in {200, 203, 204}:
            raise ProviderError(payload.get("errmsg") or f"Unexpected Market Data status {status}")
        self.token_validated = True
        self._record_quota(path, headers)
        return ApiResponse(payload, headers, status)

    def _record_quota(self, endpoint: str, headers: dict[str, str]) -> None:
        def integer(name: str) -> int | None:
            try:
                return int(headers[name]) if name in headers else None
            except (TypeError, ValueError):
                return None

        self.store.record_quota(
            endpoint,
            integer("x-api-ratelimit-consumed") or 0,
            integer("x-api-ratelimit-remaining"),
            integer("x-api-ratelimit-limit"),
            integer("x-api-ratelimit-reset"),
        )

    def _parse_stock_bars(self, raw: dict[str, Any], adjusted: dict[str, Any]) -> list[StockBar]:
        timestamps = raw.get("t") or []
        adjusted_by_date: dict[str, float] = {}
        for index, stamp in enumerate(adjusted.get("t") or []):
            adjusted_by_date[self._date_value(stamp)] = float(self._at(adjusted.get("c"), index, 0.0))
        bars: list[StockBar] = []
        previous_ratio: float | None = None
        for index, stamp in enumerate(timestamps):
            market_date = self._date_value(stamp)
            close = float(self._at(raw.get("c"), index, 0.0))
            adjusted_close = adjusted_by_date.get(market_date, close)
            ratio = adjusted_close / close if close else 1.0
            split_detected = bool(previous_ratio and abs(ratio / previous_ratio - 1) > 0.20)
            previous_ratio = ratio
            bars.append(
                StockBar(
                    market_date,
                    float(self._at(raw.get("o"), index, close)),
                    float(self._at(raw.get("h"), index, close)),
                    float(self._at(raw.get("l"), index, close)),
                    close,
                    adjusted_close,
                    float(self._at(raw.get("v"), index, 0.0)),
                    split_detected,
                )
            )
        return bars

    def _parse_option_quotes(self, payload: dict[str, Any], underlying: str, fallback_date: str) -> list[OptionQuote]:
        symbols = payload.get("optionSymbol") or payload.get("option_symbol") or []
        if isinstance(symbols, str):
            vector_fields = (
                "updated",
                "expiration",
                "strike",
                "bid",
                "ask",
                "last",
                "openInterest",
                "volume",
            )
            row_count = max(
                (
                    len(payload.get(field) or [])
                    for field in vector_fields
                    if isinstance(payload.get(field), list)
                ),
                default=1,
            )
            symbols = [symbols] * row_count
        output: list[OptionQuote] = []
        for index, option_symbol in enumerate(symbols):
            expiration = self._date_value(self._at(payload.get("expiration"), index, self._occ_expiration(option_symbol)))
            market_date = self._date_value(self._at(payload.get("updated"), index, fallback_date))
            side_raw = str(self._at(payload.get("side"), index, self._occ_side(option_symbol))).lower()
            side = "put" if side_raw.startswith("p") else "call"
            quote_item = OptionQuote(
                market_date=market_date,
                option_symbol=str(option_symbol),
                underlying=str(self._at(payload.get("underlying"), index, underlying)).upper(),
                expiration=expiration,
                side=side,  # type: ignore[arg-type]
                strike=float(self._at(payload.get("strike"), index, self._occ_strike(option_symbol))),
                bid=float(self._at(payload.get("bid"), index, 0.0) or 0.0),
                ask=float(self._at(payload.get("ask"), index, 0.0) or 0.0),
                last=float(self._at(payload.get("last"), index, 0.0) or 0.0),
                delta=self._float_or_none(self._at(payload.get("delta"), index, None)),
                gamma=self._float_or_none(self._at(payload.get("gamma"), index, None)),
                theta=self._float_or_none(self._at(payload.get("theta"), index, None)),
                vega=self._float_or_none(self._at(payload.get("vega"), index, None)),
                iv=self._float_or_none(self._at(payload.get("iv"), index, None)),
                open_interest=int(self._at(payload.get("openInterest"), index, 0) or 0),
                volume=int(self._at(payload.get("volume"), index, 0) or 0),
                underlying_price=float(self._at(payload.get("underlyingPrice"), index, 0.0) or 0.0),
                is_monthly=is_monthly_expiration(expiration),
                is_nonstandard=bool(self._at(payload.get("nonstandard"), index, False)),
                bid_size=int(self._at(payload.get("bidSize"), index, 0) or 0),
                ask_size=int(self._at(payload.get("askSize"), index, 0) or 0),
                source_timestamp=str(self._at(payload.get("updated"), index, fallback_date)),
                pricing_source="exact",
            )
            output.append(quote_item)
        return output

    @staticmethod
    def _eligible_chain(quotes: list[OptionQuote], market_date: str, rule: OptionRule) -> list[OptionQuote]:
        current = date.fromisoformat(market_date)
        filtered = [
            item
            for item in quotes
            if item.side == rule.side
            and not item.is_nonstandard
            and (rule.expiration_type != "monthly" or item.is_monthly)
            and (date.fromisoformat(item.expiration) - current).days > rule.roll_dte
        ]
        if not filtered:
            return []
        best_expiration = min(
            {item.expiration for item in filtered},
            key=lambda value: abs((date.fromisoformat(value) - current).days - rule.target_dte),
        )
        return [item for item in filtered if item.expiration == best_expiration]

    @staticmethod
    def _covers(bars: list[StockBar], start: str, end: str) -> bool:
        return bool(bars) and not MarketDataProvider._missing_stock_sessions(bars, start, end)

    @staticmethod
    def _missing_stock_sessions(bars: list[StockBar], start: str, end: str) -> list[str]:
        present = {item.market_date for item in bars}
        return [
            item.isoformat()
            for item in trading_dates(date.fromisoformat(start), date.fromisoformat(end))
            if item.isoformat() not in present
        ]

    @staticmethod
    def _covers_quotes(quotes: list[OptionQuote], start: str, end: str) -> bool:
        if not quotes:
            return False
        expiration = date.fromisoformat(quotes[0].expiration)
        expected_end = min(date.fromisoformat(end), expiration)
        return date.fromisoformat(quotes[0].market_date) <= date.fromisoformat(start) + timedelta(days=7) and date.fromisoformat(
            quotes[-1].market_date
        ) >= expected_end - timedelta(days=7)

    def _require_token(self) -> None:
        if not self.available:
            raise ProviderError("Market Data mode needs MARKETDATA_API_TOKEN on the server")

    @staticmethod
    def _date_value(value: Any) -> str:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(float(value), tz=EASTERN).date().isoformat()
        raw = str(value)
        if "T" in raw:
            return raw.split("T", 1)[0]
        if " " in raw and len(raw) >= 10:
            return raw[:10]
        return raw[:10]

    @staticmethod
    def _at(value: Any, index: int, default: Any) -> Any:
        if isinstance(value, list):
            return value[index] if index < len(value) else default
        return value if value is not None else default

    @staticmethod
    def _float_or_none(value: Any) -> float | None:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _underlying_from_occ(symbol: str) -> str:
        for index, char in enumerate(symbol):
            if char.isdigit():
                return symbol[:index]
        return symbol

    @staticmethod
    def _occ_expiration(symbol: str) -> str:
        root_length = next((index for index, char in enumerate(symbol) if char.isdigit()), 0)
        value = symbol[root_length : root_length + 6]
        return date(2000 + int(value[:2]), int(value[2:4]), int(value[4:6])).isoformat()

    @staticmethod
    def _occ_side(symbol: str) -> str:
        root_length = next((index for index, char in enumerate(symbol) if char.isdigit()), 0)
        return "call" if symbol[root_length + 6 : root_length + 7] == "C" else "put"

    @staticmethod
    def _occ_strike(symbol: str) -> float:
        root_length = next((index for index, char in enumerate(symbol) if char.isdigit()), 0)
        try:
            return int(symbol[root_length + 7 : root_length + 15]) / 1000
        except ValueError:
            return 0.0
