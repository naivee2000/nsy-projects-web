from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import replace
from datetime import datetime, timezone
from math import sqrt
import re
from typing import Any
from urllib.parse import parse_qsl, urlsplit

from car_compare.condition import is_implausible_new, sanitize_listing_condition
from car_compare.models import BucketStats, Listing, MSRP, VehicleQuery
from car_compare.market_evidence import aggregate_buckets, aggregate_diagnostics, verified_scope
from car_compare.resolver import resolve_vehicle_query
from car_compare.statistics import round_money, round_pct, weighted_mean, weighted_median, weighted_percentile
from car_compare.trim_normalization import build_trim_normalization
from car_compare.vehicle_catalog import model_year_bounds
from car_compare.vehicle_match import matches_vehicle_text


EVIDENCE_LISTING_LIMIT = 1000
MIN_AUTHORITATIVE_BUCKET_SAMPLES = 2
MIN_IQR_WHISKER_SAMPLES = 4
MAX_STABLE_NEIGHBOR_SPREAD = 0.30
MIN_ISOLATED_CURVE_DEVIATION = 0.35
MAX_RAW_ANCHOR_DEVIATION = 0.25


def build_report(
    request: VehicleQuery,
    listings: list[Listing],
    msrp: MSRP,
    current_year: int | None = None,
    generation_impact: dict[str, Any] | None = None,
    aggregate_snapshots: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    current_year = current_year if current_year is not None else _runtime_current_year()
    normalized_listings = [
        replace(
            listing,
            condition=sanitize_listing_condition(
                listing.condition,
                listing.title,
                listing.year,
                current_year=current_year,
                verified_new=verified_scope(listing.scope, request, complete=False),
            ),
        )
        for listing in listings
    ]
    filtered_raw = _filter_listings(request, normalized_listings)
    deduped, dedupe_diagnostics = dedupe_listings_with_diagnostics(filtered_raw)
    lifecycle_bounds = model_year_bounds(request.make, request.model)
    filtered: list[Listing] = []
    outside_horizon: list[Listing] = []
    outside_lifecycle: list[Listing] = []
    grouped: dict[int, list[Listing]] = defaultdict(list)
    aggregates = aggregate_buckets(request, aggregate_snapshots or [], current_year)
    for listing in deduped:
        if not _within_model_year_bounds(listing.year, lifecycle_bounds):
            outside_lifecycle.append(listing)
            continue
        age = _listing_age(listing, current_year)
        if 0 <= age <= request.max_age:
            filtered.append(listing)
            if not _is_aggregate_observation(listing) and (
                (age > 0 and not _is_new_listing(listing))
                or (_is_new_listing(listing) and verified_scope(listing.scope, request, complete=False))
            ):
                grouped[age].append(replace(listing, market_weight=1.0))
        else:
            outside_horizon.append(listing)

    effective_msrp = msrp
    if not grouped and not aggregates:
        buckets = _empty_buckets(request, current_year)
        trim_normalization = build_trim_normalization(request, [])
        _apply_trim_normalization(buckets, trim_normalization)
        return _report_payload(
            request=request,
            msrp=effective_msrp,
            filtered=filtered,
            filtered_raw=filtered_raw,
            deduped_count=len(deduped),
            dedupe_diagnostics=dedupe_diagnostics,
            outside_horizon=outside_horizon,
            outside_lifecycle=outside_lifecycle,
            model_year_bounds=lifecycle_bounds,
            buckets=buckets,
            current_year=current_year,
            data_quality="needs_collection",
            generation_impact=generation_impact,
            trim_normalization=trim_normalization,
            aggregate_snapshots=aggregate_snapshots,
        )

    trim_normalization = build_trim_normalization(request, [row for rows in grouped.values() for row in rows])

    buckets: list[BucketStats] = [
        _age_zero_bucket(
            effective_msrp,
            grouped.get(0, []),
            current_year,
            cohort_year=request.target_year,
        )
    ]

    for age in range(1, request.max_age + 1):
        rows = grouped.get(age, [])
        bucket_model_year = _bucket_model_year(request, current_year, age, lifecycle_bounds)
        if age in aggregates:
            buckets.append(aggregates[age])
        elif rows:
            values = sorted(item.price for item in rows)
            weights = [item.market_weight for item in rows]
            observed_median = weighted_median([item.price for item in rows], weights)
            observed_q1 = weighted_percentile([item.price for item in rows], weights, 0.25)
            observed_q3 = weighted_percentile([item.price for item in rows], weights, 0.75)
            observed_low, observed_high, outlier_count = _iqr_whiskers(
                values,
                observed_q1,
                observed_q3,
            )
            source_counts = dict(Counter(item.source for item in rows))
            model_years = [request.target_year] if request.target_year else sorted({item.year for item in rows})
            if len(rows) >= MIN_AUTHORITATIVE_BUCKET_SAMPLES:
                buckets.append(
                    BucketStats(
                        age=age,
                        model_year=bucket_model_year,
                        sample_count=len(values),
                        observed=True,
                        predicted=False,
                        values=values,
                        model_years=model_years,
                        average=weighted_mean([item.price for item in rows], weights),
                        median=observed_median,
                        q1=observed_q1,
                        q3=observed_q3,
                        low=observed_low,
                        high=observed_high,
                        market_median=observed_median,
                        curve_median=observed_median,
                        source_counts=source_counts,
                        outlier_count=outlier_count,
                        confidence="observed",
                        pricing_method="individual_sample_median",
                    )
                )
            else:
                # Keep a solitary accepted row as disclosed market evidence, but
                # never let it define the authoritative trend. This is the
                # failure mode that allowed a parsed ZIP code to become a whole
                # model year's median. The projection pass below retains the raw
                # market median and sample count while replacing chart values.
                buckets.append(
                    BucketStats(
                        age=age,
                        model_year=bucket_model_year,
                        sample_count=len(values),
                        observed=False,
                        predicted=True,
                        values=values,
                        model_years=model_years,
                        market_median=observed_median,
                        source_counts=source_counts,
                        confidence="insufficient_sample",
                    )
                )
        else:
            buckets.append(
                BucketStats(
                    age=age,
                    model_year=bucket_model_year,
                    sample_count=0,
                    observed=False,
                    predicted=True,
                    model_years=[bucket_model_year] if bucket_model_year is not None else [],
                    source_counts={},
                    confidence="projected",
                )
            )

    if 0 in aggregates:
        buckets[0] = aggregates[0]
    _apply_trim_normalization(buckets, trim_normalization)
    _stabilize_observed_curve(buckets)
    _apply_trend_and_predictions(
        buckets,
        generation_impact,
        current_year,
        generation_base_year=request.target_year or current_year,
    )
    _apply_depreciation(buckets)
    data_quality = "observed" if grouped or aggregates else "needs_collection"
    return _report_payload(
        request=request,
        msrp=effective_msrp,
        filtered=filtered,
        filtered_raw=filtered_raw,
        deduped_count=len(deduped),
        dedupe_diagnostics=dedupe_diagnostics,
        outside_horizon=outside_horizon,
        outside_lifecycle=outside_lifecycle,
        model_year_bounds=lifecycle_bounds,
        buckets=buckets,
        current_year=current_year,
        data_quality=data_quality,
        generation_impact=generation_impact,
        trim_normalization=trim_normalization,
        aggregate_snapshots=aggregate_snapshots,
    )


def _report_payload(
    request: VehicleQuery,
    msrp: MSRP,
    filtered: list[Listing],
    filtered_raw: list[Listing],
    deduped_count: int,
    dedupe_diagnostics: dict[str, Any],
    outside_horizon: list[Listing],
    outside_lifecycle: list[Listing],
    model_year_bounds: dict[str, int | None],
    buckets: list[BucketStats],
    current_year: int,
    data_quality: str,
    generation_impact: dict[str, Any] | None,
    trim_normalization: dict[str, Any],
    aggregate_snapshots: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    source_counts = Counter(item.source for item in filtered)
    source_urls = sorted({item.url for item in filtered if item.url})
    return {
        "analysisRevision": 3,
        "query": request.to_dict(),
        "resolution": resolve_vehicle_query(request),
        "msrp": msrp.to_dict(),
        "summary": {
            "analysisRevision": 3,
            "baselineAvailable": buckets[0].median is not None,
            "pricingMethods": sorted({bucket.pricing_method for bucket in buckets}),
            "aggregatePricingCount": sum(bucket.aggregate_count for bucket in buckets),
            "currentYearUsedInventory": [item.to_dict() for item in filtered if item.year == current_year and not _is_new_listing(item) and not _is_aggregate_observation(item)],
            "currentYearUsedSnapshots": [row for row in (aggregate_snapshots or []) if isinstance(row, dict) and row.get("year") == current_year and row.get("condition") in {"used", "cpo", "certified"}],
            "displayName": request.display_name,
            "listingCount": len(filtered),
            "individualListingCount": sum(not _is_aggregate_observation(item) for item in filtered),
            "aggregateObservationRows": sum(_is_aggregate_observation(item) for item in filtered),
            "rawListingCount": len(filtered_raw),
            "duplicatesRemoved": max(0, len(filtered_raw) - deduped_count),
            "dedupeDiagnostics": dedupe_diagnostics,
            "conditionDiagnostics": {
                "counts": dict(Counter((item.condition or "unknown").lower() for item in filtered)),
                "implausibleNewRows": sum(
                    1
                    for item in filtered
                    if is_implausible_new(item.condition, item.title, item.year, current_year)
                ),
                "conditionConflicts": sum(
                    1 for item in filtered if "condition_conflict" in (item.confidence or "").lower()
                ),
            },
            "trimNormalization": _clean_trim_normalization(trim_normalization),
            "curveStabilizedAges": [
                bucket.age for bucket in buckets if bucket.curve_adjustment_reason
            ],
            "outsideHorizonRows": len(outside_horizon),
            "outsideHorizonYears": dict(sorted(Counter(item.year for item in outside_horizon).items(), reverse=True)),
            "modelYearBounds": model_year_bounds,
            "outsideLifecycleRows": len(outside_lifecycle),
            "outsideLifecycleYears": dict(
                sorted(Counter(item.year for item in outside_lifecycle).items(), reverse=True)
            ),
            "sources": dict(source_counts),
            "observedAges": [bucket.age for bucket in buckets if bucket.observed],
            "predictedAges": [bucket.age for bucket in buckets if bucket.predicted],
            "insufficientSampleAges": [
                bucket.age
                for bucket in buckets
                if bucket.sample_count > 0 and not bucket.observed
            ],
            "currentYear": current_year,
            "maxAge": request.max_age,
            "sourceUrls": source_urls[:20],
            "dataQuality": data_quality,
            "needsSourceCapture": not any(bucket.observed for bucket in buckets),
            "needsMsrpCapture": (
                msrp.source in {"needs_manufacturer_capture", "estimated_from_used_market"}
                or (request.target_year is None and msrp.year is not None and msrp.year != current_year)
                or (request.target_year is not None and msrp.year != request.target_year)
            ),
        },
        "buckets": [_clean_bucket(bucket) for bucket in buckets],
        "generationImpact": _clean_generation_impact(
            generation_impact,
            request.target_year or current_year,
        ),
        "listings": [item.to_dict() for item in filtered[:250]],
        "evidence": {
            "aggregateDiagnostics": aggregate_diagnostics(request, aggregate_snapshots or [], buckets, current_year),
            "aggregateSnapshots": aggregate_snapshots or [],
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
        "market_weight": listing.market_weight,
    }


def _filter_listings(request: VehicleQuery, listings: list[Listing]) -> list[Listing]:
    if not request.make and not request.model:
        # A year-only/empty query has no vehicle identity. Passing arbitrary
        # rows through would create a cross-model depreciation curve.
        return []

    start_year = request.start_year
    target_year = request.target_year

    rows = []
    for listing in listings:
        if not matches_vehicle_text(request, listing.title, listing.trim, listing.source):
            continue
        if start_year and listing.year < start_year:
            continue
        if target_year and listing.year != target_year:
            continue
        rows.append(listing)

    return rows


def _listing_age(listing: Listing, current_year: int) -> int:
    if _is_new_listing(listing):
        return 0
    if listing.year > current_year:
        return -1
    return current_year - listing.year


def _within_model_year_bounds(year: int, bounds: dict[str, int | None]) -> bool:
    first_year = bounds.get("first")
    last_year = bounds.get("last")
    if first_year is not None and year < first_year:
        return False
    if last_year is not None and year > last_year:
        return False
    return True


def _bucket_model_year(
    request: VehicleQuery,
    current_year: int,
    age: int,
    bounds: dict[str, int | None] | None = None,
) -> int | None:
    model_year = request.target_year or (current_year - age)
    lifecycle_bounds = bounds if bounds is not None else model_year_bounds(request.make, request.model)
    return model_year if _within_model_year_bounds(model_year, lifecycle_bounds) else None


def _is_new_listing(listing: Listing) -> bool:
    title = (listing.title or "").lower().lstrip()
    if title.startswith("new arrival"):
        return False
    condition = getattr(listing, "condition", "").lower()
    return condition == "new"


def _age_zero_bucket(
    msrp: MSRP,
    rows: list[Listing],
    current_year: int,
    cohort_year: int | None = None,
) -> BucketStats:
    market_rows = [item for item in rows if item.price > 0 and _is_new_listing(item)]
    prices = [item.price for item in market_rows]
    weights = [item.market_weight for item in market_rows]
    source_counts = Counter(item.source for item in market_rows)
    model_years = sorted({item.year for item in market_rows})
    model_year = model_years[0] if len(model_years) == 1 else None

    # `prices` and `weights` are one aligned observation vector. Keep that
    # pairing for every weighted statistic; `values` is only the sorted display
    # copy returned in the report. Sorting prices alone used to attach aggregate
    # population weights to different vehicles whenever new and used rows were
    # ordered separately.
    values = sorted(prices)
    if not values:
        return BucketStats(
            age=0,
            model_year=cohort_year or current_year,
            sample_count=0,
            observed=False,
            predicted=False,
            model_years=[cohort_year or current_year],
            source_counts={},
            confidence="needs_collection",
        )

    observed_median = weighted_median(prices, weights)
    observed_q1 = weighted_percentile(prices, weights, 0.25)
    observed_q3 = weighted_percentile(prices, weights, 0.75)
    observed_low, observed_high, outlier_count = _iqr_whiskers(
        values,
        observed_q1,
        observed_q3,
    )
    return BucketStats(
        age=0,
        model_year=model_year,
        sample_count=len(values),
        observed=True,
        predicted=False,
        values=values,
        model_years=model_years,
        average=weighted_mean(prices, weights),
        median=observed_median,
        q1=observed_q1,
        q3=observed_q3,
        low=observed_low,
        high=observed_high,
        market_median=observed_median,
        curve_median=observed_median,
        trend_median=observed_median,
        source_counts=dict(source_counts),
        outlier_count=outlier_count,
        confidence="new_market",
        pricing_method="individual_sample_median",
    )


def _effective_msrp(msrp: MSRP, grouped: dict[int, list[Listing]]) -> float:
    if msrp.price > 0:
        return msrp.price
    if not grouped:
        return 0
    youngest_age = min(grouped)
    values = [row.price for row in grouped[youngest_age]]
    weights = [row.market_weight for row in grouped[youngest_age]]
    med = weighted_median(values, weights)
    if med is None:
        return 0
    retention = 1.0
    for age in range(1, youngest_age + 1):
        retention *= _projection_rate(age, [])
    if retention <= 0:
        return med
    return med / retention


def _iqr_whiskers(
    values: list[float],
    q1: float | None,
    q3: float | None,
) -> tuple[float | None, float | None, int]:
    """Return Tukey whiskers while leaving the source observations untouched."""
    if not values:
        return None, None, 0
    ordered = sorted(values)
    if len(ordered) < MIN_IQR_WHISKER_SAMPLES or q1 is None or q3 is None:
        return ordered[0], ordered[-1], 0
    iqr = max(0.0, q3 - q1)
    if iqr <= 0:
        # Weighted aggregate facets can put both quartiles in one dominant bin.
        # In that case Tukey fences would collapse to a single price and falsely
        # classify every other represented bin as an outlier.
        return ordered[0], ordered[-1], 0
    lower_fence = q1 - (1.5 * iqr)
    upper_fence = q3 + (1.5 * iqr)
    inliers = [value for value in ordered if lower_fence <= value <= upper_fence]
    if not inliers:
        return ordered[0], ordered[-1], 0
    return inliers[0], inliers[-1], len(ordered) - len(inliers)


def _empty_buckets(request: VehicleQuery, current_year: int) -> list[BucketStats]:
    lifecycle_bounds = model_year_bounds(request.make, request.model)
    return [
        BucketStats(
            age=age,
            model_year=_bucket_model_year(request, current_year, age, lifecycle_bounds),
            sample_count=0,
            observed=False,
            predicted=False,
            model_years=(
                [model_year]
                if (model_year := _bucket_model_year(request, current_year, age, lifecycle_bounds)) is not None
                else []
            ),
            forecast_year=(request.target_year or current_year) + age,
            confidence="needs_collection",
        )
        for age in range(0, request.max_age + 1)
    ]


def _apply_trim_normalization(
    buckets: list[BucketStats],
    normalization: dict[str, Any],
) -> None:
    normalized_years = normalization.get("years") or {}
    applied = normalization.get("status") == "applied"
    for bucket in buckets:
        if bucket.aggregate_count or bucket.age == 0 or not bucket.observed:
            continue
        if bucket.observed:
            bucket.curve_median = bucket.market_median if bucket.market_median is not None else bucket.median
        if not applied or bucket.model_year is None:
            continue
        year_data = normalized_years.get(bucket.model_year) or normalized_years.get(str(bucket.model_year))
        if not isinstance(year_data, dict):
            continue
        try:
            normalized_median = float(year_data["median"])
            coverage = float(year_data["coverage"])
        except (KeyError, TypeError, ValueError):
            continue
        bucket.trim_normalized_median = normalized_median
        bucket.trim_normalization_coverage_pct = coverage
        bucket.trim_cohort_counts = {
            str(key): int(value)
            for key, value in (year_data.get("cohortCounts") or {}).items()
        }
        bucket.curve_median = normalized_median


def _stabilize_observed_curve(buckets: list[BucketStats]) -> None:
    """Replace isolated, unsupported curve spikes without hiding raw evidence."""
    if len(buckets) < 3:
        return

    original_values = [
        bucket.curve_median if bucket.curve_median is not None else bucket.market_median
        for bucket in buckets
    ]
    adjustments: list[tuple[BucketStats, float, str]] = []
    for index in range(1, len(buckets) - 1):
        previous = buckets[index - 1]
        bucket = buckets[index]
        if bucket.aggregate_count:
            continue
        following = buckets[index + 1]
        if not (previous.observed and bucket.observed and following.observed):
            continue
        if not (previous.age + 1 == bucket.age == following.age - 1):
            continue

        previous_value = original_values[index - 1]
        current_value = original_values[index]
        following_value = original_values[index + 1]
        if not previous_value or not current_value or not following_value:
            continue

        anchor = sqrt(previous_value * following_value)
        neighbor_spread = abs(previous_value - following_value) / anchor
        curve_deviation = abs(current_value - anchor) / anchor
        if (
            neighbor_spread > MAX_STABLE_NEIGHBOR_SPREAD
            or curve_deviation < MIN_ISOLATED_CURVE_DEVIATION
        ):
            continue

        market_median = bucket.market_median
        normalized_mismatch = (
            market_median is not None
            and bucket.trim_normalized_median is not None
            and abs(market_median - anchor) / anchor <= MAX_RAW_ANCHOR_DEVIATION
            and abs(current_value - market_median) / market_median >= MIN_ISOLATED_CURVE_DEVIATION
        )
        if normalized_mismatch:
            adjustments.append(
                (
                    bucket,
                    market_median,
                    "Trim-normalized spike replaced by the raw market median because adjacent model years support the raw level.",
                )
            )
            continue

        independent_sources = len([count for count in bucket.source_counts.values() if count > 0])
        if bucket.sample_count < MIN_IQR_WHISKER_SAMPLES and independent_sources < 2:
            adjustments.append(
                (
                    bucket,
                    anchor,
                    "Low-sample isolated spike replaced by interpolation between adjacent model years.",
                )
            )

    for bucket, replacement, reason in adjustments:
        bucket.curve_unadjusted_median = bucket.curve_median
        bucket.curve_median = replacement
        bucket.curve_adjustment_reason = reason


def dedupe_listings(listings: list[Listing]) -> list[Listing]:
    return dedupe_listings_with_diagnostics(listings)[0]


def dedupe_listings_with_diagnostics(listings: list[Listing]) -> tuple[list[Listing], dict[str, Any]]:
    # Normalize and sort copies so the result does not depend on which source
    # happened to finish first. VIN groups are kept distinct by construction.
    normalized = [replace(item, vin=_normalize_vin(item.vin)) for item in listings]
    removed_by_method: Counter[str] = Counter()
    raw_exact_groups = _count_cross_source_exact_groups(normalized)
    vin_rows: dict[str, list[Listing]] = defaultdict(list)
    no_vin_rows: list[Listing] = []
    for listing in normalized:
        if listing.vin:
            vin_rows[listing.vin].append(listing)
        else:
            no_vin_rows.append(listing)

    by_vin = {}
    for vin, rows in sorted(vin_rows.items()):
        by_vin[vin] = _merge_group(rows)
        if len(rows) > 1:
            removed_by_method["vin"] += len(rows) - 1

    no_vin_groups: list[list[Listing]] = []
    for listing in sorted(no_vin_rows, key=_listing_sort_key):
        matches = [
            (index, method)
            for index, group in enumerate(no_vin_groups)
            if (method := _duplicate_match_method(_merge_group(group), listing))
        ]
        if len(matches) == 1:
            index, method = matches[0]
            no_vin_groups[index].append(listing)
            removed_by_method[method] += 1
        else:
            # An ambiguous row that matches more than one cluster must not
            # bridge two real vehicles together.
            no_vin_groups.append([listing])

    unmatched: list[Listing] = []
    for group in no_vin_groups:
        no_vin = _merge_group(group)
        vin_matches = [
            (vin, method)
            for vin, existing in by_vin.items()
            if (method := _duplicate_match_method(existing, no_vin))
        ]
        if len(vin_matches) == 1:
            vin, method = vin_matches[0]
            by_vin[vin] = _merge_duplicate(by_vin[vin], no_vin)
            removed_by_method[method] += 1
        else:
            unmatched.append(no_vin)

    result = sorted([*by_vin.values(), *unmatched], key=_output_listing_sort_key)
    diagnostics = {
        "rawIndividualRows": sum(1 for item in normalized if not _is_aggregate_observation(item)),
        "totalRemoved": max(0, len(normalized) - len(result)),
        "removedByMethod": dict(sorted(removed_by_method.items())),
        "rawCrossSourceExactGroups": raw_exact_groups,
        "unresolvedCrossSourceExactGroups": _count_cross_source_exact_groups(result),
    }
    return result, diagnostics


def _merge_group(rows: list[Listing]) -> Listing:
    ordered = sorted(rows, key=_listing_sort_key)
    merged = replace(ordered[0])
    for row in ordered[1:]:
        merged = _merge_duplicate(merged, row)
    return merged


def _listing_sort_key(listing: Listing) -> tuple[object, ...]:
    return (
        listing.year,
        float(listing.price),
        listing.mileage if listing.mileage is not None else -1,
        _norm(listing.title),
        _norm(listing.trim),
        _norm(listing.dealer),
        listing.vin,
        listing.source,
        listing.url,
        listing.condition,
        listing.confidence,
    )


def _output_listing_sort_key(listing: Listing) -> tuple[object, ...]:
    return (
        -listing.year,
        0 if _is_new_listing(listing) else 1,
        *_listing_sort_key(listing)[1:],
    )


def _normalize_vin(vin: str) -> str:
    normalized = re.sub(r"[^A-HJ-NPR-Z0-9]", "", (vin or "").upper())
    if len(normalized) == 17:
        return normalized
    return ""


def _fallback_duplicate(left: Listing, right: Listing) -> bool:
    return bool(_duplicate_match_method(left, right))


def _duplicate_match_method(left: Listing, right: Listing) -> str:
    if _is_aggregate_observation(left) or _is_aggregate_observation(right):
        return ""
    if left.year != right.year:
        return ""
    if left.vin and right.vin and left.vin != right.vin:
        return ""
    identity_method = _same_listing_identity_method(left, right)
    if identity_method:
        return identity_method
    if not _conditions_compatible(left.condition, right.condition):
        return ""
    overlapping_sources = bool(_source_names(left.source) & _source_names(right.source))
    if overlapping_sources:
        # Without VIN/detail/stock identity, similar cards from one source are
        # separate inventory. Source-local exact repeats are already removed by
        # the adapter before reaching global cross-source deduplication.
        if _same_source_detail_echo(left, right):
            return "same_source_detail_echo"
        return "same_source_exact" if _exact_listing_fingerprint(left) == _exact_listing_fingerprint(right) else ""
    left_fingerprint = _cross_source_exact_fingerprint(left)
    if left_fingerprint and left_fingerprint == _cross_source_exact_fingerprint(right):
        return "cross_source_exact"
    if not left.dealer or not right.dealer:
        return ""
    if _norm(left.dealer) != _norm(right.dealer):
        return ""
    if left.mileage is None or right.mileage is None:
        return ""
    if abs(left.price - right.price) > 250:
        return ""
    if abs(left.mileage - right.mileage) > 500:
        return ""

    left_title = _norm(left.title or left.trim)
    right_title = _norm(right.title or right.trim)
    if not left_title or not right_title:
        return ""
    left_tokens = set(left_title.split())
    right_tokens = set(right_title.split())
    shared = left_tokens & right_tokens
    required = max(2, min(len(left_tokens), len(right_tokens)) // 2)
    return "dealer_fuzzy" if len(shared) >= required else ""


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
    merged_condition = _merge_condition(left.condition, right.condition)
    condition_conflict = merged_condition == "unknown" and "new" in {
        (left.condition or "unknown").lower(),
        (right.condition or "unknown").lower(),
    }
    left.confidence = "deduped_condition_conflict" if condition_conflict else "deduped"
    left.condition = merged_condition
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
    left = (left or "unknown").lower()
    right = (right or "unknown").lower()
    if left == right:
        return left
    values = {left, right}
    if values == {"new", "unknown"}:
        return "new"
    if "new" in values:
        return "unknown"
    if "cpo" in values:
        return "cpo"
    if "used" in values:
        return "used"
    return "unknown"


def _conditions_compatible(left: str, right: str) -> bool:
    left = (left or "unknown").lower()
    right = (right or "unknown").lower()
    if left == right:
        return True
    return {left, right} <= {"used", "cpo", "unknown"}


def _same_listing_identity(left: Listing, right: Listing) -> bool:
    return bool(_same_listing_identity_method(left, right))


def _same_listing_identity_method(left: Listing, right: Listing) -> str:
    left_urls = _detail_listing_urls(left.url)
    right_urls = _detail_listing_urls(right.url)
    if left_urls & right_urls:
        return "detail_url"
    if not (_stock_ids(left) & _stock_ids(right)):
        return ""
    if left.dealer and right.dealer and _norm(left.dealer) == _norm(right.dealer):
        return "stock_id"
    left_title = _identity_title(left.title or left.trim)
    right_title = _identity_title(right.title or right.trim)
    if left_title and left_title == right_title:
        if left.mileage is None or right.mileage is None:
            return "stock_id"
        return "stock_id" if abs(left.mileage - right.mileage) <= 1000 else ""
    return ""


def _same_source_detail_echo(left: Listing, right: Listing) -> bool:
    left_detail = bool(_detail_listing_urls(left.url))
    right_detail = bool(_detail_listing_urls(right.url))
    if left_detail == right_detail:
        return False
    if abs(float(left.price) - float(right.price)) > 1:
        return False
    if _identity_title(left.title or left.trim) != _identity_title(right.title or right.trim):
        return False
    if left.mileage is not None and right.mileage is not None:
        return abs(left.mileage - right.mileage) <= 50
    return True


def _detail_listing_urls(value: str) -> set[str]:
    return {
        normalized
        for raw in (value or "").split(" | ")
        if _is_detail_listing_url(raw)
        if (normalized := _normalize_listing_url(raw))
    }


def _is_detail_listing_url(value: str) -> bool:
    try:
        parsed = urlsplit((value or "").strip())
    except ValueError:
        return False
    identity_keys = {"stock", "stockid", "listing", "listingid", "inventoryid", "vehicleid", "vin"}
    for key, item in parse_qsl(parsed.query, keep_blank_values=False):
        normalized_key = re.sub(r"[^a-z0-9]", "", key.lower())
        if normalized_key in identity_keys and len(re.sub(r"[^A-Z0-9]", "", item.upper())) >= 5:
            return True
    if re.search(r"[A-HJ-NPR-Z0-9]{17}", parsed.path, re.I):
        return True
    return bool(
        re.search(
            r"/(?:vehicle|listing|inventory|stock|vehicle-details?)/[a-z0-9-]{5,}(?:/|$)",
            parsed.path,
            re.I,
        )
    )


def _identity_title(value: str) -> str:
    normalized = _norm(value)
    return re.sub(r"^(?:new|used|cpo|certified)\s+", "", normalized).strip()


def _exact_listing_fingerprint(listing: Listing) -> tuple[object, ...]:
    return (
        listing.year,
        (listing.condition or "unknown").lower(),
        _identity_title(listing.title),
        _norm(listing.trim),
        float(listing.price),
        listing.mileage,
        _norm(listing.dealer),
    )


def _cross_source_exact_fingerprint(listing: Listing) -> tuple[object, ...] | None:
    trim_identity = _identity_trim(listing.trim)
    title_identity = _identity_title(listing.title or listing.trim)
    vehicle_identity = trim_identity or title_identity
    if listing.mileage is None or not vehicle_identity:
        return None
    return (
        listing.year,
        vehicle_identity,
        round(float(listing.price), 2),
        listing.mileage,
    )


def _identity_trim(value: str) -> str:
    normalized = _norm(value)
    if not normalized:
        return ""
    patterns = [
        (r"\bgt3 rs\b", "gt3 rs"),
        (r"\bgt2 rs\b", "gt2 rs"),
        (r"\bgt3\b", "gt3"),
        (r"\bturbo s\b", "turbo s"),
        (r"\bturbo\b", "turbo"),
        (r"\btarga 4 gts\b", "targa 4 gts"),
        (r"\btarga 4s\b", "targa 4s"),
        (r"\btarga 4\b", "targa 4"),
        (r"\bcarrera 4 gts\b", "carrera 4 gts"),
        (r"\bcarrera gts\b", "carrera gts"),
        (r"\bcarrera 4s\b", "carrera 4s"),
        (r"\bcarrera s\b", "carrera s"),
        (r"\bcarrera 4\b", "carrera 4"),
        (r"\bcarrera t\b", "carrera t"),
        (r"\bcarrera\b", "carrera"),
        (r"\bcompetition xdrive\b", "competition xdrive"),
        (r"\bcompetition\b", "competition"),
        (r"\bcsl\b", "csl"),
        (r"\bcs\b", "cs"),
        (r"\bgts\b", "gts"),
    ]
    for pattern, label in patterns:
        if re.search(pattern, normalized):
            return label
    normalized = re.split(r"\b(?:certified|pre owned|used|new|in transit)\b", normalized, maxsplit=1)[0]
    normalized = re.sub(r"\b(?:coupe|convertible|cabriolet|sedan|roadster)\b", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _count_cross_source_exact_groups(listings: list[Listing]) -> int:
    groups: dict[tuple[object, ...], list[Listing]] = defaultdict(list)
    for listing in listings:
        if _is_aggregate_observation(listing):
            continue
        if listing.mileage is None:
            continue
        fingerprint = (listing.year, round(float(listing.price), 2), listing.mileage)
        groups[fingerprint].append(listing)
    return sum(
        1
        for rows in groups.values()
        if len(rows) > 1 and len(set().union(*(_source_names(row.source) for row in rows))) > 1
    )


def _source_names(value: str) -> set[str]:
    return {item.strip().lower() for item in (value or "").split("+") if item.strip()}


def _normalized_listing_urls(value: str) -> set[str]:
    return {
        normalized
        for raw in (value or "").split(" | ")
        if (normalized := _normalize_listing_url(raw))
    }


def _normalize_listing_url(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    try:
        parsed = urlsplit(value)
    except ValueError:
        return ""
    host = (parsed.hostname or "").lower()
    path = re.sub(r"/+", "/", parsed.path or "/").rstrip("/") or "/"
    kept_query = []
    for key, item in parse_qsl(parsed.query, keep_blank_values=False):
        lowered = key.lower()
        if lowered.startswith("utm_") or lowered in {"gclid", "fbclid", "ref", "source", "campaign"}:
            continue
        kept_query.append((lowered, item.strip()))
    query = "&".join(f"{key}={item}" for key, item in sorted(kept_query))
    return f"{host}{path}" + (f"?{query}" if query else "")


def _stock_ids(listing: Listing) -> set[str]:
    values: set[str] = set()
    for raw_url in (listing.url or "").split(" | "):
        try:
            parsed = urlsplit(raw_url.strip())
        except ValueError:
            continue
        for key, value in parse_qsl(parsed.query, keep_blank_values=False):
            normalized_key = re.sub(r"[^a-z0-9]", "", key.lower())
            if normalized_key in {"stock", "stockid", "listing", "listingid", "inventoryid", "vehicleid"}:
                _add_stock_id(values, value)
        for match in re.finditer(
            r"(?:stock|listing|inventory|vehicle)[/_=-]+([a-z0-9-]{5,})",
            parsed.path,
            re.I,
        ):
            _add_stock_id(values, match.group(1))
    for match in re.finditer(r"\bstock\s*(?:#|no\.?|id)?\s*[:#-]?\s*([a-z0-9-]{5,})\b", listing.title or "", re.I):
        _add_stock_id(values, match.group(1))
    return values


def _add_stock_id(values: set[str], value: str) -> None:
    normalized = re.sub(r"[^A-Z0-9]", "", (value or "").upper())
    if len(normalized) >= 5:
        values.add(normalized)


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", value.lower()).strip()


def _apply_trend_and_predictions(
    buckets: list[BucketStats],
    generation_impact: dict[str, Any] | None = None,
    current_year: int | None = None,
    generation_base_year: int | None = None,
) -> None:
    current_year = current_year if current_year is not None else _runtime_current_year()
    last_trend = buckets[0].curve_median or buckets[0].trend_median or buckets[0].median
    baseline_forecast_year = buckets[0].model_year or (
        max(buckets[0].model_years) if buckets[0].model_years else current_year
    )
    retention_rates: list[float] = []
    last_spread = (0.92, 1.08)
    for bucket in buckets:
        if bucket.age == 0:
            bucket.forecast_year = baseline_forecast_year
        else:
            bucket.forecast_year = baseline_forecast_year + bucket.age
        if bucket.age == 0:
            continue

        if bucket.observed and (bucket.curve_median is not None or bucket.median is not None):
            raw_trend = bucket.curve_median if bucket.curve_median is not None else bucket.median
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
        q1_ratio, q3_ratio = last_spread
        bucket.predicted = True
        bucket.pricing_method = "used_market_forecast" if buckets[0].median is None else "market_forecast"
        bucket.observed = False
        bucket.trend_median = projected
        bucket.curve_median = projected
        bucket.median = projected
        bucket.average = projected * 1.01
        bucket.q1 = projected * q1_ratio
        bucket.q3 = projected * q3_ratio
        bucket.low = projected * max(0.68, q1_ratio - 0.08)
        bucket.high = projected * min(1.32, q3_ratio + 0.08)
        if bucket.sample_count > 0:
            bucket.confidence = (
                "long_range_projected_sparse_sample"
                if bucket.age > 10
                else "projected_sparse_sample"
            )
        else:
            beyond_history = bucket.model_year is None
            if bucket.age > 10 and beyond_history:
                bucket.confidence = "long_range_projected_beyond_model_history"
            elif beyond_history:
                bucket.confidence = "projected_beyond_model_history"
            else:
                bucket.confidence = "long_range_projected" if bucket.age > 10 else "projected"
        last_trend = projected
        retention_rates.append(rate)
    _apply_generation_adjustments(
        buckets,
        generation_impact,
        generation_base_year if generation_base_year is not None else current_year,
    )


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
    baseline = buckets[0].curve_median or buckets[0].trend_median or buckets[0].median
    previous = baseline
    for bucket in buckets:
        bucket.value_change_from_previous = None
        bucket.value_change_from_previous_pct = None
        bucket.value_change_from_baseline = None
        bucket.value_change_from_baseline_pct = None
        current = bucket.curve_median or bucket.trend_median or bucket.median
        if current is None:
            previous = None
            continue
        if bucket.age == 0:
            bucket.depreciation_from_previous = 0
            bucket.depreciation_from_previous_pct = 0
            bucket.value_change_from_previous = 0
            bucket.value_change_from_previous_pct = 0
        elif previous:
            value_change = current - previous
            bucket.value_change_from_previous = value_change
            bucket.value_change_from_previous_pct = value_change / previous
            bucket.depreciation_from_previous = max(0, -value_change)
            bucket.depreciation_from_previous_pct = (
                bucket.depreciation_from_previous / previous if previous else None
            )
        if baseline:
            value_change = current - baseline
            bucket.value_change_from_baseline = value_change
            bucket.value_change_from_baseline_pct = value_change / baseline
            bucket.depreciation_from_baseline = max(0, -value_change)
            bucket.depreciation_from_baseline_pct = bucket.depreciation_from_baseline / baseline
        previous = current


def _apply_generation_adjustments(
    buckets: list[BucketStats],
    generation_impact: dict[str, Any] | None,
    current_year: int,
) -> None:
    adjustments = sorted(_generation_adjustments_by_age(generation_impact, current_year).values(), key=lambda row: row["age"])
    if not adjustments:
        return
    for bucket in buckets:
        # A generation event is a forecast scenario, not a correction to market
        # evidence already observed for a historical model year.
        if bucket.age == 0 or not bucket.predicted:
            continue
        active = [item for item in adjustments if item["age"] <= bucket.age]
        if not active:
            continue
        ratio = 1.0
        for item in active:
            ratio *= max(0.5, 1 - item["extra_depreciation_pct"])
        if ratio >= 1:
            continue
        event = active[-1]
        basis_value = bucket.trend_median or bucket.median
        if basis_value is None:
            continue
        bucket.generation_unadjusted_median = basis_value
        bucket.generation_adjustment_pct = 1 - ratio
        bucket.generation_adjustment_ratio = ratio
        bucket.generation_adjustment_year = event.get("calendar_year")
        bucket.generation_adjustment_label = event["label"] if bucket.age == event["age"] else "Post-generation adjusted curve"
        bucket.generation_adjustment_basis = event["basis"]
        if bucket.trend_median is not None:
            bucket.trend_median *= ratio
        _scale_bucket_prices(bucket, ratio)


def _scale_bucket_prices(bucket: BucketStats, scale: float) -> None:
    if scale <= 0:
        return
    for field in ("average", "median", "curve_median", "q1", "q3", "low", "high"):
        value = getattr(bucket, field)
        if value is not None:
            setattr(bucket, field, value * scale)


def _generation_adjustments_by_age(
    generation_impact: dict[str, Any] | None,
    current_year: int,
) -> dict[int, dict[str, Any]]:
    if not isinstance(generation_impact, dict):
        return {}
    if generation_impact.get("status") not in {"success", "partial"}:
        return {}
    adjustments: dict[int, dict[str, Any]] = {}
    for item in generation_impact.get("adjustments") or []:
        if not isinstance(item, dict):
            continue
        try:
            extra_pct = float(item.get("extra_depreciation_pct"))
        except (TypeError, ValueError):
            continue
        calendar_year = _optional_int(item.get("calendar_year"))
        age = _effective_adjustment_age(item, current_year)
        if age <= 0 or not (0 < extra_pct < 0.5):
            continue
        adjustments[age] = {
            "age": age,
            "calendar_year": calendar_year or current_year + age,
            "extra_depreciation_pct": max(0.0, min(0.35, extra_pct)),
            "label": str(item.get("label") or "Generation adjustment"),
            "basis": str(item.get("basis") or item.get("rationale") or ""),
        }
    return adjustments


def _effective_adjustment_age(item: dict[str, Any], current_year: int) -> int:
    calendar_year = _optional_int(item.get("calendar_year"))
    if calendar_year and calendar_year >= current_year:
        return calendar_year - current_year
    try:
        return int(item.get("age"))
    except (TypeError, ValueError):
        return -1


def _clean_generation_impact(generation_impact: dict[str, Any] | None, current_year: int) -> dict[str, Any] | None:
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
    cleaned["adjustments"] = sorted(_generation_adjustments_by_age(generation_impact, current_year).values(), key=lambda row: row["age"])
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


def _clean_trim_normalization(value: dict[str, Any]) -> dict[str, Any]:
    def clean(item: Any) -> Any:
        if isinstance(item, float):
            return round(item, 4)
        if isinstance(item, dict):
            return {str(key): clean(child) for key, child in item.items() if key != "years"}
        if isinstance(item, list):
            return [clean(child) for child in item]
        return item

    return clean(value)


def _runtime_current_year() -> int:
    return datetime.now(timezone.utc).year
