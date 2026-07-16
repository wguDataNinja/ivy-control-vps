#!/usr/bin/env bash
# show_portfolio_status.sh — Operator-readable portfolio registry table.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$DIR/portfolio_registry.py" --table "$@"
