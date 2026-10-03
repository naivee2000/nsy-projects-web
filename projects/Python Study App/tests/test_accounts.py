import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from code_practice import accounts, database, app as app_module
from code_practice.shared_auth import SharedSessionAuth
from code_practice.schemas import AttemptCreate
from test_shared_auth import _token

HEADERS = {"X-Requested-With": "CodePractice"}
TEMP = "temporary-password-123"
CHOSEN = "my-personal-password-456"


@pytest.fixture
def online(monkeypatch):
    monkeypatch.setattr(app_module, "AUTH", SharedSessionAuth("admin", "shared-secret", public_origin="http://testserver"))
    with TestClient(app_module.app) as admin:
        admin.cookies.set("dem_session", _token("admin", "shared-secret"))
        admin.headers.update({**HEADERS, "X-Study-Profile": "owner"})
        yield admin


def create(admin, username="learner"):
    response = admin.post("/api/admin/accounts", json={"username": username, "password": TEMP})
    assert response.status_code == 201, response.text
    return response.json()


def sign_in(client, username, password=TEMP, change=True):
    client.headers.update(HEADERS)
    result = client.post("/api/auth/login", json={"username": username, "password": password})
    assert result.status_code == 200, result.text
    user = result.json()["user"]
    client.headers["X-Study-Profile"] = user["id"]
    if change:
        assert client.post("/api/auth/password", json={"current_password": password, "password": CHOSEN}).status_code == 200
    return user


def attempt():
    return dict(problem_id="pair-sum-indices", problem_version=1,
                source_code="return [0, 1]", result="accepted", runtime_ms=5,
                tests_passed=12, tests_total=12, hint_level=1, elapsed_study_seconds=60)


def test_original_owner_progress_preserved_and_new_accounts_start_empty(online):
    database.save_draft("pair-sum-indices", "owner draft")
    database.save_attempt(AttemptCreate(**attempt()))
    user = create(online)
    assert "password_hash" not in user
    with TestClient(app_module.app) as member:
        sign_in(member, "learner")
        assert member.get("/api/dashboard").json()["solvedCount"] == 0
        detail = member.get("/api/problems/pair-sum-indices").json()
        assert detail["savedDraft"] != "owner draft" and not detail["solved"]
        assert member.put("/api/problems/pair-sum-indices/draft", json={"source_code": "member draft"}).status_code == 200
        assert member.post("/api/problems/pair-sum-indices/hints/1").status_code == 200
        assert member.post("/api/attempts", json=attempt()).status_code == 200
        assert member.get("/api/problems?completion=passed").json()["total"] == 1
    with TestClient(app_module.app) as restarted:
        sign_in(restarted, "learner", CHOSEN, change=False)
        assert restarted.get("/api/problems/pair-sum-indices").json()["savedDraft"] == "member draft"
        assert restarted.get("/api/dashboard").json()["solvedCount"] == 1
        assert restarted.get("/api/problems/pair-sum-indices").json()["revealedHintLevel"] == 1
    assert online.get("/api/problems/pair-sum-indices").json()["savedDraft"] == "owner draft"
    assert online.get("/api/problems/pair-sum-indices").json()["revealedHintLevel"] == 0
    assert database.profile_database_path(user["id"]).is_file()


def test_members_cannot_manage_accounts_or_use_owner_codex(online):
    create(online)
    with TestClient(app_module.app) as member:
        sign_in(member, "learner")
        assert member.get("/api/admin/accounts").status_code == 403
        assert member.post("/api/admin/accounts", json={"username": "intruder", "password": TEMP}).status_code == 403
        assert member.post("/api/admin/accounts/owner/password", json={"password": TEMP}).status_code == 403
        assert member.patch("/api/admin/accounts/owner", json={"disabled": True}).status_code == 403
        assert member.get("/api/coach/codex-status").status_code == 403
        assert member.post("/api/problems/pair-sum-indices/codex-coach", json={}).status_code == 403
        assert member.get("/api/problems/pair-sum-indices?user_id=owner").json()["solved"] is False


def test_temporary_password_reset_disable_and_logout_revoke_access(online):
    user = create(online)
    with TestClient(app_module.app) as member:
        sign_in(member, "learner", change=False)
        assert member.get("/api/progress").status_code == 403
        assert member.post("/api/auth/password", json={"current_password": "wrong", "password": CHOSEN}).status_code == 400
        assert member.post("/api/auth/password", json={"current_password": TEMP, "password": CHOSEN}).status_code == 200
        old_token = member.cookies.get(accounts.COOKIE)
        assert online.post(f"/api/admin/accounts/{user['id']}/password", json={"password": TEMP}).status_code == 200
        assert accounts.session_user(old_token) is None
        assert member.get("/api/progress").status_code == 401
        sign_in(member, "learner")
        assert online.patch(f"/api/admin/accounts/{user['id']}", json={"disabled": True}).status_code == 200
        assert member.get("/api/progress").status_code == 401
        assert member.post("/api/auth/login", json={"username": "learner", "password": CHOSEN}).status_code == 401
        assert online.patch(f"/api/admin/accounts/{user['id']}", json={"disabled": False}).status_code == 200
        sign_in(member, "learner", CHOSEN, change=False)
        # Logging a member out must not fall back to an owner cookie in the same browser.
        member.cookies.set("dem_session", _token("admin", "shared-secret"))
        assert member.get("/api/auth/me").json()["user"]["id"] == user["id"]
        assert member.post("/api/auth/logout").status_code == 200
        assert member.get("/api/auth/me").json()["user"] is None
        assert member.get("/api/progress").status_code == 401


