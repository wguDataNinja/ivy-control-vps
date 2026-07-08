# Operating Model

## Purpose

IvyControlVPS is the operational control plane for the VPS portfolio. The managed repositories remain separate projects with their own code, data, and roadmaps. Together they should present a cohesive standard of engineering, documentation, operations, and automation. Differences between repositories should be justified by their actual purpose rather than by habit.

## Living standards

Shared standards documented here are baselines, not blind templates. Every repository must be reviewed against its actual contents, runtime environment, data flows, workflows, and public presentation. Templates are starting points; they must evolve when new repositories, workflows, incidents, or operational needs expose gaps.

## Workflow classification

Workflows are classified by VPS readiness. Every roadmap must classify each meaningful workflow into exactly one category:

| # | Category | Meaning |
|---|----------|---------|
| 1 | **VPS-ready now** | Deterministic, script exists, no credential/browser/quota barrier |
| 2 | **VPS-ready after shadow/parity** | Needs dual-write validation window before cutover |
| 3 | **VPS-ready after gate design** | Needs approval-gate process before automation |
| 4 | **VPS-ready after hardening** | Needs extraction script, credential isolation, or quota management |
| 5 | **Local/manual long term** | Requires human judgment, legal sensitivity, or paid LLM budget gate |
| 6 | **Deferred** | Not yet scoped; explicitly parked |
| 7 | **Unclear** | Architecture decision required before classification |

## Public and private documentation

Content tracked in Git must be polished and safe for publication.

Private working material belongs under `_internal/` (the canonical path). Legacy `internal/` exists and is preserved temporarily.

`_internal/`:
- Is a separate local-only Git repository with no remote.
- Is excluded from the public repository via `.gitignore` and pre-commit/pre-push hooks. It remains visible on disk — ignoring is not hiding.
- May contain private operating notes, draft decisions, publication notes, and session logs.
- Is authoritative only according to the future private-note policy.
- Must not contain secrets merely because it is private.
- Is not synchronized by Git.

## GitHub and deployment model

The following high-level direction is agreed:

- GitHub is the shared public source of truth for tracked material.
- Mac and VPS will use approved commits.
- Automated agents should propose changes through branches and pull requests.
- Agents should not merge their own work.
- Direct production edits are not the intended workflow.

Development happens on Mac. GitHub distributes approved code. VPS checkouts are deployment targets only. No direct VPS code editing.

VPS filesystem layout separates concerns:
- **Code** in `apps/{project}/` — Git working trees, throwable and re-cloned from GitHub
- **Persistent data** in `data/{project}/` — raw captures, exports, staging artifacts
- **Configuration** in `config/` — per-project `.env` files outside Git
- **Logs** in `logs/{project}/` — service-level runtime output
- **Backups** in `backups/postgres/{project}/` — database dumps and manifests

No mutable production data lives inside Git working trees. Working trees are disposable.

An initial Git workflow is defined in `docs/GIT_WORKFLOW.md` (provisional). Repository protection settings, VPS deployment details, and Hermes permissions remain explicitly unresolved.

## Hermes and agents

The following high-level direction is agreed:

- Hermes is expected to orchestrate work across managed repositories.
- Hermes may invoke narrowly defined agents.
- Workflows should be defined independently of any single provider or model.

Portfolio-level principles for designing LLM workflows are defined in `docs/LLM_TENETS.md`. These tenets establish the baseline for auditable interfaces, constrained workflows, model portability, minimal context, and deterministic preprocessing.

A provisional VPS/Hermes orchestration contract is defined in `agents/VPS_ORCHESTRATION.md`. The actual VPS path, deployment mechanism, credentials, destructive permissions, and private-context provisioning remain unresolved.

## Work ownership

| Owner | Work class | Examples |
|---|---|---|
| **Buddy** | Authority and risk decisions | License choice, publication scope, gate approvals, destructive-operation approval, cross-repo policy |
| **OpenCode** | Bounded low-risk implementation | Repo documentation updates, inert service templates, validation commands, tests, path parameterization, report consolidation |
| **Strong Codex** | Architecture and irreversible decisions | PostgreSQL schema design, cutover choreography, backup/restore standard, health contracts, history rewrite planning, destructive cleanup design |
| **Orchestration agents** (future Hermes) | Monitoring, drift detection, PR proposal | Scheduled scans, health checks, SHA drift detection, structured PR creation |

OpenCode agents receive bounded tasks with explicit scope, allowed files, and validation criteria. They do not invent architecture, mutate production state, or approve their own work. Strong Codex resolves architecture-level contradictions and designs fragile cross-repo boundaries. Orchestration agents observe and propose but never execute production changes directly.

## Documentation maintenance

A daily documentation loop is planned but not yet implemented. The intended workflow:

1. Inspect changes from the prior period.
2. Determine which documents are affected.
3. Update only the affected documents.
4. Propose changes in a pull request (or commit directly when explicitly authorized).
5. Do not merge automatically.

## Pending standards

The following areas are identified as requiring standards that have not yet been drafted or resolved:

- **Git workflow** — initial standard defined in `docs/GIT_WORKFLOW.md` (provisional). Repository protection settings, VPS deployment details, and Hermes permissions remain pending.
- **Logging standard** — initial three-layer model defined in `docs/LOGGING_STANDARD.md` (provisional). Detailed retention, automation, aggregation, and repository-specific implementation remain pending.
- **VPS/Hermes orchestration contract** — provisional contract defined in `agents/VPS_ORCHESTRATION.md`. The actual VPS path, deployment mechanism, credentials, destructive permissions, and private-context provisioning remain unresolved.
- **Repository admission process** — defined in `docs/REPOSITORY_CONTROL_MODEL.md`. The six-gate model (Portfolio Admission through Operational Activation) applies to every managed repository. Repository-specific gate evidence is recorded in `repos/<repo>/RELEASE_GATES.md`.
- **Data lifecycle and storage** — foundational principles are defined in `docs/DATA_LIFECYCLE_STANDARD.md`. Repository-specific retention windows, pruning configurations, and growth thresholds are set in each repo's `CONTROL.md` or local retention policy.
- **Portfolio-level LLM strategy** — foundational design tenets are defined in `docs/LLM_TENETS.md`. Operational adoption, benchmarking, provider interfaces, validation patterns, and repository-specific implementation remain pending.
- **Repository-specific templates** — conventions for `README.md`, `AGENTS.md`, `.gitignore`, and other files tailored to project types.
- **Private orchestration workflow** — GPT-orchestrated roadmap work, numbered handoffs, high-reasoning gates, and session-close procedures are defined in `_internal/GPT_ORCHESTRATED_WORKFLOW.md`. That document is the private authority; this public document describes only the agent taxonomy.

These items are explicitly pending and should not be treated as resolved until a standard is drafted, reviewed, and approved.
