"""Exercise existing profile backups in a temporary study store with fresh test accounts."""

from argparse import ArgumentParser
from contextlib import closing
from datetime import timedelta
import os
from pathlib import Path
import secrets
import sqlite3
from tempfile import TemporaryDirectory


def readonly(path):
    return sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)


def validate(path):
    with closing(readonly(path)) as db:
        assert db.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []


def unchanged_records(original, restored):
    # A dashboard read can add a daily assignment when the date is new. All
    # rows already saved in either track must still match the backup.
    with closing(readonly(restored)) as db:
        db.execute("ATTACH DATABASE ? AS original", (original.resolve().as_uri() + "?mode=ro",))
        tables = db.execute(
            "SELECT name FROM original.sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        for (name,) in tables:
            quoted = '"' + name.replace('"', '""') + '"'
            assert (
                db.execute(
                    f"SELECT * FROM original.{quoted} EXCEPT SELECT * FROM main.{quoted} LIMIT 1"
                ).fetchone()
                is None
            ), name


def run(backup, directory):
    os.environ.update(
        CODE_PRACTICE_DATA_DIR=str(directory),
        CODE_PRACTICE_DB=str(directory / "code_practice.db"),
        CODE_PRACTICE_SEED_DB="",
        CODE_PRACTICE_AUTH_USERNAME="",
        CODE_PRACTICE_SESSION_SECRET="",
    )
    from code_practice import accounts, database, database_track, review_v2
    from code_practice.database_catalog import INVENTORY, CREDITS
    from code_practice.database_routes import problem_detail

    validate(backup / "accounts.db")
    with closing(readonly(backup / "accounts.db")) as registry:
        roles = registry.execute("SELECT id,role FROM users ORDER BY role,id").fetchall()
    accounts.initialize("restore-owner")
    snapshots = {}
    for index, (old_id, role) in enumerate(roles):
        is_owner = old_id == "owner"
        assert is_owner or role == "member"
        profile = (
            "owner"
            if is_owner
            else accounts.create_user(f"restore-{index}", secrets.token_urlsafe(24))["id"]
        )
        original = backup / (
            "owner/code_practice.db" if is_owner else f"profiles/{old_id}/code_practice.db"
        )
        target = database.profile_database_path(profile)
        target.parent.mkdir(parents=True, exist_ok=True)
        validate(original)
        with closing(readonly(original)) as source, closing(sqlite3.connect(target)) as destination:
            source.backup(destination)
        with database.profile_scope(profile):
            database.initialize_database()
            with database.db_session() as db:
                passed = database_track.completion(db)
            today = database_track.dashboard()
            assert today["total"] == today["runnable"] == 323 and today["solved"] == len(passed)
            assert sum(CREDITS[p["difficulty"]] for p in today["dailyAssignment"]) <= 5
            assert len(today["reviewAssignment"]) <= 5
            assert {p["id"] for p in today["reviewAssignment"]} <= passed.keys()
            assert set(problem_detail(3832)["starters"]) == {"mysql", "pandas"}
            next_day = database_track.dashboard(
                review_v2.midnight(review_v2.local_day() + timedelta(days=1))
            )
            assert len(next_day["reviews"]) <= 5 and next_day["day"] != today["day"]
            unchanged_records(original, target)
            validate(target)
            snapshots[profile] = today
    assert "owner" in snapshots and len(snapshots) > 1
    new_id = accounts.create_user("new-restore-test", secrets.token_urlsafe(24))["id"]
    with database.profile_scope(new_id):
        first = database_track.dashboard()
        assert first["solved"] == 0 and not first["reviews"]
        assert sum(CREDITS[INVENTORY[p["id"]]["difficulty"]] for p in first["newProblems"]) == 5
    for profile, original_today in snapshots.items():
        with database.profile_scope(profile):
            assert database_track.dashboard() == original_today
    print(
        f"Restored and checked {len(snapshots)} existing profiles plus one new member; saved rows and daily sets preserved."
    )


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("backup", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="study-restore-") as location:
        run(args.backup.resolve(), Path(location))
