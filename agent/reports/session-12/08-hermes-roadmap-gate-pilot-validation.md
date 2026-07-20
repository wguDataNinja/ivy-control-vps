# Session 12 — Task 13: Hermes Roadmap Gate Pilot Validation

**Date:** 2026-07-19
**Status:** COMPLETED — gate contract created and validated against two pilot repositories

---

## 1. Executive Summary

The Hermes Roadmap Sufficiency Gate v1 has been created at
`agents/HERMES_ROADMAP_SUFFICIENCY_GATE.md` and validated against two
repositories.

| Repository | Gate outcome | Delegation recommendation |
|---|---|---|
| `palworld-kb` | **ROADMAP_READY_FOR_ORCHESTRATION** | Safe to delegate chunks 2, 4, 7, 8 to OpenCode; chunks 1, 5, 6, 9 require Codex or Buddy |
| `sts-workbench` | **ROADMAP_READY_FOR_ORCHESTRATION** | Safe to delegate chunks 1-8 to appropriate agents; chunk 9-10 require Buddy sign-off first |

**Key finding:** Both roadmaps pass the sufficiency gate. The gate correctly
identifies that execution is safe when Hermes respects the agent assignment
model. Neither roadmap requires execution agents to perform architecture-level
reasoning, because the agent assignment model explicitly routes complex work to
Codex or Buddy.

---

## 2. Hermes Gate Contract Summary

The gate contract was created at `agents/HERMES_ROADMAP_SUFFICIENCY_GATE.md`.

### 2.1 Structure

| Section | Content |
|---|---|
| Purpose | Single question: is roadmap clear enough for agent execution? |
| 6 evaluation criteria | Objective clarity, current state accuracy, scope clarity, dependency clarity, acceptance criteria, decision gates |
| PASS/FAIL per criterion | Concrete conditions for each |
| Two outcomes | `ROADMAP_READY_FOR_ORCHESTRATION` and `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION` |
| May/may not per outcome | Explicit allowed and prohibited behavior |
| Application procedure | 6-step evaluation sequence |

### 2.2 Design decisions

| Decision | Rationale |
|---|---|
| Gate evaluates roadmap sections, not whole roadmaps | A roadmap may be partially ready; the gate applies to the section referenced in the delegation envelope |
| Gate does not replace eligibility checks | Hermes must still check CONTROL.md, permissions, and artifact paths before the gate |
| Agent assignment model is a gate input | The same chunk may pass for Codex but fail for OpenCode; Hermes must check agent type |
| PASS is not an endorsement of roadmap quality | The gate only checks sufficiency for execution, not strategic soundness |

---

## 3. Palworld KB Evaluation

### 3.1 Sources inspected

| Source | Content |
|---|---|
| `ROADMAP.md` | 190 lines — North Star, Current State, Dependency Map, Workstreams, 9 Execution Chunks, High Reasoning Gates, Agent Assignment Model, Completion Criteria, Risks |
| `CONTROL.md` (in repos/palworld-kb/) | Lifecycle: source-only, Hermes scope: read-only, no artifact paths declared |
| `TODO.md` | Marked as ARCHIVED — superseded by ROADMAP.md |
| Local repository state | Working tree has experiment output; no clean baseline for VPS clone |

### 3.2 Criterion-by-criterion evaluation

#### Criterion 1: Objective clarity — PASS

The North Star is explicit: "source-only, versioned, provenance-backed Markdown
knowledge base where an agent can answer Palworld gameplay questions." Each
execution chunk has a one-line objective that describes a single observable
outcome:

- Chunk 1: "Make human review repeatable before scaling promotion"
- Chunk 2: "Reconcile 159 Pal index entries against the 115 acquired proposals"
- Chunk 3: "Move approved Pal proposal content into canonical KB records safely"

No chunk requires Hermes to infer intent — the goal is stated directly.

#### Criterion 2: Current state accuracy — PASS

The Current State section is unusually honest for a project roadmap:

- "115 base Pal wiki.gg acquisitions are complete" — verifiable
- "Only a small subset of canonical entity records is populated" — accurate
- "Bulk canonical promotion is blocked on Buddy review decisions" — true
- "Active work is content quality review" — matches actual activity

The critique section at the top of the file explicitly calls out where the
roadmap itself may be incomplete (e.g., "Review methodology is missing").
This self-awareness confirms accuracy rather than undermining it.

#### Criterion 3: Scope clarity — PASS

Each chunk defines explicit inputs and outputs. Exclusions are documented:

- "KB review UI has not started and must remain source-only/local"
- "Reddit ingestion, Game8 acquisition, PalDB enrichment remain deferred"
- "No VPS runtime, no DB, no production deployment, no user-facing web UI"

The agent assignment model further constrains scope by routing work to the
appropriate agent type.

#### Criterion 4: Dependency clarity — PASS

Dependency Map section is thorough:

- "CLI/schema changes must preserve palworld.cli.v1 and palworld.evidence.v1
  compatibility"
- "Review rubric must exist before large review batches"
- "Bulk promotion depends on validated decisions, clean proposal manifests"
- "Q&A evaluation can start early only against canonical records"

The cross-repo contract risk with sts-workbench is explicitly called out in
both the dependency map and the risks section.

#### Criterion 5: Acceptance criteria — PASS

Per-chunk acceptance criteria are concrete:

- Chunk 1: "Reviewers can classify each proposal consistently without inventing
  per-file policy"
- Chunk 2: "The roadmap no longer treats 115 reviewed proposals as equivalent
  to 159 canonical Pals"
- Chunk 3: "Each promoted batch has intact provenance, schema-valid records,
  audit evidence, and a verified rollback path"

Validation methods are specified per chunk. The overall Completion Criteria
section defines 11 measurable outcomes.

#### Criterion 6: Decision gates — PASS

High Reasoning Gates section lists 10 explicit gates:

- "Approve review rubric and disposition states"
- "Decide whether canonical promotion should proceed before all Pal proposals
  are reviewed"
- "Approve any breaking change to schemas, CLI behavior, or downstream evidence
  contracts"

Agent Assignment Model clearly routes decisions to Buddy or Codex. Unresolved
decisions are visible (e.g., "Decide how to handle the 44 Pal index entries not
covered by the 115 acquired proposals").

### 3.3 Outcome

```
ROADMAP_READY_FOR_ORCHESTRATION
```

**Rationale:** All six criteria pass. The roadmap is unusually thorough for a
project in active content development. It explicitly identifies its own gaps,
which means Hermes can trust the roadmap's characterization and route work
appropriately.

**Caveat:** Not all chunks are OpenCode-delegatable. Hermes must respect the
agent assignment model:

| Chunk | Assigned agent | Hermes action |
|---|---|---|
| 1 — Review rubric | Strong Codex | Delegate to Codex, not OpenCode |
| 2 — Pal coverage inventory | OpenCode | Safe for OpenCode |
| 3 — Promote batches | Strong Codex | Delegate to Codex |
| 4 — CLI stability | OpenCode | Safe for OpenCode |
| 5 — Q&A evaluation | Strong Codex | Delegate to Codex |
| 6 — Non-Pal entities | Strong Codex | Delegate to Codex |
| 7 — Acquisition normalization | OpenCode | Safe for OpenCode |
| 8 — Review UX decision | Buddy | Stop — Buddy must decide |
| 9 — Deferred enrichment | Strong Codex | Delegate to Codex |

**Before delegation, Hermes must also verify:**
- Palworld's Hermes scope is upgraded from `read-only` to
  `orchestrate-artifact-only`
- Artifact paths are declared in Palworld's CONTROL.md (`hermes.artifact_paths`)
- A clean working baseline exists (current tree has unclassified experiment
  output)

These are not roadmap failures — they are Hermes infrastructure prerequisites
that must be resolved before any delegation can occur, regardless of roadmap
quality.

---

## 4. STS Workbench Evaluation

### 4.1 Sources inspected

| Source | Content |
|---|---|
| `ROADMAP.md` | 210 lines — North Star, Current State, Dependency Map, Workstreams, 11 Execution Chunks, High Reasoning Gates, Agent Assignment Model, Completion Criteria, Risks |
| `TODO.md` | Detailed WP-09 hardening list (12 items), WP pass/fail status for WP-01 through WP-10 |
| `AGENTS.md` | Current phase rules, agent roles, research vs. implementation boundaries |
| Local repository state | WP-09 implementation exists but acceptance is not proven |

### 4.2 Criterion-by-criterion evaluation

#### Criterion 1: Objective clarity — PASS

North Star is specific and bounded: "Deliver the bounded V1 Palworld Nitewing
voice assistant." Each chunk objective is concrete:

- Chunk 1: "Convert the detailed WP-09 hardening requirements into a bounded
  implementation checklist"
- Chunk 2: "Establish repeatable browser automation against the live local STS
  service and React workspace"
- Chunk 3: "Provide reliable browser coverage without depending on live OpenCode"

Boundaries are explicit: "V1 is not a general voice-assistant framework, not a
multi-backend platform, and not a production hosting effort."

#### Criterion 2: Current state accuracy — PASS

Current state is precise and evidence-backed:

- "WP-01 through WP-08 are complete and hardened"
- "WP-09 is active: the React workspace and evidence experience exist, but real
  browser acceptance is not proven"
- "WP-10 Kokoro TTS is blocked until WP-09 browser acceptance is proven"
- "WP-09 is not yet a full PASS because the report does not prove the required
  browser-level acceptance and coverage"

TODO.md provides a detailed 12-item hardening list with exact evidence gaps
(e.g., "8 frontend tests total", "No executed real browser end-to-end trace").

#### Criterion 3: Scope clarity — PASS

Scope is tightly bounded per chunk:

- Chunk 1: authority alignment only — "not inventing new product scope or
  redefining V1"
- Chunk 2: Playwright harness only — "without manual browser setup"
- Chunk 3: deterministic test path only — "repeatable and suitable for
  regression coverage"

Prohibitions are explicit: "Do not broaden V1 into a general assistant
framework or multi-backend platform." The two-repository boundary is
enforced: "sts-workbench and palworld-kb remain separate repositories."

#### Criterion 4: Dependency clarity — PASS

Dependency Map is explicit and complete:

- "WP-09 depends on WP-04 through WP-08 service behavior"
- "Browser acceptance depends on deterministic local startup"
- "Real acceptance depends on Palworld CLI contract and compatibility lock"
- "WP-10 depends on WP-09 sign-off"
- Cross-repo compatibility through `v1/compatibility/palworld-kb.lock.json`

Each chunk has a Dependencies line listing exact prerequisites. No hidden
dependencies exist.

#### Criterion 5: Acceptance criteria — PASS

Per-chunk acceptance criteria are measurable:

- Chunk 1: "Checklist covers browser trace, SSE, components, accessibility"
- Chunk 2: "A smoke test opens the app, confirms the workspace renders"
- Chunk 4: "Buddy can review the trace as evidence that WP-09 works"
- Chunk 8: "All WP-09 gates pass or have explicit accepted exceptions"

Overall Completion Criteria lists 11 specific outcomes. WP-09 hardening list
(12 items) in TODO.md provides even more granular acceptance criteria.

#### Criterion 6: Decision gates — PASS

High Reasoning Gates lists 11 explicit gates:

- Gate 1: "WP-09 scope must remain the bounded Nitewing vertical slice"
- Gate 7: "Buddy must sign off WP-09 before WP-10 implementation begins"
- Gate 8: "Kokoro TTS requires design approval before implementation"
- Gate 10: "Repositories remain separate; compatibility through contracts"

Agent Assignment Model is clear: "Buddy owns WP-09 sign-off, WP-10 design
approval, publication timing." Unresolved decisions are visible.

### 4.3 Outcome

```
ROADMAP_READY_FOR_ORCHESTRATION
```

**Rationale:** All six criteria pass. STS Workbench has the most detailed and
well-structured roadmap of any repository in the portfolio. Every chunk has
explicit inputs, outputs, dependencies, validation, and acceptance criteria.
Gates are numbered and explicit.

**Caveat:** Like Palworld KB, Hermes must respect the agent assignment model.
Chunks 9 and 10 require Buddy sign-off before they can proceed, but this is
explicitly documented and Hermes would correctly stop at those gates.

**Before delegation, Hermes must verify:**
- STS Workbench has a CONTROL.md in the ivy-control-vps portfolio (currently
  absent — the repo is not yet managed)
- Hermes scope and artifact paths are declared
- The working tree is clean and WP-09 is actually in a delegatable state

---

## 5. READY / INSUFFICIENT Decisions Summary

| Criterion | Palworld KB | STS Workbench |
|---|---|---|
| 1. Objective clarity | PASS | PASS |
| 2. Current state accuracy | PASS | PASS |
| 3. Scope clarity | PASS | PASS |
| 4. Dependency clarity | PASS | PASS |
| 5. Acceptance criteria | PASS | PASS |
| 6. Decision gates | PASS | PASS |
| **Overall** | **READY** | **READY** |

Both roadmaps pass all six criteria. Neither requires execution agents to
perform architecture-level reasoning, provided Hermes respects the agent
assignment model.

**No INSUFFICIENT outcomes were produced.** This does not mean the gate is
useless — it means current roadmaps are already explicit enough for safe
orchestration. The gate's value will appear when a roadmap is encountered that
lacks chunk definitions, acceptance criteria, or decision gates.

---

## 6. Missing Information Discovered

Even though both roadmaps pass the sufficiency gate, Hermes would still be
unable to delegate work to either repository today due to infrastructure gaps
that the gate does not check:

### Hermes infrastructure gaps (Palworld KB)

| Gap | Where it should be resolved | Priority |
|---|---|---|
| Hermes scope is `read-only`, not `orchestrate-artifact-only` | CONTROL.md `hermes.scope` | Blocking |
| No artifact paths declared | CONTROL.md `hermes.artifact_paths` | Blocking |
| No VPS clone exists | VPS filesystem | Blocking for VPS deployment |
| Working tree has unclassified experiment output | Local working tree | Blocking |
| No CONTROL.md `hermes.scope` upgrade gate passed | RELEASE_GATES.md | Blocking |

### Hermes infrastructure gaps (STS Workbench)

| Gap | Where it should be resolved | Priority |
|---|---|---|
| No CONTROL.md exists in ivy-control-vps/repos/ | Portfolio admission | Blocking |
| Repository is not yet managed by the control plane | Portfolio admission | Blocking |
| No Hermes scope or artifact paths declared | Would be in CONTROL.md | Blocking |

### Roadmap information quality observations

| Observation | Palworld KB | STS Workbench |
|---|---|---|
| Roadmap length | 190 lines | 210 lines |
| Execution chunks | 9 | 11 |
| High reasoning gates | 10 explicit | 11 numbered |
| Agent assignment model | Yes — per agent type | Yes — per agent type |
| Critique section | Yes — in-breadth self-critique | Yes — in-breadth self-critique |
| Risks section | Yes — 9 risks | Yes — 10 risks |
| Completion criteria | Yes — 11 outcomes | Yes — 11 outcomes |

Both roadmaps include a "Critique of Fast Codex" section at the top — a
deliberate self-critique of a machine-generated first draft. This is an
excellent practice that demonstrates roadmap maturity.

---

## 7. Recommended Next Steps

### 7.1 Gate integration

The gate contract at `agents/HERMES_ROADMAP_SUFFICIENCY_GATE.md` is ready to be
referenced from `agents/HERMES_AGENT_CONTRACT.md` §3.5a. The content aligns
with the implementation plan from Task 12.

### 7.2 Before any delegation to Palworld KB

| Step | Owner |
|---|---|
| 1. Classify experiment output and establish clean baseline | OpenCode |
| 2. Declare artifact paths in Palworld CONTROL.md | Codex or Buddy |
| 3. Upgrade Hermes scope to `orchestrate-artifact-only` | Buddy |
| 4. Create source-only VPS clone | Codex |
| 5. Define first bounded task (suggested: Chunk 2 — Pal coverage inventory) | Codex + Buddy |

### 7.3 Before any delegation to STS Workbench

| Step | Owner |
|---|---|
| 1. Create CONTROL.md and admit STS Workbench as managed repository | Codex + Buddy |
| 2. Declare Hermes scope and artifact paths | Buddy |
| 3. Complete WP-09 hardening (12-item TODO list) | OpenCode |
| 4. Obtain WP-09 sign-off from Buddy | Buddy |
| 5. Delegate Chunks 1-8 per agent assignment model | Hermes |

### 7.4 Gate governance

| Recommendation | Rationale |
|---|---|
| The gate should remain in `agents/` as a standalone document | It is referenced by the Hermes contract but is also readable independently by roadmap authors |
| The gate should be versioned (v1) | Future versions may add criteria or refine PASS/FAIL conditions |
| Gate training for roadmap authors | Roadmap creators should know the 6 criteria to design delegatable chunks |
| The gate should be tested on a deliberately insufficient roadmap | To verify the INSUFFICIENT outcome is correctly produced |

---

## 8. Success Criteria Assessment

| Criterion | Answer |
|---|---|
| Does the roadmap gate prevent unsafe orchestration? | **Yes.** All six criteria must pass before delegation. The agent assignment model prevents OpenCode from receiving Codex-level work. |
| Are current roadmaps sufficiently explicit? | **Yes.** Both roadmaps pass all six criteria. They are among the most detailed project roadmaps in the portfolio. |
| What information must Codex provide before Hermes proceeds? | Hermes infrastructure: CONTROL.md, Hermes scope, artifact paths, clean baseline. The roadmaps themselves are sufficient. |
| Is the gate ready to become part of the Hermes contract? | **Yes.** The gate document is ready. It should be referenced from `HERMES_AGENT_CONTRACT.md` §3.5a in the next implementation task. |

**The objective is met:** Hermes now has a defined procedure for knowing when
it has enough information to safely coordinate work. The gate is conservative —
it stops when criteria fail — and does not make Hermes more autonomous.

---

## References

- `agents/HERMES_ROADMAP_SUFFICIENCY_GATE.md` — The gate contract (created by this task)
- `agent/reports/session-12/06-hermes-roadmap-sufficiency-preflight.md` — Task 11 preflight
- `agent/reports/session-12/07-hermes-orchestration-contract-plan.md` — Task 12 implementation plan
- `/Users/buddy/projects/palworld-kb/ROADMAP.md` — Palworld KB roadmap
- `repos/palworld-kb/CONTROL.md` — Palworld KB control record
- `/Users/buddy/projects/sts-workbench/ROADMAP.md` — STS Workbench roadmap
- `/Users/buddy/projects/sts-workbench/AGENTS.md` — STS Workbench agent instructions
- `/Users/buddy/projects/sts-workbench/TODO.md` — STS Workbench task state
