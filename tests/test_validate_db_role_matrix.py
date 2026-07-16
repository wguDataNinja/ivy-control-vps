"""Tests for validate_db_role_matrix.py — role-matrix completeness check."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.validate_db_role_matrix import validate_role_matrix


VALID_MANIFEST = {
    'project_slug': 'test',
    'roles': {
        'owner': {'name': 'test_owner', 'login': False, 'applies': True},
        'migrator': {'name': 'test_migrator', 'login': True, 'applies': True},
        'writer': {'name': 'test_writer', 'login': True, 'applies': True},
        'reader': {'name': 'test_reader', 'login': True, 'applies': True},
        'monitor': {'name': 'test_monitor', 'login': True, 'applies': True},
        'backup': {'name': 'test_backup', 'login': True, 'applies': True},
    },
    'privilege_matrix': {
        'test_owner': {'positive': ['OWNER'], 'negative': ['LOGIN']},
        'test_migrator': {'positive': ['CONNECT', 'DDL'], 'negative': ['SUPERUSER']},
        'test_writer': {'positive': ['CONNECT', 'DML'], 'negative': ['DDL']},
        'test_reader': {'positive': ['CONNECT', 'SELECT'], 'negative': ['INSERT', 'UPDATE', 'DELETE']},
        'test_monitor': {'positive': ['CONNECT', 'SELECT health'], 'negative': ['SELECT app']},
        'test_backup': {'positive': ['CONNECT', 'SELECT'], 'negative': ['WRITE']},
    },
}


class TestValidateRoleMatrix:
    def test_valid_matrix(self):
        errors = validate_role_matrix(VALID_MANIFEST)
        assert errors == []

    def test_missing_role_class(self):
        data = {'roles': {'owner': {'name': 'test_owner', 'login': False, 'applies': True}}}
        errors = validate_role_matrix(data)
        assert any('migrator' in e for e in errors)

    def test_missing_role_field(self):
        data = {
            'roles': {
                'owner': {'name': 'test_owner', 'applies': True},
                'migrator': {'name': 'test_migrator', 'login': True, 'applies': True},
                'writer': {'name': 'test_writer', 'login': True, 'applies': True},
                'reader': {'name': 'test_reader', 'login': True, 'applies': True},
                'monitor': {'name': 'test_monitor', 'login': True, 'applies': True},
                'backup': {'name': 'test_backup', 'login': True, 'applies': True},
            }
        }
        errors = validate_role_matrix(data)
        assert any('login' in e for e in errors)
        assert any('roles.owner' in e for e in errors)

    def test_owner_must_be_nologin(self):
        data = {
            'roles': {
                'owner': {'name': 'test_owner', 'login': True, 'applies': True},
                'migrator': {'name': 'test_migrator', 'login': True, 'applies': False},
                'writer': {'name': 'test_writer', 'login': True, 'applies': False},
                'reader': {'name': 'test_reader', 'login': True, 'applies': False},
                'monitor': {'name': 'test_monitor', 'login': True, 'applies': False},
                'backup': {'name': 'test_backup', 'login': True, 'applies': False},
            }
        }
        errors = validate_role_matrix(data)
        assert any('owner.login must be false' in e for e in errors)

    def test_invalid_role_name(self):
        data = {
            'roles': {
                'owner': {'name': 'test_admin', 'login': False, 'applies': True},
                'migrator': {'name': 'test_migrator', 'login': True, 'applies': False},
                'writer': {'name': 'test_writer', 'login': True, 'applies': False},
                'reader': {'name': 'test_reader', 'login': True, 'applies': False},
                'monitor': {'name': 'test_monitor', 'login': True, 'applies': False},
                'backup': {'name': 'test_backup', 'login': True, 'applies': False},
            }
        }
        errors = validate_role_matrix(data)
        assert any('naming pattern' in e for e in errors)

    def test_no_applicable_roles(self):
        data = {
            'roles': {
                'owner': {'name': 'test_owner', 'login': False, 'applies': False},
                'migrator': {'name': 'test_migrator', 'login': True, 'applies': False},
                'writer': {'name': 'test_writer', 'login': True, 'applies': False},
                'reader': {'name': 'test_reader', 'login': True, 'applies': False},
                'monitor': {'name': 'test_monitor', 'login': True, 'applies': False},
                'backup': {'name': 'test_backup', 'login': True, 'applies': False},
            }
        }
        errors = validate_role_matrix(data)
        assert any('No roles have applies: true' in e for e in errors)

    def test_empty_roles(self):
        errors = validate_role_matrix({'roles': {}})
        assert len(errors) >= 6

    def test_all_valid_if_some_applies_false(self):
        data = {
            'roles': {
                'owner': {'name': 'test_owner', 'login': False, 'applies': True},
                'migrator': {'name': 'test_migrator', 'login': True, 'applies': False},
                'writer': {'name': 'test_writer', 'login': True, 'applies': False},
                'reader': {'name': 'test_reader', 'login': True, 'applies': False},
                'monitor': {'name': 'test_monitor', 'login': True, 'applies': False},
                'backup': {'name': 'test_backup', 'login': True, 'applies': False},
            }
        }
        errors = validate_role_matrix(data)
        assert errors == []
