# Hermes Roadmap Sufficiency Gate v1

**Status:** Current authority. Defines the pre-delegation evaluation Hermes
performs before orchestrating implementation work.

**Parent document:** `agents/HERMES_AGENT_CONTRACT.md` — this gate is the
pre-delegation validation referenced in §3.5a.

**Purpose:** Answer one question before Hermes creates any task packet or
delegates any work:

> Is this roadmap sufficiently clear that an execution agent can succeed by
> following instructions without performing architecture-level reasoning?

This gate is not an architectural review. It does not evaluate roadmap quality,
completeness, or strategic direction. It evaluates only whether the roadmap is
explicit enough for safe agent delegation.

---

## Evaluation Criteria

### 1. Objective clarity

**Question:** Is the desired end state explicit enough that an execution agent
can describe completion without interpretation?

**PASS if:**
- The chunk or phase goal is a single observable outcome
- Completion can be described in concrete terms
- An agent would not need to infer intent

**FAIL if:**
- The goal is abstract or multi-interpretation
- Hermes would need to choose between competing interpretations
- Success could be claimed for multiple different outcomes

### 2. Current state accuracy

**Question:** Does the roadmap reflect the actual repository state that an
execution agent would encounter?

**PASS if:**
- Current state matches observable repository condition
- Completed work is marked as done
- Known blockers are surfaced
- Stale or superseded information is clearly identified

**FAIL if:**
- The roadmap claims something is done when it is not
- Blockers are hidden or omitted
- The roadmap describes a state that no longer exists
- An execution agent would discover contradictory conditions

### 3. Scope clarity

**Question:** Are the execution boundaries clear enough that an agent knows
what to change and what to leave alone?

**PASS if:**
- Included changes are explicitly listed
- Excluded areas are explicitly listed
- Dangerous or prohibited areas are identified
- The chunk does not require the agent to decide scope

**FAIL if:**
- An agent would need to discover scope boundaries independently
- Exclusions are not documented
- Dangerous actions (production data, credentials, destructive ops) are
  not called out
- The chunk description invites scope expansion

### 4. Dependency clarity

**Question:** Are dependencies explicit enough that an agent can discover,
understand, and respect cross-boundary contracts?

**PASS if:**
- Required inputs (files, data, authority, services) are listed
- Cross-repository contracts are identified
- Blocked-by relationships are explicit
- Interfaces are stable or the migration plan is documented

**FAIL if:**
- An agent would need to discover architecture between repos
- Hidden dependencies could block mid-work
- Cross-project contracts are undocumented
- An agent would need to make assumptions about external systems

### 5. Acceptance criteria

**Question:** Is there a measurable definition of done that an agent can verify
independently?

**PASS if:**
- Acceptance criteria are concrete and testable
- Validation methods are specified
- Evidence can prove completion without subjective judgment
- The criteria distinguish done from not-done unambiguously

**FAIL if:**
- Completion is subjective or depends on reviewer preference
- Validation methods are not defined
- An agent would need to decide whether its own output is acceptable
- The criteria describe effort instead of outcome

### 6. Decision gates

**Question:** Are unresolved decisions surfaced so Hermes knows when to stop
and escalate rather than proceeding autonomously?

**PASS if:**
- Buddy decisions are identified
- Unresolved architecture questions are visible
- Gates that must pass before delegation are enumerated
- The roadmap distinguishes settled decisions from open questions

**FAIL if:**
- Hermes would need to make strategic choices during execution
- Unresolved architecture questions are hidden
- Required human decisions are not surfaced
- The roadmap implies a decision was made when it was not

---

## Gate Outcomes

### ROADMAP_READY_FOR_ORCHESTRATION

**Meaning:** All six criteria pass. The roadmap section referenced in the
delegation envelope is explicit enough for safe delegation.

When this outcome is produced, Hermes may:

- Create bounded task packets using the existing
  `agents/orchestrator-task-packet-template.md`
- Delegate implementation to the assigned execution agent
- Collect evidence and result reports after delegation
- Track progress against the roadmap section
- Escalate normally when checkpoint conditions are met

Hermes must still respect:
- The delegation envelope's maximum task count, checkpoint cadence, and
  escalation owner
- Per-repository Hermes scope from `CONTROL.md`
- The execution agent's capability boundary (OpenCode ≠ Codex)
- All existing stop conditions from `HERMES_AGENT_CONTRACT.md`

### ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION

**Meaning:** One or more criteria fail. The roadmap is not explicit enough for
safe delegation. Hermes may not proceed.

When this outcome is produced, Hermes must:

1. **STOP** — do not create any task packet
2. **EXPLAIN** — for each failed criterion, state exactly what is missing
3. **IDENTIFY** — list the specific fields, sections, or decisions that are
   insufficient
4. **REQUEST** — recommend the clarification needed before re-evaluation

Hermes must not:

- Invent requirements to fill gaps
- Choose architecture to resolve ambiguity
- Silently expand scope to compensate for missing information
- Delegate work that requires architecture-level reasoning from an
  execution agent
- Proceed with partial information and "figure it out as we go"

---

## Application Procedure

1. **Read the roadmap section** referenced in the delegation envelope. If no
   section is specified, read the full roadmap for the target repository.
2. **Read the target repository's CONTROL.md** for Hermes scope, artifact
   paths, and blockers.
3. **Inspect current repository state** (git status, SHA, working tree
   cleanliness, recent activity).
4. **Evaluate each criterion** (1-6) against the roadmap content and current
   state. Record PASS or FAIL per criterion.
5. **Produce outcome:**
   - All PASS → ROADMAP_READY_FOR_ORCHESTRATION
   - Any FAIL → ROADMAP_INSUFFICIENT_FOR_ORCHESTRATION
6. **Report** the outcome with evidence — which criteria passed, which failed,
   and why.

---

## Integration

This gate is called during the Hermes startup sequence, after reading the
delegation envelope and before creating any task packet. It is checked once per
delegation — not once per chunk within a delegation.

This gate does not replace:
- Repository eligibility checks (`HERMES_AGENT_CONTRACT.md` §3.1)
- Permission derivation (`HERMES_AGENT_CONTRACT.md` §3.2)
- Artifact path declaration check
- Mode 0 envelope requirements

It is an additional safeguard before those checks proceed to packet creation.
