# Session 12 — Task 14: Codex Handoff Skill Historical Reconciliation and Contract Design

**Date:** 2026-07-19
**Status:** COMPLETED — architecture reconciliation and contract design, no files modified

---

## 1. Executive Summary

The `codex-handoff` skill exists at
`/Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/SKILL.md` in
the predecessor repository. It is an **OpenCode-local skill**, not a Hermes
capability. It was created in June 2026 (pre-Session 1) to enable OpenCode to
compose and send a one-shot prompt to Codex and capture the output.

**Five findings:**

1. **Why it exists:** OpenCode needed a bounded, governed way to invoke Codex
   for architecture-level work. The skill is the gate — it prevents ad-hoc
   `codex exec "do something smart"` calls.

2. **It was intentionally OpenCode-local.** The original design decision was
   that Hermes would *detect* the need for Codex (missing roadmap, stale
   roadmap) but would not invoke Codex directly. Hermes would signal, and
   OpenCode (or the skill) would execute.

3. **The skill is currently orphaned.** It lives in the old `ivy-control`
   repository, not in `ivy-control-vps`. Session 10 planned a more sophisticated
   `codex-roadmap` skill that was never implemented. The original skill is
   functional but disconnected from the current architecture.

4. **The roadmap sufficiency gate creates the natural trigger.** When Hermes
   produces `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION`, the next logical step is
   a Codex clarification request. The architecture supports this — the contract
   just needs to be documented.

5. **Recommended contract location:** `agents/HERMES_AGENT_CONTRACT.md` — a
   new section describing the escalation path, not the invocation mechanics.
   The skill mechanics remain in the skill file.

---

## 2. Historical Findings

### 2.1 Artifacts recovered

| Source | Date | Session | Content |
|---|---|---|---|
| `ivy-control/.opencode/skills/codex-handoff/SKILL.md` | 2026-06-23 | Pre-1 | The skill file — 99 lines, defines input/output paths, command shape, preflight checks, completion report |
| `ivy-control/.opencode/skills/codex-handoff/test-prompt.md` | 2026-06-23 | Pre-1 | Example test prompt (dark mode toggle roadmap) |
| `_internal/outbox/session-3/agent-3-code-review.md` | 2026-07-XX | 3 | References Codex handoff as "implementation authority" for health producer |
| `_internal/outbox/session-6/...` | 2026-07-XX | 6 | References "Strong Codex Handoff" as privileged execution packet pattern |
| `_internal/outbox/session-10/119-codex-handoff-plan.md` | 2026-07-18 | 10 | Full implementation plan for `codex-roadmap` skill — 4-phase workflow, skill-owned prompt, approval gate, reconciliation requirement. Never implemented. |
| `_internal/outbox/session-10/120-roadmap-handoff-prompt-audit.md` | 2026-07-18 | 10 | Prompt format audit, Codex output specification, governance refinement. Produced draft prompt, defined Option B lifecycle (proposal → reconciliation → approval → authority). |
| `_internal/logs/sessions/GPT-1-bootstrap-gpt-workflow.md` | 2026-07-XX | 1 | Rejects "over-prescriptive Codex handoffs that define every command" |
| `_internal/logs/sessions/session-10/TASK_JOURNAL.md` | 2026-07-18 | 10 | Records Task 119 completion and deferral |

### 2.2 Intent timeline

| Date | Event | Design decision |
|---|---|---|
| 2026-06-23 | Pre-1 | `codex-handoff` skill created in `ivy-control/.opencode/skills/` |
| — | Pre-1 | Purpose: bounded Codex invocation from OpenCode. Not a Hermes capability. |
| 2026-07-07 | Pre-1 | Deletion incident; `_internal/` created. Skill survives in separate repo. |
| 2026-07-XX | Session 1 | "Rejected: over-prescriptive Codex handoffs that define every command" — concern about rigid prompts |
| 2026-07-XX | Session 3 | Codex handoff used as "implementation authority" for health producer — pattern: OpenCode uses skill to get Codex output, reconciles, produces final artifact |
| 2026-07-XX | Session 6 | "Strong Codex Handoff" pattern for privileged execution packets — two-axis model begins to form |
| 2026-07-18 | Session 10 T119 | Full `codex-roadmap` skill plan produced: skill-owned prompt, approval gates, reconciliation requirement, Hermes pipeline vision |
| 2026-07-18 | Session 10 T120 | Prompt format and governance audit. Output specification drafted. Implementation deferred. |
| 2026-07-19 | Session 12 T14 | This analysis |

### 2.3 Why it was created

The skill was created to solve a specific governance problem: **OpenCode should
not invoke Codex ad-hoc.** Without the skill, an agent could run:

```
codex exec "design an architecture for X"
```

...and use the output without review. The skill enforces:

- A composed input file with explicit output path
- Preflight checks before invocation
- A specific command shape (no fallback models, no output capture tricks)
- A completion report that confirms the output exists and is reviewable

### 2.4 Why it was disabled or limited

The skill was **not disabled** — it was **orphaned by the repository split.**
When Ivy Control was restructured into `ivy-control-vps` (the new control-plane
repo), the `.opencode/skills/codex-handoff/` directory remained in the old
`ivy-control` repository. Session 10's planned `codex-roadmap` skill would have
replaced it in the new repo, but was never implemented.

### 2.5 Previous intended use cases

| Use case | Source | Status |
|---|---|---|
| Roadmap generation for repos without a ROADMAP.md | Session 10 T119 | Planned, not implemented |
| Architecture clarification for complex design decisions | Session 3, Session 6 | Used informally |
| Privileged execution packet preparation | Session 6 | Used informally |
| Cross-repo contract decisions | Session 10 T120 | Identified but not scoped |

### 2.6 Unresolved concerns from prior discussions

| Concern | Source | Current relevance |
|---|---|---|
| "Over-prescriptive Codex handoffs that define every command" | GPT-1 journal | Still relevant — the skill should define the contract, not every CLI flag |
| Codex output must never bypass reconciliation | Session 10 T119 appendix | Still relevant — Codex output → reconciliation → approval → authority |
| Palworld KB too simple for first Codex call | Session 10 T120 | Still relevant — first Codex call should target a repo with real architecture complexity |
| Hermes detection should remain read-only | Session 10 T119 appendix | Core design constraint — Hermes detects, does not invoke |
| Agent-internal skill vs. Hermes capability boundary unclear | Implicit across sessions | Needs resolution — this report |

---

## 3. Current Capability Assessment

### 3.1 Where the skill lives today

```
Old location (functional but orphaned):
  /Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/
    SKILL.md           — 99 lines: contract, input format, command shape, completion report
    test-prompt.md     — 39 lines: example dark-mode toggle prompt

New location (planned but not implemented):
  /Users/buddy/projects/ivy-control-vps/
    skills/            — does not exist
    .opencode/skills/  — does not exist
```

### 3.2 What the skill does

```
Input: composed prompt file with handoff header + output path
  ↓
Preflight: file exists? header correct? path correct? prompt appropriate?
  ↓
Codex exec: one-shot, specific model, skip-git-repo-check
  ↓
Output: Codex writes to specified output file
  ↓
Completion report: command, exit code, output path, file exists check
```

### 3.3 What it does NOT do

- It does NOT perform roadmap sufficiency validation
- It does NOT maintain orchestration state
- It does NOT track whether the output was reconciled or approved
- It does NOT enforce the reconciliation step (that's the caller's responsibility)
- It does NOT interface with Hermes or any orchestration layer
- It does NOT have a configurable model mapping (model is hardcoded: `gpt-5.5`)

### 3.4 Current architecture gaps

| Gap | Impact | Resolution |
|---|---|---|
| Skill is in old repo, not `ivy-control-vps` | Cannot be used in current workflow | Migrate to `ivy-control-vps/.opencode/skills/codex-handoff/` or create `skills/codex-roadmap/` |
| No Hermes integration point | Hermes cannot trigger Codex clarification | Define escalation path in Hermes contract |
| No reconciliation requirement in skill | Codex output could be used directly | Add to skill contract or caller workflow |
| Model is hardcoded | Cannot switch between fast/strong models | Use config file per Session 10 plan |
| No approval gate in current skill | OpenCode can invoke Codex without human approval | Add to future skill version |

---

## 4. Hermes/Codex Relationship Model

### 4.1 Current relationship

```
Current model (post-Task 13):

Hermes
  → reads roadmap
  → applies sufficiency gate
  → if INSUFFICIENT: stops, reports
  → report goes to Buddy (not Codex)

OpenCode (via codex-handoff skill)
  → can invoke Codex for architecture work
  → reconciles output
  → produces proposal
```

### 4.2 Proposed future relationship

```
Future model:

Hermes
  → reads roadmap
  → applies sufficiency gate
  → if INSUFFICIENT:
      1. stops
      2. produces ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION report
      3. identifies what Codex should clarify
      4. ESCALATES TO BUDDY:
         "This roadmap is insufficient for orchestration.
          Recommended: dispatch Codex to clarify [specific gaps]."

Buddy
  → reviews insufficiency report
  → decides: dispatch Codex, override, or defer

If Buddy dispatches Codex:
  → Buddy or OpenCode invokes codex-handoff skill
  → Codex produces clarification
  → OpenCode reconciles
  → roadmap updated
  → Hermes re-evaluates (new delegation)
```

### 4.3 Hermes does NOT invoke Codex directly

This is a critical design constraint. Hermes should never:

- Run `codex exec` directly
- Compose a Codex prompt
- Receive Codex output directly
- Decide whether Codex output is correct

**Why:** Hermes is an orchestrator, not an architect. Codex invocation requires:

1. Context gathering (reading repos, understanding current state) — OpenCode's job
2. Prompt composition (crafting the right question) — requires understanding the architecture gap
3. Approval (the call costs money) — Buddy's decision
4. Reconciliation (reviewing, fixing, approving) — OpenCode + Buddy

Hermes does none of these. Hermes's role is to **detect and signal** — to
recognize when the roadmap is insufficient and identify what clarification is
needed.

### 4.4 The two capabilities are related but distinct

| Dimension | Current codex-handoff skill | Future Hermes escalation |
|---|---|---|
| Who invokes | OpenCode | OpenCode or Buddy on Hermes's recommendation |
| When | On request or detected need | When Hermes produces INSUFFICIENT |
| What it produces | Architecture output, roadmap proposal | Clarification of specific gaps |
| Who reconciles | OpenCode | OpenCode |
| Who approves | Buddy | Buddy |
| Trigger | Human or agent discretion | Hermes sufficiency gate failure |

**They should share the same contract** (input/output format, boundary rules)
but serve different triggers.

---

## 5. Proposed Contract

### 5.1 Contract name

**Codex Clarification Contract** — not "Codex Handoff Contract" or "Codex
Invocation Contract". The term "handoff" implies fire-and-forget. The term
"clarification" correctly describes the purpose: resolving ambiguity that
prevents safe orchestration.

### 5.2 Inputs (what Codex receives)

| Field | Required | Description |
|---|---|---|
| Objective | Yes | What decision or clarification is needed. Single question, not a brief. |
| Current state | Yes | Verified facts from the repository. What exists, what is known, what is uncertain. |
| Roadmap section | Conditionally | The specific roadmap section that failed the sufficiency gate. Include the insufficiency report. |
| Constraints | Yes | What Codex must not assume, change, or recommend. Budget, scope, legal, architectural limits. |
| Specific questions | Yes | The exact questions Codex must answer. Not "design an architecture" but "should we use X or Y for Z?" |
| Output format | Yes | What the output should look like. Structured sections, not free-form prose. |

### 5.3 Outputs (what Codex returns)

| Field | Required | Description |
|---|---|---|
| Clarification | Yes | Direct answer to the specific questions asked |
| Options considered | Recommended | Alternatives evaluated and why each was accepted or rejected |
| Risks | Recommended | Risks introduced by the recommended approach |
| Assumptions made | Yes | What Codex assumed that must be verified by the reconciler |
| Missing information | Yes | What Codex wishes it had |
| Recommended next steps | Recommended | What to do with this clarification |

### 5.4 Boundaries

Codex may:

- Make architecture recommendations
- Resolve design questions
- Create or refine roadmap sections
- Evaluate options and tradeoffs
- Identify risks and missing information
- Produce implementation guidance for Codex-suitable chunks

Codex may not:

- Silently expand scope beyond the specific questions
- Make human business decisions (budget, priority, personnel)
- Bypass approval gates
- Write directly to ROADMAP.md or any canonical document
- Recommend anything requiring credentials, secrets, or paid services beyond the accepted OpenCode cost model
- Claim work is complete without evidence

### 5.5 Contract lifecycle

```
1. TRIGGER: Hermes produces ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION
   (or Buddy/OpenCode identifies a need for Codex clarification)

2. PREPARE: OpenCode gathers context, composes input packet
   - Reads the insufficiency report
   - Reads relevant repository state
   - Formulates specific questions
   - Defines output format

3. APPROVE: Buddy reviews and approves the Codex call
   - Target repo and specific questions
   - Model selection (fast/strong)
   - Cost implication
   - Explicit non-goals

4. EXECUTE: codex-handoff skill invokes Codex
   - Uses the approved input packet
   - Captures output to declared path

5. RECONCILE: OpenCode reviews Codex output
   - Fix hallucinated paths
   - Correct inaccurate claims
   - Flag assumptions that need verification
   - Produce reconciled proposal

6. APPROVE OUTPUT: Buddy reviews reconciled proposal
   - Accept, reject, or request revision

7. INTEGRATE: If accepted, update roadmap section
   - git-steward commits changes
   - Update CONTROL.md if needed

8. RE-EVALUATE: Hermes re-applies sufficiency gate (if triggered by INSUFFICIENT)
   - New delegation may proceed
```

### 5.6 Interaction with roadmap sufficiency gate

The gate and the contract form a closed loop:

```
Hermes reads roadmap
  ↓
Gate evaluation
  ↓
[PASS] → proceed with orchestration
  ↓
[FAIL] → ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION
  ↓
         Buddy reviews insufficiency report
           ↓
         [DISPATCH CODEX] → Codex clarification contract
                               ↓
                             Codex produces clarification
                               ↓
                             OpenCode reconciles
                               ↓
                             Buddy approves
                               ↓
                             Roadmap section updated
                               ↓
                             Hermes re-evaluates (gate applied again)
                               ↓
                             [PASS] or [FAIL] → loop continues
```

This is appropriate and safe because:
- Hermes never invokes Codex (OpenCode + Buddy do)
- Every Codex output goes through reconciliation and approval
- The gate is re-applied after the roadmap is updated
- The loop cannot spin without Buddy's explicit decisions

---

## 6. Documentation Ownership Recommendation

### 6.1 Where the contract should live

| Document | Content | Decision |
|---|---|---|
| `agents/HERMES_AGENT_CONTRACT.md` | **The escalation path from Hermes to Codex.** A new section after §3.5b describing: when Hermes escalates, what the insufficiency report should contain to enable Codex dispatch, and the rule that Hermes does not invoke Codex directly. | **Required** — this is where Hermes behavior is defined. |
| `.opencode/skills/codex-handoff/SKILL.md` or `skills/codex-roadmap/SKILL.md` | **The invocation mechanics.** Input format, command shape, preflight checks, completion report. The skill file itself. | **Required** — but it needs to be migrated to `ivy-control-vps` and updated. |
| `agents/CODEX_CONTRACT.md` | **Do NOT create.** The contract belongs in the Hermes agent contract (for the escalation path) and the skill file (for the invocation mechanics). A standalone Codex contract would violate documentation governance. | **Do not create.** |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | A one-sentence note that Codex handoffs follow the same inbox → execution → outbox → review → journal → promotion lifecycle as other work. | **Optional** — nice to have, not required. |
| `docs/OPERATING_MODEL.md` | The Hermes → Codex relationship is already described implicitly in the authority model. No change needed. | **No change.** |
| `agents/VPS_ORCHESTRATION.md` | If Codex is invoked from the VPS, it follows the same mode model. No Hermes-specific change needed. | **No change.** |

### 6.2 Summary of documentation changes needed

| File | Change | When |
|---|---|---|
| `agents/HERMES_AGENT_CONTRACT.md` | Add §3.5c "Codex clarification escalation" — defines when Hermes escalates, what the report must contain, and the prohibition against direct invocation | Next implementation session |
| `.opencode/skills/codex-handoff/SKILL.md` | Migrate from old `ivy-control` repo to `ivy-control-vps/.opencode/skills/codex-handoff/` | Before first Codex invocation in current workflow |
| `skills/codex-roadmap/` (planned) | Implement per Session 10 plan — adds configurable model, owned prompt, approval gate, reconciliation requirement | After codex-handoff is migrated |

### 6.3 No new permanent documents

The Codex Clarification Contract is not a standalone document. It is:

- An **escalation section** in `HERMES_AGENT_CONTRACT.md`
- An **invocation skill** in `.opencode/skills/codex-handoff/SKILL.md`

This satisfies the documentation governance rules in `docs/README.md` because
each question the contract answers already has an existing owner.

---

## 7. Implementation Sequence Recommendation

### 7.1 Ordered steps

```
Step 1: Migrate codex-handoff skill to ivy-control-vps
  Action: Copy SKILL.md from old ivy-control repo to
          ivy-control-vps/.opencode/skills/codex-handoff/
  Update: test-prompt.md paths for current repo
  Effort: 10 minutes

Step 2: Add §3.5c to HERMES_AGENT_CONTRACT.md
  Action: Define escalation path, report requirements, direct-invocation prohibition
  Content: ~20 lines
  Dependency: None

Step 3: Plan codex-roadmap skill (optional, deferred from Session 10)
  Action: Implement per Session 10 Task 119 plan
  Content: skills/codex-roadmap/{README.md, SKILL.md, config.example.yaml, prompts/generate-roadmap.md}
  Dependency: Step 1 (or reuse migrated skill)
  Priority: Low — current codex-handoff skill is functional

Step 4: Test Hermes → Codex escalation path
  Action: Run a controlled test:
          1. Hermes evaluates a deliberately insufficient roadmap
          2. Produces INSUFFICIENT report
          3. OpenCode uses report to compose Codex input
          4. Codex produces clarification
          5. OpenCode reconciles
          6. Buddy approves
          7. Hermes re-evaluates
  Dependency: Steps 1-2
  Priority: After first successful Hermes pilot
```

### 7.2 Minimum viable cut

Steps 1 and 2 are sufficient to establish the contract. The skill exists in the
old repo and can be referenced. The escalation path can be documented without
the skill being physically present in `ivy-control-vps`.

### 7.3 What NOT to implement

| Item | Reason |
|---|---|
| Hermes automatic Codex dispatch | Violates the core constraint: Hermes detects, does not invoke |
| Codex contract as standalone document | Would duplicate content from HERMES_AGENT_CONTRACT.md and SKILL.md |
| Automated reconciliation of Codex output | Reconciliation requires understanding of repo state — OpenCode's job |
| Removal of old skill before migration | Leave the old skill in place until the new one is verified |

---

## 8. Risks and Unresolved Questions

### 8.1 Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Hermes is given Codex invocation authority by accident | Low | Hermes becomes architect | Enforce "Hermes detects, does not invoke" in contract |
| Codex output used without reconciliation | Medium | Hallucinations enter roadmap | Skill contract must require reconciliation before use |
| Old skill disappears from ivy-control | Low | Cannot invoke Codex | Migrate before it's needed |
| Insufficiency report is too vague to prompt Codex | Medium | Codex clarification is useless | Design insufficiency report template to include specific questions (see §5.2) |
| Codex produces output that conflicts with roadmap gate | Low | Confusion about authority | Buddy resolves; gate is re-applied after update |

### 8.2 Unresolved questions

| Question | Options | Recommendation |
|---|---|---|
| Should the insufficiency report template include a "suggested Codex prompt" field? | Yes / No | **Yes** — Hermes identifies the specific gaps; this naturally becomes the prompt. But Hermes does not compose the prompt text — it lists the gaps, and OpenCode formulates the question. |
| Should the skill enforce configurable model mapping (fast/strong)? | Hardcoded vs. configurable | **Configurable** per Session 10 plan. Model names should not be in the skill contract. |
| Should the skill enforce an approval gate before Codex invocation? | In skill vs. in workflow | **In skill** — the skill is the natural enforcement point. Preflight checks should include "has Buddy approved this call?" |
| Should `codex-handoff` and `codex-roadmap` be one skill or two? | One vs. two | **One skill** with two modes (clarification vs. generation). The invocation mechanics are identical; only the prompt template differs. |
| Should the contract live in the skill file or in a separate contract doc? | Skill vs. separate | **Skill file** — the skill IS the contract for invocation. The escalation path (when to use it) lives in HERMES_AGENT_CONTRACT.md. |

### 8.3 Deferred decisions

| Decision | Defer until |
|---|---|
| `skills/codex-roadmap/` full implementation | After codex-handoff is migrated and first Hermes pilot succeeds |
| Hermes → Codex automated handoff | After >=2 manual escalation cycles prove the pattern |
| Model configuration beyond fast/strong | When a third model tier is needed |
| Cost tracking for Codex calls | When Codex calls become frequent enough to track |

---

## 9. Success Criteria Assessment

| Criterion | Answer |
|---|---|
| Why does codex-handoff exist? | To provide a bounded, governed invocation path from OpenCode to Codex. It prevents ad-hoc `codex exec` calls and ensures outputs are reviewable. |
| Should Hermes eventually use this capability? | **Indirectly.** Hermes should detect the need and signal Buddy, who dispatches OpenCode to use the skill. Hermes should never invoke the skill directly. |
| What contract should govern it? | A Codex Clarification Contract with: specific questions (inputs), structured clarification (outputs), reconciliation requirement, approval gate, and prohibition against direct Hermes invocation. |
| Where should that contract live? | **Escalation path** in `agents/HERMES_AGENT_CONTRACT.md` (§3.5c). **Invocation mechanics** in `.opencode/skills/codex-handoff/SKILL.md`. |
| Does this fit the roadmap sufficiency gate model? | **Yes.** The natural flow is: sufficiency gate fails → insufficiency report → Buddy reviews → dispatches Codex → Codex clarifies → roadmap updated → gate re-evaluated. Hermes does not invoke Codex — it signals the need. |

**The goal is met:** Escalation to Codex is now a controlled, auditable
architectural capability with clear boundaries, not an ad-hoc invocation path.

---

## References

- `/Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/SKILL.md` — Original skill file (99 lines)
- `/Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/test-prompt.md` — Test prompt
- `_internal/outbox/session-10/119-codex-handoff-plan.md` — Full codex-roadmap skill plan (489 lines)
- `_internal/outbox/session-10/120-roadmap-handoff-prompt-audit.md` — Prompt audit and format contract (490 lines)
- `_internal/logs/sessions/GPT-1-bootstrap-gpt-workflow.md` — Session 1 bootstrap decisions
- `agents/HERMES_ROADMAP_SUFFICIENCY_GATE.md` — Current sufficiency gate (Task 13)
- `agent/reports/session-12/06-hermes-roadmap-sufficiency-preflight.md` — Task 11 preflight
- `agent/reports/session-12/07-hermes-orchestration-contract-plan.md` — Task 12 implementation plan
- `agent/reports/session-12/08-hermes-roadmap-gate-pilot-validation.md` — Task 13 pilot validation
- `agents/HERMES_AGENT_CONTRACT.md` — Hermes contract (target for §3.5c)
- `docs/OPERATING_MODEL.md` — Work ownership
- `docs/REPOSITORY_WORK_PROTOCOL.md` — Artifact lifecycle
