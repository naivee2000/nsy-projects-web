from __future__ import annotations

from datetime import datetime, timezone
import html as html_lib
import json
import io
import re
import ssl
import time
import sys
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, replace
from typing import Any

from car_compare.models import Listing, MSRP, VehicleQuery
from car_compare.collection_scope import verified_scope, COLLECTION_SECONDS, VALIDATION_REVISION
from car_compare.sources.request_budget import host_slot, rate_limited, run_bounded
from car_compare.trim_match import trim_tokens, trim_value_matches_request
from car_compare.vehicle_catalog import (
    collection_start_year,
    source_model_contains_trim,
    source_query_model,
    trim_scope_profile,
)
from car_compare.vehicle_match import vehicle_text_match_score


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
    scope: dict[str, Any] = field(default_factory=dict)


def collect_visor_public_facets(request: VehicleQuery, current_year: int | None = None, deadline_at: float | None = None) -> dict[str, Any]:
    """Capture disjoint model/condition partitions with fail-closed scope proof."""
    current_year = current_year if current_year is not None else _runtime_current_year()
    deadline_at = deadline_at or time.time() + COLLECTION_SECONDS
    rows: list[VisorYearData] = []
    notes: list[str] = []
    tasks = []
    expected: dict[tuple[str, int], set[str]] = {}
    completed: dict[tuple[str, int], set[str]] = {}
    manifest: list[dict[str, Any]] = []
    try:
        models = _resolve_source_models(request, deadline_at=deadline_at)
    except Exception as exc:
        models = []
        notes.append(f"Visor catalog unavailable: {exc}")
        manifest.append({"id": "model_discovery", "condition": "all", "year": None,
                         "status": "failed", "reason": str(exc)})
    for condition in ("used", "certified", "new"):
        for model in models:
            try:
                if time.time() >= deadline_at:
                    raise TimeoutError("Collection deadline reached during catalog resolution")
                base_url = _visor_url(request, car_type=condition, model_value=model)
                base = _fetch_text(base_url, deadline_at=deadline_at)
                if not _html_confirms_vehicle(request, base) or not _html_confirms_applied_value(base, "car_type", condition):
                    raise ValueError("unverified model/condition selection")
                parent_count = _parse_num_found(base)
                if not re.search(r"num_found:\d+", base):
                    raise ValueError("Missing population count is not verified zero")
                available = {int(x["value"]): int(x["count"]) for x in _parse_facet_items(base, "year") if str(x["value"]).isdigit()}
                if parent_count and not available:
                    raise ValueError("Year facet missing from nonempty population")
                years = sorted(available, reverse=True) if condition == "new" else _requested_years(request, current_year)
                if request.target_year:
                    years = [request.target_year]
                if request.start_year:
                    years = [year for year in years if year >= request.start_year]
                if parent_count == 0:
                    for year in years or [request.target_year or current_year]:
                        manifest.append({"id": json.dumps([model, condition, year, "empty"]), "year": year, "condition": condition, "status": "verified_empty", "captured_at": time.time()})
                    continue
                specs = _specs_from_html(request, base, model)
                if request.trim and not specs:
                    raise ValueError("requested trim could not be resolved from source catalog")
                for year in years:
                    if available.get(year, 0) <= 0:
                        manifest.append({"id": json.dumps([model, condition, year, "empty"]), "year": year, "condition": condition, "status": "verified_empty", "captured_at": time.time()})
                        continue
                    for spec in specs or [{"name": "", "value": ""}]:
                        partition = json.dumps([model, spec["name"], spec["value"]], separators=(",", ":"))
                        expected.setdefault((condition, year), set()).add(partition)
                        url = _visor_url(request, year, condition, str(spec["name"]), str(spec["value"]), model_value=model)
                        tasks.append((condition, year, partition, url, spec, min(parent_count, available[year])))
                        manifest.append({"id": partition, "year": year, "condition": condition, "status": "unattempted"})
            except Exception as exc:
                notes.append(f"Visor {model} {condition}: {exc}")
                # A failed model partition makes the whole condition incomplete.
                for year in ([request.target_year] if request.target_year else range(current_year - request.max_age, current_year + 3)):
                    expected.setdefault((condition, year), set()).add(f"unresolved:{model}")
                    manifest.append({"id": f"unresolved:{model}", "year": year, "condition": condition, "status": "unattempted" if isinstance(exc, TimeoutError) else "failed", "reason": str(exc)})
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {}
        for condition, year, partition, url, spec, limit in tasks:
            futures[pool.submit(_fetch_visor_facets, request, year, condition, url, str(spec["name"]), str(spec["value"]), limit, deadline_at)] = (condition, year, partition)
        for future in as_completed(futures):
            condition, year, partition = futures[future]
            entry = next(item for item in manifest if item["id"] == partition and item["year"] == year and item["condition"] == condition)
            try:
                row = future.result()
                if row is not None:
                    entry.update(status="successful" if row.num_found else "verified_empty", captured_at=row.scope["captured_at"])
                    completed.setdefault((condition, year), set()).add(partition)
                    row.scope.update(partition_key=partition)
                    if row.num_found:
                        rows.append(row)
                else:
                    entry.update(status="failed", reason="Response scope or population could not be verified")
            except Exception as exc:
                entry.update(status="unattempted" if isinstance(exc, TimeoutError) else "failed", reason=str(exc))
                notes.append(f"Visor {condition} {year}: {exc}")
    for row in rows:
        key = (row.car_type, row.year)
        relevant = [item for item in manifest if (item["condition"] == "new" if row.car_type == "new" else item["condition"] != "new" and item["year"] == row.year)]
        row.scope.update(complete=bool(relevant) and all(item["status"] in {"successful", "verified_empty"} for item in relevant), partition_manifest=relevant, expected_partitions=sorted(expected.get(key, set())))
    listings = _listings_from_years(request, rows, current_year)
    evidence = _facet_evidence(rows)
    msrp = _msrp_from_years(request, rows, request.target_year or current_year)
    sources = []
    for source, is_new in ((SOURCE, False), (NEW_SOURCE, True)):
        captured = [r for r in rows if (r.car_type == "new") == is_new]
        partitions = [item for item in manifest if item["condition"] == "all" or (item["condition"] == "new") == is_new]
        complete = bool(partitions) and all(item["status"] in {"successful", "verified_empty"} for item in partitions)
        sources.append({"source": source, "url": _visor_url(request, car_type="new" if is_new else "used"),
                        "status": ("success" if captured else "verifiedzero") if complete else "partial" if captured else "unavailable",
                        "load_more_clicked": 0, "notes": f"Verified {len(captured)} condition/year/model partitions; aggregate counts are not individual listings."})
    complete = bool(manifest) and all(item["status"] in {"successful", "verified_empty"} for item in manifest)
    return {"query": request.raw, "status": ("success" if rows else "verifiedzero") if complete else "partial" if rows else "blocked",
            "notes": ["Visor aggregates are separate from individual marketplace samples.", *notes[:25]], "msrp": msrp.to_dict() if msrp else None,
            "sources": sources, "evidence": evidence, "partition_manifest": manifest, "listings": [x.to_dict() for x in listings], "validation_revision": VALIDATION_REVISION}


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
    max_count: int | None = None,
    deadline_at: float | None = None,
) -> VisorYearData | None:
    if deadline_at and time.time() >= deadline_at:
        raise TimeoutError("Collection deadline reached")
    html = _fetch_text(url, deadline_at=deadline_at) if deadline_at else _fetch_text(url)
    if not _html_confirms_vehicle(request, html):
        return None
    if not _html_confirms_applied_value(html, "car_type", car_type):
        return None
    if not _html_confirms_applied_value(html, "year", str(year)):
        return None
    if filter_name and filter_value and not _html_confirms_applied_value(html, filter_name, filter_value):
        return None
    num_found = _parse_num_found(html)
    if not re.search(r"num_found:\d+", html):
        return None
    params = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    if any(not _html_confirms_applied_value(html, name, values[0]) for name, values in params.items() if name in {"make", "model", "car_type", "trim", "version", "year", "drivetrain"}):
        return None
    if max_count is None:
        parent_params = {k: v[0] for k, v in params.items() if k not in {"year", "trim", "version", "drivetrain"}}
        parent = _fetch_text("https://visor.vin/search/filters?" + urllib.parse.urlencode(parent_params))
        if not _html_confirms_vehicle(request, parent):
            return None
        years = {str(x["value"]): x["count"] for x in _parse_facet_items(parent, "year")}
        max_count = min(_parse_num_found(parent), years.get(str(year), _parse_num_found(parent)))
    if num_found > max_count:
        raise ValueError("Filtered inventory exceeds verified parent population")
    price_stats = _parse_stat_block(html, "price")
    price_bins = _parse_range_bins(html, "price")
    if num_found and not price_bins and int(price_stats.get("count", 0)) <= 0:
        return None
    if int(price_stats.get("count", 0)) + int(price_stats.get("missing", 0)) != num_found:
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
        scope=verified_scope(request, years=[year], conditions=[car_type], selected_filters=_response_selections(html), adapter_revision=2),
    )


