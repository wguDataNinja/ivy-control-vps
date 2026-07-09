# Reddit Ops — Release Gates

**Authority:** ivy-control-vps — gate decisions are owned by the control plane.
**Active governance authority:** `repos/reddit-ops/CONTROL.md`

---

## Gate Framework

Each gate produces `PASS`, `PASS WITH CONDITIONS`, `BLOCKED`, or `NOT APPLICABLE`. Gates are sequential but some may be assessed in parallel. All operational gates remain open until stabilization completes.

---

## Source and SHA

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Producer repository exists | ✅ PASS | WGU-Reddit-Feedback-Analyzer on GitHub |
| Exact SHA deployed | ❌ FAIL | VPS checkout is not a Git checkout |
| SHA recorded in health | ❌ FAIL | Not implemented |
| Drift detectable | ❌ FAIL | No Git checkout to compare against |

**Status: ❌ FAIL** — SHA tracking not yet implemented.

---

## Migration Validation

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Migrations 0001–0006 applied | ✅ PASS | Verified on VPS PostgreSQL |
| Rollback SQL exists | ✅ PASS | All 6 rollback files exist |
| Validation SQL passes | ✅ PASS | All 6 validation queries pass |
| Migration versioning works | ✅ PASS | Schema version tracking present |

**Status: ✅ PASS**

---

## Role Permissions

| Criterion | Result | Evidence |
|-----------|--------|----------|
| 6 roles provisioned | ✅ PASS | owner, migrator, writer, reader, monitor, backup |
| Least-privilege positive tests pass | ✅ PASS | Each role connects with expected permissions |
| No superuser usage | ✅ PASS | No application uses postgres superuser |

**Status: ✅ PASS**

---

## Frontier Correctness

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Existing targets use stored frontier | ✅ PASS | VPS proof 1 (run 23): WGU frontier=1783539742 |
| New targets use bootstrap cap | ✅ PASS | `NEW_TARGET_BOOTSTRAP_CAP=100` implemented |
| Case normalization correct | ✅ PASS | `getattr(subreddit, "id", None)` uses canonical Reddit ID |
| No silent 0.0 frontier | ✅ PASS | Empty subreddit ID logged as lookup_error |
| Idempotent rerun | ✅ PASS | Proof 2 (run 25): 0 new posts, correct frontiers |

**Status: ✅ PASS**

---

## Heartbeat/Progress

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Per-target commits | ✅ PASS | Each subreddit committed individually |
| Heartbeat updates | ✅ PASS | `heartbeat_at` updated after each target |
| Progress visible in DB | ✅ PASS | `current_target`, `targets_completed`, `targets_total` updated |

**Status: ✅ PASS**

---

## Stale-Run Recovery

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Stale `running` runs recovered at startup | ✅ PASS | `recover_stale_runs()` implemented |
| Threshold configurable | ✅ PASS | `REDDIT_OPS_STALE_THRESHOLD_MINUTES` env var |
| Minimum threshold enforced | ✅ PASS | 1 minute minimum |
| SIGKILL → recovery proven | ✅ PASS | Hard-termination proof completed |

**Status: ✅ PASS**

---

## Advisory Locking

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Lock acquired at startup | ✅ PASS | `pg_try_advisory_lock` with fixed lock ID |
| Lock released in `finally` | ✅ PASS | `release_collector_lock()` in `finally` block |
| Concurrent run prevented | ✅ PASS | Second process aborts if lock held |
| Survives transaction commits | ✅ PASS | Session-level advisory lock |

**Status: ✅ PASS**

---

## OAuth

| Criterion | Result |
|-----------|--------|
| App-only auth works | ✅ PASS |
| No OAuth errors in latest runs | ✅ PASS |
| Credentials stored outside Git | ✅ PASS |

**Status: ✅ PASS**

---

## Single Scheduler Authority

| Criterion | Result |
|-----------|--------|
| One production timer active | ✅ PASS — `wgu-reddit-postgres-run.timer` |
| Legacy timer disabled | ✅ PASS — `wgu-reddit-shadow-run.timer` disabled |
| Mac launchd disabled | ✅ PASS |
| No duplicate writers | ✅ PASS — advisory lock prevents |

**Status: ✅ PASS**

---

## Process Exit Semantics

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Success (0) → systemd success | ✅ PASS | Implemented |
| Partial (1) → systemd success | ❌ FAIL | Known open item |
| Cancelled (1) → systemd failure | ✅ PASS | Acceptable |
| Failure (1) → systemd failure | ✅ PASS | Correct |
| Expected partial conditions documented | ✅ PASS | In CONTROL.md |

**Status: ❌ FAIL** — approved-partial exit semantics not yet hardened.

---

## Scheduled-Run Stabilization

| Criterion | Result |
|-----------|--------|
| Three consecutive natural scheduled runs | ❌ NOT YET — PG timer recently enabled |
| No unexpected failures | ❌ NOT YET |
| Heartbeat observed per run | ❌ NOT YET |

**Status: ❌ NOT YET** — timer was enabled after final cutover; natural runs pending.

---

## Reboot Recovery

| Criterion | Result |
|-----------|--------|
| PostgreSQL restarts after reboot | ❌ NOT TESTED |
| Service restarts after reboot | ❌ NOT TESTED |
| Scheduled run fires after reboot | ❌ NOT TESTED |

**Status: ❌ NOT YET** — reboot not yet performed.

---

## SQLite Retirement

| Criterion | Result |
|-----------|--------|
| SQLite preserved as rollback | ✅ PASS |
| Retirement criteria documented | ❌ MISSING |
| Backup/restore proven before retirement | ❌ NOT YET |

**Status: ❌ NOT YET** — retirement criteria not yet defined.

---

## Stop Conditions

Deployment, cutover, or timer activation must stop immediately if:
- Unexpected `frontier=0` for any known subreddit
- Unbounded listing scan (>100 posts per subreddit without frontier break)
- Stale heartbeat (no update within stale threshold)
- Multiple active collectors (advisory lock failure)
- Unexpected target errors beyond the known 403/404 set
- OAuth errors
- PostgreSQL connection or query errors
- Backup failure or backup age exceeds threshold
- Restore mismatch (row counts differ)
- Scheduler ambiguity (both PG and SQLite timers active)
- Drift from deployed SHA detected

---

## Current Blockers

1. SHA tracking not implemented — VPS checkout is not a Git checkout
2. Approved-partial exit semantics not hardened
3. Automated backups not implemented
4. Restore drill not completed
5. Reboot recovery not tested
6. Scheduled-run stabilization pending (3 consecutive natural runs)
7. SQLite retirement criteria not defined
