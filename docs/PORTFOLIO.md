# Portfolio View

**Status:** Human portfolio working view — Buddy's all-project surface for thinking, notes,
priorities, goals, direction, and decisions.

**Last reconciliation:** 2026-07-25

## Document Authority

| Content | Authority |
|---|---|
| Buddy's goals, priorities, direction, explicit decisions | **Human portfolio authority** — recorded here |
| Informal notes, ideas, questions | **Working input** — not automatic approval |
| Repository lifecycle, support state, permissions, blockers, approved SHA, operational boundaries | **`repos/<repo>/CONTROL.md`** — always authoritative |
| Detailed gate evidence | **`repos/<repo>/RELEASE_GATES.md`** |
| Portfolio execution sequencing | **`ROADMAP.md`** |
| Historical execution evidence | **Task reports and journals** (`_internal/outbox/`, `_internal/logs/`) |
| Generated aggregate status | **Derived orientation only** (`tools/show_portfolio_status.sh`, `tools/portfolio_registry.py`) |

**A note in this document does not silently override `CONTROL.md`.** If a note here
conflicts with a repository control record, the control record governs until the
conflict is reconciled. See §Reconciliation Workflow.

**Human notes are preserved — agents must not overwrite Buddy's written notes.**
Agents may populate project state from CONTROL.md data but must not delete or
modify text Buddy has written in the notes sections. Derived state (project
summaries, priority lists) may be refreshed from canonical sources when the
document explicitly labels them as derived.

---

## Portfolio Command View

Quick-scan table for the human operator. Fields sourced from `CONTROL.md`,
`ROADMAP.md`, and this document's per-repo entries.

| Repository | Intent | Desired outcome | State | Priority | Blocker | Human decision | Hermes next action | Executor |
|---|---|---|---|---|---|---|---|---|
| ivy-control-vps | Portfolio control plane | Reliable Hermes-centered orchestration | Admitted (Gate 3) | — | None | Next trial objective | Prove delegation cycle | OpenCode |
| palworld-kb | Capability prototype | Clean published baseline | Source-only (Gate 3) | P4 | None pending | PR #2 merge | Post-merge governance | OpenCode |
| reddit-ops | Data pipeline | Canonical collection | Production (Gate 5) | P1 | Credential commit e4acae0 | Clean publication strategy | Inspect/report only | Codex |
| traderie | Data pipeline | Focused pc_hc_nl recovery | Production (Gate 5) | P3 | pc_hc_nl timeout | Recovery approach | Inspect/report only | Codex |
| idlehacking-kb | Knowledge system | Acknowledged, replayable capture | Browser-dep. | P2 | Privacy/publication | IH ownership disposition | Inspect/report only | — |
| ih-market-companion | Knowledge system | Acknowledged, replayable capture | Browser-dep. (Gate 2) | P2 | Userscript authority | Userscript source decision | Inspect/report only | — |
| sjc-intel | Source-only | Remote configured | Source-only (Gate 2) | Low | No remote | Remote establishment plan | Inspect/report only | — |
| wgu-catalog | Batch process | Version/manifest procedure | Batch | Low | Procedure design | Admission path | Inspect/report only | — |
| wgu-atlas | Downstream | Boundary resolved | Downstream | Low | Boundary gates | Admission path | Inspect/report only | — |
| bsda-courses | Downstream | Path, remote, boundary resolved | Downstream | Low | All unknown | Source discovery | Inspect/report only | — |
| reckless-ben | Restricted | Preserve restricted | Restricted | — | NO_LAUNCH | None needed | None | — |

## Portfolio Purpose and Desired Direction

*Ivy Control VPS is the portfolio control plane for governing and improving a collection
of independent engineering assets through shared standards, evidence-based operations,
Git workflows, and bounded human/agent collaboration.*

---

## Current Priorities

*Buddy: adjust these priorities freely. Derived from ROADMAP.md and CONTROL.md
at last reconciliation. Agents may refresh this list but must not overwrite
Buddy's edited version.*

