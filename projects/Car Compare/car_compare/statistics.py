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


def round_money(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 2)


def round_pct(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 4)
