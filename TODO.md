

# TODO

This file tracks approved follow-up work for IvyControlVPS. Keep entries concise, current, and limited to actionable work. Completed items should be removed or moved into the appropriate log or durable documentation rather than retained indefinitely.

## Next

- Review the drafted root `AGENTS.md` for correctness and scope.
- Confirm the local implementation path is `/Users/buddy/projects/ivy-control-vps`.
- Leave the VPS repository path unresolved until the actual deployment location is approved.
- Verify that `AGENTS.md` routes meaningful agent work to `docs/LOGGING_STANDARD.md`.
- Create or update the required private agent log for the `AGENTS.md` work.
- Review the latest edits to `docs/LOGGING_STANDARD.md`.
- Validate Markdown links and confirm no private material appears in tracked files.
- Commit and push the approved tracked changes only.

## Agent and orchestration standards

- Define the detailed local implementation contract for OpenCode, Codex, and similar agents.
- Define the detailed VPS orchestration contract for Hermes and agents invoked by Hermes.
- Define approval boundaries for monitoring, maintenance, deployment, rollback, destructive actions, credentials, and production changes.
- Define how Hermes routes work to bounded implementation agents.
- Define the actual VPS checkout path and replace the placeholder in `AGENTS.md`.
- Define the VPS private-context location and provisioning model.

## Git workflow

- Define branch naming.
- Define commit conventions.
- Define pull-request requirements.
- Define merge authority and prohibit agents from self-merging.
- Define how approved commits are updated on the MacBook and VPS.
- Define rollback and dirty-working-tree handling.

## Logging and self-review

- Finalize agent-log naming, retention, and aggregation.
- Define machine/runtime log retention, rotation, and storage expectations.
- Define periodic review of private GPT session logs for decisions, TODOs, rejected ideas, and process lessons.
- Define how approved lessons are promoted from private logs into durable standards.
- Define when agents must report friction, unclear instructions, missing prerequisites, and process improvements.

## Portfolio standards

- Define the repository-admission process.
- Locate or explicitly recreate the missing strategy-first LLM tenets; do not invent them without approval.
- Define portfolio-level LLM strategy, including provider independence, bounded context, evaluation, cost/performance, graceful degradation, and human review.
- Define repo-specific templates only after validating them against real repository needs.
- Define the planned daily documentation loop and its pull-request workflow.

## Later

- Decide whether a license should be added.
- Decide whether any private MacBook context should be provisioned to the VPS for Hermes.
- Decide whether `SESSION.md` provides unique value or should remain optional.