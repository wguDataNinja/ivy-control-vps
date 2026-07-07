# Traderie — VPS Status

**Purpose:** Single source of current operational state for ivy-control agents.
**Canonical repo:** `github.com/wguDataNinja/d2-market-helper` (public)
**Local path:** `/Users/buddy/projects/traderie`
**Updated:** 2026-07-07

---

## Phase

| Phase | Status |
|-------|--------|
| P0 Discovery | ✅ Complete |
| P1 Roadmap | ✅ Complete |
| P2 GitHub readiness | ✅ Complete — pushed to public GitHub, fresh-clone proof passed |
| P3 Shared infra (PG) | ✅ Complete — 17 migrations, 25-row pilot loaded, 57 tests pass |
| P4 VPS deployment | ❌ Not started (blocked on VPS capacity) |
| P5 Mac fallback | ❌ Not started |
| P6 Monitoring | ❌ Not started |

## Gates

| Gate | Status |
|------|--------|
| GitHub Push | ✅ Passed — public repo at `github.com/wguDataNinja/d2-market-helper` |
| Database Authority | ✅ Passed (Mac PG16, traderie DB, 6 roles) |
| Real-Data Pilot | ✅ Passed — 25 records (pc_sc_l), digest verified, rollback proven |
| VPS Capacity | ❌ Failed — current host 91% disk (3.3 GB free, 2026-07-07) |
| Backup/Restore | ✅ Passed (clean baseline + restore drill + pre-push backup) |
| Scheduler | 🔲 Not yet applicable |
| PostgreSQL Cutover | 🔲 Not yet applicable |
| Destructive Operation | 🔲 Not yet applicable |

## Current state

- **Collector:** 4x daily via launchd, ~22K rows/day, ~12 MB/day
- **Database:** `traderie` on Mac PG16, 3 schemas (app/health/archive), 17 migrations, 9.7 MB
- **Adapter:** Real PostgreSQL adapter (`scripts/traderie_pg_adapter.py`) — env-gated (`TRADERIE_PG_ADAPTER_ENABLED`), disabled by default (fallback to in-memory dry store for tests)
- **Pilot completed:** 25 records loaded (pc_sc_l), rollback/parity proven, pre-push backup at `/Users/buddy/projects/backups/postgres/traderie/traderie_pre_push_20260707T083001Z.dump`
- **App row counts:** segments 4, completed_trades 25, price_entries 37, prune_audit 50, collection_run_metrics 1, segment_aggregates 2, rune_registry 33, prune_archive_audit 25
- **Tests:** 57/57 pass
- **VPS wrappers:** All 3 scripts exist (`run_traderie_snapshot.sh`, `run_traderie_backup.sh`, `run_traderie_validate.sh`)
- **GitHub CI:** GitHub Actions workflow with syntax checks, tests, safety gates
- **Health export:** `scripts/traderie_health_export.py` exists, wired with bounded insert/delete proof

## Known blockers

1. VPS `ih-market-vps` at 91% disk (3.3 GB free) — PostgreSQL capacity Gate failed
2. No passwordless sudo on VPS — blocks non-interactive provisioning
3. VPS has no PostgreSQL installed and no traderie checkout

## Next planned work

Phase B: VPS capacity remediation either via cleanup or host resize, then deployment proof by exact commit SHA.
