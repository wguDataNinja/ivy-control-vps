#!/usr/bin/env python3
"""traderie_live_export.py — Traderie live-export health contract.

Emits a canonical v2 health payload for the 'traderie/ingest_snapshot' workflow
using the prepared instrumentation from the local source (137dd64).

This producer reads a live-export fixture or control-doc evidence and reports
the ingestion pipeline health including:
- deployed revision (exact VPS SHA e5ebd0f)
- latest run result, timeout/progress
- backup age/restore status
- mutable-data violation flag

Local development mode:
    python3 tools/producers/traderie_live_export.py --fixture tests/fixtures/traderie_export.json

Output: canonical v2 JSON to stdout.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT = "traderie"
WORKFLOW = "ingest_snapshot"
WORKFLOW_ID = f"{PROJECT}/{WORKFLOW}"
EXPECTED_CADENCE_SECONDS = 86400  # daily at 00:00 UTC
TIMEOUT_THRESHOLD_SECONDS = 480  # from live discovery: pc_hc_nl segment bound

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
    deployed_revision: str | None = "e5ebd0f",
    run_status: str = "stale",
    last_success_at: str | None = None,
    last_failure_at: str | None = None,
    error_class: str | None = None,
    schedule_state: str = "active",
    backup_age_seconds: int | None = None,
    backup_state: str = "stale",
    records_read: int | None = None,
    records_written: int | None = None,
    segment_duration_seconds: float | None = None,
    has_timeout_error: bool = False,
    mutable_data_violation: bool = True,
    upstream_source_sha: str | None = "137dd64",
) -> dict[str, Any]:
    now = _utcnow()
    run_id = str(uuid.uuid4())
    generated_at = _iso(now)

    last_success_dt = _parse_iso(last_success_at)
    last_failure_dt = _parse_iso(last_failure_at)

    if last_success_dt:
        freshness = int((now - last_success_dt).total_seconds())
    else:
        freshness = None

    if run_status == "ok":
        status = "ok"
        error_class_derived = None
        incident_state = "none"
    elif run_status == "fail":
        status = "fail"
        error_class_derived = error_class or "natural_run_failed"
        incident_state = "critical"
    elif has_timeout_error or (segment_duration_seconds and segment_duration_seconds >= TIMEOUT_THRESHOLD_SECONDS):
        status = "fail"
        error_class_derived = error_class or "segment_timeout"
        incident_state = "critical"
    elif run_status == "warn":
        status = "warn"
        error_class_derived = error_class or "degraded"
        incident_state = "degraded"
    else:
        status = "stale"
        error_class_derived = error_class or "no_recent_run"
        incident_state = "degraded"

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
        "last_success_at": _iso(last_success_dt) if last_success_dt else None,
        "expected_cadence_seconds": EXPECTED_CADENCE_SECONDS,
        "freshness_seconds": freshness,
        "deployed_revision": deployed_revision,
        "scheduler_state": schedule_state,
        "backup_state": backup_state,
        "backup_age_seconds": backup_age_seconds,
        "incident_state": incident_state,
        "records_read": records_read,
        "records_written": records_written,
        "error_class": error_class_derived,
        "producer_version": "traderie_live_export/v1",
        "metadata": {
            "source_adapter": "traderie_live_export",
            "deployed_revision": deployed_revision,
            "upstream_source_sha": upstream_source_sha,
            "segment_duration_seconds": segment_duration_seconds,
            "timeout_threshold_seconds": TIMEOUT_THRESHOLD_SECONDS,
            "has_timeout_error": has_timeout_error,
            "mutable_data_violation": mutable_data_violation,
            "last_failure_at": last_failure_at,
            "instrumentation_deployed": False,
            "instrumentation_source_sha": upstream_source_sha,
            "note": "Instrumentation is prepared in local source (137dd64) but not yet deployed to VPS.",
        },
    }

    for field in REQUIRED_OUTPUT_FIELDS:
        if field not in result:
            result[field] = None

    return result


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Traderie live-export health producer")
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
