from __future__ import annotations

import argparse
from collections import defaultdict, deque
import csv
from datetime import date, datetime, timedelta
from io import StringIO
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import time
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit
from zoneinfo import ZoneInfo

from stock_strategy_lab.calendar import trading_dates
from stock_strategy_lab.calibration import AccuracyCalibration
from stock_strategy_lab.collector import DailyCollectorScheduler, VaultCollector
from stock_strategy_lab.credentials import LocalTokenStore
from stock_strategy_lab.jobs import JobManager
from stock_strategy_lab.models import ROBINHOOD_OPTION_FEE_PER_CONTRACT, OptionRule, StockBar, strategy_from_dict
from stock_strategy_lab.modeled import FreeModeledProvider
from stock_strategy_lab.onclick import OnclickBacktestProvider
from stock_strategy_lab.portfolio import DemoPortfolioProvider, Holding, run_portfolio_backtest
from stock_strategy_lab.providers import FixtureProvider, MarketDataProvider, ProviderError
from stock_strategy_lab.reference_data import FreeReferenceData
from stock_strategy_lab.shared_auth import SharedSessionAuth
from stock_strategy_lab.storage import CAPTURE_PROFILE_CREDITS, AppStore, MarketVault
from stock_strategy_lab.tiingo import TiingoProvider
from stock_strategy_lab.unified import HybridMarketProvider, InstrumentHolding, run_unified_backtest


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
DATA_DIR = Path(os.environ.get("STOCK_STRATEGY_DATA_DIR", ROOT / "data")).expanduser()
MAX_REQUEST_BYTES = 10 * 1024 * 1024


def environment_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


PUBLIC_MODE = environment_flag("STOCK_STRATEGY_PUBLIC_MODE")
PUBLIC_BACKTESTS_PER_HOUR = max(1, int(os.environ.get("STOCK_STRATEGY_PUBLIC_BACKTESTS_PER_HOUR", "12")))

VAULT = MarketVault(DATA_DIR)
STORE = AppStore(DATA_DIR)
TOKEN_STORE = LocalTokenStore(DATA_DIR)
ENVIRONMENT_TOKEN = os.environ.get("MARKETDATA_API_TOKEN", "").strip()
SAVED_TOKEN = TOKEN_STORE.load()
TOKEN_SOURCE = "local_file" if SAVED_TOKEN else ("environment" if ENVIRONMENT_TOKEN else "none")
MARKET_DATA = MarketDataProvider(VAULT, STORE, token=SAVED_TOKEN or ENVIRONMENT_TOKEN)
TIINGO_TOKEN_STORE = LocalTokenStore(DATA_DIR, "tiingo_token", "Tiingo")
TIINGO_ENVIRONMENT_TOKEN = os.environ.get("TIINGO_API_TOKEN", "").strip()
TIINGO_SAVED_TOKEN = TIINGO_TOKEN_STORE.load()
TIINGO_TOKEN_SOURCE = "local_file" if TIINGO_SAVED_TOKEN else ("environment" if TIINGO_ENVIRONMENT_TOKEN else "none")
TIINGO = TiingoProvider(VAULT, STORE, TIINGO_SAVED_TOKEN or TIINGO_ENVIRONMENT_TOKEN)
REFERENCE_DATA = FreeReferenceData(DATA_DIR)
ACCURACY = AccuracyCalibration(VAULT, STORE, MARKET_DATA, REFERENCE_DATA)
DEMO_PORTFOLIO = DemoPortfolioProvider()
UNIFIED_REAL = HybridMarketProvider(TIINGO, MARKET_DATA)
FREE_MODELED = FreeModeledProvider(
    TIINGO,
    DATA_DIR,
    fred=REFERENCE_DATA,
    calibration=ACCURACY,
    allow_exact_downloads=not PUBLIC_MODE,
)
ONCLICK = OnclickBacktestProvider(
    TIINGO,
    strict_quality=True,
    quote_provider=MARKET_DATA,
    verified_engine=True,
)
COLLECTOR = VaultCollector(MARKET_DATA, VAULT, STORE)
SCHEDULER = DailyCollectorScheduler(COLLECTOR)
AUTH = SharedSessionAuth.from_environment()
EASTERN = ZoneInfo("America/New_York")


def provider_factory(name: str, scenario: str = "wave") -> Any:
    if name == "marketdata":
        return MARKET_DATA
    return FixtureProvider(scenario=scenario if scenario in {"up", "down", "flat", "wave"} else "wave")


JOBS = JobManager(STORE, COLLECTOR, provider_factory)


class RequestError(ValueError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def public_route_allowed(method: str, path: str) -> bool:
    if path == "/api/health":
        return True
    if method == "GET":
        return (
            path in {"/", "/options", "/options/", "/api/portfolio/status", "/api/portfolio/search"}
            or path.startswith("/static/")
            or path.startswith("/api/backtests/")
        )
    return method == "POST" and path == "/api/portfolio/backtests"


class PublicBacktestLimiter:
    def __init__(self, limit: int, window_seconds: int = 3600):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, client_key: str, now: float | None = None) -> bool:
        current = time.monotonic() if now is None else now
        cutoff = current - self.window_seconds
        with self._lock:
            requests = self._requests[client_key]
            while requests and requests[0] <= cutoff:
                requests.popleft()
            if len(requests) >= self.limit:
                return False
            requests.append(current)
            return True


PUBLIC_BACKTEST_LIMITER = PublicBacktestLimiter(PUBLIC_BACKTESTS_PER_HOUR)


