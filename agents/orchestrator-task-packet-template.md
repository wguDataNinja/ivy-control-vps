# Orchestrator Task Packet Template

**Role:** Reusable bounded-work template. The authoritative lifecycle remains
`docs/REPOSITORY_WORK_PROTOCOL.md`; the authority and permission boundary
remains `agents/HERMES_AGENT_CONTRACT.md` and
`agents/VPS_ORCHESTRATION.md`.

Use this template only for an explicitly dispatched Hermes Mode 0 task. Replace
every bracketed field. A packet does not grant authority beyond its delegation
envelope.

```markdown
# [Task ID] — [Short title]

**Status:** DISPATCHED
**Delegation envelope:** [envelope ID / approved roadmap section]

## Read First

- [target repository]/AGENTS.md
- [target repository]/ROADMAP.md §[section]
- [target repository]/CONTROL.md
- [relevant release gate / standard / prior result]

## Objective

[One bounded, observable outcome.]

## Context

[Verified facts, known uncertainty, and why this chunk is authorized now.]

## Scope

- [Allowed action]
- [Allowed action]

## Do Not

- [Prohibited action / boundary]
- Do not change production data, services, credentials, canonical authority, or Git state unless this packet explicitly and separately authorizes it.

## Delegation Target

- **Executor:** [OpenCode / Codex / Hermes subagent / other approved executor]
- **Repository / working tree:** [exact repository]
- **One task in flight:** Yes
- **Hermes implements directly?** [Yes / No] — if Yes, state the exception
  reason and additional review control per §3.5f Exception policy

## Allowed Paths

- [exact source/test/doc paths the executor may change]
- **Hermes artifact paths only:** [declared task/report/log/journal-proposal paths]

## Validation Requirements

- [command or inspection]
- [expected evidence]

## Result Report Requirements

Record objective, sources inspected, files changed, validation, verified facts,
uncertainty, blockers, Git state, and next handoff in [declared report path].
Create the required execution log in [declared log path].

## Checkpoint Rules

After completion, Hermes validates the execution report against the criteria
defined in `agents/HERMES_AGENT_CONTRACT.md` §3.5b. Required checks: result
report and log exist; validation evidence is present; changed files are in
scope; no stop condition or gate change occurred; and the next work remains
inside the envelope.

Hermes produces a validation report with one of these outcomes:
`HERMES_ACCEPT`, `HERMES_ACCEPT_WITH_NOTE`, `HERMES_REJECT`,
`NEEDS_BUDDY_REVIEW`, or `NEEDS_CODEX`. See
`agents/HERMES_AGENT_CONTRACT.md` §3.5c for outcome definitions.

## After Completion

Hermes may write the next packet only if the validation outcome permits
continuation (`HERMES_ACCEPT` or `HERMES_ACCEPT_WITH_NOTE`) and the envelope
still permits another task. Hermes writes only a factual
`PENDING_GPT_REVIEW` journal proposal; GPT/Buddy supplies acceptance, decisions,
lessons, and canonical promotion.
```
