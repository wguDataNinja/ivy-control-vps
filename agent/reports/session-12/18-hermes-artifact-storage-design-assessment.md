# Session 12 — Task 18: Hermes Artifact Storage Design Assessment

**Date:** 2026-07-19
**Status:** DESIGN_COMPLETE

---

## Files Inspected

| Path | Purpose |
|---|---|
| `_internal/GPT_ORCHESTRATED_WORKFLOW.md` | Private workflow — 1695 lines, defines the full agent lifecycle and artifact conventions |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | Public work protocol — task lifecycle, artifact-only orchestration |
| `agents/HERMES_AGENT_CONTRACT.md` | Hermes contract — checkpoint rules, orchestration lifecycle |
| `agents/HERMES_OPERATOR_GUIDE.md` | Hermes operator guide — bridge paths, role boundaries |
| `agent/reports/session-12/` | Existing public session reports (11 files) |
| `_internal/inbox/session-12/` | Private task prompts |
| `_internal/outbox/session-12/` | Private result reports |
| `/Users/buddy/projects/palworld-kb/agent/` | Palworld KB agent conventions (inbox, reports, templates) |
| `/Users/buddy/projects/palworld-kb/agent-reports/` | Palworld KB public-facing reports |
| `/Users/buddy/projects/sts-workbench/agent/` | STS Workbench agent conventions (inbox, reports, templates) |

---

## 1. Current State

### 1.1 Ivy Control VPS conventions

| Artifact | Location | Visibility |
|---|---|---|
| Task prompts | `_internal/inbox/session-<N>/` | Private (VPS checkout must not rely on it) |
| Result reports | `_internal/outbox/session-<N>/` | Private |
| Execution logs | `_internal/logs/agents/YYYY-MM-DD/` | Private |
| Session journal | `_internal/logs/sessions/SESSION_JOURNAL.md` | Private |
| Public session reports | `agent/reports/session-<N>/` | Public |
| Hermes contracts | `agents/` | Public |
| Task packet template | `agents/orchestrator-task-packet-template.md` | Public |

### 1.2 Palworld KB conventions

| Artifact | Location | Visibility |
|---|---|---|
| Task inbox | `agent/inbox/` | Tracked |
| Reports | `agent/reports/` | Tracked |
| Templates | `agent/templates/` | Tracked |
| Public reports | `agent-reports/` (by category) | Tracked |
| Session journal | `agent-reports/SESSION_JOURNAL.md` | Tracked |
| Private material | `_internal/`, `_inbox/` | Ignored |

### 1.3 STS Workbench conventions

| Artifact | Location | Visibility |
|---|---|---|
| Task inbox | `agent/inbox/` | Tracked |
| Reports | `agent/reports/` | Tracked |
| Templates | `agent/templates/` | Tracked |
| Private material | `_internal/` | Ignored |

### 1.4 Gap: Hermes validation artifact

The existing lifecycle defined in `_internal/GPT_ORCHESTRATED_WORKFLOW.md` is:

```
agent execution → result report → GPT reviews → journal entry
```

The intended Hermes lifecycle is:

```
agent execution → result report → Hermes validates → Hermes acceptance/rejection → journal entry
```

The `Hermes acceptance/rejection` artifact does not exist anywhere in the
current convention. Hermes currently either:
- Passes the checkpoint silently (no durable artifact)
- Or stops with `NEEDS_GPT_OR_BUDDY_DECISION` (documented in contract but no
  template for the rejection artifact)

---

## 2. Options Considered

### Option A: All Hermes artifacts stay in Ivy Control VPS

**Layout:**
```
ivy-control-vps/_internal/hermes/
  orchestrations/<repo>/<envelope-id>/
    task-packets/
    validation-reports/
    acceptance-records/
```

| Pro | Con |
|---|---|
| Single source of truth for orchestration state | Target repo engineer cannot see their own orchestration history |
| No cross-repo convention needed | VPS checkout cannot rely on `_internal/` — Hermes cannot access these from VPS |
| Private orchestration mechanics stay private | Violates §1A of GPT_ORCHESTRATED_WORKFLOW: "a repository should be understandable without relying on chat history" — except now it relies on Ivy Control history |
| Works with current tooling | Ivy Control becomes a bottleneck for all orchestration records |

### Option B: Each target repository stores its own Hermes artifacts

**Layout:**
```
sts-workbench/agent/orchestration/
  task-packets/
  execution-reports/
  hermes-validations/
  acceptance-records/
```

