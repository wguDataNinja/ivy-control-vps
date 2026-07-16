"""ih_dashboard_adapter.py — Maps canonical v2 health to dashboard row format.

Loads the Wave 1 chat and market health adapters from their external repos
(ih_market_companion, idlehacking_kb), calls them with the raw /health
payload, and maps the canonical v2 output to the ingestion_dashboard row format.

Status derivation preserves:
- Separate chat and market statuses (never merged)
- Lifetime failure counts do not override current success (Wave 1 fix)
- Acknowledgement semantics from the adapters
- deployed_revision = None/unknown while source authority unresolved

Evidence semantics (evidence_level values):
- live: fresh observation from live system
- stale: observation exists but exceeds freshness threshold
- missing_producer: no producer/exporter for this field
- unsupported_field: field is not yet instrumented
- doc_fallback: derived from documentation, not live observation
- unresolved_authority: authority decision pending (Buddy)

External adapter paths are configurable via environment variables:
    IVY_IH_MARKET_ADAPTER  — path to ih_market_companion health_adapter_market.py
    IVY_IH_CHAT_ADAPTER    — path to idlehacking_kb health_adapter_chat.py
"""

from __future__ import annotations

import importlib.util
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure the repository root is on sys.path for standalone usage.
_ADAPTER_ROOT = Path(__file__).resolve().parent.parent
if str(_ADAPTER_ROOT) not in sys.path:
    sys.path.insert(0, str(_ADAPTER_ROOT))


# External repos are co-located under ~/projects/ alongside ivy-control-vps.
# This is a local development tool; when adapters are deployed to VPS the
# path strategy will change.
# Paths can be overridden via environment variables.
_ADAPTER_PROJECTS = Path(__file__).resolve().parent.parent.parent
_IH_MARKET_PATH = Path(
    os.environ.get("IVY_IH_MARKET_ADAPTER")
    or str(_ADAPTER_PROJECTS / "ih_market_companion" / "scripts" / "health_adapter_market.py")
)
_IDLEHACKING_KB_PATH = Path(
    os.environ.get("IVY_IH_CHAT_ADAPTER")
    or str(_ADAPTER_PROJECTS / "idlehacking_kb" / "scripts" / "health_adapter_chat.py")
)

_ADAPTERS_LOADED = False
_ADAPTER_CHAT_FN = None
_ADAPTER_MARKET_FN = None


def _ensure_loaded() -> None:
    global _ADAPTERS_LOADED, _ADAPTER_CHAT_FN, _ADAPTER_MARKET_FN
    if _ADAPTERS_LOADED:
        return
    if not _IH_MARKET_PATH.is_file():
        raise FileNotFoundError(
            f"Market adapter not found at {_IH_MARKET_PATH}. "
            "Clone ih_market_companion into ~/projects/."
        )
    if not _IDLEHACKING_KB_PATH.is_file():
        raise FileNotFoundError(
            f"Chat adapter not found at {_IDLEHACKING_KB_PATH}. "
            "Clone idlehacking_kb into ~/projects/."
        )
    spec_m = importlib.util.spec_from_file_location(
        "_ih_dash_market_adapter", str(_IH_MARKET_PATH)
    )
    mod_m = importlib.util.module_from_spec(spec_m)
    sys.modules["_ih_dash_market_adapter"] = mod_m
    spec_m.loader.exec_module(mod_m)
    _ADAPTER_MARKET_FN = mod_m.adapter_market

    spec_c = importlib.util.spec_from_file_location(
        "_ih_dash_chat_adapter", str(_IDLEHACKING_KB_PATH)
    )
    mod_c = importlib.util.module_from_spec(spec_c)
    sys.modules["_ih_dash_chat_adapter"] = mod_c
    spec_c.loader.exec_module(mod_c)
    _ADAPTER_CHAT_FN = mod_c.adapter_chat

    _ADAPTERS_LOADED = True


def _s(v: Any) -> str:
    return str(v) if v is not None else "unknown"


def _now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _row(name: str, collector: str, reference: str) -> dict:
    now = _now_iso()
    return {
        "workload": name,
        "collector": collector,
        "reference": reference,
        "last_success": "unknown",
        "source_freshness": "unknown",
        "db_freshness": "unknown",
        "offload": "unknown",
        "backup": "unknown",
        "capacity": "unknown",
        "status": "UNKNOWN",
        "evidence_level": "missing_producer",
        "evidence_timestamp": now,
        "detail": {},
        "issues": [],
    }


def _v2_status_to_dash(v2_status: str) -> str:
    return {"ok": "YELLOW", "warn": "YELLOW", "fail": "RED", "stale": "RED"}.get(
        v2_status, "UNKNOWN"
    )


