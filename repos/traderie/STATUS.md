# Traderie — VPS Status

**Purpose:** Single source of current operational state for ivy-control agents.
**Canonical repo:** `github.com/buddyowens/traderie`
**Local path:** `/Users/buddy/projects/traderie`
**Updated:** 2026-07-06

---

## Phase

| Phase | Status |
|-------|--------|
| P0 Discovery | ✅ Complete |
| P1 Roadmap | ✅ Complete |
| P2 GitHub readiness | ⏳ Pre-push cleanup in progress (dev/, captures/, stale CSVs, README, LICENSE) |
| P3 Shared infra (PG) | ⏳ Schema migrated, PG adapter still in-memory |
| P4 VPS deployment | ❌ Not started |
| P5 Mac fallback | ❌ Not started |
| P6 Monitoring | ❌ Not started |

## Gates

| Gate | Status |
|------|--------|
| GitHub Push | 🔲 Ready for Buddy approval after cleanup |
| Database Authority | ✅ Passed (Mac PG16, traderie DB, 6 roles) |
| Real-Data Pilot | 🔲 Blocked on PG adapter + Buddy Gate approval |
| VPS Capacity | ❌ Failed — current host 89% disk |
| Scheduler | 🔲 Not yet applicable |
| PostgreSQL Cutover | 🔲 Not yet applicable |
| Backup/Restore | ✅ Passed (clean baseline + restore drill) |
| Destructive Operation | 🔲 Not yet applicable |

## Current state

- **Collector:** 4x daily via launchd, ~22K rows/day, ~12 MB/day
- **Database:** `traderie` on Mac PG16, 3 schemas, 9 migrations, 0 real data rows
- **Adapter:** In-memory dry store — cannot write to PostgreSQL
- **Pilot candidate:** 25 records, pc_sc_l, digest `df82ac34e7ccb16688963a1100d30bfc1eeeb8223d00b2243c75146e88bf794f`
- **Queue (IMPLEMENTATION_PROGRAM.md):** TRD-002 BLOCKED, TRD-005 BLOCKED, TRD-007 PARTIAL
- **Tests:** 46/46 pass

## Known blockers

1. `scripts/traderie_pg_adapter.py` is in-memory only — real PG writer needed first
2. VPS `ih-market-vps` at 89% disk — PostgreSQL capacity Gate failed
3. Three VPS wrapper scripts missing (run_traderie_snapshot.sh, _backup.sh, _validate.sh)

## Next planned work

Strong Codex implementation: real PG adapter → collection metrics → aggregates → prune → health export → pilot.
