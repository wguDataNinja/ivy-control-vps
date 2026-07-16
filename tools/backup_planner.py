#!/usr/bin/env python3
"""Portfolio backup planner — read-only, never copies data.

Reads backup policy from CONTROL.md records, inspects the local filesystem
and an optional external volume, resolves include/exclude groups to concrete
paths, and emits a structured execution packet for human review.

The planner never copies, compresses, or modifies data.

Usage:
    python3 tools/backup_planner.py                        # inspect all repos, no target
    python3 tools/backup_planner.py --target /Volumes/NAME  # validate target + produce packet
    python3 tools/backup_planner.py --repo idlehacking-kb   # single repo
    python3 tools/backup_planner.py --repo idlehacking-kb --target /Volumes/NAME
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
REPOS_DIR = REPO_ROOT / "repos"
UTC = timezone.utc

# Backup dimensions — valid enumerations
IMPORTANCE_VALUES = {"critical", "important", "replaceable", "unknown"}
SENSITIVITY_VALUES = {"private", "internal", "public", "unknown"}
STRATEGY_VALUES = {"file_archive", "database_dump", "git_remote", "regenerate", "unknown"}
PRIORITY_VALUES = {"P0", "P1", "P2", "P3", "unknown"}

# Standard include groups — maps group name to glob/label
INCLUDE_GROUPS: dict[str, dict[str, Any]] = {
    "raw_corpus": {
        "label": "Raw irreplaceable captures",
        "patterns": ["capture/", "data/raw/"],
        "doc": "Original captured data that cannot be regenerated",
    },
    "derived_irreplaceable": {
        "label": "Derived data (expensive to recreate)",
        "patterns": [
            "data/kb/",
            "data/chat/",
            "data/derived/",
            "data/imports/",
        ],
        "doc": "Derived data that would take significant effort to regenerate",
    },
    "database_dump": {
        "label": "PostgreSQL dump artifacts",
        "patterns": ["backups/postgres/"],
        "doc": "Database dump files and manifests",
    },
    "private_state": {
        "label": "Private agent state and evidence",
        "patterns": [
            "_internal/",
            "_outbox/",
            "inbox/",
            "runtime/",
        ],
        "doc": "Private operational state, agent outboxes, session evidence",
    },
    "source": {
        "label": "Git-tracked source and tests",
        "patterns": ["**/*.py", "**/*.js", "**/*.ts", "**/*.sh"],
        "doc": "Source code and tests (usually covered by git remote)",
    },
}

# Standard exclude groups
EXCLUDE_GROUPS: dict[str, dict[str, Any]] = {
    "cache": {
        "label": "Build caches and temp files",
        "patterns": ["__pycache__/", ".pytest_cache/", ".next/", ".ipynb_checkpoints/"],
        "doc": "Reproducible build caches",
    },
    "virtualenv": {
        "label": "Virtual environments and dependencies",
        "patterns": [".venv/", "node_modules/", ".opencode/"],
        "doc": "Installable dependencies",
    },
    "build_output": {
        "label": "Generated build output",
        "patterns": ["out/", "site/", "public/", "dist/", "build/"],
        "doc": "Regenerable build artifacts",
    },
    "git_objects": {
        "label": "Git object store (covered by remote)",
        "patterns": [".git/objects/"],
        "doc": "Git history (already on GitHub or remote)",
    },
    "temp": {
        "label": "Temporary working directories",
        "patterns": ["tmp/", ".claude/", ".engram/"],
        "doc": "Disposable temporary data",
    },
    "os_metadata": {
        "label": "OS metadata files",
        "patterns": [".DS_Store", "Thumbs.db"],
        "doc": "Filesystem metadata",
    },
    "regenerable_output": {
        "label": "Regenerable generated output",
        "patterns": [
            "reports/",
            "notebook/",
            "logs/",
            "bench_llm/results/",
        ],
        "doc": "Output that can be recreated from source and data",
    },
}

# Default rsync flags for content-backup policy.
# Preserves bytes, paths, timestamps, directory structure, and symlinks.
# Does NOT preserve extended attributes, ACLs, ownership, or macOS metadata
# (irrelevant for corpus data — JSON, JSONL, CSV, media files).
BASE_RSYNC_FLAGS = [
    "-a", "--progress",
    "--exclude", "._*",
    "--exclude", ".DS_Store",
]

# Verification flags — checksum comparison only, no transfer
VERIFY_RSYNC_FLAGS = [
    "-avc", "--dry-run",
    "--exclude", "._*",
    "--exclude", ".DS_Store",
]


def relative_repo_path(absolute_path: Path, repo_local_path: Path) -> str:
    """Compute the path of a resolved include relative to its repo root.

    Example:
        absolute_path: /Users/buddy/projects/idlehacking_kb/capture
        repo_local_path: /Users/buddy/projects/idlehacking_kb
        returns: capture
    """
    try:
        rel = absolute_path.relative_to(repo_local_path)
        return str(rel)
    except ValueError:
        # Path is outside the repo root — use basename as fallback
        return absolute_path.name


INTERNAL_DISK_PATHS = [
    "/",
    "/System",
    "/Users",
    "/Applications",
    "/Library",
    "/home",
]


def iso_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_yaml_block(text: str, block_name: str) -> dict[str, Any]:
    """Naive YAML block parser for CONTROL.md front matter.
    Extracts nested keys like backup.importance and list items from
    the --- delimited block.  Handles:
        key: value
        key:
          - list_item
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    end_idx = 1
    while end_idx < len(lines) and lines[end_idx].strip() != "---":
        end_idx += 1
    if end_idx >= len(lines):
        return {}
    result: dict[str, Any] = {}
    stack: list[tuple[str, int]] = []
    list_indices: dict[str, int] = {}

    for raw_line in lines[1:end_idx]:
        stripped = raw_line.rstrip()
        if not stripped.strip():
            continue
        content = stripped.lstrip()
        indent = len(stripped) - len(content)

        # Pop stack until we find a parent at lower indentation
        while stack and stack[-1][1] >= indent:
            stack.pop()

        # Build current prefix from remaining stack
        prefix = ".".join(p[0] for p in stack)
        full_prefix = f"{prefix}." if prefix else ""

        if content.startswith("- "):
            # List item — belongs to the current stack top
            list_value = content[2:].strip().strip('"').strip("'")
            if stack:
                # The prefix already includes the collection key; use it directly
                # as the disambiguation key for counting
                idx = list_indices.get(prefix, 0)
                list_indices[prefix] = idx + 1
                result[f"{prefix}.{idx}"] = list_value
            continue

        if ":" not in content:
            continue

        key_raw, _, val_raw = content.partition(":")
        leaf_key = key_raw.strip()
        val = val_raw.strip().strip('"').strip("'")

        if val:
            # Key with value
            result[f"{full_prefix}{leaf_key}"] = val
            # Reset list index for this key since it might be followed by list items
            list_idx_key = f"{prefix}.{leaf_key}" if prefix else leaf_key
            list_indices.pop(list_idx_key, None)
        else:
            # Key without value — push to stack for children
            stack.append((leaf_key, indent))

    return result


