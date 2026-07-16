"""Tests for validate_db_restore_packet.py — restore-packet completeness check."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.validate_db_restore_packet import validate_restore_packet, TEMP_DB_PATTERN


class TestValidateRestorePacket:
    def test_valid_evidence(self):
        data = {
            'restore_evidence': {
                'dump_file': 'test_20260715.dump',
                'checksum': 'abc123',
                'temp_database': 'test_restore_buddy_20260715120000',
                'validation_passed': True,
                'cleanup_packet_ready': True,
            }
        }
        errors = validate_restore_packet(data)
        assert errors == []

    def test_missing_field(self):
        errors = validate_restore_packet({'restore_evidence': {}})
        assert len(errors) >= 5

    def test_validation_not_passed(self):
        data = {
            'restore_evidence': {
                'dump_file': 'test.dump',
                'checksum': 'abc',
                'temp_database': 'test_restore_me_20260715120000',
                'validation_passed': False,
                'cleanup_packet_ready': False,
            }
        }
        errors = validate_restore_packet(data)
        assert any('validation_passed must be true' in e for e in errors)

    def test_cleanup_without_packet_ready(self):
        data = {
            'restore_evidence': {
                'dump_file': 'test.dump',
                'checksum': 'abc',
                'temp_database': 'test_restore_me_20260715120000',
                'validation_passed': True,
                'cleanup_packet_ready': False,
                'cleanup_completed_at': '2026-07-15T12:00:00Z',
            }
        }
        errors = validate_restore_packet(data)
        assert any('cleanup_packet_ready' in e for e in errors)

    def test_invalid_temp_db_name(self):
        data = {
            'restore_evidence': {
                'dump_file': 'test.dump',
                'checksum': 'abc',
                'temp_database': 'invalid_name',
                'validation_passed': True,
                'cleanup_packet_ready': True,
            }
        }
        errors = validate_restore_packet(data)
        assert any('does not match pattern' in e for e in errors)

    def test_no_restore_evidence_key(self):
        data = {
            'dump_file': 'test.dump',
            'checksum': 'abc',
            'temp_database': 'test_restore_me_20260715120000',
            'validation_passed': True,
            'cleanup_packet_ready': True,
        }
        errors = validate_restore_packet(data)
        assert errors == []


class TestTempDbPattern:
    def test_valid(self):
        assert TEMP_DB_PATTERN.match('traderie_restore_buddy_20260715120000')
        assert TEMP_DB_PATTERN.match('reddit_ops_restore_codex_20260715083000')

    def test_invalid(self):
        assert not TEMP_DB_PATTERN.match('traderie_restore')
        assert not TEMP_DB_PATTERN.match('traderie_restore_buddy')
        assert not TEMP_DB_PATTERN.match('traderie_buddy_20260715120000')
