from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from urllib.parse import quote, quote_plus, urlencode

from car_compare.models import VehicleQuery
from car_compare.resolver import resolve_vehicle_query
from car_compare.vehicle_catalog import source_model_profile, source_query_model


TOP_US_BRAND_SOURCE_NOTE = (
    "Seeded from 2025 full-year U.S. brand sales reports; EV-only brands such as "
    "Tesla, Rivian, Lucid, Polestar, and VinFast are included in the same coverage set."
)

TOP_US_BRANDS = [
    "Toyota",
    "Ford",
    "Chevrolet",
    "Honda",
    "Hyundai",
    "Nissan",
    "Kia",
    "GMC",
    "Subaru",
    "Jeep",
    "Tesla",
    "RAM",
    "Mazda",
    "BMW",
    "Lexus",
    "Volkswagen",
    "Mercedes-Benz",
    "Buick",
    "Cadillac",
    "Audi",
    "Acura",
    "Chrysler",
    "Volvo",
    "Lincoln",
    "Dodge",
    "Mitsubishi",
    "Genesis",
    "Porsche",
    "INFINITI",
    "Rivian",
    "MINI",
    "Land Rover",
    "Lucid",
    "Polestar",
    "Alfa Romeo",
    "Maserati",
    "Bentley",
    "Lamborghini",
    "VinFast",
    "Rolls-Royce",
]


MANUFACTURER_URLS = {
    "Acura": "https://www.acura.com/tools/inventory",
    "Alfa Romeo": "https://www.alfaromeousa.com/new-inventory",
    "Aston Martin": "https://www.astonmartin.com/en-us/models",
    "Audi": "https://www.audiusa.com/us/web/en/inventory.html",
    "Bentley": "https://www.bentleymotors.com/en/models.html",
    "BMW": "https://www.bmwusa.com/vehicles.html",
    "Buick": "https://www.buick.com/shopping/inventory/",
    "Cadillac": "https://www.cadillac.com/shopping/inventory/",
    "Chevrolet": "https://www.chevrolet.com/shopping/inventory/",
    "Chrysler": "https://www.chrysler.com/new-inventory.html",
    "Dodge": "https://www.dodge.com/new-inventory.html",
    "Ferrari": "https://www.ferrari.com/en-US/auto/car-range",
    "FIAT": "https://www.fiatusa.com/new-inventory.html",
    "Ford": "https://shop.ford.com/inventory/",
    "Genesis": "https://www.genesis.com/us/en/inventory",
    "GMC": "https://www.gmc.com/shopping/inventory/",
    "Honda": "https://automobiles.honda.com/tools/search-inventory",
    "Hyundai": "https://www.hyundaiusa.com/us/en/inventory-search",
    "INFINITI": "https://www.infinitiusa.com/shopping-tools/search-inventory.html",
    "Jaguar": "https://www.jaguarusa.com/inventory/index.html",
    "Jeep": "https://www.jeep.com/new-inventory.html",
    "Kia": "https://www.kia.com/us/en/inventory",
    "Lamborghini": "https://www.lamborghini.com/en-en/dealerships",
    "Land Rover": "https://www.landroverusa.com/inventory/index.html",
    "Lexus": "https://www.lexus.com/search-inventory",
    "Lincoln": "https://shop.lincoln.com/inventory/",
    "Lucid": "https://lucidmotors.com/available-cars",
    "Maserati": "https://www.maserati.com/us/en/shopping-tools/new-car-inventory",
    "Mazda": "https://www.mazdausa.com/shopping-tools/inventory",
    "McLaren": "https://retailers.mclaren.com/us/en",
    "Mercedes-Benz": "https://www.mbusa.com/en/vehicles",
    "MINI": "https://www.miniusa.com/inventory.html",
    "Mitsubishi": "https://www.mitsubishicars.com/new-car-lease-special-offers/search-inventory",
    "Nissan": "https://www.nissanusa.com/shopping-tools/search-inventory.html",
    "Polestar": "https://www.polestar.com/us/preconfigured-cars/",
    "Porsche": "https://finder.porsche.com/us/en-US/search",
    "RAM": "https://www.ramtrucks.com/new-inventory.html",
    "Rivian": "https://rivian.com/configurations/list",
    "Rolls-Royce": "https://www.rolls-roycemotorcars.com/en_US/showroom.html",
    "Subaru": "https://www.subaru.com/shopping-tools/inventory.html",
    "Tesla": "https://www.tesla.com/inventory/new/",
    "Toyota": "https://www.toyota.com/search-inventory/",
    "VinFast": "https://vinfastauto.us/vehicles",
    "Volkswagen": "https://www.vw.com/en/inventory.html",
    "Volvo": "https://www.volvocars.com/us/inventory/",
}

