#!/usr/bin/env python3
"""reddit_backup_evidence.py — Reddit backup/restore evidence ingestion structure.

Emits a canonical v2 health payload for the 'reddit_ops/backup_verification'
workflow.  Reports backup age, latest dump/checksum timestamps, restore proof
status, and archive continuity as separate fields.

Backup evidence is classified as:
- live: systemd unit shows recent success AND a checksum-verified dump exists
- stale: backup exists but exceeds expected cadence
- fail: no valid backup, unit failure, or missing checksum
- missing_producer: no backup evidence producer deployed

Local development mode:
    python3 tools/producers/reddit_backup_evidence.py --fixture tests/fixtures/reddit_backup.json

Output: canonical v2 JSON to stdout.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT = "reddit_ops"
WORKFLOW = "backup_verification"
WORKFLOW_ID = f"{PROJECT}/{WORKFLOW}"
EXPECTED_CADENCE_SECONDS = 86400  # daily
BACKUP_STALE_SECONDS = int(36 * 3600)  # 36 hours
BACKUP_FAIL_SECONDS = int(72 * 3600)   # 72 hours

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


def _parse_iso(text: str | None) -> datetime | None:
    if not text:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(text.replace("Z", "+0000"), fmt if "+" not in fmt else fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def produce(
    last_dump_at: str | None = None,
    last_checksum_at: str | None = None,
    last_restore_proof_at: str | None = None,
    backup_unit_ok: bool = False,
    dump_exists: bool = False,
    checksum_valid: bool = False,
    restore_proven: bool = False,
    archive_earliest: str | None = None,
    archive_latest: str | None = None,
    errors: list[str] | None = None,
) -> dict[str, Any]:
    now = _utcnow()
    run_id = str(uuid.uuid4())
    generated_at = _iso(now)

    last_dump_dt = _parse_iso(last_dump_at)
    last_checksum_dt = _parse_iso(last_checksum_at)
    last_restore_dt = _parse_iso(last_restore_proof_at)
    archive_earliest_dt = _parse_iso(archive_earliest)
    archive_latest_dt = _parse_iso(archive_latest)

    newest_evidence = max(
        dt for dt in [last_dump_dt, last_checksum_dt, last_restore_dt] if dt
    ) if any([last_dump_dt, last_checksum_dt, last_restore_dt]) else None

    if newest_evidence:
        backup_age = int((now - newest_evidence).total_seconds())
    else:
        backup_age = None

    all_ok = all([backup_unit_ok, dump_exists, checksum_valid])

    if not dump_exists or not checksum_valid:
        backup_state = "fail"
        status = "fail"
        error_class = "dump_or_checksum_missing"
        incident_state = "critical"
    elif not backup_unit_ok:
        backup_state = "fail"
        status = "fail"
        error_class = "systemd_unit_failed"
        incident_state = "critical"
    elif not restore_proven:
        backup_state = "stale"
        status = "warn"
        error_class = "restore_not_proven"
        incident_state = "degraded"
    elif backup_age is not None and backup_age > BACKUP_FAIL_SECONDS:
        backup_state = "fail"
        status = "fail"
        error_class = "backup_too_old"
        incident_state = "critical"
    elif backup_age is not None and backup_age > BACKUP_STALE_SECONDS:
        backup_state = "stale"
        status = "warn"
        error_class = "backup_stale"
        incident_state = "degraded"
    else:
        backup_state = "ok"
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
        "last_success_at": _iso(newest_evidence) if all_ok else None,
        "expected_cadence_seconds": EXPECTED_CADENCE_SECONDS,
        "freshness_seconds": backup_age,
        "deployed_revision": None,
        "scheduler_state": "active",
        "backup_state": backup_state,
        "backup_age_seconds": backup_age,
        "incident_state": incident_state,
        "error_class": error_class,
        "producer_version": "reddit_backup_evidence/v1",
        "metadata": {
            "source_adapter": "reddit_backup_evidence",
            "backup_unit_ok": backup_unit_ok,
            "dump_exists": dump_exists,
            "checksum_valid": checksum_valid,
            "restore_proven": restore_proven,
            "last_dump_at": last_dump_at,
            "last_checksum_at": last_checksum_at,
            "last_restore_proof_at": last_restore_proof_at,
            "archive_earliest": archive_earliest,
            "archive_latest": archive_latest,
            "errors": errors or [],
        },
    }

    for field in REQUIRED_OUTPUT_FIELDS:
        if field not in result:
            result[field] = None

    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Reddit backup evidence producer")
    parser.add_argument("--fixture", help="Read fixture file")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    if args.fixture:
        data = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
        payload = produce(**data)
    else:
        payload = produce()

    indent = 2 if args.pretty else None
    json.dump(payload, sys.stdout, indent=indent, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
