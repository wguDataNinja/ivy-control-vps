# Documentation Index

This index is the operational map for agents and maintainers working with IvyControlVPS. It lists every document in the repository and serves as the entry point for understanding the repo's structure and purpose.

## Documents

### Core governance and operating model

| Document | Purpose |
|----------|---------|
| [`README.md`](../README.md) | Public repository overview — purpose, current stage, design principles |
| [`ROADMAP.md`](../ROADMAP.md) | Portfolio-wide roadmap — ingestion-first readiness campaign, shared VPS platform workstreams, and controlled cutover waves |
| [`OPERATING_MODEL.md`](OPERATING_MODEL.md) | Operating model — public/private boundary, living standards, Git, deployment, agents, documentation maintenance |
| [`RESIDENT_AGENT_MODEL.md`](RESIDENT_AGENT_MODEL.md) | Resident Agent Interface (RAI) architecture — why resident agents exist, file-backed bridge, verification principle, separation of interface from implementation |
| [`REPOSITORY_CONTROL_MODEL.md`](REPOSITORY_CONTROL_MODEL.md) | Portfolio repository-control model — governance mechanism, standards applicability, gate framework, approved SHA tracking |
| [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) | Git workflow — branch naming, commits, PRs, agents, VPS provisional rules, git-steward delegation |

### Standards and conventions

| Document | Purpose |
|----------|---------|
| [`PORTFOLIO_CONVENTIONS.md`](PORTFOLIO_CONVENTIONS.md) | Cross-repo conventions and VPS admission requirements — PostgreSQL naming, backup/restore, systemd, health contract, deployment prerequisites, gates, and stop conditions |
| [`HEALTH_CONTRACT.md`](HEALTH_CONTRACT.md) | Canonical portfolio health contract v2 — current-state, consecutive-failure, cumulative-failure, and recovery state; producer registry contract; alert boundaries |
| [`DATA_LIFECYCLE_STANDARD.md`](DATA_LIFECYCLE_STANDARD.md) | Portfolio data-lifecycle principles — data classes, retention, growth measurement, disk thresholds, health metrics |
| [`LOGGING_STANDARD.md`](LOGGING_STANDARD.md) | Three-layer logging standard — machine/runtime, agent work, and GPT/planning logs |
| [`LLM_TENETS.md`](LLM_TENETS.md) | Design tenets for auditable, constrained, portable, and data-efficient LLM systems |

### Operations and access

| Document | Purpose |
|----------|---------|
| [`VPS_ACCESS.md`](VPS_ACCESS.md) | VPS access procedures — SSH, SCP, desktop access, identity key management |
| [`VPS_ADMISSION_CHECKLIST.md`](VPS_ADMISSION_CHECKLIST.md) | VPS repository admission evidence checklist — required gates before any portfolio repository can be deployed |
| [`DATABASE.md`](DATABASE.md) | Database architecture and operations — PostgreSQL topology, schema ownership, migrations, backup/restore, and operation history |
| [`HERMES_OPERATOR_GUIDE.md`](HERMES_OPERATOR_GUIDE.md) | Hermes operator guide — bridge protocol, orientation, independent verification, file-based communication loop |

### Agent contracts

| Document | Purpose |
|----------|---------|
| [`../agents/VPS_ORCHESTRATION.md`](../agents/VPS_ORCHESTRATION.md) | VPS/Hermes orchestration contract — interaction modes (read-only inspection, bounded mutation, full production), approval boundaries, logging |
| [`../agents/LOCAL_IMPLEMENTATION.md`](../agents/LOCAL_IMPLEMENTATION.md) | Local implementation agent contract — rules for OpenCode, Codex, and similar agents operating from this repository |

### Health subsystem

| Document | Purpose |
|----------|---------|
| [`health/adapter-interface.md`](health/adapter-interface.md) | Health adapter interface contract — required schema for producer registration, normalized health fields |
| [`health/api-alert-boundaries.md`](health/api-alert-boundaries.md) | API alert boundary definitions — thresholds for freshness, failure counts, disk, memory, and database growth |
| [`health/portfolio-conformance-matrix.md`](health/portfolio-conformance-matrix.md) | Portfolio-wide health conformance matrix — which producers are registered, their current health semantic alignment, and gaps to v2 contract compliance |
| [`health/producer-registry.md`](health/producer-registry.md) | Registered health producers — exact producer-ids, current schema versions, and registration metadata |
| [`health/schemas/portfolio_health_schema.json`](health/schemas/portfolio_health_schema.json) | JSON Schema for portfolio health reports — validation target for all adapters |
| [`health/database/normalized_health_schema.sql`](health/database/normalized_health_schema.sql) | Normalized PostgreSQL schema for aggregated portfolio health |

### Traderie governance

