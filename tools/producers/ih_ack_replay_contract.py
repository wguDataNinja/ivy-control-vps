#!/usr/bin/env python3
"""ih_ack_replay_contract.py — IH acknowledgement/replay contract template.

This producer emits a canonical v2 health payload for the
'idlehacking_kb/ack_replay' workflow.  All fields that depend on unresolved
authority (Buddy decisions) are marked as 'unresolved_authority'.

Unresolved decisions (from live discovery report §63, §98):
- canonical userscript source
- separate chat/market acknowledgement destination
- acknowledgement receipt action
- replay procedure
- PostgreSQL market import pilot

Local development mode:
    python3 tools/producers/ih_ack_replay_contract.py

Output: canonical v2 JSON to stdout with status=skip, incident_state=degraded.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from typing import Any


PROJECT = "idlehacking_kb"
WORKFLOW = "ack_replay"
WORKFLOW_ID = f"{PROJECT}/{WORKFLOW}"
EXPECTED_CADENCE_SECONDS = 900  # 15 minutes (aligned with helper cadence)


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
        "error_class": "unresolved_authority",
        "producer_version": "ih_ack_replay_contract/v1",
        "metadata": {
            "source_adapter": "ih_ack_replay_contract",
            "acknowledgement": {
                "status": "unresolved_authority",
                "canonical_userscript_source": "unresolved_authority — Buddy must decide",
                "chat_ack_destination": "unresolved_authority — Buddy must decide separate from market",
                "market_ack_destination": "unresolved_authority — Buddy must decide separate from chat",
                "acknowledgement_receipt_action": "unresolved_authority — not yet defined",
            },
            "replay": {
                "status": "unsupported_field",
                "replay_procedure": "unsupported_field — no replay mechanism defined",
                "replay_verified_at": None,
            },
            "installed_revision": {
                "chat_userscript": "unresolved_authority — cannot inspect Chrome/Tampermonkey profile",
                "market_userscript": "unresolved_authority — cannot inspect Chrome/Tampermonkey profile",
                "helper_source_match": "observed 2026-07-15; not runtime-verified",
            },
            "durability": {
                "archive_freshness": "missing_producer — no archive freshness adapter",
                "durable_write_status": "reported by helper; not independently verified",
                "postgresql_market_pilot": "unsupported_field — no PG market import pilot",
            },
            "note": "This producer is a template/contract placeholder. All authority-dependent fields are unresolved_authority and must be resolved by Buddy before live deployment.",
        },
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="IH acknowledgement/replay contract template")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    indent = 2 if args.pretty else None
    json.dump(produce(), sys.stdout, indent=indent, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
