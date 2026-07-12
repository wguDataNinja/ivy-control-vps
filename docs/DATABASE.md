

# Database Architecture and Operations

## Purpose

This document is the current consolidated reference for database architecture, schema ownership, migrations, operations, backup and restore, retention, production topology, and the Reddit Ops migration history across the Ivy portfolio.

For now, these concerns are kept in one document to avoid fragmentation. They may be split into smaller documents later when the portfolio stabilizes.

## Documentation ownership

Use the following ownership model:

- project repositories own their schema contracts, migrations, data models, and application-facing database behavior;
- `ivy-control-vps` owns production topology, deployment, service health, backup, restore, retention, archive flow, and operational history;
- `_internal/` owns detailed execution evidence, agent reports, prompts, host-specific paths, credentials-adjacent context, and private chronology.

No secrets, passwords, private keys, or live credentials belong in this document.

## Portfolio database model

The Ivy VPS runs one PostgreSQL instance for portfolio workloads.

Projects use isolated databases and/or schemas according to their role and sharing model. The default is project isolation. Shared platform services may use multiple schemas when they support more than one repository or research program.

### Current portfolio inventory

| Service | Database | Schemas | Production authority | Archive authority | Status |
|---|---|---|---|---|---|
| Reddit Ops | `reddit_ops` | `reddit_core`, `wgu_reddit`, `bsda_courses` | VPS PostgreSQL collector | Mac archive/PostgreSQL | PostgreSQL collector cutover complete; SQLite preserved as rollback |
| Traderie | `traderie` | `app`, `archive`, `health` | VPS PostgreSQL | Mac backup/archive | Cutover complete but production-degraded pending natural-run recovery |
| Idle Hacking KB | Existing migration design | Project-isolated schema | VPS PostgreSQL planned | Mac archive | Schema exists; ingestion design pending |
| IH Market Companion | Existing migration design | Project-isolated schema | VPS PostgreSQL planned | Mac archive | Schema exists; pipeline design pending |

## Reusable PostgreSQL onboarding system

PostgreSQL onboarding is a portfolio product, not a repo-by-repo checklist. Medium agents prepare source, manifests, validation, and evidence. Strong Codex executes only the bounded privileged packet when Buddy authorizes live VPS work.

### Current privilege evidence

The current bounded workflow is supported by session evidence, not by a fully promoted platform helper:

| Fact | Evidence |
|---|---|
| Earlier onboarding required repeated interactive sudo/password participation. | `_internal/vps-inventory-and-runbook.md`; `_internal/outbox/session3/agent-5-production-unblock-dossier.md` |
| PostgreSQL admin operations later worked non-interactively through `sudo -n -u postgres` for `psql`, `createdb`, and `dropdb`. | `_internal/outbox/session3/agent-6-portfolio-vps-operations-discovery.md`; `_internal/outbox/session3/codex-7-operations-access-and-traderie-cutover.md` |
| The migration-phase sudo policy lives at `/etc/sudoers.d/ivy-migration`. | `_internal/outbox/session3/codex-7-operations-access-and-traderie-cutover.md` |
| The scoped systemd helper lives at `/usr/local/sbin/ivy-systemd-deploy`, is root-owned, logs to `/var/log/ivy-systemd-deploy.log`, and only allows listed project/actions. | `_internal/outbox/session3/codex-7-operations-access-and-traderie-cutover.md` |
| Broad sudo still requires a password. Arbitrary `systemctl`, arbitrary file install, arbitrary helper arguments, unknown projects, and shell actions were denied. | `_internal/outbox/session3/codex-7-operations-access-and-traderie-cutover.md` |
| The helper was not version-controlled and could not update its own pinned SHA through the current NOPASSWD boundary. | `_internal/outbox/session4/agent-1-traderie-cutover-unblock-audit.md` |
| Reboot is allowlisted by the migration-phase policy but remains production-affecting and requires explicit Buddy timing/authorization. | `_internal/outbox/session3/codex-7-operations-access-and-traderie-cutover.md`; `repos/reddit-ops/STABILIZATION.md` |

Until a version-controlled helper and reviewed installer exist, reuse this workflow only through an explicit Strong Codex packet that cites the exact current boundary.