| Document | Purpose |
|----------|---------|
| [`repos/traderie/CONTROL.md`](../repos/traderie/CONTROL.md) | Traderie governance control sheet — production authority, lifecycle state, approved SHA, unresolved gates |
| [`repos/traderie/RELEASE_GATES.md`](../repos/traderie/RELEASE_GATES.md) | Traderie release gate evidence — deployment proof, runtime gate status, health check results |
| [`repos/traderie/PHASE_B_CODEX_PACKET.md`](../repos/traderie/PHASE_B_CODEX_PACKET.md) | Traderie Phase B Codex execution packet — superseded; retained as historical execution evidence |
| [`repos/traderie/STATUS.md`](../repos/traderie/STATUS.md) | Traderie VPS status — deprecated; replaced by CONTROL.md. Retained as historical reference only |

### Reddit Ops governance

| Document | Purpose |
|----------|---------|
| [`repos/reddit-ops/CONTROL.md`](../repos/reddit-ops/CONTROL.md) | Reddit Ops governance control sheet — production authority, lifecycle state, unresolved gates |
| [`repos/reddit-ops/RELEASE_GATES.md`](../repos/reddit-ops/RELEASE_GATES.md) | Reddit Ops release gate evidence — frontier, idempotence, locking, migration, OAuth gates |
| [`repos/reddit-ops/CUTOVER_HISTORY.md`](../repos/reddit-ops/CUTOVER_HISTORY.md) | Reddit Ops PostgreSQL cutover chronology — two failed attempts, root cause, final cutover |
| [`repos/reddit-ops/STABILIZATION.md`](../repos/reddit-ops/STABILIZATION.md) | Reddit Ops stabilization checklist — 13 gates remaining to production-complete |
| [`repos/reddit-ops/RUNBOOK.md`](../repos/reddit-ops/RUNBOOK.md) | Reddit Ops operational runbook — health checks, manual run, rollback, drift detection |

### Workflows

| Document | Purpose |
|----------|---------|
| [`../workflows/session-close.md`](../workflows/session-close.md) | Session close workflow — preserving important decisions, closing without losing context |
| [`../_internal/GPT_ORCHESTRATED_WORKFLOW.md`](../_internal/GPT_ORCHESTRATED_WORKFLOW.md) | Private GPT-orchestrated workflow authority — numbered handoffs, gates, session logs, ad-hoc tasks, session close |
| [`../_internal/vps-inventory-and-runbook.md`](../_internal/vps-inventory-and-runbook.md) | Private VPS inventory and runbook — host identity, SSH access, workload map, capacity evidence, read-only procedures |

### Portfolio baseline

| Document | Purpose |
|----------|---------|
| [`PORTFOLIO_BASELINE.md`](PORTFOLIO_BASELINE.md) | Portfolio-wide repository baseline — inventory, current state, LLM inventory, standards gaps, sequencing |

## Reading order for a new maintainer or agent

1. `README.md` — what this repository is and is not
2. `OPERATING_MODEL.md` — how the repository and portfolio are governed
3. `RESIDENT_AGENT_MODEL.md` — resident-agent architecture and interface (RAI)
4. `REPOSITORY_CONTROL_MODEL.md` — how portfolio standards apply to each repository
5. Applicable portfolio standards (read per task):
   - `PORTFOLIO_CONVENTIONS.md` — shared technical conventions and VPS admission requirements
   - `HEALTH_CONTRACT.md` — health reporting contract and producer registry
   - `DATA_LIFECYCLE_STANDARD.md` — retention, pruning, storage thresholds
   - `LOGGING_STANDARD.md` — logging for machine, agent, and planning work
   - `GIT_WORKFLOW.md` — Git branch naming, commits, agent rules
   - `LLM_TENETS.md` — LLM system design principles
6. Repository control sheet — `repos/<repo>/CONTROL.md` for repo-specific evidence, exceptions, blockers, and current VPS admission status
7. Detailed gate evidence or phase packet only when the task requires gate-specific detail
8. For GPT-orchestrated session work, read `_internal/GPT_ORCHRONESTED_WORKFLOW.md` (private) for numbered handoffs, gate packets, session logging, and session close
9. For VPS operational work, first read `_internal/vps-inventory-and-runbook.md` (private) for host identity, SSH access, workload map, current capacity, and read-only assessment procedures
10. For Hermes bridge interaction, read `HERMES_OPERATOR_GUIDE.md` — bridge protocol, orientation flow, independent verification

## Authority model

### Hierarchy

`ROADMAP.md` is the portfolio-wide execution authority. Per-repo `CONTROL.md` files govern individual repository lifecycle, production authority, and gate status. Portfolio standards (`PORTFOLIO_CONVENTIONS.md`, `HEALTH_CONTRACT.md`, `DATA_LIFECYCLE_STANDARD.md`, etc.) define cross-repo conventions that CONTROL.md records must comply with or explicitly deviate from.

```
ROADMAP.md (portfolio-wide execution authority)
  └── repos/<repo>/CONTROL.md (per-repo lifecycle, gates, deviations)
        └── standards/ (cross-repo conventions)
```

A repo `CONTROL.md` may grant a standards exception; the standards may not override a CONTROL.md exception. `ROADMAP.md` may override a CONTROL.md gate only during an authorized campaign phase.

### Active vs historical materials

