#!/usr/bin/env python3
"""Backup-manifest validation — verify backup artifacts and their manifest files."""

import os
import sys
import hashlib
import yaml


REQUIRED_MANIFEST_FIELDS = {'project', 'database', 'dump_file', 'checksum', 'file_size_bytes', 'pg_version'}
REQUIRED_CHECKSUM_FIELDS = {'algorithm', 'value'}


def validate_backup_manifest(manifest_path: str, dump_dir: str | None = None) -> list[str]:
    errors = []

    if not os.path.isfile(manifest_path):
        return [f"Manifest file not found: {manifest_path}"]

    with open(manifest_path) as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return [f"YAML parse error: {e}"]

    manifest = data.get('backup_manifest', data)

    for key in REQUIRED_MANIFEST_FIELDS:
        if key not in manifest:
            errors.append(f"Missing manifest field: {key}")

    checksum = manifest.get('checksum', {})
    for key in REQUIRED_CHECKSUM_FIELDS:
        if key not in checksum:
            errors.append(f"Missing checksum field: {key}")

    dump_file = manifest.get('dump_file')
    if dump_dir and dump_file:
        dump_path = os.path.join(dump_dir, dump_file)
        if os.path.isfile(dump_path):
            actual_size = os.path.getsize(dump_path)
            expected_size = manifest.get('file_size_bytes')
            if expected_size and actual_size != expected_size:
                errors.append(f"File size mismatch: expected {expected_size}, actual {actual_size}")

            if checksum.get('algorithm') == 'sha256' and checksum.get('value'):
                sha256_hash = hashlib.sha256()
                with open(dump_path, 'rb') as df:
                    for chunk in iter(lambda: df.read(65536), b''):
                        sha256_hash.update(chunk)
                actual_checksum = sha256_hash.hexdigest()
                if actual_checksum != checksum['value']:
                    errors.append(f"SHA-256 mismatch for {dump_file}")

    if manifest.get('file_size_bytes', 0) == 0:
        errors.append("file_size_bytes is 0 — dump may be empty")

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_db_backup_manifest.py <manifest.yaml> [dump_directory]", file=sys.stderr)
        sys.exit(1)

    manifest_path = sys.argv[1]
    dump_dir = sys.argv[2] if len(sys.argv) > 2 else None

    errors = validate_backup_manifest(manifest_path, dump_dir)
    if errors:
        print(f"FAIL: {manifest_path}")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"PASS: {manifest_path}")
        sys.exit(0)


if __name__ == '__main__':
    main()
