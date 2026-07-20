# Session 12 — Task 16: Hermes Orchestration Contract and Lifecycle Formalization

**Date:** 2026-07-19
**Status:** COMPLETED — documentation updates applied to 4 files

---

## Changed Files

| File | Changes |
|---|---|
| `agents/HERMES_AGENT_CONTRACT.md` | Title updated to "Orchestration Layer". New role statement. Updated §1 applicability. New §3.5 (Orchestration lifecycle), §3.5a (Roadmap sufficiency gate), §3.5b (Lifecycle diagram), §3.5c (Authority boundaries). Old §3.5 renamed to §3.6. Pilot section updated. |
| `agents/VPS_ORCHESTRATION.md` | Updated §2 (Hermes role) — added orchestration definition, "what Hermes does not" list. New §2.1 (Artifact-driven orchestration lifecycle). |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | Updated artifact-only orchestration section — added lifecycle diagram, roadmap gate reference, "Hermes coordinates; agents implement; Buddy approves" summary. |
| `docs/OPERATING_MODEL.md` | Updated authority model — Hermes redefined as orchestration layer. Updated work ownership table — Hermes moved above OpenCode with orchestration work class. Added roadmap gate reference. Expanded agent descriptions. |

---

## Design Decisions Preserved

| Decision | How the documents reflect it |
|---|---|
| Roadmap gate remains a procedure, not a software system | Referenced from `agents/HERMES_ROADMAP_SUFFICIENCY_GATE.md` in both HERMES_AGENT_CONTRACT.md and REPOSITORY_WORK_PROTOCOL.md. Explicitly called "behavioral procedure, not a software gate" in §3.5a. |
| Specialist agents not created for checklist tasks | Hermes role emphasizes coordination, not separate sub-agents. The lifecycle shows Hermes follows procedures, not that it spawns specialist agents for each step. |
| Codex remains architecture authority | §3.5c authority table and OPERATING_MODEL.md work ownership both assign architecture to Codex, not Hermes. |
| Execution remains bounded by task packets | VPS_ORCHESTRATION.md §2.1 lifecycle shows task packet as the delegation boundary. HERMES_AGENT_CONTRACT.md §3.5a says Hermes must not invent requirements or expand scope. |

---

## Remaining Gaps (Intentionally Not Addressed)

| Gap | Why deferred |
|---|---|
| Structured result artifact schema | Would require changing how all agents write reports — beyond a Hermes contract update. |
| Branch workflow for Hermes | Requires per-repo Buddy decisions, scope upgrades, and credential design. Not a documentation gap. |
| Codex escalation automation | Task 14 defined the contract; implementation requires §3.5c to be added to HERMES_AGENT_CONTRACT.md. Deferred until after first pilot. |
| Persistent Hermes task state | Hermes currently operates fresh per delegation. State persistence would require a new artifact type (orchestration state file). Not needed until multi-step orchestration is piloted. |
| Journal proposal template | Hermes can write `PENDING_GPT_REVIEW` journal proposals now, but has no defined format. Deferred until a template is extracted from practice. |

---

## References

- `_internal/outbox/session-12/15-hermes-orchestration-learning-capture.md` — Authority for this task
- `agent/reports/session-12/06-hermes-roadmap-sufficiency-preflight.md` — Task 11
- `agent/reports/session-12/07-hermes-orchestration-contract-plan.md` — Task 12
- `agent/reports/session-12/08-hermes-roadmap-gate-pilot-validation.md` — Task 13
- `agent/reports/session-12/09-codex-handoff-contract-preflight.md` — Task 14
