# Session 12 — Task 10: _internal Historical Intent and Migration Reconciliation

**Date:** 2026-07-20
**Status:** COMPLETED — analysis only, no files modified

---

## 1. Executive Summary

_internal/ was not designed as a permanent architecture layer. It was created as an emergency response to the 2026-07-07 deletion incident, hardened over subsequent sessions, and has accumulated three distinct roles that were never formally separated.

**Critical correction to Task 09:** The DB templates were already promoted to public templates/ in Session 9 (19-final-opencode-cleanup-and-commits.md). The copies remaining in _internal/templates/ are harmless gitignored duplicates. Task 09's primary recommendation was already executed.

The future of _internal/ should be: keep it as the private orchestration workspace, acknowledge the public templates as already migrated, and trim README_INTERNAL.md of duplicated public content (a recommendation from Session 10 that was never executed).

---

## 2. Creation History

### Origin: 2026-07-07 deletion incident

Before the incident, private content lived under internal/ (gitignored). An ambiguous instruction caused an agent to run a destructive find/xargs rm command that deleted every top-level file except .git/, including the entire internal/ tree. Six private logs were permanently lost. The original README_INTERNAL.md was lost and had to be reconstructed from memory.

### _internal/ creation: commit 0a300b9 (2026-07-07)

The replacement was deliberately engineered with: separate private Git repo with no remote, .gitignore exclusion, pre-commit hook blocking staging, pre-push hook blocking publication, private push protection, and underscore naming convention.

### Evolution across sessions

| Session | Date | _internal/ decision |
|---|---|---|
| Pre-1 | 2026-07-07 | _internal/ created as private Git repo with safety hooks |
| Pre-1 | 2026-07-07 | .gitignore added, visibility fixed (commit 450294b) |
| 1 | 2026-07-XX | "Exact orchestration mechanics remain private under _internal/" |
| 3 | 2026-07-XX | Inbox/outbox convention formalized (session-N/slug) |
| 7 | 2026-07-14 | _internal/ policy confirmed sound, hooks verified |
| 9 | 2026-07-15 | Templates migrated _internal/templates/ to public templates/ (16 files) |
| 9 | 2026-07-15 | Level 2 cleanup proposed: move agent-reports/logs under _internal/ |
| 10 | 2026-07-18 | README_INTERNAL.md analyzed: 55% duplicates public content |
| 10 | 2026-07-18 | Evidence cards: move to _internal/evidence/cards/ proposed |
| 12 | 2026-07-20 | Task 09: boundary audit (missed Session 9 template migration) |
| 12 | 2026-07-20 | Task 10: historical intent recovery (this report) |

---

## 3. Intent Timeline

### Session 1: "Orchestration mechanics remain private"

GPT-1 established the core principle: exact orchestration mechanics (agent routing, inbox/outbox, task artifacts, gate packets, GPT session logs, session-close behavior) remain private under _internal/. Public docs describe the durable interface, not the private orchestration.

This decision has never been challenged or changed.

### Session 3: Inbox/outbox convention

The session-N/slug convention for inbox and outbox paths was formalized. This remains the current convention.

### Session 7: Boundary confirmed sound

Buddy approved direct-to-main commits. Safety verification confirmed _internal/ never published. Pre-commit and pre-push hooks verified working.

### Session 9: Template migration (already executed)

Session 9 discovered that _internal/templates/ contained durable repository products (CONTROL_TEMPLATE.md, 15 DB_*.md) that were not session evidence. These were moved to public templates/ (tracked in Git) and doc references were updated from _internal/templates/DB_* to templates/DB_*.

This is the only case where _internal/ content was intentionally promoted to public. It was executed cleanly. The copies in _internal/templates/ are harmless gitignored duplicates.

### Session 9: Level 2 cleanup proposed (not executed)

Session 9 proposed moving agent-reports/, prompts/, logs/, and _inbox/ under _internal/. This was a cleanup recommendation, not a migration. It was never executed but remains valid.

### Session 10: README_INTERNAL.md pruning (not executed)

Session 10 extensively analyzed README_INTERNAL.md and found ~55% duplication with public authority documents. A detailed pruning plan was created but never implemented. The recommendations remain valid.

### Session 10: Evidence card relocation (partially executed)

Three evidence cards were to be moved to _internal/evidence/cards/. The git-closeout-classification.md noted this but it's unclear whether the move was completed.

---

## 4. Decision Log