| Pro | Con |
|---|---|
| Repository is self-contained — a new engineer can see full history | Every repo needs the same convention enforced |
| No dependency on Ivy Control for task history | Hermes contracts (cross-repo) are duplicated or hard to reference |
| VPS-resident repos keep their artifacts in their checkout | Repos without Hermes scope still get the directory structure |
| Matches existing agent conventions (inbox/reports/templates) | Existing repos already have `agent/` but no `agent/orchestration/` |

### Option C: Hybrid model (recommended)

**Layout:**
```
# In each target repository:
repository-root/agent/
  orchestration/
    <envelope-id>/
      01-task-packet.md          ← Hermes writes
      02-execution-report.md     ← Execution agent writes
      03-hermes-validation.md    ← Hermes writes (NEW)
      04-execution-log.md        ← Execution agent writes (optional)

# In Ivy Control VPS:
ivy-control-vps/
  agents/                          ← Hermes contracts (public)
  agent/reports/session-<N>/       ← Cross-repo orchestration summaries
  _internal/hermes/state/          ← Private orchestration state (tracked tasks, envelopes)
  _internal/logs/sessions/         ← Portfolio journal
```

| Pro | Con |
|---|---|
| Target repos are self-contained for their history | Requires conventions to be documented per-repo |
| Ivy Control keeps cross-repo orchestration and contracts | Some duplication between repo-local and portfolio records |
| VPS checkout can access repo-local artifacts | Hermes needs write access to `agent/orchestration/` in target repos |
| Existing `agent/` conventions extend naturally | Existing repos need migration |
| Private orchestration state stays private in `_internal/` | New path pattern to learn |

---

## 3. Repository Independence Assessment

**Question:** Would a future engineer entering sts-workbench understand its
Hermes-managed history if validation records only existed in ivy-control-vps?

**Answer: No.** A future engineer reading sts-workbench would find task packets
and execution reports (if stored locally) but would not find Hermes's
independent validation of those results. They would see "work was done" but not
"work was verified and accepted."

**Question:** Would Ivy Control become overloaded if every repository's
execution history lived there?

**Answer: Yes.** With 10+ managed repositories, each producing multiple
delegations per session, Ivy Control's `_internal/outbox/` would grow
unboundedly. The current outbox already has ~100 artifacts across 12 sessions.
Adding per-delegation artifacts for every repo would make the outbox
unmanageable.

**Principle applied:** `_internal/GPT_ORCHESTRATED_WORKFLOW.md` §10B says
repositories may use alternative paths such as `inbox/`, `outbox/`,
`agent/reports/`. This supports the hybrid model — each repo extends its
existing `agent/` convention with an `orchestration/` subdirectory.

---

## 4. Autonomous Hermes Requirements

For Hermes to safely resume after interruption, validate completed tasks, and
decide whether to proceed, these artifacts are required:

### Required for safe autonomous progression

| Artifact | Purpose | Produced by | Consumed by |
|---|---|---|---|
| **Task packet** | Defines what was delegated | Hermes | Execution agent |
| **Execution report** | Records what was done and evidence | Execution agent | Hermes |
| **Hermes validation report** | Records Hermes's independent assessment of the execution report | Hermes | Journal, next delegation decision |
| **Orchestration state record** | Tracks which tasks are delegated, completed, accepted, rejected | Hermes | Hermes (resume after interruption) |

### The Hermes validation report

This is the key missing artifact. It should contain:

```
## Hermes Validation

**Envelope:** <id>
**Task packet:** <path>
**Execution report:** <path>

### Checkpoint review
- Result report exists? PASS/FAIL
- Validation evidence present? PASS/FAIL
- Changed files in scope? PASS/FAIL
- Stop conditions triggered? PASS/FAIL

### Assessment
- HERMES_ACCEPT — validation passes, no issues found
- HERMES_ACCEPT_WITH_NOTE — validation passes, minor observations
- HERMES_REJECT — validation fails, specific defects identified
- NEEDS_BUDDY_REVIEW — checkpoint rule requires escalation

### Evidence
- <links to checked artifacts>

### Next action
- Continue (next task within envelope)
- Stop (envelope exhausted)
- Escalate (needs Buddy/Codex)
```

This is analogous to GPT's `ACCEPT`/`REWORK_REQUIRED`/`HUMAN_DECISION_REQUIRED`
in the existing workflow (GPT_ORCHESTRATED_WORKFLOW.md §7C), but performed by
Hermes instead of GPT.

---

## 5. Recommended Model

### 5.1 Directory layout

