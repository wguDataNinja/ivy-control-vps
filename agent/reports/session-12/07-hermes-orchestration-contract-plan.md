# Session 12 — Task 12: Hermes Orchestration Contract Implementation Plan

**Date:** 2026-07-19
**Status:** COMPLETED — implementation plan, no files modified
**Predecessor:** Task 11 — Hermes Roadmap Sufficiency Gate Preflight

---

## 1. Executive Summary

This report defines the smallest safe implementation required to establish
Hermes as a governed roadmap-driven orchestrator. It converts the architectural
conclusions from Tasks 10 and 11 into a concrete plan.

**Seven deliverables:**

| # | Deliverable | Key decision |
|---|---|---|
| 1 | Hermes contract changes | New §3.5a in `HERMES_AGENT_CONTRACT.md` — explicit may/may not |
| 2 | Roadmap sufficiency contract | Formal checklist in `REPOSITORY_CONTROL_MODEL.md` §Per-repo roadmap |
| 3 | Failure behavior | `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` with 7-field report |
| 4 | Codex relationship | Manual bridge handoff; no automation yet |
| 5 | OpenCode boundary | Existing task packet template is sufficient with minor field alignment |
| 6 | Palworld pilot design | Read-only diagnostic pilot — does not delegate implementation |
| 7 | Implementation sequence | 5 ordered steps, no code changes, no new documents |

**Guiding principle:** The goal is a Hermes that knows when it has enough
information to safely coordinate work, not a more autonomous Hermes.

---

## 2. Current Hermes Model Assessment

### 2.1 What Hermes currently can do

From `agents/HERMES_AGENT_CONTRACT.md` and `agents/VPS_ORCHESTRATION.md`:

| Action | Currently authorized | Where defined |
|---|---|---|
| Read CONTROL.md and derive permissions | Yes | HERMES_AGENT_CONTRACT.md §3.1-3.2 |
| Inspect repository state | Yes | HERMES_AGENT_CONTRACT.md §3.3 |
| Report findings | Yes | HERMES_AGENT_CONTRACT.md §3.3 |
| Create task packets (Mode 0) | Yes, with explicit delegation envelope | HERMES_AGENT_CONTRACT.md §3.5 |
| Delegate one bounded task | Yes, inside envelope | HERMES_AGENT_CONTRACT.md §3.5 |
| Checkpoint after delegation | Yes | HERMES_AGENT_CONTRACT.md §3.5 |
| Validate roadmap sufficiency | **No** — not defined anywhere | Gap |
| Stop for insufficient roadmap | **No** — not a recognized stop condition | Gap |
| Request Codex clarification | **No** — not defined | Gap |

### 2.2 What the proposed model adds

| New responsibility | Type | Impact |
|---|---|---|
| Read approved roadmaps | Clarification | Already implicit; make explicit |
| Validate roadmap sufficiency | New gate | Pre-delegation check |
| Create bounded task packets | Clarification | Already exists; align with sufficiency gate |
| Delegate implementation | Clarification | Already exists |
| Collect reports | Clarification | Already exists |
| Maintain orchestration state | New responsibility | Track which tasks are delegated, completed, blocked |
| Detect insufficient roadmaps | New stop condition | Before Mode 0 entry |
| Escalate to Codex/Buddy | Clarification | Already exists; formalize the trigger |

### 2.3 What explicitly does NOT change

- Hermes still does not invent architecture
- Hermes still does not silently resolve unclear requirements
- Hermes still does not perform major design decisions
- Hermes still does not delegate ambiguous work
- Hermes still does not write code, Git branches, production data, services,
  databases, credentials, or canonical documents
- Hermes still requires an explicit delegation envelope for Mode 0

---

## 3. Proposed Hermes Contract Changes

### 3.1 New §3.5a in `HERMES_AGENT_CONTRACT.md`

Add a new section after the existing §3.5 (Artifact-only orchestration gate):

