# Reddit Ops — Repository Control

**Purpose:** Active governance authority for Reddit Ops (WGU-Reddit PostgreSQL collector).
**Managed service:** Reddit Ops — daily WGU subreddit collection and analysis
**Producer repository:** `/Users/buddy/Desktop/WGU-Reddit` — `github.com/wguDataNinja/WGU-Reddit-Feedback-Analyzer.git`
**Production database:** `reddit_ops` on VPS PostgreSQL 16
**Schemas:** `reddit_core` (shared canonical data), `wgu_reddit` (WGU project state), `bsda_courses` (future project schema)
**Detailed gate evidence:** `repos/reddit-ops/RELEASE_GATES.md`
**Cutover history:** `repos/reddit-ops/CUTOVER_HISTORY.md`
**Stabilization checklist:** `repos/reddit-ops/STABILIZATION.md`
**Runbook:** `repos/reddit-ops/RUNBOOK.md`

---

## Portfolio Admission State

| Gate | State | Notes |
|------|-------|-------|
| 1 — Portfolio Admission | PASS | Repository is recognized as managed. Identity, remote, SHA documented. |
| 2 — Public Repository Readiness | BLOCKED | Credential-bearing commit `e4acae0` in local history blocks clean GitHub publication. |
| 3 — GitHub Publication | BLOCKED | Cannot publish until Gate 2 blocker is resolved. |
| 4 — Deployment Readiness | PASS WITH CONDITION | VPS deployment, roles, migrations, locking, frontier/idempotence proven; backup unit drift on VPS requires remediation. |
| 5 — VPS Deployment | PASS | Bounded one-shot deployment proven; service is sole collector. |
| 6 — Operational Activation | UNDEFINED | Not yet assessed — blocked on Gates 2/3. |

---

## Production Authority

| Component | State |
|---|---|
| Active timer | `wgu-reddit-postgres-run.timer` — enabled, active, waiting (07:00 UTC daily) |
| Active service | `wgu-reddit-postgres-run.service` — runs `python -m wgu_reddit_analyzer.daily.daily_update` |
| Storage backend | PostgreSQL (`WGU_REDDIT_STORAGE_BACKEND=postgres`) |
| Disabled legacy | `wgu-reddit-shadow-run.timer` — disabled, inactive (SQLite rollback) |
| Mac launchd | Disabled — not loaded |
| Host | `ih-market-vps` (Hetzner CX23, Ubuntu 24.04) |
| Runtime user | `scraper` |
| Working directory | `/home/scraper/apps/wgu-reddit` |
| Environment files | `/home/scraper/config/wgu-reddit.env`, `/home/scraper/config/wgu-reddit-pg.env` |

---

## Applicable Standards Matrix

| Standard | Applicability | Compliance | Notes |
|---|---|---|---|
| Git workflow | REQUIRED | BLOCKED | Credential-bearing history prevents standard Git workflow. Clean publication requires history remediation. |
| Public/private boundary | REQUIRED | PASS WITH CONDITION | VPS secrets externalized in config files. Local history contains credentials — publication blocked until strategy approved. |
| Runtime logging | REQUIRED | PASS | systemd journal captures service output. No evidence gap identified. |
| LLM tenets | NOT YET ASSESSED | UNDEFINED | This repo includes LLM stages; LLM tenets applicability has not been evaluated. |
| PostgreSQL naming | REQUIRED | PASS | Database, schemas, roles follow conventions. |
| Backup/restore | REQUIRED | BLOCKED | VPS backup unit references wrong script (`backup_reddit_ops.sh` instead of `backup_reddit_ops_pg.sh`). Fresh dump/checksum/manifest/restore not proven. |
| Systemd naming | REQUIRED | PASS WITH CONDITION | Units exist in repo but VPS-installed backup unit has drifted from source. |
| Health contract | REQUIRED | PASS | Health tooling exists (`tools/check_reddit_ops_pg_health.py`); deployed revision tracking remains open. |
| Repository control model | REQUIRED | PASS | This file and `RELEASE_GATES.md` are current authority. |
| Data lifecycle | REQUIRED | NOT YET ASSESSED | Retention, archive, and growth thresholds not documented. |

---

