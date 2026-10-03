"""Study-only accounts; the original progress database belongs to the owner."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import getpass
import hashlib
import hmac
import json
import re
import secrets
import sqlite3
import time
from pathlib import Path
from uuid import uuid4

from . import database

COOKIE = "code_practice_session"
SESSION_SECONDS = 7 * 24 * 60 * 60


def registry_path() -> Path:
    return database.DATA_DIR / "accounts.db"


@contextmanager
def registry():
    registry_path().parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(registry_path(), timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize(owner_username: str = "admin") -> None:
    with registry() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT,
                role TEXT NOT NULL CHECK (role IN ('admin','member')),
                disabled INTEGER NOT NULL DEFAULT 0,
                must_change_password INTEGER NOT NULL DEFAULT 0,
                created_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                expires_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS login_limits (
                key TEXT PRIMARY KEY, failures INTEGER NOT NULL, expires_at INTEGER NOT NULL
            );
        """)
        db.execute("INSERT OR IGNORE INTO users(id,username,role,created_at) VALUES('owner',?,'admin',?)",
                   (owner_username or "admin", int(time.time())))
        ids = [row[0] for row in db.execute("SELECT id FROM users")]
    for profile_id in ids:
        with database.profile_scope(profile_id):
            database.initialize_database()


def public_user(user: dict) -> dict:
    return {**{key: user[key] for key in ("id", "username", "role")},
            "disabled": bool(user["disabled"]), "must_change_password": bool(user["must_change_password"])}


def get_user(user_id: str) -> dict | None:
    with registry() as db:
        row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None


def list_users() -> list[dict]:
    with registry() as db:
        return [public_user(dict(row)) for row in db.execute("SELECT * FROM users ORDER BY role,username")]


def password_hash(password: str) -> str:
    if not 12 <= len(password) <= 256:
        raise ValueError("Use a password between 12 and 256 characters.")
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32)
    return f"scrypt${salt.hex()}${derived.hex()}"


def password_matches(password: str, encoded: str | None) -> bool:
    # Do the same work for unknown users and owners without a study password.
    encoded = encoded or ("scrypt$" + "00" * 16 + "$" + "00" * 32)
    try:
        version, salt, expected = encoded.split("$")
        actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1, dklen=32)
        return version == "scrypt" and hmac.compare_digest(actual.hex(), expected)
    except (ValueError, TypeError):
        return False


def create_user(username: str, password: str) -> dict:
    username = username.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{2,31}", username):
        raise ValueError("Username must be 3–32 letters, numbers, dots, underscores, or hyphens.")
    encoded = password_hash(password)
    user_id = uuid4().hex
    with registry() as db:
        try:
            db.execute("INSERT INTO users(id,username,password_hash,role,must_change_password,created_at) VALUES(?,?,?,'member',1,?)",
                       (user_id, username, encoded, int(time.time())))
            with database.profile_scope(user_id):
                database.initialize_database()
        except sqlite3.IntegrityError as error:
            raise ValueError("That username is already in use.") from error
    return public_user(get_user(user_id))


def set_password(user_id: str, password: str, *, must_change: bool = False) -> None:
    encoded = password_hash(password)
    with registry() as db:
        if not db.execute("UPDATE users SET password_hash=?,must_change_password=? WHERE id=?",
                          (encoded, int(must_change), user_id)).rowcount:
            raise ValueError("Account not found.")
        db.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))


def set_disabled(user_id: str, disabled: bool) -> None:
    if user_id == "owner":
        raise ValueError("The owner account cannot be disabled.")
    with registry() as db:
        if not db.execute("UPDATE users SET disabled=? WHERE id=?", (int(disabled), user_id)).rowcount:
            raise ValueError("Account not found.")
        db.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))


def new_session(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    with registry() as db:
        db.execute("DELETE FROM sessions WHERE expires_at<=?", (int(time.time()),))
        db.execute("INSERT INTO sessions VALUES(?,?,?)",
                   (hashlib.sha256(token.encode()).hexdigest(), user_id, int(time.time()) + SESSION_SECONDS))
    return token


def session_user(token: str | None) -> dict | None:
    if not token or len(token) > 128:
        return None
    with registry() as db:
        row = db.execute("""SELECT users.* FROM users JOIN sessions ON users.id=sessions.user_id
                            WHERE token_hash=? AND expires_at>? AND disabled=0""",
                         (hashlib.sha256(token.encode()).hexdigest(), int(time.time()))).fetchone()
    return dict(row) if row else None


def revoke_session(token: str | None) -> None:
    if token:
        with registry() as db:
            db.execute("DELETE FROM sessions WHERE token_hash=?", (hashlib.sha256(token.encode()).hexdigest(),))


class LoginLimited(ValueError):
    pass


def authenticate(username: str, password: str, client_ip: str) -> dict | None:
    now = int(time.time())
    # The IP counter also limits attempts spread across many usernames.
    keys = [hashlib.sha256(value.encode()).hexdigest() for value in
            ("ip:" + client_ip, "user:" + username.strip().casefold())]
    with registry() as db:
        db.execute("DELETE FROM login_limits WHERE expires_at<=?", (now,))
        for key, limit in zip(keys, (30, 10)):
            row = db.execute("SELECT failures FROM login_limits WHERE key=?", (key,)).fetchone()
            if row and row[0] >= limit:
                raise LoginLimited("Too many sign-in attempts. Try again in five minutes.")
        # Reserve attempts before password work to bound concurrent requests.
        for key in keys:
            db.execute("""INSERT INTO login_limits VALUES(?,1,?) ON CONFLICT(key)
                          DO UPDATE SET failures=failures+1""", (key, now + 300))
        row = db.execute("SELECT * FROM users WHERE username=? COLLATE NOCASE", (username.strip(),)).fetchone()
    valid = password_matches(password, row["password_hash"] if row else None)
    if not valid or not row or row["disabled"]:
        return None
    with registry() as db:
        db.execute("DELETE FROM login_limits WHERE key=?", (keys[1],))
        db.execute("UPDATE login_limits SET failures=MAX(0,failures-1) WHERE key=?", (keys[0],))
    return dict(row)


def backup_all(destination: Path) -> dict:
    """Use SQLite backup, including accounts and every profile. Never copy a seed."""
    if destination.exists():
        raise ValueError("Choose a new backup directory.")
    destination.mkdir(parents=True)
    sources = {"accounts.db": registry_path(), "owner/code_practice.db": database.DB_PATH}
    if registry_path().exists():
        for user in list_users():
            if user["id"] != "owner":
                sources[f"profiles/{user['id']}/code_practice.db"] = database.profile_database_path(user["id"])
    for name, source in sources.items():
        if not source.exists():
            raise ValueError(f"Database missing: {source}")
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(f"file:{source.resolve()}?mode=ro", uri=True) as original, sqlite3.connect(target) as copy:
            original.backup(copy)
    return {"databases": len(sources), "backup": str(destination.resolve())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("reset-owner", help="Set the owner's study password on this host.")
    backup = commands.add_parser("backup", help="Back up all accounts and progress.")
    backup.add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.command == "backup":
        print(json.dumps(backup_all(args.destination)))
        return
    from .shared_auth import SharedSessionAuth
    initialize(SharedSessionAuth.from_environment().username or "admin")
    password = getpass.getpass("New owner password (at least 12 characters): ")
    if password != getpass.getpass("Confirm password: "):
        raise SystemExit("Passwords did not match; nothing changed.")
    set_password("owner", password)
    print("Owner study password updated; previous study sessions revoked.")


if __name__ == "__main__":
    main()
