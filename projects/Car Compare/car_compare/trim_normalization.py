from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
import re
from typing import Any

from car_compare.models import Listing, VehicleQuery
from car_compare.statistics import weighted_median
from car_compare.trim_match import trim_tokens
from car_compare.vehicle_catalog import trim_candidates


MIN_COHORT_ROWS_PER_YEAR = 2
MIN_COHORTS_PER_YEAR = 2
MIN_REFERENCE_COVERAGE = 0.70
MIN_YEAR_RETENTION = 0.80

GENERIC_TRIM_NOISE_TOKENS = {
    "automatic",
    "cabriolet",
    "car",
    "certified",
    "cpo",
    "convertible",
    "coupe",
    "cvt",
    "dct",
    "door",
    "doors",
    "hatchback",
    "in",
    "inventory",
    "manual",
    "new",
    "owned",
    "pre",
    "roadster",
    "sedan",
    "suv",
    "transmission",
    "used",
    "vehicle",
    "wagon",
}
GENERIC_TRIM_TOKEN_LIMIT = 6
GENERIC_CONFIGURATION_ONLY_TOKENS = {
    "4matic",
    "4wd",
    "4x4",
    "awd",
    "electric",
    "fwd",
    "hybrid",
    "phev",
    "plug",
    "quattro",
    "rwd",
    "shawd",
    "xdrive",
}


def build_trim_normalization(
    request: VehicleQuery,
    listings: list[Listing],
) -> dict[str, Any]:
    if request.trim:
        return _empty_result("exact_trim")

    rows_by_year: dict[int, list[tuple[Listing, str]]] = defaultdict(list)
    excluded_aggregate = 0
    excluded_unknown = 0
    cohort_strategies: Counter[str] = Counter()
    for listing in listings:
        if _is_aggregate(listing):
            excluded_aggregate += 1
            continue
        cohort, strategy = _canonical_trim_cohort_with_strategy(request, listing)
        if not cohort:
            excluded_unknown += 1
            continue
        cohort_strategies[strategy] += 1
        rows_by_year[listing.year].append((listing, cohort))

    eligible_rows: dict[int, list[tuple[Listing, str]]] = {}
    raw_mix: dict[int, dict[str, float]] = {}
    for year, rows in rows_by_year.items():
        counts = Counter(cohort for _, cohort in rows)
        supported = {cohort for cohort, count in counts.items() if count >= MIN_COHORT_ROWS_PER_YEAR}
        if len(supported) < MIN_COHORTS_PER_YEAR:
            continue
        accepted = [(listing, cohort) for listing, cohort in rows if cohort in supported]
        accepted_counts = Counter(cohort for _, cohort in accepted)
        total = sum(accepted_counts.values())
        eligible_rows[year] = accepted
        raw_mix[year] = {cohort: count / total for cohort, count in accepted_counts.items()}

    if len(eligible_rows) < 2:
        result = _empty_result("insufficient_coverage")
        result.update(
            {
                "excludedAggregateRows": excluded_aggregate,
                "excludedUnknownTrimRows": excluded_unknown,
                "eligibleYearCount": len(eligible_rows),
                "cohortStrategyCounts": dict(sorted(cohort_strategies.items())),
            }
        )
        return result

    reference = _reference_mix(raw_mix)
    year_results: dict[int, dict[str, Any]] = {}
    effective_mix: dict[int, dict[str, float]] = {}
    for year, rows in eligible_rows.items():
        counts = Counter(cohort for _, cohort in rows)
        available = set(counts)
        coverage = sum(reference.get(cohort, 0.0) for cohort in available)
        if coverage < MIN_REFERENCE_COVERAGE or len(available) < MIN_COHORTS_PER_YEAR:
            continue
        row_weights = [reference[cohort] / counts[cohort] / coverage for _, cohort in rows]
        median = weighted_median([listing.price for listing, _ in rows], row_weights)
        if median is None:
            continue
        normalized_mix = {cohort: reference[cohort] / coverage for cohort in available}
        effective_mix[year] = normalized_mix
        year_results[year] = {
            "median": median,
            "coverage": coverage,
            "cohortCounts": dict(sorted(counts.items())),
            "effectiveMix": dict(sorted(normalized_mix.items())),
        }

    retention = len(year_results) / len(eligible_rows) if eligible_rows else 0.0
    raw_comparable_mix = {year: raw_mix[year] for year in year_results}
    raw_divergence = _max_total_variation(raw_comparable_mix)
    normalized_divergence = _max_total_variation(effective_mix)
    status = "applied" if len(year_results) >= 2 and retention >= MIN_YEAR_RETENTION else "insufficient_coverage"
    if status != "applied":
        year_results = {}

    return {
        "status": status,
        "method": "fixed_reference_trim_mix",
        "minimumReferenceCoverage": MIN_REFERENCE_COVERAGE,
        "minimumYearRetention": MIN_YEAR_RETENTION,
        "referenceMix": dict(sorted(reference.items())),
        "rawMaxTotalVariation": raw_divergence,
        "normalizedMaxTotalVariation": normalized_divergence,
        "divergenceRatio": (
            normalized_divergence / raw_divergence
            if raw_divergence > 0
            else 0.0
        ),
        "eligibleYearCount": len(eligible_rows),
        "normalizedYearCount": len(year_results),
        "yearRetention": retention,
        "excludedAggregateRows": excluded_aggregate,
        "excludedUnknownTrimRows": excluded_unknown,
        "cohortStrategyCounts": dict(sorted(cohort_strategies.items())),
        "years": year_results,
    }


def canonical_trim_cohort(request: VehicleQuery, listing: Listing) -> str:
    return _canonical_trim_cohort_with_strategy(request, listing)[0]


