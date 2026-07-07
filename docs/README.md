# Documentation Index

This index is the operational map for agents and maintainers working with IvyControlVPS. It lists every document in the repository and serves as the entry point for understanding the repo's structure and purpose.

## Documents

| Document | Purpose |
|----------|---------|
| [`README.md`](../README.md) | Public repository overview — purpose, current stage, design principles |
| [`OPERATING_MODEL.md`](OPERATING_MODEL.md) | Operating model — public/private boundary, living standards, Git, deployment, agents, documentation maintenance |
| [`LOGGING_STANDARD.md`](LOGGING_STANDARD.md) | Three-layer logging standard — machine/runtime, agent work, and GPT/planning logs |
| [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) | Initial Git workflow — branch naming, commits, PRs, agents, VPS provisional rules |
| [`../agents/LOCAL_IMPLEMENTATION.md`](../agents/LOCAL_IMPLEMENTATION.md) | Detailed local implementation agent contract — required reading, task boundaries, editing rules, validation, logging, git behavior |
| [`../workflows/session-close.md`](../workflows/session-close.md) | Workflow for closing a session without losing important decisions |

## Future documentation

A provisional VPS/Hermes orchestration contract is the next planned document. Deeper workflow documents, project-specific standards, and process guides will be added as they are developed and approved. Each addition will be reviewed against actual operational need before inclusion.

## Reading order for a new maintainer or agent

1. `AGENTS.md` — router to the correct context
2. `agents/LOCAL_IMPLEMENTATION.md` — local agent contract (required reading for agents)
3. `README.md` — what this repository is and is not
4. `OPERATING_MODEL.md` — how the repository and portfolio are governed
5. `LOGGING_STANDARD.md` — logging conventions for machine, agent, and planning work
6. `GIT_WORKFLOW.md` — branch naming, commit messages, PRs, agent rules
7. `workflows/session-close.md` — closeout workflow (useful after any session)