### Onboarding manifest schema

Each PostgreSQL candidate must provide a private or repo-local manifest before privileged execution:

```yaml
project_slug: sjc_intel
repository:
  local_path: /Users/buddy/projects/sjc_intel
  remote: null
  branch: main
  reviewed_sha: null
database:
  name: sjc_intel
  owner_role: sjc_intel_owner
  schemas:
    - name: app
      owner_role: sjc_intel_owner
    - name: health
      owner_role: sjc_intel_owner
roles:
  owner:
    name: sjc_intel_owner
    login: false
    applies: true
  migrator:
    name: sjc_intel_migrator
    login: true
    applies: true
  writer:
    name: sjc_intel_writer
    login: true
    applies: true
  reader:
    name: sjc_intel_reader
    login: true
    applies: true
  monitor:
    name: sjc_intel_monitor
    login: true
    applies: true
  backup:
    name: sjc_intel_backup
    login: true
    applies: true
environment:
  env_example: deploy/env.example
  vps_env_path: /home/scraper/config/sjc-intel.env
  required_variables:
    - SJC_INTEL_PG_URL
    - SJC_INTEL_PG_MIGRATOR_URL
    - SJC_INTEL_HEALTH_OUTPUT
migrations:
  directory: db/migrations
  expected_count: 11
  validation_directory: db/migrations/validation
  rollback_directory: db/migrations/rollback
backup:
  command: scripts/run_sjc_intel_backup.sh
  output_root: /home/scraper/backups/postgres/sjc-intel
health:
  workflow_id: sjc_intel/daily_ingest
  producer_or_adapter: scripts/health_export.py
rollback:
  source_authority_fallback: documented in packet
  database_rollback: rollback SQL or irreversible statement
evidence:
  output_dir: _internal/outbox/session5/<packet-evidence-dir>
```

### Naming rules

- Database names use lowercase snake case and match the stable project slug unless a documented legacy exception exists.
- Role names use `{project}_owner`, `{project}_migrator`, `{project}_writer`, `{project}_reader`, `{project}_monitor`, and `{project}_backup`.
- Standard schemas are `app`, `archive`, and `health`. Additional schemas require a repository-specific reason in `CONTROL.md`.
- Temporary restore databases use `{project}_restore_<operator>_<yyyymmddhhmmss>` and must be dropped only by an approved cleanup packet after validation is recorded.
- File/export-only workloads, such as WGU Catalog when no database is needed, mark PostgreSQL roles `applies: false` and satisfy the backup/restore gate with manifest, checksum, archive, and rollback evidence instead.

### Conditional role applicability

| Role | Required when | May be omitted when |
|---|---|---|
| owner | Any PostgreSQL schema exists | No PostgreSQL database is used |
| migrator | Migrations or schema changes are applied | Read-only consumer of another database |
| writer | Workload writes database rows | File/export-only batch, static site, or read-only consumer |
| reader | Human/reporting queries or local validation need read access | No read-only SQL surface exists |
| monitor | Health producer reads DB-backed health or current-state views | Health is file/export-only |
| backup | Database backups are required | Non-database workload with manifest/checksum archive |

### Privilege matrix

| Role | Positive permissions | Negative permissions to test |
|---|---|---|
| owner | Owns schemas and objects; no login | Cannot log in |
| migrator | `CONNECT`; migration-time DDL; `SET ROLE` to owner when designed | Cannot run as superuser; cannot access unrelated databases |
| writer | `CONNECT`; DML only on application write tables/sequences | Cannot alter schema; cannot read restricted views; cannot write outside project schema |
| reader | `CONNECT`; `SELECT` on approved tables/views | Cannot insert/update/delete; cannot alter schema |
| monitor | `CONNECT`; `SELECT` on health/current-state views | Cannot read raw sensitive tables; cannot write |
| backup | `CONNECT`; read privileges needed for `pg_dump` | Cannot write; cannot alter; cannot create objects |

### Environment-variable contract

