# Session 12 — Task 22: Hermes Contract Phase 1 Implementation

**Date:** 2026-07-19
**Status:** PHASE1_COMPLETE

---

## Changes Made

### Preflight: Artifact convention decision

Before implementing, I inspected current artifact conventions across
ivy-control-vps, palworld-kb, and sts-workbench.

**Decision: Do NOT introduce `agent/orchestration/` in Phase 1.**

Rationale:
- Phase 1 is contract updates only. No Hermes orchestration runs yet — no task
  packets are being created, no validation reports are being written.
- The lifecycle is documented using existing declared artifact paths. The
  contract says "artifacts will be stored in the target repository's declared
  artifact paths" without mandating a specific subdirectory.
- Introducing a directory convention before any orchestration runs would create
  empty directories and violate the "on-demand, not proactive" principle.
- The `agent/orchestration/` convention can be introduced in Phase 2
  (templates) when templates need to reference actual paths.

Existing locations (`agent/inbox/`, `agent/reports/`, `_internal/outbox/`) are
sufficient for Phase 1 documentation. Adding a new directory now would create
a duplicate workflow system (two places to find Hermes artifacts) without any
artifacts to store.

### File-by-file summary

| File | Change | Type |
|---|---|---|
| `agents/HERMES_AGENT_CONTRACT.md` | Replaced §3.5b with Hermes validation lifecycle, 5-point checklist, and 6 outcome paths. New §3.5c (validation outcomes table). New §3.5d (Codex escalation capabilities — 4 capabilities with purpose, trigger, authority limits, approval). New §3.5e (authority boundaries updated). Added Codex invocation prohibition to §3.4. | **Additive + replacement** |
| `docs/REPOSITORY_CONTROL_MODEL.md` | New "Codex capabilities field" subsection after Hermes permissions field. Defines `hermes.codex_capabilities` YAML block with 4 capabilities, enable states, schema example, and state meanings. | **Additive** |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | Updated artifact-only orchestration lifecycle to include Hermes validation step and all 5 validation outcomes. Added reference to HERMES_AGENT_CONTRACT.md for criteria and outcomes. | **Additive** |
| `docs/OPERATING_MODEL.md` | Added Codex escalation capabilities to Strong Codex work class examples in work ownership table. | **Additive** |
| `docs/HERMES_OPERATOR_GUIDE.md` | Updated role boundaries table — Hermes row now describes orchestration layer; Strong Codex row describes controlled invocation; Buddy row includes Codex escalation approval. Added Codex escalation to escalate-to-Buddy list. | **Replacement** |
| `agents/VPS_ORCHESTRATION.md` | Updated Hermes role description to include evidence validation, acceptance/rejection outcomes, and controlled Codex escalation. | **Additive** |
| `agents/orchestrator-task-packet-template.md` | Updated Checkpoint Rules to reference validation criteria from HERMES_AGENT_CONTRACT.md §3.5b. Updated After Completion to reference validation outcomes (ACCEPT/ACCEPT_WITH_NOTE as continuation gates). | **Replacement** |

---

## New Concepts Introduced

| Concept | Defined in | Default state |
|---|---|---|
| Hermes validation lifecycle | §3.5b | Required step between execution and continuation |
| 5 validation checks | §3.5b | Completeness, evidence, scope, stop conditions, claims |
| `HERMES_ACCEPT` | §3.5c | May continue |
| `HERMES_ACCEPT_WITH_NOTE` | §3.5c | May continue |
| `HERMES_REJECT` | §3.5c | No — rework or escalate |
| `NEEDS_BUDDY_REVIEW` | §3.5c | No — stop and report |
| `NEEDS_CODEX` | §3.5c | No — check capability registry |
| `roadmap_repair` capability | §3.5d | Disabled, approval required |
| `architecture_review` capability | §3.5d | Disabled, approval required |
| `implementation_blocker_review` capability | §3.5d | Disabled, approval required |
| `production_change_review` capability | §3.5d | Disabled, approval required |
| `hermes.codex_capabilities` schema | REPOSITORY_CONTROL_MODEL.md | All disabled, approval required |

---

## Validation

| Check | Result |
|---|---|
| No contradictory authority statements | PASS — validation lifecycle is additive (between execution and continuation); does not conflict with any existing authority |
| No duplicate workflow concepts | PASS — validation outcomes extend existing checkpoint rule; they do not replace it |
| No claim that Codex is autonomous | PASS — explicit prohibition: "Hermes does not autonomously invoke Codex" in §3.5d, "never autonomously" in HERMES_OPERATOR_GUIDE.md |
| No claim that validation already exists operationally | PASS — validation is documented as a required future step, not an existing operational practice |
| All 7 modified documents consistent | PASS — outcomes, capability names, and authority limits are consistent across all documents |
| `NEEDS_CODEX` correctly gated | PASS — defined as "not permission to call Codex" with fallback to `NEEDS_BUDDY_REVIEW` when disabled |

---

## Remaining Work (Phase 2+)

| Phase | Items | When |
|---|---|---|
| Phase 2 — Templates | Create `agents/hermes-validation-report-template.md`, `agents/codex-escalation-context-template.md`. Update `orchestrator-task-packet-template.md` with orchestration path references. | After Phase 1 approved |
| Phase 3 — Per-repo policy | Add `hermes.codex_capabilities` to CONTROL.md for pilot repos. Create `agent/orchestration/` directories on demand. | After Phase 2 |
| Phase 4 — Codex skill migration | Migrate `codex-handoff` skill from old `ivy-control` repo to `ivy-control-vps/.opencode/skills/` | Before Phase 4 pilot |
| Phase 5 — Pilot | Enable `roadmap_repair` on Palworld KB. Run full escalation chain. | After Phases 1-4 |
| Phase 6 — Evaluation | Review pilot results, decide on broader capability enablement | After Phase 5 |

---

## References

- `agent/reports/session-12/21-hermes-contract-integration-plan.md` — Task 21 implementation plan (source for this task)
- `agent/reports/session-12/20-hermes-workflow-integration-preflight.md` — Integration assessment
- `agent/reports/session-12/19-hermes-codex-escalation-capability-model.md` — Capability model design
- `agent/reports/session-12/18-hermes-artifact-storage-design-assessment.md` — Artifact model design
