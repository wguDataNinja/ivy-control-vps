#!/usr/bin/env python3
"""Restore-packet completeness check — verify that an isolated restore packet
has all required fields and evidence."""

import os
import sys
import re
import yaml


REQUIRED_RESTORE_FIELDS = {'prerequisites', 'temp_database', 'restore_procedure', 'validation_queries', 'cleanup_procedure', 'stop_conditions'}
REQUIRED_EVIDENCE_FIELDS = {'dump_file', 'checksum', 'temp_database', 'validation_passed', 'cleanup_packet_ready'}
TEMP_DB_PATTERN = re.compile(r'^[a-z][a-z0-9_]*_restore_[a-z0-9_]+_\d{14}$')


def validate_restore_packet(data: dict) -> list[str]:
    errors = []
    restore = data.get('restore_evidence', data)

    for key in REQUIRED_EVIDENCE_FIELDS:
        if key not in restore:
            errors.append(f"Missing evidence field: {key}")

    temp_db = restore.get('temp_database', '')
    if temp_db and not TEMP_DB_PATTERN.match(temp_db):
        errors.append(f"temp_database '{temp_db}' does not match pattern project_restore_operator_yyyymmddhhmmss")
    if temp_db and temp_db.count('_restore_') != 1:
        errors.append(f"temp_database '{temp_db}' must contain exactly one '_restore_' segment")

    if restore.get('validation_passed') is not True:
        errors.append("validation_passed must be true before cleanup")

    if restore.get('cleanup_completed_at'):
        if not restore.get('cleanup_packet_ready'):
            errors.append("cleanup_packet_ready should be true before cleanup_completed_at is set")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_db_restore_packet.py <evidence.yaml>", file=sys.stderr)
        sys.exit(1)

    exit_code = 0
    for path in sys.argv[1:]:
        if not os.path.isfile(path):
            print(f"ERROR: {path} not found", file=sys.stderr)
            exit_code = 1
            continue
        with open(path) as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"ERROR: {path} — YAML parse error: {e}", file=sys.stderr)
                exit_code = 1
                continue

        errors = validate_restore_packet(data)
        if errors:
            print(f"FAIL: {path}")
            for e in errors:
                print(f"  - {e}")
            exit_code = 1
        else:
            print(f"PASS: {path}")

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
