from __future__ import annotations

from datetime import date
import json
import ssl
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import certifi

from .calendar import trading_dates
from .models import StockBar
from .providers import ProviderError
from .storage import AppStore, MarketVault


class TiingoProvider:
    name = "tiingo"
    base_url = "https://api.tiingo.com/tiingo/daily"

    def __init__(self, vault: MarketVault, store: AppStore, token: str = "", timeout: int = 45):
        self.vault = vault
        self.store = store
        self.token = token.strip()
        self.timeout = timeout
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.token_validated = False
        self._transient_bars: dict[str, list[StockBar]] = {}
        self._transient_ranges: dict[str, tuple[str, str]] = {}
        self.requests_this_run = 0

    @property
    def available(self) -> bool:
        return bool(self.token)

    def set_token(self, token: str) -> None:
        self.token = token.strip()
        self.token_validated = False

    def begin_run(self) -> None:
        self.requests_this_run = 0

    def clear_transient(self) -> None:
        """Forget provider-licensed rows after the result has been calculated."""
        self._transient_bars.clear()
        self._transient_ranges.clear()

    def search(self, query_text: str, limit: int = 8) -> list[dict[str, Any]]:
        if not self.token:
            raise ProviderError("Add a free Tiingo API token before searching its stock and ETF directory")
        params = urlencode({"query": query_text.strip(), "token": self.token})
        request = Request(
            f"https://api.tiingo.com/tiingo/utilities/search?{params}",
            headers={"Authorization": f"Token {self.token}", "Accept": "application/json", "User-Agent": "NSY-Portfolio-Lab/1.0"},
        )
        try:
            with urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code in {401, 403}:
                raise ProviderError("Tiingo rejected the saved token") from exc
            raise ProviderError(f"Tiingo symbol search failed ({exc.code})") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProviderError(f"Tiingo symbol search could not be reached: {exc}") from exc
        output = []
        for item in payload if isinstance(payload, list) else []:
            asset_type = str(item.get("assetType") or "").lower()
            if item.get("isActive") is False or asset_type not in {"stock", "etf", "mutual fund"}:
                continue
            ticker = str(item.get("ticker") or "").upper()
            if not ticker:
                continue
            output.append({"symbol": ticker, "name": str(item.get("name") or ticker), "type": asset_type.title()})
            if len(output) >= limit:
                break
        return output

    def stock_bars(self, symbol: str, start: str, end: str) -> list[StockBar]:
        symbol = symbol.upper()
        # A user-imported file is their own durable copy and takes priority over
        # the transient Tiingo Starter response. It must cover the entire request
        # before it can be used so two sources are never silently spliced.
        imported = self.vault.stock_bars("user-csv", symbol, start, end)
        if self._covers_request(imported, start, end):
            return imported
        transient = [bar for bar in self._transient_bars.get(symbol, []) if start <= bar.market_date <= end]
        cached_range = self._transient_ranges.get(symbol)
        if cached_range and cached_range[0] <= start and cached_range[1] >= end and transient:
            return transient
        if not self.token:
            if imported:
                raise ProviderError(
                    f"The imported {symbol} file does not cover the full selected period. "
                    "Import a wider file or add a free Tiingo token."
                )
            raise ProviderError("Add a free Tiingo API token or import your own CSV to load long-term stock history")
        params = urlencode({"startDate": start, "endDate": end, "resampleFreq": "daily", "token": self.token})
        request = Request(
            f"{self.base_url}/{quote(symbol)}/prices?{params}",
            headers={"Authorization": f"Token {self.token}", "Accept": "application/json", "User-Agent": "NSY-Portfolio-Lab/1.0"},
        )
        try:
            self.requests_this_run += 1
            with urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                error: Any = json.loads(raw)
            except json.JSONDecodeError:
                error = raw
            if exc.code in {401, 403}:
                self.token_validated = False
                raise ProviderError("Tiingo rejected the saved token. Check it in Data source settings.") from exc
            raise ProviderError(f"Tiingo price request failed ({exc.code}): {error}") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProviderError(f"Tiingo could not be reached: {exc}") from exc
        if not isinstance(payload, list) or not payload:
            raise ProviderError(f"Tiingo returned no daily prices for {symbol} in the selected period")
        bars: list[StockBar] = []
        for row in payload:
            market_date = str(row.get("date") or "")[:10]
            if not market_date:
                continue
            close = float(row.get("close") or row.get("adjClose") or 0)
            adjusted = float(row.get("adjClose") or close)
            bars.append(
                StockBar(
                    market_date=market_date,
                    open=float(row.get("open") or close),
                    high=float(row.get("high") or close),
                    low=float(row.get("low") or close),
                    close=close,
                    adjusted_close=adjusted,
                    volume=float(row.get("volume") or row.get("adjVolume") or 0),
                    split_detected=abs(float(row.get("splitFactor") or 1) - 1) > 1e-9,
                    dividend_cash=float(row.get("divCash") or 0),
                    split_factor=float(row.get("splitFactor") or 1),
                    source_timestamp=str(row.get("date") or ""),
                )
            )
        bars.sort(key=lambda item: item.market_date)
        self._validate_internal_coverage(symbol, bars)
        self._transient_bars[symbol] = bars
        self._transient_ranges[symbol] = (start, end)
        self.token_validated = True
        actual = {item.market_date for item in bars}
        expected = {item.isoformat() for item in trading_dates(date.fromisoformat(start), date.fromisoformat(end))}
        if not actual or not (actual & expected):
            raise ProviderError(f"No usable Tiingo prices were returned for {symbol}")
        return bars

    @staticmethod
    def _covers_request(bars: list[StockBar], start: str, end: str) -> bool:
        if not bars:
            return False
        expected = trading_dates(date.fromisoformat(start), date.fromisoformat(end))
        if not expected:
            return True
        dates = {bar.market_date for bar in bars}
        return all(day.isoformat() in dates for day in expected)

    @staticmethod
    def _validate_internal_coverage(symbol: str, bars: list[StockBar]) -> None:
        if not bars:
            return
        first = date.fromisoformat(bars[0].market_date)
        last = date.fromisoformat(bars[-1].market_date)
        expected = {item.isoformat() for item in trading_dates(first, last)}
        actual = {bar.market_date for bar in bars}
        missing = sorted(expected - actual)
        if missing:
            sample = ", ".join(missing[:3])
            suffix = "…" if len(missing) > 3 else ""
            raise ProviderError(
                f"Tiingo returned {len(missing)} missing trading session(s) inside {symbol}'s history "
                f"({sample}{suffix}). The test stopped instead of silently bridging the gap."
            )
