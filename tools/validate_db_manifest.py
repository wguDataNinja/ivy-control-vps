#!/usr/bin/env python3
"""Manifest schema validation — check a YAML onboarding manifest against the required schema."""

import os
import sys
import re
import yaml


REQUIRED_TOP_LEVEL = {'project_slug', 'repository', 'database', 'roles', 'environment', 'migrations', 'backup', 'health', 'rollback', 'evidence'}
REQUIRED_REPOSITORY = {'local_path', 'remote', 'branch', 'reviewed_sha'}
REQUIRED_DATABASE = {'name', 'owner_role', 'schemas'}
REQUIRED_SCHEMA = {'name', 'owner_role'}
ROLE_NAMES = {'owner', 'migrator', 'writer', 'reader', 'monitor', 'backup'}
REQUIRED_ROLE = {'name', 'login', 'applies'}
REQUIRED_ENVIRONMENT = {'env_example', 'vps_env_path', 'required_variables'}
REQUIRED_MIGRATIONS = {'directory', 'expected_count'}
REQUIRED_BACKUP = {'command', 'output_root'}
REQUIRED_HEALTH = {'workflow_id'}
REQUIRED_ROLLBACK = {'source_authority_fallback', 'database_rollback'}
REQUIRED_EVIDENCE = {'output_dir'}

PROHIBITED_PATTERNS = [
    re.compile(r'(?i)(?:password|secret|api[_-]?key|token)[_\w]*\s*[=:]\s*\S+'),
    re.compile(r'(?:sk-[a-zA-Z0-9]{20,}|pk-[a-zA-Z0-9]{20,})'),
    re.compile(r'/home/(?!scraper/)[^/]+/\S*'),
    re.compile(r'(?:postgresql://\S+:\S+@)'),
]


def validate_manifest(data: dict, path: str = "<manifest>") -> list[str]:
    errors = []

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            errors.append(f"Missing top-level key: {key}")

    for key in REQUIRED_REPOSITORY:
        if key not in data.get('repository', {}):
            errors.append(f"Missing repository.{key}")

    db = data.get('database', {})
    for key in REQUIRED_DATABASE:
        if key not in db:
            errors.append(f"Missing database.{key}")

    schemas = db.get('schemas', [])
    if not isinstance(schemas, list):
        errors.append("database.schemas must be a list")
    else:
        for i, s in enumerate(schemas):
            for key in REQUIRED_SCHEMA:
                if key not in s:
                    errors.append(f"database.schemas[{i}] missing '{key}'")
            if 'name' in s and not re.match(r'^[a-z][a-z0-9_]*$', s['name']):
                errors.append(f"database.schemas[{i}].name '{s['name']}' must be lowercase snake_case")

    roles = data.get('roles', {})
    for role_name in ROLE_NAMES:
        role = roles.get(role_name, {})
        for key in REQUIRED_ROLE:
            if key not in role:
                errors.append(f"roles.{role_name} missing '{key}'")
        if role.get('name') and not re.match(r'^[a-z][a-z0-9_]*_(owner|migrator|writer|reader|monitor|backup)$', role['name']):
            errors.append(f"roles.{role_name}.name '{role['name']}' does not match {role_name} pattern")

    for key in REQUIRED_ENVIRONMENT:
        if key not in data.get('environment', {}):
            errors.append(f"Missing environment.{key}")

    for key in REQUIRED_MIGRATIONS:
        if key not in data.get('migrations', {}):
            errors.append(f"Missing migrations.{key}")

    for key in REQUIRED_BACKUP:
        if key not in data.get('backup', {}):
            errors.append(f"Missing backup.{key}")

    for key in REQUIRED_HEALTH:
        if key not in data.get('health', {}):
            errors.append(f"Missing health.{key}")

    for key in REQUIRED_ROLLBACK:
        if key not in data.get('rollback', {}):
            errors.append(f"Missing rollback.{key}")

    for key in REQUIRED_EVIDENCE:
        if key not in data.get('evidence', {}):
            errors.append(f"Missing evidence.{key}")

    for pattern in PROHIBITED_PATTERNS:
        raw = yaml.dump(data)
        matches = pattern.findall(raw)
        if matches:
            errors.append(f"Prohibited content detected matching {pattern.pattern}: {matches[:3]}")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_db_manifest.py <manifest.yaml> [manifest.yaml ...]", file=sys.stderr)
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
        if not isinstance(data, dict):
            print(f"ERROR: {path} — not a YAML mapping", file=sys.stderr)
            exit_code = 1
            continue
        errors = validate_manifest(data, path)
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
