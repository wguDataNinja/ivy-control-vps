# Ivy Control VPS Roadmap

**Status:** Active roadmap, created 2026-07-08; factual status reconciled at Session 4 closeout on 2026-07-11.
**Scope:** Portfolio-wide VPS operating model with Traderie as the first detailed reference deployment.

This roadmap defines the long-horizon path for moving the Ivy portfolio onto a governed VPS operating model. It is public, durable, and agent-neutral. Current repository facts are separated from intended future state, and repository sequencing after Traderie remains flexible unless a dependency requires a specific order.

## §1 Program Authority and Baseline

**Current authority**

- `README.md` defines IvyControlVPS as the operational control plane.
- `docs/OPERATING_MODEL.md` defines the shared operating model and workflow readiness classes.
- `docs/REPOSITORY_CONTROL_MODEL.md` defines the six-gate repository control framework.
- `docs/PORTFOLIO_CONVENTIONS.md` defines PostgreSQL, systemd, health, migration, environment, and deployment conventions.
- `docs/DATA_LIFECYCLE_STANDARD.md` defines retention, storage, backup, and recovery principles.
- `docs/PORTFOLIO_BASELINE.md` defines the current portfolio inventory and repository baseline.
- `repos/traderie/CONTROL.md` and `repos/traderie/RELEASE_GATES.md` are the current Traderie governance authority.

**Current portfolio**

| Repository | Runtime class | Planning depth now | Current roadmap posture |
|------------|---------------|--------------------|-------------------------|
| Traderie | Deterministic data pipeline | Full | First reference deployment |
| SJC Intel | Deterministic data collection | Moderate | Likely early follow-on |
| WGU-Reddit operations | LLM/data pipeline | Moderate | Early risk inspection, later LLM reference candidate |
| WGU Catalog | Deterministic canonical data source | Moderate | Shared WGU data dependency |
| BSDA Courses | LLM pipeline consumer | Light to moderate | Consumer of WGU-Reddit and WGU Catalog data |
| WGU Atlas | Read-oriented public site and LLM QA layer | Light to moderate | Catalog consumer and possible mature LLM runtime reference |
| Idle Hacking KB | LLM knowledge base | Light | Later sensitive LLM workflow candidate |
| IH Market Companion | Deterministic browser/runtime pipeline | Light | Deterministic runtime and browser-supervision candidate |
| Reckless Ben | Restricted evidence workspace | Light | `NO_LAUNCH`; patterns only unless separately authorized |

**Settled target architecture**

- The Ivy VPS is the long-term production platform.
- One PostgreSQL instance runs on the VPS.
- Each repository receives isolated project data boundaries according to portfolio conventions.
- The VPS stores only operational data needed for live workflows, health, UI/API use, bounded aggregates, and continuity.
- The VPS is not the long-term archive.
- The Mac remains the primary development, backup, archive, restore, and emergency-recovery environment.
- Production operation must not depend on the Mac being online.
- GitHub is the reviewed code authority.
- Deployments use exact approved SHAs.
- Initial deployment is simple and manual; broader automation comes later.
- Hermes starts with read-only inspection and gains execution authority only through explicit gates.

**Transitional assumptions**

Historical Mac-authoritative PostgreSQL and reverse-tunnel designs are transitional evidence. They may inform migration and rollback but are not the target production topology.

## §2 Repository Admission and Public Readiness

### §2A Admission Standard

**Outcome**

Every managed repository has a control sheet, gate evidence, publication posture, runtime classification, data boundary, and next authorized phase.

**Dependencies**

Portfolio standards in `docs/` remain the shared baseline. Repository-specific deviations are recorded in each repository control sheet.

**Work**

- Create `repos/<repo>/CONTROL.md` for each admitted repository.
- Create `repos/<repo>/RELEASE_GATES.md` for detailed gate evidence.
- Classify each workflow using the `docs/OPERATING_MODEL.md` readiness categories.
- Identify public/private boundaries, dependency manifests, `.env.example` coverage, license posture, CI/test posture, generated-data boundaries, and local-machine path risks.
- Identify the current collector, scheduler, writer, database, runtime data, backup path, and rollback path.

**High-reasoning gates**

- `§2A-G1` Repository Admission Gate.
- `§2A-G2` Public Repository Readiness Gate.

**Required evidence**

Repository status, remotes, branches, dirty state, dependency manifests, tracked-data scan, secret/history scan where publication is planned, `.env.example`, license decision, README quality, tests, CI, runtime-data boundaries, and documented exceptions.

**Completion proof**

Each repository has a current control sheet and release-gate file, or is explicitly marked deferred/restricted with the reason.

**Status**

Active for Traderie. Not started for most other repositories.

### §2B Repository Polish Track

**Outcome**

Repository polish becomes a deployment prerequisite rather than optional cleanup.

**Dependencies**

`§2A` admission evidence.

**Work**

- Cleanly separate source, generated artifacts, runtime data, logs, private state, and backups.
- Add or update setup, operation, troubleshooting, deployment, backup, recovery, and retention docs.
- Ensure tests and CI match repository risk.
- Remove or parameterize hardcoded local-machine paths.
- Document license decisions, including explicit no-license choices.
- Preserve project-specific strengths as patterns for later repositories.

**Required evidence**

Documentation index, test output, CI definition, `.gitignore`, tracked-file scan, generated-data scan, and exception log.

**Completion proof**

Publication readiness can be evaluated without relying on private notes or personal memory.

**Status**

Active and ongoing.

## §3 VPS Platform Foundation

### §3A Host Capacity and Access Baseline

**Outcome**

The VPS has enough headroom and known access limits for the first bounded deployment proof.

**Dependencies**

No deployment or cleanup occurs without the applicable approval gates.

**Work**

