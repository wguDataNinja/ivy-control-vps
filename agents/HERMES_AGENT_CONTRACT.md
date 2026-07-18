# Hermes Agent Contract — Bounded Work Discovery

**Status:** Provisional. Hermes read-only inspection authority is established; PR, branch, and bounded-work authority require per-repo Buddy approval.

**Parent documents:**
- `agents/VPS_ORCHESTRATION.md` — interaction modes, role definition, allowed/prohibited
- `docs/HERMES_OPERATOR_GUIDE.md` — installation, bridge protocol, current read-only scope
- `docs/OPERATING_MODEL.md` — Hermes role boundaries, agent hierarchy
- `docs/REPOSITORY_CONTROL_MODEL.md` — gate model, CONTROL.md schema

---

## 1. Applicability

This contract governs Hermes when tasked with discovering and proposing bounded work. It does not grant write authority, deployment permission, or production mutation rights. Hermes identifies work; Buddy or a separately approved execution agent performs it.

---

## 2. Deterministic Hermes Reading and Observation Route

Before any Hermes bounded-work discovery, establish orientation through the smallest sufficient route:

| Step | File | Purpose |
|------|------|---------|
| 1 | `AGENTS.md` | Repository-level agent rules, protected data, Git constraints |
| 2 | `agents/VPS_ORCHESTRATION.md` | Interaction modes, role boundaries, allowed/prohibited actions |
| 3 | `agents/HERMES_AGENT_CONTRACT.md` | This file — bounded work contract |
| 4 | `docs/README.md` and `docs/OPERATING_MODEL.md` | Authority map, navigation, role and public/private boundary |
| 5 | `docs/PORTFOLIO_UNIVERSE.md` and `ROADMAP.md` | Known assets and current portfolio priority |
| 6 | `tools/show_portfolio_status.sh --no-color` | Generated managed-record orientation; not authority |
| 7 | `python3 tools/ingestion_dashboard.py --summary --stdout-only` | Permitted read-only evidence summary; inspect mode must follow `VPS_ORCHESTRATION.md` |
| 8 | `repos/<target-repo>/CONTROL.md` | Per-repo governance, permissions, blockers, next work |
| 9 | `repos/<target-repo>/RELEASE_GATES.md` | Detailed gate evidence for the target repo |
| 10 | `docs/HEALTH_CONTRACT.md`, `docs/GIT_WORKFLOW.md`, and `docs/LOGGING_STANDARD.md` | Read only when the proposed work concerns health, tracked change, or durable work record |

Steps 1–7 establish portfolio orientation. Steps 8–10 are target- and task-specific. Generated command output routes attention; it cannot authorize an action or override `CONTROL.md`, evidence, or a gate.

---

## 3. Repository Eligibility and Permission Representation

### 3.1 Eligible repository determination

A repository is eligible for Hermes bounded work when **all** of the following are true:

| Criterion | Evidence location | Check |
|-----------|-------------------|-------|
| Published on GitHub | `CONTROL.md` has a canonical remote URL | `#` line with `**Canonical remote:**` |
| CONTROL.md exists | `repos/<repo>/CONTROL.md` is present and parseable | File exists on disk |
| Lifecycle state defined | CONTROL.md has a recognized lifecycle field | `**Lifecycle state:**` or `**Lifecycle**` |
| No blocking gate | CONTROL.md and RELEASE_GATES.md show no active BLOCKED gate | `## Current Blocker` section is absent or non-blocking |
| No prohibition from ROADMAP | ROADMAP.md §4C does not say `NO_LAUNCH` or `DEFERRED` for this repo | ROADMAP §4C table |

### 3.2 Permission fields from CONTROL.md

Hermes derives its per-repo permissions from these CONTROL.md fields:

| CONTROL.md field | Hermes meaning | Values → Permission |
|---|---|---|
| `**Lifecycle state:**` | Production maturity → task class eligibility | `production-complete` → full inspection, PR prep; `production-stabilizing` → inspection only; `production_degraded` → recovery-path inspection; `readiness_placeholder` → admission packet prep; `deferred` → no work |
| `**Approved production SHA:**` | Current deterministic deployment | If absent → no deployment assumption; Hermes may inspect but not propose deployment work |
| `## Current Blocker` | Blocked tasks → prohibited | If "stop" or "block" language → no Hermes work in that path |
| Standards matrix compliance | Repo maturity | `PASS` on required standards → Hermes may propose related work; `FAIL` → Hermes may report but not propose |
| `## Next Authorized Work` | Explicitly permitted task classes | Hermes may discover tasks matching these descriptions |
| `## Production Authority` table | Writer, scheduler, DB state | Hermes may inspect but not touch these components |

### 3.3 Hermes-allowed actions per permission level

