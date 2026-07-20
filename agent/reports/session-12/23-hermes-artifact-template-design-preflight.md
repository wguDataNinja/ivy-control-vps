# Session 12 — Task 23: Hermes Artifact Template Design Preflight

**Date:** 2026-07-19
**Status:** TEMPLATE_DESIGN_READY

---

## Documents Reviewed

| Document | Role |
|---|---|
| `_internal/templates/TASK_TEMPLATE.md` | Private general task template |
| `_internal/templates/GPT_SESSION_LOG_TEMPLATE.md` | Private session narrative |
| `_internal/templates/GATE_PACKET_TEMPLATE.md` | Private high-reasoning gate packet |
| `_internal/templates/ROADMAP_SECTION_TEMPLATE.md` | Private roadmap section template |
| `agents/orchestrator-task-packet-template.md` | Public Hermes task packet template |
| `agents/HERMES_AGENT_CONTRACT.md` | Hermes contract (validation lifecycle, outcomes, capabilities) |
| `agents/HERMES_OPERATOR_GUIDE.md` | Hermes operator role boundaries |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | Artifact lifecycle, result report fields |
| `docs/REPOSITORY_CONTROL_MODEL.md` | CONTROL.md schema |
| `_internal/GPT_ORCHESTRATED_WORKFLOW.md` | Private workflow (result report spec, artifact conventions) |
| `/Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/SKILL.md` | Codex invocation skill (input/output format, command shape) |
| `palworld-kb/agent/templates/PROMPT.md` | Per-repo agent prompt template |
| `palworld-kb/agent/templates/REPORT.md` | Per-repo agent report template |
| `sts-workbench/agent/templates/PROMPT.md` | Per-repo agent prompt template |
| `sts-workbench/agent/templates/REPORT.md` | Per-repo agent report template |

---

## 1. Existing Template Inventory

### 1.1 Private templates (`_internal/templates/`)

| Template | Purpose | Hermes-relevant? |
|---|---|---|
| `TASK_TEMPLATE.md` | General task definition (objective, context, work requested, boundaries, validation, completion condition) | **Indirectly** — Hermes task packets serve a similar role but are Hermes-specific. This template is a general pattern for any agent. |
| `GPT_SESSION_LOG_TEMPLATE.md` | Session narrative (decisions, rationale, rejected approaches, open questions) | **No** — session logs are GPT-level, not Hermes-level |
| `GATE_PACKET_TEMPLATE.md` | High-reasoning gate evidence (decision requested, evidence, pass condition, reviewer result) | **No** — gates are for human/Codex review, not Hermes checkpoint validation |
| `ROADMAP_SECTION_TEMPLATE.md` | Roadmap section structure (north star, current state, phases) | **No** — content definition, not operational artifact |

### 1.2 Public templates (`agents/`)

| Template | Purpose | Hermes-relevant? |
|---|---|---|
| `orchestrator-task-packet-template.md` | Hermes Mode 0 task packet (objective, scope, paths, validation, checkpoint rules) | **Yes** — already updated in Phase 1. Covers task packets. |

### 1.3 Per-repository templates (`agent/templates/`)

| Template | Purpose | Hermes-relevant? |
|---|---|---|
| `PROMPT.md` (palworld-kb, sts-workbench) | Execution agent prompt (objective, constraints, deliverables) | **No** — execution agent templates, used independently of Hermes |
| `REPORT.md` (palworld-kb, sts-workbench) | Execution agent result report (changes, decisions, validation, risks, next task) | **Yes** — covers execution reports. Reusable as-is. |

### 1.4 Codex invocation skill

| Skill | Purpose | Hermes-relevant? |
|---|---|---|
| `codex-handoff/SKILL.md` | Invoke Codex with input file, capture output to file. Defines invocation mechanics (command shape, preflight, completion report). | **Yes** — defines HOW Codex is called but not WHAT the prompt should contain. |

---

## 2. Reuse/Extend/Create Decisions

