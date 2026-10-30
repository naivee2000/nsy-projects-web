"""Offline regression coverage for rev3 partition and baseline integrity."""

from copy import deepcopy
import json
import unittest
import tempfile
import time
import subprocess
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from car_compare.collection_scope import verified_scope
from car_compare.depreciation import build_report
from car_compare.market_evidence import aggregate_buckets
from car_compare.models import Listing, MSRP, VehicleQuery
from car_compare.sources.visor_facets import _resolve_source_models, _specs_from_html
from car_compare.sources.visor_facets import collect_visor_public_facets
from car_compare.collector import CollectionManager, CollectorConfig, _merge_collector_results
from car_compare.capture_cache import CaptureCache


CURRENT_YEAR = 2026


def facet_page(name, values, **selections):
    state = json.dumps(json.dumps(["facets", {"facets": "price,year", **selections}]))
    items = ",".join(
        f'$R[{index + 2}]={{item:{json.dumps(value)},count:{count}}}'
        for index, (value, count) in enumerate(values)
    )
    return f'queryHash:{state},{name}:$R[1]=[{items}]'


def partition(key, condition="used", year=2025, status="successful"):
    return {"id": key, "year": year, "condition": condition, "status": status}


class OfflineTestCase(unittest.TestCase):
    def setUp(self):
        # A forgotten mock must fail locally instead of reaching any marketplace.
        guard = patch("socket.socket.connect", side_effect=AssertionError("Network forbidden in offline tests"))
        guard.start()
        self.addCleanup(guard.stop)
        self.query = VehicleQuery("BMW M4", "BMW", "M4", max_age=3)
        self.msrp = MSRP(200_000, "Reference only", "manufacturer", "")

    def snapshot(self, key="coupe", *, condition="used", year=2025,
                 median=70_000, count=10, manifest=None, bins=None,
                 source="visor_public_facets", complete=True):
        if manifest is None:
            manifest = [partition(key, condition, year)]
        return {
            "source": source, "year": year, "condition": condition,
            "price_stats": {"median": median, "count": count},
            "price_bins": deepcopy(bins or []),
            "scope": verified_scope(
                self.query, captured_at=1_793_232_000, complete=complete,
                partition_key=key, partition_manifest=deepcopy(manifest),
            ),
        }

    def buckets(self, *rows):
        return aggregate_buckets(self.query, list(rows), CURRENT_YEAR)

    def report(self, rows, listings=None):
        return build_report(self.query, listings or [], self.msrp,
                            current_year=CURRENT_YEAR, aggregate_snapshots=rows)

    def pooled_rows(self):
        manifest = [partition("coupe"), partition("convertible", "certified")]
        return [
            self.snapshot("coupe", median=60_000, count=4, manifest=manifest, bins=[
                {"lower": 40_000, "upper": 60_000, "count": 3},
                {"lower": 60_000, "upper": 80_000, "count": 1},
            ]),
            self.snapshot("convertible", condition="certified", median=70_000,
                          count=6, manifest=manifest, bins=[
                {"lower": 40_000, "upper": 60_000, "count": 1},
                {"lower": 60_000, "upper": 80_000, "count": 5},
            ]),
        ]


