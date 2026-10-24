"""Loopback-only preview of the real sign-in template using disposable credentials.

Run with the project's virtualenv: python preview_login.py --port 8788.
This creates no files and does not import the DEM processing app or production ops config.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import secrets

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

import auth_gate as auth


def create_preview_app() -> FastAPI:
    encode = lambda value: base64.urlsafe_b64encode(value).decode().rstrip('=')
    salt = b'nsy-disposable-preview'
    password_hash = encode(hashlib.pbkdf2_hmac('sha256', b'preview-only', salt, 1000))
    auth.AUTH_USERNAME = 'preview'
    auth.AUTH_PASSWORD_HASH = f'pbkdf2_sha256$1000${encode(salt)}${password_hash}'
    auth.AUTH_SESSION_SECRET = secrets.token_urlsafe(32)
    auth.AUTH_COOKIE_NAME = 'nsy_preview_session'
    auth.SIGNED_IN_COOKIE_NAME = 'nsy_preview_signed_in'
    auth.AUTH_COOKIE_DOMAIN = None
    auth.AUTH_COOKIE_SECURE = False
    auth.AUTH_ENABLED = True
    app = FastAPI(title='Local sign-in preview')
    auth.install_auth(app)

    @app.get('/', response_class=HTMLResponse)
    def signed_in() -> str:
        return '<h1>Preview sign-in succeeded</h1><p><a href="/logout?next=/">Sign out</a></p>'

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8788)
    args = parser.parse_args()
    print(f'Preview: http://127.0.0.1:{args.port}/login', flush=True)
    print('Disposable credentials: preview / preview-only. Never use these for deployment.', flush=True)
    uvicorn.run(create_preview_app(), host='127.0.0.1', port=args.port)


if __name__ == '__main__':
    main()