class StrategyLabHandler(BaseHTTPRequestHandler):
    server_version = "LongTermStockAllocationLab/0.1"

    def do_GET(self) -> None:
        parsed_url = urlsplit(self.path)
        path = parsed_url.path
        if path == "/api/health":
            self._send_json(
                {"status": "ok", "app": "long-term-stock-allocation-lab", "publicMode": PUBLIC_MODE}
            )
            return
        if not self._require_auth():
            return
        if path == "/":
            self._send_file(STATIC / "index.html")
            return
        if path in {"/options", "/options/"}:
            self.send_response(303)
            self.send_header("Location", "/")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if path.startswith("/static/"):
            self._serve_static(path)
            return
        if path in {"/api/data-status", "/api/vault"}:
            self._send_json(data_status())
            return
        if path == "/api/portfolio/status":
            self._send_json(portfolio_status())
            return
        if path == "/api/reference-data/status":
            self._send_json(REFERENCE_DATA.status())
            return
        if path == "/api/pricing-calibration/status":
            self._send_json(ACCURACY.status())
            return
        if path == "/api/portfolio/search":
            query = str((parse_qs(parsed_url.query).get("q") or [""])[0]).strip()
            provider_name = str((parse_qs(parsed_url.query).get("provider") or ["demo"])[0]).lower()
            try:
                self._send_json({"results": search_portfolio_symbols(query, provider_name)})
            except ProviderError as exc:
                self._send_error(502, str(exc))
            return
        if path == "/api/favorites":
            self._send_json({"favorites": favorite_payloads()})
            return
        if path == "/api/strategies":
            self._send_json({"strategies": STORE.list_strategies()})
            return
        if path == "/api/runs":
            self._send_json({"runs": STORE.list_runs()})
            return
        if path == "/api/jobs":
            self._send_json({"jobs": JOBS.list_recent()})
            return
        if path.startswith("/api/jobs/") or path.startswith("/api/backtests/"):
            job_id = path.rsplit("/", 1)[-1]
            if job_id.endswith(".json") or job_id.endswith(".csv"):
                self._send_error(404, "Not found")
                return
            job = JOBS.get(job_id)
            if job:
                self._send_json(job)
                return
            saved = STORE.get_run(job_id)
            if saved:
                self._send_json({"id": job_id, "status": "complete", "stage": "Saved result", "result": saved})
                return
            self._send_error(404, "Job or saved result not found")
            return
        if path.startswith("/api/runs/"):
            suffix = path.removeprefix("/api/runs/")
            if suffix.endswith("/export.json"):
                run_id = suffix.removesuffix("/export.json")
                self._send_run_json(run_id)
                return
            if suffix.endswith("/export.csv"):
                run_id = suffix.removesuffix("/export.csv")
                self._send_run_csv(run_id)
                return
            payload = STORE.get_run(suffix)
            if not payload:
                self._send_error(404, "Saved result not found")
                return
            self._send_json(payload)
            return
        self._send_error(404, "Not found")

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        if not self._require_auth():
            return
        try:
            body = self._read_json()
            if path == "/api/backtests":
                strategy = strategy_from_dict(dict(body.get("strategy") or body))
                provider_name = str(body.get("provider") or "fixture").lower()
                if provider_name not in {"fixture", "marketdata"}:
                    raise RequestError(400, "Provider must be fixture or marketdata")
                mode = str(body.get("mode") or "single").lower()
                if mode not in {"single", "sweep"}:
                    raise RequestError(400, "Mode must be single or sweep")
                job = JOBS.start_backtest(strategy, provider_name, mode, str(body.get("scenario") or "wave"))
                self._send_json(job, status=202)
                return
            if path == "/api/strategies":
                strategy = strategy_from_dict(dict(body.get("strategy") or body))
                strategy_id = STORE.save_strategy(
                    str(body.get("name") or strategy.name),
                    strategy.to_dict(),
                    str(body.get("id") or "") or None,
                )
                self._send_json({"id": strategy_id, "status": "saved"}, status=201)
                return
            if path == "/api/settings/marketdata-token":
                self._send_json(configure_marketdata_token(body))
                return
            if path == "/api/settings/tiingo-token":
                self._send_json(configure_tiingo_token(body))
                return
            if path == "/api/data/import-stock-csv":
                self._send_json(import_stock_csv(body), status=201)
                return
            if path == "/api/pricing-calibration/sync":
                try:
                    batches = int(body.get("maxSymbolDays") or 4)
                    self._send_json(ACCURACY.sync(max_symbol_days=batches))
                except RuntimeError as exc:
                    raise RequestError(409, str(exc)) from exc
                return
            if path == "/api/pricing-calibration/validate":
                self._send_json(ACCURACY.validate())
                return
            if path == "/api/portfolio/backtests":
                request = portfolio_backtest_request(body)
                provider_name = request.pop("provider")
                if PUBLIC_MODE:
                    if provider_name not in {"demo", "modeled"}:
                        raise RequestError(403, "This public lab supports demo and free automatic tests only")
                    client_key = self.headers.get("CF-Connecting-IP") or self.client_address[0]
                    if not PUBLIC_BACKTEST_LIMITER.allow(client_key):
                        raise RequestError(
                            429,
                            f"This public lab allows {PUBLIC_BACKTESTS_PER_HOUR} tests per hour from one visitor. Please try again later.",
                        )
                provider = (
                    FREE_MODELED
                    if provider_name == "modeled"
                    else (UNIFIED_REAL if provider_name == "real" else (ONCLICK if provider_name == "onclick" else FixtureProvider()))
                )
                self._send_json(JOBS.start_portfolio_backtest(request, provider), status=202)
                return
            if path == "/api/portfolio/backtest":
                request = portfolio_backtest_request(body)
                provider_name = request.pop("provider")
                provider = (
                    FREE_MODELED
                    if provider_name == "modeled"
                    else (UNIFIED_REAL if provider_name == "real" else (ONCLICK if provider_name == "onclick" else FixtureProvider()))
                )
                try:
                    external_runner = getattr(provider, "run_portfolio_backtest", None)
                    result = external_runner(**request) if callable(external_runner) else run_unified_backtest(provider, **request)
                    self._send_json(result)
                except ProviderError as exc:
                    raise RequestError(502, str(exc)) from exc
                return
            if path == "/api/favorites":
                symbol = validate_symbol(str(body.get("symbol") or ""))
                profile = str(body.get("captureProfile") or "balanced")
                active = bool(body.get("active", True))
                current = STORE.estimated_collection_credits()
                existing = next((item for item in STORE.list_favorites() if item["symbol"] == symbol), None)
                old_cost = existing["estimatedDailyCredits"] if existing and existing["active"] else 0
                new_cost = CAPTURE_PROFILE_CREDITS.get(profile, 7) if active else 0
                if current - old_cost + new_cost > 70:
                    raise RequestError(
                        409,
                        "This favorite would use the credits reserved for interactive tests. Pause another symbol or choose a smaller capture profile.",
                    )
                favorite = STORE.save_favorite(symbol, profile, active)
                self._send_json(favorite, status=201)
                return
            if path.startswith("/api/favorites/") and path.endswith("/toggle"):
                symbol = validate_symbol(path.split("/")[3])
                existing = next((item for item in STORE.list_favorites() if item["symbol"] == symbol), None)
                if not existing:
                    raise RequestError(404, "Favorite not found")
                profile = str(body.get("captureProfile") or existing["captureProfile"])
                active = bool(body.get("active", not existing["active"]))
                current = STORE.estimated_collection_credits()
                old_cost = existing["estimatedDailyCredits"] if existing["active"] else 0
                new_cost = CAPTURE_PROFILE_CREDITS.get(profile, 7) if active else 0
                if current - old_cost + new_cost > 70:
                    raise RequestError(
                        409,
                        "Resuming this favorite would use the credits reserved for interactive tests. Pause another symbol or use a smaller profile.",
                    )
                favorite = STORE.save_favorite(symbol, profile, active)
                self._send_json(favorite)
                return
            if path == "/api/vault/sync":
                if not MARKET_DATA.available:
                    raise RequestError(409, "Real-data collection needs MARKETDATA_API_TOKEN on the server")
                self._send_json(JOBS.start_sync(), status=202)
                return
            if path == "/api/vault/backfill/estimate":
                request = historical_backfill_request(body)
                estimate = COLLECTOR.estimate_backfill(**request)
                estimate["historyYears"] = int(body.get("years") or 5)
                self._send_json(estimate)
                return
            if path == "/api/vault/backfill":
                if not MARKET_DATA.available:
                    raise RequestError(409, "Connect a Market Data token before downloading historical data")
                if body.get("confirm") is not True:
                    raise RequestError(400, "Review the estimate and confirm the provider-credit use before starting")
                request = historical_backfill_request(body)
                self._send_json(JOBS.start_backfill(**request), status=202)
                return
            if path == "/api/vault/history-access/verify":
                if not MARKET_DATA.available:
                    raise RequestError(409, "Save a Market Data token before checking five-year access")
                try:
                    self._send_json(MARKET_DATA.verify_five_year_access("SPY"))
                except ProviderError as exc:
                    raise RequestError(502, str(exc)) from exc
                return
            if path == "/api/vault/leaps-protection/estimate":
                request = leaps_protection_request(body, require_verified=False)
                estimate = COLLECTOR.estimate_leaps_protection(**request)
                self._send_json(estimate)
                return
            if path == "/api/vault/leaps-protection/backfill":
                if body.get("confirm") is not True:
                    raise RequestError(400, "Review the estimate and confirm the provider-credit use before starting")
                request = leaps_protection_request(body, require_verified=True)
                estimate = COLLECTOR.estimate_leaps_protection(**request)
                if not estimate["fitsWithinCreditCap"]:
                    raise RequestError(409, "This download exceeds the 9,500-credit safety cap")
                self._send_json(JOBS.start_leaps_protection_backfill(**request), status=202)
                return
            if path == "/api/vault/purge":
                if body.get("confirm") != "DELETE":
                    raise RequestError(400, "Type DELETE to confirm removal of downloaded market data")
                VAULT.purge("marketdata")
                STORE.purge_marketdata_metadata()
                MARKET_DATA.clear_cache()
                ACCURACY.invalidate()
                self._send_json({"status": "deleted", "message": "Downloaded Market Data history was removed."})
                return
            raise RequestError(404, "Not found")
        except RequestError as exc:
            self._send_error(exc.status, str(exc))
        except (TypeError, ValueError) as exc:
            self._send_error(400, str(exc))

    def do_DELETE(self) -> None:
        path = urlsplit(self.path).path
        if not self._require_auth():
            return
        if path.startswith("/api/favorites/"):
            STORE.delete_favorite(path.rsplit("/", 1)[-1])
            self._send_json({"status": "deleted"})
            return
        if path.startswith("/api/strategies/"):
            STORE.delete_strategy(path.rsplit("/", 1)[-1])
            self._send_json({"status": "deleted"})
            return
        if path.startswith("/api/runs/"):
            STORE.delete_run(path.rsplit("/", 1)[-1])
            self._send_json({"status": "deleted"})
            return
        self._send_error(404, "Not found")

    def _require_auth(self) -> bool:
        path = urlsplit(self.path).path
        if path == "/api/health":
            return True
        if PUBLIC_MODE:
            if public_route_allowed(self.command, path):
                return True
            self._send_json({"error": "This owner-only control is unavailable in the public lab"}, status=403)
            return False
        if not AUTH.enabled:
            return True
        if AUTH.valid_cookie_header(self.headers.get("Cookie")):
            return True
        if self.command == "GET" and not path.startswith("/api/"):
            self.send_response(303)
            self.send_header("Location", AUTH.login_redirect(self.path))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            self._send_json({"error": "authentication_required"}, status=401)
        return False

    def _serve_static(self, path: str) -> None:
        relative = unquote(path.removeprefix("/static/"))
        target = (STATIC / relative).resolve()
        if not str(target).startswith(str(STATIC.resolve())):
            self._send_error(403, "Forbidden")
            return
        self._send_file(target)

    def _read_json(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError as exc:
            raise RequestError(400, "Invalid request length") from exc
        if length < 0 or length > MAX_REQUEST_BYTES:
            raise RequestError(413, "Request is too large")
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            payload = json.loads(raw or "{}")
        except json.JSONDecodeError as exc:
            raise RequestError(400, "Request must contain valid JSON") from exc
        if not isinstance(payload, dict):
            raise RequestError(400, "Request must be a JSON object")
        return payload

    def _send_json(self, payload: Any, status: int = 200, headers: dict[str, str] | None = None) -> None:
        data = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: Path) -> None:
        if not path.is_file():
            self._send_error(404, "Not found")
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'")
        self.end_headers()
        self.wfile.write(data)

    def _send_run_json(self, run_id: str) -> None:
        payload = STORE.get_run(run_id)
        if not payload:
            self._send_error(404, "Saved result not found")
            return
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Disposition", f'attachment; filename="strategy-result-{run_id[:8]}.json"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_run_csv(self, run_id: str) -> None:
        payload = STORE.get_run(run_id)
        if not payload:
            self._send_error(404, "Saved result not found")
            return
        output = StringIO()
        fields = ["market_date", "leg", "action", "symbol", "quantity", "price", "cash_flow", "fees", "reason"]
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for trade in payload.get("trades") or []:
            writer.writerow({field: trade.get(field, "") for field in fields})
        data = output.getvalue().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="strategy-trades-{run_id[:8]}.csv"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_error(self, status: int, message: str) -> None:
        self._send_json({"error": message}, status=status)

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{self.address_string()} - {fmt % args}")