Use the naming rules in `docs/PORTFOLIO_CONVENTIONS.md`. A repo may expose role-specific URLs such as `{PROJECT}_PG_MIGRATOR_URL`, `{PROJECT}_PG_WRITER_URL`, `{PROJECT}_PG_READER_URL`, `{PROJECT}_PG_MONITOR_URL`, and `{PROJECT}_PG_BACKUP_URL` when one full `{PROJECT}_PG_URL` is too broad. Live values stay outside Git under `/home/scraper/config/`. `.env.example` files list variable names and safe placeholders only.

### Execution packet contracts

Every PostgreSQL privileged handoff must be split into packets with explicit stop gates:

| Packet | Prepared by medium agent | Executed by Strong Codex | Completion proof |
|---|---|---|---|
| Provisioning | Manifest, exact SQL/commands, role matrix, stop gates | `sudo -n -u postgres psql/createdb/dropdb` only as authorized | DB, schemas, roles, and grants exist; no app uses `postgres` |
| Migration execution | Ordered migrations, checksums, rollback/irreversible notes | Apply migrations with migrator role | Migration ledger and validation SQL pass |
| Migration validation | Positive/negative SQL tests, expected row counts | Run validation in target env | Evidence bundle records pass/fail and exact revision |
| Backup/checksum/manifest | Backup command, output root, expected manifest fields | Run or schedule approved backup | Non-zero dump/export, SHA-256, manifest, `pg_restore --list` where DB-backed |
| Isolated restore | Restore DB name, restore command, validation queries | Create temp DB, restore, validate | Restore DB validates and cleanup packet is ready |
| Restore cleanup | Exact temp DB name and proof it is not active | `dropdb` only for named temp restore DB | Temp DB absent; original DB unchanged |
| Health registration | Workflow IDs, producer/adapter command, freshness/backup thresholds | Production registration only when authorized | Phase 0 view or producer registry shows current status |
| Rollback | Rollback SHA, scheduler rollback, DB rollback or preservation plan | Execute only on failed gate or explicit approval | One writer remains; evidence preserved |

### Required evidence bundle

PostgreSQL admission evidence must include:

- onboarding manifest;
- exact reviewed source SHA or publication blocker statement;
- migration file list and checksums;
- role and privilege matrix;
- positive and negative privilege-test output;
- command transcript summaries with secrets redacted;
- backup artifact path class, checksum, manifest, and validation;
- isolated restore proof or documented non-DB recovery equivalent;
- health producer or adapter output;
- rollback procedure and stop gates;
- cleanup evidence for temporary restore databases;
- final single-writer/scheduler authority statement.

### Product inventory

| Product | Current status | Source or evidence | Durable destination | Medium prepares | Strong Codex executes | Validation | Stop conditions | Completion proof |
|---|---|---|---|---|---|---|---|---|
| Database onboarding manifest | Planned and required | Traderie/Reddit Ops packet patterns | This section plus private template | Fill manifest | Consume during execution | YAML fields complete | Missing authority/SHA/role data | Manifest accepted without rediscovery |
| Provisioning packet | Existing evidence, needs promotion | Traderie/Reddit Ops Codex packets | `_internal/templates/SESSION5_REUSABLE_TASK_TEMPLATES.md` | Exact command packet | Bounded `postgres` sudo | Roles/schemas exist | Ambiguous destructive command | Provision evidence bundle |
| Role matrix | Existing reusable | `docs/PORTFOLIO_CONVENTIONS.md`; this doc | This document | Mark applicability | Validate grants | Positive/negative tests | App role needs superuser | Matrix attached to gate |
| Migration packet | Existing per repo, needs standardization | Repo `db/migrations` | Private PostgreSQL onboarding template | File list/checksums/tests | Apply as migrator | Ledger + validation SQL | Irreversible migration undocumented | Migration evidence |
| Backup/restore wrapper | Existing per repo, needs promotion | Traderie/Reddit Ops scripts | Future shared helper or template | Identify command/manifest | Run when authorized | Dump/export validated | Missing checksum/restore path | Backup and restore proof |
| Health registration | Planned | `docs/HEALTH_CONTRACT.md` | Health task template | Producer metadata | Production registration | Phase 0 row visible | Secrets/private paths in output | Registered/visible workflow |
| Bounded privilege execution | Existing session evidence; productization required | `ivy-systemd-deploy`, `ivy-migration` | `docs/PORTFOLIO_CONVENTIONS.md` | Installation packet/source diff | Install/update only with approval | Helper hash/source match | Arbitrary shell or secret work | Logged allowlisted execution |
## Reddit Ops architecture

