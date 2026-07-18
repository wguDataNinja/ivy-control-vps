# Operating Model

**Status:** Current authority. The project is in implementation and operational-hardening mode — no longer documenting a future VPS model. It now governs a live VPS with multiple production workloads, PostgreSQL, archives, health evidence, deployment records, Hermes, and repository admission.

## Purpose

IvyControlVPS is the portfolio control plane for the Ivy engineering portfolio. It owns:

- portfolio operational governance, topology, and standards;
- health contracts, backup/restore, archive and retention rules;
- repository admission, production topology, and lifecycle state;
- deployment evidence, exact revision tracking, and privileged execution packets;
- Hermes governance and cross-repository operational status;
- portfolio roadmap and sequencing.

Managed repositories remain separate projects with their own code, data, implementation schemas, runtime behavior, tests, and local workflows. Together they present a cohesive standard of engineering, documentation, operations, and automation. Differences between repositories are justified by their actual purpose rather than by habit.

Current work is implementation mode, where task-specific Buddy authorization controls each change. Later production admission activates stricter production operating rules. This document defines the operating model; `ROADMAP.md` owns current portfolio execution priorities and `repos/<repo>/CONTROL.md` owns current managed-repository state. `docs/PORTFOLIO_BASELINE.md` is a dated assessment reference, not the live authority.

## Portfolio dimensions

Ivy Control serves repositories; repositories do not exist to satisfy Ivy Control. The portfolio therefore keeps these dimensions independent:

| Dimension | Question | Authority |
|---|---|---|
| Portfolio value | Why does this asset matter? | `docs/PORTFOLIO_UNIVERSE.md` |
| Operational priority | Where does uncertainty create loss now? | `ROADMAP.md` |
| Lifecycle / support state | What operational support is authorized? | `repos/<repo>/CONTROL.md` |
| Evidence confidence | What current proof exists, and is it still valid? | `docs/HEALTH_CONTRACT.md` and dated evidence |
| Exposure class | What may be public, private, restricted, or absent from VPS operation? | Portfolio universe and applicable control record |

**Not admitted does not mean unimportant.** Admission is an operational capability decision: it says an asset is ready for a specified support model, such as source-only review, a batch procedure, or production runtime. It is not a portfolio ranking, quality score, or requirement that a valuable asset deploy to the VPS.

**P0 means uncertainty creates loss.** P0 work protects irreplaceable data, collection continuity, recovery confidence, or another condition where lack of current evidence can cause material loss. It is not a measure of a project's novelty, polish, or personal interest.

## Living standards

Shared standards documented here are baselines, not blind templates. Every repository must be reviewed against its actual contents, runtime environment, data flows, workflows, and public presentation. Templates are starting points; they must evolve when new repositories, workflows, incidents, or operational needs expose gaps.

## Operational support classification

Workflows are classified by the support model they may use. This classification is operational only and must not be used to infer portfolio value.

| # | Category | Meaning |
|---|----------|---------|
| 1 | **VPS-ready now** | Deterministic, script exists, no credential/browser/quota barrier |
| 2 | **VPS-ready after shadow/parity** | Needs dual-write validation window before cutover |
| 3 | **VPS-ready after gate design** | Needs approval-gate process before automation |
| 4 | **VPS-ready after hardening** | Needs extraction script, credential isolation, or quota management |
| 5 | **Local/manual long term** | Requires human judgment, legal sensitivity, or paid LLM budget gate |
| 6 | **Deferred** | Not yet scoped; explicitly parked |
| 7 | **Unclear** | Architecture decision required before classification |

## Ingestion-first admission

Portfolio planning distinguishes ingestion operational readiness from full public repository maturity. It also distinguishes both from the decision to acknowledge an asset in the portfolio universe.

**Ingestion operational readiness** is the minimum evidence required to move authoritative data collection to the VPS safely: one scheduler, one writer, deterministic entrypoints, visible health, backup/restore proof, rollback path, exact deployed revision, and documented cutover authority.

**Full public repository maturity** remains required for long-term portfolio quality, but broader polish, UI/dashboard refinement, downstream LLM features, and presentation work should not block a safe ingestion cutover when the operational evidence is sufficient.

Eligible ingestion repositories should be prepared in parallel where their source files and authority boundaries do not conflict. Production cutovers should still occur in controlled waves sized to the portfolio's monitoring maturity, rollback complexity, and review bandwidth.

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

In implementation mode, agents may operate under task-specific Buddy authorization. During this phase:

- Buddy authorizes bounded implementation work (edits, tests, documentation, staging, non-production proof runs).
- Strong Codex handles architecture, privileged execution, and irreversible operations through explicit packets.
- Hermes operates as a read-only resident inspector — no production write, systemd, database, or destructive authority.
- Future production activation will apply stricter separation: all changes flow through branches and pull requests; agents do not merge their own work; Hermes may gain recurring inspection and PR authority through a separate gate.

