# Session 12 — Task 19: Hermes Codex Escalation Capability Model Assessment

**Date:** 2026-07-19
**Status:** DESIGN_COMPLETE

**Predecessor:** Task 18 — Hermes Artifact Storage Design Assessment

---

## 1. Current State

### 1.1 What Hermes currently may do when stuck

From `agents/HERMES_AGENT_CONTRACT.md` §3.5a:

> `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` — Hermes must stop, produce a
> structured report identifying the missing fields or decisions, and escalate
> to Buddy.

From §3.5b:

> A failed or incomplete check ends the run with `NEEDS_GPT_OR_BUDDY_DECISION`.

**Current behavior:** Hermes may stop and report. It may not invoke Codex
directly, compose a Codex prompt, or request Codex clarification. The
escalation path is:

```
Hermes fails → reports to Buddy → Buddy decides manually → (if Codex is needed,
Buddy dispatches OpenCode to use codex-handoff skill)
```

### 1.2 What Codex can currently do

From `docs/OPERATING_MODEL.md` §Work ownership:

> **Strong Codex:** Architecture, privileged execution, and irreversible
> decisions.

Codex is architecture authority, not an execution agent. Codex output is
advisory — it must be reconciled by OpenCode and approved by Buddy before
affecting roadmaps or implementation.

### 1.3 The gap

There is no defined mechanism for Hermes to **request** Codex within an
orchestration run. The only option today is:
1. Hermes stops and reports to Buddy
2. Buddy manually dispatches a separate Codex task
3. After Codex output, Buddy manually resumes Hermes

This works but is entirely manual. The capability registry model formalizes
this flow so it can be controlled, approved, and audited without requiring
Buddy to manually compose every escalation.

### 1.4 Relationship to Task 18 artifact model

Task 18 established:

```
Hermes validation → HERMES_ACCEPT / HERMES_REJECT / NEEDS_BUDDY_REVIEW
```

The `NEEDS_BUDDY_REVIEW` outcome is the natural trigger point for Codex
escalation. When Hermes produces `NEEDS_BUDDY_REVIEW` or
`ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION`, it may (if authorized) request Codex
rather than stopping entirely.

---

## 2. Design Options

### Option A: Manual only (current state)

Hermes stops and reports. Buddy handles all escalation manually.

| Pro | Con |
|---|---|
| Simplest. No new mechanisms needed. | Bottleneck on Buddy for every escalation. Breaks autonomous flow. |
| Buddy has full control. | Does not scale beyond a few repositories. |

### Option B: Capability registry (recommended)

Hermes has a defined set of Codex capabilities, each with explicit enable
state, approval requirements, and artifact formats.

| Pro | Con |
|---|---|
| Controlled escalation — not an escape hatch. | Requires mechanism design before implementation. |
| Per-capability enable/disable. | Adds complexity to Hermes contract. |
| Buddy can pre-approve capabilities. | Must resist scope creep (Codex becomes hidden orchestrator). |
| Artifact lifecycle formalized. | Needs documentation and templates. |

### Option C: Unrestricted Codex access

Hermes may invoke Codex for any reason without explicit capability gating.

| Pro | Con |
|---|---|
| Maximum flexibility. | Codex becomes hidden orchestrator. Violates core principle. |
| No mechanism design needed. | No audit trail. No approval gates. Uncontrolled cost. |

**Recommendation: Option B.** The capability registry provides controlled
escalation without making Buddy the bottleneck for every request. Each
capability is gated, audited, and artifact-driven.

---

## 3. Recommended Model

### 3.1 Capability registry

The registry is a set of named capabilities that Hermes may request. Each
capability has:

| Field | Description |
|---|---|
| **id** | Unique capability identifier |
| **purpose** | What Codex is asked to do |
| **trigger** | Condition under which Hermes may request this capability |
| **input artifact** | What Hermes must produce before requesting |
| **output artifact** | What Codex produces |
| **requires_buddy_approval** | Whether Buddy must approve each use |
| **enabled** | Whether the capability is available at all |
| **authority_limit** | What Codex may and may not do |

### 3.2 Capabilities defined

#### roadmap_repair

