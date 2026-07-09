#!/usr/bin/env python3
"""Validate health contract examples against the JSON Schema.

Usage:
    python3 docs/health/examples/test_validate_schema.py

Returns exit code 0 if all examples pass, 1 if any fail.
"""

import json
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "portfolio_health_schema.json"

REQUIRED_CORE_FIELDS = {
    "contract_version", "generated_at", "project", "workflow", "workflow_id",
    "run_id", "status", "started_at", "finished_at", "last_success_at",
    "expected_cadence_seconds", "freshness_seconds", "deployed_revision",
    "scheduler_state", "backup_state", "incident_state",
}

OPTIONAL_PRODUCER_FIELDS = {
    "records_read", "records_written", "records_rejected", "backlog",
    "retry_count", "error_class", "schema_version", "migration_version",
    "backup_age_seconds", "storage_bytes", "storage_growth_bytes_24h",
    "database_size_bytes", "data_directory_size_bytes", "prune_status",
    "heartbeat_at", "disk_free_bytes", "disk_usage_pct", "producer_version",
    "project_environment",
}

OPERATOR_ONLY_FIELDS = {"error_code", "error_message_private"}

DERIVED_AGGREGATOR_FIELDS = {
    "degraded_reason_code", "heartbeat_age_seconds", "volume_24h",
    "growth_rate_24h", "growth_rate_7d", "retention_boundary_proximity",
    "last_failure_at", "failure_count", "drift_state",
}

PUBLIC_FIELDS = {
    "contract_version", "generated_at", "project", "workflow", "status",
    "last_success_at", "expected_cadence_seconds", "freshness_seconds",
    "volume_24h", "incident", "backup_state", "migration_version",
}


def load_json(path):
    with open(path) as f:
        return json.load(f)


def validate_example(example_data, schema):
    """Basic structural validation without a JSON Schema library.

    We check: all required fields present, enum values valid, types correct.
    This avoids introducing a new dependency (jsonschema) solely for this task.
    """
    errors = []
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    # Check required fields — field must be present (may be null if nullable)
    for field in required:
        if field not in example_data:
            errors.append(f"Missing required field: {field}")

    # Check enum values
    for field_name, field_schema in properties.items():
        if field_name not in example_data:
            continue
        value = example_data[field_name]
        enum_vals = field_schema.get("enum")
        if enum_vals is not None and value is not None and value not in enum_vals:
            errors.append(f"Field '{field_name}' has invalid enum value: {value}")

    # Check type constraints
    for field_name, field_schema in properties.items():
        if field_name not in example_data:
            continue
        value = example_data[field_name]
        if value is None:
            expected_type = field_schema.get("type")
            if isinstance(expected_type, list):
                if "null" not in expected_type:
                    errors.append(f"Field '{field_name}' is null but null is not allowed")
            elif expected_type == "object":
                pass  # object allows null in practice
            continue
        expected_type = field_schema.get("type")
        if expected_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(f"Field '{field_name}' should be integer, got {type(value).__name__}")
        elif expected_type == "string":
            if not isinstance(value, str):
                errors.append(f"Field '{field_name}' should be string, got {type(value).__name__}")
        elif expected_type == "number":
            if not isinstance(value, (int, float)):
                errors.append(f"Field '{field_name}' should be number, got {type(value).__name__}")
        elif expected_type == "boolean":
            if not isinstance(value, bool):
                errors.append(f"Field '{field_name}' should be boolean, got {type(value).__name__}")

    # Check minimum constraints
    for field_name, field_schema in properties.items():
        if field_name not in example_data or example_data[field_name] is None:
            continue
        value = example_data[field_name]
        minimum = field_schema.get("minimum")
        maximum = field_schema.get("maximum")
        if minimum is not None and isinstance(value, (int, float)):
            if value < minimum:
                errors.append(f"Field '{field_name}' value {value} is below minimum {minimum}")
        if maximum is not None and isinstance(value, (int, float)):
            if value > maximum:
                errors.append(f"Field '{field_name}' value {value} is above maximum {maximum}")

    # Check regex patterns
    for field_name, field_schema in properties.items():
        if field_name not in example_data or example_data[field_name] is None:
            continue
        pattern = field_schema.get("pattern")
        if pattern and isinstance(example_data[field_name], str):
            import re
            if not re.match(pattern, example_data[field_name]):
                errors.append(f"Field '{field_name}' does not match pattern {pattern}")

    # Check conditional requirements: fail status requires error_class
    if example_data.get("status") == "fail" and not example_data.get("error_class"):
        errors.append("Status 'fail' requires error_class")

    # Check conditional requirements: running status requires started_at
    if example_data.get("status") == "running" and not example_data.get("started_at"):
        errors.append("Status 'running' requires started_at")

    return errors


def check_prohibited_fields(data, prohibited):
    """Check that no prohibited fields appear in sanitized public output."""
    found = [f for f in data if f in prohibited]
    return found


