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

## Phase B — STS Workbench Repository Admission (DONE)

- [x] Create `repos/sts-workbench/CONTROL.md` with standard gate model
- [x] Verify STS Workbench checkout state against V1_FINISH_LINE_ROADMAP.md
- [x] Record admission evidence

## Phase C — H4 Supervised Pilot: STS-V1-01 (DONE)

- [x] Preflight STS Workbench checkout (baseline SHA, dirty state, worktrees)
- [x] Create bounded task packet for Dirty-State Preservation and Reconciliation
- [x] Delegate to OpenCode for execution
- [x] Review evidence against task packet (HERMES_ACCEPT)
- [x] Buddy approved preservation commit at `d60c3d5`

## Phase D — H4.1 Custody Pilot (DONE)

- [x] Integrate H4.1 branch into main (merge commit `412082b`)
- [x] Enable `local_commit: true` in STS CONTROL.md
- [x] Execute full supervised cycle + custody commit on V1_FINISH_LINE_ROADMAP.md
- [x] CUSTODY_COMMITTED at `cd36e36` on branch `custody/h4-1-roadmap-update`
- [x] Bug found and fixed in `_git()` stdout stripping
- [x] `local_commit` reset to `false` (bounded dispatch complete)

## Phase E — STS-V1-02 (PENDING BUDDY DECISION)

STS-V1-02 task packet is prepared at `_internal/inbox/runs/session-14-sts-h4/sts-v1-02-validation-baseline.md`.

**H4.1 custody pilot is complete and does NOT block STS-V1-02.** STS-V1-02 is a read-only classification task (no commit needed). The two are independent.

**Requires Buddy decision on the following pre-existing conditions:**

1. Whisper-adapter test failures (2) — environment-dependent; recommend defer
2. Contract validator exit 1 — known behavior; recommend defer
3. Palworld KB commit drift — locked `f94a618` vs current `9debe47`; expected
4. Contract registry not found at `v1/contracts/contract-registry.json`

See Decision Packet at: `_internal/outbox/runs/session-14-sts-h4/sts-v1-02-eligibility-decision-packet.md`

**After Buddy decision:** dispatch STS-V1-02 to OpenCode for validation baseline recording.