| Decision | Status | Source |
|---|---|---|
| _internal/ is a separate private Git repo with no remote | Current | commit 0a300b9 |
| _internal/ is excluded by .gitignore + hooks | Current | commit 450294b |
| Orchestration mechanics stay private | Current | GPT-1 session log |
| Inbox/outbox use session-N convention | Current | GPT-3 session log |
| Templates are public (not private) | Executed (S9) | 19-final-opencode-cleanup |
| README_INTERNAL.md should be pruned | Not executed | S10 doc-architecture-audit |
| Evidence cards in _internal/evidence/cards/ | Partially executed | S10 hygiene-architecture |
| Level 2 cleanup (more dirs under _internal/) | Not executed | S9 39-portfolio-placement |
| _internal/ never enters VPS | Current | GIT_WORKFLOW.md + CONTROL.md + OPERATING_MODEL.md |
| Legacy internal/ should be migrated and removed | Not executed | GIT_WORKFLOW.md |

---

## 5. Contradiction Analysis

### Claim: DB templates should be promoted to public

**Task 09 finding:** 14 DB templates are public documentation candidates.
**Historical fact:** They were already promoted in Session 9. The public templates/ directory contains all 16 DB templates + CONTROL_TEMPLATE.

**Resolution:** No action needed. Task 09's recommendation was already executed. The _internal/templates/ copies are stale duplicates.

### Claim: _internal/templates/ is all private

**Task 09 classification:** templates/ are "private orchestration."
**Historical fact:** 16 of 21 templates were already moved to public templates/ in Session 9. The remaining 5 (SESSION5_REUSABLE_TASK_TEMPLATES, TASK_TEMPLATE, GATE_PACKET_TEMPLATE, GPT_SESSION_LOG_TEMPLATE, ROADMAP_SECTION_TEMPLATE) are genuinely private orchestration templates.

**Resolution:** Correction accepted. 16 templates are already public. 5 workflow templates correctly remain private.

### Claim: README_INTERNAL.md should be trimmed

**Task 09 finding:** README_INTERNAL.md is long with duplication.
**Historical fact:** Session 10 reached the same conclusion with detailed analysis (55% duplicated public content, 16% stale handoff, 16% outdated baseline).

**Resolution:** The recommendation is sound. Session 10's pruning plan should be used as the reference.

---

## 6. Migration Reconciliation

### Plans already executed

| Plan | Session | Status |
|---|---|---|
| Template promotion (16 files to public templates/) | S9 | Already done |
| _internal/ as private Git repo with hooks | Pre-1 | Already done |
| .gitignore + visibility fixes | Pre-1 | Already done |
| Inbox/outbox convention | S3 | Already done |

### Plans not yet executed

| Plan | Session | Priority | Notes |
|---|---|---|---|
| Trim README_INTERNAL.md | S10 | Medium | 55% duplication with public docs; plan exists in S10 outbox |
| Level 2 cleanup (move agent-reports/prompts/logs under _internal/) | S9 | Low | Would declutter public tree; not urgent |
| Legacy internal/ migration + removal | GIT_WORKFLOW.md | Low | Old internal/ dir still exists; content already migrated |
| Evidence card relocation | S10 | Low | To _internal/evidence/cards/ |

### Plans that should NOT be executed

| Plan | Reason |
|---|---|
| Re-promote DB templates | Already promoted in S9 — re-executing would duplicate |
| Create a new RESIDENCY.md | Concepts already owned by 4 existing docs |
| Move _internal/ outbox to public | Outbox contains session artifacts that are correctly private |

---

## 7. Recommendations

### What _internal/ should be

_internal/ is the **private orchestration workspace** for GPT-orchestrated sessions. It is not:
- A public template library (templates are already in public templates/)
- A general engineering standards repository (standards belong in docs/)
- A VPS-resident directory (it never enters VPS residency)

### Immediate actions (from deferred Session 10 plans)

1. **Trim README_INTERNAL.md** — remove sections duplicating public authority docs per Session 10's pruning plan. Keep: purpose, directory structure, safety rules, deletion incident. Remove: program charter (in OPERATING_MODEL.md), per-repo baselines (in CONTROL.md and PORTFOLIO_BASELINE.md), agent role definitions (in AGENTS.md and work-ownership table).

2. **Clean up _internal/templates/ duplicates** — remove the 16 stale template copies that now live in public templates/. Keep the 5 workflow-internal templates (SESSION5_REUSABLE_TASK_TEMPLATES, TASK_TEMPLATE, GATE_PACKET_TEMPLATE, GPT_SESSION_LOG_TEMPLATE, ROADMAP_SECTION_TEMPLATE).

### What to leave unchanged

- inbox/outbox/logs — correctly private
- vps-inventory-and-runbook.md — correctly private (contains SSH/auth details)
- GPT_ORCHESTRATED_WORKFLOW.md — correctly private (workflow internals)
- generated/ — correctly private (dashboard output)
- evidence/ — correctly private (operational evidence cards)

### Nothing new to create

No new documents, no new directories, no new authority rules. The historical intent is already well-documented. The only missing step is executing deferred cleanup from Sessions 9 and 10.
