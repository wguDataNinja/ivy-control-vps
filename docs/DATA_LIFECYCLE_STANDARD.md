# Data Lifecycle Standard

**Status:** Current authority — promotes principles from historical `ivy-control/vps/` material.
**Purpose:** Portfolio-wide data-lifecycle principles. Repository-specific retention windows are set in each repo's `CONTROL.md` or `docs/retention.md`.

---

## Core principle

**Maintain the smallest persistent footprint that satisfies current operational, audit, recovery, and legal requirements.**

Every data class must have a documented retention window, a pruning mechanism, and a defined archive or deletion path. No data is retained indefinitely by default.

---

## Data classes

| Class | Definition | Examples | Backup treatment |
|-------|-----------|----------|-----------------|
| **Canonical source** | Authoritative origin data. Irreplaceable. | Source files, raw API responses, original database before transformation. | Always backed up. Immutable or bounded retention. |
| **Derived operational** | Queryable processed data built from canonical source. Regenerable. | PostgreSQL hydrated tables, aggregated views, materialized caches. | Backed up but regenerable from canonical source. |
| **Product / export** | Published artifacts consumed by downstream tools or UI. | JSON exports, static site data, product price files. | Managed by version control or bounded archive. |
| **Cached / staging** | Temporary working data, intermediate pipeline state. Disposable. | Normalized snapshots, staging tables, temp files. | Not backed up. Pruned after processing completes. |
| **Audit trail** | Immutable record of operations. | Prune archive logs, collection run metrics, migration history. | Included in DB dump. Retained per project policy. |
| **Health** | Operational state used for monitoring. | Health run records, workflow status. | Included in DB dump. Retention bounded per project. |
| **Backup** | Point-in-time recovery artifacts. | PostgreSQL dumps, checksums, manifests. | Separate retention from application data. Never stored inside a working tree. |
| **Disposable / ephemeral** | Runtime caches, logs, temporary artifacts. | Browser caches, .venv, __pycache__, systemd logs. | Not backed up. Pruneable at any time. |

### Git boundary on data classes

| Class | In Git? | Rule |
|-------|---------|------|
| Canonical source | Never | Raw HTML, PDF, screenshots, DB dumps, large JSONL history. Stay on VPS or Mac with bounded retention. |
| Derived operational | Never | Production database state, intermediate pipeline outputs. PostgreSQL holds current state; Git holds migrations. |
| Product / export | May be | Small deterministic exports (<1 MB), manifests, test fixtures (<100 KB), schema/migration files, `.env.example`. |
| Cached / staging | Never | Working temp files, normalized snapshots, staging tables. Pruned after processing. |
| Audit trail | Schema only | Migration version tables, prune logs. Schema is committed; data stays in DB. |
| Health | Schema only | Health table definitions committed. Row data stays in DB or exempted JSON export. |
| Backup | Never | `.dump`, `.dump.gz`, `.sha256` files. Separate retention from application data. Never inside a working tree. |
| Disposable / ephemeral | Never | `.venv`, `__pycache__`, `node_modules/`, browser caches, systemd logs. |

## Restore-proof requirements

Every project with a database must demonstrate a working restore before any real-data operation or destructive change:

1. Create a restore test database: `{db}_restore_verify_{timestamp}`
2. Restore the latest baseline dump using `pg_restore`
3. Run the project's `db/validation/999_full_validation.sql`
4. Verify schema ownership, table ownership, and row counts against documented expected values
5. Drop the restore test database
6. Record evidence in the project's durable activity log

The restore drill confirms that the backup format, transport, and procedure all produce a usable database. A failing restore drill blocks cutover, destructive work, and authority transfer.

Monthly restore verification is recommended for any continuously running project.

## Backup versus application retention

Backup retention is independent of application-history retention:

- **Backups** serve point-in-time recovery — kept as long as recovery must be possible
- **Application history** serves UI queries, audits, and regeneration — kept as long as users or downstream consumers need it

A project may prune old application history while maintaining the ability to restore from backup. A project may expire old backups while retaining application history for query.

Backups are never pruned to free application storage. Application history is never removed from backup scope to reduce backup size without documented approval.

## Raw artifact and export Git boundaries

The following NEVER enter Git history:
- Raw HTML, PDF, screenshots, browser traces
- Large JSONL history files (>1 MB)
- Database dumps of any kind
- Mutable production data
- Working intermediate pipeline outputs
- Caches, virtual environments, compiled dependencies
- Runtime logs

The following MAY be in Git:
- Small deterministic exports (product JSON, manifests under 1 MB)
- Safe test fixtures (<100 KB representative samples)
- Schemas, migrations, model definitions
- Generated manifests and run summaries
- Configuration files without secrets
- Environment variable examples (`.env.example`)

## Deletion prerequisites

