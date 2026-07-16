#!/usr/bin/env python3
"""Health fixture validation — verify that a health JSON output or fixture
matches the canonical health contract schema."""

import os
import sys
import json
import re


REQUIRED_FIELDS = {'project', 'workflow', 'run_id', 'status', 'started_at', 'finished_at', 'last_success_at', 'deployed_revision', 'incident_state'}
ALLOWED_STATUSES = {'ok', 'warn', 'fail', 'skip'}
ALLOWED_INCIDENT_STATES = {'none', 'active', 'resolved'}
PROHIBITED_PATTERNS = [
    re.compile(r'/Users/[^/\s]+(?:/[^\s]*)*'),
    re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    re.compile(r'(?i)(?:api[_-]?key|token|secret|password|credential)\s*[=:]\s*\S+'),
    re.compile(r'(?i)(?:sk-[a-zA-Z0-9]{20,}|pk-[a-zA-Z0-9]{20,})'),
]


def validate_health_fixture(data: dict) -> list[str]:
    errors = []

    for key in REQUIRED_FIELDS:
        if key not in data:
            errors.append(f"Missing required field: {key}")

    status = data.get('status')
    if status and status not in ALLOWED_STATUSES:
        errors.append(f"Invalid status '{status}'; must be one of {ALLOWED_STATUSES}")

    incident = data.get('incident_state')
    if incident and incident not in ALLOWED_INCIDENT_STATES:
        errors.append(f"Invalid incident_state '{incident}'; must be one of {ALLOWED_INCIDENT_STATES}")

    deployed = data.get('deployed_revision')
    if deployed and not re.match(r'^[a-f0-9]{7,40}$', str(deployed)) and str(deployed) != 'None':
        errors.append(f"deployed_revision '{deployed}' is not a valid SHA or None")

    raw = json.dumps(data)
    for pattern in PROHIBITED_PATTERNS:
        matches = pattern.findall(raw)
        if matches:
            errors.append(f"Prohibited content detected matching {pattern.pattern}: {matches[:3]}")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_db_health_fixture.py <health.json> [health.json ...]", file=sys.stderr)
        sys.exit(1)

    exit_code = 0
    for path in sys.argv[1:]:
        if not os.path.isfile(path):
            print(f"ERROR: {path} not found", file=sys.stderr)
            exit_code = 1
            continue
        with open(path) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"ERROR: {path} — JSON parse error: {e}", file=sys.stderr)
                exit_code = 1
                continue

        errors = validate_health_fixture(data)
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