def validate_symbol(value: str) -> str:
    symbol = value.strip().upper()
    if not symbol or len(symbol) > 12 or not all(char.isalnum() or char in {".", "-"} for char in symbol):
        raise RequestError(400, "Enter a valid U.S. stock or ETF ticker")
    return symbol


PORTFOLIO_CATALOG = [
    ("SPY", "SPDR S&P 500 ETF Trust", "ETF"), ("QQQ", "Invesco QQQ Trust", "ETF"),
    ("VTI", "Vanguard Total Stock Market ETF", "ETF"), ("VOO", "Vanguard S&P 500 ETF", "ETF"),
    ("IWM", "iShares Russell 2000 ETF", "ETF"), ("DIA", "SPDR Dow Jones Industrial Average ETF", "ETF"),
    ("VEA", "Vanguard FTSE Developed Markets ETF", "ETF"), ("VWO", "Vanguard FTSE Emerging Markets ETF", "ETF"),
    ("BND", "Vanguard Total Bond Market ETF", "ETF"), ("TLT", "iShares 20+ Year Treasury Bond ETF", "ETF"),
    ("GLD", "SPDR Gold Shares", "ETF"), ("SCHD", "Schwab U.S. Dividend Equity ETF", "ETF"),
    ("AAPL", "Apple Inc.", "Stock"), ("MSFT", "Microsoft Corporation", "Stock"),
    ("GOOGL", "Alphabet Inc. Class A", "Stock"), ("AMZN", "Amazon.com Inc.", "Stock"),
    ("NVDA", "NVIDIA Corporation", "Stock"), ("META", "Meta Platforms Inc.", "Stock"),
    ("TSLA", "Tesla Inc.", "Stock"), ("BRK-B", "Berkshire Hathaway Inc. Class B", "Stock"),
    ("JPM", "JPMorgan Chase & Co.", "Stock"), ("COST", "Costco Wholesale Corporation", "Stock"),
]