- Confirm disk, memory, failed units, timers, running processes, and current app checkouts.
- Confirm exact SSH/user model and sudo limits.
- Preserve protected workloads and data.
- Keep deployment blocked if root filesystem usage exceeds the portfolio stop threshold.

**High-reasoning gates**

- `§3A-G1` VPS Capacity Gate.

**Required evidence**

Disk usage, free space, memory, failed units, timers, process inventory, app checkout inventory, protected-data list, and approved cleanup or resize path if needed.

**Completion proof**

Capacity is below the deployment stop threshold, or a resize/remediation decision is recorded before deployment continues.

**Status**

Passing during Work Session 3. Capacity was rechecked during Traderie readiness and cutover work and remained below the portfolio deployment stop threshold. Durable migration-phase operations access is now installed through `/usr/local/sbin/ivy-systemd-deploy` and `/etc/sudoers.d/ivy-migration`; the temporary unrestricted bootstrap grant was removed and unrestricted passwordless sudo is not present. Capacity must still be rechecked before each deployment or reboot-sensitive cutover step.

### §3B PostgreSQL Foundation

**Outcome**

The VPS has a production PostgreSQL foundation suitable for project-isolated databases, bounded backups, restore drills, and monitored operation.

**Dependencies**

`§3A` capacity remains passing.

**Work**

- Install and configure PostgreSQL on the VPS when authorized.
- Define project database, roles, schemas, backup role, monitor role, and migration role according to portfolio conventions.
- Keep credentials outside Git checkouts.
- Define backup destination on VPS and Mac.
- Define restore-test naming, checksum, and manifest conventions.

**High-reasoning gates**

- `§3B-G1` PostgreSQL Foundation Gate.
- `§3B-G2` Credential Boundary Gate.

**Required evidence**

PostgreSQL version, role list, database list, grants, schema ownership, connection checks by role, credential file location, backup path, restore-test procedure, and disk impact.

**Completion proof**

A non-application restore drill can be run against a test database without using application superuser access.

**Status**

Implemented on VPS during Work Session 3 for the current portfolio migration phase. PostgreSQL is installed and operational. Traderie project roles, database, credentials outside Git, migrations, validation, backup, and isolated restore paths are proven. Delegated PostgreSQL administration remains available through the durable operations model. Broader portfolio standardization remains ongoing.

### §3C Storage, Retention, Backup, Restore, and Recovery

**Outcome**

All production repositories have bounded storage, documented retention, automated backup candidates, and restore proof before authority transfer.

**Dependencies**

`§3B` PostgreSQL foundation and repository-specific retention policy.

**Work**

- Define data classes per repository.
- Keep mutable production data outside Git working trees.
- Store backups outside working trees.
- Prove `pg_dump -Fc -Z 9`, checksum, manifest, restore, validation, and cleanup.
- Record Mac backup/archive responsibilities separately from VPS live retention.

**High-reasoning gates**

- `§3C-G1` Backup/Restore Gate.
- `§3C-G2` Retention and Pruning Gate.
- `§3C-G3` Disaster Recovery Gate.

**Required evidence**

Backup manifest, checksum, restore output, validation SQL output, row counts, data directory size, database size, retention windows, dry-run prune report, and rollback path.

**Completion proof**

The repository can be restored into an isolated database and validated before any production cutover.

**Status**

Proven on VPS for Traderie during Work Session 3: production backup creation, checksum evidence, isolated restore, validation, and recovery evidence passed. Portfolio-wide retention automation, recurring restore drills, and multi-repository coverage remain future work.

## §4 Exact-SHA Deployment and Drift Control

### §4A Deployment Contract

**Outcome**

Every deployable repository can be checked out on the VPS at an exact approved SHA and verified against GitHub.

**Dependencies**

Repository publication gate passes or repository is explicitly private and approved for local-only deployment.

**Work**

- Record canonical remote, default branch, approved SHA, and rollback SHA.
- Confirm clean checkout before deployment.
- Keep runtime data and secrets outside checkout.
- Run dependency install only after capacity and credential boundaries are known.
- Record deployment revision in health output.

**High-reasoning gates**

- `§4A-G1` Publication or Private-Deployment Authority Gate.
- `§4A-G2` Exact-SHA Deployment Gate.

**Required evidence**

Remote URL, branch, SHA, clean checkout status, dependency-change flag, migration-change flag, rollback SHA, health revision field, and drift check command.

**Completion proof**

The VPS checkout matches the approved SHA, has no tracked local modifications, and can report its revision through health.

**Status**

Traderie has been deployed on the VPS by exact approved SHA. The current production SHA is `e5ebd0f6dd41bcb4e1d8a88f272be89b225cfd40`. The VPS checkout is clean at that SHA, the root-owned deployment helper is pinned to it, and the deployed revision metadata matches. All six Traderie systemd services and the timer are installed from the reviewed source. The helper SHA pin uses a direct `sed` interim mechanism; a durable template-based mechanism is deferred. The prior roadmap SHA `b3b70a01426694d06d6c07a09f0c33427f530f0d` is historical.

### §4B Drift Detection

**Outcome**

The control plane can detect stale deployments, unexpected local changes, unapproved SHAs, and missing health revisions.

**Dependencies**

`§4A` deployment contract.

**Work**

- Define drift checks for Git SHA, database schema version, deployed health revision, service unit revision, and expected scheduler state.
- Report drift without automatically changing production.
- Require review before redeployment or rollback.

**Required evidence**

Drift report with expected SHA, actual SHA, dirty status, schema version, health revision, service state, and timer state.

**Completion proof**

Drift is visible as a health or control-plane finding before operational activation.

**Status**

Partially implemented for Traderie during Work Session 3. Exact SHA, clean checkout, schema version, installed unit hashes, scheduler state, and health revision are included in deployment and cutover validation. Portfolio-wide automated drift reporting remains future work.

## §5 Scheduler Ownership and Single-Writer Controls

