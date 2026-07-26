# Codex Escalation Context

**Role:** Reusable operational template. Hermes produces one escalation context
artifact when it determines a Codex capability is needed and the capability
registry permits escalation. The capability definitions, enablement policy, and
authority limits remain in `agents/HERMES_AGENT_CONTRACT.md` §3.5d and the
target repository's `CONTROL.md`.

Use this template for every `NEEDS_CODEX` outcome that reaches an enabled
capability. This artifact ensures Codex receives bounded reasoning requests,
not open-ended "fix this" prompts.

---

## Escalation Identity

- **Capability:**
    - `roadmap_repair`
    - `architecture_review`
    - `implementation_blocker_review`
    - `production_change_review`
- **Repository:** [target repository slug]
- **Envelope:** [delegation envelope ID]
- **Hermes validation reference:** [path to the Hermes validation report that
  produced NEEDS_CODEX]

---

## Trigger Condition

Describe:

- What condition did Hermes detect?
- Why can Hermes not resolve it? (architecture reasoning required /
  cross-repo design conflict / missing system boundary / tradeoff analysis /
  repeated execution failure)
- Why does this exceed Hermes authority?

---

## Verified Current State

Include facts only — no speculation, no interpretation:

- Relevant artifact paths (task packet, execution report, Hermes validation
  report, prior escalation context)
- Documents Codex must read first (roadmap section, CONTROL.md, relevant
  standards)
- Known constraints (source-only repo, no DB, no VPS runtime, budget limits)
- Decisions already made that Codex must not reopen

---

## Specific Questions

Codex must answer each of these bounded questions:

1. [Question 1 — specific, not open-ended]
2. [Question 2 — specific, not open-ended]
3. [Question 3 — specific, not open-ended]

Questions must be answerable from analysis, not from execution. If a question
requires running code, accessing data, or modifying files, it is not a Codex
question.

---

## Constraints

Codex must not:

- Modify implementation files, configuration, or data
- Bypass approval gates or change authority boundaries
- Expand scope beyond the specific questions asked
- Make human business decisions (priority, budget, personnel)
- Recommend anything requiring credentials, secrets, or paid services beyond
  the accepted OpenCode cost model
- Claim work is complete without evidence

---

## Expected Output

Codex should produce a structured markdown document with:

1. **Direct answers** to each specific question
2. **Options considered** — alternatives evaluated and why each was accepted or
   rejected
3. **Recommended approach** — the recommended path with rationale
4. **Risks** — risks introduced by the recommended approach
5. **Assumptions made** — what Codex assumed that must be verified by the
   reconciler
6. **Unresolved questions** — what Codex wishes it had but could not determine
   from the provided context

---

## Authority Boundary

Codex may:

- Analyze design options and tradeoffs
- Recommend approaches and identify risks
- Propose roadmap changes, dependency clarifications, or phase refinements
- Evaluate architecture decisions against constraints
- Identify missing information that would be needed for a final decision

Codex may not:

- Authorize execution of any change
- Approve continuation of orchestration work
- Replace Hermes validation or Buddy approval
- Make final decisions about architecture, scope, or priority
