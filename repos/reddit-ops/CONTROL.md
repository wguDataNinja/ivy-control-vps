# Reddit Ops — Repository Control

**Purpose:** Active governance authority for Reddit Ops (WGU-Reddit PostgreSQL collector).
**Managed service:** Reddit Ops — daily WGU subreddit collection and analysis
**Producer repository:** `/Users/buddy/Desktop/WGU-Reddit` — `github.com/wguDataNinja/WGU-Reddit-Feedback-Analyzer.git`
**Production database:** `reddit_ops` on VPS PostgreSQL 16
**Schemas:** `reddit_core` (shared canonical data), `wgu_reddit` (WGU project state), `bsda_courses` (future project schema)
**Lifecycle state:** `production-stabilizing` — production authority has moved, but scheduled-run, backup, restore, monitoring, and governance gates remain open.
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
| Deployed SHA | Not tracked — VPS checkout is not a Git checkout |
| Deployment path | Manual `scp` from Mac to VPS |
| Drift detection | Not implemented |
| Fresh-clone reproducible | No — untracked runtime files exist |
| Last deployment | 2026-07-08 — frontier fix (`reddit_ops_pg.py`) |

---

## Database

| Item | Status |
|------|--------|
| Migrations applied | `0001` through `0006` |
| Role model | `owner`, `migrator`, `writer`, `reader`, `monitor`, `backup` |
| Health tooling | `tools/check_reddit_ops_pg_health.py` |
| Backup | Not automated |
| Restore drill | Not completed |
| SQLite rollback | Preserved at `/home/scraper/data/wgu-reddit/WGU-Reddit.db` |

---

## Process Exit Semantics

| Exit | systemd Result | Status |
|------|----------------|--------|
| `success` (0) | success | ✅ Implemented |
| `partial` (1) | failed | ⚠️ Open — accepted partial runs (known 403/404 subreddits) produce systemd failure |
| `cancelled` (1) | failed | ✅ Acceptable — cancellation is externally initiated |
| `failed` (1) | failed | ✅ Correct — unexpected errors should produce failure |

---

## Known Inaccessible Targets

The following subreddits in `data/wgu_subreddits.txt` are expected to return 403 or 404:
- `WGUBusinessManagement` (404)
- `WGU_BSIT` (403)
- `WGU_BSSE` (404)
- `WguTutorReddit` (404)

These are treated as approved partial results. A `partial` run with only expected errors is operationally acceptable but currently produces systemd failure. See `STABILIZATION.md` gate 1.

---

## Unresolved Gates

See `STABILIZATION.md` for the complete gate list. Key open items:
1. Approved partial produces systemd success
2. Three consecutive natural scheduled runs
3. Automated PostgreSQL backups
4. Full restore drill
5. Reboot recovery
6. Monitoring thresholds
7. Deployed SHA tracked
8. Drift detection

---

## Private Evidence

Detailed reports, commands, and agent logs are stored under `_internal/` in the ivy-control-vps repository:
- `_internal/outbox/` — all cutover, frontier-fix, and closeout reports
- `_internal/logs/agents/2026-07-08/` — agent execution logs