Reddit Ops is a shared research-data platform rather than a database for only one repository.

It supports:

- the standing WGU subreddit collection;
- future expansion of the subreddit set;
- bounded ad-hoc research projects;
- project requests for posts not already present;
- project-scoped selective comment acquisition;
- future subreddit and Redditor research where justified;
- reuse of canonical Reddit objects across multiple projects.

### Database and schemas

Database:

- `reddit_ops`

Schemas:

- `reddit_core`
- `wgu_reddit`
- `bsda_courses`
- future named project schemas created only when a real project exists.

Do not create a generic `ad_hoc` schema.

### `reddit_core`

Owns shared canonical Reddit and ingestion data:

- posts;
- comments;
- subreddits;
- Redditors;
- ingestion runs;
- collection plans;
- collection targets;
- post observations;
- comment observations;
- subreddit observations;
- Redditor observations where later justified;
- fetch errors;
- archive/export records;
- health state.

A canonical Reddit object exists once in `reddit_core` even when multiple projects use it.

### `wgu_reddit`

Owns WGU-specific state:

- standing collection configuration;
- WGU project memberships;
- WGU-specific processing state;
- project views;
- project outputs that do not belong in canonical Reddit entities.

The VPS is the authoritative WGU-Reddit collector.

As of July 8, 2026, the active WGU-Reddit scheduler authority is the VPS
PostgreSQL timer. The prior VPS SQLite shadow timer and the Mac launchd daily
collector are disabled. SQLite remains preserved as a rollback artifact during
stabilization.

### `bsda_courses`

Owns BSDA-specific Reddit consumption and requests:

- project memberships;
- requests for comments on selected posts;
- requests for specific posts not already present;
- bounded search or subreddit acquisition requests;
- BSDA-specific processing state and outputs.

BSDA Courses consumes canonical Reddit data. It must not run an independent broad Reddit collector.

### Future projects

Create project schemas only for named, real research programs.

Each project schema should contain only project-specific:

- memberships;
- acquisition requests;
- processing state;
- derived results;
- review state;
- project views.

Canonical posts, comments, subreddits, and Redditors remain in `reddit_core`.

## Canonical data model

### Stable entities and mutable observations

Separate stable identity/content from changing values.

Examples:

- post identity and content live in `posts`;
- score, comment count, upvote ratio, edit state, lock state, and similar mutable values live in `post_observations`;
- subreddit identity lives in `subreddits`;
- subscriber and activity counts live in `subreddit_observations`;
- Redditor identity lives in `redditors`;
- karma and other changing profile values live in `redditor_observations` when collection is justified.

### Time semantics

Model these separately:

- `created_utc`: when Reddit says the object was created;
- `first_captured_at`: when Ivy first observed it;
- `last_refreshed_at`: when Ivy most recently refreshed it;
- `observed_at`: when a mutable observation was recorded.

This distinction is important for deciding whether a post should be refreshed or whether comments should be fetched later.

### Raw payload policy

New PRAW-collected records should preserve the raw API payload where available.

Use:

- stable typed columns for the application contract;
- `JSONB` raw payloads for provenance and compatibility;
- optional payload hashes and capture timestamps.

Legacy SQLite rows may have `raw_payload = NULL` when clearly marked with:

- source system;
- legacy import batch;
- legacy record identity where available;
- explicit import timestamp.

### Deleted and unavailable objects

The schema must support:

- deleted authors;
- deleted posts or comments;
- suspended users;
- unavailable Redditors;
- missing profile metadata.

Author foreign keys must remain nullable.

## Collection and research contracts

### Research projects

Each project should have:

- a stable project slug;
- owning repository;
- purpose;
- status;
- retention class;
- sensitivity class;
- created and retired timestamps.

### Collection plans

Collection plans define approved recurring or one-time work.

Examples:

- scheduled subreddit listing;
- subreddit search;
- specific submission fetch;
- submission comments fetch;
- subreddit metadata collection;
- Redditor history collection;
- bounded ad-hoc import.

A collection run must preserve the exact plan or query snapshot used.

### Project memberships

Project schemas associate canonical Reddit objects with a project.

Membership should record why the object belongs to the project, such as:

- directly collected;
- matched a query;
- manually selected;
- selected for comment refresh;
- imported legacy data;
- included in a frozen corpus.

## Comments policy

General comment ingestion remains disabled initially.

The schema supports comments so that future projects can request bounded collection.

BSDA Courses is the primary expected consumer of selective comment collection.

Selective comment acquisition should require:

- a named project;
- specific target posts or bounded criteria;
- a reason;
- a maximum API scope;
- refresh policy;
- collection-run lineage.

The existing legacy comments remain preserved in SQLite and are not part of the initial PostgreSQL cutover.

## Course references

Course codes and course matches do not belong in canonical Reddit tables.

Do not migrate:

- `course_code`;
- `course_code_count`;
- `matched_course_codes`.

The future WGU Course Reference Contract must decide:

- the authoritative course catalog source;
- versioning of course codes and aliases;
- versioning of matching rules;
- whether matching is centralized or consumer-specific;
- how BSDA Courses and WGU Atlas consume course references;
- how historical matches remain reproducible.

Until that contract exists, Reddit Ops remains course-agnostic.

## Legacy migration policy

### Migrated

- selected canonical posts;
- canonical subreddits;
- WGU project memberships;
- reliable capture timestamps;
- bounded current observations needed for production.

### Preserved outside VPS operational storage

- historical subreddit observations are archived to the Mac;
- original SQLite databases remain untouched;
- legacy comments remain in SQLite;
- old run logs remain in SQLite;
- legacy user statistics remain in SQLite.

### Not migrated

- `vader_compound`;
- `course_code`;
- `course_code_count`;
- `matched_course_codes`;
- `posts_keyword`;
- `comments_keyword`;
- `user_map`;
- `users_backup`;
- `processed_stage0_at`;
- old run logs;
- legacy user-stat history.

## Roles and permissions

Reddit Ops uses separate roles for distinct responsibilities.

Current role classes:

- owner;
- migrator;
- writer;
- reader;
- monitor;
- backup.

Expected boundaries:

- owner does not serve as an application login;
- migrator applies schema changes;
- writer performs collector and application writes;
- reader has read-only application access;
- monitor reads health and operational state;
- backup can read required objects and sequences for `pg_dump` but cannot write application data.

Use least privilege and validate each role with both positive and negative tests.

## Migrations

### Migration rules

- migrations are ordered and immutable after production application;
- every forward migration has a rollback or clearly documented irreversible boundary;
- validation SQL accompanies each migration;
- migration state is recorded in the database;
- migrations run as the migrator role;
- schema ownership and default privileges are explicit;
- no application role should own the database.

### Current Reddit Ops migration set

The current deployed migration sequence is:

- `0001` through `0006`.

These migrations create:

- schemas;
- shared collection contracts;
- canonical Reddit entities;
- comments and project schemas;
- archive, health, and supporting views.
- collector heartbeat and progress fields for ingestion-run recovery and
  cutover monitoring.

### Validation

Validation must confirm:

- all expected schemas exist;
- all expected tables and indexes exist;
- constraints are valid;
- role permissions are correct;
- project isolation is enforced;
- canonical objects are not duplicated per project;
- rollback scripts are syntactically valid and tested where practical.

## Production topology

### Host

The Ivy VPS runs PostgreSQL 16 on Ubuntu 24.04.

Do not publish credentials, private host addresses, SSH keys, or secret file contents in public documentation.

### Authority

The VPS is the production authority for active Reddit collection and the operational PostgreSQL database.

The Mac is the authority for:

- long-term archive;
- historical exports;
- backup copies;
- restore testing;
- emergency recovery;
- development and review.

### Scheduler ownership

Each workload must have one authoritative scheduler and writer.

For WGU-Reddit:

- the VPS owns collection;
- only one production timer/service should be active after cutover;
- SQLite remains a rollback artifact during stabilization;
- duplicate Mac collection must remain disabled after authority transfer.