MANUFACTURER_MAKE_NAMES = {brand.lower() for brand in MANUFACTURER_URLS}
@dataclass
class SourceTarget:
    source: str
    url: str
    method: str
    trim_keywords: list[str]
    required_keywords: list[str]
    exclude_keywords: list[str]
    model_aliases: list[str]
    load_more: str
    fields: list[str]
    notes: str
    nationwide: bool
    location_policy: str
    validation: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_collection_plan(request: VehicleQuery, current_year: int | None = None) -> dict[str, object]:
    current_year = current_year if current_year is not None else _runtime_current_year()
    model_query = source_query_model(request.make, request.model, request.trim)
    matching = source_model_profile(request.make, request.model, request.trim, "matching")
    resolution = resolve_vehicle_query(request)
    trim_keywords = _trim_keywords(matching)
    targets = [
        _manufacturer_target(request, model_query, matching),
        _visor_new_target(request, matching, current_year),
        _autotrader_target(request, current_year),
        _edmunds_target(request, matching, current_year),
        _visor_target(request, matching, current_year),
    ]
    workflow = [
        "Open the source URL in the browser.",
        "Confirm the visible page is either a matching result page or a make-level fallback that still contains matching rows.",
        "Set the search radius/location to Nationwide, All miles, or equivalent. If a zip is required, use it only as a search unlock parameter.",
        "Before capturing a row, apply the target required_keywords and exclude_keywords as whole tokens.",
        "For exact trims, reject neighboring variants that add a distinct trim/drivetrain token the user did not ask for.",
        "If a site returns all cars for a make, do not trust the page filter; collect only rows that pass the matching rule.",
        "Scroll through listings and click visible Load More / Show More / See More buttons when present.",
        "Extract visible listing text after each loaded section.",
        "Import the capture text into the app with the source name and URL.",
        "Let the app deduplicate by VIN first, then by year/title/trim/price/mileage/dealer.",
    ]
    if request.target_year:
        workflow.insert(3, f"Collect only model-year {request.target_year}; reject every other year even if the source broadens the search.")
    elif request.start_year:
        workflow.insert(3, f"Collect model-year {request.start_year} and newer only.")
    if request.make == "BMW" and request.model == "M4" and request.trim.lower() == "competition":
        workflow.insert(
            4,
            "For 2021+ accept M4 Competition Coupe/Convertible and RWD/xDrive. For 2016-2020 accept an M4 only when "
            "the visible row/detail evidence identifies the factory ZCP Competition Package. Reject ordinary Base, CS, CSL, and GTS rows.",
        )

    return {
        "query": request.to_dict(),
        "resolution": resolution,
        "modelQuery": model_query,
        "matching": {
            "canonical": request.display_name,
            "required_keywords": matching["required_keywords"],
            "exclude_keywords": matching["exclude_keywords"],
            "model_aliases": matching["model_aliases"],
            "rule": (
                "A captured row must contain every required keyword as a separate token, none of the excluded keywords, "
                "and must not be a neighboring exact-trim variant such as EX-L for EX, GT500 for GT, Carrera S for Carrera, "
                "or xDrive for a constrained exact trim. BMW M4 Competition is a named family exception: unspecified "
                "body style and drivetrain remain inclusive, and verified 2016-2020 factory Competition Package cars qualify."
            ),
            "include_all": resolution["include_all"],
            "exact": resolution["exact"],
        },
        "targets": [target.to_dict() for target in targets],
        "codexWorkflow": workflow,
    }


