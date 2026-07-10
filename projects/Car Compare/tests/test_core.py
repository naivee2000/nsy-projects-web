from __future__ import annotations

import os
import json
import tempfile
import time
import unittest

from car_compare.depreciation import build_report, dedupe_listings
from pathlib import Path

from car_compare.collector import (
    CollectionManager,
    CollectorConfig,
    _format_elapsed,
    build_codex_command,
    clean_codex_error,
    codex_failure_message,
    listings_from_result,
    msrp_from_result,
)
from car_compare.codex_cli import MACOS_CODEX_CLI_PATHS, codex_environment, codex_login_status, find_codex_cli
from car_compare.generation_impact import GenerationResearchConfig, GenerationResearchManager
from car_compare.models import Listing, MSRP
from car_compare.parser import parse_vehicle_query
from car_compare.resolver import resolve_vehicle_query
from car_compare.sample_data import sample_listings_for
from car_compare.sources.browser_capture import parse_visible_listing_text
from car_compare.sources.source_plan import MANUFACTURER_URLS, TOP_US_BRANDS, build_collection_plan
from car_compare.sources.visor_facets import (
    NEW_SOURCE,
    VisorYearData,
    _facet_evidence,
    _facet_value_matches_request,
    _listings_from_years,
    _parse_facet_items,
    _parse_range_bins,
    _parse_stat_block,
    _visor_url,
)
from car_compare.statistics import percentile
from car_compare.vehicle_match import vehicle_text_match_score


