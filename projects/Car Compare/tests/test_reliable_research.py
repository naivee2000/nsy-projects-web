import json
import time
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from car_compare.collection_scope import ANALYSIS_REVISION, VALIDATION_REVISION, verified_scope
from car_compare.depreciation import build_report
from car_compare.market_evidence import _pooled_stats, aggregate_buckets
from car_compare.models import Listing, MSRP
from car_compare.parser import parse_vehicle_query
from car_compare.generation_impact import _generation_cache_identity
from car_compare.sources.visor_facets import collect_visor_public_facets, VisorYearData


class ReliableResearchTests(unittest.TestCase):
    def setUp(self):
        self.query = parse_vehicle_query("Lexus NX")
        self.msrp = MSRP(1, "Reference", "reference", "")

    def test_saved_lexus_replay_recovers_baseline_and_eight_years(self):
        fixture = json.loads((Path(__file__).parent / "fixtures/lexus_nx_20261102.json").read_text())
        snapshots = deepcopy(fixture["evidence"])
        # Re-run the new adapter's year completeness rule against original
        # selected-filter evidence. Original timestamps stay unchanged. This
        # controlled historical replay never writes a production cache entry.
        for row in snapshots:
            scope = row["scope"]
            self.assertEqual(scope["selected_filters"]["model"], "NX")
            self.assertEqual(int(scope["selected_filters"]["year"]), row["year"])
            scope["validation_revision"] = VALIDATION_REVISION
            scope["partition_manifest"] = [x for x in scope["partition_manifest"] if x["year"] == row["year"]]
            scope["complete"] = all(x["status"] in {"successful", "verified_empty"} for x in scope["partition_manifest"])
        with patch("car_compare.collection_scope.time.time", return_value=fixture["captured_at"] + 1):
            report = build_report(self.query, [], self.msrp, current_year=2026, aggregate_snapshots=snapshots)
        self.assertEqual(report["analysisRevision"], ANALYSIS_REVISION)
        self.assertEqual(report["buckets"][0]["market_median"], 54623)
        self.assertEqual(report["summary"]["pricedYearCount"], 8)
        self.assertEqual(report["summary"]["individualListingCount"], 0)
        self.assertEqual(report["summary"]["readiness"], "partial")
        self.assertNotEqual(report["summary"]["aggregatePricingCount"], 795)
        rejected = [snapshots[d["index"]]["year"] for d in report["evidence"]["aggregateDiagnostics"] if d["reason"] == "Histogram counts do not reconcile"]
        self.assertEqual(set(rejected), {2019, 2016})

    def test_pooling_coarsens_whole_bins_and_retains_count(self):
        rows = [{"price_stats": {"count": 10}, "price_bins": [{"lower": 100, "upper": 110, "count": 5}, {"lower": 110, "upper": 120, "count": 5}]},
                {"price_stats": {"count": 5}, "price_bins": [{"lower": 110, "upper": 115, "count": 2}, {"lower": 115, "upper": 120, "count": 3}]}]
        stats = _pooled_stats(rows)
        self.assertEqual(stats["count"], 15)
        self.assertEqual(stats["median_interval"], [110, 120])
        self.assertEqual(stats["median"], 112.5)
        rows[1]["price_stats"]["count"] = 6
        self.assertIsNone(_pooled_stats(rows))

    def test_wide_median_interval_is_range_only(self):
        rows = [{"price_stats": {"count": 4}, "price_bins": [{"lower": 10, "upper": 100, "count": 4}]}] * 2
        stats = _pooled_stats(rows)
        self.assertIsNone(stats["median"])
        self.assertEqual(stats["median_interval"], [10, 100])

    def test_cpo_subset_keeps_certified_alias_in_usage_diagnostics(self):
        manifest=[{"id":"u","year":2025,"condition":"used","status":"failed"},
                  {"id":"c","year":2025,"condition":"certified","status":"successful"}]
        snapshot={"source":"visor_public_facets","year":2025,"condition":"certified", "price_stats":{"count":10,"median":40000},
                  "scope":verified_scope(self.query,complete=False,partition_key="c",partition_manifest=manifest)}
        report=build_report(self.query,[],self.msrp,current_year=2026,aggregate_snapshots=[snapshot])
        self.assertEqual(report["summary"]["populationScope"],"cpo_only")
        self.assertEqual(report["evidence"]["aggregateDiagnostics"][0]["status"],"used")

    def test_unused_individual_normalization_cannot_label_aggregate_curve(self):
        snapshot={"source":"visor_public_facets","year":2025,"condition":"used","price_stats":{"count":10,"median":40000},"scope":verified_scope(self.query)}
        with patch("car_compare.depreciation.build_trim_normalization",return_value={"status":"applied","years":{}}):
            report=build_report(self.query,[],self.msrp,current_year=2026,aggregate_snapshots=[snapshot])
        self.assertEqual(report["summary"]["trimNormalization"]["status"],"not_applied_to_primary_population")

    def test_archived_unverified_rows_cannot_enter_report(self):
        rows = [Listing("edmunds_browser", 2025, p, title="2025 Lexus NX", provenance="collector") for p in [30000, 31000]]
        report = build_report(self.query, rows, self.msrp, current_year=2026)
        self.assertEqual(report["summary"]["readiness"], "unavailable")
        for row in rows:
            row.scope = verified_scope(self.query, captured_at=time.time() - 259201)
        report = build_report(self.query, rows, self.msrp, current_year=2026)
        self.assertEqual(report["summary"]["individualListingCount"], 0)

    def test_forecast_requires_three_observed_years_and_scenario_is_optional(self):
        rows = [Listing("manual", year, p, title=f"{year} Lexus NX") for year in [2025, 2024, 2023] for p in [30000, 31000]]
        impact = {"status": "partial", "adjustments": [{"age": 2, "extra_depreciation_pct": .1, "calendar_year": 2028}]}
        report = build_report(self.query, rows, self.msrp, current_year=2026, generation_impact=impact)
        self.assertIsNone(report["buckets"][4]["generation_adjustment_pct"])
        self.assertGreater(report["scenarioBuckets"][4]["generation_adjustment_pct"], 0)
        short = build_report(self.query, rows[:4], self.msrp, current_year=2026)
        self.assertEqual(short["summary"]["predictedAges"], [])

    def test_newest_new_year_and_generation_cache_context(self):
        snapshots = [{"source":"visor_public_facets_new", "year":year,"condition":"new", "scope":verified_scope(self.query),"price_stats":{"count":100,"median":price}} for year,price in [(2026,50000),(2027,55000)]]
        report = build_report(self.query, [], self.msrp, current_year=2026, aggregate_snapshots=snapshots)
        self.assertEqual(report["summary"]["analysisModelYear"], 2027)
        self.assertEqual(report["summary"]["baselineModelYear"], 2027)
        self.assertEqual(report["buckets"][0]["market_median"], 55000)
        first = _generation_cache_identity(self.query)
        self.query.target_year = 2023
        self.assertNotEqual(first, _generation_cache_identity(self.query))

    def test_retry_reuses_only_fresh_compatible_partitions_without_retimestamping(self):
        from tests.test_partition_integrity import facet_page
        from urllib.parse import urlsplit, parse_qs
        def fetch(url, **kwargs):
            condition=parse_qs(urlsplit(url).query)["car_type"][0]
            return facet_page("year",[("2025",10)],make="Lexus",model="NX",car_type=condition)+",num_found:10"
        def partition(request, year, condition, url, *args):
            return VisorYearData(year,url,condition,{"median":40000,"count":10},{},{},[],num_found=10,scope=verified_scope(request,captured_at=time.time()-10))
        with patch("car_compare.sources.visor_facets._resolve_source_models",return_value=["NX"]), patch("car_compare.sources.visor_facets._fetch_text",side_effect=fetch), patch("car_compare.sources.visor_facets._fetch_visor_facets",side_effect=partition) as captured:
            first=collect_visor_public_facets(self.query,current_year=2026)
            original={row["condition"]:row["scope"]["captured_at"] for row in first["evidence"]}
            first["evidence"]=[row for row in first["evidence"] if row["condition"]!="certified"]
            captured.reset_mock()
            second=collect_visor_public_facets(self.query,current_year=2026,reuse=first)
        self.assertEqual(captured.call_count,1)
        self.assertEqual(captured.call_args.args[2],"certified")
        for row in second["evidence"]:
            if row["condition"]!="certified": self.assertEqual(row["scope"]["captured_at"],original[row["condition"]])


if __name__ == "__main__":
    unittest.main()
