# Operating Model

## Purpose

IvyControlVPS is the operational control plane for the VPS portfolio. The managed repositories remain separate projects with their own code, data, and roadmaps. Together they should present a cohesive standard of engineering, documentation, operations, and automation. Differences between repositories should be justified by their actual purpose rather than by habit.

## Living standards

Shared standards documented here are baselines, not blind templates. Every repository must be reviewed against its actual contents, runtime environment, data flows, workflows, and public presentation. Templates are starting points; they must evolve when new repositories, workflows, incidents, or operational needs expose gaps.

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

An initial Git workflow is defined in `docs/GIT_WORKFLOW.md` (provisional). Repository protection settings, VPS deployment details, and Hermes permissions remain explicitly unresolved.

## Hermes and agents

The following high-level direction is agreed:

- Hermes is expected to orchestrate work across managed repositories.
- Hermes may invoke narrowly defined agents.
- Workflows should be defined independently of any single provider or model.

Portfolio-level principles for designing LLM workflows are defined in `docs/LLM_TENETS.md`. These tenets establish the baseline for auditable interfaces, constrained workflows, model portability, minimal context, and deterministic preprocessing.

A provisional VPS/Hermes orchestration contract is defined in `agents/VPS_ORCHESTRATION.md`. The actual VPS path, deployment mechanism, credentials, destructive permissions, and private-context provisioning remain unresolved.

## Documentation maintenance

A daily documentation loop is planned but not yet implemented. The intended workflow:

1. Inspect changes from the prior period.
2. Determine which documents are affected.
3. Update only the affected documents.
4. Propose changes in a pull request.
5. Do not merge automatically.

## Pending standards

The following areas are identified as requiring standards that have not yet been drafted or resolved:

- **Git workflow** — initial standard defined in `docs/GIT_WORKFLOW.md` (provisional). Repository protection settings, VPS deployment details, and Hermes permissions remain pending.
- **Logging standard** — initial three-layer model defined in `docs/LOGGING_STANDARD.md` (provisional). Detailed retention, automation, aggregation, and repository-specific implementation remain pending.
- **VPS/Hermes orchestration contract** — provisional contract defined in `agents/VPS_ORCHESTRATION.md`. The actual VPS path, deployment mechanism, credentials, destructive permissions, and private-context provisioning remain unresolved.
- **Repository admission process** — criteria and gate for onboarding a new project.
- **Portfolio-level LLM strategy** — foundational design tenets are defined in `docs/LLM_TENETS.md`. Operational adoption, benchmarking, provider interfaces, validation patterns, and repository-specific implementation remain pending.
- **Repository-specific templates** — conventions for `README.md`, `AGENTS.md`, `.gitignore`, and other files tailored to project types.

These items are explicitly pending and should not be treated as resolved until a standard is drafted, reviewed, and approved.
