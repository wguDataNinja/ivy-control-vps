# Session 12 — Task 07: Documentation Architecture Review and Consolidation Assessment

**Date:** 2026-07-20
**Status:** COMPLETED — analysis only, no files modified

---

## 1. Executive Summary

The documentation system is **appropriately modular** with clear authority boundaries, but the **Hermes/agent cluster is fragmented** — 4 documents covering overlapping territory with blurry ownership lines. The repository governance and VPS clusters are well-separated.

**Two consolidation opportunities identified, both in the Hermes cluster.** No consolidation needed in repository governance or VPS documentation.

**The "what belongs where" question** is already answerable from existing documents — no new central authority needed.

---

## 2. Current Documentation Map

### Cluster 1: Repository Governance (4 docs, ~1525 lines)

| Document | Lines | Purpose | Authority level |
|---|---|---|---|
| `REPOSITORY_CONTROL_MODEL.md` | 583 | CONTROL.md schema, 6-gate admission, approved SHA, lifecycle | Canonical |
| `PORTFOLIO_CONVENTIONS.md` | 351 | Cross-repo technical standards (PostgreSQL, systemd, naming, deployment requirements) | Canonical |
| `REPOSITORY_WORK_PROTOCOL.md` | 255 | Task lifecycle, result reports, logs, journals, artifact-only orchestration | Canonical |
| `GIT_WORKFLOW.md` | 336 | Git mechanics, branching, commits, _internal boundary, VPS workspace readiness | Canonical |

### Cluster 2: Hermes / Agent Model (4 docs, ~790 lines)

| Document | Lines | Purpose | Authority level |
|---|---|---|---|
| `RESIDENT_AGENT_MODEL.md` | 197 | Architectural model for resident agents, RAI concept | Architecture reference |
| `HERMES_OPERATOR_GUIDE.md` | 190 | Bridge protocol, operator instructions, file-based communication | Operational guide |
| `agents/VPS_ORCHESTRATION.md` | 341 | VPS interaction modes, approval boundaries, deployment sequence | Contract |
| `agents/HERMES_AGENT_CONTRACT.md` | 184 | Hermes bounded-work discovery, permissions, checkpoint rules | Contract |

### Cluster 3: VPS Operations (3 docs, ~502 lines)

| Document | Lines | Purpose | Authority level |
|---|---|---|---|
| `VPS_ACCESS.md` | 86 | SSH/SCP procedures, key management | Operational guide |
| `VPS_ADMISSION_CHECKLIST.md` | 25 | Evidence checklist for repo admission | Supporting checklist |
| `VPS_INVENTORY.md` | 391 | Workload topology, systemd units, data paths | Deployment topology |

### Other notable documents

| Document | Lines | Purpose |
|---|---|---|
| `OPERATING_MODEL.md` | 182 | Portfolio purpose, agent ownership, public/private boundary |
| `HEALTH_CONTRACT.md` | 776 | Health signal architecture, 46-field schema |
| `PORTFOLIO_INTENT.md` | 121 | Buddy's priorities (new, untracked) |
| `PORTFOLIO_UNIVERSE.md` | 61 | Asset classification |
| `AGENTS.md` | 158 | Agent operating instructions (root) |
| `agents/LOCAL_IMPLEMENTATION.md` | 166 | Local agent contract, reading order |
| `orchestrator-task-packet-template.md` | 78 | Mode 0 task template |

---

## 3. Authority Hierarchy

```
OPERATING_MODEL.md            ← why the control plane exists
  ├── PORTFOLIO_INTENT.md     ← what Buddy cares about
  ├── ROADMAP.md              ← where we're investing
  ├── REPOSITORY_CONTROL_MODEL.md  ← how repos are governed
  ├── REPOSITORY_WORK_PROTOCOL.md  ← how work is done
  ├── GIT_WORKFLOW.md         ← how changes are tracked
  ├── PORTFOLIO_CONVENTIONS.md ← technical standards
  ├── HEALTH_CONTRACT.md      ← health evidence rules
  └── AGENTS.md               ← agent behavior
        ├── LOCAL_IMPLEMENTATION.md
        ├── VPS_ORCHESTRATION.md
        ├── HERMES_AGENT_CONTRACT.md
        ├── RESIDENT_AGENT_MODEL.md
        └── HERMES_OPERATOR_GUIDE.md
```

Each layer answers a distinct question. The hierarchy is sound.

---

## 4. Duplication Analysis

### Repository Governance Cluster — LOW overlap

| Pair | Overlap | Assessment |
|---|---|---|
| CONTROL_MODEL vs CONVENTIONS | Both reference `VPS admission requirements` but CONTROL_MODEL describes the *gate framework* while CONVENTIONS describes *technical standards* that gates verify. | **Clear boundary** — keep separate |
| CONTROL_MODEL vs GIT_WORKFLOW | CONTROL_MODEL mentions approved SHA; GIT_WORKFLOW mentions exact-SHA deployment | **Minimal overlap** — SHA appears in both for different purposes (governance vs mechanics) |
| WORK_PROTOCOL vs CONVENTIONS | No significant overlap | Clean separation |
| WORK_PROTOCOL vs GIT_WORKFLOW | WORK_PROTOCOL defines artifact lifecycle; GIT_WORKFLOW defines Git mechanics | Clean separation |

**Verdict: No consolidation needed.** These 4 documents have clear ownership boundaries. Merging any pair would blur distinct concepts (lifecycle gates ≠ technical standards ≠ task workflow ≠ Git mechanics).

### Hermes / Agent Cluster — HIGH overlap

| Pair | Overlap | Assessment |
|---|---|---|
| RESIDENT_AGENT_MODEL vs HERMES_OPERATOR_GUIDE | Both describe what a resident agent is and how it communicates. RESIDENT_AGENT_MODEL defines the architecture; HERMES_OPERATOR_GUIDE defines the implementation. | **Significant overlap** — the architectural model could live as a section in the operator guide or in OPERATING_MODEL.md |
| VPS_ORCHESTRATION vs HERMES_AGENT_CONTRACT | Both define what Hermes can and cannot do. VPS_ORCHESTRATION defines interaction modes; HERMES_AGENT_CONTRACT defines task discovery and permissions. | **Moderate overlap** — both have "allowed/prohibited" rules for Hermes |
| RESIDENT_AGENT_MODEL vs VPS_ORCHESTRATION | RESIDENT_AGENT_MODEL is abstract architecture; VPS_ORCHESTRATION is concrete contract | Low overlap |
| HERMES_OPERATOR_GUIDE vs HERMES_AGENT_CONTRACT | Operator guide is for humans; agent contract is for Hermes itself | Low overlap |

**Verdict: Consolidation opportunity.** RESIDENT_AGENT_MODEL.md has the weakest justification as a standalone document. It was created as an architecture reference before Hermes existed; now that Hermes is real, the architecture document adds little beyond what the concrete documents contain.

### VPS Operations Cluster — MINIMAL overlap

| Pair | Overlap | Assessment |
|---|---|---|
| VPS_ACCESS vs VPS_INVENTORY | Access procedures vs workload topology | Clean separation |
| VPS_ACCESS vs ADMISSION_CHECKLIST | No overlap | — |
| VPS_INVENTORY vs ADMISSION_CHECKLIST | Both mention deployment but at different levels | Clean separation |

**Verdict: No consolidation needed.** These 3 docs serve distinct purposes.

---

## 5. Consolidation Recommendations

### Recommended: Merge RESIDENT_AGENT_MODEL.md into OPERATING_MODEL.md

**Current state:** RESIDENT_AGENT_MODEL.md (197 lines) defines the Resident Agent Interface (RAI) concept — an architectural abstraction for how agents communicate with the VPS. It was written when Hermes was still conceptual. Now that Hermes has concrete contracts (VPS_ORCHESTRATION.md, HERMES_AGENT_CONTRACT.md, HERMES_OPERATOR_GUIDE.md), the architectural document is redundant.

**Proposal:**
- Move the RAI concept (2-3 paragraphs) into `docs/OPERATING_MODEL.md` §Hermes and agents
- Retire `docs/RESIDENT_AGENT_MODEL.md` with a redirect note pointing to OPERATING_MODEL.md and HERMES_OPERATOR_GUIDE.md
- Update `docs/README.md` index to remove the entry

**Why this improves clarity:** Removes one of 4 Hermes documents without losing any content. The architectural concept belongs as context in the operating model, not as its own authority document.

### Not recommended: Merge VPS_ORCHESTRATION.md + HERMES_AGENT_CONTRACT.md

Despite moderate overlap, these serve different actors:
- VPS_ORCHESTRATION.md is for anyone interacting with the VPS (defines modes, boundaries)
- HERMES_AGENT_CONTRACT.md is specifically for Hermes the agent (defines its task discovery, permissions)

A human operator needs VPS_ORCHESTRATION.md but not HERMES_AGENT_CONTRACT.md. Merging them would force every reader to filter out irrelevant content.

### Not recommended: Merge PORTFOLIO_CONVENTIONS.md into REPOSITORY_CONTROL_MODEL.md

Despite the "VPS admission requirements" overlap, these address different questions: CONTROL_MODEL asks "what gates exist" and CONVENTIONS asks "what technical standards must be met at each gate." Merging them would create a 934-line document mixing framework with standards.

### Not recommended: Any VPS cluster consolidation

ACCESS, ADMISSION, and INVENTORY serve different readers with different purposes. Merging any pair would make each harder to find.

---

## 6. Migration Risks

| Risk | Consolidation | Likelihood | Mitigation |
|---|---|---|---|
| Lost architecture context | RESIDENT_AGENT_MODEL → OPERATING_MODEL | Low | Preserve key paragraphs, index redirect |
| Broken references | Any | Medium | Check docs/README.md + grep for cross-refs before merging |
| Hermes operator confusion | VPS_ORCHESTRATION + HERMES_AGENT_CONTRACT | Low | Not merging — risk avoided |
| Scope creep | Any | Medium | Task constraints already prevent merging in this session |

---

## 7. Reading Path Analysis

### New human maintainer (what they must read)

```
1. README.md (repo overview)
2. docs/README.md (documentation index + core reading path)
3. ROADMAP.md (current priorities)
4. docs/OPERATING_MODEL.md (why this exists)
5. docs/REPOSITORY_CONTROL_MODEL.md (how repos are governed)
6. The relevant repos/<repo>/CONTROL.md
```

The core reading path in `docs/README.md §Core reading path` already defines this correctly.

### OpenCode execution agent

```
1. AGENTS.md
2. agents/LOCAL_IMPLEMENTATION.md
3. docs/README.md → core reading path
4. docs/GIT_WORKFLOW.md
5. docs/REPOSITORY_WORK_PROTOCOL.md
6. Task-relevant CONTROL.md
```

Already defined in LOCAL_IMPLEMENTATION.md reading order. Correct.

### Strong Codex

```
Core path + docs/PORTFOLIO_CONVENTIONS.md + docs/HEALTH_CONTRACT.md
+ docs/DATA_LIFECYCLE_STANDARD.md + agents/VPS_ORCHESTRATION.md
```

Strong Codex needs the broadest reading path due to architecture, deployment, and database work. No change needed.

### Hermes

```
1. docs/README.md → core reading path
2. agents/HERMES_AGENT_CONTRACT.md
3. agents/VPS_ORCHESTRATION.md
4. docs/HERMES_OPERATOR_GUIDE.md
5. docs/REPOSITORY_WORK_PROTOCOL.md (artifact-only orchestration §)
6. Target repo CONTROL.md
```

**Problem:** Hermes needs to read 3 agent documents before it can work. After merging RESIDENT_AGENT_MODEL into OPERATING_MODEL.md, this reduces to 2.

---

## 8. Session 12 Impact — Residency Boundary Ownership

**Question:** Where should "every managed repository must explicitly declare what belongs in GitHub/VPS and what must remain private" live?

**Answer: CONTROL.md**, with field definitions in REPOSITORY_CONTROL_MODEL.md.

### Existing coverage already distributed

| Concept | Already owned by |
|---|---|
| What goes in VPS checkout | `docs/GIT_WORKFLOW.md` §VPS engineering-workspace readiness |
| What Hermes can create | `docs/REPOSITORY_WORK_PROTOCOL.md` §Artifact-only orchestration |
| What stays private | `docs/GIT_WORKFLOW.md` §Private _internal/ rules |
| Per-repo deployed paths | `repos/<repo>/CONTROL.md` (vps.runtime_location, data_locations) |
| Per-repo Hermes scope | `repos/<repo>/CONTROL.md` (hermes.scope, hermes.artifact_paths) |

### CONTROL.md addition (already done in Task 06)

The `artifact_paths` field was added to the CONTROL.md schema in `docs/REPOSITORY_CONTROL_MODEL.md` and to `repos/ivy-control-vps/CONTROL.md`. This closes the gap without creating a new document.

**No new document needed.** The distributed model is correct — different actors need different parts of the answer:

- **Git engineer** looks at GIT_WORKFLOW.md
- **Hermes operator** looks at REPOSITORY_WORK_PROTOCOL.md + CONTROL.md
- **Repo maintainer** looks at CONTROL.md
- **New engineer** looks at the core reading path

---

## 9. Proposed Future Documentation Structure

### Keep as-is

| Document | Reason |
|---|---|
| `OPERATING_MODEL.md` | Central operating authority — no overlap |
| `REPOSITORY_CONTROL_MODEL.md` | Gate framework — no overlap |
| `PORTFOLIO_CONVENTIONS.md` | Technical standards — no overlap |
| `REPOSITORY_WORK_PROTOCOL.md` | Task lifecycle — no overlap |
| `GIT_WORKFLOW.md` | Git mechanics — no overlap |
| `HEALTH_CONTRACT.md` | Health signals — no overlap |
| `PORTFOLIO_INTENT.md` | Buddy priorities — unique role |
| `PORTFOLIO_UNIVERSE.md` | Asset inventory — unique role |
| `VPS_INVENTORY.md` | Topology — no overlap |
| `VPS_ACCESS.md` | Access procedures — no overlap |
| `VPS_ADMISSION_CHECKLIST.md` | Admission checklist — unique role |
| `AGENTS.md` | Agent rules — unique role |
| `agents/LOCAL_IMPLEMENTATION.md` | Local agent contract — unique role |
| `agents/orchestrator-task-packet-template.md` | Task template — unique role (new) |
| `agents/HERMES_AGENT_CONTRACT.md` | Hermes permissions — needed by Hermes only |
| `agents/VPS_ORCHESTRATION.md` | VPS interaction modes — needed by operators |
| `docs/HERMES_OPERATOR_GUIDE.md` | Hermes bridge — needed by operators |

### Merge (1 doc)

| From | Into | Content |
|---|---|---|
| `docs/RESIDENT_AGENT_MODEL.md` | `docs/OPERATING_MODEL.md` | RAI architecture concept (2-3 paragraphs), then retire with redirect |

### Result after consolidation

21 tracked documents → 20 tracked documents. One architecture reference merged into its parent, eliminating the highest-overlap document without reducing discoverability.

---

## 10. Required Follow-up Tasks

| Task | Priority | Notes |
|---|---|---|
| Merge RESIDENT_AGENT_MODEL.md into OPERATING_MODEL.md | Low | Not urgent — the current state is functional. Only 197 lines of overlap. |
| Review `agents/LOCAL_IMPLEMENTATION.md` overlap with `AGENTS.md` | Low | Both define agent behavior. LOCAL_IMPLEMENTATION.md was created as a local supplement to AGENTS.md. Similar consolidation question exists. |
| No other consolidation needed | — | Repository governance, VPS operations, and health documentation are appropriately modular. |

---

## 11. Risks of NOT Consolidating

| Scenario | Impact |
|---|---|
| A new engineer reads all 4 Hermes documents before working | Overhead of ~790 lines to understand what Hermes can do, when ~500 lines would suffice |
| Two documents contradict each other on Hermes authority | Possible — VPS_ORCHESTRATION.md and HERMES_AGENT_CONTRACT.md both define boundaries. Currently aligned but not tested. |
| RESIDENT_AGENT_MODEL.md drifts from reality | Already possible — it's an architecture reference written before Hermes existed. The concrete contracts have since evolved. |

None of these are critical. The system is functional. Consolidation would improve but is not urgent.

---

## 12. Success Criteria Assessment

| Criterion | Result |
|---|---|
| Appropriately modular? | ✅ Mostly — 6 distinct clusters with clear boundaries |
| Overly fragmented? | ⚠️ Slightly in the Hermes/agent cluster (4 docs where 2-3 would suffice) |
| Missing a central authority? | ❌ No — the "what belongs where" question is answerable from 4 existing documents |
| Ready for consolidation? | ✅ One low-risk merge identified (RESIDENT_AGENT_MODEL → OPERATING_MODEL.md) |
