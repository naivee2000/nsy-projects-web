#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="${CODE_PRACTICE_DATA_DIR:-$APP_DIR/data}"
SOURCE_DB="${CODE_PRACTICE_DB:-$DATA_DIR/code_practice.db}"
SEED_DIR="$APP_DIR/seed_data"
SEED_DB="$SEED_DIR/initial_progress.db"

if [[ ! -f "$SOURCE_DB" ]]; then
  echo "No progress database exists at $SOURCE_DB"
  exit 1
fi

mkdir -p "$SEED_DIR"
TEMP_DB="$(mktemp "$SEED_DIR/.initial-progress.XXXXXX.db")"
cleanup() {
  rm -f "$TEMP_DB"
}
trap cleanup EXIT

sqlite3 "$SOURCE_DB" ".backup '$TEMP_DB'"
INTEGRITY="$(sqlite3 "$TEMP_DB" "PRAGMA integrity_check;")"
if [[ "$INTEGRITY" != "ok" ]]; then
  echo "Seed creation failed SQLite integrity validation: $INTEGRITY"
  exit 1
fi

mv "$TEMP_DB" "$SEED_DB"
trap - EXIT

ATTEMPTS="$(sqlite3 "$SEED_DB" "SELECT COUNT(*) FROM attempts;")"
DRAFTS="$(sqlite3 "$SEED_DB" "SELECT COUNT(*) FROM drafts;")"
REVIEWS="$(sqlite3 "$SEED_DB" "SELECT COUNT(*) FROM review_states;")"
echo "Progress seed refreshed: $SEED_DB"
echo "Included $ATTEMPTS attempts, $DRAFTS drafts, and $REVIEWS review states."
