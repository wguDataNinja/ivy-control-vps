# Documentation Index

This index is the operational map for agents and maintainers working with IvyControlVPS. It lists every document in the repository and serves as the entry point for understanding the repo's structure and purpose.

## Documents

| Document | Purpose |
|----------|---------|
| [`README.md`](../README.md) | Public repository overview — purpose, current stage, design principles |
| [`OPERATING_MODEL.md`](OPERATING_MODEL.md) | Operating model — public/private boundary, living standards, Git, deployment, agents, documentation maintenance |
| [`LOGGING_STANDARD.md`](LOGGING_STANDARD.md) | Three-layer logging standard — machine/runtime, agent work, and GPT/planning logs |
| [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) | Initial Git workflow — branch naming, commits, PRs, agents, VPS provisional rules |
| [`LLM_TENETS.md`](LLM_TENETS.md) | Design tenets for auditable, constrained, portable, and data-efficient LLM systems |
| [`PORTFOLIO_CONVENTIONS.md`](PORTFOLIO_CONVENTIONS.md) | Cross-repo conventions — PostgreSQL naming, backup/restore, systemd, health contract, Gates, deployment stop conditions |
| [`REPOSITORY_CONTROL_MODEL.md`](REPOSITORY_CONTROL_MODEL.md) | Portfolio repository-control model — governance mechanism, standards applicability, gate framework, approved SHA tracking |
| [`DATA_LIFECYCLE_STANDARD.md`](DATA_LIFECYCLE_STANDARD.md) | Portfolio data-lifecycle principles — data classes, retention, growth measurement, disk thresholds, health metrics |
| [`../agents/VPS_ORCHESTRATION.md`](../agents/VPS_ORCHESTRATION.md) | Provisional VPS/Hermes orchestration contract — role, delegation, approval boundaries, logging |
| [`../workflows/session-close.md`](../workflows/session-close.md) | Workflow for closing a session without losing important decisions |
| `repos/` | Per-project status files — current phase, gates, blockers, deployment state. Read by ivy-control agents before acting on a project. |

## Reading order for a new maintainer or agent

1. `README.md` — what this repository is and is not
2. `OPERATING_MODEL.md` — how the repository and portfolio are governed
3. `REPOSITORY_CONTROL_MODEL.md` — how portfolio standards apply to each repository
4. Applicable portfolio standards (read per task):
   - `PORTFOLIO_CONVENTIONS.md` — shared technical conventions
   - `DATA_LIFECYCLE_STANDARD.md` — retention, pruning, storage thresholds
   - `LOGGING_STANDARD.md` — logging for machine, agent, and planning work
   - `GIT_WORKFLOW.md` — Git branch naming, commits, agent rules
   - `LLM_TENETS.md` — LLM system design principles
5. Repository control sheet — `repos/<repo>/CONTROL.md` when working with a specific managed repository
6. Detailed gate evidence or phase packet only when the task requires gate-specific detail
7. For VPS operational work, first read `_internal/vps-inventory-and-runbook.md` (private) for host identity, SSH access, workload map, current capacity, and read-only assessment procedures

## Old-tree cross-reference

The predecessor VPS authority tree at `ivy-control/vps/` (in the old `ivy-control` repository) contains documents that remain authoritative for this portfolio until promoted here. This table classifies every old-tree artifact:

| Old path | Classification | New path or note |
|----------|---------------|------------------|
| `vps/vps-host.md` | PROMOTE NOW — canonical VPS host identity, workloads, disk state | `_internal/vps-inventory-and-runbook.md` (private) consolidates operational details |
| `vps/shared-conventions.md` | PARTIALLY PROMOTED — §1-3, §5-7, §9-10, §12-17 not yet in new repo | `docs/PORTFOLIO_CONVENTIONS.md` contains promoted subset (§2-3 PG, §5 systemd, §6 health, §7 gates, §8 deploy stop) |
| `vps/DEPLOYMENT_WORKFLOW.md` | PROMOTE NOW — canonical deployment workflow | No equivalent in new repo |
| `vps/repo-operating-standard.md` | PARTIALLY PROMOTED — §1-5, §8 concepts incorporated | No direct equivalent for §1 required doc set, §9 Admission Gate |
| `vps/github-readiness-checklist.md` | PROMOTE NOW — GitHub promotion gate | No equivalent in new repo |
| `vps/IMPLEMENTATION_PROGRAM.md` | PROMOTE NOW — active work queue | No equivalent in new repo |
| `vps/VPS_MIGRATION_STATUS.md` | PROMOTE NOW — per-repo migration tracker | No equivalent in new repo |
| `vps/postgres/` (templates, env ref, project files) | KEEP PRIVATE / REFERENCE ONLY — inert templates, no secrets | Reference design; live state in DATABASE_AUTHORITY_GATE report |
| `vps/worker-control/reports/` (19 reports) | PROMOTE NOW — active gate evidence, Git forensics, execution reports | No reports mechanism in new repo yet |
| `vps/archive/` (full tree) | HISTORICAL EVIDENCE — well-organized, replacement authorities documented | Referenced only; not promoted |
| `vps/README.md` | PARTIALLY PROMOTED — old VPS doc index | Concepts incorporated in this file |
| `vps-worker-control/` | HISTORICAL EVIDENCE | Archived in old tree |

**Key finding:** The old tree CANNOT yet be archived. Eight critical document classes lack equivalents in this repository. See `_internal/vps-inventory-and-runbook.md` §14 for the archive-readiness assessment.

## VPS access

VPS host identity, SSH access, workload map, current capacity evidence, and read-only assessment procedures are documented privately:

`_internal/vps-inventory-and-runbook.md`

Read this file before any VPS inspection work. It consolidates operational details from the authoritative old-tree documents and provides safe read-only inspection commands.

## New documents

A new document must serve a distinct durable authority role that no existing document can absorb. Before creating a file, identify its unique purpose, why an existing document cannot hold the material, and which current document it supersedes or complements. Index it here on creation.
