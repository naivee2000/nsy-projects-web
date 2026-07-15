from __future__ import annotations


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return float(values[0])
    ordered = sorted(values)
    rank = (len(ordered) - 1) * pct
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    fraction = rank - low
    return ordered[low] + (ordered[high] - ordered[low]) * fraction


def median(values: list[float]) -> float | None:
    return percentile(values, 0.5)


def weighted_mean(values: list[float], weights: list[float]) -> float | None:
    pairs = _weighted_pairs(values, weights)
    if not pairs:
        return None
    total_weight = sum(weight for _, weight in pairs)
    return sum(value * weight for value, weight in pairs) / total_weight


def weighted_percentile(values: list[float], weights: list[float], pct: float) -> float | None:
    pairs = _weighted_pairs(values, weights)
    if not pairs:
        return None
    first_weight = pairs[0][1]
    if all(abs(weight - first_weight) < 1e-9 for _, weight in pairs):
        return percentile([value for value, _ in pairs], pct)

    target = max(0.0, min(1.0, pct)) * sum(weight for _, weight in pairs)
    cumulative = 0.0
    for value, weight in sorted(pairs):
        cumulative += weight
        if cumulative >= target:
            return value
    return max(value for value, _ in pairs)


def weighted_median(values: list[float], weights: list[float]) -> float | None:
    return weighted_percentile(values, weights, 0.5)


def _weighted_pairs(values: list[float], weights: list[float]) -> list[tuple[float, float]]:
    if len(values) != len(weights):
        return []
    return [
        (float(value), float(weight))
        for value, weight in zip(values, weights)
        if float(weight) > 0
    ]


def round_money(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 2)


def round_pct(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 4)
