#!/usr/bin/env python3
"""Start the local Auto CAD Drawing web app."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
import webbrowser


ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"

if VENV_PYTHON.exists() and Path(sys.prefix).resolve() != VENV_DIR.resolve():
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])

try:
    import uvicorn
except ModuleNotFoundError as exc:
    if exc.name != "uvicorn":
        raise
    raise SystemExit(
        "uvicorn is not installed for this Python.\n\n"
        "Run these commands once:\n"
        f'cd "{ROOT}"\n'
        "python3 -m venv .venv\n"
        "source .venv/bin/activate\n"
        "python -m pip install -r requirements.txt\n\n"
        "Then start the app with:\n"
        "python app.py"
    ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8008)
    parser.add_argument("--reload", action="store_true", help="Restart automatically after code changes.")
    parser.add_argument("--open", action="store_true", help="Open the app in the default browser.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    url = f"http://{args.host}:{args.port}"
    print(f"Auto CAD Drawing: {url}")
    if args.open:
        webbrowser.open(url)
    uvicorn.run("web.app:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
