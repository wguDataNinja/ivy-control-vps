"""Tests for validate_db_health_fixture.py — health fixture validation."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.validate_db_health_fixture import validate_health_fixture


class TestValidateHealthFixture:
    def test_valid_ok(self):
        data = {
            'project': 'test',
            'workflow': 'daily_ingest',
            'run_id': '550e8400-e29b-41d4-a716-446655440000',
            'status': 'ok',
            'started_at': '2026-07-15T07:00:00Z',
            'finished_at': '2026-07-15T07:05:00Z',
            'last_success_at': '2026-07-15T07:05:00Z',
            'deployed_revision': 'abc123def456abc123def456abc123def456abc1',
            'incident_state': 'none',
        }
        errors = validate_health_fixture(data)
        assert errors == []

    def test_valid_warn(self):
        data = {
            'project': 'test',
            'workflow': 'daily_ingest',
            'run_id': '550e8400-e29b-41d4-a716-446655440000',
            'status': 'warn',
            'started_at': '2026-07-15T07:00:00Z',
            'finished_at': '2026-07-15T07:05:00Z',
            'last_success_at': '2026-07-14T07:05:00Z',
            'deployed_revision': 'abc123d',
            'incident_state': 'active',
        }
        errors = validate_health_fixture(data)
        assert errors == []

    def test_missing_required_fields(self):
        errors = validate_health_fixture({'status': 'ok'})
        assert len(errors) >= 7

    def test_invalid_status(self):
        data = {
            'project': 'test',
            'workflow': 'daily_ingest',
            'run_id': 'x',
            'status': 'invalid',
            'started_at': 'x',
            'finished_at': 'x',
            'last_success_at': 'x',
            'deployed_revision': 'abc',
            'incident_state': 'none',
        }
        errors = validate_health_fixture(data)
        assert any('Invalid status' in e for e in errors)

    def test_invalid_incident_state(self):
        data = {
            'project': 'test',
            'workflow': 'daily_ingest',
            'run_id': 'x',
            'status': 'ok',
            'started_at': 'x',
            'finished_at': 'x',
            'last_success_at': 'x',
            'deployed_revision': 'abc',
            'incident_state': 'unknown',
        }
        errors = validate_health_fixture(data)
        assert any('Invalid incident_state' in e for e in errors)

    def test_invalid_deployed_revision(self):
        data = {
            'project': 'test',
            'workflow': 'daily_ingest',
            'run_id': 'x',
            'status': 'ok',
            'started_at': 'x',
            'finished_at': 'x',
            'last_success_at': 'x',
            'deployed_revision': 'not-a-valid-sha!!!',
            'incident_state': 'none',
        }
        errors = validate_health_fixture(data)
        assert any('deployed_revision' in e for e in errors)

    def test_none_deployed_revision(self):
        data = {
            'project': 'test',
            'workflow': 'daily_ingest',
            'run_id': 'x',
            'status': 'ok',
            'started_at': 'x',
            'finished_at': 'x',
            'last_success_at': 'x',
            'deployed_revision': 'None',
            'incident_state': 'none',
        }
        errors = validate_health_fixture(data)
        assert errors == []

    def test_prohibited_local_path(self):
        data = {
            'project': 'test',
            'workflow': 'daily_ingest',
            'run_id': 'x',
            'status': 'ok',
            'started_at': 'x',
            'finished_at': 'x',
            'last_success_at': 'x',
            'deployed_revision': 'abc',
            'incident_state': 'none',
            'description': 'see /Users/buddy/projects/test for details',
        }
        errors = validate_health_fixture(data)
        assert any('Prohibited content' in e for e in errors)

    def test_prohibited_ip(self):
        data = {
            'project': 'test',
            'workflow': 'daily_ingest',
            'run_id': 'x',
            'status': 'ok',
            'started_at': 'x',
            'finished_at': 'x',
            'last_success_at': 'x',
            'deployed_revision': 'abc',
            'incident_state': 'none',
            'host': '192.168.1.1',
        }
        errors = validate_health_fixture(data)
        assert any('Prohibited content' in e for e in errors)
