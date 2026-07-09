# Portfolio Baseline

**Status:** Current authority for portfolio-wide repository inventory, classification, current state, and sequencing.
**Purpose:** Compact reference for roadmap authoring and portfolio management. Derived from per-repository audits (2026-07-05), current-state inspection (2026-07-08), and the ivy-control-vps control documents.
**Source audits:** `ivy-control/vps/archive/audits/` (historical — not current authority).

---

## §1 Repository Inventory

### §1A Classification

| # | Repository | Class | Runtime type | LLM stages | VPS candidate |
|---|-----------|-------|-------------|------------|---------------|
| 1 | Traderie | Deterministic | Data pipeline | 0 | First reference |
| 2 | SJC Intel | Deterministic | Data collection | 0 | Early follow-on |
| 3 | IH Market Companion | Deterministic | Browser/API | 0 | After Traderie |
| 4 | WGU-Reddit Operations | LLM pipeline | Multi-stage LLM | 18 (3 active) | After deployment pattern proven |
| 5 | BSDA Courses | LLM pipeline | Multi-stage LLM | 9 (6 active) | After LLM workflow contract |
| 6 | WGU Atlas | LLM pipeline | QA generation | 11 (8 live) | After LLM workflow contract |
| 7 | Idle Hacking KB | LLM pipeline | Knowledge base | 34 (5 live) | After LLM workflow contract |
| 8 | Reckless Ben | Restricted | NO_LAUNCH | 0 planned active | Not applicable |

**Total active LLM stages across portfolio:** 22 (as of 2026-07-05)

---

### §1B Per-Repository Current Status

#### Traderie

**Phase A complete.** First reference-deployment candidate for the VPS portfolio.

- GitHub: `github.com/wguDataNinja/d2-market-helper`
- 17 PostgreSQL migrations (001–017), each with forward + rollback + validation
- 57/57 tests pass
- Real PostgreSQL adapter (`traderie_pg_adapter.py`), env-gated, writer-role-safe
- Bounded 25-record pilot (`pc_sc_l`) — parity, rollback, delete/reimport, backup, checksum, isolated restore proven
- Health export writes to `health.health_runs` with bounded insert/delete
- 6 inert systemd service/timer pairs
- 3 VPS wrapper scripts (snapshot, backup, validate)
- VPS Capacity Gate passes at 84% disk (5.8 GB free)
- VPS has no PostgreSQL and no Traderie checkout yet
- No LLM stages — deterministic collection and analysis only
- Repository control document: `repos/traderie/CONTROL.md`

#### SJC Intel

Deterministic file-based data collection and classification. Strong operational and agent-oriented structure.

- All 14+ workflows use HTTP fetch + HTML parse + regex extraction — zero LLM imports
- Best-in-portfolio three-tier logging model (agent logs, run logs, conversation logs)
- Structured agent startup sequence defined in AGENTS.md
- 11 Hermes task prompt files exist as planning artifacts (not LLM stages)
- Likely early follow-on after Traderie; good first case for Hermes deterministic workflow execution

#### IH Market Companion

Deterministic browser/VPS runtime. No LLM stages exist.

- All execution paths deterministic: `nl_parser.py` (100% regex/string matching), 8 trading pipeline scripts
- 5 prompt files under `prompts/` are planning artifacts only — no runtime consumes them
- Useful for testing browser supervision, restart, resource isolation, and deterministic workflow execution
- Future LLM trading features should remain advisory unless separately approved

#### WGU-Reddit Operations

Active multi-stage LLM pipeline. Highest operational risk in portfolio.

- 3 active pipeline stages (pain point classification, course-level clustering, NL query translation)
- 10 experimental scripts, 2 orphaned, 2 QC stages — total 18 LLM stages
- Best-in-portfolio benchmark/fixture pattern (DEV/TEST splits, artifact preservation)
- **Critical:** Secrets in git history (commits `6881e0d`, `ae2961b`) — requires history rewrite before GitHub push
- **Operational risk:** Suspected duplicate ingestion from both Mac launchd and VPS systemd
- No `.env.example`, no LICENSE, no AGENTS.md
- Requires ingestion-authority inspection, history cleanup, one authoritative scheduler, and Hermes-managed LLM workflow contracts

#### BSDA Courses

Best-in-portfolio staged LLM design.

- 6 production stages + 3 ancillary = 9 total LLM stages
- Each stage has single purpose, structured I/O contracts, provider abstraction (`llm_provider.py`), prompt version history, token metadata (`.meta.json`), and human review gates (`--llm-decision`)
- Production model `deepseek-v4-flash` hardcoded — not configurable per-deployment
- No cost tracking on active stages (tokens counted but no dollar cost)
- 21 scripts contain hardcoded Desktop WGU-Reddit DB paths as fallbacks — must be removed before GitHub push
- Consumer-only; must not gain independent Reddit-fetching authority
- Should be treated as a standards source for provider abstraction, structured stage contracts, and human-review gates

