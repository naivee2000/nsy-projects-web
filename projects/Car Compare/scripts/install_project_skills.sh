#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
TARGET_DIR="$CODEX_HOME/skills"

mkdir -p "$TARGET_DIR"
for skill in generation-impact-research collect-car-marketplaces; do
  rsync -a --delete "$PROJECT_ROOT/skills/$skill/" "$TARGET_DIR/$skill/"
  echo "Installed $skill to $TARGET_DIR/$skill"
done
