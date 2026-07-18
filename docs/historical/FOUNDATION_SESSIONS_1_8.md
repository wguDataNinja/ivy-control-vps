# Foundation Sessions 1–8

**Status:** Historical public evidence. This narrative preserves the foundation history and priorities recorded at the time. It is not current execution authority; use `ROADMAP.md` for current work and repository `CONTROL.md` records for current managed state.

## Completed foundation

- **Sessions 1–2:** Bootstrap GPT workflow, Reddit Ops migration cutover, PostgreSQL frontier
- **Session 3:** Health contract v2, Traderie production readiness, Reddit Ops closeout
- **Session 4:** Traderie cutover (Mac→VPS), portfolio ingestion-admission matrix, Reddit Ops backup/restore remediation
- **Session 5:** Ingestion-first roadmap rewrite, platform productization, PostgreSQL provisioning, isolated restore proof, reboot persistence proof, idlehacking_kb / ih-market-companion safe-ingestion boundary
- **Session 6:** Phase 0 health CLI, Hermes VPS data estate audit, Idle Hacker KB and IH Market capacity archive
- **Session 7:** Hermes bridge bootstrap, Codex VPS-1/VPS-2 capacity recovery and execution, Git publication
- **Session 8:** Complete Git cleanup (both repos reconciled and committed), Session 5 reconstruction, Git publication assessment, ingestion dashboard prototype

## Priorities recorded at Session 8

1. **Stabilize ingestion health visibility.** Health contract v2 is defined; producers are registered (Traderie, Reddit Ops). Build the portfolio aggregator and normalized views so all workloads have observable current-state health.
2. **Complete remaining stabilization gates.** Reddit Ops has 13 unresolved stabilization gates (STABILIZATION.md). Close these to move from `PRODUCTION_ACTIVE` to `PRODUCTION_COMPLETE`.
3. **Admit SJC Intel.** Next deterministic admission candidate — has systemd units, 11 migrations, health scripts, `.env.example`. Admission packet is ready from Session 5.
4. **Publish sanitized Reddit Ops history.** Local history contains a credential-bearing root commit. Cherry-pick clean commits onto a sanitized publication branch and push.
5. **Continue repository publication and standards work** after the ingestion foundation is observable and stable.
6. **Keep Hermes read-only** for production operations today. Plan a later reviewed pull-request workflow for bounded repository maintenance.

## Monitoring and operations

- Verify all VPS ingestion workloads and identify the sole scheduler and writer for each.
- Confirm recent successful database writes and source-data freshness.
- Monitor disk, memory, database growth, backups, and restore readiness on the small Hetzner VPS.
- Treat workloads as deployed but untrusted until health and recovery evidence are visible.

## Decision record

| Date | Decision | Source |
|------|----------|--------|
| 2026-07-12 | Traderie approved SHA `e5ebd0f` deployed via systemd timer | Session 5 |
| 2026-07-12 | PostgreSQL provisioned on VPS; Idle Hacking KB boundaries defined | Session 5 |
| 2026-07-13 | Idle Hacker KB capacity archive completed; Hermes estate audit completed | Session 6 |
| 2026-07-14 | Hermes bridge operational as read-only resident assistant | Session 7 |
| 2026-07-14 | Codex VPS-1 (capacity archive) and VPS-2 (live execution) completed | Session 7 |
| 2026-07-15 | Both repos fully reconciled and committed; Sessions 1–7 durably recorded | Session 8 |
