from __future__ import annotations

import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from car_compare.models import Listing, MSRP, VehicleQuery
from car_compare.trim_match import trim_tokens, trim_value_matches_request
from car_compare.vehicle_catalog import source_model_contains_trim, source_query_model


CURRENT_YEAR = 2026
SOURCE = "visor_public_facets"
NEW_SOURCE = "visor_public_facets_new"
TIMEOUT_SECONDS = 18


@dataclass
class VisorYearData:
    year: int
    url: str
    car_type: str
    price_stats: dict[str, float]
    msrp_stats: dict[str, float]
    mileage_stats: dict[str, float]
    price_bins: list[dict[str, float]]
    num_found: int = 0
    filter_name: str = ""
    filter_value: str = ""


def collect_visor_public_facets(request: VehicleQuery, current_year: int = CURRENT_YEAR) -> dict[str, Any]:
    years = list(range(current_year, current_year - request.max_age - 1, -1))
    used_rows: list[VisorYearData] = []
    new_rows: list[VisorYearData] = []
    notes: list[str] = []
    used_filters = _matching_filter_specs(request, "used")
    new_filters = _matching_filter_specs(request, "new", current_year)

    if used_filters:
        notes.append(
            "Visor trim/version aliases used for used inventory: "
            + ", ".join(f"{item['name']}={item['value']} ({item['count']})" for item in used_filters)
        )
    if new_filters:
        notes.append(
            "Visor trim/version aliases used for new inventory: "
            + ", ".join(f"{item['name']}={item['value']} ({item['count']})" for item in new_filters)
        )

    with ThreadPoolExecutor(max_workers=4) as pool:
        future_map: dict[Any, tuple[str, int]] = {}
        for url, year, filter_name, filter_value in _used_visor_requests(request, years, used_filters):
            if year == current_year:
                continue
            future_map[pool.submit(fetch_visor_year, request, year, "used", url, filter_name, filter_value)] = ("used", year)
        for url, filter_name, filter_value in _visor_urls_for_specs(request, current_year, "new", new_filters):
            future_map[pool.submit(fetch_visor_year, request, current_year, "new", url, filter_name, filter_value)] = ("new", current_year)
        for future in as_completed(future_map):
            car_type, year = future_map[future]
            try:
                data = future.result()
            except Exception as exc:  # Network and page-format failures should not kill collection.
                notes.append(f"Visor public {car_type} facets failed for {year}: {exc}")
                continue
            if data:
                if data.car_type == "new":
                    new_rows.append(data)
                else:
                    used_rows.append(data)

    used_rows.sort(key=lambda item: item.year, reverse=True)
    new_rows.sort(key=lambda item: item.year, reverse=True)
    listings = _listings_from_years(request, used_rows + new_rows, current_year)
    msrp = _msrp_from_years(request, new_rows + used_rows, current_year)
    status = "success" if listings else "blocked"
    sources = [
        {
            "source": SOURCE,
            "url": _visor_url(request, car_type="used"),
            "status": "success" if any(item.source == SOURCE for item in listings) else "unavailable",
            "load_more_clicked": 0,
            "notes": (
                f"Read public Visor used-market facets for {len(used_rows)} model years and expanded "
                f"price histograms into {sum(1 for item in listings if item.source == SOURCE)} aggregate observations."
                if used_rows
                else "No usable public Visor price histogram data was found."
            ),
        },
        {
            "source": NEW_SOURCE,
            "url": _visor_url(request, current_year, car_type="new"),
            "status": "success" if any(item.source == NEW_SOURCE for item in listings) else "unavailable",
            "load_more_clicked": 0,
            "notes": (
                f"Read public Visor new-car facets for {len(new_rows)} model years and expanded "
                f"price histograms into {sum(1 for item in listings if item.source == NEW_SOURCE)} labeled new observations."
                if new_rows
                else "No usable public Visor new-car price histogram data was found."
            ),
        },
    ]
    if notes:
        notes = notes[:8]
    return {
        "query": request.raw,
        "status": status,
        "notes": [
            "Visor public facets are aggregate market data, not individual dealer listing rows.",
            "New-car facet observations are labeled with condition=new and support the age-0 box plot when available.",
            *notes,
        ],
        "msrp": msrp.to_dict() if msrp else None,
        "sources": sources,
        "evidence": _facet_evidence(used_rows + new_rows),
        "listings": [item.to_dict() for item in listings],
    }