def _fetch_text(url: str, deadline_at: float | None = None) -> str:
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
    with host_slot(url, deadline=deadline_at):
        completed = run_bounded(
            [sys.executable, str(Path(__file__).with_name("http_capture.py"))],
            deadline_at=deadline_at, timeout=TIMEOUT_SECONDS,
            input=json.dumps({"url": url, "headers": dict(request.header_items()), "timeout": TIMEOUT_SECONDS}),
            text=True, capture_output=True, check=False,
        )
        result = json.loads(completed.stdout)
        status = int(result.get("status") or 0)
        if status == 429:
            rate_limited(url, result.get("retry_after"))
        if status >= 400:
            raise urllib.error.HTTPError(url, status, result.get("error", "HTTP error"), {"Retry-After": result.get("retry_after")}, io.BytesIO())
        if completed.returncode or not isinstance(result.get("text"), str):
            raise RuntimeError(result.get("error") or "Visor capture failed without a response")
        return result["text"]


def _decode(raw: bytes) -> str:
    return raw.replace(b"\x00", b"").decode("utf-8", "replace")


def _visor_url(
    request: VehicleQuery,
    year: int | None = None,
    car_type: str = "used",
    filter_name: str = "",
    filter_value: str = "",
    include_user_trim: bool = False,
    model_value: str | None = None,
) -> str:
    model_query = source_query_model(request.make, request.model, request.trim, "visor")
    params = {
        "make": request.make,
        "model": model_value or model_query,
        "car_type": car_type,
    }
    if filter_name and filter_value:
        params[filter_name] = json.dumps(filter_value) if filter_value.isdigit() else filter_value
    elif include_user_trim and request.trim and not source_model_contains_trim(model_query, request.trim):
        params["trim"] = json.dumps(request.trim) if request.trim.isdigit() else request.trim
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
    if not _html_confirms_vehicle(request, html):
        return []
    if not _html_confirms_applied_value(html, "car_type", car_type):
        return []
    if filter_name and filter_value and not _html_confirms_applied_value(html, filter_name, filter_value):
        return []
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
    if not _html_confirms_vehicle(request, html):
        return []
    if not _html_confirms_applied_value(html, "car_type", car_type):
        return []
    if year and not _html_confirms_applied_value(html, "year", str(year)):
        return []

    matches: list[dict[str, Any]] = []
    for name in ["version", "trim"]:
        for item in _parse_facet_items(html, name):
            if _facet_value_matches_request(request, item["value"]):
                matches.append({"name": name, **item})
        if matches:
            break
    limit = 16 if trim_scope_profile(request.make, request.model, request.trim)["mode"] == "family" else 8
    return sorted(matches, key=lambda item: int(item.get("count", 0)), reverse=True)[:limit]


