# Resident Agent Model

**Status:** Current architecture. Defines the resident-agent concept, the Resident Agent Interface (RAI), and how human operators and agents interact with the VPS.

**Parent document:** `docs/OPERATING_MODEL.md`

**Child documents:**
- `docs/HERMES_OPERATOR_GUIDE.md` — current Hermes implementation
- `docs/VPS_ACCESS.md` — operational SSH, SCP, and graphical access

---

## Purpose

This document describes the architectural model for resident agents on the Ivy VPS — what they are, why they exist, how they communicate, and how they remain bounded.

The model separates the interface from the implementation so that the communication pattern survives individual agent changes.

## Why resident agents

The VPS runs production workloads: data collection, ingestion, health checks, backups. These workloads are deterministic — they follow scripts, systemd timers, and PostgreSQL queries without requiring a human at the keyboard.

But not every question or task is deterministic. Sometimes an operator needs to:

- inspect current state;
- investigate a failure;
- summarize recent health;
- prepare evidence for a decision;
- execute a bounded non-production action.

A resident agent handles these tasks without requiring a live SSH session or a graphical desktop connection. It reads requests, inspects state, and writes responses to a shared file bridge.

## The Resident Agent Interface (RAI)

RAI is the architectural interface between human operators (and their tools) and resident agents on the VPS.

```
Buddy / ChatGPT / OpenCode / Strong Codex
                    │
                    ▼
     Resident Agent Interface (RAI)
     — file-backed request/response bridge
                    │
                    ▼
            Resident Agent
          (e.g., Hermes)
```

### What RAI is

- A durable, auditable, file-based communication channel.
- Requests and responses are plain Markdown files transferred over SSH/SCP.
- The interface survives if the resident agent is replaced.
- The interface imposes no watchers, schedulers, or automatic execution.

### What RAI is not

- Not an autonomous task queue.
- Not a production control plane.
- Not a credential or secret transfer path.
- Not a substitute for deterministic schedulers.

### RAI workflow

```
request
  → file
    → resident agent
      → response
        → verification
          → documentation
```

1. A human or upstream agent places a structured request file in the bridge inbox.
2. The resident agent reads the request, performs bounded investigation.
3. The resident agent writes a structured response to the bridge outbox.
4. A human or verification agent independently verifies the claims.
5. Verified outcomes are promoted to durable documentation.

## File bridge

The current RAI implementation is the file bridge at `/home/scraper/Desktop/hermes-bridge/`:

```
hermes-bridge/
├── README.md   # Bridge protocol (VPS-local runtime artifact)
├── inbox/      # Request files from operator to resident agent
├── outbox/     # Response files from resident agent to operator
└── archive/    # Completed exchanges
```

**Filename convention:** `YYYY-MM-DD_HHMM_<sender>_<topic>_<type>.md`

**SCP from Mac:**
```bash
scp ./request.md ih-market-vps:/home/scraper/Desktop/hermes-bridge/inbox/
```

**SCP to Mac:**
```bash
scp ih-market-vps:/home/scraper/Desktop/hermes-bridge/outbox/<response>.md .
```

Do not put credentials, API keys, `.env` contents, chat bodies, or production data into bridge files.

## Current implementation: Hermes

Hermes Agent (`v0.18.2`) is the current resident agent on the VPS. It is installed as user `scraper` and operates with read-only authority.

See `docs/HERMES_OPERATOR_GUIDE.md` for full implementation details.

The model is designed so that a different resident agent could replace Hermes through the same RAI interface without changing the operator workflow.

## Authority model

- Resident agents are read-only by default.
- Bridge files are context and bounded requests. They are not automatic authorization for broader actions.
- Production writes, systemd changes, database mutations, Git writes, and destructive actions require separate explicit Buddy approval.
- Authority expansion occurs only through documented gates.

## Verification principle

Resident-agent factual claims that influence operational decisions should be independently verified before becoming repository truth.

Session 7 demonstrated why: the agent was 95% correct, but the remaining 5% ("all workloads stable") would have been operationally incorrect. The verification step caught a failed systemd service that the agent had not reported.

```
resident agent
    ↓
independent verification
    ↓
repository truth
```

not

```
resident agent
    ↓
repository truth
```

## Relationship to other documents

| Document | Role |
|----------|------|
| `docs/OPERATING_MODEL.md` | Public governance and operating model |
| `docs/RESIDENT_AGENT_MODEL.md` | **This document** — resident-agent architecture and RAI |
| `docs/HERMES_OPERATOR_GUIDE.md` | Hermes implementation — install, launch, authority, commands |
| `docs/VPS_ACCESS.md` | SSH, SCP, and graphical desktop access |
| `agents/VPS_ORCHESTRATION.md` | Interaction-mode model and approval boundaries |
| `_internal/vps-inventory-and-runbook.md` | Private VPS host identity, workloads, SSH details |

## Proposed future evolution — not implemented

The following ideas are documented for discussion. They are not current architecture.

### Bridge subdirectory structure

```
hermes-bridge/
├── inbox/
│   └── requests/
├── outbox/
│   ├── responses/
│   └── reports/
├── orientation/
├── context/
└── archive/
```

### Persistent context files

Possible files under `context/`: current authority, current priorities, current session, repository map, production boundaries.

### Risks

- Duplicating repository authority in bridge files
- Stale persistent context
- Artifact sprawl
- Treating request files as automatic authorization
- Putting secrets or private bodies into agent files
- Turning a simple bridge into an autonomous task engine
- Allowing agent conclusions to bypass evidence verification

### Recommended constraints

- Repository authority remains canonical.
- Bridge context should reference authoritative files, not duplicate them.
- Bridge files remain bounded, operational, and disposable or archivable.
- No watchers, schedulers, or automatic execution yet.
- No broad multi-agent control framework.
- No authority expansion based on one successful exercise.