No production data file or storage artifact may be deleted without:
1. **Backup/restore verification** — a recent successful restore drill exists
2. **Destructive Operation Gate approval** — Buddy approved the exact target set
3. **Explicit target list** — every file, directory, table row, or storage path to be deleted
4. **Dry-run verification** — the deletion operation ran in dry-run mode and reported only the intended targets
5. **Buddy approval for each operation** — blanket deletion authority is not granted

## Archive verification

Data transferred to archive status (cold storage, long-term retention, or removal from active query path) must be:
1. **Checksum-verified** — SHA-256 of the archive artifact matches the source
2. **Manifest-recorded** — archive timestamp, source path, checksum, retention window, and restore procedure are documented
3. **Restore-tested** — at least one restore from archive confirmed functional before the active copy is removed
4. **Retention-labeled** — archive is labeled with its planned deletion or review date

Archives without a documented retention date are not truly archived — they are deferred clutter.

## Backup retention vs application retention

Canonical source data SHOULD flow through a bounded raw phase into a derived/aggregated phase, after which the raw copy MAY be pruned once parity is proven:

```
Canonical source (file/API)
  → raw snapshot (bounded retention)
  → derived operational DB (current state)
  → product/export (published artifacts)
  → archive (cold storage, if required)
```

Data SHOULD NOT exist in both raw and derived form indefinitely unless the raw copy serves a distinct audit or re-derivation purpose.

---

## Retention principles

1. **Repository-specific:** Each repo defines its own retention windows. The portfolio standard provides defaults and minimums.
2. **Bounded by default:** Every data class must have a maximum retention window. "Indefinite" requires documented approval.
3. **Recovery-first:** Backup retention is independent of application-history retention. Backups serve point-in-time recovery; application retention serves UI queries and audits.
4. **Regenerable data may be pruned:** Data that can be re-derived from canonical source does not need extended retention.
5. **Pruning must be provable:** Pruning operations must produce a dry-run report, execute against confirmed targets, and log the outcome.
6. **Evidence before deletion:** No destructive pruning without a verified backup/restore drill, Destructive Operation Gate approval, explicit target list, dry-run verification, and Buddy approval.

---

## Growth measurement

Every managed repository must record at minimum:

- current database size
- current file artifact size (data directory, exports)
- estimated daily/weekly growth rate
- growth trend (increasing, stable, decreasing)

These metrics SHOULD be collected by the health export and recorded in the health schema.

---

## Disk thresholds

These portfolio-wide thresholds apply to all hosts (VPS, Mac). Repository-specific thresholds MAY be stricter.

| Level | Root filesystem used | Action |
|-------|---------------------|--------|
| Nominal | < 75% | Normal operation. |
| Warning | 75–85% | Investigate growth sources. Schedule pruning review. |
| Critical | 85–90% or < 5 GB free | No new deployments. Immediate pruning or growth mitigation required. |
| Emergency | > 90% or < 1 GB free | Stop all non-essential writes. Emergency pruning or扩容. |

---

## Failure behavior near thresholds

When approaching or exceeding the critical threshold:

1. **Deployment stop:** `docs/REPOSITORY_CONTROL_MODEL.md` stop conditions apply — deployments blocked.
2. **Ingestion backpressure:** Collection services SHOULD continue if they produce bounded files, but SHOULD NOT accumulate unbounded data.
3. **Health alert:** The health export MUST report disk/volume usage as degraded or failed.
4. **Immutable protection:** Immutable retention classes (cutover baselines, pre-migration snapshots) are never pruned to free space.

---

## Backup retention vs application retention

| Retention type | Purpose | Window | Location |
|----------------|---------|--------|----------|
| Application (raw snapshots) | UI queries, product regeneration | Per repo policy (commonly 14–30 days) | VPS `data/` |
| Application (derived DB) | Queryable operational state | Current state + archive per migration | PostgreSQL |
| Application (product) | Published consumer artifacts | Bounded per repo | Git + web |
| Backup (daily dump) | Point-in-time recovery | 7 daily on VPS, 14→7 on Mac | `backups/postgres/` |
| Backup (weekly dump) | Weekly checkpoint | 4 on VPS, 4 on Mac | `backups/postgres/` |
| Backup (immutable) | Pre-migration, pre-cutover | Never pruned without Destructive Operation Gate | `backups/postgres/` |
| Health | Operational monitoring | Per project (typically trim oldest on insert) | PostgreSQL health schema |
| Logs (runtime) | Debugging and incident analysis | Rotated by size/time per service | System journal, `logs/` |
| Caches (browser, venv) | Acceleration | Pruneable at any time | Filesystem |

---

## Health metrics required

Every health export MUST include at minimum:

- database size
- disk usage for data/export directories
- growth rate (24h, 7d) where measurable
- whether any data class is approaching its retention boundary
- prune/archive status (last run, records affected)

---

## Applicability

This standard applies to all managed repositories. Repository-specific retention policies MAY deviate with documented approval in the repo CONTROL.md.
