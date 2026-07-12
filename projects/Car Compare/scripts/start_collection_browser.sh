#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${CAR_COMPARE_BROWSER_DEBUG_PORT:-9222}"
PROFILE="${CAR_COMPARE_BROWSER_PROFILE:-$ROOT/data/browser-profile}"
LOG_DIR="$ROOT/ops/logs"

if [[ -n "${CAR_COMPARE_BROWSER_EXECUTABLE:-}" ]]; then
  BROWSER="$CAR_COMPARE_BROWSER_EXECUTABLE"
elif [[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
  BROWSER="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif command -v google-chrome >/dev/null 2>&1; then
  BROWSER="$(command -v google-chrome)"
elif command -v chromium >/dev/null 2>&1; then
  BROWSER="$(command -v chromium)"
elif command -v chromium-browser >/dev/null 2>&1; then
  BROWSER="$(command -v chromium-browser)"
else
  echo "No Chrome/Chromium executable found. Install Chromium or set CAR_COMPARE_BROWSER_EXECUTABLE." >&2
  exit 1
fi

mkdir -p "$PROFILE" "$LOG_DIR"
ARGS=(
  "--remote-debugging-address=127.0.0.1"
  "--remote-debugging-port=$PORT"
  "--user-data-dir=$PROFILE"
  "--no-first-run"
  "--no-default-browser-check"
  "about:blank"
)

if [[ "$(uname -s)" == "Darwin" && "$BROWSER" == "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
  open -na "Google Chrome" --args "${ARGS[@]}"
  BROWSER_PID="$(pgrep -n -f "remote-debugging-port=$PORT" || true)"
elif [[ "$(uname -s)" == "Linux" && -z "${DISPLAY:-}" ]]; then
  if ! command -v xvfb-run >/dev/null 2>&1; then
    echo "A visible browser is recommended for marketplace access. Install xvfb or provide DISPLAY." >&2
    exit 1
  fi
  nohup xvfb-run -a "$BROWSER" "${ARGS[@]}" >"$LOG_DIR/collection-browser.log" 2>&1 &
  BROWSER_PID="$!"
else
  nohup "$BROWSER" "${ARGS[@]}" >"$LOG_DIR/collection-browser.log" 2>&1 &
  BROWSER_PID="$!"
fi

echo "Collection browser started${BROWSER_PID:+ with PID $BROWSER_PID}."
echo "Set CAR_COMPARE_BROWSER_CDP_URL=http://127.0.0.1:$PORT for the Car Compare backend."