## Operations

### Health checks

Operational health should cover:

- PostgreSQL readiness;
- service state;
- latest successful ingestion run;
- consecutive failures;
- latest run status;
- post and observation freshness;
- archive lag;
- database size;
- disk free space;
- scheduler state;
- deployed revision.

### Collector requirements

The collector must:

- use one authoritative writer;
- upsert canonical objects idempotently;
- record ingestion runs;
- record structured fetch errors;
- create observations for mutable state;
- preserve raw payloads for new records where available;
- avoid writing course-code fields;
- keep general comment collection disabled;
- support future project-scoped acquisition requests.

### OAuth mode

The current PostgreSQL collector path uses app-only Reddit authentication.

The required configuration includes:

- `WGU_REDDIT_REDDIT_AUTH_MODE=app_only`

Do not publish credentials or tokens.

### Manual proof run

A production-equivalent proof should verify:

- OAuth succeeds;
- ingestion-run status is successful;
- no new authentication errors are recorded;
- canonical posts are inserted or updated;
- observations increase;
- a second run does not duplicate canonical objects.

The first July 8, 2026 PostgreSQL cutover attempt did not pass this proof. The
bounded PostgreSQL proof runs succeeded, but the full production-equivalent run
scanned 999 posts for `WGU` with `frontier=0`, took about 899 seconds before
the first target completed, and was cancelled during rollback. This showed the
full production PostgreSQL path was not yet safely idempotent or bounded enough
to become authoritative.

The defect was fixed later the same day. Root cause: the PostgreSQL frontier
path used `subreddit.subreddit_id`, which is not populated on PRAW `Subreddit`
objects. The fixed code uses `subreddit.id`, adds a bounded bootstrap cap of 100
posts for genuinely new targets, and logs each target's frontier source. Two
full production-equivalent proofs then completed with correct frontier behavior
and idempotence before the final authority transfer.

Accepted `partial` runs are valid only when the error set is exactly these
known inaccessible targets:

- `WGUBusinessManagement` / `NotFound`;
- `WGU_BSIT` / `Forbidden`;
- `WGU_BSSE` / `NotFound`;
- `WguTutorReddit` / `NotFound`.

Any OAuth, PostgreSQL, timeout, stale-heartbeat, duplicate-writer, or unexpected
target error remains a failed collector run.

## Backup and restore

### Backup format

Use PostgreSQL custom-format dumps where practical.

Backups should be created with the dedicated backup role.

Validate each dump with:

- successful `pg_dump` completion;
- non-zero artifact size;
- checksum;
- `pg_restore --list`;
- periodic restore to a test database or environment.

### Backup authority

Reddit Ops owns its export and archive acknowledgment records.

Ivy Control reads summarized backup age, archive lag, and prune eligibility.

Ivy Control is not the transactional source of truth for each repository's archive lifecycle.

### Restore expectations

A restore procedure should document:

- required PostgreSQL version;
- role and extension prerequisites;
- database creation;
- migration compatibility;
- restore command;
- validation queries;
- application health checks;
- rollback to the prior service authority if restore validation fails.

### SQLite rollback artifact

The original SQLite database remains preserved through the stabilization period.

Do not delete or overwrite it until:

- PostgreSQL has completed multiple successful scheduled runs;
- backup and restore have been tested;
- rollback no longer depends on SQLite;
- explicit approval is given.

## Archive and retention

### General rule

Preserve first, verify second, prune third.

Before removing VPS data:

- create an immutable Mac archive copy;
- generate a checksum;
- record a manifest;
- verify entry counts or row counts;
- confirm readability;
- confirm no active writer depends on the source;
- record archive acknowledgment;
- mark the source prune-eligible.

### VPS retention

The VPS should retain only bounded operational data needed for active services.

The VPS is not the long-term historical archive.

### Mac archive

The Mac archive should retain:

- historical PostgreSQL exports;
- preserved SQLite databases;
- immutable raw exports;
- manifests and checksums;
- archive/import batch records;
- historical observations not needed on VPS;
- restore evidence.

### Legacy subreddit observations

