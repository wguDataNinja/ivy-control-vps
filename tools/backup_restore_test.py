#!/usr/bin/env python3
"""Bounded portfolio restore test.

Reads a snapshot manifest, selects sample files from each repository,
restores them to /private/tmp/ivy-restore-test-<date>/, and verifies
SHA-256 checksums against the source tree. Never modifies source data.

Usage:
    python3 tools/backup_restore_test.py --snapshot /Volumes/.../snapshot-2026-07-17
    python3 tools/backup_restore_test.py --snapshot ... --sample-count 20
    python3 tools/backup_restore_test.py --snapshot ... --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc


def iso_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_of(path: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["shasum", "-a", "256", str(path)],
            capture_output=True, text=True, timeout=60,
        )
        if proc.returncode == 0:
            return proc.stdout.split()[0]
        return None
    except (OSError, subprocess.TimeoutExpired):
        return None


def check_skip_path(rel_path: str) -> bool:
    skip_patterns = [
        ".DS_Store",
        "._",
        "__pycache__",
        ".git/",
    ]
    for p in skip_patterns:
        if p in rel_path:
            return True
    return False


def select_samples(
    snapshot_repo: dict[str, Any],
    snapshot_path: Path,
    count: int,
) -> list[dict[str, Any]]:
    """Select sample files from a snapshot repo's backed-up directories."""
    samples: list[dict[str, Any]] = []

    backup_path_str = snapshot_repo.get("backup_path", "")
    if not backup_path_str:
        return samples

    repo_dest = snapshot_path / backup_path_str
    if not repo_dest.exists():
        return samples

    try:
        find_proc = subprocess.run(
            ["find", str(repo_dest), "-type", "f", "-size", "+1M"],
            capture_output=True, text=True, timeout=30,
        )
        candidates = [l.strip() for l in find_proc.stdout.split("\n") if l.strip()]
    except (OSError, subprocess.TimeoutExpired):
        return samples

    # Filter out skip patterns
    candidates = [c for c in candidates if not check_skip_path(c)]

    # If not enough large files, include smaller ones
    if len(candidates) < count:
        try:
            find_proc = subprocess.run(
                ["find", str(repo_dest), "-type", "f"],
                capture_output=True, text=True, timeout=30,
            )
            smaller = [l.strip() for l in find_proc.stdout.split("\n") if l.strip()]
            smaller = [c for c in smaller if not check_skip_path(c)]
            candidates = list(dict.fromkeys(candidates + smaller))
        except (OSError, subprocess.TimeoutExpired):
            pass

    # Deterministic selection based on sorted order
    candidates.sort()
    selected = candidates[:count]

    for f in selected:
        rel_path = Path(f).relative_to(repo_dest)
        samples.append({
            "dest_path": f,
            "relative_path": str(rel_path),
        })

    return samples


def find_source_for(
    rel_path: str,
    repo_config: dict[str, Any],
    packet: dict[str, Any] | None,
) -> Path | None:
    """Find the source file corresponding to a relative backup path.

    Looks up the source root from the packet's copy_roots or falls back
    to the manifest's source_path.
    """
    # Try to find matching copy root from packet
    if packet:
        for root in repo_config.get("copy_roots", []):
            root_rel = root.get("relative_path", "")
            if rel_path.startswith(root_rel):
                # Build source path
                source_base = root.get("source", "").rstrip("/")
                sub_path = rel_path[len(root_rel):].lstrip("/")
                candidate = Path(source_base) / sub_path
                if candidate.exists():
                    return candidate

    # Fallback: use source_path from repo config
    source_path_str = repo_config.get("source_path") or repo_config.get("source_path")
    if not source_path_str:
        return None

    source_root = Path(source_path_str)
    candidate = source_root / rel_path
    if candidate.exists():
        return candidate

    return None