def search_portfolio_symbols(query: str, provider_name: str) -> list[dict[str, str]]:
    cleaned = query.strip()
    if len(cleaned) < 1:
        return []
    if provider_name == "tiingo":
        return TIINGO.search(cleaned)
    lowered = cleaned.lower()
    return [
        {"symbol": symbol, "name": name, "type": asset_type}
        for symbol, name, asset_type in PORTFOLIO_CATALOG
        if lowered in symbol.lower() or lowered in name.lower()
    ][:8]


def portfolio_backtest_request(payload: dict[str, Any]) -> dict[str, Any]:
    provider = str(payload.get("provider") or "demo").lower()
    if provider == "tiingo":
        provider = "real"
    if provider not in {"demo", "modeled", "real", "onclick"}:
        raise RequestError(400, "Choose free automatic, demo, or an optional real-data source")
    raw_holdings = payload.get("holdings")
    if not isinstance(raw_holdings, list) or not 1 <= len(raw_holdings) <= 18:
        raise RequestError(400, "Choose between one and eighteen share, call, or put rows")
    call_rule = option_rule_request(payload.get("callRule"), "call", 540, 180)
    put_rule = option_rule_request(payload.get("putRule"), "put", 45, 21)
    holdings: list[InstrumentHolding] = []
    option_rules: dict[str, OptionRule] = {}
    seen: set[str] = set()
    for item in raw_holdings:
        if not isinstance(item, dict):
            raise RequestError(400, "Each investment needs a symbol, type, and percentage")
        symbol = validate_symbol(str(item.get("symbol") or ""))
        kind = str(item.get("kind") or "stock").lower()
        if kind not in {"stock", "call", "put", "short_put"}:
            raise RequestError(400, f"Choose shares, a long call, a protective put, or a cash-secured short put for {symbol}")
        key = f"{symbol}:{kind}"
        if key in seen:
            raise RequestError(400, f"{symbol} {kind} appears more than once")
        seen.add(key)
        try:
            weight = float(item.get("weight"))
        except (TypeError, ValueError) as exc:
            raise RequestError(400, f"Enter a valid allocation for {symbol}") from exc
        holdings.append(InstrumentHolding(symbol, kind, weight))  # type: ignore[arg-type]
        if kind != "stock":
            default_rule = call_rule if kind == "call" else put_rule
            option_rules[key] = option_rule_request(
                item.get("optionRule"),
                "put" if kind == "short_put" else kind,
                default_rule.target_dte,
                default_rule.roll_dte,
                default_rule,
            )
    try:
        cash_weight = float(payload.get("cashWeight") or 0)
        initial_capital = float(payload.get("initialCapital") or 100_000)
        start = date.fromisoformat(str(payload.get("startDate") or ""))
        end = date.fromisoformat(str(payload.get("endDate") or ""))
    except (TypeError, ValueError) as exc:
        raise RequestError(400, "Enter valid dates and starting money") from exc
    if PUBLIC_MODE:
        if provider not in {"demo", "modeled"}:
            raise RequestError(403, "This public lab supports demo and free automatic tests only")
        if start >= end:
            raise RequestError(400, "The test end date must be after the start date")
        if (end - start).days > 16 * 366:
            raise RequestError(400, "Public tests are limited to a 15-year history window")
    has_options = any(item.kind != "stock" for item in holdings)
    if provider == "modeled" and not TIINGO.available:
        imported = {item["symbol"] for item in VAULT.list_symbols("user-csv")}
        required = {item.symbol.upper() for item in holdings} | {"SPY", "QQQ"}
        missing = sorted(required - imported)
        if missing:
            raise RequestError(
                409,
                f"Add a free Tiingo token or import owned CSV history for {', '.join(missing)} before running this test.",
            )
    if provider == "real" and not TIINGO.available:
        raise RequestError(409, "Add a free Tiingo API token in Data source settings first")
    if provider == "real" and has_options and not MARKET_DATA.available:
        raise RequestError(409, "Add a Market Data token before testing real calls or puts")
    if provider == "real" and has_options:
        provider_start = MARKET_DATA.history_window_start()
        if provider_start and start < provider_start:
            raise RequestError(
                409,
                f"Real option history under the current plan begins around {provider_start.isoformat()}. "
                "Choose a later start date, use locally retained option history, or run the demo first.",
            )
    if provider == "onclick":
        if any(item.kind == "short_put" for item in holdings):
            raise RequestError(400, "Cash-secured short puts are available in Free automatic and Real historical modes")
        if not TIINGO.available:
            raise RequestError(409, "Add a free Tiingo token so verified beta can price shares and benchmarks")
        if not MARKET_DATA.available:
            raise RequestError(
                409,
                "Add a Market Data token before using verified beta. "
                "Every option contract is selected and priced from its historical chains and quotes.",
            )
        provider_start = MARKET_DATA.history_window_start()
        if provider_start and start < provider_start:
            raise RequestError(
                409,
                f"Verified option history under the current plan begins around {provider_start.isoformat()}. "
                "Choose a later start date or use exact contract history previously retained in the local vault.",
            )
        positive_options = [item for item in holdings if item.kind != "stock" and item.weight > 0]
        if not positive_options:
            raise RequestError(400, "Add at least one call or put with a positive percentage for verified beta")
        if str(payload.get("rebalance") or "quarterly").lower() != "none":
            raise RequestError(
                400,
                "Choose Never — buy and hold for verified independent option sleeves. "
                "The option will still roll using its Replace with days left setting.",
            )
    return {
        "provider": provider,
        "holdings": holdings,
        "cash_weight": cash_weight,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "initial_capital": initial_capital,
        "rebalance": str(payload.get("rebalance") or "quarterly").lower(),
        "call_rule": call_rule,
        "put_rule": put_rule,
        "option_rules": option_rules,
        "option_commission": float(
            payload.get("optionCommission")
            if payload.get("optionCommission") is not None
            else ROBINHOOD_OPTION_FEE_PER_CONTRACT
        ),
    }


