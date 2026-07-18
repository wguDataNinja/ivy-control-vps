# Logging Standard

**Status:** Current authority. Includes public/private logging boundaries.

## 1. Purpose

Define the logging layers used across the IvyControlVPS portfolio and make the requirements discoverable to agents through the repository entry point. Detailed retention, automation, aggregation, and repository-specific implementation remain pending.

## 2. Machine and runtime logs

These cover services, jobs, errors, retries, timing, record counts, health checks, backups, pruning, and storage or database growth.

Requirements:

- **Structured where practical.** Use JSON or a delimited format that supports programmatic parsing.
- **Rotated and retained intentionally.** Each repository should document its own retention policy. Default to bounded retention with a clear archival or purge schedule.
- **Secret-safe.** Never write credentials, tokens, API keys, or private host paths to log output.
- **Stored outside Git.** Runtime logs belong in the operating environment (VPS, Mac, container), not in repository history.
- **Suitable for operational diagnosis.** Include enough context (timestamps, correlation IDs, exit codes, error messages) to diagnose failures without requiring interactive access.

Exact tooling (systemd journal, file rotation, structured logging libraries, log aggregation) remains repository-specific.

## 3. Agent work logs

Short records of meaningful agent work.

### 3A. When a log is required

An agent log is required whenever an agent performs meaningful work that changes repository state, creates a durable artifact, changes configuration, performs deployment work, or completes a substantive operational task.

### 3B. When a log is normally not required

- Read-only exploration
- Simple factual answers
- Brief question answering
- Inspection that produces no durable result or decision

### 3C. Rules

- Remain concise. A few lines per entry is preferred.
- Do not duplicate Git history. Reference commits by hash or message where relevant.
- Record validation results and any unresolved issues.
- Identify the task or agent clearly.
- Create or update the log before the agent declares meaningful work complete.
- `AGENTS.md` or the applicable agent contract should route agents to this standard before meaningful work begins.
- When requested, include concise process feedback covering friction, unclear instructions, missing prerequisites, or possible improvements.
- Do not treat a missing log as agent failure when the logging requirement was not yet written or discoverable at the time of the work.

### 3D. Path convention

```
_internal/logs/agents/YYYY-MM-DD/<agent-or-task-slug>.md
```

(The legacy path `internal/logs/` is preserved temporarily but should not be used for new logs.)

### 3E. Format

A concise record covering what was done, the result, validation performed, and next steps. Full templates and detailed format guidance are in the private orchestration workflow.

## 4. GPT and planning-session logs

These preserve planning and design discussions that may contain approved decisions, rejected ideas, unresolved questions, and private reasoning.

### 4A. Path convention

```
_internal/logs/sessions/GPT-<number>-<session-slug>.md
```

### 4B. Rules

- These logs are private and ignored by Git.
- They are not automatically synchronized to GitHub or the VPS.
- They should be reviewed periodically for decisions, TODOs, and items to promote.
- Durable approved decisions should be promoted into the correct public or private authority document.
- Logs are evidence and source material, not automatically authoritative policy.
- Secrets should not be stored in these logs merely because they are private.
- Each session log should begin with metadata defining its purpose, session number, and related artifacts.
- Keep session logs concise and avoid duplicating Git history, implementation reports, or public documentation unless an undocumented decision or process lesson is attached.
- Flag uncertainty rather than guessing.
- MacBook-private session logs are not automatically copied to the VPS; only material needed for VPS or Hermes operations should later be promoted or provisioned deliberately.

### 4C. Session close

Session close follows a two-part model: repository-side closeout by an agent, then discussion-side capture by GPT. A locally provisioned private supplement may define exact session mechanics; it does not replace the public work protocol.

### 4D. Templates and detailed mechanics

Detailed private session-log templates and append mechanics may be locally provisioned. Public artifact roles and boundaries remain defined here and in `docs/REPOSITORY_WORK_PROTOCOL.md`.