```
### 3.5a Pre-delegation roadmap sufficiency validation

Before Hermes creates any task packet or enters Mode 0 delegation, it must
validate that the roadmap section referenced in the delegation envelope is
sufficient for an execution agent to succeed by following instructions alone.

#### Sufficiency checklist

A roadmap section is sufficient for orchestration when it contains:

| Field | Required | Purpose |
|---|---|---|
| Execution chunk goal | Yes | Agent needs a bounded, observable outcome |
| Worker tasks (bounded) | Yes | Unbounded tasks invite architecture interpretation |
| Inputs (files, data, authority references) | Yes | Agent cannot discover inputs independently |
| Outputs (expected files, evidence) | Yes | Required for verification |
| Validation criteria | Yes | How completion is verified |
| Dependencies | Recommended | Risk of blocked work mid-delegation |
| Exit gate or acceptance review | Recommended | Ensures review at chunk boundary |
| Agent assignment model | Recommended | Not every chunk is OpenCode-suitable |
| Risks and unknowns | Recommended | Helps agent know when to stop |

#### Outcomes

If all required fields are present and clear: `SUFFICIENT_FOR_ORCHESTRATION`.
Hermes may proceed to create a task packet and delegate.

If any required field is missing or ambiguous:
`ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION`. Hermes must stop, produce a
structured report (see §3.5b), and escalate to Buddy. Hermes may not delegate.

#### Prohibited behavior

- Hermes must not infer, guess, or invent missing fields
- Hermes must not substitute its own interpretation for unclear acceptance
  criteria
- Hermes must not delegate work that an OpenCode agent cannot complete by
  following explicit instructions
- Hermes must not silently downgrade a required field to recommended
```

### 3.2 New §3.5b — Failure report template

The `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` report must contain:

```
## ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION

**Repository:** [name]
**Roadmap section:** [section reference]
**Delegation envelope:** [envelope ID]

### Missing decisions
- [list of decisions that must be made before delegation]

### Ambiguous requirements
- [list of requirements that are unclear or underspecified]

### Unclear dependencies
- [list of dependencies that are missing or uncertain]

### Missing validation criteria
- [list of acceptance criteria or validation methods not defined]

### Unresolved gates
- [list of gates that must pass before delegation]

### Recommended clarification
- [specific recommended actions to resolve insufficiency]

### Evidence
- [links to roadmap, CONTROL.md, or other authority documents inspected]
```

---

## 4. Roadmap Sufficiency Contract

### 4.1 Where the contract belongs

The roadmap sufficiency checklist belongs in two places:

| Location | Content | Rationale |
|---|---|---|
| `docs/REPOSITORY_CONTROL_MODEL.md` §Per-repo roadmap | Formal required fields for roadmap structure | Roadmap creators need to know what Hermes requires |
| `agents/HERMES_AGENT_CONTRACT.md` §3.5a | The sufficiency checklist (identical) | Hermes needs the checklist at runtime |

**Decision:** Duplicate the checklist in both documents. This is acceptable
because the two documents serve different actors (roadmap creators vs. Hermes
itself) and the checklist is small (~10 fields). A cross-reference should
connect them.

### 4.2 Required roadmap fields

The per-repo roadmap contract in `REPOSITORY_CONTROL_MODEL.md` §Required
structure already defines most fields. The change is to mark which are required
vs. recommended, and to add a note that Hermes validates these before
delegation.

Current required structure (unchanged):

```
- North Star
- Current State
- Dependency Map
- Workstreams
- Execution Chunks (with Goal, Worker Tasks, Inputs, Outputs,
  Validation, Dependencies, Exit Gate)
- Implementation Specifications
- High Reasoning Gates
- Agent Assignment Model
- Risks and Unknowns
- Completion Criteria
```

**Addition:** Mark which execution-chunk fields are required for Hermes
delegation. Add a note:

> Hermes validates that each execution chunk has a goal, bounded worker tasks,
> declared inputs and outputs, and validation criteria before delegating work.
> Roadmap sections without these fields will receive
> `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` and will not be delegated until
> resolved.

### 4.3 Interaction with existing roadmap lifecycle states

The roadmap lifecycle states (`PROPOSAL`, `TRIAL`, `ACTIVE`, `CANONICAL`)
already distinguish draft from executable. The sufficiency gate adds a quality
dimension: an `ACTIVE` roadmap may still be `INSUFFICIENT_FOR_ORCHESTRATION`
if its chunks are underspecified.