def option_rule_request(
    raw: Any,
    side: str,
    target_dte: int,
    roll_dte: int,
    base_rule: OptionRule | None = None,
) -> OptionRule:
    payload = dict(raw) if isinstance(raw, dict) else {}
    base = base_rule or OptionRule(side=side, target_dte=target_dte, roll_dte=roll_dte)  # type: ignore[arg-type]
    try:
        rule = OptionRule(
            side=side,  # type: ignore[arg-type]
            target_dte=int(payload.get("targetDte") or base.target_dte),
            roll_dte=int(payload.get("rollDte") if payload.get("rollDte") is not None else base.roll_dte),
            target_delta=float(payload.get("targetDelta") or base.target_delta),
            fallback_moneyness_pct=float(
                payload.get("fallbackMoneynessPct")
                if payload.get("fallbackMoneynessPct") is not None
                else base.fallback_moneyness_pct
            ),
            expiration_type=str(payload.get("expirationType") or base.expiration_type),
            min_open_interest=int(
                payload.get("minOpenInterest")
                if payload.get("minOpenInterest") is not None
                else base.min_open_interest
            ),
            max_spread_pct=float(
                payload.get("maxSpreadPct")
                if payload.get("maxSpreadPct") is not None
                else base.max_spread_pct
            ),
            strike_mode=str(payload.get("strikeMode") or base.strike_mode),
            strike_value=float(
                payload.get("strikeValue")
                if payload.get("strikeValue") is not None
                else base.strike_value
            ),
        )
        rule.validate()
        return rule
    except (TypeError, ValueError) as exc:
        raise RequestError(400, f"Enter valid {side} expiration and selection settings: {exc}") from exc


