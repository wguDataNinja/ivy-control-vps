# TODO

This file tracks approved follow-up work for IvyControlVPS. Keep entries concise, current, and limited to actionable work. Completed items should be removed or moved into the appropriate log or durable documentation rather than retained indefinitely.

## Next

- Define the detailed local implementation agent contract for OpenCode, Codex, and similar agents.
- Define the provisional VPS/Hermes orchestration contract.
- Resolve the actual VPS checkout path and private-context model only when known.
- Define logging retention and periodic review automation.
- Define the repository-admission process.
- Define the portfolio-level LLM strategy.
- Define the planned daily documentation loop and its pull-request workflow.

## Later

- Define repo-specific templates only after validating them against real repository needs.
- Decide whether a license should be added.
- Decide whether any private MacBook context should be provisioned to the VPS for Hermes.
- Decide whether `SESSION.md` provides unique value or should remain optional.

# Work Session 5 TODO

**Session name:** `gpt-5-traderie-recovery-and-reddit-ops-stabilization`

**Primary operating model:** OpenCode performs discovery, source preparation, evidence gathering, and Codex packet construction. Codex is reserved for privileged production execution. Routine Git publication is a direct git-steward instruction. One failed production attempt produces one focused remediation task rather than broad rediscovery.

**Workflow rules:**

1. One combined OpenCode admission/source-readiness task per workstream.
2. Routine Git publication through a direct git-steward instruction.
3. One privileged Codex production task.
4. One passive natural-run acceptance check.
5. Closeout.

Use objective progress monitoring. Journal silence alone is not a hang signal — include file mtime/size and process state.

---

## 1. Authoritative starting state

### 1.1 Traderie

- **Classification:** `PRODUCTION_DEGRADED`
- **Authority:** VPS systemd is sole scheduler and writer. Mac launchd is inactive.
- **Deployed SHA:** `e5ebd0f6dd41bcb4e1d8a88f272be89b225cfd40`
- **Runtime:** Segmented execution deployed. Per-segment timeouts: pc_sc_nl=180s, pc_sc_l=240s, pc_hc_l=360s, pc_hc_nl=480s.
- **Timer:** `traderie-ingest-snapshot.timer` enabled, active, waiting. Next fire: 2026-07-12 00:01:29 UTC.
- **Manual bounded generation:** Passed (Codex 5, 15:45–15:57 UTC, all 4 segments, exit=0).
- **Persistent catch-up:** Passed (15:58–16:10 UTC, all 4 segments, exit=0).
- **Natural scheduled generation (18:01:46 UTC):** **Partially failed.** pc_sc_nl, pc_sc_l, pc_hc_l succeeded. pc_hc_nl reached its 480s bound and timed out. Overall exit=1.
- **Health:** DB-backed `health_runs` exist and report `ok`. File-based health export path is empty (`/home/scraper/data/traderie/health/` is an empty directory).
- **Backup:** Newest dump `traderie_20260709T090253Z.dump` (July 9, ~2 days stale). Health reports `backup_state=ok` — no explicit freshness threshold is defined.
- **Reboot:** `/var/run/reboot-required` exists. `Linger=yes`. Controlled reboot not yet performed.

### 1.2 Reddit Ops

- **Authority:** VPS systemd user timer is sole ingestion scheduler (daily 07:00 UTC).
- **Backup service:** `wgu-reddit-backup.service` fails with 203/EXEC — ExecStart references `backup_reddit_ops.sh`; actual file is `backup_reddit_ops_pg.sh`.
- **Backup timer:** `wgu-reddit-backup.timer` enabled, active, but will trigger the failing service.
- **Reviewed source:** Backup unit files exist at `deploy/systemd/wgu-reddit-backup.{service,timer}` plus tests (Agent 5, untracked).
- **Restore drill:** Contradictory evidence — DATABASE.md claims done, CONTROL.md says not.
- **Git publication:** **Blocked.** Local history is 12 ahead of `origin/main`. Commit `e4acae0` contains tracked credentials. Must not push normally.
- **Mac:** No active Reddit ingestion launchd jobs.
- **Reboot:** Linger untested. Timer `Persistent=true`.

### 1.3 Portfolio

- Ingestion-admission matrix complete (11 repositories classified).
- Next deterministic admission candidate: **SJC Intel** (has systemd units, 11 migrations, health scripts, `.env.example`).

---

## 2. Workstream 1 — Traderie production recovery

**Primary agents:** OpenCode then Codex then OpenCode (review)

**Roadmap:** §§4A, 5A, 7G, 7H, 19A

