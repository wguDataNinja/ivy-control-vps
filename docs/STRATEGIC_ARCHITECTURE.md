# Strategic Architecture

**Status:** ACTIVE — records architectural decisions, portfolio thesis, and sequencing rationale established during Session 12.
**Supersedes:** Does not replace ROADMAP.md, OPERATING_MODEL.md, PORTFOLIO_INTENT.md, or per-repo CONTROL.md records.
**Amendment:** Update only when an architectural decision is changed or a new phase is entered. Do not add transient task status.
**Evidence labels:** DECIDED (GPT+Buddy approved), PROPOSED (accepted direction not yet implemented), VERIFIED (confirmed from repository evidence), DOCUMENTED_BUT_UNVERIFIED (stated in docs but not live-verified), DEFERRED (intentionally postponed).

---

## 1. Purpose and Authority

This document records the architectural decisions, portfolio thesis, and execution sequencing established during Session 12. It exists so a future engineer or agent can understand why the portfolio is structured as it is and why work is sequenced in a particular order, without reading Session 12 chat history.

It is not a task queue, a roadmap, or an operating model. Those roles belong to TODO.md, ROADMAP.md, and docs/OPERATING_MODEL.md respectively.

The authoritative input sources are:
- `_internal/inbox/session-12/99-strategic-alignment-report.md` — strategic direction (DECIDED)
- `_internal/outbox/session-12/99-strategic-response-from-repository-evidence.md` — repository-grounded response (VERIFIED)
- `_internal/outbox/session-12/100-strong-codex-architecture-reconciliation.md` — Codex reconciliation (PROPOSED/DECIDED)
- `_internal/outbox/session-12/32-portfolio-repository-discovery-and-vps-pr-readiness.md` — discovery evidence (VERIFIED)

---

## 2. Paramount User Goals

DECIDED. The portfolio is governed by these goals:

1. Build useful provider-independent knowledge systems.
2. Make Idle Hacker the eventual flagship product.
3. Demonstrate employable capability in data engineering, knowledge architecture, AI systems, and operations.
4. Reach approximately 90% autonomous execution while retaining human authority over direction, spending, merge, deployment, publication, and destructive actions.
5. Turn the VPS into a safe and productive engineering environment, not merely a production host.
6. Make autonomous work bounded, reviewable, testable, and reversible.
7. Spend strong paid-model capacity deliberately.
8. Prove the workflow first with a small, safe repository before scaling it.

**Decision test:** Does this work materially advance a provider-independent flagship product, a credible engineering portfolio, or a safe autonomous engineering loop? Work that does not support one of those outcomes should normally be deferred.

---

## 3. Portfolio Thesis

DECIDED. The portfolio is not a collection of unrelated projects. It is a coherent body of work centered on one professional capability:

> Building efficient, continuously updated, provider-independent knowledge systems and the autonomous engineering infrastructure required to maintain them.

Key principles (DECIDED):
- Structured records, schemas, databases, and provenance provide durable value.
- Retrieval logic, indexes, evaluations, domain contracts, and operational pipelines matter more than provider-specific assistant configurations.
- Provider independence means the system architecture does not collapse when a provider changes — not that every provider produces identical quality.
- Knowledge should not exist only inside ChatGPT threads, Claude projects, provider-specific assistants, proprietary context stores, undocumented embeddings, or giant prompts.

---

## 4. Repository and Product Roles

DECIDED. Repositories are classified by role, not only by maturity:

| Role | Repositories | Purpose in portfolio |
|------|-------------|---------------------|
| **Production services** | Traderie, Reddit Ops | Demonstrate data engineering, ETL, PostgreSQL, systemd, health monitoring, backup/restore, operational ownership |
| **Product development** | Palworld KB, STS Workbench, WGU Atlas, WGU Catalog, IH Assistant, SJC Intel | Primary targets for agent-driven branch-and-PR work |
| **Flagship ecosystem** | idlehacking-kb, ih-market-companion, IH Assistant, selected parts of idle-hacker | Long-term product destination; not yet ready for autonomous development |
| **Control plane** | ivy-control-vps | Portfolio orchestration, standards, governance, agent workflow |
| **Research / experimentation** | Hermes (local eval), open-code (eval), IVY-git, chive_gate, idle-hacker (research areas) | Exploration, not portfolio product |
| **Historical** | ivy-control | Superseded predecessor; preserved for lineage |
| **Personal / internal** | Portfolio, passport, private session archives | Not portfolio-facing |

---

## 5. Flagship Strategy

