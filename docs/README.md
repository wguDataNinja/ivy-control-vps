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
| [`../_internal/GPT_ORCHESTRATED_WORKFLOW.md`](../_internal/GPT_ORCHESTRATED_WORKFLOW.md) | Private GPT-orchestrated workflow authority — numbered handoffs, gates, session logs, ad-hoc tasks, session close |
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
7. For GPT-orchestrated session work, read `_internal/GPT_ORCHESTRATED_WORKFLOW.md` (private) for numbered handoffs, gate packets, session logging, and session close
8. For VPS operational work, first read `_internal/vps-inventory-and-runbook.md` (private) for host identity, SSH access, workload map, current capacity, and read-only assessment procedures

## Predecessor tree

The `ivy-control/vps/` directory in the old `ivy-control` repository contains historical planning documents, completed execution evidence, and reference material that has not been promoted here.

The current authority set lives in this repository. Old-tree material is reference-only unless explicitly cited by a current CONTROL.md, RELEASE_GATES.md, or phase packet. No old-tree document overrides an active document in this repository.

Private VPS access details, workload map, and read-only assessment procedures are consolidated at:

`_internal/vps-inventory-and-runbook.md`

Read that file before any VPS inspection work.

## New documents

A new document must serve a distinct durable authority role that no existing document can absorb. Before creating a file, identify its unique purpose, why an existing document cannot hold the material, and which current document it supersedes or complements. Index it here on creation.
