from contextlib import nullcontext
import json
import subprocess
import unittest
from unittest.mock import patch
import urllib.error

from car_compare.sources.http_capture import allowed, VisorRedirects
from car_compare.sources.visor_facets import _fetch_text


class HttpCaptureTests(unittest.TestCase):
    def test_only_public_https_host_is_allowed(self):
        self.assertTrue(allowed("https://visor.vin/search/filters?make=BMW"))
        for url in ("http://visor.vin/", "https://example.com/", "https://visor.vin.evil.test/", "https://user@visor.vin/", "https://visor.vin:1234/"):
            self.assertFalse(allowed(url), url)
        with self.assertRaises(ValueError):
            VisorRedirects().redirect_request(None, None, 302, "redirect", {}, "https://example.com/")

    def test_fetch_passes_global_deadline_and_total_request_timeout(self):
        response = subprocess.CompletedProcess([], 0, json.dumps({"status": 200, "text": "verified page"}), "")
        with patch("car_compare.sources.visor_facets.host_slot", return_value=nullcontext()), patch("car_compare.sources.visor_facets.run_bounded", return_value=response) as run:
            self.assertEqual(_fetch_text("https://visor.vin/search/filters", deadline_at=123), "verified page")
        self.assertEqual(run.call_args.kwargs["deadline_at"], 123)
        self.assertLessEqual(run.call_args.kwargs["timeout"], 18)

    def test_rate_limit_header_reaches_shared_cooldown(self):
        response = subprocess.CompletedProcess([], 0, json.dumps({"status": 429, "retry_after": "120", "error": "limited"}), "")
        with patch("car_compare.sources.visor_facets.host_slot", return_value=nullcontext()), patch("car_compare.sources.visor_facets.run_bounded", return_value=response), patch("car_compare.sources.visor_facets.rate_limited") as cooldown:
            with self.assertRaises(urllib.error.HTTPError) as raised:
                _fetch_text("https://visor.vin/search/filters", deadline_at=123)
            raised.exception.close()
        cooldown.assert_called_once_with("https://visor.vin/search/filters", "120")
