# VPS Control-Plane Admission Runbook

## Purpose

This runbook defines the admission process for deploying `ivy-control-vps`
to a VPS checkout. It covers the checks, evidence, and documentation
required before an exact SHA can be deployed and activated.

## Admission Gate Requirements

Before `ivy-control-vps` can be deployed as a VPS control plane:

1. **Exact-SHA verification** — Every deployment must use an approved
   commit SHA recorded in CONTROL.md or the SHA registry.
2. **Clean-tree enforcement** — The working tree must be clean before
   deployment. No dirty tracked files, no untracked secrets.
3. **Upstream comparison** — The deployed SHA must be reachable from the
   canonical upstream remote.
4. **Mutable state outside checkout** — All generated artifacts, logs,
   data, and backups must reside outside the Git working tree.
5. **Configuration validation** — Path classes, `.env` files, and
   `.gitignore` must be validated before deployment.
6. **Rollback plan** — Every deployment must record the prior SHA as the
   rollback target and confirm the rollback path works.

## Path Classes

| Class | Default | Purpose |
|-------|---------|---------|
| `VPS_REPO_ROOT` | `/home/scraper/apps/ivy-control-vps` | Git working tree |
| `VPS_STATE_DIR` | `$HOME/.ivy-control-vps` | All mutable state root |
| `VPS_GENERATED_DIR` | `$VPS_STATE_DIR/generated` | Reports, dashboards |
| `VPS_CONFIG_DIR` | `$VPS_STATE_DIR/config` | `.env` files, config |
| `VPS_DATA_DIR` | `$VPS_STATE_DIR/data` | Runtime data |
| `VPS_LOG_DIR` | `$VPS_STATE_DIR/logs` | Service logs |
| `VPS_BACKUP_DIR` | `$VPS_STATE_DIR/backups` | Backup artifacts |
| `VPS_SHA_REGISTRY` | `$VPS_STATE_DIR/sha-registry.json` | Approved SHA tracking |

## Tooling

| Tool | Purpose |
|------|---------|
| `tools/vps_paths.sh` | Path class library (source from other tools) |
| `tools/verify_exact_sha.sh` | Verify clean tree + exact SHA match |
| `tools/check_upstream_drift.sh` | Compare local vs upstream commits |
| `tools/report_deployed_revision.sh` | Report current deployed SHA and state |
| `tools/plan_rollback.sh` | Generate non-destructive rollback plan |
| `tools/validate_config.sh` | Validate config paths and standards |
| `tools/check_vps_readiness.sh` | Aggregated readiness check (runs all above) |

## Deployment Workflow

1. Record approved SHA in CONTROL.md and SHA registry.
2. Run `tools/check_vps_readiness.sh` to confirm pre-deployment state.
3. Fetch from origin: `git fetch origin`
4. Check out the approved SHA: `git checkout <sha>`
5. Verify post-checkout state: `tools/verify_exact_sha.sh --expected-sha=<sha>`
6. Record deployed revision: `tools/report_deployed_revision.sh --format=json`
7. Record rollback SHA (the prior HEAD).

See `docs/runbooks/exact-sha-deployment.md` for detailed deployment procedure.

## Hermes Integration

Hermes may use `tools/check_vps_readiness.sh --format=json` to collect
evidence for drift and health reports. Hermes may NOT execute rollbacks
or deployments without explicit task authorization.

## Admission Evidence

Every admission must produce:
- Pre-deployment readiness report
- SHA verification result (PASS/FAIL)
- Deployed revision JSON
- Rollback SHA recorded
- Configuration validation result
