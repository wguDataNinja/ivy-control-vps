#!/usr/bin/env python3
"""Required migration file check — verify that each forward migration has matching rollback and validation files."""

import os
import sys
import re


MIGRATION_PATTERN = re.compile(r'^(\d{8}_\d{3}_[a-z0-9_]+)\.sql$')


def check_migration_dir(migration_dir: str, expected_count: int | None = None) -> list[str]:
    errors = []

    rollback_dir = os.path.join(migration_dir, 'rollback')
    validation_dir = os.path.join(migration_dir, 'validation')

    if not os.path.isdir(migration_dir):
        return [f"Migration directory not found: {migration_dir}"]

    forward_files = sorted([
        f for f in os.listdir(migration_dir)
        if f.endswith('.sql') and os.path.isfile(os.path.join(migration_dir, f))
    ])

    if not forward_files:
        return [f"No migration SQL files found in {migration_dir}"]

    if expected_count is not None and len(forward_files) != expected_count:
        errors.append(f"Expected {expected_count} migration files, found {len(forward_files)}")

    for fname in forward_files:
        m = MIGRATION_PATTERN.match(fname)
        if not m:
            errors.append(f"Migration file '{fname}' does not match YYYYMMDD_NNN_description.sql pattern")
            continue

        base = m.group(1)
        rollback_file = f"{base}_down.sql"
        validation_file = f"{base}_check.sql"

        if not os.path.isdir(rollback_dir):
            errors.append(f"Rollback directory missing: {rollback_dir}")
        elif rollback_file not in os.listdir(rollback_dir):
            errors.append(f"Missing rollback for {fname}: expected {rollback_file}")

        if not os.path.isdir(validation_dir):
            errors.append(f"Validation directory missing: {validation_dir}")
        elif validation_file not in os.listdir(validation_dir):
            errors.append(f"Missing validation for {fname}: expected {validation_file}")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_db_migrations.py <migration_dir> [expected_count]", file=sys.stderr)
        sys.exit(1)

    migration_dir = sys.argv[1]
    expected_count = int(sys.argv[2]) if len(sys.argv) > 2 else None

    errors = check_migration_dir(migration_dir, expected_count)
    if errors:
        print(f"FAIL: {migration_dir}")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"PASS: {migration_dir}")
        sys.exit(0)


if __name__ == '__main__':
    main()
