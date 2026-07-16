"""Tests for validate_db_manifest.py — manifest schema validation."""

import os
import sys
import tempfile
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.validate_db_manifest import validate_manifest


VALID_MANIFEST = {
    'project_slug': 'test_project',
    'repository': {
        'local_path': '/Users/buddy/projects/test_project',
        'remote': 'github.com/test/test',
        'branch': 'main',
        'reviewed_sha': 'abc123def456abc123def456abc123def456abc1',
    },
    'database': {
        'name': 'test_project',
        'owner_role': 'test_project_owner',
        'schemas': [
            {'name': 'app', 'owner_role': 'test_project_owner'},
            {'name': 'health', 'owner_role': 'test_project_owner'},
        ],
    },
    'roles': {
        'owner': {'name': 'test_project_owner', 'login': False, 'applies': True},
        'migrator': {'name': 'test_project_migrator', 'login': True, 'applies': True},
        'writer': {'name': 'test_project_writer', 'login': True, 'applies': True},
        'reader': {'name': 'test_project_reader', 'login': True, 'applies': True},
        'monitor': {'name': 'test_project_monitor', 'login': True, 'applies': True},
        'backup': {'name': 'test_project_backup', 'login': True, 'applies': True},
    },
    'environment': {
        'env_example': 'deploy/env.example',
        'vps_env_path': '/home/scraper/config/test.env',
        'required_variables': ['TEST_PG_URL'],
    },
    'migrations': {
        'directory': 'db/migrations',
        'expected_count': 5,
        'validation_directory': 'db/migrations/validation',
        'rollback_directory': 'db/migrations/rollback',
    },
    'backup': {
        'command': 'scripts/backup.sh',
        'output_root': '/home/scraper/backups/postgres/test',
    },
    'health': {
        'workflow_id': 'test_project/daily_ingest',
        'producer_or_adapter': 'scripts/health_export.py',
    },
    'rollback': {
        'source_authority_fallback': 'previous_service',
        'database_rollback': 'rollback SQL',
    },
    'evidence': {
        'output_dir': '_internal/outbox/session-N/evidence',
    },
}


class TestValidateManifest:
    def test_valid_manifest(self):
        errors = validate_manifest(VALID_MANIFEST)
        assert errors == []

    def test_missing_top_level(self):
        data = dict(VALID_MANIFEST)
        del data['project_slug']
        errors = validate_manifest(data)
        assert any('Missing top-level key: project_slug' in e for e in errors)

    def test_missing_multiple_top_level(self):
        data = dict(VALID_MANIFEST)
        del data['project_slug']
        del data['backup']
        errors = validate_manifest(data)
        assert any('project_slug' in e for e in errors)
        assert any('backup' in e for e in errors)

    def test_missing_repository_fields(self):
        data = dict(VALID_MANIFEST)
        del data['repository']['local_path']
        errors = validate_manifest(data)
        assert any('repository.local_path' in e for e in errors)

    def test_missing_database_fields(self):
        data = dict(VALID_MANIFEST)
        del data['database']['name']
        errors = validate_manifest(data)
        assert any('database.name' in e for e in errors)

    def test_missing_schema_fields(self):
        data = dict(VALID_MANIFEST)
        del data['database']['schemas'][0]['owner_role']
        errors = validate_manifest(data)
        assert any('database.schemas[0]' in e for e in errors)

    def test_invalid_schema_name(self):
        data = dict(VALID_MANIFEST)
        data['database']['schemas'][0]['name'] = 'App-Schema'
        errors = validate_manifest(data)
        assert any('snake_case' in e for e in errors)

    def test_missing_role_field(self):
        data = dict(VALID_MANIFEST)
        del data['roles']['owner']['login']
        errors = validate_manifest(data)
        assert any('roles.owner' in e for e in errors)

    def test_invalid_role_name(self):
        data = dict(VALID_MANIFEST)
        data['roles']['owner']['name'] = 'test_project_admin'
        errors = validate_manifest(data)
        assert any('owner pattern' in e for e in errors)

    def test_missing_environment_field(self):
        data = dict(VALID_MANIFEST)
        del data['environment']['vps_env_path']
        errors = validate_manifest(data)
        assert any('environment.vps_env_path' in e for e in errors)

    def test_schemas_not_list(self):
        data = dict(VALID_MANIFEST)
        data['database']['schemas'] = 'not a list'
        errors = validate_manifest(data)
        assert any('must be a list' in e for e in errors)

    def test_empty_manifest(self):
        errors = validate_manifest({})
        assert len(errors) >= 10

    def test_prohibited_content_detected(self):
        data = dict(VALID_MANIFEST)
        data['backup']['command'] = 'pg_dump --password=secret123'
        errors = validate_manifest(data)
        assert any('Prohibited content' in e for e in errors)
