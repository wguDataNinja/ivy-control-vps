#!/bin/sh
# report_deployed_revision.sh — Report current deployed revision
#
# Outputs a machine-readable summary of what is currently deployed at
# a git checkout. Suitable for ingestion by dashboard generators and
# Hermes drift checks.
#
# Usage:
#   ./tools/report_deployed_revision.sh [--checkout=<path>] [--format=text|json]

set -eu

die() { printf 'FATAL: %s\n' "$1" >&2; exit 1; }

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

CHECKOUT_PATH="$REPO_ROOT"
FORMAT="text"

while [ $# -gt 0 ]; do
    case "$1" in
        --checkout=*) CHECKOUT_PATH="${1#*=}" ;;
        --checkout)   CHECKOUT_PATH="${2:-}"; shift ;;
        --format=*)   FORMAT="${1#*=}" ;;
        --format)     FORMAT="${2:-}"; shift ;;
        --help|-h)
            cat <<HELP
Usage: $0 [options]
  --checkout=<path>  Path to git checkout (default: repo root)
  --format=<fmt>     Output format: text (default) or json
HELP
            exit 0 ;;
        *) die "Unknown argument: $1" ;;
    esac
    shift
done

cd "$CHECKOUT_PATH"
git rev-parse --git-dir >/dev/null 2>&1 || die "Not a git repository: $CHECKOUT_PATH"

HEAD_SHA=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
SHORT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "unknown")
DIRTY=$(git status --porcelain 2>/dev/null || echo "")
DIRTY_STATE="clean"
[ -n "$DIRTY" ] && DIRTY_STATE="dirty"
COMMIT_TIME=$(git log -1 --format="%cI" 2>/dev/null || echo "unknown")
COMMIT_MSG=$(git log -1 --format="%s" 2>/dev/null || echo "unknown")

if [ "$FORMAT" = "json" ]; then
    cat <<JSON
{
  "checkout_path": "$CHECKOUT_PATH",
  "head_sha": "$HEAD_SHA",
  "short_sha": "$SHORT_SHA",
  "branch": "$BRANCH",
  "remote_url": "$REMOTE_URL",
  "dirty": "$DIRTY_STATE",
  "commit_time": "$COMMIT_TIME",
  "commit_message": "$COMMIT_MSG"
}
JSON
else
    cat <<REPORT
CHECKOUT: $CHECKOUT_PATH
HEAD_SHA: $HEAD_SHA
SHORT_SHA: $SHORT_SHA
BRANCH: $BRANCH
REMOTE: $REMOTE_URL
DIRTY: $DIRTY_STATE
COMMIT_TIME: $COMMIT_TIME
COMMIT_MSG: $COMMIT_MSG
REPORT
fi

exit 0