| Field | Value |
|---|---|
| **Purpose** | Improve a roadmap section that failed the sufficiency gate |
| **Trigger** | `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` on criteria 1, 2, or 4 (objective clarity, current state accuracy, dependency clarity) |
| **Input artifact** | Insufficiency report + roadmap section + repository state summary |
| **Output artifact** | Improved roadmap section proposal (advisory, not authority) |
| **Requires buddy approval** | Yes |
| **Enabled by default** | No |
| **Authority limit** | Codex may suggest new phases, reorder work, clarify dependencies. Codex may not change scope, add new requirements, or bypass gates. |

#### architecture_review

| Field | Value |
|---|---|
| **Purpose** | Resolve an architecture question Hermes cannot answer |
| **Trigger** | Hermes encounters cross-repository design conflict, missing system boundary, or tradeoff requiring stronger reasoning |
| **Input artifact** | Architecture question packet: current state, constraints, specific questions, options considered |
| **Output artifact** | Architecture design proposal (advisory) |
| **Requires buddy approval** | Yes |
| **Enabled by default** | No |
| **Authority limit** | Codex may evaluate options, recommend approaches, identify risks. Codex may not commit to an implementation path, modify files, or override existing architecture decisions without Buddy approval. |

#### implementation_blocker_review

| Field | Value |
|---|---|
| **Purpose** | Diagnose why execution repeatedly fails or validation cannot pass |
| **Trigger** | Two consecutive `HERMES_REJECT` outcomes for the same task |
| **Input artifact** | Execution reports, validation evidence, task packet, Hermes validation reports |
| **Output artifact** | Blocker analysis and recommended resolution |
| **Requires buddy approval** | Yes |
| **Enabled by default** | No |
| **Authority limit** | Codex may analyze failure patterns, suggest fixes, recommend scope changes. Codex may not silently modify the task or change acceptance criteria. |

#### production_change_review

| Field | Value |
|---|---|
| **Purpose** | Review high-risk operational planning before Buddy approval |
| **Trigger** | Hermes encounters a production migration, destructive operation, or rollback design within its delegation envelope |
| **Input artifact** | Change proposal, risk assessment, rollback plan, evidence of current state |
| **Output artifact** | Safety review and recommendations |
| **Requires buddy approval** | Yes |
| **Enabled by default** | No |
| **Authority limit** | Codex may analyze risks, identify failure modes, recommend safeguards. Codex may not authorize the change, modify production state, or bypass the existing gate model. |

### 3.3 Hermes may not request Codex for

| Situation | Why not |
|---|---|
| Obvious documentation corrections | No architecture reasoning needed |
| Bounded implementation tasks | Already handled by execution agents |
| Normal task decomposition | Hermes's own responsibility |
| Routine validation or test execution | Programmatic — no reasoning needed |
| Any situation where Codex would replace Hermes's judgment | Hermes must remain orchestrator |
| Any situation where the question can be answered by reading files | Hermes can read files directly |

### 3.4 Escalation lifecycle

```
Hermes detects condition (insufficiency, rejection, blocker)
  ↓
Hermes evaluates: does a Codex capability match this condition?
  ↓
[NO matching capability] → stop, report to Buddy, wait
  ↓
[YES, capability exists but disabled] → stop, report capability not available
  ↓
[YES, capability exists and enabled] →
  ↓
Hermes checks: does this capability require Buddy approval?
  ↓
[YES] → Hermes produces escalation context artifact
         → Buddy reviews and approves/rejects
         → [approved] → Hermes creates Codex handoff artifact
         → [rejected] → stop, report reason
  ↓
[NO (pre-approved)] → Hermes creates Codex handoff artifact directly
  ↓
Codex handoff artifact is placed in agent/orchestration/<id>/ directory
  ↓
OpenCode (or Buddy) invokes codex-handoff skill with the artifact
  ↓
Codex produces output artifact
  ↓
OpenCode reconciles output (fixes paths, corrects assumptions)
  ↓
Hermes evaluates reconciled output:
  → ACCEPT → update roadmap/state, resume orchestration
  → REJECT → produce rejection report, escalate to Buddy
```

### 3.5 Artifact chain

Following the Task 18 directory model:

```
agent/orchestration/<envelope-id>/
  01-<task>-packet.md
  02-<task>-execution.md
  03-<task>-validation.md          ← Hermes validation (contains NEEDS_CODEX outcome)
  04-<task>-codex-escalation.md    ← NEW: Hermes writes escalation context
  05-codex-output.md               ← NEW: Codex output (after reconciliation)
  06-<task>-post-codex-validation.md ← NEW: Hermes re-evaluation
```