| Artifact | Existing coverage | Decision | Rationale |
|---|---|---|---|
| Task packet | `agents/orchestrator-task-packet-template.md` | **Reuse as-is** | Already updated in Phase 1 with validation outcomes. No further changes needed. |
| Execution report | `REPORT.md` (per-repo), `_internal/GPT_ORCHESTRATED_WORKFLOW.md` §11 | **Reuse existing** | Both the per-repo REPORT.md templates and the private workflow already define result report format. Creating a Hermes-specific report template would duplicate existing conventions. |
| Hermes validation report | **None** | **Create new** | No existing template covers a structured 5-point checkpoint checklist with accept/reject outcomes. The existing `GATE_PACKET_TEMPLATE.md` is for human/Codex gate review, not mechanical Hermes validation. The existing task packet template references validation but does not define the validation artifact itself. |
| Codex escalation context | `codex-handoff/SKILL.md` defines invocation mechanics but not content structure | **Create new** | The skill defines HOW to call Codex (input file format, command shape) but not WHAT to ask. Without a structured context template, escalations risk becoming "Codex, fix this" — exactly what the capability model prevents. The context template is the guard. |
| Codex output | **None** | **Do NOT create** | Codex output structure varies by capability. The escalation context template should specify the expected output format per capability. Adding a Codex output template would create a third artifact where the context template can define the output contract. |

### 2.1 Summary

| Action | Count |
|---|---|
| Reuse existing | 2 (task packet template, execution report templates) |
| Create new | 2 (validation report, escalation context) |
| Do NOT create | 1 (Codex output — covered by context template) |

---

## 3. Proposed Artifact Schemas

### 3.1 Hermes validation report template

**File:** `agents/hermes-validation-report-template.md`

**Purpose:** Hermes writes one validation report per delegated task. It records
the 5-point checkpoint review and produces a structured outcome.

**Proposed fields:**

```
# Hermes Validation Report

**Task:** [task ID]
**Envelope:** [envelope ID]
**Task packet:** [path to 01-*-packet.md]
**Execution report:** [path to 02-*-execution.md]

## 1. Artifact completeness
- Result report exists? [PASS / FAIL]
- Contains required fields? [PASS / FAIL]
- Details: [what was checked]

## 2. Validation evidence
- Required tests run? [PASS / FAIL / NOT_APPLICABLE]
- Results present and passing? [PASS / FAIL]
- Details: [evidence reviewed]

## 3. Scope compliance
- Changed files within allowed paths? [PASS / FAIL]
- Scope boundary respected? [PASS / FAIL]
- Details: [paths checked]

## 4. Stop conditions
- New blockers appeared? [NONE / BLOCKER_IDENTIFIED]
- Gate changes occurred? [NONE / GATE_CHANGED]
- Details: [conditions checked]

## 5. Claim verification
- Claims supported by evidence? [PASS / FAIL]
- Unexplained claims? [NONE / ISSUES_FOUND]
- Details: [claims verified]

## 6. Outcome
- **Result:** [HERMES_ACCEPT / HERMES_ACCEPT_WITH_NOTE / HERMES_REJECT /
  NEEDS_BUDDY_REVIEW / NEEDS_CODEX]
- Notes: [observations for ACCEPT_WITH_NOTE, defects for REJECT, what
  Buddy/Codex would resolve for escalation outcomes]

## 7. Next action
- [Continue / Stop / Escalate to Buddy / Escalate to Codex]
- Remaining tasks in envelope: [N]
```

**Why this is not covered by existing templates:**
- `GATE_PACKET_TEMPLATE.md` is for human/Codex decisions about roadmap gates,
  not mechanical checkpoint verification
- `REPORT.md` templates are for execution agents to report what they did, not
  for Hermes to evaluate whether it was done correctly
- This template is a **procedural checklist**, not a narrative report

### 3.2 Codex escalation context template

**File:** `agents/codex-escalation-context-template.md`

**Purpose:** Hermes produces this artifact when it determines a Codex
capability is needed (NEEDS_CODEX outcome). It structures the problem so Codex
receives bounded questions with clear constraints, not open-ended "fix this"
requests.

**Proposed fields:**