def fetch_visor_year(
    request: VehicleQuery,
    year: int,
    car_type: str = "used",
    url: str | None = None,
    filter_name: str = "",
    filter_value: str = "",
) -> VisorYearData | None:
    url = url or _visor_url(request, year, car_type=car_type)
    return _fetch_visor_facets(request, year, car_type, url, filter_name, filter_value)


def fetch_visor_new(request: VehicleQuery, current_year: int) -> VisorYearData | None:
    errors: list[Exception] = []
    for year in [current_year, None]:
        url = _visor_url(request, year, car_type="new")
        try:
            data = _fetch_visor_facets(request, current_year, "new", url)
        except Exception as exc:
            errors.append(exc)
            continue
        if data:
            return data
    if errors:
        raise errors[-1]
    return None


def _fetch_visor_facets(
    request: VehicleQuery,
    year: int,
    car_type: str,
    url: str,
    filter_name: str = "",
    filter_value: str = "",
) -> VisorYearData | None:
    html = _fetch_text(url)
    if not _html_confirms_vehicle(request, html):
        return None
    num_found = _parse_num_found(html)
    price_stats = _parse_stat_block(html, "price")
    price_bins = _parse_range_bins(html, "price")
    if not price_bins and int(price_stats.get("count", 0)) <= 0:
        return None
    return VisorYearData(
        year=year,
        url=url,
        car_type=car_type,
        price_stats=price_stats,
        msrp_stats=_parse_stat_block(html, "msrp"),
        mileage_stats=_parse_stat_block(html, "miles"),
        price_bins=price_bins,
        num_found=num_found,
        filter_name=filter_name,
        filter_value=filter_value,
    )


def _fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return _decode(response.read())
        except (ssl.SSLCertVerificationError, TimeoutError, urllib.error.URLError) as exc:
            last_error = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code == 429:
                time.sleep(1.5 * (attempt + 1))
                continue
            try:
                context = ssl._create_unverified_context()
                with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS, context=context) as response:
                    return _decode(response.read())
            except (TimeoutError, urllib.error.URLError) as retry_exc:
                last_error = retry_exc
                if isinstance(retry_exc, urllib.error.HTTPError) and retry_exc.code == 429:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                if attempt < 2:
                    time.sleep(0.75 * (attempt + 1))
                    continue
                raise
    if last_error:
        raise last_error
    raise urllib.error.URLError("Visor request failed")


def _decode(raw: bytes) -> str:
    return raw.replace(b"\x00", b"").decode("utf-8", "replace")


def _visor_url(
    request: VehicleQuery,
    year: int | None = None,
    car_type: str = "used",
    filter_name: str = "",
    filter_value: str = "",
    include_user_trim: bool = False,
) -> str:
    model_query = source_query_model(request.make, request.model, request.trim, "visor")
    params = {
        "make": request.make,
        "model": model_query,
        "car_type": car_type,
    }
    if filter_name and filter_value:
        params[filter_name] = filter_value
    elif include_user_trim and request.trim and not source_model_contains_trim(model_query, request.trim):
        params["trim"] = request.trim
    if year:
        params["year"] = str(year)
    return f"https://visor.vin/search/filters?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)}"


def _visor_urls_for_specs(
    request: VehicleQuery,
    year: int,
    car_type: str,
    specs: list[dict[str, Any]],
) -> list[tuple[str, str, str]]:
    if specs:
        return [
            (
                _visor_url(request, year, car_type=car_type, filter_name=str(spec["name"]), filter_value=str(spec["value"])),
                str(spec["name"]),
                str(spec["value"]),
            )
            for spec in specs
        ]
    if request.trim and not source_model_contains_trim(source_query_model(request.make, request.model, request.trim, "visor"), request.trim):
        return [(_visor_url(request, year, car_type=car_type, include_user_trim=True), "trim", request.trim)]
    return [(_visor_url(request, year, car_type=car_type), "", "")]


def _used_visor_requests(
    request: VehicleQuery,
    years: list[int],
    specs: list[dict[str, Any]],
) -> list[tuple[str, int, str, str]]:
    if specs:
        rows: list[tuple[str, int, str, str]] = []
        for spec in specs:
            filter_name = str(spec["name"])
            filter_value = str(spec["value"])
            for year in _available_years(request, "used", years, filter_name, filter_value):
                rows.append((_visor_url(request, year, car_type="used", filter_name=filter_name, filter_value=filter_value), year, filter_name, filter_value))
        return rows

    filter_name = ""
    filter_value = ""
    include_trim = bool(request.trim and not source_model_contains_trim(source_query_model(request.make, request.model, request.trim, "visor"), request.trim))
    if include_trim:
        filter_name = "trim"
        filter_value = request.trim
    return [
        (
            _visor_url(request, year, car_type="used", filter_name=filter_name, filter_value=filter_value, include_user_trim=include_trim),
            year,
            filter_name,
            filter_value,
        )
        for year in _available_years(request, "used", years, filter_name, filter_value)
    ]


