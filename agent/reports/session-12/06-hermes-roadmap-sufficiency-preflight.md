# Session 12 — Task 11: Hermes Roadmap Sufficiency Gate Preflight

**Date:** 2026-07-19
**Status:** COMPLETED — architecture preflight analysis, no files modified
**Type:** Parallel architecture preflight (not implementation)

---

## 1. Executive Summary

The proposed Hermes roadmap-sufficiency gate is **compatible** with the current
Ivy Control architecture. It introduces one new concept — a pre-delegation
quality check on roadmap clarity — that does not conflict with any existing
authority document.

**Four findings:**

1. **No conflicts found.** The proposal is additive, not contradictory. Every
   proposed responsibility either already exists in current documents or fills a
   genuine gap that no document currently addresses.

2. **The rule belongs in `agents/HERMES_AGENT_CONTRACT.md`.** It is a Hermes
   behavioral change — how Hermes decides whether to proceed before delegation.
   It does not belong in the roadmap contract, operating model, or a new
   document.

3. **Three documents need targeted updates** when implementation begins:
   `HERMES_AGENT_CONTRACT.md` (new pre-delegation section),
   `VPS_ORCHESTRATION.md` (Mode 0 envelope expansion), and
   `REPOSITORY_CONTROL_MODEL.md` (roadmap contract formalization).

4. **The Palworld pilot would have benefited from this gate.** The current
   Palworld roadmap lacks explicit agent-executable chunks, acceptance criteria,
   and declared Hermes artifact paths — all things the sufficiency gate would
   have caught before delegation was attempted.

**Bottom line:** The proposal improves safety and reliability of agent
orchestration without making Hermes more autonomous. It is ready for
implementation after the minimum documentation changes identified below.

---

## 2. Proposed Design Evaluation

### 2.1 What the proposal says

The proposed Hermes model introduces a validation step between roadmap reading
and task delegation:

```
roadmap → sufficiency gate → [sufficient] → bounded task → delegate
                           → [insufficient] → ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION
                                             → missing decisions, ambiguous requirements,
                                               unclear dependencies, missing validation
                                             → recommended clarification
```

Core principle: Hermes must recognize the capability boundary of execution
agents and not delegate work that requires architecture decisions, ambiguous
requirement resolution, or missing acceptance criteria.

### 2.2 What the current model says

Current Hermes behavior (from `agents/HERMES_AGENT_CONTRACT.md` §3.5):

> Before Hermes enters Mode 0, it must have an explicit dispatch that states
> the target repository, approved roadmap section, allowed artifact paths,
> executor, validation requirements, maximum task/chunk count, checkpoint
> cadence, and stop/escalation owner.

The current model assumes the delegation envelope is provided by Buddy/GPT,
not evaluated by Hermes. Hermes currently checks:
- Is the repo eligible? (§3.1 — CONTROL.md presence, lifecycle, no blocker)
- Are the permissions correct? (§3.2 — per-repo permission derivation)
- Are artifact paths declared? (referenced from REPOSITORY_WORK_PROTOCOL.md)

It does NOT currently check:
- Is the roadmap section clear enough for an execution agent?
- Are acceptance criteria present and unambiguous?
- Are dependencies and risks identified?
- Can the bounded chunk be executed without architecture interpretation?

### 2.3 Gap analysis

| Current Hermes check | Proposed sufficiency gate | Gap |
|---|---|---|
| Repo eligibility (CONTROL.md exists, no blocker) | Roadmap clarity for agent execution | Not currently checked |
| Permission derivation (what Hermes may do) | Task specification completeness | Not currently checked |
| Artifact paths declared | Acceptance criteria present | Not currently checked |
| Stop/escalation owner named | Dependencies and risks identified | Not currently checked |
| Max task/chunk count | Bounded chunk is self-contained | Not currently checked |

### 2.4 Assessment

The proposal is a **genuine gap in the current model**, not a rehash of
existing checks. The current model assumes the delegation envelope creator
(Buddy/GPT) has already validated roadmap sufficiency. The proposal adds a
safeguard where Hermes independently verifies before delegating.

**Risk of adoption:** Low. The gate is conservative — it only stops execution;
it does not grant new permissions. If the gate is too strict initially, it can
be relaxed. If it is too lenient, execution agents fail on ambiguous tasks,
which is the current default behavior.

---

## 3. Existing Document Conflicts

### 3.1 Authority conflict table