def portfolio_status() -> dict[str, Any]:
    status = {
        "tiingo": {
            "configured": TIINGO.available,
            "source": TIINGO_TOKEN_SOURCE,
            "validated": TIINGO.token_validated,
            "canRemove": TIINGO_TOKEN_SOURCE == "local_file",
            "storageMode": "transient",
            "requestsThisRun": TIINGO.requests_this_run,
            "importedSymbols": VAULT.list_symbols("user-csv"),
        },
        "marketdata": {
            "configured": MARKET_DATA.available,
            "source": TOKEN_SOURCE,
            "validated": MARKET_DATA.token_validated,
            "canRemove": TOKEN_SOURCE == "local_file",
            "historyYears": MARKET_DATA.history_years,
            "windowStart": MARKET_DATA.history_window_start().isoformat() if MARKET_DATA.history_window_start() else None,
            "quota": STORE.quota_status(),
        },
        "onclick": {
            "available": True,
            "experimental": True,
            "verifiedStart": MARKET_DATA.history_window_start().isoformat() if MARKET_DATA.history_window_start() else None,
            "end": (datetime.now(EASTERN).date() - timedelta(days=1)).isoformat(),
            "requiresToken": False,
            "requiresMarketDataToken": True,
            "pricingSource": "marketdata",
            "selectionSource": "marketdata",
            "stockSource": "tiingo",
        },
        "modeled": {
            "available": TIINGO.available or bool(VAULT.list_symbols("user-csv")),
            "requiresTiingoToken": not bool(VAULT.list_symbols("user-csv")),
            "requiresMarketDataToken": False,
            "stockSource": "transient-tiingo-or-user-csv",
            "optionSource": "exact-first-calibrated-american-model",
            "historyLimit": "underlying-history",
            "modelVersion": "calibrated-american-v3",
        },
        "pricingCalibration": ACCURACY.status(),
        "referenceData": REFERENCE_DATA.status(),
        "demoAvailable": True,
        "publicMode": PUBLIC_MODE,
        "publicBacktestsPerHour": PUBLIC_BACKTESTS_PER_HOUR if PUBLIC_MODE else None,
        "dataSourceNote": (
            "Free automatic uses real share history transiently from Tiingo, or a CSV you own. Raw Tiingo rows are not "
            "saved; saved runs keep summary calculations only. Options are clearly labeled estimates backed by historical "
            "Cboe volatility, U.S. Treasury rates, and locally retained SPY/QQQ quote calibration. Market Data remains "
            "optional for exact recent option quotes and the strict accuracy evidence gate."
        ),
    }
    if PUBLIC_MODE:
        status["tiingo"] = {
            "configured": TIINGO.available,
            "source": "server" if TIINGO.available else "none",
            "validated": TIINGO.token_validated,
            "canRemove": False,
            "storageMode": "transient",
            "requestsThisRun": TIINGO.requests_this_run,
            "importedSymbols": [],
        }
        status["marketdata"] = {
            "configured": False,
            "source": "unavailable",
            "validated": False,
            "canRemove": False,
            "historyYears": None,
            "windowStart": None,
            "quota": {},
        }
        status["onclick"] = {
            "available": False,
            "experimental": True,
            "requiresToken": False,
            "requiresMarketDataToken": True,
        }
        status["pricingCalibration"] = {}
        status["dataSourceNote"] = (
            "Public mode offers built-in demo data and, when the server data connection is available, transient real share "
            "history with locally modeled options. Visitors cannot change credentials, download licensed records, or run "
            "provider-collection jobs."
        )
    return status


