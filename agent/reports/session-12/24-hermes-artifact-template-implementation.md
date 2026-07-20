# Session 12 — Task 24: Hermes Artifact Template Implementation

**Date:** 2026-07-19
**Status:** TEMPLATES_IMPLEMENTED

---

## Files Created

| File | Lines | Purpose |
|---|---|---|
| `agents/hermes-validation-report-template.md` | 105 | Hermes records whether an execution result is acceptable before allowing continuation |
| `agents/codex-escalation-context-template.md` | 93 | Hermes creates a bounded reasoning request when a Codex capability is authorized |

---

## Design Validation

### Hermes validation report — why it is distinct

| Existing template | Why it does not cover validation |
|---|---|
| `orchestrator-task-packet-template.md` | Defines what the execution agent should do, not whether it was done correctly |
| `GATE_PACKET_TEMPLATE.md` | For human/Codex decisions about roadmap gates, not mechanical checkpoint verification |
| `REPORT.md` (per-repo) | Execution agent reports what it did; Hermes validation evaluates whether it was done correctly |
| `TASK_TEMPLATE.md` | General task definition, not a structured checklist with accept/reject outcomes |

The validation report fills a distinct lifecycle position: between execution
report and continuation. No existing template occupies this position.

### Codex escalation context — why it is distinct

| Existing template | Why it does not cover escalation |
|---|---|
| `codex-handoff/SKILL.md` | Defines HOW to call Codex (input format, command shape), but not WHAT to ask |
| `GATE_PACKET_TEMPLATE.md` | For internal review decisions, not Codex-bound requests with specific authority limits |
| `ROADMAP_SECTION_TEMPLATE.md` | Content structure, not operational request format |

The escalation context fills the gap between "a Codex capability exists" and
"Codex is invoked." It prevents the skill from being used with open-ended
"fix this" prompts by requiring specific questions, constraints, and authority
boundaries.

---

## Overlap Check

| Check | Result |
|---|---|
| Overlap with task packet template (`orchestrator-task-packet-template.md`) | **None** — no Objective, Scope, or Delegation Target fields in either new template |
| Overlap with execution report templates (`REPORT.md`) | **None** — no "files changed", "commands executed", "decisions made" fields |
| Overlap with `GATE_PACKET_TEMPLATE.md` | **None** — no pass condition, reviewer result, or evidence summary in the gate packet sense |
| Overlap between the two new templates | **None** — validation report checks past execution; escalation context defines future reasoning request |
| Claims that Codex is autonomous | **None** — escalation context explicitly lists "Codex may not authorize execution, approve continuation, or replace Hermes validation" |
| Claims that templates enable behavior | **None** — both templates reference the contract (§3.5d, §3.5b) as the authority; templates are operational forms |

---

## Remaining Work

| Item | Phase | Status |
|---|---|---|
| Migrate `codex-handoff` skill from old `ivy-control` repo to `ivy-control-vps/.opencode/skills/` | Before pilot | **Pending** — requires file copy, no modification |
| Enable `roadmap_repair` capability on pilot repository | Pilot setup | **Pending** — requires CONTROL.md edit |
| Run controlled pilot: full escalation chain | Pilot | **Pending** — requires Phases 1-4 complete |
| Decision on `agent/orchestration/` directory convention | Phase 2 follow-up | **Deferred** — not needed until orchestration runs produce artifacts |
| Create per-repo `hermes.codex_capabilities` in CONTROL.md | Phase 3 | **Pending** — schema defined in Phase 1, not yet populated |

---

## Template Locations

```
ivy-control-vps/agents/
├── HERMES_AGENT_CONTRACT.md     ← Phase 1 (contract)
├── HERMES_ROADMAP_SUFFICIENCY_GATE.md  ← Gate contract
├── HERMES_OPERATOR_GUIDE.md     ← Phase 1 (role update)
├── VPS_ORCHESTRATION.md         ← Phase 1 (role update)
├── orchestrator-task-packet-template.md  ← Reused (Phase 1 update)
├── hermes-validation-report-template.md  ← NEW (Phase 2)
└── codex-escalation-context-template.md  ← NEW (Phase 2)
```

---

## References

- `agents/hermes-validation-report-template.md` — Created
- `agents/codex-escalation-context-template.md` — Created
- `agent/reports/session-12/23-hermes-artifact-template-design-preflight.md` — Design preflight (source for this task)
- `agents/HERMES_AGENT_CONTRACT.md` — Contract (validation outcomes §3.5c, capabilities §3.5d)
- `agents/orchestrator-task-packet-template.md` — Existing task packet template (checked for overlap)
- `_internal/templates/GATE_PACKET_TEMPLATE.md` — Existing gate template (checked for overlap)
