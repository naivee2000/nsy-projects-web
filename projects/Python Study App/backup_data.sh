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
sqlite3 "$SOURCE_DB" ".backup '$BACKUP_DIR/code-practice-$STAMP.db'"
echo "Backup created: $BACKUP_DIR/code-practice-$STAMP.db"
