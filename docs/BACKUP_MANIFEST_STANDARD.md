# Backup Manifest Standard

**Status:** Current authority for portfolio backup manifest format.
**Version:** 1.0
**Design principle:** The manifest is the single machine-readable record of what was backed up, when, whether it was verified, and how to restore. It is not a backup policy — policy lives in CONTROL.md.

---

## 1. Purpose

Every portfolio backup produces one manifest file. The manifest answers:

- What drive or volume holds the backup?
- When was it created?
- Which repositories and paths are included?
- What is intentionally excluded?
- Are checksums verified?
- Was a restore sample extracted and validated?
- How to restore?

One manifest per backup run. Multiple runs produce multiple manifest files.

---

## 2. Location

```
/Volumes/<volume-name>/
  .backup-manifest-<date>.json       ← current or latest run
  .backup-manifest-<date>.sha256     ← manifest checksum sidecar
  archives/
    <date>/
      repos/
        <slug>/
          ...
```

The manifest resides on the backup volume, not in any repository. It is never committed to Git.

---

## 3. Schema

```json
{
  "manifest_version": "1.0",
  "backup_id": "2026-07-17_mac-cold-archive",
  "created_at": "2026-07-17T12:00:00Z",
  "source_host": "<hostname>",
  "target_volume": {
    "name": "Ivy-Backup-2026Q3",
    "mount_path": "/Volumes/Ivy-Backup-2026Q3",
    "filesystem": "APFS",
    "encrypted": true,
    "encryption_verified": true
  },
  "target_path": "archives/2026-07-17/",
  "backup_class": "full",

  "repositories": [
    {
      "slug": "<repo-slug>",
      "source_path": "<absolute-source-path>",
      "backup_path": "repos/<slug>/",
      "backup_policy": {
        "importance": "critical",
        "sensitivity": "private",
        "strategy": "file_archive",
        "priority": "P0"
      },
      "include_groups": ["raw_corpus", "derived_irreplaceable"],
      "exclude_groups": ["cache", "virtualenv", "build_output"],
      "resolved_include": [
        "/Users/buddy/projects/idlehacking_kb/capture/",
        "/Users/buddy/projects/idlehacking_kb/data/"
      ],
      "resolved_exclude": [
        "/Users/buddy/projects/idlehacking_kb/.venv/",
        "**/__pycache__/**"
      ],
      "estimated": {
        "bytes": 130000000000,
        "files": 15000,
        "dirs": 500
      }
    }
  ],

  "verification": {
    "method": "rsync_checksum",
    "source_file_count": 15000,
    "dest_file_count": 15000,
    "source_bytes": 130000000000,
    "dest_bytes": 130000000000,
    "checksum_mismatch_count": 0,
    "restore_sample_path": "/private/tmp/ivy-backup-verify-2026-07-17/",
    "restore_sample_files": 10,
    "restore_sample_bytes": 1073741824,
    "restore_sample_checksum_pass": true,
    "verified_at": "2026-07-17T14:00:00Z"
  },

  "excluded_globally": [
    "**/.venv/**",
    "**/__pycache__/**",
    "**/node_modules/**",
    "**/.next/**",
    "**/.git/objects/**",
    "**/*.pyc",
    "**/.DS_Store",
    "**/tmp/**",
    "**/bench_llm/results/**"
  ],

  "restore_procedure": {
    "steps": [
      "Mount the backup volume",
      "Verify manifest checksum: shasum -a 256 .backup-manifest-<date>.json",
      "Copy desired paths: rsync -a /Volumes/.../archives/<date>/repos/<slug>/ <restore-path>/",
      "Verify restored files: rsync -avc --dry-run <restore-path>/ /Volumes/.../archives/<date>/repos/<slug>/"
    ],
    "notes": "Full restore guide at docs/BACKUP_RESTORE_GUIDE.md"
  }
}
```

---

## 4. Required fields

| Field | Required | Description |
|---|---|---|
| `manifest_version` | Yes | Schema version |
| `backup_id` | Yes | Unique human-readable identifier |
| `created_at` | Yes | ISO 8601 timestamp |
| `target_volume` | Yes | Volume identity, encryption status |
| `repositories[].slug` | Yes | Portfolio repo slug |
| `repositories[].backup_policy` | Yes | Policy from CONTROL.md at time of backup |
| `repositories[].include_groups` | Yes | What was included |
| `repositories[].exclude_groups` | Yes | What was excluded |
| `repositories[].estimated.bytes` | Yes | Estimated size (from planner) — NOT actual transferred size |
| `verification.method` | Yes | How verification was performed |
| `verification.checksum_mismatch_count` | Yes | Count of failed checksums |
| `excluded_globally` | Yes | Glob patterns excluded across all repos |
| `restore_procedure` | Yes | Steps to restore |

---

## 5. Verification fields

The manifest records what verification was performed, not what the verifier thinks.

| `method` | Meaning |
|---|---|
| `none` | Not yet verified |
| `rsync_checksum` | Full rsync --checksum comparison of source and destination trees |
| `sample_restore` | A subset of files was restored to a temp location and checksummed |
| `full_restore_drill` | All files restored to temp location and verified |

A manifest with `verification.method: none` is an unverified copy, not a backup.

---

## 6. Excluded from manifest

- File contents (the archive itself holds these)
- Credentials, keys, connection strings
- Private host paths beyond the source-path record
- Backup schedules or cadence (policy belongs in CONTROL.md)

---

## 7. Hermes interface

Hermes reads the manifest to determine backup state. It does not scan the archive.

To check backup freshness, Hermes compares `created_at` to the repo's `evidence_max_age_days`. To check verification, Hermes reads the `verification` block.

If no manifest exists, Hermes reports UNKNOWN.
