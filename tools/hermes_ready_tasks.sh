#!/usr/bin/env bash
# Hermes ready-task scanner — read-only, no mutations.
# Discover Hermes-eligible tasks from repos/<repo>/CONTROL.md files.
# Usage: ./tools/hermes_ready_tasks.sh [--format table|json|markdown] [--repo <name>]
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FORMAT="table"
REPO_FILTER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --format) FORMAT="$2"; shift 2 ;;
        --repo) REPO_FILTER="$2"; shift 2 ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

declare -a RESULTS=()

for ctrl in "$REPO_ROOT"/repos/*/CONTROL.md; do
    [ -f "$ctrl" ] || continue
    REPO_NAME=$(basename "$(dirname "$ctrl")")
    [ -n "$REPO_FILTER" ] && [ "$REPO_NAME" != "$REPO_FILTER" ] && continue

    LIFECYCLE=$(grep -E '^\*\*Lifecycle' "$ctrl" 2>/dev/null | sed -E 's/^\*\*Lifecycle[^*]*\*\*:?\s*//' | sed -E 's/[`"'"'"']//g' | head -1 || true)
    if [ -z "$LIFECYCLE" ]; then
        # Fallback: parse Gate 6 from ## Portfolio Admission State table
        GATE6=$(awk '/^## Portfolio Admission State/{flag=1; next} /^## /{flag=0} flag' "$ctrl" 2>/dev/null | grep -i '6.*Operational' | head -1 || true)
        case "$GATE6" in
            *PASS*) LIFECYCLE="production-active" ;;
            *BLOCKED*) LIFECYCLE="production-degraded" ;;
            *CONDITION*) LIFECYCLE="production-stabilizing" ;;
            *UNDEFINED*) LIFECYCLE="readiness-pending" ;;
            *) LIFECYCLE="unknown" ;;
        esac
    fi
    [ -z "$LIFECYCLE" ] && LIFECYCLE="unknown"

    BLOCKER=""
    if grep -q '^## Current Blocker' "$ctrl" 2>/dev/null; then
        BLOCKER=$(awk '/^## Current Blocker/{flag=1; next} /^## /{flag=0} flag' "$ctrl" 2>/dev/null | grep -v '^[[:space:]]*$' | head -3 | tr '\n' ' ' | xargs || true)
        [ -z "$BLOCKER" ] && BLOCKER="present (see CONTROL.md)"
    fi
    [ -z "$BLOCKER" ] && BLOCKER="none"

    NEXT_WORK=$(awk '/^## Next Authorized (Work|Phase)/{flag=1; next} flag && NF{print; exit}' "$ctrl" 2>/dev/null | head -c 80 || true)
    [ -z "$NEXT_WORK" ] && NEXT_WORK="(not defined)"

    PERMISSION="inspect"
    case "$LIFECYCLE" in
        *readiness*|*admission*)
            PERMISSION="admit"
            ;;
        *stabilizing*)
            PERMISSION="inspect+report"
            ;;
        *degraded*)
            PERMISSION="inspect"
            ;;
        *complete*|*active*)
            PERMISSION="inspect+report"
            [ "$BLOCKER" = "none" ] && PERMISSION="inspect+report+propose"
            ;;
    esac

    RESULTS+=("$REPO_NAME|$LIFECYCLE|$PERMISSION|$BLOCKER|$NEXT_WORK")
done

for repo_dir in "$REPO_ROOT"/repos/*/; do
    [ -d "$repo_dir" ] || continue
    REPO_NAME=$(basename "$repo_dir")
    [ -f "$repo_dir/CONTROL.md" ] && continue
    [ -n "$REPO_FILTER" ] && [ "$REPO_NAME" != "$REPO_FILTER" ] && continue
    RESULTS+=("$REPO_NAME|no_control_sheet|none|missing CONTROL.md|create CONTROL.md")
done

case "$FORMAT" in
    table)
        printf "%-25s %-28s %-22s %-40s %-40s\n" "REPO" "LIFECYCLE" "PERMISSION" "BLOCKER" "NEXT_WORK"
        printf '%.0s-' {1..155}
        printf "\n"
        for r in "${RESULTS[@]}"; do
            IFS='|' read -r name lifecycle permission blocker nextwork <<< "$r"
            printf "%-25s %-28s %-22s %-40s %-40s\n" "$name" "$lifecycle" "$permission" "$blocker" "$nextwork"
        done
        ;;
    json)
        printf "{\n  \"tasks\": [\n"
        first=true
        for r in "${RESULTS[@]}"; do
            if $first; then first=false; else printf ",\n"; fi
            IFS='|' read -r name lifecycle permission blocker nextwork <<< "$r"
            name=$(echo "$name" | sed 's/"/\\"/g')
            lifecycle=$(echo "$lifecycle" | sed 's/"/\\"/g')
            permission=$(echo "$permission" | sed 's/"/\\"/g')
            blocker=$(echo "$blocker" | sed 's/"/\\"/g')
            nextwork=$(echo "$nextwork" | sed 's/"/\\"/g')
            printf '    {"repo": "%s", "lifecycle": "%s", "permission": "%s", "blocker": "%s", "next_work": "%s"}' \
                "$name" "$lifecycle" "$permission" "$blocker" "$nextwork"
        done
        printf "\n  ]\n}\n"
        ;;
    markdown)
        printf "# Hermes Ready Tasks\n\n"
        printf "| Repo | Lifecycle | Permission | Blocker | Next Work |\n"
        printf "|------|-----------|------------|---------|-----------|\n"
        for r in "${RESULTS[@]}"; do
            IFS='|' read -r name lifecycle permission blocker nextwork <<< "$r"
            name=$(echo "$name" | sed 's/|/\\|/g')
            lifecycle=$(echo "$lifecycle" | sed 's/|/\\|/g')
            permission=$(echo "$permission" | sed 's/|/\\|/g')
            blocker=$(echo "$blocker" | sed 's/|/\\|/g')
            nextwork=$(echo "$nextwork" | sed 's/|/\\|/g')
            printf "| %s | %s | %s | %s | %s |\n" "$name" "$lifecycle" "$permission" "$blocker" "$nextwork"
        done
        printf "\n"
        ;;
    *)
        echo "Unknown format: $FORMAT (use table, json, or markdown)" >&2
        exit 1
        ;;
esac