## Accepted Deviations

| Deviation | Justification |
|-----------|---------------|
| Deployed via SCP, not clean Git clone | Git publication blocked by credential history. Deployment path is documented and drift-detectable via SHA/sha256sum comparison. |
| No `AGENTS.md` in producer repo | Agent interaction is expected through ivy-control-vps; producer repo does not host agents directly. |

---

## Deployment Status

| Item | Status |
|------|--------|
| Approved SHA (local) | `7047400` — approved-partial fix commit. Not a canonical published SHA. |
| Deployment path | Manual `scp` from Mac to VPS (Git publication blocked — secrets in early commit history). |
| Drift detection | Checksum comparison via `sha256sum` / `git rev-parse HEAD`. |
| Last deployment | 2026-07-09 — approved-partial exit semantics fix + backup scripts. |

**Note:** The approved SHA `7047400` is a local commit anchoring an approved-partial fix, not a canonical published SHA. Publication to GitHub remains blocked. These are separate concerns — the local SHA tracks deployment, not publication.

---

## Database

| Item | Status |
|------|--------|
| Migrations applied | `0001` through `0006` |
| Role model | `owner`, `migrator`, `writer`, `reader`, `monitor`, `backup` |
| Health tooling | `tools/check_reddit_ops_pg_health.py` |
| Backup | Automated source exists and has been tested. VPS backup unit references wrong script — remediation required. |
| Restore drill | Completed with conditions — isolated restore validated row counts; full role-owner restore remains a later hardening item. |
| SQLite rollback | Preserved at `/home/scraper/data/wgu-reddit/WGU-Reddit.db`. |

---

## Process Exit Semantics

| Exit | Systemd result | Status |
|------|----------------|--------|
| `success` (0) | success | ✅ Implemented |
| `approved partial` (0) | success | ✅ Implemented (2026-07-09) — all errors match known inaccessible set |
| `unexpected partial` (1) | failed | ✅ Correct — unexpected errors still produce failure |
| `cancelled` (1) | failed | ✅ Acceptable — cancellation is externally initiated |
| `failed` (1) | failed | ✅ Correct — unexpected errors produce failure |

---

## Known Inaccessible Targets

The following subreddits in `data/wgu_subreddits.txt` are expected to return 403 or 404:
- `WGUBusinessManagement` (404)
- `WGU_BSIT` (403)
- `WGU_BSSE` (404)
- `WguTutorReddit` (404)

These are treated as approved partial results. A `partial` run with only expected errors is operationally acceptable and now exits successfully. See `STABILIZATION.md` gate 1.

---

## Current Blocker

The installed VPS backup unit `wgu-reddit-backup.service` references the non-existent script `backup_reddit_ops.sh`. The correct script is `backup_reddit_ops_pg.sh`. The unit file in the repository is already correct, but the VPS copy has drifted. Fresh backup/checksum/manifest/restore cannot be proven until the unit is remediated via SCP.

---

## Next Authorized Phase

1. Strong Codex deploys corrected backup unit to VPS, runs fresh dump/checksum/manifest/isolated restore.
2. OpenCode prepares monitor-role canonicality query design and archive-continuity report.
3. Buddy approves clean Git publication strategy (history remediation or replacement repo).
4. After publication unblocked: exact-SHA deployment, drift detection, reboot recovery proof.
5. After backup/restore and canonicality proven: Buddy decides legacy fallback retirement.

---

## Hermes Scope

Hermes may perform read-only inspection: timer/service status, backup age, deployed SHA drift, PostgreSQL connectivity, health run freshness. Hermes must not install units, start services, modify timers, mutate databases, or deploy code.

### Stop conditions

Abort and escalate on: service/timer not found or inactive, backup unit `ExecStart` mismatch, deployed SHA cannot be determined, disk >85%, backup dump missing or zero-byte, restore validation failure, unexplained data gaps, duplicate writer evidence, credential or secret exposure in logs.

---

## Private Evidence

Detailed reports, commands, and agent logs are stored under `_internal/` in the ivy-control-vps repository:
- `_internal/outbox/` — all cutover, frontier-fix, and closeout reports
- `_internal/logs/agents/2026-07-08/` — agent execution logs
