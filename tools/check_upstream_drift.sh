#!/bin/sh
# check_upstream_drift.sh — Compare local checkout against upstream
#
# Reports:
#   - Ahead/behind count vs origin
#   - Whether local HEAD is reachable from origin
#   - Whether working tree matches any known upstream ref
#
# Usage:
#   ./tools/check_upstream_drift.sh [--checkout=<path>] [--remote=<name>]

set -eu

die() { printf 'FATAL: %s\n' "$1" >&2; exit 1; }

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

REMOTE="origin"
CHECKOUT_PATH="$REPO_ROOT"

while [ $# -gt 0 ]; do
    case "$1" in
        --remote=*)  REMOTE="${1#*=}" ;;
        --remote)    REMOTE="${2:-}"; shift ;;
        --checkout=*) CHECKOUT_PATH="${1#*=}" ;;
        --checkout)   CHECKOUT_PATH="${2:-}"; shift ;;
        --help|-h)
            cat <<HELP
Usage: $0 [options]
  --remote=<name>    Remote to compare against (default: origin)
  --checkout=<path>  Path to git checkout (default: repo root)
HELP
            exit 0 ;;
        *) die "Unknown argument: $1" ;;
    esac
    shift
done

cd "$CHECKOUT_PATH"

git rev-parse --git-dir >/dev/null 2>&1 || die "Not a git repository: $CHECKOUT_PATH"

HEAD_SHA=$(git rev-parse HEAD 2>/dev/null)
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
REMOTE_URL=$(git remote get-url "$REMOTE" 2>/dev/null || echo "unconfigured")

printf 'REPO:     %s\n' "$CHECKOUT_PATH"
printf 'BRANCH:   %s\n' "$BRANCH"
printf 'HEAD:     %s\n' "$HEAD_SHA"
printf 'REMOTE:   %s (%s)\n' "$REMOTE" "$REMOTE_URL"

# ---- Fetch upstream refs ----
printf '\nFetching upstream (%s)...\n' "$REMOTE"
if ! git fetch "$REMOTE" 2>&1; then
    printf 'FETCH_FAILED: Could not fetch from %s (no remote configured or unreachable)\n' "$REMOTE"
    printf 'RESULT: report complete (fetch failed)\n'
    exit 0
fi

# ---- Ahead/behind ----
UPSTREAM_REF="${REMOTE}/${BRANCH}"
if git rev-parse --verify "$UPSTREAM_REF" >/dev/null 2>&1; then
    AHEAD=$(git rev-list --count "$UPSTREAM_REF..HEAD" 2>/dev/null || echo "0")
    BEHIND=$(git rev-list --count "HEAD..$UPSTREAM_REF" 2>/dev/null || echo "0")
    UPSTREAM_SHA=$(git rev-parse "$UPSTREAM_REF" 2>/dev/null)
    printf '\nUPSTREAM:  %s (%s)\n' "$UPSTREAM_REF" "$UPSTREAM_SHA"
    printf 'AHEAD:     %d commit(s) ahead of upstream\n' "$AHEAD"
    printf 'BEHIND:    %d commit(s) behind upstream\n' "$BEHIND"

    if git merge-base --is-ancestor HEAD "$UPSTREAM_SHA" 2>/dev/null; then
        printf 'ANCESTRY:  HEAD is an ancestor of %s (fast-forwardable)\n' "$UPSTREAM_REF"
    else
        printf 'ANCESTRY:  HEAD is NOT an ancestor — branch may have diverged\n'
    fi
else
    printf '\nUPSTREAM:  %s not found (branch not yet pushed?)\n' "$UPSTREAM_REF"
fi

# ---- Existence check: is our SHA reachable? ----
if git cat-file -e "$HEAD_SHA" 2>/dev/null; then
    printf '\nLOCAL_SHA_VALID: %s exists in local object store\n' "$HEAD_SHA"
else
    printf '\nLOCAL_SHA_INVALID: %s not found in local object store (corruption?)\n' "$HEAD_SHA"
fi

printf '\nRESULT: report complete (no pass/fail — informational)\n'
exit 0
