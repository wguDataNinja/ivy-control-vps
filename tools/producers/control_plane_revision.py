#!/usr/bin/env python3
"""control_plane_revision.py — Control-plane deployed-revision and drift producer.

Emits a canonical v2 health payload for the 'control_plane' project, reporting:
- Git SHA of the ivy-control-vps checkout
- Clean/dirty tree state
- Drift from origin/main
- Checkout path and existence status

Local development mode:
    python3 tools/producers/control_plane_revision.py

Fixture mode:
    python3 tools/producers/control_plane_revision.py --fixture tests/fixtures/control_plane_revision.json

Output: canonical v2 JSON to stdout.
"""

from __future__ import annotations

import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT = "ivy_control_vps"
WORKFLOW = "deployed_revision"
WORKFLOW_ID = f"{PROJECT}/{WORKFLOW}"
EXPECTED_CADENCE_SECONDS = 3600  # hourly

REQUIRED_OUTPUT_FIELDS = {
    "contract_version", "generated_at", "project", "workflow", "workflow_id",
    "run_id", "status", "started_at", "finished_at", "last_success_at",
    "expected_cadence_seconds", "freshness_seconds", "deployed_revision",
    "scheduler_state", "backup_state", "incident_state",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None) -> str | None:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z") if dt else None


def _run(cmd: list[str], cwd: str | Path | None = None, timeout: int = 10) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout, check=False, cwd=str(cwd) if cwd else None,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    if completed.returncode:
        return False, (completed.stderr or completed.stdout).strip()
    return True, completed.stdout.strip()


def _find_checkout() -> Path | None:
    candidates = [
        Path.home() / "apps" / "ivy-control-vps",
        Path("/home/scraper/apps/ivy-control-vps"),
        Path(__file__).resolve().parent.parent.parent,
    ]
    for p in candidates:
        if (p / ".git").is_dir():
            return p.resolve()
    return None


