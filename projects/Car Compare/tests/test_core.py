from __future__ import annotations

import os
import re
import base64
import hashlib
import hmac
import json
import tempfile
import time
import unittest
from unittest.mock import patch
from dataclasses import replace
from io import BytesIO
from types import SimpleNamespace

from car_compare.depreciation import build_report, dedupe_listings
from pathlib import Path

from car_compare.collector import (
    CollectionManager,
    CollectorConfig,
    _apply_browser_captures,
    _format_elapsed,
    _merge_collector_results,
    build_codex_command,
    clean_codex_error,
    codex_failure_message,
    listings_from_result,
    msrp_from_result,
)
from car_compare.codex_cli import MACOS_CODEX_CLI_PATHS, codex_environment, codex_login_status, find_codex_cli
from car_compare.generation_impact import GenerationResearchConfig, GenerationResearchManager
from car_compare.models import Listing, MSRP, VehicleQuery
from car_compare.parser import parse_vehicle_query
from car_compare.resolver import resolve_vehicle_query
from car_compare.sample_data import default_msrp_for, sample_listings_for
from car_compare.shared_auth import SharedSessionAuth, valid_shared_session_token
from car_compare.sources.browser_capture import parse_visible_listing_text
from car_compare.sources.source_plan import MANUFACTURER_URLS, TOP_US_BRANDS, build_collection_plan
from car_compare.sources.visor_facets import (
    NEW_SOURCE,
    VisorYearData,
    collect_visor_public_facets,
    _allocate_bin_samples,
    _facet_evidence,
    _facet_value_matches_request,
    _fetch_visor_facets,
    _html_confirms_vehicle,
    _listings_from_years,
    _parse_facet_items,
    _parse_range_bins,
    _parse_stat_block,
    _requested_years,
    _visor_url,
)
from car_compare.statistics import percentile
from car_compare.vehicle_match import vehicle_text_match_score
from car_compare.vehicle_catalog import MODEL_CATALOG
import app as web_app


class SharedAuthTests(unittest.TestCase):
    def _token(self, username: str, secret: str, expires: int) -> str:
        payload = f"{username}|{expires}|test-nonce"
        signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return base64.urlsafe_b64encode(f"{payload}|{signature}".encode()).decode().rstrip("=")

    def test_accepts_current_shared_session(self) -> None:
        token = self._token("admin", "shared-secret", int(time.time()) + 60)
        self.assertTrue(valid_shared_session_token(token, "admin", "shared-secret"))
        auth = SharedSessionAuth("admin", "shared-secret")
        self.assertTrue(auth.valid_cookie_header(f"theme=dark; dem_session={token}"))

    def test_rejects_expired_or_wrong_secret(self) -> None:
        expired = self._token("admin", "shared-secret", int(time.time()) - 1)
        current = self._token("admin", "shared-secret", int(time.time()) + 60)
        self.assertFalse(valid_shared_session_token(expired, "admin", "shared-secret"))
        self.assertFalse(valid_shared_session_token(current, "admin", "wrong-secret"))

    def test_login_redirect_uses_fixed_public_origin(self) -> None:
        auth = SharedSessionAuth("admin", "shared-secret")
        redirect = auth.login_redirect("/api/setup?full=1")
        self.assertIn("dem.nsyprojects.com/login", redirect)
        self.assertIn("carcompare.nsyprojects.com%2Fapi%2Fsetup%3Ffull%3D1", redirect)


