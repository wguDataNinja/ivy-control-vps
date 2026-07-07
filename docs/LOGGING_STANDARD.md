# Logging Standard

**Status:** Initial / provisional. This standard will be evaluated through actual use and revised when friction or gaps are discovered.

## Purpose

Define the logging layers used across the IvyControlVPS portfolio and make the requirements discoverable to agents through the repository entry point. Detailed retention, automation, aggregation, and repository-specific implementation remain pending.

## Layer 1: Machine and runtime logs

These cover services, jobs, errors, retries, timing, record counts, health checks, backups, pruning, and storage or database growth.

Requirements:

- **Structured where practical.** Use JSON or a delimited format that supports programmatic parsing.
- **Rotated and retained intentionally.** Each repository should document its own retention policy. Default to bounded retention with a clear archival or purge schedule.
- **Secret-safe.** Never write credentials, tokens, API keys, or private host paths to log output.
- **Stored outside Git.** Runtime logs belong in the operating environment (VPS, Mac, container), not in repository history.
- **Suitable for operational diagnosis.** Include enough context (timestamps, correlation IDs, exit codes, error messages) to diagnose failures without requiring interactive access.

Exact tooling (systemd journal, file rotation, structured logging libraries, log aggregation) remains repository-specific.

## Layer 2: Agent work logs

Short records of meaningful agent work.

### When a log is required

An agent log is required whenever an agent performs meaningful work that changes repository state, creates a durable artifact, changes configuration, performs deployment work, or completes a substantive operational task.

### When a log is normally not required

- Read-only exploration
- Simple factual answers
- Brief question answering
- Inspection that produces no durable result or decision

### Provisional format

```markdown
# <agent or task>

- Did:
- Result:
- Checked:
- Next:
```

### Rules

- Remain concise. A few lines per entry is preferred.
- Do not duplicate Git history. Reference commits by hash or message where relevant.
- Record validation results and any unresolved issues.
- Identify the task or agent clearly.
- Create or update the log before the agent declares meaningful work complete.

- `AGENTS.md` or the applicable agent contract should route agents to this standard before meaningful work begins.
- When requested, include concise process feedback covering friction, unclear instructions, missing prerequisites, or possible improvements.
- Do not treat a missing log as agent failure when the logging requirement was not yet written or discoverable at the time of the work.

### Provisional path convention

```
internal/logs/agents/YYYY-MM-DD/<agent-or-task-slug>.md
```

Exact naming, retention, and later aggregation policy are provisional.

## Layer 3: GPT and planning-session logs

These preserve planning and design discussions that may contain:

- Approved decisions not yet promoted into durable documentation
- Rejected or superseded ideas
- Unresolved questions
- Future work
- Private reasoning and context
- Design and process observations

### Provisional path convention

```
internal/logs/gpt/YYYY-MM-DD/<session-slug>.md
```

### Rules

- These logs are private and ignored by Git.
- They are not automatically synchronized to GitHub or the VPS.
- They should be reviewed periodically for decisions, TODOs, and items to promote.
- Durable approved decisions should be promoted into the correct public or private authority document.
- Logs are evidence and source material, not automatically authoritative policy.
- Secrets should not be stored in these logs merely because they are private.

- Each session log should begin with a short meta section defining its purpose and structure.
- A recommended structure is: Context, Approved decisions, Work completed, Process observations, Unresolved items, Items to promote later, and Next-session handoff.
- Keep session logs concise and avoid duplicating Git history, implementation reports, or public documentation unless an undocumented decision or process lesson is attached.
- Flag uncertainty rather than guessing.
- MacBook-private session logs are not automatically copied to the VPS; only material needed for VPS or Hermes operations should later be promoted or provisioned deliberately.

### Session close review

GPT planning sessions should normally be closed using the [session-close workflow](../workflows/session-close.md) before the resulting private record is saved.

The resulting record should be saved under the GPT/planning-session path above unless a more specific private location has been approved.
