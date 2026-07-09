# Reddit Ops — Stabilization Checklist

**Lifecycle state:** `production-stabilizing`
**Goal:** `production-complete` — PostgreSQL collector is authoritative, observable, recoverable, and documented.

---

## Gate 1: Approved-Partial Exit Semantics

| Criterion | Status |
|-----------|--------|
| `partial` (expected errors only) → exit 0, systemd success | ❌ Open |
| `partial` (unexpected errors) → exit 1, systemd failure | ❌ Open |
| Known inaccessible-target set documented | ✅ Done (CONTROL.md) |
| List is validated per run | ❌ Open |

---

## Gate 2: Unexpected Failures

| Criterion | Status |
|-----------|--------|
| `failed` status → exit 1, systemd failure | ✅ Done |
| OAuth errors produce failure | ✅ Done |
| PostgreSQL errors produce failure | ✅ Done |

---

## Gate 3: Three Consecutive Natural Scheduled Runs

| Criterion | Status |
|-----------|--------|
| Run 1 (scheduled, not manual) completes | ❌ Pending |
| Run 2 completes | ❌ Pending |
| Run 3 completes | ❌ Pending |
| No unexpected errors across all three | ❌ Pending |
| Heartbeat observed in each run | ❌ Pending |

---

## Gate 4: Automated PostgreSQL Backup

| Criterion | Status |
|-----------|--------|
| Backup script exists and is tested | ❌ Missing |
| Backup runs on a schedule | ❌ Missing |
| Backup artifact checksummed | ❌ Missing |
| Backup age monitored | ❌ Missing |

---

## Gate 5: Mac Archive Verification

| Criterion | Status |
|-----------|--------|
| Latest backup copied to Mac | ❌ Not done |
| Archive manifest created | ❌ Not done |
| Archive checksum verified | ❌ Not done |

---

## Gate 6: Full Restore Drill

| Criterion | Status |
|-----------|--------|
| Restore procedure documented | ❌ Missing |
| Database restored to test DB | ❌ Not done |
| Row counts match origin | ❌ Not done |
| Validation SQL passes | ❌ Not done |
| Owner/permissions verified | ❌ Not done |

---

## Gate 7: Reboot Recovery

| Criterion | Status |
|-----------|--------|
| PostgreSQL restarts after reboot | ❌ Not tested |
| Collector service restarts after reboot | ❌ Not tested |
| Timer fires after reboot | ❌ Not tested |

---

## Gate 8: Post-Reboot Scheduled Run

| Criterion | Status |
|-----------|--------|
| Timer fires after reboot | ❌ Not tested |
| Run completes successfully | ❌ Not tested |
| No stale-run recovery confusion | ❌ Not tested |

---

## Gate 9: Monitoring Thresholds

| Criterion | Status |
|-----------|--------|
| Service state monitored | ❌ Not implemented |
| Schedule freshness monitored | ❌ Not implemented |
| Run duration thresholds defined | ❌ Not implemented |
| Heartbeat age thresholds defined | ❌ Not implemented |
| Database health monitored | ❌ Not implemented |
| Backup age monitored | ❌ Not implemented |
| Disk growth monitored | ❌ Not implemented |

---

## Gate 10: Deployed SHA Recorded

| Criterion | Status |
|-----------|--------|
| VPS checkout is a Git checkout | ❌ Not done |
| Deployed SHA recorded in health | ❌ Not done |
| SHA drift detectable | ❌ Not done |

---

## Gate 11: Drift Detection

| Criterion | Status |
|-----------|--------|
| Git SHA can be checked | ❌ Not done |
| Schema version can be checked | ❌ Not done |
| Service unit version can be checked | ❌ Not done |
| Drift produces actionable signal | ❌ Not done |

---

## Gate 12: Rebuild Reproducibility

| Criterion | Status |
|-----------|--------|
| Fresh clone + config can rebuild deployment | ❌ Not done |
| Dependency installation documented | ❌ Not done |
| Database bootstrap documented | ❌ Not done |

---

## Gate 13: SQLite Retirement Policy

| Criterion | Status |
|-----------|--------|
| SQLite preserved as rollback | ✅ Done |
| Retirement criteria defined | ❌ Not done |
| Backup/restore proven before retirement | ❌ Not done |

---

## Summary

| Gate | Status |
|------|--------|
| 1. Approved-partial exit | ❌ Open |
| 2. Unexpected failures | ✅ Done |
| 3. Natural scheduled runs (×3) | ❌ Open |
| 4. Automated backup | ❌ Open |
| 5. Mac archive | ❌ Open |
| 6. Restore drill | ❌ Open |
| 7. Reboot recovery | ❌ Open |
| 8. Post-reboot run | ❌ Open |
| 9. Monitoring | ❌ Open |
| 10. SHA tracking | ❌ Open |
| 11. Drift detection | ❌ Open |
| 12. Rebuild reproducibility | ❌ Open |
| 13. SQLite retirement | ❌ Open |
| **Final: production-complete** | ❌ Open |
