from __future__ import annotations

from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class InputParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.inputs: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "input":
            self.inputs.append({key: value or "" for key, value in attrs})


class UiAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        self.javascript = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        self.styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")

    def test_default_number_inputs_are_browser_valid(self) -> None:
        parser = InputParser()
        parser.feed(self.html)
        for field in parser.inputs:
            if field.get("type") != "number" or "value" not in field or field.get("step") in {None, "", "any"}:
                continue
            value = Decimal(field["value"])
            step = Decimal(field["step"])
            base = Decimal(field.get("min", "0") or "0")
            self.assertEqual(
                (value - base) % step,
                Decimal("0"),
                f'{field.get("id", "number input")} has a default value rejected by its HTML step rule',
            )

    def test_portfolio_actions_and_benchmarks_are_explicit(self) -> None:
        self.assertIn("Run strategy comparison", self.html)
        self.assertIn("100% QQQ", self.html)
        self.assertIn("100% SPY", self.html)
        self.assertIn("Restore target percentages", self.html)
        self.assertIn("run_portfolio", (ROOT / "app.py").read_text(encoding="utf-8"))

    def test_stock_picker_requires_verified_search_result(self) -> None:
        self.assertIn("Search stocks and ETFs", self.html)
        self.assertIn("Find a verified ticker", self.html)
        self.assertIn("data-search-index", self.javascript)
        self.assertNotIn("addHolding({symbol:value(\"symbolQuery\")", self.javascript)

    def test_tiingo_is_subtle_and_machine_local(self) -> None:
        self.assertIn("Free share-data settings", self.html)
        self.assertIn("saved on this computer", self.html)
        self.assertIn("price rows are used during a run and are not kept afterward", self.html)
        self.assertIn("Import local history", self.html)

    def test_allocations_are_direct_and_cash_can_fill_the_remainder(self) -> None:
        self.assertIn("independent percentage", self.html)
        self.assertIn("Put remainder in cash", self.html)
        self.assertIn("Normalize to 100%", self.html)
        self.assertIn("Cash allocation percentage number", self.javascript)
        self.assertIn("cashWeight:state.cashWeight", self.javascript)
        self.assertIn("normalizeAllocations", self.javascript)
        self.assertNotIn("normalizeHoldings", self.javascript)

    def test_default_portfolio_is_the_requested_balanced_options_mix(self) -> None:
        self.assertIn("holdings:defaultPortfolio(), cashWeight:25", self.javascript)
        self.assertIn('stockItem("SPY","SPDR S&P 500 ETF Trust","ETF",27.5)', self.javascript)
        self.assertIn('stockItem("QQQ","Invesco QQQ Trust","ETF",27.5)', self.javascript)
        self.assertIn('optionItem("SPY","SPDR S&P 500 ETF Trust","ETF","call",8)', self.javascript)
        self.assertIn('optionItem("QQQ","Invesco QQQ Trust","ETF","call",8)', self.javascript)
        self.assertIn('optionItem("SPY","SPDR S&P 500 ETF Trust","ETF","put",2)', self.javascript)
        self.assertIn('optionItem("QQQ","Invesco QQQ Trust","ETF","put",2)', self.javascript)
        self.assertIn("Balanced shares, options &amp; cash", self.html)

    def test_decimal_percentage_has_separate_visible_suffix(self) -> None:
        self.assertIn("grid-template-columns:minmax(0,1fr) 12px", self.styles)
        self.assertIn("font-variant-numeric:tabular-nums", self.styles)
        self.assertIn("text-align:center", self.styles)
        self.assertIn("::-webkit-inner-spin-button", self.styles)

    def test_chart_has_ranges_zoom_scroll_and_point_comparison(self) -> None:
        for label in ("1M", "3M", "1Y", "3Y", "5Y", "All", "Fit all"):
            self.assertIn(f">{label}<", self.html)
        self.assertIn("Hover or touch the chart", self.html)
        self.assertIn("showChartPoint", self.javascript)
        self.assertIn("Strategy vs QQQ", self.javascript)
        self.assertIn("overflow-x:auto", self.styles)

    def test_shorter_usable_coverage_is_prominent(self) -> None:
        self.assertIn('id="coverageNotice"', self.html)
        self.assertIn("usable comparison", self.javascript)

    def test_one_page_can_add_shares_calls_or_puts_from_one_search_result(self) -> None:
        self.assertNotIn('href="/options"', self.html)
        self.assertFalse((ROOT / "static" / "options.html").exists())
        for choice in ("Shares", "Long call", "Protective put", "Short put"):
            self.assertIn(f'>{choice}</button>', self.javascript)
        self.assertIn("data-add-kind", self.javascript)
        self.assertIn("item.kind", self.javascript)

    def test_unified_page_has_option_rules_and_both_real_data_connections(self) -> None:
        self.assertIn("Option selection", self.html)
        self.assertIn("Expiration, roll &amp; strike", self.html)
        self.assertIn("Expiration days", self.javascript)
        self.assertIn("Optional exact-options connection", self.html)
        self.assertIn("Real share history plus clearly labeled option estimates", self.html)
        self.assertIn("callRule", self.javascript)
        self.assertIn("putRule", self.javascript)

    def test_strike_rules_are_beginner_friendly_and_provider_safe(self) -> None:
        for label in (
            "Near the stock price (ATM)",
            "Percentage below stock price",
            "Percentage above stock price",
            "Dollar amount below stock price",
            "Dollar amount above stock price",
        ):
            self.assertIn(label, self.javascript)
        for field in ("targetDte", "rollDte", "strikeMode", "strikeValue"):
            self.assertIn(f'data-option-field="{field}"', self.javascript)
        self.assertIn("optionRule:{...advanced,...ensureOptionRule(item)}", self.javascript)
        self.assertIn("Use target delta (advanced)", self.javascript)

    def test_unified_page_explains_credit_and_history_consequences(self) -> None:
        self.assertIn("exact-option credits remained", self.javascript)
        self.assertIn("Exact option history under the current plan begins", self.javascript)
        self.assertIn("Saved dates are reused", self.javascript)

    def test_long_runs_use_a_polled_background_job(self) -> None:
        self.assertIn("/api/portfolio/backtests", self.javascript)
        self.assertIn("waitForBacktest", self.javascript)
        self.assertIn("/api/backtests/", self.javascript)
        self.assertIn("all model scenarios reuse this run's download", self.javascript)

    def test_free_long_history_controls_are_explicit(self) -> None:
        for label in ("5 years", "10 years", "15 years"):
            self.assertIn(f">{label}<", self.html)
        self.assertIn("data-history-years", self.html)
        self.assertIn("setHistoryYears", self.javascript)
        self.assertIn("real share history and reference-backed modeled options", self.html)

    def test_free_automatic_mode_is_default_and_needs_no_option_token(self) -> None:
        self.assertIn('name="provider" value="modeled" checked', self.html)
        self.assertIn("No paid option plan", self.html)
        self.assertIn("Retained exact quotes are reused first", self.javascript)
        self.assertIn("30-credit reserve", self.javascript)
        self.assertIn('result.pricingMode==="modeled"', self.javascript)
        self.assertIn("Adjusted shares • exact-first calibrated options", self.javascript)

    def test_modeled_results_show_quality_and_sensitivity(self) -> None:
        self.assertIn("HOW RELIABLE IS THIS RESULT?", self.html)
        self.assertIn('id="sensitivityText"', self.html)
        self.assertIn("Measured model range", self.html)
        self.assertIn("strategyLow", self.javascript)
        self.assertIn("sensitivityBand", self.javascript)

    def test_option_accuracy_workflow_and_labels_are_visible(self) -> None:
        server = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("Improve option accuracy", self.html)
        self.assertIn("Save next calibration batch", self.html)
        self.assertIn("Check measured accuracy", self.html)
        self.assertIn("at most 70 credits", self.html)
        self.assertIn("keeps 30 credits untouched", self.html)
        for endpoint in (
            "/api/pricing-calibration/status",
            "/api/pricing-calibration/sync",
            "/api/pricing-calibration/validate",
        ):
            self.assertIn(endpoint, server)
        for label in (
            "Exact historical quotes",
            "Validated within 1%",
            "Extrapolated historical estimate",
            "Insufficient evidence",
        ):
            self.assertIn(label, (ROOT / "stock_strategy_lab" / "calibration.py").read_text(encoding="utf-8"))
        self.assertIn("assignmentUncertaintyPct", self.javascript)
        self.assertIn("@media(max-width:620px){.accuracyPanelHead", self.styles)

    def test_price_sources_have_accessible_hover_explanations(self) -> None:
        self.assertEqual(self.html.count('class="infoTip"'), 4)
        self.assertEqual(self.html.count('role="tooltip"'), 4)
        self.assertEqual(self.html.count('class="infoTip" tabindex="0" aria-label="About '), 4)
        self.assertIn("Practice mode only", self.html)
        self.assertIn("Missing executable option evidence stops the test", self.html)
        self.assertIn(".infoTip:hover .infoBubble", self.styles)
        self.assertIn(".infoTip:focus .infoBubble", self.styles)

    def test_verified_beta_reprices_and_rejects_unverifiable_data(self) -> None:
        self.assertIn('value="onclick"', self.html)
        self.assertIn("Strict recent validation", self.html)
        self.assertIn("Market Data historical chains and required bid/ask quotes", self.javascript)
        self.assertIn("experimentalIssue", self.javascript)
        self.assertIn("Missing evidence stops the run", self.javascript)
        self.assertIn("Two data connections needed", self.javascript)

    def test_robinhood_option_fee_is_the_visible_default(self) -> None:
        self.assertIn("Robinhood fee model", self.html)
        self.assertIn("$0.04 regulatory/clearing fee", self.html)
        self.assertIn("optionCommission:0.04", self.javascript)


if __name__ == "__main__":
    unittest.main()