DECIDED. Idle Hacker is the eventual flagship product. It combines live market scraping, changing game mechanics, game knowledge, changelog ingestion, player state, AI assistance, and immediate real users.

The envisioned architecture has five services:
1. **Knowledge service** — canonical game concepts, mechanics, provenance, version boundaries
2. **Market ingestion service** — live collection, normalization, price history, freshness
3. **Player/session context service** — game-state extraction, inventory, session records
4. **Assistant interface** — queries, retrieval, provider abstraction, evidence presentation, UI
5. **Control and operations** — scheduling, health, backups, deployment, monitoring

**Why it is not the first autonomous pilot:** Idle Hacker currently has very large local data (139GB+), privacy and publication concerns, unresolved repository authority, browser and game dependencies, and multiple overlapping repositories with unclear ownership. It is the strategic destination, not the first branch-to-PR pilot.

---

## 6. Provider-Independence Principles

DECIDED. These principles are architectural requirements for knowledge-system repos:

1. **Structured before prompted** — normalize information before repeatedly inserting it into prompts.
2. **Provenance as a first-class field** — every important fact retains source, acquisition time, version, confidence, transformation history, and conflict state.
3. **Freshness is domain-specific** — market prices may need minute-level freshness; static reference facts may be durable.
4. **Version awareness** — the system must answer when a fact became true, whether it still applies, which game version it applies to, and whether later evidence superseded it.
5. **Retrieval should be bounded** — retrieve minimum relevant evidence, not entire archives.
6. **Model use should be deliberate** — use models for synthesis, ambiguity, inference, and explanation. Do not use models for exact joins, deterministic filtering, version comparison, or repository-state verification.
7. **Evaluation must exist outside the provider** — maintain tests and evaluation cases that can compare providers and model versions.

---

## 7. Autonomous Engineering Target

DECIDED. The target autonomy level is approximately 90%. This means agents perform most implementation labor. Buddy retains:
- priorities and strategic direction
- API-spend approval
- public/private decisions
- user-facing design judgment
- merge approval
- production deployment approval
- destructive authority
- final release judgment

Agents may eventually work unattended while Buddy is asleep or away, but always on isolated branches with deterministic gates and human review before merge.

---

## 8. Human Authority Boundaries

DECIDED. The following are reserved for human decision:

| Authority | Holder | Notes |
|-----------|--------|-------|
| Roadmap priority | Buddy | |
| Strategic direction | Buddy | |
| API spending | Buddy | Per-task budget may be delegated |
| Public/private boundaries | Buddy | Per-repository decisions |
| User-facing design | Buddy | |
| Merge approval | Buddy | |
| Production deployment | Buddy | Exact-SHA deployment |
| Destructive actions | Buddy | Cleanup, deletion, history rewrite |
| Publication | Buddy | Making repos/artifacts public |

Hermes may never merge, push directly to a protected default branch, change repository settings, change branch protections, deploy to production, publish private/sensitive repositories, approve destructive cleanup, or decide product direction.

---

## 9. First-Pilot Decision

DECIDED. Palworld KB is the first autonomous VPS branch-to-PR pilot.

Reasons (VERIFIED):
- ~3MB tracked source + 6.5MB .git = smallest footprint
- Public GitHub repository with deterministic pytest tests
- Linux-compatible CLI, no production database, no scheduler
- Direct relevance to knowledge-system architecture
- Existing cross-repository contract with STS Workbench
- Suitable for one-PR-sized tasks that change one behavior and add tests

**Constraint:** No implementation task should begin until the Palworld publication baseline and workflow authority are reconciled.

---

## 10. Palworld Baseline Principles

DECIDED. The 36 local commits ahead of origin/main contain substantial product work and must not be casually discarded or reset. They require a dedicated publication audit followed by a separately authorized baseline-construction task.

The work should distinguish:
- product source (publishable)
- tests (publishable)
- public provenance evidence (publishable with review)
- generated artifacts (review before publish)
- workflow documentation (publishable with review)
- agent reports (review before publish)
- private session logs (DO NOT PUBLISH)
- temporary working material (DO NOT PUBLISH)

Tracked `_internal` content must be classified by meaning, not by directory name alone. Public repository validation must not depend on private GPT transcripts or private session logs.

The current approved SHA remains `origin/main` (`004e9968135...`) until Buddy approves a reconciled baseline.

---

## 11. Git Steward Decision

DECIDED. A concrete predecessor implementation exists in the `ivy-control` repository (3 Python scripts + JSON schema + agent skill at `scripts/git_steward*.py`, `schemas/git_steward_commit.schema.json`, `skills/git_steward_agent.md`).

