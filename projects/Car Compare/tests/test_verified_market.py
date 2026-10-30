import json
import unittest

from car_compare.collection_scope import verified_scope
from car_compare.depreciation import build_report
from car_compare.models import Listing, MSRP, VehicleQuery
from car_compare.sources.visor_facets import (
    _html_confirms_applied_value, _html_confirms_vehicle, _parse_facet_items,
)


class VerifiedMarketTests(unittest.TestCase):
    def setUp(self):
        self.query = VehicleQuery("BMW M4", "BMW", "M4")
        self.msrp = MSRP(100000, "Reference", "manufacturer", "")

    def state(self, **values):
        return 'queryHash:' + json.dumps(json.dumps(["facets", {"facets": "price,year", **values}]))

    def test_generic_title_with_structured_scope(self):
        page = '<title>Visor | See the whole market</title>' + self.state(make="BMW", model="M4 Coupe", year="2023")
        self.assertTrue(_html_confirms_vehicle(self.query, page))
        self.assertTrue(_html_confirms_applied_value(page, "year", "2023"))
        self.assertFalse(_html_confirms_applied_value(page, "year", "2024"))

    def test_links_and_titles_are_not_scope_proof(self):
        page = '<title>BMW M4</title><a href="?year=2023&trim=Competition">Other</a>'
        self.assertFalse(_html_confirms_vehicle(self.query, page))
        self.assertFalse(_html_confirms_applied_value(page, "year", "2023"))

    def test_balanced_facet_array(self):
        page = 'model:$R[1]=[$R[2]={item:"M4 Coupe",count:12},$R[3]={item:"M4 Convertible",count:8}],anything:1'
        self.assertEqual(len(_parse_facet_items(page, "model")), 2)

    def test_missing_baseline_does_not_use_msrp(self):
        report = build_report(self.query, [Listing("sample", 2025, 70000, title="BMW M4")], self.msrp, current_year=2026)
        self.assertIsNone(report["buckets"][0]["median"])
        self.assertIsNone(report["buckets"][1]["depreciation_from_baseline"])

    def test_exact_aggregate_not_blended_with_individuals(self):
        snapshot = {"source": "visor_public_facets", "condition": "used", "year": 2025,
                    "scope": verified_scope(self.query), "price_stats": {"median": 70000, "count": 100}}
        report = build_report(self.query, [Listing("sample", 2025, 10000, title="BMW M4")], self.msrp,
                              current_year=2026, aggregate_snapshots=[snapshot])
        self.assertEqual(report["buckets"][1]["median"], 70000)
        self.assertEqual(report["buckets"][1]["pricing_method"], "exact_source_median")

    def test_unverified_aggregate_is_excluded(self):
        snapshot = {"source": "visor_public_facets", "condition": "new", "year": 2026,
                    "price_stats": {"median": 135500, "count": 100}}
        report = build_report(self.query, [], self.msrp, current_year=2026, aggregate_snapshots=[snapshot])
        self.assertIsNone(report["buckets"][0]["median"])


if __name__ == "__main__":
    unittest.main()
