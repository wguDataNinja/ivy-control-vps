# Session 12 — Task 20: Hermes Workflow Integration Preflight

**Date:** 2026-07-19
**Status:** INTEGRATION_READY

---

## Documents Reviewed

| Document | Relevant sections |
|---|---|
| `agents/HERMES_AGENT_CONTRACT.md` | §§3.5-3.5c (lifecycle, gate, authority boundaries), §3.4 (prohibited), role statement |
| `agents/HERMES_OPERATOR_GUIDE.md` | Role boundaries, stop conditions |
| `agents/HERMES_ROADMAP_SUFFICIENCY_GATE.md` | Full gate contract |
| `agents/VPS_ORCHESTRATION.md` | §§2, 4 (Hermes role, orchestration behavior) |
| `agents/orchestrator-task-packet-template.md` | Full template |
| `_internal/GPT_ORCHESTRATED_WORKFLOW.md` | §§10-16 (artifact lifecycle, session model, journal, agent roles, standard repo convention) |
| `docs/OPERATING_MODEL.md` | Hermes role, work ownership, authority model |
| `docs/REPOSITORY_CONTROL_MODEL.md` | CONTROL.md schema, Hermes permissions field, `codex_stops` |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | Artifact locations, artifact-only orchestration, lifecycle |
| `agent/reports/session-12/18-hermes-artifact-storage-design-assessment.md` | Artifact model (hybrid, `agent/orchestration/`) |
| `agent/reports/session-12/19-hermes-codex-escalation-capability-model.md` | Capability registry, NEEDS_CODEX outcome |

---

## 1. Workflow Overlap Analysis

### 1.1 Task 18 artifact lifecycle vs. existing workflow

The existing lifecycle defined in `_internal/GPT_ORCHESTRATED_WORKFLOW.md` §10E:

```
GPT reviews previous result
  → GPT emits next task prompt
  → agent performs task
  → agent writes result report
  → GPT reviews result
  → loop continues
```

Task 18 proposes:

```
Hermes reads delegation envelope
  → Hermes creates task packet
  → Execution agent produces report
  → Hermes validates and writes 03-*-validation.md
  → Continue or stop
```

| Existing concept | Task 18 equivalent | Relationship |
|---|---|---|
| Task prompt (`_internal/inbox/session-N/`) | Task packet (`agent/orchestration/<id>/01-*-packet.md`) | **Analogous role, different location.** The task packet is the public counterpart of the private inbox prompt. Same function (define delegated work), different visibility domain. |
| Result report (`_internal/outbox/session-N/`) | Execution report (`agent/orchestration/<id>/02-*-execution.md`) | **Analogous.** Existing private reports remain; execution reports in orchestration directories are the Hermes-visible public counterpart. |
| GPT acceptance (`ACCEPT`/`REWORK_REQUIRED`/etc.) | Hermes validation (`HERMES_ACCEPT`/`HERMES_REJECT`/etc.) | **New layer, not a replacement.** GPT acceptance remains the final review. Hermes validation is an intermediate check between execution and GPT review. |
| Portfolio journal | Orchestration state (`_internal/hermes/state/`) | **Complementary.** Journal records accepted outcomes; orchestration state tracks in-flight progress. Different retention (journal is permanent; state is per-envelope). |

**Conflict assessment: None.** Task 18 adds a new intermediate layer between
execution and review. It does not replace any existing artifact. The existing
private artifacts (`_internal/`) remain; the new public artifacts
(`agent/orchestration/`) are a parallel track for the Hermes-controlled flow.

### 1.2 Hermes validation vs. GPT session logs

`_internal/GPT_ORCHESTRATED_WORKFLOW.md` §14 defines detailed GPT session logs
as the narrative record of a session. Hermes validation reports
(`03-*-validation.md`) serve a different purpose:

| Dimension | GPT session log | Hermes validation report |
|---|---|---|
| Purpose | Narrative — decisions, rationale, rejected approaches | Checkpoint — did the execution report pass 5-point inspection? |
| Content | Free-form discussion | Structured PASS/FAIL checklist |
| Produced by | GPT (content) + agent (write) | Hermes |
| When | Session-level | Per-delegation |
| Audience | Future agents and Buddy | Hermes (next-delegation decision) |

**Conflict assessment: None.** Different purpose, different granularity,
different audience.

### 1.3 Task 19 Codex escalation vs. existing escalation

Existing escalation paths:

| Source | State | Behavior |
|---|---|---|
| `HERMES_AGENT_CONTRACT.md` §3.5 | `NEEDS_GPT_OR_BUDDY_DECISION` | Stop. Report. Wait. |
| `HERMES_AGENT_CONTRACT.md` §3.5a | `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` | Stop. Produce report. Escalate to Buddy. |
| Task 18 | `NEEDS_BUDDY_REVIEW` | Stop. Report to Buddy. |
| Task 19 | `NEEDS_CODEX` | Check capability registry → escalate to Codex or fall back to `NEEDS_BUDDY_REVIEW` |