Historical subreddit observations were exported to the Mac archive and removed from VPS operational PostgreSQL after validation.

The VPS may retain only bounded current observations required for live health or research.

### Idle Hacking data

Historical IH Market and Idle Hacking chat data were archived to the Mac and verified before approved VPS removal.

The active collector recreated both source paths, proving they remain operational outputs.

Future work must define:

- incremental archive cadence;
- retention windows;
- writer-aware pruning;
- health monitoring;
- growth alerts;
- distinction between raw durable data and regenerable runtime data.

Do not delete recreated active paths without a new archive and writer-aware approval.

## Idle Hacking KB database direction

Idle Hacking KB already has a real PostgreSQL migration set with rollback and validation support.

Current major TODO:

- design and later implement reliable Discord ingestion on the VPS.

The design must cover:

- browser and Chrome extension runtime;
- manual authentication and reauthentication;
- bounded server/channel scope;
- incremental export;
- download detection;
- immutable raw export preservation;
- manifests and checksums;
- normalized ingestion;
- duplicate prevention;
- edit/deletion reconciliation;
- attachments and embeds;
- browser watchdog and recovery;
- privacy controls;
- archive acknowledgment;
- retention and pruning.

Automated Discord login remains deferred.

## IH Market Companion database direction

IH Market Companion already has a real PostgreSQL migration set with rollback and validation support.

Future work must finalize:

- raw market observation identity;
- receipt identity and deduplication;
- browser-run lineage;
- durable versus regenerable outputs;
- operational PostgreSQL versus file archive responsibilities;
- archive cadence;
- restore behavior;
- retention based on measured footprint.

Long-term retention classes remain intentionally undecided until actual growth and research value are measured.

## Reddit Ops migration case study

### Starting condition

The original WGU-Reddit system used SQLite and accumulated:

- canonical Reddit fields;
- derived sentiment;
- course matching;
- processing state;
- legacy tables;
- comments no longer actively collected;
- duplicated or unclear operational concerns.

The VPS was also near its storage threshold.

### Main risks

- unclear collector authority;
- duplicate ingestion;
- overloaded schema;
- insufficient storage headroom;
- no PostgreSQL runtime;
- weak archive boundaries;
- no project-aware shared Reddit platform;
- no professional run, backup, or health contracts.

### Architecture chosen

The migration introduced:

- PostgreSQL 16 on the VPS;
- shared `reddit_ops` database;
- canonical `reddit_core` schema;
- isolated project schemas;
- explicit collection and membership contracts;
- observation tables;
- least-privilege roles;
- archive/export tracking;
- health tooling;
- rollback preservation.

### Storage remediation

Before import and cutover:

- IH Market and Idle Hacking chat data were archived to the Mac;
- archives were checksum-verified and tested;
- approved historical VPS copies were removed;
- approximately 12.7 GB of free space was recovered;
- active collectors later recreated bounded working paths, which were preserved.

### Migration execution

The process included:

- PostgreSQL installation;
- role and database provisioning;
- migrations `0001` through `0005`;
- validation SQL;
- Python PostgreSQL driver installation;
- read-only SQLite import tooling;
- pre-import PostgreSQL backup;
- import of canonical posts and subreddits;
- project membership creation;
- exclusion of comments, users, user statistics, old run logs, course matches, and obsolete derived fields.

### Validation

Validation included:

- schema checks;
- role positive and negative tests;
- backup-role `pg_dump` proof;
- `pg_restore --list` verification;
- OAuth correction to app-only mode;
- two bounded PostgreSQL collector proof runs;
- idempotence proof;
- health and disk checks;
- preservation of SQLite rollback artifacts.

### Result

The resulting platform supports:

- one canonical Reddit data store;
- multiple research projects;
- bounded project-specific acquisition requests;
- future selective comments;
- professional ingestion and health records;
- operational VPS storage;
- Mac archive authority;
- tested backup and rollback paths.

### First final cutover attempt

On July 8, 2026, the PostgreSQL-backed WGU-Reddit timer was enabled for a final
production-equivalent cutover proof after bounded proof runs, stale-run recovery,
and advisory-lock checks had passed.

