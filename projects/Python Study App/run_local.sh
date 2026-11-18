#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
fi

if [[ ! -d frontend/node_modules ]]; then
  npm --prefix frontend install
fi

# The website service may serve frontend/dist directly from this checkout.
export CODE_PRACTICE_FRONTEND_DIST="$APP_DIR/frontend/dist-local"
npm --prefix frontend run build -- --outDir "$CODE_PRACTICE_FRONTEND_DIST"

mkdir -p data
echo "Code Practice Lab is available at http://127.0.0.1:8765"
exec .venv/bin/python -m uvicorn code_practice.app:app --host 127.0.0.1 --port 8765
