from __future__ import annotations

import pytest

from code_practice import catalog, database


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATA_DIR", tmp_path)
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    database.initialize_database()
    catalog.refresh_catalog()
    yield
    catalog.refresh_catalog()