```
# Target repository agent directory (extends existing convention)
repo/agent/
  README.md                           ← describes convention
  INDEX.md                            ← index of reports
  inbox/                              ← task prompts (existing)
  reports/                            ← execution reports (existing)
  templates/                          ← templates (existing)
  orchestration/                      ← NEW: Hermes orchestration artifacts
    <envelope-id>/                    ← one directory per delegation envelope
      01-<task-slug>-packet.md        ← Hermes writes task packet
      02-<task-slug>-execution.md     ← Execution agent writes result
      03-<task-slug>-validation.md    ← NEW: Hermes writes validation (accept/reject)
      04-<task-slug>-log.md           ← Execution agent writes log (optional)

# Ivy Control VPS cross-repo records
ivy-control-vps/agent/reports/session-<N>/   ← public cross-repo summaries
ivy-control-vps/_internal/hermes/
  state/                                      ← private orchestration state (envelopes, progress)
```

### 5.2 Artifact ownership rules

| Artifact | Owner | Location |
|---|---|---|
| Task packet | Hermes writes | Target repo `agent/orchestration/<envelope-id>/` |
| Execution report | Execution agent writes | Target repo `agent/orchestration/<envelope-id>/` |
| Hermes validation | Hermes writes | Target repo `agent/orchestration/<envelope-id>/` |
| Execution log | Execution agent writes (optional) | Target repo `agent/orchestration/<envelope-id>/` |
| Orchestration state | Hermes maintains | Ivy Control `_internal/hermes/state/` |
| Cross-repo summary | Hermes writes | Ivy Control `agent/reports/session-<N>/` |
| Portfolio journal | GPT/Buddy | Ivy Control `_internal/logs/sessions/` |

### 5.3 Lifecycle

```
Hermes reads delegation envelope
  ↓
Hermes creates 01-<task>-packet.md in target repo agent/orchestration/<id>/
  ↓
Execution agent reads packet, implements
  ↓
Execution agent writes 02-<task>-execution.md
  ↓
Hermes reads execution report
  ↓
Hermes writes 03-<task>-validation.md:
  - HERMES_ACCEPT → proceed
  - HERMES_REJECT → rework or escalate
  - NEEDS_BUDDY_REVIEW → stop
  ↓
Hermes updates orchestration state in _internal/hermes/state/
  ↓
Hermes writes cross-repo summary to agent/reports/session-<N>/ (if applicable)
  ↓
Portfolio journal updated (GPT or Hermes proposal)
```

### 5.4 Validation boundary

Hermes validation checks, in order:

1. **Artifact completeness** — does the execution report exist? Does it contain
   the required fields? (objective, sources, changes, validation, findings)
2. **Validation evidence** — did the execution agent run the required tests?
   Are the results present and passing?
3. **Scope compliance** — are the changed files within the allowed paths
   defined in the task packet?
4. **Stop conditions** — are any stop conditions triggered? (blocker appeared,
   gate change, scope violation)
5. **Claim verification** — can the claims in the execution report be verified
   against existing files, tests, and evidence?

Only artifacts that pass all five checks receive `HERMES_ACCEPT`.

### 5.5 Migration plan

| Phase | Action | Impact |
|---|---|---|
| 1 | Document convention: add `agent/orchestration/` to AGENTS.md or CONTROL.md for each repo | No existing artifacts moved |
| 2 | Create `agent/orchestration/` directory in target repos | Empty until first delegation |
| 3 | Update task packet template to declare orchestration artifact paths | New packets use new paths |
| 4 | Create Hermes validation template (`agents/hermes-validation-template.md`) | Hermes writes structured validation |
| 5 | Update HERMES_AGENT_CONTRACT.md checkpoint rule to reference validation template | New lifecycle formally documented |
| 6 | Backfill: existing task packets remain; no migration needed | No disruption |

---

## 6. Relationship to Existing Workflow

### 6.1 Required updates (do not implement — proposed only)

| Document | Proposed change |
|---|---|
| `_internal/GPT_ORCHESTRATED_WORKFLOW.md` | Add Hermes as a reviewer in the lifecycle (between agent execution and journal). Update the lifecycle diagram in §10E to include Hermes validation step. Update §16E (Hermes role) to include validation and acceptance/rejection artifacts. |
| `agents/HERMES_AGENT_CONTRACT.md` | Update §3.5b checkpoint lifecycle to reference `03-<task>-validation.md` as the artifact Hermes produces. Define the four validation outcomes. |
| `agents/HERMES_OPERATOR_GUIDE.md` | Document where Hermes reads and writes orchestration artifacts in target repositories. |
| `docs/REPOSITORY_WORK_PROTOCOL.md` | Add `agent/orchestration/` to the repository-approved locations table (§4). |
| `agents/orchestrator-task-packet-template.md` | Add an `Orchestration artifact paths` section declaring where `02-*` and `03-*` artifacts go. |
| Target repo AGENTS.md or CONTROL.md | Declare `agent/orchestration/` as an allowed Hermes artifact path (required for Mode 0). |

