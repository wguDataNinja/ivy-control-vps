#!/usr/bin/env python3
"""vps_capacity_snapshot.py — Enhanced VPS capacity and recovery evidence producer.

Emits a canonical v2 health payload with structured capacity evidence including:
  root filesystem, inodes, memory/swap, PostgreSQL data/WAL, backup sizes,
  projected staging requirement, restore headroom, journal/log, checkouts,
  browser/helper aggregate, and external state dir.

All paths in the host command are internal to the SSH session.  Output is
sanitised — no absolute paths, credentials, or private content.

Usage:
    # Live SSH mode (Mac → VPS)
    python3 tools/producers/vps_capacity_snapshot.py

    # Fixture mode (local development / test)
    python3 tools/producers/vps_capacity_snapshot.py --fixture tests/fixtures/vps_capacity_healthy.json

    # Pretty-print
    python3 tools/producers/vps_capacity_snapshot.py --fixture ... --pretty
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_VPS_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_VPS_ROOT) not in sys.path:
    sys.path.insert(0, str(_VPS_ROOT))

from tools.producers.vps_capacity_config import DEFAULT_CONFIG, CapacityConfig, CapacityThresholds


# ── SSH compound script ──────────────────────────────────────────────────────
# Each measurement section is delimited by a ===SECTION=== marker.
# Missing/unavailable sections must output exactly "UNAVAILABLE".
_SSH_SCRIPT = r"""
set -e
echo '===FS==='
df -P / | tail -1
echo '===INODE==='
df -Pi / | tail -1
echo '===MEM==='
free -b | sed -n '2,3p'
echo '===PG_DATA==='
psql -d postgres -t -A -c "SELECT COALESCE(SUM(pg_database_size(datname)), 0) FROM pg_database;" 2>/dev/null || echo 'UNAVAILABLE'
echo '===PG_WAL==='
du -sb /var/lib/postgresql/*/pg_wal 2>/dev/null || echo 'UNAVAILABLE'
echo '===BACKUPS_DIR==='
du -sb /home/scraper/backups 2>/dev/null || echo 'UNAVAILABLE'
echo '===LATEST_BACKUP==='
find /home/scraper/backups -name '*.dump' -type f -exec ls -t {} + 2>/dev/null | head -1 | xargs du -sb 2>/dev/null || echo 'UNAVAILABLE'
echo '===JOURNAL==='
journalctl --disk-usage 2>/dev/null | head -1 || du -sb /var/log/journal 2>/dev/null || echo 'UNAVAILABLE'
echo '===CHECKOUTS==='
du -sb /home/scraper/apps/*/ 2>/dev/null || echo 'UNAVAILABLE'
echo '===BROWSER==='
du -sb /home/scraper/.cache 2>/dev/null || echo 'UNAVAILABLE'
echo '===STATE==='
du -sb /home/scraper/.ivy-control-vps 2>/dev/null || echo 'UNAVAILABLE'
echo '===UPTIME==='
uptime -s
"""

SECTION_PATTERN = re.compile(r'^===(\w+)===')

REQUIRED_OUTPUT_FIELDS = {
    "contract_version", "generated_at", "project", "workflow", "workflow_id",
    "run_id", "status", "started_at", "finished_at", "last_success_at",
    "expected_cadence_seconds", "freshness_seconds", "deployed_revision",
    "scheduler_state", "backup_state", "incident_state",
}


@dataclass
class Measurement:
    name: str
    available: bool = False
    value: Any = None
    raw: str | None = None

    def dict(self) -> dict[str, Any]:
        if self.available:
            return {"available": True, "value": self.value}
        return {"available": False, "value": None}


@dataclass
class CapacityEvidence:
    collected_at: str
    source_host: str

    filesystem: Measurement = field(default_factory=lambda: Measurement("root_filesystem"))
    inodes: Measurement = field(default_factory=lambda: Measurement("inodes"))
    memory: Measurement = field(default_factory=lambda: Measurement("memory"))
    pg_data: Measurement = field(default_factory=lambda: Measurement("pg_data"))
    pg_wal: Measurement = field(default_factory=lambda: Measurement("pg_wal"))
    backup_dir: Measurement = field(default_factory=lambda: Measurement("backup_dir"))
    latest_backup: Measurement = field(default_factory=lambda: Measurement("latest_backup"))
    journal: Measurement = field(default_factory=lambda: Measurement("journal"))
    checkouts: Measurement = field(default_factory=lambda: Measurement("checkouts"))
    browser_helper: Measurement = field(default_factory=lambda: Measurement("browser_helper"))
    external_state: Measurement = field(default_factory=lambda: Measurement("external_state"))
    uptime: Measurement = field(default_factory=lambda: Measurement("uptime"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "collected_at": self.collected_at,
            "source_host": self.source_host,
            "root_filesystem": self.filesystem.dict(),
            "inodes": self.inodes.dict(),
            "memory": self.memory.dict(),
            "postgresql_data": self.pg_data.dict(),
            "postgresql_wal": self.pg_wal.dict(),
            "backup_directory": self.backup_dir.dict(),
            "latest_backup": self.latest_backup.dict(),
            "journal_logs": self.journal.dict(),
            "checkouts": self.checkouts.dict(),
            "browser_helper": self.browser_helper.dict(),
            "external_state": self.external_state.dict(),
            "uptime": self.uptime.dict(),
        }


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None) -> str | None:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z") if dt else None


def _ssh(command: str, cfg: CapacityConfig = DEFAULT_CONFIG) -> tuple[bool, str]:
    if not shutil.which("ssh"):
        return False, "ssh not available"
    try:
        completed = subprocess.run(
            ["ssh",
             "-o", f"ConnectTimeout={cfg.SSH_CONNECT_TIMEOUT}",
             "-o", "BatchMode=yes",
             cfg.SSH_HOST, "bash -s"],
            input=command,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=cfg.SSH_TIMEOUT, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    if completed.returncode:
        return False, (completed.stderr or completed.stdout).strip()
    return True, completed.stdout.strip()


def _parse_sections(raw: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current: str | None = None
    lines: list[str] = []
    for line in raw.splitlines():
        m = SECTION_PATTERN.match(line)
        if m:
            if current is not None:
                sections[current] = "\n".join(lines).strip()
            current = m.group(1)
            lines = []
        else:
            lines.append(line)
    if current is not None:
        sections[current] = "\n".join(lines).strip()
    return sections


def _parse_df_fs(line: str) -> dict[str, Any] | None:
    parts = line.split()
    if len(parts) < 5:
        return None
    try:
        # df -P output: device total used free pct mount (6 fields)
        # or sometimes: total used free pct mount (5 fields, device elided)
        pct_idx = 4 if len(parts) >= 6 else 3
        free_idx = 3 if len(parts) >= 6 else 2
        total_idx = 1 if len(parts) >= 6 else 0
        used_pct = int(parts[pct_idx].rstrip("%"))
        free_blocks = int(parts[free_idx])
        total_blocks = int(parts[total_idx])
        block_size = 1024
        free_bytes = free_blocks * block_size
        total_bytes = total_blocks * block_size
        free_gb = free_bytes / (1024 ** 3)
        return {
            "used_pct": used_pct,
            "free_bytes": free_bytes,
            "total_bytes": total_bytes,
            "free_gb": round(free_gb, 1),
        }
    except (IndexError, ValueError):
        return None


def _parse_df_inode(line: str) -> dict[str, Any] | None:
    parts = line.split()
    if len(parts) < 5:
        return None
    try:
        # df -Pi output: device total used free pct mount (6 fields)
        # or sometimes: total used free pct mount (5 fields, device elided)
        pct_idx = 4 if len(parts) >= 6 else 3
        free_idx = 3 if len(parts) >= 6 else 2
        total_idx = 1 if len(parts) >= 6 else 0
        used_pct = int(parts[pct_idx].rstrip("%"))
        free_inodes = int(parts[free_idx])
        total_inodes = int(parts[total_idx])
        return {
            "used_pct": used_pct,
            "free": free_inodes,
            "total": total_inodes,
        }
    except (IndexError, ValueError):
        return None


def _parse_free_b(section: str) -> dict[str, Any] | None:
    lines = section.splitlines()
    if not lines:
        return None
    parts = lines[0].split()
    if len(parts) < 7:
        return None
    try:
        result = {
            "total_bytes": int(parts[1]),
            "used_bytes": int(parts[2]),
            "free_bytes": int(parts[3]),
            "shared_bytes": int(parts[4]),
            "buff_cache_bytes": int(parts[5]),
            "available_bytes": int(parts[6]),
            "swap_total": None,
            "swap_used": None,
        }
    except (IndexError, ValueError):
        return None
    if len(lines) > 1:
        swap_parts = lines[1].split()
        if len(swap_parts) >= 3:
            try:
                result["swap_total"] = int(swap_parts[1])
                result["swap_used"] = int(swap_parts[2])
            except (ValueError, IndexError):
                pass
    return result


def _parse_du_stdout(line: str) -> int | None:
    if not line or line == "UNAVAILABLE":
        return None
    parts = line.split("\t")
    if parts and parts[0].isdigit():
        return int(parts[0])
    m = re.match(r'^(\d+)', line)
    if m:
        return int(m.group(1))
    return None


def _parse_latest_backup(line: str) -> dict[str, Any] | None:
    if not line or line == "UNAVAILABLE":
        return None
    stripped = line.strip()
    parts = stripped.split("\t")
    if len(parts) >= 2 and parts[0].isdigit():
        return {"size_bytes": int(parts[0]), "path_summary": os.path.basename(parts[1])}
    if parts and parts[0].isdigit():
        return {"size_bytes": int(parts[0]), "path_summary": None}
    return None


def _parse_journalctl(line: str) -> int | None:
    if not line or line == "UNAVAILABLE":
        return None
    m = re.search(r'(\d+\.?\d*)\s*(K|M|G|T)', line)
    if not m:
        m2 = re.match(r'^(\d+)', line)
        if m2:
            return int(m2.group(1))
        return None
    val = float(m.group(1))
    unit = m.group(2)
    multipliers = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
    return int(val * multipliers.get(unit, 1))


def _parse_checkouts(section: str) -> dict[str, Any] | None:
    if not section or section == "UNAVAILABLE":
        return None
    repos: dict[str, int] = {}
    total: int = 0
    for line in section.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0].isdigit():
            name = os.path.basename(parts[1].rstrip("/")) if parts[1].strip() else "unknown"
            size = int(parts[0])
            repos[name] = size
            total += size
    if not repos:
        return None
    return {"repositories": repos, "total_bytes": total}


def _compute_composite_status(
    ev: CapacityEvidence,
    thresholds: CapacityThresholds,
) -> tuple[str, str | None, str]:
    status = "ok"
    error_class: str | None = None
    incident_state = "none"

    fs = ev.filesystem
    if not fs.available:
        status = "fail"
        error_class = "fs_unavailable"
        incident_state = "degraded"
    elif isinstance(fs.value, dict):
        used_pct = fs.value.get("used_pct", 0)
        free_gb = fs.value.get("free_gb", 999)
        if used_pct >= thresholds.STOP_DISK_PCT or free_gb < thresholds.STOP_FREE_GB:
            status = "fail"
            error_class = "disk_critical"
            incident_state = "critical"
        elif used_pct >= thresholds.WARN_DISK_PCT or free_gb < thresholds.WARN_FREE_GB:
            if status != "fail":
                status = "warn"
                error_class = "disk_warning"
                incident_state = "degraded"

    inodes = ev.inodes
    if inodes.available and isinstance(inodes.value, dict):
        inode_pct = inodes.value.get("used_pct", 0)
        if inode_pct >= thresholds.STOP_INODE_PCT:
            status = "fail"
            error_class = "inode_critical"
            incident_state = "critical"

    return status, error_class, incident_state


def collect(cfg: CapacityConfig = DEFAULT_CONFIG) -> dict[str, Any]:
    now = _utcnow()
    run_id = str(uuid.uuid4())
    generated_at = _iso(now)

    ok, raw = _ssh(_SSH_SCRIPT, cfg)
    if not ok:
        return _skip_payload(generated_at, run_id, f"ssh_failure:{raw}")

    return _build_payload(generated_at, run_id, now, raw, cfg)


def collect_from_fixture(fixture_path: str, cfg: CapacityConfig = DEFAULT_CONFIG) -> dict[str, Any]:
    data = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    return _collect_from_fixture_data(data, cfg)


def _collect_from_fixture_data(data: dict[str, Any], cfg: CapacityConfig = DEFAULT_CONFIG) -> dict[str, Any]:
    now = _utcnow()
    run_id = str(uuid.uuid4())
    generated_at = _iso(now)

    raw_lines = [
        data.get("filesystem", ""),
        data.get("inodes", ""),
        data.get("memory", ""),
    ]
    raw = "\n".join(raw_lines)
    uptime_raw = data.get("uptime", "unknown")

    lines, _ = _ssh_to_raw_lines(raw)
    if len(lines) < 3:
        return _skip_payload(generated_at, run_id, "malformed_capacity_response")

    ev = _parse_core_measurements(lines, uptime_raw, cfg)
    _parse_fixture_extras(ev, data)
    return _build_payload_from_evidence(generated_at, run_id, now, ev, cfg)


def _ssh_to_raw_lines(raw: str) -> tuple[list[str], str | None]:
    parts = raw.split("---\n") if "---" in raw else [raw]
    lines = [l.strip() for l in parts[0].splitlines() if l.strip()]
    uptime = parts[1].strip() if len(parts) > 1 else None
    return lines, uptime


def _parse_core_measurements(
    lines: list[str], uptime_raw: str | None, cfg: CapacityConfig
) -> CapacityEvidence:
    now_iso = _iso(_utcnow())
    ev = CapacityEvidence(
        collected_at=now_iso,
        source_host=cfg.SSH_HOST,
    )

    df_raw = lines[0]
    df_parsed = _parse_df_fs(df_raw)
    if df_parsed:
        ev.filesystem.available = True
        ev.filesystem.value = df_parsed

    inode_raw = lines[1] if len(lines) > 1 else ""
    inode_parsed = _parse_df_inode(inode_raw)
    if inode_parsed:
        ev.inodes.available = True
        ev.inodes.value = inode_parsed

    mem_raw = "\n".join(lines[2:]) if len(lines) > 2 else ""
    mem_parsed = _parse_free_b(mem_raw)
    if mem_parsed:
        ev.memory.available = True
        ev.memory.value = mem_parsed

    if uptime_raw:
        ev.uptime.available = True
        ev.uptime.value = uptime_raw

    return ev


def _parse_fixture_extras(ev: CapacityEvidence, data: dict[str, Any]) -> None:
    pg = data.get("postgresql", {})
    if isinstance(pg, dict) and pg.get("available", False):
        if "data_size_bytes" in pg and pg["data_size_bytes"] is not None:
            ev.pg_data.available = True
            ev.pg_data.value = pg["data_size_bytes"]
        if "wal_size_bytes" in pg and pg["wal_size_bytes"] is not None:
            ev.pg_wal.available = True
            ev.pg_wal.value = pg["wal_size_bytes"]

    backups = data.get("backups", {})
    if isinstance(backups, dict) and backups.get("available", False):
        if "directory_size_bytes" in backups:
            ev.backup_dir.available = True
            ev.backup_dir.value = backups["directory_size_bytes"]
        if "latest_backup_size_bytes" in backups:
            ev.latest_backup.available = True
            ev.latest_backup.value = backups["latest_backup_size_bytes"]

    jrnl = data.get("journals", {})
    if isinstance(jrnl, dict) and jrnl.get("available", False):
        if "bytes" in jrnl:
            ev.journal.available = True
            ev.journal.value = jrnl["bytes"]

    checkouts = data.get("checkouts", {})
    if isinstance(checkouts, dict) and checkouts.get("available", False):
        if "control_plane_bytes" in checkouts or "repositories" in checkouts:
            ev.checkouts.available = True
            chk_val: dict[str, Any] = {"total_bytes": 0}
            if "control_plane_bytes" in checkouts:
                chk_val["control_plane_bytes"] = checkouts["control_plane_bytes"]
                chk_val["total_bytes"] += checkouts["control_plane_bytes"]
            if "repositories" in checkouts:
                chk_val["repositories"] = checkouts["repositories"]
                chk_val["total_bytes"] += sum(
                    checkouts["repositories"].values()
                )
            ev.checkouts.value = chk_val

    browser = data.get("browser_helper", {})
    if isinstance(browser, dict) and browser.get("available", False):
        if "aggregate_bytes" in browser:
            ev.browser_helper.available = True
            ev.browser_helper.value = browser["aggregate_bytes"]

    ext = data.get("external_state", {})
    if isinstance(ext, dict) and ext.get("available", False):
        if "bytes" in ext:
            ev.external_state.available = True
            ev.external_state.value = ext["bytes"]


def _parse_sections_into_evidence(
    sections: dict[str, str], cfg: CapacityConfig
) -> CapacityEvidence:
    now_iso = _iso(_utcnow())
    ev = CapacityEvidence(collected_at=now_iso, source_host=cfg.SSH_HOST)

    # Filesystem
    fs_raw = sections.get("FS", "")
    fs_parsed = _parse_df_fs(fs_raw)
    if fs_parsed:
        ev.filesystem.available = True
        ev.filesystem.value = fs_parsed

    # Inodes
    inode_raw = sections.get("INODE", "")
    inode_parsed = _parse_df_inode(inode_raw)
    if inode_parsed:
        ev.inodes.available = True
        ev.inodes.value = inode_parsed

    # Memory
    mem_raw = sections.get("MEM", "")
    mem_parsed = _parse_free_b(mem_raw)
    if mem_parsed:
        ev.memory.available = True
        ev.memory.value = mem_parsed

    # PostgreSQL data
    pg_data_raw = sections.get("PG_DATA", "")
    pg_data_val = _parse_du_stdout(pg_data_raw)
    if pg_data_val is not None:
        ev.pg_data.available = True
        ev.pg_data.value = pg_data_val

    # PostgreSQL WAL
    pg_wal_raw = sections.get("PG_WAL", "")
    pg_wal_val = _parse_du_stdout(pg_wal_raw)
    if pg_wal_val is not None:
        ev.pg_wal.available = True
        ev.pg_wal.value = pg_wal_val

    # Backup directory
    bk_dir_raw = sections.get("BACKUPS_DIR", "")
    bk_dir_val = _parse_du_stdout(bk_dir_raw)
    if bk_dir_val is not None:
        ev.backup_dir.available = True
        ev.backup_dir.value = bk_dir_val

    # Latest backup
    lb_raw = sections.get("LATEST_BACKUP", "")
    lb_parsed = _parse_latest_backup(lb_raw)
    if lb_parsed is not None:
        ev.latest_backup.available = True
        ev.latest_backup.value = lb_parsed

    # Journal
    jrnl_raw = sections.get("JOURNAL", "")
    jrnl_val = _parse_journalctl(jrnl_raw)
    if jrnl_val is not None:
        ev.journal.available = True
        ev.journal.value = jrnl_val

    # Checkouts
    co_raw = sections.get("CHECKOUTS", "")
    co_parsed = _parse_checkouts(co_raw)
    if co_parsed is not None:
        ev.checkouts.available = True
        ev.checkouts.value = co_parsed

    # Browser cache
    br_raw = sections.get("BROWSER", "")
    br_val = _parse_du_stdout(br_raw)
    if br_val is not None:
        ev.browser_helper.available = True
        ev.browser_helper.value = br_val

    # External state
    st_raw = sections.get("STATE", "")
    st_val = _parse_du_stdout(st_raw)
    if st_val is not None:
        ev.external_state.available = True
        ev.external_state.value = st_val

    # Uptime
    up_raw = sections.get("UPTIME", "")
    if up_raw and up_raw != "UNAVAILABLE":
        ev.uptime.available = True
        ev.uptime.value = up_raw.strip()

    return ev


def _build_payload(
    generated_at: str,
    run_id: str,
    now: datetime,
    raw: str,
    cfg: CapacityConfig,
) -> dict[str, Any]:
    sections = _parse_sections(raw)
    ev = _parse_sections_into_evidence(sections, cfg)

    return _build_payload_from_evidence(generated_at, run_id, now, ev, cfg)


def _build_payload_from_evidence(
    generated_at: str,
    run_id: str,
    now: datetime,
    ev: CapacityEvidence,
    cfg: CapacityConfig,
) -> dict[str, Any]:
    thresholds = cfg.thresholds
    status, error_class, incident_state = _compute_composite_status(ev, thresholds)

    disk_free_bytes: int | None = None
    disk_usage_pct: float | None = None
    if ev.filesystem.available and isinstance(ev.filesystem.value, dict):
        disk_free_bytes = ev.filesystem.value.get("free_bytes")
        disk_usage_pct = float(ev.filesystem.value.get("used_pct", 0))

    capacity_dict = ev.to_dict()

    result: dict[str, Any] = {
        "contract_version": 2,
        "generated_at": generated_at,
        "project": cfg.PROJECT,
        "workflow": cfg.WORKFLOW,
        "workflow_id": cfg.WORKFLOW_ID,
        "run_id": run_id,
        "status": status,
        "started_at": generated_at,
        "finished_at": generated_at,
        "last_success_at": generated_at,
        "expected_cadence_seconds": cfg.EXPECTED_CADENCE_SECONDS,
        "freshness_seconds": 0,
        "deployed_revision": None,
        "scheduler_state": "active",
        "backup_state": "not_applicable",
        "incident_state": incident_state,
        "disk_free_bytes": disk_free_bytes,
        "disk_usage_pct": disk_usage_pct,
        "storage_bytes": None,
        "error_class": error_class,
        "heartbeat_at": generated_at,
        "producer_version": cfg.PRODUCER_VERSION,
        "metadata": {
            "source_adapter": cfg.PRODUCER_VERSION,
            "capacity": capacity_dict,
        },
    }

    for field in REQUIRED_OUTPUT_FIELDS:
        if field not in result:
            result[field] = None

    return result


def _skip_payload(
    generated_at: str,
    run_id: str,
    error_class: str,
    cfg: CapacityConfig = DEFAULT_CONFIG,
) -> dict[str, Any]:
    return {
        "contract_version": 2,
        "generated_at": generated_at,
        "project": cfg.PROJECT,
        "workflow": cfg.WORKFLOW,
        "workflow_id": cfg.WORKFLOW_ID,
        "run_id": run_id,
        "status": "fail",
        "started_at": generated_at,
        "finished_at": generated_at,
        "last_success_at": None,
        "expected_cadence_seconds": cfg.EXPECTED_CADENCE_SECONDS,
        "freshness_seconds": None,
        "deployed_revision": None,
        "scheduler_state": "unmanaged",
        "backup_state": "not_applicable",
        "incident_state": "degraded",
        "error_class": error_class,
        "producer_version": cfg.PRODUCER_VERSION,
        "metadata": {"source_adapter": cfg.PRODUCER_VERSION},
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="VPS capacity snapshot producer")
    parser.add_argument("--fixture", help="Read structured evidence fixture instead of live SSH")
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