def _parse_facet_items(text: str, name: str) -> list[dict[str, Any]]:
    match = re.search(rf"\b{re.escape(name)}:\$R\[\d+\]=\[", text)
    if not match:
        return []
    start = match.end()
    depth, quoted, escaped = 1, False, False
    end = start
    for end in range(start, len(text)):
        char = text[end]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                break
    if depth:
        return []
    rows = []
    for item in re.finditer(r'item:(?P<value>"(?:\\.|[^"\\])*"),count:(?P<count>\d+)', text[start:end]):
        value = json.loads(item.group("value"))
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
    selected = _response_selections(text)
    if str(selected.get("make", "")).casefold() != request.make.casefold():
        return False
    identity = VehicleQuery(raw=request.raw, make=request.make, model=request.model)
    models = str(selected.get("model", "")).split(",")
    return bool(models) and all(model and vehicle_text_match_score(identity, f"{request.make} {model}", source=SOURCE)["accepted"] for model in models)


def _response_selections(text: str) -> dict[str, Any]:
    """Read the response's facet query state, never arbitrary links or titles."""
    candidates = []
    for match in re.finditer(r'queryHash:("(?:\\.|[^"\\])*")', text):
        try:
            key = json.loads(json.loads(match.group(1)))
        except (ValueError, TypeError):
            continue
        if isinstance(key, list) and len(key) == 2 and key[0] == "facets" and isinstance(key[1], dict):
            if "price" in str(key[1].get("facets", "")):
                candidates.append(key[1])
    if not candidates or any(item != candidates[0] for item in candidates):
        return {}
    return candidates[0]