### §5A Authority-Transfer Lifecycle

**Outcome**

Each workflow has one authoritative collector, scheduler, and writer unless a separately approved mirroring design exists.

**Dependencies**

Repository control sheet identifies current and future authorities.

**Work**

- Document current collector, scheduler, writer, data store, downstream consumers, and disable point.
- Run shadow mode where needed.
- Prove parity, freshness, reject handling, and rollback.
- Obtain cutover approval before switching authority.
- Retire or archive legacy paths only after stabilization and destructive-operation approval.

**High-reasoning gates**

- `§5A-G1` Database Authority Gate.
- `§5A-G2` Scheduler Gate.
- `§5A-G3` Cutover Gate.
- `§5A-G4` Destructive Operation Gate, only for deletion or retirement.

**Required evidence**

Authority map, scheduler inventory, write-path inventory, parity report, freshness report, backup/restore proof, rollback proof, disable plan, and stabilization report.

**Completion proof**

The old and new paths are not both writing production data after cutover.

**Status**

Exercised for Traderie during Work Sessions 3 and 4. The authority transfer lifecycle was executed through 4 cutover attempts: one 300s timeout rollback (Codex 2), one 600s timeout rollback (Codex 3), one segmented premature-monitor rollback (Codex 4), and one successful segmented cutover (Codex 5). VPS systemd is now the sole Traderie scheduler and writer authority. Mac launchd is unloaded. The timer `traderie-ingest-snapshot.timer` is enabled and active. Reddit Ops authority transfer was completed earlier during Work Session 3; VPS systemd remains the sole Reddit Ops authority.

## §6 Monitoring, Health, Alerting, and Resource Management

### §6A Health Contract

**Outcome**

Every production workflow emits health records that identify status, freshness, records read/written/rejected, backlog, retries, schema version, deployed revision, backup state, and incident state.

**Dependencies**

Repository-specific health schema or safe file-mode export.

**Work**

- Implement health tables or exports.
- Sanitize public health outputs.
- Include database size, data directory size, growth rate, prune status, and backup state.
- Route health failures into a reviewable incident path.

**High-reasoning gates**

- `§6A-G1` Health Contract Gate.

**Required evidence**

Health schema/export sample, prohibited-field scan, stale-data sample, failed-run sample, and growth metrics.

**Completion proof**

A health report can distinguish healthy, stale, failed, skipped, backup-stale, and resource-pressure states.

**Status**

Substantially implemented during Work Session 3. A canonical portfolio health contract was reconciled, Reddit Ops became the first canonical producer, and Traderie emits validated private and public health with environment, revision, database, scheduler, backup, freshness, and drift-related state. Traderie currently reports `ok` with `project_environment=production`. Central collector, historical storage, API, dashboard, alert delivery, and portfolio-wide growth reporting remain future work.

### §6B Resource and Incident Management

**Outcome**

The VPS reports storage pressure, failed services, stale data, backup failure, and incident state before silent degradation.

**Dependencies**

`§6A` health contract and `§3C` backup/retention design.

**Work**

- Define warning/critical/emergency thresholds.
- Add checks for disk usage, database size, data directory size, service failure, stale workflows, and backup age.
- Define incident response and rollback paths.

**Required evidence**

Threshold definitions, health output, simulated stale/failure samples, and recovery instructions.

**Completion proof**

A failed or stale workflow produces a bounded, actionable signal without exposing secrets or private paths.

**Status**

Partially implemented through deployment gates, health checks, backup-age checks, disk thresholds, service-state checks, one-writer rollback, and cutover incident handling. Portfolio-wide alert delivery, incident persistence, and standardized threshold enforcement remain future work.

## §7 Traderie Reference Deployment

Traderie is first because it currently has the strongest deployment foundation: public GitHub repository, 17 PostgreSQL migrations, 57 passing tests, real PostgreSQL adapter, bounded pilot, parity and rollback tooling, backup/checksum/restore evidence, health export, inert systemd units, wrapper scripts, and deterministic runtime. SJC Intel was previously considered first, but current evidence shows Traderie is the better complete reference deployment. SJC Intel remains a strong early follow-on.

### §7A Traderie Current State

**Current facts**

- Production SHA is `e5ebd0f6dd41bcb4e1d8a88f272be89b225cfd40`.
- VPS systemd is the sole scheduler and writer authority. Mac launchd is unloaded.
- Segmented orchestrator (`run_traderie_generation.sh`) is installed with per-segment `timeout` bounds: pc_sc_nl=180s, pc_sc_l=240s, pc_hc_l=360s, pc_hc_nl=480s.
- Bounded manual generation succeeded (all 4 segments, exit=0).
- `traderie-ingest-snapshot.timer` is enabled and active.
- A natural scheduled generation occurred (2026-07-11 18:01:46 UTC) but partially failed: pc_hc_nl reached its 480-second bound and timed out. Overall exit=1.
- Current classification: **`PRODUCTION_DEGRADED`**.
- Controlled reboot proof is deferred until natural-run success is restored.
- DB-backed health records report `ok`. File-based health export is an empty directory.
- Backup freshness lacks an explicit contract threshold.

### §7B VPS PostgreSQL Foundation for Traderie

**Outcome**

Traderie has a VPS PostgreSQL database, roles, schemas, migrations, validation, backup role, monitor role, and credential boundary.

**Dependencies**

`§3A` capacity recheck passes. `§3B` PostgreSQL foundation is authorized.

**Work**

- Create the `traderie` database and project roles on VPS.
- Apply the 17 migrations in order.
- Run validation SQL.
- Confirm role permissions by connection type.
- Keep secrets in VPS config outside Git.
- Record schema version and database size.

**High-reasoning gates**

- `§7B-G1` Traderie PostgreSQL Foundation Gate.

**Required evidence**

