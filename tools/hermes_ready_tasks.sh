#!/usr/bin/env bash
# Hermes ready-task scanner — read-only, no mutations.
# Uses the portfolio registry for lifecycle/permission data.
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

python3 -c "
import json, sys
sys.path.insert(0, '$REPO_ROOT/tools')
from portfolio_registry import build_registry, VALID_LIFECYCLES, UNKNOWN, NA

records = build_registry(include_missing=True)
if '$REPO_FILTER':
    records = [r for r in records if r['repo_id'] == '$REPO_FILTER']

def compute_permission(rec):
    lc = rec['lifecycle'].lower()
    blocker = rec['blocker'].lower()
    source = rec['source']
    is_restricted = 'restricted' in lc or 'no_launch' in lc
    is_deferred = lc in ('downstream', 'batch', 'unknown')
    is_browser_dependent = 'browser' in lc
    is_source_only = lc in ('source-only', 'published')
    is_active_prod = any(t in lc for t in ['production', 'runtime', 'active', 'stabilizing', 'degraded'])

    # Restricted repos: Hermes may not inspect
    if is_restricted:
        return 'none'
    # Deferred/downstream repos: Hermes may not inspect
    if is_deferred and source == 'MISSING':
        return 'none'
    if is_deferred and blocker != 'none':
        return 'none' if 'not yet admitted' in blocker else 'inspect'
    # Source-only repos: read-only pilot only
    if is_source_only:
        return 'inspect'
    # Browser-dependent repos: read-only inspection
    if is_browser_dependent:
        return 'inspect'
    # Active production with blocker: inspect + report
    if is_active_prod and blocker != 'none':
        return 'inspect+report'
    # Active production, no blocker: inspect + report + propose
    if is_active_prod and blocker == 'none':
        return 'inspect+report+propose'
    # No CONTROL.md: Hermes may not inspect
    if source == 'MISSING':
        return 'none'
    return 'inspect'

tasks = []
for rec in records:
    permission = compute_permission(rec)
    tasks.append({
        'repo': rec['repo_id'],
        'lifecycle': rec['lifecycle'],
        'permission': permission,
        'blocker': rec['blocker'][:80] if len(rec['blocker']) > 80 else rec['blocker'],
        'next_work': rec['next_task'][:80] if len(rec['next_task']) > 80 else rec['next_task'],
    })

fmt = '$FORMAT'
if fmt == 'json':
    print(json.dumps({'tasks': tasks}, indent=2))
elif fmt == 'markdown':
    print('# Hermes Ready Tasks\n')
    print('| Repo | Lifecycle | Permission | Blocker | Next Work |')
    print('|------|-----------|------------|---------|-----------|')
    for t in tasks:
        print(f\"| {t['repo']} | {t['lifecycle'][:28]} | {t['permission']} | {t['blocker'][:60]} | {t['next_work'][:60]} |\")
    print()
else:
    # table
    print(f\"{'REPO':25s} {'LIFECYCLE':28s} {'PERMISSION':22s} {'BLOCKER':60s} {'NEXT_WORK':60s}\")
    print('-' * 195)
    for t in tasks:
        print(f\"{t['repo']:25s} {t['lifecycle'][:28]:28s} {t['permission']:22s} {t['blocker'][:60]:60s} {t['next_work'][:60]:60s}\")
" 2>&1
