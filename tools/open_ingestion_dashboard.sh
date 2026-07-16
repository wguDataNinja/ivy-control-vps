#!/bin/sh
# Generate a private read-only ingestion dashboard and open it in a browser.
# Supports macOS (open), Linux (xdg-open), and fallback to path print.
# Passes unknown flags through to ingestion_dashboard.py (--mode, --host, --no-live, --json, --output-dir).
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON=${PYTHON:-python3}
NO_OPEN=false
PASSTHROUGH=""

for arg in "$@"; do
  case "$arg" in
    --no-open) NO_OPEN=true ;;
    *) PASSTHROUGH="$PASSTHROUGH $arg" ;;
  esac
done

# shellcheck disable=SC2086
HTML=$($PYTHON "$ROOT/tools/ingestion_dashboard.py" $PASSTHROUGH)
printf 'Dashboard: %s\n' "$HTML"

if $NO_OPEN; then
  exit 0
fi
if command -v open >/dev/null 2>&1; then
  open "$HTML"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$HTML"
else
  printf 'Generated dashboard; open the printed file path manually.\n' >&2
fi