### 3.6 Hermes validation outcome: NEEDS_CODEX

The current validation outcomes from Task 18 are:

- `HERMES_ACCEPT`
- `HERMES_ACCEPT_WITH_NOTE`
- `HERMES_REJECT`
- `NEEDS_BUDDY_REVIEW`

A new outcome is needed:

- `NEEDS_CODEX` — Hermes has identified a condition that matches a Codex
  capability. Hermes will produce an escalation artifact and (if authorized)
  proceed to the escalation flow rather than stopping.

The distinction between `NEEDS_BUDDY_REVIEW` and `NEEDS_CODEX`:

| Outcome | Meaning | Next action |
|---|---|---|
| `NEEDS_BUDDY_REVIEW` | Cannot proceed. Requires human judgment. | Stop. Report to Buddy. |
| `NEEDS_CODEX` | Can proceed to Codex escalation if capability is enabled | Check capability registry → escalate or fall back to NEEDS_BUDDY_REVIEW |

---

## 4. Capability Registry Governance

### 4.1 Where the registry lives

The capability registry should live in one of two places:

| Option | Pro | Con |
|---|---|---|
| **`agents/HERMES_AGENT_CONTRACT.md`** §3.5d | Single source of truth for Hermes behavior. Natural extension of existing contract. | Contract grows longer. Capability enable/disable is a policy decision, not a contract definition. |
| **Per-repository `CONTROL.md` `hermes.codex_capabilities`** | Per-repo control. Repos with simpler scope can disable capabilities. Buddy decisions tracked per repo. | Introduces another CONTROL.md field. Repos without Hermes scope don't need it. |

**Recommendation: Both.**

The **capability definitions** (purpose, trigger, input/output, authority
limits) belong in `agents/HERMES_AGENT_CONTRACT.md` §3.5d — this is the
contract that defines what Hermes may do.

The **enable/disable state and approval requirements** belong in each
repository's `CONTROL.md` under `hermes.codex_capabilities` — this is per-repo
policy.

This follows the existing pattern: `HERMES_AGENT_CONTRACT.md` defines the
permission levels; `CONTROL.md` `hermes.scope` sets which level applies per
repo.

### 4.2 Example CONTROL.md addition

```yaml
hermes:
  scope: "orchestrate-artifact-only"
  codex_capabilities:
    roadmap_repair:
      enabled: false
      requires_buddy_approval: true
    architecture_review:
      enabled: false
      requires_buddy_approval: true
    implementation_blocker_review:
      enabled: false
      requires_buddy_approval: true
    production_change_review:
      enabled: false
      requires_buddy_approval: true
```

### 4.3 Enablement states

| State | Meaning | Transition |
|---|---|---|
| `disabled` | Capability is not available. Hermes must not request it. | Buddy sets to `enabled_via_approval` or `enabled` |
| `enabled_via_approval` | Capability is available but requires per-use Buddy approval | Buddy approves each use; capability stays in this state |
| `enabled` | Capability is available without per-use approval (pre-authorized for session or envelope) | Buddy sets when trust is established |

The distinction between `enabled_via_approval` and `enabled` protects against
a permanently-open Codex escape hatch. Most capabilities should start at
`disabled` and move to `enabled_via_approval` after review. `enabled` is the
exception, not the default.

---

## 5. Required Documentation Updates

### 5.1 Files to update (do not implement — proposed only)

| File | Change |
|---|---|
| `agents/HERMES_AGENT_CONTRACT.md` | Add §3.5d "Codex escalation capabilities" — capability definitions, triggers, input/output specs, authority limits. Add `NEEDS_CODEX` to validation outcomes. |
| `docs/REPOSITORY_CONTROL_MODEL.md` | Add `hermes.codex_capabilities` field definition to CONTROL.md schema. |
| `repos/*/CONTROL.md` (per-repo) | Add `hermes.codex_capabilities` block with per-repo enable states. |
| `agents/hermes-validation-report-template.md` (new) | Add `NEEDS_CODEX` as a validation outcome. Add escalation context artifact format. |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | Add orchestration artifact chain including codex escalation artifacts (§4 artifact locations table). |

### 5.2 Files NOT to create

