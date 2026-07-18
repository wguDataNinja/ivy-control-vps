#!/usr/bin/env python3
"""Generate a private, read-only ingestion operations dashboard.

The dashboard is intentionally a transitional view: it combines safe live VPS
measurements with current control evidence, labels their provenance, and makes
missing adapters visible as UNKNOWN.  It never reads secrets or browser
profiles and never changes production state.

Execution modes
---------------
auto     — try direct (systemd locally), fall back to remote SSH
direct   — run all probes locally (VPS mode, no SSH)
remote   — run probes via SSH (Mac mode, configurable host)
no-live  — skip live probes, use only fallback evidence
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "_internal" / "generated" / "ingestion-dashboard"
ROADMAP = ROOT / "ROADMAP.md"
UTC = dt.timezone.utc
STATUSES = ("GREEN", "YELLOW", "RED", "UNKNOWN")
EVIDENCE_LEVELS = ("live", "evidence_card", "stale", "missing_producer", "unsupported_field", "doc_fallback", "unresolved_authority")
SUMMARY_ORDER = {"UNKNOWN": 0, "RED": 1, "YELLOW": 2, "GREEN": 3}

# Ensure the repository root is on sys.path so that 'from tools.*' imports
# work regardless of the caller's working directory.
_THIS_DIR = str(ROOT)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

# This small registry is intentionally explicit rather than a fragile
# general-purpose ROADMAP Markdown parser.  The coverage check below warns if
# expected roadmap ingestion labels disappear or need mapping review.
ROADMAP_WORKLOADS = {
    "Traderie": "§7A-G1",
    "Reddit Ops": "§7B-G1",
    "IH Market Companion": "§4D-G1",
    "Idle Hacking KB": "§4I-G1",
    "SJC Intel": "§4C-G1",
    "WGU Catalog": "§4E-G1",
}


def now() -> str:
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(command: list[str], timeout: int = 18) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    if completed.returncode:
        return False, (completed.stderr or completed.stdout).strip()
    return True, completed.stdout.strip()


# ---------------------------------------------------------------------------
# Transport abstraction — handles direct (VPS) and remote (SSH) execution.
# ---------------------------------------------------------------------------

class Transport:
    """Abstract execution transport.

    Modes
    -----
    auto     — try direct, fall back to remote SSH
    direct   — run probes locally (no SSH)
    remote   — run probes via SSH
    no-live  — skip all live probes
    """

    AUTO = "auto"
    DIRECT = "direct"
    REMOTE = "remote"
    NO_LIVE = "no-live"

    def __init__(self, mode: str = "", host: str = "") -> None:
        mode = mode or os.environ.get("IVY_VPS_MODE", self.AUTO)
        self.host = host or os.environ.get("IVY_VPS_HOST", "")
        if mode == self.AUTO:
            mode = self._detect()
        self.mode = mode

    def _detect(self) -> str:
        ok, _ = run(["systemctl", "--user", "show", "-p", "ActiveState", "--value",
                      "wgu-reddit-postgres-run.timer"])
        if ok:
            return self.DIRECT
        return self.REMOTE

    def exec(self, command: str) -> tuple[bool, str]:
        if self.mode == self.NO_LIVE:
            return False, "live evidence disabled"
        if self.mode == self.DIRECT:
            return run(["sh", "-c", command])
        return self._ssh(command)

    def _ssh(self, command: str) -> tuple[bool, str]:
        if not shutil.which("ssh"):
            return False, "ssh not available"
        host = self.host or "ih-market-vps"
        return run(["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
                     host, command])


# Global transport instance — set in main() before any collector runs.
transport: Transport | None = None


def iso_from_systemd(value: str) -> str:
    # systemd's human date is useful evidence even when it cannot be parsed
    # portably; label it as host time rather than inventing a conversion.
    return value.strip() or "unknown"


def row(name: str, collector: str, reference: str) -> dict:
    return {
        "workload": name, "collector": collector, "reference": reference,
        "last_success": "unknown", "source_freshness": "unknown",
        "db_freshness": "unknown", "offload": "unknown", "backup": "unknown",
        "capacity": "unknown", "status": "UNKNOWN", "evidence_level": "missing_producer",
        "evidence_timestamp": now(), "collected_at": "unknown",
        "detail": {}, "issues": [],
    }


def control_text(path: str) -> str:
    try:
        return (ROOT / path).read_text(encoding="utf-8")
    except OSError:
        return ""


def collect_reddit(_transport: Transport | None = None) -> dict:
    result = row("WGU Reddit", "wgu-reddit-postgres-run.timer", "ROADMAP §7B-G1")
    result["evidence_level"] = "missing_producer"
    result["detail"].update({
        "deployed_revision": "unknown (SCP-managed runtime; no Git checkout)",
        "source_frontier_adapter": "missing_producer (monitor-role source/frontier adapter needed)",
        "source_frontier": "UNKNOWN — no live source frontier adapter",
        "db_frontier_adapter": "missing_producer (monitor-role DB adapter needed)",
        "db_frontier": "UNKNOWN — no live DB frontier adapter",
        "duplicate_gap_adapter": "missing_producer (duplicate/gap check adapter needed)",
        "duplicate_gap": "UNKNOWN — no duplicate/gap adapter",
        "archive_continuity_adapter": "missing_producer (archive continuity adapter needed)",
        "archive_continuity": "UNKNOWN — no archive continuity adapter",
        "recovery_proof": "UNKNOWN — no recovery proof adapter",
        "natural_run_observation": "UNKNOWN — no natural-run observation adapter",
    })
    # Manual and natural recovery proof known regardless of live access
    result["backup"] = "BACKUP_RECOVERY_PROVEN (manual dump/restore proof from Session 9 report 23; natural timer acceptance at 2026-07-16 08:00:14 UTC)"
    t = _transport or transport
    command = (
        "systemctl --user show wgu-reddit-postgres-run.timer "
        "-p ActiveState -p UnitFileState --value; echo ---; "
        "systemctl --user show wgu-reddit-postgres-run.service "
        "-p Result -p ExecMainExitTimestamp -p ActiveState --value; echo ---; "
        "systemctl --user show wgu-reddit-shadow-run.timer -p ActiveState -p UnitFileState --value; echo ---; "
        "systemctl --user show wgu-reddit-backup.service -p Result -p ExecMainExitTimestamp --value"
    )
    ok, output = t.exec(command) if t else (False, "no transport")
    if not ok:
        result["evidence_level"] = "missing_producer"
        result["issues"].append("Live VPS service evidence unavailable: " + output)
        return result
    groups = output.split("\n---\n")
    if len(groups) != 4:
        result["issues"].append("Unexpected systemd response; live state left UNKNOWN")
        return result
    timer, service, legacy, backup = [[x.strip() for x in g.splitlines()] for g in groups]
    result["evidence_level"] = "live"
    result["collected_at"] = now()
    result["detail"].update({"scheduler": timer, "service": service, "legacy_scheduler": legacy, "backup_unit": backup, "sole_writer": "candidate only; DB lock/query adapter pending"})
    if "success" in service:
        result["last_success"] = iso_from_systemd(next((item for item in service if item != "success" and item != "inactive"), "unknown"))
        result["source_freshness"] = "missing_producer (monitor-role source/frontier adapter needed)"
        result["db_freshness"] = "missing_producer (monitor-role DB adapter needed)"
        result["detail"]["source_frontier_adapter"] = "missing_producer (monitor-role source/frontier adapter needed)"
        result["detail"]["db_frontier_adapter"] = "missing_producer (monitor-role DB adapter needed)"
    # Criterion-level canonicality — each dimension independent, live or UNKNOWN
    result["detail"]["source_frontier"] = "UNKNOWN — requires live source/frontier adapter; psycopg2 not installed on VPS, SQLite old-ID comparison has 0 old IDs missing from PG"
    result["detail"]["db_frontier"] = "UNKNOWN — requires live DB frontier adapter; PostgreSQL 45,469 posts observed; VPS lacks psycopg2 for programmatic ID extract"
    result["detail"]["duplicate_gap"] = "UNKNOWN — requires duplicate/gap adapter; manual check found 0 duplicate IDs in both sources; 561 PG-only IDs (559 later than old frontier) require review"
    result["detail"]["archive_continuity"] = "UNKNOWN — requires archive continuity adapter; no DB export records; filesystem backup inventory exists but archive check has shell defect"
    result["detail"]["recovery_proof"] = "BACKUP_RECOVERY_PROVEN (manual dump, checksum, manifest, pg_restore --list, isolated restore from Session 9 report 23; natural timer acceptance at 2026-07-16 08:00:14 UTC)"
    result["detail"]["natural_run_observation"] = "natural_backup_accepted (timer fired 2026-07-16 08:00:14 UTC; artifact 16,156,397 bytes, SHA-256 and manifest valid; session-9 report 38)"
    if backup and "success" not in backup:
        result["backup"] = "FAILED: systemd backup unit (daily failures since 2026-07-11)"
        result["status"] = "RED"
        result["evidence_level"] = "live"
        result["issues"].append("Backup service currently failed; manual recovery proof from Session 9 remains valid but no current restore; canonicality cannot be fully verified")
    if backup and len(backup) > 0 and backup[0] == "success":
        result["backup"] = "BACKUP_RECOVERY_PROVEN (manual + natural acceptance)"
        result["status"] = "YELLOW"
        result["issues"].append("Backup recovery proven (manual and natural); canonicality dimensions remain UNKNOWN without dedicated adapters (source frontier, DB frontier, duplicates, archive continuity); recovery alone does not constitute canonicality")
    return result


def collect_ih(_transport: Transport | None = None) -> tuple[dict, dict]:
    chat = row("Idle Hacking chat", "Idle Hacking Collector / Chrome + helper", "ROADMAP §4I-G1")
    chat["detail"].update({
        "installed_revision_adapter": "unresolved_authority (no userscript hash verification; inspection of Chrome/Tampermonkey profile not permitted)",
        "replay_proof_adapter": "unsupported_field (no replay mechanism observed)",
        "acknowledgement_destination_adapter": "unresolved_authority (Buddy must decide canonical source and destination)",
        "durable_destination_adapter": "unresolved_authority (no durable archive path contract)",
        "live_chat_exporter_adapter": "missing_producer (no live IH chat exporter adapter deployed)",
        "canonicality_adapter": "missing_producer (no canonicality evidence adapter for IH chat)",
    })
    market = row("Idle Hacking market", "Idle Hacking Collector / Chrome + helper", "ROADMAP §4D-G1")
    market["detail"].update({
        "installed_revision_adapter": "unresolved_authority (no userscript hash verification)",
        "replay_proof_adapter": "unsupported_field (no replay mechanism observed)",
        "acknowledgement_destination_adapter": "unresolved_authority (Buddy must decide canonical source and destination)",
        "postgresql_reconciliation_adapter": "unsupported_field (no PG market import pilot)",
        "live_market_exporter_adapter": "missing_producer (no live IH market exporter adapter deployed)",
        "canonicality_adapter": "missing_producer (no canonicality evidence adapter for IH market)",
    })
    t = _transport or transport
    ok, output = t.exec(
        "curl --max-time 5 -s http://127.0.0.1:8765/health; echo; "
        "systemctl --user is-active ih-collector-helper.service"
    ) if t else (False, "no transport")
    if not ok:
        for item in (chat, market):
            item["evidence_level"] = "missing_producer"
            item["issues"].append("Live browser/helper evidence unavailable: " + output)
        return chat, market
    payload_text, _, service_state = output.rpartition("\n")
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        for item in (chat, market):
            item["evidence_level"] = "missing_producer"
            item["issues"].append("Malformed helper health payload; treated as UNKNOWN")
        return chat, market
    if not isinstance(payload, dict):
        for item in (chat, market):
            item["evidence_level"] = "missing_producer"
            item["issues"].append("Non-dict payload from helper; treated as UNKNOWN")
        return chat, market
    from tools.ih_dashboard_adapter import adapt_chat, adapt_market
    helper_sha = "7747c2eb…bec1020 (observed 2026-07-15; not runtime-verified — installed-copy verification unavailable)"
    component = "Idle Hacking Collector (namespace ih-market-companion; observed v2026-05-03.3)"
    try:
        chat = adapt_chat(payload, service_state=service_state.strip() or "unknown", helper_sha=helper_sha, component=component)
        market = adapt_market(payload, service_state=service_state.strip() or "unknown", helper_sha=helper_sha, component=component)
    except (FileNotFoundError, ImportError, AttributeError) as exc:
        # The adapters live in separate repositories and are intentionally
        # optional on the VPS.  Their absence is evidence of a missing
        # producer, never a reason for the operator dashboard to abort.
        for item in (chat, market):
            item["evidence_level"] = "missing_producer"
            item["issues"].append(
                "Idle Hacking adapter unavailable; live helper payload is not "
                f"mapped to a dashboard row: {type(exc).__name__}"
            )
        return chat, market
    return chat, market


def collect_capacity(_transport: Transport | None = None) -> dict:
    result = row("VPS / control plane", "VPS host", "ROADMAP §3E")
    result["detail"].update({
        "deployed_revision_adapter": "missing_producer (no ivy-control-vps checkout on VPS)",
        "drift_adapter": "missing_producer (no checkout to compare drift)",
        "capacity_snapshot_adapter": "missing_producer (no recurring capacity snapshot producer deployed)",
        "postgresql_wal_adapter": "missing_producer (no WAL measurement adapter deployed)",
        "postgresql_wal": "unavailable/WAL not measured (no access to pg_wal — permission or path issue; NOT zero)",
    })

    t = _transport or transport
    ok, output = t.exec(
        "df -P / | tail -1; df -Pi / | tail -1; free -b | sed -n '2,3p'; "
        "psql -d postgres -t -A -c \"SELECT COALESCE(SUM(pg_database_size(datname)), 0) FROM pg_database;\" 2>/dev/null || echo 'PG_DATA_UNAVAILABLE'; "
        "du -sb /var/lib/postgresql/*/pg_wal 2>/dev/null || echo 'PG_WAL_UNAVAILABLE'"
    ) if t else (False, "no transport")
    if not ok:
        result["evidence_level"] = "missing_producer"
        result["issues"].append("Live capacity unavailable: " + output)
        return result
    lines = output.splitlines()
    if not lines:
        result["evidence_level"] = "missing_producer"
        result["issues"].append("Malformed capacity response")
        return result
    parts = lines[0].split()
    try:
        used_pct = int(parts[4].rstrip("%"))
    except (IndexError, ValueError):
        result["evidence_level"] = "missing_producer"
        result["issues"].append("Cannot parse root filesystem utilization")
        return result
    free_blocks = int(parts[3]) if len(parts) > 3 else 0
    free_gb = round(free_blocks * 1024 / (1024 ** 3), 1)
    collected = now()
    result.update({"evidence_level": "live", "last_success": collected, "source_freshness": "not applicable", "db_freshness": "not applicable", "offload": "not applicable", "backup": "not applicable", "capacity": f"{free_gb}G free / {used_pct}% used", "status": "GREEN" if used_pct < 80 else "YELLOW" if used_pct <= 85 else "RED", "collected_at": collected})
    inode_line = lines[1] if len(lines) > 1 else "unknown"
    mem_lines = "\n".join(lines[2:]) if len(lines) > 2 else "unknown"
    # Parse PG data and WAL from remaining lines
    pg_data = "unavailable/PG not measured"
    pg_wal = "unavailable/WAL not measured"
    for line in lines[3:]:
        stripped = line.strip()
        if stripped == "PG_DATA_UNAVAILABLE":
            pg_data = "unavailable/PG not measured"
            break
        elif stripped and stripped != "PG_WAL_UNAVAILABLE" and not stripped.startswith("du: cannot access"):
            pg_data = f"{stripped} bytes"
    for line in lines[3:]:
        stripped = line.strip()
        if stripped == "PG_WAL_UNAVAILABLE":
            pg_wal = "unavailable/WAL not measured"
            break
        elif stripped and stripped != "PG_DATA_UNAVAILABLE" and not stripped.startswith("du: cannot access"):
            pg_wal = f"{stripped} bytes"
    result["detail"].update({
        "filesystem": lines[0], "inodes": inode_line, "memory": mem_lines,
        "deployed_revision_adapter": "missing_producer (no ivy-control-vps checkout on VPS)",
        "drift_adapter": "missing_producer (no checkout to compare drift)",
        "capacity_snapshot_adapter": "missing_producer",
        "disk_free_gb": free_gb, "disk_used_pct": used_pct,
        "postgresql_data": pg_data,
        "postgresql_wal": pg_wal,
    })
    if used_pct >= 85:
        result["issues"].append("Capacity deployment stop threshold reached")
    elif used_pct >= 80 or free_gb < 7:
        result["issues"].append("Capacity warning threshold approached")
    return result


def traderie_unknown() -> dict:
    result = row("Traderie", "traderie-ingest-snapshot.timer", "ROADMAP §7A-G1")
    result["evidence_level"] = "missing_producer"
    result["detail"].update({
        "deployed_revision": "unknown (no live probe adapter)",
        "live_exporter_adapter": "missing_producer (no live Traderie probe adapter deployed)",
        "scheduler_owner": "missing_producer (root systemd timer confirmed by Session 9 live discovery; no live probe to report current state)",
        "authority_type": "file_based (PG traderie DB has zero non-system tables; data is file-authoritative)",
        "postgresql": "zero_non_system_tables (PG traderie DB reachable but contains zero application tables)",
    })
    result["issues"].append("No live Traderie probe adapter deployed; status is UNKNOWN. Session 9 confirmed root systemd timer and file-based authority.")
    return result


def passport_recovery_unknown() -> dict:
    """Represent missing dated backup evidence without treating policy as proof."""
    result = row("Passport / backup", "recovery-confidence review", "ROADMAP P0")
    result["detail"].update({
        "recovery_confidence_adapter": "missing_producer (dated recovery-confidence observation needed)",
        "recovery_confidence": "UNKNOWN — no dated recovery-confidence observation supplied",
        "evidence_requirement": "verified snapshot, restore proof, review date, policy hash, and expiry",
    })
    result["issues"].append(
        "No dated Passport recovery-confidence evidence is available to this read-only view."
    )
    return result


def passport_recovery_evidence(evidence_path: Path | None = None) -> dict:
    """Evaluate one explicitly supplied Passport evidence card, if present.

    The path is intentionally opt-in: this read-only surface never searches
    backup locations or private workflow directories for evidence.
    """
    if evidence_path is None:
        return passport_recovery_unknown()

    from tools.evidence_cards import evaluate_card, load_card, validate_card

    result = row("Passport / backup", "recovery-confidence review", "ROADMAP P0")
    try:
        card = load_card(evidence_path)
    except ValueError as exc:
        result["detail"]["recovery_confidence_adapter"] = "evidence_card (unreadable)"
        result["detail"]["recovery_confidence"] = "UNKNOWN — supplied evidence card could not be read"
        result["issues"].append(f"Passport recovery-confidence evidence card is unreadable: {exc}")
        return result

    errors = validate_card(card, expected_asset="passport", expected_evidence_type="recovery_confidence")
    if errors:
        result["detail"]["recovery_confidence_adapter"] = "evidence_card (invalid)"
        result["detail"]["recovery_confidence"] = "UNKNOWN — supplied evidence card is invalid"
        result["issues"].append("Passport recovery-confidence evidence card is invalid: " + "; ".join(errors))
        return result

    confidence_state, reason = evaluate_card(card)
    result["evidence_level"] = "evidence_card"
    result["confidence_state"] = confidence_state
    result["status"] = {"VERIFIED": "GREEN", "DEGRADED": "YELLOW", "UNKNOWN": "UNKNOWN"}[confidence_state]
    result["last_success"] = card["observed_at"]
    result["source_freshness"] = "dated evidence card"
    result["backup"] = confidence_state
    result["evidence_timestamp"] = card["observed_at"]
    result["collected_at"] = card["observed_at"]
    result["detail"].update({
        "recovery_confidence_adapter": "evidence_card (explicit local input)",
        "recovery_confidence": confidence_state,
        "observed_at": card["observed_at"],
        "expires_at": card["expires_at"],
        "verification_method": card["verification_method"],
        "policy_reference": card["policy_reference"],
        "disposition": card["disposition"],
        "evidence_requirement": "dated observation, verification method, findings, disposition, and expiry",
    })
    result["issues"].append(reason)
    return result


def collect_rows(active_transport: Transport, passport_evidence: Path | None = None) -> list[dict]:
    """Collect the bounded, read-only portfolio observation set."""
    reddit = collect_reddit(active_transport)
    chat, market = collect_ih(active_transport)
    capacity = collect_capacity(active_transport)
    return [reddit, chat, market, traderie_unknown(), passport_recovery_evidence(passport_evidence), capacity]


def roadmap_coverage() -> dict:
    try:
        text = ROADMAP.read_text(encoding="utf-8")
    except OSError as exc:
        return {"roadmap_read": False, "unmapped": list(ROADMAP_WORKLOADS), "error": str(exc), "priorities": []}
    missing = [name for name in ROADMAP_WORKLOADS if name not in text]
    priorities = []
    for line in text.splitlines():
        low = line.lower()
        if any(term in low for term in ("health", "backup", "canonical", "browser", "ingestion")) and (line.startswith("- ") or line.startswith("1.") or line.startswith("2.")):
            priorities.append(line.strip())
    return {"roadmap_read": True, "unmapped": missing, "priorities": priorities[:12]}


def format_summary(rows: list[dict]) -> str:
    """Render a concise operator/Hermes surface from normalized dashboard rows."""
    attention = [row for row in rows if row["status"] != "GREEN"]
    verified = [row for row in rows if row.get("confidence_state") == "VERIFIED"]
    attention.sort(key=lambda item: (SUMMARY_ORDER.get(item["status"], 99), item["workload"]))
    lines = ["Ivy Control Portfolio Health", "", "P0 attention:"]
    for item in attention:
        reason = item["issues"][0] if item["issues"] else "No current evidence reason supplied."
        lines.extend(["", f"{item['workload']}", item.get("confidence_state", item["status"]), f"Reason: {reason}"])

    if verified:
        lines.extend(["", "Current verified evidence:"])
        for item in verified:
            lines.append(f"- {item['workload']}: VERIFIED (expires {item['detail'].get('expires_at', 'unknown')})")

    recommendations = {
        "WGU Reddit": "Verify current Reddit recovery, canonicality, and single-writer evidence.",
        "Idle Hacking chat": "Review Idle Hacking chat capture, acknowledgement, and replay evidence.",
        "Idle Hacking market": "Review Idle Hacking market collector and durable-offload evidence.",
        "Traderie": "Collect a current Traderie exporter, backup, and natural-run observation.",
        "Passport / backup": "Refresh Passport recovery-confidence evidence with an explicit expiry.",
        "VPS / control plane": "Collect a current VPS capacity and control-plane observation.",
    }
    lines.extend(["", "Recommended next actions:"])
    for index, item in enumerate(attention, start=1):
        action = recommendations.get(item["workload"], "Collect current evidence and route the next bounded action.")
        lines.append(f"{index}. {action}")
    return "\n".join(lines) + "\n"


def render(rows: list[dict], coverage: dict) -> str:
    counts = {status: sum(r["status"] == status for r in rows) for status in STATUSES}
    highest = next((r for r in rows if r["status"] == "RED"), next((r for r in rows if r["status"] == "YELLOW"), None))
    def cell(value: object) -> str:
        return html.escape(str(value))
    table = "\n".join(
        "<tr class='{status}'><td>{workload}</td><td>{collector}</td><td>{last_success}</td><td>{source}</td><td>{db}</td><td>{offload}</td><td>{backup}</td><td>{capacity}</td><td>{collected}</td><td><strong>{status}</strong><br><small class='ev-{level}'>{level}</small></td></tr>".format(
            status=cell(r["status"]), workload=cell(r["workload"]), collector=cell(r["collector"]), last_success=cell(r["last_success"]), source=cell(r["source_freshness"]), db=cell(r["db_freshness"]), offload=cell(r["offload"]), backup=cell(r["backup"]), capacity=cell(r["capacity"]), collected=cell(r.get("collected_at", "unknown")), level=cell(r["evidence_level"])
        ) for r in rows
    )
    details = "\n".join("<details><summary><strong>{}</strong> — {} ({})</summary><pre>{}</pre><p>{}</p></details>".format(cell(r["workload"]), cell(r["status"]), cell(r["evidence_level"]), cell(json.dumps(r["detail"], indent=2, sort_keys=True)), cell("; ".join(r["issues"]) or "No additional issue text")) for r in rows)
    priorities = "".join(f"<li>{cell(item)}</li>" for item in coverage["priorities"]) or "<li>No matching roadmap priority lines found.</li>"
    unmapped = ", ".join(coverage["unmapped"]) if coverage["unmapped"] else "None"
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>Ivy Control Portfolio Health</title><style>
body{{font-family:system-ui,sans-serif;margin:2rem;color:#171717}} table{{border-collapse:collapse;width:100%;font-size:.9rem}}th,td{{border:1px solid #bbb;padding:.55rem;text-align:left;vertical-align:top}}th{{background:#eee}}.GREEN{{background:#e8f5e9}}.YELLOW{{background:#fff8d8}}.RED{{background:#ffe5e5}}.UNKNOWN{{background:#eeeeee}}pre{{white-space:pre-wrap;word-break:break-word}}small{{color:#555}}.ev-live,.ev-evidence_card{{color:#2e7d32}}.ev-stale{{color:#e65100}}.ev-missing_producer{{color:#c62828;font-weight:bold}}.ev-unsupported_field{{color:#6a1b9a}}.ev-doc_fallback{{color:#e65100;font-style:italic}}.ev-unresolved_authority{{color:#6a1b9a;font-style:italic}}.notice{{padding:.75rem;background:#fff8d8;border-left:4px solid #b8860b}}</style></head><body>
<h1>Ivy Control Portfolio Health</h1><p class='notice'>Generated {cell(now())}. Evidence levels: <strong class='ev-live'>live</strong> (fresh observation) · <strong class='ev-evidence_card'>evidence_card</strong> (explicit dated local observation) · <strong class='ev-stale'>stale</strong> (exceeds freshness) · <strong class='ev-missing_producer'>missing_producer</strong> · <strong class='ev-unsupported_field'>unsupported_field</strong> · <strong class='ev-doc_fallback'>doc_fallback</strong> (not live) · <strong class='ev-unresolved_authority'>unresolved_authority</strong> (needs Buddy). Doc_fallback evidence cannot render GREEN. Browser/helper process health does not prove chat or market capture and offload.</p>
<p><strong>Summary:</strong> GREEN {counts['GREEN']} · YELLOW {counts['YELLOW']} · RED {counts['RED']} · UNKNOWN {counts['UNKNOWN']}. <strong>Highest priority:</strong> {cell(highest['workload'] + ': ' + '; '.join(highest['issues'])) if highest else 'none'}</p>
<table><thead><tr><th>Workload</th><th>Collector</th><th>Last success</th><th>Source freshness</th><th>DB freshness</th><th>Offload / sync</th><th>Backup</th><th>Capacity</th><th>Collected at</th><th>Status</th></tr></thead><tbody>{table}</tbody></table>
<h2>Details</h2>{details}<h2>ROADMAP.md coverage</h2><p>Expected ingestion workload labels missing from roadmap: <strong>{cell(unmapped)}</strong>.</p><h3>Open priority items</h3><ul>{priorities}</ul>
<p><small>Status rules: GREEN requires current live/producer evidence for required path; YELLOW is pending/incomplete/grace; RED is a current hard failure/stale critical condition; UNKNOWN is absent or unverified evidence.</small></p></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate private read-only ingestion dashboard")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--mode", choices=("auto", "direct", "remote", "no-live"),
                        default="", help="Execution transport mode")
    parser.add_argument("--host", default="",
                        help="SSH host for remote execution (env: IVY_VPS_HOST)")
    parser.add_argument("--no-live", action="store_true",
                        help="Alias for --mode=no-live")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON to stdout (machine-readable)")
    parser.add_argument("--summary", action="store_true",
                        help="Output a concise read-only operator/Hermes health summary")
    parser.add_argument("--passport-evidence", type=Path,
                        help="explicit local Passport recovery-confidence JSON card; never searched automatically")
    parser.add_argument("--stdout-only", action="store_true",
                        help="Do not write dashboard files; emit only requested stdout output")
    args = parser.parse_args()
    if args.no_live:
        args.mode = args.mode or "no-live"
    global transport
    transport = Transport(mode=args.mode, host=args.host)
    rows = collect_rows(transport, passport_evidence=args.passport_evidence)
    coverage = roadmap_coverage()
    missing_live_adapters = [
        "Reddit: source-frontier adapter (missing_producer)",
        "Reddit: DB-frontier adapter (missing_producer)",
        "Reddit: duplicate/gap adapter (missing_producer)",
        "Reddit: archive-continuity adapter (missing_producer)",
        "Reddit: canonicality evidence (unresolved_authority)",
        "Reddit: backup/restore proof adapter (missing_producer)",
        "Traderie: live exporter probe adapter (missing_producer)",
        "Traderie: backup-age/restore adapter (missing_producer)",
        "Traderie: timeout/progress instrumentation (unsupported_field; local source 137dd64 has it)",
        "IH: installed-userscript source verification (unresolved_authority)",
        "IH: acknowledgement destination/receipt adapter (unresolved_authority)",
        "IH: replay proof (unsupported_field)",
        "IH: durable destination contract (unresolved_authority)",
        "IH market: PostgreSQL reconciliation (unsupported_field)",
        "VPS: recurring capacity snapshot producer (missing_producer)",
        "VPS: control-plane deployed-revision producer (missing_producer)",
        "VPS: checkout drift producer (missing_producer)",
    ]
    passport_row = next(row for row in rows if row["workload"] == "Passport / backup")
    if passport_row["evidence_level"] != "evidence_card":
        missing_live_adapters.append("Passport: dated recovery-confidence observation (missing_producer)")
    data: dict[str, Any] = {
        "generated_at": now(), "rows": rows, "roadmap_coverage": coverage,
        "execution_mode": transport.mode,
        "missing_live_adapters": missing_live_adapters,
    }
    if not args.stdout_only and not args.summary:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "status.json").write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8",
        )
        (args.output_dir / "index.html").write_text(render(rows, coverage), encoding="utf-8")
    if args.summary:
        sys.stdout.write(format_summary(rows))
    elif args.json:
        json.dump(data, sys.stdout, indent=2, sort_keys=True, default=str)
        sys.stdout.write("\n")
    else:
        if args.stdout_only:
            parser.error("--stdout-only requires --json or --summary")
        print(args.output_dir / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
