# Reddit Ops — Repository Control

**Purpose:** Active governance authority for Reddit Ops (WGU-Reddit PostgreSQL collector).
**Canonical remote:** `github.com/wguDataNinja/WGU-Reddit-Feedback-Analyzer.git`
**Default branch:** main
**Approved production SHA:** `7047400`
**VPS path:** /home/scraper/apps/wgu-reddit
**Lifecycle state:** `production-stabilizing`

---

## Production Authority

| Component | State |
|---|---|
| Active timer | wgu-reddit-postgres-run.timer — enabled, active, waiting (07:00 UTC daily) |
| Active service | wgu-reddit-postgres-run.service |
| Runtime host | ih-market-vps (Hetzner CX23, Ubuntu 24.04) |
| Runtime user | scraper |
| Storage backend | PostgreSQL (WGU_REDDIT_STORAGE_BACKEND=postgres) |
| Health tooling | tools/check_reddit_ops_pg_health.py |
| Backup | Automated source exists and has been tested. |

---

## Deployment Status

| Item | Status |
|---|---|
| Deployed SHA | 7047400 — local WGU-Reddit commit. Pending clean Git publication because local history contains credential-bearing commit e4acae0. |
| Drift detection | Checksum comparison via sha256sum / git rev-parse HEAD |
