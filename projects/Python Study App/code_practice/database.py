from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

from .learning import next_review
from .schemas import Attempt, AttemptCreate, ReviewState


APP_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("CODE_PRACTICE_DATA_DIR", APP_ROOT / "data"))
DB_PATH = Path(os.environ.get("CODE_PRACTICE_DB", DATA_DIR / "code_practice.db"))
_seed_path = os.environ.get("CODE_PRACTICE_SEED_DB", "").strip()
SEED_DB_PATH: Path | None = Path(_seed_path).expanduser() if _seed_path else None
_profile: ContextVar[str] = ContextVar("study_profile", default="owner")


def profile_database_path(profile_id: str) -> Path:
    if profile_id == "owner":
        return DB_PATH
    if not re.fullmatch(r"[a-f0-9]{32}", profile_id):
        raise ValueError("Invalid profile ID")
    return DATA_DIR / "profiles" / profile_id / "code_practice.db"


@contextmanager
def profile_scope(profile_id: str):
    """Request-local selection also propagates to FastAPI's worker threads."""
    profile_database_path(profile_id)
    token = _profile.set(profile_id)
    try:
        yield
    finally:
        _profile.reset(token)


MIGRATION_VERSION = 3
MIGRATION_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id TEXT NOT NULL,
        problem_version INTEGER NOT NULL,
        source_code TEXT NOT NULL,
        result TEXT NOT NULL,
        runtime_ms REAL NOT NULL,
        tests_passed INTEGER NOT NULL,
        tests_total INTEGER NOT NULL,
        elapsed_study_seconds INTEGER NOT NULL DEFAULT 0,
        hint_level INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS review_states (
        problem_id TEXT PRIMARY KEY,
        interval_index INTEGER NOT NULL,
        due_at TEXT NOT NULL,
        latest_result TEXT NOT NULL,
        latest_accepted_source TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS drafts (
        problem_id TEXT PRIMARY KEY,
        source_code TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS hint_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id TEXT NOT NULL,
        hint_level INTEGER NOT NULL,
        created_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS generated_variants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id TEXT NOT NULL UNIQUE,
        seed_problem_id TEXT NOT NULL,
        status TEXT NOT NULL,
        problem_json TEXT NOT NULL,
        validation_json TEXT NOT NULL DEFAULT '{}',
        generated_at TEXT NOT NULL,
        reviewed_at TEXT
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_attempts_problem_created ON attempts(problem_id, created_at DESC);",
    "CREATE INDEX IF NOT EXISTS idx_attempts_created ON attempts(created_at DESC);",
    "CREATE INDEX IF NOT EXISTS idx_review_states_due ON review_states(due_at);",
    "CREATE INDEX IF NOT EXISTS idx_variants_status ON generated_variants(status);",
]
MIGRATION_2_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS daily_sessions (
        assignment_date TEXT PRIMARY KEY,
        created_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_session_problems (
        assignment_date TEXT NOT NULL,
        position INTEGER NOT NULL,
        problem_id TEXT NOT NULL,
        PRIMARY KEY (assignment_date, position),
        UNIQUE (assignment_date, problem_id),
        FOREIGN KEY (assignment_date) REFERENCES daily_sessions(assignment_date) ON DELETE CASCADE
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_daily_session_problems_date ON daily_session_problems(assignment_date, position);",
]
MIGRATION_3_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS daily_review_sessions (
        assignment_date TEXT PRIMARY KEY,
        assigned_at TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_review_problems (
        assignment_date TEXT NOT NULL,
        position INTEGER NOT NULL,
        problem_id TEXT NOT NULL,
        PRIMARY KEY (assignment_date, position),
        UNIQUE (assignment_date, problem_id),
        FOREIGN KEY (assignment_date) REFERENCES daily_review_sessions(assignment_date) ON DELETE CASCADE
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_daily_review_problems_date ON daily_review_problems(assignment_date, position);",
]
MIGRATIONS = {1: MIGRATION_STATEMENTS, 2: MIGRATION_2_STATEMENTS, 3: MIGRATION_3_STATEMENTS}


def install_seed_database() -> bool:
    """Copy the versioned progress snapshot only when no runtime database exists."""
    if _profile.get() != "owner" or DB_PATH.exists() or SEED_DB_PATH is None or not SEED_DB_PATH.is_file():
        return False
    if SEED_DB_PATH.resolve() == DB_PATH.resolve():
        raise RuntimeError("CODE_PRACTICE_SEED_DB must differ from the runtime database path")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(f"file:{SEED_DB_PATH.resolve()}?mode=ro", uri=True) as seed_connection:
        integrity = seed_connection.execute("PRAGMA integrity_check").fetchone()
        if not integrity or integrity[0] != "ok":
            raise RuntimeError("The configured Code Practice progress seed is not a valid SQLite database")

    temporary_path = DB_PATH.with_name(f".{DB_PATH.name}.seed-{os.getpid()}")
    try:
        shutil.copy2(SEED_DB_PATH, temporary_path)
        os.replace(temporary_path, DB_PATH)
    finally:
        temporary_path.unlink(missing_ok=True)
    return True


def connect(*, owner: bool = False) -> sqlite3.Connection:
    path = profile_database_path("owner" if owner else _profile.get())
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def db_session(*, owner: bool = False) -> Iterator[sqlite3.Connection]:
    connection = connect(owner=owner)
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database() -> None:
    install_seed_database()
    with db_session() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
            """
        )
        applied = {
            row["version"]
            for row in connection.execute("SELECT version FROM schema_migrations").fetchall()
        }
        for version, statements in MIGRATIONS.items():
            if version in applied:
                continue
            for statement in statements:
                connection.execute(statement)
            connection.execute(
                "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                (version, datetime.now(timezone.utc).isoformat()),
            )
        connection.execute("PRAGMA optimize")


def _attempt_from_row(row: sqlite3.Row) -> Attempt:
    return Attempt(**dict(row))


def list_attempts(limit: int | None = 500) -> list[Attempt]:
    with db_session() as connection:
        rows = connection.execute(
            "SELECT * FROM attempts ORDER BY created_at DESC, id DESC LIMIT ?", (-1 if limit is None else limit,)
        ).fetchall()
    return [_attempt_from_row(row) for row in rows]


def solved_problem_ids() -> set[str]:
    """Completion persists even after an accepted submission leaves recent history."""
    with db_session() as connection:
        return {row[0] for row in connection.execute("SELECT DISTINCT problem_id FROM attempts WHERE result = 'accepted'")}


def learning_attempts() -> list[Attempt]:
    """Scoring needs full history, but never needs to read thousands of saved sources."""
    with db_session() as connection:
        rows = connection.execute("""
            SELECT id, problem_id, problem_version, '' AS source_code, result,
                   runtime_ms, tests_passed, tests_total, elapsed_study_seconds,
                   hint_level, created_at
            FROM attempts ORDER BY created_at DESC, id DESC
        """).fetchall()
    return [_attempt_from_row(row) for row in rows]


def save_attempt(payload: AttemptCreate) -> Attempt:
    now = datetime.now(timezone.utc)
    with db_session() as connection:
        cursor = connection.execute(
            """
            INSERT INTO attempts (
                problem_id, problem_version, source_code, result, runtime_ms,
                tests_passed, tests_total, elapsed_study_seconds, hint_level, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.problem_id,
                payload.problem_version,
                payload.source_code,
                payload.result,
                payload.runtime_ms,
                payload.tests_passed,
                payload.tests_total,
                payload.elapsed_study_seconds,
                payload.hint_level,
                now.isoformat(),
            ),
        )
        previous = connection.execute(
            "SELECT interval_index FROM review_states WHERE problem_id = ?", (payload.problem_id,)
        ).fetchone()
        index, due_at = next_review(
            previous["interval_index"] if previous else None,
            payload.result == "accepted",
            now,
        )
        accepted_source = payload.source_code if payload.result == "accepted" else None
        connection.execute(
            """
            INSERT INTO review_states(problem_id, interval_index, due_at, latest_result, latest_accepted_source)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(problem_id) DO UPDATE SET
                interval_index = excluded.interval_index,
                due_at = excluded.due_at,
                latest_result = excluded.latest_result,
                latest_accepted_source = COALESCE(excluded.latest_accepted_source, review_states.latest_accepted_source)
            """,
            (payload.problem_id, index, due_at.isoformat(), payload.result, accepted_source),
        )
        row = connection.execute("SELECT * FROM attempts WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _attempt_from_row(row)


def list_review_states() -> list[ReviewState]:
    with db_session() as connection:
        rows = connection.execute("SELECT * FROM review_states ORDER BY due_at").fetchall()
    return [ReviewState(**dict(row)) for row in rows]


def get_daily_assignment(assignment_date: str) -> list[str] | None:
    with db_session() as connection:
        session = connection.execute(
            "SELECT 1 FROM daily_sessions WHERE assignment_date = ?", (assignment_date,)
        ).fetchone()
        if not session:
            return None
        rows = connection.execute(
            "SELECT problem_id FROM daily_session_problems WHERE assignment_date = ? ORDER BY position",
            (assignment_date,),
        ).fetchall()
    return [row["problem_id"] for row in rows]


def save_daily_assignment(assignment_date: str, problem_ids: list[str]) -> list[str]:
    with db_session() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO daily_sessions(assignment_date, created_at) VALUES (?, ?)",
            (assignment_date, datetime.now(timezone.utc).isoformat()),
        )
        connection.executemany(
            "INSERT OR IGNORE INTO daily_session_problems(assignment_date, position, problem_id) VALUES (?, ?, ?)",
            [(assignment_date, position, problem_id) for position, problem_id in enumerate(problem_ids)],
        )
        rows = connection.execute(
            "SELECT problem_id FROM daily_session_problems WHERE assignment_date = ? ORDER BY position",
            (assignment_date,),
        ).fetchall()
    return [row["problem_id"] for row in rows]


def remove_daily_assignment_problems(assignment_date: str, problem_ids: list[str]) -> list[str]:
    """Permanently remove newly ineligible work without refilling a fixed daily set."""
    unique_ids = list(dict.fromkeys(problem_ids))
    if not unique_ids:
        return get_daily_assignment(assignment_date) or []
    placeholders = ", ".join("?" for _ in unique_ids)
    with db_session() as connection:
        connection.execute(
            f"DELETE FROM daily_session_problems WHERE assignment_date = ? AND problem_id IN ({placeholders})",
            (assignment_date, *unique_ids),
        )
        rows = connection.execute(
            "SELECT problem_id FROM daily_session_problems WHERE assignment_date = ? ORDER BY position",
            (assignment_date,),
        ).fetchall()
    return [row["problem_id"] for row in rows]


def get_daily_review_assignment(assignment_date: str) -> tuple[datetime, list[str]] | None:
    with db_session() as connection:
        session = connection.execute(
            "SELECT assigned_at FROM daily_review_sessions WHERE assignment_date = ?", (assignment_date,)
        ).fetchone()
        if not session:
            return None
        rows = connection.execute(
            "SELECT problem_id FROM daily_review_problems WHERE assignment_date = ? ORDER BY position",
            (assignment_date,),
        ).fetchall()
    return datetime.fromisoformat(session["assigned_at"]), [row["problem_id"] for row in rows]


def recent_daily_review_problem_ids(assignment_date: str, lookback_days: int = 3) -> set[str]:
    """Return questions assigned during the preceding calendar-day cooldown."""
    if lookback_days <= 0:
        return set()
    current_date = date.fromisoformat(assignment_date)
    earliest_date = (current_date - timedelta(days=lookback_days)).isoformat()
    with db_session() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT problem_id
            FROM daily_review_problems
            WHERE assignment_date >= ? AND assignment_date < ?
            """,
            (earliest_date, assignment_date),
        ).fetchall()
    return {row["problem_id"] for row in rows}


def save_daily_review_assignment(assignment_date: str, problem_ids: list[str]) -> tuple[datetime, list[str]]:
    assigned_at = datetime.now(timezone.utc)
    with db_session() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO daily_review_sessions(assignment_date, assigned_at) VALUES (?, ?)",
            (assignment_date, assigned_at.isoformat()),
        )
        connection.executemany(
            "INSERT OR IGNORE INTO daily_review_problems(assignment_date, position, problem_id) VALUES (?, ?, ?)",
            [(assignment_date, position, problem_id) for position, problem_id in enumerate(problem_ids)],
        )
        session = connection.execute(
            "SELECT assigned_at FROM daily_review_sessions WHERE assignment_date = ?", (assignment_date,)
        ).fetchone()
        rows = connection.execute(
            "SELECT problem_id FROM daily_review_problems WHERE assignment_date = ? ORDER BY position",
            (assignment_date,),
        ).fetchall()
    return datetime.fromisoformat(session["assigned_at"]), [row["problem_id"] for row in rows]


def save_draft(problem_id: str, source_code: str) -> None:
    with db_session() as connection:
        connection.execute(
            """
            INSERT INTO drafts(problem_id, source_code, updated_at) VALUES (?, ?, ?)
            ON CONFLICT(problem_id) DO UPDATE SET source_code = excluded.source_code, updated_at = excluded.updated_at
            """,
            (problem_id, source_code, datetime.now(timezone.utc).isoformat()),
        )


def get_draft(problem_id: str) -> str | None:
    with db_session() as connection:
        row = connection.execute("SELECT source_code FROM drafts WHERE problem_id = ?", (problem_id,)).fetchone()
    return row["source_code"] if row else None


def record_hint(problem_id: str, hint_level: int) -> None:
    with db_session() as connection:
        connection.execute(
            "INSERT INTO hint_events(problem_id, hint_level, created_at) VALUES (?, ?, ?)",
            (problem_id, hint_level, datetime.now(timezone.utc).isoformat()),
        )


def highest_hint(problem_id: str) -> int:
    with db_session() as connection:
        row = connection.execute(
            "SELECT COALESCE(MAX(hint_level), 0) AS level FROM hint_events WHERE problem_id = ?",
            (problem_id,),
        ).fetchone()
    return int(row["level"])


def approved_variant_rows() -> list[dict]:
    with db_session(owner=True) as connection:
        rows = connection.execute(
            "SELECT problem_json FROM generated_variants WHERE status = 'approved' ORDER BY id"
        ).fetchall()
    problems = []
    for row in rows:
        problem = json.loads(row["problem_json"])
        problem["status"] = "approved"
        problems.append(problem)
    return problems


def save_variant(problem_json: dict, seed_problem_id: str, status: str = "draft", validation: dict | None = None) -> None:
    problem_id = str(problem_json["id"])
    with db_session(owner=True) as connection:
        connection.execute(
            """
            INSERT INTO generated_variants(
                problem_id, seed_problem_id, status, problem_json, validation_json, generated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(problem_id) DO UPDATE SET
                seed_problem_id = excluded.seed_problem_id,
                status = excluded.status,
                problem_json = excluded.problem_json,
                validation_json = excluded.validation_json,
                generated_at = excluded.generated_at,
                reviewed_at = NULL
            """,
            (
                problem_id,
                seed_problem_id,
                status,
                json.dumps(problem_json),
                json.dumps(validation or {}),
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def list_variants() -> list[dict]:
    with db_session(owner=True) as connection:
        rows = connection.execute("SELECT * FROM generated_variants ORDER BY id DESC").fetchall()
    return [
        {
            **dict(row),
            "problem": json.loads(row["problem_json"]),
            "validation": json.loads(row["validation_json"]),
        }
        for row in rows
    ]


def update_variant_status(problem_id: str, status: str, validation: dict | None = None) -> bool:
    with db_session(owner=True) as connection:
        cursor = connection.execute(
            """
            UPDATE generated_variants
            SET status = ?, validation_json = COALESCE(?, validation_json), reviewed_at = ?
            WHERE problem_id = ?
            """,
            (
                status,
                json.dumps(validation) if validation is not None else None,
                datetime.now(timezone.utc).isoformat(),
                problem_id,
            ),
        )
    return cursor.rowcount == 1
