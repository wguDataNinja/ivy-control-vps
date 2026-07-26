# Hermes Validation Report

**Role:** Reusable operational template. Hermes writes one validation report
per delegated task to independently verify the execution agent's evidence and
produce a structured outcome. The authoritative lifecycle and outcome
definitions remain in `agents/HERMES_AGENT_CONTRACT.md` §§3.5b-3.5c.

Use this template for every Hermes Mode 0 checkpoint review. Replace every
bracketed field. This artifact evaluates work; it does not describe work.

---

## Task Identity

- **Task ID:** [task slug]
- **Envelope:** [envelope ID]
- **Target repository:** [repository slug]
- **Roadmap reference:** [roadmap section]
- **Task packet:** [path to task packet]
- **Execution report:** [path to execution report]

---

## Artifact Completeness

Check:
- Execution report exists.
- Required fields are present (objective, sources, changes, validation, findings).
- Referenced artifacts (logs, evidence files) exist.

**Result:** PASS / FAIL
**Details:** [what was checked, what was missing]

---

## Evidence Validation

Check:
- Required validation commands were executed.
- Test results are present and passing.
- Evidence artifacts exist and match claimed outputs.
- Claims are supported by the evidence provided.

**Result:** PASS / FAIL / NOT_APPLICABLE
**Details:** [which validations were reviewed, which failed]

---

## Scope Compliance

Check:
- Changed paths are within the allowed paths defined in the task packet.
- No prohibited changes (production data, credentials, canonical docs, Git state).
- No unexpected modifications outside the declared scope.

**Result:** PASS / FAIL
**Details:** [paths checked, any violations found]

---

## Stop Condition Review

Check:
- No new blockers appeared during execution.
- No new decisions are required before continuation.
- No scope expansion occurred.
- No gate changes or authority boundary shifts.

**Result:** NONE / BLOCKER / GATE_CHANGED
**Details:** [conditions checked, any changes found]

---

## Claim Verification

Check:
- Execution claims are supported by evidence (file diffs, test output, validation results).
- Unsupported claims are identified.
- Missing evidence is noted.

**Result:** PASS / FAIL
**Details:** [claims verified, unsupported claims noted]

---

## Outcome

One of:

- **HERMES_ACCEPT** — all checks pass, no issues found
- **HERMES_ACCEPT_WITH_NOTE** — all checks pass, minor observations recorded
- **HERMES_REJECT** — one or more checks fail, specific defects identified
- **NEEDS_BUDDY_REVIEW** — cannot determine pass/fail without human judgment
- **NEEDS_CODEX** — a matching Codex capability may resolve the issue, but
  approval is required

**Reason:** [explanation of the outcome, defects for REJECT, what Buddy/Codex
would resolve for escalation outcomes]

---

## Next Action

- **Continue** — next task within envelope authorized
- **Stop** — envelope exhausted or blocker prevents continuation
- **Request decision** — needs Buddy review or Codex escalation
- **Create escalation artifact** — produce Codex escalation context
