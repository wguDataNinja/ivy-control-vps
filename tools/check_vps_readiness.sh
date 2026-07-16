#!/bin/sh
# check_vps_readiness.sh — Aggregated VPS control-plane readiness check
#
# Runs all VPS readiness checks and produces a structured report.
# This is the primary entry point for VPS readiness evaluation.
#
# Usage:
#   ./tools/check_vps_readiness.sh [--state-dir=<path>] [--format=text|json]

set -eu

die() { printf 'FATAL: %s\n' "$1" >&2; exit 1; }

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

# Source path classes
. "$SCRIPT_DIR/vps_paths.sh"

FORMAT="text"

while [ $# -gt 0 ]; do
    case "$1" in
        --state-dir=*) VPS_STATE_DIR="${1#*=}" ;;
        --state-dir)   VPS_STATE_DIR="${2:-}"; shift ;;
        --format=*)    FORMAT="${1#*=}" ;;
        --format)      FORMAT="${2:-}"; shift ;;
        --help|-h)
            cat <<HELP
Usage: $0 [options]
  --state-dir=<path>  Override VPS state directory
  --format=<fmt>      Output format: text (default) or json
HELP
            exit 0 ;;
        *) die "Unknown argument: $1" ;;
    esac
    shift
done

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%S 2>/dev/null || echo "unknown")

# ---- Run individual checks ----
printf '%s\n' '=== VPS Control-Plane Readiness Check ===' >&2
printf 'TIMESTAMP: %s\n' "$TIMESTAMP" >&2
printf 'REPO_ROOT: %s\n' "$REPO_ROOT" >&2
printf '\n' >&2

# 1. Path validation
printf '%s\n' '--- [1] Path Classes ---' >&2
vps_print_paths >&2
printf '\n' >&2

# 2. Exact SHA verification
if [ "$FORMAT" = "json" ]; then
    if "$SCRIPT_DIR/verify_exact_sha.sh" >/dev/null 2>&1; then SHA_RESULT="PASS"; else SHA_RESULT="FAIL"; fi
else
    printf '%s\n' '--- [2] Exact SHA / Clean Tree ---' >&2
    if "$SCRIPT_DIR/verify_exact_sha.sh" >&2 2>&1; then SHA_RESULT="PASS"; else SHA_RESULT="FAIL"; fi
    printf '\n' >&2
fi

# 3. Config validation
if [ "$FORMAT" = "json" ]; then
    if "$SCRIPT_DIR/validate_config.sh" >/dev/null 2>&1; then CONFIG_RESULT="PASS"; else CONFIG_RESULT="FAIL"; fi
else
    printf '%s\n' '--- [3] Config Validation ---' >&2
    if "$SCRIPT_DIR/validate_config.sh" >&2 2>&1; then CONFIG_RESULT="PASS"; else CONFIG_RESULT="FAIL"; fi
    printf '\n' >&2
fi

# 4. Deployed revision
if [ "$FORMAT" = "json" ]; then
    REVISION_OUTPUT=$("$SCRIPT_DIR/report_deployed_revision.sh" --format=json 2>/dev/null || echo '{"error":"deployed revision unavailable"}')
else
    printf '%s\n' '--- [4] Deployed Revision ---' >&2
    REVISION_OUTPUT=$("$SCRIPT_DIR/report_deployed_revision.sh" 2>&1 || true)
    printf '%s\n' "$REVISION_OUTPUT"
    printf '\n' >&2
fi

# 5. Upstream drift (informational, no pass/fail)
if [ "$FORMAT" != "json" ]; then
    printf '%s\n' '--- [5] Upstream Drift (fetch) ---' >&2
    DRIFT_OUTPUT=$("$SCRIPT_DIR/check_upstream_drift.sh" 2>&1 || true)
    printf '%s\n' "$DRIFT_OUTPUT"
    printf '\n' >&2
fi

# ---- Derive overall ----
OVERALL="FAIL"
if [ "$SHA_RESULT" = "PASS" ] && [ "$CONFIG_RESULT" = "PASS" ]; then
    OVERALL="PASS"
fi

if [ "$FORMAT" = "json" ]; then
    # REVISION_OUTPUT is already JSON from report_deployed_revision.sh --format=json
    printf '%s\n' "$REVISION_OUTPUT" | python3 -c "
import json, sys
rev = json.loads(sys.stdin.read())
status = json.dumps({
    'check_type': 'vps_control_plane_readiness',
    'timestamp': '$TIMESTAMP',
    'repo_root': '$REPO_ROOT',
    'state_dir': '$VPS_STATE_DIR',
    'results': {'sha_verification': '$SHA_RESULT', 'config_validation': '$CONFIG_RESULT'},
    'deployed': {
        'head_sha': rev.get('head_sha', 'unknown'),
        'branch': rev.get('branch', 'unknown'),
        'dirty': rev.get('dirty', 'unknown')
    },
    'overall': '$OVERALL'
}, indent=2)
print(status)
" 2>/dev/null || printf '{"error":"json generation failed"}\n'
else
    EXTRACT_SHA=$(printf '%s\n' "$REVISION_OUTPUT" | grep "^HEAD_SHA:" | cut -d' ' -f2- || echo "unknown")
    EXTRACT_BRANCH=$(printf '%s\n' "$REVISION_OUTPUT" | grep "^BRANCH:" | cut -d' ' -f2- || echo "unknown")
    EXTRACT_DIRTY=$(printf '%s\n' "$REVISION_OUTPUT" | grep "^DIRTY:" | cut -d' ' -f2- || echo "unknown")
    cat <<REPORT

=== Readiness Summary ===
OVERALL: $OVERALL
SHA_VERIFICATION: $SHA_RESULT
CONFIG_VALIDATION: $CONFIG_RESULT
DEPLOYED_SHA: $EXTRACT_SHA
BRANCH: $EXTRACT_BRANCH
DIRTY: $EXTRACT_DIRTY
REPORT
fi

exit 0
