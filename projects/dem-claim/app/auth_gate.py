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
ALLOWED_NEXT_HOSTS = {
    "nsyprojects.com",
    "www.nsyprojects.com",
    "dem.nsyprojects.com",
    "carcompare.nsyprojects.com",
    *{
        host.strip()
        for host in os.environ.get("DEM_ALLOWED_NEXT_HOSTS", "").split(",")
        if host.strip()
    },
}


LOGIN_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Sign in to access private NSY Projects tools.">
  <title>Sign in - NSY Projects</title>
  <style>
/* Hallmark · shape: app screen · genre: editorial · theme: brand · redesign: full
 * paper: #f7f5ef · accent: #23594f · display: Georgia · body: system-ui · nav: shared public header · footer: colophon · signature: native private-access form · posture: Restrained · v2.0.0 */
/* Hallmark · pre-emit critique: Public-site chrome, type scale and spacing unify the native sign-in form with Home. */
:root {{
  color-scheme: light;
  --background: #f7f5ef; --surface: #fffcf6; --ink: #252820;
  --muted: #62675c; --primary: #23594f; --primary-strong: #19443c;
  --line: #d8ddd3; --soft: #e9eeea; --error: #a52c25; --error-soft: #fff0ed;
  --font-body: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-heading: Georgia, "Times New Roman", "Songti SC", SimSun, serif;
  --radius: 6px; --container: 1120px; --text-hero: clamp(44px, 5.2vw, 68px);
}}
*, *::before, *::after {{ box-sizing: border-box; }}
html, body {{ overflow-x: clip; }}
html {{ scrollbar-color: var(--muted) var(--background); }}
body {{ min-height: 100vh; margin: 0; display: flex; flex-direction: column; background: var(--background); color: var(--ink); font-family: var(--font-body); font-size: 16px; line-height: 1.65; -webkit-font-smoothing: antialiased; caret-color: var(--primary); }}
.container {{ width: min(var(--container), calc(100% - 48px)); margin-inline: auto; }}
a {{ color: inherit; text-underline-offset: 4px; }}
.skip-link {{ position: fixed; z-index: 20; top: 8px; left: 8px; padding: 8px 12px; background: var(--ink); color: var(--surface); font-weight: 600; transform: translateY(-160%); }}
.skip-link:focus {{ transform: translateY(0); }}
.site-header {{ border-bottom: 1px solid var(--line); }}
.header-inner {{ min-height: 88px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; padding-block: 12px; }}
.brand {{ display: inline-flex; align-items: center; gap: 12px; min-width: max-content; font-size: 20px; font-weight: 600; text-decoration: none; }}
.mark {{ width: 32px; height: 32px; display: inline-block; position: relative; border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); }}
.mark::after {{ content: ""; position: absolute; top: 0; bottom: 0; left: 50%; width: 2px; background: var(--primary); }}
.site-nav {{ display: flex; flex: 1; align-items: center; justify-content: center; flex-wrap: wrap; gap: 32px; }}
.site-nav a, .header-action {{ min-height: 44px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 600; text-decoration: none; white-space: nowrap; }}
.site-nav a {{ color: var(--muted); }}
.site-nav a:hover {{ color: var(--primary); }}
.header-action {{ min-width: 88px; padding-inline: 16px; border: 1px solid var(--line); border-radius: var(--radius); color: var(--primary); }}
.header-action:hover {{ background: var(--soft); }}
main {{ flex: 1; padding-block: 80px; }}
.login-layout {{ display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); align-items: start; gap: 48px; }}
h1 {{ margin: 0; font-family: var(--font-heading); font-size: var(--text-hero); font-weight: 400; line-height: 1.12; letter-spacing: -0.025em; overflow-wrap: break-word; min-width: 0; text-wrap: balance; }}
.intro {{ margin: 24px 0 0; max-width: 35ch; color: var(--muted); font-size: 20px; text-wrap: pretty; }}
.login-panel {{ width: min(440px, 100%); justify-self: center; }}
form {{ display: grid; gap: 24px; }}
label {{ display: grid; gap: 8px; font-size: 14px; font-weight: 600; }}
input {{ min-height: 48px; width: 100%; border: 1px solid var(--muted); border-radius: var(--radius); padding: 12px; background: var(--surface); color: var(--ink); font: inherit; font-size: 16px; font-weight: 400; }}
button {{ min-height: 48px; border: 1px solid var(--primary); border-radius: var(--radius); padding: 12px 24px; background: var(--primary); color: var(--surface); font: inherit; font-weight: 600; cursor: pointer; white-space: nowrap; }}
button:hover, button:active {{ background: var(--primary-strong); border-color: var(--primary-strong); }}
button:disabled, input:disabled {{ opacity: 0.55; cursor: not-allowed; }}
a:hover {{ color: var(--primary-strong); }}
:focus-visible {{ outline: 3px solid var(--primary); outline-offset: 4px; }}
input:focus-visible {{ outline-offset: 2px; }}
.error {{ margin: 0 0 24px; padding: 16px; border: 1px solid var(--error); border-radius: var(--radius); background: var(--error-soft); color: var(--error); font-size: 14px; }}
input[aria-invalid="true"] {{ border-color: var(--error); }}
.required-note {{ margin: 0; color: var(--muted); font-size: 14px; }}
.site-footer {{ border-top: 1px solid var(--line); }}
.footer-inner {{ min-height: 96px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; padding-block: 24px; color: var(--muted); font-size: 14px; }}
.footer-inner a {{ min-height: 44px; display: inline-flex; align-items: center; color: var(--primary); font-weight: 600; white-space: nowrap; }}
::selection {{ background: var(--primary); color: var(--surface); }}
@media (max-width: 799px) {{
  .header-inner {{ min-height: 80px; }}
  .site-nav {{ flex: 0 0 100%; order: 3; justify-content: flex-start; gap: 24px; }}
  main {{ padding-block: 48px; }}
  .login-layout {{ grid-template-columns: minmax(0, 1fr); gap: 32px; }}
  .login-panel {{ justify-self: start; }}
}}
@media (max-width: 767px) {{ .container {{ width: calc(100% - 32px); }} }}
@media (max-width: 399px) {{ .brand {{ font-size: 16px; gap: 8px; }} .header-action {{ min-width: 76px; padding-inline: 12px; }} }}
@media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ animation: none !important; transition: none !important; scroll-behavior: auto !important; }} }}
  </style>