| Permission level | Hermes may |
|-----------------|------------|
| **inspect** | Read CONTROL.md, README, file tree, test results, health data |
| **report** | Write bridge outbox files, create evidence-backed summaries |
| **propose** | Create PR branches with verified changes (requires per-repo Buddy approval) |
| **test** | Run existing test suites, report pass/fail |
| **admit** | Prepare CONTROL.md, RELEASE_GATES.md for new repo admission |

### 3.4 Prohibited actions (all repos)

Hermes must never:

- Self-merge any branch
- Push directly to main
- Deploy code, configuration, or services
- Modify systemd units, timers, or service state
- Write to production databases
- Access or expose secrets, credentials, or .env contents
- Modify Git hooks, CI config, or deployment infrastructure
- Expand its own permissions
- Delete files or data
- Commit `_internal/` or `internal/` content
- Claim work that did not occur

---

## 4. Task Discovery Mechanism

### 4.1 Discovery method

Hermes discovers ready tasks by:

1. **Scanning `repos/`** — enumerate all `repos/<repo>/CONTROL.md` files
2. **Parsing each CONTROL.md** — extract lifecycle state, blocker, next authorized work, standards matrix
3. **Filtering by eligibility** — apply §3.1 criteria
4. **Classifying by permission level** — apply §3.2 to determine what Hermes may do
5. **Matching against Next Authorized Work** — compare permitted Hermes actions to the repo's explicit next-work descriptions

### 4.2 Command: `tools/hermes_ready_tasks.sh`

Usage:
```bash
./tools/hermes_ready_tasks.sh [--format table|json|markdown] [--repo <name>]
```

Read-only. Outputs a table of Hermes-eligible tasks. Never writes to disk.

### 4.3 Task classes

| Class | Description | Requires | Example |
|-------|-------------|----------|---------|
| `inspect` | Read-only file/status review | inspect permission only | "Check deployed SHA vs approved SHA" |
| `audit` | Cross-reference CONTROL.md claims vs live evidence | inspect + report | "Verify backup unit references correct script" |
| `admit` | Prepare CONTROL.md + RELEASE_GATES.md for new repo | admit permission | "Create Palworld KB CONTROL.md" |
| `test` | Run existing test suite for a repo | test permission | "Run traderie test suite, report pass/fail" |
| `propose` | Create branch with verified bounded change | propose permission (Buddy-approved per repo) | "Fix documentation link, create PR" |

---

## 5. Palworld KB Pilot Packet

### 5.1 Inspection scope

| Item | Scope |
|------|-------|
| Repo path | `/Users/buddy/projects/ivy-control-vps/repos/palworld-kb/` |
| CONTROL.md | Create initial governance record at `repos/palworld-kb/CONTROL.md` |
| Lifecycle state | `readiness_placeholder` — source-only admission; no service/DB/runtime |
| Permission level | `admit` — Hermes may prepare admission packet |
| Prohibited | No service, timer, PostgreSQL, archive, or deployment work |

### 5.2 Allowed files

| Allowed | Not allowed |
|---------|-------------|
| `repos/palworld-kb/CONTROL.md` | Any file outside `repos/palworld-kb/` |
| `repos/palworld-kb/RELEASE_GATES.md` | Source content from the actual Palworld KB repo |
| `docs/README.md` (index update) | Credentials, secrets, `.env` files |
| Hermes agent contract files | Production files, systemd, timer |

### 5.3 Test commands

```bash
# Validate CONTROL.md existence and parse
test -f repos/palworld-kb/CONTROL.md && echo "CONTROL.md exists"

# Validate RELEASE_GATES.md if created
test -f repos/palworld-kb/RELEASE_GATES.md && echo "RELEASE_GATES.md exists"

# Run Hermes ready-task scanner to confirm listing
./tools/hermes_ready_tasks.sh --repo palworld-kb

# Git diff check for tracked changes
git diff --check
```

### 5.4 Branch naming convention

```
admit/palworld-kb-control-sheet
```

Types for Palworld KB work:
- `admit/` — admission packet preparation
- `docs/` — documentation updates
- `fix/` — content corrections
- `chore/` — maintenance

### 5.5 Pull-request content expectations

Every PR from Hermes for Palworld KB must include:

1. Purpose statement (one sentence)
2. Files changed (list)
3. Validation result (test commands and output)
4. Evidence of read-only nature (no credential access, no service changes)
5. Explicit "Stop before merge" block (see §5.6)

### 5.6 Stop-before-merge rule

**Do not merge automatically. Do not authorize a merge.**

Palworld KB PRs require Buddy review and explicit approval before merge. Hermes may create the branch and PR content but must never self-merge, auto-approve, or set auto-merge labels.

If a PR remains unmerged after 7 days, Hermes may add a single reminder comment. After 14 days, Hermes must escalate to Buddy with no further automated action.
