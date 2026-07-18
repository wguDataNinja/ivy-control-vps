"""Reusable, local-only evidence-card validation and evaluation helpers.

Evidence cards are observations, not policy.  Callers must supply their path
explicitly; this module never searches private directories or contacts hosts.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any


CARD_VERSION = "1.0"
SUPPORTED_RESULTS = frozenset({"VERIFIED", "DEGRADED", "UNKNOWN"})
REQUIRED_FIELDS = frozenset({
    "schema_version", "asset", "evidence_type", "observed_at", "expires_at",
    "host_identity", "ivy_revision", "policy_reference", "backup_scope",
    "verification_method", "result", "findings", "disposition", "review_owner",
})


def parse_timestamp(value: object) -> dt.datetime | None:
    """Parse a required RFC 3339 UTC timestamp without accepting local time."""
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def load_card(path: Path) -> dict[str, Any]:
    """Load one JSON evidence card, raising ValueError with a safe message."""
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON evidence card: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError("evidence card root must be a JSON object")
    return loaded


def validate_card(
    card: dict[str, Any], *, expected_asset: str | None = None,
    expected_evidence_type: str | None = None,
) -> list[str]:
    """Return structural validation errors. Expiry is evaluated separately."""
    errors: list[str] = []
    for field in sorted(REQUIRED_FIELDS - set(card)):
        errors.append(f"missing required field: {field}")
    for field in sorted(set(card) - REQUIRED_FIELDS):
        errors.append(f"unsupported field: {field}")

    if card.get("schema_version") != CARD_VERSION:
        errors.append(f"unsupported schema_version: {card.get('schema_version')!r}")
    for field in ("asset", "evidence_type", "host_identity", "ivy_revision",
                  "policy_reference", "backup_scope", "disposition", "review_owner"):
        if field in card and (not isinstance(card[field], str) or not card[field].strip()):
            errors.append(f"{field} must be a non-empty string")
    if expected_asset and card.get("asset") != expected_asset:
        errors.append(f"asset must be {expected_asset!r}")
    if expected_evidence_type and card.get("evidence_type") != expected_evidence_type:
        errors.append(f"evidence_type must be {expected_evidence_type!r}")
    if card.get("result") not in SUPPORTED_RESULTS:
        errors.append("result must be one of: VERIFIED, DEGRADED, UNKNOWN")
    if not isinstance(card.get("verification_method"), list) or not card.get("verification_method"):
        errors.append("verification_method must be a non-empty list")
    elif not all(isinstance(item, str) and item.strip() for item in card["verification_method"]):
        errors.append("verification_method entries must be non-empty strings")
    if not isinstance(card.get("findings"), list) or not card.get("findings"):
        errors.append("findings must be a non-empty list")
    elif not all(isinstance(item, str) and item.strip() for item in card["findings"]):
        errors.append("findings entries must be non-empty strings")

    observed = parse_timestamp(card.get("observed_at"))
    expires = parse_timestamp(card.get("expires_at"))
    if observed is None:
        errors.append("observed_at must be an RFC 3339 UTC timestamp ending in Z")
    if expires is None:
        errors.append("expires_at must be an RFC 3339 UTC timestamp ending in Z")
    if observed is not None and expires is not None and expires <= observed:
        errors.append("expires_at must be later than observed_at")
    return errors


def is_expired(card: dict[str, Any], *, at: dt.datetime | None = None) -> bool:
    """Return true only for structurally parseable cards whose evidence expired."""
    expires = parse_timestamp(card.get("expires_at"))
    if expires is None:
        return False
    current = at or dt.datetime.now(dt.timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=dt.timezone.utc)
    return expires <= current


def evaluate_card(card: dict[str, Any], *, at: dt.datetime | None = None) -> tuple[str, str]:
    """Return the safe display state and a concise explanation.

    An expired card never retains a VERIFIED/DEGRADED health claim.  Structural
    validation belongs to the caller because it may include asset-specific
    expectations.
    """
    if is_expired(card, at=at):
        return "UNKNOWN", "Dated recovery-confidence evidence has expired; perform a bounded review."
    result = card.get("result")
    if result == "VERIFIED":
        return "VERIFIED", "Current dated recovery-confidence evidence is verified."
    if result == "DEGRADED":
        return "DEGRADED", "Current dated recovery-confidence evidence is degraded."
    return "UNKNOWN", "Current dated recovery-confidence evidence remains unknown."
