#!/usr/bin/env bash
# show_ready_work.sh — Show repos whose next_task is actionable
# (no blocker and CONTROL.md exists).
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"

python3 -c "
import json, sys
sys.path.insert(0, '$DIR')
from portfolio_registry import build_registry

records = build_registry(include_missing=False)
ready = [r for r in records if r['blocker'] in ('none', '', 'N/A', 'UNKNOWN') and r['source'] != 'MISSING']
if not ready:
    print('No repos with actionable next tasks.')
    sys.exit(0)

print(f'=== Repos ready for next work ({len(ready)}) ===\n')
for r in ready:
    print(f\"  {r['repo_id']:22s}  {r['next_task'][:70]}\")
print()
print('Flag: repos with blockers are excluded.')
" "$@"