def _available_years(
    request: VehicleQuery,
    car_type: str,
    years: list[int],
    filter_name: str = "",
    filter_value: str = "",
) -> list[int]:
    try:
        html = _fetch_text(_visor_url(request, None, car_type=car_type, filter_name=filter_name, filter_value=filter_value))
    except Exception:
        return years
    available = {
        int(item["value"])
        for item in _parse_facet_items(html, "year")
        if str(item["value"]).isdigit() and int(item.get("count", 0)) > 0
    }
    if not available:
        return years
    year_set = set(years)
    return sorted((year for year in available if year in year_set), reverse=True)


def _matching_filter_specs(request: VehicleQuery, car_type: str, year: int | None = None) -> list[dict[str, Any]]:
    if not request.trim:
        return []
    if source_model_contains_trim(source_query_model(request.make, request.model, request.trim, "visor"), request.trim):
        return []
    try:
        html = _fetch_text(_visor_url(request, year, car_type=car_type))
    except Exception:
        return []

    matches: list[dict[str, Any]] = []
    for name in ["version", "trim"]:
        for item in _parse_facet_items(html, name):
            if _facet_value_matches_request(request, item["value"]):
                matches.append({"name": name, **item})
        if matches:
            break
    return sorted(matches, key=lambda item: int(item.get("count", 0)), reverse=True)[:8]


def _parse_facet_items(text: str, name: str) -> list[dict[str, Any]]:
    match = re.search(rf"{re.escape(name)}:\$R\[\d+\]=\[(?P<items>.*?)\]\s*(?:,\s*\w+:\$R|\}},\s*range_facets)", text, re.S)
    if not match:
        return []
    rows = []
    for item in re.finditer(r'item:"(?P<value>(?:\\"|[^"])*)",count:(?P<count>\d+)', match.group("items")):
        value = item.group("value").replace('\\"', '"')
        if not value or value == "-":
            continue
        rows.append({"value": value, "count": int(item.group("count"))})
    return rows


def _facet_value_matches_request(request: VehicleQuery, value: str) -> bool:
    return trim_value_matches_request(request, value)


def _tokens(value: str) -> list[str]:
    return trim_tokens(value)


def _parse_num_found(text: str) -> int:
    match = re.search(r"num_found:(\d+)", text)
    return int(match.group(1)) if match else 0


def _html_confirms_vehicle(request: VehicleQuery, text: str) -> bool:
    title_match = re.search(r"<title>(?P<title>.*?)</title>", text, re.I | re.S)
    title = re.sub(r"\s+", " ", title_match.group("title")).strip() if title_match else ""
    if not title or title.startswith("Visor |"):
        return False
    haystack = title.lower()
    if request.make.lower() not in haystack:
        return False
    model_query = source_query_model(request.make, request.model, request.trim, "visor")
    return all(token.lower() in haystack for token in model_query.split())


def _parse_stat_block(text: str, name: str) -> dict[str, float]:
    match = re.search(
        rf"{re.escape(name)}:\$R\[\d+\]=\{{"
        r"min:(?P<min>-?\d+(?:\.\d+)?),"
        r"max:(?P<max>-?\d+(?:\.\d+)?),"
        r"count:(?P<count>\d+),"
        r"missing:(?P<missing>\d+),"
        r"mean:(?P<mean>-?\d+(?:\.\d+)?),"
        r"median:(?P<median>-?\d+(?:\.\d+)?),"
        r"stddev:(?P<stddev>-?\d+(?:\.\d+)?)",
        text,
    )
    if not match:
        return {}
    return {key: float(value) for key, value in match.groupdict().items()}