- P0: Uncertainty creates loss — protect irreplaceable data, collection continuity, recovery confidence
- P1: Reddit Ops canonicality review toward Buddy gate decision
- P2: Idle Hacking durability (chat + market acknowledgement, archive continuity)
- P3: Traderie bounded recovery (`pc_hc_nl` timeout investigation)
- P4: Palworld KB post-merge governance assessment
- P5: Missing dashboard adapters

---

## Near-Term Sequence

1. Post-merge governance assessment for Palworld KB
2. Reddit Ops canonicality review progress
3. Idle Hacking ownership and acknowledgement resolution
4. Traderie `pc_hc_nl` recovery
5. Dashboard adapter completion

---

## Portfolio-Wide Notes

*Free-form space for Buddy's portfolio-level thoughts.*

```

```

---

## Portfolio-Wide Decisions

| # | Decision | Date | Status |
|---|---|---|---|
| 1 | Palworld KB publication branch-to-PR pilot completed | 2026-07-25 | Complete |
| 2 | Git Steward MVP implemented with three-gate model | 2026-07-25 | Complete |
| 3 | Remaining decisions deferred to individual repo control records | — | Pending |

---

## Cross-Repository Dependencies

| Dependency | Affects | Status |
|---|---|---|
| Reddit Ops clean publication (credential-bearing commit `e4acae0`) | reddit-ops | Blocked — Buddy decision needed |
| Idle Hacking ownership/acknowledgement resolution | idlehacking-kb, ih-market-companion | Blocked — Buddy decision needed |
| BSDA Courses source path resolution | bsda-courses | Unknown — needs discovery |

---

## Human Decisions Queue

| # | Decision | Needed by | Priority |
|---|---|---|---|
| 1 | Reddit Ops clean Git publication strategy | Buddy | High |
| 2 | Canonical Idle Hacking userscript source and duplicate disposition | Buddy | High |
| 3 | Chat/market archive acknowledgement destination and authority | Buddy | Medium |
| 4 | Palworld KB VPS source-only clone timing | Buddy | Low |
| 5 | STS Workbench managed-repository admission timing | Buddy | Low |

---

## Work That May Proceed Without Buddy

- Git Steward maintenance and test improvements
- Internal documentation updates aligned with existing authority
- Read-only inspection and evidence collection
- Repository control record updates authorized by existing gates

---

## Paused or Deferred Work

| Work | Reason |
|---|---|
| WGU Atlas publication | Blocked by upstream boundaries and LLM configuration |
| BSDA Courses admission | Source path unresolved |
| Reckless Ben | NO_LAUNCH — restricted |
| Idle Hacker consolidation | Deferred — not yet scoped |

---

## Portfolio Health Snapshot

*Derived snapshot from last reconciliation. Not live operational evidence.*
*See `tools/show_portfolio_status.sh` and `tools/ingestion_dashboard.py` for current state.*

| Dimension | State |
|---|---|
| Control plane version | `main` @ `12ca8c2` (merged `feat/git-steward-mvp-integration`) |
| Managed repositories | 11 (5 operational, 3 source-only, 2 downstream, 1 restricted) |
| Palworld publication pilot | PR #1 merged — `publish/baseline-v1` -> `main` |
| Git Steward tests | 53/53 passing |
| Main branch protection | NONE (all repos) |
| Hermes scope | Read-only / artifact-only orchestration defined |

---

## Reconciliation Workflow

When Buddy writes a note in this document that may affect repository authority:

1. **Identify** the changed notes (orchestrator or GPT compares with prior state)
2. **Inspect** relevant `CONTROL.md`, evidence, and roadmap sections
3. **Classify** each note:

   | Classification | Meaning |
   |---|---|
   | `TENTATIVE_NOTE` | Idea or question — no action required |
   | `PORTFOLIO_PRIORITY` | Affects sequencing — may update `ROADMAP.md` |
    | `REPOSITORY_DIRECTION_CANDIDATE` | Suggests repo direction — prepare CONTROL.md update |
   | `CONTROL_UPDATE_CANDIDATE` | Alters lifecycle, gates, blockers, or authorized work |
   | `ROADMAP_UPDATE_CANDIDATE` | Alters portfolio sequencing or active initiatives |
   | `BOUNDED_TASK_CANDIDATE` | Clear enough for a bounded task packet |
   | `HUMAN_DECISION_REQUIRED` | Requires Buddy's explicit decision before action |
   | `RECONCILED` | Processed — note is reflected in canonical documents |
   | `REJECTED_WITH_REASON` | Reviewed but not adopted — reason recorded |

4. **Propose** exact canonical updates or bounded tasks
5. **Apply** only changes authorized by the task and existing approval boundaries
6. **Record** reconciliation status in the notes section or a separate reconciliation log
7. **Escalate** publication, production, privacy, destructive, permission, or architectural changes

**How notes are preserved:** Buddy's original wording is retained in this document.
Agents must never overwrite Buddy-written text in the Notes sections. Agents may
append derived state or refresh project summaries from CONTROL.md only when
those sections are not written by Buddy. Reconciled notes carry a
`RECONCILED → <destination> <date>` annotation.

**How derived state is refreshed:** Generated views (status tool, registry) re-read
CONTROL.md and evidence — they do not read this document for operational state.

---

## Known Projects

---

### ivy-control-vps

**Purpose:** Portfolio control plane for governing and improving a collection of
independent engineering assets through shared standards, evidence-based operations,
Git workflows, and bounded human/agent collaboration.

**Current state:** Admitted (Gate 3). `feat/git-steward-mvp-integration` merged to `main` at
`12ca8c2`. Git Steward MVP at 53 tests. Post-merge validation passes.

**Priority:** N/A (this is the control plane)
**What Buddy wants next:** First bounded artifact-only pilot through complete
packet → delegate → report → review cycle.

**Notes:**

```

```

**Last reconciliation:** 2026-07-25

---

### palworld-kb

**Purpose:** Provenance-backed Palworld gameplay knowledge base with human-gated
canonical promotion.

**Current state:** Source-only. PR #1 merged (`publish/baseline-v1` to `main`).
Clean governed baseline established.

**Priority:** Medium — pilot completed. Next: governance assessment, VPS clone timing.

**What Buddy wants next:** Post-merge governance assessment. Source-only VPS clone
timing decision.

**Notes:**

```

```

**Last reconciliation:** 2026-07-25

---

### reddit-ops

**Purpose:** WGU Reddit PostgreSQL collector and corpus operations workload.

**Current state:** Production-runtime (Gate 5). Git publication blocked by
credential-bearing commit `e4acae0` in local history.

**Priority:** High — canonicality review and clean publication strategy needed.

**What Buddy wants next:** Buddy decides clean Git publication strategy. Monitor-role
canonicality query design. Exact-SHA deployment, drift detection, reboot recovery proof.

**Notes:**

```

```

**Last reconciliation:** 2026-07-25

---

### traderie

**Purpose:** Diablo II market-data pipeline for transparent, segment-separated
completed-trade analysis.

**Current state:** Production-runtime (Gate 5). First natural scheduled generation
partially failed — `pc_hc_nl` segment timed out at 480s bound.

**Priority:** Medium — bounded recovery. No architecture reopening.

**What Buddy wants next:** `pc_hc_nl` timeout investigation. Verify DB/file health
behavior. Refine backup freshness policy. Prove bounded + natural scheduled generation.

**Notes:**

```

```

**Last reconciliation:** 2026-07-25

---

### idlehacking-kb

**Purpose:** Idle Hacking knowledge base — chat archive, market metadata, userscript
source, and LLM/agent framework.

**Current state:** Browser-dependent. Privacy/publication and userscript authority
gating unresolved. IH ownership and acknowledgement decisions needed from Buddy.

**Priority:** Medium — gated on ownership decision.

