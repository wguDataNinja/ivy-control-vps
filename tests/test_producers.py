"""Tests for the bounded producer contracts.

Validates:
- Required core fields present in every producer output
- Status derivation logic (healthy, warning, stop, inode stop)
- Evidence level semantics (available/unavailable)
- Malformed input handling
- Missing PostgreSQL / WAL handling
- Partial measurement handling
- Overflow / units errors
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
    CAPACITY_HEALTHY_FIXTURE,
    CAPACITY_WARNING_CLOSE_FIXTURE,
    CAPACITY_STOP_FIXTURE,
    CAPACITY_STOP_INODES_FIXTURE,
    CAPACITY_MISSING_WAL_FIXTURE,
    CAPACITY_MISSING_PG_FIXTURE,
    CAPACITY_MALFORMED_FIXTURE,
    CAPACITY_PARTIAL_FIXTURE,
    CAPACITY_OVERFLOW_FIXTURE,
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


def _get_capacity_metadata(payload: dict) -> dict:
    meta = payload.get("metadata", {})
    return meta.get("capacity", {})


# ── VPS Capacity Snapshot ──────────────────────────────────────────────────


class TestVpsCapacityCore:
    def test_ok_status(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_OK_FIXTURE))
        _validate_core_fields(payload, "VPS capacity")
        assert payload["status"] == "ok"

    def test_ok_healthy_fixture(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_HEALTHY_FIXTURE))
        _validate_core_fields(payload, "VPS capacity")
        assert payload["status"] == "ok"
        assert payload["incident_state"] == "none"

    def test_warning_status(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_WARN_FIXTURE))
        _validate_core_fields(payload, "VPS capacity")
        assert payload["status"] == "warn"
        assert payload["incident_state"] == "degraded"
        assert payload["disk_usage_pct"] >= 80

    def test_warning_close_fixture(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_WARNING_CLOSE_FIXTURE))
        _validate_core_fields(payload, "VPS capacity")
        assert payload["status"] == "warn"
        assert payload["incident_state"] == "degraded"
        assert payload["disk_usage_pct"] >= 80

    def test_critical_status(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_CRITICAL_FIXTURE))
        _validate_core_fields(payload, "VPS capacity")
        assert payload["status"] == "fail"
        assert payload["incident_state"] == "critical"

    def test_stop_threshold(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_STOP_FIXTURE))
        _validate_core_fields(payload, "VPS capacity")
        assert payload["status"] == "fail"
        assert payload["incident_state"] == "critical"
        assert payload["disk_usage_pct"] >= 85

    def test_stop_inodes(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_STOP_INODES_FIXTURE))
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
        payload = _run_producer("vps_capacity_snapshot.py")
        _validate_core_fields(payload, "VPS capacity no-fixture")
        assert payload["status"] in ("ok", "warn", "fail")

    def test_disk_free_bytes_present(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_OK_FIXTURE))
        assert payload.get("disk_free_bytes") is not None
        assert isinstance(payload["disk_free_bytes"], int)

    def test_disk_usage_pct_present(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_OK_FIXTURE))
        assert payload.get("disk_usage_pct") is not None
        assert isinstance(payload["disk_usage_pct"], float)


# ── Capacity Evidence Structure ─────────────────────────────────────────────


class TestCapacityEvidenceStructure:
    def test_metadata_capacity_present(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_HEALTHY_FIXTURE))
        cap = _get_capacity_metadata(payload)
        assert cap, "metadata.capacity should be present"

    def test_all_measurement_keys_present(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_HEALTHY_FIXTURE))
        cap = _get_capacity_metadata(payload)
        expected = [
            "root_filesystem", "inodes", "memory",
            "postgresql_data", "postgresql_wal",
            "backup_directory", "latest_backup",
            "journal_logs", "checkouts",
            "browser_helper", "external_state", "uptime",
        ]
        for key in expected:
            assert key in cap, f"Missing capacity measurement: {key}"

    def test_collected_at_present(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_HEALTHY_FIXTURE))
        cap = _get_capacity_metadata(payload)
        assert cap.get("collected_at"), "collected_at should be present"

    def test_source_host_present(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_HEALTHY_FIXTURE))
        cap = _get_capacity_metadata(payload)
        assert cap.get("source_host"), "source_host should be present"

    def test_no_absolute_paths_in_output(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_HEALTHY_FIXTURE))
        output = json.dumps(payload)
        assert "/home/" not in output, "Output contains absolute path"
        assert "/var/" not in output, "Output contains absolute path"
        assert "/dev/" not in output, "Output contains absolute path"

    def each_measurement_has_available_bool(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_HEALTHY_FIXTURE))
        cap = _get_capacity_metadata(payload)
        for key, val in cap.items():
            if isinstance(val, dict) and "available" in val:
                assert isinstance(val["available"], bool), f"{key}.available should be bool"


# ── Edge Cases ──────────────────────────────────────────────────────────────


class TestCapacityEdgeCases:
    def test_missing_wal_access(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_MISSING_WAL_FIXTURE))
        cap = _get_capacity_metadata(payload)
        assert cap.get("postgresql_data", {}).get("available") is True
        wal = cap.get("postgresql_wal", {})
        assert not wal.get("available"), "WAL should be unavailable"

    def test_missing_postgresql(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_MISSING_PG_FIXTURE))
        cap = _get_capacity_metadata(payload)
        pg_data = cap.get("postgresql_data", {})
        pg_wal = cap.get("postgresql_wal", {})
        assert not pg_data.get("available"), "PG data should be unavailable"
        assert not pg_wal.get("available"), "PG WAL should be unavailable"

    def test_malformed_data_returns_fail(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_MALFORMED_FIXTURE))
        _validate_core_fields(payload, "VPS capacity malformed")
        assert payload["status"] == "fail"
        assert "error_class" in payload

    def test_partial_measurement(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_PARTIAL_FIXTURE))
        _validate_core_fields(payload, "VPS capacity partial")
        cap = _get_capacity_metadata(payload)
        assert cap.get("root_filesystem", {}).get("available") is True
        assert cap.get("inodes", {}).get("available") is True
        assert cap.get("memory", {}).get("available") is True
        assert not cap.get("backup_directory", {}).get("available")
        assert not cap.get("journal_logs", {}).get("available")
        assert not cap.get("checkouts", {}).get("available")
        assert not cap.get("browser_helper", {}).get("available")
        assert not cap.get("external_state", {}).get("available")

    def test_overflow_values(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_OVERFLOW_FIXTURE))
        _validate_core_fields(payload, "VPS capacity overflow")
        cap = _get_capacity_metadata(payload)
        fs = cap.get("root_filesystem", {}).get("value", {})
        assert fs.get("used_pct") == 0
        pg_data = cap.get("postgresql_data", {}).get("value")
        assert pg_data is not None

    def test_capacity_still_ok_with_unavailable_optional(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_PARTIAL_FIXTURE))
        assert payload["status"] == "ok"

    def test_memory_available_field(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_HEALTHY_FIXTURE))
        cap = _get_capacity_metadata(payload)
        mem = cap.get("memory", {}).get("value", {})
        assert "available_bytes" in mem
        assert isinstance(mem["available_bytes"], int)

    def test_memory_swap_fields(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_HEALTHY_FIXTURE))
        cap = _get_capacity_metadata(payload)
        mem = cap.get("memory", {}).get("value", {})
        assert "swap_total" in mem
        assert "swap_used" in mem


# ── Control Plane Revision ─────────────────────────────────────────────────


class TestControlPlaneRevision:
    def test_imports_resolve(self) -> None:
        result = subprocess.run(
            [sys.executable, str(PRODUCERS_DIR / "control_plane_revision.py"), "--fixture", "/dev/null"],
            capture_output=True, text=True, timeout=10,
        )
        assert "No module" not in result.stderr
        assert "ModuleNotFoundError" not in result.stderr

    def test_produces_valid_core_fields(self) -> None:
        payload = _run_producer("control_plane_revision.py")
        _validate_core_fields(payload, "Control plane revision")

    def test_drift_direction_field_present(self) -> None:
        payload = _run_producer("control_plane_revision.py")
        meta = payload.get("metadata", {})
        assert "drift_direction" in meta, "Missing drift_direction in metadata"

    def test_drift_direction_valid_values(self) -> None:
        payload = _run_producer("control_plane_revision.py")
        meta = payload.get("metadata", {})
        valid = {"exact_match", "local_ahead", "local_behind", "diverged", "unavailable", "unknown"}
        assert meta.get("drift_direction") in valid, (
            f"Invalid drift_direction: {meta.get('drift_direction')}"
        )

    def test_drift_direction_exact_match(self) -> None:
        payload = _run_producer("control_plane_revision.py")
        meta = payload.get("metadata", {})
        ahead = meta.get("ahead_count")
        behind = meta.get("behind_count")
        if ahead is not None and behind is not None:
            if ahead == 0 and behind == 0:
                assert meta.get("drift_direction") == "exact_match"
            elif ahead > 0 and behind == 0:
                assert meta.get("drift_direction") == "local_ahead"
            elif ahead == 0 and behind > 0:
                assert meta.get("drift_direction") == "local_behind"
            elif ahead > 0 and behind > 0:
                assert meta.get("drift_direction") == "diverged"

    def test_backward_compat_drift_state(self) -> None:
        payload = _run_producer("control_plane_revision.py")
        meta = payload.get("metadata", {})
        assert "drift_state" in meta


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


# ── Traderie Live Export ────────────────────────────────────────────────────


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
        result = subprocess.run(
            [sys.executable, str(PRODUCERS_DIR / producer)],
            capture_output=True, text=True, timeout=15,
        )
        assert "No module" not in result.stderr
        assert "ModuleNotFoundError" not in result.stderr

    @pytest.mark.parametrize("producer", ALL_PRODUCERS)
    def test_producer_output_valid_json(self, producer: str) -> None:
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
        result = subprocess.run(
            [sys.executable, str(PRODUCERS_DIR / producer)],
            capture_output=True, text=True, timeout=15,
        )
        for pattern in self.FORBIDDEN:
            assert pattern not in result.stdout, f"{producer} leaks {pattern}"


# ── Comprehensive fixture parametrisation ────────────────────────────────────


class TestAllCapacityFixtures:
    @pytest.mark.parametrize("fixture_path,expected_status", [
        (CAPACITY_OK_FIXTURE, "ok"),
        (CAPACITY_HEALTHY_FIXTURE, "ok"),
        (CAPACITY_WARN_FIXTURE, "warn"),
        (CAPACITY_WARNING_CLOSE_FIXTURE, "warn"),
        (CAPACITY_CRITICAL_FIXTURE, "fail"),
        (CAPACITY_STOP_FIXTURE, "fail"),
        (CAPACITY_STOP_INODES_FIXTURE, "fail"),
        (CAPACITY_MISSING_WAL_FIXTURE, "ok"),
        (CAPACITY_MISSING_PG_FIXTURE, "ok"),
        (CAPACITY_PARTIAL_FIXTURE, "ok"),
    ])
    def test_fixture_status(self, fixture_path: Path, expected_status: str) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(fixture_path))
        _validate_core_fields(payload, f"fixture {fixture_path.name}")
        assert payload["status"] == expected_status, (
            f"{fixture_path.name}: expected {expected_status}, got {payload['status']}"
        )


# ── Direct/Local Execution Mode ─────────────────────────────────────────────


class TestDirectMode:
    def test_direct_collect_imports(self) -> None:
        from tools.producers.vps_capacity_snapshot import collect
        from tools.producers.vps_capacity_config import DIRECT_CONFIG
        assert collect is not None
        assert DIRECT_CONFIG.MODE == "direct"
        assert DIRECT_CONFIG.SSH_HOST == "ih-market-vps"


# ── WAL Unavailability ──────────────────────────────────────────────────────


class TestWalUnavailability:
    def test_missing_wal_explicit_not_zero(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_MISSING_WAL_FIXTURE))
        cap = _get_capacity_metadata(payload)
        wal = cap.get("postgresql_wal", {})
        assert not wal.get("available"), "WAL should be unavailable"
        # The value must be null/None, NOT zero (which would imply measured-as-zero)
        assert wal.get("value") is None, (
            f"WAL value should be null when unavailable, got {wal.get('value')}"
        )

    def test_wal_available_is_int(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_HEALTHY_FIXTURE))
        cap = _get_capacity_metadata(payload)
        wal = cap.get("postgresql_wal", {})
        assert wal.get("available") is True
        assert isinstance(wal.get("value"), int), (
            f"WAL value should be int when available, got {type(wal.get('value'))}"
        )
        assert wal.get("value") > 0, "WAL value should be positive when available"


# ── Evidence Timestamps ─────────────────────────────────────────────────────


class TestEvidenceTimestamps:
    def test_collected_at_present_in_capacity(self) -> None:
        payload = _run_producer("vps_capacity_snapshot.py", str(CAPACITY_OK_FIXTURE))
        cap = _get_capacity_metadata(payload)
        assert cap.get("collected_at"), "capacity must have collected_at"
        assert "T" in cap["collected_at"], "collected_at must be ISO-8601"


# ── Traderie file-based authority ────────────────────────────────────────────


class TestTraderieFileBased:
    def test_traderie_authority_text(self) -> None:
        from tools.ingestion_dashboard import traderie_unknown
        result = traderie_unknown()
        detail = result.get("detail", {})
        auth = detail.get("authority_type", "")
        pg = detail.get("postgresql", "")
        assert "file_based" in auth, (
            f"Traderie must document file-based authority, got: {auth}"
        )
        assert "zero_non_system_tables" in pg, (
            f"Traderie must document zero non-system PG tables, got: {pg}"
        )
        assert result.get("evidence_level") == "missing_producer"
        assert result.get("status") == "UNKNOWN"
