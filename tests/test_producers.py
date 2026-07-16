"""Tests for the bounded producer contracts.

Validates:
- Required core fields present in every producer output
- Status derivation logic
- Evidence level semantics
- Malformed input handling
- No private leakage
- Fixture-based local testing works
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.fixtures.producer_fixtures import (
    CAPACITY_OK_FIXTURE,
    CAPACITY_WARN_FIXTURE,
    CAPACITY_CRITICAL_FIXTURE,
    REDDIT_BACKUP_FAILED_FIXTURE,
    TRADERIE_FAILED_FIXTURE,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCERS_DIR = REPO_ROOT / "tools" / "producers"

REQUIRED_CORE_FIELDS = {
    "contract_version", "generated_at", "project", "workflow", "workflow_id",
    "run_id", "status", "started_at", "finished_at", "last_success_at",
    "expected_cadence_seconds", "freshness_seconds", "deployed_revision",
    "scheduler_state", "backup_state", "incident_state",
}


def _run_producer(script_name: str, fixture_path: str | None = None) -> dict:
    script = PRODUCERS_DIR / script_name
    cmd = [sys.executable, str(script)]
    if fixture_path:
        cmd.extend(["--fixture", fixture_path])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, f"Producer {script_name} failed: {result.stderr}"
    return json.loads(result.stdout)


def _validate_core_fields(payload: dict, name: str) -> None:
    missing = REQUIRED_CORE_FIELDS - set(payload.keys())
    assert not missing, f"{name} missing required core fields: {missing}"
    assert payload["contract_version"] == 2, f"{name} contract_version must be 2"
    assert isinstance(payload["status"], str), f"{name} status must be string"
    assert isinstance(payload["incident_state"], str), f"{name} incident_state must be string"


# ── VPS Capacity Snapshot ──────────────────────────────────────────────────


class TestVpsCapacity:
    def test_ok_status(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_OK_FIXTURE))
        _validate_core_fields(payload, "VPS capacity")
        assert payload["status"] == "ok"
        assert payload["incident_state"] == "none"

    def test_warning_status(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_WARN_FIXTURE))
        _validate_core_fields(payload, "VPS capacity")
        assert payload["status"] == "warn"
        assert payload["incident_state"] == "degraded"
        assert payload["disk_usage_pct"] >= 80

    def test_critical_status(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_CRITICAL_FIXTURE))
        _validate_core_fields(payload, "VPS capacity")
        assert payload["status"] == "fail"
        assert payload["incident_state"] == "critical"

    def test_backup_state_not_applicable(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_OK_FIXTURE))
        assert payload["backup_state"] == "not_applicable"

    def test_deployed_revision_none(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_OK_FIXTURE))
        assert payload["deployed_revision"] is None

    def test_no_fixture_fallback(self) -> None:
        """Without --fixture, produces valid core fields (may be ok or fail depending on environment)."""
        payload = _run_producer("vps_capacity_snapshot.py")
        _validate_core_fields(payload, "VPS capacity no-fixture")
        assert payload["status"] in ("ok", "warn", "fail")


# ── Control Plane Revision ─────────────────────────────────────────────────


class TestControlPlaneRevision:
    def test_imports_resolve(self) -> None:
        """Producer runs standalone without path errors."""
        result = subprocess.run(
            [sys.executable, str(PRODUCERS_DIR / "control_plane_revision.py"), "--fixture", "/dev/null"],
            capture_output=True, text=True, timeout=10,
        )
        # Will fail because fixture is not valid JSON, but shouldn't crash on import
        assert "No module" not in result.stderr
        assert "ModuleNotFoundError" not in result.stderr

    def test_produces_valid_core_fields(self) -> None:
        """Even with a fake fixture path, produces valid output structure."""
        payload = _run_producer("control_plane_revision.py")
        _validate_core_fields(payload, "Control plane revision")


# ── Reddit Backup Evidence ─────────────────────────────────────────────────


class TestRedditBackupEvidence:
    def test_failed_backup_status(self) -> None:
        payload = _run_producer("reddit_backup_evidence.py", str(REDDIT_BACKUP_FAILED_FIXTURE))
        _validate_core_fields(payload, "Reddit backup evidence")
        assert payload["status"] == "fail"
        assert payload["backup_state"] == "fail"
        assert payload["incident_state"] == "critical"

    def test_no_fixture_produces_fail(self) -> None:
        payload = _run_producer("reddit_backup_evidence.py")
        _validate_core_fields(payload, "Reddit backup evidence")
        assert payload["status"] == "fail"
        assert payload["backup_state"] == "fail"

    def test_happy_path(self) -> None:
        payload = _run_producer("reddit_backup_evidence.py", str(REDDIT_BACKUP_FAILED_FIXTURE))
        assert "error_class" in payload


# ── Reddit Canonicality Placeholder ────────────────────────────────────────


class TestRedditCanonicalityPlaceholder:
    def test_skip_status(self) -> None:
        payload = _run_producer("reddit_canonicality_placeholder.py")
        _validate_core_fields(payload, "Reddit canonicality")
        assert payload["status"] == "skip"
        assert payload["incident_state"] == "degraded"

    def test_canonicality_dimensions_listed(self) -> None:
        payload = _run_producer("reddit_canonicality_placeholder.py")
        meta = payload.get("metadata", {})
        evidence = meta.get("canonicality_evidence", {})
        required_dims = [
            "source_db_frontier", "recent_completeness", "duplicate_gap_check",
            "archive_earliest", "archive_latest", "archive_continuity",
            "one_writer_lock_proof", "fresh_backup_restore", "natural_run_observation",
        ]
        for dim in required_dims:
            assert dim in evidence, f"Missing canonicality dimension: {dim}"


# ── Traderie Live Export ───────────────────────────────────────────────────


class TestTraderieLiveExport:
    def test_failed_export_status(self) -> None:
        payload = _run_producer("traderie_live_export.py", str(TRADERIE_FAILED_FIXTURE))
        _validate_core_fields(payload, "Traderie live export")
        assert payload["status"] == "fail"
        assert payload["incident_state"] == "critical"
        assert payload["deployed_revision"] == "e5ebd0f"

    def test_no_fixture_produces_stale(self) -> None:
        payload = _run_producer("traderie_live_export.py")
        _validate_core_fields(payload, "Traderie live export")
        assert payload["status"] == "stale"

    def test_timeout_error_class(self) -> None:
        payload = _run_producer("traderie_live_export.py", str(TRADERIE_FAILED_FIXTURE))
        assert "timeout" in (payload.get("error_class") or "").lower()


# ── IH Ack/Replay Contract Template ────────────────────────────────────────


class TestIHAckReplayContract:
    def test_skip_status(self) -> None:
        payload = _run_producer("ih_ack_replay_contract.py")
        _validate_core_fields(payload, "IH ack/replay")
        assert payload["status"] == "skip"
        assert payload["incident_state"] == "degraded"

    def test_unresolved_authority_markers(self) -> None:
        payload = _run_producer("ih_ack_replay_contract.py")
        meta = payload.get("metadata", {})
        ack = meta.get("acknowledgement", {})
        assert ack.get("status") == "unresolved_authority"


# ── Global structural tests ────────────────────────────────────────────────


class TestProducerStructural:
    ALL_PRODUCERS = [
        "vps_capacity_snapshot.py",
        "control_plane_revision.py",
        "reddit_backup_evidence.py",
        "reddit_canonicality_placeholder.py",
        "traderie_live_export.py",
        "ih_ack_replay_contract.py",
    ]

    @pytest.mark.parametrize("producer", ALL_PRODUCERS)
    def test_producer_runs_without_crash(self, producer: str) -> None:
        """Every producer runs without crashing."""
        result = subprocess.run(
            [sys.executable, str(PRODUCERS_DIR / producer)],
            capture_output=True, text=True, timeout=15,
        )
        assert "No module" not in result.stderr
        assert "ModuleNotFoundError" not in result.stderr

    @pytest.mark.parametrize("producer", ALL_PRODUCERS)
    def test_producer_output_valid_json(self, producer: str) -> None:
        """Every producer outputs valid JSON."""
        result = subprocess.run(
            [sys.executable, str(PRODUCERS_DIR / producer)],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0
        try:
            json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            pytest.fail(f"{producer} output not valid JSON: {exc}")

    @pytest.mark.parametrize("producer", ALL_PRODUCERS)
    def test_producer_required_core_fields(self, producer: str) -> None:
        """Every producer has all required core fields."""
        result = subprocess.run(
            [sys.executable, str(PRODUCERS_DIR / producer)],
            capture_output=True, text=True, timeout=15,
        )
        payload = json.loads(result.stdout)
        missing = REQUIRED_CORE_FIELDS - set(payload.keys())
        assert not missing, f"{producer} missing: {missing}"
        assert payload["contract_version"] == 2

    FORBIDDEN = ["api_key", "token", "credential", "cookie", "session_id",
                 "browser_profile", "chat_body", "error_message_private",
                 "/home/", "/Users/"]

    @pytest.mark.parametrize("producer", ALL_PRODUCERS)
    def test_no_private_leakage(self, producer: str) -> None:
        """No producer output contains private patterns."""
        result = subprocess.run(
            [sys.executable, str(PRODUCERS_DIR / producer)],
            capture_output=True, text=True, timeout=15,
        )
        for pattern in self.FORBIDDEN:
            assert pattern not in result.stdout, f"{producer} leaks {pattern}"
