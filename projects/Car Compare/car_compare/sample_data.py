from __future__ import annotations

from datetime import datetime, timezone

from car_compare.models import Listing, MSRP, VehicleQuery


BMW_M4_COMPETITION_SAMPLE = [
    Listing("edmunds_browser", 2025, 83999, "Competition Coupe", 4461, "2025 BMW M4 Competition Coupe", "https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&make=bmw&model=m4"),
    Listing("autotrader_browser", 2025, 78750, "Competition Coupe", 2000, "Used 2025 BMW M4 Competition Coupe", "https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4/new-york-ny?searchRadius=0&startYear=2021&zip=10001"),
    Listing("sample", 2025, 79991, "Competition Coupe", 6200, "2025 BMW M4 Competition Coupe"),
    Listing("sample", 2025, 84590, "Competition xDrive Coupe", 5100, "2025 BMW M4 Competition xDrive Coupe"),
    Listing("sample", 2025, 82979, "Competition Coupe", 7300, "2025 BMW M4 Competition Coupe"),
    Listing("edmunds_browser", 2024, 67991, "Competition xDrive Convertible", 24741, "2024 BMW M4 Competition xDrive Convertible", "https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&make=bmw&model=m4"),
    Listing("sample", 2024, 79988, "Competition xDrive Coupe", 11800, "2024 BMW M4 Competition xDrive Coupe"),
    Listing("sample", 2024, 74995, "Competition Coupe", 15800, "2024 BMW M4 Competition Coupe"),
    Listing("sample", 2024, 72491, "Competition Coupe", 22100, "2024 BMW M4 Competition Coupe"),
    Listing("sample", 2024, 75999, "Competition xDrive Coupe", 18200, "2024 BMW M4 Competition xDrive Coupe"),
    Listing("edmunds_browser", 2023, 83015, "Competition xDrive Coupe", 22958, "2023 BMW M4 Competition xDrive Coupe", "https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&make=bmw&model=m4"),
    Listing("edmunds_browser", 2023, 66500, "Competition xDrive Coupe", 52395, "2023 BMW M4 Competition xDrive Coupe", "https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&make=bmw&model=m4"),
    Listing("autotrader_browser", 2023, 99500, "Competition Coupe", 1000, "Used 2023 BMW M4 Competition Coupe", "https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4/new-york-ny?searchRadius=0&startYear=2021&zip=10001"),
    Listing("sample", 2023, 75999, "Competition xDrive Coupe", 28900, "2023 BMW M4 Competition xDrive Coupe"),
    Listing("sample", 2023, 79588, "Competition Coupe", 19000, "2023 BMW M4 Competition Coupe"),
    Listing("sample", 2023, 70491, "Competition Coupe", 44100, "2023 BMW M4 Competition Coupe"),
    Listing("edmunds_browser", 2022, 87491, "Competition xDrive Coupe", 11483, "2022 BMW M4 Coupe Competition xDrive", "https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&make=bmw&model=m4"),
    Listing("sample", 2022, 68500, "Competition Coupe", 32700, "2022 BMW M4 Competition Coupe"),
    Listing("sample", 2022, 72500, "Competition xDrive Coupe", 29000, "2022 BMW M4 Competition xDrive Coupe"),
    Listing("sample", 2022, 66991, "Competition Coupe", 41100, "2022 BMW M4 Competition Coupe"),
    Listing("sample", 2022, 69500, "Competition Coupe", 38000, "2022 BMW M4 Competition Coupe"),
    Listing("edmunds_browser", 2021, 67725, "Competition Coupe", 18698, "2021 BMW M4 Competition Coupe", "https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&make=bmw&model=m4"),
    Listing("sample", 2021, 59991, "Competition Coupe", 48000, "2021 BMW M4 Competition Coupe"),
    Listing("sample", 2021, 64900, "Competition Coupe", 34200, "2021 BMW M4 Competition Coupe"),
    Listing("sample", 2021, 57500, "Competition Coupe", 60400, "2021 BMW M4 Competition Coupe"),
    Listing("sample", 2021, 61995, "Competition Coupe", 51900, "2021 BMW M4 Competition Coupe"),
]


REFERENCE_MSRP_YEAR = 2026


def default_msrp_for(request: VehicleQuery, current_year: int | None = None) -> MSRP:
    runtime_year = current_year if current_year is not None else datetime.now(timezone.utc).year
    if request.target_year and request.target_year != REFERENCE_MSRP_YEAR:
        return MSRP(
            price=0,
            label=f"Needs official {request.target_year} historical MSRP capture",
            source="needs_manufacturer_capture",
            url="",
            year=request.target_year,
        )
    if request.target_year is None and runtime_year != REFERENCE_MSRP_YEAR:
        return MSRP(
            price=0,
            label=f"Needs official {runtime_year} MSRP capture",
            source="needs_manufacturer_capture",
            url="",
            year=runtime_year,
        )
    if request.make == "BMW" and request.model == "M4" and request.trim == "Competition":
        return MSRP(
            price=86600,
            label="2026 historical BMW M4 Competition Coupe starting MSRP (demo reference)",
            source="bmwusa_demo_reference_2026",
            url="https://www.bmwusa.com/vehicles/m-series/bmw-4-series-m-models/bmw-m4-coupe.html",
            year=2026,
        )
    return MSRP(
        price=0,
        label="Needs official MSRP capture",
        source="needs_manufacturer_capture",
        url="",
        year=None,
    )


def sample_listings_for(request: VehicleQuery) -> list[Listing]:
    name = request.display_name.lower()
    if "bmw" in name and "m4" in name:
        return list(BMW_M4_COMPETITION_SAMPLE)
    return []
