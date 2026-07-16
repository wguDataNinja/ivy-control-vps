#!/usr/bin/env bash
# validate_portfolio_controls.sh — Run all registry validation rules.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
echo "=== Portfolio Control Validation ==="
echo ""
python3 "$DIR/portfolio_registry.py" --validate "$@"
