# Session 12 — Task 06: Documentation Reconciliation After VPS Residency Implementation

**Date:** 2026-07-20
**Status:** COMPLETED — documentation analysis and controlled updates
**Predecessor:** Codex Session 12 implementation (report at `agent/reports/session-12/00-session12-implementation-report.md`)

---

## 1. Codex Changes Reviewed

### Files created

| File | Purpose |
|---|---|
| `agents/orchestrator-task-packet-template.md` | Reusable bounded-task packet for Hermes Mode 0 dispatch |
| `repos/ivy-control-vps/CONTROL.md` | Self-governance record for the control plane itself |

### Files modified

| File | What Codex added |
|---|---|
| `docs/OPERATING_MODEL.md` | Hermes scope updated to "dispatched artifact-only coordination"; separated workspace from production |
| `docs/GIT_WORKFLOW.md` | New §VPS engineering-workspace readiness — sparse checkout, _internal exclusion, rollback SHA, boundary rules |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | New §VPS workspace artifact boundary (artifact paths declaration requirement); §Artifact-only orchestration (Hermes Mode 0 envelope rules) |
| `agents/VPS_ORCHESTRATION.md` | Current resident checkout state; Mode 0 interaction mode |
| `agents/HERMES_AGENT_CONTRACT.md` | Delegation-envelope checkpoint rule; Palworld pilot conditions |
| `docs/HERMES_OPERATOR_GUIDE.md` | Aligned with resident-agent boundaries |
| `docs/RESIDENT_AGENT_MODEL.md` | Minor alignment updates |
| `docs/REPOSITORY_CONTROL_MODEL.md` | Artifact-only scope vocabulary |
| `tools/portfolio_registry.py` | Artifact-only scope support |
| `docs/VPS_INVENTORY.md` | ivy-control-vps workspace entry updated with approved SHA and residency verification note |

### New concepts introduced

| Concept | Definition |
|---|---|
| **VPS engineering workspace** | Clean public Git checkout for controlled ongoing work — not production |
| **Mode 0 / artifact-only orchestration** | Hermes may only create task packets, factual reviews, orchestration logs, journal proposals in declared paths |
| **Delegation envelope** | Bounded authority container: target repo, roadmap section, permitted paths, executor, validation, max tasks, checkpoint cadence, escalation owner |
| **VPS artifact boundary** | AGENTS.md or CONTROL.md must declare publication-safe artifact paths for Hermes |
| **Self-governance CONTROL.md** | ivy-control-vps now has its own CONTROL.md like any managed repo |

---

## 2. Documentation Impact Map

### Documents that now accurately describe the system

| Document | Status |
|---|---|
| `docs/OPERATING_MODEL.md` | ✅ Accurate — Hermes role updated, workspace/production distinction clear |
| `docs/GIT_WORKFLOW.md` | ✅ Accurate — residency rules, sparse checkout, _internal exclusion defined |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | ✅ Accurate — artifact boundary and orchestration lifecycle added |
| `agents/VPS_ORCHESTRATION.md` | ✅ Accurate — Mode 0 and current checkout state |
| `agents/HERMES_AGENT_CONTRACT.md` | ✅ Accurate — envelope checkpoint, Palworld pilot |
| `agents/orchestrator-task-packet-template.md` | ✅ Created — matches session-close process, complements REPOSITORY_WORK_PROTOCOL.md |
| `repos/ivy-control-vps/CONTROL.md` | ✅ Created — self-governance, workspace residency, Hermes scope |
| `docs/VPS_INVENTORY.md` | ✅ Updated — control-plane workspace entry with approved SHA |

### Documents that are stale or need attention

| Document | Issue |
|---|---|
| `docs/PORTFOLIO_INTENT.md` | Pre-existing untracked authority doc — not in scope but public README.md indexes it |
| `_internal/vps-inventory-and-runbook.md` | Private runbook references historical VPS op state that may conflict with verified workspace state (noted in Codex report, not altered) |

### Documents that correctly did NOT change

| Document | Why unchanged |
|---|---|
| `README.md` | High-level overview — no new concept requires a change |
| `ROADMAP.md` | Priorities unchanged by workspace residency |
| `TODO.md` | Protected — workspace residency was tracked there |
| `docs/REPOSITORY_CONTROL_MODEL.md` | Only minor vocabulary addition — 6-gate model unchanged |
| `docs/PORTFOLIO_CONVENTIONS.md` | Naming/systemd conventions unaffected by residency |

---

## 3. Existing Authority Analysis

### Concept ownership trace

