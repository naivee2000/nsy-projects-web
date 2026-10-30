"""Select non-overlapping verified populations, never synthetic listing samples."""
from __future__ import annotations

from collections import defaultdict
from math import isfinite
from typing import Any
import json

from car_compare.collection_scope import query_key, scope_is_verified
from car_compare.models import BucketStats, VehicleQuery


def canonical_query_key(request: VehicleQuery) -> list[Any]:
    return query_key(request)


def verified_scope(scope: Any, request: VehicleQuery, *, complete: bool = True) -> bool:
    return bool(
        scope_is_verified(scope, request)
        and (not complete or scope.get("complete") is True)
    )


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if isfinite(number) and number >= 0 else None


def _versions(row: dict) -> frozenset[str]:
    scope = row["scope"]
    versions = scope.get("versions", scope.get("selected_versions", []))
    if not versions and row.get("filter_name") in {"version", "trim"}:
        versions = [row.get("filter_value")]
    if isinstance(versions, str):
        versions = [versions]
    return frozenset(str(value) for value in versions if value)


def _partitions(rows: list[dict]) -> list[dict] | None:
    manifests = [row["scope"].get("partition_manifest") for row in rows if row["scope"].get("partition_manifest") is not None]
    if manifests:
        entries = [item for manifest in manifests for item in manifest]
        if any(item.get("status") not in {"successful", "verified_empty"} for item in entries):
            return None
        condition = lambda value: "cpo" if value == "certified" else value
        required = {(item["year"], condition(item["condition"]), item["id"]) for item in entries if item["status"] == "successful"}
        actual = {(row["year"], condition(row["condition"]), row["scope"].get("partition_key")) for row in rows}
        if required != actual:
            return None
        unique = {}
        for row in rows:
            unique.setdefault((row["year"], condition(row["condition"]), row["scope"].get("partition_key")), row)
        return list(unique.values())
    populations: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        populations[(row["year"], row["condition"])].append(row)
    selected = []
    for population in populations.values():
        if any(row["scope"].get("expected_partitions") for row in population):
            encode = lambda value: json.dumps(value, sort_keys=True)
            actual = {encode(row["scope"].get("partition_key")) for row in population}
            expected = set().union(*(
                {encode(key) for key in row["scope"].get("expected_partitions", [])}
                for row in population
            ))
            if not expected or actual != expected:
                return None
            unique_partitions = {}
            for row in population:
                unique_partitions.setdefault(encode(row["scope"]["partition_key"]), row)
            selected.extend(unique_partitions.values())
            continue
        full = [row for row in population if not _versions(row)]
        if full:
            selected.append(max(full, key=lambda row: _number(row["price_stats"].get("count")) or 0))
            continue
        seen: set[str] = set()
        unique: dict[frozenset, dict] = {}
        for row in population:
            unique.setdefault(_versions(row), row)
        for versions, row in unique.items():
            if seen & versions:
                return None
            seen.update(versions)
            selected.append(row)
    return selected


def _histogram(row: dict) -> list[tuple[float, float, float]] | None:
    bins = []
    for item in row.get("price_bins") or []:
        if not isinstance(item, dict):
            return None
        lower, upper, count = (_number(item.get(key)) for key in ("lower", "upper", "count"))
        if lower is None or upper is None or count is None or upper <= lower:
            return None
        bins.append((lower, upper, count))
    bins.sort()
    if not bins or any(left[1] > right[0] for left, right in zip(bins, bins[1:])):
        return None
    count = _number(row["price_stats"].get("count"))
    if not count or abs(sum(item[2] for item in bins) - count) > 0.001:
        return None
    return bins


def _pooled_stats(rows: list[dict]) -> dict[str, float] | None:
    histograms = [_histogram(row) for row in rows]
    if any(hist is None for hist in histograms):
        return None
    # Different bin grids would invent within-bin detail and imply false precision.
    grid = [(low, high) for low, high, _ in histograms[0]]
    if any([(low, high) for low, high, _ in hist] != grid for hist in histograms[1:]):
        return None
    counts = [sum(hist[index][2] for hist in histograms) for index in range(len(grid))]
    total = sum(counts)
    if total <= 0:
        return None

    def quantile(fraction: float) -> float:
        cumulative = 0.0
        for (low, high), count in zip(grid, counts):
            if count and cumulative + count >= total * fraction:
                return low + (high - low) * (total * fraction - cumulative) / count
            cumulative += count
        return grid[-1][1]

    return {"count": total, "median": quantile(0.5), "q1": quantile(0.25),
            "q3": quantile(0.75), "min": grid[0][0], "max": grid[-1][1],
            "mean": sum((low + high) / 2 * count for (low, high), count in zip(grid, counts)) / total}