def _manufacturer_target(request: VehicleQuery, model_query: str, matching: dict[str, object]) -> SourceTarget:
    url = MANUFACTURER_URLS.get(request.make, f"https://www.google.com/search?q={quote_plus(request.make + ' official new car inventory MSRP')}")
    return SourceTarget(
        source="manufacturer_official_new",
        url=url,
        method="browser_msrp_or_new_inventory",
        trim_keywords=[model_query, *_trim_keywords(matching)],
        required_keywords=list(matching["required_keywords"]),
        exclude_keywords=list(matching["exclude_keywords"]),
        model_aliases=list(matching["model_aliases"]),
        load_more="Use the official build/MSRP or inventory flow when visible; do not bypass region, login, or dealer walls.",
        fields=["official MSRP", "model year", "trim/version", "new inventory asking price when visible", "dealer", "VIN when visible"],
        notes="Use this for age-0 MSRP and actual new-car samples. If inventory is unavailable, capture MSRP only.",
        nationwide=True,
        location_policy="Official MSRP is national. New inventory should be nationwide/all dealers when the manufacturer site supports it.",
        validation=[
            "Confirm model/trim name against the official make site before collecting MSRP or new inventory.",
            "If inventory is dealer-local only, record that limitation in source notes.",
            *_year_validation(request),
        ],
    )


def _autotrader_target(request: VehicleQuery, current_year: int) -> SourceTarget:
    profile = source_model_profile(request.make, request.model, request.trim, "autotrader")
    path = "/".join(_slug(part) for part in profile["path_segments"])
    params = {
        "zip": "10001",
        "searchRadius": "0",
        "newSearch": "true",
    }
    if request.target_year:
        params["startYear"] = str(request.target_year)
        params["endYear"] = str(request.target_year)
    else:
        lower_year = max(current_year - request.max_age, request.start_year or current_year - request.max_age)
        params["startYear"] = str(lower_year)
        params["endYear"] = str(current_year)
    return SourceTarget(
        source="autotrader_browser",
        url=f"https://www.autotrader.com/cars-for-sale/all-cars/{path}/new-york-ny?{urlencode(params)}",
        method="browser_visible_text",
        trim_keywords=_trim_keywords(profile),
        required_keywords=list(profile["required_keywords"]),
        exclude_keywords=list(profile["exclude_keywords"]),
        model_aliases=list(profile["model_aliases"]),
        load_more="Set/confirm Nationwide or All miles, then scroll result list; click any visible Load More / Next page control before each capture.",
        fields=["year", "make", "model", "trim/version", "price", "mileage", "dealer", "VIN when detail page is opened"],
        notes="Location is used only to unlock nationwide search; depreciation stays national/market-average. " + " ".join(profile["notes"]),
        nationwide=True,
        location_policy="Use zip=10001 only as an Autotrader URL requirement. searchRadius=0 means the target is nationwide/all-distance; verify the visible UI does not say local-only.",
        validation=[
            "If Autotrader redirects to a make-level page, keep collecting only rows that pass required/exclude keyword matching.",
            "For Bentley Continental GT, Autotrader commonly uses Continental as model and GT as trim/path segment.",
            "Reject Bentley rows for GTC, Bentayga, Flying Spur, and Mulsanne when the query is Continental GT.",
            *_year_validation(request),
        ],
    )


def _edmunds_target(request: VehicleQuery, matching: dict[str, object], current_year: int) -> SourceTarget:
    model_query = source_query_model(request.make, request.model, request.trim, "edmunds")
    params = {
        "inventorytype": "used,cpo",
        "make": request.make.lower().replace(" ", "-"),
        "model": model_query.lower().replace(" ", "-"),
    }
    if request.target_year:
        params["year"] = str(request.target_year)
    else:
        lower_year = max(current_year - request.max_age, request.start_year or current_year - request.max_age)
        params["year"] = f"{lower_year}-{current_year}"
    return SourceTarget(
        source="edmunds_browser",
        url=f"https://www.edmunds.com/inventory/srp.html?{urlencode(params)}",
        method="browser_visible_text",
        trim_keywords=_trim_keywords(matching),
        required_keywords=list(matching["required_keywords"]),
        exclude_keywords=list(matching["exclude_keywords"]),
        model_aliases=list(matching["model_aliases"]),
        load_more="Set/confirm nationwide/all-distance when available; scroll listings; click Show More Results / Next if visible.",
        fields=["year", "make", "model", "trim", "price", "mileage", "dealer", "VIN in detail URL/page"],
        notes="If direct SRP is blank, use Edmunds Used Cars search form and select make/model visually.",
        nationwide=True,
        location_policy="Use any location field only to unlock inventory search; prefer nationwide/all-distance if the UI offers it.",
        validation=[
            "Do not collect rows from a broad make page unless they pass required/exclude keyword matching.",
            "Record a source note if Edmunds cannot be made nationwide.",
            *_year_validation(request),
        ],
    )