def get_backup_policy(repo_slug: str) -> dict[str, Any]:
    """Read backup policy from CONTROL.md YAML front matter."""
    # Directories use hyphens (same as slugs)
    ctrl_path = REPOS_DIR / repo_slug / "CONTROL.md"
    if not ctrl_path.exists():
        # Fallback: try underscore variant for legacy path
        legacy = repo_slug.replace("-", "_")
        ctrl_path = REPOS_DIR / legacy / "CONTROL.md"
    if not ctrl_path.exists():
        return {}
    text = ctrl_path.read_text(encoding="utf-8")
    meta = read_yaml_block(text, "backup")

    policy: dict[str, Any] = {}
    for key in ("importance", "sensitivity", "strategy", "priority", "evidence_max_age_days"):
        fk = f"backup.{key}"
        if fk in meta:
            val = meta[fk]
            try:
                if key == "evidence_max_age_days":
                    val = int(val)
            except (ValueError, TypeError):
                val = None
            policy[key] = val

    # Parse lists
    for list_key in ("include_groups", "exclude_groups"):
        fk = f"backup.{list_key}"
        items = []
        i = 0
        while True:
            item_key = f"{fk}.{i}"
            if item_key in meta:
                items.append(meta[item_key])
                i += 1
            else:
                break
        if items:
            policy[list_key] = items
    return policy


