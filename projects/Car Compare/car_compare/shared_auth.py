from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from http.cookies import SimpleCookie
from urllib.parse import urlencode


def _b64decode_url(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def valid_shared_session_token(token: str | None, username: str, session_secret: str) -> bool:
    """Validate the session token issued by the NSY DEM sign-in service."""
    if not token or not username or not session_secret:
        return False
    try:
        raw = _b64decode_url(token).decode("utf-8")
        token_username, expires_value, nonce, signature = raw.split("|", 3)
        if not nonce or token_username != username or int(expires_value) < int(time.time()):
            return False
        payload = f"{token_username}|{expires_value}|{nonce}"
        expected = hmac.new(session_secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    except Exception:
        return False
    return hmac.compare_digest(signature, expected)


@dataclass(frozen=True)
class SharedSessionAuth:
    username: str
    session_secret: str
    cookie_name: str = "dem_session"
    login_url: str = "https://dem.nsyprojects.com/login"
    public_origin: str = "https://carcompare.nsyprojects.com"

    @classmethod
    def from_environment(cls) -> "SharedSessionAuth":
        return cls(
            username=os.environ.get("CAR_COMPARE_AUTH_USERNAME", os.environ.get("DEM_AUTH_USERNAME", "")).strip(),
            session_secret=os.environ.get("CAR_COMPARE_SESSION_SECRET", os.environ.get("DEM_SESSION_SECRET", "")).strip(),
            cookie_name=os.environ.get("CAR_COMPARE_AUTH_COOKIE_NAME", "dem_session").strip() or "dem_session",
            login_url=os.environ.get("CAR_COMPARE_LOGIN_URL", "https://dem.nsyprojects.com/login").strip(),
            public_origin=os.environ.get("CAR_COMPARE_PUBLIC_ORIGIN", "https://carcompare.nsyprojects.com").strip().rstrip("/"),
        )

    @property
    def enabled(self) -> bool:
        return bool(self.username and self.session_secret)

    def valid_cookie_header(self, header: str | None) -> bool:
        if not self.enabled or not header:
            return False
        try:
            cookies = SimpleCookie()
            cookies.load(header)
            morsel = cookies.get(self.cookie_name)
        except Exception:
            return False
        return valid_shared_session_token(morsel.value if morsel else None, self.username, self.session_secret)

    def login_redirect(self, request_target: str) -> str:
        target = request_target if request_target.startswith("/") and not request_target.startswith("//") else "/"
        return f"{self.login_url}?{urlencode({'next': f'{self.public_origin}{target}'})}"
