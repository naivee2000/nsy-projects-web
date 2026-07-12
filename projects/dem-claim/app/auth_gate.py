"""Session-cookie auth gate for the public DEM app deployment."""

from __future__ import annotations

import base64
import hashlib
import hmac
import html
import os
import secrets
import time
from typing import Any
from urllib.parse import urlencode, urlparse

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response


AUTH_USERNAME = os.environ.get("DEM_AUTH_USERNAME", "").strip()
AUTH_PASSWORD_HASH = os.environ.get("DEM_AUTH_PASSWORD_HASH", "").strip()
AUTH_SESSION_SECRET = os.environ.get("DEM_SESSION_SECRET", "").strip()
AUTH_COOKIE_NAME = os.environ.get("DEM_AUTH_COOKIE_NAME", "dem_session")
AUTH_COOKIE_DOMAIN = os.environ.get("DEM_AUTH_COOKIE_DOMAIN", ".nsyprojects.com").strip() or None
SIGNED_IN_COOKIE_NAME = os.environ.get("NSY_SIGNED_IN_COOKIE_NAME", "nsy_signed_in")
AUTH_SESSION_TTL_SECONDS = int(os.environ.get("DEM_SESSION_TTL_SECONDS", "86400"))
AUTH_COOKIE_SECURE = os.environ.get("DEM_COOKIE_SECURE", "1").lower() not in {"0", "false", "no"}
AUTH_ENABLED = bool(AUTH_USERNAME and AUTH_PASSWORD_HASH and AUTH_SESSION_SECRET)
ALLOWED_NEXT_HOSTS = {"nsyprojects.com", "www.nsyprojects.com", "dem.nsyprojects.com", "carcompare.nsyprojects.com"}


LOGIN_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sign in - NSY Projects</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f6f8;
      --surface: #ffffff;
      --ink: #182230;
      --muted: #667085;
      --line: #d0d5dd;
      --primary: #175cd3;
      --primary-strong: #1849a9;
      --red: #b42318;
      --red-soft: #fef3f2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      min-height: 100vh;
      margin: 0;
      display: grid;
      place-items: center;
      padding: 24px;
      background: linear-gradient(180deg, #eef2f6 0, var(--bg) 280px);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }}
    main {{
      width: min(420px, 100%);
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      padding: 24px;
      box-shadow: 0 20px 48px rgba(16, 24, 40, 0.10);
    }}
    a {{
      color: var(--primary);
      font-size: 13px;
      font-weight: 800;
      text-decoration: none;
    }}
    .login-nav {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-bottom: 18px;
    }}
    .cancel-action {{
      min-height: 34px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #ffffff;
      color: var(--ink);
      padding: 0 11px;
      cursor: pointer;
      font: inherit;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0;
    }}
    .eyebrow {{
      margin: 18px 0 8px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 0 0 18px;
      font-size: 32px;
      line-height: 1.06;
      letter-spacing: 0;
    }}
    form {{
      display: grid;
      gap: 14px;
    }}
    label {{
      display: grid;
      gap: 7px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 800;
    }}
    input {{
      min-height: 42px;
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 0 12px;
      color: var(--ink);
      font: inherit;
      letter-spacing: 0;
    }}
    button {{
      min-height: 44px;
      border: 0;
      border-radius: 6px;
      background: var(--primary);
      color: #ffffff;
      cursor: pointer;
      font: inherit;
      font-weight: 850;
      letter-spacing: 0;
    }}
    button:hover {{ background: var(--primary-strong); }}
    .error {{
      margin: 0;
      border: 1px solid #fecdca;
      border-radius: 6px;
      background: var(--red-soft);
      color: var(--red);
      padding: 10px 12px;
      font-size: 13px;
      font-weight: 800;
      line-height: 1.35;
    }}
  </style>
</head>
<body>
  <main>
    <div class="login-nav">
      <a class="cancel-action" href="{cancel_url}">Cancel</a>
      <a href="https://nsyprojects.com/">NSY Projects</a>
    </div>
    <p class="eyebrow">Private access</p>
    <h1>Sign in</h1>
    {error}
    <form method="post" action="/login">
      <input type="hidden" name="next" value="{next}">
      <label>
        用户名
        <input name="username" autocomplete="username" required autofocus>
      </label>
      <label>
        密码
        <input name="password" type="password" autocomplete="current-password" required>
      </label>
      <button type="submit">登录</button>
    </form>
  </main>