**Conflict assessment: None.** `NEEDS_CODEX` is more specific than
`NEEDS_BUDDY_REVIEW` — it says "I know what capability would help, and it's
enabled." Hierarchy:

```
NEEDS_GPT_OR_BUDDY_DECISION (catch-all)
  └── NEEDS_BUDDY_REVIEW (needs human judgment)
  └── NEEDS_CODEX (needs architecture reasoning, capability is available)
  └── ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION (specific to roadmap gate failure)
```

---

## 2. Hermes Authority Model Assessment

### 2.1 Is NEEDS_CODEX a valid new state?

**Yes.** It fits naturally into the existing outcome hierarchy:

Current Hermes validation outcomes (from Task 18):
- `HERMES_ACCEPT`
- `HERMES_ACCEPT_WITH_NOTE`
- `HERMES_REJECT`
- `NEEDS_BUDDY_REVIEW`

Adding:
- `NEEDS_CODEX`

This gives Hermes four possible actions after reviewing an execution report:
1. Accept → continue
2. Accept with note → continue with observation
3. Reject → rework or escalate
4. Escalate to Codex → check registry → escalate or fall back
5. Escalate to Buddy → stop

### 2.2 Does NEEDS_CODEX conflict with existing escalation states?

**No.** Existing states are defined in:
- `HERMES_AGENT_CONTRACT.md` §3.5: `NEEDS_GPT_OR_BUDDY_DECISION` — catch-all
- `HERMES_AGENT_CONTRACT.md` §3.5a: `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` — gate-specific

`NEEDS_CODEX` is more specific than `NEEDS_GPT_OR_BUDDY_DECISION` and
different from `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` (which is about
roadmap quality, not execution failure).

### 2.3 Where should Codex escalation authority be defined?

**Capability definitions** in `HERMES_AGENT_CONTRACT.md` §3.5d. This follows
the existing pattern: §3.5a defines the gate, §3.5b defines the lifecycle,
§3.5c defines authority boundaries. §3.5d is the natural next section.

**Per-repo enable states** in `CONTROL.md`. The `hermes.codex_capabilities`
block follows the existing `hermes.scope` pattern — the contract defines what
_can_ happen; CONTROL.md defines what _does_ happen per repo.

### 2.4 Does CONTROL.md already provide the right per-repo policy boundary?

**Yes.** The existing pattern is:

```
CONTROL.md:
  hermes.scope: restricts Hermes action level
  hermes.artifact_paths: restricts where Hermes may write
  codex_stops: restricts Strong Codex
  buddy_decisions: pending decisions
```

Adding `hermes.codex_capabilities` follows this pattern exactly — per-repo
policy for a Hermes behavior dimension. No new mechanism needed.

---

## 3. Final Ownership Model

### 3.1 Artifact ownership

| Artifact | Proposed owner | Location | Existing precedent |
|---|---|---|---|
| Task packet | Hermes writes | Target repo `agent/orchestration/<id>/` | Analogous to `_internal/inbox/session-N/` (GPT_ORCHESTRATED_WORKFLOW §10A) |
| Execution report | Execution agent writes | Target repo `agent/orchestration/<id>/` | Analogous to `_internal/outbox/session-N/` (GPT_ORCHESTRATED_WORKFLOW §10A) |
| Hermes validation report | Hermes writes | Target repo `agent/orchestration/<id>/` | New — no existing precedent |
| Codex escalation context | Hermes writes | Target repo `agent/orchestration/<id>/` | New — no existing precedent |
| Codex output (reconciled) | OpenCode reconciles, Hermes validates | Target repo `agent/orchestration/<id>/` | Analogous to Codex handoff output (Task 17 analysis) |
| Execution log | Execution agent writes (optional) | Target repo `agent/orchestration/<id>/` or `_internal/logs/` | Defined in GPT_ORCHESTRATED_WORKFLOW §12C |
| Orchestration state | Hermes maintains | Ivy Control `_internal/hermes/state/` | New — private, per-envelope |
| Cross-repo session summary | Hermes writes | Ivy Control `agent/reports/session-<N>/` | Existing convention (e.g., `agent/reports/session-12/`) |
| Portfolio journal | GPT content, agent writes | Ivy Control `_internal/logs/sessions/` | Defined in GPT_ORCHESTRATED_WORKFLOW §13 |

### 3.2 Exceptions

