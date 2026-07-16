"""Tests for validate_db_migrations.py — required migration file check."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.validate_db_migrations import check_migration_dir, MIGRATION_PATTERN


class TestCheckMigrationDir:
    def test_valid_migration_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            mig_dir = os.path.join(tmp, 'migrations')
            roll_dir = os.path.join(mig_dir, 'rollback')
            val_dir = os.path.join(mig_dir, 'validation')
            os.makedirs(roll_dir)
            os.makedirs(val_dir)

            for i in range(1, 4):
                base = f"20260715_00{i}_test_migration"
                open(os.path.join(mig_dir, f"{base}.sql"), 'w').close()
                open(os.path.join(roll_dir, f"{base}_down.sql"), 'w').close()
                open(os.path.join(val_dir, f"{base}_check.sql"), 'w').close()

            errors = check_migration_dir(mig_dir, expected_count=3)
            assert errors == []

    def test_missing_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            mig_dir = os.path.join(tmp, 'migrations')
            roll_dir = os.path.join(mig_dir, 'rollback')
            val_dir = os.path.join(mig_dir, 'validation')
            os.makedirs(roll_dir)
            os.makedirs(val_dir)

            open(os.path.join(mig_dir, "20260715_001_test.sql"), 'w').close()
            open(os.path.join(val_dir, "20260715_001_test_check.sql"), 'w').close()

            errors = check_migration_dir(mig_dir)
            assert any('Missing rollback' in e for e in errors)

    def test_missing_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            mig_dir = os.path.join(tmp, 'migrations')
            roll_dir = os.path.join(mig_dir, 'rollback')
            val_dir = os.path.join(mig_dir, 'validation')
            os.makedirs(roll_dir)
            os.makedirs(val_dir)

            open(os.path.join(mig_dir, "20260715_001_test.sql"), 'w').close()
            open(os.path.join(roll_dir, "20260715_001_test_down.sql"), 'w').close()

            errors = check_migration_dir(mig_dir)
            assert any('Missing validation' in e for e in errors)

    def test_bad_filename_pattern(self):
        with tempfile.TemporaryDirectory() as tmp:
            mig_dir = os.path.join(tmp, 'migrations')
            roll_dir = os.path.join(mig_dir, 'rollback')
            val_dir = os.path.join(mig_dir, 'validation')
            os.makedirs(roll_dir)
            os.makedirs(val_dir)

            open(os.path.join(mig_dir, "bad_file.sql"), 'w').close()

            errors = check_migration_dir(mig_dir)
            assert any('does not match' in e for e in errors)

    def test_no_migration_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            mig_dir = os.path.join(tmp, 'migrations')
            os.makedirs(mig_dir)
            errors = check_migration_dir(mig_dir)
            assert any('No migration SQL files' in e for e in errors)

    def test_missing_directories(self):
        errors = check_migration_dir('/nonexistent/path')
        assert any('Migration directory not found' in e for e in errors)

    def test_expected_count_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            mig_dir = os.path.join(tmp, 'migrations')
            roll_dir = os.path.join(mig_dir, 'rollback')
            val_dir = os.path.join(mig_dir, 'validation')
            os.makedirs(roll_dir)
            os.makedirs(val_dir)

            open(os.path.join(mig_dir, "20260715_001_test.sql"), 'w').close()
            open(os.path.join(roll_dir, "20260715_001_test_down.sql"), 'w').close()
            open(os.path.join(val_dir, "20260715_001_test_check.sql"), 'w').close()

            errors = check_migration_dir(mig_dir, expected_count=5)
            assert any('Expected 5' in e for e in errors)

    def test_missing_rollback_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            mig_dir = os.path.join(tmp, 'migrations')
            os.makedirs(mig_dir)
            open(os.path.join(mig_dir, "20260715_001_test.sql"), 'w').close()
            errors = check_migration_dir(mig_dir)
            assert any('Rollback directory missing' in e for e in errors)

    def test_missing_validation_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            mig_dir = os.path.join(tmp, 'migrations')
            roll_dir = os.path.join(mig_dir, 'rollback')
            os.makedirs(mig_dir)
            os.makedirs(roll_dir)
            open(os.path.join(mig_dir, "20260715_001_test.sql"), 'w').close()
            open(os.path.join(roll_dir, "20260715_001_test_down.sql"), 'w').close()
            errors = check_migration_dir(mig_dir)
            assert any('Validation directory missing' in e for e in errors)


class TestMigrationPattern:
    def test_valid_patterns(self):
        assert MIGRATION_PATTERN.match("20260715_001_create_users.sql")
        assert MIGRATION_PATTERN.match("20260715_010_add_index.sql")
        assert MIGRATION_PATTERN.match("20260715_999_last_migration.sql")

    def test_invalid_patterns(self):
        assert not MIGRATION_PATTERN.match("create_users.sql")
        assert not MIGRATION_PATTERN.match("001_create_users.sql")
        assert not MIGRATION_PATTERN.match("2026-07-15_001_create.sql")
        assert not MIGRATION_PATTERN.match("20260715_001.sql")