class ParserTests(unittest.TestCase):
    def test_parse_after_query(self) -> None:
        query = parse_vehicle_query("bmw M4 competition after 2021")
        self.assertEqual(query.make, "BMW")
        self.assertEqual(query.model, "M4")
        self.assertEqual(query.trim, "Competition")
        self.assertEqual(query.start_year, 2021)

    def test_parse_target_year_query(self) -> None:
        query = parse_vehicle_query("bmw 440 2022")
        self.assertEqual(query.make, "BMW")
        self.assertEqual(query.model, "440")
        self.assertEqual(query.target_year, 2022)

    def test_parse_bentley_continental_gt(self) -> None:
        query = parse_vehicle_query("Bentley Continental GT")
        self.assertEqual(query.make, "Bentley")
        self.assertEqual(query.model, "Continental GT")
        self.assertEqual(query.trim, "")

    def test_parse_trim_specific_queries(self) -> None:
        cases = {
            "honda civic": ("Honda", "Civic", ""),
            "camry xse": ("Toyota", "Camry", "XSE"),
            "toyota camry": ("Toyota", "Camry", ""),
            "toyota camry x s e": ("Toyota", "Camry", "XSE"),
            "toyota camry xse": ("Toyota", "Camry", "XSE"),
            "lexus lc 500": ("Lexus", "LC", "500"),
            "lc500": ("Lexus", "LC", "500"),
            "ls 500": ("Lexus", "LS", "500"),
            "lx 600": ("Lexus", "LX", "600"),
            "nx350 f sport": ("Lexus", "NX", "350 F Sport"),
            "bmw M3 competition": ("BMW", "M3", "Competition"),
            "bmw M4competition xdrive": ("BMW", "M4", "Competition xDrive"),
            "bmw m4 competition x drive": ("BMW", "M4", "Competition xDrive"),
            "bmw 440i xdrive": ("BMW", "440", "i xDrive"),
            "mercedes c300": ("Mercedes-Benz", "C-Class", "300"),
            "benz c 300 4matic": ("Mercedes-Benz", "C-Class", "300 4MATIC"),
            "mercedes amg c43": ("Mercedes-Benz", "C-Class", "43 AMG"),
            "mercedes glc300": ("Mercedes-Benz", "GLC", "300"),
            "porsche cayenne gts": ("Porsche", "Cayenne", "GTS"),
            "porsche taycan 4s": ("Porsche", "Taycan", "4S"),
            "bentley continental gt speed": ("Bentley", "Continental GT", "Speed"),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                query = parse_vehicle_query(text)
                self.assertEqual((query.make, query.model, query.trim), expected)

    def test_parse_top_brand_queries(self) -> None:
        cases = {
            "ford f150": ("Ford", "F-150", ""),
            "chevy corvette z06": ("Chevrolet", "Corvette", "Z06"),
            "subaru outback limited": ("Subaru", "Outback", "Limited"),
            "tesla modely performance": ("Tesla", "Model Y", "Performance"),
            "jeep wrangler rubicon": ("Jeep", "Wrangler", "Rubicon"),
            "gmc yukon denali": ("GMC", "Yukon", "Denali"),
            "genesis gv80 prestige": ("Genesis", "GV80", "Prestige"),
            "rivian r1s adventure": ("Rivian", "R1S", "Adventure"),
            "lucid air touring": ("Lucid", "Air", "Touring"),
            "volvo xc90 recharge": ("Volvo", "XC90", "Recharge"),
            "land rover range rover sport": ("Land Rover", "Range Rover Sport", ""),
            "vin fast vf 8": ("VinFast", "VF 8", ""),
            "rolls royce cullinan": ("Rolls-Royce", "Cullinan", ""),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                query = parse_vehicle_query(text)
                self.assertEqual((query.make, query.model, query.trim), expected)

    def test_parse_user_supplied_make_model_trim_matrix(self) -> None:
        cases = {
            "Toyota Camry LE": ("Toyota", "Camry", "LE"),
            "Toyota Camry XSE": ("Toyota", "Camry", "XSE"),
            "Toyota RAV4 Limited": ("Toyota", "RAV4", "Limited"),
            "Honda Civic EX": ("Honda", "Civic", "EX"),
            "Honda Accord Touring": ("Honda", "Accord", "Touring"),
            "Ford F-150 Lariat": ("Ford", "F-150", "Lariat"),
            "Ford Mustang GT": ("Ford", "Mustang", "GT"),
            "Chevrolet Silverado 1500 LT": ("Chevrolet", "Silverado 1500", "LT"),
            "BMW 3 Series 330i": ("BMW", "3 Series", "330i"),
            "BMW X5 xDrive40i": ("BMW", "X5", "xDrive40i"),
            "Mercedes-Benz C-Class C300": ("Mercedes-Benz", "C-Class", "300"),
            "Mercedes-Benz GLE 350 4MATIC": ("Mercedes-Benz", "GLE", "350 4MATIC"),
            "Audi Q5 Premium Plus": ("Audi", "Q5", "Premium Plus"),
            "Lexus RX RX 350": ("Lexus", "RX", "350"),
            "Tesla Model 3 Long Range AWD": ("Tesla", "Model 3", "Long Range AWD"),
            "Tesla Model Y Performance": ("Tesla", "Model Y", "Performance"),
            "Jeep Wrangler Rubicon": ("Jeep", "Wrangler", "Rubicon"),
            "Subaru Outback Touring XT": ("Subaru", "Outback", "Touring XT"),
            "Hyundai Tucson SEL": ("Hyundai", "Tucson", "SEL"),
            "Kia Telluride SX": ("Kia", "Telluride", "SX"),
            "Porsche 911 Carrera": ("Porsche", "911", "Carrera"),
            "Porsche 911 Carrera S": ("Porsche", "911", "Carrera S"),
            "Porsche Cayenne Base": ("Porsche", "Cayenne", "Base"),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                query = parse_vehicle_query(text)
                self.assertEqual((query.make, query.model, query.trim), expected)


class StatisticsTests(unittest.TestCase):
    def test_percentile(self) -> None:
        values = [10, 20, 30, 40]
        self.assertEqual(percentile(values, 0.25), 17.5)
        self.assertEqual(percentile(values, 0.5), 25)
        self.assertEqual(percentile(values, 0.75), 32.5)


class ResolverTests(unittest.TestCase):
    def test_unspecified_trim_body_and_drivetrain_include_all(self) -> None:
        query = parse_vehicle_query("honda civic")
        resolution = resolve_vehicle_query(query)
        self.assertIn("trim", resolution["include_all"])
        self.assertIn("body_style", resolution["include_all"])
        self.assertIn("drivetrain", resolution["include_all"])
        trim_chip = next(chip for chip in resolution["chips"] if chip["key"] == "trim")
        self.assertEqual(trim_chip["mode"], "all")
        self.assertEqual(trim_chip["value"], "All trims")

        score = vehicle_text_match_score(query, "2024 Honda Civic Sport Touring Hatchback", source="autotrader_browser")
        self.assertTrue(score["accepted"])
        self.assertEqual(score["confidence"], "exact_model_all_trims")

    def test_exact_trim_stays_restrictive(self) -> None:
        query = parse_vehicle_query("toyota camry xse")
        resolution = resolve_vehicle_query(query)
        self.assertNotIn("trim", resolution["include_all"])
        self.assertEqual(resolution["exact"]["trim"], "XSE")

        accepted = vehicle_text_match_score(query, "2024 Toyota Camry XSE Sedan", source="autotrader_browser")
        rejected = vehicle_text_match_score(query, "2024 Toyota Camry LE Sedan", source="autotrader_browser")
        self.assertTrue(accepted["accepted"])
        self.assertFalse(rejected["accepted"])


class ReportTests(unittest.TestCase):
    def test_report_has_age_zero_to_ten(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition after 2021")
        report = build_report(
            request=query,
            listings=sample_listings_for(query),
            msrp=MSRP(86600, "BMW M4 Competition Coupe starting MSRP", "bmwusa", "https://example.test"),
        )
        self.assertEqual(len(report["buckets"]), 11)
        self.assertEqual(report["buckets"][0]["age"], 0)
        self.assertEqual(report["buckets"][-1]["age"], 10)
        self.assertTrue(any(bucket["predicted"] for bucket in report["buckets"]))
        self.assertIn("duplicatesRemoved", report["summary"])

    def test_report_can_extend_to_twenty_year_horizon(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition after 2021")
        query.max_age = 20
        report = build_report(
            request=query,
            listings=sample_listings_for(query),
            msrp=MSRP(86600, "BMW M4 Competition Coupe starting MSRP", "bmwusa", "https://example.test"),
        )
        self.assertEqual(len(report["buckets"]), 21)
        self.assertEqual(report["buckets"][-1]["age"], 20)
        self.assertEqual(report["summary"]["maxAge"], 20)
        self.assertEqual(report["buckets"][-1]["confidence"], "long_range_projected")

    def test_unknown_car_needs_collection_not_fake_demo(self) -> None:
        query = parse_vehicle_query("Bentley Continental GT")
        report = build_report(query, sample_listings_for(query), MSRP(0, "Needs official MSRP capture", "needs_manufacturer_capture", ""))
        self.assertEqual(report["summary"]["listingCount"], 0)
        self.assertTrue(report["summary"]["needsSourceCapture"])
        self.assertEqual(report["summary"]["dataQuality"], "needs_collection")

    def test_dedupe_by_vin(self) -> None:
        rows = [
            Listing("edmunds", 2023, 83015, "Competition", 22958, "2023 BMW M4 Competition", vin="WBS43AZ02PCN03113"),
            Listing("autotrader", 2023, 83015, "Competition", 22958, "2023 BMW M4 Competition", vin="WBS43AZ02PCN03113"),
        ]
        deduped = dedupe_listings(rows)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0].source, "autotrader+edmunds")

    def test_dedupe_without_vin_same_dealer_price(self) -> None:
        rows = [
            Listing("edmunds", 2024, 74995, "Competition", 15800, "2024 BMW M4 Competition Coupe", dealer="North BMW"),
            Listing("autotrader", 2024, 74995, "Competition", 15820, "Used 2024 BMW M4 Competition Coupe", dealer="North BMW"),
        ]
        self.assertEqual(len(dedupe_listings(rows)), 1)

    def test_age_zero_can_include_new_vehicle_samples(self) -> None:
        query = parse_vehicle_query("Bentley Continental GT")
        rows = [
            Listing(
                "visor_public_facets_new",
                2026,
                305000,
                title="New 2026 Bentley Continental GT",
                confidence="new_vehicle_facets",
                condition="new",
            ),
            Listing(
                "visor_public_facets_new",
                2026,
                315000,
                title="New 2026 Bentley Continental GT",
                confidence="new_vehicle_facets",
                condition="new",
            ),
            Listing("visor_public_facets", 2025, 245000, title="2025 Bentley Continental GT", condition="used"),
        ]
        report = build_report(
            request=query,
            listings=rows,
            msrp=MSRP(288750, "Visor median listing MSRP for Bentley Continental GT", "visor_public_facets_new", "https://example.test", 2026),
        )
        age_zero = report["buckets"][0]
        self.assertEqual(age_zero["confidence"], "new_market")
        self.assertEqual(age_zero["sample_count"], 2)
        self.assertEqual(age_zero["median"], 310000)
        self.assertEqual(age_zero["source_counts"]["visor_public_facets_new"], 2)
        self.assertEqual(report["buckets"][1]["depreciation_from_baseline"], 65000)
        self.assertEqual(report["buckets"][1]["depreciation_from_baseline_pct"], 0.2097)
        self.assertEqual(report["listings"][0]["condition"], "new")

    def test_generation_adjustment_applies_to_predicted_rows(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        query.max_age = 3
        rows = [
            Listing(
                "new_inventory",
                2026,
                100000,
                "Competition Coupe",
                title="New 2026 BMW M4 Competition Coupe",
                confidence="new_inventory",
                condition="new",
            ),
            Listing(
                "used_market",
                2025,
                90000,
                "Competition Coupe",
                title="2025 BMW M4 Competition Coupe",
                condition="used",
            ),
        ]
        report = build_report(
            request=query,
            listings=rows,
            msrp=MSRP(86600, "BMW M4 Competition Coupe starting MSRP", "bmwusa", "https://example.test"),
            generation_impact={
                "query": "BMW M4 Competition",
                "status": "success",
                "adjustments": [
                    {
                        "age": 2,
                        "calendar_year": 2028,
                        "extra_depreciation_pct": 0.1,
                        "label": "New generation launch shock",
                        "basis": "Synthetic regression fixture.",
                    }
                ],
            },
        )
        age_one = report["buckets"][1]
        age_two = report["buckets"][2]
        self.assertFalse(age_one["predicted"])
        self.assertIsNone(age_one["generation_adjustment_pct"])
        self.assertTrue(age_two["predicted"])
        self.assertEqual(age_two["median"], 72900)
        self.assertEqual(age_two["generation_adjustment_pct"], 0.1)
        self.assertEqual(age_two["generation_adjustment_label"], "New generation launch shock")
        self.assertEqual(age_two["depreciation_from_baseline"], 27100)

    def test_generation_adjustment_applies_to_observed_future_proxy_age(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        query.max_age = 3
        rows = [
            Listing(
                "new_inventory",
                2026,
                100000,
                "Competition Coupe",
                title="New 2026 BMW M4 Competition Coupe",
                confidence="new_inventory",
                condition="new",
            ),
            Listing("used_market", 2025, 90000, "Competition Coupe", title="2025 BMW M4 Competition Coupe"),
            Listing("used_market", 2024, 82000, "Competition Coupe", title="2024 BMW M4 Competition Coupe"),
            Listing("used_market", 2023, 76000, "Competition Coupe", title="2023 BMW M4 Competition Coupe"),
        ]
        report = build_report(
            request=query,
            listings=rows,
            msrp=MSRP(86600, "BMW M4 Competition Coupe starting MSRP", "bmwusa", "https://example.test"),
            generation_impact={
                "query": "BMW M4 Competition",
                "status": "partial",
                "adjustments": [
                    {
                        "age": 99,
                        "calendar_year": 2029,
                        "extra_depreciation_pct": 0.06,
                        "label": "Expected replacement-generation launch shock",
                        "basis": "Synthetic calendar-year regression fixture.",
                    }
                ],
            },
            current_year=2026,
        )
        age_three = report["buckets"][3]
        self.assertTrue(age_three["observed"])
        self.assertFalse(age_three["predicted"])
        self.assertEqual(age_three["forecast_year"], 2029)
        self.assertEqual(age_three["generation_adjustment_pct"], 0.06)
        self.assertEqual(age_three["generation_adjustment_ratio"], 0.94)
        self.assertEqual(age_three["generation_unadjusted_median"], 76000)
        self.assertEqual(age_three["median"], 71440)
        self.assertEqual(age_three["depreciation_from_baseline"], 28560)

    def test_aggregate_facet_samples_are_not_deduped_as_dealer_duplicates(self) -> None:
        rows = [
            Listing("visor_public_facets", 2024, 80100, "Competition xDrive", title="2024 BMW M4 Competition xDrive Visor aggregate bin 1 sample 1", confidence="aggregate_facets"),
            Listing("visor_public_facets", 2024, 80200, "Competition xDrive", title="2024 BMW M4 Competition xDrive Visor aggregate bin 1 sample 2", confidence="aggregate_facets"),
        ]
        self.assertEqual(len(dedupe_listings(rows)), 2)

    def test_report_includes_source_evidence_rows(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition after 2021")
        report = build_report(
            request=query,
            listings=sample_listings_for(query),
            msrp=MSRP(86600, "BMW M4 Competition Coupe starting MSRP", "bmwusa", "https://example.test"),
        )
        self.assertIn("resolution", report)
        self.assertIn("evidence", report)
        self.assertGreater(len(report["evidence"]["sources"]), 0)
        self.assertGreater(len(report["evidence"]["listings"]), 0)
        self.assertIn("url", report["evidence"]["listings"][0])


class BrowserCaptureTests(unittest.TestCase):
    def test_parse_visible_text(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition xDrive after 2021")
        text = """
        2023 BMW M4
        Competition xDrive Coupe
        $83,015
        22,958 miles
        Check Availability
        """
        listings = parse_visible_listing_text("edmunds_browser", "https://example.test", text, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].year, 2023)
        self.assertEqual(listings[0].price, 83015)
        self.assertEqual(listings[0].mileage, 22958)

    def test_parse_visible_text_with_vin(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition xDrive after 2021")
        text = """
        2023 BMW M4
        Competition xDrive Coupe
        $83,015
        22,958 miles
        WBS43AZ02PCN03113
        """
        listings = parse_visible_listing_text("edmunds_browser", "https://example.test", text, query)
        self.assertEqual(listings[0].vin, "WBS43AZ02PCN03113")

    def test_parse_multiline_bentley_autotrader_capture(self) -> None:
        query = parse_vehicle_query("Bentley Continental GT Speed")
        text = """
        Used
        2022 Bentley Continental
        GT Speed
        6K mi
        234,999
        See payment
        No Accidents
        Sponsored by STERLING MOTORCARS
        Used
        2020 Bentley Continental
        GT
        22K mi
        153,900
        """
        listings = parse_visible_listing_text("autotrader_browser", "https://example.test", text, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].year, 2022)
        self.assertEqual(listings[0].price, 234999)
        self.assertEqual(listings[0].mileage, 6000)

    def test_bentley_continental_gt_does_not_match_gtc_or_other_bentley(self) -> None:
        query = parse_vehicle_query("Bentley Continental GT")
        text = """
        Used
        2023 Bentley Continental
        GTC Convertible
        3K mi
        251,000
        Used
        2022 Bentley Bentayga
        Speed
        12K mi
        189,500
        Used
        2021 Bentley Continental
        GT V8 Coupe
        19K mi
        176,900
        """
        listings = parse_visible_listing_text("autotrader_browser", "https://example.test", text, query)
        self.assertEqual(len(listings), 1)
        self.assertIn("GT", listings[0].title)
        self.assertEqual(listings[0].year, 2021)

    def test_parse_does_not_bleed_trim_from_next_row(self) -> None:
        query = parse_vehicle_query("Bentley Continental GT Speed")
        text = """
        Used
        2026 Bentley Continental
        GTC
        569 mi
        Plug-In Hybrid
        369,990
        Used
        2025 Bentley Continental
        GT Speed
        3K mi
        Plug-In Hybrid
        279,990
        """
        listings = parse_visible_listing_text("autotrader_browser", "https://example.test", text, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].year, 2025)

    def test_parse_autotrader_single_line_listing(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        text = """
        Used 2022 BMW M4 Competition
        32K mi
        71,088
        See payment
        """
        listings = parse_visible_listing_text("autotrader_browser", "https://example.test", text, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].price, 71088)

    def test_parse_visible_text_rejects_neighbor_trim_variants(self) -> None:
        cases = [
            (
                "Porsche 911 Carrera",
                """
                Used 2023 Porsche 911 Carrera S Coupe
                8K mi
                143,000
                Used 2023 Porsche 911 Carrera Coupe
                9K mi
                119,000
                """,
                "2023 Porsche 911 Carrera Coupe",
            ),
            (
                "Honda Civic EX",
                """
                Used 2022 Honda Civic EX-L CVT
                21K mi
                25,000
                Used 2022 Honda Civic EX CVT
                18K mi
                23,000
                """,
                "2022 Honda Civic EX CVT",
            ),
        ]
        for query_text, visible_text, expected_title in cases:
            with self.subTest(query_text=query_text):
                query = parse_vehicle_query(query_text)
                listings = parse_visible_listing_text("autotrader_browser", "https://example.test", visible_text, query)
                self.assertEqual(len(listings), 1)
                self.assertIn(expected_title, listings[0].title)


class VisorFacetTests(unittest.TestCase):
    def test_parse_visor_price_stats_and_bins(self) -> None:
        html = """
        range_facets:$R[248]={price:$R[249]={counts:$R[250]=[
        $R[251]={lower_bound:285900,upper_bound:292174,count:3},
        $R[252]={lower_bound:292174,upper_bound:298448,count:6}],interval:6274,start:285900,end:411380}},
        stats:$R[281]={price:$R[282]={min:285900,max:411375,count:18,missing:0,mean:309620,median:298891.5,stddev:29944.8},
        miles:$R[283]={min:24,max:7157,count:18,missing:0,mean:2676.2,median:2405,stddev:1827.4}}
        """
        stats = _parse_stat_block(html, "price")
        self.assertEqual(stats["count"], 18)
        self.assertEqual(stats["median"], 298891.5)
        bins = _parse_range_bins(html, "price")
        self.assertEqual(len(bins), 2)
        self.assertEqual(bins[0]["count"], 3)

    def test_visor_new_url_and_labeled_samples(self) -> None:
        query = parse_vehicle_query("Bentley Continental GT")
        url = _visor_url(query, 2026, car_type="new")
        self.assertIn("car_type=new", url)
        rows = [
            VisorYearData(
                year=2026,
                url=url,
                car_type="new",
                price_stats={},
                msrp_stats={},
                mileage_stats={"median": 20},
                price_bins=[{"lower": 300000, "upper": 302000, "count": 2}],
                num_found=2,
            )
        ]
        listings = _listings_from_years(query, rows, 2026)
        self.assertEqual(len(listings), 2)
        self.assertEqual(listings[0].source, NEW_SOURCE)
        self.assertEqual(listings[0].condition, "new")
        self.assertTrue(listings[0].title.startswith("New 2026"))

    def test_visor_numeric_trim_model_urls_do_not_duplicate_trim(self) -> None:
        lexus = parse_vehicle_query("lexus lc 500")
        lexus_url = _visor_url(lexus, 2026, car_type="used")
        self.assertIn("model=LC", lexus_url)
        self.assertNotIn("trim=500", lexus_url)

        mercedes = parse_vehicle_query("mercedes c300")
        mercedes_url = _visor_url(mercedes, 2026, car_type="used")
        self.assertIn("model=C-Class", mercedes_url)
        self.assertNotIn("model=C&", mercedes_url)
        self.assertNotIn("trim=300", mercedes_url)

    def test_visor_uses_source_version_aliases_for_trim_tokens(self) -> None:
        html = """
        version:$R[397]=[
        $R[398]={item:"-",count:269},
        $R[399]={item:"Competition Convertible xDrive",count:99},
        $R[400]={item:"Competition xDrive",count:81},
        $R[401]={item:"M4 Competition xDrive Coupe",count:62},
        $R[402]={item:"Competition",count:56}],
        year:$R[409]=[]
        """
        query = parse_vehicle_query("bmw m4 competition xdrive")
        items = _parse_facet_items(html, "version")
        matches = [item for item in items if _facet_value_matches_request(query, item["value"])]
        self.assertEqual([item["value"] for item in matches], ["Competition Convertible xDrive", "Competition xDrive", "M4 Competition xDrive Coupe"])

        url = _visor_url(query, 2026, car_type="used")
        self.assertNotIn("trim=Competition", url)

    def test_visor_numeric_variants_match_trim_or_version_aliases(self) -> None:
        lexus = parse_vehicle_query("lexus lc 500")
        self.assertTrue(_facet_value_matches_request(lexus, "500 Convertible"))
        self.assertFalse(_facet_value_matches_request(lexus, "500h"))

        mercedes = parse_vehicle_query("mercedes glc300")
        self.assertTrue(_facet_value_matches_request(mercedes, "GLC300 4MATIC"))
        self.assertTrue(_facet_value_matches_request(mercedes, "GLC 300"))
        self.assertFalse(_facet_value_matches_request(mercedes, "AMG GLC43"))

        c_class = parse_vehicle_query("mercedes c300")
        self.assertTrue(_facet_value_matches_request(c_class, "C300"))
        self.assertTrue(_facet_value_matches_request(c_class, "C 300 4MATIC"))
        self.assertFalse(_facet_value_matches_request(c_class, "AMG C43"))

    def test_visor_exact_trim_rejects_neighbor_variants(self) -> None:
        civic = parse_vehicle_query("honda civic ex")
        self.assertTrue(_facet_value_matches_request(civic, "EX CVT"))
        self.assertFalse(_facet_value_matches_request(civic, "EX-L CVT"))
        self.assertFalse(_facet_value_matches_request(civic, "EX-T CVT"))

        mustang = parse_vehicle_query("ford mustang gt")
        self.assertTrue(_facet_value_matches_request(mustang, "GT Coupe Premium"))
        self.assertFalse(_facet_value_matches_request(mustang, "Shelby GT500"))

        carrera = parse_vehicle_query("porsche 911 carrera")
        self.assertTrue(_facet_value_matches_request(carrera, "Carrera Coupe"))
        self.assertTrue(_facet_value_matches_request(carrera, "Carrera Cabriolet"))
        self.assertFalse(_facet_value_matches_request(carrera, "Carrera S Coupe"))
        self.assertFalse(_facet_value_matches_request(carrera, "Carrera GTS Coupe"))

        carrera_s = parse_vehicle_query("porsche 911 carrera s")
        self.assertTrue(_facet_value_matches_request(carrera_s, "Carrera S Coupe"))
        self.assertFalse(_facet_value_matches_request(carrera_s, "Carrera Coupe"))

        competition = parse_vehicle_query("bmw m4 competition")
        self.assertTrue(_facet_value_matches_request(competition, "M4 Competition Coupe"))
        self.assertFalse(_facet_value_matches_request(competition, "M4 Competition xDrive Coupe"))

    def test_visor_facet_evidence_keeps_raw_stats(self) -> None:
        row = VisorYearData(
            year=2026,
            url="https://example.test",
            car_type="new",
            price_stats={"median": 351503, "mean": 358881},
            msrp_stats={"median": 288750},
            mileage_stats={"median": 30},
            price_bins=[{"lower": 300000, "upper": 350000, "count": 4}],
            num_found=283,
        )
        evidence = _facet_evidence([row])
        self.assertEqual(evidence[0]["source"], NEW_SOURCE)
        self.assertEqual(evidence[0]["num_found"], 283)
        self.assertEqual(evidence[0]["price_bins"][0]["count"], 4)


class CollectionPlanTests(unittest.TestCase):
    def test_top_us_brands_have_official_sources(self) -> None:
        self.assertGreaterEqual(len(TOP_US_BRANDS), 40)
        self.assertGreaterEqual(len(MANUFACTURER_URLS), 40)
        missing = [brand for brand in TOP_US_BRANDS[:40] if brand not in MANUFACTURER_URLS]
        self.assertEqual(missing, [])

        query = parse_vehicle_query("subaru outback")
        query.max_age = 20
        plan = build_collection_plan(query)
        self.assertEqual(plan["query"]["max_age"], 20)
        self.assertIn("resolution", plan)
        self.assertIn("trim", plan["resolution"]["include_all"])
        manufacturer = next(target for target in plan["targets"] if target["source"] == "manufacturer_official_new")
        self.assertEqual(manufacturer["url"], MANUFACTURER_URLS["Subaru"])

    def test_plan_keeps_trim_specific_keywords(self) -> None:
        query = parse_vehicle_query("toyota camry xse")
        plan = build_collection_plan(query)
        self.assertEqual(plan["modelQuery"], "Camry")
        autotrader = next(target for target in plan["targets"] if target["source"] == "autotrader_browser")
        self.assertIn("XSE", autotrader["required_keywords"])
        visor = next(target for target in plan["targets"] if target["source"] == "visor_api_or_facets")
        self.assertNotIn("trim=XSE", visor["url"])

    def test_lexus_source_model_uses_number(self) -> None:
        query = parse_vehicle_query("lexus lc 500")
        plan = build_collection_plan(query)
        self.assertEqual(plan["modelQuery"], "LC 500")

    def test_bentley_autotrader_uses_continental_gt_path_and_filters(self) -> None:
        query = parse_vehicle_query("bentley continental GT")
        plan = build_collection_plan(query)
        autotrader = next(target for target in plan["targets"] if target["source"] == "autotrader_browser")
        self.assertIn("/bentley/continental/gt/", autotrader["url"])
        self.assertIn("searchRadius=0", autotrader["url"])
        self.assertTrue(autotrader["nationwide"])
        self.assertIn("GT", autotrader["required_keywords"])
        self.assertIn("GTC", autotrader["exclude_keywords"])
        self.assertIn("nationwide", autotrader["location_policy"].lower())


class CollectorPayloadTests(unittest.TestCase):
    def test_macos_chatgpt_cli_location_is_recognized(self) -> None:
        self.assertIn(
            Path("/Applications/ChatGPT.app/Contents/Resources/codex"),
            MACOS_CODEX_CLI_PATHS,
        )

    def test_codex_environment_preserves_configured_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            previous = os.environ.get("CODEX_HOME")
            os.environ["CODEX_HOME"] = tmp
            try:
                self.assertEqual(codex_environment()["CODEX_HOME"], str(Path(tmp).resolve()))
            finally:
                if previous is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = previous

    def test_login_status_uses_cli_instead_of_auth_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake_codex = Path(tmp) / "codex"
            fake_codex.write_text("#!/bin/sh\necho 'Logged in using ChatGPT'\n", encoding="utf-8")
            os.chmod(fake_codex, 0o755)
            status = codex_login_status(str(fake_codex))
            self.assertTrue(status["authenticated"])
            self.assertEqual(status["authMethod"], "chatgpt")

    def test_shared_cli_lookup_is_used_by_both_research_managers(self) -> None:
        expected_path = find_codex_cli()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            collector = CollectionManager(CollectorConfig(root=root))
            generation = GenerationResearchManager(GenerationResearchConfig(root=root))
            self.assertEqual(collector._codex_path(), expected_path)
            self.assertEqual(generation._codex_path(), expected_path)

    def test_codex_command_places_global_args_before_exec(self) -> None:
        command = build_codex_command(
            codex_path="/usr/local/bin/codex",
            root=Path("/tmp/car-compare"),
            schema_path=Path("/tmp/schema.json"),
            output_path=Path("/tmp/output.json"),
        )
        self.assertEqual(command[:4], ["/usr/local/bin/codex", "--ask-for-approval", "never", "exec"])
        self.assertIn("--output-schema", command)

    def test_clean_codex_error_keeps_usage_limit_message(self) -> None:
        raw = """
        2026-07-06T04:35:31Z  WARN codex_core_plugins::manifest: ignoring interface.defaultPrompt
        ERROR: You've hit your usage limit. Upgrade to Pro or try again at 4:51 PM.
        """
        cleaned = clean_codex_error(raw)
        self.assertNotIn("codex_core_plugins", cleaned)
        self.assertIn("usage limit", cleaned.lower())
        self.assertNotIn("https://", cleaned)
        self.assertEqual(codex_failure_message(cleaned), "Codex usage limit reached")

    def test_clean_codex_error_extracts_structured_message(self) -> None:
        raw = """
        ERROR: {
          "type": "error",
          "error": {
            "type": "invalid_request_error",
            "code": "invalid_json_schema",
            "message": "Invalid schema for response_format 'codex_output_schema': Missing 'condition'."
          }
        }
        """
        cleaned = clean_codex_error(raw)
        self.assertIn("Missing 'condition'", cleaned)
        self.assertEqual(codex_failure_message(cleaned), "Codex collector schema failed")

    def test_collector_schema_requires_every_listing_property(self) -> None:
        schema = json.loads(Path("car_compare/collector_schema.json").read_text(encoding="utf-8"))
        listing_schema = schema["properties"]["listings"]["items"]
        self.assertEqual(set(listing_schema["required"]), set(listing_schema["properties"]))

    def test_format_elapsed_for_heartbeat(self) -> None:
        self.assertEqual(_format_elapsed(8), "8s")
        self.assertEqual(_format_elapsed(75), "1m 15s")
        self.assertEqual(_format_elapsed(3671), "1h 1m 11s")

    def test_configured_codex_path_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manager = CollectionManager(
                CollectorConfig(root=root, codex_path=str(root / "missing-codex"), use_visor_facets=False)
            )
            self.assertFalse(manager.availability()["available"])

    def test_collection_job_reports_running_heartbeat(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_codex = root / "fake_codex.py"
            fake_codex.write_text(
                """#!/usr/bin/env python3
import json
import sys
import time
from pathlib import Path

if sys.argv[1:] == ["login", "status"]:
    print("Logged in using ChatGPT")
    raise SystemExit(0)

out = Path(sys.argv[sys.argv.index("-o") + 1])
sys.stdin.read()
time.sleep(1.0)
out.write_text(json.dumps({
    "query": "Honda Civic",
    "status": "success",
    "notes": [],
    "msrp": None,
    "sources": [],
    "listings": []
}))
""",
                encoding="utf-8",
            )
            os.chmod(fake_codex, 0o755)
            manager = CollectionManager(
                CollectorConfig(root=root, codex_path=str(fake_codex), timeout_seconds=10, use_visor_facets=False)
            )
            job = manager.start("Honda Civic")
            running = None
            # The deployment-safe path verifies `codex login status` before
            # launching the worker, so allow startup time on slower hosts.
            deadline = time.time() + 4
            while time.time() < deadline:
                current = manager.get(job.id)
                if current and current.status == "running" and current.process_id:
                    running = current
                    break
                time.sleep(0.05)
            self.assertIsNotNone(running)
            self.assertIn("PID", running.message)

            deadline = time.time() + 6
            while time.time() < deadline:
                current = manager.get(job.id)
                if current and current.status == "completed":
                    break
                time.sleep(0.05)
            self.assertEqual(manager.get(job.id).status, "completed")

    def test_listings_from_collector_result(self) -> None:
        result = {
            "listings": [
                {
                    "source": "edmunds_browser",
                    "year": 2026,
                    "price": 324999,
                    "trim": "GT Speed",
                    "mileage": 20,
                    "title": "New 2026 Bentley Continental GT Speed",
                    "url": "https://example.test",
                    "vin": "SCBCG2ZG0NC000001",
                    "dealer": "Example Bentley",
                    "condition": "new",
                    "confidence": "new_inventory",
                }
            ]
        }
        listings = listings_from_result(result)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].vin, "SCBCG2ZG0NC000001")
        self.assertEqual(listings[0].condition, "new")
        self.assertEqual(listings[0].confidence, "new_inventory")

    def test_msrp_from_collector_result(self) -> None:
        msrp = msrp_from_result(
            {
                "msrp": {
                    "price": 302100,
                    "label": "Bentley Continental GT Speed MSRP",
                    "source": "bentley",
                    "url": "https://example.test",
                    "year": 2026,
                }
            }
        )
        self.assertIsNotNone(msrp)
        self.assertEqual(msrp.price, 302100)


if __name__ == "__main__":
    unittest.main()
