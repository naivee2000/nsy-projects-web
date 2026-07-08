#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
TARGET_DIR="$CODEX_HOME/skills"

mkdir -p "$TARGET_DIR"
rsync -a --delete "$PROJECT_ROOT/skills/generation-impact-research/" "$TARGET_DIR/generation-impact-research/"

echo "Installed generation-impact-research to $TARGET_DIR/generation-impact-research"