def run_restore_test(
    snapshot_path: Path,
    sample_count: int = 10,
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute bounded restore test."""
    manifest_path = snapshot_path / "manifest.json"
    if not manifest_path.exists():
        return {
            "status": "RESTORE_FAILED",
            "error": f"Manifest not found: {manifest_path}",
        }

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    restore_root = Path(f"/private/tmp/ivy-restore-test-{date_str}")
    restore_root.mkdir(parents=True, exist_ok=True)

    # Get repo config from packet if available, otherwise from manifest
    repos_config = manifest.get("repositories", [])
    packet_repos = {r["slug"]: r for r in (packet.get("repositories", []) if packet else [])}

    results: dict[str, Any] = {
        "manifest_path": str(manifest_path),
        "snapshot_path": str(snapshot_path.resolve()),
        "test_run_at": iso_now(),
        "restore_root": str(restore_root),
        "repos": [],
        "total_restored": 0,
        "total_checksum_match": 0,
        "total_checksum_mismatch": 0,
        "total_errors": 0,
        "status": "RESTORE_PROVEN",
    }

    for repo_config in repos_config:
        slug = repo_config.get("slug", "unknown")
        packet_repo = packet_repos.get(slug, repo_config)

        samples = select_samples(repo_config, snapshot_path, sample_count)
        if not samples:
            results["repos"].append({
                "slug": slug,
                "samples_requested": sample_count,
                "samples_found": 0,
                "status": "SKIPPED",
                "detail": "No sample files found in backup",
            })
            results["total_errors"] += 1
            continue

        repo_result: dict[str, Any] = {
            "slug": slug,
            "samples_requested": sample_count,
            "samples_found": len(samples),
            "restored": 0,
            "checksum_match": 0,
            "checksum_mismatch": 0,
            "errors": [],
            "files": [],
        }

        for sample in samples:
            rel_path = sample["relative_path"]
            dest_file = Path(sample["dest_path"])
            restore_file = restore_root / slug / rel_path
            restore_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy from backup (simulating restore)
            try:
                cp_proc = subprocess.run(
                    ["cp", str(dest_file), str(restore_file)],
                    capture_output=True, text=True, timeout=60,
                )
                if cp_proc.returncode != 0:
                    repo_result["errors"].append(f"cp failed for {rel_path}: {cp_proc.stderr.strip()}")
                    continue
            except (OSError, subprocess.TimeoutExpired) as exc:
                repo_result["errors"].append(f"cp error for {rel_path}: {exc}")
                continue

            repo_result["restored"] += 1

            # Find source file and compare checksums
            source_file = find_source_for(rel_path, packet_repo, packet)
            if source_file is None:
                repo_result["errors"].append(f"Cannot find source for {rel_path}")
                continue

            source_sha = sha256_of(source_file)
            restored_sha = sha256_of(restore_file)

            if source_sha is None or restored_sha is None:
                repo_result["errors"].append(f"Cannot checksum {rel_path}")
                continue

            match = source_sha == restored_sha
            repo_result["files"].append({
                "relative_path": rel_path,
                "source_sha": source_sha[:16] + "...",
                "restored_sha": restored_sha[:16] + "...",
                "match": match,
            })

            if match:
                repo_result["checksum_match"] += 1
            else:
                repo_result["checksum_mismatch"] += 1
                repo_result["errors"].append(f"Checksum mismatch: {rel_path}")

        repo_result["status"] = (
            "FAILED" if repo_result["checksum_mismatch"] > 0 or repo_result["errors"]
            else "PASSED"
        )

        results["repos"].append(repo_result)
        results["total_restored"] += repo_result["restored"]
        results["total_checksum_match"] += repo_result["checksum_match"]
        results["total_checksum_mismatch"] += repo_result["checksum_mismatch"]
        results["total_errors"] += len(repo_result["errors"])

    if results["total_checksum_mismatch"] > 0 or results["total_errors"] > 0:
        results["status"] = "RESTORE_FAILED"

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bounded portfolio restore test"
    )
    parser.add_argument(
        "--snapshot", type=str, required=True,
        help="Path to snapshot directory (e.g., /Volumes/.../snapshot-2026-07-17)",
    )
    parser.add_argument(
        "--sample-count", type=int, default=10,
        help="Number of sample files per repository (default: 10)",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    parser.add_argument(
        "--output", type=str, default=None,
        help="Write result to file (e.g., verification/restore-test.json)",
    )
    parser.add_argument(
        "--packet", type=str, default=None,
        help="Execution packet JSON (used for source path resolution)",
    )
    args = parser.parse_args()

    snapshot_path = Path(args.snapshot).resolve()
    if not snapshot_path.exists():
        print(f"Snapshot path does not exist: {snapshot_path}", file=sys.stderr)
        return 1

    packet = None
    if args.packet:
        packet_path = Path(args.packet)
        if packet_path.exists():
            packet = json.loads(packet_path.read_text(encoding="utf-8"))

    result = run_restore_test(
        snapshot_path,
        sample_count=args.sample_count,
        packet=packet,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2) + "\n")
        print(f"Restore test result written to {output_path}")

    if args.json:
        json.dump(result, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
    else:
        print("=" * 60)
        print("PORTFOLIO RESTORE TEST")
        print(f"Snapshot: {result['snapshot_path']}")
        print(f"Restore root: {result['restore_root']}")
        print(f"Status: {result['status']}")
        print()
        for r in result.get("repos", []):
            status_mark = "✓" if r["status"] == "PASSED" else ("✗" if r["status"] == "FAILED" else "~")
            print(f"  [{status_mark}] {r['slug']}: {r['status']}")
            print(f"       {r.get('restored', 0)} restored, "
                  f"{r.get('checksum_match', 0)} match, "
                  f"{r.get('checksum_mismatch', 0)} mismatch")
            if r.get("errors"):
                for e in r["errors"]:
                    print(f"       ✗ {e}")
        print()
        print(f"Total: {result['total_restored']} files, "
              f"{result['total_checksum_match']} checksum match, "
              f"{result['total_checksum_mismatch']} mismatch")
        print(f"Result: {result['status']}")

    return 0 if result["status"] == "RESTORE_PROVEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
