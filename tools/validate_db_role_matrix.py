#!/usr/bin/env python3
"""Role-matrix completeness check — verify that all required role fields are present for applicable roles."""

import os
import sys
import re
import yaml


ROLE_NAMES = {'owner', 'migrator', 'writer', 'reader', 'monitor', 'backup'}
REQUIRED_ROLE_FIELDS = {'name', 'login', 'applies'}
ROLE_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]*_(owner|migrator|writer|reader|monitor|backup)$')
ROLE_APPLICABLE_POSITIVE_FIELDS = {'name', 'positive_permissions', 'negative_permissions'}


def validate_role_matrix(data: dict) -> list[str]:
    errors = []
    roles = data.get('roles', {})

    for role_name in ROLE_NAMES:
        if role_name not in roles:
            errors.append(f"Missing role class: '{role_name}'")
            continue

        role = roles[role_name]
        for field in REQUIRED_ROLE_FIELDS:
            if field not in role:
                errors.append(f"roles.{role_name} missing field '{field}'")

        if role.get('name'):
            if not ROLE_NAME_PATTERN.match(role['name']):
                errors.append(f"roles.{role_name}.name '{role['name']}' does not match naming pattern")

        if role.get('applies') is True:
            if role.get('login') is None:
                errors.append(f"roles.{role_name}.login must be set when applies=true")
            if role_name == 'owner' and role.get('login') is not False:
                errors.append(f"roles.{role_name}.login must be false (owner is NOLOGIN)")

    applicable_count = sum(1 for r in roles.values() if isinstance(r, dict) and r.get('applies') is True)
    if applicable_count == 0:
        errors.append("No roles have applies: true — at minimum owner must apply if a database exists")

    matrix = data.get('privilege_matrix', data.get('matrix', None))
    if matrix:
        applicable_roles = [r for r in roles.values() if isinstance(r, dict) and r.get('applies') is True]
        for role in applicable_roles:
            role_name = role.get('name', 'unknown')
            if role_name not in matrix:
                errors.append(f"Privilege matrix missing entry for '{role_name}'")
            else:
                entry = matrix[role_name]
                if not entry.get('positive', []) and not entry.get('negative', []):
                    errors.append(f"Privilege matrix for '{role_name}' has no positive or negative permissions")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_db_role_matrix.py <manifest.yaml>", file=sys.stderr)
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

        errors = validate_role_matrix(data)
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