#### WGU Atlas

Strongest implemented provider-agnostic LLM runtime.

- 8 live QA stages + 3 offline artifacts = 11 total LLM stages
- Provider-agnostic substrate (Ollama default, OpenAI wired but key absent)
- Deterministic narrowing before every LLM call
- Pydantic structured output contracts with validation
- Per-run artifact capture (JSONL prompt/output pairs)
- Comprehensive test coverage (17 classifier tests, 11 generation tests, 16 post-check tests, eval harness)
- Default model `llama3` hardcoded — not configurable per-deployment
- 9+ files contain hardcoded `/Users/buddy/Desktop/WGU-Reddit/` paths
- Pattern reference for mature Hermes-managed LLM workflow execution

#### Idle Hacking KB

Strong content-safety guards; most complex LLM architecture.

- 34 total registered stages: 5 live, 7 historical/Ollama, 1 archived/OpenAI, 14 draft prompt-only, 4 KB discovery, 1 benchmark, 2 answerability
- Best-in-portfolio content safety: `production_mutation_allowed: false`, `not_approved_for_filter_change`, `llm_annotation_is_not_truth` enforced at output parsing level
- All 5 live stages use OpenCode CLI as sole provider — not provider-agnostic
- Cross-repo credential dependency: falls back to `ivy-control/.env` for `OPENCODE_API_KEY`
- 14 draft prompt-only stages with no runtime runner — need implementation or archival decision
- Should come later in migration sequence

#### Reckless Ben

Restricted — NO_LAUNCH. No active LLM execution.

- Zero LLM imports or API calls
- Highest-quality LLM approval architecture: 18 approval types, orchestrator stops autonomous chaining on `llm_execution`, `config/refresh.yaml` defaults to `dry_run`
- 10+ comprehensive prompt specifications with zero implementation
- Cross-repo credential coupling (reads `.env` from `chive_gate`)
- Should contribute approval-gate and evidence-first patterns without becoming an early production workload

---

## §2 LLM Stage Inventory

As of 2026-07-05 audit:

| Repository | Active pipeline stages | Draft/planned | Total registered | Primary provider(s) |
|------------|:---------------------:|:-------------:|:----------------:|---------------------|
| WGU-Reddit | 3 | 15 | 18 | OpenAI, Ollama |
| BSDA Courses | 6 | 3 | 9 | deepseek-v4-flash |
| WGU Atlas | 8 | 3 | 11 | Ollama |
| Idle Hacking KB | 5 | 29 | 34 | deepseek-v4-flash |
| SJC Intel | 0 | 0 | 0 | None |
| Traderie | 0 | 0 | 0 | None |
| IH Market Companion | 0 | 0 | 0 | None |
| Reckless Ben | 0 | 10+ | 10+ | None |

**Key observations:**
- 22 active LLM stages across the portfolio
- No portfolio-wide prompt versioning convention
- No portfolio-wide provider abstraction beyond per-repo patterns
- Cost tracking incomplete or absent on all active stages
- Timeout/retry configuration hardcoded in all repos
- WGU-Reddit benchmark/fixture pattern is best-in-portfolio

---

## §3 Standards Gap Summary

Derived from the 2026-07-05 portfolio audits. These gaps are organized by severity.

### §3A Pre-GitHub Blockers (must fix before publication)

| Blocker | Affected repos |
|---------|---------------|
| Secrets in git history | WGU-Reddit |
| Hardcoded `/Users/buddy/` paths in source | WGU-Reddit, BSDA Courses, WGU Atlas, Traderie, Reckless Ben |
| Cross-repo credential fallback | Reckless Ben → chive_gate, Idle Hacking KB → ivy-control |
| No LICENSE file | WGU-Reddit, SJC Intel, Traderie, Reckless Ben, Idle Hacking KB, IH Market Companion |
| No `.env.example` | WGU-Reddit, SJC Intel, Traderie, WGU Atlas, Reckless Ben, Idle Hacking KB, IH Market Companion |
| Experimental scripts mixed with production | WGU-Reddit, Traderie, Idle Hacking KB |
| Tracked log/runtime files | Traderie, Idle Hacking KB |
| No AGENTS.md or skeletal | WGU-Reddit, Traderie, IH Market Companion |

### §3B Migration-Integrated Gaps (resolve before or during deployment)

| Gap | Affected repos |
|-----|---------------|
| No health check script | SJC Intel, Traderie, BSDA Courses, WGU Atlas, Reckless Ben, Idle Hacking KB |
| No backup/restore documentation | All 8 repos |
| No service/scheduler definitions in repo | SJC Intel, BSDA Courses, Reckless Ben, Idle Hacking KB |
| No CI test step in workflows | All 8 repos |
| LLM provider hardcoded, not configurable per-deployment | BSDA Courses, WGU Atlas, Idle Hacking KB, WGU-Reddit |
| No cost tracking on LLM stages | All repos with LLM stages |
| No timeout/retry configuration externalized | All repos with LLM stages |
| Deployment instructions not documented | All 8 repos (WGU Atlas partial) |