| Concept | Current owner(s) | Missing? | Proposed action |
|---|---|---|---|
| GitHub/public repo boundary | `docs/GIT_WORKFLOW.md` §Principles | No | Already clear — principles declare public-only content, _internal is separate repo |
| VPS residency | `docs/GIT_WORKFLOW.md` §VPS engineering-workspace readiness | No | Added by Codex — covers checkout conditions, sparse profile, rollback |
| Deployment eligibility | `docs/OPERATING_MODEL.md` §Operational support classification, `docs/REPOSITORY_CONTROL_MODEL.md` §6-gate admission | No | Workspace ≠ deployment; deployment requires separate gate |
| Private artifacts / `_internal/` | `docs/GIT_WORKFLOW.md` §Principles, §Private `_internal/` rules, `docs/REPOSITORY_WORK_PROTOCOL.md` §VPS workspace artifact boundary | No | Triple-covered: git exclusion + artifact boundary + no-transfer rule |
| Credentials / secrets | `docs/GIT_WORKFLOW.md` §Secrets | No | Clear prohibition in existing authority |
| Generated evidence | `docs/HEALTH_CONTRACT.md` (health payloads), `docs/VPS_INVENTORY.md` (topology), `repos/*/CONTROL.md` (health state) | No | Evidence is producer output; workspace residency does not change this |
| Agent artifacts (task packets, reports) | `docs/REPOSITORY_WORK_PROTOCOL.md` §Artifact-only orchestration, `agents/orchestrator-task-packet-template.md` | No | Codex added the artifact-boundary and Mode 0 rules |
| Repository admission | `docs/REPOSITORY_CONTROL_MODEL.md` | No | 6-gate model covers full lifecycle from admission through operational activation |
| Per-repo what-goes-where boundary | `repos/<repo>/CONTROL.md` (vps_path, data_locations, hermes scope, codex_stops) | Partial — no explicit "allowed/excluded artifact paths" field | Add `artifact_paths` field pattern to CONTROL.md design (see §5) |

### Verdict

All residency-related concepts already have an owner in the existing authority model. **No new high-level document (RESIDENCY.md or equivalent) is needed.**

---

## 4. Residency Document Decision

**Decision: Do not create a new residency/boundary document.**

### Rationale

| Criterion | Assessment |
|---|---|
| Is the question durable? | Yes — "what goes on VPS / what stays out" is permanent |
| Can existing authority answer it? | Yes — distributed across GIT_WORKFLOW.md, REPOSITORY_WORK_PROTOCOL.md, CONTROL.md, REPOSITORY_CONTROL_MODEL.md |
| Is ownership clear? | Yes — Git boundaries in GIT_WORKFLOW.md, artifacts in REPOSITORY_WORK_PROTOCOL.md, per-repo in CONTROL.md |
| Does a new doc have a distinct purpose? | No — a RESIDENCY.md would duplicate concepts already owned by at least 3 existing documents |

### Where the answer lives today

After Codex Session 12, the question "what belongs on VPS / what stays out" is answerable from:

1. **`docs/GIT_WORKFLOW.md` §VPS engineering-workspace readiness** — answers: what kind of checkout is allowed, what must be excluded (_internal, secrets, private prompts, raw evidence, experiments)
2. **`docs/REPOSITORY_WORK_PROTOCOL.md` §VPS workspace artifact boundary** — answers: what Hermes may create (task packets, reports, logs, journal proposals in declared paths)
3. **`docs/REPOSITORY_WORK_PROTOCOL.md` §Artifact-only orchestration** — answers: what Hermes may NOT do (write code, schemas, production data, merge branches)
4. **`repos/*/CONTROL.md`** — per-repo answers: what's deployed, what data paths exist, what Hermes scope is, what the stop conditions are
5. **`docs/REPOSITORY_CONTROL_MODEL.md`** — answers: which lifecycle stages exist, what gates control admission
6. **`docs/OPERATING_MODEL.md`** — answers: workspace vs production distinction

### Recommended small addition

Rather than a new document, add an `artifact_paths` YAML field to the CONTROL.md schema pattern (in `docs/REPOSITORY_CONTROL_MODEL.md` or the CONTROL.md template). This would give each repository a machine-readable declaration of allowed Hermes artifact paths, closing the gap identified in REPOSITORY_WORK_PROTOCOL.md §VPS workspace artifact boundary.

---

## 5. CONTROL.md Integration Assessment

### Current CONTROL.md coverage of residency boundaries

The ivy-control-vps CONTROL.md created by Codex establishes the pattern:

```yaml
vps:
  runtime_location: "/home/scraper/apps/ivy-control-vps"
data_locations:
  source_only: true
hermes:
  scope: "read-only"
codex_stops:
  - "Do not transfer _internal, credentials, private evidence, or raw agent material"
```

