# IvyControlVPS

Portfolio control plane for governing and improving a collection of independent engineering assets through shared standards, evidence-based operations, Git workflows, and bounded human/agent collaboration.

## What it is

IvyControlVPS is the operational hub for a collection of related but independent projects. It provides shared conventions, evidence routes, and workflows that let each project receive the support it actually needs without forcing every project into a VPS service, database, scheduler, or common codebase.

The repository does not contain application code for any single project. Instead it tracks:

- **Shared standards** — conventions for deployment, logging, documentation, and repository structure that projects adopt as baselines, not templates to be copied blindly.
- **Workflows** — reusable, iteratively validated processes for common operations such as deployment, session closeout, and health checks.
- **Documentation** — the operating model, documentation index, and growing body of process guides that describe how the portfolio is governed.
- **Per-project control** — `repos/<project>/CONTROL.md` and `RELEASE_GATES.md` files track each managed project's authorized support, gates, exceptions, and current operational state.

It does **not** own application code, mutable production data, or the portfolio value of a repository. Admission is an operational support decision, not a portfolio ranking.

## Start here

An engineer new to the control plane should read:

1. [`ROADMAP.md`](ROADMAP.md) — current execution priorities and sequencing.
2. [`docs/OPERATING_MODEL.md`](docs/OPERATING_MODEL.md) — mission, boundaries, roles, and independent portfolio dimensions.
3. [`docs/PORTFOLIO_UNIVERSE.md`](docs/PORTFOLIO_UNIVERSE.md) — known assets and their portfolio relationship.
4. [`docs/REPOSITORY_CONTROL_MODEL.md`](docs/REPOSITORY_CONTROL_MODEL.md) — managed repository controls and support gates.
5. [`docs/REPOSITORY_WORK_PROTOCOL.md`](docs/REPOSITORY_WORK_PROTOCOL.md) and [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md) — how changes are made and promoted.
6. [`docs/HEALTH_CONTRACT.md`](docs/HEALTH_CONTRACT.md) — health/evidence semantics when a task concerns an operational workload.
7. The relevant `repos/<project>/CONTROL.md` — current repository-specific authority.

[`docs/README.md`](docs/README.md) classifies the rest of the documentation into active authority, supporting technical reference, historical material, and private workflow context.

## Current stage

This repository is in controlled stabilization and authority-alignment. Core control, workflow, health, and backup foundations exist; the immediate priority is reducing P0 operational uncertainty before broad portfolio migration or automation.

## Design principles

- **Standards support, not bureaucracy.** Shared conventions exist to reduce friction across the portfolio. Every standard is a starting point that evolves when a real project, incident, or operational gap exposes a need.
- **Iterative validation.** Workflows are drafted, tested against real project needs, and refined. No workflow is considered final until it has been exercised.
- **Git-based source of truth.** Tracked material lives in Git. Proposed changes flow through branches and pull requests.
- **Public by default.** All tracked content is intended to be publication-safe. Private working notes, session logs, and unresolved design drafts belong in the untracked `_internal/` tree (legacy `internal/` also exists and is preserved temporarily).
