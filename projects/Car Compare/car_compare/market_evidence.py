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
        if lower is None or upper is None or count is None or count != int(count) or upper <= lower:
            return None
        bins.append((lower, upper, count))
    bins.sort()
    if not bins or any(left[1] > right[0] for left, right in zip(bins, bins[1:])):
        return None
    count = _number(row["price_stats"].get("count"))
    if not count or count != int(count) or abs(sum(item[2] for item in bins) - count) > 0.001:
        return None
    return bins


def _pooled_stats(rows: list[dict]) -> dict[str, Any] | None:
    histograms = [_histogram(row) for row in rows]
    if any(hist is None for hist in histograms):
        return None
    # Keep only edges which do not split any populated input bin. Every count
    # moves intact to one coarser bin; missing gaps are zero only because each
    # input histogram has already reconciled to its full priced count.
    bins = [item for hist in histograms for item in hist if item[2] > 0]
    edges = sorted({edge for low, high, _ in bins for edge in (low, high)})
    edges = [edge for edge in edges if not any(low < edge < high for low, high, _ in bins)]
    grid = list(zip(edges, edges[1:]))
    counts = [sum(count for low, high, count in bins if start <= low and high <= end) for start, end in grid]
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

    cumulative = 0
    interval = []
    for (low, high), count in zip(grid, counts):
        if count and cumulative + count >= total / 2:
            interval = [low, high]
            break
        cumulative += count
    midpoint = sum(interval) / 2
    median = quantile(0.5) if midpoint and (interval[1] - interval[0]) / midpoint <= 0.2 else None
    return {"count": total, "median": median, "median_interval": interval, "q1": quantile(0.25),
            "q3": quantile(0.75), "min": grid[0][0], "max": grid[-1][1],
            "mean": sum((low + high) / 2 * count for (low, high), count in zip(grid, counts)) / total}


def _population(rows: list[dict], age: int, scope_name: str) -> BucketStats | None:
    partitions = _partitions(rows)
    if not partitions:
        return None
    stats = partitions[0]["price_stats"] if len(partitions) == 1 else _pooled_stats(partitions)
    if not stats:
        return None
    count = int(_number(stats.get("count")) or 0)
    if count != _number(stats.get("count")):
        return None
    years = sorted({row["year"] for row in partitions})
    median = _number(stats.get("median"))
    source = str(partitions[0].get("source") or "unknown")
    method = "exact_source_median" if len(partitions) == 1 else "pooled_histogram_estimate" if median is not None else "histogram_range"
    return BucketStats(
        age=age, model_year=years[0] if len(years) == 1 else None,
        model_years=years, sample_count=0, aggregate_count=count,
        observed=median is not None, predicted=False, median=median, market_median=median,
        curve_median=median, trend_median=median,
        average=_number(stats.get("mean", stats.get("average"))),
        q1=_number(stats.get("q1")), q3=_number(stats.get("q3")),
        low=_number(stats.get("min")), high=_number(stats.get("max")),
        confidence="new_market" if age == 0 else "observed" if median is not None else "range_only",
        pricing_method=method, pricing_sources=[source], source_counts={source: count},
        population_scope=scope_name, median_interval=stats.get("median_interval", []),
        pricing_reason="Median interval exceeds 20% of its midpoint" if median is None else "",
    )


def _subset(rows: list[dict], condition: str) -> list[dict]:
    selected = []
    for row in rows:
        if row.get("condition") == "certified":
            row = {**row, "condition": "cpo"}
        if row["condition"] != condition:
            continue
        scope = dict(row["scope"])
        manifest = scope.get("partition_manifest")
        if manifest is not None:
            if scope.get("complete") is not True and all(item.get("status") in {"successful", "verified_empty"} for item in manifest):
                continue  # An unexplained validation failure is not repaired by selecting a subset.
            manifest = [item for item in manifest if item.get("condition") in ({"cpo", "certified"} if condition == "cpo" else {condition}) or item.get("condition") == "all"]
            scope["partition_manifest"] = manifest
            scope["complete"] = bool(manifest) and all(item.get("status") in {"successful", "verified_empty"} for item in manifest)
        if scope.get("complete") is True:
            selected.append({**row, "scope": scope})
    return selected