| Exception | Rationale |
|---|---|
| **VPS resident checkout** cannot store `_internal/hermes/state/` | The VPS checkout is a clean public clone. Private orchestration state stays on Mac. Hermes on VPS would need a different state mechanism (bridge-based) or must operate without persistent state (each delegation is fresh). |
| **Codex output may originate from a different environment** | Codex is invoked by OpenCode via the `codex-handoff` skill, which runs on the development machine. The output artifact is copied or synced to the target repo's orchestration directory. This is acceptable because the orchestration directory is the durable record. |

### 3.3 Relationship to GPT_ORCHESTRATED_WORKFLOW.md §22 standard convention

§22 defines a standard repository convention with `agent/inbox/`,
`agent/reports/`, `agent/templates/`. Task 18's `agent/orchestration/` is a
natural extension — it handles the new Hermes-specific lifecycle while leaving
the existing convention intact. The existing `agent/reports/` continues to
hold standalone execution reports; `agent/orchestration/` holds multi-artifact
delegation sequences.

---

## 4. Document Sprawl Assessment

### 4.1 Proposed new documents from Tasks 18-19

| Proposed document | Needed? | Rationale |
|---|---|---|
| `agents/hermes-validation-report-template.md` | **Yes** — new template | Reusable template for the Hermes validation artifact, analogous to the existing `orchestrator-task-packet-template.md`. Following the existing pattern (templates live in `agents/`). |
| `agents/codex-escalation-context-template.md` | **Yes** — new template | Reusable template for the escalation context artifact. Same pattern as above. |
| `agents/CODEX_ESCALATION_PROTOCOL.md` | **No** | Capability definitions belong in `HERMES_AGENT_CONTRACT.md` §3.5d. Escalation lifecycle is already defined there. |
| `agents/CODEX_CAPABILITY_REGISTRY.md` | **No** | The capability registry is a section of the Hermes contract, not a standalone document. Per-repo enable states go in CONTROL.md. |
| `docs/HERMES_ARTIFACT_STORAGE.md` | **No** | Artifact storage conventions belong in `HERMES_AGENT_CONTRACT.md` (lifecycle) and `REPOSITORY_WORK_PROTOCOL.md` (artifact location table). |
| New permanent authority document | **None needed** | Both Task 18 and Task 19 concepts fit into existing documents. |

### 4.2 Net document change

| Type | Count |
|---|---|
| New permanent documents | **0** |
| New templates | **2** (`hermes-validation-report-template.md`, `codex-escalation-context-template.md`) |
| Existing contracts to update | **4** (HERMES_AGENT_CONTRACT.md, REPOSITORY_CONTROL_MODEL.md, REPOSITORY_WORK_PROTOCOL.md, OPERATING_MODEL.md) |

This satisfies the documentation governance rule from `docs/README.md`: each
new concept has a home in an existing authority document. No new permanent
documents are created.

### 4.3 Detailed update map

| Document | Content to add | New section |
|---|---|---|
| `agents/HERMES_AGENT_CONTRACT.md` | Validation outcomes (NEEDS_CODEX), capability definitions, escalation lifecycle, orchestration artifact chain | §3.5d Codex escalation capabilities |
| `agents/HERMES_AGENT_CONTRACT.md` | Reference to `agent/orchestration/` directory convention | §3.5b lifecycle |
| `docs/REPOSITORY_CONTROL_MODEL.md` | `hermes.codex_capabilities` field definition | Hermes permissions field section |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | `agent/orchestration/` in artifact location table | §4 table |
| `docs/OPERATING_MODEL.md` | Minor alignment — Codex escalation context | Work ownership table |
| `_internal/GPT_ORCHESTRATED_WORKFLOW.md` | Hermes validation step in lifecycle, update §16E Hermes role | §10E lifecycle, §16E |

---

## 5. Implementation Sequence

### 5.1 Ordered phases

```
Phase 1 — Contract updates (no behavioral change)
  1a. Add §3.5d Codex escalation capabilities to HERMES_AGENT_CONTRACT.md
      (capability definitions, NEEDS_CODEX outcome, escalation lifecycle)
  1b. Add orchestration artifact chain to §3.5b lifecycle
  1c. Add hermes.codex_capabilities field to REPOSITORY_CONTROL_MODEL.md
  1d. Add agent/orchestration/ to REPOSITORY_WORK_PROTOCOL.md artifact table
  1e. Align OPERATING_MODEL.md work ownership table

Phase 2 — Templates (enables artifact-driven operation)
  2a. Create agents/hermes-validation-report-template.md
  2b. Create agents/codex-escalation-context-template.md
  2c. Update orchestrator-task-packet-template.md to reference
      agent/orchestration/ paths

Phase 3 — Per-repo policy (enables controlled use)
  3a. Add hermes.codex_capabilities to each managed repository's CONTROL.md
  3b. Set initial state: all capabilities disabled
  3c. Create agent/orchestration/ directory in target repos

Phase 4 — Pilot (proves the model)
  4a. Enable roadmap_repair capability for one repository
  4b. Run controlled test: produce ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION
      → escalate to Codex → evaluate output
  4c. Validate the artifact chain (packet → execution → Hermes validation
      → Codex escalation → Codex output → Hermes re-validation)

Phase 5 — Broader enablement
  5a. Enable additional capabilities per-repo as needed
  5b. Add per-envelope orchestration state tracking
  5c. Evaluate whether NEEDS_CODEX should become a recurring pattern
```