class AppContractTests(unittest.TestCase):
    def test_json_body_contract_rejects_invalid_non_object_and_oversize_payloads(self) -> None:
        cases = [
            (b"{bad", 400),
            (b"[]", 400),
        ]
        for raw, expected_status in cases:
            with self.subTest(raw=raw):
                handler = SimpleNamespace(headers={"Content-Length": str(len(raw))}, rfile=BytesIO(raw))
                with self.assertRaises(web_app.RequestBodyError) as raised:
                    web_app.CarCompareHandler._read_json(handler)
                self.assertEqual(raised.exception.status, expected_status)

        handler = SimpleNamespace(
            headers={"Content-Length": str(web_app.MAX_REQUEST_BODY_BYTES + 1)},
            rfile=BytesIO(b""),
        )
        with self.assertRaises(web_app.RequestBodyError) as raised:
            web_app.CarCompareHandler._read_json(handler)
        self.assertEqual(raised.exception.status, 413)

    def test_production_mode_does_not_inject_bundled_sample_rows(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        with patch.object(web_app, "SAMPLE_MODE_ENABLED", False):
            self.assertEqual(web_app._initial_listings(query), [])
            self.assertEqual(web_app._initial_msrp(query).price, 0)
            self.assertEqual(web_app._initial_msrp(query).source, "needs_manufacturer_capture")
        with patch.object(web_app, "SAMPLE_MODE_ENABLED", True):
            self.assertGreater(len(web_app._initial_listings(query)), 0)
            self.assertIn("demo", web_app._initial_msrp(query).source)

    def test_manual_msrp_validation_and_vehicle_identity_contract(self) -> None:
        self.assertEqual(web_app._validated_vehicle_price("$86,600"), 86600)
        for invalid in ["NaN", -1, 1200, web_app.MAX_MSRP_PRICE + 1]:
            with self.subTest(invalid=invalid), self.assertRaises((TypeError, ValueError)):
                web_app._validated_vehicle_price(invalid)
        self.assertTrue(web_app._has_vehicle_identity(parse_vehicle_query("Civic")))
        self.assertTrue(web_app._has_vehicle_identity(parse_vehicle_query("UnknownMake UnknownModel")))
        self.assertFalse(web_app._has_vehicle_identity(parse_vehicle_query("2022")))
        self.assertFalse(web_app._has_vehicle_identity(parse_vehicle_query("BMW")))

    def test_unauthenticated_api_get_returns_json_401_instead_of_redirect(self) -> None:
        sent: list[tuple[dict[str, str], int]] = []
        handler = SimpleNamespace(
            path="/api/collect/job-id",
            headers={},
            command="GET",
            _send_json=lambda payload, status=200: sent.append((payload, status)),
        )
        auth = SimpleNamespace(enabled=True, valid_cookie_header=lambda _header: False)
        with patch.object(web_app, "AUTH", auth):
            self.assertFalse(web_app.CarCompareHandler._require_auth(handler))
        self.assertEqual(sent, [({"error": "authentication_required"}, 401)])

    def test_request_key_binds_canonical_vehicle_and_horizon(self) -> None:
        typo = parse_vehicle_query("BMW M4 Cometition")
        typo.max_age = 10
        canonical = parse_vehicle_query("BMW M4 Competition")
        canonical.max_age = 10
        longer = parse_vehicle_query("BMW M4 Competition")
        longer.max_age = 15
        self.assertEqual(web_app._request_key(typo), web_app._request_key(canonical))
        self.assertNotEqual(web_app._request_key(canonical), web_app._request_key(longer))

    def test_report_metadata_separates_dealer_aggregate_and_demo_rows(self) -> None:
        report = {
            "summary": {"listingCount": 9, "sources": {"autotrader": 3, "visor_public_facets": 4, "sample": 2}},
            "evidence": {
                "listings": [
                    {"source": "autotrader", "year": 2024, "dealer": "Dealer A"},
                    {"source": "autotrader", "year": 2024, "dealer": "Dealer B"},
                    {"source": "autotrader", "year": 2024, "dealer": "Dealer C"},
                ]
            },
        }
        with patch.object(web_app, "SAMPLE_MODE_ENABLED", False):
            web_app._attach_report_metadata(report)
        self.assertEqual(report["summary"]["dealerListings"], 3)
        self.assertEqual(report["summary"]["individualListingRows"], 3)
        self.assertEqual(report["summary"]["aggregateObservationPoints"], 4)
        self.assertEqual(report["summary"]["aggregateMarketCount"], 4)
        self.assertEqual(report["summary"]["sampleRows"], 2)

        demo_report = {"summary": {"listingCount": 9, "sources": {"autotrader": 3, "visor_public_facets": 4, "sample": 2}}}
        with patch.object(web_app, "SAMPLE_MODE_ENABLED", True):
            web_app._attach_report_metadata(demo_report)
        self.assertEqual(demo_report["summary"]["dealerListings"], 0)
        self.assertEqual(demo_report["summary"]["aggregateObservationPoints"], 0)
        self.assertEqual(demo_report["summary"]["aggregateMarketCount"], 0)
        self.assertEqual(demo_report["summary"]["sampleRows"], 9)

        rejected_facets = {
            "summary": {"listingCount": 0, "sources": {}},
            "evidence": {
                "listings": [],
                "facets": [{"source": "visor_public_facets", "year": 2024, "price_bins": [{"count": 100}]}],
            },
        }
        with patch.object(web_app, "SAMPLE_MODE_ENABLED", False):
            web_app._attach_report_metadata(rejected_facets)
        self.assertEqual(rejected_facets["summary"]["aggregateMarketCount"], 0)


class ParserTests(unittest.TestCase):
    def test_corrects_high_confidence_make_model_and_trim_typos(self) -> None:
        query = parse_vehicle_query("Toyta Camy XSE")
        self.assertEqual((query.make, query.model, query.trim), ("Toyota", "Camry", "XSE"))
        self.assertEqual([item["field"] for item in query.corrections], ["make", "model"])

        competition = parse_vehicle_query("BMW M4 Cometition")
        self.assertEqual(competition.trim, "Competition")
        self.assertEqual(competition.corrections, [{"field": "trim", "original": "Cometition", "corrected": "Competition"}])

    def test_damerau_typo_correction_handles_transpositions_and_discloses_them(self) -> None:
        cases = {
            "BWM M4": ("BMW", "M4", ""),
            "Telsa Modle Y": ("Tesla", "Model Y", ""),
            "Hodna Civic": ("Honda", "Civic", ""),
            "Bucik Envision": ("Buick", "Envision", ""),
            "Bently Continetal GT": ("Bentley", "Continental GT", ""),
            "Merceds GLE": ("Mercedes-Benz", "GLE", ""),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                query = parse_vehicle_query(text)
                self.assertEqual((query.make, query.model, query.trim), expected)
                self.assertTrue(query.corrections)
                resolution = resolve_vehicle_query(query)
                for correction in query.corrections:
                    self.assertTrue(
                        any(
                            correction["original"] in warning and correction["corrected"] in warning
                            for warning in resolution["warnings"]
                        )
                    )

    def test_model_parser_normalizes_attached_split_and_longer_sibling_forms(self) -> None:
        cases = {
            "Chevy Silverado1500 LT": ("Chevrolet", "Silverado 1500", "LT"),
            "Mercedes c class 300": ("Mercedes-Benz", "C-Class", "300"),
            "Toyota rav 4 xse": ("Toyota", "RAV4", "XSE"),
            "Ford broncosport": ("Ford", "Bronco Sport", ""),
            "Bentley ContinentalGT": ("Bentley", "Continental GT", ""),
            "Volkswagen Atlas Corss Sport": ("Volkswagen", "Atlas Cross Sport", ""),
            "Ford Bronco Sprt": ("Ford", "Bronco Sport", ""),
            "Mitsubishi Outlander Sprt": ("Mitsubishi", "Outlander Sport", ""),
            "Land Rover Discovery Sprt": ("Land Rover", "Discovery Sport", ""),
            "Bentley Continental TG": ("Bentley", "Continental GT", ""),
            "Bentley Continental GCT": ("Bentley", "Continental GTC", ""),
            "Cadillac Escalade IQQ": ("Cadillac", "Escalade IQ", ""),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                query = parse_vehicle_query(text)
                self.assertEqual((query.make, query.model, query.trim), expected)

    def test_longer_make_alias_typo_does_not_consume_model_or_trim(self) -> None:
        cases = {
            "Mercedes Bnez GLE": ("Mercedes-Benz", "GLE", ""),
            "Rolls Royec Ghost": ("Rolls-Royce", "Ghost", ""),
            "RAM Trcuk 1500": ("RAM", "1500", ""),
            "Mercedes-Benz SL": ("Mercedes-Benz", "SL", ""),
            "BMW 3 Series 330i": ("BMW", "3 Series", "330i"),
            "Honda Civic S": ("Honda", "Civic", "S"),
            "Ford Bronco Big Bend": ("Ford", "Bronco", "Big Bend"),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                query = parse_vehicle_query(text)
                self.assertEqual((query.make, query.model, query.trim), expected)

    def test_trim_transpositions_use_unique_catalog_winner(self) -> None:
        cases = {
            "Audi Q5 Premium Plsu": "Premium Plus",
            "Honda Civic Tuoring": "Touring",
            "Ford F-150 Larait": "Lariat",
            "Toyota Camry Limtied": "Limited",
            "Porsche 911 Carerra": "Carrera",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                query = parse_vehicle_query(text)
                self.assertEqual(query.trim, expected)
                self.assertEqual(query.corrections[-1]["field"], "trim")

    def test_true_single_edit_model_ties_are_left_unmodified(self) -> None:
        self.assertEqual(parse_vehicle_query("Aston Martin DB2").model, "Db2")
        self.assertEqual(parse_vehicle_query("Lincoln Naviator").model, "Naviator")

    def test_real_historical_compact_models_are_not_changed_to_near_neighbors(self) -> None:
        cases = {
            "Acura ILX": "ILX",
            "Aston Martin DBS": "DBS",
            "Aston Martin DB9": "DB9",
            "Audi RS3": "RS 3",
            "Audi RS5": "RS 5",
            "Audi RS7": "RS 7",
            "Chrysler 200": "200",
            "Honda CR-Z": "CR-Z",
            "Honda HRV": "HR-V",
            "INFINITI Q70": "Q70",
            "Mazda CX-9": "CX-9",
            "Mazda CX-7": "CX-7",
            "Mazda CX-3": "CX-3",
            "Mazda6": "Mazda6",
            "Mazda Mazda6": "Mazda6",
            "McLaren 570S": "570S",
            "McLaren 650S": "650S",
            "Porsche 914": "914",
            "Volvo C30": "C30",
        }
        for text, expected_model in cases.items():
            with self.subTest(text=text):
                query = parse_vehicle_query(text)
                self.assertEqual(query.model, expected_model)
                self.assertFalse(any(item["field"] == "model" for item in query.corrections))

    def test_real_bmw_compact_trims_are_not_changed_to_330i(self) -> None:
        cases = {
            "BMW 3 Series 320i": "320i",
            "BMW 3 Series 335i": "335i",
            "BMW 3 Series 320i xDrive": "320i xDrive",
        }
        for text, expected_trim in cases.items():
            with self.subTest(text=text):
                query = parse_vehicle_query(text)
                self.assertEqual(query.trim, expected_trim)
                self.assertFalse(any(item["field"] == "trim" for item in query.corrections))

    def test_unique_make_and_model_single_edit_property_subset(self) -> None:
        def variants(value: str) -> list[str]:
            index = (len(value) // 2) - 1
            return [
                value[:index] + value[index + 1] + value[index] + value[index + 2 :],
                value[:index] + value[index + 1 :],
            ]

        make_cases = [
            ("Toyota", "Camry"),
            ("Honda", "Civic"),
            ("Buick", "Envision"),
            ("Bentley", "Bentayga"),
            ("Tesla", "Model Y"),
            ("Subaru", "Outback"),
            ("Porsche", "Cayenne"),
        ]
        for make, model in make_cases:
            for typo in variants(make):
                with self.subTest(field="make", canonical=make, typo=typo):
                    query = parse_vehicle_query(f"{typo} {model}")
                    self.assertEqual((query.make, query.model), (make, model))

        model_cases = [
            ("Toyota", "Camry"),
            ("Honda", "Civic"),
            ("Buick", "Envision"),
            ("Bentley", "Bentayga"),
            ("Kia", "Telluride"),
            ("Porsche", "Cayenne"),
            ("Subaru", "Outback"),
        ]
        for make, model in model_cases:
            for typo in variants(model):
                with self.subTest(field="model", canonical=model, typo=typo):
                    query = parse_vehicle_query(f"{make} {typo}")
                    self.assertEqual((query.make, query.model), (make, model))

    def test_leaves_unknown_or_ambiguous_trim_text_untouched(self) -> None:
        self.assertEqual(parse_vehicle_query("BMW M4 Heritage").trim, "Heritage")
        self.assertEqual(parse_vehicle_query("Porsche 911 Carrera T").trim, "Carrera T")

    def test_resolver_discloses_automatic_correction(self) -> None:
        resolution = resolve_vehicle_query(parse_vehicle_query("BMW M4 Cometition"))
        self.assertEqual(resolution["canonical"], "BMW M4 Competition")
        self.assertEqual(resolution["confidence"], "medium")
        self.assertIn('Corrected trim spelling from "Cometition" to "Competition".', resolution["warnings"])
        self.assertIn("Competition", resolution["matching"]["required_keywords"])
        self.assertNotIn("Cometition", resolution["matching"]["required_keywords"])

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

    def test_exact_trim_discloses_named_drivetrain_sibling_exclusion(self) -> None:
        for text, sibling in [
            ("BMW 3 Series 330i", "330i xDrive"),
        ]:
            with self.subTest(text=text):
                resolution = resolve_vehicle_query(parse_vehicle_query(text))
                drivetrain = next(
                    chip for chip in resolution["chips"] if chip["key"] == "drivetrain"
                )
                self.assertNotIn("drivetrain", resolution["include_all"])
                self.assertEqual(drivetrain["mode"], "constrained")
                self.assertEqual(drivetrain["value"], "Constrained by exact trim")
                self.assertTrue(any(sibling in warning for warning in resolution["warnings"]))

    def test_m4_competition_is_a_generation_aware_family(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        resolution = resolve_vehicle_query(query)
        self.assertIn("drivetrain", resolution["include_all"])
        self.assertIn("body_style", resolution["include_all"])
        self.assertTrue(any("generation-aware family" in item for item in resolution["warnings"]))

        accepted = [
            "2025 BMW M4 Competition Coupe",
            "2024 BMW M4 Competition xDrive Coupe",
            "2023 BMW M4 Competition xDrive Convertible",
            "2018 BMW M4 Coupe with Competition Package",
            "2017 BMW M4 Convertible ZCP Competition Package",
        ]
        rejected = [
            "2024 BMW M4 Coupe Base",
            "2024 BMW M4 CS",
            "2023 BMW M4 CSL",
            "2016 BMW M4 GTS",
        ]
        for title in accepted:
            with self.subTest(title=title):
                self.assertTrue(vehicle_text_match_score(query, title, source="autotrader_browser")["accepted"])
        for title in rejected:
            with self.subTest(title=title):
                self.assertFalse(vehicle_text_match_score(query, title, source="autotrader_browser")["accepted"])

    def test_family_models_match_common_dealer_shorthand_without_losing_trim_precision(self) -> None:
        accepted = [
            ("BMW 3 Series 330i", "2024 BMW 330i Sedan"),
            ("BMW 3 Series M340i", "2024 BMW M340i Sedan"),
            ("BMW 4 Series 430i", "2024 BMW 430i Coupe"),
            ("BMW 4 Series 440i", "2024 BMW 440i Coupe"),
            ("Mercedes CLA250", "2024 Mercedes-Benz CLA250 Coupe"),
            ("Mercedes CLE300", "2024 Mercedes-Benz CLE300 Coupe"),
            ("Mercedes GLE 450", "2024 Mercedes-Benz GLE450 4MATIC SUV"),
        ]
        for query_text, title in accepted:
            with self.subTest(query=query_text, title=title):
                score = vehicle_text_match_score(parse_vehicle_query(query_text), title)
                self.assertTrue(score["accepted"])

        rejected = [
            ("BMW 3 Series 330i", "2024 BMW 330i xDrive Sedan"),
            ("BMW 3 Series 330i", "2024 BMW 340i Sedan"),
            ("Mercedes GLE 350", "2024 Mercedes-Benz GLE350 4MATIC SUV"),
        ]
        for query_text, title in rejected:
            with self.subTest(query=query_text, title=title):
                score = vehicle_text_match_score(parse_vehicle_query(query_text), title)
                self.assertFalse(score["accepted"])

    def test_sample_source_does_not_bypass_vehicle_matching(self) -> None:
        query = parse_vehicle_query("Toyota Camry XSE")
        score = vehicle_text_match_score(query, "2024 BMW M4 Competition Coupe", source="sample")
        self.assertFalse(score["accepted"])

    def test_catalog_neighbor_trims_are_rejected_generically(self) -> None:
        cases = [
            ("Audi Q5 Premium", "2024 Audi Q5 Premium Plus"),
            ("Subaru Outback Touring", "2024 Subaru Outback Touring XT"),
            ("Kia Telluride SX", "2024 Kia Telluride SX Prestige"),
            ("BMW 3 Series 330i", "2024 BMW 3 Series 330i xDrive"),
        ]
        for query_text, title in cases:
            with self.subTest(query=query_text):
                score = vehicle_text_match_score(parse_vehicle_query(query_text), title, source="sample")
                self.assertFalse(score["accepted"])
                self.assertEqual(score["confidence"], "rejected_trim_variant")

        exact = vehicle_text_match_score(
            parse_vehicle_query("Audi Q5 Premium Plus"),
            "2024 Audi Q5 Premium Plus",
            source="sample",
        )
        self.assertTrue(exact["accepted"])

    def test_make_aliases_and_attached_f150_match_as_whole_tokens(self) -> None:
        cases = [
            ("Mercedes C300", "2024 Mercedes C300 Sedan"),
            ("Chevy Corvette Z06", "2024 Chevy Corvette Z06 Coupe"),
            ("Ford F-150 Lariat", "2024 Ford F150 Lariat SuperCrew"),
        ]
        for query_text, title in cases:
            with self.subTest(query=query_text):
                self.assertTrue(vehicle_text_match_score(parse_vehicle_query(query_text), title, source="sample")["accepted"])

    def test_catalog_models_accept_self_and_reject_strict_superset_siblings(self) -> None:
        for make, models in MODEL_CATALOG.items():
            for model in models:
                request = VehicleQuery(raw=f"{make} {model}", make=make, model=model)
                with self.subTest(make=make, model=model, case="self"):
                    self.assertTrue(
                        vehicle_text_match_score(request, f"2024 {make} {model}", source="catalog_test")["accepted"]
                    )

                requested_tokens = set(re.findall(r"[a-z0-9]+", model.lower().replace("-", " ")))
                for sibling in models:
                    sibling_tokens = set(re.findall(r"[a-z0-9]+", sibling.lower().replace("-", " ")))
                    if not requested_tokens < sibling_tokens:
                        continue
                    with self.subTest(make=make, model=model, sibling=sibling):
                        score = vehicle_text_match_score(
                            request,
                            f"2024 {make} {sibling}",
                            source="catalog_test",
                        )
                        self.assertFalse(score["accepted"])
                        self.assertEqual(score["confidence"], "rejected_model_variant")

    def test_model_sibling_words_in_descriptions_do_not_trigger_conflict(self) -> None:
        cases = [
            ("Ford Bronco Big Bend", "2024 Ford Bronco Big Bend Sport Utility"),
            ("Mitsubishi Outlander SE", "2024 Mitsubishi Outlander SE Sport Utility"),
            ("Land Rover Discovery S", "2024 Land Rover Discovery S Sport Utility"),
            ("Land Rover Range Rover SE", "2024 Land Rover Range Rover SE Sport Utility"),
        ]
        for query_text, title in cases:
            with self.subTest(query=query_text):
                self.assertTrue(vehicle_text_match_score(parse_vehicle_query(query_text), title, source="catalog_test")["accepted"])

        self.assertFalse(
            vehicle_text_match_score(
                parse_vehicle_query("Ford Bronco"),
                "2024 Ford Bronco Sport Big Bend",
                source="catalog_test",
            )["accepted"]
        )
        self.assertFalse(
            vehicle_text_match_score(
                parse_vehicle_query("Ford Bronco"),
                "2024 Ford Bronco Sport Utility 4D",
                source="catalog_test",
            )["accepted"]
        )

    def test_trim_sibling_words_in_descriptions_do_not_trigger_conflict(self) -> None:
        accepted = vehicle_text_match_score(
            parse_vehicle_query("Porsche Cayenne S"),
            "2024 Porsche Cayenne S AWD Twin Turbo V8",
            source="catalog_test",
        )
        rejected = vehicle_text_match_score(
            parse_vehicle_query("Porsche Cayenne S"),
            "2024 Porsche Cayenne Turbo S AWD",
            source="catalog_test",
        )
        self.assertTrue(accepted["accepted"])
        self.assertFalse(rejected["accepted"])
        self.assertEqual(rejected["confidence"], "rejected_trim_variant")


class ReportTests(unittest.TestCase):
    def test_msrp_reference_drives_depreciation_when_new_market_samples_are_missing(self) -> None:
        query = parse_vehicle_query("BMW M4 Cometition")
        query.max_age = 15
        report = build_report(query, sample_listings_for(query), default_msrp_for(query))
        age_zero = report["buckets"][0]
        self.assertEqual(report["summary"]["displayName"], "BMW M4 Competition")
        self.assertEqual(report["msrp"]["price"], 86600)
        self.assertIn("2026 historical", report["msrp"]["label"])
        self.assertEqual(report["msrp"]["source"], "bmwusa_demo_reference_2026")
        self.assertEqual(age_zero["confidence"], "msrp_reference")
        self.assertFalse(age_zero["observed"])
        self.assertEqual(age_zero["trend_median"], 86600)
        self.assertTrue(any(bucket["depreciation_from_baseline"] for bucket in report["buckets"][1:]))

    def test_reference_msrp_is_year_and_variant_specific(self) -> None:
        cases = [
            VehicleQuery(raw="BMW M4", make="BMW", model="M4", trim=""),
            VehicleQuery(raw="BMW M4 Competition xDrive", make="BMW", model="M4", trim="Competition xDrive"),
            VehicleQuery(raw="BMW M4 Competition Convertible", make="BMW", model="M4", trim="Competition Convertible"),
        ]
        for query in cases:
            with self.subTest(query=query.raw):
                self.assertEqual(default_msrp_for(query, current_year=2026).price, 0)

        exact = VehicleQuery(raw="BMW M4 Competition", make="BMW", model="M4", trim="Competition")
        self.assertEqual(default_msrp_for(exact, current_year=2026).price, 86600)
        self.assertEqual(default_msrp_for(exact, current_year=2027).price, 0)
        exact.target_year = 2026
        self.assertEqual(default_msrp_for(exact, current_year=2027).price, 86600)

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

    def test_used_only_report_builds_disclosed_estimated_baseline(self) -> None:
        query = parse_vehicle_query("Toyota Camry XSE")
        rows = [
            Listing("used_market", 2022, 25000, "XSE", 45000, "2022 Toyota Camry XSE", dealer="Toyota Dealer")
        ]
        report = build_report(query, rows, MSRP(0, "No MSRP", "needs_manufacturer_capture", ""), current_year=2026)
        self.assertEqual(report["msrp"]["source"], "estimated_from_used_market")
        self.assertGreater(report["msrp"]["price"], 25000)
        self.assertEqual(report["buckets"][0]["confidence"], "estimated_baseline")
        self.assertTrue(report["summary"]["needsMsrpCapture"])
        self.assertIsNotNone(report["buckets"][4]["depreciation_from_baseline"])

    def test_target_year_report_uses_one_cohort_lifecycle_and_generation_clock(self) -> None:
        query = parse_vehicle_query("2022 Toyota Camry XSE")
        query.max_age = 6
        rows = [
            Listing(
                "used_market",
                2022,
                25000,
                "XSE",
                45000,
                "2022 Toyota Camry XSE",
            )
        ]
        generation = {
            "status": "success",
            "adjustments": [
                {
                    "calendar_year": 2028,
                    "extra_depreciation_pct": 0.1,
                    "label": "Generation event",
                }
            ],
        }
        report = build_report(
            query,
            rows,
            MSRP(0, "No MSRP", "needs_manufacturer_capture", ""),
            current_year=2026,
            generation_impact=generation,
        )
        self.assertEqual(report["msrp"]["year"], 2022)
        self.assertIn("age-0 baseline", report["msrp"]["label"])
        self.assertTrue(all(bucket["model_year"] == 2022 for bucket in report["buckets"]))
        self.assertTrue(all(bucket["model_years"] == [2022] for bucket in report["buckets"]))
        self.assertEqual(
            [bucket["forecast_year"] for bucket in report["buckets"]],
            list(range(2022, 2029)),
        )
        self.assertTrue(report["buckets"][4]["observed"])
        self.assertEqual(report["generationImpact"]["adjustments"][0]["age"], 6)
        self.assertIsNone(report["buckets"][5]["generation_adjustment_pct"])
        self.assertEqual(report["buckets"][6]["generation_adjustment_pct"], 0.1)

        empty = build_report(
            query,
            [],
            MSRP(0, "No MSRP", "needs_manufacturer_capture", ""),
            current_year=2026,
        )
        self.assertTrue(all(bucket["model_year"] == 2022 for bucket in empty["buckets"]))
        self.assertEqual(
            [bucket["forecast_year"] for bucket in empty["buckets"]],
            list(range(2022, 2029)),
        )

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

    def test_dedupe_vin_and_no_vin_is_order_independent(self) -> None:
        rows = [
            Listing(
                "edmunds",
                2024,
                74995,
                "Competition",
                15800,
                "2024 BMW M4 Competition Coupe",
                vin="WBS43AZ02PCN03113",
                dealer="North BMW",
            ),
            Listing(
                "autotrader",
                2024,
                74995,
                "Competition",
                15820,
                "Used 2024 BMW M4 Competition Coupe",
                dealer="North BMW",
            ),
        ]
        forward = dedupe_listings(rows)
        reverse = dedupe_listings(list(reversed(rows)))
        self.assertEqual([item.to_dict() for item in forward], [item.to_dict() for item in reverse])
        self.assertEqual(len(forward), 1)
        self.assertEqual(forward[0].vin, "WBS43AZ02PCN03113")
        self.assertEqual(forward[0].source, "autotrader+edmunds")

    def test_dedupe_never_merges_different_vins(self) -> None:
        rows = [
            Listing("one", 2024, 74995, "Competition", 15800, "2024 BMW M4 Competition", vin="WBS43AZ02PCN03113"),
            Listing("two", 2024, 74995, "Competition", 15800, "2024 BMW M4 Competition", vin="WBS43AZ02PCN03114"),
        ]
        self.assertEqual(len(dedupe_listings(rows)), 2)

    def test_dedupe_same_source_different_detail_urls_stay_distinct(self) -> None:
        rows = [
            Listing(
                "dealer_feed",
                2024,
                74995,
                "Competition",
                15800,
                "2024 BMW M4 Competition",
                url="https://dealer.test/vehicle/STOCK-A",
                dealer="North BMW",
            ),
            Listing(
                "dealer_feed",
                2024,
                74995,
                "Competition",
                16300,
                "2024 BMW M4 Competition",
                url="https://dealer.test/vehicle/STOCK-B",
                dealer="North BMW",
            ),
        ]
        self.assertEqual(len(dedupe_listings(rows)), 2)

    def test_dedupe_same_detail_url_allows_price_drift_and_cpo_used(self) -> None:
        rows = [
            Listing(
                "edmunds",
                2024,
                74995,
                "Competition",
                15800,
                "2024 BMW M4 Competition",
                url="https://dealer.test/vehicle/ABC123?utm_source=edmunds",
                dealer="North BMW",
                condition="cpo",
            ),
            Listing(
                "autotrader",
                2024,
                75995,
                "Competition",
                15820,
                "Used 2024 BMW M4 Competition",
                url="https://dealer.test/vehicle/ABC123?ref=autotrader",
                dealer="North BMW Center",
                condition="used",
            ),
        ]
        deduped = dedupe_listings(rows)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0].condition, "cpo")

    def test_dedupe_shared_stock_id_needs_supporting_vehicle_identity(self) -> None:
        matching = [
            Listing(
                "one",
                2024,
                74995,
                "Competition",
                15800,
                "2024 BMW M4 Competition",
                url="https://one.test/listing?stockId=ABC123",
            ),
            Listing(
                "two",
                2024,
                75995,
                "Competition",
                15820,
                "Used 2024 BMW M4 Competition",
                url="https://two.test/inventory?stock=ABC123",
            ),
        ]
        self.assertEqual(len(dedupe_listings(matching)), 1)

        collision = [
            matching[0],
            Listing(
                "two",
                2024,
                74995,
                "XSE",
                12000,
                "2024 Toyota Camry XSE",
                url="https://two.test/inventory?stock=ABC123",
            ),
        ]
        self.assertEqual(len(dedupe_listings(collision)), 2)

    def test_shared_search_results_url_does_not_collapse_distinct_rows(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        source_url = "https://example.test/cars-for-sale/bmw/m4?radius=0"
        visible = """
        2024 BMW M4 Competition
        $75,000
        20K miles
        2024 BMW M4 Competition
        $82,000
        8K miles
        2024 BMW M4 Competition
        $68,000
        40K miles
        """
        parsed = parse_visible_listing_text("autotrader_browser", source_url, visible, query)
        self.assertEqual(len(parsed), 3)
        self.assertEqual(len(dedupe_listings(parsed)), 3)

    def test_same_source_near_rows_are_not_fuzzy_merged(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        source_url = "https://example.test/cars-for-sale/bmw/m4?radius=0"
        visible = """
        2024 BMW M4 Competition
        $75,000
        20K miles
        2024 BMW M4 Competition
        $75,200
        20,500 miles
        """
        parsed = parse_visible_listing_text("autotrader_browser", source_url, visible, query)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(len(dedupe_listings(parsed)), 2)

    def test_same_source_exact_fingerprint_is_deduped(self) -> None:
        row = Listing(
            "codex_collector",
            2024,
            75000,
            "Competition",
            20000,
            "2024 BMW M4 Competition",
            dealer="North BMW",
            condition="used",
        )
        self.assertEqual(len(dedupe_listings([row, replace(row)])), 1)

    def test_cross_source_fuzzy_dedupe_requires_dealer_and_mileage(self) -> None:
        complete = [
            Listing("one", 2024, 75000, "Competition", 20000, "2024 BMW M4 Competition", dealer="North BMW"),
            Listing("two", 2024, 75200, "Competition", 20500, "Used 2024 BMW M4 Competition", dealer="North BMW"),
        ]
        self.assertEqual(len(dedupe_listings(complete)), 1)

        missing_dealer = [replace(complete[0], dealer=""), replace(complete[1], dealer="")]
        self.assertEqual(len(dedupe_listings(missing_dealer)), 2)

        missing_mileage = [replace(complete[0], mileage=None), replace(complete[1], mileage=None)]
        self.assertEqual(len(dedupe_listings(missing_mileage)), 2)

    def test_target_year_is_an_exact_filter(self) -> None:
        query = parse_vehicle_query("2022 BMW M4 Competition")
        rows = [
            Listing("market", 2022, 70000, "Competition", title="2022 BMW M4 Competition"),
            Listing("market", 2021, 65000, "Competition", title="2021 BMW M4 Competition"),
            Listing("market", 2023, 76000, "Competition", title="2023 BMW M4 Competition"),
        ]
        report = build_report(query, rows, MSRP(86600, "MSRP", "bmwusa", ""))
        self.assertEqual(report["summary"]["listingCount"], 1)
        self.assertEqual(report["listings"][0]["year"], 2022)
        historical_msrp = default_msrp_for(query)
        self.assertEqual(historical_msrp.price, 0)
        self.assertEqual(historical_msrp.year, 2022)
        self.assertIn("historical MSRP capture", historical_msrp.label)

    def test_year_only_query_does_not_accept_arbitrary_vehicle_rows(self) -> None:
        query = parse_vehicle_query("2022")
        rows = [
            Listing("market", 2022, 70000, title="2022 BMW M4 Competition"),
            Listing("market", 2022, 30000, title="2022 Toyota Camry XSE"),
        ]
        report = build_report(query, rows, MSRP(0, "No MSRP", "none", ""))
        self.assertEqual(report["summary"]["listingCount"], 0)
        self.assertEqual(report["summary"]["dataQuality"], "needs_collection")

    def test_rows_outside_horizon_are_not_claimed_as_plotted_samples(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        query.max_age = 10
        rows = [Listing("market", 2005, 25000, "Competition", title="2005 BMW M4 Competition")]
        report = build_report(query, rows, MSRP(0, "No MSRP", "none", ""), current_year=2026)
        self.assertEqual(report["summary"]["listingCount"], 0)
        self.assertEqual(report["summary"]["outsideHorizonRows"], 1)
        self.assertEqual(report["summary"]["dataQuality"], "needs_collection")
        self.assertEqual(sum(bucket["sample_count"] for bucket in report["buckets"]), 0)

    def test_current_year_used_listing_is_not_new_market_age_zero(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        rows = [
            Listing(
                "used_market",
                2026,
                81000,
                "Competition",
                title="Used 2026 BMW M4 Competition",
                condition="used",
            )
        ]
        report = build_report(query, rows, MSRP(86600, "MSRP", "bmwusa", ""), current_year=2026)
        age_zero = report["buckets"][0]
        self.assertEqual(age_zero["model_year"], 2026)
        self.assertEqual(age_zero["sample_count"], 1)
        self.assertTrue(age_zero["observed"])
        self.assertEqual(age_zero["median"], 81000)
        self.assertEqual(age_zero["trend_median"], 86600)
        self.assertEqual(age_zero["confidence"], "current_year_market")
        self.assertEqual(report["buckets"][1]["sample_count"], 0)

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

    def test_future_new_model_year_anchors_age_zero_and_forecast_years(self) -> None:
        query = parse_vehicle_query("2027 BMW M4 Competition")
        query.max_age = 2
        rows = [
            Listing(
                "new_inventory",
                2027,
                90000,
                "Competition",
                title="New 2027 BMW M4 Competition",
                condition="new",
            )
        ]
        report = build_report(query, rows, MSRP(89000, "2027 MSRP", "bmwusa", "", 2027), current_year=2026)
        age_zero = report["buckets"][0]
        self.assertEqual(age_zero["model_year"], 2027)
        self.assertEqual(age_zero["model_years"], [2027])
        self.assertEqual(age_zero["forecast_year"], 2027)
        self.assertEqual(report["buckets"][1]["forecast_year"], 2028)

    def test_report_resolves_runtime_year_per_call(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        rows = [Listing("market", 2026, 75000, "Competition", title="2026 BMW M4 Competition")]
        with patch("car_compare.depreciation._runtime_current_year", return_value=2027):
            report = build_report(query, rows, MSRP(0, "No MSRP", "none", ""))
        self.assertEqual(report["summary"]["currentYear"], 2027)
        self.assertEqual(report["buckets"][1]["model_year"], 2026)

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

    def test_price_parser_accepts_two_million_and_rejects_non_sale_amounts(self) -> None:
        query = parse_vehicle_query("Rolls Royce Cullinan Black Badge")
        text = """
        2025 Rolls-Royce Cullinan Black Badge
        MSRP $1,950,000
        Discount $25,000
        Down payment $100,000
        Sale Price $2,000,000
        3,200 miles
        """
        listings = parse_visible_listing_text("luxury_browser", "https://example.test", text, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].price, 2_000_000)

    def test_price_parser_accepts_dollar_prefixed_four_digit_price(self) -> None:
        query = parse_vehicle_query("Toyota Camry XSE")
        text = """
        2015 Toyota Camry XSE
        Price $9500
        120K miles
        """
        listings = parse_visible_listing_text("dealer_browser", "https://example.test", text, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].price, 9500)

        bare = """
        2014 Toyota Camry XSE
        Price 9,500
        130K miles
        """
        listings = parse_visible_listing_text("dealer_browser", "https://example.test/other", bare, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].price, 9500)

        bare_number = """
        2013 Toyota Camry XSE
        9500
        140K miles
        """
        listings = parse_visible_listing_text("dealer_browser", "https://example.test/bare", bare_number, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].price, 9500)

    def test_sale_price_survives_same_line_estimated_payment(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        text = """
        2023 BMW M4 Competition
        Price $75,000, estimated payment $1,200 per month
        20K miles
        """
        listings = parse_visible_listing_text("dealer_browser", "https://example.test", text, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].price, 75000)

    def test_preferred_sale_price_beats_reference_amounts(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        price_lines = [
            "Original Price $80,000 Sale Price $75,000",
            "Market Value $80,000 Our Price $75,000",
            "Was $80,000 Now $75,000",
            "List Price $80,000 Internet Price $75,000",
        ]
        for price_line in price_lines:
            with self.subTest(price_line=price_line):
                text = f"2023 BMW M4 Competition\n{price_line}\n20K miles"
                listings = parse_visible_listing_text("dealer_browser", "https://example.test", text, query)
                self.assertEqual(len(listings), 1)
                self.assertEqual(listings[0].price, 75000)

    def test_fees_packages_and_options_are_not_vehicle_prices(self) -> None:
        query = parse_vehicle_query("Toyota Camry XSE")
        cases = [
            ("Navigation package $500", 30000),
            ("Dealer fee $999", 28500),
            ("Delivery $1,500", 42000),
            ("Option $2,500", 35000),
        ]
        for misleading, actual in cases:
            with self.subTest(misleading=misleading):
                text = f"2020 Toyota Camry XSE\n{misleading}\n${actual:,}\n40K miles"
                listings = parse_visible_listing_text("dealer_browser", "https://example.test", text, query)
                self.assertEqual(len(listings), 1)
                self.assertEqual(listings[0].price, actual)

    def test_low_value_used_vehicle_price_is_retained(self) -> None:
        query = parse_vehicle_query("Toyota Camry XSE")
        text = "2010 Toyota Camry XSE\nSale Price $3,500\n180K miles"
        listings = parse_visible_listing_text("dealer_browser", "https://example.test", text, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].price, 3500)

        comma_only = "2010 Toyota Camry XSE\n3,500\n180K miles"
        listings = parse_visible_listing_text("dealer_browser", "https://example.test/comma", comma_only, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].price, 3500)

    def test_ids_phone_and_unlabeled_low_numbers_are_not_prices(self) -> None:
        query = parse_vehicle_query("Toyota Camry XSE")
        misleading = ["3500", "Stock #12345", "Listing ID 54321", "Unit 98765", "Call 5551234", "Odometer 3500"]
        for value in misleading:
            with self.subTest(value=value):
                text = f"2010 Toyota Camry XSE\n{value}\n$30,000\n40K miles"
                listings = parse_visible_listing_text("dealer_browser", "https://example.test", text, query)
                self.assertEqual(len(listings), 1)
                self.assertEqual(listings[0].price, 30000)

    def test_zip_vin_reference_and_hash_identifiers_are_not_prices(self) -> None:
        query = parse_vehicle_query("Toyota Camry XSE")
        misleading = [
            "#12345",
            "ZIP 10001",
            "Postal code 10001",
            "Address 12345",
            "VIN ending 12345",
            "Dealer ID 54321",
            "Inventory ID 54321",
            "Offer ID 54321",
            "Reference #54321",
            "Serial 54321",
            "Lot 54321",
            "Phone (555) 12345",
        ]
        for value in misleading:
            with self.subTest(value=value):
                text = (
                    "2020 Toyota Camry XSE\n"
                    f"{value} · Sale Price $30,000\n"
                    "40K miles"
                )
                listings = parse_visible_listing_text(
                    "dealer_browser", "https://example.test", text, query
                )
                self.assertEqual(len(listings), 1)
                self.assertEqual(listings[0].price, 30000)

    def test_mileage_parser_ignores_range_and_warranty_miles(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        for misleading in ["EPA range 310 miles", "Warranty coverage 50,000 miles"]:
            with self.subTest(misleading=misleading):
                text = f"2023 BMW M4 Competition\n$75,000\n{misleading}\n12,400 miles"
                listings = parse_visible_listing_text("dealer_browser", "https://example.test", text, query)
                self.assertEqual(len(listings), 1)
                self.assertEqual(listings[0].mileage, 12400)

    def test_mileage_parser_scores_each_same_line_candidate(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        cases = [
            "EPA 300 miles · Mileage 12,400 miles",
            "Range 300 mi | Odometer 12,400 mi",
            "5 miles away · 12,400 miles",
            "Warranty coverage 50,000 miles · Mileage 12,400 miles",
        ]
        for mileage_line in cases:
            with self.subTest(mileage_line=mileage_line):
                text = (
                    "2023 BMW M4 Competition\n"
                    "$75,000\n"
                    f"{mileage_line}"
                )
                listings = parse_visible_listing_text(
                    "dealer_browser", "https://example.test", text, query
                )
                self.assertEqual(len(listings), 1)
                self.assertEqual(listings[0].mileage, 12400)

    def test_new_arrival_is_not_assumed_to_be_new_condition(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        text = """
        New Arrival
        2025 BMW M4 Competition
        $78,000
        8K miles
        """
        listings = parse_visible_listing_text("dealer_browser", "https://example.test", text, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].condition, "used")

    def test_year_in_warranty_text_does_not_end_listing_row(self) -> None:
        query = parse_vehicle_query("Bentley Continental GT Speed")
        text = """
        2023 Bentley Continental GT Speed
        Warranty coverage through 2028
        $234,999
        6K miles
        """
        listings = parse_visible_listing_text("autotrader_browser", "https://example.test", text, query)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].price, 234999)


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

    def test_visor_keeps_current_year_used_and_new_as_distinct_conditions(self) -> None:
        query = parse_vehicle_query("2026 BMW M4 Competition")
        rows = [
            VisorYearData(
                year=2026,
                url="https://example.test/used",
                car_type="used",
                price_stats={},
                msrp_stats={},
                mileage_stats={"median": 5000},
                price_bins=[{"lower": 78000, "upper": 79000, "count": 1}],
            ),
            VisorYearData(
                year=2026,
                url="https://example.test/new",
                car_type="new",
                price_stats={},
                msrp_stats={},
                mileage_stats={"median": 20},
                price_bins=[{"lower": 86000, "upper": 87000, "count": 1}],
            ),
        ]
        listings = _listings_from_years(query, rows, 2026)
        self.assertEqual(len(listings), 2)
        self.assertEqual({item.condition for item in listings}, {"used", "new"})

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
        self.assertFalse(_facet_value_matches_request(c_class, "C 300 4MATIC"))
        self.assertFalse(_facet_value_matches_request(c_class, "AMG C43"))

    def test_visor_trim_matching_rejects_neighbors_and_keeps_named_families(self) -> None:
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
        self.assertTrue(_facet_value_matches_request(competition, "M4 Competition xDrive Coupe"))
        self.assertTrue(_facet_value_matches_request(competition, "M4 Competition Convertible"))
        self.assertFalse(_facet_value_matches_request(competition, "M4 CS"))
        self.assertFalse(_facet_value_matches_request(competition, "M4 CSL"))

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

    def test_visor_bin_cap_preserves_source_proportions(self) -> None:
        bins = [
            {"lower": 100000, "upper": 110000, "count": 400},
            {"lower": 110000, "upper": 120000, "count": 40},
        ]
        self.assertEqual(_allocate_bin_samples(bins, cap=40), [36, 4])
        rare_tail = [
            {"lower": 100000, "upper": 110000, "count": 10000},
            {"lower": 110000, "upper": 120000, "count": 1},
        ]
        self.assertEqual(_allocate_bin_samples(rare_tail, cap=40), [39, 1])

    def test_visor_vehicle_confirmation_uses_whole_model_tokens(self) -> None:
        query = parse_vehicle_query("BMW M4")
        self.assertTrue(_html_confirms_vehicle(query, "<title>Used 2024 BMW M4 for sale</title>"))
        self.assertFalse(_html_confirms_vehicle(query, "<title>Used 2024 BMW M440i for sale</title>"))

    def test_visor_rejects_ignored_year_or_trim_filter(self) -> None:
        query = parse_vehicle_query("2023 BMW M4 Competition")
        stats = """
        num_found:4,
        stats:$R[281]={price:$R[282]={min:70000,max:80000,count:4,missing:0,mean:75000,median:75000,stddev:2000}}
        """
        ignored_trim = f'<title>Used 2023 BMW M4 for sale</title>selection={{car_type:"used",year:"2023"}}{stats}'
        with patch("car_compare.sources.visor_facets._fetch_text", return_value=ignored_trim):
            row = _fetch_visor_facets(
                query,
                2023,
                "used",
                "https://example.test",
                filter_name="version",
                filter_value="Competition",
            )
        self.assertIsNone(row)

        forged_title_only = f'<title>Used 2023 BMW M4 Competition for sale</title>selection={{car_type:"used",year:"2023"}}{stats}'
        with patch("car_compare.sources.visor_facets._fetch_text", return_value=forged_title_only):
            row = _fetch_visor_facets(
                query,
                2023,
                "used",
                "https://example.test",
                filter_name="version",
                filter_value="Competition",
            )
        self.assertIsNone(row)

        ignored_year = f'<title>Used BMW M4 Competition for sale</title>selection={{car_type:"used",version:"Competition"}}{stats}'
        with patch("car_compare.sources.visor_facets._fetch_text", return_value=ignored_year):
            row = _fetch_visor_facets(
                query,
                2023,
                "used",
                "https://example.test",
                filter_name="version",
                filter_value="Competition",
            )
        self.assertIsNone(row)

        ignored_car_type = f'<title>Used 2023 BMW M4 Competition for sale</title>selection={{version:"Competition",year:"2023"}}{stats}'
        with patch("car_compare.sources.visor_facets._fetch_text", return_value=ignored_car_type):
            row = _fetch_visor_facets(
                query,
                2023,
                "used",
                "https://example.test",
                filter_name="version",
                filter_value="Competition",
            )
        self.assertIsNone(row)

        applied = f'<title>Used 2023 BMW M4 Competition for sale</title>selection={{car_type:"used",version:"Competition",year:"2023"}}{stats}'
        with patch("car_compare.sources.visor_facets._fetch_text", return_value=applied):
            row = _fetch_visor_facets(
                query,
                2023,
                "used",
                "https://example.test",
                filter_name="version",
                filter_value="Competition",
            )
        self.assertIsNotNone(row)

    def test_visor_requested_years_obey_exact_and_range_queries(self) -> None:
        exact = parse_vehicle_query("2022 BMW M4 Competition")
        self.assertEqual(_requested_years(exact, 2026), [2022])
        range_query = parse_vehicle_query("BMW M4 Competition after 2023")
        self.assertEqual(_requested_years(range_query, 2026), [2026, 2025, 2024, 2023])

    def test_visor_resolves_runtime_year_per_collection_call(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        with (
            patch("car_compare.sources.visor_facets._runtime_current_year", return_value=2027),
            patch("car_compare.sources.visor_facets._matching_filter_specs", return_value=[]),
            patch("car_compare.sources.visor_facets._used_visor_requests", return_value=[]),
            patch("car_compare.sources.visor_facets._visor_urls_for_specs", return_value=[]),
        ):
            result = collect_visor_public_facets(query)
        new_source = next(item for item in result["sources"] if item["source"] == NEW_SOURCE)
        self.assertIn("year=2027", new_source["url"])


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

    def test_target_year_is_applied_to_every_year_capable_source(self) -> None:
        plan = build_collection_plan(parse_vehicle_query("2022 BMW M4 Competition"))
        by_source = {target["source"]: target for target in plan["targets"]}
        self.assertIn("startYear=2022", by_source["autotrader_browser"]["url"])
        self.assertIn("endYear=2022", by_source["autotrader_browser"]["url"])
        self.assertIn("year=2022", by_source["edmunds_browser"]["url"])
        self.assertIn("year=2022", by_source["visor_api_or_facets"]["url"])
        self.assertIn("year=2022", by_source["visor_new_facets"]["url"])
        self.assertTrue(any("only model-year 2022" in step for step in plan["codexWorkflow"]))

    def test_default_horizon_is_pushed_into_source_urls(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        query.max_age = 10
        plan = build_collection_plan(query, current_year=2027)
        by_source = {target["source"]: target for target in plan["targets"]}
        autotrader = by_source["autotrader_browser"]["url"]
        self.assertIn("startYear=2017", autotrader)
        self.assertIn("endYear=2027", autotrader)
        self.assertIn("year=2017-2027", by_source["edmunds_browser"]["url"])
        self.assertIn("year=2027", by_source["visor_new_facets"]["url"])

        query = parse_vehicle_query("BMW M4 Competition after 2020")
        plan = build_collection_plan(query, current_year=2027)
        autotrader = next(target for target in plan["targets"] if target["source"] == "autotrader_browser")
        self.assertIn("startYear=2020", autotrader["url"])


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

    def test_codex_command_registers_project_browser_mcp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            server = Path(tmp) / "browser.mjs"
            server.write_text("", encoding="utf-8")
            command = build_codex_command(
                codex_path="/usr/local/bin/codex",
                root=Path(tmp),
                schema_path=Path(tmp) / "schema.json",
                output_path=Path(tmp) / "output.json",
                browser_server_path=server,
            )
        joined = " ".join(command)
        self.assertIn("mcp_servers.car_compare_browser.command", joined)
        self.assertIn(str(server), joined)

    def test_only_audited_browser_rows_are_accepted(self) -> None:
        query = parse_vehicle_query("BMW M4 Competition")
        with tempfile.TemporaryDirectory() as tmp:
            job_dir = Path(tmp)
            capture = {
                "source": "autotrader_browser",
                "url": "https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4",
                "browser_verified": True,
                "status": "partial",
                "pages_examined": 2,
                "cards_examined": 40,
                "accepted": 3,
                "load_more_clicked": 1,
                "stop_reason": "source_exhausted",
                "rejected_by_reason": {"excluded_variant": 1},
                "year_quota": {"sparse_years": [2016]},
                "listings": [
                    {
                        "source": "autotrader_browser",
                        "year": 2024,
                        "price": 78000,
                        "trim": "Competition xDrive Convertible",
                        "mileage": 12000,
                        "title": "2024 BMW M4 Competition xDrive Convertible",
                        "url": "https://www.autotrader.com/cars-for-sale/inventory/one",
                        "vin": "",
                        "dealer": "",
                        "condition": "used",
                        "confidence": "browser_worker_verified",
                    },
                    {
                        "source": "autotrader_browser",
                        "year": 2018,
                        "price": 48000,
                        "trim": "Competition Package",
                        "mileage": 32000,
                        "title": "2018 BMW M4 Coupe with factory ZCP Competition Package",
                        "url": "https://www.autotrader.com/cars-for-sale/inventory/two",
                        "vin": "",
                        "dealer": "",
                        "condition": "used",
                        "confidence": "browser_worker_verified",
                    },
                    {
                        "source": "autotrader_browser",
                        "year": 2024,
                        "price": 120000,
                        "trim": "CS",
                        "mileage": 3000,
                        "title": "2024 BMW M4 CS",
                        "url": "https://www.autotrader.com/cars-for-sale/inventory/three",
                        "vin": "",
                        "dealer": "",
                        "condition": "used",
                        "confidence": "browser_worker_verified",
                    },
                ],
            }
            (job_dir / "browser_capture_autotrader_browser.json").write_text(json.dumps(capture), encoding="utf-8")
            result = _apply_browser_captures(
                {
                    "notes": [],
                    "sources": [{"source": "autotrader_browser", "status": "collected"}],
                    "listings": [
                        {
                            "source": "autotrader_browser",
                            "year": 2025,
                            "price": 1,
                            "title": "Unverified model prose",
                        }
                    ],
                },
                job_dir,
                query,
            )
        self.assertEqual(len(result["listings"]), 2)
        self.assertTrue(all(item["confidence"] == "browser_worker_verified" for item in result["listings"]))
        source = next(item for item in result["sources"] if item["source"] == "autotrader_browser")
        self.assertTrue(source["browser_verified"])
        self.assertEqual(source["accepted"], 2)

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
        self.assertEqual(listing_schema["properties"]["price"]["minimum"], 500)
        self.assertEqual(listing_schema["properties"]["price"]["maximum"], 10_000_000)
        self.assertEqual(listing_schema["properties"]["year"]["minimum"], 1980)
        self.assertEqual(listing_schema["properties"]["year"]["maximum"], 2100)
        self.assertEqual(schema["properties"]["msrp"]["properties"]["price"]["minimum"], 5000)

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

    def test_visor_keeps_collector_available_without_codex(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manager = CollectionManager(
                CollectorConfig(root=root, codex_path=str(root / "missing-codex"), use_visor_facets=True)
            )
            availability = manager.availability()
            self.assertTrue(availability["available"])
            self.assertTrue(availability["visorAvailable"])
            self.assertFalse(availability["websiteCollectorAvailable"])

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

    def test_explicit_title_condition_overrides_contradictory_payload(self) -> None:
        base = {
            "source": "collector",
            "year": 2026,
            "price": 35000,
            "trim": "XSE",
            "mileage": 12000,
            "url": "https://example.test/vehicle",
            "vin": "",
            "dealer": "Dealer",
            "confidence": "collected",
        }
        cases = [
            ("New Arrival 2026 Toyota Camry XSE", "new", "used"),
            ("Used 2026 Toyota Camry XSE", "new", "used"),
            ("Certified 2026 Toyota Camry XSE", "new", "cpo"),
            ("CPO 2026 Toyota Camry XSE", "used", "cpo"),
            ("New 2026 Toyota Camry XSE", "used", "new"),
            ("2026 Toyota Camry XSE", "cpo", "cpo"),
        ]
        for title, payload_condition, expected in cases:
            with self.subTest(title=title):
                rows = listings_from_result(
                    {
                        "listings": [
                            {**base, "title": title, "condition": payload_condition}
                        ]
                    }
                )
                self.assertEqual(rows[0].condition, expected)

    def test_collector_ingest_rejects_invalid_price_year_and_mileage(self) -> None:
        base = {
            "source": "collector",
            "year": 2024,
            "price": 9500,
            "trim": "XSE",
            "mileage": 120000,
            "title": "2024 Toyota Camry XSE",
            "url": "https://example.test/valid",
            "vin": "",
            "dealer": "Dealer",
            "condition": "used",
            "confidence": "collected",
        }
        invalid = [
            {**base, "price": 499},
            {**base, "price": -9500},
            {**base, "price": 10_000_001},
            {**base, "year": 2077},
            {**base, "year": 1900},
            {**base, "mileage": -1},
        ]
        rows = listings_from_result({"listings": [base, *invalid]})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].price, 9500)

        low_value = listings_from_result({"listings": [{**base, "price": 3500}]})
        self.assertEqual(len(low_value), 1)
        self.assertEqual(low_value[0].price, 3500)

    def test_collector_ingest_uses_runtime_future_year_limit(self) -> None:
        base = {
            "source": "collector",
            "price": 3500,
            "trim": "XSE",
            "mileage": 120000,
            "title": "Toyota Camry XSE",
            "url": "",
            "vin": "",
            "dealer": "Dealer",
            "condition": "used",
            "confidence": "collected",
        }
        with patch("car_compare.collector._runtime_current_year", return_value=2026):
            rows = listings_from_result({"listings": [{**base, "year": 2028}, {**base, "year": 2029}]})
        self.assertEqual([row.year for row in rows], [2028])

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
        self.assertIsNone(msrp_from_result({"msrp": {**msrp.to_dict(), "price": 1200}}))
        self.assertIsNone(msrp_from_result({"msrp": {**msrp.to_dict(), "year": 2077}}))

    def test_merge_keeps_valid_facet_msrp_when_codex_msrp_is_invalid(self) -> None:
        facet = {
            "status": "success",
            "listings": [{"source": "facet"}],
            "msrp": {"price": 50000, "label": "Facet MSRP", "source": "visor", "url": "", "year": 2026},
        }
        codex = {
            "status": "success",
            "listings": [],
            "msrp": {"price": 1200, "label": "Payment", "source": "codex", "url": "", "year": 2026},
        }
        merged = _merge_collector_results(facet, codex)
        self.assertEqual(merged["msrp"]["price"], 50000)
        self.assertEqual(merged["msrp"]["source"], "visor")

    def test_merge_binds_automatic_msrp_to_target_year(self) -> None:
        request = parse_vehicle_query("2022 BMW M4 Competition")
        facet = {
            "status": "success",
            "listings": [],
            "msrp": {"price": 80000, "label": "2022 MSRP", "source": "visor", "url": "", "year": 2022},
        }
        codex = {
            "status": "success",
            "listings": [],
            "msrp": {"price": 90000, "label": "2026 MSRP", "source": "codex", "url": "", "year": 2026},
        }
        merged = _merge_collector_results(facet, codex, request)
        self.assertEqual(merged["msrp"]["year"], 2022)
        self.assertEqual(merged["msrp"]["source"], "visor")


if __name__ == "__main__":
    unittest.main()
