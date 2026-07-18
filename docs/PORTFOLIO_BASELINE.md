# Portfolio Baseline

**Status:** Supporting reference — dated baseline assessment. It is not current authority for inventory, operational state, or priority.
**Purpose:** Preserve audit-derived inventory, patterns, and gaps observed during the 2026-07-05 to 2026-07-08 baseline work. `docs/PORTFOLIO_UNIVERSE.md` owns the current known-universe view; `ROADMAP.md` and repository control sheets own current priority and managed-repository state.
**Source audits:** `ivy-control/vps/archive/audits/` (historical — not current authority).

---

## §1 Repository Inventory

### §1A Classification

| # | Repository | Class | Runtime type | LLM stages | VPS candidate |
|---|-----------|-------|-------------|------------|---------------|
| 1 | Traderie | Deterministic | Data pipeline | 0 | First reference |
| 2 | SJC Intel | Deterministic | Data collection | 0 | Early follow-on |
| 3 | IH Market Companion | Deterministic | Browser/API | 0 | After Traderie |
| 4 | WGU-Reddit Operations | Boundary unclear | Reddit-derived ingestion/catalog/analysis/LLM split unresolved | 18 (3 active, baseline audit) | Deferred behind boundary reconciliation |
| 5 | BSDA Courses | LLM pipeline | Multi-stage LLM | 9 (6 active) | After LLM workflow contract |
| 6 | WGU Atlas | LLM pipeline | QA generation | 11 (8 live) | After LLM workflow contract |
| 7 | Idle Hacking KB | LLM pipeline | Knowledge base | 34 (5 live) | After LLM workflow contract |
| 8 | Reckless Ben | Restricted | NO_LAUNCH | 0 planned active | Not applicable |

**Total active LLM stages across portfolio:** 22 (as of 2026-07-05)

---

### §1B Dated per-repository observations

#### Traderie

First reference deployment for the VPS portfolio; currently production-degraded pending Session 5 recovery.

- GitHub: `github.com/wguDataNinja/d2-market-helper`
- 17 PostgreSQL migrations (001–017), each with forward + rollback + validation
- 57/57 tests passed at publication baseline; later runtime fixes added focused regression coverage
- Real PostgreSQL adapter (`traderie_pg_adapter.py`), env-gated, writer-role-safe
- Bounded 25-record pilot (`pc_sc_l`) — parity, rollback, delete/reimport, backup, checksum, isolated restore proven
- Health export writes to `health.health_runs` with bounded insert/delete
- 6 inert systemd service/timer pairs
- 3 VPS wrapper scripts (snapshot, backup, validate)
- VPS PostgreSQL, roles, migrations, backup/restore, exact-SHA checkout, systemd units, and scheduler activation have been proven
- Current production SHA: `e5ebd0f6dd41bcb4e1d8a88f272be89b225cfd40`
- Current state: VPS systemd is sole scheduler/writer; first natural scheduled generation partially failed when `pc_hc_nl` timed out at 480 seconds
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

- GitHub: `https://github.com/wguDataNinja/ih-market-companion`
- Remote main SHA: `ae50fd47b49c13016a98034677e16151b337c871`
- All execution paths deterministic: `nl_parser.py` (100% regex/string matching), 8 trading pipeline scripts
- 5 prompt files under `prompts/` are planning artifacts only — no runtime consumes them
- Mac archive verified; bounded snapshot/receipt retention deployed
- Natural-run containment evidence exists
- PostgreSQL import, reconciliation, backup, restore, and cleanup remain pending
- Shared-helper deployment authority remains transitional
- Useful for testing browser supervision, restart, resource isolation, and deterministic workflow execution
- Future LLM trading features should remain advisory unless separately approved

#### WGU-Reddit Operations

Reddit-derived workload family with unresolved repository and responsibility split. Highest operational ambiguity in portfolio.

