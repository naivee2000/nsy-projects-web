from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
import csv
from io import StringIO
from pathlib import Path
import ssl
import threading
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import certifi


CBOE_SERIES = {
    "VIXCLS": "VIX",
    "VXNCLS": "VXN",
    "VIX9D": "VIX9D",
    "VIX3M": "VIX3M",
    "VIX6M": "VIX6M",
    "VIX1Y": "VIX1Y",
    "BXM": "BXM",
    "PUT": "PUT",
    "PPUT": "PPUT",
}
CBOE_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/{symbol}_History.csv"
TREASURY_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"
    "?data=daily_treasury_yield_curve&field_tdr_date_value={year}"
)
TREASURY_FIELDS = {
    "BC_1MONTH": "UST1MO",
    "BC_2MONTH": "UST2MO",
    "BC_3MONTH": "UST3MO",
    "BC_4MONTH": "UST4MO",
    "BC_6MONTH": "UST6MO",
    "BC_1YEAR": "UST1Y",
    "BC_2YEAR": "UST2Y",
}


class FreeReferenceData:
    """Official volatility and Treasury history for personal local research.

    The cache contains one attributed local copy of each public reference file.
    It is separate from provider-licensed stock/option history and can be safely
    refreshed without ever becoming a raw market-data export surface.
    """

    def __init__(self, data_dir: Path, timeout: int = 12, allow_network: bool = True):
        self.cache_dir = data_dir / "reference_data"
        self.timeout = timeout
        self.allow_network = allow_network
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._memory: dict[str, dict[str, float]] = {}
        self._prepared_ranges: set[tuple[int, int]] = set()
        self._lock = threading.RLock()
        self.errors: list[str] = []
        self.sources_used: set[str] = set()
        self._load_local_cache()

    def prepare(self, start: str, end: str) -> None:
        start_year = date.fromisoformat(start).year
        end_year = date.fromisoformat(end).year
        key = (start_year, end_year)
        with self._lock:
            if key in self._prepared_ranges:
                return
        jobs: list[tuple[str, str | int]] = [
            ("cboe", symbol) for symbol in CBOE_SERIES.values()
        ] + [("treasury", year) for year in range(start_year, end_year + 1)]
        if jobs:
            with ThreadPoolExecutor(max_workers=6, thread_name_prefix="reference-data") as executor:
                list(executor.map(self._prepare_one, jobs))
        with self._lock:
            self._prepared_ranges.add(key)

    def _prepare_one(self, job: tuple[str, str | int]) -> None:
        kind, value = job
        try:
            if kind == "cboe":
                self._ensure_cboe(str(value))
            else:
                self._ensure_treasury(int(value))
        except Exception as exc:  # a documented local fallback remains available
            with self._lock:
                message = f"{kind} {value}: {exc}"
                if message not in self.errors:
                    self.errors.append(message)

    def values(self, series: str) -> dict[str, float]:
        with self._lock:
            cached = self._memory.get(series)
            if cached is not None:
                if cached:
                    self.sources_used.add(series)
                return dict(cached)
        if series in CBOE_SERIES:
            self._ensure_cboe(CBOE_SERIES[series])
        elif series.startswith("UST"):
            self._load_all_treasury_cache()
        with self._lock:
            values = dict(self._memory.get(series, {}))
            if values:
                self.sources_used.add(series)
            return values

    def status(self) -> dict[str, object]:
        with self._lock:
            coverage = {
                series: {
                    "startDate": min(values) if values else None,
                    "endDate": max(values) if values else None,
                    "observations": len(values),
                }
                for series, values in sorted(self._memory.items())
            }
            return {
                "available": bool(coverage),
                "coverage": coverage,
                "errors": list(self.errors),
                "sources": [
                    "Cboe historical volatility and strategy indices",
                    "U.S. Treasury daily par yield curve",
                ],
                "localPersonalCopy": True,
            }

    def _ensure_cboe(self, symbol: str) -> None:
        series = next((key for key, value in CBOE_SERIES.items() if value == symbol), symbol)
        with self._lock:
            if series in self._memory:
                return
        target = self.cache_dir / f"cboe-{symbol}.csv"
        raw = self._read_or_download(target, CBOE_URL.format(symbol=symbol), refresh_current=True)
        parsed = self._parse_cboe(raw, symbol)
        with self._lock:
            self._memory[series] = parsed

    @staticmethod
    def _parse_cboe(raw: str, symbol: str) -> dict[str, float]:
        parsed: dict[str, float] = {}
        if raw:
            for row in csv.DictReader(StringIO(raw)):
                raw_date = str(row.get("DATE") or row.get("Date") or "").strip()
                if not raw_date:
                    continue
                try:
                    market_date = datetime.strptime(raw_date, "%m/%d/%Y").date().isoformat()
                except ValueError:
                    market_date = raw_date[:10]
                raw_value = row.get("CLOSE") or row.get("Close") or row.get(symbol)
                try:
                    parsed[market_date] = float(raw_value)  # type: ignore[arg-type]
                except (TypeError, ValueError):
                    continue
        return parsed

    def _load_local_cache(self) -> None:
        if not self.cache_dir.exists():
            return
        for series, symbol in CBOE_SERIES.items():
            target = self.cache_dir / f"cboe-{symbol}.csv"
            if not target.is_file():
                continue
            try:
                parsed = self._parse_cboe(target.read_text(encoding="utf-8"), symbol)
            except OSError:
                continue
            if parsed:
                self._memory[series] = parsed
        self._load_all_treasury_cache()

    def _ensure_treasury(self, year: int) -> None:
        target = self.cache_dir / f"treasury-{year}.xml"
        raw = self._read_or_download(
            target,
            TREASURY_URL.format(year=year),
            refresh_current=year == date.today().year,
        )
        if raw:
            self._merge_treasury(raw)

    def _load_all_treasury_cache(self) -> None:
        if not self.cache_dir.exists():
            return
        for target in sorted(self.cache_dir.glob("treasury-*.xml")):
            try:
                self._merge_treasury(target.read_text(encoding="utf-8"))
            except OSError:
                continue

    def _merge_treasury(self, raw: str) -> None:
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            return
        additions = {series: {} for series in TREASURY_FIELDS.values()}
        for entry in root.iter():
            if _local_name(entry.tag).lower() != "properties":
                continue
            fields = {_local_name(child.tag): (child.text or "").strip() for child in entry}
            raw_date = fields.get("NEW_DATE") or fields.get("Date") or fields.get("date")
            if not raw_date:
                continue
            market_date = raw_date[:10]
            for field, series in TREASURY_FIELDS.items():
                try:
                    additions[series][market_date] = float(fields[field])
                except (KeyError, TypeError, ValueError):
                    continue
        with self._lock:
            for series, values in additions.items():
                self._memory.setdefault(series, {}).update(values)

    def _read_or_download(self, target: Path, url: str, refresh_current: bool) -> str:
        if target.is_file():
            try:
                modified = datetime.fromtimestamp(target.stat().st_mtime, tz=timezone.utc).date()
                if not refresh_current or modified >= date.today():
                    return target.read_text(encoding="utf-8")
            except OSError:
                pass
        if not self.allow_network:
            try:
                return target.read_text(encoding="utf-8")
            except OSError:
                return ""
        request = Request(url, headers={"Accept": "text/csv, application/xml", "User-Agent": "NSY-Portfolio-Lab/2.0"})
        try:
            with urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
                raw = response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError, UnicodeDecodeError) as exc:
            try:
                return target.read_text(encoding="utf-8")
            except OSError:
                raise RuntimeError(str(exc)) from exc
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(raw, encoding="utf-8")
        return raw


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def interpolate_term(points: Iterable[tuple[int, float]], target_dte: int) -> float | None:
    ordered = sorted((days, value) for days, value in points if value > 0)
    if not ordered:
        return None
    if target_dte <= ordered[0][0]:
        return ordered[0][1]
    if target_dte >= ordered[-1][0]:
        return ordered[-1][1]
    for (left_day, left), (right_day, right) in zip(ordered, ordered[1:]):
        if left_day <= target_dte <= right_day:
            weight = (target_dte - left_day) / max(1, right_day - left_day)
            return left + (right - left) * weight
    return ordered[-1][1]