| Roadmap status | May be delegated? | Sufficiency gate outcome |
|---|---|---|
| PROPOSAL | No | Not checked — not authorized for execution |
| TRIAL | Yes (with explicit envelope) | Must pass sufficiency gate |
| ACTIVE | Yes | Must pass sufficiency gate |
| CANONICAL | Yes | Must pass sufficiency gate |

---

## 5. Documentation Changes Required

### 5.1 Documents to modify

| File | Change type | Content | Effort |
|---|---|---|---|
| `agents/HERMES_AGENT_CONTRACT.md` | Add §3.5a, §3.5b | Sufficiency checklist, failure report template, may/may not table | ~60 lines |
| `docs/REPOSITORY_CONTROL_MODEL.md` | Update §Per-repo roadmap | Mark required chunk fields, add Hermes validation note | ~15 lines |
| `agents/VPS_ORCHESTRATION.md` | Update §1a Mode 0 | Reference sufficiency gate as Mode 0 prerequisite | ~10 lines |
| `docs/HERMES_OPERATOR_GUIDE.md` | Update §Stop and escalation | Add roadmap insufficiency as a stop condition | ~5 lines |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | Add note to §6 | Reference pre-delegation gate in orchestration lifecycle | ~5 lines |
| `docs/OPERATING_MODEL.md` | Minor update §Work ownership | Expand Hermes description to include pre-delegation validation | ~3 lines |

### 5.2 Documents NOT to modify

| Document | Reason |
|---|---|
| `ROADMAP.md` | Portfolio roadmap — not an operational contract |
| `TODO.md` | Protected — session-scoped task list |
| `AGENTS.md` | Root agent instructions — Hermes-specific rules belong in agent contract |
| `agents/LOCAL_IMPLEMENTATION.md` | OpenCode contract — no Hermes changes needed |
| `docs/README.md` | No index change needed — content goes in existing documents |

### 5.3 New documents NOT to create

| Potential document | Decision | Reason |
|---|---|---|
| "Hermes Sufficiency Contract" | Do not create | Concept lives in HERMES_AGENT_CONTRACT.md §3.5a |
| "Roadmap Readiness Checklist" | Do not create | Checklist lives in REPOSITORY_CONTROL_MODEL.md §Per-repo roadmap |
| "Codex-Hermes Handoff Protocol" | Do not create yet | Defer until after first pilot; handoff is manual for now |

---

## 6. Task Packet Implications

### 6.1 Current template assessment

The existing `agents/orchestrator-task-packet-template.md` has:

| Field | Present? | Sufficient? |
|---|---|---|
| Task ID | Yes | Yes |
| Objective | Yes | Yes |
| Context | Yes | Yes |
| Scope (Allowed / Do Not) | Yes | Yes |
| Delegation target (executor, repo, one-task-in-flight) | Yes | Yes |
| Allowed paths | Yes | Yes |
| Validation requirements | Yes | Yes |
| Result report requirements | Yes | Yes |
| Checkpoint rules | Yes | Yes |
| After-completion instructions | Yes | Yes |

**Verdict:** The existing template is sufficient. No changes needed.

### 6.2 What the sufficiency gate adds BEFORE the template

The sufficiency gate does not change the packet template. It adds a prerequisite:

```
[Before packet creation]
  → Validate roadmap sufficiency (§3.5a)
  → If INSUFFICIENT: stop, report, escalate
  → If SUFFICIENT: proceed to create packet using template
```

The packet remains the same. Only the entry condition changes.

### 6.3 Implicit fields the gate validates

The sufficiency checklist maps to the packet template:

| Sufficiency field | Maps to packet field | Gap? |
|---|---|---|
| Execution chunk goal | Objective | None |
| Worker tasks (bounded) | Scope → Allowed actions | None |
| Inputs (files, data, authority) | Context + Read First | None |
| Outputs (files, evidence) | Validation requirements + Result report | None |
| Validation criteria | Validation requirements | None |
| Dependencies | Context | None |
| Exit gate | Checkpoint rules → stop condition | None |
| Agent assignment | Delegation target → executor | None |
| Risks and unknowns | Context → known uncertainty | None |

No gap. The template already covers all required fields.

---

## 7. Failure Behavior Design

### 7.1 Required behavior

When Hermes encounters an insufficient roadmap, the required behavior is:

