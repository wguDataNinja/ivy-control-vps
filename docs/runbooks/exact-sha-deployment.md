# Exact-SHA Deployment Procedure

## Prerequisites

- Checkout exists at `$VPS_REPO_ROOT` (resolved by `tools/vps_paths.sh`)
- State directory exists (created by `vps_ensure_dirs()`)
- Approved SHA is recorded in the SHA registry
- VPS capacity confirmed (disk <85%, >1 GB free)

## Procedure

### 1. Pre-deployment check

```bash
cd /home/scraper/apps/ivy-control-vps
./tools/check_vps_readiness.sh
```

Confirm:
- `OVERALL: PASS`
- `SHA_VERIFICATION: PASS` (or expected mismatch if first deployment)
- `CONFIG_VALIDATION: PASS`
- `DIRTY: clean`

### 2. Record pre-deployment state

```bash
./tools/report_deployed_revision.sh --format=json > "$VPS_STATE_DIR/pre-deploy-revision.json"
```

### 3. Fetch and deploy

```bash
git fetch origin
git checkout <approved-sha>
```

### 4. Post-deployment verification

```bash
./tools/verify_exact_sha.sh --expected-sha=<approved-sha> --remote-url=<expected-remote>
./tools/report_deployed_revision.sh --format=json > "$VPS_STATE_DIR/post-deploy-revision.json"
```

### 5. Record evidence

Record in `_internal/` or the state directory:
- Pre-deployment revision JSON
- Post-deployment revision JSON
- Verification result
- Rollback SHA (the pre-deployment HEAD)

## Rollback

If health checks fail post-deployment:

```bash
# Plan the rollback
./tools/plan_rollback.sh --target-sha=<prior-sha>

# Execute (requires explicit authorization)
git checkout <prior-sha>
# Restart services if needed
# Verify health
```

## Service Restart

Only restart services whose code, configuration, or dependencies changed.
Do not enable timers or schedulers without separate authorization
(Operational Activation Gate 6).

## Error Handling

| Symptom | Action |
|---------|--------|
| Dirty working tree | Stash or commit before deployment; never deploy over dirty state |
| SHA not found locally | `git fetch origin` to retrieve |
| Remote mismatch | Verify origin URL; update if authorized |
| Insufficient disk | Free space or abort deployment |
| Health check fails | Roll back to prior SHA immediately |
