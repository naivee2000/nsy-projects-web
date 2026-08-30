#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DB="$APP_DIR/data/code_practice.db"
BACKUP_DIR="$APP_DIR/backups"

if [[ ! -f "$SOURCE_DB" ]]; then
  echo "No database exists yet at $SOURCE_DB"
  exit 1
fi

mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d-%H%M%S)"
sqlite3 "$SOURCE_DB" ".backup '$BACKUP_DIR/code-practice-$STAMP.db'"
echo "Backup created: $BACKUP_DIR/code-practice-$STAMP.db"