def aggregate_buckets(request: VehicleQuery, snapshots: list[dict], current_year: int) -> dict[int, BucketStats]:
    candidates: dict[int, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for raw in snapshots:
        if not isinstance(raw, dict) or not verified_scope(raw.get("scope"), request):
            continue
        year = raw.get("year")
        condition = {"certified": "cpo"}.get(raw.get("condition"), raw.get("condition"))
        if type(year) is not int or condition not in {"new", "used", "cpo"}:
            continue
        if request.target_year and year != request.target_year:
            continue
        if request.start_year and year < request.start_year:
            continue
        age = 0 if condition == "new" else current_year - year
        if age < 0 or age > request.max_age or (age == 0 and condition != "new"):
            continue
        stats = raw.get("price_stats")
        if not isinstance(stats, dict) or not (_number(stats.get("median")) or 0) > 0:
            continue
        if not (_number(stats.get("count")) or 0) > 0:
            continue
        row = {**raw, "condition": condition}
        source = str(row.get("source") or "unknown")
        candidates[age][source].append(row)

    buckets = {}
    for age, sources in candidates.items():
        choices = []
        for source, rows in sources.items():
            partitions = _partitions(rows)
            if not partitions:
                continue
            stats = partitions[0]["price_stats"] if len(partitions) == 1 else _pooled_stats(partitions)
            if not stats:
                continue
            count = int(_number(stats.get("count")) or 0)
            years = sorted({row["year"] for row in partitions})
            median = _number(stats.get("median"))
            method = "exact_source_median" if len(partitions) == 1 else "pooled_histogram_estimate"
            choices.append(BucketStats(
                age=age, model_year=years[0] if len(years) == 1 else None,
                model_years=years, sample_count=0, aggregate_count=count,
                observed=True, predicted=False, median=median, market_median=median,
                curve_median=median, trend_median=median,
                average=_number(stats.get("mean", stats.get("average"))),
                q1=_number(stats.get("q1")), q3=_number(stats.get("q3")),
                low=_number(stats.get("min")), high=_number(stats.get("max")),
                confidence="new_market" if age == 0 else "observed",
                pricing_method=method, pricing_sources=[source], source_counts={source: count},
            ))
        if choices:
            # Separate marketplaces overlap. Pick one population; never sum them.
            buckets[age] = max(choices, key=lambda bucket: (bucket.aggregate_count, bucket.pricing_sources))
    return buckets


def aggregate_diagnostics(request: VehicleQuery, snapshots: list[dict], buckets: list[BucketStats], current_year: int) -> list[dict]:
    by_age = {bucket.age: bucket for bucket in buckets}
    diagnostics = []
    for index, row in enumerate(snapshots):
        if not isinstance(row, dict):
            diagnostics.append({"index": index, "status": "excluded", "reason": "Invalid snapshot"})
            continue
        year = row.get("year")
        age = 0 if row.get("condition") == "new" else current_year - year if type(year) is int else None
        bucket = by_age.get(age)
        if not scope_is_verified(row.get("scope"), request):
            reason = "Unverified or incompatible search scope"
        elif row["scope"].get("complete") is not True:
            reason = "Required partitions failed or were not attempted"
        elif age == 0 and row.get("condition") != "new":
            reason = "Current-year used inventory is not a new-car baseline"
        elif bucket is None or (request.target_year and year != request.target_year) or (request.start_year and year < request.start_year):
            reason = "Outside the requested year range"
        elif not bucket.aggregate_count:
            reason = "Incomplete population or incompatible price histograms"
        elif row.get("source") not in bucket.pricing_sources:
            reason = "Alternative population excluded to avoid double counting"
        else:
            diagnostics.append({"index": index, "status": "used", "reason": bucket.pricing_method})
            continue
        diagnostics.append({"index": index, "status": "excluded", "reason": reason})
    return diagnostics
