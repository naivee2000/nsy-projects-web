"""Run transfer helpers only against disposable databases, never owner progress."""
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not shutil.which("sqlite3"), reason="SQLite CLI required")


@pytest.mark.parametrize("script", ["backup_data.sh", "scripts/refresh_progress_seed.sh"])
@pytest.mark.parametrize("location", ["default", "data_dir", "explicit_db"])
def test_transfer_uses_the_same_database_precedence_as_the_app(tmp_path, script, location):
    app = tmp_path / "checkout with spaces"
    target = app / script
    target.parent.mkdir(parents=True)
    shutil.copy2(ROOT / script, target)
    paths = {
        "default": app / "data/code_practice.db",
        "data_dir": tmp_path / "persistent data/code_practice.db",
        "explicit_db": tmp_path / "custom progress.db",
    }
    for name, path in paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as connection:
            for table in ("attempts", "drafts", "review_states"):
                connection.execute(f"CREATE TABLE {table}(marker TEXT)")
                connection.execute(f"INSERT INTO {table} VALUES(?)", (name,))
    before = {name: path.read_bytes() for name, path in paths.items()}
    env = {key: value for key, value in os.environ.items() if not key.startswith("CODE_PRACTICE_")}
    if location != "default":
        env["CODE_PRACTICE_DATA_DIR"] = str(paths["data_dir"].parent)
    if location == "explicit_db":
        env["CODE_PRACTICE_DB"] = str(paths["explicit_db"])
    backups = tmp_path / "external backups"
    env["CODE_PRACTICE_BACKUP_DIR"] = str(backups)
    subprocess.run(["bash", str(target)], env=env, check=True, capture_output=True, text=True)
    if script == "backup_data.sh":
        copies = list(backups.glob("*.db"))
        assert len(copies) == 1
        snapshot = copies[0]
    else:
        snapshot = app / "seed_data/initial_progress.db"
    with sqlite3.connect(snapshot) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert connection.execute("SELECT marker FROM drafts").fetchone()[0] == location
    assert {name: path.read_bytes() for name, path in paths.items()} == before


@pytest.mark.parametrize("script", ["backup_data.sh", "scripts/refresh_progress_seed.sh"])
def test_missing_transfer_source_does_not_create_a_database(tmp_path, script):
    existing = set(tmp_path.rglob("*.db"))
    target = tmp_path / script
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / script, target)
    env = {key: value for key, value in os.environ.items() if not key.startswith("CODE_PRACTICE_")}
    env["CODE_PRACTICE_DB"] = str(tmp_path / "absent.db")
    result = subprocess.run(["bash", str(target)], env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert set(tmp_path.rglob("*.db")) == existing
