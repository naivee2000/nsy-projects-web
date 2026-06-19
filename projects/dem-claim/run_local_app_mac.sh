#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$ROOT_DIR/app"

if [ ! -d "$APP_DIR" ]; then
  APP_DIR="$ROOT_DIR"
fi

cd "$APP_DIR"

if [ ! -x ".venv/bin/python" ]; then
  echo "Missing .venv. Run: python3 -m venv .venv && ./.venv/bin/python -m pip install -r requirements.txt" >&2
  exit 1
fi

export DEM_SKILL_ROOT="${DEM_SKILL_ROOT:-$HOME/.codex/skills/dem-claim-excel}"
export DEM_JOB_ROOT="${DEM_JOB_ROOT:-$APP_DIR/web_outputs}"
export CODEX_BIN="${CODEX_BIN:-/Applications/Codex.app/Contents/Resources/codex}"
export PORT="${PORT:-8000}"

exec ./.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port "$PORT"