| Potential document | Decision |
|---|---|
| `agents/CODEX_ESCALATION_PROTOCOL.md` | Do not create. Capability definitions live in HERMES_AGENT_CONTRACT.md. Per-repo policy lives in CONTROL.md. A standalone protocol would duplicate both. |
| `agents/CODEX_CAPABILITY_REGISTRY.md` | Do not create. Same reason — the registry is a section of the Hermes contract, not a standalone document. |

### 5.3 New template needed: Codex escalation context

A template file is needed:

```
agents/codex-escalation-context-template.md
```

This template defines the artifact Hermes produces when escalating to Codex.
It ensures consistency so Codex always receives the same structured context.

Fields:
- Capability requested
- Trigger condition
- Repository and envelope
- Problem statement (what Hermes cannot resolve)
- Current state (verified facts)
- Constraints (what Codex must not do)
- Specific questions Codex must answer
- Output format expected
- Authority limits (what Codex may not decide)

---

## 6. Open Decisions

| Decision | Options | Recommendation |
|---|---|---|
| Should capabilities be enabled globally or per-repo? | Global vs. per-repo | **Per-repo** — different repos have different complexity and trust levels. |
| Should Hermes produce the escalation context artifact directly, or should OpenCode compose it? | Hermes vs. OpenCode | **Hermes produces the context; OpenCode may refine before invocation.** Hermes identifies the gap and constraints; OpenCode adds the specific prompt framing. |
| Should Codex output go through Hermes validation before adoption? | Hermes validates vs. directly adopted | **Hermes validates** — consistent with the validation model from Task 18. Codex output is advisory; Hermes must evaluate it against the original problem before accepting. |
| Should capabilities be discoverable by Hermes or hardcoded in the contract? | Discoverable vs. hardcoded | **Hardcoded in contract.** The four capabilities are known design points. Discovery would imply Hermes can find capabilities it wasn't designed to use. |
| What happens when a capability is disabled but Hermes needs it? | Stop vs. fall back | **Stop and report.** Hermes produces `NEEDS_BUDDY_REVIEW` with a note that the condition matches a disabled capability. Buddy may enable it or resolve manually. |
| Should capabilities have usage quotas? | Quotas vs. unlimited | **Defer.** Quotas add complexity. Start with simple on/off per capability. Add cost tracking if Codex usage becomes frequent enough to need it. |

---

## 7. Summary

| Question | Answer |
|---|---|
| How does Hermes gain controlled Codex access? | Through a capability registry: four defined capabilities (roadmap_repair, architecture_review, implementation_blocker_review, production_change_review), each with explicit enable/approve/authority rules. |
| Where does the registry live? | **Capability definitions** in `HERMES_AGENT_CONTRACT.md` §3.5d. **Per-repo enable states** in `CONTROL.md` `hermes.codex_capabilities`. |
| How does this interact with Task 18? | The `NEEDS_CODEX` validation outcome extends the Task 18 validation model. Codex escalation artifacts follow the same `agent/orchestration/<envelope-id>/` directory convention. |
| How does Codex remain an advisor, not the hidden orchestrator? | Codex never invokes itself. Codex output is always advisory. Hermes evaluates Codex output before accepting. Buddy approves every capability use unless pre-authorized. |
| Is this design ready for implementation? | **DESIGN_COMPLETE.** The capability model is stable. Implementation should follow the Task 18 migration plan, with Codex escalation added as a parallel track. |

---

## References

- `agents/HERMES_AGENT_CONTRACT.md` — Current Hermes contract (target for §3.5d)
- `agents/HERMES_ROADMAP_SUFFICIENCY_GATE.md` — Gate contract (trigger for roadmap_repair)
- `docs/OPERATING_MODEL.md` — Work ownership (Codex as architecture authority)
- `docs/REPOSITORY_CONTROL_MODEL.md` — CONTROL.md schema (target for codex_capabilities field)
- `agent/reports/session-12/18-hermes-artifact-storage-design-assessment.md` — Task 18 (artifact model)
- `agent/reports/session-12/09-codex-handoff-contract-preflight.md` — Task 14 (Codex escalation contract)
- `_internal/outbox/session-12/17-codex-handoff-integration-preflight.md` — Task 17 (integration analysis)
- `_internal/outbox/session-12/15-hermes-orchestration-learning-capture.md` — Learning capture (Codex escalation gap)