def import_stock_csv(payload: dict[str, Any]) -> dict[str, Any]:
    symbol = validate_symbol(str(payload.get("symbol") or ""))
    raw = str(payload.get("csv") or "")
    if not raw.strip():
        raise RequestError(400, "Choose a CSV file that contains daily prices")
    reader = csv.DictReader(StringIO(raw.lstrip("\ufeff")))
    if not reader.fieldnames:
        raise RequestError(400, "The CSV needs a header row")
    normalized = {_normalize_csv_header(name): name for name in reader.fieldnames if name}
    date_key = normalized.get("date") or normalized.get("timestamp")
    close_key = normalized.get("close")
    adjusted_key = normalized.get("adjclose") or normalized.get("adjustedclose")
    if not date_key or not (close_key or adjusted_key):
        raise RequestError(400, "The CSV must include Date and Close (or Adjusted Close) columns")

    bars: list[StockBar] = []
    seen: set[str] = set()
    for line_number, row in enumerate(reader, start=2):
        raw_date = str(row.get(date_key) or "").strip()
        if not raw_date:
            continue
        market_date = _parse_csv_date(raw_date, line_number)
        if market_date in seen:
            raise RequestError(400, f"The CSV contains the date {market_date} more than once")
        seen.add(market_date)
        try:
            close = float(row.get(close_key) or row.get(adjusted_key) or 0)
            adjusted = float(row.get(adjusted_key) or close)
            opening = float(row.get(normalized.get("open", "")) or close)
            high = float(row.get(normalized.get("high", "")) or close)
            low = float(row.get(normalized.get("low", "")) or close)
            volume = float(str(row.get(normalized.get("volume", "")) or "0").replace(",", ""))
            dividend = float(row.get(normalized.get("dividends", "")) or row.get(normalized.get("dividend", "")) or 0)
            split = float(row.get(normalized.get("stocksplits", "")) or row.get(normalized.get("splitfactor", "")) or 1)
        except (TypeError, ValueError) as exc:
            raise RequestError(400, f"Line {line_number} contains a price, dividend, split, or volume that is not a number") from exc
        if min(close, adjusted, opening, high, low) <= 0 or split <= 0:
            raise RequestError(400, f"Line {line_number} contains a non-positive price or split factor")
        bars.append(StockBar(
            market_date=market_date,
            open=opening,
            high=high,
            low=low,
            close=close,
            adjusted_close=adjusted,
            volume=volume,
            split_detected=abs(split - 1) > 1e-9,
            dividend_cash=dividend,
            split_factor=split,
            source_timestamp=raw_date,
        ))
    if len(bars) < 2:
        raise RequestError(400, "The CSV needs at least two valid daily rows")
    bars.sort(key=lambda item: item.market_date)
    VAULT.purge_symbol("user-csv", symbol)
    VAULT.save_stock_bars("user-csv", symbol, bars)
    expected = {
        day.isoformat()
        for day in trading_dates(date.fromisoformat(bars[0].market_date), date.fromisoformat(bars[-1].market_date))
    }
    missing = sorted(expected - {bar.market_date for bar in bars})
    return {
        "status": "imported",
        "symbol": symbol,
        "startDate": bars[0].market_date,
        "endDate": bars[-1].market_date,
        "observations": len(bars),
        "missingSessions": len(missing),
        "message": (
            f"Imported {len(bars):,} {symbol} rows."
            + (f" {len(missing):,} expected trading sessions are missing, so a test needing those dates will stop or use Tiingo if connected." if missing else " The covered trading sessions are continuous.")
        ),
    }


def _normalize_csv_header(value: str) -> str:
    return "".join(character for character in value.strip().lower() if character.isalnum())


def _parse_csv_date(value: str, line_number: int) -> str:
    candidate = value[:10]
    try:
        return date.fromisoformat(candidate).isoformat()
    except ValueError:
        for pattern in ("%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d"):
            try:
                return datetime.strptime(value, pattern).date().isoformat()
            except ValueError:
                continue
    raise RequestError(400, f"Line {line_number} has an unreadable date: {value}")


def configure_tiingo_token(payload: dict[str, Any]) -> dict[str, Any]:
    global TIINGO_TOKEN_SOURCE
    if bool(payload.get("clear")):
        TIINGO_TOKEN_STORE.delete()
        if TIINGO_ENVIRONMENT_TOKEN:
            TIINGO.set_token(TIINGO_ENVIRONMENT_TOKEN)
            TIINGO_TOKEN_SOURCE = "environment"
            message = "The locally saved token was removed; the terminal-provided Tiingo token remains active."
        else:
            TIINGO.set_token("")
            TIINGO_TOKEN_SOURCE = "none"
            message = "The locally saved Tiingo token was removed from this computer."
        return {"configured": TIINGO.available, "source": TIINGO_TOKEN_SOURCE, "message": message}
    token = str(payload.get("token") or "")
    TIINGO_TOKEN_STORE.save(token)
    TIINGO.set_token(token)
    TIINGO_TOKEN_SOURCE = "local_file"
    return {"configured": True, "source": TIINGO_TOKEN_SOURCE, "message": "Tiingo token saved only on this computer."}


def subtract_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year - years)
    except ValueError:
        return value.replace(year=value.year - years, day=28)


def historical_backfill_request(payload: dict[str, Any]) -> dict[str, str]:
    symbol = validate_symbol(str(payload.get("symbol") or ""))
    profile = str(payload.get("captureProfile") or "used")
    if profile not in CAPTURE_PROFILE_CREDITS:
        raise RequestError(400, "Capture profile must be used, balanced, or full")
    try:
        years = int(payload.get("years") or 5)
    except (TypeError, ValueError) as exc:
        raise RequestError(400, "History length must be one or five years") from exc
    if years not in {1, 5}:
        raise RequestError(400, "This version supports one-year or five-year backfills")
    available_years = MARKET_DATA.history_years
    if available_years is not None and years > available_years:
        raise RequestError(
            409,
            f"The detected Market Data allowance supports {available_years} year{'s' if available_years != 1 else ''} of history, not {years}. "
            "Verify the token has made a successful request or use a plan with a longer history window.",
        )
    provider_today = date.today()
    provider_today = datetime.now(EASTERN).date()
    end = provider_today - timedelta(days=1)
    start = subtract_years(provider_today, years)
    return {"symbol": symbol, "start": start.isoformat(), "end": end.isoformat(), "profile": profile}


def leaps_protection_request(payload: dict[str, Any], require_verified: bool) -> dict[str, Any]:
    if not MARKET_DATA.available:
        raise RequestError(409, "Save a Market Data token before downloading historical data")
    try:
        call_dte = int(payload.get("callDte") or 540)
    except (TypeError, ValueError) as exc:
        raise RequestError(400, "Long-call target must be a whole number of days") from exc
    if not 365 <= call_dte <= 730:
        raise RequestError(400, "Long-call target must be between 365 and 730 days")
    if require_verified and MARKET_DATA.history_years is not None and MARKET_DATA.history_years < 5:
        raise RequestError(409, "Verify five-year access before starting this download")
    current = datetime.now(EASTERN).date()
    end = current - timedelta(days=1)
    start = subtract_years(current, 5)
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "call_dte": call_dte,
        "put_dte": 45,
        "strike_limit": 40,
    }


