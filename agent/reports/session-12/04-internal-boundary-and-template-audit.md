# Session 12 — Task 09: Internal Artifact Boundary and Template Audit

**Date:** 2026-07-20
**Status:** COMPLETED — analysis only, no files modified

---

## 1. Executive Summary

`_internal/` serves **three distinct roles** that are not currently separated: private orchestration workspace, reusable engineering template library, and session artifact archive. The residency boundary (`_internal/` never enters VPS) is correct and well-documented. The templates require attention — 14 of 21 are reusable portfolio standards that would benefit from public documentation but are currently invisible in the private tree.

| Category | Artifacts | Verdict |
|---|---|---|
| Private orchestration | README_INTERNAL.md, GPT_ORCHESTRATED_WORKFLOW.md, inbox/tasks/logs/outbox | ✅ Correctly private — stay in `_internal/` |
| Reusable engineering templates | 14 DB_* templates, CONTROL_TEMPLATE.md | ⚠️ Public documentation candidates — consider promoting |
| Workflow templates | TASK_TEMPLATE, GATE_PACKET, GPT_SESSION_LOG, ROADMAP_SECTION, SESSION5_REUSABLE | ✅ Stay private — workflow-internal |
| Private evidence | vps-archives/, deep-research/, rollback/ | ✅ Correctly private |
| Generated output | generated/ | ✅ Correctly private — dashboard output |
| VPS inventory | vps-inventory-and-runbook.md | ✅ Correctly private — contains SSH/auth details |

---

## 2. `_internal/` Purpose Definition

**Current state:** `_internal/` is a combination of three concepts that share a directory but serve different roles:

### Role A: Private GPT orchestration workspace

| Content | Purpose |
|---|---|
| `README_INTERNAL.md` | Strategic context, program charter, agent roles, safety rules |
| `GPT_ORCHESTRATED_WORKFLOW.md` | Private workflow definition for GPT-orchestrated sessions |
| `inbox/` | Task prompts from Buddy/GPT to agents |
| `tasks/` | Historical ad-hoc task definitions (T1-T5) |
| `outbox/` | Result reports, gate packets, session artifacts |
| `logs/` | Agent execution logs, GPT session logs |

**Verdict:** Correctly private. These expose GPT orchestration mechanics, private decisions, and session continuity that would confuse public readers.

### Role B: Reusable engineering template library

| Content | Purpose |
|---|---|
| `templates/DB_*.md` (14 files) | PostgreSQL naming, migration, backup, restore, health registration, importer contracts, rollback packets |
| `templates/CONTROL_TEMPLATE.md` | CONTROL.md YAML front matter template |

**Verdict:** These are **portfolio engineering standards**, not private orchestration notes. They describe PostgreSQL conventions that any managed repo should follow. They are currently invisible to public consumers.

### Role C: Session artifact archive

| Content | Purpose |
|---|---|
| `outbox/session-*/` (10+ session directories) | Historical result reports |
| `outbox/hermes-vps/` | Hermes-related evidence |
| `logs/sessions/GPT-*.md` | GPT session continuity logs |
| `logs/agents/YYYY-MM-DD/` | Agent execution chronology |
| `generated/` | Dashboard HTML/JSON output |
| `vps-archives/` | Historical VPS audit material |
| `deep-research/` | Unreviewed research output |
| `rollback/` | Rollback recovery material |

**Verdict:** Correctly private. Session artifacts reference decisions, reasoning, and evidence that belong in the private history.

---

## 3. Residency Boundary Analysis

### Current rule

`_internal/` must not enter VPS residency. This rule is documented in:

| Document | Reference |
|---|---|
| `docs/GIT_WORKFLOW.md` §VPS engineering-workspace readiness | "Confirm `_internal/` is ignored and absent" |
| `docs/GIT_WORKFLOW.md` §Principles | "`_internal/` is excluded via `.gitignore`" |
| `_internal/README_INTERNAL.md` §Public/private boundary | "`_internal/` must not be pushed to the public GitHub repository" |
| `repos/ivy-control-vps/CONTROL.md` | `codex_stops` includes "Do not transfer _internal, credentials, private evidence, or raw agent material to the VPS checkout" |

### Assessment

**The boundary is correctly defined and sufficiently enforced.** Four separate documents assert it. The `codex_stops` in the CONTROL.md provides an agent-enforceable rule. No new documentation is needed.

### Recommended addition

Add a single sentence to `docs/README.md` core reading path or authority model section:

> `_internal/` is the private orchestration workspace. It never enters VPS residency. See `docs/GIT_WORKFLOW.md` §VPS engineering-workspace readiness.

This makes the rule discoverable from the documentation index without requiring a reader to know which specific document owns it.

---

## 4. Full Artifact Classification Table

### Root files

