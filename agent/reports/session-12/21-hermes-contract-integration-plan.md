# Session 12 — Task 21: Hermes Contract Integration Implementation Plan

**Date:** 2026-07-19
**Status:** IMPLEMENTATION_PLAN_READY

---

## Documents Reviewed

| Document | Version/Status |
|---|---|
| `agents/HERMES_AGENT_CONTRACT.md` | 241 lines — current with §3.5a-3.5c |
| `agents/VPS_ORCHESTRATION.md` | 341 lines — Mode 0, Hermes role, lifecycle |
| `agents/HERMES_ROADMAP_SUFFICIENCY_GATE.md` | 203 lines — gate v1 |
| `agents/orchestrator-task-packet-template.md` | 78 lines — current template |
| `docs/HERMES_OPERATOR_GUIDE.md` | 190 lines — role boundaries, stop conditions |
| `docs/OPERATING_MODEL.md` | 235 lines — work ownership, authority model |
| `docs/REPOSITORY_CONTROL_MODEL.md` | 583 lines — CONTROL.md schema, Hermes permissions field |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | 265 lines — artifact lifecycle, orchestration section |
| `_internal/GPT_ORCHESTRATED_WORKFLOW.md` | 1695 lines — private workflow, agent roles, artifact conventions |
| `agent/reports/session-12/18-hermes-artifact-storage-design-assessment.md` | Task 18 design |
| `agent/reports/session-12/19-hermes-codex-escalation-capability-model.md` | Task 19 design |
| `agent/reports/session-12/20-hermes-workflow-integration-preflight.md` | Task 20 integration assessment |

---

## 1. Current Architecture

### 1.1 Hermes lifecycle (current)

Defined in `HERMES_AGENT_CONTRACT.md` §3.5b:

```
Orient → Read authority → Eligibility checks
  → Roadmap sufficiency evaluation
  → [READY] → Create task packet → Delegate execution
  → Review result evidence → Update journal/state → Continue or stop
  → [INSUFFICIENT] → Report → Escalate → Wait
```

### 1.2 Orchestration artifacts (current)

- Task packet: `agents/orchestrator-task-packet-template.md`
- Result report: free-form, per-repo convention (table in `REPOSITORY_WORK_PROTOCOL.md` §4)
- No structured validation artifact between execution and continuation
- No Codex escalation artifact

### 1.3 Gaps to close

| Gap | Addressed by |
|---|---|
| No durable Hermes validation artifact between execution and continuation | Task 18: `03-*-validation.md` |
| No structured validation outcomes | Task 18: `HERMES_ACCEPT`/`REJECT`/`NEEDS_BUDDY_REVIEW`/`NEEDS_CODEX` |
| No Codex escalation mechanism | Task 19: capability registry, escalation lifecycle |
| No standard orchestration directory | Task 18: `agent/orchestration/<envelope-id>/` |
| No per-repo Codex capability policy | Task 19: `hermes.codex_capabilities` in CONTROL.md |
| No validation or escalation templates | Task 18/19: two new templates needed |

---

## 2. Exact File-by-File Change Map

### 2.1 `agents/HERMES_AGENT_CONTRACT.md`

| Change | Location | Type | Purpose |
|---|---|---|---|
| Add orchestration artifact chain to lifecycle | §3.5b | **Additive** | Show `agent/orchestration/` path convention and new artifact sequence (packet → execution → Hermes validation → escalation if needed → accept/reject → next) |
| Add `NEEDS_CODEX` to validation outcomes | §3.5b | **Additive** | New outcome when Hermes identifies a matching Codex capability |
| Add reference to orchestration directory convention | §3.5b | **Additive** | Link to `agent/orchestration/` as the standard location for orchestration artifacts |
| Add §3.5d Codex Escalation Capabilities | New section after §3.5c | **Additive** | Define four capabilities (roadmap_repair, architecture_review, implementation_blocker_review, production_change_review) with purpose, trigger, input/output, authority limits |
| Add escalation lifecycle to §3.5d | §3.5d | **Additive** | Flow: detect condition → check registry → produce escalation context → Buddy approves → Codex invoked → Codex output reconciled → Hermes evaluates |
| Add prohibition: Hermes must not invoke Codex directly | §3.4 | **Additive** | Reinforce that Codex invocation requires Buddy approval |
| Update reading route step 10 to include orchestration directory | §2 | **Additive** | Hermes reads `agent/orchestration/` during orientation |