The immediate need is a minimum viable migration, not a greenfield design and not the full future eight-gate platform.

Before the first branch-to-PR pilot, the minimum Git Steward must enforce:
1. Current branch is not the protected default branch
2. Recorded base SHA is valid
3. Changed and staged paths remain within declared task scope
4. Candidate manifest equals staged manifest exactly
5. No undeclared files enter the commit
6. Residual dirty state is reported
7. Secret and large-file checks occur before public push

Commit validation and publication should remain separable operations. The `publish` command must not run before a successful `commit` result.

The predecessor code is approximately 50-60% reusable for the required safety layer (mechanics are reusable; mandatory gates are new). Effort estimate: ~6 hours.

---

## 12. Development versus Production Workspace Rule

DECIDED. Production checkouts are immutable deployment targets. Approved development workspaces must be created separately for isolated branch-based agent work.

Path convention:
- Production: `/home/scraper/apps/<repo>`
- Development: `/home/scraper/workspaces/agent-tasks/<repo>/<task-id>/repo`

The first pilot should use a clean development clone, not a worktree attached to a production checkout. An agent must never implement in the deployed production checkout.

---

## 13. Credential and PR Authority

DECIDED. For the first pilot, a fine-grained repository-scoped GitHub credential is acceptable.

It must allow:
- clone, fetch
- push non-default task branches
- create and update draft PRs
- comment
- read checks

It must not allow:
- merge
- direct default-branch push
- branch-protection administration
- repository administration
- secret administration
- repository deletion

Branch protection on `main` must reject direct pushes and require PR review before merge.

PR branch naming convention: `agent/<task-id>-<slug>`

Every agent PR must contain: task ID, task objective, base SHA, scope, files changed, acceptance criteria, tests run and results, known limitations, generated artifacts, model usage, Git Steward result, unresolved concerns, and deployment impact. The PR is the primary execution record.

---

## 14. Deferred Architecture

DEFERRED. Do not treat the following as prerequisites for the first pilot:

- A general eight-gate execution framework
- A resident fully autonomous Hermes service
- Multi-repository workspace scheduling
- Universal model-provider abstraction (partial implementations in idlehacking-kb and STS workbench exist but are not required for the pilot)
- STS domain-adapter extraction (Palworld is the only adapter needed initially)
- Automated deployment
- Idle Hacker repository restructuring
- Broad documentation consolidation (only authority corrections that prevent unsafe execution should happen before the pilot)
- Cross-repository autonomous implementation

These may enter later roadmap phases after the single-repository workflow is proven.

---

## 15. Execution Sequence

DECIDED. The intended sequence after Session 12 close:

**Phase A — Preconditions (Session 13)**
1. Verify actual VPS runtime facts (Hermes, OpenCode, Codex, credentials, disk, workspace paths)
2. Perform read-only Palworld publication audit (classify 36 commits)
3. Buddy approves pilot scope and Palworld baseline disposition
4. Buddy approves credential model

**Phase B — Baseline construction (separately authorized)**
5. Reconcile Palworld into one clean approved baseline branch/SHA
6. Update Palworld CONTROL.md and AGENTS.md for agent workflow
7. Create Palworld RELEASE_GATES.md

**Phase C — Minimum tooling (one-time build)**
8. Port Git Steward MVP to ivy-control-vps with mandatory gates
9. Add minimal task/result/quota/PR contract fields to existing templates
10. Create PR template for pilot repository
11. Configure scoped GitHub credential and branch protection

**Phase D — First pilot execution**
12. Create clean VPS workspace clone
13. Execute bounded Palworld implementation task (CLI compatibility regression recommended)
14. Git Steward validates branch/base/scope/staging/security gates
15. Push task branch and open draft PR
16. Stop for human review

**Phase E — After successful pilot**
17. Review pilot evidence
18. Update operating documents from proven behavior
19. Admit or complete admission of STS Workbench as managed repository
20. Extend workspace management and deterministic gates
21. Prepare cross-repository Palworld-to-STS work

---

## 16. Decision Test for Future Roadmap Work

DECIDED. When evaluating proposed work, ask:

> Does this materially advance a provider-independent flagship product, a credible engineering portfolio, or a safe autonomous engineering loop?

Work that does not support one of those outcomes should normally be deferred.

---

## 17. Supersession and Amendment Policy

This document records decisions reached during Session 12. It may be amended when:
- A new architectural decision is made in a later session
- A decision recorded here is overturned by new evidence or changed priorities
- A deferred item becomes active

Amendments should note the session and date that changed the decision. Superseded decisions should be struck through or marked REPLACED with a reference to the replacement.
