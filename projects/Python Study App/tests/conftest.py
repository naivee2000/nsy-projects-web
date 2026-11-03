from __future__ import annotations

import pytest

from code_practice import catalog, database


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    # Existing legacy-contract tests run with the rollback policy. V2 tests
    # explicitly opt in and exercise its migrations, events and HTTP surface.
    monkeypatch.setenv("CODE_PRACTICE_REVIEW_V2", "0")
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    database.initialize_database()
    catalog.refresh_catalog()
    yield
    catalog.refresh_catalog()

