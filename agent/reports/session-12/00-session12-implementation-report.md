# Session 12 — VPS Workspace and Hermes Foundation

**Status:** Implemented foundation; Hermes pilot and Palworld residency remain pending.
**Role:** Public completion report and handoff evidence. It does not replace
the control records, roadmap, or agent contracts.

## Executive summary

Ivy Control VPS now has a verified clean public engineering workspace on the
VPS at the published `main` revision
`1cd48d756ede1018b7f74f0ecc30c3f8fc68e044`. It is not a production service.
The checkout contains no `_internal/` tree and uses a sparse profile to omit
the obsolete tracked root `TODO.md`; the profile is reversible by disabling
sparse checkout.

The public model now distinguishes engineering-workspace residency from
production activation and defines a bounded Hermes Mode 0 for artifact-only
orchestration. Hermes still has no authority to write code, Git branches,
production data, services, databases, credentials, or canonical documents.

## Files changed

- `docs/OPERATING_MODEL.md` — VPS workspace boundary and Mode 0 role.
- `docs/GIT_WORKFLOW.md` — workspace residency and sparse-`TODO.md` rules.
- `docs/REPOSITORY_WORK_PROTOCOL.md` — VPS artifact boundary and orchestration
  lifecycle.
- `agents/VPS_ORCHESTRATION.md` — current resident checkout and Mode 0.
- `agents/HERMES_AGENT_CONTRACT.md` — delegation-envelope checkpoint rule and
  current Palworld pilot conditions.
- `agents/orchestrator-task-packet-template.md` — reusable bounded packet.
- `docs/HERMES_OPERATOR_GUIDE.md`, `docs/RESIDENT_AGENT_MODEL.md` — aligned
  resident-agent boundaries.
- `docs/REPOSITORY_CONTROL_MODEL.md`, `tools/portfolio_registry.py` —
  artifact-only scope vocabulary.
- `repos/ivy-control-vps/CONTROL.md` — self-governance record.
- `docs/VPS_INVENTORY.md` — verified control-plane workspace topology.

## VPS residency evidence

- Existing checkout verified as a Git worktree owned by the expected workspace
  account, clean, and public-only.
- Previous workspace revision: `71dfdd26dd3117cfa22b9ee810014084200c690c`.
- Current revision: `1cd48d756ede1018b7f74f0ecc30c3f8fc68e044`.
- Rollback: check out the recorded previous revision after confirming a clean
  worktree.
- `_internal/` is absent and no tracked `_internal/` paths exist.
- Resident read-only orientation and health-summary commands completed.
- Capacity remained 8.7 GB free / 76% used at the preceding read-only check;
  the checkout footprint was approximately 2.2 MB before refresh.

## Hermes model changes

Mode 0 requires an explicit delegation envelope naming the target repository,
roadmap section, permitted artifact paths, executor, validation, maximum task
count, checkpoint cadence, and stop/escalation owner. Hermes can create only
task packets, factual reviews, concise orchestration logs, and
`PENDING_GPT_REVIEW` journal proposals in those declared paths.

After every delegated task Hermes must confirm the report, log, validation,
changed-file scope, stop conditions, and remaining envelope before creating the
next packet. A failed checkpoint stops the run for GPT/Buddy review.

## Palworld preparation finding

Palworld is not ready to clone from its current local working tree. It contains
staged promotion work, modified knowledge/index/log files, and substantial
untracked experiment and proposal output. No Palworld path was changed,
staged, deleted, transferred, or cleaned. The next Palworld task must classify
that state, select an approved clean baseline, and obtain the required
repository-specific artifact-path and Hermes-scope decision.

## Validation

- `python3 -m pytest -q tests/test_portfolio_registry.py tests/test_vps_paths.py`
  — 78 passed, 1 skipped.
- `python3 tools/portfolio_registry.py --validate` — 0 issues.
- `./tools/show_portfolio_status.sh --context --repo ivy-control-vps` — pass.
- `./tools/hermes_ready_tasks.sh --repo ivy-control-vps` — pass.
- Resident checkout: clean exact SHA, `_internal/` absent, no-live portfolio
  status and health-summary commands passed.
- `git diff --check` — pass.

## Remaining work and risks

- The Session 12 public governance changes are local pending review/publication;
  the resident checkout remains at the published SHA above until an approved
  Git update occurs.
- `docs/PORTFOLIO_INTENT.md` is an existing untracked protected file while the
  public documentation index refers to it. It requires its separate authority
  review before public publication; it was not changed here.
- The private VPS runbook contains historical statements that conflict with the
  verified resident Hermes/workspace state. It remains private evidence and was
  not altered in this public-control-plane task.
- No artifact-only filesystem write barrier exists yet for a multi-task Hermes
  run. Until one is implemented and verified, Hermes is limited to one
  human-dispatched delegated task per run.

## Recommended next bounded tasks

1. Review and publish the exact public governance change set, then update the
   resident checkout to its newly approved SHA.
2. Perform a non-destructive Palworld baseline classification and choose a
   clean clone source; do not use its current worktree.
3. Define and verify Palworld's declared Hermes artifact paths and an explicit
   single-task Mode 0 envelope.
4. Run one documentation-safe pilot cycle and obtain GPT/Buddy journal
   acceptance before considering multi-task continuation or PR credentials.