def favorite_payloads() -> list[dict[str, Any]]:
    output = []
    for favorite in STORE.list_favorites():
        favorite = dict(favorite)
        coverage = VAULT.coverage("marketdata", favorite["symbol"])
        collection = STORE.collection_summary(favorite["symbol"])
        favorite["coverage"] = coverage
        favorite["collection"] = collection
        favorite["coverageManifest"] = coverage_manifest(coverage, collection)
        output.append(favorite)
    return output


def coverage_manifest(coverage: dict[str, Any], collection: dict[str, Any]) -> dict[str, Any]:
    detected_start = MARKET_DATA.history_window_start()
    window_start = detected_start.isoformat() if detected_start else None
    attempted = int(collection.get("attempted") or 0)
    complete = int(collection.get("complete") or 0)
    has_stock = int(coverage.get("stockDays") or 0) > 0
    has_options = int(coverage.get("optionDays") or 0) > 0
    option_start = coverage.get("optionStart")
    if not has_stock and not has_options:
        state = "provider_accessible_missing" if MARKET_DATA.available else "missing"
        message = (
            "No history is saved yet; dates inside the provider window can be collected."
            if MARKET_DATA.available
            else "No history is saved, and collection needs a Market Data token."
        )
    elif attempted > complete or not has_stock or not has_options:
        state = "partial"
        message = "Some sessions or option chains are missing, so only strategies covered by the stored contracts can run completely."
    elif option_start and window_start and option_start < window_start:
        state = "locally_retained"
        message = "This includes locally retained option history older than the provider's currently detected window."
    else:
        state = "complete_local"
        message = "Collected sessions are complete locally; dates not shown may still require provider retrieval."
    permanently_unavailable_before = min(option_start, window_start) if option_start and window_start else window_start
    return {
        "state": state,
        "message": message,
        "providerWindowStart": window_start,
        "localStart": option_start or coverage.get("stockStart"),
        "localEnd": coverage.get("optionEnd") or coverage.get("stockEnd"),
        "permanentlyUnavailableBefore": permanently_unavailable_before,
    }


def data_status() -> dict[str, Any]:
    history_years = MARKET_DATA.history_years
    history_start = MARKET_DATA.history_window_start()
    history_verification = MARKET_DATA.history_verification
    if history_verification.get("status") == "verified":
        history_label = "Five-year access verified"
    elif history_verification.get("status") == "one_year_only":
        history_label = "One-year trial/free access"
    else:
        history_label = "Five-year access not verified"
    return {
        "realDataAvailable": MARKET_DATA.available,
        "marketDataCredential": {
            "configured": MARKET_DATA.available,
            "source": TOKEN_SOURCE,
            "validated": MARKET_DATA.token_validated,
            "canRemove": TOKEN_SOURCE == "local_file",
        },
        "fixtureAvailable": True,
        "authEnabled": AUTH.enabled,
        "quota": STORE.quota_status(),
        "creditReserve": COLLECTOR.reserve_credits,
        "estimatedCollectionCredits": STORE.estimated_collection_credits(),
        "vaultBytes": VAULT.disk_bytes(),
        "favorites": favorite_payloads(),
        "collector": COLLECTOR.last_result,
        "historyAccess": {
            "years": history_years,
            "unlimited": history_years is None,
            "label": "Unlimited historical access" if history_years is None else history_label,
            "windowStart": history_start.isoformat() if history_start else None,
            "detectedFromDailyLimit": False,
            "verified": bool(history_verification.get("verified")),
            "status": history_verification.get("status") or "not_checked",
            "checkedAt": history_verification.get("checkedAt"),
            "message": history_verification.get("message"),
        },
        "profiles": {
            "balanced": {"label": "Balanced Monthly", "estimatedCredits": 7, "coverage": "Monthly expirations through 180 days"},
            "full": {"label": "Full", "estimatedCredits": 30, "coverage": "Weekly and monthly expirations through 365 days"},
            "used": {"label": "Only Contracts Used", "estimatedCredits": 3, "coverage": "Nearest monthly expiration around 45 days"},
        },
    }


def configure_marketdata_token(payload: dict[str, Any]) -> dict[str, Any]:
    global TOKEN_SOURCE
    if bool(payload.get("clear")):
        MARKET_DATA.clear_history_verification()
        TOKEN_STORE.delete()
        if ENVIRONMENT_TOKEN:
            MARKET_DATA.set_token(ENVIRONMENT_TOKEN)
            TOKEN_SOURCE = "environment"
            message = "The locally saved token was removed. The environment-provided token remains active."
        else:
            MARKET_DATA.set_token("")
            TOKEN_SOURCE = "none"
            message = "The locally saved Market Data token was removed from this computer."
        return {"configured": MARKET_DATA.available, "source": TOKEN_SOURCE, "message": message}

    token = str(payload.get("token") or "")
    TOKEN_STORE.save(token)
    MARKET_DATA.clear_history_verification()
    MARKET_DATA.set_token(token)
    TOKEN_SOURCE = "local_file"
    return {
        "configured": True,
        "source": TOKEN_SOURCE,
        "message": "Token saved only on this computer. It will be verified when the first real-data request is made.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Portfolio Strategy Lab")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8790, type=int)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), StrategyLabHandler)
    SCHEDULER.start()
    print(f"Portfolio Strategy Lab running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Portfolio Strategy Lab")
    finally:
        SCHEDULER.stop()
        JOBS.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
