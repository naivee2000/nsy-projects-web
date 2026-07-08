from __future__ import annotations

import re

from car_compare.models import Listing, VehicleQuery
from car_compare.vehicle_match import vehicle_text_match_score


PRICE_RE = re.compile(r"(?P<prefix>\$?\s?)(?P<value>[1-9]\d{1,2}(?:,\d{3})|\d{5,6})(?:\s|$)")
YEAR_RE = re.compile(r"\b(20[0-3]\d|19[8-9]\d)\b")
MILEAGE_RE = re.compile(r"(\d{1,3}(?:,\d{3})?|\d+(?:\.\d+)?)\s*(k)?\s*(?:mi|miles)\b", re.I)
VIN_RE = re.compile(r"\b([A-HJ-NPR-Z0-9]{17})\b", re.I)


def parse_visible_listing_text(
    source: str,
    url: str,
    text: str,
    request: VehicleQuery,
) -> list[Listing]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    listings: list[Listing] = []
    for idx, line in enumerate(lines):
        year_match = YEAR_RE.search(line)
        if not year_match:
            continue
        window = _listing_window(lines, idx)
        haystack = " ".join(window).lower()
        match = vehicle_text_match_score(request, haystack, source=source)
        if not match["accepted"]:
            continue

        price = _find_price(window)
        if not price:
            continue

        mileage = _find_mileage(window)
        vin = _find_vin(window)
        title = " ".join(window[:2]) if len(window) > 1 and "$" not in window[1] else line
        trim = _trim_from_title(title, request)
        condition = "new" if _looks_new(window) else "used"
        listings.append(
            Listing(
                source=source,
                year=int(year_match.group(1)),
                price=price,
                trim=trim,
                mileage=mileage,
                title=title,
                url=url,
                vin=vin,
                confidence=str(match["confidence"]),
                condition=condition,
            )
        )

    return _dedupe(listings)


def _find_price(lines: list[str]) -> float | None:
    for line in lines:
        for match in PRICE_RE.finditer(line):
            if _looks_like_mileage_candidate(line, match):
                continue
            raw = match.group("value").replace(",", "")
            try:
                value = float(raw)
            except ValueError:
                continue
            if 5000 <= value <= 500000:
                return value
    return None


def _looks_like_mileage_candidate(line: str, match: re.Match[str]) -> bool:
    after = line[match.end() : match.end() + 12].lower()
    before = line[max(0, match.start() - 4) : match.start()].lower()
    return "mi" in after or "mile" in after or before.endswith("k ")


def _listing_window(lines: list[str], start: int, limit: int = 12) -> list[str]:
    window = [lines[start]]
    for line in lines[start + 1 : start + limit]:
        if line == "---":
            break
        if YEAR_RE.search(line):
            break
        window.append(line)
    return window


def _find_mileage(lines: list[str]) -> int | None:
    for line in lines:
        match = MILEAGE_RE.search(line)
        if not match:
            continue
        number = float(match.group(1).replace(",", ""))
        if match.group(2):
            number *= 1000
        return int(number)
    return None


def _find_vin(lines: list[str]) -> str:
    for line in lines:
        match = VIN_RE.search(line)
        if match:
            return match.group(1).upper()
    return ""


def _looks_new(lines: list[str]) -> bool:
    return any(re.search(r"^(new|new vehicle|new arrival)\b", line.strip(), re.I) for line in lines[:4])


def _trim_from_title(title: str, request: VehicleQuery) -> str:
    pattern = re.compile(
        rf"\b{re.escape(request.make)}\s+{re.escape(request.model)}\b",
        re.I,
    )
    parts = pattern.split(title, maxsplit=1)
    if len(parts) == 2:
        return re.sub(r"\s+", " ", parts[1]).strip()
    return request.trim


def _dedupe(listings: list[Listing]) -> list[Listing]:
    seen = set()
    result = []
    for item in listings:
        key = (item.source, item.year, int(item.price), item.mileage, item.title.lower())
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