| Artifact | Purpose | Role | Classification | Recommendation |
|---|---|---|---|---|
| `README_INTERNAL.md` | Strategic context, program charter, agent roles, safety rules, session continuity | Private operating overview | Private orchestration | ✅ Keep private |
| `GPT_ORCHESTRATED_WORKFLOW.md` | Detailed private workflow for GPT-orchestrated sessions | Private workflow authority | Private orchestration | ✅ Keep private |
| `vps-inventory-and-runbook.md` | SSH config, host identity, workloads, interaction modes, protected data | Private operations runbook | Private orchestration | ✅ Keep private (contains SSH host key, IP, auth details) |

### Directories

| Directory | Contents | Classification | Recommendation |
|---|---|---|---|
| `inbox/` | Task prompts from Buddy/GPT | Private orchestration | ✅ Keep private |
| `tasks/` | Historical ad-hoc task definitions | Private orchestration | ✅ Keep private |
| `outbox/` | Session result reports, gate packets | Session artifact archive | ✅ Keep private |
| `logs/` | Agent execution logs, GPT session logs | Session artifact archive | ✅ Keep private |
| `generated/` | Dashboard JSON/HTML output | Session artifact archive | ✅ Keep private |
| `evidence/` | Evidence cards | Session artifact archive | ✅ Keep private |
| `vps-archives/` | Historical VPS audit material | Historical record | ✅ Keep private |
| `deep-research/` | Unreviewed research output | Temporary/experimental | ✅ Keep private |
| `rollback/` | Rollback recovery material | Historical record | ✅ Keep private |

### Templates

| Template | Purpose | Classification | Recommendation |
|---|---|---|---|
| `CONTROL_TEMPLATE.md` | CONTROL.md YAML schema template | Reusable engineering template | ⚠️ **Promote to public** — already partially documented in `docs/REPOSITORY_CONTROL_MODEL.md`; could point there |
| `DB_BACKUP_MANIFEST_TEMPLATE.md` | Backup manifest schema | Reusable engineering template | ⚠️ **Public documentation candidate** — portfolio engineering standard |
| `DB_CLEANUP_RETENTION_CRITERIA_TEMPLATE.md` | Cleanup/retention criteria | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_EVIDENCE_BUNDLE_INDEX_TEMPLATE.md` | Evidence bundle index | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_HEALTH_REGISTRATION_TEMPLATE.md` | Health producer registration | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_IMPORTER_CONTRACT.md` | Read-only import contract | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_MIGRATION_PACKET_TEMPLATE.md` | Migration execution packet | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_NAMING_REFERENCE.md` | Database naming conventions | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_NATURAL_RUN_PROOF_TEMPLATE.md` | Natural-run evidence | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_ONBOARDING_MANIFEST_TEMPLATE.md` | PostgreSQL onboarding manifest | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_PILOT_GATE_TEMPLATE.md` | Pilot gate criteria | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_PRIVILEGE_MATRIX_TEMPLATE.md` | PostgreSQL role permissions | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_RECONCILIATION_PACKET_TEMPLATE.md` | Data reconciliation template | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_RESTORE_CHECKLIST.md` | Isolated restore procedure | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_ROLE_APPLICABILITY_TABLE.md` | Conditional role requirements | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `DB_ROLLBACK_PACKET_TEMPLATE.md` | Rollback execution packet | Reusable engineering template | ⚠️ **Public documentation candidate** |
| `GATE_PACKET_TEMPLATE.md` | Gate packet structure | Workflow template | ✅ Keep private — workflow-internal |
| `GPT_SESSION_LOG_TEMPLATE.md` | GPT session log format | Workflow template | ✅ Keep private — workflow-internal |
| `ROADMAP_SECTION_TEMPLATE.md` | ROADMAP section template | Workflow template | ✅ Keep private — workflow-internal |
| `SESSION5_REUSABLE_TASK_TEMPLATES.md` | Session 5 task templates | Historical/temporary | ✅ Keep private — session-specific |
| `TASK_TEMPLATE.md` | Task definition structure | Workflow template | ✅ Keep private — workflow-internal |

---

## 5. Template Recommendations

### DB template cluster (14 files)

**Recommendation: Promote to public reference directory.**

These templates are not private orchestration notes. They are:
- PostgreSQL naming conventions (`DB_NAMING_REFERENCE.md`)
- Migration procedures (`DB_MIGRATION_PACKET_TEMPLATE.md`, `DB_ROLLBACK_PACKET_TEMPLATE.md`)
- Backup/restore standards (`DB_BACKUP_MANIFEST_TEMPLATE.md`, `DB_RESTORE_CHECKLIST.md`)
- Health registration patterns (`DB_HEALTH_REGISTRATION_TEMPLATE.md`)
- Onboarding checklists (`DB_ONBOARDING_MANIFEST_TEMPLATE.md`)