### Objective

Restore Traderie to a healthy production classification. Resolve the pc_hc_nl timeout, verify health-output behavior, define backup freshness policy, prove one natural scheduled run, then perform controlled reboot proof.

### Required work

**Phase 1 — Root-cause investigation (OpenCode)**

- Collect direct runtime, retry, volume, latency, and progress evidence for pc_hc_nl from the 18:01:46 natural run.
- Determine whether the 480s timeout reflects normal workload variability or an application/runtime defect (e.g., rate limiting, Traderie.com latency, cloudscraper behavior).
- Do not increase the timeout without evidence.
- Verify health export output path and behavior — understand why the file-based health path is empty while DB-backed health_runs exist.
- Define an explicit backup-freshness threshold for `backup_state` in the health contract.

**Phase 2 — Source correction and publication (OpenCode + git-steward)**

- Apply the exact source change determined by Phase 1.
- Add or update regression tests.
- Run full test suite.
- Publish through git-steward. Record new SHA.

**Phase 3 — Production deployment and verification (Codex)**

- Deploy the exact published SHA to VPS.
- Update helper pin, revision metadata, and installed units.
- Run health smoke.
- Prove one bounded generation (all 4 segments, exit=0).
- Enable timer only after bounded generation passes.
- Wait for and prove one genuine natural scheduled generation.

**Phase 4 — Controlled reboot proof (Codex)**

- Only after natural-run success.
- Perform controlled reboot during low-activity window.
- Verify post-reboot: timer fires, generation completes, health reports ok, Mac authority remains absent.

**Phase 5 — Evidence review (OpenCode)**

- Review all Phase 1–4 evidence.
- Update classification to `PRODUCTION_COMPLETE` or identify remaining gaps.

### Definition of done

- pc_hc_nl segment completes within its bound during a natural scheduled run.
- Health output is verifiable (file-based or DB-backed with evidence).
- Backup freshness threshold is defined in the health contract.
- One natural scheduled generation passes with all 4 segments.
- Controlled reboot passes with post-reboot recovery.
- Classification: `PRODUCTION_COMPLETE`.

### Stop gates

- Bounded generation fails → stop, investigate root cause before retrying.
- Natural scheduled run fails → roll back if authority is at risk, otherwise remediate per the one-fix rule.
- Reboot fails → restore Mac authority if VPS does not recover.

---

## 3. Workstream 2 — Reddit Ops sanitized publication

**Primary agents:** OpenCode then git-steward

**Roadmap:** §§2A, 4A, 9A, 9B

### Objective

Publish the Reddit Ops production code and reviewed backup units to GitHub without exposing credentials in history.

### Required work

**Phase 1 — History reconstruction (OpenCode)**

- Reconstruct clean publishable history from the 12 unpublished commits, excluding the credential-bearing root commit `e4acae0`.
- Cherry-pick the 11 safe commits (`4bf07f2` through `7047400`) onto `origin/main`.
- Add the Agent 5 backup unit files (`deploy/systemd/wgu-reddit-backup.{service,timer}`, `tests/test_wgu_reddit_backup_units.py`).

**Phase 2 — Review and secret scan (OpenCode then human)**

- Review the full published range for any remaining secrets, local paths, or private material.
- Run a full secret scan on the publication branch.
- Present for Buddy approval.

**Phase 3 — Publication (git-steward)**

- Push the approved publication branch to `origin/main`.
- Return the authoritative SHA.

### Definition of done

- Reddit Ops is published at an exact SHA on `origin/main`.
- No credentials, local paths, or private material in published history.
- Backup unit source and tests are part of the published repository.

### Stop gates

- Any secret found in the proposed publication range → stop, remove before push.
- Buddy must approve the publication strategy before any push.

---

## 4. Workstream 3 — Reddit Ops production recovery

**Primary agents:** OpenCode then Codex then OpenCode (review)

**Roadmap:** §§3C, 5A, 6A, 7B, 7E

**Condition:** Workstream 2 (publication) must complete first, or Buddy must authorize rsync-based deployment from the reviewed source.

### Required work

**Phase 1 — Codex production execution**

- Deploy the exact published SHA to VPS (or rsync the reviewed source if publication is not yet complete).
- Repair the backup service: install the reviewed unit or correct the ExecStart path.
- Create a fresh backup by running the repaired service.
- Verify checksum, artifact age, and manifest.
- Perform an isolated restore drill into a temporary database.
- Validate schemas, migrations, and representative row counts.
- Clean up the isolated restore database.
- Reconcile the restore documentation (resolve the DATABASE.md vs CONTROL.md contradiction).

