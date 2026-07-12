from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class VehicleQuery:
    raw: str
    make: str
    model: str
    trim: str = ""
    start_year: int | None = None
    target_year: int | None = None
    max_age: int = 10
    corrections: list[dict[str, str]] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        parts = [self.make, self.model, self.trim]
        return " ".join(part for part in parts if part).strip()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Listing:
    source: str
    year: int
    price: float
    trim: str = ""
    mileage: int | None = None
    title: str = ""
    url: str = ""
    vin: str = ""
    dealer: str = ""
    confidence: str = "observed"
    condition: str = "used"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MSRP:
    price: float
    label: str
    source: str
    url: str
    year: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BucketStats:
    age: int
    model_year: int | None
    sample_count: int
    observed: bool
    predicted: bool
    values: list[float] = field(default_factory=list)
    model_years: list[int] = field(default_factory=list)
    average: float | None = None
    median: float | None = None
    q1: float | None = None
    q3: float | None = None
    low: float | None = None
    high: float | None = None
    trend_median: float | None = None
    source_counts: dict[str, int] = field(default_factory=dict)
    depreciation_from_previous: float | None = None
    depreciation_from_previous_pct: float | None = None
    depreciation_from_baseline: float | None = None
    depreciation_from_baseline_pct: float | None = None
    generation_adjustment_pct: float | None = None
    generation_adjustment_ratio: float | None = None
    generation_adjustment_year: int | None = None
    generation_unadjusted_median: float | None = None
    generation_adjustment_label: str = ""
    generation_adjustment_basis: str = ""
    forecast_year: int | None = None
    confidence: str = "observed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