These are the same type of content as `docs/PORTFOLIO_CONVENTIONS.md` — durable engineering conventions that any repository following the portfolio model would benefit from.

**Proposed location:** `templates/database/` under the public repo root, or add to `docs/` as a `docs/templates/` directory. The templates reference private workflow mechanics (e.g., "Strong Codex executes this packet") which must be sanitized before promotion.

**Precondition:** Before promotion, each template must be reviewed for:
1. References to `_internal/` paths → remove or generalize
2. References to "GPT", "OpenCode", "Strong Codex" agent roles → generalize to "operator" or "engineer"
3. References to private workflow steps → remove
4. References to specific session numbers → remove

### Control template

`CONTROL_TEMPLATE.md` duplicates the schema already documented in `docs/REPOSITORY_CONTROL_MODEL.md`. The public schema is more current. The template can be kept as a private convenience copy or replaced with a redirect to the public schema.

**Recommendation:** Update `CONTROL_TEMPLATE.md` to reference the public schema in `docs/REPOSITORY_CONTROL_MODEL.md` rather than duplicating it.

### Workflow templates (5 files)

`TASK_TEMPLATE.md`, `GATE_PACKET_TEMPLATE.md`, `GPT_SESSION_LOG_TEMPLATE.md`, `ROADMAP_SECTION_TEMPLATE.md`, `SESSION5_REUSABLE_TASK_TEMPLATES.md`

These define the internal GPT orchestration workflow. They expose agent delegation patterns, private role definitions, and session mechanics that should remain private.

**Recommendation:** ✅ Keep private. These are correctly placed in `_internal/`.

---

## 6. README_INTERNAL Assessment

| Criterion | Assessment |
|---|---|
| Defines purpose? | ✅ Yes — "private operating context for IvyControlVPS" |
| Defines ownership? | ⚠️ Partially — describes agent roles but not who maintains the file |
| Defines residency exclusion? | ✅ Yes — "must not be pushed to the public GitHub repository" |
| Defines lifecycle? | ❌ No — no lifecycle policy for _internal/ content |
| Defines allowed contents? | ✅ Yes — list of 10 allowed categories |
| Defines prohibited contents? | ✅ Yes — secrets must not be stored here |
| Length | ⚠️ ~1200 lines — very long for a README |

**Assessment:** README_INTERNAL.md is comprehensive but has grown to include historical program charter material, detailed agent role definitions, and session-level operating procedures that are also documented in GPT_ORCHESTRATED_WORKFLOW.md. There is duplication between the two files.

**Recommendation:** Trim README_INTERNAL.md to focus on:
1. What `_internal/` is (purpose and boundary)
2. Directory structure overview
3. Allowed and prohibited contents
4. VPS residency exclusion rule
5. Critical safety rules (deletion incident)
6. Links to detailed references (GPT_ORCHESTRATED_WORKFLOW.md, AGENTS.md, etc.)

Move the detailed program charter, agent role definitions, and per-repository status to GPT_ORCHESTRATED_WORKFLOW.md or retire them as historical.

---

## 7. Public/Private Split Recommendation

### Recommended boundary

```
Public (tracked in Git, safe for VPS residency)
  ├── docs/                                  ← canonical authority
  ├── repos/<repo>/CONTROL.md               ← per-repo governance
  ├── tools/                                 ← operational tooling
  └── templates/database/                    ← *proposed* reusable standards

_internal/ (private, never enters VPS)
  ├── README_INTERNAL.md                     ← trimmed overview + safety rules
  ├── GPT_ORCHESTRATED_WORKFLOW.md           ← private workflow
  ├── inbox/                                 ← task prompts
  ├── tasks/                                 ← historical tasks
  ├── outbox/                                ← session results
  ├── logs/                                  ← execution chronology
  ├── generated/                             ← dashboard output
  ├── templates/                             ← workflow templates (5)
  │   (DB_* templates → moved to public)
  └── vps-inventory-and-runbook.md           ← SSH/auth details
```

### Key change

Move 14 DB_* templates and CONTROL_TEMPLATE.md patterns to a public location after sanitization. This is the only actionable change — everything else is correctly placed.

---

## 8. Follow-up Implementation Tasks

| Task | Priority | Notes |
|---|---|---|
| Sanitize and promote 14 DB templates to public `templates/database/` | Medium | Remove _internal/ references, agent role names, session numbers. Each template is 20-80 lines — low effort. |
| Update CONTROL_TEMPLATE.md to reference public schema | Low | Replace content with redirect to `docs/REPOSITORY_CONTROL_MODEL.md` |
| Add VPS residency rule to docs/README.md | Low | Single sentence under authority model |
| Trim README_INTERNAL.md | Low | Remove program charter duplication, keep boundary + safety rules |
| Leave everything else in `_internal/` | — | Correctly placed |
