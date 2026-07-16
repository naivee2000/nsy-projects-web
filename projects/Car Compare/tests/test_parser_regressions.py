from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from car_compare.collector import (
    CollectionManager,
    CollectorConfig,
    _browser_year_quota,
    _msrp_matches_request,
)
from car_compare.models import MSRP
from car_compare.parser import parse_vehicle_query
from car_compare.sources.browser_capture import listing_year_in_scope, parse_visible_listing_text
from car_compare.vehicle_match import vehicle_text_match_score


BMW_ZERO_RESULTS_TEXT = """
Skip To Main Content
Cars for SaleBMWM42014
2014 BMW M4 for Sale in New York, NY
10001
Save Search
|
Clear Filters
Items 1 to 2 of 3.
BMW
M4
2014 - 2014
Location & Delivery
ZIP Code
10001
0 Matches
Sort By:
Relevance
No results found, but it’s not the end of the road.
Expand your search distance
"""


class VisibleListingRegressionTests(unittest.TestCase):
    def test_seven_car_marketplace_accuracy_benchmark_improves_twenty_percent(self) -> None:
        fixture = json.loads(
            (Path(__file__).parent / "fixtures" / "search_accuracy_benchmark.json").read_text(
                encoding="utf-8"
            )
        )
        correct = 0
        total = 0
        for sample in fixture["samples"]:
            request = parse_vehicle_query(sample["query"])
            for expected, title in sample["cases"]:
                actual = bool(
                    vehicle_text_match_score(request, title, "", "autotrader_browser")["accepted"]
                )
                correct += int(actual == expected)
                total += 1
        accuracy = correct / total
        self.assertGreaterEqual(accuracy, fixture["baseline"]["target_accuracy"])

    def test_card_parser_preserves_verified_requested_drivetrain_context(self) -> None:
        request = parse_vehicle_query("Tesla Model 3 Long Range AWD")
        listings = parse_visible_listing_text(
            "edmunds_browser",
            "https://www.edmunds.com/tesla/model-3/2022/vin/5YJ3E1EB1NF234347/",
            "2022 Tesla Model 3 Long Range Sedan\n$19,995\n81,994 miles\nAWD/4WD\nVIN: 5YJ3E1EB1NF234347",
            request,
        )

        self.assertEqual(len(listings), 1)
        self.assertIn("AWD", listings[0].trim)
        self.assertTrue(
            vehicle_text_match_score(request, listings[0].title, listings[0].trim, listings[0].source)["accepted"]
        )

    def test_bmw_zero_results_search_page_cannot_create_zip_price_listing(self) -> None:
        request = parse_vehicle_query("BMW M4")
        url = (
            "https://www.autotrader.com/cars-for-sale/all-cars/2014/bmw/m4/"
            "new-york-ny?searchRadius=0&zip=10001"
        )

        self.assertEqual(parse_visible_listing_text("autotrader_browser", url, BMW_ZERO_RESULTS_TEXT, request), [])

    def test_porsche_search_results_heading_is_not_a_vehicle_card(self) -> None:
        request = parse_vehicle_query("Porsche 911")
        text = """
        Cars for SalePorsche9112007
        2007 Porsche 911 for Sale in New York, NY
        10001
        Save Search
        2 Matches
        """
        url = (
            "https://www.autotrader.com/cars-for-sale/all-cars/2007/porsche/911/"
            "new-york-ny?searchRadius=0&zip=10001"
        )

        self.assertEqual(parse_visible_listing_text("autotrader_browser", url, text, request), [])

    def test_url_zip_is_rejected_but_explicit_same_value_price_is_allowed(self) -> None:
        request = parse_vehicle_query("BMW M4")
        url = "https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4?zip=10001"

        postal_only = "2015 BMW M4 Coupe\n10001\n120,000 miles"
        self.assertEqual(parse_visible_listing_text("autotrader_browser", url, postal_only, request), [])

        explicit_price = "Used 2015 BMW M4 Coupe\nSale Price $10,001\n120,000 miles"
        listings = parse_visible_listing_text("autotrader_browser", url, explicit_price, request)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].price, 10001)

    def test_unlabeled_number_needs_an_independent_vehicle_card_signal(self) -> None:
        request = parse_vehicle_query("BMW M4")
        url = "https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4"

        self.assertEqual(
            parse_visible_listing_text("autotrader_browser", url, "2015 BMW M4 Coupe\n42,000", request),
            [],
        )
        listings = parse_visible_listing_text(
            "autotrader_browser",
            url,
            "2015 BMW M4 Coupe\n42,000\n80,000 miles",
            request,
        )
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].price, 42000)


