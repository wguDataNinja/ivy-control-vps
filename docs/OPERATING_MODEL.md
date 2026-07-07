# Operating Model

## Purpose

IvyControlVPS is the operational control plane for the VPS portfolio. The managed repositories remain separate projects with their own code, data, and roadmaps. Together they should present a cohesive standard of engineering, documentation, operations, and automation. Differences between repositories should be justified by their actual purpose rather than by habit.

## Living standards

Shared standards documented here are baselines, not blind templates. Every repository must be reviewed against its actual contents, runtime environment, data flows, workflows, and public presentation. Templates are starting points; they must evolve when new repositories, workflows, incidents, or operational needs expose gaps.

## Public and private documentation

Content tracked in Git must be polished and safe for publication.

Private working material belongs under `internal/`. This directory:

- Is not tracked by Git.
- May contain private operating notes, draft decisions, publication notes, and session logs.
- Is authoritative only according to the future private-note policy.
- Must not contain secrets merely because it is untracked.
- Is not synchronized by Git.

## GitHub and deployment model

The following high-level direction is agreed:

- GitHub is the shared public source of truth for tracked material.
- Mac and VPS will use approved commits.
- Automated agents should propose changes through branches and pull requests.
- Agents should not merge their own work.
- Direct production edits are not the intended workflow.

A detailed Git standard is still pending.

## Hermes and agents

The following high-level direction is agreed:

- Hermes is expected to orchestrate work across managed repositories.
- Hermes may invoke narrowly defined agents.
- Workflows should be defined independently of any single provider or model.
- Agent permissions, routing, and repository-local contracts are still pending.

## Documentation maintenance

A daily documentation loop is planned but not yet implemented. The intended workflow:

1. Inspect changes from the prior period.
2. Determine which documents are affected.
3. Update only the affected documents.
4. Propose changes in a pull request.
5. Do not merge automatically.

## Pending standards

The following areas are identified as requiring standards that have not yet been drafted or resolved:

- **Git workflow** — branch naming, commit conventions, merge policy.
- **Logging standard** — structured logging format, retention, and aggregation.
- **Agent/Hermes contract** — agent capabilities, permissions, and communication protocol.
- **Repository admission process** — criteria and gate for onboarding a new project.
- **Portfolio-level LLM strategy** — when and how LLMs are used operationally.
- **Repository-specific templates** — conventions for `README.md`, `AGENTS.md`, `.gitignore`, and other files tailored to project types.

These items are explicitly pending and should not be treated as resolved until a standard is drafted, reviewed, and approved.