This covers the residency boundary for the control plane itself. For other repos, the existing CONTROL.md fields already cover:
- `vps.runtime_location` — where it lives on VPS
- `data_locations` — what data paths exist
- `hermes.scope` — what Hermes may do
- `codex_stops` — what boundaries exist
- `lifecycle.state` — whether it's deployed or not

### Gap: No declared artifact paths

The REPOSITORY_WORK_PROTOCOL.md requires: "For a VPS-resident repository, its AGENTS.md or CONTROL.md must declare the publication-safe artifact paths Hermes may use." Currently no CONTROL.md has an `artifact_paths` field.

**Proposed addition to CONTROL.md schema** (in `repos/ivy-control-vps/CONTROL.md` as the pattern-setter):

```yaml
hermes:
  scope: "read-only"
  artifact_paths:
    - "agent/reports/"
    - "logs/"
```

This is a small, bounded addition. It does not require a new document. It fills the identified gap without violating documentation governance.

---

## 6. Agent Impact Assessment

### Reading paths

The agent reading paths defined in AGENTS.md and REPOSITORY_WORK_PROTOCOL.md §7 still apply. No update needed — the new documents (orchestrator template, ivy-control-vps CONTROL.md) are child documents referenced from existing authority.

### Task packet instructions

The `orchestrator-task-packet-template.md` is a complementary template, not a replacement for existing workflow authority. Agents already know to read AGENTS.md, CONTROL.md, and ROADMAP.md before working. The template's "Read First" section reinforces this.

### OpenCode expectations

No change. OpenCode agents receive bounded tasks with explicit scope — the residency model does not change how OpenCode operates. The workspace artifact boundary affects Hermes, not OpenCode.

### Hermes rules

Updated by Codex — Mode 0, delegation envelope, checkpoint rules, artifact paths. These are now in `agents/HERMES_AGENT_CONTRACT.md`, `agents/VPS_ORCHESTRATION.md`, and `docs/REPOSITORY_WORK_PROTOCOL.md`.

---

## 7. Proposed Documentation Changes

### Change 1: Add `artifact_paths` to ivy-control-vps CONTROL.md

This sets the pattern for all managed repos. Without it, the REPOSITORY_WORK_PROTOCOL.md declaration requirement is unmet for the control plane itself.

**File:** `repos/ivy-control-vps/CONTROL.md`
**Addition:** Add `artifact_paths` under `hermes:` YAML block.

### Change 2: Document `artifact_paths` field in REPOSITORY_CONTROL_MODEL.md

Add the field definition so future CONTROL.md creators know the pattern.

**File:** `docs/REPOSITORY_CONTROL_MODEL.md`
**Addition:** Brief field definition under the CONTROL.md schema section.

### No other changes needed.

These are the minimum changes to close the gap between the REPOSITORY_WORK_PROTOCOL.md requirement and the current CONTROL.md design.

---

## 8. Changes Made

| File | Change | Status |
|---|---|---|
| `repos/ivy-control-vps/CONTROL.md` | Add `hermes.artifact_paths` field | ✅ Applied |
| `docs/REPOSITORY_CONTROL_MODEL.md` | Document `artifact_paths` field in CONTROL.md schema | ⏸ Pending review |

### Change 1 detail: `repos/ivy-control-vps/CONTROL.md`

Added under the `hermes:` block:

```yaml
hermes:
  scope: "read-only"
  artifact_paths:
    - "agent/reports/"
    - "logs/"
```

This declares the publication-safe paths Hermes may use for task packets, reports, logs, and journal proposals — satisfying the REPOSITORY_WORK_PROTOCOL.md §VPS workspace artifact boundary requirement.

---

## 9. Success Criteria Evaluation

**Question:** After Session 12, can a new engineer or agent determine what belongs in GitHub/VPS and what must remain private without guessing?

**Answer: Yes.** The rules live in:

| If you want to know... | Read... |
|---|---|
| What goes in a VPS checkout | `docs/GIT_WORKFLOW.md` §VPS engineering-workspace readiness |
| What Hermes can create on VPS | `docs/REPOSITORY_WORK_PROTOCOL.md` §Artifact-only orchestration |
| What stays private (_internal, secrets, prompts) | `docs/GIT_WORKFLOW.md` §Private `_internal/` rules |
| What a specific repo has on VPS | `repos/<repo>/CONTROL.md` (vps.runtime_location, data_locations) |
| What Hermes can do in a specific repo | `repos/<repo>/CONTROL.md` (hermes.scope, hermes.artifact_paths) |
| Whether a repo is eligible for deployment | `docs/REPOSITORY_CONTROL_MODEL.md` (6-gate model) |
| Whether workspace == production | `docs/OPERATING_MODEL.md` (explicitly: no) |
