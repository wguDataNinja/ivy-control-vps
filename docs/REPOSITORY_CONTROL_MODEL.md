# Repository Control Model

**Status:** Current authority.
**Purpose:** Defines how ivy-control-vps governs managed repositories. Each managed repository receives a `CONTROL.md` that records admission, applicable standards, compliance, blockers, and next authorized work.

---

## ivy-control-vps role

ivy-control-vps is the portfolio control plane. It owns:

- cross-repository standards and conventions
- gate decisions (admission, publication, deployment, activation)
- approved SHA tracking
- repository status aggregation
- agent instruction model (`AGENTS.md`)

Managed repositories remain separate codebases with their own code, data, tests, and local workflows.

---

## Control mechanism

Every managed repository receives a file at `repos/<repo>/CONTROL.md` containing:

- repository identity (purpose, remote, branch)
- current approved SHA (publication anchor)
- portfolio admission state
- applicable standards matrix
- accepted repository-specific deviations
- link to detailed release-gate evidence (`RELEASE_GATES.md`)
- current blocker
- next authorized phase

---

## Standards applicability

Each portfolio standard is assigned one of these applicability states for every repository:

| State | Meaning |
|-------|---------|
| **REQUIRED** | Standard applies and compliance must be demonstrated. |
| **NOT APPLICABLE** | Repository has no use for this standard. Must be documented why. |
| **REQUIRED WITH EXCEPTION** | Standard applies but an approved deviation exists. Exception must be documented in CONTROL.md. |
| **NOT YET ASSESSED** | Standard has not been evaluated. Does not imply exemption. |

---

## Compliance states

Within each applicable standard, compliance is recorded as:

| State | Meaning |
|-------|---------|
| **PASS** | Repository meets the standard. |
| **PASS WITH CONDITION** | Repository meets the standard with documented conditions. Conditions must be resolved by a named gate. |
| **BLOCKED** | Repository does not meet the standard and cannot proceed past the blocking gate. |
| **UNDEFINED** | Compliance has not been evaluated. |

---

## Gate separation

The following gates are defined sequentially:

| # | Gate | Controls |
|---|------|----------|
| 1 | Portfolio Admission | Repository is recognized as managed. |
| 2 | Public Repository Readiness | Repository is safe for GitHub publication. |
| 3 | GitHub Publication | Repository is published at an approved SHA. |
| 4 | Deployment Readiness | Repository can be deployed to infrastructure. |
| 5 | VPS Deployment | Bounded one-shot deployment proof. |
| 6 | Operational Activation | Continuous collection and production authority. |

A later gate cannot pass until the previous gate has passed. Each requires explicit Buddy dispatch to proceed.

Detailed gate evidence is recorded in `repos/<repo>/RELEASE_GATES.md`.

---

## Approved SHA tracking

Every managed repository has a recorded approved SHA. This is the commit that was verified at publication time. Future deployment must use this SHA or a later reviewed and recorded replacement. The approved SHA is recorded in `CONTROL.md` and cross-referenced in `RELEASE_GATES.md`.

---

## Control-sheet update triggers

CONTROL.md must be reviewed or updated when:

- a new gate passes or blocks
- the approved SHA changes
- a standard changes applicability
- a deviation is granted or revoked
- the blocker changes
- the next authorized phase changes

---

## Relationship between documents

| Document | Role |
|----------|------|
| `repos/<repo>/CONTROL.md` | Active governance authority. One-stop for current state. |
| `repos/<repo>/RELEASE_GATES.md` | Detailed gate evidence. Referenced by CONTROL.md. |
| `repos/<repo>/STATUS.md` | **Deprecated** once CONTROL.md exists. Retained as historical reference, not updated. |
| `repos/<repo>/<phase-packet>.md` | Bounded execution instructions for the next authorized phase. Not a governance document. |
| `docs/PORTFOLIO_CONVENTIONS.md` | Durable cross-repo conventions. Referenced by CONTROL.md applicability matrix. |
| `docs/DATA_LIFECYCLE_STANDARD.md` | Portfolio data-lifecycle principles. Referenced by CONTROL.md. |