- 3 active pipeline stages (pain point classification, course-level clustering, NL query translation)
- 10 experimental scripts, 2 orphaned, 2 QC stages — total 18 LLM stages
- Best-in-portfolio benchmark/fixture pattern (DEV/TEST splits, artifact preservation)
- **Critical:** Credential-bearing local history exists; current Session 5 authority identifies commit `e4acae0` as the must-not-publish root commit. Clean publication must exclude it before any normal push.
- **Operational status:** Reddit Ops collector authority is current for production ingestion. The final relationship among WGU-Reddit, Reddit Ops, Reddit catalog or catalog-like exports, analysis, and LLM workloads is not settled.
- No `.env.example`, no LICENSE, no AGENTS.md
- Requires boundary reconciliation before detailed downstream, catalog, or LLM admission planning.

#### WGU Catalog

Low-frequency event-driven or scheduled batch ingestion/source-authority workload.

- Local path: `/Users/buddy/projects/wgu-catalog`
- Purpose: canonical WGU catalog ingestion, parsing, validation, and versioned export
- Runtime type: deterministic CLI/file-export workflow
- Current scheduler: none; operator or future monthly/release-detection trigger
- Database: none required by current evidence
- Admission should be proportional: source version/acquisition date, deterministic command, validation, checksums/manifests, prior-version preservation, freshness/last-success health, and operator procedure
- Do not force daemon, database, or continuous scheduler work unless new evidence requires it

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

Most complex LLM architecture; PostgreSQL metadata onboarding complete; GitHub publication blocked.

- GitHub: `https://github.com/wguDataNinja/idlehacking-kb` (repo exists; implementation commit `61379d38220d10196661c6ee0e58ecc32521385e` unpushed pending privacy/history review)
- PostgreSQL metadata database `idlehacking_kb` established with migration `011`
- 49 historical cutoff identities reconciled; idempotent rerun passed (0 inserts / 49 duplicates)
- Backup checksum verified; isolated restore passed
- No raw-body columns in PostgreSQL — metadata-only boundary
- Legacy cutoff cleanup: 47 files deleted, 8,134,330,994 bytes reclaimed
- Root usage improved from approximately 95% to approximately 75% (free: ~1.9 GB → ~9.9 GB)
- 44 genuine post-cleanup natural exports succeeded with zero failures or warning-journal entries
- Current bounded runtime state: approximately 112 managed generations / 350 MB
- Top-level client health incorrectly reports down — treats cumulative historical failure count as current failure
- Cross-repo credential dependency: falls back to `ivy-control/.env` for `OPENCODE_API_KEY` (unresolved)
- 34 total registered stages: 5 live, 7 historical/Ollama, 1 archived/OpenAI, 14 draft prompt-only, 4 KB discovery, 1 benchmark, 2 answerability
- 14 draft prompt-only stages still need implementation or archival decision

#### Palworld KB

Published and structurally ready, but early as a knowledge product.

- GitHub: `https://github.com/wguDataNinja/palworld-kb`
- Remote main SHA: `1c8d411406ce45cf948390e82f1e8494ca0352b6`
- Repository is clean and validated
- Not yet admitted to the VPS; planned admission is source-only under `~/workspace/palworld-kb`
- No service, timer, dependency installation, or PostgreSQL requirement currently exists
- Current project bottleneck is evidence-rich factual content, not infrastructure

#### Publication Authority Snapshot

Current GitHub authority and VPS-admission snapshot for the three repositories named in Session 6:

| Repository | Canonical GitHub URL | Canonical branch | GitHub visibility | Published SHA | Current VPS state | PostgreSQL state | Archive state | Admission status |
|---|---|---|---|---|---|---|---|---|
| IH Market Companion | `https://github.com/wguDataNinja/ih-market-companion` | `main` | `PUBLIC` | `ae50fd47b49c13016a98034677e16151b337c871` | Containment deployed on VPS; shared-helper normalization still pending | No production PostgreSQL authority; proposal only | Mac archives verified; no VPS deletion authorized | Published; authority established; cleanup still blocked |
| Idle Hacking KB | `https://github.com/wguDataNinja/idlehacking-kb` | `main` | `PUBLIC` on GitHub; treat as privacy-sensitive regardless | Not published; implementation SHA `61379d38220d10196661c6ee0e58ecc32521385e` | Live PostgreSQL metadata database `idlehacking_kb` with migration `011`; bounded filesystem runtime state; legacy cutoff cleanup completed | VPS PostgreSQL for archive metadata; bounded filesystem state for current runtime; Mac private archive | Mac archive verified; no deletion authorized | PostgreSQL onboarding complete; 44 successful natural exports; publication blocked by privacy/history review; top-level health semantics still need correction |
| Palworld KB | `https://github.com/wguDataNinja/palworld-kb` | `main` | `PUBLIC` | `1c8d411406ce45cf948390e82f1e8494ca0352b6` | Not admitted to VPS yet; source-only repository authority established | No PostgreSQL requirement identified yet | No VPS archive or deletion scope yet | Published; later VPS admission only |

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
| No health check script | SJC Intel, Traderie, BSDA Courses, WGU Atlas, Reckless Ben |
| No backup/restore documentation | All 8 repos |
| No service/scheduler definitions in repo | SJC Intel, BSDA Courses, Reckless Ben |
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

