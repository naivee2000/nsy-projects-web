from __future__ import annotations

import unittest
from urllib.parse import parse_qs, urlparse

from car_compare.models import VehicleQuery
from car_compare.sources.source_plan import build_collection_plan
from car_compare.sources.visor_facets import _requested_years
from car_compare.vehicle_catalog import (
    collection_start_year,
    model_year_bounds,
    msrp_label_matches_scope,
)


class ModelLifecycleTests(unittest.TestCase):
    def test_m4_has_one_shared_us_model_year_boundary(self) -> None:
        self.assertEqual(model_year_bounds("BMW", "M4"), {"first": 2015, "last": None})
        self.assertEqual(collection_start_year("BMW", "M4", 2006), 2015)
        self.assertEqual(collection_start_year("Porsche", "911", 2006), 2006)

    def test_m4_collection_plan_does_not_search_prelaunch_years(self) -> None:
        request = VehicleQuery(raw="BMW M4", make="BMW", model="M4", max_age=20)
        plan = build_collection_plan(request, current_year=2026)
        targets = {item["source"]: item for item in plan["targets"]}

        autotrader_query = parse_qs(urlparse(targets["autotrader_browser"]["url"]).query)
        edmunds_query = parse_qs(urlparse(targets["edmunds_browser"]["url"]).query)
        visor_query = parse_qs(urlparse(targets["visor_api_or_facets"]["url"]).query)

        self.assertEqual(autotrader_query["startYear"], ["2015"])
        self.assertEqual(edmunds_query["year"], ["2015-2026"])
        self.assertEqual(visor_query["year"][0].split(",")[0], "2015")
        self.assertEqual(plan["modelYearBounds"], {"first": 2015, "last": None})

    def test_visor_year_requests_stop_at_model_boundary(self) -> None:
        request = VehicleQuery(raw="BMW M4", make="BMW", model="M4", max_age=20)
        self.assertEqual(_requested_years(request, 2026), list(range(2026, 2014, -1)))

    def test_model_wide_msrp_rejects_named_performance_trim(self) -> None:
        self.assertFalse(
            msrp_label_matches_scope(
                "Porsche",
                "911",
                "",
                "2026 Porsche 911 Turbo S Coupe base MSRP",
            )
        )
        self.assertTrue(
            msrp_label_matches_scope(
                "Porsche",
                "911",
                "",
                "2026 Porsche 911 Carrera Coupe base MSRP",
            )
        )
        self.assertTrue(
            msrp_label_matches_scope(
                "BMW",
                "M4",
                "",
                "2027 BMW M4 Coupe starting MSRP",
            )
        )

    def test_exact_trim_msrp_requires_the_same_trim_scope(self) -> None:
        self.assertTrue(
            msrp_label_matches_scope(
                "BMW",
                "M4",
                "Competition",
                "BMW M4 Competition Coupe starting MSRP",
            )
        )
        self.assertFalse(
            msrp_label_matches_scope(
                "BMW",
                "M4",
                "Competition",
                "BMW M4 GTS starting MSRP",
            )
        )


if __name__ == "__main__":
    unittest.main()