class CollectorIntegrityRegressionTests(unittest.TestCase):
    def test_host_chrome_zero_card_report_cannot_accept_visible_text(self) -> None:
        request = parse_vehicle_query("2014 BMW M4")
        url = (
            "https://www.autotrader.com/cars-for-sale/all-cars/2014/bmw/m4/"
            "new-york-ny?searchRadius=0&zip=10001"
        )
        capture = {
            "url": url,
            "text": "Used 2014 BMW M4 Coupe\n$42,000\n35,000 miles",
            "pagesExamined": 1,
            "cardsExamined": 0,
            "loadMoreClicked": 0,
            "backgroundMode": True,
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job_dir = root / "job"
            job_dir.mkdir()
            manager = CollectionManager(CollectorConfig(root=root, cache_enabled=False))
            payload = {
                "source": "autotrader_browser",
                "url": url,
                "start_year": 2014,
                "end_year": 2014,
                "target_years": [2015],
            }
            with patch("car_compare.collector.capture_with_host_chrome", return_value=capture) as mocked_capture:
                audit = manager._collect_host_chrome_source(request, payload, job_dir)

        mocked_capture.assert_called_once()
        self.assertEqual(audit["accepted"], 0)
        self.assertEqual(audit["listings"], [])
        self.assertEqual(audit["rejected_by_reason"], {"zero_listing_cards": 1})

    def test_host_chrome_never_accepts_more_rows_than_reported_cards(self) -> None:
        request = parse_vehicle_query("BMW M4")
        url = "https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4?zip=10001"
        capture = {
            "url": url,
            "text": (
                "Used 2025 BMW M4 Coupe\n$75,000\n10,000 miles\n"
                "Used 2024 BMW M4 Coupe\n$68,000\n20,000 miles\n"
            ),
            "pagesExamined": 1,
            "cardsExamined": 1,
            "loadMoreClicked": 0,
            "backgroundMode": True,
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manager = CollectionManager(CollectorConfig(root=root, cache_enabled=False))
            payload = {
                "source": "autotrader_browser",
                "url": url,
                "start_year": 2015,
                "end_year": 2026,
                "target_years": [],
            }
            with (
                patch("car_compare.collector.capture_with_host_chrome", return_value=capture),
                patch(
                    "car_compare.collector._browser_year_quota",
                    return_value={"counts": {2025: 1}, "targets": {2025: 1}, "sparse_years": [], "met": True},
                ),
            ):
                audit = manager._collect_host_chrome_source(request, payload, root)

        self.assertEqual(audit["cards_examined"], 1)
        self.assertEqual(audit["accepted"], 1)
        self.assertEqual(audit["rejected_by_reason"], {"accepted_rows_exceeded_cards": 1})

    def test_generic_m4_browser_years_start_at_2015_but_explicit_year_is_preserved(self) -> None:
        generic = parse_vehicle_query("BMW M4")
        generic.max_age = 20
        explicit = parse_vehicle_query("2014 BMW M4")

        with (
            patch("car_compare.collector._runtime_current_year", return_value=2026),
            patch("car_compare.sources.browser_capture._runtime_current_year", return_value=2026),
        ):
            quota = _browser_year_quota([], generic)
            explicit_quota = _browser_year_quota([], explicit)
            self.assertFalse(listing_year_in_scope(2014, generic))
            self.assertTrue(listing_year_in_scope(2015, generic))

        self.assertEqual(min(quota["targets"]), 2015)
        self.assertEqual(list(explicit_quota["targets"]), [2014])

    def test_empty_cache_audit_does_not_store_preproduction_m4_years(self) -> None:
        request = parse_vehicle_query("BMW M4")
        request.max_age = 20
        manager = object.__new__(CollectionManager)
        manager._capture_cache = Mock()
        audit = {
            "source": "autotrader_browser",
            "browser_verified": True,
            "year_quota": {"targets": {year: 8 for year in range(2006, 2027)}},
            "listings": [],
        }

        manager._store_audit_cache(request, audit, current_year=2026)

        stored_years = {call.args[2] for call in manager._capture_cache.store_year.call_args_list}
        self.assertEqual(min(stored_years), 2015)
        self.assertEqual(max(stored_years), 2026)
        self.assertNotIn(2014, stored_years)

    def test_porsche_model_wide_msrp_rejects_turbo_s_reference(self) -> None:
        request = parse_vehicle_query("Porsche 911")
        turbo_s = MSRP(
            price=270300,
            label="2026 Porsche 911 Turbo S starting MSRP",
            source="porsche",
            url="https://www.porsche.com/usa/models/911/911-turbo-models/911-turbo-s/",
            year=2026,
        )
        carrera = MSRP(
            price=132300,
            label="2026 Porsche 911 Carrera starting MSRP",
            source="porsche",
            url="https://www.porsche.com/usa/models/911/911-models/carrera/",
            year=2026,
        )

        with patch("car_compare.collector._runtime_current_year", return_value=2026):
            self.assertFalse(_msrp_matches_request(turbo_s, request))
            self.assertTrue(_msrp_matches_request(carrera, request))


if __name__ == "__main__":
    unittest.main()
