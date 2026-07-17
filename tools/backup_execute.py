#!/usr/bin/env python3
"""Portfolio backup executor — prepare and execute backup runs.

Two modes:

  --prepare  Validate target, run scope audit, check capacity and retention,
             freeze an execution packet, and print a review summary.  NO copy.

  --execute  Verify and execute a frozen execution packet.  Runs copy,
             verify, and restore-test phases with state transitions.

Usage:
    python3 tools/backup_execute.py --target /Volumes/Ivy-Portfolio-Backup --prepare
    python3 tools/backup_execute.py --packet execution-packet.json --execute
    python3 tools/backup_execute.py --help
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
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

STATE_TRANSITIONS = [
    "PREPARED",
    "COPY_IN_PROGRESS",
    "COPY_COMPLETE",
    "VERIFY_IN_PROGRESS",
    "VERIFIED",
    "RESTORE_IN_PROGRESS",
    "RESTORE_PROVEN",
    "FINALIZED",
]


def iso_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_git_sha() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
            cwd=REPO_ROOT,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def hash_packet(packet: dict[str, Any]) -> str:
    """Compute integrity hash of a packet, excluding any existing hash field."""
    clean = {k: v for k, v in packet.items() if k != "integrity_hash"}
    serialized = json.dumps(clean, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


def read_yaml_block(text: str, block_name: str) -> dict[str, Any]:
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

        while stack and stack[-1][1] >= indent:
            stack.pop()

        prefix = ".".join(p[0] for p in stack)
        full_prefix = f"{prefix}." if prefix else ""

        if content.startswith("- "):
            list_value = content[2:].strip().strip('"').strip("'")
            if stack:
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
            result[f"{full_prefix}{leaf_key}"] = val
            list_idx_key = f"{prefix}.{leaf_key}" if prefix else leaf_key
            list_indices.pop(list_idx_key, None)
        else:
            stack.append((leaf_key, indent))

    return result


def get_backup_policy(repo_slug: str) -> dict[str, Any]:
    ctrl_path = REPOS_DIR / repo_slug / "CONTROL.md"
    if not ctrl_path.exists():
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
    from tools.backup_planner import INCLUDE_GROUPS, EXCLUDE_GROUPS

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


def get_local_path(repo_dir: Path) -> Path | None:
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


def get_device_for_mount(mount_path: Path) -> str:
    try:
        df_proc = subprocess.run(
            ["df", str(mount_path)],
            capture_output=True, text=True, timeout=10,
        )
        for line in df_proc.stdout.splitlines():
            parts = line.split()
            if parts and parts[0].startswith("/dev/"):
                return parts[0]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def get_backing_image_info(mount_device: str) -> tuple[str, bool]:
    try:
        hdiutil = subprocess.run(
            ["hdiutil", "info"],
            capture_output=True, text=True, timeout=15,
        )
        sections = hdiutil.stdout.split("================================================")
        for section in sections:
            if mount_device not in section:
                continue
            found_path = ""
            found_encrypted = False
            for line in section.splitlines():
                s = line.strip()
                if s.startswith("image-path"):
                    found_path = s.split(":", 1)[1].strip()
                elif s.startswith("image-encrypted"):
                    val = s.split(":", 1)[1].strip().upper()
                    if val == "TRUE":
                        found_encrypted = True
            if found_path:
                return found_path, found_encrypted
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "", False


def get_last_verified_snapshot(target: Path) -> dict[str, Any]:
    """Find the last verified snapshot on the target volume."""
    snapshots = sorted(target.glob("snapshot-*"))
    if not snapshots:
        return {}

    last = snapshots[-1]
    result: dict[str, Any] = {"id": last.name}

    manifest_path = last / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            ver = manifest.get("verification", {})
            result["manifest_id"] = manifest.get("backup_id", "")
            result["verified_at"] = ver.get("verified_at", "")
        except (json.JSONDecodeError, OSError):
            pass

    return result


def check_capacity_and_retention(target: Path, estimated_bytes: int) -> dict[str, Any]:
    """Check target capacity and retention policy."""
    usage = shutil.disk_usage(str(target))
    logical_total = usage.total
    used = usage.used
    remaining = usage.free

    safety_margin = 20_000_000_000  # 20 GB
    fits = (remaining - safety_margin) > estimated_bytes

    existing_snapshots = len(list(target.glob("snapshot-*")))

    retention: dict[str, Any] = {
        "status": "CAPACITY_OK",
        "action_required": False,
        "existing_snapshots": existing_snapshots,
    }

    if not fits:
        retention["status"] = "INSUFFICIENT_CAPACITY"
        retention["action_required"] = True
    elif existing_snapshots >= 2:
        retention["status"] = "RETENTION_LIMIT_REACHED"
        retention["action_required"] = True
        retention["note"] = f"Already have {existing_snapshots} snapshots; manual cleanup needed"

    return {
        "logical_total": logical_total,
        "used": used,
        "remaining": remaining,
        "new_snapshot_estimated": estimated_bytes,
        "safety_margin": safety_margin,
        "fits": fits,
        "retention": retention,
    }


def prepare(target_path: Path) -> dict[str, Any]:
    """--prepare mode: validate, audit, build packet, no copy."""
    target = target_path.resolve()

    # 1. Validate target mount
    if not target.exists():
        return {"error": f"Target mount does not exist: {target}", "state": "FAILED"}
    if not os.access(str(target), os.W_OK):
        return {"error": f"Target is not writable: {target}", "state": "FAILED"}

    mount_device = get_device_for_mount(target)
    if not mount_device:
        return {"error": "Cannot determine mount device", "state": "FAILED"}

    # 2. Validate encryption
    backing_image, encrypted = get_backing_image_info(mount_device)
    if not encrypted:
        return {"error": f"Target {target} is not backed by an encrypted disk image", "state": "FAILED"}

    # 3. Run scope audit
    try:
        from tools.backup_scope_audit import audit
        findings = audit(last_manifest=None, scan_new=True)
        blocking = [f for f in findings if f["status"] in {
            "NEW_CANDIDATE", "POLICY_UNKNOWN", "STRATEGY_MISMATCH", "HUMAN_DECISION_REQUIRED",
        }]
        if blocking:
            return {
                "error": "Scope audit has unresolved blockers",
                "blocking_findings": blocking,
                "state": "BLOCKED",
            }
        scope_audit = {
            "status": "ALL_RESOLVED",
            "findings": findings,
        }
    except ImportError as exc:
        scope_audit = {"status": "AUDIT_SKIPPED", "error": str(exc)}

    # 4. Select snapshot ID
    now = datetime.now(UTC)
    snapshot_id = f"snapshot-{now.strftime('%Y-%m-%d')}"
    snapshot_path = target / snapshot_id

    # 5. Read backup policy and build repo entries
    repos: list[dict[str, Any]] = []
    total_estimated_bytes = 0

    for d in sorted(REPOS_DIR.iterdir()):
        if d.name.startswith("."):
            continue
        ctrl_path = d / "CONTROL.md"
        if not ctrl_path.exists():
            continue
        slug = d.name.replace("_", "-")
        policy = get_backup_policy(slug)
        local_path = get_local_path(d)

        if not policy:
            continue

        strategy = policy.get("strategy", "unknown")
        if strategy not in ("file_archive",):
            repos.append({
                "slug": slug,
                "strategy": strategy,
                "copy_roots": [],
            })
            continue

        if not local_path or not local_path.exists():
            continue

        include_groups = policy.get("include_groups", [])
        exclude_groups = policy.get("exclude_groups", [])

        resolved_includes, exclude_patterns = resolve_paths(
            local_path, include_groups, exclude_groups
        )
        if not resolved_includes:
            repos.append({
                "slug": slug,
                "strategy": strategy,
                "copy_roots": [],
            })
            continue

        copy_roots: list[dict[str, Any]] = []
        for inc_path in resolved_includes:
            rel = _relative_repo_path(inc_path, local_path)
            source = str(inc_path) + "/"
            dest = str(snapshot_path / "repos" / slug / rel)

            args = [
                "rsync", "-a", "--progress",
                "--exclude", "._*",
                "--exclude", ".DS_Store",
            ]
            for pattern in exclude_patterns:
                args.extend(["--exclude", pattern])
            args.append(source)
            args.append(dest)

            verify_args = [
                "rsync", "-avc", "--dry-run",
                "--exclude", "._*",
                "--exclude", ".DS_Store",
            ]
            for pattern in exclude_patterns:
                verify_args.extend(["--exclude", pattern])
            verify_args.append(source)
            verify_args.append(dest)

            copy_roots.append({
                "source": source,
                "dest": dest,
                "relative_path": rel,
                "args": args,
                "verify_args": verify_args,
            })

        # Estimate size
        estimated = _estimate_size(resolved_includes)
        total_estimated_bytes += estimated.get("bytes", 0)

        repos.append({
            "slug": slug,
            "strategy": strategy,
            "source_path": str(local_path),
            "include_groups": include_groups,
            "exclude_groups": exclude_groups,
            "copy_roots": copy_roots,
            "estimated": estimated,
        })

    # 6. Capacity and retention
    last_verified = get_last_verified_snapshot(target)
    capacity = check_capacity_and_retention(target, total_estimated_bytes)

    if not capacity["fits"]:
        return {
            "error": "Insufficient capacity",
            "capacity": capacity,
            "state": "FAILED",
        }

    git_sha = get_git_sha()

    packet: dict[str, Any] = {
        "packet_version": "1.0",
        "created_at": iso_now(),
        "ivy_control_sha": git_sha,
        "snapshot_id": snapshot_id,
        "snapshot_path": str(snapshot_path),
        "target": {
            "mount_path": str(target),
            "device": mount_device,
            "backing_image": backing_image,
            "encrypted": encrypted,
        },
        "last_verified_snapshot": last_verified,
        "scope_audit": scope_audit,
        "capacity": {k: v for k, v in capacity.items() if k != "retention"},
        "retention": capacity["retention"],
        "repositories": repos,
        "exclusions": [".DS_Store", "._*", "__pycache__/"],
        "forbidden_flags": ["--delete"],
    }

    integrity_hash = hash_packet(packet)
    packet["integrity_hash"] = integrity_hash

    return packet


def _relative_repo_path(absolute_path: Path, repo_local_path: Path) -> str:
    try:
        return str(absolute_path.relative_to(repo_local_path))
    except ValueError:
        return absolute_path.name


def _estimate_size(paths: list[Path]) -> dict[str, Any]:
    total_bytes = 0
    total_files = 0
    for path in paths:
        if not path.exists():
            continue
        try:
            du_proc = subprocess.run(
                ["du", "-sk", str(path)],
                capture_output=True, text=True, timeout=60,
            )
            if du_proc.returncode == 0:
                try:
                    total_bytes += int(du_proc.stdout.split("\t")[0]) * 1024
                except (IndexError, ValueError):
                    pass

            find_proc = subprocess.run(
                ["find", str(path), "-type", "f"],
                capture_output=True, text=True, timeout=60,
            )
            if find_proc.returncode == 0:
                total_files += len([l for l in find_proc.stdout.split("\n") if l.strip()])
        except (OSError, subprocess.TimeoutExpired):
            pass
    return {"bytes": total_bytes, "files": total_files}


def write_state(state_file: Path, data: dict[str, Any]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(data, indent=2, default=str) + "\n")


def execute(packet_path: Path) -> dict[str, Any]:
    """--execute mode: verify packet, run copy/verify/restore."""
    # Load packet
    try:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {"error": f"Cannot read packet: {exc}", "final_state": "FAILED"}

    # 1. Verify packet integrity hash
    stored_hash = packet.get("integrity_hash", "")
    if not stored_hash:
        return {"error": "Packet has no integrity_hash", "final_state": "FAILED"}
    computed = hash_packet(packet)
    if computed != stored_hash:
        return {"error": f"Packet integrity hash mismatch: stored={stored_hash[:16]}..., computed={computed[:16]}...", "final_state": "FAILED"}

    snapshot_path = Path(packet["snapshot_path"])
    target_info = packet["target"]
    target = Path(target_info["mount_path"])

    # 2. Revalidate target identity
    if not target.exists():
        return {"error": f"Target {target} not mounted", "final_state": "FAILED"}
    current_device = get_device_for_mount(target)
    if current_device != target_info["device"]:
        return {"error": f"Device mismatch: expected {target_info['device']}, got {current_device}", "final_state": "FAILED"}
    _, current_encrypted = get_backing_image_info(current_device)
    if current_encrypted != target_info.get("encrypted", False):
        return {"error": "Encryption state mismatch", "final_state": "FAILED"}

    # 3. Revalidate all sources exist
    copy_roots: list[dict[str, Any]] = []
    for repo in packet.get("repositories", []):
        for root in repo.get("copy_roots", []):
            source_stripped = root["source"].rstrip("/")
            if not Path(source_stripped).exists():
                return {"error": f"Source path does not exist: {source_stripped}", "final_state": "FAILED"}
            copy_roots.append(root)

    # 4. Confirm no unresolved scope findings
    scope_audit = packet.get("scope_audit", {})
    if scope_audit.get("status") not in ("ALL_RESOLVED", "AUDIT_SKIPPED"):
        return {"error": "Scope audit has unresolved findings", "final_state": "FAILED"}

    # 5. Confirm no pending retention decision
    retention = packet.get("retention", {})
    if retention.get("action_required", False):
        return {"error": f"Retention action required: {retention.get('status', 'unknown')}", "final_state": "FAILED"}

    # Initialize result
    created_at = iso_now()
    result: dict[str, Any] = {
        "packet": str(packet_path),
        "executed_at": created_at,
        "snapshot_id": packet["snapshot_id"],
        "snapshot_path": str(snapshot_path),
        "state": "PREPARED",
        "state_history": [{"state": "PREPARED", "timestamp": created_at}],
        "operations": [],
        "final_state": None,
    }
    result_path = snapshot_path / "execution-result.json"
    write_state(result_path, result)

    def transition(new_state: str) -> None:
        nonlocal result
        result["state"] = new_state
        result["state_history"].append({
            "state": new_state,
            "timestamp": iso_now(),
        })
        write_state(result_path, result)

    # 6. Execute copy commands sequentially
    transition("COPY_IN_PROGRESS")

    for root in copy_roots:
        args = root["args"]
        rel = root.get("relative_path", "")
        slug = root.get("slug") or next(
            (r["slug"] for r in packet["repositories"] if root in r.get("copy_roots", [])),
            "unknown",
        )

        print(f"Copying {slug}/{rel}...")
        sys.stdout.flush()

        op: dict[str, Any] = {
            "type": "copy",
            "repo_slug": slug,
            "relative_path": rel,
            "source": root["source"],
            "dest": root["dest"],
            "started_at": iso_now(),
        }

        try:
            proc = subprocess.run(
                args, capture_output=True, text=True, timeout=7200,
            )
            op["returncode"] = proc.returncode
            op["stdout"] = proc.stdout[-2000:] if len(proc.stdout) > 2000 else proc.stdout
            op["stderr"] = proc.stderr[-2000:] if len(proc.stderr) > 2000 else proc.stderr
            op["completed_at"] = iso_now()

            if proc.returncode != 0:
                op["status"] = "FAILED"
                result["operations"].append(op)
                result["final_state"] = "COPY_FAILED"
                write_state(result_path, result)
                return result

            op["status"] = "PASSED"
        except subprocess.TimeoutExpired:
            op["status"] = "TIMEOUT"
            op["error"] = "rsync timed out after 7200s"
            result["operations"].append(op)
            result["final_state"] = "COPY_FAILED"
            write_state(result_path, result)
            return result

        result["operations"].append(op)

    transition("COPY_COMPLETE")

    # 7. Execute verify commands
    transition("VERIFY_IN_PROGRESS")

    for root in copy_roots:
        verify_args = root["verify_args"]
        rel = root.get("relative_path", "")
        slug = root.get("slug") or next(
            (r["slug"] for r in packet["repositories"] if root in r.get("copy_roots", [])),
            "unknown",
        )

        print(f"Verifying {slug}/{rel}...")
        sys.stdout.flush()

        op: dict[str, Any] = {
            "type": "verify",
            "repo_slug": slug,
            "relative_path": rel,
            "started_at": iso_now(),
        }

        try:
            proc = subprocess.run(
                verify_args, capture_output=True, text=True, timeout=600,
            )
            op["returncode"] = proc.returncode
            op["stdout"] = proc.stdout[-2000:] if len(proc.stdout) > 2000 else proc.stdout
            op["stderr"] = proc.stderr[-2000:] if len(proc.stderr) > 2000 else proc.stderr
            op["completed_at"] = iso_now()

            output = proc.stdout + proc.stderr
            # Count diff lines: lines between "Transfer starting:" and "sent "
            in_file_list = False
            diffs: list[str] = []
            for raw_line in output.split("\n"):
                line = raw_line.strip()
                if "Transfer starting:" in line or "sending incremental file list" in line:
                    in_file_list = True
                    continue
                if in_file_list and line.startswith("sent "):
                    in_file_list = False
                    continue
                if in_file_list and not line.endswith("/") and line != ".":
                    diffs.append(line)

            op["diff_count"] = len(diffs)

            if proc.returncode != 0 or len(diffs) > 0:
                op["status"] = "FAILED"
                op["diffs"] = diffs[:20]
                result["operations"].append(op)
                result["final_state"] = "VERIFY_FAILED"
                write_state(result_path, result)
                return result

            op["status"] = "PASSED"
        except subprocess.TimeoutExpired:
            op["status"] = "TIMEOUT"
            result["operations"].append(op)
            result["final_state"] = "VERIFY_FAILED"
            write_state(result_path, result)
            return result

        result["operations"].append(op)

    transition("VERIFIED")

    # 8. Execute restore test
    transition("RESTORE_IN_PROGRESS")

    try:
        restore_test_args = [
            sys.executable,
            str(REPO_ROOT / "tools" / "backup_restore_test.py"),
            "--snapshot", str(snapshot_path),
            "--sample-count", "10",
            "--packet", str(packet_path),
            "--json",
        ]
        restore_proc = subprocess.run(
            restore_test_args,
            capture_output=True, text=True, timeout=300,
        )
        restore_result: dict[str, Any] = {
            "type": "restore_test",
            "returncode": restore_proc.returncode,
            "started_at": iso_now(),
        }
        if restore_proc.returncode == 0:
            try:
                restore_result["detail"] = json.loads(restore_proc.stdout)
            except json.JSONDecodeError:
                restore_result["detail"] = {"raw": restore_proc.stdout[:1000]}
            restore_result["status"] = "PASSED" if restore_proc.returncode == 0 else "FAILED"
        else:
            restore_result["status"] = "FAILED"
            restore_result["stderr"] = restore_proc.stderr[:1000]
            result["operations"].append(restore_result)
            result["final_state"] = "RESTORE_FAILED"
            write_state(result_path, result)
            return result

        result["operations"].append(restore_result)
    except (OSError, subprocess.TimeoutExpired) as exc:
        result["operations"].append({
            "type": "restore_test",
            "status": "FAILED",
            "error": str(exc),
        })
        result["final_state"] = "RESTORE_FAILED"
        write_state(result_path, result)
        return result

    transition("RESTORE_PROVEN")

    # 9. Write manifest
    # Build manifest from packet data
    manifest: dict[str, Any] = {
        "manifest_version": "1.0",
        "backup_id": f"{packet['snapshot_id']}_mac-cold-archive",
        "created_at": created_at,
        "source_host": os.uname().nodename,
        "target_volume": {
            "name": target.name,
            "mount_path": str(target),
            "encrypted": target_info.get("encrypted", False),
            "encryption_verified": target_info.get("encrypted", False),
        },
        "target_path": packet["snapshot_id"] + "/",
        "backup_class": "full",
        "repositories": [],
        "verification": {
            "method": "rsync_checksum",
            "checksum_mismatch_count": 0,
            "verified_at": iso_now(),
        },
        "excluded_globally": packet.get("exclusions", []),
        "restore_procedure": {
            "steps": [
                "Mount the backup volume",
                "Verify manifest checksum: shasum -a 256 manifest.json",
                "Copy desired paths: rsync -a <snapshot>/repos/<slug>/ <restore-path>/",
                "Verify restored files: rsync -avc --dry-run <restore-path>/ <snapshot>/repos/<slug>/",
            ],
            "notes": "Full restore guide at docs/BACKUP_RESTORE_GUIDE.md",
        },
    }
    for repo in packet.get("repositories", []):
        manifest["repositories"].append({
            "slug": repo["slug"],
            "source_path": repo.get("source_path", ""),
            "backup_path": f"repos/{repo['slug']}/",
            "backup_policy": get_backup_policy(repo["slug"]),
            "include_groups": repo.get("include_groups", []),
            "exclude_groups": repo.get("exclude_groups", []),
            "estimated": repo.get("estimated", {"bytes": 0, "files": 0}),
        })

    manifest_path = snapshot_path / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    # Write SHA256 sidecar
    try:
        sha_proc = subprocess.run(
            ["shasum", "-a", "256", str(manifest_path)],
            capture_output=True, text=True, timeout=30,
        )
        if sha_proc.returncode == 0:
            sha_path = manifest_path.with_suffix(manifest_path.suffix + ".sha256")
            sha_path.write_text(sha_proc.stdout)
    except (OSError, subprocess.TimeoutExpired):
        pass

    # 10. Mark FINALIZED
    transition("FINALIZED")
    result["final_state"] = "FINALIZED"
    write_state(result_path, result)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Portfolio backup executor — prepare and execute backup runs"
    )
    parser.add_argument(
        "--target", type=str, default=None,
        help="Target backup volume path (used with --prepare)",
    )
    parser.add_argument(
        "--prepare", action="store_true",
        help="Prepare mode: validate, scope audit, build execution packet (no copy)",
    )
    parser.add_argument(
        "--packet", type=str, default=None,
        help="Path to execution packet JSON (used with --execute)",
    )
    parser.add_argument(
        "--execute", action="store_true",
        help="Execute mode: run copy, verify, restore test from packet",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    args = parser.parse_args()

    if args.prepare:
        if not args.target:
            print("--target is required with --prepare", file=sys.stderr)
            return 1

        target = Path(args.target).resolve()
        result = prepare(target)

        if "error" in result:
            print(f"PREPARATION FAILED: {result['error']}", file=sys.stderr)
            if "blocking_findings" in result:
                for f in result["blocking_findings"]:
                    print(f"  ✗ {f['slug']}: {f['detail']}", file=sys.stderr)
            if args.json:
                json.dump(result, sys.stdout, indent=2, default=str)
                sys.stdout.write("\n")
            return 1

        # Write packet
        packet_path = REPO_ROOT / "execution-packet.json"
        packet_path.write_text(json.dumps(result, indent=2, default=str) + "\n")

        if args.json:
            json.dump(result, sys.stdout, indent=2, default=str)
            sys.stdout.write("\n")
        else:
            snapshot_path = result["snapshot_path"]
            target_info = result["target"]
            capacity = result["capacity"]
            retention = result["retention"]
            repos = result["repositories"]

            print("=" * 60)
            print("PORTFOLIO BACKUP EXECUTOR — PREPARE")
            print(f"Snapshot:  {result['snapshot_id']}")
            print(f"Created:   {result['created_at']}")
            print(f"Git SHA:   {result['ivy_control_sha']}")
            print(f"Target:    {target_info['mount_path']}")
            print(f"Device:    {target_info['device']}")
            print(f"Encrypted: {target_info['encrypted']}")
            print(f"Backing:   {target_info['backing_image']}")
            print(f"Capacity:  {capacity.get('logical_total', 0) / (1024**3):.1f} GB total, "
                  f"{capacity.get('remaining', 0) / (1024**3):.1f} GB free, "
                  f"estimate {capacity.get('new_snapshot_estimated', 0) / (1024**3):.1f} GB")
            print(f"Retention: {retention.get('status', 'unknown')} "
                  f"({retention.get('existing_snapshots', 0)} snapshots)")
            print(f"Scope:     {result['scope_audit'].get('status', 'unknown')}")
            print(f"Last verified: {result.get('last_verified_snapshot', {}).get('id', 'none')}")
            print()
            print("Repositories:")
            for r in repos:
                roots = r.get("copy_roots", [])
                est = r.get("estimated", {})
                print(f"  {r['slug']}: {len(roots)} root(s), "
                      f"{est.get('files', 0)} files, "
                      f"{est.get('bytes', 0) / (1024**3):.1f} GB")
                for root in roots:
                    print(f"    → {root['relative_path']}")
            print()
            print(f"Packet written to: {packet_path}")
            print(f"Integrity hash: {result['integrity_hash'][:16]}...")
            print()
            print("Review the packet, then execute:")
            print(f"  python3 tools/backup_execute.py --packet {packet_path} --execute")

        return 0

    elif args.execute:
        if not args.packet:
            print("--packet is required with --execute", file=sys.stderr)
            return 1

        packet_path = Path(args.packet)
        if not packet_path.exists():
            print(f"Packet not found: {packet_path}", file=sys.stderr)
            return 1

        result = execute(packet_path)
        final_state = result.get("final_state", "UNKNOWN")

        if args.json:
            json.dump(result, sys.stdout, indent=2, default=str)
            sys.stdout.write("\n")
        else:
            print("=" * 60)
            print("PORTFOLIO BACKUP EXECUTOR — EXECUTE")
            print(f"Packet:  {result['packet']}")
            print(f"Snapshot: {result.get('snapshot_id', '?')}")
            print(f"Result:  {final_state}")
            print()
            for op in result.get("operations", []):
                op_type = op.get("type", "?").upper()
                op_status = op.get("status", "?")
                slug = op.get("repo_slug", "")
                rel = op.get("relative_path", "")
                detail = ""
                if op_type == "COPY":
                    detail = f"{slug}/{rel}"
                elif op_type == "VERIFY":
                    diff_count = op.get("diff_count", -1)
                    detail = f"{slug}/{rel} ({diff_count} diffs)"
                elif op_type == "RESTORE_TEST":
                    detail = slug or ""
                marker = "✓" if op_status == "PASSED" else "✗"
                print(f"  [{marker}] {op_type}: {detail} [{op_status}]")

            print()
            state_history = result.get("state_history", [])
            for sh in state_history:
                print(f"  → {sh['state']} ({sh['timestamp']})")

        return 0 if final_state == "FINALIZED" else 1

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
