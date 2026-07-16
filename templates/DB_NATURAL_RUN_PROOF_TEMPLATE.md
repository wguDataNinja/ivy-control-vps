# Natural-Run Proof Template

**Purpose:** Document evidence that a genuine scheduled or event-triggered
production run completed successfully after PostgreSQL onboarding.

---

## 1. Run identity

```yaml
natural_run:
  project: <project_slug>
  workflow: <workflow_name>
  run_id: <uuid_or_sequence_number>
  trigger: <systemd_timer | cron | event>
  timer_name: <project>-<role>-<action>.timer
  service_name: <project>-<role>-<action>.service
  scheduled_time: <yyyymmddThhmmssZ>
  actual_start: <yyyymmddThhmmssZ>
  actual_finish: <yyyymmddThhmmssZ>
  exit_code: 0
```

## 2. Proof of natural trigger

- [ ] Timer was enabled and active before the run (not manually started).
- [ ] Systemd journal shows `TriggeredBy: timer` for the service unit.
- [ ] No manual `systemctl start` was used as substitute.

```bash
# Capture timer state before run
systemctl --user list-timers --all | grep <project>

# Capture trigger source from journal
journalctl --user -u <service_name> --no-pager | grep -i trigger

# Capture run start from journal
journalctl --user -u <service_name> --no-pager | grep "Started\|Starting"
```

## 3. Run results

```yaml
results:
  status: <success | partial | failed>
  records_processed: <N>
  records_inserted: <N>
  records_updated: <N>
  errors: <count>
  error_details:
    - target: <name>
      error: <type>
      expected: true/false
  health_status_after: <ok | warn | fail>
```

## 4. Health verification

```yaml
health_after_run:
  status: ok
  last_success_at: <timestamp>
  run_id: <run_id>
  deployed_revision: <sha>
  schema_version: <version>
  backup_state: ok
```

## 5. Distinction from manual run

```yaml
manual_run_substitution_prevented: true
verification:
  - timer was enabled before run start
  - timer was not disabled after run
  - no manual service start commands in journal
  - health shows timer as active scheduler
```

## 6. Evidence record

```yaml
evidence:
  timer_status_capture: <path>
  journal_trigger_capture: <path>
  health_output: <path>
  run_manifest: <path>
  evidence_recorded_by: <agent>
  date: <yyyymmdd>
```