Role list, database list, migration table, validation output, role-specific connection checks, schema version, database size, and credential boundary confirmation.

**Completion proof**

Validation passes on the VPS database and application scripts can connect using the intended non-superuser role.

**Status**

Complete for Traderie during Work Session 3. PostgreSQL is installed; Traderie roles and database exist; migrations 1–17 are applied; role-specific validation, credential boundaries, backup, restore, and application connectivity passed.

### §7C Mac-to-VPS Data Transfer and Parity

**Outcome**

The VPS database contains the approved Traderie operational baseline, and the Mac copy is preserved for backup/archive/restore.

**Dependencies**

`§7B` complete. Fresh Mac backup and isolated restore drill pass.

**Work**

- Create a fresh Mac PostgreSQL backup and checksum.
- Restore or import the approved operational baseline into VPS PostgreSQL.
- Compare schemas, row counts, primary/natural keys, date ranges, segment coverage, completed trades, price entries, aggregates, duplicates, and reject records.
- Identify records present only on Mac or only on VPS.
- Define reject rules for unmappable data.

**High-reasoning gates**

- `§7C-G1` Traderie Data Transfer and Parity Gate.

**Required evidence**

Backup manifest, checksum, restore drill output, row-count table, segment coverage, date ranges, duplicate report, reject report, and unmapped-field table.

**Completion proof**

Parity is either proven or explicit exceptions are accepted before any authority transfer.

**Status**

Complete for the approved Traderie operational baseline during Work Session 3. Mac source data was transferred to VPS PostgreSQL and parity evidence passed. The Mac remains the backup, archive, restore, and emergency-recovery environment.

### §7D Bounded Manual Deployment Proof

**Outcome**

Traderie runs one bounded manual cycle on VPS without enabling services or timers.

**Dependencies**

`§7B` and `§7C` pass or have accepted conditions. Exact SHA checkout exists on VPS.

**Work**

- Clone Traderie to the approved VPS app path.
- Check out the approved SHA.
- Install dependencies.
- Configure secrets outside the repo.
- Run tests if practical in the VPS environment.
- Run one snapshot, validation, health export, and backup cycle.
- Verify backup checksum and manifest.
- Measure disk growth from one cycle.

**High-reasoning gates**

- `§7D-G1` Bounded Deployment Proof Gate.

**Required evidence**

Remote URL, SHA, clean checkout status, dependency install output, test output or reason tests could not run, snapshot row counts, validation output, health output, backup manifest, checksum, and disk-growth measurement.

**Completion proof**

One clean manual cycle completes and produces validation, health, backup, checksum, and growth evidence.

**Status**

Complete during Work Session 3. Traderie was deployed by exact SHA, dependencies and environment were validated, bounded PostgreSQL proof passed twice, health export passed, backup/checksum evidence passed, and the checkout remained clean.

### §7E Rollback and Restore Proof

**Outcome**

Traderie can roll back a bounded test run and restore from backup before production authority changes.

**Dependencies**

`§7D` bounded cycle.

**Work**

- Capture pre-run row counts and observation keys.
- Delete only test-run records by explicit key set.
- Confirm row counts return to baseline.
- Re-run snapshot and prove stable reinsertion.
- Restore latest backup into an isolated database and run full validation.
- Record rollback SHA and service disable path.

**High-reasoning gates**

- `§7E-G1` Rollback and Restore Gate.

**Required evidence**

Pre/post row counts, exact key set, rollback command, validation output, isolated restore output, checksum, and rollback instruction review.

**Completion proof**

Rollback returns counts to baseline and isolated restore validates.

**Status**

Complete for the current Traderie migration phase. Bounded rollback/idempotence proof passed, isolated restore validated, scheduler rollback was exercised during the first cutover attempt, and Mac authority was restored without duplicate writers.

### §7F One-Writer Cutover Preparation

**Outcome**

Traderie has an approved cutover plan from current Mac collection to VPS production collection.

**Dependencies**

`§7D` and `§7E` pass.

**Work**

- Inventory current Mac launchd collector and any other writer.
- Define VPS writer and future scheduler.
- Define shadow window, parity checks, freshness checks, and disable point.
- Define fallback to Mac collection if VPS run fails.
- Keep Mac as backup/archive/restore environment after cutover.

**High-reasoning gates**

- `§7F-G1` Traderie Database Authority Gate.
- `§7F-G2` Traderie Cutover Approval Gate.

**Required evidence**

Current scheduler inventory, current writer inventory, future scheduler plan, parity report, disable command, fallback command, backup/restore proof, and rollback criteria.

**Completion proof**

Buddy can approve or reject cutover from a concrete evidence packet without further rediscovery.

**Status**

Complete as a preparation packet and exercised twice. Current and future authorities, disable and fallback commands, parity, freshness, backup/restore, and one-writer criteria are documented. The first cutover attempt rolled back safely after a natural health-timer failure. The second attempt deployed the corrected SHA but stopped before scheduler transfer because the health-role and deployment-helper SHA gates failed. Mac launchd remains authoritative and VPS Traderie units remain disabled/inactive.

### §7G Scheduler Activation

**Outcome**

Traderie services and timers are enabled only after manual proof, rollback proof, and cutover approval.

**Dependencies**

`§7F` cutover approval.

**Work**

- Install service/timer units.
- Confirm all units map to approved scripts and config.
- Start with a bounded schedule.
- Monitor first scheduled runs.
- Confirm no Mac collector duplicate write remains active.

**High-reasoning gates**

- `§7G-G1` Scheduler Gate.

**Required evidence**

Unit files, timer schedule, service environment, first scheduled run output, health output, duplicate-writer check, and rollback/disable path.

**Completion proof**

Scheduled collection runs successfully, health remains current, backups run, and there is exactly one authoritative writer.

**Status**