**What Buddy wants next:** Buddy decides IH ownership/acknowledgement destination.
Resolve privacy/publication gates. Resolve canonical userscript source.

**Notes:**

```

```

**Last reconciliation:** 2026-07-25

---

### ih-market-companion

**Purpose:** Public market site, VPS/cloud collector, market publishing, health checks,
and ecosystem docs for IdleHacker.

**Current state:** Browser-dependent. Userscript source authority unresolved (pending
Buddy decision). Health `deployed_revision` cannot be populated.

**Priority:** Medium — gated on ownership decision.

**What Buddy wants next:** Buddy decides canonical userscript source. Implement tracked
canonical path. Resolve acknowledgement destination/archive authority. Prepare idempotent
PostgreSQL import pilot. Source-only VPS clone.

**Notes:**

```

```

**Last reconciliation:** 2026-07-25

---

### sjc-intel

**Purpose:** AI-assisted local intelligence/reporting for St. Johns County, Florida.

**Current state:** Source-only. No remote configured for local checkout.

**Priority:** Low — needs publication-readiness review.

**What Buddy wants next:** Establish canonical remote and publication-readiness review.
Prepare Gate 4 readiness packet.

**Notes:**

```

```

**Last reconciliation:** 2026-07-25

---

### wgu-atlas

**Purpose:** WGU Atlas — downstream LLM consumer for WGU program lineage and course analysis.

**Current state:** Downstream. Boundary, configuration/cost, and source-path remediation needed.

**Priority:** Deferred — blocked by upstream boundaries.

**What Buddy wants next:** Resolve boundary gates and LLM cost/configuration. Prepare
Gate 1 admission packet.

**Notes:**

```

```

**Last reconciliation:** 2026-07-25

---

### wgu-catalog

**Purpose:** WGU academic catalog data — canonical degree program, course, and requirement
definitions.

**Current state:** Batch. Not yet admitted — needs source/version/manifest/retention procedure.

**Priority:** Low — not yet admitted.

**What Buddy wants next:** Source/version/manifest/retention procedure. Gate 1 admission
packet. Footprint review. Source-only VPS clone.

**Notes:**

```

```

**Last reconciliation:** 2026-07-25

---

### bsda-courses

**Purpose:** BSDA course data — program definitions, course lineage, and comparison
artifacts for WGU BSDA degree.

**Current state:** Downstream. Local path not found at expected location. Boundary,
configuration/cost, and source-path remediation needed.

**Priority:** Deferred — source path unresolved.

**What Buddy wants next:** Resolve source path and remote. Prepare Gate 1 admission packet.

**Notes:**

```

```

**Last reconciliation:** 2026-07-25

---

### reckless-ben

**Purpose:** Preserved `NO_LAUNCH` asset with approval-governance value.

**Current state:** Restricted — `NO_LAUNCH`. No admission work authorized.

**Priority:** None — restricted.

**What Buddy wants next:** No admission work. Preserve restricted status.

**Notes:**

```

```

**Last reconciliation:** 2026-07-25

---

## Hermes Orchestration Readiness

| Capability | State |
|---|---|
| Mode 0 artifact-only orchestration defined | ✅ Documented in `agents/VPS_ORCHESTRATION.md` and `agents/HERMES_AGENT_CONTRACT.md` |
| Hermes required to delegate to OpenCode for substantial implementation | ✅ Documented in `docs/OPERATING_MODEL.md` |
| OpenCode as preferred execution agent | ✅ Documented in `docs/OPERATING_MODEL.md` |
| Three-gate model (Git Steward) | ✅ Implemented and tested (53 tests) |
| Palworld pilot completed (branch-to-PR-to-merge) | ✅ Done |
| Hermes-first multi-repository pilot | ❌ Not yet attempted |
| Multi-task or multi-repo delegation envelope | ❌ Not yet designed |
| Hermes-per-repo credential model | ❌ Not yet configured |
| Hermes PR/branch authority | ❌ Requires per-repo Buddy approval |
| Cross-repository Hermes orchestration | ❌ Not yet attempted |