def _resolve_source_models(request: VehicleQuery, deadline_at: float | None = None) -> list[str]:
    catalog = []
    for condition in ("new", "used", "certified"):
        url = "https://visor.vin/search/filters?" + urllib.parse.urlencode({"make": request.make, "car_type": condition})
        text = _fetch_text(url, deadline_at=deadline_at) if deadline_at else _fetch_text(url)
        if not _html_confirms_applied_value(text, "make", request.make) or not _html_confirms_applied_value(text, "car_type", condition):
            raise ValueError("Unverified make/condition catalog")
        catalog.extend(_parse_facet_items(text, "model"))
    identity = VehicleQuery(raw=request.raw, make=request.make, model=request.model)
    models = [item["value"] for item in catalog if vehicle_text_match_score(identity, f'{request.make} {item["value"]}', source=SOURCE)["accepted"]]
    if request.make.casefold() == "porsche" and request.model == "911" and request.trim:
        if "carrera" in request.trim.casefold() or request.trim.casefold() == "base":
            models = [model for model in models if "carrera" in model.casefold()]
    if not models:
        raise ValueError("No verified source model aliases")
    return sorted(set(models))


def _specs_from_html(request: VehicleQuery, text: str, model: str) -> list[dict[str, Any]]:
    if not request.trim:
        return []
    if source_model_contains_trim(model, request.trim) and all(token in trim_tokens(model) for token in trim_tokens(request.trim)):
        return [{"name": "", "value": ""}]
    if request.make.casefold() == "porsche" and request.model == "911" and "carrera" in model.casefold():
        suffix = re.sub(r"^carrera\s*", "", request.trim, flags=re.I).strip()
        if request.trim.casefold() == "carrera":
            return [{"name": "", "value": ""}]
        request = replace(request, trim=suffix)
    for name in ("trim", "version"):
        matches = [{"name": name, **item} for item in _parse_facet_items(text, name) if _facet_value_matches_request(request, item["value"])]
        if matches:
            return matches
    return []


