"""Integration tests for ingestion_dashboard IH adapter integration.

Tests the adapt_chat / adapt_market functions which are called by
collect_ih() in the dashboard.  Covers:

1. Chat healthy, market unhealthy
2. Market healthy, chat unhealthy
3. Historical failures + current success
4. Stale data
5. Malformed input
6. No private body leakage
7. Bounded output and required core field presence
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.ih_dashboard_adapter import adapt_chat, adapt_market
from tools.ingestion_dashboard import (
    apply_workload_evidence,
    format_summary,
    passport_recovery_evidence,
    passport_recovery_unknown,
)

from tests.fixtures.ih_helper_payloads import (
    both_healthy_payload,
    chat_healthy_payload,
    market_healthy_payload,
    stale_payload,
    NOW,
)


# ── helpers ────────────────────────────────────────────────────────────────


def _flatten_text(obj: dict[str, Any]) -> str:
    """Flatten a dashboard row to a searchable text string."""
    return json.dumps(obj, sort_keys=True, default=str)


# ── 1. Chat healthy, market unhealthy ─────────────────────────────────────


class TestChatHealthyMarketUnhealthy:
    def test_chat_yellow_when_healthy(self) -> None:
        payload = chat_healthy_payload()
        row = adapt_chat(payload)
        assert row["status"] == "YELLOW"
        assert row["workload"] == "Idle Hacking chat"
        assert "Adapter reports OK" in " ".join(row["issues"])

    def test_market_red_when_failed(self) -> None:
        payload = chat_healthy_payload()
        row = adapt_market(payload)
        assert row["status"] == "RED"
        assert "fail" in " ".join(row["issues"])

    def test_independent_statuses(self) -> None:
        payload = chat_healthy_payload()
        chat_row = adapt_chat(payload)
        market_row = adapt_market(payload)
        assert chat_row["status"] == "YELLOW"
        assert market_row["status"] == "RED"
        assert chat_row["status"] != market_row["status"]


# ── 2. Market healthy, chat unhealthy ─────────────────────────────────────


class TestMarketHealthyChatUnhealthy:
    def test_market_yellow_when_healthy(self) -> None:
        payload = market_healthy_payload()
        row = adapt_market(payload)
        assert row["status"] == "YELLOW"
        assert row["workload"] == "Idle Hacking market"

    def test_chat_red_when_failed(self) -> None:
        payload = market_healthy_payload()
        row = adapt_chat(payload)
        assert row["status"] == "RED"
        assert "fail" in " ".join(row["issues"])

    def test_independent_statuses_reverse(self) -> None:
        payload = market_healthy_payload()
        chat_row = adapt_chat(payload)
        market_row = adapt_market(payload)
        assert chat_row["status"] == "RED"
        assert market_row["status"] == "YELLOW"
        assert chat_row["status"] != market_row["status"]


# ── 3. Historical failures + current success (Wave 1 fix) ─────────────────


class TestHistoricalFailuresCurrentSuccess:
    def test_chat_ok_despite_high_cumulative_fails(self) -> None:
        payload = both_healthy_payload()
        payload["chat"]["writes_ok"] = 4555
        payload["chat"]["writes_failed"] = 4554
        row = adapt_chat(payload)
        assert row["status"] == "YELLOW"
        text = _flatten_text(row)
        assert '"cumulative_writes_failed": 4554' in text or "4554" in text

    def test_market_ok_despite_high_cumulative_fails(self) -> None:
        payload = both_healthy_payload()
        payload["market"]["writes_ok"] = 4555  # not in market schema but in metadata
        payload["market"]["writes_failed"] = 4554
        row = adapt_market(payload)
        assert row["status"] == "YELLOW"

    def test_historical_fails_visible_in_metadata(self) -> None:
        payload = chat_healthy_payload()
        row = adapt_chat(payload)
        text = _flatten_text(row)
        assert "cumulative_writes_failed" in text


# ── 4. Stale data ─────────────────────────────────────────────────────────


class TestStaleData:
    def test_chat_stale_is_red(self) -> None:
        payload = stale_payload()
        row = adapt_chat(payload)
        assert row["status"] == "RED"
        assert "stale" in " ".join(row["issues"])

    def test_market_stale_is_red(self) -> None:
        payload = stale_payload()
        row = adapt_market(payload)
        assert row["status"] == "RED"
        assert "stale" in " ".join(row["issues"])

    def test_stale_freshness_reflected(self) -> None:
        payload = stale_payload()
        row = adapt_market(payload)
        assert "source_freshness" in row
        assert "s ago" in row["source_freshness"]


# ── 5. Malformed input ────────────────────────────────────────────────────


class TestMalformedInput:
    def test_non_dict_payload_chat(self) -> None:
        row = adapt_chat("not a dict")  # type: ignore[arg-type]
        assert row["status"] == "RED"
        assert "stale" or "fail" in " ".join(row["issues"])

    def test_non_dict_payload_market(self) -> None:
        row = adapt_market("not a dict")  # type: ignore[arg-type]
        assert row["status"] == "RED"

    def test_empty_dict_chat(self) -> None:
        row = adapt_chat({})
        assert row["status"] == "RED"

    def test_empty_dict_market(self) -> None:
        row = adapt_market({})
        assert row["status"] == "RED"

    def test_missing_chat_data(self) -> None:
        payload = both_healthy_payload()
        del payload["chat"]
        row = adapt_chat(payload)
        assert row["status"] == "RED"

    def test_missing_market_data(self) -> None:
        payload = both_healthy_payload()
        del payload["market"]
        row = adapt_market(payload)
        assert row["status"] == "RED"

    def test_chat_none(self) -> None:
        payload = both_healthy_payload()
        payload["chat"] = None
        row = adapt_chat(payload)
        assert row["status"] == "RED"

    def test_market_none(self) -> None:
        payload = both_healthy_payload()
        payload["market"] = None
        row = adapt_market(payload)
        assert row["status"] == "RED"


# ── 6. No private body leakage ────────────────────────────────────────────


class TestNoPrivateBodyLeakage:
    FORBIDDEN_PATTERNS = [
        "raw_body", "chat_body", "credential", "api_key", "token",
        "cookie", "session_id", "browser_profile", "error_message_private",
    ]

    def test_chat_no_forbidden_content(self) -> None:
        payload = both_healthy_payload()
        row = adapt_chat(payload)
        text = _flatten_text(row)
        for pattern in self.FORBIDDEN_PATTERNS:
            assert pattern not in text, f"Forbidden pattern found in chat row: {pattern}"

    def test_market_no_forbidden_content(self) -> None:
        payload = both_healthy_payload()
        row = adapt_market(payload)
        text = _flatten_text(row)
        for pattern in self.FORBIDDEN_PATTERNS:
            assert pattern not in text, f"Forbidden pattern found in market row: {pattern}"

    def test_no_filesystem_paths(self) -> None:
        payload = both_healthy_payload()
        for adapt_fn in (adapt_chat, adapt_market):
            text = _flatten_text(adapt_fn(payload))
            for indicator in ("/home/", "/Users/", "/tmp/", "data_dir"):
                assert indicator not in text, f"Path leak in {adapt_fn.__name__}: {indicator}"

    def test_no_raw_error_bodies(self) -> None:
        payload = both_healthy_payload()
        payload["errors"] = ["TypeError: 'NoneType' object has no attribute 'items'"]
        for adapt_fn in (adapt_chat, adapt_market):
            text = _flatten_text(adapt_fn(payload))
            assert "NoneType" not in text


# ── 7. Bounded output / structural integrity ──────────────────────────────


class TestBoundedOutput:
    REQUIRED_ROW_KEYS = {
        "workload", "collector", "reference", "last_success",
        "source_freshness", "db_freshness", "offload", "backup",
        "capacity", "status", "evidence_level", "evidence_timestamp",
        "detail", "issues",
    }

    def test_all_row_keys_present_chat(self) -> None:
        payload = both_healthy_payload()
        row = adapt_chat(payload)
        missing = self.REQUIRED_ROW_KEYS - set(row.keys())
        assert not missing, f"Missing row keys: {missing}"

    def test_all_row_keys_present_market(self) -> None:
        payload = both_healthy_payload()
        row = adapt_market(payload)
        missing = self.REQUIRED_ROW_KEYS - set(row.keys())
        assert not missing, f"Missing row keys: {missing}"

    def test_detail_is_dict(self) -> None:
        for payload in (both_healthy_payload(), chat_healthy_payload(), stale_payload()):
            for adapt_fn in (adapt_chat, adapt_market):
                assert isinstance(adapt_fn(payload)["detail"], dict)

    def test_issues_is_list(self) -> None:
        for adapt_fn in (adapt_chat, adapt_market):
            row = adapt_fn(both_healthy_payload())
            assert isinstance(row["issues"], list)

    def test_workload_names_correct(self) -> None:
        payload = both_healthy_payload()
        assert adapt_chat(payload)["workload"] == "Idle Hacking chat"
        assert adapt_market(payload)["workload"] == "Idle Hacking market"

    def test_evidence_level_live(self) -> None:
        payload = both_healthy_payload()
        assert adapt_chat(payload)["evidence_level"] == "live"
        assert adapt_market(payload)["evidence_level"] == "live"

    def test_references_correct(self) -> None:
        payload = both_healthy_payload()
        assert adapt_chat(payload)["reference"] == "ROADMAP §4I-G1"
        assert adapt_market(payload)["reference"] == "ROADMAP §4D-G1"

    def test_deployed_revision_null(self) -> None:
        payload = both_healthy_payload()
        text = _flatten_text(adapt_chat(payload))
        assert "deployed_revision" not in text

    def test_capacity_unknown(self) -> None:
        payload = both_healthy_payload()
        assert "missing_producer" in adapt_chat(payload)["capacity"]
        assert "missing_producer" in adapt_market(payload)["capacity"]

    def test_last_success_is_iso_or_unknown(self) -> None:
        payload = both_healthy_payload()
        for adapt_fn in (adapt_chat, adapt_market):
            ls = adapt_fn(payload)["last_success"]
            assert ls == "unknown" or "T" in ls or "Z" in ls

    def test_offload_preserved(self) -> None:
        payload = both_healthy_payload()
        row = adapt_market(payload)
        assert row["offload"] != "unknown"


class TestPortfolioSummary:
    def test_passport_is_unknown_without_dated_evidence(self) -> None:
        row = passport_recovery_unknown()
        assert row["workload"] == "Passport / backup"
        assert row["status"] == "UNKNOWN"
        assert "dated Passport recovery-confidence evidence" in row["issues"][0]

    def test_summary_routes_actions_without_claiming_health(self) -> None:
        rows = [
            passport_recovery_unknown(),
            {
                "workload": "Traderie",
                "status": "UNKNOWN",
                "issues": ["No live Traderie probe adapter deployed."],
            },
        ]
        output = format_summary(rows)
        assert "Ivy Control Portfolio Health" in output
        assert "Passport / backup\nUNKNOWN" in output
        assert "Refresh Passport recovery-confidence evidence" in output
        assert "Collect a current Traderie exporter" in output

    def test_current_passport_evidence_is_verified_without_identity_leak(self) -> None:
        evidence = Path(__file__).parent / "fixtures" / "passport_recovery_confidence_verified.json"
        row = passport_recovery_evidence(evidence)
        assert row["status"] == "GREEN"
        assert row["confidence_state"] == "VERIFIED"
        assert row["detail"]["observed_at"] == "2030-07-18T12:00:00Z"
        assert "host_identity" not in row["detail"]

    def test_expired_passport_evidence_returns_unknown(self) -> None:
        evidence = Path(__file__).parent / "fixtures" / "passport_recovery_confidence_expired.json"
        row = passport_recovery_evidence(evidence)
        assert row["status"] == "UNKNOWN"
        assert row["confidence_state"] == "UNKNOWN"
        assert "expired" in row["issues"][0]

    def test_explicit_reddit_card_overlays_only_its_workload(self, tmp_path: Path) -> None:
        card = {
            "schema_version": "1.0",
            "asset": "reddit-ops",
            "evidence_type": "operational_confidence",
            "observed_at": "2030-07-18T12:00:00Z",
            "expires_at": "2030-08-17T12:00:00Z",
            "host_identity": "sanitized-test-host",
            "ivy_revision": "test-revision",
            "policy_reference": "docs/HEALTH_CONTRACT.md",
            "backup_scope": "bounded test scope",
            "verification_method": ["fixture review"],
            "result": "VERIFIED",
            "findings": ["Fixture only."],
            "disposition": "No production action.",
            "review_owner": "test",
        }
        (tmp_path / "reddit-ops-operational.json").write_text(json.dumps(card), encoding="utf-8")
        rows = [
            {"workload": "WGU Reddit", "status": "UNKNOWN", "evidence_level": "missing_producer",
             "evidence_timestamp": "unknown", "detail": {}, "issues": ["missing"]},
            {"workload": "Traderie", "status": "UNKNOWN", "evidence_level": "missing_producer",
             "evidence_timestamp": "unknown", "detail": {}, "issues": ["missing"]},
        ]
        updated = apply_workload_evidence(rows, tmp_path)
        assert updated[0]["confidence_state"] == "VERIFIED"
        assert updated[0]["status"] == "GREEN"
        assert updated[1]["status"] == "UNKNOWN"
