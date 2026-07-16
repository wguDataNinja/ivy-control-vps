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
EVIDENCE_LEVELS = ("live", "stale", "missing_producer", "unsupported_field", "doc_fallback", "unresolved_authority")

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
        "evidence_timestamp": now(), "detail": {}, "issues": [],
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
        "canonicality": "unresolved_authority — needs source/DB frontier, duplicate/gap check, archive continuity, lock proof, fresh backup/restore, natural-run observation",
        "source_frontier_adapter": "missing_producer",
        "db_frontier_adapter": "missing_producer",
        "duplicate_gap_adapter": "missing_producer",
        "archive_continuity_adapter": "missing_producer",
    })
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
    result["detail"].update({"scheduler": timer, "service": service, "legacy_scheduler": legacy, "backup_unit": backup, "sole_writer": "candidate only; DB lock/query adapter pending"})
    if "success" in service:
        result["last_success"] = iso_from_systemd(next((item for item in service if item != "success" and item != "inactive"), "unknown"))
        result["source_freshness"] = "missing_producer (monitor-role source/frontier adapter needed)"
        result["db_freshness"] = "missing_producer (monitor-role DB adapter needed)"
    if backup and "success" not in backup:
        result["backup"] = "FAILED: systemd backup unit (daily failures since 2026-07-11)"
        result["status"] = "RED"
        result["evidence_level"] = "live"
        result["issues"].append("Backup service currently failed; no current restore proof; canonicality cannot be verified")
    if backup and len(backup) > 0 and backup[0] == "success":
        result["backup"] = "current (live systemd evidence)"
        result["status"] = "YELLOW"
        result["issues"].append("Backup OK per systemd, but restore proof, archive continuity, and canonicality remain unverified")
    return result


def collect_ih(_transport: Transport | None = None) -> tuple[dict, dict]:
    chat = row("Idle Hacking chat", "Idle Hacking Collector / Chrome + helper", "ROADMAP §4I-G1")
    chat["detail"]["installed_revision"] = "unresolved_authority (no userscript hash verification; inspection of Chrome/Tampermonkey profile not permitted)"
    chat["detail"]["replay_proof"] = "unsupported_field (no replay mechanism observed)"
    chat["detail"]["acknowledgement_destination"] = "unresolved_authority (Buddy must decide canonical source and destination)"
    chat["detail"]["durable_destination"] = "unresolved_authority (no durable archive path contract)"
    market = row("Idle Hacking market", "Idle Hacking Collector / Chrome + helper", "ROADMAP §4D-G1")
    market["detail"]["installed_revision"] = "unresolved_authority (no userscript hash verification)"
    market["detail"]["replay_proof"] = "unsupported_field (no replay mechanism observed)"
    market["detail"]["acknowledgement_destination"] = "unresolved_authority (Buddy must decide canonical source and destination)"
    market["detail"]["postgresql_reconciliation"] = "unsupported_field (no PG market import pilot)"
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
    chat = adapt_chat(payload, service_state=service_state.strip() or "unknown", helper_sha=helper_sha, component=component)
    market = adapt_market(payload, service_state=service_state.strip() or "unknown", helper_sha=helper_sha, component=component)
    return chat, market


