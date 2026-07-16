"""Shared fixture paths and payloads for producer tests.

Path references to all JSON fixture files for capacity and recovery evidence.
"""

from __future__ import annotations

from pathlib import Path


FIXTURES_DIR = Path(__file__).resolve().parent

# Legacy backward-compatible fixtures (updated to free -b format)
CAPACITY_OK_FIXTURE = FIXTURES_DIR / "vps_capacity.json"
CAPACITY_WARN_FIXTURE = FIXTURES_DIR / "vps_capacity_warning.json"
CAPACITY_CRITICAL_FIXTURE = FIXTURES_DIR / "vps_capacity_critical.json"

# New structured capacity fixtures
CAPACITY_HEALTHY_FIXTURE = FIXTURES_DIR / "vps_capacity_healthy.json"
CAPACITY_WARNING_CLOSE_FIXTURE = FIXTURES_DIR / "vps_capacity_warning_close.json"
CAPACITY_STOP_FIXTURE = FIXTURES_DIR / "vps_capacity_stop.json"
CAPACITY_STOP_INODES_FIXTURE = FIXTURES_DIR / "vps_capacity_stop_inodes.json"
CAPACITY_MISSING_WAL_FIXTURE = FIXTURES_DIR / "vps_capacity_missing_wal.json"
CAPACITY_MISSING_PG_FIXTURE = FIXTURES_DIR / "vps_capacity_missing_pg.json"
CAPACITY_MALFORMED_FIXTURE = FIXTURES_DIR / "vps_capacity_malformed.json"
CAPACITY_PARTIAL_FIXTURE = FIXTURES_DIR / "vps_capacity_partial.json"
CAPACITY_OVERFLOW_FIXTURE = FIXTURES_DIR / "vps_capacity_overflow.json"

# Other producers
REDDIT_BACKUP_FAILED_FIXTURE = FIXTURES_DIR / "reddit_backup.json"
TRADERIE_FAILED_FIXTURE = FIXTURES_DIR / "traderie_export.json"
CONTROL_PLANE_REVISION_FIXTURE = FIXTURES_DIR / "control_plane_revision.json"

# Registry of all capacity fixtures by expected status
CAPACITY_FIXTURES_BY_STATUS = {
    "ok": [CAPACITY_OK_FIXTURE, CAPACITY_HEALTHY_FIXTURE],
    "warn": [CAPACITY_WARN_FIXTURE, CAPACITY_WARNING_CLOSE_FIXTURE],
    "fail": [
        CAPACITY_CRITICAL_FIXTURE, CAPACITY_STOP_FIXTURE,
        CAPACITY_STOP_INODES_FIXTURE,
    ],
}