### 2.2 `docs/REPOSITORY_CONTROL_MODEL.md`

| Change | Location | Type | Purpose |
|---|---|---|---|
| Add `hermes.codex_capabilities` field definition | Hermes permissions field section (line 505) | **Additive** | Define the YAML block for per-repo Codex capability enablement |
| Add capability state semantics (disabled/enabled_via_approval/enabled) | Same section | **Additive** | Define what each state means and how transitions work |

### 2.3 `docs/REPOSITORY_WORK_PROTOCOL.md`

| Change | Location | Type | Purpose |
|---|---|---|---|
| Add `agent/orchestration/` to repository-approved locations table | §4 table | **Additive** | New row for orchestration artifact location convention |
| Add orchestration artifacts to artifact distinctions table | §6 table | **Additive** | New rows: task packet (evidence only), Hermes validation report (evidence only), Codex output (advisory) |
| Update artifact-only orchestration section to reference validation | §6 Artifact-only orchestration | **Additive** | After "Hermes review" step, add "Hermes writes validation report → ACCEPT/REJECT/NEEDS_CODEX → next" |

### 2.4 `docs/OPERATING_MODEL.md`

| Change | Location | Type | Purpose |
|---|---|---|---|
| Add Codex escalation context to Strong Codex work class | Work ownership table | **Additive** | Strong Codex row: add "Codex escalation (roadmap repair, architecture review, blocker review, production review)" to examples |

### 2.5 `docs/HERMES_OPERATOR_GUIDE.md`

| Change | Location | Type | Purpose |
|---|---|---|---|
| Add Codex escalation to stop conditions | Stop and escalation boundaries section | **Additive** | Add "Hermes detecting a condition requiring Codex escalation must produce escalation context and wait for Buddy approval" |
| Update role boundaries to match | Role boundaries table | **Replacement** | Hermes row: change "may coordinate explicit artifact-only tasks" to include validation and escalation |

### 2.6 `agents/VPS_ORCHESTRATION.md`

| Change | Location | Type | Purpose |
|---|---|---|---|
| Update Hermes role description to mention validation | §2 Hermes role | **Additive** | Hermes validates execution results and may escalate to Codex when authorized |
| Update orchestration behavior to reference validation outcomes | §4 Orchestration behavior | **Additive** | After delegation, Hermes writes validation report before continuing |

### 2.7 `agents/orchestrator-task-packet-template.md`

| Change | Location | Type | Purpose |
|---|---|---|---|
| Add orchestration artifact path template | After Delegation Target section | **Additive** | "Orchestration artifacts will be stored at: `agent/orchestration/<envelope-id>/`" |
| Update Checkpoint Rules to reference validation report | Checkpoint Rules section | **Replacement** | Change "Hermes verifies" to "Hermes writes 03-*-validation.md and verifies" |

---

## 3. New Files to Create

### 3.1 `agents/hermes-validation-report-template.md`

**Type:** Reusable template (like `orchestrator-task-packet-template.md`)

**Fields:**
- Envelope reference
- Task packet path
- Execution report path
- 5-point checkpoint checklist: (1) artifact completeness, (2) validation evidence, (3) scope compliance, (4) stop conditions, (5) claim verification
- Outcome: `HERMES_ACCEPT` / `HERMES_ACCEPT_WITH_NOTE` / `HERMES_REJECT` / `NEEDS_BUDDY_REVIEW` / `NEEDS_CODEX`
- Evidence links
- Next action: continue / stop / escalate

### 3.2 `agents/codex-escalation-context-template.md`

**Type:** Reusable template

**Fields:**
- Capability requested
- Trigger condition
- Repository and envelope ID
- Problem statement (what Hermes cannot resolve)
- Current state (verified facts)
- Constraints (what Codex must not do)
- Specific questions Codex must answer
- Output format expected
- Authority limits (what Codex may not decide)

---

## 4. Per-Repository CONTROL.md Updates

### 4.1 None in initial Phase 1 (contracts only)

Per-repo CONTROL.md updates are Phase 3. The initial implementation adds the
field definition to `REPOSITORY_CONTROL_MODEL.md` but does not populate it in
any repo.

### 4.2 Future CONTROL.md additions

Each managed repository that will use Hermes orchestration gets:

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

Initial state: all capabilities disabled, approval required.

---

## 5. Migration Sequence

### Phase 1: Documentation and contracts