### 6.2 Template needed: Hermes validation report

A new template file is needed:

```
agents/hermes-validation-report-template.md
```

Content:
- Envelope reference
- Task packet reference
- Execution report reference
- 5-point checkpoint checklist (completeness, validation, scope, stop conditions, claims)
- Four outcome states (ACCEPT, ACCEPT_WITH_NOTE, REJECT, NEEDS_BUDDY_REVIEW)
- Evidence links
- Next action recommendation

This is NOT a new permanent document — it is a reusable template analogous to
`agents/orchestrator-task-packet-template.md`.

---

## 7. Recommendation

**Recommend Option C (Hybrid model).**

| Criterion | Option A (centralized) | Option B (per-repo) | Option C (hybrid) |
|---|---|---|---|
| Repo self-contained | No | Yes | Yes |
| Cross-repo visibility | Strong | Weak | Strong (via summaries) |
| VPS compatibility | Poor (relies on `_internal/`) | Good | Good |
| Migration effort | Low | Medium | Medium |
| Scalability (10+ repos) | Poor | Good | Good |

The hybrid model gives each target repository a self-contained orchestration
history (anyone entering sts-workbench can see task → execution → validation
for each delegation) while keeping cross-repo orchestration state and contracts
in Ivy Control where they belong.

**This recommendation does not require immediate implementation.** The existing
checkpoint rule in `HERMES_AGENT_CONTRACT.md` §3.5 functions without a
dedicated validation artifact. The validation artifact formalizes what Hermes
already does — it just makes the outcome durable, structured, and discoverable.

---

## 8. Unresolved Decisions

| Decision | Options | Recommendation |
|---|---|---|
| Should the Hermes validation report template live in `agents/` or be per-repo? | `agents/` vs per-repo | **`agents/`** — it is a reusable template, same as `orchestrator-task-packet-template.md`. |
| Should `agent/orchestration/` be public or private? | Public vs. private | **Public (tracked).** Task packets and validation reports are publication-safe — they describe delegated work, not private reasoning. Execution logs should stay in `_internal/` if they contain sensitive detail. |
| Should validation outcomes map to journal statuses? | Direct vs. indirect | **Direct** — `HERMES_ACCEPT` maps to a journal entry, `HERMES_REJECT` triggers rework or escalation. This mirrors GPT's `ACCEPT`/`REWORK_REQUIRED`. |
| Who archives old orchestration directories? | Hermes vs. manual | **Defer.** Orchestration directories are small and append-only. Archive policy is not needed until volume becomes a concern. |
| Should the orchestration directory use envelope ID or task slug? | Envelope vs. slug | **Envelope ID.** Multiple tasks share one envelope. Grouping by envelope keeps related artifacts together. |

---

## 9. Summary

| Question | Answer |
|---|---|
| Current gap? | Hermes validation produces no durable artifact. The checkpoint is passed silently or escalated, but there is no structured `03-*-validation.md` record. |
| Where should Hermes artifacts live? | **Hybrid model (Option C):** per-repo `agent/orchestration/<envelope-id>/` for task-level artifacts; Ivy Control for cross-repo orchestration state and contracts. |
| Are target repos ready? | Both palworld-kb and sts-workbench already have `agent/` conventions with `inbox/`, `reports/`, and `templates/`. Adding `agent/orchestration/` is a natural extension. |
| What new artifacts are needed? | Hermes validation report template (`03-<task>-validation.md`), orchestration state record, validation outcomes (ACCEPT/REJECT/NEEDS_BUDDY_REVIEW). |
| What documents need updates? | 6 documents identified (see §6.1). None require immediate changes. |
| Is this design ready for implementation? | **DESIGN_COMPLETE.** The storage model is stable. Implementation should follow the 6-phase migration plan (§5.5) when Hermes pilot begins. |

---

## References

- `_internal/GPT_ORCHESTRATED_WORKFLOW.md` — Private workflow (1695 lines)
- `docs/REPOSITORY_WORK_PROTOCOL.md` — Public work protocol
- `agents/HERMES_AGENT_CONTRACT.md` — Hermes contract, checkpoint rules
- `agents/HERMES_OPERATOR_GUIDE.md` — Hermes operator guide
- `agents/orchestrator-task-packet-template.md` — Current task packet template
- `/Users/buddy/projects/palworld-kb/agent/` — Palworld KB agent conventions
- `/Users/buddy/projects/sts-workbench/agent/` — STS Workbench agent conventions