| Document | Current statement | Conflict with proposal? | Required change |
|---|---|---|---|
| `docs/OPERATING_MODEL.md` §Work ownership | "OpenCode agents receive bounded tasks with explicit scope, allowed files, and validation criteria. They do not invent architecture." | **No conflict.** Proposal reinforces this boundary. | None — supporting alignment. |
| `docs/OPERATING_MODEL.md` §Work ownership | "Hermes (resident agent): Read-only inspection, monitoring, drift detection, and explicitly dispatched artifact-only coordination." | **No conflict.** Sufficiency gate is an extension of Hermes' existing coordination role. | Minor — expand Hermes description to include pre-delegation validation. |
| `docs/OPERATING_MODEL.md` §Authority model | "Hermes may invoke narrowly defined agents for bounded tasks." | **No conflict.** Proposal refines "bounded" to include explicit sufficiency check. | None. |
| `agents/HERMES_AGENT_CONTRACT.md` §3.5 | "Before Hermes enters Mode 0, it must have an explicit dispatch..." | **No conflict.** Sufficiency gate is additive before the dispatch check. | Add new §3.5a — pre-delegation roadmap sufficiency validation. |
| `agents/HERMES_AGENT_CONTRACT.md` §3.2 | Hermes derives per-repo permissions from CONTROL.md fields. | **No conflict.** Proposal does not change permission derivation. | None. |
| `agents/VPS_ORCHESTRATION.md` §1a Mode 0 | "Mode 0 is coordination, not implementation or operational access." | **No conflict.** Sufficiency gate is a coordination activity. | Expand Mode 0 definition to include pre-delegation evaluation. |
| `agents/VPS_ORCHESTRATION.md` §4 | "Keep work bounded to the assigned task." | **No conflict.** Proposal enforces this by preventing delegation of unbounded work. | None — alignment. |
| `docs/REPOSITORY_WORK_PROTOCOL.md` §6 | Roadmaps are canonical authority; reports are evidence only. | **No conflict.** Proposal does not change artifact hierarchy. | None. |
| `docs/REPOSITORY_CONTROL_MODEL.md` §Per-repo roadmap | Roadmap structure includes current state, objective, chunks, dependencies, acceptance criteria, risks, gates, agent assignment, evidence requirements. | **No conflict.** Proposal's sufficiency gate would validate that these fields are present and clear. | Formalize roadmap contract requirements if not already enforced. |
| `docs/REPOSITORY_CONTROL_MODEL.md` §Creation workflow | Roadmap creation uses controlled Codex handoff. | **No conflict.** Proposal adds Hermes feedback loop to Codex, not replacement. | Optionally document the "Hermes detects → Codex refines" cycle. |
| `ROADMAP.md` §6 Hermes Evolution | "Current: read-only inspection, health comparison, status reports, drift detection, bounded evidence requests. Next stage: inspect VPS clones, identify bounded work, create isolated branches, run tests, prepare PRs." | **No conflict.** Sufficiency gate fits under "identify bounded work" — it's a prerequisite for bounded-task identification. | None — implicit. |
| `docs/HERMES_OPERATOR_GUIDE.md` | Hermes is a read-only operator assistant. | **No conflict.** Sufficiency gate is a read-only evaluation. | Minor — add pre-delegation check to operator guidance. |

### 3.2 Summary

**Zero conflicts found.** All proposed changes are additive or clarifying. No
existing statement would need to be contradicted or removed.

---

## 4. Recommended Documentation Location

### 4.1 Where the rule should live

**Primary home:** `agents/HERMES_AGENT_CONTRACT.md` — new section §3.5a
"Pre-delegation roadmap sufficiency validation"

**Rationale:**
- The sufficiency gate is a **Hermes behavioral rule** — it defines how Hermes
  decides whether to proceed before creating a task packet.
- `HERMES_AGENT_CONTRACT.md` already owns §3 (Repository Eligibility and
  Permission Representation) and §3.5 (Artifact-only orchestration gate). The
  pre-delegation gate is a natural extension of these checks.
- It does NOT belong in the roadmap contract documents because the rule is
  about Hermes behavior, not roadmap structure. (Roadmap structure is already
  defined in `REPOSITORY_CONTROL_MODEL.md` §Per-repo roadmap.)

### 4.2 Supporting locations

| Document | Change type | Content |
|---|---|---|
| `agents/HERMES_AGENT_CONTRACT.md` | ⭐ **Add §3.5a** | Pre-delegation sufficiency validation: checklist, stop conditions, `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` report template |
| `agents/VPS_ORCHESTRATION.md` | Update §1a Mode 0 | Expand Mode 0 envelope definition to include sufficiency gate as prerequisite |
| `docs/REPOSITORY_CONTROL_MODEL.md` | Update §Per-repo roadmap | Formalize required fields if not already required; add note that Hermes validates these |
| `docs/HERMES_OPERATOR_GUIDE.md` | Minor update §Stop and escalation | Add roadmap insufficiency as a stop/escalation condition |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | Optional note | Add reference to new pre-delegation gate in artifact-only orchestration lifecycle |