Every document in `docs/` is either active authority, supporting reference, or explicitly marked historical/superseded. Old-tree documents (from the predecessor `ivy-control/vps/` path) are not present in this repository. Any reference to an old-tree file is a historical marker, not an active-reading link. Documents in `repos/<repo>/` with "deprecated" or "superseded" status (e.g., `STATUS.md`) are retained for provenance only.

### CONTROL.md role

Each managed repository has a control sheet at `repos/<repo>/CONTROL.md` that records:
- lifecycle state and production authority;
- approved SHA and deployment status;
- standards compliance state and accepted deviations;
- current blockers and next authorized work.

A repository without a CONTROL.md is not yet under active portfolio governance.

### Portfolio registry

The portfolio registry is a derived/aggregated view of all CONTROL.md records, not a separate static authority. It is generated by a tool (e.g., `tools/portfolio_registry.py` or extended `ingestion_dashboard.py`) that reads CONTROL.md files and canonical health outputs. The registry does not replace CONTROL.md as the per-repo source of truth.

### Session artifacts

`_internal/outbox/` contains ignored session artifacts — execution packets, evidence files, and intermediate reports produced during GPT-orchestrated work. These files are not durable Git authority. They are retained for provenance and traceability but must not be treated as active standards, policy, or configuration. The current live document set in `docs/` is the authoritative source.

## Predecessor tree

The `ivy-control/vps/` directory in the old `ivy-control` repository contains historical planning documents, completed execution evidence, and reference material that has not been promoted here.

The current authority set lives in this repository. Old-tree material is reference-only unless explicitly cited by a current CONTROL.md, RELEASE_GATES.md, or phase packet. No old-tree document overrides an active document in this repository.

Private VPS access details, workload map, and read-only assessment procedures are consolidated at:

`_internal/vps-inventory-and-runbook.md`

Read that file before any VPS inspection work.

## New documents

A new document must serve a distinct durable authority role that no existing document can absorb. Before creating a file, identify its unique purpose, why an existing document cannot hold the material, and which current document it supersedes or complements. Index it here on creation.


## Current Operating Emphasis

The documentation set describes the full intended control model, but the immediate program priority is narrower.

### Completed foundation (Sessions 1–8)

- **Sessions 1–2:** Bootstrap GPT workflow, Reddit Ops migration cutover, PostgreSQL frontier
- **Session 3:** Health contract v2, Traderie production readiness, Reddit Ops closeout
- **Session 4:** Traderie cutover (Mac→VPS), portfolio ingestion-admission matrix, Reddit Ops backup/restore remediation
- **Session 5:** Ingestion-first roadmap rewrite, platform productization, PostgreSQL provisioning, isolated restore proof, reboot persistence proof, Idle Hacking safe-ingestion boundary
- **Session 6:** Phase 0 health CLI, Hermes VPS data estate audit, Idle Hacker KB and IH Market capacity archive
- **Session 7:** Hermes bridge bootstrap, Codex VPS-1/VPS-2 capacity recovery and execution, Git publication
- **Session 8:** Complete Git cleanup (both repos reconciled and committed), Session 5 reconstruction, Git publication assessment, ingestion dashboard prototype

### Active priorities

1. **Stabilize ingestion health visibility.** Health contract v2 is defined; producers are registered (Traderie, Reddit Ops). Build the portfolio aggregator and normalized views so all workloads have observable current-state health.
2. **Complete remaining stabilization gates.** Reddit Ops has 13 unresolved stabilization gates (STABILIZATION.md). Close these to move from `PRODUCTION_ACTIVE` to `PRODUCTION_COMPLETE`.
3. **Admit SJC Intel.** Next deterministic admission candidate — has systemd units, 11 migrations, health scripts, `.env.example`. Admission packet is ready from Session 5.
4. **Publish sanitized Reddit Ops history.** Local history contains a credential-bearing root commit. Cherry-pick clean commits onto a sanitized publication branch and push.
5. **Continue repository publication and standards work** after the ingestion foundation is observable and stable.
6. **Keep Hermes read-only** for production operations today. Plan a later reviewed pull-request workflow for bounded repository maintenance.

### Monitoring and operations

- Verify all VPS ingestion workloads and identify the sole scheduler and writer for each.
- Confirm recent successful database writes and source-data freshness.
- Monitor disk, memory, database growth, backups, and restore readiness on the small Hetzner VPS.
- Treat workloads as deployed but untrusted until health and recovery evidence are visible.

### Decision record

| Date | Decision | Source |
|------|----------|--------|
| 2026-07-12 | Traderie approved SHA `e5ebd0f` deployed via systemd timer | Session 5 |
| 2026-07-12 | PostgreSQL provisioned on VPS; Idle Hacking KB boundaries defined | Session 5 |
| 2026-07-13 | Idle Hacker KB capacity archive completed; Hermes estate audit completed | Session 6 |
| 2026-07-14 | Hermes bridge operational as read-only resident assistant | Session 7 |
| 2026-07-14 | Codex VPS-1 (capacity archive) and VPS-2 (live execution) completed | Session 7 |
| 2026-07-15 | Both repos fully reconciled and committed; Sessions 1–7 durably recorded | Session 8 |
