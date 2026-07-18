# VPS Repository Admission Checklist

**Status:** Supporting checklist. `docs/PORTFOLIO_CONVENTIONS.md` and `docs/REPOSITORY_CONTROL_MODEL.md` remain the active authorities for VPS admission requirements and gate semantics.

Use this checklist before admitting any portfolio repository (for example,
palworld_kb or sts-workbench). It is an evidence checklist, not deployment
authority.

1. **Identity and fit:** canonical name, owner, purpose, portfolio fit, and public/private classification.
2. **GitHub authority:** authenticated owner, intended remote, default branch, reviewed SHA, and publication-history review.
3. **Hygiene:** dirty/untracked/ignored inventory, secret scan, large-file scan, dependency lockfiles, and no runtime data in the proposed push.
4. **Data lifecycle:** source owner, archive destination, retention/cleanup rule, data classification, and raw-data boundary.
5. **PostgreSQL:** database/schema/role, migration and rollback plan, importer reconciliation, and backup/restore contract.
6. **Capacity:** live free bytes and inodes, clone/dependency/build/runtime estimates, active growth, and safety reserve.
7. **Placement and deployment:** `~/workspace` versus `~/apps`, exact-SHA source, production entrypoint, configuration source, and rollback artifact.
8. **Runtime authority:** sole service/timer/writer, concurrency/timeout/retry behavior, health producer, freshness and retained-byte evidence.
9. **Secrets and recovery:** secret injection boundary, archive access, backup location, restore drill, and rollback owner.
10. **Acceptance and cleanup:** bounded manual run, genuine natural run, exact active-writer proof, explicit deletion predicate, and Buddy approval gate.

Required roles: Hermes may inspect and report; Medium OpenCode may implement
repo-local schemas, importers, tests, health, bounded staging, docs, and a
non-sensitive publication packet; Strong Codex handles live archive, production
PostgreSQL, cutover, natural-run/restore proof, capacity-sensitive work,
private-data movement, rollback, and cleanup; Buddy decides portfolio fit,
visibility, authority transfer, and deletion.
