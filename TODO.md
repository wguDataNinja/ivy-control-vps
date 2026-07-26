# Session 13 — Establish the Verified Execution Baseline for the First Branch-to-PR Pilot

## Intent

Session 12 established the architecture, policy, and sequencing for the first
autonomous branch-to-PR pilot on Palworld KB. Session 13 begins the verified
execution baseline: direct VPS verification, read-only Palworld publication
audit, and minimum tooling design — not pilot implementation.

The architecture and strategic decisions from Session 12 are preserved in
`docs/STRATEGIC_ARCHITECTURE.md`. Read that first.

## Current verified state (end of Session 12)

- `docs/STRATEGIC_ARCHITECTURE.md` created — durable architectural decisions
- `ROADMAP.md` updated — §6A Autonomous Branch-to-PR Pilot Transition added
- `TODO.md` updated — Session 13 sequence
- ivy-control-vps on `architecture/gold-standard-control-plane` branch (6 ahead)
- Palworld KB 36 commits ahead of `origin/main`, dirty tracked + untracked
- Git Steward predecessor found in `ivy-control` repo (3 scripts, schema, skill)
- STS Workbench identified as key reference architecture (not yet managed)
- Hermes terminology overload identified — needs reconciliation in docs
- VPS runtime facts remain UNVERIFIED — no SSH inspection performed

## Non-negotiable boundaries

- Same as Session 12: `_internal/` never staged/pushed, private content stays
  private, no destructive cleanup without approval.
- Do not begin the Palworld implementation pilot during Session 13.
- Do not port Git Steward code during Session 13 (design only if needed).
- Do not create GitHub credentials, modify branch protection, or push repos.

---

## Task 1 — VPS Runtime Verification (READ-ONLY, SSH IF AUTHORIZED)

Directly verify the VPS engineering environment. Read-only commands only.
Do not modify services, credentials, or deployments.

### Subtasks

1. Host, disk, and workspace paths
   - `df -h` — confirm free space
   - Verify `/home/scraper/apps/` structure
   - Verify `/home/scraper/workspaces/` exists or can be created
   - Check largest consumers: `du -sh /home/scraper/*/ | sort -rh | head -10`

2. Hermes runtime
   - `which hermes` and `hermes --version`
   - `systemctl --user list-units --all | grep hermes` or equivalent
   - `ps aux | grep hermes`
   - Check `~/.hermes/` structure if it exists

3. OpenCode / Codex runtime
   - `which opencode` and `opencode version`
   - `which codex` and `codex --version`
   - Check `~/.opencode/` or equivalent config paths

4. GitHub credential
   - `gh auth status`
   - Token scopes (do not print token value)
   - Which repositories are visible

5. API key capability
   - Check configured model providers (do not print key values)
   - Determine available models

6. Palworld KB status
   - Check whether any clone exists at expected paths
   - If not, verify clone is feasible (disk, auth)

### Expected artifact

`_internal/outbox/session-13/01-vps-verification-report.md`

### Stop conditions

- Any unverified credential or secret exposure
- Disk below 4 GB free
- Production service access without explicit authorization
- Cannot determine Hermes/OpenCode/Codex/credential state

---

## Task 2 — Palworld Publication Audit (READ-ONLY)

Read-only classification of Palworld KB's 36 ahead commits and dirty/untracked
state. Do not modify the repository.

### Subtasks

1. List all 36 commits: `git log --oneline origin/main..HEAD`
2. Classify each commit by type (source, test, docs, session, evidence)
3. Identify commit contents for any `_internal/` or private paths
4. Classify each dirty tracked file (modified, deleted)
5. Classify each untracked file or directory
6. Determine which files contain private session content
7. Determine which files contain generated artifacts
8. Produce disposition recommendation: publish, review-and-publish, private-only

### Expected artifact

`_internal/outbox/session-13/02-palworld-publication-audit.md`

Containing a table per commit/path: `path | type | publishable | recommended disposition`

### Acceptance criteria

Every dirty/untracked path has a classification and recommended disposition.
Private session logs are clearly identified and excluded from publication.

### Read-only? YES
### May write? NO — report only
### Requires Buddy approval? YES — before any baseline construction

---

## Task 3 — Minimum Task/PR/Quota Contract Design (READ-ONLY DESIGN)

Design the minimum contract fields needed for the first pilot. Do not implement.

Review existing templates at:
- `agents/orchestrator-task-packet-template.md`
- `agents/hermes-validation-report-template.md`
- `docs/REPOSITORY_WORK_PROTOCOL.md` (result report requirements)

Propose additions for:
1. Task packet: `model_budget`, `base_sha`, `branch`, `allowed_paths`, `denied_paths`
2. Result report: `stop_conditions_hit`, `evidence_paths`, `residual_dirty_state`
3. PR body: minimum required sections

### Expected artifact

`_internal/outbox/session-13/03-minimum-contract-design.md`

### Read-only? YES
### May write? NO — design document only
### Requires Buddy approval? YES — before template modification

---

## Task 4 — Git Steward Migration Plan (READ-ONLY DESIGN)

Inspect the predecessor Git Steward implementation in `~/projects/ivy-control`.
Design the migration plan. Do not copy code.

### Subtasks

1. Inspect `~/projects/ivy-control/scripts/git_steward.py` (610 lines)
2. Inspect `~/projects/ivy-control/scripts/git_steward_review.py` (354 lines)
3. Inspect `~/projects/ivy-control/scripts/git_steward_commit.py` (498 lines)
4. Inspect `~/projects/ivy-control/schemas/git_steward_commit.schema.json` (100 lines)
5. Inspect `~/projects/ivy-control/skills/git_steward_agent.md` (337 lines)
6. Design the minimum viable migration with mandatory gates
7. Propose target paths in `ivy-control-vps`

### Expected artifact

`_internal/outbox/session-13/04-git-steward-migration-plan.md`

### Read-only? YES
### May write? NO — plan only
### Requires Buddy approval? YES — before implementation

---

## Task 5 — Session 13 Closeout

1. Consolidate all Task 1-4 reports
2. Produce session close record
3. Produce next-session handoff
4. Reconcile Git state

### Expected artifact

Session close record at `_internal/logs/sessions/session-13/TASK_JOURNAL.md`
Next-session handoff at `_internal/outbox/session-13/`

---

## Explicit non-goals for Session 13

- Do NOT begin Palworld pilot implementation
- Do NOT port Git Steward code
- Do NOT create GitHub credentials
- Do NOT modify branch protection
- Do NOT modify Palworld KB
- Do NOT push any branches
- Do NOT modify production services
- Do NOT perform broad document consolidation
- Do NOT begin Idle Hacker restructuring
- Do NOT extract STS adapters

---

## Deferred (Session 14+)

- Palworld baseline construction (requires Task 2 approval)
- Git Steward implementation (requires Task 4 approval)
- Credential configuration (requires Task 1 findings)
- First pilot execution (requires all above)
