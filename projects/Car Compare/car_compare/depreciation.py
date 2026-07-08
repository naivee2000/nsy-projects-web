from __future__ import annotations

from collections import Counter, defaultdict
import re
from typing import Any

from car_compare.models import BucketStats, Listing, MSRP, VehicleQuery
from car_compare.resolver import resolve_vehicle_query
from car_compare.statistics import mean, median, percentile, round_money, round_pct
from car_compare.vehicle_match import matches_vehicle_text


CURRENT_YEAR = 2026
EVIDENCE_LISTING_LIMIT = 1000


def build_report(
    request: VehicleQuery,
    listings: list[Listing],
    msrp: MSRP,
    current_year: int = CURRENT_YEAR,
    generation_impact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    filtered_raw = _filter_listings(request, listings)
    filtered = dedupe_listings(filtered_raw)
    grouped: dict[int, list[Listing]] = defaultdict(list)
    for listing in filtered:
        age = _listing_age(listing, current_year)
        if 0 <= age <= request.max_age:
            grouped[age].append(listing)

    if not filtered and msrp.price <= 0:
        buckets = _empty_buckets(request, current_year)
        return _report_payload(
            request=request,
            msrp=msrp,
            filtered=filtered,
            filtered_raw=filtered_raw,
            buckets=buckets,
            current_year=current_year,
            data_quality="needs_collection",
            generation_impact=generation_impact,
        )

    buckets: list[BucketStats] = [_age_zero_bucket(msrp, grouped.get(0, []), current_year)]

    for age in range(1, request.max_age + 1):
        rows = grouped.get(age, [])
        if rows:
            values = sorted(item.price for item in rows)
            source_counts = dict(Counter(item.source for item in rows))
            buckets.append(
                BucketStats(
                    age=age,
                    model_year=current_year - age,
                    sample_count=len(values),
                    observed=True,
                    predicted=False,
                    values=values,
                    average=mean(values),
                    median=median(values),
                    q1=percentile(values, 0.25),
                    q3=percentile(values, 0.75),
                    low=min(values),
                    high=max(values),
                    source_counts=source_counts,
                    confidence="observed",
                )
            )
        else:
            buckets.append(
                BucketStats(
                    age=age,
                    model_year=current_year - age,
                    sample_count=0,
                    observed=False,
                    predicted=True,
                    source_counts={},
                    confidence="projected",
                )
            )

    _apply_trend_and_predictions(buckets, generation_impact, current_year)
    _apply_depreciation(buckets)
    data_quality = "observed" if filtered else "msrp_only"
    return _report_payload(
        request=request,
        msrp=msrp,
        filtered=filtered,
        filtered_raw=filtered_raw,
        buckets=buckets,
        current_year=current_year,
        data_quality=data_quality,
        generation_impact=generation_impact,
    )


def _report_payload(
    request: VehicleQuery,
    msrp: MSRP,
    filtered: list[Listing],
    filtered_raw: list[Listing],
    buckets: list[BucketStats],
    current_year: int,
    data_quality: str,
    generation_impact: dict[str, Any] | None,
) -> dict[str, Any]:
    source_counts = Counter(item.source for item in filtered)
    source_urls = sorted({item.url for item in filtered if item.url})
    return {
        "query": request.to_dict(),
        "resolution": resolve_vehicle_query(request),
        "msrp": msrp.to_dict(),
        "summary": {
            "displayName": request.display_name,
            "listingCount": len(filtered),
            "rawListingCount": len(filtered_raw),
            "duplicatesRemoved": max(0, len(filtered_raw) - len(filtered)),
            "sources": dict(source_counts),
            "observedAges": [bucket.age for bucket in buckets if bucket.observed],
            "predictedAges": [bucket.age for bucket in buckets if bucket.predicted],
            "currentYear": current_year,
            "maxAge": request.max_age,
            "sourceUrls": source_urls[:20],
            "dataQuality": data_quality,
            "needsSourceCapture": len(filtered) == 0,
            "needsMsrpCapture": msrp.source in {"needs_manufacturer_capture", "estimated_from_used_market"},
        },
        "buckets": [_clean_bucket(bucket) for bucket in buckets],
        "generationImpact": _clean_generation_impact(generation_impact),
        "listings": [item.to_dict() for item in filtered[:250]],
        "evidence": {
            "sources": _evidence_sources(filtered, msrp),
            "listings": [_listing_evidence(item, index + 1) for index, item in enumerate(filtered[:EVIDENCE_LISTING_LIMIT])],
            "listingLimit": EVIDENCE_LISTING_LIMIT,
            "listingCount": len(filtered),
        },
    }


def _evidence_sources(listings: list[Listing], msrp: MSRP) -> list[dict[str, Any]]:
    sources: dict[str, list[Listing]] = defaultdict(list)
    for listing in listings:
        sources[listing.source].append(listing)

    rows: list[dict[str, Any]] = []
    for source, items in sorted(sources.items()):
        urls = sorted({item.url for item in items if item.url})
        rows.append(
            {
                "source": source,
                "count": len(items),
                "conditions": dict(Counter(getattr(item, "condition", "unknown") or "unknown" for item in items)),
                "years": dict(sorted(Counter(item.year for item in items).items(), reverse=True)),
                "urlCount": len(urls),
                "urls": urls[:100],
                "kind": "aggregate_facets" if "facets" in source else "listing_rows",
            }
        )

    if msrp.url:
        rows.append(
            {
                "source": msrp.source,
                "count": 1,
                "conditions": {"msrp": 1},
                "years": {msrp.year: 1} if msrp.year else {},
                "urlCount": 1,
                "urls": [msrp.url],
                "kind": "msrp",
            }
        )
    return rows


def _listing_evidence(listing: Listing, index: int) -> dict[str, Any]:
    return {
        "index": index,
        "source": listing.source,
        "condition": getattr(listing, "condition", "unknown") or "unknown",
        "year": listing.year,
        "price": round_money(listing.price),
        "trim": listing.trim,
        "mileage": listing.mileage,
        "title": listing.title,
        "url": listing.url,
        "vin": listing.vin,
        "dealer": listing.dealer,
        "confidence": listing.confidence,
    }


def _filter_listings(request: VehicleQuery, listings: list[Listing]) -> list[Listing]:
    if not request.make and not request.model:
        return listings

    start_year = request.start_year
    target_year = request.target_year

    rows = []
    for listing in listings:
        if not matches_vehicle_text(request, listing.title, listing.trim, listing.source):
            continue
        if start_year and listing.year < start_year:
            continue
        if target_year and listing.year < target_year - 10:
            continue
        rows.append(listing)

    return rows


def _listing_age(listing: Listing, current_year: int) -> int:
    if _is_new_listing(listing) and listing.year >= current_year:
        return 0
    return current_year - listing.year


def _is_new_listing(listing: Listing) -> bool:
    condition = getattr(listing, "condition", "").lower()
    if condition == "new":
        return True
    if (listing.title or "").lower().lstrip().startswith("new "):
        return True
    haystack = f"{listing.source} {listing.confidence} {listing.title}".lower()
    return "new_vehicle" in haystack


def _age_zero_bucket(msrp: MSRP, rows: list[Listing], current_year: int) -> BucketStats:
    values = [item.price for item in rows if item.price > 0]
    source_counts = Counter(item.source for item in rows)

    values = sorted(values)
    if not values:
        return BucketStats(
            age=0,
            model_year=current_year,
            sample_count=0,
            observed=False,
            predicted=False,
            source_counts={},
            confidence="msrp_reference" if msrp.price > 0 else "needs_collection",
        )

    return BucketStats(
        age=0,
        model_year=current_year,
        sample_count=len(values),
        observed=True,
        predicted=False,
        values=values,
        average=mean(values),
        median=median(values),
        q1=percentile(values, 0.25),
        q3=percentile(values, 0.75),
        low=min(values),
        high=max(values),
        trend_median=median(values),
        source_counts=dict(source_counts),
        confidence="new_market",
    )


def _effective_msrp(msrp: MSRP, grouped: dict[int, list[Listing]]) -> float:
    if msrp.price > 0:
        return msrp.price
    if not grouped:
        return 0
    youngest_age = min(grouped)
    values = [row.price for row in grouped[youngest_age]]
    med = median(values)
    if med is None:
        return 0
    retention = 1.0
    for age in range(1, youngest_age + 1):
        retention *= _projection_rate(age, [])
    if retention <= 0:
        return med
    return med / retention


def _empty_buckets(request: VehicleQuery, current_year: int) -> list[BucketStats]:
    return [
        BucketStats(
            age=age,
            model_year=current_year - age,
            sample_count=0,
            observed=False,
            predicted=False,
            confidence="needs_collection",
        )
        for age in range(0, request.max_age + 1)
    ]


def dedupe_listings(listings: list[Listing]) -> list[Listing]:
    by_vin: dict[str, Listing] = {}
    no_vin: list[Listing] = []

    for listing in listings:
        vin = _normalize_vin(listing.vin)
        if vin:
            if vin in by_vin:
                by_vin[vin] = _merge_duplicate(by_vin[vin], listing)
            else:
                listing.vin = vin
                by_vin[vin] = listing
            continue

        match_index = None
        for index, existing in enumerate(no_vin):
            if _fallback_duplicate(existing, listing):
                match_index = index
                break
        if match_index is None:
            no_vin.append(listing)
        else:
            no_vin[match_index] = _merge_duplicate(no_vin[match_index], listing)

    return list(by_vin.values()) + no_vin


def _normalize_vin(vin: str) -> str:
    normalized = re.sub(r"[^A-HJ-NPR-Z0-9]", "", (vin or "").upper())
    if len(normalized) == 17:
        return normalized
    return ""


def _fallback_duplicate(left: Listing, right: Listing) -> bool:
    if _is_aggregate_observation(left) or _is_aggregate_observation(right):
        return False
    if left.year != right.year:
        return False
    if getattr(left, "condition", "") != getattr(right, "condition", ""):
        return False
    if abs(left.price - right.price) > 500:
        return False
    if left.mileage is not None and right.mileage is not None and abs(left.mileage - right.mileage) > 750:
        return False
    if left.dealer and right.dealer and _norm(left.dealer) != _norm(right.dealer):
        return False

    left_title = _norm(left.title or left.trim)
    right_title = _norm(right.title or right.trim)
    if not left_title or not right_title:
        return True
    left_tokens = set(left_title.split())
    right_tokens = set(right_title.split())
    shared = left_tokens & right_tokens
    required = max(2, min(len(left_tokens), len(right_tokens)) // 2)
    return len(shared) >= required


def _is_aggregate_observation(listing: Listing) -> bool:
    haystack = f"{listing.source} {listing.confidence}".lower()
    return "facets" in haystack or "aggregate" in haystack


def _merge_duplicate(left: Listing, right: Listing) -> Listing:
    sources = sorted(set(left.source.split("+")) | set(right.source.split("+")))
    left.source = "+".join(sources)
    left.price = (left.price + right.price) / 2
    left.mileage = _merge_mileage(left.mileage, right.mileage)
    left.trim = left.trim or right.trim
    left.title = _longer(left.title, right.title)
    left.url = _merge_url(left.url, right.url)
    left.vin = _normalize_vin(left.vin or right.vin)
    left.dealer = left.dealer or right.dealer
    left.confidence = "deduped"
    left.condition = _merge_condition(left.condition, right.condition)
    return left


def _merge_mileage(left: int | None, right: int | None) -> int | None:
    if left is None:
        return right
    if right is None:
        return left
    return round((left + right) / 2)


def _longer(left: str, right: str) -> str:
    return left if len(left or "") >= len(right or "") else right


def _merge_url(left: str, right: str) -> str:
    urls = [url for url in [left, right] if url]
    return " | ".join(dict.fromkeys(urls))


def _merge_condition(left: str, right: str) -> str:
    if left == right:
        return left
    if "new" in {left, right}:
        return "new"
    return left or right or "used"


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", value.lower()).strip()


def _apply_trend_and_predictions(
    buckets: list[BucketStats],
    generation_impact: dict[str, Any] | None = None,
    current_year: int = CURRENT_YEAR,
) -> None:
    last_trend = buckets[0].median if buckets[0].observed else None
    retention_rates: list[float] = []
    last_spread = (0.92, 1.08)
    generation_adjustments = _generation_adjustments_by_age(generation_impact)

    for bucket in buckets:
        bucket.forecast_year = current_year + bucket.age
        if bucket.age == 0:
            continue

        if bucket.observed and bucket.median is not None:
            raw_trend = bucket.median
            if last_trend is not None and raw_trend > last_trend:
                raw_trend = last_trend * 0.995
            bucket.trend_median = raw_trend
            if last_trend:
                retention_rates.append(max(0.65, min(0.99, raw_trend / last_trend)))
            if bucket.q1 and bucket.q3 and bucket.median:
                last_spread = (
                    max(0.75, min(0.98, bucket.q1 / bucket.median)),
                    max(1.02, min(1.25, bucket.q3 / bucket.median)),
                )
            last_trend = raw_trend
            continue

        if last_trend is None:
            bucket.predicted = False
            bucket.observed = False
            bucket.confidence = "needs_age_zero_or_observed_prior"
            continue

        rate = _projection_rate(bucket.age, retention_rates)
        projected = last_trend * rate
        adjustment = generation_adjustments.get(bucket.age)
        if adjustment:
            extra_pct = adjustment["extra_depreciation_pct"]
            projected *= max(0.5, 1 - extra_pct)
            bucket.generation_adjustment_pct = extra_pct
            bucket.generation_adjustment_label = adjustment["label"]
            bucket.generation_adjustment_basis = adjustment["basis"]
        q1_ratio, q3_ratio = last_spread
        bucket.predicted = True
        bucket.observed = False
        bucket.sample_count = 0
        bucket.trend_median = projected
        bucket.median = projected
        bucket.average = projected * 1.01
        bucket.q1 = projected * q1_ratio
        bucket.q3 = projected * q3_ratio
        bucket.low = projected * max(0.68, q1_ratio - 0.08)
        bucket.high = projected * min(1.32, q3_ratio + 0.08)
        bucket.values = []
        bucket.confidence = "long_range_projected" if bucket.age > 10 else "projected"
        last_trend = projected
        retention_rates.append(rate)


def _projection_rate(age: int, observed_rates: list[float]) -> float:
    priors = {
        1: 0.86,
        2: 0.90,
        3: 0.91,
        4: 0.92,
        5: 0.93,
        6: 0.94,
        7: 0.945,
        8: 0.95,
        9: 0.955,
        10: 0.96,
    }
    prior = priors.get(age, 0.95)
    if len(observed_rates) < 2:
        return prior
    recent = observed_rates[-3:]
    observed = sorted(recent)[len(recent) // 2]
    return max(0.78, min(0.98, (observed * 0.6) + (prior * 0.4)))


def _apply_depreciation(buckets: list[BucketStats]) -> None:
    baseline = buckets[0].trend_median if buckets[0].observed else None
    previous = baseline
    for bucket in buckets:
        current = bucket.trend_median or bucket.median
        if current is None:
            continue
        if bucket.age == 0:
            bucket.depreciation_from_previous = 0
            bucket.depreciation_from_previous_pct = 0
        elif previous:
            bucket.depreciation_from_previous = max(0, previous - current)
            bucket.depreciation_from_previous_pct = (
                bucket.depreciation_from_previous / previous if previous else None
            )
        if baseline:
            bucket.depreciation_from_baseline = max(0, baseline - current)
            bucket.depreciation_from_baseline_pct = bucket.depreciation_from_baseline / baseline
        previous = current


def _generation_adjustments_by_age(generation_impact: dict[str, Any] | None) -> dict[int, dict[str, Any]]:
    if not isinstance(generation_impact, dict):
        return {}
    if generation_impact.get("status") not in {"success", "partial"}:
        return {}
    adjustments: dict[int, dict[str, Any]] = {}
    for item in generation_impact.get("adjustments") or []:
        if not isinstance(item, dict):
            continue
        try:
            age = int(item.get("age"))
            extra_pct = float(item.get("extra_depreciation_pct"))
        except (TypeError, ValueError):
            continue
        if age <= 0 or not (0 < extra_pct < 0.5):
            continue
        adjustments[age] = {
            "age": age,
            "calendar_year": _optional_int(item.get("calendar_year")),
            "extra_depreciation_pct": max(0.0, min(0.35, extra_pct)),
            "label": str(item.get("label") or "Generation adjustment"),
            "basis": str(item.get("basis") or item.get("rationale") or ""),
        }
    return adjustments


def _clean_generation_impact(generation_impact: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(generation_impact, dict):
        return None
    allowed = {
        "query",
        "status",
        "vehicle",
        "current_generation",
        "next_generation",
        "impact_estimate",
        "adjustments",
        "historical_transitions",
        "sources",
        "notes",
    }
    cleaned = {key: value for key, value in generation_impact.items() if key in allowed}
    cleaned["adjustments"] = sorted(_generation_adjustments_by_age(generation_impact).values(), key=lambda row: row["age"])
    return cleaned


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _clean_bucket(bucket: BucketStats) -> dict[str, Any]:
    data = bucket.to_dict()
    for key, value in list(data.items()):
        if isinstance(value, float):
            if key.endswith("_pct"):
                data[key] = round_pct(value)
            else:
                data[key] = round_money(value)
        elif isinstance(value, list):
            data[key] = [round_money(item) if isinstance(item, float) else item for item in value]
    return data