class VisorPartitionDiscoveryTests(OfflineTestCase):
    def test_carrera_s_selects_s_not_4s_or_whole_carrera_model(self):
        query = VehicleQuery("Porsche 911 Carrera S", "Porsche", "911", trim="Carrera S")
        page = facet_page("trim", [("4S", 80), ("S", 12), ("GTS", 30), ("Base", 20)],
                          make="Porsche", model="911 Carrera", car_type="used")
        specs = _specs_from_html(query, page, "911 Carrera")
        self.assertEqual([(item["name"], item["value"]) for item in specs], [("trim", "S")])

    def test_model_discovery_unions_new_used_and_certified_catalogs(self):
        catalogs = {
            "new": [("M4 CSL", 3), ("M3", 100)],
            "used": [("M4 Coupe", 20)],
            "certified": [("M4 Convertible", 7), ("M4 Coupe", 2)],
        }

        def fetch(url, **kwargs):
            params = parse_qs(urlsplit(url).query)
            self.assertEqual(params["make"], ["BMW"])
            condition = params["car_type"][0]
            return facet_page("model", catalogs[condition], make="BMW", car_type=condition)

        with patch("car_compare.sources.visor_facets._fetch_text", side_effect=fetch) as mocked:
            models = _resolve_source_models(self.query, deadline_at=12345)
        self.assertEqual(set(models), {"M4 CSL", "M4 Coupe", "M4 Convertible"})
        self.assertEqual(len(models), 3)
        self.assertEqual(mocked.call_count, 3)
        self.assertEqual(
            {parse_qs(urlsplit(call.args[0]).query)["car_type"][0] for call in mocked.call_args_list},
            {"new", "used", "certified"},
        )
        self.assertTrue(all(call.kwargs["deadline_at"] == 12345 for call in mocked.call_args_list))

    def test_catalog_options_and_title_without_query_hash_are_not_proof(self):
        page = '<title>BMW M4</title>model:$R[1]=[$R[2]={item:"M4 Coupe",count:10}]'
        with patch("car_compare.sources.visor_facets._fetch_text", return_value=page):
            with self.assertRaises(ValueError):
                _resolve_source_models(self.query)

    def test_catalog_rejects_mismatched_structured_condition(self):
        page = facet_page("model", [("M4 Coupe", 10)], make="BMW", car_type="used")
        with patch("car_compare.sources.visor_facets._fetch_text", return_value=page):
            with self.assertRaises(ValueError):
                _resolve_source_models(self.query)


class PartitionManifestTests(OfflineTestCase):
    def test_all_empty_partitions_remain_evidence_without_listings(self):
        page = facet_page("year", [], make="BMW", model="M4", car_type="used") + ",num_found:0"
        with patch("car_compare.sources.visor_facets._resolve_source_models", return_value=["M4"]), patch("car_compare.sources.visor_facets._fetch_text", return_value=page), patch("car_compare.sources.visor_facets._html_confirms_vehicle", return_value=True), patch("car_compare.sources.visor_facets._html_confirms_applied_value", return_value=True):
            result = collect_visor_public_facets(self.query, current_year=2026)
        self.assertEqual(result["status"], "verifiedzero")
        self.assertFalse(result["listings"])
        self.assertFalse(result["evidence"])
        self.assertTrue(result["partition_manifest"])
        self.assertTrue(all(row["status"] == "verified_empty" for row in result["partition_manifest"]))

    def test_merge_preserves_failed_partition_and_partial_status(self):
        manifest = [partition("cpo", "certified", status="failed")]
        result = _merge_collector_results({"status": "success", "partition_manifest": manifest}, {"status": "success", "listings": [{"price": 1}]})
        self.assertEqual(result["partition_manifest"], manifest)
        self.assertEqual(result["status"], "partial")

    def test_verified_zero_cache_cannot_cross_requested_year_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = CaptureCache(Path(directory) / "cache.db")
            cache.store_year(self.query, "source", 2025, {"listings": [], "scope": verified_scope(self.query)}, current_year=2026, captured_at=100)
            other = deepcopy(self.query)
            other.target_year = 2025
            self.assertEqual(cache.load(other, "source", [2025], now=101), [])
            self.assertEqual(cache.load(self.query, "source", [2025], now=101)[0].captured_at, 100)

    def test_deadline_preserves_current_worker_checkpoint_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manager = CollectionManager(CollectorConfig(root=root, cache_enabled=False))
            target = {"source": "autotrader_browser", "url": "https://autotrader.com/test", "deadline_at": time.time() + 10}
            checkpoint_path = root / "browser_capture_autotrader_browser.json"
            def timeout(*args, **kwargs):
                checkpoint_path.write_text(json.dumps({"source": target["source"], "url": target["url"], "scope": verified_scope(self.query), "listings": [{"price": 70000}], "browser_verified": True}), encoding="utf-8")
                raise subprocess.TimeoutExpired("worker", 1)
            with patch("car_compare.collector.run_bounded", side_effect=timeout):
                result = manager._run_browser_batch_unleased([target], root, timeout=1)[0]
            self.assertEqual(result["status"], "partial")
            self.assertEqual(result["accepted"] if "accepted" in result else len(result["listings"]), 1)
            old = json.loads(checkpoint_path.read_text())
            old["scope"]["captured_at"] = 100
            checkpoint_path.write_text(json.dumps(old))
            with patch("car_compare.collector.run_bounded", side_effect=subprocess.TimeoutExpired("worker", 1)):
                result = manager._run_browser_batch_unleased([target], root, timeout=1)[0]
            self.assertEqual(result["status"], "unavailable")

    def test_fixture_uses_current_rev3_scope(self):
        self.assertEqual(self.snapshot()["scope"]["validation_revision"], 3)

    def test_verified_empty_other_partition_preserves_exact_median(self):
        manifest = [partition("coupe"), partition("convertible", status="verified_empty"),
                    partition("cpo", "certified", status="verified_empty")]
        bucket = self.buckets(self.snapshot(median=72_085, manifest=manifest))[1]
        self.assertEqual(bucket.median, 72_085)
        self.assertEqual(bucket.pricing_method, "exact_source_median")
        self.assertEqual(bucket.aggregate_count, 10)
        self.assertEqual(bucket.sample_count, 0)

    def test_failed_or_unattempted_cpo_excludes_used_population(self):
        for status in ("failed", "unattempted"):
            with self.subTest(status=status):
                manifest = [partition("coupe"), partition("cpo", "certified", status=status)]
                self.assertEqual(self.buckets(self.snapshot(manifest=manifest)), {})

    def test_missing_successful_partition_excludes_population(self):
        for condition in ("used", "certified"):
            with self.subTest(condition=condition):
                manifest = [partition("coupe"), partition("missing", condition)]
                self.assertEqual(self.buckets(self.snapshot(manifest=manifest)), {})

    def test_partition_identity_includes_key_year_and_condition(self):
        for changed in ({"id": "other"}, {"year": 2024}, {"condition": "certified"}):
            with self.subTest(changed=changed):
                manifest = [{**partition("coupe"), **changed}]
                self.assertEqual(self.buckets(self.snapshot(manifest=manifest)), {})

    def test_incomplete_scope_is_excluded_even_with_successful_manifest(self):
        self.assertEqual(self.buckets(self.snapshot(complete=False)), {})

    def test_certified_manifest_matches_cpo_snapshot(self):
        row = self.snapshot(condition="cpo", manifest=[partition("coupe", "certified")])
        self.assertEqual(self.buckets(row)[1].aggregate_count, 10)

    def test_legacy_revision_and_wrong_query_scope_are_excluded(self):
        for changed in ({"validation_revision": 2}, {"query_key": ["different query"]}):
            with self.subTest(changed=changed):
                row = self.snapshot()
                row["scope"].update(changed)
                self.assertEqual(self.buckets(row), {})


