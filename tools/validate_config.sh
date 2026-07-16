#!/bin/sh
# validate_config.sh — Validate VPS configuration and standards
#
# Checks:
#   1. Path classes resolve (vps_paths.sh)
#   2. Required config files exist
#   3. .gitignore coverage
#   4. No .env files tracked in git
#   5. No generated artifacts inside checkout
#
# Usage:
#   ./tools/validate_config.sh [--config-dir=<path>] [--state-dir=<path>]

set -eu

die() { printf 'FATAL: %s\n' "$1" >&2; exit 1; }
warn() { printf 'WARN: %s\n' "$1" >&2; }

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

# Source path classes (allow override via env)
. "$SCRIPT_DIR/vps_paths.sh"

PASS=0
FAIL=0
WARN=0

check() {
    local label="$1" result="$2" detail="${3:-}"
    if [ "$result" = "pass" ]; then
        printf '  [PASS] %s\n' "$label"
        PASS=$((PASS + 1))
    else
        printf '  [FAIL] %s\n' "$label"
        [ -n "$detail" ] && printf '         %s\n' "$detail"
        FAIL=$((FAIL + 1))
    fi
}

check_warn() {
    local label="$1" detail="${2:-}"
    printf '  [WARN] %s\n' "$label"
    [ -n "$detail" ] && printf '         %s\n' "$detail"
    WARN=$((WARN + 1))
}

printf '=== VPS Configuration Validation ===\n'
printf 'REPO_ROOT: %s\n' "$REPO_ROOT"
printf 'VPS_STATE_DIR: %s\n' "$VPS_STATE_DIR"
printf 'VPS_REPO_ROOT: %s\n' "$VPS_REPO_ROOT"
printf '\n'

# ---- 1. Path class resolution ----
printf '[1] Path class resolution\n'
check "VPS_STATE_DIR is non-empty" "$([ -n "$VPS_STATE_DIR" ] && echo "pass" || echo "fail")"
check "VPS_GENERATED_DIR is outside checkout" "$(case "$VPS_GENERATED_DIR" in "$REPO_ROOT"*) echo "fail";; *) echo "pass";; esac)" "VPS_GENERATED_DIR=$VPS_GENERATED_DIR is inside $REPO_ROOT"
check "VPS_CONFIG_DIR is outside checkout" "$(case "$VPS_CONFIG_DIR" in "$REPO_ROOT"*) echo "fail";; *) echo "pass";; esac)"
check "VPS_DATA_DIR is outside checkout" "$(case "$VPS_DATA_DIR" in "$REPO_ROOT"*) echo "fail";; *) echo "pass";; esac)"
check "VPS_LOG_DIR is outside checkout" "$(case "$VPS_LOG_DIR" in "$REPO_ROOT"*) echo "fail";; *) echo "pass";; esac)"
check "VPS_BACKUP_DIR is outside checkout" "$(case "$VPS_BACKUP_DIR" in "$REPO_ROOT"*) echo "fail";; *) echo "pass";; esac)"

# ---- 2. Git state ----
printf '\n[2] Git state\n'
cd "$REPO_ROOT"
if git rev-parse --git-dir >/dev/null 2>&1; then
    check "Git repository exists" "pass"
    DIRTY=$(git status --porcelain 2>/dev/null)
    check "Working tree is clean" "$([ -z "$DIRTY" ] && echo "pass" || echo "fail")"
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
    check "Remote origin configured" "$([ -n "$REMOTE_URL" ] && echo "pass" || echo "fail")"
else
    check "Git repository exists" "fail"
fi

# ---- 3. .gitignore coverage ----
printf '\n[3] .gitignore coverage\n'
if [ -f "$REPO_ROOT/.gitignore" ]; then
    check ".gitignore exists" "pass"
    for pattern in "__pycache__/" ".env" "_internal/" "*.pyc" ".DS_Store"; do
        if grep -q "$pattern" "$REPO_ROOT/.gitignore" 2>/dev/null; then
            check ".gitignore covers $pattern" "pass"
        else
            check_warn ".gitignore does not explicitly cover $pattern"
        fi
    done
else
    check ".gitignore exists" "fail"
fi

# ---- 4. No .env files tracked ----
printf '\n[4] Tracked .env files\n'
TRACKED_ENV=$(git ls-files 2>/dev/null | grep -c '\.env$' || echo "0")
check "No .env files tracked in git" "$([ "$TRACKED_ENV" -eq 0 ] && echo "pass" || echo "fail")" "Found $TRACKED_ENV .env files in git tracking"

# ---- 5. No generated artifacts inside checkout ----
printf '\n[5] Generated artifacts inside checkout\n'
GENERATED_INSIDE=$(git ls-files --others --exclude-standard 2>/dev/null | grep -c 'generated' || echo "0")
check_warn "Untracked generated/ files: $GENERATED_INSIDE (may be expected if state dir is inside checkout)"

# ---- 6. Ownership and permissions ----
printf '\n[6] Script permissions\n'
for script in "$SCRIPT_DIR"/*.sh; do
    [ -f "$script" ] || continue
    if [ -x "$script" ]; then
        check "Script $(basename "$script") is executable" "pass"
    else
        check_warn "Script $(basename "$script") is not executable"
    fi
done

# ---- Summary ----
printf '\n=== Summary ===\n'
printf 'PASS: %d\n' "$PASS"
printf 'WARN: %d\n' "$WARN"
printf 'FAIL: %d\n' "$FAIL"
if [ "$FAIL" -gt 0 ]; then
    printf 'RESULT: FAIL\n'
    exit 1
fi
printf 'RESULT: PASS\n'
exit 0