Activated during Work Session 4. After 4 cutover attempts (Codex 2–5) and two runtime remediation cycles (Agent 7, Agent 8), `traderie-ingest-snapshot.timer` is enabled, active, and the sole scheduler. The segmented runtime uses per-segment `timeout` with `TimeoutStartSec=infinity`. The first natural scheduled generation (2026-07-11 18:01:46 UTC) completed 3 of 4 segments; pc_hc_nl timed out at 480s. Restoration to `PRODUCTION_COMPLETE` is the first objective of Work Session 5.

### §7H Operational Acceptance

**Outcome**

Traderie becomes the reference deployment for the portfolio.

**Dependencies**

`§7G` Scheduler Gate passes and a stabilization window completes.

**Work**

- Review health, drift, backup age, growth, prune behavior, and service state over the stabilization window.
- Confirm Mac backup/archive responsibilities.
- Record lessons to update shared standards.
- Identify reusable deployment patterns for SJC Intel and other follow-ons.

**High-reasoning gates**

- `§7H-G1` Operational Activation Gate.

**Required evidence**

Stabilization report, health history, backup manifests, restore proof, growth trend, prune evidence, drift report, incident log, and unresolved issue list.

**Completion proof**

Traderie is accepted as the first operational reference deployment, or conditions are recorded before broader reuse.

**Status**

Not yet started as a stabilization window. Scheduler activation is complete but the natural generation is partially failing (pc_hc_nl timeout). Operational acceptance begins after Session 5 resolves the segment timeout, restores healthy natural runs, proves controlled reboot recovery, verifies one-writer authority, and completes a documented stabilization period.

## §8 Hermes Operating Model

### §8A Read-Only Inspection

**Outcome**

Hermes can inspect approved health, drift, logs, deployment state, and repository status without changing production.

**Dependencies**

Public-safe health exports and configured read-only credentials.

**Work**

- Define read-only data sources.
- Define allowed inspection commands.
- Block secrets, private paths, and raw sensitive data from outputs.
- Produce evidence packets for review without mutation.

**High-reasoning gates**

- `§8A-G1` Hermes Read-Only Gate.

**Required evidence**

Read-only credential check, allowed command list, sample health report, sample drift report, and prohibited-output scan.

**Completion proof**

Hermes can report status without write permissions or production mutation.

**Status**

Not started.

### §8B Deterministic Workflow Execution

**Outcome**

Hermes can run approved deterministic workflows with bounded inputs, outputs, locks, timeouts, retries, and health reporting.

**Dependencies**

`§8A` read-only gate passes and at least one deterministic reference workflow is accepted.

**Work**

- Define command contracts for fetch, process, validate, export, backup, retain, and check workflows.
- Require idempotency, locks, timeout/retry limits, and failure outputs.
- Keep scheduler authority separate from workflow execution authority.

**High-reasoning gates**

- `§8B-G1` Deterministic Workflow Execution Gate.

**Required evidence**

Workflow contract, dry-run output, failure-mode output, lock behavior, timeout behavior, health output, and rollback path.

**Completion proof**

Hermes can execute a deterministic workflow without changing its contract or bypassing scheduler gates.

**Status**

Not started.

### §8C LLM Workflow Execution

**Outcome**

Hermes can run approved LLM stages only when prompt version, model/provider, input contract, output schema, validation, cost accounting, audit artifact, and review boundary are defined.

**Dependencies**

`§8A` read-only gate and `§8B` deterministic workflow gate. A selected LLM reference repository has passed admission.

**Work**

- Define prompt versioning.
- Externalize provider/model configuration.
- Enforce structured inputs and outputs.
- Record token and cost metadata.
- Preserve audit artifacts.
- Define human-review and production-write boundaries.

**High-reasoning gates**

- `§8C-G1` LLM Stage Authority Gate.
- `§8C-G2` LLM Budget Gate.
- `§8C-G3` Sensitive Review Gate, where applicable.

**Required evidence**

Prompt path, prompt version, model profile, provider config, input schema, output schema, validation results, token/cost estimate, audit sample, review trigger, and reprocessing rules.

**Completion proof**

An approved LLM stage can run reproducibly with budget, audit, validation, and review controls.

**Status**

Not started.

### §8D Branch and Deployment Assistance

**Outcome**

Hermes may eventually prepare branches or deployment evidence, but does not merge, approve, silently redeploy, or alter production contracts.

**Dependencies**

`§8A` through `§8C` as applicable, repository-specific approval, and Git workflow controls.

**Work**

- Define branch preparation boundaries.
- Define pull-request evidence requirements.
- Define deployment-assistance limits.
- Keep merge and production authority separate.

**High-reasoning gates**

- `§8D-G1` Branch Preparation Gate.
- `§8D-G2` Approved Deployment Assistance Gate.

**Required evidence**

Diff summary, validation output, exact path list, no-secret proof, deployment SHA, rollback SHA, and approval record.

**Completion proof**

Hermes can assist without becoming the authority that approves its own changes.

**Status**

Deferred.

## §9 WGU-Reddit Duplicate-Ingestion Risk

### §9A Early Ingestion-Authority Inspection

**Outcome**

The WGU-Reddit operational boundary is factually understood before any LLM or scheduler migration depends on it.

**Dependencies**

Read-only inspection authority for the relevant Mac and VPS scheduler surfaces.

**Work**

- Determine which local repository or repositories represent WGU-Reddit operations.
- Inspect current collectors, schedulers, source data, databases, downstream consumers, and duplicate execution risk.
- Confirm or reject the hypothesis that both Mac and VPS are fetching.
- Identify one authoritative fetcher plan and one disable/cutover plan.

**High-reasoning gates**

- `§9A-G1` WGU-Reddit Ingestion Authority Gate.

**Required evidence**

Repository map, launchd inventory, systemd timer inventory, running process inventory, database/source inventory, duplicate execution evidence, downstream consumer list, and proposed one-writer plan.

