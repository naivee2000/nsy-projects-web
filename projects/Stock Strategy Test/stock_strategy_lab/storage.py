from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import threading
from typing import Any, Iterable, Iterator
import uuid
import zlib

try:
    import duckdb
except ImportError:  # pragma: no cover - surfaced with an actionable runtime error
    duckdb = None  # type: ignore[assignment]

from .models import OptionQuote, StockBar


CAPTURE_PROFILE_CREDITS = {"balanced": 7, "full": 30, "used": 3}


class MarketVault:
    """Compressed columnar history used by both collection and backtests."""

    def __init__(self, data_dir: Path):
        if duckdb is None:
            raise RuntimeError("DuckDB is required. Install the packages in requirements.txt.")
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.data_dir / "market_history.duckdb"
        self._lock = threading.RLock()
        self._initialize()

    @contextmanager
    def _connection(self) -> Iterator[Any]:
        with self._lock:
            connection = duckdb.connect(str(self.path))
            try:
                yield connection
            finally:
                connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS stock_bars (
                    provider VARCHAR NOT NULL,
                    symbol VARCHAR NOT NULL,
                    market_date VARCHAR NOT NULL,
                    open DOUBLE NOT NULL,
                    high DOUBLE NOT NULL,
                    low DOUBLE NOT NULL,
                    close DOUBLE NOT NULL,
                    adjusted_close DOUBLE NOT NULL,
                    volume DOUBLE NOT NULL,
                    split_detected BOOLEAN NOT NULL DEFAULT FALSE,
                    dividend_cash DOUBLE NOT NULL DEFAULT 0,
                    split_factor DOUBLE NOT NULL DEFAULT 1,
                    source_timestamp VARCHAR NOT NULL DEFAULT '',
                    PRIMARY KEY (provider, symbol, market_date)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS option_quotes (
                    provider VARCHAR NOT NULL,
                    underlying VARCHAR NOT NULL,
                    market_date VARCHAR NOT NULL,
                    option_symbol VARCHAR NOT NULL,
                    expiration VARCHAR NOT NULL,
                    side VARCHAR NOT NULL,
                    strike DOUBLE NOT NULL,
                    bid DOUBLE NOT NULL,
                    ask DOUBLE NOT NULL,
                    last DOUBLE NOT NULL,
                    delta DOUBLE,
                    gamma DOUBLE,
                    theta DOUBLE,
                    vega DOUBLE,
                    iv DOUBLE,
                    open_interest INTEGER NOT NULL,
                    volume INTEGER NOT NULL,
                    underlying_price DOUBLE NOT NULL,
                    is_monthly BOOLEAN NOT NULL,
                    is_nonstandard BOOLEAN NOT NULL,
                    contract_multiplier DOUBLE NOT NULL DEFAULT 100,
                    bid_size INTEGER NOT NULL DEFAULT 0,
                    ask_size INTEGER NOT NULL DEFAULT 0,
                    source_timestamp VARCHAR NOT NULL DEFAULT '',
                    pricing_source VARCHAR NOT NULL DEFAULT 'exact',
                    PRIMARY KEY (provider, option_symbol, market_date)
                )
                """
            )
            stock_columns = {row[1] for row in connection.execute("PRAGMA table_info('stock_bars')").fetchall()}
            # DuckDB cannot add constrained columns to an existing table. Add
            # nullable migration columns, populate them, and keep defaults in
            # the application insert path.
            for name, definition, fallback in (
                ("dividend_cash", "DOUBLE", "0"),
                ("split_factor", "DOUBLE", "1"),
                ("source_timestamp", "VARCHAR", "''"),
            ):
                if name not in stock_columns:
                    connection.execute(f"ALTER TABLE stock_bars ADD COLUMN {name} {definition}")
                connection.execute(f"UPDATE stock_bars SET {name} = {fallback} WHERE {name} IS NULL")
            option_columns = {row[1] for row in connection.execute("PRAGMA table_info('option_quotes')").fetchall()}
            for name, definition, fallback in (
                ("contract_multiplier", "DOUBLE", "100"),
                ("bid_size", "INTEGER", "0"),
                ("ask_size", "INTEGER", "0"),
                ("source_timestamp", "VARCHAR", "''"),
                ("pricing_source", "VARCHAR", "'exact'"),
            ):
                if name not in option_columns:
                    connection.execute(f"ALTER TABLE option_quotes ADD COLUMN {name} {definition}")
                connection.execute(f"UPDATE option_quotes SET {name} = {fallback} WHERE {name} IS NULL")
            # Tiingo Starter data is transient-only under the current provider
            # terms. Remove rows written by older versions; user-imported CSV
            # and exact-data providers remain untouched.
            connection.execute("DELETE FROM stock_bars WHERE provider = 'tiingo'")
            connection.execute("CHECKPOINT")
            connection.execute("CREATE INDEX IF NOT EXISTS stock_lookup ON stock_bars(provider, symbol, market_date)")
            connection.execute(
                "CREATE INDEX IF NOT EXISTS option_chain_lookup ON option_quotes(provider, underlying, market_date, expiration)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS option_series_lookup ON option_quotes(provider, option_symbol, market_date)"
            )

    def save_stock_bars(self, provider: str, symbol: str, bars: Iterable[StockBar]) -> int:
        rows = [
            (
                provider,
                symbol.upper(),
                bar.market_date,
                bar.open,
                bar.high,
                bar.low,
                bar.close,
                bar.adjusted_close,
                bar.volume,
                bar.split_detected,
                bar.dividend_cash,
                bar.split_factor,
                bar.source_timestamp,
            )
            for bar in bars
        ]
        if not rows:
            return 0
        with self._connection() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO stock_bars(
                    provider, symbol, market_date, open, high, low, close,
                    adjusted_close, volume, split_detected, dividend_cash,
                    split_factor, source_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def stock_bars(self, provider: str, symbol: str, start: str, end: str) -> list[StockBar]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT market_date, open, high, low, close, adjusted_close, volume,
                       split_detected, dividend_cash, split_factor, source_timestamp
                FROM stock_bars
                WHERE provider = ? AND symbol = ? AND market_date BETWEEN ? AND ?
                ORDER BY market_date
                """,
                [provider, symbol.upper(), start, end],
            ).fetchall()
        return [StockBar(*row) for row in rows]

    def save_option_quotes(self, provider: str, quotes: Iterable[OptionQuote]) -> int:
        rows = [
            (
                provider,
                quote.underlying.upper(),
                quote.market_date,
                quote.option_symbol,
                quote.expiration,
                quote.side,
                quote.strike,
                quote.bid,
                quote.ask,
                quote.last,
                quote.delta,
                quote.gamma,
                quote.theta,
                quote.vega,
                quote.iv,
                quote.open_interest,
                quote.volume,
                quote.underlying_price,
                quote.is_monthly,
                quote.is_nonstandard,
                quote.contract_multiplier,
                quote.bid_size,
                quote.ask_size,
                quote.source_timestamp,
                quote.pricing_source,
            )
            for quote in quotes
        ]
        if not rows:
            return 0
        with self._connection() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO option_quotes(
                    provider, underlying, market_date, option_symbol, expiration,
                    side, strike, bid, ask, last, delta, gamma, theta, vega, iv,
                    open_interest, volume, underlying_price, is_monthly,
                    is_nonstandard, contract_multiplier, bid_size, ask_size,
                    source_timestamp, pricing_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def option_chain(
        self,
        provider: str,
        underlying: str,
        market_date: str,
        side: str | None = None,
        expiration: str | None = None,
    ) -> list[OptionQuote]:
        conditions = ["provider = ?", "underlying = ?", "market_date = ?"]
        params: list[Any] = [provider, underlying.upper(), market_date]
        if side:
            conditions.append("side = ?")
            params.append(side)
        if expiration:
            conditions.append("expiration = ?")
            params.append(expiration)
        with self._connection() as connection:
            rows = connection.execute(
                f"""
                SELECT market_date, option_symbol, underlying, expiration, side, strike,
                       bid, ask, last, delta, gamma, theta, vega, iv, open_interest,
                       volume, underlying_price, is_monthly, is_nonstandard,
                       contract_multiplier, bid_size, ask_size, source_timestamp,
                       pricing_source
                FROM option_quotes
                WHERE {' AND '.join(conditions)}
                ORDER BY expiration, strike
                """,
                params,
            ).fetchall()
        return [OptionQuote(*row) for row in rows]

    def option_series(self, provider: str, option_symbol: str, start: str, end: str) -> list[OptionQuote]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT market_date, option_symbol, underlying, expiration, side, strike,
                       bid, ask, last, delta, gamma, theta, vega, iv, open_interest,
                       volume, underlying_price, is_monthly, is_nonstandard,
                       contract_multiplier, bid_size, ask_size, source_timestamp,
                       pricing_source
                FROM option_quotes
                WHERE provider = ? AND option_symbol = ? AND market_date BETWEEN ? AND ?
                ORDER BY market_date
                """,
                [provider, option_symbol, start, end],
            ).fetchall()
        return [OptionQuote(*row) for row in rows]

    def calibration_quotes(
        self,
        symbols: Iterable[str],
        end: str,
        start: str | None = None,
        provider: str = "marketdata",
    ) -> list[OptionQuote]:
        normalized = sorted({item.upper() for item in symbols})
        if not normalized:
            return []
        placeholders = ",".join("?" for _ in normalized)
        conditions = ["provider = ?", f"underlying IN ({placeholders})", "market_date <= ?"]
        params: list[Any] = [provider, *normalized, end]
        if start:
            conditions.append("market_date >= ?")
            params.append(start)
        with self._connection() as connection:
            rows = connection.execute(
                f"""
                SELECT market_date, option_symbol, underlying, expiration, side, strike,
                       bid, ask, last, delta, gamma, theta, vega, iv, open_interest,
                       volume, underlying_price, is_monthly, is_nonstandard,
                       contract_multiplier, bid_size, ask_size, source_timestamp,
                       pricing_source
                FROM option_quotes
                WHERE {' AND '.join(conditions)}
                ORDER BY market_date, underlying, expiration, side, strike
                """,
                params,
            ).fetchall()
        return [OptionQuote(*row) for row in rows]

    def coverage(self, provider: str, symbol: str) -> dict[str, Any]:
        with self._connection() as connection:
            stock = connection.execute(
                """
                SELECT MIN(market_date), MAX(market_date), COUNT(*)
                FROM stock_bars WHERE provider = ? AND symbol = ?
                """,
                [provider, symbol.upper()],
            ).fetchone()
            options = connection.execute(
                """
                SELECT MIN(market_date), MAX(market_date), COUNT(*), COUNT(DISTINCT market_date)
                FROM option_quotes WHERE provider = ? AND underlying = ?
                """,
                [provider, symbol.upper()],
            ).fetchone()
        return {
            "stockStart": stock[0] if stock else None,
            "stockEnd": stock[1] if stock else None,
            "stockDays": int(stock[2] or 0) if stock else 0,
            "optionStart": options[0] if options else None,
            "optionEnd": options[1] if options else None,
            "optionContracts": int(options[2] or 0) if options else 0,
            "optionDays": int(options[3] or 0) if options else 0,
        }

    def disk_bytes(self) -> int:
        return self.path.stat().st_size if self.path.exists() else 0

    def list_symbols(self, provider: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT symbol, MIN(market_date), MAX(market_date), COUNT(*)
                FROM stock_bars WHERE provider = ?
                GROUP BY symbol ORDER BY symbol
                """,
                [provider],
            ).fetchall()
        return [
            {"symbol": row[0], "startDate": row[1], "endDate": row[2], "observations": int(row[3])}
            for row in rows
        ]

    def purge(self, provider: str = "marketdata") -> None:
        with self._connection() as connection:
            connection.execute("DELETE FROM option_quotes WHERE provider = ?", [provider])
            connection.execute("DELETE FROM stock_bars WHERE provider = ?", [provider])
            connection.execute("CHECKPOINT")

    def purge_symbol(self, provider: str, symbol: str) -> None:
        with self._connection() as connection:
            connection.execute(
                "DELETE FROM option_quotes WHERE provider = ? AND underlying = ?",
                [provider, symbol.upper()],
            )
            connection.execute(
                "DELETE FROM stock_bars WHERE provider = ? AND symbol = ?",
                [provider, symbol.upper()],
            )


class AppStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.data_dir / "strategy_lab.sqlite3"
        self._lock = threading.RLock()
        self._initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            connection = sqlite3.connect(self.path, timeout=30)
            connection.row_factory = sqlite3.Row
            try:
                yield connection
                connection.commit()
            finally:
                connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS favorites (
                    symbol TEXT PRIMARY KEY,
                    capture_profile TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    priority INTEGER NOT NULL DEFAULT 100,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS strategies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload BLOB NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    provider TEXT NOT NULL DEFAULT '',
                    mode TEXT NOT NULL DEFAULT '',
                    error TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT
                );
                CREATE TABLE IF NOT EXISTS quota_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    occurred_at TEXT NOT NULL,
                    consumed INTEGER NOT NULL,
                    remaining INTEGER,
                    limit_value INTEGER,
                    reset_at INTEGER,
                    endpoint TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS collection_manifest (
                    symbol TEXT NOT NULL,
                    market_date TEXT NOT NULL,
                    capture_profile TEXT NOT NULL,
                    status TEXT NOT NULL,
                    contract_count INTEGER NOT NULL DEFAULT 0,
                    credits INTEGER NOT NULL DEFAULT 0,
                    error TEXT NOT NULL DEFAULT '',
                    checksum TEXT NOT NULL DEFAULT '',
                    collected_at TEXT NOT NULL,
                    PRIMARY KEY (symbol, market_date, capture_profile)
                );
                CREATE TABLE IF NOT EXISTS provider_fetches (
                    cache_key TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    fetched_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            columns = {row[1] for row in connection.execute("PRAGMA table_info(collection_manifest)").fetchall()}
            if "checksum" not in columns:
                connection.execute("ALTER TABLE collection_manifest ADD COLUMN checksum TEXT NOT NULL DEFAULT ''")
            connection.execute("DELETE FROM provider_fetches WHERE provider = 'tiingo'")
            self._sanitize_legacy_free_runs(connection)

    @staticmethod
    def _sanitize_legacy_free_runs(connection: sqlite3.Connection) -> None:
        rows = connection.execute("SELECT id, payload FROM runs").fetchall()
        for row in rows:
            try:
                payload = json.loads(zlib.decompress(row["payload"]).decode("utf-8"))
            except (KeyError, TypeError, ValueError, zlib.error, json.JSONDecodeError):
                continue
            provider = str(payload.get("provider") or "")
            if provider not in {"free-modeled", "tiingo"} or "timeline" not in payload:
                continue
            payload.pop("timeline", None)
            payload["summaryOnly"] = True
            payload["summaryNotice"] = (
                "Daily provider-derived graph points are not retained under the free data license. Rerun to rebuild the chart."
            )
            compressed = zlib.compress(json.dumps(payload, separators=(",", ":")).encode("utf-8"), 6)
            connection.execute("UPDATE runs SET payload = ? WHERE id = ?", [compressed, row["id"]])

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def list_favorites(self) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT symbol, capture_profile, active, priority, created_at, updated_at FROM favorites ORDER BY priority, symbol"
            ).fetchall()
        return [
            {
                "symbol": row["symbol"],
                "captureProfile": row["capture_profile"],
                "active": bool(row["active"]),
                "priority": row["priority"],
                "estimatedDailyCredits": CAPTURE_PROFILE_CREDITS.get(row["capture_profile"], 7),
                "createdAt": row["created_at"],
                "updatedAt": row["updated_at"],
            }
            for row in rows
        ]

    def save_favorite(self, symbol: str, profile: str = "balanced", active: bool = True) -> dict[str, Any]:
        symbol = symbol.strip().upper()
        if profile not in CAPTURE_PROFILE_CREDITS:
            raise ValueError("Capture profile must be balanced, full, or used")
        now = self._now()
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO favorites(symbol, capture_profile, active, priority, created_at, updated_at)
                VALUES (?, ?, ?, 100, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET
                    capture_profile = excluded.capture_profile,
                    active = excluded.active,
                    updated_at = excluded.updated_at
                """,
                [symbol, profile, int(active), now, now],
            )
        return next(item for item in self.list_favorites() if item["symbol"] == symbol)

    def delete_favorite(self, symbol: str) -> None:
        with self._connection() as connection:
            connection.execute("DELETE FROM favorites WHERE symbol = ?", [symbol.upper()])

    def estimated_collection_credits(self) -> int:
        return sum(item["estimatedDailyCredits"] for item in self.list_favorites() if item["active"])

    def save_strategy(self, name: str, payload: dict[str, Any], strategy_id: str | None = None) -> str:
        strategy_id = strategy_id or uuid.uuid4().hex
        now = self._now()
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO strategies(id, name, payload, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name = excluded.name, payload = excluded.payload, updated_at = excluded.updated_at
                """,
                [strategy_id, name, json.dumps(payload, separators=(",", ":")), now, now],
            )
        return strategy_id

    def list_strategies(self) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute("SELECT * FROM strategies ORDER BY updated_at DESC").fetchall()
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "strategy": json.loads(row["payload"]),
                "createdAt": row["created_at"],
                "updatedAt": row["updated_at"],
            }
            for row in rows
        ]

    def delete_strategy(self, strategy_id: str) -> None:
        with self._connection() as connection:
            connection.execute("DELETE FROM strategies WHERE id = ?", [strategy_id])

    def save_run(self, run_id: str, name: str, ticker: str, status: str, payload: dict[str, Any]) -> None:
        stored_payload = self.summary_safe_result(payload)
        compressed = zlib.compress(json.dumps(stored_payload, separators=(",", ":")).encode("utf-8"), 6)
        with self._connection() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO runs(id, name, ticker, status, payload, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                [run_id, name, ticker, status, compressed, self._now()],
            )

    @staticmethod
    def summary_safe_result(payload: dict[str, Any]) -> dict[str, Any]:
        if str(payload.get("provider") or "") not in {"free-modeled", "tiingo"}:
            return payload
        sanitized = dict(payload)
        sanitized.pop("timeline", None)
        sanitized["summaryOnly"] = True
        sanitized["summaryNotice"] = (
            "Daily provider-derived graph points are not retained under the free data license. Rerun to rebuild the chart."
        )
        return sanitized

    def list_runs(self) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT id, name, ticker, status, created_at, length(payload) AS bytes FROM runs ORDER BY created_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute("SELECT payload FROM runs WHERE id = ?", [run_id]).fetchone()
        if not row:
            return None
        return json.loads(zlib.decompress(row["payload"]).decode("utf-8"))

    def delete_run(self, run_id: str) -> None:
        with self._connection() as connection:
            connection.execute("DELETE FROM runs WHERE id = ?", [run_id])
            connection.execute("DELETE FROM jobs WHERE id = ?", [run_id])

    def save_job(self, job: dict[str, Any]) -> None:
        now = self._now()
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO jobs(
                    id, kind, status, stage, provider, mode, error,
                    created_at, updated_at, started_at, finished_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    stage = excluded.stage,
                    provider = excluded.provider,
                    mode = excluded.mode,
                    error = excluded.error,
                    updated_at = excluded.updated_at,
                    started_at = excluded.started_at,
                    finished_at = excluded.finished_at
                """,
                [
                    job["id"],
                    job.get("kind", "backtest"),
                    job.get("status", "queued"),
                    job.get("stage", "Waiting to start"),
                    job.get("provider", ""),
                    job.get("mode", ""),
                    job.get("error", ""),
                    job.get("createdAt", now),
                    now,
                    job.get("startedAt"),
                    job.get("finishedAt"),
                ],
            )

    @staticmethod
    def _job_payload(row: sqlite3.Row) -> dict[str, Any]:
        payload = {
            "id": row["id"],
            "kind": row["kind"],
            "status": row["status"],
            "stage": row["stage"],
            "provider": row["provider"],
            "mode": row["mode"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
        }
        for column, key in (("error", "error"), ("started_at", "startedAt"), ("finished_at", "finishedAt")):
            if row[column]:
                payload[key] = row[column]
        return payload

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", [job_id]).fetchone()
        return self._job_payload(row) if row else None

    def list_jobs(self, kind: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        with self._connection() as connection:
            if kind:
                rows = connection.execute(
                    "SELECT * FROM jobs WHERE kind = ? ORDER BY created_at DESC LIMIT ?",
                    [kind, limit],
                ).fetchall()
            else:
                rows = connection.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", [limit]).fetchall()
        return [self._job_payload(row) for row in rows]

    def fail_incomplete_jobs(self) -> int:
        now = self._now()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE jobs
                SET status = 'failed',
                    stage = 'Stopped before completion',
                    error = 'The local app stopped before this job completed. Start the test again.',
                    updated_at = ?,
                    finished_at = ?
                WHERE status IN ('queued', 'running')
                """,
                [now, now],
            )
        return int(cursor.rowcount)

    def record_quota(self, endpoint: str, consumed: int, remaining: int | None, limit_value: int | None, reset_at: int | None) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO quota_events(occurred_at, consumed, remaining, limit_value, reset_at, endpoint)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [self._now(), consumed, remaining, limit_value, reset_at, endpoint],
            )

    def quota_status(self) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM quota_events ORDER BY id DESC LIMIT 1").fetchone()
        if not row:
            return {"known": False, "limit": 100, "remaining": None, "consumed": None, "resetAt": None}
        return {
            "known": True,
            "limit": row["limit_value"],
            "remaining": row["remaining"],
            "consumed": row["consumed"],
            "resetAt": row["reset_at"],
            "updatedAt": row["occurred_at"],
        }

    def save_setting(self, key: str, value: dict[str, Any]) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO app_settings(key, value, updated_at) VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                [key, json.dumps(value, separators=(",", ":")), self._now()],
            )

    def get_setting(self, key: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute("SELECT value FROM app_settings WHERE key = ?", [key]).fetchone()
        if not row:
            return None
        try:
            value = json.loads(row["value"])
        except (TypeError, json.JSONDecodeError):
            return None
        return value if isinstance(value, dict) else None

    def delete_setting(self, key: str) -> None:
        with self._connection() as connection:
            connection.execute("DELETE FROM app_settings WHERE key = ?", [key])

    def mark_collection(
        self,
        symbol: str,
        market_date: str,
        profile: str,
        status: str,
        contract_count: int = 0,
        credits: int = 0,
        error: str = "",
        checksum: str = "",
    ) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO collection_manifest(
                    symbol, market_date, capture_profile, status, contract_count,
                    credits, error, checksum, collected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [symbol.upper(), market_date, profile, status, contract_count, credits, error, checksum, self._now()],
            )

    def mark_provider_fetch(
        self,
        cache_key: str,
        provider: str,
        kind: str,
        start_date: str,
        end_date: str,
        status: str = "complete",
    ) -> None:
        with self._connection() as connection:
            existing = connection.execute(
                "SELECT start_date, end_date FROM provider_fetches WHERE cache_key = ?",
                [cache_key],
            ).fetchone()
            if existing:
                start_date = min(start_date, str(existing["start_date"]))
                end_date = max(end_date, str(existing["end_date"]))
            connection.execute(
                """
                INSERT OR REPLACE INTO provider_fetches(
                    cache_key, provider, kind, start_date, end_date, status, fetched_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [cache_key, provider, kind, start_date, end_date, status, self._now()],
            )

    def provider_fetch_covers(self, cache_key: str, start_date: str, end_date: str) -> bool:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT 1 FROM provider_fetches
                WHERE cache_key = ? AND status = 'complete'
                  AND start_date <= ? AND end_date >= ?
                """,
                [cache_key, start_date, end_date],
            ).fetchone()
        return bool(row)

    def collection_dates(self, symbol: str, profile: str) -> set[str]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT market_date FROM collection_manifest WHERE symbol = ? AND capture_profile = ? AND status = 'complete'",
                [symbol.upper(), profile],
            ).fetchall()
        return {row["market_date"] for row in rows}

    def collection_summary(self, symbol: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT MIN(market_date) AS first_date, MAX(market_date) AS last_date,
                       COUNT(*) AS attempted,
                       SUM(CASE WHEN status = 'complete' THEN 1 ELSE 0 END) AS complete,
                       SUM(contract_count) AS contracts
                FROM collection_manifest WHERE symbol = ?
                """,
                [symbol.upper()],
            ).fetchone()
        return dict(row) if row else {}

    def purge_marketdata_metadata(self) -> None:
        with self._connection() as connection:
            connection.execute("DELETE FROM collection_manifest")
            connection.execute("DELETE FROM quota_events")
            connection.execute("DELETE FROM provider_fetches WHERE provider = 'marketdata'")
            connection.execute("DELETE FROM app_settings WHERE key LIKE 'marketdata_chain_membership:%'")
            connection.execute(
                "DELETE FROM app_settings WHERE key IN ('option_pricing_validation_v1', 'option_pricing_calibration_daily_budget_v1')"
            )