</head>
<body>
  <a class="skip-link" href="#mainContent">Skip to main content</a>
  <header class="site-header">
    <div class="header-inner container">
      <a class="brand" href="https://nsyprojects.com/" aria-label="NSY Projects home"><span class="mark" aria-hidden="true"></span><span>NSY Projects</span></a>
      <nav class="site-nav" aria-label="Primary navigation">
        <a href="https://nsyprojects.com/">Home</a>
        <a href="https://nsyprojects.com/about.html">About Me</a>
        <a href="https://nsyprojects.com/projects.html">Projects</a>
      </nav>
      <a class="header-action cancel-action" href="{cancel_url}">Cancel</a>
    </div>
  </header>
  <main id="mainContent" tabindex="-1" aria-labelledby="loginTitle" class="container">
    <div class="login-layout">
      <div class="login-intro">
        <h1 id="loginTitle">Sign in</h1>
        <p class="intro">Sign in to access private NSY Projects tools.</p>
      </div>
    <div class="login-panel">
      {error}
      <form method="post" action="/login">
        <input type="hidden" name="next" value="{next}">
        <label for="username">Username
          <input id="username" name="username" autocomplete="username" required aria-required="true" {username_focus} {field_error}>
        </label>
        <label for="password">Password
          <input id="password" name="password" type="password" autocomplete="current-password" required aria-required="true" {field_error}>
        </label>
        <button type="submit">Sign in</button>
        <p class="required-note">Both fields are required.</p>
      </form>
    </div>
    </div>
  </main>
  <footer class="site-footer">
    <div class="footer-inner container">
      <span>© {year} Shaoyang Ni</span>
      <a href="https://www.linkedin.com/in/naivee-ni/" target="_blank" rel="noreferrer">Connect on LinkedIn</a>
    </div>
  </footer>
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
    error_html = f'<p id="loginError" class="error" role="alert" tabindex="-1" autofocus>{html.escape(error)}</p>' if error else ""
    body = LOGIN_HTML.format(
        error=error_html,
        year=time.gmtime().tm_year,
        username_focus="" if error else "autofocus",
        field_error='aria-invalid="true" aria-describedby="loginError"' if error else "",
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
