# Traderie — Repository Control

**Purpose:** Active governance authority for Traderie within IvyControlVPS.
**Canonical remote:** `github.com/wguDataNinja/d2-market-helper`
**Default branch:** `master`
**Approved production SHA:** `e5ebd0f6dd41bcb4e1d8a88f272be89b225cfd40`
**Local path:** /Users/buddy/projects/traderie
**VPS path:** /home/scraper/apps/traderie
**Lifecycle state:** `production-stabilizing` / `PRODUCTION_DEGRADED`

---

## Production Authority

| Component | Current state |
|---|---|
| Runtime host | Ivy VPS |
| Runtime user | scraper |
| Active scheduler | traderie-ingest-snapshot.timer enabled, active, waiting |
| Active writer | VPS systemd service path only |
| Production database | PostgreSQL database traderie on VPS |
| Health | DB-backed health.health_runs exists |
| Backup | Latest known dump: traderie_20260709T090253Z.dump |

---

## Current Blocker

The first genuine natural scheduled generation after segmented cutover partially failed on 2026-07-11 at 18:01:46 UTC. Segments `pc_sc_nl`, `pc_sc_l`, and `pc_hc_l` completed; `pc_hc_nl` reached its 480-second bound and timed out. Overall service exit was `1`.

## Next Authorized Work

Session 5 §7A Traderie production recovery:
1. Investigate the pc_hc_nl natural-run timeout.
2. Verify DB-backed and file-based health behavior.
3. Confirm or refine backup freshness policy in the repo contract.