def _html_title(text: str) -> str:
    match = re.search(r"<title>(?P<title>.*?)</title>", text, re.I | re.S)
    if not match:
        return ""
    title = re.sub(r"<[^>]+>", " ", match.group("title"))
    return re.sub(r"\s+", " ", html_lib.unescape(title)).strip()


def _html_confirms_applied_value(text: str, name: str, value: str) -> bool:
    """Require the response to echo an applied year/trim/version selection.

    Facet option arrays alone are deliberately insufficient: an ignored query
    can still advertise the requested option while returning the broad model
    histogram. A value is accepted only in a direct ``name=value`` /
    ``name: value`` selection state; the title alone is not proof.
    """
    actual = _response_selections(text).get(name)
    def normalized(item: Any) -> set[str]:
        values = item if isinstance(item, list) else str(item or "").split(",")
        return {" ".join(trim_tokens(str(part).strip('"'))) for part in values}
    return actual is not None and normalized(actual) == normalized(value)


def _contains_token_sequence(haystack: list[str], needle: list[str]) -> bool:
    if not needle or len(needle) > len(haystack):
        return False
    return any(haystack[index : index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1))


def _requested_years(request: VehicleQuery, current_year: int) -> list[int]:
    if request.target_year:
        return [request.target_year]
    requested_start = current_year - request.max_age
    if request.start_year:
        requested_start = max(requested_start, request.start_year)
    start_year = collection_start_year(request.make, request.model, requested_start)
    years = list(range(current_year, start_year - 1, -1))
    return years


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
        mileage = _optional_int(row.mileage_stats.get("median"))
        bins = row.price_bins or _bins_from_stats(row.price_stats)
        sample_counts = _allocate_bin_samples(bins)
        display_name = _row_display_name(request, row)
        for bin_index, (item, sample_count) in enumerate(zip(bins, sample_counts)):
            lower = item["lower"]
            upper = item["upper"]
            if sample_count <= 0:
                continue
            step = (upper - lower) / max(sample_count, 1)
            market_weight = float(item["count"]) / sample_count
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
                        condition="new" if is_new else "cpo" if row.car_type == "certified" else "used",
                        market_weight=market_weight,
                        scope=row.scope,
                    )
                )
    return listings


def _allocate_bin_samples(bins: list[dict[str, float]], cap: int = 40) -> list[int]:
    """Cap a histogram without flattening the source bin proportions."""
    counts = [max(0, int(item.get("count", 0))) for item in bins]
    total = sum(counts)
    if total <= 0 or cap <= 0:
        return [0] * len(counts)
    if total <= cap:
        return counts

    positive = [index for index, count in enumerate(counts) if count > 0]
    if len(positive) > cap:
        keep = set(sorted(positive, key=lambda index: (counts[index], -index), reverse=True)[:cap])
        return [1 if index in keep else 0 for index in range(len(counts))]

    # Preserve evidence from every non-empty source bin before distributing the
    # remaining synthetic observations proportionally.
    allocated = [1 if count > 0 else 0 for count in counts]
    remaining = cap - sum(allocated)
    residual = [max(0, count - allocated[index]) for index, count in enumerate(counts)]
    residual_total = sum(residual)
    if residual_total <= 0 or remaining <= 0:
        return allocated
    quotas = [count * remaining / residual_total for count in residual]
    floors = [min(residual[index], int(quota)) for index, quota in enumerate(quotas)]
    allocated = [allocated[index] + floors[index] for index in range(len(counts))]
    remaining = cap - sum(allocated)
    order = sorted(
        range(len(counts)),
        key=lambda index: (quotas[index] - floors[index], counts[index], -index),
        reverse=True,
    )
    while remaining > 0:
        progressed = False
        for index in order:
            if allocated[index] >= counts[index]:
                continue
            allocated[index] += 1
            remaining -= 1
            progressed = True
            if remaining == 0:
                break
        if not progressed:
            break
    return allocated


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
                "scope": row.scope,
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


def _runtime_current_year() -> int:
    return datetime.now(timezone.utc).year
