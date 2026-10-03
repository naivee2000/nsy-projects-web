#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="${CODE_PRACTICE_DATA_DIR:-$APP_DIR/data}"
SOURCE_DB="${CODE_PRACTICE_DB:-$DATA_DIR/code_practice.db}"
BACKUP_DIR="${CODE_PRACTICE_BACKUP_DIR:-$APP_DIR/backups}"

if [[ ! -f "$SOURCE_DB" ]]; then
  echo "No database exists yet at $SOURCE_DB"
  exit 1
fi

mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d-%H%M%S)"
if [[ -f "$DATA_DIR/accounts.db" ]]; then
  cd "$APP_DIR"
  CODE_PRACTICE_DATA_DIR="$DATA_DIR" CODE_PRACTICE_DB="$SOURCE_DB" \
    "$APP_DIR/.venv/bin/python" -m code_practice.accounts backup "$BACKUP_DIR/code-practice-$STAMP"
  exit 0
fi
sqlite3 "$SOURCE_DB" ".backup '$BACKUP_DIR/code-practice-$STAMP.db'"
echo "Backup created: $BACKUP_DIR/code-practice-$STAMP.db"
