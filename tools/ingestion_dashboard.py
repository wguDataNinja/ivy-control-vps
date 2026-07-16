#!/usr/bin/env python3
"""Generate a private, read-only ingestion operations dashboard.

The dashboard is intentionally a transitional view: it combines safe live VPS
measurements with current control evidence, labels their provenance, and makes
missing adapters visible as UNKNOWN.  It never reads secrets or browser
profiles and never changes production state.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "_internal" / "generated" / "ingestion-dashboard"
ROADMAP = ROOT / "ROADMAP.md"
UTC = dt.timezone.utc
STATUSES = ("GREEN", "YELLOW", "RED", "UNKNOWN")

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


def ssh(remote_command: str) -> tuple[bool, str]:
    if not shutil.which("ssh"):
        return False, "ssh unavailable on this Mac"
    return run(["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", "ih-market-vps", remote_command])


def iso_from_systemd(value: str) -> str:
    # systemd's human date is useful evidence even when it cannot be parsed
    # portably; label it as host time rather than inventing a conversion.
    return value.strip() or "unknown"


def row(name: str, collector: str, reference: str) -> dict:
    return {
        "workload": name, "collector": collector, "reference": reference,
        "last_success": "unknown", "source_freshness": "unknown",
        "db_freshness": "unknown", "offload": "unknown", "backup": "unknown",
        "capacity": "unknown", "status": "UNKNOWN", "evidence_level": "unknown",
        "evidence_timestamp": now(), "detail": {}, "issues": [],
    }


def control_text(path: str) -> str:
    try:
        return (ROOT / path).read_text(encoding="utf-8")
    except OSError:
        return ""


def collect_reddit() -> dict:
    result = row("WGU Reddit", "wgu-reddit-postgres-run.timer", "ROADMAP §7B-G1")
    command = (
        "systemctl --user show wgu-reddit-postgres-run.timer "
        "-p ActiveState -p UnitFileState --value; echo ---; "
        "systemctl --user show wgu-reddit-postgres-run.service "
        "-p Result -p ExecMainExitTimestamp -p ActiveState --value; echo ---; "
        "systemctl --user show wgu-reddit-shadow-run.timer -p ActiveState -p UnitFileState --value; echo ---; "
        "systemctl --user show wgu-reddit-backup.service -p Result -p ExecMainExitTimestamp --value"
    )
    ok, output = ssh(command)
    if not ok:
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
        result["source_freshness"] = "unknown (monitor-role source/frontier adapter pending)"
        result["db_freshness"] = "unknown (monitor-role DB adapter pending)"
    if backup and "success" not in backup:
        result["backup"] = "FAILED: systemd backup unit"
        result["status"] = "RED"
        result["issues"].append("Backup service currently failed; canonicality cannot be verified")
    else:
        result["backup"] = "unknown"
        result["status"] = "UNKNOWN"
    return result


def collect_ih() -> tuple[dict, dict]:
    chat = row("Idle Hacking chat", "Idle Hacking Collector / Chrome + helper", "ROADMAP §4I-G1")
    market = row("Idle Hacking market", "Idle Hacking Collector / Chrome + helper", "ROADMAP §4D-G1")
    ok, output = ssh("curl --max-time 5 -s http://127.0.0.1:8765/health; echo; systemctl --user is-active ih-collector-helper.service")
    if not ok:
        for item in (chat, market):
            item["issues"].append("Live browser/helper evidence unavailable: " + output)
        return chat, market
    payload_text, _, service_state = output.rpartition("\n")
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        for item in (chat, market):
            item["issues"].append("Malformed helper health payload; treated as UNKNOWN")
        return chat, market
    retention = payload.get("storage_retention", {}) if isinstance(payload, dict) else {}
    for item in (chat, market):
        item["evidence_level"] = "live"
        item["detail"]["component"] = "Idle Hacking Collector (namespace ih-market-companion; observed v2026-05-03.3)"
        item["detail"]["helper_service"] = service_state.strip() or "unknown"
        item["detail"]["userscript_authority"] = "unresolved; installed-copy verification unavailable"
        item["detail"]["helper_sha256"] = "7747c2eb…bec1020 (fresh 2026-07-15 inspection)"
        item["capacity"] = "unknown (host adapter pending)"
        item["backup"] = "unknown (acknowledgement is not backup)"
    chat_data = payload.get("chat", {})
    chat_retention = retention.get("chat", {}) if isinstance(retention, dict) else {}
    chat["last_success"] = chat_retention.get("updated_at", "unknown")
    chat["source_freshness"] = chat_data.get("last_message_at", "unknown")
    chat["db_freshness"] = "unknown (metadata DB does not prove raw chat capture)"
    chat["offload"] = chat_retention.get("archive_acknowledgement_status", "unknown")
    chat["detail"].update({"helper_reported_status": chat_data.get("status", "unknown"), "current_durable_write": chat_retention.get("durable_local_write_status", "unknown"), "collection": chat_retention.get("collection_status", "unknown"), "lifetime_writes_ok": chat_data.get("writes_ok", "unknown"), "lifetime_writes_failed": chat_data.get("writes_failed", "unknown"), "retention": chat_retention.get("chat", {})})
    # The known counter is lifetime cumulative.  It cannot make a current good
    # local write red; lack of a current/consecutive-failure adapter is yellow.
    if chat_retention.get("durable_local_write_status") == "failed":
        chat["status"] = "RED"
        chat["issues"].append("Current durable chat write failed")
    elif chat_retention.get("collection_status") == "success":
        chat["status"] = "YELLOW"
        chat["issues"].append("Current write looks successful, but status semantics, source authority, and archive acknowledgement remain unresolved")
    else:
        chat["status"] = "UNKNOWN"
    market_data = payload.get("market", {})
    market_retention = retention.get("market", {}) if isinstance(retention, dict) else {}
    market["last_success"] = market_data.get("last_good_capture_at", "unknown")
    market["source_freshness"] = market_data.get("last_capture_at", "unknown")
    market["db_freshness"] = "unknown (PostgreSQL import/reconciliation pending)"
    market["offload"] = market_retention.get("archive_acknowledgement_status", "unknown")
    market["detail"].update({"helper_reported_status": market_data.get("status", "unknown"), "current_durable_write": market_retention.get("durable_local_write_status", "unknown"), "collection": market_retention.get("collection_status", "unknown"), "retention": market_retention.get("market", {}), "records": {"books": market_data.get("books"), "commodities": market_data.get("commodities")}})
    if market_retention.get("durable_local_write_status") == "failed":
        market["status"] = "RED"
        market["issues"].append("Current durable market write failed")
    elif market_data.get("status") == "ok":
        market["status"] = "YELLOW" if market["offload"] != "current" else "YELLOW"
        market["issues"].append("Capture is current, but archive acknowledgement/source authority are unresolved")
    return chat, market


def collect_capacity() -> dict:
    result = row("VPS capacity", "VPS host", "ROADMAP §3E")
    ok, output = ssh("df -P / | tail -1; df -Pi / | tail -1; free -h | sed -n '2p'")
    if not ok:
        result["issues"].append("Live capacity unavailable: " + output)
        return result
    lines = output.splitlines()
    if not lines:
        result["issues"].append("Malformed capacity response")
        return result
    parts = lines[0].split()
    try:
        used_pct = int(parts[4].rstrip("%"))
    except (IndexError, ValueError):
        result["issues"].append("Cannot parse root filesystem utilization")
        return result
    result.update({"evidence_level": "live", "last_success": now(), "source_freshness": "not applicable", "db_freshness": "not applicable", "offload": "not applicable", "backup": "not applicable", "capacity": f"{parts[3]} free / {used_pct}% used", "status": "GREEN" if used_pct < 80 else "YELLOW" if used_pct <= 85 else "RED"})
    result["detail"] = {"filesystem": lines[0], "inodes": lines[1] if len(lines) > 1 else "unknown", "memory": lines[2] if len(lines) > 2 else "unknown"}
    if used_pct >= 85:
        result["issues"].append("Capacity deployment stop threshold reached")
    return result


def traderie_fallback() -> dict:
    result = row("Traderie", "traderie-ingest-snapshot.timer", "ROADMAP §7A-G1")
    text = control_text("repos/traderie/CONTROL.md")
    if "pc_hc_nl" in text and "timed out" in text:
        result.update({"status": "RED", "evidence_level": "control-doc", "source_freshness": "unknown", "db_freshness": "unknown", "offload": "not applicable", "backup": "unknown", "capacity": "unknown"})
        result["issues"].append("Control evidence records a failed natural run; no fresh Traderie probe adapter")
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
        "<tr class='{status}'><td>{workload}</td><td>{collector}</td><td>{last_success}</td><td>{source}</td><td>{db}</td><td>{offload}</td><td>{backup}</td><td>{capacity}</td><td><strong>{status}</strong><br><small>{level}</small></td></tr>".format(
            status=cell(r["status"]), workload=cell(r["workload"]), collector=cell(r["collector"]), last_success=cell(r["last_success"]), source=cell(r["source_freshness"]), db=cell(r["db_freshness"]), offload=cell(r["offload"]), backup=cell(r["backup"]), capacity=cell(r["capacity"]), level=cell(r["evidence_level"])
        ) for r in rows
    )
    details = "\n".join("<details><summary><strong>{}</strong> — {} ({})</summary><pre>{}</pre><p>{}</p></details>".format(cell(r["workload"]), cell(r["status"]), cell(r["evidence_level"]), cell(json.dumps(r["detail"], indent=2, sort_keys=True)), cell("; ".join(r["issues"]) or "No additional issue text")) for r in rows)
    priorities = "".join(f"<li>{cell(item)}</li>" for item in coverage["priorities"]) or "<li>No matching roadmap priority lines found.</li>"
    unmapped = ", ".join(coverage["unmapped"]) if coverage["unmapped"] else "None"
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>Ivy ingestion dashboard</title><style>
body{{font-family:system-ui,sans-serif;margin:2rem;color:#171717}} table{{border-collapse:collapse;width:100%;font-size:.9rem}}th,td{{border:1px solid #bbb;padding:.55rem;text-align:left;vertical-align:top}}th{{background:#eee}}.GREEN{{background:#e8f5e9}}.YELLOW{{background:#fff8d8}}.RED{{background:#ffe5e5}}.UNKNOWN{{background:#eeeeee}}pre{{white-space:pre-wrap;word-break:break-word}}small{{color:#555}}.notice{{padding:.75rem;background:#fff8d8;border-left:4px solid #b8860b}}</style></head><body>
<h1>Ivy ingestion dashboard</h1><p class='notice'>Generated {cell(now())}. Live evidence is preferred; control/roadmap evidence cannot render GREEN. Browser/helper process health does not prove chat or market capture and offload.</p>
<p><strong>Summary:</strong> GREEN {counts['GREEN']} · YELLOW {counts['YELLOW']} · RED {counts['RED']} · UNKNOWN {counts['UNKNOWN']}. <strong>Highest priority:</strong> {cell(highest['workload'] + ': ' + '; '.join(highest['issues'])) if highest else 'none'}</p>
<table><thead><tr><th>Workload</th><th>Collector</th><th>Last success</th><th>Source freshness</th><th>DB freshness</th><th>Offload / sync</th><th>Backup</th><th>Capacity</th><th>Status</th></tr></thead><tbody>{table}</tbody></table>
<h2>Details</h2>{details}<h2>ROADMAP.md coverage</h2><p>Expected ingestion workload labels missing from roadmap: <strong>{cell(unmapped)}</strong>.</p><h3>Open priority items</h3><ul>{priorities}</ul>
<p><small>Status rules: GREEN requires current live/producer evidence for required path; YELLOW is pending/incomplete/grace; RED is a current hard failure/stale critical condition; UNKNOWN is absent or unverified evidence.</small></p></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate private read-only ingestion dashboard")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--no-live", action="store_true", help="Do not use read-only SSH; render only safe fallback evidence")
    args = parser.parse_args()
    global ssh
    if args.no_live:
        original_ssh = ssh
        ssh = lambda _: (False, "live evidence disabled by --no-live")  # type: ignore[assignment]
    reddit = collect_reddit()
    chat, market = collect_ih()
    capacity = collect_capacity()
    traderie = traderie_fallback()
    rows = [reddit, chat, market, traderie, capacity]
    coverage = roadmap_coverage()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    data = {"generated_at": now(), "rows": rows, "roadmap_coverage": coverage, "missing_live_adapters": ["Reddit monitor-role canonicality/source/DB/duplicate-gap adapter", "Traderie live exporter adapter", "IH installed-userscript source verification", "IH acknowledgement destination/receipt adapter", "portfolio recurring host-capacity producer"]}
    (args.output_dir / "status.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output_dir / "index.html").write_text(render(rows, coverage), encoding="utf-8")
    print(args.output_dir / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
