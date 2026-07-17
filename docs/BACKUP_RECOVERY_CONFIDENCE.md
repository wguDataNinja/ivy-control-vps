# Backup Recovery Confidence Model

**Status:** Current authority for portfolio backup recovery confidence assessment.
**Version:** 1.0
**Design principle:** Confidence is DERIVED from evidence, never manually set.

---

## 1. Confidence Levels

| Level | Label | Criteria |
|-------|-------|----------|
| HIGH   | Verified and tested | Verified manifest + checksum verification passed + restore test passed + snapshot age < 90 days |
| MEDIUM | Verified, no recent test | Verified manifest + checksum passed but no recent restore test, or snapshot age >= 90 days |
| LOW    | Unverified or stale | No verified snapshot or snapshot age > 90 days |
| UNKNOWN | No manifest exists | No manifest file found on backup target |

---

## 2. Derivation Rules

Confidence is computed from three evidence sources:

1. **Manifest integrity** — the manifest file parses, SHA256 sidecar matches, required fields present
2. **Checksum verification** — rsync `-avc --dry-run` reports zero mismatches across all backed-up trees
3. **Restore test** — a bounded sample of files was restored to `/private/tmp/ivy-restore-test-<date>/`, and every restored file matched its source SHA-256
4. **Snapshot age** — days since `created_at` in the latest manifest

### Rule table

| Manifest | Checksum | Restore test | Age < 90d | Result |
|----------|----------|-------------|-----------|--------|
| ✓        | ✓         | ✓           | ✓         | HIGH   |
| ✓        | ✓         | —            | ✓         | MEDIUM |
| ✓        | ✓         | ✓           | ✗         | MEDIUM |
| ✓        | ✓         | —            | ✗         | MEDIUM |
| ✓        | ✗         | any          | any       | LOW    |
| ✗        | any       | any          | any       | LOW    |
| —        | —         | —            | —         | UNKNOWN |

---

## 3. Computation

```python
def compute_confidence(
    manifest_valid: bool,
    checksum_verified: bool,
    restore_proven: bool,
    snapshot_age_days: int | None,
) -> str:
    if manifest_valid and checksum_verified and restore_proven and snapshot_age_days is not None and snapshot_age_days < 90:
        return "HIGH"
    if manifest_valid and checksum_verified:
        return "MEDIUM"
    if manifest_valid or checksum_verified or restore_proven:
        return "LOW"
    return "UNKNOWN"
```

---

## 4. Reporting

Confidence is recorded in `execution-result.json` under the key `recovery_confidence`. The confidence value is computed after the final state is reached.

Confidence is never user-configurable. To increase confidence, produce more evidence: run a restore test, verify checksums, or create a fresh snapshot.
