#!/bin/sh
# plan_rollback.sh — Plan a rollback to a prior approved SHA
#
# This tool does NOT execute the rollback. It inspects the current state
# and reports what would be needed to roll back to a given SHA.
#
# Usage:
#   ./tools/plan_rollback.sh [--target-sha=<sha>] [--checkout=<path>]
#   ./tools/plan_rollback.sh --sha-registry <path>

set -eu

die() { printf 'FATAL: %s\n' "$1" >&2; exit 1; }

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

CHECKOUT_PATH="$REPO_ROOT"
TARGET_SHA=""
SHA_REGISTRY=""

while [ $# -gt 0 ]; do
    case "$1" in
        --target-sha=*)  TARGET_SHA="${1#*=}" ;;
        --target-sha)    TARGET_SHA="${2:-}"; shift ;;
        --checkout=*)    CHECKOUT_PATH="${1#*=}" ;;
        --checkout)      CHECKOUT_PATH="${2:-}"; shift ;;
        --sha-registry=*) SHA_REGISTRY="${1#*=}" ;;
        --sha-registry)   SHA_REGISTRY="${2:-}"; shift ;;
        --help|-h)
            cat <<HELP
Usage: $0 [options]
  --target-sha=<sha>   The commit SHA to roll back to
  --checkout=<path>    Path to git checkout (default: repo root)
  --sha-registry=<path> Path to SHA registry JSON file
HELP
            exit 0 ;;
        *) die "Unknown argument: $1" ;;
    esac
    shift
done

cd "$CHECKOUT_PATH"
git rev-parse --git-dir >/dev/null 2>&1 || die "Not a git repository: $CHECKOUT_PATH"

CURRENT_SHA=$(git rev-parse HEAD 2>/dev/null || die "Cannot resolve HEAD")
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
DIRTY=$(git status --porcelain 2>/dev/null || echo "")

printf '=== Rollback Plan ===\n'
printf 'CHECKOUT: %s\n' "$CHECKOUT_PATH"
printf 'CURRENT_SHA: %s\n' "$CURRENT_SHA"
printf 'CURRENT_BRANCH: %s\n' "$CURRENT_BRANCH"

if [ -n "$DIRTY" ]; then
    printf 'WARNING: Working tree is dirty. Commit or stash before rollback.\n'
fi

# ---- Look up SHA registry ----
if [ -n "$SHA_REGISTRY" ] && [ -f "$SHA_REGISTRY" ]; then
    printf '\nSHA REGISTRY: %s\n' "$SHA_REGISTRY"
    # shellcheck disable=SC2016
    python3 -c "
import json, sys
try:
    with open('$SHA_REGISTRY') as f:
        data = json.load(f)
    if isinstance(data, dict):
        for k, v in data.items():
            print(f'  {k}: {v}')
    elif isinstance(data, list):
        for item in data:
            print(f'  {item}')
except Exception as e:
    print(f'  (parse error: {e})')
" 2>/dev/null || printf '  (unreadable or invalid JSON)\n'
fi

# ---- Check if target SHA exists locally ----
if [ -n "$TARGET_SHA" ]; then
    printf '\nTARGET_SHA: %s\n' "$TARGET_SHA"

    if git cat-file -e "$TARGET_SHA" 2>/dev/null; then
        printf 'TARGET_STATUS: available in local object store\n'
        TARGET_BRANCH=$(git branch --contains "$TARGET_SHA" 2>/dev/null | head -1 || echo "")
        [ -n "$TARGET_BRANCH" ] && printf 'TARGET_BRANCH: %s\n' "$TARGET_BRANCH"
        TARGET_TIME=$(git log -1 --format="%cI" "$TARGET_SHA" 2>/dev/null || echo "unknown")
        TARGET_MSG=$(git log -1 --format="%s" "$TARGET_SHA" 2>/dev/null || echo "unknown")
        printf 'TARGET_TIME: %s\n' "$TARGET_TIME"
        printf 'TARGET_MSG: %s\n' "$TARGET_MSG"
    else
        printf 'TARGET_STATUS: NOT available locally — must fetch from remote\n'
    fi

    # ---- Check ancestry ----
    if git merge-base --is-ancestor "$TARGET_SHA" HEAD 2>/dev/null; then
        printf 'ROLLBACK_TYPE: fast-forward (reverse) — target is behind HEAD\n'
        printf 'ROLLBACK_CMD:  git checkout %s\n' "$TARGET_SHA"
    elif git merge-base --is-ancestor HEAD "$TARGET_SHA" 2>/dev/null; then
        printf 'ROLLBACK_TYPE: forward — target is ahead of HEAD (not a rollback)\n'
    else
        printf 'ROLLBACK_TYPE: divergent — target is on a different branch lineage\n'
        printf 'ROLLBACK_CMD:  git checkout %s  (may lose commits not in target ancestry)\n' "$TARGET_SHA"
    fi
else
    printf '\nNo target SHA specified. Use --target-sha to plan a specific rollback.\n'
fi

printf '\nNOTE: This is a planning report only. No changes were made.\n'
exit 0