def _v2_backup_to_dash(v2_backup: str | None) -> str:
    return {"ok": "current", "stale": "pending", "fail": "FAILED"}.get(
        v2_backup or "", "unknown"
    )


def _v2_ack_to_dash(ack: str | None) -> str:
    return {"current": "current", "pending": "pending", "required": "required"}.get(
        ack or "", "unknown"
    )


def _v2_to_row(
    v2: dict[str, Any],
    name: str,
    collector: str,
    reference: str,
    service_state: str,
    helper_sha: str,
    component: str,
) -> dict[str, Any]:
    """Convert a canonical v2 health payload to a dashboard row."""
    result = _row(name, collector, reference)
    meta = v2.get("metadata", {}) or {}
    v2_status = v2.get("status", "unknown")

    result["status"] = _v2_status_to_dash(v2_status)
    result["last_success"] = _s(v2.get("last_success_at"))
    result["evidence_level"] = "live"
    result["evidence_timestamp"] = _s(v2.get("generated_at"))

    freshness = v2.get("freshness_seconds")
    result["source_freshness"] = (
        f"{freshness}s ago" if freshness is not None else "unknown"
    )
    result["db_freshness"] = "missing_producer (no DB adapter; no PostgreSQL reconciliation)"

    ack = meta.get("archive_acknowledgement_status")
    result["offload"] = _v2_ack_to_dash(ack)

    result["backup"] = _v2_backup_to_dash(v2.get("backup_state"))

    result["capacity"] = "missing_producer (host capacity adapter pending)"

    detail: dict[str, Any] = {
        "component": component
        or "Idle Hacking Collector (namespace ih-market-companion; observed v2026-05-03.3)",
        "helper_service": service_state,
        "helper_sha256": helper_sha
        or "7747c2eb…bec1020 (observed 2026-07-15; not runtime-verified)",
        "userscript_source_authority": "unresolved_authority — installed-copy verification unavailable; cannot inspect Chrome/Tampermonkey profile",
        "installed_revision": "unresolved_authority (no userscript hash verification possible without profile access)",
        "replay_proof": "unsupported_field (no replay mechanism observed or contract defined)",
        "acknowledgement_destination": "unresolved_authority (Buddy must decide canonical source and destination for acknowledgement)",
        "durable_destination": "unresolved_authority (no durable archive path contract beyond local helper storage)",
        "adapter_version": v2.get("producer_version", "unknown"),
    }
    ec = v2.get("error_class")
    if ec:
        detail["adapter_error_class"] = ec

    for k in (
        "helper_reported_status",
        "durable_local_write_status",
        "archive_acknowledgement_status",
        "collection_status",
        "cumulative_writes_ok",
        "cumulative_writes_failed",
        "unacknowledged_generation_count",
        "unacknowledged_bytes",
        "managed_generation_count",
        "acknowledged_generation_count",
    ):
        if k in meta and meta[k] is not None:
            detail[k] = meta[k]

    result["detail"] = detail

    issues: list[str] = []
    if v2_status in ("fail", "stale"):
        issues.append(f"Adapter reports {v2_status}: {ec or v2_status}")
    elif v2_status == "warn":
        issues.append(f"Adapter reports warning: {ec or 'warning'}")
    else:
        issues.append(
            "Adapter reports OK, but source authority, archive acknowledgement "
            "destination, and consecutive-failure adapter remain unresolved"
        )
    if ack == "required":
        issues.append("Archive acknowledgement is required but not confirmed")
    if ack == "pending":
        issues.append("Archive acknowledgement is pending; replay and durability not confirmed")
    result["issues"] = issues

    return result


def adapt_chat(
    payload: dict[str, Any],
    *,
    service_state: str = "unknown",
    helper_sha: str = "",
    component: str = "",
) -> dict[str, Any]:
    """Build a dashboard row for Idle Hacking chat from the raw helper payload."""
    _ensure_loaded()
    v2 = _ADAPTER_CHAT_FN(payload)
    return _v2_to_row(
        v2,
        "Idle Hacking chat",
        "Idle Hacking Collector / Chrome + helper",
        "ROADMAP §4I-G1",
        service_state,
        helper_sha,
        component,
    )


def adapt_market(
    payload: dict[str, Any],
    *,
    service_state: str = "unknown",
    helper_sha: str = "",
    component: str = "",
) -> dict[str, Any]:
    """Build a dashboard row for Idle Hacking market from the raw helper payload."""
    _ensure_loaded()
    v2 = _ADAPTER_MARKET_FN(payload)
    return _v2_to_row(
        v2,
        "Idle Hacking market",
        "Idle Hacking Collector / Chrome + helper",
        "ROADMAP §4D-G1",
        service_state,
        helper_sha,
        component,
    )
