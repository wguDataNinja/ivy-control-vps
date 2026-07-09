# Reddit Ops — Cutover History

## 1. PostgreSQL Platform and Import (2026-07-06 — 2026-07-07)

PostgreSQL 16 installed on VPS. Database `reddit_ops` created with schemas `reddit_core`, `wgu_reddit`, `bsda_courses`. Migrations 0001-0005 applied. Legacy SQLite data imported (canonical posts, subreddits, memberships). Comments, course codes, legacy run logs excluded per migration contract.

**Evidence:** `_internal/outbox/codex-output-consolidated.md`

---

## 2. First Failed Cutover and Rollback (2026-07-08, ~12:24 UTC)

The first production-equivalent PostgreSQL service run did not finish or commit after ~35 minutes. Root cause: the PostgreSQL collector path had **no frontier check** — it iterated all 52 subreddits × 1000 posts without per-subreddit commit, heartbeat, or cancellation handling. The SQLite path breaks early via `created_utc <= frontier`.

**Rollback:** Service stopped, SQLite timer restored, PostgreSQL timer removed. No data lost.

**Evidence:** `_internal/outbox/codex-output-reddit-ops-cutover.md`

---

## 3. Frontier/Progress Parity Work (2026-07-08)

**Fixes applied:**
- Per-subreddit frontier check via `MAX(created_utc)` on `reddit_core.posts`
- Per-subreddit commits (progress visible immediately)
- Migration 0006: heartbeat, progress, cancellation columns
- SIGTERM/SIGINT handlers for graceful cancellation
- Idempotent behavior confirmed (run 14: 0 new posts)
- Cancellation proof (run 16: cancelled, 1/52 targets, data preserved)

**Deployed to VPS:** `reddit_ops_pg.py` (via SCP), migration 0006 applied.

**Evidence:** `_internal/outbox/sqlite-pg-frontier-parity-report.md`

---

## 4. Stale-Run Recovery and Advisory Lock (2026-07-08)

**Additions:**
- `recover_stale_runs()` — startup stale-run recovery with configurable threshold (default 30 min)
- `acquire_collector_lock()` / `release_collector_lock()` — PostgreSQL advisory lock
- Hard-termination proof: SIGKILL → stale → recovery → normal run

**Evidence:** `_internal/outbox/stale-recovery-cutover-readiness.md`

---

## 5. Second Failed Cutover and Rollback (2026-07-08, ~19:52 UTC)

The second production-equivalent proof (run 21) failed the health gate. First target WGU reported `frontier=0`, scanned 999 posts, took 899 seconds. Root cause was thought to be unknown at the time.

**Rollback:** Run cancelled at target 3/52. SQLite timer restored.

**Evidence:** `_internal/outbox/codex-output-reddit-ops-final-cutover.md`

---

## 6. Root Cause Found: `subreddit.subreddit_id` vs `subreddit.id` (2026-07-08)

The frontier fix from step 3 had a bug: `_subreddit_id_from_obj()` used `subreddit.subreddit_id` which returns `None` on PRAW Subreddit objects (that attribute exists only on Submission objects). The correct attribute is `subreddit.id`.

Earlier bounded proofs (runs 13-20) masked the bug because they used `limit_per_sub=1`, limiting each subreddit to 1 post regardless of frontier.

**Fix:** Changed `getattr(subreddit, "subreddit_id", None)` to `getattr(subreddit, "id", None)`. Added `NEW_TARGET_BOOTSTRAP_CAP = 100`. Added per-target logging with subreddit ID, frontier value, and source (existing/new/lookup_error).

**Evidence:** `_internal/outbox/pg-frontier-fix-report.md`

---

## 7. Production-Equivalent Proofs (2026-07-08, ~20:25 UTC)

**Proof 1 (run 23/24):** Full 52-target production-equivalent run. WGU: `frontier=1783539742`, `seen=2`, `elapsed=2.4s` (vs run 21: `frontier=0`, `seen=999`, `elapsed=898.9s`). Total duration: ~59s. Only 2 new posts inserted.

**Proof 2 (run 25/26):** Idempotence rerun. 0 new posts. All frontiers correct. Duration: ~55s.

---

## 8. Successful Final Cutover (2026-07-08)

Production timer `wgu-reddit-postgres-run.timer` enabled and activated. Legacy `wgu-reddit-shadow-run.timer` disabled. SQLite preserved as rollback artifact.

---

## 9. Current Caveat

The collector exits with code 1 for `partial` status (expected 4 inaccessible subreddits). This causes systemd to report a failed result. Approved-partial exit semantics hardening is the next operational task.
