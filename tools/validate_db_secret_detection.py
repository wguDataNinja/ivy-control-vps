#!/usr/bin/env python3
"""Prohibited secret detection — scan files for credentials, private paths,
IP addresses, and other prohibited content patterns."""

import os
import sys
import re


PROHIBITED_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r'(?i)(?:password|secret|api[_-]?key|token|credential)[_\w]*\s*[=:]\s*\S+'), 'credential assignment'),
    (re.compile(r'(?i)(?:sk-[a-zA-Z0-9]{20,}|pk-[a-zA-Z0-9]{20,})'), 'API key'),
    (re.compile(r'postgresql://\S+:\S+@'), 'PostgreSQL URL with password'),
    (re.compile(r'/Users/[^/\s]+(?:/[^\s]*)'), 'local filesystem path'),
    (re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'), 'IP address'),
    (re.compile(r'(BEGIN RSA PRIVATE KEY|BEGIN OPENSSH PRIVATE KEY|BEGIN DSA PRIVATE KEY)'), 'private key'),
]

EXEMPT_EXTENSIONS = {'.pyc', '.pyo', '.pytest_cache'}
EXEMPT_PATTERNS = [
    re.compile(r'__pycache__'),
    re.compile(r'\.git/'),
    re.compile(r'_internal/'),
    re.compile(r'node_modules/'),
    re.compile(r'\.venv/'),
]

CONTENT_EXEMPTIONS = [
    re.compile(r'(?i)example.*password'),
    re.compile(r'PGPASSWORD=...'),
    re.compile(r'<credential-redacted>'),
    re.compile(r'<key-redacted>'),
    re.compile(r'<local-path>'),
    re.compile(r'<ip>'),
    re.compile(r'<host>'),
]


def scan_file(filepath: str) -> list[tuple[str, str, str]]:
    findings = []
    for exempt in EXEMPT_PATTERNS:
        if exempt.search(filepath):
            return findings

    ext = os.path.splitext(filepath)[1].lower()
    if ext in EXEMPT_EXTENSIONS:
        return findings

    try:
        with open(filepath, 'r', errors='replace') as f:
            for i, line in enumerate(f, 1):
                stripped = line.rstrip('\n')
                normalized = stripped.strip()
                for pattern, label in PROHIBITED_PATTERNS:
                    if pattern.search(stripped):
                        is_exempt = any(ex.search(normalized) for ex in CONTENT_EXEMPTIONS)
                        if is_exempt:
                            continue
                        truncated = normalized[:80]
                        findings.append((filepath, label, f"line {i}: {truncated}"))
    except (OSError, UnicodeDecodeError):
        pass

    return findings


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_db_secret_detection.py <file_or_dir> [file_or_dir ...]", file=sys.stderr)
        sys.exit(1)

    exit_code = 0
    total_findings = []

    for target in sys.argv[1:]:
        if os.path.isfile(target):
            total_findings.extend(scan_file(target))
        elif os.path.isdir(target):
            for root, dirs, files in os.walk(target):
                dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'node_modules', '.venv')]
                for fname in files:
                    fpath = os.path.join(root, fname)
                    total_findings.extend(scan_file(fpath))

    if total_findings:
        print("FAIL: Prohibited content detected")
        for filepath, label, detail in total_findings:
            print(f"  [{label}] {filepath}: {detail}")
        sys.exit(1)
    else:
        print("PASS: No prohibited content detected")
        sys.exit(0)


if __name__ == '__main__':
    main()
