# Reddit Ops — Repository Control

**Purpose:** Active governance authority for Reddit Ops (WGU-Reddit PostgreSQL collector).
**Managed service:** Reddit Ops — daily WGU subreddit collection and analysis
**Producer repository:** `/Users/buddy/Desktop/WGU-Reddit` — `github.com/wguDataNinja/WGU-Reddit-Feedback-Analyzer.git`
**Production database:** `reddit_ops` on VPS PostgreSQL 16
**Schemas:** `reddit_core` (shared canonical data), `wgu_reddit` (WGU project state), `bsda_courses` (future project schema)
**Lifecycle state:** `production-stabilizing` — production authority is established; Git publication, exact-SHA deployment, drift tracking, and reboot recovery remain open. Most backup/restore gates have passed.
**Detailed gate evidence:** `repos/reddit-ops/RELEASE_GATES.md`
**Cutover history:** `repos/reddit-ops/CUTOVER_HISTORY.md`
**Stabilization checklist:** `repos/reddit-ops/STABILIZATION.md`
**Runbook:** `repos/reddit-ops/RUNBOOK.md`

---

## Production Authority

| Component | State |
|-----------|-------|
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

## Deployment Status

| Item | Status |
|------|--------|
| Deployed SHA | `7047400` — local WGU-Reddit commit (approved-partial fix). Pending clean Git publication because local history contains credential-bearing commit `e4acae0`. |
| Deployment path | Manual `scp` from Mac to VPS (Git publication blocked — secrets in early commit history) |
| Drift detection | Checksum comparison via `sha256sum` / `git rev-parse HEAD` |
| Last deployment | 2026-07-09 — approved-partial exit semantics fix + backup scripts |

---

## Database

| Item | Status |
|------|--------|
| Migrations applied | `0001` through `0006` |
| Role model | `owner`, `migrator`, `writer`, `reader`, `monitor`, `backup` |
| Health tooling | `tools/check_reddit_ops_pg_health.py` |
| Backup | Automated source exists and has been tested; installed unit remediation/publication remains required where the VPS unit references the wrong script name. |
| Restore drill | Completed with conditions — isolated restore validated row counts; full role-owner restore remains a later hardening item. |
| SQLite rollback | Preserved at `/home/scraper/data/wgu-reddit/WGU-Reddit.db` |

---

## Process Exit Semantics

| Exit | systemd Result | Status |
|------|----------------|--------|
| `success` (0) | success | ✅ Implemented |
| `approved partial` (0) | success | ✅ Implemented (2026-07-09) — all errors match known inaccessible set |
| `unexpected partial` (1) | failed | ✅ Correct — unexpected errors still produce failure |
| `cancelled` (1) | failed | ✅ Acceptable — cancellation is externally initiated |
| `failed` (1) | failed | ✅ Correct — unexpected errors should produce failure |

---

## Known Inaccessible Targets

The following subreddits in `data/wgu_subreddits.txt` are expected to return 403 or 404:
- `WGUBusinessManagement` (404)
- `WGU_BSIT` (403)
- `WGU_BSSE` (404)
- `WguTutorReddit` (404)

These are treated as approved partial results. A `partial` run with only expected errors is operationally acceptable and now exits successfully. See `STABILIZATION.md` gate 1.

---

## Unresolved Gates

See `STABILIZATION.md` for the complete gate list. Key open items:
1. Clean Git publication excluding credential-bearing history
2. Exact-SHA deployment and deployed revision tracked in health
3. Backup unit remediation from reviewed source where installed unit drift exists
4. Reboot recovery and post-reboot timer proof
5. Monitoring thresholds and automated alerting
6. Drift detection

---

## Private Evidence

Detailed reports, commands, and agent logs are stored under `_internal/` in the ivy-control-vps repository:
- `_internal/outbox/` — all cutover, frontier-fix, and closeout reports
- `_internal/logs/agents/2026-07-08/` — agent execution logs