def _parse_range_bins(text: str, name: str) -> list[dict[str, float]]:
    match = re.search(
        rf"{re.escape(name)}:\$R\[\d+\]=\{{counts:\$R\[\d+\]=\[(?P<items>.*?)\],interval:",
        text,
        re.S,
    )
    if not match:
        return []
    bins = []
    for item in re.finditer(
        r"lower_bound:(?P<lower>-?\d+(?:\.\d+)?),"
        r"upper_bound:(?P<upper>-?\d+(?:\.\d+)?),"
        r"count:(?P<count>\d+)",
        match.group("items"),
    ):
        lower = float(item.group("lower"))
        upper = float(item.group("upper"))
        count = int(item.group("count"))
        if count > 0 and upper > lower:
            bins.append({"lower": lower, "upper": upper, "count": count})
    return bins


def _listings_from_years(request: VehicleQuery, rows: list[VisorYearData], current_year: int) -> list[Listing]:
    listings: list[Listing] = []
    for row in rows:
        is_new = row.car_type == "new"
        if row.year > current_year and not is_new:
            continue
        if row.year == current_year and not is_new:
            continue
        mileage = _optional_int(row.mileage_stats.get("median"))
        bins = row.price_bins or _bins_from_stats(row.price_stats)
        display_name = _row_display_name(request, row)
        for bin_index, item in enumerate(bins):
            lower = item["lower"]
            upper = item["upper"]
            count = int(item["count"])
            sample_count = min(count, 40)
            step = (upper - lower) / max(sample_count, 1)
            for sample_index in range(sample_count):
                price = lower + step * (sample_index + 0.5)
                listings.append(
                    Listing(
                        source=NEW_SOURCE if is_new else SOURCE,
                        year=row.year,
                        price=round(price, 2),
                        trim=row.filter_value or request.trim,
                        mileage=mileage,
                        title=(
                            f"New {row.year} {display_name} Visor aggregate bin {bin_index + 1} sample {sample_index + 1}"
                            if is_new
                            else f"{row.year} {display_name} Visor aggregate bin {bin_index + 1} sample {sample_index + 1}"
                        ),
                        url=row.url,
                        dealer=(
                            f"Visor public new-market facets {row.filter_name}={row.filter_value}"
                            if is_new and row.filter_value
                            else "Visor public new-market facets"
                            if is_new
                            else f"Visor public market facets {row.filter_name}={row.filter_value}"
                            if row.filter_value
                            else "Visor public market facets"
                        ),
                        confidence="new_vehicle_facets" if is_new else "aggregate_facets",
                        condition="new" if is_new else "used",
                    )
                )
    return listings


def _row_display_name(request: VehicleQuery, row: VisorYearData) -> str:
    if not row.filter_value:
        return request.display_name
    value = row.filter_value.strip()
    if value.lower().startswith(request.model.lower()):
        return f"{request.make} {value}"
    return f"{request.make} {request.model} {value}"


def _bins_from_stats(stats: dict[str, float]) -> list[dict[str, float]]:
    if not stats:
        return []
    count = int(stats.get("count", 0))
    if count <= 0:
        return []
    median = stats.get("median") or stats.get("mean")
    if not median:
        return []
    return [{"lower": median, "upper": median + 1, "count": count}]


def _msrp_from_years(request: VehicleQuery, rows: list[VisorYearData], current_year: int) -> MSRP | None:
    for row in rows:
        if row.year == current_year and row.msrp_stats.get("median"):
            return _msrp(request, row, current_year)
    for row in rows:
        if row.msrp_stats.get("median"):
            return _msrp(request, row, row.year)
    return None


def _msrp(request: VehicleQuery, row: VisorYearData, year: int) -> MSRP:
    return MSRP(
        price=float(row.msrp_stats["median"]),
        label=f"Visor median listing MSRP for {request.display_name}",
        source=NEW_SOURCE if row.car_type == "new" else SOURCE,
        url=row.url,
        year=year,
    )


def _facet_evidence(rows: list[VisorYearData]) -> list[dict[str, Any]]:
    evidence = []
    for row in sorted(rows, key=lambda item: (item.car_type != "new", -item.year)):
        evidence.append(
            {
                "source": NEW_SOURCE if row.car_type == "new" else SOURCE,
                "kind": "visor_public_facets",
                "condition": row.car_type,
                "year": row.year,
                "url": row.url,
                "num_found": row.num_found,
                "price_stats": row.price_stats,
                "msrp_stats": row.msrp_stats,
                "mileage_stats": row.mileage_stats,
                "price_bins": row.price_bins,
                "filter_name": row.filter_name,
                "filter_value": row.filter_value,
            }
        )
    return evidence


def _optional_int(value: float | None) -> int | None:
    if value is None:
        return None
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None
