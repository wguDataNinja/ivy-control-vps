"""Tests for reusable dated evidence-card validation and evaluation."""

from __future__ import annotations

import datetime as dt
import subprocess
import sys
from pathlib import Path

from tools.evidence_cards import evaluate_card, is_expired, load_card, validate_card


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
VALIDATOR = ROOT / "tools" / "validate_evidence_card.py"


def card(name: str) -> dict:
    return load_card(FIXTURES / name)


def test_current_verified_card_is_structurally_valid() -> None:
    evidence = card("passport_recovery_confidence_verified.json")
    assert validate_card(evidence, expected_asset="passport",
                         expected_evidence_type="recovery_confidence") == []
    assert evaluate_card(evidence, at=dt.datetime(2030, 7, 19, tzinfo=dt.timezone.utc))[0] == "VERIFIED"


def test_expired_card_loses_verified_claim() -> None:
    evidence = card("passport_recovery_confidence_expired.json")
    assert is_expired(evidence, at=dt.datetime(2026, 7, 18, tzinfo=dt.timezone.utc))
    state, reason = evaluate_card(evidence, at=dt.datetime(2026, 7, 18, tzinfo=dt.timezone.utc))
    assert state == "UNKNOWN"
    assert "expired" in reason


def test_missing_required_identity_is_rejected() -> None:
    evidence = card("passport_recovery_confidence_verified.json")
    del evidence["host_identity"]
    assert "missing required field: host_identity" in validate_card(evidence)


def test_unsupported_field_is_rejected() -> None:
    evidence = card("passport_recovery_confidence_verified.json")
    evidence["manual_confidence"] = "HIGH"
    assert "unsupported field: manual_confidence" in validate_card(evidence)


def test_validator_rejects_expired_evidence_by_default() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(FIXTURES / "passport_recovery_confidence_expired.json"),
         "--asset", "passport", "--evidence-type", "recovery_confidence"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1
    assert "evidence is expired" in result.stdout


def test_validator_can_inspect_expired_structure_when_requested() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(FIXTURES / "passport_recovery_confidence_expired.json"),
         "--allow-expired"], capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout
