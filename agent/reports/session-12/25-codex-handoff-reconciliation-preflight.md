# Session 12 — Task 25: Codex Handoff Reconciliation Preflight

**Date:** 2026-07-19
**Status:** CODEX_HANDOFF_READY_FOR_INTEGRATION

---

## 1. Current Codex Handoff Behavior

### 1.1 Location

The skill exists at:
```
/Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/
├── SKILL.md          (99 lines — contract, preflight, command, completion)
├── test-prompt.md    (39 lines — example prompt)
```

It is NOT present in `ivy-control-vps/.opencode/skills/` — that directory does
not exist. The skill is orphaned in the predecessor repository.

### 1.2 Invocation mechanics

| Aspect | Current behavior |
|---|---|
| **Input** | A markdown file beginning with a handoff header that declares the output file path |
| **Command** | `codex exec --skip-git-repo-check -m gpt-5.5 - < "<input-file>"` |
| **Output** | Codex writes directly to the declared output file path |
| **Preflight** | 5 checks: file exists, header correct, output path set, prompt appropriate, not edited without permission |
| **Completion report** | Command run, exit code, output path, file exists check, stderr summary |

### 1.3 Prompt structure

The skill does NOT define the content of the prompt. It defines:
- The handoff header format (required preamble)
- That the output path must be declared inside the input file
- That Codex should write to the file and respond with a brief completion note

The actual prompt content is caller-supplied. The skill enforces format, not
substance.

### 1.4 Output handling

Codex writes to the declared output file path. The skill does NOT:
- Require reconciliation of Codex output
- Check whether the output contains the requested artifact
- Validate that Codex stayed within authority boundaries
- Track whether the output was reviewed or acted upon

### 1.5 Safety assumptions

| Assumption | Current state |
|---|---|
| Caller is responsible for prompt quality | True — skill enforces format only |
| Caller is responsible for output review | True — skill does not reconcile |
| Codex invocation is gated by human approval | **False** — skill has no approval gate; any agent may invoke it |
| Codex output is advisory, not authoritative | Implicit but not enforced |
| Codex model is fixed | Hardcoded to `gpt-5.5` |

### 1.6 Key limitation

The skill has no concept of:
- Capability gating (what Codex is allowed to do)
- Approval requirements (who must approve before invocation)
- Reconciliation (output verification before use)
- Hermes integration (no reference to orchestration artifacts)

---

## 2. Hermes Integration Analysis

### 2.1 Overlap with new Hermes artifacts

| Hermes concept | Codex-handoff overlap | Assessment |
|---|---|---|
| **Task packet** (`orchestrator-task-packet-template.md`) | **None** — skill does not define task structure | No overlap |
| **Execution report** (`REPORT.md`) | **None** — skill does not define result reporting | No overlap |
| **Hermes validation report** (`hermes-validation-report-template.md`) | **None** — skill does not define checkpoint review | No overlap |
| **Codex escalation context** (`codex-escalation-context-template.md`) | **Complementary** — context template defines WHAT to ask; skill defines HOW to invoke | **Reuse together** |
| **Gate packet** (`GATE_PACKET_TEMPLATE.md`) | **None** — skill does not define decision gates | No overlap |

### 2.2 Classification

| Element | Classification | Rationale |
|---|---|---|
| Input file format (handoff header) | **Reuse as-is** | Becomes the carrier for the escalation context content |
| Invocation command | **Reuse as-is** | May need model config update (currently hardcoded `gpt-5.5`) |
| Preflight checks | **Reuse as-is** | 5 checks are still valid |
| Completion report | **Reuse as-is** | Still needed for invocation audit |
| Prompt content structure | **Now covered by escalation context template** | Replaces ad-hoc prompt construction |
| Approval gate | **Missing — needs addition** | No check for Buddy approval before invocation |
| Reconciliation requirement | **Missing — needs addition** | No requirement to review Codex output before use |
| Capability awareness | **Missing — needs addition** | No concept of which capability is being invoked |

---

## 3. Recommended Architecture

### 3.1 Final relationship

```
Hermes detects reasoning boundary
  ↓
Hermes produces NEEDS_CODEX validation outcome
  ↓
Hermes checks capability registry (CONTROL.md):
  - Is the capability enabled?
  - Does it require Buddy approval?
  ↓
[disabled] → fall back to NEEDS_BUDDY_REVIEW
[enabled, approval required] → produce escalation context → Buddy approves
[enabled, pre-authorized] → produce escalation context directly
  ↓
Hermes writes Codex Escalation Context artifact
  (using codex-escalation-context-template.md)
  ↓
OpenCode reads escalation context
  ↓
OpenCode prepends skill handoff header to escalation context
  → input file = handoff header + escalation context content
  ↓
OpenCode invokes codex-handoff skill
  → codex exec --skip-git-repo-check -m <model> - < "<input-file>"
  ↓
Codex writes output to declared path
  ↓
OpenCode reconciles Codex output
  (fixes hallucinated paths, corrects assumptions)
  ↓
Hermes evaluates reconciled output
  (produces HERMES_ACCEPT or HERMES_REJECT)
  ↓
If ACCEPT: roadmap/state updated, orchestration resumes
If REJECT: escalation to Buddy
```

### 3.2 What changes about the skill

| Aspect | Current | Future |
|---|---|---|
| Prompt source | Caller-supplied, unstructured | Escalation context template with bounded questions |
| Approval gate | None | Required — Buddy must approve before invocation |
| Reconciliation | None | Required — OpenCode reconciles before Hermes evaluates |
| Model selection | Hardcoded `gpt-5.5` | Configurable per capability (fast/strong) |
| Capability awareness | None | Implicit — context template declares capability |
| Output tracking | None | Hermes validation report records whether output was accepted |

### 3.3 The skill itself does NOT need modification

The architecture does not require changing a single line of `SKILL.md`. All
governance additions happen at the Hermes level:

| Governance | Lives in | How it works |
|---|---|---|
| Approval gate | Hermes check before escalation | Hermes checks `requires_buddy_approval` before producing escalation context |
| Reconciliation requirement | Hermes validation after Codex output | Hermes requires reconciled output before evaluating |
| Content structure | `codex-escalation-context-template.md` | Hermes fills this template; OpenCode uses it as the skill input |
| Capability enablement | `CONTROL.md` `hermes.codex_capabilities` | Hermes checks before producing NEEDS_CODEX |

The skill remains a pure invocation mechanism. The governance is layered on
top by Hermes.

---

## 4. Migration Plan

### 4.1 Required: Copy skill to ivy-control-vps

| From | To |
|---|---|
| `/Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/SKILL.md` | `ivy-control-vps/.opencode/skills/codex-handoff/SKILL.md` |
| `/Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/test-prompt.md` | `ivy-control-vps/.opencode/skills/codex-handoff/test-prompt.md` |

**Nature:** Pure file copy. Zero modifications. The skill is 99 lines and
requires no changes to integrate with the Hermes model.

### 4.2 Not required: Skill modification

The following changes are intentionally NOT made to the skill:

| Potential change | Why deferred |
|---|---|
| Model config (hardcoded `gpt-5.5`) | The skill's model selection is a practical concern for the pilot, not an architecture issue. Can be addressed by adding a `config.example.yaml` (per Session 10 plan) or by letting OpenCode override the model flag when invoking. |
| Approval gate in preflight | Approval is enforced by Hermes before the skill is invoked. Adding it to the skill would duplicate governance. |
| Reconciliation requirement | Reconciliation is Hermes's responsibility after Codex output arrives. The skill's job ends when Codex writes the output file. |

### 4.3 Validation after migration

| Check | How |
|---|---|
| Skill loads correctly | `cat .opencode/skills/codex-handoff/SKILL.md` produces valid markdown |
| Command shape works | Dry-run only — do not invoke Codex |
| Preflight checks pass | Run preflight against a sample escalation context |

---

## 5. Ownership Recommendation

### 5.1 Where should codex-handoff live?

**Option A: `ivy-control-vps/.opencode/skills/`** (Recommended)

| Pro | Con |
|---|---|
| Follows OpenCode conventions for repository-local skills | Skill is not useful outside this repo's workflow |
| Keeps the skill with the contracts and templates that govern it | Requires migration from old repo |
| Discoverable — same directory as other Hermes tooling | |
| Portfolio-owned — any agent working in this repo can use it | |

**Option B: `_internal/`**

| Pro | Con |
|---|---|
| Keeps invocation mechanics private | Private — VPS checkout cannot use it |
| | Violates `_internal/` purpose (orchestration notes, not tooling) |

**Option C: System-level OpenCode skills directory (`~/.config/opencode/skills/`)**

| Pro | Con |
|---|---|
| Available to all repositories | Ivy-specific tooling should not be system-global |
| | Would require installing across machines |

**Recommendation: Option A.** The skill is a repository-local tool that should
live alongside the Hermes contracts and templates in `ivy-control-vps`. It is
not system-level infrastructure and not private orchestration material.

### 5.2 Final artifact ownership

| Artifact | Location | Owner |
|---|---|---|
| Capability definitions | `agents/HERMES_AGENT_CONTRACT.md` §3.5d | Ivy Control (contract) |
| Capability enablement | `CONTROL.md` `hermes.codex_capabilities` | Per-repository |
| Escalation context template | `agents/codex-escalation-context-template.md` | Ivy Control (template) |
| Escalation context artifact | Target repo declared artifact paths | Hermes writes one per NEEDS_CODEX |
| Codex invocation skill | `.opencode/skills/codex-handoff/SKILL.md` | Ivy Control (tooling) |
| Codex output artifact | Target repo declared artifact paths | Codex writes (via skill) |
| Reconciled Codex output | Target repo declared artifact paths | OpenCode reconciles |
| Post-escalation Hermes validation | Target repo declared artifact paths | Hermes writes |

---

## 6. Capability Integration

### 6.1 What happens when NEEDS_CODEX occurs

```
1. Hermes validation report contains NEEDS_CODEX outcome
2. Hermes checks CONTROL.md hermes.codex_capabilities for matching capability
3. If capability is:
   - [disabled] → fall back to NEEDS_BUDDY_REVIEW
   - [enabled, requires_buddy_approval] → produce escalation context → Buddy approves
   - [enabled, pre-authorized] → produce escalation context directly
4. Hermes writes escalation context artifact using codex-escalation-context-template.md
5. OpenCode reads escalation context
6. OpenCode prepends skill handoff header (without modifying the context content)
7. OpenCode invokes: codex exec --skip-git-repo-check -m <model> - < "<input-file>"
8. Codex writes output to declared path
9. OpenCode reconciles output (fixes paths, corrects assumptions)
10. Hermes evaluates reconciled output

Artifacts before invocation:
  - Hermes validation report (with NEEDS_CODEX)
  - Codex escalation context

Artifacts after completion:
  - Codex output (raw, before reconciliation)
  - Reconciled Codex output (after OpenCode fixes)
  - Hermes post-escalation validation (ACCEPT or REJECT)

Continuation decision:
  - Hermes decides (ACCEPT → continue; REJECT → escalate to Buddy)
```

### 6.2 Example: roadmap_repair enabled for Palworld KB

```yaml
# In palworld-kb CONTROL.md
hermes:
  codex_capabilities:
    roadmap_repair:
      enabled: true
      requires_buddy_approval: true
```

Flow:
1. Hermes runs roadmap gate on Palworld KB → `ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION`
   (criteria 1, 2, or 4 fail)
2. Hermes checks `hermes.codex_capabilities.roadmap_repair` → enabled, approval required
3. Hermes produces escalation context with specific questions about the roadmap gaps
4. Buddy reviews and approves the escalation
5. OpenCode invokes codex-handoff with the escalation context
6. Codex produces a roadmap improvement proposal
7. OpenCode reconciles (fixes any hallucinated paths)
8. Hermes evaluates the reconciled output and reruns the roadmap gate
9. If gate passes → orchestration proceeds. If still insufficient → escalate to Buddy.

---

## 7. Implementation Tasks Required

| Task | Files | Effort |
|---|---|---|
| Copy skill to `ivy-control-vps/.opencode/skills/codex-handoff/` | 2 files | 5 minutes |
| Add `codex_capabilities` to pilot repo CONTROL.md | 1 file | 5 minutes |
| Enable `roadmap_repair` capability | CONTROL.md edit | 1 line change |
| Run pilot escalation test | Multiple artifacts | 1 session |

No skill modification is required. No Hermes contract changes are required.
The architecture is ready for the pilot.

---

## 8. Open Decisions

| Decision | Options | Recommendation |
|---|---|---|
| Should the skill's hardcoded `gpt-5.5` model be configurable before the pilot? | Yes vs. defer | **Defer.** Hardcoded model works for initial test. Configurable model mapping (fast/strong) can be added after pilot. |
| Should the skill be invoked by OpenCode or by Buddy? | OpenCode vs. Buddy | **OpenCode.** OpenCode reconciles the output. Buddy approves but does not invoke. |
| Should the escalation context be the EXACT input file, or should OpenCode be allowed to add supporting context? | Exact vs. extensible | **Extensible.** The escalation context is the core; OpenCode may add context (file snippets, diffs) as long as the original questions and constraints remain intact. |
| Should Codex output be stored alongside the escalation context or in a separate location? | Same directory vs. separate | **Same directory.** Co-location makes the escalation chain discoverable. |

---

## 9. Summary

| Question | Answer |
|---|---|
| Does `codex-handoff` overlap with new Hermes artifacts? | **No** — it is complementary. The skill defines HOW (invocation); Hermes defines WHEN and WHAT (capability gating, content structure). |
| Does the skill need modification? | **No** — all governance additions happen at the Hermes level (capability registry, approval check, reconciliation requirement). |
| Where should it live? | **`ivy-control-vps/.opencode/skills/codex-handoff/`** — repository-local tool alongside contracts and templates. |
| What migration is needed? | **Pure file copy.** 2 files, 5 minutes, zero modifications. |
| What is the integration status? | **CODEX_HANDOFF_READY_FOR_INTEGRATION.** The architecture is defined. The skill is the execution layer. Hermes is the governance layer. No design work remains before the pilot. |

---

## References

- `/Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/SKILL.md` — Current skill (99 lines)
- `/Users/buddy/projects/ivy-control/.opencode/skills/codex-handoff/test-prompt.md` — Example prompt (39 lines)
- `agents/HERMES_AGENT_CONTRACT.md` §§3.5d-3.5e — Capability definitions, escalation flow
- `agents/codex-escalation-context-template.md` — Escalation context template (113 lines)
- `agents/hermes-validation-report-template.md` — Validation report template (107 lines)
- `agent/reports/session-12/23-hermes-artifact-template-design-preflight.md` — Template design (source)
- `agent/reports/session-12/24-hermes-artifact-template-implementation.md` — Template implementation
