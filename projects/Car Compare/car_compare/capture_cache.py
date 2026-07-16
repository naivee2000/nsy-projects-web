from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from car_compare.models import VehicleQuery


# Version 4 invalidates marketplace captures created before scoped missing-make
# cards, drivetrain context, and the expanded trim aliases were validated.
# Research version 3 prevents an optional cached review from reintroducing rows
# classified under the preceding matching rules.
CACHE_SCHEMA_VERSION = 4
RESEARCH_CACHE_SCHEMA_VERSION = 3
MAX_RECENT_TTL_SECONDS = 3 * 24 * 60 * 60
MAX_OLDER_TTL_SECONDS = 3 * 24 * 60 * 60


@dataclass(frozen=True)
class CaptureCacheEntry:
    source: str
    model_year: int
    captured_at: float
    expires_at: float
    payload: dict[str, Any]


class CaptureCache:
    def __init__(
        self,
        path: Path,
        *,
        enabled: bool = True,
        recent_ttl_seconds: int = MAX_RECENT_TTL_SECONDS,
        older_ttl_seconds: int = MAX_OLDER_TTL_SECONDS,
    ) -> None:
        self.path = path
        self.enabled = bool(enabled)
        self.recent_ttl_seconds = max(60, min(MAX_RECENT_TTL_SECONDS, int(recent_ttl_seconds)))
        self.older_ttl_seconds = max(60, min(MAX_OLDER_TTL_SECONDS, int(older_ttl_seconds)))
        if self.enabled:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._initialize()

    def status(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "path": str(self.path),
            "ready": bool(self.enabled and self.path.exists()),
            "recentTtlSeconds": self.recent_ttl_seconds,
            "olderTtlSeconds": self.older_ttl_seconds,
        }

    def load(
        self,
        request: VehicleQuery,
        source: str,
        years: Iterable[int],
        *,
        now: float | None = None,
    ) -> list[CaptureCacheEntry]:
        if not self.enabled:
            return []
        requested_years = sorted({int(year) for year in years})
        if not requested_years:
            return []
        timestamp = time.time() if now is None else float(now)
        query_key = _query_key(request)
        placeholders = ",".join("?" for _ in requested_years)
        sql = f"""
            SELECT source, model_year, captured_at, expires_at, payload_json
            FROM marketplace_capture_cache
            WHERE query_key = ? AND source = ? AND model_year IN ({placeholders}) AND expires_at > ?
            ORDER BY model_year DESC
        """
        with self._connect() as connection:
            rows = connection.execute(sql, [query_key, source, *requested_years, timestamp]).fetchall()
            connection.execute("DELETE FROM marketplace_capture_cache WHERE expires_at <= ?", (timestamp,))
        entries: list[CaptureCacheEntry] = []
        for row in rows:
            try:
                payload = json.loads(str(row[4]))
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, dict):
                continue
            entries.append(
                CaptureCacheEntry(
                    source=str(row[0]),
                    model_year=int(row[1]),
                    captured_at=float(row[2]),
                    expires_at=float(row[3]),
                    payload=payload,
                )
            )
        return entries

    def store_year(
        self,
        request: VehicleQuery,
        source: str,
        model_year: int,
        payload: dict[str, Any],
        *,
        current_year: int,
        captured_at: float | None = None,
        overwrite_existing: bool = True,
    ) -> None:
        if not self.enabled:
            return
        timestamp = time.time() if captured_at is None else float(captured_at)
        ttl = self.recent_ttl_seconds if model_year >= current_year - 2 else self.older_ttl_seconds
        expires_at = timestamp + ttl
        query_key = _query_key(request)
        cache_key = _entry_key(query_key, source, model_year)
        serialized = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        conflict_clause = (
            """
                INSERT INTO marketplace_capture_cache (
                    cache_key, query_key, source, model_year, captured_at, expires_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    captured_at = excluded.captured_at,
                    expires_at = excluded.expires_at,
                    payload_json = excluded.payload_json
            """
            if overwrite_existing
            else """
                INSERT INTO marketplace_capture_cache (
                    cache_key, query_key, source, model_year, captured_at, expires_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO NOTHING
            """
        )
        with self._connect() as connection:
            connection.execute(
                conflict_clause,
                (cache_key, query_key, source, int(model_year), timestamp, expires_at, serialized),
            )

    def delete_expired(self, *, now: float | None = None) -> int:
        if not self.enabled:
            return 0
        timestamp = time.time() if now is None else float(now)
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM marketplace_capture_cache WHERE expires_at <= ?", (timestamp,))
            return max(0, int(cursor.rowcount or 0))

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS marketplace_capture_cache (
                    cache_key TEXT PRIMARY KEY,
                    query_key TEXT NOT NULL,
                    source TEXT NOT NULL,
                    model_year INTEGER NOT NULL,
                    captured_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS marketplace_capture_lookup
                ON marketplace_capture_cache(query_key, source, model_year, expires_at)
                """
            )
            current_year = time.gmtime().tm_year
            connection.execute(
                """
                UPDATE marketplace_capture_cache
                SET expires_at = captured_at + CASE
                    WHEN model_year >= ? THEN ?
                    ELSE ?
                END
                """,
                (current_year - 2, self.recent_ttl_seconds, self.older_ttl_seconds),
            )

    @contextmanager
    def _connect(self) -> Any:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.execute("PRAGMA busy_timeout=10000")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()


class ResearchResultCache:
    def __init__(
        self,
        path: Path,
        *,
        enabled: bool = True,
        ttl_seconds: int = MAX_OLDER_TTL_SECONDS,
    ) -> None:
        self.path = path
        self.enabled = bool(enabled)
        self.ttl_seconds = max(60, min(MAX_OLDER_TTL_SECONDS, int(ttl_seconds)))
        if self.enabled:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self._connect() as connection:
                connection.execute("PRAGMA journal_mode=WAL")
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS research_result_cache (
                        cache_key TEXT PRIMARY KEY,
                        kind TEXT NOT NULL,
                        captured_at REAL NOT NULL,
                        expires_at REAL NOT NULL,
                        payload_json TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    "UPDATE research_result_cache SET expires_at = captured_at + ?",
                    (self.ttl_seconds,),
                )

    def status(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "path": str(self.path),
            "ready": bool(self.enabled and self.path.exists()),
            "ttlSeconds": self.ttl_seconds,
        }

    def load(self, kind: str, identity: dict[str, Any], *, now: float | None = None) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        timestamp = time.time() if now is None else float(now)
        cache_key = _research_key(kind, identity)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM research_result_cache WHERE cache_key = ? AND expires_at > ?",
                (cache_key, timestamp),
            ).fetchone()
            connection.execute("DELETE FROM research_result_cache WHERE expires_at <= ?", (timestamp,))
        if not row:
            return None
        try:
            payload = json.loads(str(row[0]))
        except json.JSONDecodeError:
            return None
        return payload if isinstance(payload, dict) else None

    def store(
        self,
        kind: str,
        identity: dict[str, Any],
        payload: dict[str, Any],
        *,
        captured_at: float | None = None,
    ) -> None:
        if not self.enabled:
            return
        timestamp = time.time() if captured_at is None else float(captured_at)
        cache_key = _research_key(kind, identity)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO research_result_cache (cache_key, kind, captured_at, expires_at, payload_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    captured_at = excluded.captured_at,
                    expires_at = excluded.expires_at,
                    payload_json = excluded.payload_json
                """,
                (
                    cache_key,
                    kind,
                    timestamp,
                    timestamp + self.ttl_seconds,
                    json.dumps(payload, separators=(",", ":"), sort_keys=True),
                ),
            )

    @contextmanager
    def _connect(self) -> Any:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.execute("PRAGMA busy_timeout=10000")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()


def _query_key(request: VehicleQuery) -> str:
    identity = {
        "version": CACHE_SCHEMA_VERSION,
        "make": request.make.strip().casefold(),
        "model": request.model.strip().casefold(),
        "trim": request.trim.strip().casefold(),
    }
    return hashlib.sha256(json.dumps(identity, sort_keys=True).encode("utf-8")).hexdigest()


def _entry_key(query_key: str, source: str, model_year: int) -> str:
    raw = f"{CACHE_SCHEMA_VERSION}|{query_key}|{source}|{int(model_year)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _research_key(kind: str, identity: dict[str, Any]) -> str:
    raw = json.dumps(
        {"version": RESEARCH_CACHE_SCHEMA_VERSION, "kind": kind, "identity": identity},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