### 5.2 Dependencies

| Phase | Depends on | Notes |
|---|---|---|
| 1 (contract) | Task 20 approval | Design is complete; contracts can be updated immediately |
| 2 (templates) | Phase 1 | Templates reference contract concepts |
| 3 (per-repo policy) | Phase 1 | CONTROL.md field must be defined before it can be set |
| 4 (pilot) | Phases 1-3 | All infrastructure must exist before test |
| 5 (broader) | Phase 4 | Pilot validates the model before scaling |

### 5.3 Items explicitly NOT in scope for initial implementation

| Item | Why excluded |
|---|---|
| `_internal/hermes/state/` orchestration state persistence | Not needed until multi-envelope orchestration is piloted. Hermes can operate stateless (each delegation is fresh) in v1. |
| `NEEDS_CODEX` automatic routing without Buddy approval | All capabilities start as `enabled_via_approval` — Buddy must approve each use until the pattern is proven. |
| Codex output auto-reconciliation | OpenCode must reconcile Codex output. Hermes cannot evaluate architecture output directly. |
| Cost tracking for Codex calls | Defer until Codex usage becomes frequent enough to need tracking. |

---

## 6. Unresolved Decisions

| Decision | Options | Recommendation |
|---|---|---|
| Should `agent/orchestration/` be created upfront in all repos or only when first needed? | Proactive vs. on-demand | **On-demand.** Create when the first delegation occurs. No empty directories. |
| Should Hermes validation outcomes include a severity level? | Yes vs. no | **Defer.** Start with binary outcomes (ACCEPT/REJECT) and add granularity if needed. |
| Should Codex escalation context include the full execution report or a summary? | Full vs. summary | **Summary + references.** The escalation context should be compact enough for Codex to read efficiently, with links to the full execution report for detail. |
| Should the capability registry be discoverable by Hermes or hardcoded in the contract? | Discoverable vs. hardcoded | **Hardcoded.** The four defined capabilities cover known escalation needs. Discovery would imply Hermes can use capabilities not designed for it. |
| Should Hermes log every escalation attempt (including disabled ones) for audit? | Log vs. no log | **Yes.** Log the attempt, capability requested, and why it was denied (disabled, not approved, no matching capability). Audit trail for security review. |

---

## 7. Summary

| Question | Answer |
|---|---|
| Does Task 18 artifact lifecycle conflict with existing workflow? | **No.** Adds an intermediate validation layer between execution and GPT review. Complements existing artifacts without replacing them. |
| Does Task 19 Codex capability model conflict with Hermes contract? | **No.** `NEEDS_CODEX` fits naturally into the outcome hierarchy. Per-repo CONTROL.md follows existing pattern. |
| What is the final ownership model? | **Hybrid.** Target repos own `agent/orchestration/<id>/` artifacts. Ivy Control owns contracts, state, and cross-repo summaries. |
| How many new documents are needed? | **Zero permanent documents. Two templates.** All concepts fit into existing contracts. |
| What is the implementation sequence? | 5 phases: (1) contract updates, (2) templates, (3) per-repo policy, (4) pilot, (5) broader enablement. |
| What is the integration status? | **INTEGRATION_READY.** Both Task 18 and Task 19 designs integrate cleanly with the existing workflow. No conflicts, no duplication, no document sprawl. |

---

## References

- `agent/reports/session-12/18-hermes-artifact-storage-design-assessment.md` — Task 18 (artifact model)
- `agent/reports/session-12/19-hermes-codex-escalation-capability-model.md` — Task 19 (capability model)
- `agent/reports/session-12/09-codex-handoff-contract-preflight.md` — Task 14 (Codex contract)
- `_internal/outbox/session-12/17-codex-handoff-integration-preflight.md` — Task 17 (integration analysis)
- `_internal/GPT_ORCHESTRATED_WORKFLOW.md` — Private workflow (reference for all lifecycle comparisons)
- `agents/HERMES_AGENT_CONTRACT.md` — Hermes contract (target for §3.5d)
- `docs/REPOSITORY_CONTROL_MODEL.md` — CONTROL.md schema (target for codex_capabilities field)
- `docs/REPOSITORY_WORK_PROTOCOL.md` — Public work protocol (artifact locations)