**Phase 2 — Timer and reboot acceptance**

- Prove the backup timer fires on schedule.
- Verify `loginctl enable-linger scraper` for user timer persistence.
- Verify `Persistent=true` behavior.
- Perform a controlled reboot or document why it is not required.

**Phase 3 — Evidence review (OpenCode)**

- Verify backup, restore, timer, and reboot evidence.
- Update Reddit Ops classification to `PRODUCTION_ACTIVE` or identify remaining gaps.

### Definition of done

- Backup timer active and producing verified dumps.
- Restore drill completed and documented.
- Timer persistence proven.
- Reddit Ops classification: `PRODUCTION_ACTIVE` or better.

### Stop gates

- Backup script fails → stop, investigate root cause.
- Restore validation fails → stop, preserve restore database for investigation.
- Reboot causes timer failure → restore Mac ingestion if VPS does not recover.

---

## 5. Workstream 4 — SJC Intel admission readiness

**Primary agents:** OpenCode

**Roadmap:** §§2A, 10A, 18D

**Condition:** Do not require SJC Intel production cutover in Session 5 unless Traderie and Reddit Ops stabilization work completes cleanly and the session remains controlled.

### Required work

One combined admission and source-readiness task covering:

- **Authority:** Current scheduler, writer, and data ownership.
- **Runtime:** Systemd units, venv, environment files, service user.
- **Data destination:** Database, schema, migration state, role model.
- **Idempotency:** Deduplication, backfill, checkpointing behavior.
- **Health:** Existing health scripts and v2 contract compatibility.
- **Backup/restore:** Backup script existence, restore drill readiness.
- **Exact-SHA deployment:** VPS checkout readiness, systemd static analysis.
- **Scheduler transfer:** Proposed transfer sequence and rollback plan.
- **Source changes and tests:** Any source corrections identified during assessment.
- **Publication and Codex packets:** Git publication plan and Codex execution packet.

### Deliverable

`_internal/outbox/session5/agent-N-sjc-intel-admission-readiness.md`

### Definition of done

- SJC Intel has a CONTROL.md, VPS readiness assessment, and a bounded admission packet.
- Reddit Ops pattern reuse is documented.
- The admission packet is ready for Codex execution in a future session.

### Explicitly out of scope

- SJC Intel production cutover — deferred to Session 6 unless stabilization work is fully complete.
- Database provisioning, role creation, or data migration on VPS PostgreSQL.

---

## 6. Workstream 5 — Documentation and closeout

**Primary agents:** OpenCode then git-steward

### Required work

- Reconcile `ROADMAP.md` with current Traderie and Reddit Ops production state.
- Update `_internal/README_INTERNAL.md` with current production facts.
- Review and apply deferred workflow proposals from `_internal/GPT_ORCHESTRATED_WORKFLOW.md` Appendix A.
- Retain the GPT local-edit limitation until the desktop write integration is verified fixed.
- Write the Session 5 log.
- Prepare the next TODO from actual Session 5 evidence rather than forward-planning.

### Definition of done

- `ROADMAP.md` reflects current production facts and next-session scope.
- `_internal/README_INTERNAL.md` is accurate.
- All deferred Appendix A items are consolidated, superseded, or explicitly re-deferred.
- Session 5 log exists.
- Git closeout is clean, and the next TODO is ready.

---

## 7. Definition of done (session)

Session 5 is complete when:

- Traderie classification is `PRODUCTION_COMPLETE` (natural run passing, reboot proven) or `PRODUCTION_DEGRADED` with exact evidence and bounded remediation deferred.
- Reddit Ops is published at an exact SHA with no credentials in history.
- Reddit Ops backup and restore are proven.
- SJC Intel admission packet is ready.
- ROADMAP.md and README_INTERNAL.md are current.
- Authorized documentation is committed through git-steward.
- Unrelated work (product JSONs, `workflows/session-close.md`, `_internal/`) remains untouched.

---

## 8. Explicit non-goals

Do not use Session 5 to:

- Begin SJC Intel production cutover unless Traderie and Reddit Ops stabilization complete cleanly.
- Expand WGU Catalog, Atlas, BSDA Courses, or Idle Hacking KB scope.
- Design Hermes execution or LLM workflow automation.
- Perform Git-history rewriting beyond the Reddit Ops sanitization in Workstream 2.
- Migrate IH Market Companion, Idle Hacking KB, or other unreviewed workloads.
- Remove or alter Traderie product JSON files.