#!/usr/bin/env python3
"""Chinese DEM app entry point with session-cookie authentication."""

from __future__ import annotations

import os

import uvicorn
from app_zh import app
from auth_gate import install_auth


install_auth(app)


if __name__ == "__main__":
    uvicorn.run("app_zh_secure:app", host="127.0.0.1", port=int(os.environ.get("PORT", "8000")), reload=False)
