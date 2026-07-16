# Exact-SHA Deployment Checklist

Use this checklist for every VPS deployment. Do not skip steps.

## Pre-deployment

- [ ] Approved SHA recorded in CONTROL.md
- [ ] Deployment Readiness Gate (Gate 4) or VPS Deployment Gate (Gate 5) passed
- [ ] VPS capacity confirmed (<85% disk, >1 GB free)
- [ ] Backup/restore drill completed (if database involved)
- [ ] Rollback SHA recorded (the currently deployed SHA)
- [ ] Working tree is clean
- [ ] Remote origin matches expected URL
- [ ] State directory exists and has sufficient space

## Deployment

- [ ] `git fetch origin` — fetch without merging
- [ ] `git checkout <approved-sha>` — check out exact SHA (not branch)
- [ ] Verify HEAD matches approved SHA
- [ ] Verify working tree is still clean
- [ ] Apply configuration changes (only if separately authorized)
- [ ] Restart affected services (only if authorized)
- [ ] Run project health check

## Post-deployment

- [ ] Old SHA recorded (rollback target)
- [ ] New SHA recorded
- [ ] Validation result recorded
- [ ] Health check passes
- [ ] Services running
- [ ] No unexpected disk growth

## Rollback (if health check fails)

- [ ] `git checkout <rollback-sha>`
- [ ] Restart services
- [ ] Verify health
- [ ] Record rollback in evidence log

## Fields

| Field | Value |
|-------|-------|
| Repository | |
| Approved SHA | |
| Previous SHA | |
| Deployed SHA | |
| Deployed at (UTC) | |
| Deployed by | |
| Health result | |
| Rollback needed? | |
