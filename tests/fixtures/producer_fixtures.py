"""Shared fixture paths and payloads for producer tests.

These define paths to the JSON fixture files and also provide inline
fixture dicts for direct use in test assertions.
"""

from __future__ import annotations

from pathlib import Path


FIXTURES_DIR = Path(__file__).resolve().parent

CAPACITY_OK_FIXTURE = FIXTURES_DIR / "vps_capacity.json"
CAPACITY_WARN_FIXTURE = FIXTURES_DIR / "vps_capacity_warning.json"
CAPACITY_CRITICAL_FIXTURE = FIXTURES_DIR / "vps_capacity_critical.json"

REDDIT_BACKUP_FAILED_FIXTURE = FIXTURES_DIR / "reddit_backup.json"
TRADERIE_FAILED_FIXTURE = FIXTURES_DIR / "traderie_export.json"
CONTROL_PLANE_REVISION_FIXTURE = FIXTURES_DIR / "control_plane_revision.json"