class HistogramIntegrityTests(OfflineTestCase):
    def test_disjoint_compatible_histograms_pool_counts_not_medians(self):
        rows = self.pooled_rows()
        bucket = self.buckets(*rows)[1]
        self.assertEqual(bucket.pricing_method, "pooled_histogram_estimate")
        self.assertEqual(bucket.aggregate_count, 10)
        self.assertEqual(bucket.sample_count, 0)
        self.assertAlmostEqual(bucket.median, 60_000 + 20_000 / 6)
        self.assertNotEqual(bucket.median, 66_000)  # Count-weighted source medians.
        self.assertAlmostEqual(bucket.q1, 52_500)
        self.assertAlmostEqual(bucket.q3, 60_000 + 20_000 * 3.5 / 6)

    def test_duplicate_partition_does_not_double_count(self):
        rows = self.pooled_rows()
        expected = self.buckets(*rows)[1]
        actual = self.buckets(*rows, deepcopy(rows[0]))[1]
        self.assertEqual(actual.aggregate_count, expected.aggregate_count)
        self.assertEqual(actual.median, expected.median)

    def test_different_marketplaces_are_never_summed(self):
        first = self.snapshot(count=100, median=70_000)
        second = self.snapshot(source="another_marketplace", count=80, median=90_000)
        bucket = self.buckets(first, second)[1]
        self.assertEqual(bucket.aggregate_count, 100)
        self.assertEqual(bucket.median, 70_000)
        self.assertEqual(bucket.pricing_sources, ["visor_public_facets"])

    def test_incompatible_grids_do_not_average_source_medians(self):
        rows = self.pooled_rows()
        rows[1]["price_bins"][0]["lower"] = 30_000
        self.assertEqual(self.buckets(*rows), {})

    def test_overlapping_histogram_bins_are_rejected(self):
        rows = self.pooled_rows()
        rows[1]["price_bins"][0]["upper"] = 65_000
        self.assertEqual(self.buckets(*rows), {})

    def test_missing_or_incomplete_histogram_is_rejected(self):
        for bins in ([], [{"lower": 40_000, "upper": 80_000, "count": 5}]):
            with self.subTest(bins=bins):
                rows = self.pooled_rows()
                rows[1]["price_bins"] = bins
                self.assertEqual(self.buckets(*rows), {})

    def test_overlapping_version_populations_without_manifest_are_rejected(self):
        rows = self.pooled_rows()
        for row, versions in zip(rows, (["base", "competition"], ["competition", "csl"])):
            row["condition"] = "used"
            row["scope"].pop("partition_manifest")
            row["scope"].pop("partition_key")
            row["scope"]["versions"] = versions
        self.assertEqual(self.buckets(*rows), {})

    def test_incompatible_histograms_fall_back_to_individual_sample(self):
        rows = self.pooled_rows()
        rows[1]["price_bins"] = []
        listings = [Listing("sample", 2025, price, title="2025 BMW M4", vin=f"sample-{i}")
                    for i, price in enumerate((50_000, 60_000, 70_000))]
        bucket = self.report(rows, listings)["buckets"][1]
        self.assertEqual(bucket["pricing_method"], "individual_sample_median")
        self.assertEqual(bucket["market_median"], 60_000)
        self.assertEqual(bucket["aggregate_count"], 0)