**Completion proof**

The portfolio knows whether duplicate ingestion is real, what it affects, and what decision is required to stop or preserve it.

**Status**

Partially complete during Work Session 3. The operational WGU-Reddit path on VPS was identified, Reddit Ops is active under user systemd, and canonical health was implemented. Current evidence does not show an unresolved active duplicate-writer cutover in the same way as Traderie, but final repository-boundary acceptance, scheduler documentation, exporter correction, and publication/security cleanup remain open.

### §9B WGU-Reddit LLM Pipeline Admission

**Outcome**

WGU-Reddit is either admitted as the first LLM reference candidate or deferred with specific blockers.

**Dependencies**

`§9A` ingestion authority inspection.

**Work**

- Resolve publication blockers including reported history-secret risk.
- Separate experimental, orphaned, QC, and production stages.
- Define provider/model, prompt versioning, structured outputs, audit artifacts, budgets, retries, and human review.
- Add tests, CI, `.env.example`, and repository control files.

**High-reasoning gates**

- `§9B-G1` WGU-Reddit Publication Readiness Gate.
- `§9B-G2` WGU-Reddit LLM Reference Candidate Gate.

**Required evidence**

Secret/history scan, stage inventory, prompt inventory, model/provider inventory, benchmark fixtures, test output, CI, dependency manifest, data boundary, and cost estimate.

**Completion proof**

The repository can be safely published or explicitly deferred, and one LLM stage can be selected for a controlled reference plan.

**Status**

Not started.

## §10 SJC Intel Early Follow-On Path

### §10A Deterministic Repository Admission

**Outcome**

SJC Intel is admitted as an early deterministic follow-on or deferred with explicit blockers.

**Dependencies**

Traderie reference lessons through at least `§7D`; earlier admission work may proceed in parallel.

**Work**

- Create SJC Intel control sheet and gate evidence.
- Verify deterministic workflows, migrations, retention, health, backup/restore, systemd units, tests, and generated-data boundaries.
- Decide whether SJC Intel becomes the first Hermes deterministic execution candidate after Traderie.

**High-reasoning gates**

- `§10A-G1` SJC Intel Admission Gate.
- `§10A-G2` Deterministic Follow-On Candidate Gate.

**Required evidence**

Repository status, migration list, validation output, test output, health export, retention docs, deploy docs, systemd units, backup/restore docs, source list, and scheduler plan.

**Completion proof**

SJC Intel has a bounded deployment plan that reuses Traderie-proven platform patterns.

**Status**

Moderate-detail planning. Current local evidence shows migrations, deploy docs, health export, retention tooling, and tests exist.

### §10B SJC Intel Deployment and Hermes Readiness

**Outcome**

SJC Intel proves deterministic workflow execution beyond Traderie and contributes logging/run-report patterns.

**Dependencies**

`§10A` admission and applicable Traderie reference outcomes.

**Work**

- Port exact-SHA deployment, health, backup, restore, and scheduler controls.
- Define deterministic source fetch contracts.
- Define review queue and retention behavior.
- Prove read-only then deterministic Hermes workflow execution if selected.

**Required evidence**

Workflow contracts, dry-run outputs, source fetch samples, health output, backup/restore proof, and scheduler disable/enable plan.

**Completion proof**

SJC Intel can run deterministically on the VPS without introducing duplicate schedulers or unbounded data growth.

**Status**

Not started.

## §11 WGU Catalog and Shared WGU Data Dependencies

### §11A Catalog Source Authority

**Outcome**

WGU Catalog becomes the clear canonical source for WGU catalog registry exports consumed by Atlas, WGU-Reddit, and BSDA Courses.

**Dependencies**

Repository admission and consumer contract review.

**Work**

- Admit WGU Catalog as a managed repository.
- Confirm raw PDF/text artifact boundaries and export policy.
- Define canonical export schemas, versioning, checksums, and consumer contracts.
- Decide what remains in WGU Atlas and what moves to WGU Catalog.

**High-reasoning gates**

- `§11A-G1` WGU Catalog Authority Gate.
- `§11A-G2` Consumer Contract Gate.

**Required evidence**

Export schemas, fixture tests, raw artifact policy, registry data inventory, consumer list, compatibility report, and rollback/export retention plan.

**Completion proof**

WGU data consumers can point to a versioned catalog export contract rather than hardcoded local paths.

**Status**

Moderate-detail planning. Current local evidence shows WGU Catalog is intended as the canonical catalog source and has export fixtures under development.

### §11B Shared WGU Data Cutovers

**Outcome**

WGU Atlas, BSDA Courses, and WGU-Reddit consume WGU Catalog through approved contracts.

**Dependencies**

`§11A` authority and consumer contract gate.

**Work**

- Replace direct local-path dependencies with environment-driven or package/export contracts.
- Add compatibility tests in consumers.
- Record consumer rollback paths.

**Required evidence**

Consumer import tests, before/after data counts, path scan, contract version, and rollback command.

**Completion proof**

At least one consumer validates against the canonical export without local-machine paths.

**Status**

Not started.

## §12 BSDA Courses Consumer Path

### §12A Consumer-Only Admission

**Outcome**

BSDA Courses is admitted as a consumer of WGU-Reddit and WGU Catalog data, not as an independent fetch authority.

**Dependencies**

WGU-Reddit ingestion authority and WGU Catalog source authority are understood.

**Work**

- Inventory LLM stages, deterministic stages, data inputs, and publication outputs.
- Remove hardcoded WGU-Reddit DB path fallbacks.
- Externalize model/provider configuration.
- Add cost accounting for LLM stages.
- Define human-review boundaries for final Reddit publication.

**High-reasoning gates**

- `§12A-G1` Consumer-Only Authority Gate.
- `§12A-G2` BSDA LLM Stage Gate.

**Required evidence**