VPS filesystem layout separates concerns:
- **Code** in `apps/{project}/` — Git working trees, throwable and re-cloned from GitHub
- **Persistent data** in `data/{project}/` — raw captures, exports, staging artifacts
- **Configuration** in `config/` — per-project `.env` files outside Git
- **Logs** in `logs/{project}/` — service-level runtime output
- **Backups** in `backups/postgres/{project}/` — database dumps and manifests

No mutable production data lives inside Git working trees. Working trees are disposable.

The local-development Git workflow is defined in `docs/GIT_WORKFLOW.md`. Portfolio-wide Git conventions (repository naming, commit style, PR policy, history sanitization, agent Git authority, exact-SHA deployment, tags and releases) remain pending and will be drafted as a follow-on standard. Hermes is installed as a read-only resident agent; see `docs/HERMES_OPERATOR_GUIDE.md`.

## Hermes and agents

The following high-level direction is agreed:

- Hermes is installed as a read-only resident VPS assistant. It inspects, summarizes, and recommends. It does not have production write authority. See `docs/HERMES_OPERATOR_GUIDE.md`.
- Hermes may invoke narrowly defined agents for bounded tasks.
- Workflows should be defined independently of any single provider or model.

Portfolio-level principles for designing LLM workflows are defined in `docs/LLM_TENETS.md`. These tenets establish the baseline for auditable interfaces, constrained workflows, model portability, minimal context, and deterministic preprocessing.

A provisional VPS/Hermes orchestration contract is defined in `agents/VPS_ORCHESTRATION.md`. Hermes is installed; its read-only authority is established. Broader deployment automation, credentials management, destructive permissions, and private-context provisioning remain unresolved.

## Work ownership

| Owner | Work class | Examples |
|---|---|---|
| **Buddy** | Authority and risk decisions | License choice, publication scope, gate approvals, destructive-operation approval, cross-repo policy |
| **OpenCode** | Bounded low-risk implementation | Repo documentation updates, inert service templates, validation commands, tests, path parameterization, report consolidation, readiness packets |
| **Strong Codex** | Architecture, privileged execution, and irreversible decisions | PostgreSQL schema design, cutover choreography, backup/restore standard, health contracts, production deployment, reboot proof, history rewrite planning, destructive cleanup design |
| **Hermes** (resident agent) | Read-only VPS inspection, monitoring, drift detection, PR proposal | Scheduled scans, health checks, SHA drift detection, structured PR creation |

OpenCode agents receive bounded tasks with explicit scope, allowed files, and validation criteria. They do not invent architecture, mutate production state, or approve their own work. Strong Codex resolves architecture-level contradictions and designs fragile cross-repo boundaries. Orchestration agents observe and propose but never execute production changes directly.

## Documentation maintenance

A daily documentation loop is planned but not yet implemented. The intended workflow:

1. Inspect changes from the prior period.
2. Determine which documents are affected.
3. Update only the affected documents.
4. Propose changes in a pull request (or commit directly when explicitly authorized).
5. Do not merge automatically.

## Pending standards

The following areas have defined standards; remaining implementation details are noted:

- **Git workflow** — local-development standard defined in `docs/GIT_WORKFLOW.md`. Portfolio-wide Git conventions (repository naming, commit style, PR policy, history sanitization, agent Git authority, exact-SHA deployment, tags and releases) remain pending.
- **Logging standard** — three-layer model defined in `docs/LOGGING_STANDARD.md`. Detailed retention automation, aggregation, and repository-specific implementation remain pending.
- **VPS/Hermes orchestration contract** — defined in `agents/VPS_ORCHESTRATION.md`. Hermes read-only authority is resolved; recurring portfolio-review, branch creation, and PR authority are future stages.
- **Repository admission process** — defined in `docs/REPOSITORY_CONTROL_MODEL.md`. The six-gate model applies to every managed repository. Repository-specific gate evidence is recorded in `repos/<repo>/RELEASE_GATES.md`.
- **Data lifecycle and storage** — foundational principles defined in `docs/DATA_LIFECYCLE_STANDARD.md`. Repository-specific retention windows, pruning configurations, and growth thresholds are set in each repo's `CONTROL.md` or local retention policy.
- **Portfolio-level LLM strategy** — foundational design tenets defined in `docs/LLM_TENETS.md`. Operational adoption, benchmarking, provider interfaces, validation patterns, and repository-specific implementation remain pending.
- **Repository-specific templates** — conventions for `README.md`, `AGENTS.md`, `.gitignore`, and other files tailored to project types.
- **Private orchestration workflow** — GPT-orchestrated roadmap work, numbered handoffs, high-reasoning gates, and session-close procedures are defined in `_internal/GPT_ORCHESTRATED_WORKFLOW.md`.

None of these should be treated as final — they evolve with operational experience. Repository protection settings, VPS deployment details, and Hermes recurring-loop behavior remain explicitly future work.
