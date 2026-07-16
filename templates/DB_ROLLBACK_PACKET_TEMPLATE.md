# Rollback Packet Template

**Purpose:** Prepare a rollback execution packet that restores prior safe
authority after a failed activation, migration, or cutover. Strong Codex
executes only on failed gate or explicit approval.

---

## 1. Rollback target

```yaml
rollback:
  target_workload: <project_slug>
  rollback_sha: <previous_approved_sha>
  trigger_condition: <failed_gate_or_approved_rollback>
  authority: <Buddy | Strong Codex>
```

## 2. Database rollback

```yaml
database:
  strategy: <rollback_sql | restore_from_backup | preserve>
  details: >
    Apply rollback SQL from migrations in reverse order.
    Or: restore from latest backup dump.
    Or: preserve current state, disable new writer.
  prerequisite: <rollback | restore snapshot>
  evidence_preservation: true
```

## 3. Scheduler rollback

```yaml
scheduler:
  current_active_timer: <project>-<role>-<action>.timer
  rollback_timer: <previous_timer_name>
  steps:
    - disable current timer: systemctl --user disable --now {current_timer}
    - enable rollback timer: systemctl --user enable --now {rollback_timer}
    - verify: systemctl --user is-active {rollback_timer}
```

## 4. Source rollback

```yaml
source:
  checkout_path: /home/scraper/apps/<project>
  current_sha: <sha>
  rollback_sha: <sha>
  deployment_command: git checkout {rollback_sha}
  post_rollback_validation:
    - git rev-parse HEAD matches {rollback_sha}
    - git status is clean
```

## 5. Health rollback verification

```yaml
health_verification:
  - systemctl --user is-active {rollback_service}
  - systemctl --user is-active {rollback_timer}
  - check health output at {health_output_path}
  - confirm single active writer
```

## 6. Evidence preservation

```yaml
evidence:
  pre_rollback_state_capture: <path>
  rollback_commands_log: <path>
  post_rollback_health: <path>
  incident_state: active
  preserved_items:
    - all database state (no deletion)
    - all backup dumps
    - all run logs
```

## 7. Stop conditions

- Rollback would create duplicate writer.
- Rollback target SHA is not documented.
- Data deletion requested without explicit Buddy approval.
- Health verification fails after rollback.
- Evidence capture fails before rollback begins.