Input contract, `.db` disposition, stage inventory, path scan, provider config, prompt versions, output schema, review gate, token/cost metadata, and tests.

**Completion proof**

BSDA Courses can consume approved upstream data without fetching or writing upstream authority.

**Status**

Light to moderate planning. Current local evidence includes a zero-byte ignored `data/reddit_wgu.db`; its intended disposition must be resolved before deployment planning.

## §13 WGU Atlas Read-Oriented Service Path

### §13A Atlas Admission and Catalog Boundary

**Outcome**

WGU Atlas is admitted as a public read-oriented site and possible mature LLM runtime reference after its catalog dependency is clarified.

**Dependencies**

`§11A` WGU Catalog authority or an accepted interim catalog mirror.

**Work**

- Confirm stable branch, deployment target, public data boundary, and site build process.
- Replace hardcoded WGU catalog or Reddit paths with contracts.
- Preserve provider-agnostic LLM runtime patterns where useful.
- Define QA-stage budgets, audit artifacts, and public labeling rules.

**High-reasoning gates**

- `§13A-G1` Atlas Publication and Data Boundary Gate.
- `§13A-G2` Atlas LLM Runtime Candidate Gate.

**Required evidence**

Branch/SHA status, build output, data inventory, catalog contract, path scan, LLM stage inventory, test output, and public labeling review.

**Completion proof**

Atlas can build from approved data contracts and has a bounded plan for any LLM-powered QA features.

**Status**

Light to moderate planning. Current local evidence shows active UI work on `homepage-redesign` and a catalog mirror tied to WGU Catalog transition.

## §14 Idle Hacking KB Sensitive LLM Workflow Path

### §14A Deferred Sensitive LLM Admission

**Outcome**

Idle Hacking KB is prepared for later admission after simpler deterministic and LLM patterns are proven.

**Dependencies**

Hermes LLM workflow model and sensitive-review gates.

**Work**

- Inventory live, historical, and draft LLM stages.
- Decouple cross-repo credentials.
- Decide whether draft prompt-only stages are implemented, archived, or deleted under approval.
- Preserve content-safety rules and `llm_annotation_is_not_truth`-style boundaries.
- Validate migrations, health, backup, restore, and deployment docs.

**High-reasoning gates**

- `§14A-G1` Idle Hacking Sensitive Review Gate.
- `§14A-G2` Draft Stage Disposition Gate.

**Required evidence**

Stage registry, prompt registry, provider/credential inventory, content-safety tests, migration validation, health output, backup/restore proof, and draft-stage decision table.

**Completion proof**

Idle Hacking KB has a clear safe subset for deployment planning or remains deferred with explicit blockers.

**Status**

Light planning. Current local evidence shows new migrations, deploy docs, LLM docs, and tests are being developed, with substantial dirty state.

## §15 IH Market Companion Deterministic Runtime Path

### §15A Browser and Runtime Supervision

**Outcome**

IH Market Companion becomes a later deterministic runtime reference for browser/API supervision, public feed health, and runtime recovery.

**Dependencies**

Traderie reference deployment and deterministic workflow execution patterns.

**Work**

- Admit repository and clarify public/private split.
- Define browser/runtime process supervision, restart behavior, health, backup, retention, and recovery.
- Keep trade execution advisory or separately gated.
- Prove public feed health and local/VPS parity.

**High-reasoning gates**

- `§15A-G1` Browser Runtime Gate.
- `§15A-G2` Trading Authority Gate, only if any execution authority is proposed.

**Required evidence**

Runtime process inventory, deploy docs, systemd units, health output, public/private contract, tests, recovery docs, and trading authority boundary.

**Completion proof**

The project can run deterministic public-feed workflows without exposing private chat, credentials, orders, holdings, or unsafe trading automation.

**Status**

Light planning. Current local evidence shows substantial active work on deploy docs, tests, runtime DB migrations, and public/private contracts.

## §16 Reckless Ben Restricted Path

### §16A No-Launch Governance

**Outcome**

Reckless Ben remains restricted and contributes approval/evidence patterns without becoming a production workload.

**Dependencies**

No production launch unless explicit newer authority changes the classification.

**Work**

- Preserve evidence-first and approval-gate patterns.
- Keep source material, legal/sensitive claims, and public outputs behind explicit review.
- Do not deploy or activate production workflows by default.
- Use its approval taxonomy as a reference for sensitive-review gates elsewhere.

**High-reasoning gates**

- `§16A-G1` Restricted Repository Gate.
- `§16A-G2` Launch Reclassification Gate, only if requested later.

**Required evidence**

Current machine spec, claim discipline rules, source separation, approval taxonomy, credential inventory, and no-launch confirmation.

**Completion proof**

The roadmap preserves useful patterns without creating accidental production authority.

**Status**

Restricted. Current posture: `NO_LAUNCH`.

## §17 Host Rebuild, Incident Response, and Disaster Recovery

### §17A Rebuild Plan

**Outcome**

The portfolio can rebuild the VPS from GitHub, Mac backups, and documented configuration without relying on mutable checkout state.

**Dependencies**

Exact-SHA deployment, backup/restore, credential inventory, and project data boundaries.

**Work**

- Document host bootstrap order.
- Record PostgreSQL install/configuration steps.
- Restore project databases from Mac backups.
- Recreate config files from safe examples and secure credential source.
- Re-clone repositories by approved SHA.
- Validate health and scheduler state before activation.

**High-reasoning gates**

- `§17A-G1` Host Rebuild Gate.

**Required evidence**

Backup inventory, restore drill, approved SHA registry, config variable inventory, service list, scheduler list, and validation checklist.

**Completion proof**

A documented rebuild procedure can recreate serviceable runtime state from non-VPS authorities.

**Status**

Not started.

### §17B Incident Response

**Outcome**

Failures have bounded response paths: observe, stop writes if needed, preserve evidence, restore or rollback, then resume only through gates.

