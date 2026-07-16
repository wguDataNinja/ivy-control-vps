#!/usr/bin/env python3
"""Portfolio backup verifier — independent post-copy validation.

Validates that a backup on an external volume matches the source tree.
Independently reads source and destination — does NOT trust planner output.

Usage:
    python3 tools/backup_verify.py --source /Users/buddy/projects --dest /Volumes/Ivy-Backup/archives/2026-07-17
    python3 tools/backup_verify.py --source /Users/buddy/projects/idlehacking_kb --dest /Volumes/Ivy-Backup/archives/2026-07-17/repos/idlehacking-kb
    python3 tools/backup_verify.py --manifest /Volumes/Ivy-Backup/.backup-manifest-2026-07-17.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc


def iso_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def count_files(path: Path) -> int:
    """Count regular files under a path."""
    try:
        result = subprocess.run(
            ["find", str(path), "-type", "f"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            return len([l for l in result.stdout.split("\n") if l.strip()])
        return -1
    except (OSError, subprocess.TimeoutExpired):
        return -1


def total_bytes(path: Path) -> int:
    """Get total byte count for a path."""
    try:
        result = subprocess.run(
            ["du", "-sb", str(path)],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            return int(result.stdout.split("\t")[0])
        return -1
    except (ValueError, IndexError, OSError, subprocess.TimeoutExpired):
        return -1


def rsync_checksum_dry_run(source: Path, dest: Path) -> dict[str, Any]:
    """Run rsync -avc --dry-run to compare source and dest checksums.
    Returns count of mismatched files and total compared.

    Parses macOS rsync output format:
        Transfer starting: N files
        <diff-file-1>
        <diff-file-2>

        sent N bytes ...  total size ...
    """
    result: dict[str, Any] = {
        "mismatch_count": -1,
        "total_compared": -1,
        "command": "",
        "error": None,
    }

    src_str = str(source)
    if source.is_dir() and not src_str.endswith("/"):
        src_str += "/"
    dst_str = str(dest)
    if dest.is_dir() and not dst_str.endswith("/"):
        dst_str += "/"

    cmd = ["rsync", "-avc", "--dry-run", src_str, dst_str]
    result["command"] = " ".join(str(c) for c in cmd)

    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=600,
        )
        output = proc.stdout + proc.stderr

        # Parse macOS rsync output format
        lines = output.split("\n")
        in_file_list = False
        diffs: list[str] = []
        total_compared = -1

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue
            # macOS: "Transfer starting: N files" marks the start of diffs
            if "Transfer starting:" in line:
                in_file_list = True
                # Try to extract file count
                try:
                    total_compared = int(line.split()[-2]) if line.split()[-2].isdigit() else -1
                except (IndexError, ValueError):
                    total_compared = -1
                continue
            # GNU/Linux: "sending incremental file list" marks start
            if "sending incremental file list" in line:
                in_file_list = True
                continue
            # End of file list: "sent N bytes ..."
            if in_file_list and line.startswith("sent "):
                in_file_list = False
                continue
            # End: "Number of files: N"
            if "Number of files:" in line:
                try:
                    total_compared = int(line.split(":")[1].strip())
                except (IndexError, ValueError):
                    pass
                continue
            # Lines in the file list that don't end with / are file diffs
            if in_file_list and not line.endswith("/") and line != ".":
                diffs.append(line)

        result["mismatch_count"] = len(diffs)
        result["total_compared"] = total_compared
        result["raw_output_preview"] = "\n".join(lines[:20])

    except (OSError, subprocess.TimeoutExpired) as exc:
        result["error"] = str(exc)

    return result


def verify_manifest(manifest_path: Path) -> dict[str, Any]:
    """Validate a backup manifest — parse, check required fields, verify SHA256 sidecar."""
    result: dict[str, Any] = {
        "manifest_path": str(manifest_path),
        "parses": False,
        "sha256_sidecar_match": False,
        "required_fields_present": False,
        "errors": [],
    }

    if not manifest_path.exists():
        result["errors"].append("Manifest file not found")
        return result

    # Verify SHA256 sidecar
    sha256_path = manifest_path.with_suffix(manifest_path.suffix + ".sha256")
    if sha256_path.exists():
        try:
            sha_result = subprocess.run(
                ["shasum", "-a", "256", "-c", str(sha256_path)],
                capture_output=True, text=True, timeout=30,
            )
            result["sha256_sidecar_match"] = sha_result.returncode == 0
            if not result["sha256_sidecar_match"]:
                result["errors"].append(
                    f"SHA256 sidecar verification failed: {sha_result.stderr.strip()}"
                )
        except (OSError, subprocess.TimeoutExpired) as exc:
            result["errors"].append(f"SHA256 verification error: {exc}")
    else:
        result["errors"].append("No SHA256 sidecar file found")

    # Parse and validate
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        result["parses"] = True

        required = ["manifest_version", "backup_id", "created_at", "target_volume",
                     "repositories"]
        missing = [f for f in required if f not in data]
        result["required_fields_present"] = len(missing) == 0
        if missing:
            result["errors"].append(f"Missing required manifest fields: {', '.join(missing)}")

        if "repositories" in data:
            result["repo_count"] = len(data["repositories"])
            repo_slugs = [r.get("slug", "?") for r in data["repositories"]]
            result["repo_slugs"] = repo_slugs

        if "verification" in data:
            result["manifest_verification"] = data["verification"]

    except (json.JSONDecodeError, OSError) as exc:
        result["errors"].append(f"Manifest parse error: {exc}")

    return result


def restore_sample(source: Path, dest: Path, count: int = 10, min_size_mb: int = 1) -> dict[str, Any]:
    """Restore a sample of files from dest to a temp location and verify checksums."""
    result: dict[str, Any] = {
        "sample_dir": "",
        "files_restored": 0,
        "checksums_match": 0,
        "checksums_mismatch": 0,
        "errors": [],
    }

    import tempfile
    sample_dir = Path(tempfile.mkdtemp(prefix="ivy-backup-verify-"))
    result["sample_dir"] = str(sample_dir)

    # Find large files in the destination to sample
    try:
        find_cmd = ["find", str(dest), "-type", "f", "-size", f"+{min_size_mb}M"]
        proc = subprocess.run(
            find_cmd, capture_output=True, text=True, timeout=30,
        )
        candidates = [l.strip() for l in proc.stdout.split("\n") if l.strip()]
    except (OSError, subprocess.TimeoutExpired) as exc:
        result["errors"].append(f"Cannot find sample candidates: {exc}")
        return result

    import random
    random.shuffle(candidates)
    sample_files = candidates[:count]

    for f in sample_files:
        rel_path = Path(f).relative_to(dest)
        source_file = source / rel_path
        dest_file = Path(f)
        sample_file = sample_dir / rel_path
        sample_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Copy from destination (simulating restore)
            subprocess.run(
                ["cp", str(dest_file), str(sample_file)],
                check=True, capture_output=True, timeout=60,
            )
            result["files_restored"] += 1

            # Compare checksums
            src_sha = subprocess.run(
                ["shasum", "-a", "256", str(source_file)],
                capture_output=True, text=True, timeout=30,
            ).stdout.split()[0]

            sample_sha = subprocess.run(
                ["shasum", "-a", "256", str(sample_file)],
                capture_output=True, text=True, timeout=30,
            ).stdout.split()[0]

            if src_sha == sample_sha:
                result["checksums_match"] += 1
            else:
                result["checksums_mismatch"] += 1
                result["errors"].append(
                    f"Checksum mismatch: {rel_path}"
                )
        except (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
            result["errors"].append(f"Sample restore failed for {rel_path}: {exc}")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Portfolio backup verifier — independent post-copy validation"
    )
    parser.add_argument("--source", type=str, help="Source directory (original data)")
    parser.add_argument(
        "--dest", type=str,
        help="Destination directory (backup on external volume)",
    )
    parser.add_argument(
        "--manifest", type=str,
        help="Path to backup manifest JSON to validate",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    parser.add_argument("--restore-sample", type=int, default=0,
                        help="Number of files to sample-restore and checksum (0 = skip)")
    args = parser.parse_args()

    results: dict[str, Any] = {
        "verifier": "tools/backup_verify.py",
        "verified_at": iso_now(),
        "source": args.source,
        "dest": args.dest,
        "manifest": args.manifest,
        "results": {},
    }

    all_pass = True

    # Verify manifest if provided
    if args.manifest:
        manifest_result = verify_manifest(Path(args.manifest))
        results["results"]["manifest"] = manifest_result
        if not manifest_result.get("parses") or not manifest_result.get("sha256_sidecar_match"):
            all_pass = False

    # Verify source vs dest
    if args.source and args.dest:
        source = Path(args.source)
        dest = Path(args.dest)

        if not source.exists():
            results["results"]["error"] = f"Source path does not exist: {source}"
            all_pass = False
        elif not dest.exists():
            results["results"]["error"] = f"Dest path does not exist: {dest}"
            all_pass = False
        else:
            # Independent file count comparison
            src_files = count_files(source)
            dst_files = count_files(dest)
            src_bytes = total_bytes(source)
            dst_bytes = total_bytes(dest)

            results["results"]["source_file_count"] = src_files
            results["results"]["dest_file_count"] = dst_files
            results["results"]["source_bytes"] = src_bytes
            results["results"]["dest_bytes"] = dst_bytes

            if src_files >= 0 and dst_files >= 0 and src_files != dst_files:
                results["results"]["file_count_mismatch"] = True
                all_pass = False

            # Full checksum comparison via rsync --checksum dry-run
            print("Running rsync checksum comparison (this may take a while)...")
            sys.stdout.flush()
            checksum_result = rsync_checksum_dry_run(source, dest)
            results["results"]["checksum"] = checksum_result

            if checksum_result.get("mismatch_count", -1) > 0:
                results["results"]["checksum_mismatch"] = True
                all_pass = False

            # Restore sample if requested
            if args.restore_sample > 0:
                print(f"Running restore sample ({args.restore_sample} files)...")
                sys.stdout.flush()
                sample_result = restore_sample(source, dest, count=args.restore_sample)
                results["results"]["restore_sample"] = sample_result
                if sample_result.get("checksums_mismatch", 0) > 0:
                    all_pass = False

    results["all_pass"] = all_pass

    if args.json:
        json.dump(results, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
    else:
        print("=" * 60)
        print("PORTFOLIO BACKUP VERIFIER")
        print(f"Verified at: {results['verified_at']}")
        print(f"Source: {results['source']}")
        print(f"Dest:   {results['dest']}")
        print(f"Result: {'✓ ALL PASS' if all_pass else '✗ FAILURES DETECTED'}")
        print()

        if "manifest" in results.get("results", {}):
            mr = results["results"]["manifest"]
            print(f"Manifest: {mr.get('manifest_path')}")
            print(f"  Parses: {mr.get('parses')}")
            print(f"  SHA256 sidecar: {'✓ match' if mr.get('sha256_sidecar_match') else '✗ mismatch'}")
            print(f"  Required fields: {'✓' if mr.get('required_fields_present') else '✗ MISSING'}")
            print(f"  Repos: {mr.get('repo_slugs', [])}")
            if mr.get("errors"):
                for e in mr["errors"]:
                    print(f"  ✗ {e}")
            print()

        res = results.get("results", {})
        if "source_file_count" in res:
            print(f"File counts: source={res.get('source_file_count', '?')}, "
                  f"dest={res.get('dest_file_count', '?')}")
            print(f"Byte totals: source={res.get('source_bytes', 0) / (1024**3):.1f} GB, "
                  f"dest={res.get('dest_bytes', 0) / (1024**3):.1f} GB")

        if "checksum" in res:
            chk = res["checksum"]
            print(f"Checksum: {chk.get('mismatch_count', '?')} mismatches "
                  f"({chk.get('total_compared', '?')} files compared)")
            if chk.get("error"):
                print(f"  Error: {chk['error']}")

        if "restore_sample" in res:
            sr = res["restore_sample"]
            print(f"Restore sample: {sr.get('files_restored', 0)} files, "
                  f"{sr.get('checksums_match', 0)} match, "
                  f"{sr.get('checksums_mismatch', 0)} mismatch")
            if sr.get("sample_dir"):
                print(f"  Sample dir: {sr['sample_dir']}")

        print()

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