### §3C Post-Migration Improvements

- Portfolio-wide prompt versioning convention
- Three-class logging model adoption across all repos
- Full frontend test coverage
- Docker containerization
- Formal benchmarking and performance testing

---

## §4 Repository Admission Baseline

A repository is not ready for Ivy VPS merely because it can run. Admission requires evidence of:

- Clear structure with separated source, tests, data, and generated outputs
- Public/private boundaries with no tracked secrets or hardcoded local-machine dependencies
- Dependency manifest (`requirements.txt`, `pyproject.toml`, or equivalent)
- `.env.example` documenting all required configuration variables
- License decision (explicit or documented exception)
- Purpose, setup, operation, troubleshooting, deployment, backup, and recovery documentation
- Tests and CI appropriate to risk profile
- Explicit migrations, health, retention, rollback, and scheduler ownership
- Separation of source, runtime data, generated artifacts, logs, and private state
- Exact-SHA deployment capability and drift detection
- Portfolio-quality presentation

---

## §5 Cross-Repository Dependency and Sequencing

### §5A Deployment sequence

1. **Traderie** — First reference deployment. Proves VPS PostgreSQL installation, isolation, exact-SHA deployment, manual run, health reporting, backup to Mac, restore, rollback, and scheduler activation.
2. **SJC Intel** — First Hermes deterministic workflow. Follows established VPS patterns and adds structured agent/run/conversation logging.
3. **IH Market Companion** — Browser supervision, restart, resource isolation, and deterministic execution on VPS infrastructure.
4. **WGU-Reddit Operations** — First Hermes-managed LLM workflow. Requires ingestion-authority resolution, history cleanup, and single-writer cutover first.
5. **BSDA Courses** — Staged LLM design as Hermes workflow contract reference.
6. **WGU Atlas** — Provider-agnostic LLM runtime as mature Hermes workflow pattern.
7. **Idle Hacking KB** — Most complex LLM architecture; deferred until patterns proven on simpler repos.
8. **Reckless Ben** — NO_LAUNCH; contributes approval patterns only.

### §5B Dependency relationships

- VPS PostgreSQL installation is prerequisite for all database workloads
- Hermes read-only inspection authority must precede any workflow execution
- Deterministic workflow contracts must precede LLM workflow contracts
- WGU-Reddit ingestion-authority inspection is early operational risk — should not wait for deployment sequence
- Shared standards (prompt versioning, provider abstraction, cost tracking) should be defined before second LLM workflow deployment

---

## §6 Cross-Repository Patterns Worth Preserving

| Pattern | Source repository | Description |
|---------|------------------|-------------|
| Three-tier logging | SJC Intel | Agent logs, run logs, conversation logs + durable root docs |
| Agent startup sequence | SJC Intel | Ordered reading path for new agents in AGENTS.md |
| Long-LLM-stage guard | BSDA Courses | AGENTS.md explicitly bans unapproved LLM runs |
| Approval gate taxonomy | Reckless Ben | 18 structured approval types with orchestrator enforcement |
| Content safety at parser level | Idle Hacking KB | `production_mutation_allowed: false` enforced in output parsing |
| Internal three-doc system | WGU Atlas | Control, memory, dev log separation |
| Provider abstraction | BSDA Courses | `llm_provider.py` abstracts multiple LLM providers |
| Benchmark/fixture pattern | WGU-Reddit | DEV/TEST splits, artifact preservation, benchmark configs |
| Staged LLM design | BSDA Courses | Single-purpose stages with structured I/O contracts, human-review gates |
| Provider-agnostic runtime | WGU Atlas | Deterministic narrowing, Pydantic contracts, post-checks, evaluation harness |

---

## §7 Decisions Requiring Buddy

| Decision | Context |
|----------|---------|
| WGU-Reddit git history rewrite | Commits `6881e0d` and `ae2961b` contain credentials in history |
| Portfolio LICENSE choice | 6 of 8 repos need LICENSE; MIT pattern exists in WGU Atlas and BSDA Courses |
| Accept sjc_intel three-tier logging as portfolio standard | Best existing pattern; could be adopted by other repos during migration |
| Archive or implement 14 idlehacking_kb draft prompt-only stages | Significant designed but unimplemented work |
| Archive WGU-Reddit experimental scripts before GitHub push | 12 scripts with hardcoded paths and varying quality |
| Decouple cross-repo credential dependencies | Reckless Ben → chive_gate, Idle Hacking KB → ivy-control |