### 4.3 Document NOT to create

Do **not** create a standalone "Roadmap Sufficiency Contract" or "Hermes
Pre-Delegation Gate" document. The concept is a single section in an existing
agent contract. Creating a new document would violate the documentation creation
governance rules in `docs/README.md` §Repository Documentation Contract.

---

## 5. Roadmap Contract Recommendations

### 5.1 Current roadmap contract

The per-repo roadmap contract in `docs/REPOSITORY_CONTROL_MODEL.md` §Required
structure already defines most of what a sufficiency gate would check:

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

### 5.2 Sufficiency gate checklist

Hermes should validate that the roadmap (or the specific section referenced in
the delegation envelope) has:

| Field | Required for delegation | Why it matters |
|---|---|---|
| Execution chunk goal | Yes | Agent needs to know what success looks like |
| Worker tasks (bounded) | Yes | Unbounded tasks invite architecture interpretation |
| Inputs (files, data, authority) | Yes | Agent cannot discover inputs independently |
| Outputs (files, evidence) | Yes | Required for verification |
| Validation criteria | Yes | No way to verify completion without this |
| Dependencies | Recommended | Risk of blocked work mid-delegation |
| Exit gate or acceptance review | Recommended | Ensures human review at chunk boundary |
| Agent assignment model | Recommended | Not every chunk is OpenCode-suitable |
| Risks and unknowns | Recommended | Helps agent know when to stop |

A gateway with `SUFFICIENT_FOR_ORCHESTRATION` or
`INSUFFICIENT_FOR_ORCHESTRATION` outcome, plus the missing fields, is the
minimum output.

### 5.3 Current compatibility

The Palworld KB roadmap does not exist in ivy-control-vps — it lives in the
Palworld repo. The ivy-control `ROADMAP.md` references Palworld only in §4C
(per-repo status table) and §6F (which was the old reference). **There is no
agent-executable Palworld roadmap in the current ivy-control checkout.**

The sufficiency gate would immediately flag this: no execution chunks defined,
no acceptance criteria, no agent assignment model for the Palworld pilot.

---

## 6. Palworld Pilot Analysis

### 6.1 Was Hermes correct to stop?

**Yes.** The Session 12 implementation report
(`agent/reports/session-12/00-session12-implementation-report.md`) correctly
concluded:

> Palworld is not ready to clone from its current local working tree. It
> contains staged promotion work, modified knowledge/index/log files, and
> substantial untracked experiment and proposal output.

Hermes (or the Codex implementation session) recognized that:
- No clean baseline exists
- No artifact paths are declared
- Hermes scope is `read-only`, not `orchestrate-artifact-only`
- No VPS clone exists
- The Palworld working tree has unclassified experiment output

### 6.2 What would the sufficiency gate have produced?

If the roadmap sufficiency gate had existed when the Palworld pilot was
attempted, it would have produced:

```
ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION

Missing decisions:
  - Which approved SHA to use as clean baseline
  - Whether experiment output is preserved, archived, or discarded

Ambiguous requirements:
  - "Workflow remediation and bounded source-only admission preparation"
    (from CONTROL.md continuity.current_focus) is too broad
  - What does "bounded" mean for the Palworld pilot?
  - What does "documentation-safe" first chunk include?

Unclear dependencies:
  - VPS clone must exist before Hermes can coordinate
  - Hermes scope must be upgraded to "orchestrate-artifact-only"
  - Artifact paths must be declared in CONTROL.md

Missing validation criteria:
  - What proves the pilot succeeded?
  - What is the acceptance gate?

Unresolved gates:
  - Buddy must approve VPS source-only clone timing (buddy_decisions[0])
  - Hermes branch/PR creation gate is not designed

Recommended clarification:
  1. Define the first bounded task explicitly
  2. Declare artifact paths in Palworld CONTROL.md
  3. Confirm or upgrade Hermes scope
  4. Define acceptance criteria for "documentation-safe"
  5. Resolve experiment output disposition
```

### 6.3 What information was missing?

The following information was absent when the Palworld pilot was scoped:

| Missing information | Where it should live | Status |
|---|---|---|
| Clean baseline SHA for VPS clone | Palworld CONTROL.md or TODO.md | Not declared |
| Experiment output disposition decision | Palworld AGENTS.md or TODO.md | Not made |
| Hermes artifact paths for Palworld | Palworld CONTROL.md `hermes.artifact_paths` | Not declared |
| Hermes scope upgrade to `orchestrate-artifact-only` | Palworld CONTROL.md `hermes.scope` | Still `read-only` |
| First bounded chunk specification | Palworld ROADMAP.md or TODO.md | Not defined |
| Acceptance criteria for pilot phase | Palworld ROADMAP.md | Not defined |
| VPS clone footprint threshold | Neither documented | Not checked |

### 6.4 Pilot readiness criteria

Based on this analysis, the minimum criteria for a Hermes Palworld pilot are:

1. **Clean baseline** — approved SHA identified, experiment output disposed
2. **Declared artifact paths** — `hermes.artifact_paths` in Palworld CONTROL.md
3. **Hermes scope** — upgraded to `orchestrate-artifact-only`
4. **VPS clone** — clean source-only clone exists and footprint is acceptable
5. **First chunk definition** — explicit bounded task with goal, inputs, outputs,
   validation criteria, and exit gate
6. **Roadmap sufficiency pass** — Hermes validates chunk is executable by an
   OpenCode agent without architecture interpretation

---

## 7. Future Implementation Task Recommendations

### 7.1 Implementation sequence

| Priority | Task | Documents affected | Level of effort |
|---|---|---|---|
| P0 | Add §3.5a "Pre-delegation roadmap sufficiency validation" to `HERMES_AGENT_CONTRACT.md` | 1 file | Small (~40 lines) |
| P0 | Add `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` stop condition template | 1 file | Small (~20 lines) |
| P1 | Update `VPS_ORCHESTRATION.md` §1a Mode 0 to reference sufficiency gate | 1 file | Small (~10 lines) |
| P1 | Formalize required roadmap fields in `REPOSITORY_CONTROL_MODEL.md` if not already enforced | 1 file | Small (~15 lines) |
| P2 | Update `HERMES_OPERATOR_GUIDE.md` stop conditions to include roadmap insufficiency | 1 file | Small (~5 lines) |
| P2 | Add sufficiency gate reference to `REPOSITORY_WORK_PROTOCOL.md` artifact-only orchestration lifecycle | 1 file | Small (~5 lines) |

### 7.2 Minimum viable implementation

The minimum viable implementation is:

1. **One new section** in `agents/HERMES_AGENT_CONTRACT.md` (§3.5a) containing:
   - Sufficiency gate definition
   - Required roadmap fields checklist
   - Two outcomes: `SUFFICIENT_FOR_ORCHESTRATION` and
     `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION`
   - Instruction to stop and report when insufficient
   - Prohibition against delegating work the roadmap does not clearly specify

2. **No code changes.** The sufficiency gate is a behavioral rule, not a
   software gate. Hermes (the agent) evaluates it during its startup sequence,
   before Mode 0 entry.

3. **No new documents.** The concept lives in one existing file.

### 7.3 Items explicitly NOT to implement

- Do not create a roadmap sufficiency validator tool or script
- Do not modify ROADMAP.md or any per-repo roadmap
- Do not create a new gate in the 6-gate admission model
- Do not change agent permissions
- Do not create Codex-integration code (the "Hermes detects → Codex refines"
  loop is aspirational; start with Hermes detects and reports)

### 7.4 Future evolution (not for this implementation)

The proposal mentions future evolution where Hermes may request Codex
clarification automatically. This is deferred until:
- The manual sufficiency gate has been tested in at least one pilot
- A Codex integration pattern is designed
- The "Hermes detects → Codex refines → Hermes re-validates" loop is
  explicitly scoped and authorized

---

## 8. Success Criteria Assessment

| Criterion | Answer |
|---|---|
| Compatible with current Ivy Control architecture? | **Yes.** Additive change; no conflicts found. |
| Where should the rule live? | `agents/HERMES_AGENT_CONTRACT.md` §3.5a. |
| What documents need updates? | **Required:** `HERMES_AGENT_CONTRACT.md`. **Supporting:** `VPS_ORCHESTRATION.md`, `REPOSITORY_CONTROL_MODEL.md`. **Optional:** `HERMES_OPERATOR_GUIDE.md`, `REPOSITORY_WORK_PROTOCOL.md`. |
| Minimum implementation required? | One new section in one file (~40 lines). No code, no new documents. |
| Does this improve safety and reliability? | **Yes.** Catches ambiguous delegation before execution agents waste effort. Conservative gate — stops but does not autonomously act. |

