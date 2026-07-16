"""Tests for validate_db_backup_manifest.py — backup-manifest validation."""

import os
import sys
import hashlib
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.validate_db_backup_manifest import validate_backup_manifest


class TestValidateBackupManifest:
    def test_missing_manifest_file(self):
        errors = validate_backup_manifest('/nonexistent/manifest.yaml')
        assert any('Manifest file not found' in e for e in errors)

    def test_bad_yaml(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("not: valid: yaml: [")
            fpath = f.name
        try:
            errors = validate_backup_manifest(fpath)
            assert any('YAML parse error' in e for e in errors)
        finally:
            os.unlink(fpath)

    def test_missing_required_fields(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("project: test\ndatabase: test_db\n")
            fpath = f.name
        try:
            errors = validate_backup_manifest(fpath)
            assert any('Missing manifest field: dump_file' in e for e in errors)
            assert any('Missing manifest field: checksum' in e for e in errors)
        finally:
            os.unlink(fpath)

    def test_missing_checksum_fields(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("project: test\ndatabase: test_db\ndump_file: test.dump\nchecksum: {}\nfile_size_bytes: 1000\npg_version: 16\n")
            fpath = f.name
        try:
            errors = validate_backup_manifest(fpath)
            assert any('Missing checksum field' in e for e in errors)
        finally:
            os.unlink(fpath)

    def test_zero_file_size(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("project: test\ndatabase: test_db\ndump_file: test.dump\nchecksum: {algorithm: sha256, value: abc}\nfile_size_bytes: 0\npg_version: 16\n")
            fpath = f.name
        try:
            errors = validate_backup_manifest(fpath)
            assert any('file_size_bytes is 0' in e for e in errors)
        finally:
            os.unlink(fpath)

    def test_valid_manifest_without_dump_dir(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("project: test\ndatabase: test_db\ndump_file: test.dump\nchecksum: {algorithm: sha256, value: abc123}\nfile_size_bytes: 1000\npg_version: 16\n")
            fpath = f.name
        try:
            errors = validate_backup_manifest(fpath)
            assert errors == []
        finally:
            os.unlink(fpath)

    def test_checksum_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            dump_path = os.path.join(tmp, 'test.dump')
            with open(dump_path, 'wb') as f:
                f.write(b"some test data")

            sha256_hash = hashlib.sha256()
            with open(dump_path, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    sha256_hash.update(chunk)
            good_checksum = sha256_hash.hexdigest()

            manifest_path = os.path.join(tmp, 'manifest.yaml')
            with open(manifest_path, 'w') as f:
                f.write(f"project: test\ndatabase: test_db\ndump_file: test.dump\nchecksum: {{algorithm: sha256, value: {good_checksum}}}\nfile_size_bytes: {os.path.getsize(dump_path)}\npg_version: 16\n")

            errors = validate_backup_manifest(manifest_path, tmp)
            assert errors == []

    def test_checksum_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            dump_path = os.path.join(tmp, 'test.dump')
            with open(dump_path, 'wb') as f:
                f.write(b"some test data")

            manifest_path = os.path.join(tmp, 'manifest.yaml')
            with open(manifest_path, 'w') as f:
                f.write(f"project: test\ndatabase: test_db\ndump_file: test.dump\nchecksum: {{algorithm: sha256, value: {'a' * 64}}}\nfile_size_bytes: {os.path.getsize(dump_path)}\npg_version: 16\n")

            errors = validate_backup_manifest(manifest_path, tmp)
            assert any('SHA-256 mismatch' in e for e in errors)

    def test_file_size_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            dump_path = os.path.join(tmp, 'test.dump')
            with open(dump_path, 'wb') as f:
                f.write(b"test data")

            manifest_path = os.path.join(tmp, 'manifest.yaml')
            with open(manifest_path, 'w') as f:
                f.write(f"project: test\ndatabase: test_db\ndump_file: test.dump\nchecksum: {{algorithm: sha256, value: {'a'*64}}}\nfile_size_bytes: 999999\npg_version: 16\n")

            errors = validate_backup_manifest(manifest_path, tmp)
            assert any('File size mismatch' in e for e in errors)