def aggregate_buckets(request: VehicleQuery, snapshots: list[dict], current_year: int, analysis_year: int | None = None) -> dict[int, BucketStats]:
    candidates: dict[int, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    new: dict[int, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for raw in snapshots:
        if not isinstance(raw, dict) or not verified_scope(raw.get("scope"), request, complete=False):
            continue
        year = raw.get("year")
        condition = {"certified": "cpo"}.get(raw.get("condition"), raw.get("condition"))
        if type(year) is not int or condition not in {"new", "used", "cpo"}:
            continue
        if request.target_year and year != request.target_year:
            continue
        if request.start_year and year < request.start_year:
            continue
        stats = raw.get("price_stats")
        if not isinstance(stats, dict) or not (_number(stats.get("median")) or 0) > 0:
            continue
        if not (_number(stats.get("count")) or 0) > 0:
            continue
        row = {**raw, "condition": condition}
        source = str(row.get("source") or "unknown")
        (new if condition == "new" else candidates)[year][source].append(row)

    def best(choices):
        return max(choices, key=lambda b: (b.median is not None, b.aggregate_count, b.pricing_sources)) if choices else None

    buckets: dict[int, BucketStats] = {}
    for year in sorted(new, reverse=True):
        if not current_year - 1 <= year <= current_year + 2:
            continue
        choices = [_population(rows, 0, "new") for rows in new[year].values() if all(row["scope"].get("complete") is True for row in rows)]
        baseline = best([b for b in choices if b is not None and b.median is not None])
        if baseline:
            buckets[0] = baseline
            break
    anchor = analysis_year or (buckets[0].model_year if 0 in buckets and not request.target_year else current_year)
    series = {"used_cpo": {}, "used_only": {}, "cpo_only": {}}
    for year, sources in candidates.items():
        age = anchor - year
        if not 0 < age <= request.max_age:
            continue
        for name, condition in (("used_cpo", None), ("used_only", "used"), ("cpo_only", "cpo")):
            choices = []
            for rows in sources.values():
                selected = _subset(rows, condition) if condition else [row for row in rows if row["scope"].get("complete") is True]
                if condition is None:
                    conditions = {"cpo" if item.get("condition") == "certified" else item.get("condition")
                                  for row in selected for item in row["scope"].get("partition_manifest", [row])}
                    if not {"used", "cpo"}.issubset(conditions):
                        continue
                bucket = _population(selected, age, name) if selected else None
                if bucket:
                    choices.append(bucket)
            chosen = best(choices)
            if chosen:
                series[name][age] = chosen
    minimum = 1 if request.target_year else 2
    name = next((name for name, rows in series.items() if sum(b.median is not None for b in rows.values()) >= (minimum if name == "used_cpo" else 1)), "used_cpo")
    buckets.update(series[name])
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
        elif row["scope"].get("complete") is not True and not (bucket and bucket.population_scope in {"used_only", "cpo_only"} and _subset([row], "used" if bucket.population_scope == "used_only" else "cpo")):
            reason = "Required partitions failed or were not attempted"
        elif row.get("condition") == "new" and bucket and year != bucket.model_year:
            reason = "Other new model year; retained as a separate price reference"
        elif age == 0 and row.get("condition") != "new":
            reason = "Current-year used inventory is not a new-car baseline"
        elif bucket is None or (request.target_year and year != request.target_year) or (request.start_year and year < request.start_year):
            reason = "Outside the requested year range"
        elif not bucket.aggregate_count or bucket.predicted:
            reason = "Histogram counts do not reconcile" if _histogram(row) is None else "Population unavailable for the selected series"
        elif (bucket.population_scope == "used_only" and row.get("condition") != "used") or (bucket.population_scope == "cpo_only" and row.get("condition") not in {"cpo", "certified"}):
            reason = "Separate condition reference; excluded from the selected subset"
        elif row.get("source") not in bucket.pricing_sources:
            reason = "Alternative population excluded to avoid double counting"
        else:
            diagnostics.append({"index": index, "status": "used", "reason": bucket.pricing_method})
            continue
        diagnostics.append({"index": index, "status": "excluded", "reason": reason})
    return diagnostics
