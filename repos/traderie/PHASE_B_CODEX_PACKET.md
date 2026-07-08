# Traderie Phase B — Strong Codex Packet

**Prerequisite:** VPS Capacity Gate must pass before any deployment work.
**Phase A status:** Complete — 17 migrations, 57 tests, pilot loaded, GitHub published, fresh-clone proven, PG adapter real (env-gated).
**Current VPS:** 88% disk (4.4 GB free, refreshed 2026-07-07T23:09Z), no PostgreSQL, no traderie checkout, no passwordless sudo.

---

## Scope

Bounded VPS capacity remediation and one-shot deployment proof. Stop before continuous collection or production authority transfer.

## Hard boundaries

- No enabling services or timers
- No continuous collection
- No production cutover
- No changing database authority
- No destructive chat archive cleanup without separate explicit approval
- No deletion of files without current process/ownership checks

## Required preflight (read-only)

1. Confirm current VPS state (df -h, free -h, systemctl list-timers, systemctl list-units --failed, ps aux --sort=-%mem)
2. Confirm `~/.ssh/authorized_keys` and user identities
3. Confirm current app checkouts under `/home/scraper/apps/`
4. Check for any running processes that depend on files being cleaned up
5. Check `/home/scraper/mcstories-search` — is it still actively running or safe to reclaim?

## VPS cleanup (only with Buddy approval per target)

### Approved first-pass cleanup (proven disposable and inactive)

| Target | Path | Size | Command |
|--------|------|------|---------|
| Camoufox cache | `/home/scraper/.cache/camoufox/` | 1.3 GB | `rm -rf /home/scraper/.cache/camoufox/*` |
| Pip cache | `/home/scraper/.cache/pip` | 80 MB | `rm -rf /home/scraper/.cache/pip` |
| Downloads | `/home/scraper/Downloads/*` | 112 KB | `rm -f /home/scraper/Downloads/*` |
| Temp screenshots | `/tmp/*.png` | ~3 MB | `rm -f /tmp/*.png` |

**Subtotal**: ~1.4 GB reclaimable. Expected post-cleanup: ~81% used.

### Not yet approved (deferred)

| Target | Path | Size | Reason |
|--------|------|------|--------|
| Chrome cache | `/home/scraper/.cache/google-chrome/` | 706 MB | Chrome actively running (28 processes); defer to separate stop-clean-restart procedure |
| Camoufox venv | `/home/scraper/camoufox-env/` | 248 MB | Verify pinned deps and recreation procedure |
| Camoufox profiles | `/home/scraper/camoufox-profiles/` | 122 MB | Contains browser state; verify workflow dependency |
| mcstories-search | `/home/scraper/mcstories-search` | 573 MB | PROTECTED — active crawl |
| Private chat archive | `/home/scraper/data/private/chat` | 13 GB | PROTECTED — migration input |

### Requires sudo (currently unavailable — document for host resize planning)

| Target | Expected recovery |
|--------|-------------------|
| `sudo apt autoremove --purge` (old kernels) | ~500 MB – 1 GB |
| `sudo journalctl --vacuum-size=500M` | variable |
| `sudo apt-get clean` | variable |

## Deployment (after VPS capacity passes)

1. Fresh pre-deployment backup and restore drill on Mac (`pg_dump` of traderie, restore to temp DB, validate, evidence in LOG.md)
2. Clone traderie to VPS: `git clone git@github.com:wguDataNinja/d2-market-helper.git /home/scraper/apps/traderie`
3. Checkout exact SHA `b3b70a0` (or later reviewed SHA)
4. Create `.env` from `/home/scraper/config/traderie.env` (secrets outside repo)
5. Create `.venv` and `pip install -r requirements.txt`
6. Set `TRADERIE_PG_URL` for VPS PostgreSQL access (`localhost:5432`) — VPS PG is operational authority; Mac is archive/backup/restore authority
7. Run bounded manual collection (`scripts/run_traderie_snapshot.sh`)
8. Run validation (`scripts/run_traderie_validate.sh`)
9. Run health export (`scripts/traderie_health_export.py`)
10. Run backup (`scripts/run_traderie_backup.sh`)
11. Verify backup checksum and store manifest
12. Record deployed SHA, validation output, health output, and backup evidence in LOG.md

## One-shot smoke and rollback proof

1. Run one full snapshot cycle
2. Confirm new records appear in `app.completed_trades` (via VPS PG)
3. Confirm health export succeeds
4. Run rollback: delete the test-run records by observation_key set
5. Confirm row counts return to pre-test baseline
6. Re-run snapshot and confirm stable re-insertion
7. Run backup
8. Measure disk growth after one full cycle: `du -sh /home/scraper/data/traderie/`

## Stop conditions

- VPS disk >85% after cleanup → stop, require resize
- No passwordless sudo → cannot deploy dependency packages → stop
- PG connectivity fails → stop
- Snapshot script fails → stop
- Validation fails → stop
- Rollback cannot prove row-count return → stop
- Backup or checksum fails → stop
- Health export fails → stop
- VPS checkout contains dirty files → stop
- Any running process depends on a file targeted for cleanup → stop, report

## Completion criteria

- VPS disk <80% or documented reason why cleanup is insufficient
- traderie checked out at exact reviewed SHA
- One successful snapshot + validation + health + backup cycle proven
- Rollback proven (row counts return to baseline)
- Disk-growth measured and documented
- Deployed SHA, validation evidence, health evidence, backup evidence, and growth measurement recorded in LOG.md
- Next step recorded: enable timer or wait for Buddy decision

## Evidence required

- Pre/post cleanup: `df -h`, `du -sh /home/scraper/apps/traderie/data/`
- Clone SHA: `git rev-parse HEAD`
- Test run: `pytest tests/ -q`
- Snapshot: row counts from `app.completed_trades`, `app.price_entries`
- Health: `python3 scripts/traderie_health_export.py --json`
- Backup: dump path, SHA-256, manifest
- Rollback: pre/post row counts for deleted observation_key set
- Disk growth: one clean cycle delta