</body>
</html>"""


def b64decode_url(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def verify_password(password: str) -> bool:
    try:
        algorithm, iterations_value, salt_value, digest_value = AUTH_PASSWORD_HASH.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_value)
        salt = b64decode_url(salt_value)
        expected = b64decode_url(digest_value)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, len(expected))
    except Exception:
        return False
    return secrets.compare_digest(actual, expected)


def make_session_token(username: str) -> str:
    expires = str(int(time.time()) + AUTH_SESSION_TTL_SECONDS)
    nonce = secrets.token_urlsafe(16)
    payload = f"{username}|{expires}|{nonce}"
    signature = hmac.new(AUTH_SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    token = f"{payload}|{signature}".encode("utf-8")
    return base64.urlsafe_b64encode(token).decode("ascii").rstrip("=")


def valid_session_token(token: str | None) -> bool:
    if not token:
        return False
    try:
        raw = b64decode_url(token).decode("utf-8")
        username, expires_value, nonce, signature = raw.split("|", 3)
        if not nonce or username != AUTH_USERNAME:
            return False
        if int(expires_value) < int(time.time()):
            return False
        payload = f"{username}|{expires_value}|{nonce}"
        expected = hmac.new(AUTH_SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    except Exception:
        return False
    return secrets.compare_digest(signature, expected)


def safe_next_url(next_url: str | None) -> str:
    if not next_url:
        return "/"
    if next_url.startswith("/") and not next_url.startswith("//"):
        return next_url
    parsed = urlparse(next_url)
    if parsed.scheme == "https" and parsed.netloc in ALLOWED_NEXT_HOSTS:
        return next_url
    return "/"


def safe_cancel_url(next_url: str | None) -> str:
    if not next_url:
        return "https://nsyprojects.com/"
    parsed = urlparse(next_url)
    if parsed.scheme == "https" and parsed.netloc in {"nsyprojects.com", "www.nsyprojects.com"}:
        return next_url
    return "https://nsyprojects.com/projects"


def render_login(error: str = "", next_url: str = "/") -> HTMLResponse:
    error_html = f'<p class="error">{html.escape(error)}</p>' if error else ""
    body = LOGIN_HTML.format(
        error=error_html,
        next=html.escape(safe_next_url(next_url), quote=True),
        cancel_url=html.escape(safe_cancel_url(next_url), quote=True),
    )
    return HTMLResponse(body)


def auth_redirect(request: Request) -> RedirectResponse:
    next_path = request.url.path
    if request.url.query:
        next_path = f"{next_path}?{request.url.query}"
    return RedirectResponse(url=f"/login?{urlencode({'next': next_path})}", status_code=303)


def install_auth(app: FastAPI) -> None:
    @app.middleware("http")
    async def require_auth(request: Request, call_next: Any) -> Response:
        if not AUTH_ENABLED:
            return await call_next(request)
        path = request.url.path
        if path in {"/login", "/logout"}:
            return await call_next(request)
        if valid_session_token(request.cookies.get(AUTH_COOKIE_NAME)):
            return await call_next(request)
        if path.startswith("/api/"):
            return JSONResponse({"detail": "Authentication required."}, status_code=401)
        return auth_redirect(request)

    @app.get("/login", response_class=HTMLResponse)
    async def login(next: str = "/") -> HTMLResponse:
        return render_login(next_url=next)

    @app.post("/login")
    async def submit_login(
        username: str = Form(),
        password: str = Form(),
        next: str = Form(default="/"),
    ) -> Response:
        next_url = safe_next_url(next)
        if not AUTH_ENABLED:
            return RedirectResponse(url=next_url, status_code=303)
        if username.strip() != AUTH_USERNAME or not verify_password(password):
            return render_login("Username or password is incorrect.", next_url=next_url)
        response = RedirectResponse(url=next_url, status_code=303)
        response.set_cookie(
            AUTH_COOKIE_NAME,
            make_session_token(AUTH_USERNAME),
            max_age=AUTH_SESSION_TTL_SECONDS,
            httponly=True,
            secure=AUTH_COOKIE_SECURE,
            samesite="lax",
            domain=AUTH_COOKIE_DOMAIN,
        )
        response.set_cookie(
            SIGNED_IN_COOKIE_NAME,
            "1",
            max_age=AUTH_SESSION_TTL_SECONDS,
            httponly=False,
            secure=AUTH_COOKIE_SECURE,
            samesite="lax",
            domain=AUTH_COOKIE_DOMAIN,
        )
        return response

    @app.get("/logout")
    async def logout(next: str = "https://nsyprojects.com/") -> RedirectResponse:
        response = RedirectResponse(url=safe_next_url(next), status_code=303)
        response.delete_cookie(AUTH_COOKIE_NAME)
        response.delete_cookie(AUTH_COOKIE_NAME, domain=AUTH_COOKIE_DOMAIN)
        response.delete_cookie(SIGNED_IN_COOKIE_NAME, domain=AUTH_COOKIE_DOMAIN)
        return response