```
# Codex Escalation Context

**Capability:** [roadmap_repair / architecture_review /
  implementation_blocker_review / production_change_review]
**Envelope:** [envelope ID]
**Repository:** [target repository]

## 1. Trigger condition
- What condition did Hermes detect?
- What is the NEEDS_CODEX outcome reason?

## 2. Problem statement
- What is the specific question or decision Codex should address?
- Hermes CANNOT resolve because: [architecture reasoning required /
  cross-repo design conflict / missing boundary / tradeoff analysis]

## 3. Current state
- Verified facts: [what Hermes knows to be true]
- Relevant artifacts: [task packet, execution report, validation report paths]
- CONTEXT: [read first — roadmap section, CONTROL.md, prior decisions]

## 4. Specific questions Codex must answer
- [Question 1 — bounded, specific, not open-ended]
- [Question 2 — bounded, specific, not open-ended]

## 5. Constraints
- What Codex must NOT do: [no implementation, no file changes, no scope
  expansion, no bypassing gates]
- Cost/scope boundaries: [fast vs strong model, effort limit]

## 6. Expected output format
Codex should produce a structured markdown document with:
1. Direct answers to each specific question
2. Options considered and why each was accepted or rejected
3. Risks introduced by the recommended approach
4. Assumptions made during analysis
5. Missing information Codex wishes it had

## 7. Authority limits
Codex may:
- [evaluate options, recommend approaches, identify risks, propose roadmap
  changes, analyze failure patterns]

Codex may NOT:
- [modify files, authorize changes, bypass gates, expand scope, make human
  business decisions]
```

**Why this is not covered by the existing codex-handoff skill:**
- The skill defines invocation mechanics (input file header, command shape,
  preflight checks, completion report) — the HOW
- This template defines the content structure (what to ask, what to constrain,
  what output format to demand) — the WHAT
- They are complementary. The skill provides the mechanism; the context
  template provides the governance.

### 3.3 Relationship between templates

```
Task packet template (orchestrator-task-packet-template.md)
  → defines what execution agent should do
  → leads to execution report (REPORT.md template)

Execution report (REPORT.md template / per-repo)
  → execution agent writes what was done
  → leads to Hermes validation

Hermes validation report (new template)
  → Hermes evaluates evidence
  → [ACCEPT] → continue
  → [NEEDS_CODEX] → leads to escalation

Codex escalation context (new template)
  → Hermes structures the problem for Codex
  → Buddy approves
  → Codex-handoff skill invokes Codex
  → Codex produces output (format defined by context template §6)
```

---

## 4. Codex Handoff Skill Relationship

### 4.1 Current state

The `codex-handoff` skill exists at:
`/Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/SKILL.md`

It is an OpenCode-local skill, not a Hermes capability. It defines:
- Input file format (handoff header + output path)
- Preflight checks
- Exact command shape
- Completion report

### 4.2 Reuse decision

**Reuse the skill as-is for invocation mechanics.** The skill does not need to
be wrapped, extended, or duplicated for Hermes. When escalation is needed:

1. Hermes produces the `codex-escalation-context-template.md` artifact
2. Buddy approves the escalation
3. OpenCode reads the context artifact, uses it as the prompt input to the
   codex-handoff skill
4. The skill invokes Codex with the context artifact as input
5. Codex writes output to the declared path
6. OpenCode reconciles the output
7. Hermes evaluates the reconciled output

### 4.3 Migration required

The skill must be copied from the old `ivy-control` repo to
`ivy-control-vps/.opencode/skills/codex-handoff/` before the pilot. The skill
itself is 99 lines and requires no modification — just a file copy.

### 4.4 What remains separate

| Concern | Lives in | Reason |
|---|---|---|
| Invocation mechanics | `codex-handoff/SKILL.md` | Defines HOW to call Codex |
| Escalation context format | `codex-escalation-context-template.md` | Defines WHAT to ask Codex |
| Capability policy | `CONTROL.md` `hermes.codex_capabilities` | Defines WHEN Codex may be used |
| Capability definitions | `HERMES_AGENT_CONTRACT.md` §3.5d | Defines purpose and authority limits |

---

## 5. Ownership Model

### 5.1 Confirmed ownership

| Artifact | Lives in | Created by | Consumed by |
|---|---|---|---|
| Task packet | Target repo declared paths | Hermes | Execution agent |
| Execution report | Target repo declared paths | Execution agent | Hermes |
| Hermes validation report | Target repo declared paths | Hermes | Journal, next-delegation decision |
| Codex escalation context | Target repo declared paths | Hermes | Buddy (approval), OpenCode (invocation) |
| Codex output | Target repo declared paths | Codex (via codex-handoff) | OpenCode (reconciliation), Hermes (evaluation) |
| Task packet template | `agents/` (ivy-control-vps) | — | Hermes |
| Validation report template | `agents/` (ivy-control-vps) | — | Hermes |
| Escalation context template | `agents/` (ivy-control-vps) | — | Hermes |
| Codex invocation skill | `.opencode/skills/` (ivy-control-vps) | — | OpenCode |