def resolve_paths(
    repo_path: Path,
    include_groups: list[str],
    exclude_groups: list[str],
) -> tuple[list[Path], list[str]]:
    """Resolve include/exclude groups to concrete paths and glob patterns."""
    includes: list[Path] = []
    exclude_patterns: list[str] = []

    for group_name in include_groups:
        group = INCLUDE_GROUPS.get(group_name)
        if group is None:
            continue
        for pattern in group["patterns"]:
            candidate = repo_path / pattern
            if candidate.exists():
                includes.append(candidate.resolve())
            else:
                # Try glob
                matched = list(repo_path.glob(pattern))
                for m in matched:
                    if m.exists():
                        includes.append(m.resolve())

    for group_name in exclude_groups:
        group = EXCLUDE_GROUPS.get(group_name)
        if group is None:
            continue
        for pattern in group["patterns"]:
            exclude_patterns.append(pattern)

    return includes, exclude_patterns


def estimate_size(paths: list[Path], exclude_patterns: list[str]) -> dict[str, Any]:
    """Estimate total bytes and file count for a list of paths."""
    total_bytes = 0
    total_files = 0
    total_dirs = 0
    errors: list[str] = []

    for path in paths:
        if not path.exists():
            errors.append(f"Path does not exist: {path}")
            continue
        try:
            result = subprocess.run(
                ["du", "-sh", str(path)],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                pass  # human-readable size from stderr
            # Count files
            find_result = subprocess.run(
                ["find", str(path), "-type", "f"],
                capture_output=True, text=True, timeout=60,
            )
            if find_result.returncode == 0:
                file_lines = [l for l in find_result.stdout.split("\n") if l.strip()]
                total_files += len(file_lines)

            find_dir_result = subprocess.run(
                ["find", str(path), "-type", "d"],
                capture_output=True, text=True, timeout=30,
            )
            if find_dir_result.returncode == 0:
                dir_lines = [l for l in find_dir_result.stdout.split("\n") if l.strip()]
                total_dirs += len(dir_lines)

            # Get byte count (macOS: du -sk gives kilobytes)
            du_result = subprocess.run(
                ["du", "-sk", str(path)],
                capture_output=True, text=True, timeout=60,
            )
            if du_result.returncode == 0:
                try:
                    kb_str = du_result.stdout.split("\t")[0]
                    total_bytes += int(kb_str) * 1024
                except (IndexError, ValueError):
                    pass
        except (OSError, subprocess.TimeoutExpired) as exc:
            errors.append(f"Cannot estimate {path}: {exc}")

    return {"bytes": total_bytes, "files": total_files, "dirs": total_dirs, "errors": errors}


def discover_control_dirs() -> list[Path]:
    """Return all managed repo CONTROL.md directories."""
    if not REPOS_DIR.is_dir():
        return []
    return sorted(
        REPOS_DIR.iterdir()
    )


def get_local_path(repo_dir: Path) -> Path | None:
    """Get the local Mac path for a repository from its CONTROL.md."""
    ctrl_path = repo_dir / "CONTROL.md"
    if not ctrl_path.exists():
        return None
    text = ctrl_path.read_text(encoding="utf-8")
    meta = read_yaml_block(text, "repository")
    path_str = meta.get("repository.local_path")
    if path_str:
        p = Path(path_str)
        if p.exists():
            return p
    return None


def validate_target(target: Path) -> list[str]:
    """Validate an external backup target volume. Returns list of blockers."""
    blockers: list[str] = []

    if not target.exists():
        blockers.append(f"Target path does not exist: {target}")
        return blockers
    if not target.is_dir():
        blockers.append(f"Target is not a directory: {target}")
        return blockers

    # Check it's not on the internal disk
    resolved = target.resolve()
    for internal in INTERNAL_DISK_PATHS:
        try:
            if str(resolved).startswith(internal) and str(resolved) != internal:
                # Only flag if it's actually on the system volume
                pass
        except Exception:
            pass

    # Check mount point
    try:
        df_result = subprocess.run(
            ["df", str(resolved)],
            capture_output=True, text=True, timeout=10,
        )
        df_output = df_result.stdout.strip()
        # Check if it's on /dev/disk (not a mounted volume)
        if df_output:
            lines = df_output.split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                device = parts[0] if parts else ""
                # Internal disk devices start with /dev/disk0 or /dev/disk1
                if device and ("/dev/disk0" in device or "/dev/disk1" in device):
                    # Check mount point
                    mount_point = parts[-1] if len(parts) > 1 else ""
                    if mount_point and mount_point.startswith("/"):
                        # Check if it's under /Volumes (external) or not
                        if not str(resolved).startswith("/Volumes/"):
                            blockers.append(
                                f"Target appears to be on internal disk (device: {device}, "
                                f"mount: {mount_point}). Use a mounted external volume under /Volumes/"
                            )
    except (OSError, subprocess.TimeoutExpired) as exc:
        blockers.append(f"Cannot check target filesystem: {exc}")

    # Check writable
    if not os.access(str(resolved), os.W_OK):
        blockers.append(f"Target is not writable: {target}")

    # Check encryption — find the backing image via hdiutil info relationship.
    # The mounted volume's device can be traced back to a disk image record
    # in the hdiutil info output, which reports the actual image-level encryption.
    try:
        # 1. Identify the device for the mount point
        df_result = subprocess.run(
            ["df", str(resolved)],
            capture_output=True, text=True, timeout=10,
        )
        mount_device = ""
        for line in df_result.stdout.splitlines():
            parts = line.split()
            if len(parts) > 0 and parts[0].startswith("/dev/"):
                mount_device = parts[0]
                break

        if not mount_device:
            blockers.append(f"Cannot determine device for mount point {resolved}")
        else:
            # 2. Parse hdiutil info to find which image backs this device
            hdiutil = subprocess.run(
                ["hdiutil", "info"],
                capture_output=True, text=True, timeout=15,
            )
            info_text = hdiutil.stdout

            # hdiutil info output structure:
            #   framework: ...
            #   ================================================
            #   image-path      : <path>
            #   image-encrypted : TRUE|FALSE
            #   ...
            #   /dev/diskN      ...
            #   /dev/diskNs1    ...  /Volumes/...
            #
            # Each image section is separated by a "===" line.
            # After the image properties, the device mapping follows.

            sections = info_text.split("================================================")
            found_encrypted = False
            found_path = ""
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                # Check if this section mentions the mount device
                if mount_device in section:
                    # Parse image-encrypted from this section
                    for line in section.splitlines():
                        line_stripped = line.strip()
                        if line_stripped.startswith("image-encrypted"):
                            val = line_stripped.split(":", 1)[1].strip().upper()
                            if val == "TRUE":
                                found_encrypted = True
                        elif line_stripped.startswith("image-path"):
                            found_path = line_stripped.split(":", 1)[1].strip()
                    break

            if found_encrypted:
                # Confirm the backing image is on the external Passport volume
                if found_path and not found_path.startswith("/Volumes/Passport"):
                    blockers.append(
                        f"Backing image is not on the external Passport volume: {found_path}. "
                        f"Only Passport-hosted disk images are approved."
                    )
            else:
                blockers.append(
                    f"Target {resolved} (device {mount_device}) is NOT backed by an "
                    f"encrypted disk image. The backing image must have "
                    f"image-encrypted: TRUE."
                )

    except (OSError, subprocess.TimeoutExpired) as exc:
        blockers.append(f"Cannot verify target encryption: {exc}")

    # Check capacity
    try:
        usage = shutil.disk_usage(str(resolved))
        free_gb = usage.free / (1024 ** 3)
        if free_gb < 10:
            blockers.append(f"Insufficient free space on target: {free_gb:.1f} GB free (< 10 GB)")
    except OSError as exc:
        blockers.append(f"Cannot check target capacity: {exc}")

    return blockers


def build_execution_packet(
    repos: list[dict[str, Any]],
    target: Path | None,
    blockers: list[str],
) -> dict[str, Any]:
    """Build the structured execution packet for human review.

    Each resolved include path produces its own rsync command and verify
    command.  Source trees are never flattened into a single destination —
    the directory hierarchy is preserved.

    Content-backup policy: bytes, paths, timestamps, directory structure,
    and symlinks are preserved.  Extended attributes, ACLs, ownership, and
    macOS metadata are NOT preserved (irrelevant for corpus data).
    """
    now = iso_now()
    snapshot_name = f"snapshot-{now[:10]}"
    packet: dict[str, Any] = {
        "packet_version": "1.0",
        "generated_at": now,
        "snapshot_name": snapshot_name,
        "planner": "tools/backup_planner.py",
        "metadata_policy": (
            "content_backup — preserves bytes, paths, timestamps, "
            "directory structure, and symlinks. Extended attributes, "
            "ACLs, ownership, and macOS metadata are not preserved."
        ),
        "target": str(target) if target else None,
        "target_validation": {
            "valid": len(blockers) == 0,
            "blockers": blockers,
        },
        "repositories": [],
        "excluded_globally": sorted(
            f"{k}: {v['label']}"
            for k, v in EXCLUDE_GROUPS.items()
        ),
        "inventory_version": "1.0",
        "estimated_total_bytes": 0,
        "estimated_total_files": 0,
        "copy_commands": [],
        "verify_commands": [],
        "restore_sample_commands": [],
    }

    for repo in repos:
        slug = repo["slug"]
        local_path = repo.get("local_path")
        resolved_includes = repo.get("resolved_includes", [])
        resolved_excludes = repo.get("resolved_exclude_patterns", [])
        include_groups = repo.get("include_groups", [])
        exclude_groups = repo.get("exclude_groups", [])

        entry: dict[str, Any] = {
            "slug": slug,
            "policy": repo["policy"],
            "local_path": str(local_path) if local_path else None,
            "local_path_exists": local_path is not None and local_path.exists(),
            "include_groups": include_groups,
            "exclude_groups": exclude_groups,
            "resolved_includes": [str(p) for p in resolved_includes],
            "resolved_excludes": resolved_excludes,
            "estimated": repo.get("estimated", {}),
            "skipped_reason": repo.get("skipped_reason"),
        }
        packet["repositories"].append(entry)
        est = repo.get("estimated", {})
        packet["estimated_total_bytes"] += est.get("bytes", 0)
        packet["estimated_total_files"] += est.get("files", 0)

        if not target:
            continue
        if repo.get("skipped_reason") or not resolved_includes:
            continue
        if not local_path:
            continue

        # Build one copy command + verify command per resolved include path
        for inc_path in resolved_includes:
            inc_path_obj = Path(inc_path) if isinstance(inc_path, str) else inc_path
            rel = relative_repo_path(inc_path_obj, local_path)

            source = str(inc_path_obj) + "/"
            dest_base = target / snapshot_name / "repos" / slug / rel
            dest = str(dest_base)

            # Copy command — use structured args list
            cmd = ["rsync"] + BASE_RSYNC_FLAGS[:]
            for pattern in resolved_excludes:
                cmd.extend(["--exclude", pattern])
            cmd.append(source)
            cmd.append(dest)
            cmd_str = shlex.join(cmd)

            packet["copy_commands"].append({
                "source": source,
                "dest": dest,
                "relative_path": rel,
                "repo_slug": slug,
                "args": cmd,
                "command": cmd_str,
            })

            # Verify command (checksum comparison)
            vcmd = ["rsync"] + VERIFY_RSYNC_FLAGS[:]
            for pattern in resolved_excludes:
                vcmd.extend(["--exclude", pattern])
            vcmd.append(source)
            vcmd.append(dest)
            vcmd_str = shlex.join(vcmd)
            packet["verify_commands"].append({
                "source": source,
                "dest": dest,
                "relative_path": rel,
                "repo_slug": slug,
                "args": vcmd,
                "command": vcmd_str,
            })

    # Restore-sample command (picks from all verified destinations)
    if target and packet["copy_commands"]:
        sample_dir = f"/private/tmp/ivy-backup-verify-{now[:10]}/"
        for copy_cmd in packet["copy_commands"]:
            dest = copy_cmd["dest"]
            rel = copy_cmd["relative_path"]
            slug = copy_cmd["repo_slug"]
            # For each copied path, pick a few large files to sample
            # Draft restore-sample command — human should review and adjust
            sample_cmd = (
                f"mkdir -p {sample_dir} && "
                f"cd {dest} && "
                f"find . -type f -size +1M | shuf -n 5 | "
                f"xargs -I{{}} cp --parents {{}} {sample_dir}"
            )
            packet["restore_sample_commands"].append({
                "source": dest,
                "sample_dir": sample_dir,
                "relative_path": rel,
                "repo_slug": slug,
                "command": sample_cmd,
            })

    if target:
        packet["manifest_destination"] = str(
            target / snapshot_name / "manifest.json"
        )

    return packet


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Portfolio backup planner — read-only, never copies data"
    )
    parser.add_argument("--repo", type=str, default=None, help="Filter by repo slug")
    parser.add_argument(
        "--target", type=str, default=None,
        help="External backup volume path (e.g., /Volumes/Ivy-Backup)",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Write execution packet to file",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve() if args.target else None

    # Discover repos
    repo_dirs = discover_control_dirs()
    repo_slugs = []
    for d in repo_dirs:
        if d.name.startswith("."):
            continue
        slug = d.name.replace("_", "-")
        if args.repo and slug != args.repo:
            continue
        repo_slugs.append((slug, d))

    repos = []
    all_blockers: list[str] = []

    # Validate target first
    if target:
        all_blockers = validate_target(target)

    for slug, repo_dir in repo_slugs:
        policy = get_backup_policy(slug)
        local_path = get_local_path(repo_dir)

        entry: dict[str, Any] = {
            "slug": slug,
            "policy": policy,
            "local_path": local_path,
        }

        if not policy:
            entry["skipped_reason"] = "No backup policy defined (all fields UNKNOWN)"
            repos.append(entry)
            continue
        if not local_path or not local_path.exists():
            entry["skipped_reason"] = f"Local path not found: {local_path}"
            repos.append(entry)
            continue

        imp = policy.get("importance", "unknown")
        sens = policy.get("sensitivity", "unknown")
        strat = policy.get("strategy", "unknown")
        prio = policy.get("priority", "unknown")

        if imp == "unknown" or strat == "unknown":
            entry["skipped_reason"] = "Backup policy has UNKNOWN dimensions"
            repos.append(entry)
            continue

        if strat in ("git_remote", "regenerate"):
            entry["skipped_reason"] = f"Strategy is {strat} — no file archive needed"
            repos.append(entry)
            continue

        include_groups = policy.get("include_groups", [])
        exclude_groups = policy.get("exclude_groups", [])

        if not include_groups:
            entry["skipped_reason"] = "No include_groups defined — nothing to archive"
            repos.append(entry)
            continue

        # Deduplicate and resolve paths
        resolved_includes, exclude_patterns = resolve_paths(
            local_path, include_groups, exclude_groups
        )

        # Remove duplicates
        seen: set[str] = set()
        unique_includes: list[Path] = []
        for p in resolved_includes:
            ps = str(p)
            if ps not in seen:
                seen.add(ps)
                unique_includes.append(p)

        # Check that required paths exist
        missing = []
        for inc in unique_includes:
            if not inc.exists():
                missing.append(str(inc))
        if missing:
            all_blockers.append(f"{slug}: include paths missing: {', '.join(missing)}")
            entry["skipped_reason"] = f"Missing include paths: {missing}"
            repos.append(entry)
            continue

        # Estimate size
        estimated = estimate_size(unique_includes, exclude_patterns)
        entry["include_groups"] = include_groups
        entry["exclude_groups"] = exclude_groups
        entry["resolved_includes"] = unique_includes
        entry["resolved_exclude_patterns"] = exclude_patterns
        entry["estimated"] = estimated

        if estimated.get("errors"):
            for err in estimated["errors"]:
                all_blockers.append(f"{slug}: estimate error: {err}")

        repos.append(entry)

    packet = build_execution_packet(repos, target, all_blockers)

    # Exit nonzero on blockers
    has_blockers = len(all_blockers) > 0
    if target and has_blockers:
        packet["target_validation"]["blockers"] = all_blockers
        packet["target_validation"]["valid"] = False

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(packet, indent=2, default=str) + "\n")
        print(args.output)
    elif args.json:
        json.dump(packet, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
    else:
        # Human-readable output
        print("=" * 60)
        print("PORTFOLIO BACKUP PLANNER")
        print(f"Generated: {packet['generated_at']}")
        print(f"Snapshot: {packet.get('snapshot_name', 'N/A')}")
        print(f"Metadata policy: {packet['metadata_policy']}")
        print(f"Target: {packet['target'] or 'NO TARGET SPECIFIED (dry-run)'}")
        print(f"Target valid: {packet['target_validation']['valid']}")
        if packet['target_validation']['blockers']:
            print("BLOCKERS:")
            for b in packet['target_validation']['blockers']:
                print(f"  ✗ {b}")
        print()
        for repo in packet["repositories"]:
            slug = repo["slug"]
            reason = repo.get("skipped_reason")
            if reason:
                print(f"  {slug}: SKIPPED — {reason}")
            else:
                est = repo.get("estimated", {})
                inc = repo.get("resolved_includes", [])
                print(f"  {slug}: {len(inc)} path(s), "
                      f"{est.get('files', 0):,} files, "
                      f"{est.get('bytes', 0) / (1024**3):.1f} GB")
                for p in inc:
                    print(f"    include: {p}")
        print()
        print(f"Total estimated: {packet['estimated_total_bytes'] / (1024**3):.1f} GB, "
              f"{packet['estimated_total_files']:,} files")
        if packet.get("copy_commands"):
            print()
            print(f"COPY COMMANDS ({len(packet['copy_commands'])} total — one per source path):")
            print()
            for i, cmd in enumerate(packet["copy_commands"]):
                print(f"  [{i+1}] {cmd['repo_slug']} — {cmd['relative_path']}")
                print(f"      {cmd['command']}")
                print()
            print(f"VERIFY COMMANDS ({len(packet['verify_commands'])} total — one per source path):")
            print()
            for i, cmd in enumerate(packet["verify_commands"]):
                print(f"  [{i+1}] {cmd['repo_slug']} — {cmd['relative_path']}")
                print(f"      {cmd['command']}")
                print()
            print(f"Manifest destination: {packet.get('manifest_destination', 'N/A')}")
            print()

    return 1 if (target and has_blockers) else 0


if __name__ == "__main__":
    raise SystemExit(main())
