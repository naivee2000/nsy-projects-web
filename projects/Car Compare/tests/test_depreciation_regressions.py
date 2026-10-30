from __future__ import annotations

import unittest
from dataclasses import replace
from car_compare.collection_scope import verified_scope

from car_compare.depreciation import _apply_depreciation, _stabilize_observed_curve, build_report
from car_compare.models import BucketStats, Listing, MSRP
from car_compare.parser import parse_vehicle_query


class DepreciationRegressionTests(unittest.TestCase):
    def test_isolated_normalized_spike_falls_back_and_all_changes_reconcile(self) -> None:
        buckets = [
            BucketStats(0, 2026, 20, True, False, market_median=97_096, curve_median=97_096),
            BucketStats(1, 2025, 20, True, False, market_median=40_000, curve_median=40_000),
            BucketStats(
                2,
                2024,
                20,
                True,
                False,
                market_median=40_000,
                curve_median=94_285,
                trim_normalized_median=94_285,
                source_counts={"market_a": 10, "market_b": 10},
            ),
            BucketStats(3, 2023, 20, True, False, market_median=38_942, curve_median=38_942),
        ]

        _stabilize_observed_curve(buckets)
        _apply_depreciation(buckets)

        self.assertEqual(buckets[2].curve_unadjusted_median, 94_285)
        self.assertEqual(buckets[2].curve_median, 40_000)
        self.assertIn("raw market median", buckets[2].curve_adjustment_reason)
        self.assertEqual(buckets[3].depreciation_from_previous, 1_058)
        self.assertEqual(buckets[3].depreciation_from_baseline, 58_154)
        self.assertEqual(
            buckets[3].curve_median + buckets[3].depreciation_from_baseline,
            buckets[0].curve_median,
        )

    def test_age_zero_excludes_used_rows_and_ignores_population_weights(self) -> None:
        query = parse_vehicle_query("Porsche 911")
        query.max_age = 1
        rows = [
            Listing(
                "new_facets",
                2026,
                300_000,
                title="New 2026 Porsche 911 Turbo S",
                condition="new",
                market_weight=1,
            ),
            Listing(
                "used_facets",
                2026,
                100_000,
                title="Used 2026 Porsche 911 Carrera",
                condition="used",
                market_weight=100,
            ),
            Listing(
                "used_facets",
                2026,
                200_000,
                title="Used 2026 Porsche 911 Carrera S",
                condition="used",
                market_weight=1,
            ),
        ]

        rows[0] = replace(rows[0], source="new_inventory", scope=verified_scope(query))
        forward = build_report(query, rows, MSRP(135_500, "MSRP", "porsche", ""), current_year=2026)
        reverse = build_report(query, list(reversed(rows)), MSRP(135_500, "MSRP", "porsche", ""), current_year=2026)

        forward_age_zero = forward["buckets"][0]
        reverse_age_zero = reverse["buckets"][0]
        self.assertEqual(forward_age_zero, reverse_age_zero)
        self.assertEqual(forward_age_zero["values"], [300_000])
        self.assertEqual(forward_age_zero["median"], 300_000)
        self.assertEqual(forward_age_zero["q1"], 300_000)
        self.assertEqual(forward_age_zero["q3"], 300_000)
        self.assertEqual(forward_age_zero["average"], 300_000)

    def test_single_sparse_row_is_evidence_not_an_observed_trend(self) -> None:
        query = parse_vehicle_query("Porsche 911")
        query.max_age = 12
        rows = [
            Listing("source_a", 2025, 88_000, title="2025 Porsche 911 Carrera"),
            Listing("source_b", 2025, 90_000, title="Used 2025 Porsche 911 Carrera"),
            Listing(
                "autotrader_browser",
                2014,
                10_001,
                title="2014 Porsche 911 for Sale in New York, NY",
                url="https://www.autotrader.com/cars-for-sale/porsche/911?zip=10001",
            ),
        ]

        report = build_report(query, rows, MSRP(100_000, "MSRP", "porsche", ""), current_year=2026)
        age_twelve = report["buckets"][12]

        self.assertFalse(age_twelve["observed"])
        self.assertTrue(age_twelve["predicted"])
        self.assertEqual(age_twelve["sample_count"], 1)
        self.assertEqual(age_twelve["market_median"], 10_001)
        self.assertGreater(age_twelve["trend_median"], 10_001)
        self.assertEqual(age_twelve["median"], age_twelve["trend_median"])
        self.assertEqual(age_twelve["confidence"], "long_range_projected_sparse_sample")
        self.assertNotIn(12, report["summary"]["observedAges"])
        self.assertIn(12, report["summary"]["predictedAges"])
        self.assertIn(12, report["summary"]["insufficientSampleAges"])

    def test_known_prelaunch_row_is_excluded_while_later_age_projects(self) -> None:
        query = parse_vehicle_query("BMW M4")
        query.max_age = 12
        rows = [
            Listing("source_a", 2025, 88_000, title="2025 BMW M4 Coupe"),
            Listing("source_b", 2025, 90_000, title="Used 2025 BMW M4 Coupe"),
            Listing(
                "autotrader_browser",
                2014,
                10_001,
                title="2014 BMW M4 for Sale in New York, NY",
                url="https://www.autotrader.com/cars-for-sale/bmw/m4?zip=10001",
            ),
        ]

        report = build_report(query, rows, MSRP(100_000, "MSRP", "bmwusa", ""), current_year=2026)
        age_twelve = report["buckets"][12]

        self.assertEqual(report["summary"]["modelYearBounds"], {"first": 2015, "last": None})
        self.assertEqual(report["summary"]["outsideLifecycleRows"], 1)
        self.assertEqual(report["summary"]["outsideLifecycleYears"], {2014: 1})
        self.assertEqual(report["summary"]["listingCount"], 2)
        self.assertFalse(age_twelve["observed"])
        self.assertTrue(age_twelve["predicted"])
        self.assertIsNone(age_twelve["model_year"])
        self.assertEqual(age_twelve["model_years"], [])
        self.assertEqual(age_twelve["sample_count"], 0)
        self.assertIsNone(age_twelve["market_median"])
        self.assertGreater(age_twelve["trend_median"], 10_001)
        self.assertEqual(age_twelve["confidence"], "long_range_projected_beyond_model_history")
        self.assertFalse(any(row["year"] == 2014 for row in report["listings"]))

    def test_signed_value_changes_expose_appreciation_and_keep_loss_fields(self) -> None:
        query = parse_vehicle_query("Porsche 911")
        query.max_age = 2
        rows = [
            Listing("source_a", 2026, 100_000, title="Used 2026 Porsche 911 Carrera"),
            Listing("source_b", 2026, 100_000, title="Used 2026 Porsche 911 Carrera"),
            Listing("source_a", 2025, 110_000, title="Used 2025 Porsche 911 Carrera"),
            Listing("source_b", 2025, 110_000, title="Used 2025 Porsche 911 Carrera"),
            Listing("source_a", 2024, 90_000, title="Used 2024 Porsche 911 Carrera"),
            Listing("source_b", 2024, 90_000, title="Used 2024 Porsche 911 Carrera"),
        ]

        rows[:2] = [replace(row, title=row.title.replace("Used", "New"), condition="new", scope=verified_scope(query)) for row in rows[:2]]
        report = build_report(query, rows, MSRP(100_000, "MSRP", "porsche", ""), current_year=2026)
        age_one = report["buckets"][1]
        age_two = report["buckets"][2]

        self.assertEqual(age_one["value_change_from_previous"], 10_000)
        self.assertEqual(age_one["value_change_from_previous_pct"], 0.1)
        self.assertEqual(age_one["value_change_from_baseline"], 10_000)
        self.assertEqual(age_one["value_change_from_baseline_pct"], 0.1)
        self.assertEqual(age_one["depreciation_from_previous"], 0)
        self.assertEqual(age_one["depreciation_from_baseline"], 0)

        self.assertEqual(age_two["value_change_from_previous"], -20_000)
        self.assertEqual(age_two["value_change_from_previous_pct"], -0.1818)
        self.assertEqual(age_two["value_change_from_baseline"], -10_000)
        self.assertEqual(age_two["value_change_from_baseline_pct"], -0.1)
        self.assertEqual(age_two["depreciation_from_previous"], 20_000)
        self.assertEqual(age_two["depreciation_from_previous_pct"], 0.1818)
        self.assertEqual(age_two["depreciation_from_baseline"], 10_000)
        self.assertEqual(age_two["depreciation_from_baseline_pct"], 0.1)

    def test_generation_adjustment_changes_predictions_not_observed_buckets(self) -> None:
        query = parse_vehicle_query("BMW M4")
        query.max_age = 3
        rows = [
            Listing("source_a", 2026, 100_000, title="New 2026 BMW M4 Coupe", condition="new"),
            Listing("source_b", 2026, 100_000, title="New 2026 BMW M4 Coupe", condition="new"),
            Listing("source_a", 2025, 90_000, title="2025 BMW M4 Coupe"),
            Listing("source_b", 2025, 90_000, title="Used 2025 BMW M4 Coupe"),
            Listing("source_a", 2024, 82_000, title="2024 BMW M4 Coupe"),
            Listing("source_b", 2024, 82_000, title="Used 2024 BMW M4 Coupe"),
        ]
        generation = {
            "status": "success",
            "adjustments": [
                {
                    "calendar_year": 2028,
                    "extra_depreciation_pct": 0.1,
                    "label": "Replacement generation",
                    "basis": "Regression fixture",
                }
            ],
        }

        report = build_report(
            query,
            rows,
            MSRP(100_000, "MSRP", "bmwusa", ""),
            current_year=2026,
            generation_impact=generation,
        )
        observed = report["buckets"][2]
        predicted = report["buckets"][3]

        self.assertTrue(observed["observed"])
        self.assertEqual(observed["median"], 82_000)
        self.assertEqual(observed["market_median"], 82_000)
        self.assertIsNone(observed["generation_adjustment_pct"])
        self.assertIsNone(observed["generation_unadjusted_median"])

        self.assertTrue(predicted["predicted"])
        self.assertEqual(predicted["generation_adjustment_pct"], 0.1)
        self.assertIsNotNone(predicted["generation_unadjusted_median"])
        self.assertEqual(
            predicted["median"],
            round(predicted["generation_unadjusted_median"] * 0.9, 2),
        )

    def test_iqr_whiskers_hide_extreme_price_without_deleting_evidence(self) -> None:
        query = parse_vehicle_query("BMW M4")
        query.max_age = 10
        rows = [
            Listing("market", 2016, 30_000, title="2016 BMW M4 Coupe example 1"),
            Listing("market", 2016, 32_000, title="2016 BMW M4 Coupe example 2"),
            Listing("market", 2016, 35_000, title="2016 BMW M4 Coupe example 3"),
            Listing("market", 2016, 40_000, title="2016 BMW M4 Coupe example 4"),
            Listing("market", 2016, 1_001_798, title="2016 BMW M4 GTS example 5"),
        ]

        report = build_report(query, rows, MSRP(100_000, "MSRP", "bmwusa", ""), current_year=2026)
        bucket = report["buckets"][10]

        self.assertTrue(bucket["observed"])
        self.assertEqual(bucket["median"], 35_000)
        self.assertEqual(bucket["low"], 30_000)
        self.assertEqual(bucket["high"], 40_000)
        self.assertEqual(bucket["outlier_count"], 1)
        self.assertIn(1_001_798, bucket["values"])
        self.assertTrue(any(row["price"] == 1_001_798 for row in report["listings"]))

    def test_unverified_aggregate_bins_are_evidence_only(self) -> None:
        query = parse_vehicle_query("BMW M4")
        query.max_age = 10
        rows = [
            Listing("facets", 2016, 50_000, title="2016 BMW M4 aggregate bin 1", market_weight=100),
            Listing("facets", 2016, 60_000, title="2016 BMW M4 aggregate bin 2", market_weight=1),
            Listing("facets", 2016, 70_000, title="2016 BMW M4 aggregate bin 3", market_weight=1),
            Listing("facets", 2016, 1_000_000, title="2016 BMW M4 aggregate bin 4", market_weight=1),
        ]

        report = build_report(query, rows, MSRP(100_000, "MSRP", "bmwusa", ""), current_year=2026)
        bucket = report["buckets"][10]

        self.assertIsNone(bucket["q1"])
        self.assertIsNone(bucket["q3"])
        self.assertIsNone(bucket["low"])
        self.assertIsNone(bucket["high"])
        self.assertEqual(bucket["outlier_count"], 0)


if __name__ == "__main__":
    unittest.main()