def build_minimal_valid():
    """Build a minimal valid payload with all required fields."""
    return {
        "contract_version": 2,
        "generated_at": "2026-07-08T12:00:00Z",
        "project": "test",
        "workflow": "test_workflow",
        "workflow_id": "test/test_workflow",
        "run_id": "00000000-0000-0000-0000-000000000001",
        "status": "ok",
        "started_at": "2026-07-08T11:55:00Z",
        "finished_at": "2026-07-08T11:58:00Z",
        "last_success_at": "2026-07-08T11:58:00Z",
        "expected_cadence_seconds": 3600,
        "freshness_seconds": 120,
        "deployed_revision": "abc1234",
        "scheduler_state": "active",
        "backup_state": "ok",
        "incident_state": "none",
    }


def test_missing_required():
    """Each required field individually removed should cause failure."""
    schema = load_json(SCHEMA_PATH)
    required = schema.get("required", [])
    passed = 0
    failed = 0
    for field in required:
        payload = build_minimal_valid()
        del payload[field]
        errors = validate_example(payload, schema)
        if errors:
            passed += 1
        else:
            print(f"  FAIL: Missing required '{field}' was not detected")
            failed += 1
    return failed == 0, passed, failed


def test_invalid_enum():
    """Invalid enum values should be rejected."""
    schema = load_json(SCHEMA_PATH)
    payload = build_minimal_valid()
    errors = []

    # Invalid status
    payload["status"] = "unknown_status"
    errs = validate_example(payload, schema)
    if not any("invalid enum" in e for e in errs):
        errors.append("Invalid status 'unknown_status' was not rejected")

    # Invalid backup_state
    payload = build_minimal_valid()
    payload["backup_state"] = "invalid_backup"
    errs = validate_example(payload, schema)
    if not any("invalid enum" in e for e in errs):
        errors.append("Invalid backup_state was not rejected")

    # Invalid incident_state
    payload = build_minimal_valid()
    payload["incident_state"] = "maybe"
    errs = validate_example(payload, schema)
    if not any("invalid enum" in e for e in errs):
        errors.append("Invalid incident_state was not rejected")

    return errors


def test_nullable_required():
    """Required fields that are nullable should accept null (field must exist but value can be null)."""
    schema = load_json(SCHEMA_PATH)
    payload = build_minimal_valid()

    # Nullable required fields: value must be null, but key must be present
    payload["finished_at"] = None       # run still in progress
    payload["last_success_at"] = None   # first run, no prior success
    payload["deployed_revision"] = None # not yet tracked
    payload["scheduler_state"] = None
    payload["backup_state"] = None      # no backup configured

    errors = validate_example(payload, schema)
    return errors  # Empty = pass — null is acceptable for nullable required fields


def test_unknown_extension():
    """Unknown fields should pass through without error."""
    schema = load_json(SCHEMA_PATH)
    payload = build_minimal_valid()
    payload["unknown_field"] = "some_value"
    payload["another_unknown"] = 42
    errors = validate_example(payload, schema)
    return errors  # Empty = pass (additionalProperties: true)


def test_unsupported_contract_version():
    """Contract version other than 2 should be flagged."""
    schema = load_json(SCHEMA_PATH)
    payload = build_minimal_valid()
    payload["contract_version"] = 1
    errors = validate_example(payload, schema)
    # Schema says minimum: 2, maximum: 2
    if not any("below minimum" in e or "above maximum" in e for e in errors):
        return ["Contract version 1 was not rejected"]
    payload["contract_version"] = 3
    errors = validate_example(payload, schema)
    if not any("above maximum" in e for e in errors):
        return ["Contract version 3 was not rejected"]
    return []


def test_fail_requires_error_class():
    """Status 'fail' without error_class key should be rejected (absent key, not null value)."""
    schema = load_json(SCHEMA_PATH)
    payload = build_minimal_valid()
    payload["status"] = "fail"
    payload.pop("error_class", None)  # key entirely absent
    errors = validate_example(payload, schema)
    if not any("error_class" in e for e in errors):
        return ["Status 'fail' without error_class key was not rejected"]
    return []


def test_public_excludes_operator_fields():
    """Public projection must exclude operator-only fields."""
    public_example = load_json(EXAMPLES_DIR / "healthy-reddit-ops-public.json")
    operator_fields = ["error_code", "error_message_private", "error_message",
                       "raw_payload", "filesystem_path", "credential"]
    found = [f for f in operator_fields if f in public_example]
    if found:
        return [f"Public example contains operator-only fields: {found}"]
    return []


def test_running_requires_started_at():
    """Status 'running' without started_at key should be rejected."""
    schema = load_json(SCHEMA_PATH)
    payload = build_minimal_valid()
    payload["status"] = "running"
    payload.pop("started_at", None)  # key entirely absent
    errors = validate_example(payload, schema)
    if not any("started_at" in e for e in errors):
        return ["Status 'running' without started_at key was not rejected"]
    return []