def test_cross_site_requests_and_stale_account_tabs_cannot_write(online):
    create(online)
    with TestClient(app_module.app) as member:
        assert member.post("/api/auth/login", json={"username": "learner", "password": TEMP}).status_code == 403
        assert member.post("/api/auth/login", headers={**HEADERS, "Origin": "https://evil.example"}, json={"username": "learner", "password": TEMP}).status_code == 403
        sign_in(member, "learner")
        member.headers["X-Study-Profile"] = "owner"
        assert member.put("/api/problems/pair-sum-indices/draft", json={"source_code": "stale owner draft"}).status_code == 409
        assert member.get("/api/dashboard").status_code == 409
        del member.headers["X-Study-Profile"]
        assert member.post("/api/attempts", json=attempt()).status_code == 409
        assert member.get("/api/problems/pair-sum-indices").json()["savedDraft"] != "stale owner draft"


def test_credentials_are_hashed_rate_limited_and_sessions_expire(online):
    user = create(online)
    row = accounts.get_user(user["id"])
    assert row["password_hash"].startswith("scrypt$") and TEMP not in row["password_hash"]
    assert online.post("/api/admin/accounts", json={"username": "LEARNER", "password": TEMP}).status_code == 400
    with TestClient(app_module.app) as member:
        member.headers.update(HEADERS)
        for _ in range(10):
            assert member.post("/api/auth/login", json={"username": "learner", "password": "wrong"}).status_code == 401
        assert member.post("/api/auth/login", json={"username": "learner", "password": TEMP}).status_code == 429
    token = accounts.new_session(user["id"])
    with accounts.registry() as db:
        stored = db.execute("SELECT token_hash FROM sessions").fetchone()[0]
        assert stored != token
        db.execute("UPDATE sessions SET expires_at=0")
    assert accounts.session_user(token) is None


def test_concurrent_profiles_daily_sets_and_backup_restore(online, tmp_path, monkeypatch):
    first = create(online, "first")
    second = create(online, "second")
    def study(user):
        with TestClient(app_module.app) as client:
            sign_in(client, user["username"])
            for i in range(6):
                text = f"{user['username']} draft {i}"
                assert client.put("/api/problems/pair-sum-indices/draft", json={"source_code": text}).status_code == 200
                assert client.get("/api/problems/pair-sum-indices").json()["savedDraft"] == text
            client.get("/api/dashboard")
            return client.cookies.get(accounts.COOKIE)
    with ThreadPoolExecutor(max_workers=2) as pool:
        tokens = list(pool.map(study, [first, second]))
    today = datetime.now().astimezone().date().isoformat()
    with database.profile_scope(first["id"]):
        database.save_daily_review_assignment(today, ["pair-sum-indices"])
        assert database.get_daily_assignment(today) is not None
    with database.profile_scope(second["id"]):
        assert database.get_daily_review_assignment(today)[1] == []
    backup = tmp_path / "backup"
    assert accounts.backup_all(backup)["databases"] == 4
    monkeypatch.setattr(database, "DATA_DIR", backup)
    monkeypatch.setattr(database, "DB_PATH", backup / "owner/code_practice.db")
    accounts.initialize("admin")
    assert accounts.session_user(tokens[0])["id"] == first["id"]
    for user in (first, second):
        with database.profile_scope(user["id"]):
            assert database.get_draft("pair-sum-indices") == f"{user['username']} draft 5"


def test_new_profile_never_copies_owner_seed(online, tmp_path, monkeypatch):
    seed = tmp_path / "owner-seed.db"
    database.save_draft("pair-sum-indices", "private seeded draft")
    with sqlite3.connect(database.DB_PATH) as src, sqlite3.connect(seed) as dst:
        src.backup(dst)
    monkeypatch.setattr(database, "SEED_DB_PATH", seed)
    user = create(online)
    with database.profile_scope(user["id"]):
        database.initialize_database()
        assert database.get_draft("pair-sum-indices") is None


def test_study_cookie_is_host_only_secure_and_owner_cannot_be_disabled(online, monkeypatch):
    create(online)
    monkeypatch.setattr(app_module, "AUTH", SharedSessionAuth("admin", "shared-secret", public_origin="https://study.example"))
    with TestClient(app_module.app, base_url="https://study.example") as client:
        client.headers.update(HEADERS)
        response = client.post("/api/auth/login", json={"username": "learner", "password": TEMP})
        cookie = response.headers["set-cookie"]
        assert "Secure" in cookie and "HttpOnly" in cookie and "SameSite=lax" in cookie
        assert "Domain=" not in cookie
    assert online.patch("/api/admin/accounts/owner", json={"disabled": True}).status_code == 400


def test_approved_library_variants_are_shared_but_progress_is_not(online):
    user = create(online)
    database.save_variant({"id": "shared-variant"}, "pair-sum-indices", status="approved")
    database.save_draft("pair-sum-indices", "owner only")
    with database.profile_scope(user["id"]):
        assert database.approved_variant_rows()[0]["id"] == "shared-variant"
        assert database.get_draft("pair-sum-indices") is None
