# Website Research Feasibility

Test dates: 2026-07-05 and 2026-07-15

Example query: `BMW M4 Competition after 2021`

## Summary

| Source | Status | Best adapter |
| --- | --- | --- |
| Autotrader | Workable through normal browser UI | Visible listing/card parser |
| Edmunds | Workable through normal browser UI | Search-form navigation plus visible listing parser |
| Porsche Finder | Workable official inventory for Porsche | Audited visible-card parser with nationwide/year/trim URL filters |
| Visor | API-first | REST API/MCP for listings, public facets for aggregates |
| BMW USA | Workable for current MSRP | Manufacturer MSRP adapter |

## Autotrader

The direct inventory page was slow but did load a usable result page. The visible page text included listing count, model years, model names, mileage, prices or price-like lines, dealer snippets, and result sorting.

Working test URL:

```text
https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4/new-york-ny?searchRadius=0&startYear=2021&zip=10001
```

Implementation note: Autotrader wants a location/zip parameter. For our app, this should be treated as a query unlock parameter, not a depreciation variable. We can run multiple broad searches later if we need a less location-shaped sample.

For Bentley Continental GT, Autotrader redirected a model-looking URL to a Bentley make-level page, but visible rows still included Continental GT and GT Speed listings. The app filters captured rows by model and trim after import.

## Edmunds

The direct `used-bmw-m4` URL produced an empty page state during the quick pass, but the used-car search form worked. Selecting BMW, then M4, reached a visible listing page with rows containing year, trim, price, mileage, and VIN detail links.

Working test URL:

```text
https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&make=bmw&model=m4
```

Also verified:

```text
https://www.edmunds.com/inventory/srp.html?inventorytype=used%2Ccpo&make=bentley&model=continental-gt
```

Implementation note: prefer search-form navigation or a known SRP URL. Collect visible page text, parse listing rows, and store the source URL.

## Visor

Visor public pages are useful for aggregates. The BMW M4 filter page showed nationwide count, model-year buckets, trim/version buckets, installed options, drivetrain, transmission, and other facets. The listings page showed a price/mileage grid and market velocity, but individual listing prices were not visible in the unauthenticated quick pass.

Useful pages:

```text
https://visor.vin/search/filters?make=BMW&model=M4&car_type=used
https://visor.vin/search/listings?make=BMW&model=M4&car_type=used
https://visor.vin/api
```

Implementation note: Visor should be API/MCP-first when an API key is available. Its public filter pages can enrich confidence with sample counts and trim buckets.

## Porsche Finder

The official U.S. Porsche Finder exposes 15 visible listing cards per page, numbered pagination, a `Nationwide` radius, exact/range model years, condition, generation, model line, and repeatable trim categories. Omitting location can restore a saved local radius, so planned URLs explicitly retain a neutral coordinate with radius `-1`.

```text
https://finder.porsche.com/us/en-US/search/911?model=911&position=Los%20Angeles%2C34.0481%2C-118.2531%2C-1
```

Implementation note: collect `/details/` cards and follow `page` pagination. Use `minimum-model-year` and `maximum-model-year`. For the 911, repeated `category` values narrow Carrera family, Base, or known exact trims, while the deterministic title matcher remains authoritative.

## BMW USA MSRP

BMW USA exposes current official starting MSRP on model pages. Current MSRP can feed Age 0. Historical MSRP should use archived manufacturer pages, BMW press releases, or clearly labeled fallback sources.

Useful page:

```text
https://www.bmwusa.com/vehicles/m-series/bmw-4-series-m-models/bmw-m4-coupe.html
```

## Adapter Checklist For New Websites

1. Identify whether the site has an official API, export, or documented search URL.
2. Test one normal browser query with a real car.
3. Confirm visible fields: year, make, model, trim, price, mileage, URL.
4. Record whether search requires location, login, CAPTCHA, or account state.
5. Add a source adapter that returns normalized `Listing` objects.
6. Capture VIN and dealer when visible.
7. Deduplicate by VIN first, then by same year/title/trim/price/mileage/dealer.
8. Cache raw capture text and parsed listings separately.
9. Mark source confidence in the report.