class NewInventoryBaselineTests(OfflineTestCase):
    def test_new_aggregate_median_not_msrp_or_tiny_sample_sets_baseline(self):
        rows = [self.snapshot("new", condition="new", year=2026, median=100_000),
                self.snapshot("used", median=70_000)]
        listings = [Listing("sample", 2026, 150_000, title="New 2026 BMW M4",
                            condition="new", scope=verified_scope(self.query))]
        report = self.report(rows, listings)
        baseline, used = report["buckets"][:2]
        self.assertTrue(report["summary"]["baselineAvailable"])
        for field in ("median", "market_median", "curve_median", "trend_median"):
            self.assertEqual(baseline[field], 100_000, field)
            self.assertEqual(used[field], 70_000, field)
        self.assertEqual(baseline["pricing_method"], "exact_source_median")
        self.assertEqual(baseline["sample_count"], 0)
        self.assertEqual(used["value_change_from_baseline"], -30_000)
        self.assertEqual(used["depreciation_from_baseline"], 30_000)
        self.assertEqual(used["value_change_from_baseline_pct"], -0.3)
        self.assertEqual(report["msrp"]["price"], 200_000)

    def test_used_and_cpo_current_year_cannot_supply_new_baseline(self):
        for condition in ("used", "cpo", "certified"):
            with self.subTest(condition=condition):
                report = self.report([self.snapshot(condition=condition, year=2026), self.snapshot()])
                self.assertFalse(report["summary"]["baselineAvailable"])
                self.assertIsNone(report["buckets"][0]["median"])
                self.assertEqual(report["buckets"][1]["median"], 70_000)
                for field in ("value_change_from_baseline", "value_change_from_baseline_pct",
                              "depreciation_from_baseline", "depreciation_from_baseline_pct"):
                    self.assertIsNone(report["buckets"][1][field], field)

    def test_incomplete_new_population_does_not_fall_back_to_msrp(self):
        report = self.report([self.snapshot(condition="new", year=2026, complete=False), self.snapshot()])
        self.assertFalse(report["summary"]["baselineAvailable"])
        self.assertIsNone(report["buckets"][0]["median"])

    def test_new_inventory_across_model_years_pools_into_age_zero(self):
        rows = self.pooled_rows()
        manifest = [partition("coupe", "new", 2026), partition("convertible", "new", 2027)]
        for row, year in zip(rows, (2026, 2027)):
            row.update(condition="new", year=year)
            row["scope"]["partition_manifest"] = deepcopy(manifest)
        buckets = self.buckets(*rows)
        self.assertEqual(set(buckets), {0})
        self.assertEqual(buckets[0].model_years, [2026, 2027])
        self.assertIsNone(buckets[0].model_year)
        self.assertEqual(buckets[0].aggregate_count, 10)
        self.assertAlmostEqual(buckets[0].median, 60_000 + 20_000 / 6)

    def test_missing_successful_new_model_year_excludes_baseline(self):
        manifest = [partition("new", "new", 2026), partition("next", "new", 2027)]
        row = self.snapshot("new", condition="new", year=2026, manifest=manifest)
        self.assertEqual(self.buckets(row), {})


if __name__ == "__main__":
    unittest.main()
