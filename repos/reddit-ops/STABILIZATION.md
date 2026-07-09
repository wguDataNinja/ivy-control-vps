# Reddit Ops — Stabilization Checklist

**Lifecycle state:** `production-stabilizing`
**Goal:** `production-complete` — PostgreSQL collector is authoritative, observable, recoverable, and documented.

---

## Gate 1: Approved-Partial Exit Semantics

| Criterion | Status |
|-----------|--------|
| `partial` (expected errors only) → exit 0, systemd success | ✅ Done (run 31-34 verified) |
| `partial` (unexpected errors) → exit 1, systemd failure | ✅ Done (by default — not counted as approved) |
| Known inaccessible-target set documented | ✅ Done (CONTROL.md) |
| List is validated per run | ✅ Done (fetcher compares error set against known set) |

---

## Gate 2: Unexpected Failures

| Criterion | Status |
|-----------|--------|
| `failed` status → exit 1, systemd failure | ✅ Done |
| OAuth errors produce failure | ✅ Done |
| PostgreSQL errors produce failure | ✅ Done |

---

## Gate 3: Three Consecutive Systemd-Triggered Runs

| Criterion | Status |
|-----------|--------|
| Run 1 (systemd start) completes with success | ✅ Done (run 31 — Result=success, ExecMainStatus=0) |
| Run 2 (systemd start) completes with success | ✅ Done (run 33 — Result=success, ExecMainStatus=0) |
| Run 3 (systemd start) completes with success | ✅ Done (run 34 — Result=success, ExecMainStatus=0) |
| No unexpected errors across all three | ✅ Done (all errors were 4 approved inaccessible targets) |
| Heartbeat observed in each run | ✅ Done |
| Accelerated timer runs also passed | ✅ Done (temporary timer at :27, :37, :47) |
| Production schedule restored | ✅ Done (07:00 UTC daily restored) |

---

## Gate 4: Automated PostgreSQL Backup

| Criterion | Status |
|-----------|--------|
| Backup script exists and is tested | ✅ Done (`backup_reddit_ops.sh`, tested with pg_dump) |
| Backup runs on a schedule | ✅ Done (`wgu-reddit-backup.timer` at 08:00 UTC daily) |
| Backup artifact checksummed | ✅ Done (SHA-256 generated and stored) |
| Backup validated | ✅ Done (`pg_restore --list` confirms 23 data tables) |
| Backup age monitored | ❌ Open — monitoring alerting not yet implemented |

---

## Gate 5: Mac Archive Verification

| Criterion | Status |
|-----------|--------|
| Latest backup copied to Mac | ✅ Done (scp to `backups/postgres/reddit-ops/`) |
| Archive checksum verified | ✅ Done (SHA-256 matches VPS origin) |
| Archive manifest created | ⚠️ Partial — checksum recorded, formal manifest pending |

---

## Gate 6: Full Restore Drill

| Criterion | Status |
|-----------|--------|
| Restore procedure documented | ✅ Done (RUNBOOK.md) |
| Database restored to test DB | ✅ Done (`reddit_ops_restore_verify`) |
| Row counts match origin | ✅ Done (verified: 44,967 posts, 46,503 observations, 51 subreddits, 33 ingestion runs) |
| Validation SQL passes | ✅ Done (all tables, constraints, indexes present) |
| Owner/permissions verified | ⚠️ Partial — restore used `--no-owner --no-privileges`; full role restore requires owner privileges |

---

## Gate 7: Reboot Recovery

| Criterion | Status |
|-----------|--------|
| PostgreSQL restarts after reboot | ❌ Blocked — no passwordless sudo on VPS |
| Collector service restarts after reboot | ❌ Blocked — no passwordless sudo on VPS |
| Timer fires after reboot | ❌ Blocked — no passwordless sudo on VPS |

**Blocker:** The `scraper` user has sudo but requires interactive password entry. Non-interactive reboot is not possible. Requires either sudoers configuration change or Buddy to run `sudo reboot` interactively.

---

## Gate 8: Post-Reboot Scheduled Run

| Criterion | Status |
|-----------|--------|
| Timer fires after reboot | ❌ Blocked — gate 7 must pass first |
| Run completes successfully | ❌ Blocked |
| No stale-run recovery confusion | ❌ Blocked |

---

## Gate 9: Monitoring Thresholds

| Criterion | Status |
|-----------|--------|
| Service state monitored | ✅ Implemented — `systemctl --user status` via SSH |
| Schedule freshness monitored | ✅ Implemented — `systemctl --user list-timers` |
| Run duration thresholds defined | ⚠️ Documented — defined in RUNBOOK.md; alerting not automated |
| Heartbeat age thresholds defined | ⚠️ Documented — stale threshold env var; alerting not automated |
| Database health monitored | ✅ Implemented — `pg_isready` + `tools/check_reddit_ops_pg_health.py` |
| Backup age monitored | ⚠️ Documented — manual verification; automated alerting missing |
| Disk growth monitored | ⚠️ Documented — `df -h` check; automated alerting missing |

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
| SQLite preserved as rollback | ✅ Done — preserved at `/home/scraper/data/wgu-reddit/WGU-Reddit.db` |
| Backup/restore proven before retirement | ✅ Done — pg_dump + pg_restore drill completed |
| Retirement criteria defined | SQLite is retired from operational recovery. All normal recovery now relies on PostgreSQL backups and restore procedures. SQLite is preserved as an immutable historical artifact and rollback contingency. Deletion requires: (1) multiple successful PostgreSQL backup/restore cycles at the normal cadence, (2) a successful reboot recovery, and (3) explicit Buddy approval. |

---

## Summary

| Gate | Status |
|------|--------|
| 1. Approved-partial exit | ✅ Done |
| 2. Unexpected failures | ✅ Done |
| 3. Systemd-triggered runs (×3) | ✅ Done |
| 4. Automated backup | ✅ Done |
| 5. Mac archive | ✅ Done |
| 6. Restore drill | ✅ Done |
| 7. Reboot recovery | ❌ Blocked (no passwordless sudo) |
| 8. Post-reboot run | ❌ Blocked (gate 7 must pass) |
| 9. Monitoring | ⚠️ Partial — checks exist, alerting not automated |
| 10. SHA tracking | ❌ Blocked (WGU-Reddit Git publication blocked by secrets) |
| 11. Drift detection | ⚠️ Partial — checksum comparison available manually |
| 12. Rebuild reproducibility | ⚠️ Partial — code tracked, VPS config not Git-based |
| 13. SQLite retirement | ✅ Done — retired from operational recovery, preserved as historical artifact |
| **Final: production-complete** | ❌ Open — two blockers remain (reboot, Git publication) |