| Step | Files | Effort |
|---|---|---|
| 1a. Add §3.5d to `HERMES_AGENT_CONTRACT.md` | 1 file | ~50 lines |
| 1b. Update §3.5b lifecycle with validation outcomes and artifact chain | 1 file | ~15 lines |
| 1c. Add `hermes.codex_capabilities` to `REPOSITORY_CONTROL_MODEL.md` | 1 file | ~20 lines |
| 1d. Add `agent/orchestration/` to `REPOSITORY_WORK_PROTOCOL.md` artifact table | 1 file | ~10 lines |
| 1e. Update `OPERATING_MODEL.md` work ownership table | 1 file | ~5 lines |
| 1f. Update `HERMES_OPERATOR_GUIDE.md` role boundaries | 1 file | ~5 lines |
| 1g. Update `VPS_ORCHESTRATION.md` Hermes role description | 1 file | ~5 lines |

**Validation after Phase 1:** Contracts are internally consistent. No
behavioral change yet — Hermes continues to operate as before.

### Phase 2: Templates

| Step | Files | Effort |
|---|---|---|
| 2a. Create `agents/hermes-validation-report-template.md` | 1 file | ~40 lines |
| 2b. Create `agents/codex-escalation-context-template.md` | 1 file | ~40 lines |
| 2c. Update `agents/orchestrator-task-packet-template.md` with orchestration paths | 1 file | ~10 lines |

**Validation after Phase 2:** Templates exist and can be used manually.
Orchestration directory convention is documented.

### Phase 3: Per-repository policy

| Step | Files | Effort |
|---|---|---|
| 3a. Add `hermes.codex_capabilities` to `repos/ivy-control-vps/CONTROL.md` | 1 file | ~10 lines |
| 3b. Add `hermes.codex_capabilities` to Palworld KB CONTROL.md | 1 file | ~10 lines |
| 3c. Add `agent/orchestration/` to Palworld KB AGENTS.md or CONTROL.md artifact paths | 1 file | ~5 lines |
| 3d. Create `agent/orchestration/` directory in Palworld KB | 1 file | mkdir |

**Validation after Phase 3:** Policy exists but all capabilities are disabled.
No Codex calls will be made.

### Phase 4: Pilot — roadmap repair on Palworld KB

| Step | Action | Owner |
|---|---|---|
| 4a. Set `roadmap_repair.enabled` to `enabled_via_approval` for Palworld KB | Edit CONTROL.md | Buddy |
| 4b. Run Hermes roadmap gate on Palworld KB ROADMAP.md | Execute gate | Hermes |
| 4c. If gate passes — pilot ends early (roadmap is already sufficient) | Document result | Hermes |
| 4d. If gate fails — Hermes produces insufficiency report and escalation context | Write artifacts | Hermes |
| 4e. Buddy reviews and approves Codex escalation | Approve | Buddy |
| 4f. OpenCode invokes codex-handoff skill with escalation context | Execute skill | OpenCode |
| 4g. OpenCode reconciles Codex output | Reconcile | OpenCode |
| 4h. Hermes evaluates reconciled output and reruns gate | Validate | Hermes |

**Validation after Phase 4:** Full artifact chain proven. Codex escalation
works as designed.

### Phase 5: Evaluation

| Step | Action |
|---|---|
| 5a. Review pilot results: did `NEEDS_CODEX` correctly route to Codex? |
| 5b. Review artifact chain: were all 5 artifacts produced? |
| 5c. Decide: enable more capabilities, or keep all disabled except `roadmap_repair`? |
| 5d. Update contracts based on lessons learned |

---

## 6. Pilot Plan

### 6.1 Target

Palworld KB — the roadmap sufficiency gate has already been validated against
this repo in Task 13 (all 6 criteria passed). The pilot tests the escalation
path, not the gate itself.

### 6.2 Required environment

| Prerequisite | Status | Action needed |
|---|---|---|
| Palworld KB has a CONTROL.md with `hermes.codex_capabilities` | Not yet | Phase 3 |
| `roadmap_repair` capability enabled | Not yet | Phase 4a |
| `codex-handoff` skill available in ivy-control-vps | Orphaned in old repo | Migrate skill or reference it remotely |
| Palworld KB ROADMAP.md exists | Yes | Already read in Task 13 |
| Clean working baseline | Experiment output unclassified | Needed before delegation |

### 6.3 Required artifacts

