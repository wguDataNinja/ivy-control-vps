#!/usr/bin/env python3
"""vps_capacity_snapshot.py — Recurring VPS capacity snapshot producer.

Emits a canonical v2 health payload for the host capacity workflow.

Local development mode (read fixture):
    python3 tools/producers/vps_capacity_snapshot.py --fixture tests/fixtures/vps_capacity.json

Live SSH mode:
    python3 tools/producers/vps_capacity_snapshot.py

Output: canonical v2 JSON to stdout.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT = "ivy_control_vps"
WORKFLOW = "host_capacity"
WORKFLOW_ID = f"{PROJECT}/{WORKFLOW}"
EXPECTED_CADENCE_SECONDS = 3600  # hourly

REQUIRED_OUTPUT_FIELDS = {
    "contract_version", "generated_at", "project", "workflow", "workflow_id",
    "run_id", "status", "started_at", "finished_at", "last_success_at",
    "expected_cadence_seconds", "freshness_seconds", "deployed_revision",
    "scheduler_state", "backup_state", "incident_state",
}

# Capacity thresholds from live discovery report §90
WARN_DISK_PCT = 80
STOP_DISK_PCT = 85
WARN_FREE_GB = 7
STOP_FREE_GB = 5


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None) -> str | None:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z") if dt else None


def _run_ssh(command: str) -> tuple[bool, str]:
    if not shutil.which("ssh"):
        return False, "ssh not available"
    try:
        completed = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", "ih-market-vps", command],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=18, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    if completed.returncode:
        return False, (completed.stderr or completed.stdout).strip()
    return True, completed.stdout.strip()


def _ssh_to_raw_lines(raw: str) -> tuple[list[str], str | None]:
    """Parse SSH output into filesystem/inode/memory lines and optional uptime."""
    parts = raw.split("---\n") if "---" in raw else [raw]
    lines = [l.strip() for l in parts[0].splitlines() if l.strip()]
    uptime = parts[1].strip() if len(parts) > 1 else None
    return lines, uptime


def collect() -> dict[str, Any]:
    now = _utcnow()
    run_id = str(uuid.uuid4())
    generated_at = _iso(now)

    ok, raw = _run_ssh(
        "df -P / | tail -1; df -Pi / | tail -1; "
        "free -h | sed -n '2p'; "
        "echo ---; uptime -s"
    )
    if not ok:
        return _skip_payload(generated_at, run_id, f"ssh_failure:{raw}")

    lines, uptime = _ssh_to_raw_lines(raw)
    if len(lines) < 3:
        return _skip_payload(generated_at, run_id, "malformed_capacity_response")

    df_parts = lines[0].split()
    inode_parts = lines[1].split()
    memory = lines[2]

    try:
        used_pct = int(df_parts[4].rstrip("%"))
        free_blocks = int(df_parts[3])
        free_gb = free_blocks / (1024 * 1024)  # 1K blocks to GB
    except (IndexError, ValueError) as exc:
        return _skip_payload(generated_at, run_id, f"parse_error:{exc}")

    inode_pct = None
    if len(inode_parts) >= 5:
        try:
            inode_pct = int(inode_parts[4].rstrip("%"))
        except (ValueError, IndexError):
            pass

    if used_pct >= STOP_DISK_PCT or (inode_pct is not None and inode_pct >= 80):
        status = "fail"
        error_class = "disk_critical"
        incident_state = "critical"
    elif used_pct >= WARN_DISK_PCT or free_gb < WARN_FREE_GB:
        status = "warn"
        error_class = "disk_warning"
        incident_state = "degraded"
    else:
        status = "ok"
        error_class = None
        incident_state = "none"

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
        "last_success_at": generated_at,
        "expected_cadence_seconds": EXPECTED_CADENCE_SECONDS,
        "freshness_seconds": 0,
        "deployed_revision": None,
        "scheduler_state": "active",
        "backup_state": "not_applicable",
        "incident_state": incident_state,
        "disk_free_bytes": int(free_blocks * 1024),
        "disk_usage_pct": round(used_pct, 2),
        "storage_bytes": None,
        "error_class": error_class,
        "heartbeat_at": generated_at,
        "producer_version": "vps_capacity_snapshot/v1",
        "metadata": {
            "source_adapter": "vps_capacity_snapshot",
            "filesystem": lines[0],
            "inodes": lines[1],
            "memory": memory,
            "uptime": uptime,
        },
    }

    for field in REQUIRED_OUTPUT_FIELDS:
        if field not in result:
            result[field] = None

    return result


def _skip_payload(generated_at: str, run_id: str, error_class: str) -> dict[str, Any]:
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
        "producer_version": "vps_capacity_snapshot/v1",
        "metadata": {"source_adapter": "vps_capacity_snapshot"},
    }


def collect_from_fixture(fixture_path: str) -> dict[str, Any]:
    """Run collection logic over a raw-evidence fixture file."""
    data = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    mock_raw = (
        f"{data['filesystem']}\n{data['inodes']}\n{data['memory']}\n"
        f"---\n{data.get('uptime', 'unknown')}"
    )
    return _collect_from_raw(mock_raw)


def _collect_from_raw(raw: str) -> dict[str, Any]:
    """Collect capacity evidence from a raw SSH-like string."""
    now = _utcnow()
    run_id = str(uuid.uuid4())
    generated_at = _iso(now)

    lines, uptime = _ssh_to_raw_lines(raw)
    if len(lines) < 3:
        return _skip_payload(generated_at, run_id, "malformed_capacity_response")

    df_parts = lines[0].split()
    inode_parts = lines[1].split()
    memory = lines[2]

    try:
        used_pct = int(df_parts[4].rstrip("%"))
        free_blocks = int(df_parts[3])
        free_gb = free_blocks / (1024 * 1024)
    except (IndexError, ValueError) as exc:
        return _skip_payload(generated_at, run_id, f"parse_error:{exc}")

    inode_pct = None
    if len(inode_parts) >= 5:
        try:
            inode_pct = int(inode_parts[4].rstrip("%"))
        except (ValueError, IndexError):
            pass

    if used_pct >= STOP_DISK_PCT or (inode_pct is not None and inode_pct >= 80):
        status = "fail"
        error_class = "disk_critical"
        incident_state = "critical"
    elif used_pct >= WARN_DISK_PCT or free_gb < WARN_FREE_GB:
        status = "warn"
        error_class = "disk_warning"
        incident_state = "degraded"
    else:
        status = "ok"
        error_class = None
        incident_state = "none"

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
        "last_success_at": generated_at,
        "expected_cadence_seconds": EXPECTED_CADENCE_SECONDS,
        "freshness_seconds": 0,
        "deployed_revision": None,
        "scheduler_state": "active",
        "backup_state": "not_applicable",
        "incident_state": incident_state,
        "disk_free_bytes": int(free_blocks * 1024),
        "disk_usage_pct": round(used_pct, 2),
        "storage_bytes": None,
        "error_class": error_class,
        "heartbeat_at": generated_at,
        "producer_version": "vps_capacity_snapshot/v1",
        "metadata": {
            "source_adapter": "vps_capacity_snapshot",
            "filesystem": lines[0],
            "inodes": lines[1],
            "memory": memory,
            "uptime": uptime,
        },
    }

    for field in REQUIRED_OUTPUT_FIELDS:
        if field not in result:
            result[field] = None

    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="VPS capacity snapshot producer")
    parser.add_argument("--fixture", help="Read raw-evidence fixture file instead of live SSH")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    if args.fixture:
        payload = collect_from_fixture(args.fixture)
    else:
        payload = collect()

    indent = 2 if args.pretty else None
    json.dump(payload, sys.stdout, indent=indent, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
