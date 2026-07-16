#!/bin/sh
# Generate a private read-only ingestion dashboard and open it on macOS.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PYTHON=${PYTHON:-python3}
HTML=$($PYTHON "$ROOT/tools/ingestion_dashboard.py")
printf 'Dashboard: %s\n' "$HTML"

if [ "${1:-}" = "--no-open" ]; then
  exit 0
fi
if [ "$#" -ne 0 ]; then
  printf 'Usage: %s [--no-open]\n' "$0" >&2
  exit 2
fi
if command -v open >/dev/null 2>&1; then
  open "$HTML"
else
  printf 'Generated dashboard; open the printed file path manually.\n' >&2
fi