```
1. STOP — do not create any task packet
2. PRODUCE — ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION report (§3.5b)
3. ESCALATE — write report to bridge outbox (VPS) or agent report path (local)
4. WAIT — do not resume until Buddy resolves the insufficiency
5. EVIDENCE — preserve the inspection state (what was checked, what was missing)
```

### 7.2 Escalation path

| Environment | Escalation destination | Mechanism |
|---|---|---|
| VPS (Hermes resident) | Bridge outbox → Buddy reads | Hermes writes report to `~/Desktop/hermes-bridge/outbox/` |
| Local (OpenCode/Codex) | Outbox → Buddy reads | Agent writes report to `_internal/outbox/session-<N>/` |

### 7.3 Resume conditions

Hermes may resume only when:

1. The insufficiency report has been reviewed by Buddy
2. The roadmap section has been updated with the missing fields
3. Buddy explicitly authorizes re-validation (implicit from task dispatch)

### 7.4 What Hermes does while stopped

- Hermes does not poll or retry automatically
- Hermes does not downgrade requirements
- Hermes does not create a "partial" task for a subset of the work
- Hermes does not self-escalate to Buddy repeatedly without new evidence

---

## 8. Codex Relationship Boundary

### 8.1 Formal boundary

| Owns | Codex | Hermes |
|---|---|---|
| Architecture decisions | Yes | No |
| Roadmap creation | Yes | No |
| Roadmap refinement | Yes | May report insufficiency |
| Complex tradeoff resolution | Yes | No |
| Roadmap interpretation | No | Yes |
| Execution planning | No | Yes |
| Task decomposition | No | Yes |
| Progress tracking | No | Yes |
| Sufficiency validation | No | Yes |

### 8.2 Handoff artifact

For the initial implementation, the handoff from Hermes to Codex is **manual**:

```
Hermes detects insufficiency
  → writes ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION report
  → Buddy reads report
  → Buddy decides: refine roadmap (use Codex) or override (authorize anyway)
  → If refine: Buddy dispatches Codex with the insufficiency report as input
  → Codex updates roadmap
  → Hermes re-validates on next dispatch
```

No formal handoff artifact is needed yet. The insufficiency report serves as
the handoff. A dedicated "Codex refinement request" artifact can be designed
after the first pilot demonstrates the pattern is useful.

### 8.3 Future evolution (deferred)

| Feature | When | Trigger |
|---|---|---|
| Automated Codex handoff | After >=2 pilot cycles | Hermes detects familiar insufficiency pattern |
| Hermes-initiated Codex dispatch | After automated handoff is proven safe | Sufficiency gate fails |
| Codex refinement template | After handoff pattern is stable | Insufficiency reports have consistent structure |

---

## 9. OpenCode/Execution Boundary

### 9.1 What execution agents receive

An execution agent (OpenCode) receives a task packet containing:

| Field | Source | Required? |
|---|---|---|
| Objective | Roadmap chunk goal | Yes |
| Context | Roadmap + current state | Yes |
| Scope (allowed actions) | Roadmap chunk tasks | Yes |
| Do Not (prohibited actions) | Hermes contract + envelope | Yes |
| Allowed paths | CONTROL.md `hermes.artifact_paths` | Yes |
| Validation requirements | Roadmap chunk validation | Yes |
| Result report requirements | Hermes contract + template | Yes |

The execution agent does NOT receive:
- The full roadmap (only the relevant section)
- Hermes reasoning or sufficiency evaluation
- Other repository state not relevant to the task
- Architecture decisions or unresolved questions

### 9.2 Capability boundary

OpenCode execution agents are expected to:

| Can do | Cannot do |
|---|---|
| Follow explicit instructions | Resolve ambiguous requirements |
| Implement bounded changes | Make architecture decisions |
| Run validation | Resolve major tradeoffs |
| Report evidence | Decide product direction |
| Write documentation | Define acceptance criteria |
| Create tests | Design cross-repo interfaces |
| Edit declared paths | Invent missing specifications |

This boundary is already documented in `docs/OPERATING_MODEL.md` §Work ownership
and does not need to be repeated in the Hermes contract. The sufficiency gate
enforces it implicitly.

### 9.3 Existing template sufficiency

The `agents/orchestrator-task-packet-template.md` already captures all required
fields. The template's "Read First" section references the correct authority
documents. **No change needed.**