**Dependencies**

Health and drift checks.

**Work**

- Define incident severity levels.
- Define stop-write and disable-timer procedures.
- Define backup preservation and restore decision points.
- Define post-incident review requirements.

**Required evidence**

Incident template, stop commands, rollback commands, restore commands, backup preservation evidence, and post-incident report.

**Completion proof**

An operator can respond to stale data, bad writes, backup failure, disk pressure, or deployment drift without improvising.

**Status**

Not started.

## §18 Sequencing Model

### §18A Hard Dependency Floor

These ordering constraints are hard:

1. VPS PostgreSQL foundation precedes PostgreSQL-backed production workloads.
2. Backup/restore proof precedes cutover or destructive work.
3. Exact approved SHA precedes deployment.
4. Read-only Hermes inspection precedes Hermes workflow execution.
5. Deterministic workflow execution precedes LLM workflow execution.
6. Scheduler Gate precedes service/timer activation.
7. Cutover approval precedes changing production authority.
8. WGU Catalog authority precedes broad WGU consumer cutovers.
9. WGU-Reddit ingestion authority inspection should precede any dependent BSDA or LLM production plan.
10. Reckless Ben remains `NO_LAUNCH` unless explicitly reclassified.

### §18B Recommended Default Order

1. Traderie reference deployment through operational acceptance.
2. WGU-Reddit duplicate-ingestion inspection in parallel as a risk task.
3. SJC Intel deterministic follow-on.
4. WGU Catalog authority and export contracts.
5. First LLM workflow reference, likely WGU-Reddit if blockers are resolved or WGU Atlas if a cleaner read-oriented LLM candidate is preferred.
6. BSDA Courses consumer-only path.
7. IH Market Companion browser/runtime path.
8. Idle Hacking KB sensitive LLM path.
9. Reckless Ben remains restricted.

### §18C Acceptable Alternative Orders

- SJC Intel can move directly after Traderie manual deployment proof if deterministic breadth is more valuable than waiting for Traderie operational activation.
- WGU Catalog can move earlier if WGU Atlas or BSDA Courses become the next priority.
- WGU-Reddit ingestion inspection should happen early regardless of its deployment order because duplicate fetch risk is operationally important.
- WGU Atlas may become the first LLM reference if read-oriented QA and provider abstraction are more useful than WGU-Reddit's operational risk.
- BSDA Courses should not move ahead of upstream authority decisions unless scoped strictly to local refactoring and contract preparation.

### §18D Selection Criteria for the Next Repository

Choose the next detailed plan based on:

- Operational risk reduction.
- Readiness and existing test/deploy foundation.
- Dependency leverage for other repositories.
- Public portfolio value.
- LLM budget and sensitive-review burden.
- Amount of hardcoded local path or credential decoupling work.
- Whether the work proves a new reusable portfolio pattern.

## §19 Ongoing Maintenance and Portfolio Quality

### §19A Continuous Standards Loop

**Outcome**

Portfolio standards evolve from real deployments without becoming stale templates.

**Dependencies**

Completed phase evidence and unresolved issue reports.

**Work**

- Promote lessons from deployments into shared standards.
- Update repository controls when gates pass, blockers change, approved SHAs change, or deviations are accepted.
- Keep public docs publication-safe.
- Keep private/local-only material out of public history.
- Review retention, backup, restore, health, CI, and public presentation periodically.

**Required evidence**

Changed standards, affected repositories, validation output, and unresolved issue list.

**Completion proof**

The roadmap and controls reflect current operating reality rather than historical plans.

**Status**

Ongoing. Work Sessions 3 and 4 produced reusable patterns for exact-SHA deployment, root-owned allowlisted systemd deployment, scoped migration sudo, canonical health producers, segmented runtime with per-segment `timeout`, objective progress monitoring (file mtime/size in addition to journal), health-timer-first activation, natural-run proof, one-writer rollback, unit-hash verification, and venv-path regression testing. A streamlined onboarding model (admission → one publication → one Codex production task → natural-run check → closeout) was exercised during Session 4 and proposed for formalization in the private workflow appendix. GPT desktop write-tool success is explicitly not treated as proof that a local file changed.

### §19B Self-Improvement Loop

**Outcome**

The portfolio can inspect its own evidence, propose safe changes, and prepare reviewable updates without silent production changes.

**Dependencies**

Hermes read-only inspection and branch-preparation gates.

**Work**

- Generate periodic drift, stale-data, backup, and standards-gap reports.
- Prepare bounded change proposals.
- Require review for schema, prompt, threshold, credential, permission, scheduler, deployment, or production-behavior changes.

**High-reasoning gates**

- `§19B-G1` Self-Improvement Authority Gate.

**Required evidence**

Report samples, proposed diff samples, validation plan, and approval boundaries.

**Completion proof**

Self-improvement produces reviewable work, not unreviewed production mutation.

**Status**

Deferred until reference deployments and read-only inspection are proven.

## §20 Current Next Work

1. Execute Work Session 5 from `TODO.md` using the streamlined model: one combined OpenCode admission/source-readiness task per workstream, routine direct git-steward publication, one Codex production task per workstream, passive natural-run acceptance, closeout.
2. Traderie production recovery — resolve pc_hc_nl timeout, restore healthy natural scheduled runs, perform controlled reboot proof.
3. Reddit Ops sanitized publication — reconstruct clean history excluding credential-bearing commit, publish reviewed backup units.
4. Reddit Ops production recovery — install reviewed backup units, create fresh backup, perform isolated restore drill, prove timer and reboot behavior.
5. SJC Intel admission readiness — one combined task covering authority, runtime, database, health, backup, deploy, scheduler transfer, rollback. Do not require cutover in Session 5 unless stabilization completes cleanly.
6. Documentation reconciliation and closeout.