def test_freshness_boundaries():
    """Test that freshness values at boundaries pass."""
    schema = load_json(SCHEMA_PATH)
    payload = build_minimal_valid()
    payload["freshness_seconds"] = 0
    errors = validate_example(payload, schema)
    if errors:
        return [f"Freshness 0 should be valid: {errors}"]

    payload["freshness_seconds"] = 999999999
    errors = validate_example(payload, schema)
    if errors:
        return [f"Freshness high value should be valid: {errors}"]

    return []


def test_canonical_field_inventory():
    """The v2 contract has exactly 46 current fields with no double-counting."""
    schema = load_json(SCHEMA_PATH)
    properties = set(schema.get("properties", {})) - {"metadata"}
    classified = (
        REQUIRED_CORE_FIELDS
        | OPTIONAL_PRODUCER_FIELDS
        | OPERATOR_ONLY_FIELDS
        | DERIVED_AGGREGATOR_FIELDS
    )
    errors = []
    if len(classified) != 46:
        errors.append(f"Expected 46 classified fields, found {len(classified)}")
    if properties != classified:
        errors.append(f"Schema/classification mismatch: {sorted(properties ^ classified)}")
    overlap_count = (
        len(REQUIRED_CORE_FIELDS)
        + len(OPTIONAL_PRODUCER_FIELDS)
        + len(OPERATOR_ONLY_FIELDS)
        + len(DERIVED_AGGREGATOR_FIELDS)
    )
    if overlap_count != len(classified):
        errors.append("Field ownership classifications overlap")
    required = set(schema.get("required", []))
    if required != REQUIRED_CORE_FIELDS:
        errors.append(f"Required schema mismatch: {sorted(required ^ REQUIRED_CORE_FIELDS)}")
    return errors


def run_negative_tests():
    """Run all negative/edge-case tests and report results."""
    tests = [
        ("Missing required fields", test_missing_required),
        ("Invalid enum values", test_invalid_enum),
        ("Nullable required fields", test_nullable_required),
        ("Unknown extension fields", test_unknown_extension),
        ("Unsupported contract version", test_unsupported_contract_version),
        ("Fail requires error_class", test_fail_requires_error_class),
        ("Public excludes operator fields", test_public_excludes_operator_fields),
        ("Running requires started_at", test_running_requires_started_at),
        ("Freshness boundaries", test_freshness_boundaries),
        ("Canonical field inventory", test_canonical_field_inventory),
    ]

    all_passed = True
    for name, test_fn in tests:
        result = test_fn()
        if isinstance(result, tuple):
            ok, passed, failed = result
            if ok:
                print(f"PASS: {name} ({passed}/{passed + failed} checks passed)")
            else:
                all_passed = False
                print(f"FAIL: {name} ({passed}/{passed + failed} checks passed)")
        elif isinstance(result, list):
            if not result:
                print(f"PASS: {name}")
            else:
                all_passed = False
                print(f"FAIL: {name}")
                for err in result:
                    print(f"  - {err}")
        else:
            if result:
                print(f"PASS: {name}")
            else:
                all_passed = False
                print(f"FAIL: {name}")

    return all_passed


def main():
    schema = load_json(SCHEMA_PATH)
    prohibited = schema.get("prohibited", [])

    print("=== EXAMPLE VALIDATION ===")
    example_files = sorted(EXAMPLES_DIR.glob("*.json"))
    if not example_files:
        print("FAIL: No example JSON files found")
        return 1

    all_passed = True
    for example_path in example_files:
        name = example_path.name
        data = load_json(example_path)
        errors = []

        # Public examples are intentionally a subset — check only prohibited fields
        if "public" in name:
            unknown_public = [f for f in data if f not in PUBLIC_FIELDS]
            if unknown_public:
                errors.append(f"Public example contains non-public fields: {unknown_public}")
            found_prohibited = check_prohibited_fields(data, prohibited)
            if found_prohibited:
                errors.append(f"Public example contains prohibited fields: {found_prohibited}")
            missing_required_public = [
                f for f in ["project", "workflow", "status", "last_success_at",
                            "expected_cadence_seconds", "freshness_seconds", "backup_state"]
                if f not in data
            ]
            if missing_required_public:
                errors.append(f"Public example missing expected fields: {missing_required_public}")
        else:
            errors = validate_example(data, schema)
            # Producer payloads legitimately include operator-only fields like
            # error_message_private. The prohibited list applies to public
            # projection only, not to producer payloads validated here.

        if errors:
            all_passed = False
            print(f"FAIL: {name}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"PASS: {name}")

    print()
    print("=== NEGATIVE / EDGE-CASE TESTS ===")
    negative_ok = run_negative_tests()

    if not negative_ok:
        all_passed = False

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