def collect_capacity(_transport: Transport | None = None) -> dict:
    result = row("VPS / control plane", "VPS host", "ROADMAP §3E")
    result["detail"].update({
        "control_plane_deployed_revision": "missing_producer (no ivy-control-vps checkout on VPS)",
        "control_plane_drift": "missing_producer (no checkout to compare)",
        "capacity_producer": "missing_producer (no recurring capacity snapshot producer deployed)",
    })

    try:
        from tools.producers.vps_capacity_snapshot import collect as _producer_collect
        _producer_collect()
    except Exception:
        pass

    t = _transport or transport
    ok, output = t.exec(
        "df -P / | tail -1; df -Pi / | tail -1; free -b | sed -n '2,3p'"
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
    result.update({"evidence_level": "live", "last_success": now(), "source_freshness": "not applicable", "db_freshness": "not applicable", "offload": "not applicable", "backup": "not applicable", "capacity": f"{free_gb}G free / {used_pct}% used", "status": "GREEN" if used_pct < 80 else "YELLOW" if used_pct <= 85 else "RED"})
    inode_line = lines[1] if len(lines) > 1 else "unknown"
    mem_lines = "\n".join(lines[2:]) if len(lines) > 2 else "unknown"
    result["detail"].update({
        "filesystem": lines[0], "inodes": inode_line, "memory": mem_lines,
        "control_plane_deployed_revision": "missing_producer (no ivy-control-vps checkout on VPS)",
        "control_plane_drift": "missing_producer", "capacity_producer": "missing_producer",
        "disk_free_gb": free_gb, "disk_used_pct": used_pct,
    })
    if used_pct >= 85:
        result["issues"].append("Capacity deployment stop threshold reached")
    elif used_pct >= 80 or free_gb < 7:
        result["issues"].append("Capacity warning threshold approached")
    return result


def traderie_fallback() -> dict:
    result = row("Traderie", "traderie-ingest-snapshot.timer", "ROADMAP §7A-G1")
    result["detail"].update({
        "deployed_revision": "e5ebd0f (exact SHA from VPS checkout; clean/detached)",
        "live_exporter_adapter": "missing_producer (no live Traderie probe adapter deployed)",
        "backup_age": "stale (last dump 2026-07-09; backup restore proof missing)",
        "timeout_progress": "unsupported_field (instrumentation not yet deployed; local source at 137dd64 has it)",
        "mutable_data_violation": "1.2 GB mutable data inside Git checkout (violates exact-SHA deployment model)",
    })
    text = control_text("repos/traderie/CONTROL.md")
    if "pc_hc_nl" in text and "timed out" in text:
        result.update({"status": "RED", "evidence_level": "doc_fallback", "source_freshness": "stale (no live exporter; control doc from prior observation)", "db_freshness": "unknown", "offload": "not applicable", "backup": "stale (last backup 2026-07-09)", "capacity": "unknown"})
        result["issues"].append("Control evidence records a failed natural run (pc_hc_nl timeout 2026-07-16); no fresh Traderie probe adapter")
    return result


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


def render(rows: list[dict], coverage: dict) -> str:
    counts = {status: sum(r["status"] == status for r in rows) for status in STATUSES}
    highest = next((r for r in rows if r["status"] == "RED"), next((r for r in rows if r["status"] == "YELLOW"), None))
    def cell(value: object) -> str:
        return html.escape(str(value))
    table = "\n".join(
        "<tr class='{status}'><td>{workload}</td><td>{collector}</td><td>{last_success}</td><td>{source}</td><td>{db}</td><td>{offload}</td><td>{backup}</td><td>{capacity}</td><td><strong>{status}</strong><br><small class='ev-{level}'>{level}</small></td></tr>".format(
            status=cell(r["status"]), workload=cell(r["workload"]), collector=cell(r["collector"]), last_success=cell(r["last_success"]), source=cell(r["source_freshness"]), db=cell(r["db_freshness"]), offload=cell(r["offload"]), backup=cell(r["backup"]), capacity=cell(r["capacity"]), level=cell(r["evidence_level"])
        ) for r in rows
    )
    details = "\n".join("<details><summary><strong>{}</strong> — {} ({})</summary><pre>{}</pre><p>{}</p></details>".format(cell(r["workload"]), cell(r["status"]), cell(r["evidence_level"]), cell(json.dumps(r["detail"], indent=2, sort_keys=True)), cell("; ".join(r["issues"]) or "No additional issue text")) for r in rows)
    priorities = "".join(f"<li>{cell(item)}</li>" for item in coverage["priorities"]) or "<li>No matching roadmap priority lines found.</li>"
    unmapped = ", ".join(coverage["unmapped"]) if coverage["unmapped"] else "None"
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>Ivy ingestion dashboard</title><style>
body{{font-family:system-ui,sans-serif;margin:2rem;color:#171717}} table{{border-collapse:collapse;width:100%;font-size:.9rem}}th,td{{border:1px solid #bbb;padding:.55rem;text-align:left;vertical-align:top}}th{{background:#eee}}.GREEN{{background:#e8f5e9}}.YELLOW{{background:#fff8d8}}.RED{{background:#ffe5e5}}.UNKNOWN{{background:#eeeeee}}pre{{white-space:pre-wrap;word-break:break-word}}small{{color:#555}}.ev-live{{color:#2e7d32}}.ev-stale{{color:#e65100}}.ev-missing_producer{{color:#c62828;font-weight:bold}}.ev-unsupported_field{{color:#6a1b9a}}.ev-doc_fallback{{color:#e65100;font-style:italic}}.ev-unresolved_authority{{color:#6a1b9a;font-style:italic}}.notice{{padding:.75rem;background:#fff8d8;border-left:4px solid #b8860b}}</style></head><body>
<h1>Ivy ingestion dashboard</h1><p class='notice'>Generated {cell(now())}. Evidence levels: <strong class='ev-live'>live</strong> (fresh observation) · <strong class='ev-stale'>stale</strong> (exceeds freshness) · <strong class='ev-missing_producer'>missing_producer</strong> · <strong class='ev-unsupported_field'>unsupported_field</strong> · <strong class='ev-doc_fallback'>doc_fallback</strong> (not live) · <strong class='ev-unresolved_authority'>unresolved_authority</strong> (needs Buddy). Doc_fallback evidence cannot render GREEN. Browser/helper process health does not prove chat or market capture and offload.</p>
<p><strong>Summary:</strong> GREEN {counts['GREEN']} · YELLOW {counts['YELLOW']} · RED {counts['RED']} · UNKNOWN {counts['UNKNOWN']}. <strong>Highest priority:</strong> {cell(highest['workload'] + ': ' + '; '.join(highest['issues'])) if highest else 'none'}</p>
<table><thead><tr><th>Workload</th><th>Collector</th><th>Last success</th><th>Source freshness</th><th>DB freshness</th><th>Offload / sync</th><th>Backup</th><th>Capacity</th><th>Status</th></tr></thead><tbody>{table}</tbody></table>
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
    args = parser.parse_args()
    if args.no_live:
        args.mode = args.mode or "no-live"
    global transport
    transport = Transport(mode=args.mode, host=args.host)
    reddit = collect_reddit()
    chat, market = collect_ih()
    capacity = collect_capacity()
    traderie = traderie_fallback()
    rows = [reddit, chat, market, traderie, capacity]
    coverage = roadmap_coverage()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = {
        "generated_at": now(), "rows": rows, "roadmap_coverage": coverage,
        "execution_mode": transport.mode,
        "missing_live_adapters": [
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
        ],
    }
    (args.output_dir / "status.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    (args.output_dir / "index.html").write_text(render(rows, coverage), encoding="utf-8")
    if args.json:
        json.dump(data, sys.stdout, indent=2, sort_keys=True, default=str)
        sys.stdout.write("\n")
    else:
        print(args.output_dir / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
