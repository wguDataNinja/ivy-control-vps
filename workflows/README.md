# Engineering Workflows

**Role:** Public workflow landing page. The authoritative portfolio work rules are in [`docs/REPOSITORY_WORK_PROTOCOL.md`](../docs/REPOSITORY_WORK_PROTOCOL.md); this page makes the lifecycle visible to engineers and agents without exposing private session material.

## The durable lifecycle

```text
task request
  → inbox or direct handoff
  → bounded agent execution
  → result report
  → agent log
  → review and journal navigation
  → intentional promotion into ROADMAP, CONTROL, or a standard
```

Each artifact has a different role:

| Artifact | Purpose | Is it authority? |
|---|---|---|
| Task request / inbox | Intent, scope, constraints | No |
| Result report | Completed-work evidence and handoff | No |
| Agent log | Concise execution chronology and validation | No |
| Journal | Navigation across work periods | No |
| `ROADMAP.md`, `CONTROL.md`, standards | Settled current truth | Yes, by subject |

Substantial work requires a result report and, when it creates a durable result, an agent log. Small questions and read-only exploration do not need ritual artifacts. See the work protocol for the required fields, approved locations, close checks, and promotion rules.

## Public and private boundary

This public repository describes the workflow and contains durable promoted authority. A locally provisioned private work area may hold task packets, detailed logs, and private evidence; it is intentionally not a clone dependency and must never be committed to public Git. A missing private supplement does not prevent an engineer from following the public protocol.

## Supporting procedure

[`session-close.md`](session-close.md) is the supporting procedure for preserving decisions and safe closeout. It does not replace the protocol or create a separate session authority.
