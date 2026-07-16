"""Tests for validate_db_secret_detection.py — prohibited secret detection."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.validate_db_secret_detection import scan_file, PROHIBITED_PATTERNS


class TestScanFile:
    def test_clean_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write("SELECT 1;\nCREATE TABLE test (id int);\n")
            fpath = f.name
        try:
            findings = scan_file(fpath)
            assert findings == []
        finally:
            os.unlink(fpath)

    def test_password_in_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("DATABASE_URL=postgresql://user:secret123@localhost/db\n")
            fpath = f.name
        try:
            findings = scan_file(fpath)
            assert len(findings) >= 1
            assert any('credential assignment' in f[1] or 'PostgreSQL URL' in f[1] for f in findings)
        finally:
            os.unlink(fpath)

    def test_local_path_detected(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("path = '/Users/buddy/projects/test/data'\n")
            fpath = f.name
        try:
            findings = scan_file(fpath)
            assert len(findings) >= 1
            assert any('local filesystem path' in f[1] for f in findings)
        finally:
            os.unlink(fpath)

    def test_api_key_detected(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("api_key: sk-abc123def456ghi789jkl012\n")
            fpath = f.name
        try:
            findings = scan_file(fpath)
            assert len(findings) >= 1
        finally:
            os.unlink(fpath)

    def test_ip_address_detected(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("host: 10.0.0.5\n")
            fpath = f.name
        try:
            findings = scan_file(fpath)
            assert len(findings) >= 1
            assert any('IP address' in f[1] for f in findings)
        finally:
            os.unlink(fpath)

    def test_private_key_detected(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write("-----BEGIN RSA PRIVATE KEY-----\nABC123\n-----END RSA PRIVATE KEY-----\n")
            fpath = f.name
        try:
            findings = scan_file(fpath)
            assert len(findings) >= 1
            assert any('private key' in f[1] for f in findings)
        finally:
            os.unlink(fpath)

    def test_placeholder_exempted(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("PGPASSWORD=... placeholder for docs\n")
            fpath = f.name
        try:
            findings = scan_file(fpath)
            assert findings == []
        finally:
            os.unlink(fpath)

    def test_credential_redacted_exempted(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("token= <credential-redacted>\n")
            fpath = f.name
        try:
            findings = scan_file(fpath)
            assert findings == []
        finally:
            os.unlink(fpath)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            fpath = f.name
        try:
            findings = scan_file(fpath)
            assert findings == []
        finally:
            os.unlink(fpath)

    def test_binary_file_skipped(self):
        with tempfile.NamedTemporaryFile(suffix='.pyc', delete=False) as f:
            f.write(b'\x00\x01\x02\x03')
            fpath = f.name
        try:
            findings = scan_file(fpath)
            assert findings == []
        finally:
            os.unlink(fpath)


class TestProhibitedPatterns:
    def test_credential_pattern(self):
        pattern, label = PROHIBITED_PATTERNS[0]
        assert pattern.search('password = hunter2')
        assert pattern.search('SECRET_KEY=abc123')
        assert pattern.search('api_key: 12345')

    def test_api_key_pattern(self):
        pattern, label = PROHIBITED_PATTERNS[1]
        assert pattern.search('sk-abc123def456ghi789jkl012mno345')
        assert pattern.search('pk-test123456789012345678901234')

    def test_pg_url_pattern(self):
        pattern, label = PROHIBITED_PATTERNS[2]
        assert pattern.search('postgresql://user:pass@localhost/db')
        assert pattern.search('postgresql://admin:secret@host:5432/mydb')

    def test_local_path_pattern(self):
        pattern, label = PROHIBITED_PATTERNS[3]
        assert pattern.search('/Users/buddy/projects/test/file.txt')
        assert pattern.search('path = "/Users/admin/.ssh/id_rsa"')

    def test_ip_pattern(self):
        pattern, label = PROHIBITED_PATTERNS[4]
        assert pattern.search('192.168.1.1')
        assert pattern.search('10.0.0.1')
        assert pattern.search('172.16.0.1')