def collect() -> dict[str, Any]:
    now = _utcnow()
    run_id = str(uuid.uuid4())
    generated_at = _iso(now)

    checkout = _find_checkout()
    if checkout is None:
        return {
            "contract_version": 2,
            "generated_at": generated_at,
            "project": PROJECT,
            "workflow": WORKFLOW,
            "workflow_id": WORKFLOW_ID,
            "run_id": run_id,
            "status": "fail",
            "started_at": generated_at,
            "finished_at": generated_at,
            "last_success_at": None,
            "expected_cadence_seconds": EXPECTED_CADENCE_SECONDS,
            "freshness_seconds": None,
            "deployed_revision": None,
            "scheduler_state": "unmanaged",
            "backup_state": "not_applicable",
            "incident_state": "degraded",
            "error_class": "no_checkout_found",
            "producer_version": "control_plane_revision/v1",
            "metadata": {
                "source_adapter": "control_plane_revision",
                "checkout_path": "[redacted]",
                "checkout_status": "not_found",
                "drift_state": "unknown",
                "ahead_behind": None,
            },
        }

    ok_rev, rev = _run(["git", "rev-parse", "HEAD"], cwd=checkout)
    ok_branch, branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=checkout)
    ok_dirty, dirty = _run(["git", "status", "--porcelain"], cwd=checkout)
    ok_remote, remote = _run(["git", "remote", "-v"], cwd=checkout)
    ok_ahead, ahead = _run(
        ["git", "rev-list", "--count", "@{upstream}..HEAD"],
        cwd=checkout, timeout=10,
    )
    ok_behind, behind = _run(
        ["git", "rev-list", "--count", "HEAD..@{upstream}"],
        cwd=checkout, timeout=10,
    )

    if not ok_rev:
        return _error_payload(generated_at, run_id, "git_rev_parse_failed")

    sha = rev.strip()
    is_dirty = bool(dirty.strip()) if ok_dirty else None
    ahead_count = int(ahead.strip()) if ok_ahead and ahead.strip().isdigit() else None
    behind_count = int(behind.strip()) if ok_behind and behind.strip().isdigit() else None

    has_origin = bool(remote.strip()) if ok_remote else False

    # Directional drift computation.
    # "deployed" = local checkout HEAD, "remote" = @{upstream} (origin/main).
    if ahead_count is not None and behind_count is not None:
        if ahead_count == 0 and behind_count == 0:
            drift_direction = "exact_match"
        elif ahead_count > 0 and behind_count == 0:
            drift_direction = "local_ahead"
        elif ahead_count == 0 and behind_count > 0:
            drift_direction = "local_behind"
        else:
            drift_direction = "diverged"
    else:
        drift_direction = "unavailable"

    # For backward compat, map to simple drift_state.
    if is_dirty:
        drift_state = "dirty"
    elif drift_direction in ("exact_match", "local_ahead", "local_behind", "diverged"):
        drift_state = "clean" if ahead_count == 0 and behind_count == 0 else "dirty"
    else:
        drift_state = "unknown"

    status = "ok" if drift_direction == "exact_match" and not is_dirty else "warn"
    error_class = None
    incident_state = "none"

    issues = []
    if is_dirty:
        status = "warn"
        error_class = "dirty_tree"
        incident_state = "degraded"
        issues.append("Working tree has uncommitted changes")
    if ahead_count and ahead_count > 0:
        status = "warn" if status != "fail" else "fail"
        incident_state = "degraded"
        if drift_direction == "local_ahead":
            error_class = "ahead_of_upstream"
            issues.append(f"Local checkout is {ahead_count} commits ahead of upstream")
        elif drift_direction == "diverged":
            error_class = "diverged"
            issues.append(f"Diverged: {ahead_count} ahead, {behind_count} behind upstream")
    if behind_count and behind_count > 0 and error_class is None:
        status = "warn"
        error_class = "behind_upstream"
        incident_state = "degraded"
        issues.append(f"Local checkout is {behind_count} commits behind upstream")

    result: dict[str, Any] = {
        "contract_version": 2,
        "generated_at": generated_at,
        "project": PROJECT,
        "workflow": WORKFLOW,
        "workflow_id": WORKFLOW_ID,
        "run_id": run_id,
        "status": status,
        "started_at": generated_at,
        "finished_at": generated_at,
        "last_success_at": generated_at if status == "ok" else None,
        "expected_cadence_seconds": EXPECTED_CADENCE_SECONDS,
        "freshness_seconds": 0,
        "deployed_revision": sha,
        "scheduler_state": "active" if checkout else "unmanaged",
        "backup_state": "not_applicable",
        "incident_state": incident_state,
        "error_class": error_class,
        "producer_version": "control_plane_revision/v1",
        "metadata": {
            "source_adapter": "control_plane_revision",
            "checkout_path": "[redacted]",
            "branch": branch.strip() if ok_branch else None,
            "is_dirty": is_dirty,
            "drift_state": drift_state,
            "drift_direction": drift_direction,
            "ahead_count": ahead_count,
            "behind_count": behind_count,
            "has_origin": has_origin,
            "issues": issues,
        },
    }

    for field in REQUIRED_OUTPUT_FIELDS:
        if field not in result:
            result[field] = None

    return result


def _error_payload(generated_at: str, run_id: str, error_class: str) -> dict[str, Any]:
    return {
        "contract_version": 2,
        "generated_at": generated_at,
        "project": PROJECT,
        "workflow": WORKFLOW,
        "workflow_id": WORKFLOW_ID,
        "run_id": run_id,
        "status": "fail",
        "started_at": generated_at,
        "finished_at": generated_at,
        "last_success_at": None,
        "expected_cadence_seconds": EXPECTED_CADENCE_SECONDS,
        "freshness_seconds": None,
        "deployed_revision": None,
        "scheduler_state": "unmanaged",
        "backup_state": "not_applicable",
        "incident_state": "degraded",
        "error_class": error_class,
        "producer_version": "control_plane_revision/v1",
        "metadata": {"source_adapter": "control_plane_revision"},
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Control-plane revision producer")
    parser.add_argument("--fixture", help="Read fixture file instead of live checkout")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    if args.fixture:
        payload = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    else:
        payload = collect()

    indent = 2 if args.pretty else None
    json.dump(payload, sys.stdout, indent=indent, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
