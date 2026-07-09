# Reddit Ops — Operational Runbook

**Authority:** ivy-control-vps
**Producer repository:** WGU-Reddit
**Production database:** `reddit_ops` on VPS PostgreSQL

---

## Checking PostgreSQL Readiness

```bash
ssh ih-market-vps "pg_isready; systemctl is-active postgresql"
```

Expected: `accepting connections` and `active`.

---

## Checking Timer/Service State

```bash
ssh ih-market-vps "systemctl --user list-timers 'wgu-reddit*' --all --no-pager"
ssh ih-market-vps "systemctl --user show wgu-reddit-postgres-run.timer -p Id -p UnitFileState -p ActiveState -p SubState --no-pager"
ssh ih-market-vps "systemctl --user show wgu-reddit-postgres-run.service -p Id -p ActiveState -p SubState -p Result --no-pager"
```

---

## Checking Latest Ingestion Run

```bash
ssh ih-market-vps '
set -a
. /home/scraper/config/wgu-reddit-pg.env
set +a
psql "$REDDIT_OPS_PG_MONITOR_URL" -X -c "
SELECT ingestion_run_id, status, current_target,
       targets_completed || '\''/'\'' || targets_total as progress,
       posts_seen, posts_inserted, posts_updated, error_count,
       started_at, completed_at,
       EXTRACT(EPOCH FROM COALESCE(completed_at, now()) - started_at)::int as elapsed_sec
FROM reddit_core.ingestion_runs
ORDER BY ingestion_run_id DESC LIMIT 3;
"'
```

---

## Checking Heartbeat/Progress

```bash
ssh ih-market-vps '
set -a
. /home/scraper/config/wgu-reddit-pg.env
set +a
psql "$REDDIT_OPS_PG_MONITOR_URL" -X -c "
SELECT ingestion_run_id, status, current_stage, current_target,
       targets_completed, targets_total,
       heartbeat_at, now() - heartbeat_at as heartbeat_age
FROM reddit_core.ingestion_runs
WHERE status = '\''running'\''
ORDER BY ingestion_run_id DESC;
"'
```

---

## Validating Inaccessible Target Set

Expected 403/404 subreddits:
- `WGUBusinessManagement` (404)
- `WGU_BSIT` (403)
- `WGU_BSSE` (404)
- `WguTutorReddit` (404)

Check last run errors:

```bash
ssh ih-market-vps '
set -a
. /home/scraper/config/wgu-reddit-pg.env
set +a
psql "$REDDIT_OPS_PG_MONITOR_URL" -X -c "
SELECT error_class, object_id, count(*)
FROM reddit_core.fetch_errors
WHERE ingestion_run_id = (SELECT max(ingestion_run_id) FROM reddit_core.ingestion_runs)
GROUP BY 1, 2
ORDER BY 1, 2;
"'
```

If all errors match the known set, the run is operationally successful despite `partial` status.

---

## Manual Bounded Collector Execution

```bash
ssh ih-market-vps '
cd /home/scraper/apps/wgu-reddit
export WGU_REDDIT_STORAGE_BACKEND=postgres
set -a
. /home/scraper/config/wgu-reddit.env
. /home/scraper/config/wgu-reddit-pg.env
set +a
timeout 600 .venv/bin/python -m wgu_reddit_analyzer.daily.daily_update 2>&1
'
```

Expected: full run completes in ~60-120s, all 52 targets processed, frontier non-zero.

---

## Stale-Run Recovery

Stale-run recovery runs automatically at collector startup. To verify:

```bash
ssh ih-market-vps '
set -a
. /home/scraper/config/wgu-reddit-pg.env
set +a
psql "$REDDIT_OPS_PG_MONITOR_URL" -X -c "
SELECT ingestion_run_id, status, completed_at, failure_summary
FROM reddit_core.ingestion_runs
WHERE failure_summary LIKE '\''%stale run%'\''
ORDER BY ingestion_run_id DESC;
"'
```

If stale runs exist, they were recovered automatically on the next collector start.

---

## Advisory Lock Verification

```bash
ssh ih-market-vps '
set -a
. /home/scraper/config/wgu-reddit-pg.env
set +a
psql "$REDDIT_OPS_PG_MONITOR_URL" -X -c "
SELECT locktype, pid, mode, granted
FROM pg_locks
WHERE locktype = '\''advisory'\'' AND objid = 1464428100;
"'
```

The lock ID `1464428100` corresponds to hex `0x574755_5244` ("WGURD"). If a row appears, a collector is active.

---

## Backup Creation and Validation

Not yet automated. Manual backup:

```bash
ssh ih-market-vps '
set -a
. /home/scraper/config/wgu-reddit-pg.env
set +a
pg_dump "$REDDIT_OPS_PG_BACKUP_URL" -Fc -Z 9 -f /tmp/reddit_ops_$(date -u +%Y%m%dT%H%M%SZ).dump
sha256sum /tmp/reddit_ops_*.dump
'
```

---

## Rollback to SQLite Authority

```bash
# Disable PostgreSQL timer
ssh ih-market-vps "systemctl --user disable --now wgu-reddit-postgres-run.timer"

# Enable SQLite timer
ssh ih-market-vps "systemctl --user enable --now wgu-reddit-shadow-run.timer"

# Verify
ssh ih-market-vps "systemctl --user list-timers 'wgu-reddit*' --no-pager"
```

Expected: only `wgu-reddit-shadow-run.timer` shown. PostgreSQL timer is disabled.

---

## Drift Detection

Not yet automated. Manual check:

```bash
# Check if VPS is a Git checkout
ssh ih-market-vps "cd /home/scraper/apps/wgu-reddit && git rev-parse HEAD 2>/dev/null || echo 'NOT A GIT CHECKOUT'"

# Compare deployed file checksum
ssh ih-market-vps "sha256sum /home/scraper/apps/wgu-reddit/src/wgu_reddit_analyzer/storage/reddit_ops_pg.py"
```

---
