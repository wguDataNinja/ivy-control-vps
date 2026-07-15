# Hermes Operator Guide

**Status:** Current authority. Hermes is installed, launched, and operational as a read-only resident assistant on the VPS.

**Parent document:** `docs/RESIDENT_AGENT_MODEL.md` — defines the Resident Agent Interface (RAI) architecture that Hermes implements.

## Purpose

Hermes is a resident VPS operations assistant. It observes, inspects, summarizes, recommends, and produces evidence-backed files. It does not have production write authority.

Hermes is not required for routine deterministic production operation. Core fetchers, timers, backups, and health checks remain implemented through deterministic scripts, PostgreSQL, and systemd.

## Installation layout

Hermes Agent (`v0.18.2`, upstream `226e8de8`) was installed via the official per-user Linux installer:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Key paths (user: `scraper`):

| Path | Purpose |
|------|---------|
| `~/.hermes/hermes-agent/` | Hermes agent directory |
| `~/.hermes/` | Configuration, cache, sessions, skills, models |
| `~/.local/bin/hermes` | CLI entry point |
| `~/.config/Hermes/` | Desktop app config |

The installer added managed Python, Node.js, browser tooling, bundled skills, and required dependencies.

## Launch

Hermes Desktop requires a graphical X11 session. Launch command within the existing XFCE/X11/XRD桌面 session:

```bash
DISPLAY=:10.0 hermes desktop --skip-build
```

The display number (`:10.0`) is session-specific and may change on reconnection or reboot. Verify the active display with `echo $DISPLAY` before launching.

Hermes backend (the API server) runs on a dynamically assigned loopback port:

```bash
hermes serve --host 127.0.0.1 --port 0
```

The OS assigns a port (observed: 36393). The backend is loopback-only — no public listener is created.

## Current authority

Hermes is a **read-only** operator assistant. Allowed actions:

| Category | Allowed |
|----------|---------|
| Inspect | Files, directories, logs, processes, listening ports |
| Explain | System state, workload behavior, failure symptoms |
| Navigate | VPS filesystem within `/home/scraper/` boundaries |
| Search | File contents, process lists, configuration |
| Summarize | Health, capacity, workload status |
| Review | Logs, outputs, evidence |
| Recommend | Actions based on evidence |
| Produce | Evidence-backed files in the bridge outbox |

Prohibited actions:

| Category | Prohibited |
|----------|------------|
| Deploy | No code, config, or service deployment |
| Modify | No systemd, timer, or service changes |
| Database | No PostgreSQL provisioning, migration, or write |
| Network | No firewall, port, or exposure changes |
| Destructive | No cleanup, deletion, or pruning |
| Data | No production data modification |
| Git | No commits, pushes, merges, or branch operations |
| Authority | No self-expansion of permissions |

Bridge files are context and bounded requests — they are not automatic authorization for broader actions.

## Provider status

Provider authentication is **not configured**. The default free model (`deepseek-v4-flash`) was sufficient for bounded inspection and installation work. API-key-based provider access and config migration (v0 to v33) remain unresolved.

## File bridge

The Hermes bridge at `/home/scraper/Desktop/hermes-bridge/` is the durable communication mechanism:

```
hermes-bridge/
├── README.md   # Full bridge protocol (VPS-local runtime artifact)
├── inbox/      # Files from Buddy to Hermes
├── outbox/     # Responses from Hermes to Buddy
└── archive/    # Completed exchanges
```

Ownership: `scraper:scraper`, mode `775`.

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

## Validation commands

| Check | Command |
|-------|---------|
| Hermes version | `hermes --version` |
| Hermes doctor | `hermes doctor` |
| Backend port | `ss -tlnp \| grep hermes` |
| Bridge state | `ls -la ~/Desktop/hermes-bridge/{inbox,outbox,archive}` |
| Disk capacity | `df -h /` |
| Running services | `systemctl --user list-units --type=service` |
| Protected resources | Check `~/config/`, `~/.ssh/`, `~/data/private/chat/` are untouched |

## Role boundaries

| Agent | Role |
|-------|------|
| **Hermes** | Resident read-only VPS assistant. Inspects, summarizes, recommends. |
| **OpenCode** | Bounded implementation and verification agent. Used via local Mac session for source work, documentation, tests, and independent evidence verification. |
| **Strong Codex** | Privileged execution for architecture, deployment, database, migration, cutover, rollback, and other sensitive or irreversible operations. |
| **Buddy** | Authority and risk decisions. Sole approver for production mutations, Git writes, privilege expansion, and destructive actions. |

## Stop and escalation boundaries

Stop immediately if:

- A task requires production write, systemd change, database mutation, or Git write without explicit Buddy approval.
- A task would modify protected resources (chat data, `.env` files, SSH keys, `mcstories-search`).
- A task would expand Hermes authority without a separate gate review.
- Bridge content is ambiguous about authorization boundaries — ask Buddy.

Escalate to Buddy for:

- Production deployment or service activation.
- Database provisioning or migration.
- Destructive cleanup or data pruning.
- Git publication or history rewriting.
- Secret or credential management.
- Capacity remediation affecting production workloads.
- Any action requiring sudo (no passwordless sudo available).

For the Resident Agent Interface architecture, verification principle, and proposed future evolution, see `docs/RESIDENT_AGENT_MODEL.md`.
