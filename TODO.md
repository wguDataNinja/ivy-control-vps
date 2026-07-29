# Session 14 — H4 Supervised-Cycle Pilot: STS Workbench Dirty-State Preservation

## Intent

H0–H3 supervised-cycle contracts, schemas, and tests are complete and merged.
Session 14 executes the first H4 supervised-cycle pilot on STS Workbench
(STS-V1-01 — Dirty-State Preservation and Reconciliation), under the Alori
harness framework.

## Current verified state (end of Session 13 / H0-H3 completion)

- Session 13 Palworld branch-to-PR pilot completed through Gate 3 merge
- H0–H3 supervised-cycle contracts merged to main (31 passing tests)
- ROADMAP.md updated: §6B Phase 4 Complete, Phase 5 Active, §6C H4 Pilot Approved, §6D STS Admission In Progress
- ivy-control-vps on `main` at clean authoritative baseline (to be pushed)
- STS Workbench admitted as managed repository (CONTROL.md creation pending)

## Non-negotiable boundaries

- `_internal/` never staged/pushed
- No Git mutation during H4 pilot execution (read-only classification only)
- No product/runtime/credential/publishing scope in H4
- No destructive cleanup without approval
- One task in flight — H4 pilot only

---

## Phase A — ivy-control-vps Reconciliation (DONE)

- [x] Review and integrate H0–H3 branch through normal Git workflow
- [x] Preserve all unrelated pre-existing changes
- [x] Update ROADMAP.md and TODO.md
- [x] Establish clean authoritative baseline

## Phase B — STS Workbench Repository Admission

1. Create `repos/sts-workbench/CONTROL.md` with standard gate model
2. Verify STS Workbench checkout state against V1_FINISH_LINE_ROADMAP.md
3. Record admission evidence

### Read-only? YES — control record creation only
### Requires Buddy approval? YES — for admission validation

## Phase C — H4 Supervised Pilot: STS-V1-01

1. Preflight STS Workbench checkout (baseline SHA, dirty state, worktrees)
2. Create bounded task packet for Dirty-State Preservation and Reconciliation
3. Delegate to OpenCode for execution
4. Review evidence against task packet
5. Present at Buddy human gate for preservation strategy decision

### Expected artifact
- Task packet: `agent/inbox/sts-v1-01-dirty-state-preservation.md`
- Result report: `agent/reports/sts-v1-01-dirty-state-preservation.md`
- Hermes validation: `_internal/outbox/runs/session-14-sts-h4/hermes-validation.md`

### May write? Yes — task packets and reports in declared artifact paths only
### Requires Buddy approval? Yes — for preservation strategy decision (human gate)
