#!/usr/bin/env python3
"""reddit_canonicality_placeholder.py — Reddit canonicality evidence placeholder.

This producer does NOT emit canonicality conclusions.  It reports each required
canonicality dimension as 'unresolved' until live evidence exists.

Canonicality requirements (from live discovery report §50):
- source/DB frontier: missing_producer
- recent completeness: missing_producer
- duplicate/gap check: missing_producer
- archive continuity: missing_producer
- one-writer/lock proof: unresolved_authority
- fresh backup/restore: missing_producer
- natural-run observation: missing_producer

Local development mode:
    python3 tools/producers/reddit_canonicality_placeholder.py

Output: canonical v2 JSON to stdout with status=skip, incident_state=degraded.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT = "reddit_ops"
WORKFLOW = "canonicality_evidence"
WORKFLOW_ID = f"{PROJECT}/{WORKFLOW}"
EXPECTED_CADENCE_SECONDS = 86400


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None) -> str | None:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z") if dt else None


def produce() -> dict[str, Any]:
    now = _utcnow()
    run_id = str(uuid.uuid4())
    generated_at = _iso(now)

    return {
        "contract_version": 2,
        "generated_at": generated_at,
        "project": PROJECT,
        "workflow": WORKFLOW,
        "workflow_id": WORKFLOW_ID,
        "run_id": run_id,
        "status": "skip",
        "started_at": None,
        "finished_at": generated_at,
        "last_success_at": None,
        "expected_cadence_seconds": EXPECTED_CADENCE_SECONDS,
        "freshness_seconds": None,
        "deployed_revision": None,
        "scheduler_state": "unmanaged",
        "backup_state": "not_applicable",
        "incident_state": "degraded",
        "error_class": "canonicality_not_yet_evaluable",
        "producer_version": "reddit_canonicality_placeholder/v1",
        "metadata": {
            "source_adapter": "reddit_canonicality_placeholder",
            "canonicality_evidence": {
                "source_db_frontier": "missing_producer",
                "recent_completeness": "missing_producer",
                "duplicate_gap_check": "missing_producer",
                "archive_earliest": "missing_producer",
                "archive_latest": "missing_producer",
                "archive_continuity": "missing_producer",
                "one_writer_lock_proof": "unresolved_authority",
                "fresh_backup_restore": "missing_producer",
                "natural_run_observation": "missing_producer",
            },
            "overall_canonicality": "unresolved_authority — all dimensions are missing_producer or unresolved_authority",
            "note": "Canonicality cannot be declared until live evidence exists for every dimension. Do not infer canonical status from absence of evidence.",
        },
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Reddit canonicality evidence placeholder")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    indent = 2 if args.pretty else None
    json.dump(produce(), sys.stdout, indent=indent, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