---

## 10. Palworld Pilot Design

### 10.1 Pilot type

The first Hermes pilot must be a **read-only diagnostic pilot**, not an
implementation pilot.

**Goal:** Test whether Hermes can determine:
- Is Palworld KB ready for orchestration?
- What information is missing?
- What must be resolved before delegation?

**Not a goal:** Delegate implementation work, create branches, modify files.

### 10.2 Pilot sequence

```
1. Read Palworld KB CONTROL.md
   → Verify: hermes.scope, hermes.artifact_paths, lifecycle.state, blockers

2. Read Palworld KB roadmap (ROADMAP.md in the palworld-kb repo)
   → Verify: execution chunks defined? acceptance criteria present?
   → Validate sufficiency checklist (§3.5a)

3. Inspect repository state
   → Verify: clean baseline? experiment output classified?
   → Verify: approved SHA known?

4. Report outcome:
   a. SUFFICIENT_FOR_ORCHESTRATION
      → Create first bounded task packet
      → Recommend delegation to OpenCode
      → Do NOT delegate (pilot stops here)
   b. ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION
      → Produce full insufficiency report
      → List each missing field
      → Recommend specific clarifications

5. Write pilot result report
```

### 10.3 Expected outcome

Based on the current Palworld state (from Task 11 preflight analysis), the
pilot is expected to produce `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` with:

| Missing field | Where it should live | Current status |
|---|---|---|
| Hermes artifact paths | CONTROL.md `hermes.artifact_paths` | Not declared |
| Hermes scope | CONTROL.md `hermes.scope` | `read-only` (needs `orchestrate-artifact-only`) |
| Clean baseline SHA | CONTROL.md or TODO.md | Experiment output unclassified |
| First bounded chunk | Palworld ROADMAP.md or TODO.md | Not defined |
| Validation criteria | Palworld ROADMAP.md chunk definition | Not defined |
| VPS clone | VPS filesystem | Does not exist |

### 10.4 Pilot success criteria

| Criterion | What proves it |
|---|---|
| Hermes correctly identifies missing fields | Insufficiency report matches actual gaps |
| Hermes does not delegate without sufficiency | No task packet created |
| Hermes does not invent missing information | Report says "not found" not "assumed X" |
| Report is actionable for Buddy/Codex | Each missing field has a recommended action |

### 10.5 What the pilot does NOT test

- Multi-task orchestration (deferred)
- Autonomous roadmap evaluation across chunks (deferred)
- Codex handoff (deferred until after pilot)
- VPS bridge interaction (deferred — run locally first)

---

## 11. Implementation Sequence

### 11.1 Ordered steps

```
Step 1: Add §3.5a + §3.5b to HERMES_AGENT_CONTRACT.md
  Files: 1
  Effort: ~60 lines
  What: sufficiency checklist, stop conditions, failure report template
  Dependency: None

Step 2: Update REPOSITORY_CONTROL_MODEL.md §Per-repo roadmap
  Files: 1
  Effort: ~15 lines
  What: mark required chunk fields, add Hermes validation note
  Dependency: Step 1 (consistent checklist)

Step 3: Update VPS_ORCHESTRATION.md §1a Mode 0
  Files: 1
  Effort: ~10 lines
  What: reference sufficiency gate as Mode 0 prerequisite
  Dependency: Step 1

Step 4: Update HERMES_OPERATOR_GUIDE.md + REPOSITORY_WORK_PROTOCOL.md
  Files: 2
  Effort: ~10 lines total
  What: add stop condition, add lifecycle reference
  Dependency: Step 1

Step 5: Execute Palworld diagnostic pilot
  Files: 0 (read-only)
  Effort: 1 session
  What: run the pilot sequence from §10.2
  Dependency: Steps 1-4 (documentation must exist first)
```

### 11.2 Minimum viable cut

The absolute minimum implementation is **Step 1 only**. Hermes can operate with
just the sufficiency checklist and stop conditions. Steps 2-4 make the system
discoverable and maintainable but are not required for a pilot.

### 11.3 What NOT to implement