### 5.2 Exceptions

| Exception | Rationale |
|---|---|
| Codex output is not templated | The escalation context template defines the expected output format per capability. A separate Codex output template would be a third artifact duplicating what the context template already specifies. |
| Per-repo REPORT.md templates are not replaced | They already cover execution reports adequately. A Hermes-specific report template would create duplicate conventions. |

---

## 6. Recommended Implementation Sequence

### Phase 2a: Create validation report template

| Step | Detail |
|---|---|
| File | `agents/hermes-validation-report-template.md` |
| Content | 7 sections as defined in §3.1 |
| Effort | ~40 lines |
| Depends on | Phase 1 (contract defines outcomes and checklist criteria) |

### Phase 2b: Create escalation context template

| Step | Detail |
|---|---|
| File | `agents/codex-escalation-context-template.md` |
| Content | 7 sections as defined in §3.2 |
| Effort | ~50 lines |
| Depends on | Phase 1 (contract defines capabilities) |

### Phase 2c: Migrate codex-handoff skill

| Step | Detail |
|---|---|
| Source | `/Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/` |
| Destination | `ivy-control-vps/.opencode/skills/codex-handoff/` |
| Effort | 2 files, 5 minutes (copy, no modification) |
| Depends on | Nothing |

### NOT in Phase 2

| Item | Reason |
|---|---|
| Codex output template | Escalation context template defines output format |
| Task packet template changes | Already updated in Phase 1 |
| Per-repo REPORT.md changes | Existing templates are adequate |
| Private template changes | `_internal/templates/` templates are for different purposes |

---

## 7. Open Decisions

| Decision | Options | Recommendation |
|---|---|---|
| Should the validation report template include per-check severity (critical/major/minor) or just PASS/FAIL? | Binary vs. severity | **Start with binary PASS/FAIL.** Severity can be added if needed after pilot. |
| Should the escalation context template specify the Codex model (fast/strong)? | Yes vs. no | **Yes, as a constraint field** — the capability definition should specify whether fast or strong Codex is appropriate. Start with strong for all capabilities. |
| Should templates live in `agents/` (public) or `_internal/templates/` (private)? | Public vs. private | **Public (`agents/`).** They are operational templates, not private orchestration mechanics. Following the existing pattern of `orchestrator-task-packet-template.md`. |
| Should the validation report template include a "re-check after rework" loop field? | Yes vs. no | **Defer.** The initial template assumes single-pass validation. Rework loops can be added after the pilot if needed. |

---

## 8. Summary

| Question | Answer |
|---|---|
| How many new templates needed? | **2** — validation report and escalation context |
| Can any existing templates cover these? | **No** — no existing template covers a structured 5-point checkpoint with accept/reject outcomes, and no existing template structures what Hermes asks Codex to do |
| Task packet template changes needed? | **No** — already updated in Phase 1 |
| Codex output template needed? | **No** — escalation context template defines the expected output format |
| codex-handoff skill changes needed? | **No** — the skill is reused as-is for invocation mechanics. Only a file copy is needed for migration. |
| Implementation effort | 2 templates (~90 lines total) + 1 skill copy (~5 min) |

---

## References

- `_internal/templates/TASK_TEMPLATE.md` — Private task template (compared for overlap)
- `_internal/templates/GATE_PACKET_TEMPLATE.md` — Private gate template (compared for overlap)
- `agents/orchestrator-task-packet-template.md` — Existing task packet template (already updated)
- `agents/HERMES_AGENT_CONTRACT.md` — Hermes contract (validation outcomes from §3.5c, capabilities from §3.5d)
- `palworld-kb/agent/templates/REPORT.md` — Per-repo execution report template (reused as-is)
- `sts-workbench/agent/templates/REPORT.md` — Per-repo execution report template (reused as-is)
- `/Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/SKILL.md` — Codex invocation skill (reused as-is)
- `agent/reports/session-12/22-hermes-contract-phase1-implementation.md` — Phase 1 completion report