def _canonical_trim_cohort_with_strategy(
    request: VehicleQuery,
    listing: Listing,
) -> tuple[str, str]:
    text = _normalized_text(f"{listing.trim} {listing.title}")
    key = (request.make, request.model)
    if key == ("Porsche", "911"):
        if re.search(r"\b(?:gt2|gt3|speedster|dakar)\b|\bsport classic\b", text):
            return "gt_special", "explicit_profile"
        if re.search(r"\bturbo\b", text):
            return "turbo", "explicit_profile"
        if re.search(r"\bgts\b", text):
            return "gts", "explicit_profile"
        if re.search(r"\b(?:carrera 4s|carrera s|targa 4s)\b", text):
            return "s", "explicit_profile"
        if re.search(r"\b(?:carrera|targa 4)\b", text):
            return "base", "explicit_profile"
        return "", "unknown"
    if key == ("BMW", "M4"):
        if re.search(r"\b(?:competition|csl|cs|gts)\b", text):
            return "performance", "explicit_profile"
        return ("standard", "explicit_profile") if re.search(r"\bm4\b", text) else ("", "unknown")

    tokens = trim_tokens(text)
    matches: list[tuple[int, str]] = []
    for candidate in trim_candidates(request.make, request.model):
        candidate_tokens = trim_tokens(candidate)
        if candidate_tokens and _contains_sequence(tokens, candidate_tokens):
            matches.append((len(candidate_tokens), "_".join(candidate_tokens)))
    if matches:
        matches.sort(reverse=True)
        cohort = matches[0][1]
        return _with_configuration_suffix(cohort, tokens), "catalog"

    generic_tokens = _generic_trim_tokens(request, listing.trim)
    if generic_tokens:
        return "_".join(generic_tokens), "generic"
    return "", "unknown"


def _with_configuration_suffix(cohort: str, observed_tokens: list[str]) -> str:
    cohort_tokens = set(cohort.split("_"))
    tags: list[str] = []
    if "plug" in observed_tokens and "hybrid" in observed_tokens:
        tags.append("phev")
    elif "phev" in observed_tokens:
        tags.append("phev")
    elif "hybrid" in observed_tokens:
        tags.append("hybrid")

    drivetrain = ""
    if set(observed_tokens) & {"4matic", "awd", "quattro", "shawd", "xdrive"}:
        drivetrain = "awd"
    elif set(observed_tokens) & {"4wd", "4x4"}:
        drivetrain = "4wd"
    elif "fwd" in observed_tokens:
        drivetrain = "fwd"
    elif "rwd" in observed_tokens:
        drivetrain = "rwd"
    if drivetrain and not (cohort_tokens & {"4matic", "awd", "4wd", "4x4", "fwd", "quattro", "rwd", "shawd", "xdrive"}):
        tags.append(drivetrain)
    return "_".join([cohort, *tags]) if tags else cohort


def _generic_trim_tokens(request: VehicleQuery, value: str) -> list[str]:
    """Return a conservative trim/configuration label for uncatalogued models."""
    tokens = trim_tokens(value)
    if not tokens:
        return []
    tokens = _remove_sequence(tokens, trim_tokens(request.make))
    tokens = _remove_sequence(tokens, trim_tokens(request.model))
    normalized = [
        token
        for token in tokens
        if token not in GENERIC_TRIM_NOISE_TOKENS
        and not re.fullmatch(r"(?:19|20)\d{2}", token)
    ]
    if (
        not normalized
        or len(normalized) > GENERIC_TRIM_TOKEN_LIMIT
        or set(normalized) <= GENERIC_CONFIGURATION_ONLY_TOKENS
    ):
        return []
    return normalized


def _remove_sequence(tokens: list[str], sequence: list[str]) -> list[str]:
    if not sequence or len(sequence) > len(tokens):
        return tokens
    result = list(tokens)
    while True:
        for index in range(len(result) - len(sequence) + 1):
            if result[index : index + len(sequence)] == sequence:
                result = result[:index] + result[index + len(sequence) :]
                break
        else:
            return result


def _reference_mix(year_mix: dict[int, dict[str, float]]) -> dict[str, float]:
    reference: Counter[str] = Counter()
    year_count = len(year_mix)
    for mix in year_mix.values():
        for cohort, share in mix.items():
            reference[cohort] += share / year_count
    total = sum(reference.values())
    return {cohort: share / total for cohort, share in reference.items()} if total else {}


def _max_total_variation(mixes: dict[int, dict[str, float]]) -> float:
    return max(
        (_total_variation(left, right) for left, right in combinations(mixes.values(), 2)),
        default=0.0,
    )


def _total_variation(left: dict[str, float], right: dict[str, float]) -> float:
    return 0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in set(left) | set(right))


def _is_aggregate(listing: Listing) -> bool:
    haystack = f"{listing.source} {listing.confidence}".lower()
    return "facet" in haystack or "aggregate" in haystack


def _normalized_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def _contains_sequence(haystack: list[str], needle: list[str]) -> bool:
    if not needle or len(needle) > len(haystack):
        return False
    return any(haystack[index : index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1))


def _empty_result(status: str) -> dict[str, Any]:
    return {
        "status": status,
        "method": "fixed_reference_trim_mix",
        "minimumReferenceCoverage": MIN_REFERENCE_COVERAGE,
        "minimumYearRetention": MIN_YEAR_RETENTION,
        "referenceMix": {},
        "rawMaxTotalVariation": 0.0,
        "normalizedMaxTotalVariation": 0.0,
        "divergenceRatio": 0.0,
        "eligibleYearCount": 0,
        "normalizedYearCount": 0,
        "yearRetention": 0.0,
        "excludedAggregateRows": 0,
        "excludedUnknownTrimRows": 0,
        "cohortStrategyCounts": {},
        "years": {},
    }