| Item | Reason |
|---|---|
| Automated roadmap validation tool | Behavioral rule is sufficient; code adds maintenance burden |
| Codex handoff automation | Not needed until after >=2 pilots prove the pattern |
| Roadmap section template change | Existing structure is sufficient; Hermes validates, not creates |
| New Hermes permission level | Existing `orchestrate-artifact-only` is sufficient |
| Multi-task orchestration in pilot | First pilot is read-only diagnostic |

---

## 12. Risks and Unresolved Decisions

### 12.1 Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Sufficiency gate is too strict | Medium | No work ever delegated | Start strict; relax after first pilot proves gate works |
| Sufficiency checklist is too vague | Medium | Hermes misses genuine gaps | Use concrete field names (goal, inputs, outputs, validation) |
| Roadmap creators don't know checklist exists | High | Roadmaps fail gate repeatedly | Document in REPOSITORY_CONTROL_MODEL.md — roadmap creators read that |
| Hermes reports insufficiency but Buddy disagrees | Low | Friction, delay | Pilot will reveal; Buddy can override by providing missing fields directly |
| Palworld pilot produces expected insufficiency → no forward progress | Medium | Pilot feels like failure | Frame success as "correctly identified gaps," not "delegated work" |

### 12.2 Unresolved decisions

| Decision | Options | Recommendation |
|---|---|---|
| Should Hermes validate the full roadmap or only the referenced section? | Full vs. section | **Referenced section only.** Validating the full roadmap is not Hermes' role. |
| Should the sufficiency gate apply to every task or only new delegations? | All vs. new | **All delegations.** Every task packet must pass. No grandfather clause for existing envelopes. |
| Who decides when a roadmap is "clear enough" when Hermes and the author disagree? | Buddy vs. Codex vs. rule | **Buddy.** Buddy may override with a written decision. Hermes records the override. |
| Should the checklist be in Hermes contract or roadmap contract or both? | One vs. two | **Both** (duplicate with cross-ref). Different actors need different entry points. |

### 12.3 Future decisions (deferred)

| Decision | Defer until |
|---|---|
| Codex handoff protocol | After first pilot demonstrates insufficiency pattern |
| Multi-chunk orchestration | After single-chunk pilot succeeds |
| PR/branch creation for Hermes | After orchestration loop is proven safe |
| Persistent Hermes service | After orchestration loop is proven reliable |

---

## 13. Success Criteria Assessment

| Criterion | Answer |
|---|---|
| What exactly changes in Hermes? | Adds pre-delegation sufficiency validation (§3.5a) and structured failure reporting (§3.5b). No permission changes. |
| What remains Codex responsibility? | Architecture, roadmap creation/refinement, complex tradeoffs. Codex unchanged. |
| What information must exist before Hermes delegates? | Roadmap execution chunk with: goal, bounded tasks, inputs, outputs, validation criteria. |
| Where should these rules live? | `HERMES_AGENT_CONTRACT.md` (new sections), `REPOSITORY_CONTROL_MODEL.md` (field requirements), `VPS_ORCHESTRATION.md` (Mode 0 reference). |
| What is the safest first pilot? | Read-only diagnostic: "Can Hermes determine whether Palworld KB is ready for orchestration?" No delegation occurs. |

---

## References

- `agent/reports/session-12/06-hermes-roadmap-sufficiency-preflight.md` — Task 11 preflight
- `agent/reports/session-12/02-documentation-architecture-review.md` — Doc architecture review
- `agent/reports/session-12/03-documentation-consolidation-implementation.md` — Doc consolidation
- `agent/reports/session-12/04-internal-boundary-and-template-audit.md` — Internal boundary audit
- `agent/reports/session-12/05-internal-historical-intent.md` — Historical intent reconciliation
- `agents/HERMES_AGENT_CONTRACT.md` — Current Hermes contract
- `agents/VPS_ORCHESTRATION.md` — VPS orchestration contract
- `agents/orchestrator-task-packet-template.md` — Task packet template
- `docs/REPOSITORY_CONTROL_MODEL.md` — Per-repo roadmap contract
- `docs/REPOSITORY_WORK_PROTOCOL.md` — Artifact-only orchestration
- `docs/OPERATING_MODEL.md` — Work ownership
- `docs/HERMES_OPERATOR_GUIDE.md` — Hermes operator guide
- `ROADMAP.md` — Portfolio roadmap
- `repos/palworld-kb/CONTROL.md` — Palworld current governance