def _visor_new_target(request: VehicleQuery, matching: dict[str, object], current_year: int) -> SourceTarget:
    model_query = source_query_model(request.make, request.model, request.trim, "visor")
    params = {
        "make": request.make,
        "model": model_query,
        "car_type": "new",
    }
    params["year"] = str(request.target_year or current_year)
    return SourceTarget(
        source="visor_new_facets",
        url=f"https://visor.vin/search/filters?{urlencode(params, quote_via=quote_plus)}",
        method="api_or_public_facets",
        trim_keywords=_trim_keywords(matching),
        required_keywords=list(matching["required_keywords"]),
        exclude_keywords=list(matching["exclude_keywords"]),
        model_aliases=list(matching["model_aliases"]),
        load_more="Use Visor public new-car facets or API listings when available; resolve trim/version aliases from the page facets before collecting.",
        fields=["new-car price bands", "new-car MSRP bands", "trim/version buckets", "dealer/listing details via API when keyed"],
        notes="Supports age-0 box plot samples and should be labeled condition=new.",
        nationwide=True,
        location_policy="Visor public facets are nationwide aggregate market data unless a source URL says otherwise.",
        validation=[
            "Verify the facet make/model and any resolved trim/version alias in the source-data snapshot before using it.",
            *_year_validation(request),
        ],
    )


def _visor_target(request: VehicleQuery, matching: dict[str, object], current_year: int) -> SourceTarget:
    model_query = source_query_model(request.make, request.model, request.trim, "visor")
    params = {
        "make": request.make,
        "model": model_query,
        "car_type": "used",
    }
    if request.target_year:
        params["year"] = str(request.target_year)
    else:
        lower_year = max(current_year - request.max_age, request.start_year or current_year - request.max_age)
        params["year"] = ",".join(str(year) for year in range(lower_year, current_year + 1))
    return SourceTarget(
        source="visor_api_or_facets",
        url=f"https://visor.vin/search/filters?{urlencode(params, quote_via=quote_plus)}",
        method="api_or_public_facets",
        trim_keywords=_trim_keywords(matching),
        required_keywords=list(matching["required_keywords"]),
        exclude_keywords=list(matching["exclude_keywords"]),
        model_aliases=list(matching["model_aliases"]),
        load_more="Use Visor API/MCP for listings when keyed; public pages expose facets and counts. Resolve trim/version aliases from the broad make/model page.",
        fields=["year buckets", "trim/version buckets", "price bands", "mileage bands", "market velocity", "listing price via API"],
        notes="Best treated as API-first; public unauthenticated page is useful as aggregate support. Trim names may live under Version rather than Trim.",
        nationwide=True,
        location_policy="Visor public facets are nationwide aggregate market data unless a source URL says otherwise.",
        validation=[
            "Verify the facet make/model and any resolved trim/version alias in the source-data snapshot before using it.",
            *_year_validation(request),
        ],
    )


def _trim_keywords(profile: dict[str, object]) -> list[str]:
    return [str(item) for item in profile["required_keywords"] if str(item).lower() not in MANUFACTURER_MAKE_NAMES]


def _year_validation(request: VehicleQuery) -> list[str]:
    if request.target_year:
        return [f"Accept only model-year {request.target_year}; do not treat a broad or ignored year filter as valid."]
    if request.start_year:
        return [f"Accept only model-year {request.start_year} or newer."]
    return []


def _slug(value: str) -> str:
    return quote(value.lower().replace(" ", "-"))


def _runtime_current_year() -> int:
    return datetime.now(timezone.utc).year
