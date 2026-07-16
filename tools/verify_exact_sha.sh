#!/bin/sh
# verify_exact_sha.sh — Exact-SHA and clean-tree verification
#
# Verifies:
#   1. Working tree is clean (no dirty tracked files)
#   2. HEAD matches expected SHA
#   3. Remote origin is as expected
#   4. No untracked files that should be tracked (optional)
#
# Usage:
#   ./tools/verify_exact_sha.sh [--expected-sha=<sha>] [--checkout=<path>]
#   ./tools/verify_exact_sha.sh --remote-url <expected-url>

set -eu

die() { printf 'FATAL: %s\n' "$1" >&2; exit 1; }

# ---- Paths ----
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

# ---- Parse args ----
EXPECTED_SHA=""
EXPECTED_REMOTE=""
CHECKOUT_PATH="$REPO_ROOT"

while [ $# -gt 0 ]; do
    case "$1" in
        --expected-sha=*) EXPECTED_SHA="${1#*=}" ;;
        --expected-sha)   EXPECTED_SHA="${2:-}"; shift ;;
        --remote-url=*)   EXPECTED_REMOTE="${1#*=}" ;;
        --remote-url)     EXPECTED_REMOTE="${2:-}"; shift ;;
        --checkout=*)     CHECKOUT_PATH="${1#*=}" ;;
        --checkout)       CHECKOUT_PATH="${2:-}"; shift ;;
        --help|-h)
            cat <<HELP
Usage: $0 [options]
  --expected-sha=<sha>  Require HEAD to match this exact SHA
  --remote-url=<url>    Require origin remote to match this URL
  --checkout=<path>     Path to git checkout (default: repo root)
HELP
            exit 0 ;;
        *) die "Unknown argument: $1" ;;
    esac
    shift
done

cd "$CHECKOUT_PATH"

# ---- 1. Clean tree check ----
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    die "Not a git repository: $CHECKOUT_PATH"
fi

DIRTY=$(git status --porcelain 2>/dev/null)
if [ -n "$DIRTY" ]; then
    printf 'DIRTY: Working tree has uncommitted changes:\n%s\n' "$DIRTY"
    printf 'RESULT: FAIL (dirty)\n'
    exit 1
fi
printf 'CLEAN: Working tree is clean\n'

# ---- 2. Exact SHA check ----
HEAD_SHA=$(git rev-parse HEAD 2>/dev/null || die "Cannot resolve HEAD")
printf 'HEAD: %s\n' "$HEAD_SHA"

if [ -n "$EXPECTED_SHA" ]; then
    if [ "$HEAD_SHA" != "$EXPECTED_SHA" ]; then
        printf 'SHA_MISMATCH: Expected %s, got %s\n' "$EXPECTED_SHA" "$HEAD_SHA"
        printf 'RESULT: FAIL (sha-mismatch)\n'
        exit 1
    fi
    printf 'SHA_MATCH: HEAD matches expected SHA %s\n' "$EXPECTED_SHA"
fi

# ---- 3. Remote origin check ----
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ -n "$EXPECTED_REMOTE" ]; then
    if [ "$REMOTE_URL" != "$EXPECTED_REMOTE" ]; then
        printf 'REMOTE_MISMATCH: Expected %s, got %s\n' "$EXPECTED_REMOTE" "$REMOTE_URL"
        printf 'RESULT: FAIL (remote-mismatch)\n'
        exit 1
    fi
    printf 'REMOTE_MATCH: origin matches %s\n' "$EXPECTED_REMOTE"
fi

# ---- 4. Show branch ----
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
printf 'BRANCH: %s\n' "$BRANCH"

printf 'RESULT: PASS\n'
exit 0