The proof failed the health gate because the full PostgreSQL production run did
not preserve the expected frontier behavior. Run `21` reached only target 3 of
52 before rollback, with:

- status `cancelled`;
- current target `WGUAccelerators`;
- `posts_seen=1028`;
- `posts_inserted=15`;
- `posts_updated=1013`;
- `error_count=0`;
- `frontier=0` reported in service logs for the first targets.

Rollback was executed immediately:

- `wgu-reddit-postgres-run.timer` disabled and inactive;
- `wgu-reddit-postgres-run.service` inactive;
- `wgu-reddit-shadow-run.timer` enabled and active for the next run at
  `2026-07-09 07:00:00 UTC`;
- PostgreSQL remained healthy;
- SQLite was not deleted.

Do not attempt another PostgreSQL collector cutover until the full production
frontier/idempotence defect is corrected and a new production-equivalent proof
passes without excessive historical rescanning.

### Successful authority transfer

Later on July 8, 2026, after the frontier fix was deployed and proven, the
PostgreSQL cutover was retried and completed.

Final production authority:

- `wgu-reddit-postgres-run.timer`: enabled, active, waiting;
- `wgu-reddit-shadow-run.timer`: disabled, inactive;
- Mac launchd `com.buddy.wgu-reddit.dailyupdate`: disabled and not loaded.

The immediate production-equivalent PostgreSQL service execution created:

- run `29`: `partial`, `posts`, 52/52 targets, 48 posts seen, 0 inserted,
  0 updated, 4 approved inaccessible-target errors;
- run `30`: `partial`, `subreddit_metadata`, 52/52 targets, 4 approved
  inaccessible-target errors.

The WGU frontier was nonzero and idempotent:

- `WGU` used subreddit ID `2se63`;
- latest frontier after cutover: `1783551781`;
- production run `29` inserted 0 new posts.

PostgreSQL health after cutover:

- PostgreSQL accepting connections;
- 44,962 canonical posts;
- 46,498 post observations;
- 0 running ingestion runs;
- 0 comments imported;
- disk remained healthy at 9.6 GB available.

Operational caveat (resolved 2026-07-09): the collector previously exited with
status `1` when approved `partial` runs included the known inaccessible targets.
As of the closeout hardening, the collector exits `0` when all errors match the
approved set (WGUBusinessManagement, WGU_BSIT, WGU_BSSE, WguTutorReddit).
Systemd records `Result=success` and `ExecMainStatus=0` for approved partial
runs, while unexpected failures (OAuth, PostgreSQL, unknown subreddit errors)
still produce nonzero exit status.

## Deferred work

The following remain planned:

- WGU-Reddit Git publication (blocked by secrets in early commit history);
- reboot recovery and post-reboot scheduled-run validation (requires current scoped helper/sudo policy review and Buddy-approved timing);
- monitoring/alerting automation;
- incremental archive automation;
- WGU Course Reference Contract;
- selective BSDA comment acquisition implementation;
- Idle Hacking Discord ingestion design and implementation;
- IH Market pipeline and retention finalization;
- public diagrams and refined case-study presentation.

### Completed closeout items (2026-07-09)

The following items from the original deferred list are now resolved:

- ~~stabilization evidence after successful PostgreSQL scheduled runs~~ — three consecutive systemd-triggered runs verified;
- ~~observation of multiple scheduled PostgreSQL runs~~ — runs 30-34 demonstrated consistent behavior;
- ~~align systemd process success semantics with the accepted partial policy~~ — approved partial now returns exit 0;
- ~~tested full restore to a separate database~~ — `pg_restore` drill completed against `reddit_ops_restore_verify` database;
- automated PostgreSQL backup — implemented via `backup_reddit_ops.sh` + systemd service/timer.

## Private evidence

Detailed implementation evidence remains under `_internal/`, including:

- discovery reports;
- Codex architecture packets;
- PostgreSQL bootstrap evidence;
- migration and import reports;
- OAuth troubleshooting;
- archive manifests and checksums;
- proof-run evidence;
- agent execution logs;
- cutover and rollback command packets.

The private execution record should not be copied directly into public documentation. Public docs should summarize the engineering decisions, controls, and results.
