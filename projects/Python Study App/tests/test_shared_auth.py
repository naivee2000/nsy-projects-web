from __future__ import annotations

import base64
import hashlib
import hmac
import time

from fastapi.testclient import TestClient

from code_practice import app as app_module
from code_practice.shared_auth import SharedSessionAuth, valid_shared_session_token


def _token(username: str, secret: str, expires_offset: int = 300) -> str:
    expires = str(int(time.time()) + expires_offset)
    payload = f"{username}|{expires}|test-nonce"
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}|{signature}".encode()).decode().rstrip("=")


def test_shared_session_token_validation():
    token = _token("admin", "shared-secret")
    assert valid_shared_session_token(token, "admin", "shared-secret")
    assert not valid_shared_session_token(token, "someone-else", "shared-secret")
    assert not valid_shared_session_token(token, "admin", "wrong-secret")
    assert not valid_shared_session_token(_token("admin", "shared-secret", -1), "admin", "shared-secret")


def test_online_auth_protects_progress_and_redirects_pages(monkeypatch):
    auth = SharedSessionAuth(
        username="admin",
        session_secret="shared-secret",
        public_origin="https://study.nsyprojects.com",
    )
    monkeypatch.setattr(app_module, "AUTH", auth)

    with TestClient(app_module.app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["authEnabled"] is True

        assert client.get("/api/progress").status_code == 401
        page = client.get("/", follow_redirects=False)
        assert page.status_code == 303
        assert page.headers["location"] == "/login"
        owner_login = client.get("/api/auth/owner", follow_redirects=False)
        assert owner_login.headers["location"].startswith("https://dem.nsyprojects.com/login?")
        assert "study.nsyprojects.com" in owner_login.headers["location"]

        client.cookies.set("dem_session", _token("admin", "shared-secret"))
        assert client.get("/api/progress").status_code == 200