| Artifact | Path |
|---|---|
| Task packet | `palworld-kb/agent/orchestration/<id>/01-gate-packet.md` |
| Hermes insufficiency report | `palworld-kb/agent/orchestration/<id>/02-insufficiency-report.md` |
| Codex escalation context | `palworld-kb/agent/orchestration/<id>/03-escalation-context.md` |
| Codex output (reconciled) | `palworld-kb/agent/orchestration/<id>/04-codex-output.md` |
| Hermes re-validation | `palworld-kb/agent/orchestration/<id>/05-revalidation.md` |

### 6.4 Validation steps

| Step | Check |
|---|---|
| 1 | Does Hermes detect that the capability is `enabled_via_approval`? |
| 2 | Does Hermes produce the escalation context artifact? |
| 3 | Does Buddy have enough context to approve or reject? |
| 4 | Does the `codex-handoff` skill correctly invoke Codex? |
| 5 | Does OpenCode reconcile Codex output (fix paths, correct assumptions)? |
| 6 | Does Hermes evaluate the reconciled output? |
| 7 | Does Hermes produce a final validation (ACCEPT or REJECT)? |

### 6.5 Success criteria

| Criterion | Measure |
|---|---|
| Complete artifact chain | All 5 artifacts exist in `agent/orchestration/<id>/` |
| Codex output is reconciled | No hallucinated paths or assumptions in final proposal |
| Hermes validation is correct | Validation report correctly identifies outcome (ACCEPT/REJECT) |
| Roadmap gate re-run produces consistent result | If Codex clarified the roadmap, the gate should pass on re-run |

---

## 7. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Codex hallucinates paths or requirements in escalation output | High | Medium | OpenCode reconciliation step before Hermes evaluates |
| Hermes incorrectly identifies a matching capability | Low | Medium | Capability definitions are explicit; `NEEDS_CODEX` falls back to `NEEDS_BUDDY_REVIEW` if no match |
| Pilot finds the gate already passes (no escalation needed) | Medium | Low | Document that the roadmap is sufficient; pilot proves the gate works, not the escalation path |
| codex-handoff skill is unavailable in ivy-control-vps | High | High | Migrate from old repo before Phase 4 |
| Buddy becomes bottleneck for escalation approval | Medium | Low | Capabilities start as `enabled_via_approval`; evaluate whether to pre-authorize after pilot |

---

## 8. Open Decisions

| Decision | Options | Recommendation |
|---|---|---|
| Should `agent/orchestration/` be created proactively or on first use? | Proactive vs. on-demand | **On-demand** — create when first delegation occurs |
| Should the `codex-handoff` skill be migrated as part of Phase 2? | Yes vs. defer | **Yes** — it's a prerequisite for Phase 4 pilot and a simple copy operation |
| Should the Palworld KB pilot require a clean working tree first? | Yes vs. no | **Yes** — experiment output must be classified before any Hermes delegation |
| Should the implementation be done as one task or split across sessions? | One vs. multiple | **Split** — Phase 1 (contracts) is one task; Phase 2 (templates) is a second; Phase 3-4 (policy + pilot) is a third |
| Should the `NEEDS_CODEX` outcome be added before or after the pilot? | Before vs. after | **Before** — the outcome must exist in the contract before the escalation path can be tested |

---

## 9. Summary

| Dimension | Plan |
|---|---|
| Files changed | 7 existing files (additive changes only) |
| New files | 2 templates, 1 artifact directory (per target repo) |
| Phases | 5 sequential phases |
| First implementation | Phase 1 — contract updates only |
| Pilot | Phase 4 — Palworld KB roadmap repair |
| Total new contract lines | ~110 lines (across all documents) |
| Total new template lines | ~80 lines (2 templates) |

**The plan is ready for execution.** Phase 1 (contract updates) can begin
immediately. Phases 2-5 depend on Phase 1 completion.

---

## References

- `agent/reports/session-12/18-hermes-artifact-storage-design-assessment.md` — Artifact model (Task 18)
- `agent/reports/session-12/19-hermes-codex-escalation-capability-model.md` — Capability model (Task 19)
- `agent/reports/session-12/20-hermes-workflow-integration-preflight.md` — Integration assessment (Task 20)
- `agents/HERMES_AGENT_CONTRACT.md` — Current contract (target for §3.5d)
- `docs/REPOSITORY_CONTROL_MODEL.md` — CONTROL.md schema (target for codex_capabilities field)
- `docs/REPOSITORY_WORK_PROTOCOL.md` — Artifact conventions (target for orchestration directory)
- `agents/orchestrator-task-packet-template.md` — Existing template (model for new templates)