### §5A Ingestion-first sequence

1. **Stabilize existing production workloads** — Traderie recovery and Reddit Ops publication/backup/reboot closure.
2. **Prepare eligible ingestion systems in parallel** — SJC Intel, IH Market Companion, WGU Catalog batch readiness, and the safe subset of Idle Hacking KB where applicable.
3. **Cut over in controlled waves** — start with low-risk deterministic repositories rather than simultaneous portfolio-wide activation.
4. **Then mature downstream and LLM workflows** — WGU-derived workloads only after boundary reconciliation; BSDA Courses, WGU Atlas LLM stages after deterministic health, backup, and Hermes read-only patterns are proven. Idle Hacking KB metadata onboarding is complete; remaining LLM-stage work and draft-stage cleanup follow the same pattern once the publication blocker resolves.
5. **Keep Reckless Ben restricted** — `NO_LAUNCH` unless explicit newer authority reclassifies it.

### §5B Dependency relationships

- VPS PostgreSQL foundation is prerequisite for all database production workloads
- Hermes read-only inspection authority must precede any workflow execution
- Deterministic workflow contracts must precede LLM workflow contracts
- Reddit Ops ingestion authority is the current collector boundary; WGU-derived downstream/catalog/LLM ownership must be reconciled before production planning
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

---

## §8 Backup Posture

**Status:** Encrypted portfolio backup operational as of 2026-07-17.

### Baseline snapshot

| Property | Value |
|---|---|
| Snapshot | `snapshot-2026-07-17` |
| Location | `/Volumes/Ivy-Portfolio-Backup/snapshot-2026-07-17/` |
| Backing image | `/Volumes/Passport/B/ivy-portfolio.sparsebundle` (AES-256) |
| Total files | 13,484 |
| Corpus files | 13,477 |
| Allocated size | 135 GiB |
| Bundle logical capacity | 400 GiB |
| Classification | VERIFIED — RESTORE PROVEN |
| Ivy Control SHA | `87cc24b` |

### Protected scope

| Repository | Source roots | Size |
|---|---|---|
| idlehacking-kb | capture/, data/kb, data/chat, data/derived, data/imports | ~135 GB |
| ih-market-companion | _internal/, _outbox/ | ~0.4 GB |

### Retention

Retain the two newest verified snapshots. Never overwrite or automatically delete. A third full snapshot requires a forced retention decision (resize bundle, second drive, incremental strategy, archive, or explicit deletion approval).

### Coverage gaps

- **VPS state:** requires dated manual review artifact before backup preparation
- **Database dumps:** not yet included in snapshot workflow
- **Second drive / offsite:** not yet configured
- **Recovery-confidence derivation:** documented, not yet automated
- **Passport git remote:** not configured (local commit only)

### Key tools

Backup preparation: `python3 tools/backup_execute.py --target /Volumes/Ivy-Portfolio-Backup --prepare`
Backup execution: `python3 tools/backup_execute.py --packet <packet-path> --execute`
Scope audit: `python3 tools/backup_scope_audit.py`
Verifier: `python3 tools/backup_verify.py --packet <packet-path>`
Restore test: `python3 tools/backup_restore_test.py --snapshot <path>`
Passport operating doc: `~/projects/passport/docs/IVY_PORTFOLIO_BACKUP.md`