---

## 9. Future Codex Relationship Boundary

### 9.1 Proposed boundary vs current authority

| Role | Current authority (where defined) | Proposed definition | Compatible? |
|---|---|---|---|
| **Buddy** | Authority and risk decisions (OPERATING_MODEL.md §Work ownership) | Resolves strategic decisions | ✅ Matches current |
| **Codex (Strong Codex)** | Architecture, privileged execution, irreversible decisions (OPERATING_MODEL.md §Work ownership); roadmap creation (REPOSITORY_CONTROL_MODEL.md §Creation workflow) | Creates/refines architecture roadmaps | ✅ Matches; proposal narrows to roadmap/architecture specifically |
| **Hermes** | Read-only inspection, artifact-only coordination (HERMES_AGENT_CONTRACT.md, VPS_ORCHESTRATION.md) | Validates and executes against roadmaps | ✅ Expands coordination role with pre-delegation gate |
| **OpenCode** | Bounded low-risk implementation (OPERATING_MODEL.md §Work ownership) | Implements bounded tasks | ✅ Matches current |
| **New: Roadmap sufficiency gate** | Not currently defined | Hermes checks roadmap clarity before delegation | ✅ Additive; no conflict |

### 9.2 Missing contracts

| Missing contract | Why it matters | Recommended owner |
|---|---|---|
| **"How Hermes requests clarification from Codex"** | The proposal says "Hermes detects and reports; Codex refines" but provides no protocol for this handoff. | Defer until after pilot. The first version is manual: Hermes writes a bridge report; Buddy forwards to Codex. |
| **"What constitutes a sufficient roadmap" for each agent type** | OpenCode and Strong Codex have different capability boundaries. A roadmap sufficient for Strong Codex may be insufficient for OpenCode. | Hermes agent contract — incorporate into the sufficiency checklist. |
| **"Codex roadmap refinement trigger"** | Currently Codex creates roadmaps on explicit request. There is no "roadmap needs refinement" trigger from Hermes. | Future evolution; not needed for initial implementation. |

### 9.3 Agent assignment model implication

The proposal implies that roadmaps should specify an agent type per chunk
(already in `REPOSITORY_CONTROL_MODEL.md` §Per-repo roadmap required structure:
"Agent Assignment Model — Per phase: what agent type suits it and why").

The sufficiency gate should validate that:
- The assigned agent type matches the chunk's complexity
- OpenCode is not assigned chunks requiring architecture decisions
- Strong Codex is not wasted on purely mechanical chunks
- Buddy is included for chunks requiring authority decisions

---

## 10. Actionable Recommendations

### 10.1 Implement now (after this preflight is reviewed)

1. Add §3.5a "Pre-delegation roadmap sufficiency validation" to
   `agents/HERMES_AGENT_CONTRACT.md` with the checklist defined in §5.2 above.
2. Define the `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` stop condition and
   minimal report template.
3. Do not change any other file for the initial implementation.

### 10.2 Do in parallel (not blocked)

1. Update `agents/VPS_ORCHESTRATION.md` to reference the new pre-delegation gate
   in the Mode 0 envelope description.
2. Add a brief note in `docs/REPOSITORY_CONTROL_MODEL.md` §Per-repo roadmap that
   Hermes validates required fields before delegation.

### 10.3 Do not do yet

1. Do not create a Codex-clarification-request protocol.
2. Do not write Hermes code for autonomous roadmap evaluation.
3. Do not modify any per-repo roadmap or ROADMAP.md.
4. Do not change Hermes permissions or scope.

---

## References

- `agents/HERMES_AGENT_CONTRACT.md` — current Hermes contract
- `agents/VPS_ORCHESTRATION.md` — VPS interaction modes
- `docs/HERMES_OPERATOR_GUIDE.md` — Hermes operator guide
- `docs/OPERATING_MODEL.md` — operating model, work ownership
- `docs/REPOSITORY_WORK_PROTOCOL.md` — artifact-only orchestration
- `docs/REPOSITORY_CONTROL_MODEL.md` — per-repo roadmap contract
- `ROADMAP.md` — portfolio roadmap, Hermes evolution
- `TODO.md` — session 12 task plan
- `repos/palworld-kb/CONTROL.md` — Palworld current governance
- `agent/reports/session-12/00-session12-implementation-report.md` — Codex implementation
- `agent/reports/session-12/02-documentation-architecture-review.md` — doc architecture
- `agent/reports/session-12/06-documentation-reconciliation.md` — residency reconciliation
