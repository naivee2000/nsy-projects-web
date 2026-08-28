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
from urllib.parse import parse_qs, urlparse

from car_compare.condition import sanitize_listing_condition
from car_compare.depreciation import build_report, dedupe_listings, dedupe_listings_with_diagnostics
from pathlib import Path

from car_compare.collector import (
    CollectionJob,
    CollectionManager,
    CollectorConfig,
    _apply_browser_captures,
    _browser_url_for_year,
    _combined_year_coverage,
    _critical_missing_years,
    _format_elapsed,
    _merge_collector_results,
    _plan_browser_followups,
    build_codex_command,
    build_codex_prompt,
    build_codex_web_search_command,
    build_codex_web_search_prompt,
    clean_codex_error,
    codex_failure_message,
    listings_from_result,
    msrp_from_result,
)
from car_compare.capture_cache import CaptureCache, MAX_OLDER_TTL_SECONDS, MAX_RECENT_TTL_SECONDS, ResearchResultCache
from car_compare.browser_runtime import browser_cdp_status, browser_cdp_url
from car_compare.codex_cli import (
    MACOS_CODEX_CLI_PATHS,
    codex_environment,
    codex_login_status,
    find_codex_cli,
    normalize_codex_reasoning_effort,
)
from car_compare.generation_impact import (
    GenerationResearchConfig,
    GenerationResearchManager,
    _generation_cache_identity,
    build_generation_research_command,
)
from car_compare.models import Listing, MSRP, VehicleQuery
from car_compare.parser import parse_vehicle_query
from car_compare.resolver import resolve_vehicle_query
from car_compare.sample_data import default_msrp_for, sample_listings_for
from car_compare.shared_auth import SharedSessionAuth, valid_shared_session_token
from car_compare.sources.browser_capture import parse_visible_listing_cards, parse_visible_listing_text
from car_compare.sources.chrome_host import (
    background_mode_enabled,
    capture_is_access_wall,
    capture_with_host_chrome,
)
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
from car_compare.trim_normalization import build_trim_normalization, canonical_trim_cohort
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
    def test_static_ui_exposes_single_and_two_vehicle_research_modes(self) -> None:
        html = (web_app.STATIC / "index.html").read_text(encoding="utf-8")
        javascript = (web_app.STATIC / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="singleModeButton"', html)
        self.assertIn('id="compareModeButton"', html)
        self.assertIn('id="compareQuery"', html)
        self.assertIn('id="bucketTableHead"', html)
        self.assertIn("async function startComparison()", javascript)
        self.assertIn("const collectionTasks = run.vehicles.map", javascript)
        self.assertIn("await Promise.all([...collectionTasks, ...generationTasks])", javascript)
        self.assertIn("renderComparisonDepreciationChart", javascript)
        self.assertIn("change: bucketSignedPreviousChange", javascript)
        self.assertIn("Grouped signed bars show each year's value movement", javascript)
        self.assertNotIn("Grouped bars show cumulative dollar loss", javascript)
        self.assertIn("renderComparisonTable", javascript)
        self.assertIn("Market Median", javascript)
        self.assertIn("Curve Value", javascript)
        self.assertIn('scope="col">Outliers', javascript)
        self.assertIn("Raw Source Snapshots", javascript)
        self.assertIn("background workers", javascript)

    def test_codex_browser_action_surface_is_packaged(self) -> None:
        html = (web_app.STATIC / "codex-action.html").read_text(encoding="utf-8")
        javascript = (web_app.STATIC / "codex-action.js").read_text(encoding="utf-8")
        main_html = (web_app.STATIC / "index.html").read_text(encoding="utf-8")
        main_javascript = (web_app.STATIC / "app.js").read_text(encoding="utf-8")
        self.assertIn('id="captureImportForm"', html)
        self.assertIn("/api/codex-browser-actions", javascript)
        self.assertIn("/api/codex-browser-capture", javascript)
        self.assertIn('id="codexFallbackLink"', main_html)
        self.assertIn("Repair Missing Source", main_html)
        self.assertIn("beginFallbackMonitoring", main_javascript)
        self.assertIn("codex://threads/new", main_javascript)
        self.assertIn("@Chrome Use $collect-car-marketplaces", main_javascript)

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
            "Porsche 911 Base": ("Porsche", "911", "Base"),
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

    def test_configured_trim_scope_distinguishes_model_family_and_base(self) -> None:
        all_911 = parse_vehicle_query("Porsche 911")
        carrera = parse_vehicle_query("Porsche 911 Carrera")
        base = parse_vehicle_query("Porsche 911 Base")

        all_resolution = resolve_vehicle_query(all_911)
        family_resolution = resolve_vehicle_query(carrera)
        base_resolution = resolve_vehicle_query(base)
        self.assertIn("trim", all_resolution["include_all"])
        self.assertEqual(family_resolution["family"]["trim"], "Carrera family")
        self.assertEqual(base_resolution["exact"]["trim"], "Base Carrera")

        carrera_family = [
            "2026 Porsche 911 Carrera Coupe",
            "2026 Porsche 911 Carrera Cabriolet",
            "2026 Porsche 911 Carrera S Coupe",
            "2026 Porsche 911 Carrera T Coupe",
            "2026 Porsche 911 Carrera 4 Coupe",
            "2026 Porsche 911 Carrera 4S Cabriolet",
            "2026 Porsche 911 Carrera GTS Coupe",
            "2026 Porsche 911 Carrera 4 GTS Cabriolet",
            "2016 Porsche 911 Carrera Black Edition Coupe",
        ]
        non_carrera_911 = [
            "2026 Porsche 911 Turbo S Coupe",
            "2026 Porsche 911 GT3 Coupe",
            "2026 Porsche 911 Targa 4S",
        ]
        for title in [*carrera_family, *non_carrera_911]:
            with self.subTest(scope="all", title=title):
                self.assertTrue(vehicle_text_match_score(all_911, title)["accepted"])
        for title in carrera_family:
            with self.subTest(scope="family", title=title):
                self.assertTrue(vehicle_text_match_score(carrera, title)["accepted"])
        for title in non_carrera_911:
            with self.subTest(scope="family_exclusion", title=title):
                self.assertFalse(vehicle_text_match_score(carrera, title)["accepted"])
        for title in carrera_family[:2]:
            with self.subTest(scope="base", title=title):
                self.assertTrue(vehicle_text_match_score(base, title)["accepted"])
        for title in carrera_family[2:]:
            with self.subTest(scope="base_exclusion", title=title):
                self.assertFalse(vehicle_text_match_score(base, title)["accepted"])

        # Models without an explicit family policy keep exact trim semantics.
        self.assertFalse(
            vehicle_text_match_score(
                parse_vehicle_query("Honda Civic EX"),
                "2024 Honda Civic EX-L Sedan",
            )["accepted"]
        )

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
        self.assertEqual(report["buckets"][-1]["confidence"], "long_range_projected_beyond_model_history")

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
            ),
            Listing(
                "used_market_secondary",
                2022,
                25000,
                "XSE",
                45001,
                "2022 Toyota Camry XSE second observation",
            ),
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

    def test_dedupe_merges_same_source_detail_and_summary_echo(self) -> None:
        rows = [
            Listing(
                "edmunds_browser",
                2023,
                25596,
                title="2023 Honda Civic EX Sedan",
                url="https://www.edmunds.com/honda/civic/2023/vin/2HGFE1F76PH308805/",
            ),
            Listing(
                "edmunds_browser",
                2023,
                25596,
                mileage=13802,
                title="2023 Honda Civic EX Sedan",
                url="https://www.edmunds.com/inventory/srp.html?make=honda&model=civic",
            ),
        ]

        deduped, diagnostics = dedupe_listings_with_diagnostics(rows)

        self.assertEqual(len(deduped), 1)
        self.assertEqual(diagnostics["removedByMethod"], {"same_source_detail_echo": 1})
        self.assertEqual(deduped[0].mileage, 13802)

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

    def test_collection_inconsistency_benchmarks_clear_forty_percent_targets(self) -> None:
        fixture = json.loads(
            (Path(__file__).parent / "fixtures" / "collection_inconsistency_benchmarks.json").read_text(
                encoding="utf-8"
            )
        )
        limits = fixture["baselines"]

        duplicate_rows = []
        for index in range(limits["porsche_cross_source_duplicate_groups"]):
            price = 120_000 + (index * 1_000)
            mileage = 1_000 + index
            right_trim = "Carrera S (992 I) Certified Pre-Owned Black" if index < 20 else "Carrera 4S"
            duplicate_rows.extend(
                [
                    Listing(
                        "edmunds_browser",
                        2024,
                        price,
                        "Carrera S Coupe",
                        mileage,
                        "2024 Porsche 911 Carrera S Coupe",
                        condition="used",
                    ),
                    Listing(
                        "porsche_finder_browser",
                        2024,
                        price,
                        right_trim,
                        mileage,
                        f"2024 Porsche 911 {right_trim}",
                        condition="cpo",
                    ),
                ]
            )
        _, diagnostics = dedupe_listings_with_diagnostics(duplicate_rows)
        self.assertEqual(
            diagnostics["rawCrossSourceExactGroups"],
            limits["porsche_cross_source_duplicate_groups"],
        )
        self.assertLessEqual(
            diagnostics["unresolvedCrossSourceExactGroups"],
            limits["maximum_allowed_duplicate_groups"],
        )

        sanitized_conditions = [
            sanitize_listing_condition("new", "2018 Porsche 911 Carrera S", 2018, current_year=2026)
            for _ in range(limits["implausible_historical_new_rows"])
        ]
        self.assertLessEqual(
            sanitized_conditions.count("new"),
            limits["maximum_allowed_historical_new_rows"],
        )

        cohort_titles = {
            "base": "Carrera",
            "s": "Carrera S",
            "gts": "Carrera GTS",
            "turbo": "Turbo S",
            "gt_special": "GT3",
        }
        trim_rows = []
        for raw_year, counts in fixture["porsche_trim_counts"].items():
            year = int(raw_year)
            for cohort, count in counts.items():
                trim = cohort_titles[cohort]
                cohort_premium = ["base", "s", "gts", "turbo", "gt_special"].index(cohort) * 30_000
                for index in range(count):
                    trim_rows.append(
                        Listing(
                            "benchmark_browser",
                            year,
                            80_000 + cohort_premium + ((year - 2006) * 1_500) + index,
                            trim,
                            10_000 + index,
                            f"{year} Porsche 911 {trim}",
                        )
                    )
        normalization = build_trim_normalization(parse_vehicle_query("Porsche 911"), trim_rows)
        self.assertEqual(normalization["status"], "applied")
        self.assertLessEqual(normalization["divergenceRatio"], limits["maximum_divergence_ratio"])
        self.assertGreaterEqual(normalization["yearRetention"], limits["minimum_year_retention"])

        report = build_report(
            parse_vehicle_query("Porsche 911"),
            trim_rows,
            MSRP(135000, "Porsche 911 MSRP", "porsche", ""),
            current_year=2026,
        )
        self.assertEqual(report["summary"]["trimNormalization"]["status"], "applied")
        normalized_bucket = next(
            bucket for bucket in report["buckets"] if bucket["trim_normalized_median"] is not None
        )
        self.assertEqual(normalized_bucket["curve_median"], normalized_bucket["trim_normalized_median"])
        self.assertIsNotNone(normalized_bucket["market_median"])

    def test_trim_normalization_keeps_exact_trim_and_sparse_queries_raw(self) -> None:
        exact = build_trim_normalization(
            parse_vehicle_query("Porsche 911 Carrera S"),
            [Listing("market", 2024, 150000, "Carrera S", title="2024 Porsche 911 Carrera S")],
        )
        self.assertEqual(exact["status"], "exact_trim")

        sparse = build_trim_normalization(
            parse_vehicle_query("Porsche 911"),
            [
                Listing("market", 2024, 150000, "Carrera S", title="2024 Porsche 911 Carrera S"),
                Listing("market", 2023, 145000, "Carrera S", title="2023 Porsche 911 Carrera S"),
            ],
        )
        self.assertEqual(sparse["status"], "insufficient_coverage")

    def test_trim_normalization_generalizes_across_catalog_and_uncatalogued_models(self) -> None:
        cases = [
            ("Toyota Camry", "LE FWD Sedan", "XSE AWD Sedan", "catalog"),
            ("Ford Mustang", "EcoBoost Coupe", "GT Coupe", "catalog"),
            ("Mercedes GLE", "GLE 350 4MATIC SUV", "GLE 450 4MATIC SUV", "catalog"),
            ("Nissan Rogue", "SV AWD SUV", "SL AWD SUV", "generic"),
        ]
        for query_text, lower_trim, upper_trim, strategy in cases:
            with self.subTest(query_text=query_text):
                query = parse_vehicle_query(query_text)
                rows = []
                for year, counts in [(2024, (8, 2)), (2023, (2, 8)), (2022, (5, 5))]:
                    for cohort_index, (trim, count) in enumerate(zip((lower_trim, upper_trim), counts)):
                        for index in range(count):
                            rows.append(
                                Listing(
                                    "general_market",
                                    year,
                                    25_000 + (cohort_index * 20_000) + index,
                                    trim,
                                    10_000 + index,
                                    f"{year} {query.make} {query.model} {trim}",
                                )
                            )
                normalization = build_trim_normalization(query, rows)
                self.assertEqual(normalization["status"], "applied")
                self.assertEqual(normalization["yearRetention"], 1.0)
                self.assertLessEqual(normalization["divergenceRatio"], 0.60)
                self.assertGreater(normalization["cohortStrategyCounts"].get(strategy, 0), 0)

    def test_generic_trim_cohort_removes_page_noise_but_preserves_configuration(self) -> None:
        query = parse_vehicle_query("Nissan Rogue")
        listing = Listing(
            "market",
            2024,
            30_000,
            "2024 Nissan Rogue SV AWD Certified Pre-Owned SUV",
            title="2024 Nissan Rogue SV AWD Certified Pre-Owned SUV",
        )
        self.assertEqual(canonical_trim_cohort(query, listing), "sv_awd")

        configuration_only = replace(listing, trim="Hybrid AWD")
        self.assertEqual(canonical_trim_cohort(query, configuration_only), "")

        noisy = replace(listing, trim="Limited AWD with premium technology package and panoramic roof")
        self.assertEqual(canonical_trim_cohort(query, noisy), "")

    def test_identity_and_condition_rules_apply_to_general_market_rows(self) -> None:
        rows = [
            Listing("one", 2024, 31_500, "XSE Sedan", 20_000, "2024 Toyota Camry XSE Sedan"),
            Listing("two", 2024, 31_500, "XSE", 20_000, "Used 2024 Toyota Camry XSE"),
        ]
        deduped, diagnostics = dedupe_listings_with_diagnostics(rows)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(diagnostics["removedByMethod"]["cross_source_exact"], 1)
        self.assertEqual(
            sanitize_listing_condition("new", "2018 Toyota Camry XSE", 2018, current_year=2026),
            "unknown",
        )

    def test_strong_identity_condition_conflict_becomes_unknown(self) -> None:
        rows = [
            Listing(
                "one",
                2026,
                100000,
                "Competition",
                100,
                "New 2026 BMW M4 Competition",
                url="https://dealer.test/vehicle/ABC123",
                condition="new",
            ),
            Listing(
                "two",
                2026,
                100000,
                "Competition",
                100,
                "Used 2026 BMW M4 Competition",
                url="https://dealer.test/vehicle/ABC123",
                condition="used",
            ),
        ]
        deduped = dedupe_listings(rows)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0].condition, "unknown")
        self.assertEqual(deduped[0].confidence, "deduped_condition_conflict")

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
        self.assertEqual(report["summary"]["outsideHorizonRows"], 0)
        self.assertEqual(report["summary"]["outsideLifecycleRows"], 1)
        self.assertEqual(report["summary"]["outsideLifecycleYears"], {2005: 1})
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
        self.assertEqual(age_zero["trend_median"], 81000)
        self.assertEqual(age_zero["confidence"], "current_year_market")
        self.assertEqual(report["buckets"][1]["sample_count"], 0)

    def test_observed_market_baseline_is_independent_of_display_msrp(self) -> None:
        query = parse_vehicle_query("Porsche 911")
        rows = [
            Listing("market", 2026, 180000, title="Used 2026 Porsche 911 Carrera", condition="used"),
            Listing("market", 2026, 226900, title="Used 2026 Porsche 911 GT3", condition="used"),
            Listing("market", 2026, 300000, title="Used 2026 Porsche 911 Turbo S", condition="used"),
            Listing("market", 2025, 200000, title="Used 2025 Porsche 911 Carrera S", condition="used"),
            Listing("market_secondary", 2025, 200000, title="Used 2025 Porsche 911 Carrera S second observation", condition="used"),
            Listing("market", 2024, 210000, title="Used 2024 Porsche 911 GT3", condition="used"),
            Listing("market_secondary", 2024, 210000, title="Used 2024 Porsche 911 GT3 second observation", condition="used"),
        ]
        low_msrp = build_report(query, rows, MSRP(135500, "Carrera MSRP", "porsche", ""), current_year=2026)
        high_msrp = build_report(query, rows, MSRP(250000, "Display MSRP", "porsche", ""), current_year=2026)

        for report in (low_msrp, high_msrp):
            self.assertEqual(report["buckets"][0]["median"], 226900)
            self.assertEqual(report["buckets"][0]["trend_median"], 226900)
            self.assertEqual(report["buckets"][1]["depreciation_from_previous"], 26900)
            self.assertEqual(report["buckets"][1]["depreciation_from_previous_pct"], 0.1186)
            self.assertEqual(report["buckets"][2]["trend_median"], 210000)
            self.assertEqual(report["buckets"][2]["depreciation_from_previous"], 0)
            self.assertEqual(report["buckets"][2]["depreciation_from_baseline"], 16900)

    def test_aggregate_population_weights_the_combined_market_median(self) -> None:
        query = parse_vehicle_query("Porsche 911")
        rows = [
            Listing(
                "visor_public_facets_new",
                2026,
                180000,
                title="New 2026 Porsche 911 Carrera",
                confidence="aggregate_facets",
                condition="new",
                market_weight=100,
            ),
            Listing(
                "visor_public_facets",
                2026,
                300000,
                title="Used 2026 Porsche 911 GT3",
                confidence="aggregate_facets",
                condition="used",
                market_weight=10,
            ),
            Listing("edmunds_browser", 2026, 350000, title="Used 2026 Porsche 911 Turbo S", condition="used"),
        ]
        report = build_report(query, rows, MSRP(135500, "Carrera MSRP", "porsche", ""), current_year=2026)
        age_zero = report["buckets"][0]
        self.assertEqual(age_zero["sample_count"], 3)
        self.assertEqual(age_zero["market_median"], 180000)
        self.assertEqual(age_zero["trend_median"], 180000)

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
            Listing("market_secondary", 2025, 245000, title="2025 Bentley Continental GT second observation", condition="used"),
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
            Listing(
                "used_market_secondary",
                2025,
                90000,
                "Competition Coupe",
                title="2025 BMW M4 Competition Coupe second observation",
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

    def test_generation_adjustment_does_not_rewrite_observed_future_proxy_age(self) -> None:
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
                "new_inventory_secondary",
                2026,
                100000,
                "Competition Coupe",
                title="New 2026 BMW M4 Competition Coupe second observation",
                confidence="new_inventory",
                condition="new",
            ),
            Listing("used_market", 2025, 90000, "Competition Coupe", title="2025 BMW M4 Competition Coupe"),
            Listing("used_market_secondary", 2025, 90000, "Competition Coupe", title="2025 BMW M4 Competition Coupe second observation"),
            Listing("used_market", 2024, 82000, "Competition Coupe", title="2024 BMW M4 Competition Coupe"),
            Listing("used_market_secondary", 2024, 82000, "Competition Coupe", title="2024 BMW M4 Competition Coupe second observation"),
            Listing("used_market", 2023, 76000, "Competition Coupe", title="2023 BMW M4 Competition Coupe"),
            Listing("used_market_secondary", 2023, 76000, "Competition Coupe", title="2023 BMW M4 Competition Coupe second observation"),
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
        self.assertIsNone(age_three["generation_adjustment_pct"])
        self.assertIsNone(age_three["generation_adjustment_ratio"])
        self.assertIsNone(age_three["generation_unadjusted_median"])
        self.assertEqual(age_three["median"], 76000)
        self.assertEqual(age_three["depreciation_from_baseline"], 24000)

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

    def test_global_new_filter_does_not_mark_historical_listing_new(self) -> None:
        query = parse_vehicle_query("Porsche 911")
        text = """
        New
        2018 Porsche 911 Carrera S
        $109,500
        31,000 miles
        """
        listing = parse_visible_listing_text(
            "edmunds_browser",
            "https://www.edmunds.com/porsche/911/",
            text,
            query,
        )[0]
        self.assertEqual(listing.condition, "used")

    def test_structured_card_preserves_detail_url_condition_and_dealer(self) -> None:
        query = parse_vehicle_query("Porsche 911")
        detail_url = "https://www.autotrader.com/cars-for-sale/vehicle/ABC123"
        listings = parse_visible_listing_cards(
            "autotrader_browser",
            [
                {
                    "url": detail_url,
                    "text": (
                        "Certified Pre-Owned\n"
                        "2025 Porsche 911 Carrera S\n"
                        "$202,933\n"
                        "54 miles\n"
                        "Sponsored by Porsche Center North"
                    ),
                }
            ],
            query,
        )
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].url, detail_url)
        self.assertEqual(listings[0].condition, "cpo")
        self.assertEqual(listings[0].dealer, "Porsche Center North")

    def test_cached_historical_new_row_is_sanitized(self) -> None:
        listing = listings_from_result(
            {
                "listings": [
                    {
                        "source": "edmunds_browser",
                        "year": 2006,
                        "price": 45000,
                        "mileage": 91816,
                        "title": "2006 Porsche 911 Carrera S Convertible",
                        "condition": "new",
                    }
                ]
            }
        )[0]
        self.assertEqual(listing.condition, "unknown")

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

    def test_parse_porsche_finder_card_ignores_dealer_fee(self) -> None:
        query = parse_vehicle_query("Porsche 911 Carrera S")
        text = """
        2025 Porsche 911 Carrera S (992 II)
        Certified Pre-Owned
        8,206 mi
        $159,084.00
        Excl. taxes, incl. fees
        Estimated Dealer Fees: $85
        """
        listings = parse_visible_listing_text(
            "porsche_finder_browser",
            "https://finder.porsche.com/us/en-US/details/porsche-911-carrera-s-preowned-ABC123",
            text,
            query,
        )
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0].price, 159084)
        self.assertEqual(listings[0].mileage, 8206)
        self.assertEqual(listings[0].condition, "cpo")

    def test_parse_visible_text_rejects_neighbor_trim_variants(self) -> None:
        cases = [
            (
                "Porsche 911 Base",
                """
                Used 2023 Porsche 911 Carrera S Coupe
                8K mi
                143,000
                Used 2023 Porsche 911 Carrera T Coupe
                7K mi
                139,000
                Used 2023 Porsche 911 Carrera 4 GTS Coupe
                6K mi
                169,000
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
        self.assertTrue(_facet_value_matches_request(carrera, "Carrera S Coupe"))
        self.assertTrue(_facet_value_matches_request(carrera, "Carrera GTS Coupe"))
        self.assertTrue(_facet_value_matches_request(carrera, "Carrera T Coupe"))
        self.assertTrue(_facet_value_matches_request(carrera, "Carrera 4 Coupe"))
        self.assertTrue(_facet_value_matches_request(carrera, "Carrera 4 GTS Coupe"))
        self.assertFalse(_facet_value_matches_request(carrera, "Turbo S Coupe"))
        self.assertFalse(_facet_value_matches_request(carrera, "Targa 4S"))

        base_carrera = parse_vehicle_query("porsche 911 base")
        self.assertTrue(_facet_value_matches_request(base_carrera, "Carrera Coupe"))
        self.assertTrue(_facet_value_matches_request(base_carrera, "Carrera Cabriolet"))
        self.assertTrue(_facet_value_matches_request(base_carrera, "Base"))
        self.assertFalse(_facet_value_matches_request(base_carrera, "Carrera S Coupe"))
        self.assertFalse(_facet_value_matches_request(base_carrera, "Carrera T Coupe"))
        self.assertFalse(_facet_value_matches_request(base_carrera, "Carrera 4 GTS Coupe"))
        self.assertFalse(_facet_value_matches_request(base_carrera, "Carrera Black Edition Cabriolet"))

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

    def test_visor_samples_preserve_represented_market_population(self) -> None:
        query = parse_vehicle_query("Porsche 911")
        row = VisorYearData(
            year=2026,
            url="https://example.test/911",
            car_type="new",
            price_stats={},
            msrp_stats={},
            mileage_stats={"median": 10},
            price_bins=[
                {"lower": 100000, "upper": 110000, "count": 100},
                {"lower": 200000, "upper": 210000, "count": 10},
            ],
            num_found=110,
        )
        listings = _listings_from_years(query, [row], 2026)
        self.assertEqual(len(listings), 40)
        self.assertAlmostEqual(sum(item.market_weight for item in listings), 110)
        self.assertAlmostEqual(sum(item.market_weight for item in listings if item.price < 200000), 100)

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

    def test_plan_exposes_family_and_base_trim_scopes(self) -> None:
        family = build_collection_plan(parse_vehicle_query("Porsche 911 Carrera"))
        base = build_collection_plan(parse_vehicle_query("Porsche 911 Base"))
        self.assertEqual(family["matching"]["trim_scope"]["mode"], "family")
        self.assertEqual(family["resolution"]["family"]["trim"], "Carrera family")
        self.assertEqual(base["matching"]["trim_scope"]["mode"], "base")
        self.assertIn("Carrera", base["matching"]["required_keywords"])
        self.assertEqual(base["resolution"]["exact"]["trim"], "Base Carrera")

    def test_porsche_finder_uses_nationwide_year_and_911_scope_filters(self) -> None:
        all_plan = build_collection_plan(parse_vehicle_query("Porsche 911"), current_year=2026)
        family_plan = build_collection_plan(parse_vehicle_query("Porsche 911 Carrera"), current_year=2026)
        base_plan = build_collection_plan(parse_vehicle_query("Porsche 911 Base"), current_year=2026)
        exact_plan = build_collection_plan(parse_vehicle_query("Porsche 911 Carrera S"), current_year=2026)

        def finder(plan):
            return next(target for target in plan["targets"] if target["source"] == "porsche_finder_browser")

        all_query = parse_qs(urlparse(finder(all_plan)["url"]).query)
        family_query = parse_qs(urlparse(finder(family_plan)["url"]).query)
        base_query = parse_qs(urlparse(finder(base_plan)["url"]).query)
        exact_query = parse_qs(urlparse(finder(exact_plan)["url"]).query)

        self.assertEqual(all_query["position"], ["Los Angeles,34.0481,-118.2531,-1"])
        self.assertEqual(all_query["minimum-model-year"], ["2016"])
        self.assertEqual(all_query["maximum-model-year"], ["2026"])
        self.assertNotIn("category", all_query)
        self.assertIn("911-carrera-s-coupe", family_query["category"])
        self.assertIn("911-carrera-t-cabriolet", family_query["category"])
        self.assertIn("911-carrera-rs", family_query["category"])
        self.assertNotIn("911-turbo-s-coupe", family_query["category"])
        self.assertEqual(set(base_query["category"]), {"911-carrera-coupe", "911-carrera-convertible"})
        self.assertEqual(set(exact_query["category"]), {"911-carrera-s-coupe", "911-carrera-s-convertible"})

    def test_porsche_finder_is_porsche_only_and_exact_year_is_applied(self) -> None:
        porsche = build_collection_plan(parse_vehicle_query("2022 Porsche Cayenne"), current_year=2026)
        bmw = build_collection_plan(parse_vehicle_query("BMW M4 Competition"), current_year=2026)
        finder = next(target for target in porsche["targets"] if target["source"] == "porsche_finder_browser")
        query = parse_qs(urlparse(finder["url"]).query)
        self.assertEqual(query["model"], ["cayenne"])
        self.assertEqual(query["minimum-model-year"], ["2022"])
        self.assertEqual(query["maximum-model-year"], ["2022"])
        self.assertFalse(any(target["source"] == "porsche_finder_browser" for target in bmw["targets"]))

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
    def test_sparse_followup_budget_caps_individual_year_pages(self) -> None:
        request = parse_vehicle_query("BMW M4 Competition")
        payloads = [
            {
                "source": "autotrader_browser",
                "url": "https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4?startYear=2016&endYear=2026",
            },
            {
                "source": "edmunds_browser",
                "url": "https://www.edmunds.com/inventory/srp.html?make=bmw&model=m4&year=2016-2026",
            },
        ]
        audits = [
            {
                "source": source["source"],
                "status": "partial",
                "browser_verified": True,
                "listings": [],
            }
            for source in payloads
        ]

        followups = _plan_browser_followups(
            request,
            payloads,
            audits,
            list(range(2016, 2027)),
        )

        self.assertEqual(len(followups), 4)
        self.assertEqual([item["start_year"] for item in followups], [2026, 2025, 2024, 2023])

    def test_codex_search_recovery_only_targets_four_unsupported_years(self) -> None:
        coverage = {
            "sparse_years": list(range(2016, 2027)),
            "years": {
                year: {
                    "individual_rows": 0 if year <= 2024 else 3,
                    "aggregate_support": year in {2018, 2019},
                }
                for year in range(2016, 2027)
            },
        }

        self.assertEqual(_critical_missing_years(coverage), [2024, 2023, 2022, 2021])

    def test_host_chrome_fallback_uses_one_broad_range_capture(self) -> None:
        request = parse_vehicle_query("BMW M4 Competition")
        request.max_age = 10
        payload = {
            "source": "autotrader_browser",
            "url": "https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4?startYear=2016&endYear=2026",
            "start_year": 2016,
            "end_year": 2026,
            "target_years": list(range(2016, 2027)),
        }
        capture = {
            "requestedUrl": payload["url"],
            "readyState": "complete",
            "title": "BMW M4 listings",
            "text": "",
            "cards": [],
            "cardsExamined": 0,
            "pagesExamined": 3,
            "loadMoreClicked": 2,
            "backgroundMode": True,
        }
        with tempfile.TemporaryDirectory() as tmp:
            manager = CollectionManager(CollectorConfig(root=Path(tmp)))
            with patch("car_compare.collector.capture_with_host_chrome", return_value=capture) as capture_call:
                audit = manager._collect_host_chrome_source(request, payload, Path(tmp))

        capture_call.assert_called_once()
        self.assertEqual(audit["attempted_year_searches"], 0)
        self.assertEqual(audit["pages_examined"], 3)

    def test_porsche_year_followup_preserves_repeated_categories(self) -> None:
        raw = (
            "https://finder.porsche.com/us/en-US/search/911?model=911&page=3"
            "&category=911-carrera-coupe&category=911-carrera-convertible"
            "&minimum-model-year=2020&maximum-model-year=2026"
        )
        query = parse_qs(urlparse(_browser_url_for_year(raw, "porsche_finder_browser", 2024)).query)
        self.assertEqual(query["minimum-model-year"], ["2024"])
        self.assertEqual(query["maximum-model-year"], ["2024"])
        self.assertEqual(query["category"], ["911-carrera-coupe", "911-carrera-convertible"])
        self.assertNotIn("page", query)

    def test_background_mode_defaults_on_and_can_be_disabled(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(background_mode_enabled())
        with patch.dict(os.environ, {"CAR_COMPARE_BACKGROUND_MODE": "0"}, clear=True):
            self.assertFalse(background_mode_enabled())

    def test_host_chrome_receives_background_flag(self) -> None:
        capture = {
            "url": "https://www.autotrader.com/cars-for-sale/",
            "text": "listing text",
            "pages": [],
        }
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch("car_compare.sources.chrome_host.platform.system", return_value="Darwin"),
            patch("car_compare.sources.chrome_host.shutil.which", return_value="/usr/bin/osascript"),
            patch("car_compare.sources.chrome_host.Path.exists", return_value=True),
            patch(
                "car_compare.sources.chrome_host.subprocess.run",
                return_value=SimpleNamespace(returncode=0, stdout=json.dumps(capture), stderr=""),
            ) as run,
            patch.dict(os.environ, {"CAR_COMPARE_BACKGROUND_MODE": "1"}),
        ):
            result = capture_with_host_chrome(
                source="autotrader_browser",
                url=capture["url"],
                script_path=Path(tmp) / "capture.applescript",
            )

        self.assertEqual(run.call_args.args[0][-1], "1")
        self.assertTrue(result["backgroundMode"])

    def test_capture_cache_caps_ttl_and_isolates_trim_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache = CaptureCache(
                Path(tmp) / "cache.sqlite3",
                recent_ttl_seconds=10 * MAX_RECENT_TTL_SECONDS,
                older_ttl_seconds=10 * MAX_OLDER_TTL_SECONDS,
            )
            competition = parse_vehicle_query("BMW M4 Competition")
            base = parse_vehicle_query("BMW M4 Base")
            cache.store_year(
                competition,
                "autotrader_browser",
                2026,
                {"listings": [{"year": 2026, "price": 90000}]},
                current_year=2026,
                captured_at=100,
            )
            cache.store_year(
                competition,
                "autotrader_browser",
                2020,
                {"listings": [{"year": 2020, "price": 50000}]},
                current_year=2026,
                captured_at=100,
            )

            self.assertEqual(cache.recent_ttl_seconds, MAX_RECENT_TTL_SECONDS)
            self.assertEqual(cache.older_ttl_seconds, MAX_OLDER_TTL_SECONDS)
            self.assertEqual(len(cache.load(competition, "autotrader_browser", [2026], now=100 + MAX_RECENT_TTL_SECONDS - 1)), 1)
            self.assertEqual(len(cache.load(competition, "autotrader_browser", [2020], now=100 + MAX_OLDER_TTL_SECONDS - 1)), 1)
            self.assertEqual(cache.load(competition, "autotrader_browser", [2026], now=100 + MAX_RECENT_TTL_SECONDS + 1), [])
            self.assertEqual(cache.load(competition, "autotrader_browser", [2020], now=100 + MAX_OLDER_TTL_SECONDS + 1), [])
            self.assertEqual(cache.load(base, "autotrader_browser", [2020], now=101), [])

    def test_cache_policy_migrates_existing_marketplace_and_review_rows_to_three_days(self) -> None:
        self.assertEqual(MAX_RECENT_TTL_SECONDS, 3 * 24 * 60 * 60)
        self.assertEqual(MAX_OLDER_TTL_SECONDS, 3 * 24 * 60 * 60)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cache.sqlite3"
            request = parse_vehicle_query("Porsche 911 Carrera")
            old_marketplace = CaptureCache(path, recent_ttl_seconds=24 * 60 * 60)
            old_marketplace.store_year(
                request,
                "porsche_finder_browser",
                2026,
                {"listings": [{"year": 2026, "price": 150000}]},
                current_year=2026,
                captured_at=100,
            )
            old_review = ResearchResultCache(path, ttl_seconds=24 * 60 * 60)
            old_review.store("collector_review", {"query": "porsche 911 carrera"}, {"status": "success"}, captured_at=100)

            marketplace = CaptureCache(path)
            review = ResearchResultCache(path)
            self.assertEqual(
                len(marketplace.load(request, "porsche_finder_browser", [2026], now=100 + 2 * 24 * 60 * 60)),
                1,
            )
            self.assertEqual(
                review.load("collector_review", {"query": "porsche 911 carrera"}, now=100 + 2 * 24 * 60 * 60),
                {"status": "success"},
            )

    def test_empty_cache_attempt_cannot_replace_accepted_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cache = CaptureCache(Path(tmp) / "cache.sqlite3")
            request = parse_vehicle_query("BMW M4")
            cache.store_year(
                request,
                "autotrader_browser",
                2026,
                {"listings": [{"year": 2026, "price": 90000}]},
                current_year=2026,
                captured_at=100,
            )
            cache.store_year(
                request,
                "autotrader_browser",
                2026,
                {"listings": []},
                current_year=2026,
                captured_at=200,
                overwrite_existing=False,
            )
            entries = cache.load(request, "autotrader_browser", [2026], now=201)
            self.assertEqual(entries[0].payload["listings"], [{"year": 2026, "price": 90000}])

    def test_visor_facets_are_reused_from_three_day_result_cache(self) -> None:
        facet_calls = 0

        def collect_facets(request):
            nonlocal facet_calls
            facet_calls += 1
            return {
                "query": request.raw,
                "status": "success",
                "notes": [],
                "sources": [{"source": "visor_public_facets", "status": "success"}],
                "listings": [
                    {
                        "source": "visor_public_facets",
                        "year": 2023,
                        "price": 75000,
                        "title": "2023 BMW M4 Competition Visor aggregate",
                        "condition": "used",
                    }
                ],
                "msrp": None,
            }

        with tempfile.TemporaryDirectory() as tmp:
            manager = CollectionManager(CollectorConfig(root=Path(tmp), codex_path="", use_visor_facets=True))
            request = parse_vehicle_query("2023 BMW M4 Competition")
            for index in range(2):
                job = CollectionJob(
                    id=f"facet-cache-{index}",
                    query=request.raw,
                    status="queued",
                    created_at=time.time(),
                    updated_at=time.time(),
                )
                manager._jobs[job.id] = job
                with (
                    patch("car_compare.collector.collect_visor_public_facets", side_effect=collect_facets),
                    patch("car_compare.collector.codex_login_status", return_value={"authenticated": False}),
                    patch.object(manager, "_codex_path", return_value=""),
                    patch.object(manager, "_browser_worker_available", return_value=False),
                ):
                    manager._run_job(job.id, request)

        self.assertEqual(facet_calls, 1)

    def test_combined_coverage_accepts_marketplace_rows_plus_aggregate_support(self) -> None:
        request = parse_vehicle_query("2023 BMW M4 Competition")
        rows = [
            {
                "source": "autotrader_browser",
                "year": 2023,
                "price": 70000 + index,
                "mileage": 10000 + index,
                "title": "2023 BMW M4 Competition Coupe",
                "vin": f"WBS33AZ0{index:09d}"[-17:],
            }
            for index in range(15)
        ]
        audit = {
            "source": "autotrader_browser",
            "browser_verified": True,
            "listings": rows,
        }
        baseline = {
            "evidence": [
                {"source": "visor_public_facets", "year": 2023, "price_bins": [{"count": 30}]}
            ]
        }

        coverage = _combined_year_coverage(request, baseline, [audit])

        self.assertTrue(coverage["met"])
        self.assertEqual(coverage["years"][2023]["individual_rows"], 15)
        self.assertTrue(coverage["years"][2023]["aggregate_support"])

    def test_generation_research_reuses_fresh_persistent_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manager = GenerationResearchManager(GenerationResearchConfig(root=root))
            request = parse_vehicle_query("BMW M4 Competition")
            cached = {
                "status": "success",
                "query": request.raw,
                "adjustments": [],
                "sources": [],
            }
            manager._cache.store("generation_impact", _generation_cache_identity(request), cached)

            job = manager.start(request.raw, request.max_age)

            self.assertEqual(job.status, "completed")
            self.assertTrue(job.cache_hit)
            self.assertIsNotNone(job.result)

    def test_second_collection_uses_verified_cache_without_browser_restart(self) -> None:
        targets = [
            {
                "source": "autotrader_browser",
                "url": "https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4?startYear=2023&endYear=2023",
                "required_keywords": ["BMW", "M4", "Competition"],
                "exclude_keywords": ["CS"],
            },
            {
                "source": "edmunds_browser",
                "url": "https://www.edmunds.com/inventory/srp.html?make=bmw&model=m4&year=2023",
                "required_keywords": ["BMW", "M4", "Competition"],
                "exclude_keywords": ["CS"],
            },
        ]
        rows = [
            {
                "source": "autotrader_browser",
                "year": 2023,
                "price": 70000 + index,
                "mileage": 10000 + index,
                "title": "2023 BMW M4 Competition Coupe",
                "vin": f"WBS33AZ0{index:09d}",
            }
            for index in range(15)
        ]
        browser_calls = 0

        def fake_run(_command, *, input, **_kwargs):
            nonlocal browser_calls
            browser_calls += 1
            payload = json.loads(input)
            audits = []
            for item in payload["targets"]:
                accepted = rows if item["source"] == "autotrader_browser" else []
                audits.append(
                    {
                        "source": item["source"],
                        "url": item["url"],
                        "status": "partial" if accepted else "blocked",
                        "browser_verified": True,
                        "browser_mode": "persistent_profile_headful",
                        "pages_examined": 1,
                        "cards_examined": len(accepted),
                        "listings": accepted,
                        "stop_reason": "source_exhausted" if accepted else "access_wall",
                    }
                )
            return SimpleNamespace(returncode=0, stdout=json.dumps(audits), stderr="")

        baseline = {
            "evidence": [{"source": "visor_public_facets", "year": 2023, "price_bins": [{"count": 40}]}]
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first_dir = root / "first"
            second_dir = root / "second"
            first_dir.mkdir()
            second_dir.mkdir()
            manager = CollectionManager(CollectorConfig(root=root))
            request = parse_vehicle_query("2023 BMW M4 Competition")
            with (
                patch("car_compare.collector.build_collection_plan", return_value={"targets": targets}),
                patch("car_compare.collector.subprocess.run", side_effect=fake_run),
                patch.object(manager, "_run_host_chrome_fallbacks", side_effect=lambda _request, _payloads, audits, _job_dir: audits),
                patch.object(manager, "_run_codex_search_fallbacks", side_effect=lambda _request, _payloads, audits, _job_dir: audits),
            ):
                first = manager._run_browser_sources(request, first_dir, baseline)
                second = manager._run_browser_sources(request, second_dir, baseline)

        self.assertEqual(browser_calls, 1)
        self.assertTrue(first["combinedYearCoverage"]["met"])
        self.assertTrue(second["combinedYearCoverage"]["met"])
        self.assertEqual(second["collectionSummary"][0]["cacheEntries"], 1)

    def test_codex_web_search_command_and_prompt_are_unattended(self) -> None:
        command = build_codex_web_search_command(
            codex_path="/opt/codex",
            root=Path("/tmp/car-compare"),
            schema_path=Path("/tmp/search-schema.json"),
            output_path=Path("/tmp/search-output.json"),
        )
        self.assertLess(command.index("--search"), command.index("exec"))
        self.assertIn("--ephemeral", command)
        self.assertIn("never", command)
        prompt = build_codex_web_search_prompt(
            parse_vehicle_query("BMW M4 Competition"),
            [2023],
            ["https://www.edmunds.com/bmw/m4/2023/for-sale/"],
        )
        self.assertIn("verbatim source evidence", prompt)
        self.assertIn("Do not use snippets or facts from any non-Edmunds host", prompt)

    def test_codex_web_search_capture_uses_deterministic_parser(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manager = CollectionManager(CollectorConfig(root=root))
            request = parse_vehicle_query("2023 BMW M4 Competition")
            payload = {
                "source": "edmunds_browser",
                "url": "https://www.edmunds.com/inventory/srp.html?make=bmw&model=m4&year=2023",
                "start_year": 2023,
                "end_year": 2023,
            }
            output = {
                "source": "edmunds_browser",
                "status": "partial",
                "pages": [
                    {
                        "url": "https://www.edmunds.com/bmw/m4/2023/for-sale/",
                        "model_year": 2023,
                        "visible_text": (
                            "2023 BMW M4 Competition Coupe\n$78,991\n19,795 miles\nVIN:\nWBS33AZ00PCM11056\n---\n"
                            "2023 BMW M4 Base Coupe\n$65,000\n20,000 miles\nVIN:\nWBS53AZ00PCM11057\n"
                        ),
                    },
                    {
                        "url": "https://example.com/not-edmunds",
                        "model_year": 2023,
                        "visible_text": "2023 BMW M4 Competition Coupe\n$1,000\n1 mile",
                    },
                ],
                "notes": [],
            }

            def fake_search(command, **_kwargs):
                output_path = Path(command[command.index("-o") + 1])
                output_path.write_text(json.dumps(output), encoding="utf-8")
                return SimpleNamespace(returncode=0, stdout="", stderr="")

            with (
                patch("car_compare.collector.subprocess.run", side_effect=fake_search),
                patch("car_compare.sources.browser_capture._runtime_current_year", return_value=2026),
                patch("car_compare.collector._runtime_current_year", return_value=2026),
            ):
                audit = manager._collect_codex_web_search_source(
                    request,
                    payload,
                    root,
                    codex_path="/opt/codex",
                    host_chrome_attempted=True,
                )

            self.assertEqual(audit["accepted"], 1)
            self.assertFalse(audit["browser_verified"])
            self.assertTrue(audit["search_verified"])
            self.assertTrue(audit["deterministic_verified"])
            self.assertEqual(audit["rejected_by_reason"], {"invalid_search_page": 1})
            self.assertEqual(audit["listings"][0]["vin"], "WBS33AZ00PCM11056")

    def test_host_chrome_capture_is_parsed_without_manual_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manager = CollectionManager(CollectorConfig(root=Path(tmp)))
            request = parse_vehicle_query("2025 BMW M4 Competition")
            payload = {
                "source": "autotrader_browser",
                "url": "https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4?startYear=2025&endYear=2025",
                "start_year": 2025,
                "end_year": 2025,
            }
            capture = {
                "title": "BMW M4 listings",
                "url": payload["url"],
                "requestedUrl": payload["url"],
                "text": "Used 2025 BMW M4 Competition xDrive Coupe\n$83,999\n4,461 miles\n",
                "pagesExamined": 1,
                "cardsExamined": 1,
                "loadMoreClicked": 0,
            }
            with (
                patch("car_compare.collector.capture_with_host_chrome", return_value=capture),
                patch("car_compare.sources.browser_capture._runtime_current_year", return_value=2026),
                patch("car_compare.collector._runtime_current_year", return_value=2026),
            ):
                audit = manager._collect_host_chrome_source(request, payload, Path(tmp))

            self.assertEqual(audit["accepted"], 1)
            self.assertTrue(audit["host_chrome_attempted"])
            self.assertEqual(audit["browser_mode"], "system_chrome_applescript")
            self.assertTrue((Path(tmp) / "browser_capture_autotrader_browser.json").exists())

    def test_host_chrome_access_wall_does_not_create_click_fallback(self) -> None:
        self.assertTrue(
            capture_is_access_wall(
                {"title": "403 - Access Denied", "text": "Network restrictions or unusual activity."}
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            manager = CollectionManager(CollectorConfig(root=Path(tmp), dry_run=True))
            job = CollectionJob(
                id="zero-click-blocked",
                query="BMW M4 Competition",
                status="completed",
                created_at=time.time(),
                updated_at=time.time(),
                result={
                    "query": "BMW M4 Competition",
                    "status": "partial",
                    "sources": [
                        {
                            "source": "autotrader_browser",
                            "status": "blocked",
                            "accepted": 0,
                            "host_chrome_attempted": True,
                            "stop_reason": "host_chrome_access_wall",
                        },
                        {
                            "source": "edmunds_browser",
                            "status": "blocked",
                            "accepted": 0,
                            "host_chrome_attempted": True,
                            "stop_reason": "host_chrome_access_wall",
                        },
                    ],
                    "listings": [],
                },
            )
            manager._jobs[job.id] = job
            manager._sync_fallback_lease(job.id)
            self.assertIsNone(manager.job_payload(job.id)["fallback"])

    def test_codex_browser_capture_replaces_blocked_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manager = CollectionManager(CollectorConfig(root=Path(tmp), dry_run=True))
            job = CollectionJob(
                id="blocked-job",
                query="BMW M4 Competition",
                status="completed",
                created_at=time.time(),
                updated_at=time.time(),
                max_age=5,
                result={
                    "query": "BMW M4 Competition",
                    "status": "partial",
                    "notes": [],
                    "sources": [
                        {"source": "autotrader_browser", "status": "blocked", "accepted": 0},
                        {"source": "edmunds_browser", "status": "blocked", "accepted": 0},
                    ],
                    "listings": [],
                },
            )
            manager._jobs[job.id] = job
            manager._sync_fallback_lease(job.id)
            with patch("car_compare.sources.browser_capture._runtime_current_year", return_value=2026):
                result = manager.import_codex_browser_capture(
                    job.id,
                    source="autotrader_browser",
                    url="https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4",
                    visible_text=(
                        "Used 2025 BMW M4\nCompetition Coupe\n$83,999\n4,461 miles\n"
                        "Used 2025 BMW M4\nBase Coupe\n$75,000\n8,000 miles\n"
                        "Used 2009 BMW M4\nCompetition Coupe\n$25,000\n80,000 miles\n"
                    ),
                    pages_examined=1,
                    cards_examined=3,
                    load_more_clicked=1,
                )

            self.assertEqual(result["accepted"], 1)
            audit = json.loads(
                (Path(tmp) / "data" / "collector_jobs" / job.id / "browser_capture_autotrader_browser.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(audit["browser_mode"], "codex_browser_action")
            self.assertTrue(audit["browser_verified"])
            self.assertEqual(len(manager.get(job.id).result["listings"]), 1)
            actions = manager.browser_actions()
            self.assertEqual([item["source"] for item in actions[0]["sources"]], ["edmunds_browser"])
            restored = CollectionManager(CollectorConfig(root=Path(tmp), dry_run=True))
            self.assertIsNotNone(restored.get(job.id))
            self.assertEqual(restored.get(job.id).max_age, 5)
            self.assertEqual([item["source"] for item in restored.browser_actions()[0]["sources"]], ["edmunds_browser"])
            with patch("car_compare.sources.browser_capture._runtime_current_year", return_value=2026):
                restored.import_codex_browser_capture(
                    job.id,
                    source="edmunds_browser",
                    url="https://www.edmunds.com/inventory/srp.html?make=bmw&model=m4",
                    visible_text="Used 2024 BMW M4 Competition Coupe\n$79,500\n9,200 miles\n",
                )
            self.assertEqual(restored.browser_actions(), [])
            self.assertEqual(restored.job_payload(job.id)["fallback"]["status"], "completed")

    def test_codex_browser_capture_rejects_wrong_source_host(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manager = CollectionManager(CollectorConfig(root=Path(tmp), dry_run=True))
            job = CollectionJob(
                id="blocked-job",
                query="BMW M4",
                status="completed",
                created_at=time.time(),
                updated_at=time.time(),
                result={
                    "query": "BMW M4",
                    "status": "partial",
                    "sources": [{"source": "autotrader_browser", "status": "blocked", "accepted": 0}],
                    "listings": [],
                },
            )
            manager._jobs[job.id] = job
            manager._sync_fallback_lease(job.id)
            with self.assertRaisesRegex(ValueError, "autotrader.com"):
                manager.import_codex_browser_capture(
                    job.id,
                    source="autotrader_browser",
                    url="https://example.com/listings",
                    visible_text="Used 2025 BMW M4 $83,999",
                )

    def test_fallback_lease_expires_and_old_results_do_not_reopen(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manager = CollectionManager(CollectorConfig(root=root, dry_run=True))
            job = CollectionJob(
                id="expiring-job",
                query="BMW M4 Competition",
                status="completed",
                created_at=time.time(),
                updated_at=time.time(),
                result={
                    "query": "BMW M4 Competition",
                    "status": "partial",
                    "sources": [{"source": "autotrader_browser", "status": "blocked", "accepted": 0}],
                    "listings": [],
                },
            )
            manager._jobs[job.id] = job
            manager._write_job_result(job.id, job.result)
            manager._sync_fallback_lease(job.id)
            self.assertEqual(manager.job_payload(job.id)["fallback"]["status"], "pending")

            job.fallback_expires_at = time.time() - 1
            manager._write_fallback_lease(job)
            self.assertEqual(manager.browser_actions(), [])
            self.assertEqual(manager.job_payload(job.id)["fallback"]["status"], "expired")
            with self.assertRaisesRegex(RuntimeError, "not active"):
                manager.import_codex_browser_capture(
                    job.id,
                    source="autotrader_browser",
                    url="https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4",
                    visible_text="Used 2025 BMW M4 Competition $83,999",
                )

            old_job_dir = root / "data" / "collector_jobs" / "old-job"
            old_job_dir.mkdir(parents=True)
            (old_job_dir / "collector_result.json").write_text(
                json.dumps(
                    {
                        "query": "Porsche 911",
                        "status": "partial",
                        "sources": [{"source": "edmunds_browser", "status": "blocked", "accepted": 0}],
                        "listings": [],
                    }
                ),
                encoding="utf-8",
            )
            restored = CollectionManager(CollectorConfig(root=root, dry_run=True))
            self.assertEqual(restored.browser_actions(), [])

    def test_optional_collection_browser_cdp_is_local(self) -> None:
        url, configured = browser_cdp_url({})
        self.assertEqual(url, "http://127.0.0.1:9222")
        self.assertFalse(configured)
        invalid = browser_cdp_status({"CAR_COMPARE_BROWSER_CDP_URL": "https://browser.example.com:9222"})
        self.assertFalse(invalid["ready"])
        self.assertEqual(invalid["mode"], "invalid")

    def test_browser_sources_use_bounded_parallel_range_batch(self) -> None:
        targets = [
            {
                "source": "autotrader_browser",
                "url": "https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4",
                "required_keywords": ["BMW", "M4"],
                "exclude_keywords": [],
            },
            {
                "source": "edmunds_browser",
                "url": "https://www.edmunds.com/inventory/srp.html?make=bmw&model=m4",
                "required_keywords": ["BMW", "M4"],
                "exclude_keywords": [],
            },
        ]
        batches: list[dict[str, object]] = []

        def fake_run(_command, *, input, **_kwargs):
            payload = json.loads(input)
            batches.append(payload)
            audits = [
                {
                    "source": item["source"],
                    "url": item["url"],
                    "status": "blocked",
                    "browser_verified": True,
                    "browser_mode": "persistent_profile_headful",
                    "pages_examined": 1,
                    "cards_examined": 1,
                    "listings": [],
                    "range_search": {"accepted": 0},
                    "attempted_year_searches": 0,
                    "avoided_year_searches": 0,
                    "stop_reason": "access_wall",
                }
                for item in payload["targets"]
            ]
            return SimpleNamespace(returncode=0, stdout=json.dumps(audits), stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            manager = CollectionManager(CollectorConfig(root=Path(tmp)))
            with (
                patch("car_compare.collector.build_collection_plan", return_value={"targets": targets}),
                patch("car_compare.collector.subprocess.run", side_effect=fake_run),
                patch.object(manager, "_run_host_chrome_fallbacks", side_effect=lambda _request, _payloads, audits, _job_dir: audits),
                patch.object(manager, "_run_codex_search_fallbacks", side_effect=lambda _request, _payloads, audits, _job_dir: audits),
            ):
                result = manager._run_browser_sources(parse_vehicle_query("BMW M4"), Path(tmp))

        self.assertEqual(len(batches), 1)
        self.assertEqual(batches[0]["max_concurrency"], 2)
        self.assertEqual(
            [item["source"] for item in batches[0]["targets"]],
            ["autotrader_browser", "edmunds_browser"],
        )
        self.assertTrue(all(item["split_by_year"] is False for item in batches[0]["targets"]))
        self.assertTrue(result["combinedYearCoverage"]["sparse_years"])

    def test_new_marketplace_gets_bootstrap_pass_when_other_cache_meets_coverage(self) -> None:
        targets = [
            {
                "source": "autotrader_browser",
                "url": "https://www.autotrader.com/cars-for-sale/all-cars/porsche/911",
                "required_keywords": ["Porsche", "911", "Carrera"],
                "exclude_keywords": [],
            },
            {
                "source": "edmunds_browser",
                "url": "https://www.edmunds.com/inventory/srp.html?make=porsche&model=911",
                "required_keywords": ["Porsche", "911", "Carrera"],
                "exclude_keywords": [],
            },
            {
                "source": "porsche_finder_browser",
                "url": "https://finder.porsche.com/us/en-US/search/911?model=911",
                "required_keywords": ["Porsche", "911", "Carrera"],
                "exclude_keywords": [],
            },
        ]
        cached = [
            {
                "source": source,
                "url": target["url"],
                "status": "collected",
                "browser_verified": True,
                "cache_years": list(range(2016, 2027)),
                "listings": [],
            }
            for source, target in zip(("autotrader_browser", "edmunds_browser"), targets[:2])
        ]
        live = {
            "source": "porsche_finder_browser",
            "url": targets[2]["url"],
            "status": "collected",
            "browser_verified": True,
            "browser_mode": "persistent_profile_headless",
            "pages_examined": 1,
            "cards_examined": 1,
            "listings": [],
            "stop_reason": "source_exhausted",
        }
        with tempfile.TemporaryDirectory() as tmp:
            manager = CollectionManager(CollectorConfig(root=Path(tmp)))
            with (
                patch("car_compare.collector.build_collection_plan", return_value={"targets": targets}),
                patch("car_compare.collector._combined_year_coverage", return_value={"years": {}, "sparse_years": [], "met": True}),
                patch.object(manager, "_cached_browser_audits", return_value=cached),
                patch.object(manager, "_run_browser_batch", return_value=[live]) as run_batch,
                patch.object(manager, "_store_audit_cache"),
            ):
                manager._run_browser_sources(parse_vehicle_query("Porsche 911 Carrera"), Path(tmp))

        requested = run_batch.call_args.args[0]
        self.assertEqual([item["source"] for item in requested], ["porsche_finder_browser"])

    def test_fresh_complete_source_year_cache_suppresses_sparse_recollection(self) -> None:
        targets = [
            {
                "source": "autotrader_browser",
                "url": "https://www.autotrader.com/cars-for-sale/all-cars/bmw/m4",
                "required_keywords": ["BMW", "M4"],
                "exclude_keywords": [],
            },
            {
                "source": "edmunds_browser",
                "url": "https://www.edmunds.com/inventory/srp.html?make=bmw&model=m4",
                "required_keywords": ["BMW", "M4"],
                "exclude_keywords": [],
            },
        ]
        cached = [
            {
                "source": target["source"],
                "url": target["url"],
                "status": "partial",
                "browser_verified": True,
                "cache_verified": True,
                "cache_years": list(range(2016, 2027)),
                "listings": [],
            }
            for target in targets
        ]
        sparse = {"years": {}, "sparse_years": [2016, 2017], "met": False}
        with tempfile.TemporaryDirectory() as tmp:
            manager = CollectionManager(CollectorConfig(root=Path(tmp)))
            with (
                patch("car_compare.collector.build_collection_plan", return_value={"targets": targets}),
                patch("car_compare.collector._combined_year_coverage", return_value=sparse),
                patch.object(manager, "_cached_browser_audits", return_value=cached),
                patch.object(manager, "_run_browser_batch") as run_batch,
                patch.object(manager, "_run_host_chrome_fallbacks") as host_fallback,
                patch.object(manager, "_run_codex_search_fallbacks") as search_fallback,
            ):
                manager._run_browser_sources(parse_vehicle_query("BMW M4"), Path(tmp))

        run_batch.assert_not_called()
        host_fallback.assert_not_called()
        search_fallback.assert_not_called()

    def test_codex_review_does_not_repeat_marketplace_pass(self) -> None:
        prompt = build_codex_prompt(
            parse_vehicle_query("BMW M4"),
            [{"source": "edmunds_browser", "status": "blocked", "stopReason": "access_wall_circuit_breaker"}],
        )
        self.assertIn("Do not call the tool again in this job", prompt)

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
        self.assertIn('model_reasoning_effort="low"', command)

    def test_codex_workloads_pin_recommended_reasoning_efforts(self) -> None:
        web_search = build_codex_web_search_command(
            codex_path="/usr/local/bin/codex",
            root=Path("/tmp/car-compare"),
            schema_path=Path("/tmp/search-schema.json"),
            output_path=Path("/tmp/search-output.json"),
        )
        generation = build_generation_research_command(
            codex_path="/usr/local/bin/codex",
            root=Path("/tmp/car-compare"),
            schema_path=Path("/tmp/generation-schema.json"),
            output_path=Path("/tmp/generation-output.json"),
        )
        self.assertIn('model_reasoning_effort="low"', web_search)
        self.assertIn('model_reasoning_effort="high"', generation)
        self.assertEqual(normalize_codex_reasoning_effort("invalid", "low"), "low")
        self.assertEqual(normalize_codex_reasoning_effort(" XHIGH ", "high"), "xhigh")
        request = parse_vehicle_query("BMW M4")
        self.assertEqual(_generation_cache_identity(request)["reasoning_effort"], "high")

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

    def test_legacy_facet_rows_recover_market_weights_from_raw_evidence(self) -> None:
        result = {
            "listings": [
                {
                    "source": "visor_public_facets",
                    "year": 2025,
                    "price": price,
                    "title": f"2025 Porsche 911 Visor aggregate bin 1 sample {index}",
                    "url": "https://example.test/911?year=2025",
                    "confidence": "aggregate_facets",
                }
                for index, price in enumerate((190000, 200000), 1)
            ],
            "evidence": [
                {
                    "source": "visor_public_facets",
                    "year": 2025,
                    "url": "https://example.test/911?year=2025",
                    "price_bins": [{"lower": 180000, "upper": 210000, "count": 100}],
                }
            ],
        }
        listings = listings_from_result(result)
        self.assertEqual([item.market_weight for item in listings], [50, 50])

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

    def test_merge_omits_unavailable_visor_alias_when_public_facets_succeeded(self) -> None:
        facet = {
            "status": "success",
            "sources": [
                {"source": "visor_public_facets", "status": "success"},
                {"source": "visor_public_facets_new", "status": "success"},
            ],
            "listings": [{"source": "visor_public_facets", "year": 2023, "price": 200000}],
            "msrp": None,
        }
        codex = {
            "status": "partial",
            "sources": [
                {"source": "visor_api_or_facets", "status": "unavailable"},
                {"source": "visor_new_facets", "status": "blocked"},
                {"source": "manufacturer_official_new", "status": "partial"},
            ],
            "listings": [],
            "msrp": None,
        }

        merged = _merge_collector_results(facet, codex)

        self.assertEqual(
            [item["source"] for item in merged["sources"]],
            ["visor_public_facets", "visor_public_facets_new", "manufacturer_official_new"],
        )

    def test_merge_binds_automatic_msrp_to_target_year(self) -> None:
        request = parse_vehicle_query("2022 BMW M4 Competition")
        facet = {
            "status": "success",
            "listings": [],
            "msrp": {"price": 80000, "label": "2022 BMW M4 Competition MSRP", "source": "visor", "url": "", "year": 2022},
        }
        codex = {
            "status": "success",
            "listings": [],
            "msrp": {"price": 90000, "label": "2026 BMW M4 Competition MSRP", "source": "codex", "url": "", "year": 2026},
        }
        merged = _merge_collector_results(facet, codex, request)
        self.assertEqual(merged["msrp"]["year"], 2022)
        self.assertEqual(merged["msrp"]["source"], "visor")


if __name__ == "__main__":
    unittest.main()
