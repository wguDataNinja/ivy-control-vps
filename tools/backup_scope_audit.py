#!/usr/bin/env python3
"""Portfolio backup scope audit — required gate before every backup.

Compares current Mac portfolio state, CONTROL.md backup policy, and last
verified snapshot manifest to produce a structured finding list.

Statuses:
  KNOWN_AND_COVERED      — has backup policy, strategy is file_archive, sources exist
  KNOWN_GIT_REMOTE_ONLY  — strategy is git_remote, no file backup needed
  KNOWN_DATABASE_BACKUP  — strategy is database_dump
  KNOWN_EXCLUDED         — explicitly excluded by policy
  NEW_CANDIDATE          — discovered repo not in CONTROL.md
  POLICY_UNKNOWN         — in CONTROL.md but backup dimensions unknown/missing
  PATH_MISSING           — local_path doesn't exist on disk
  STRATEGY_MISMATCH      — has stateful data but strategy says git_remote
  HUMAN_DECISION_REQUIRED— needs Buddy review
  RETIREMENT_CANDIDATE   — in last snapshot but no longer in policy

NEW_CANDIDATE, POLICY_UNKNOWN, STRATEGY_MISMATCH, and HUMAN_DECISION_REQUIRED
block backup preparation.

Usage:
    python3 tools/backup_scope_audit.py
    python3 tools/backup_scope_audit.py --last-manifest /Volumes/.../manifest.json
    python3 tools/backup_scope_audit.py --last-manifest ... --output audit.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
REPOS_DIR = REPO_ROOT / "repos"
HOST_PROJECTS = Path.home() / "projects"
UTC = timezone.utc

BLOCKING_STATUSES = frozenset({
    "NEW_CANDIDATE",
    "POLICY_UNKNOWN",
    "STRATEGY_MISMATCH",
    "HUMAN_DECISION_REQUIRED",
})


def iso_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_yaml_block(text: str, block_name: str) -> dict[str, Any]:
    """Naive YAML block parser for CONTROL.md front matter."""
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


def check_stateful_data(local_path: Path) -> list[str]:
    """Check if a git_remote repo has local data that should be backed up."""
    stateful: list[str] = []
    stateful_indicators = [
        "_internal/", "_outbox/", "data/", "capture/",
        "runtime/", "inbox/", "backups/",
    ]
    for indicator in stateful_indicators:
        candidate = local_path / indicator
        if candidate.exists():
            file_count = 0
            try:
                proc = subprocess.run(
                    ["find", str(candidate), "-type", "f"],
                    capture_output=True, text=True, timeout=30,
                )
                file_count = len([l for l in proc.stdout.split("\n") if l.strip()])
            except (OSError, subprocess.TimeoutExpired):
                file_count = -1
            stateful.append(f"{indicator} ({file_count} files)")
    return stateful


def discover_new_candidates() -> list[dict[str, Any]]:
    """Scan ~/projects/ for git repos not in CONTROL.md."""
    known_slugs: set[str] = set()
    for d in sorted(REPOS_DIR.iterdir()):
        if d.name.startswith("."):
            continue
        slug = d.name.replace("_", "-")
        known_slugs.add(slug)

    candidates: list[dict[str, Any]] = []
    if not HOST_PROJECTS.exists() or not HOST_PROJECTS.is_dir():
        return candidates

    try:
        for child in sorted(HOST_PROJECTS.iterdir()):
            if child.name.startswith("."):
                continue
            if not child.is_dir():
                continue
            git_dir = child / ".git"
            if not git_dir.exists():
                continue
            slug = child.name.replace("_", "-")
            if slug in known_slugs:
                continue
            candidates.append({
                "path": str(child),
                "slug": slug,
                "discovered_at": iso_now(),
            })
    except PermissionError:
        pass

    return candidates


def read_manifest_repos(last_manifest: Path) -> list[dict[str, Any]]:
    """Read repo slugs from a backup manifest."""
    data = json.loads(last_manifest.read_text(encoding="utf-8"))
    return data.get("repositories", [])


def audit(
    last_manifest: Path | None = None,
    scan_new: bool = True,
) -> list[dict[str, Any]]:
    """Run the scope audit and return findings."""
    findings: list[dict[str, Any]] = []

    known_slugs: set[str] = set()

    for d in sorted(REPOS_DIR.iterdir()):
        if d.name.startswith("."):
            continue
        ctrl_path = d / "CONTROL.md"
        if not ctrl_path.exists():
            continue

        slug = d.name.replace("_", "-")
        known_slugs.add(slug)
        policy = get_backup_policy(slug)
        local_path = get_local_path(d)

        if not policy:
            findings.append({
                "slug": slug,
                "status": "POLICY_UNKNOWN",
                "detail": "No backup policy dimensions defined in CONTROL.md",
            })
            continue

        strategy = policy.get("strategy", "unknown")
        importance = policy.get("importance", "unknown")
        include_groups = policy.get("include_groups", [])

        if strategy == "file_archive":
            if not local_path or not local_path.exists():
                findings.append({
                    "slug": slug,
                    "status": "PATH_MISSING",
                    "detail": f"Local path does not exist: {local_path}",
                })
                continue

            if not include_groups:
                findings.append({
                    "slug": slug,
                    "status": "HUMAN_DECISION_REQUIRED",
                    "detail": "file_archive strategy but no include_groups defined",
                })
                continue

            findings.append({
                "slug": slug,
                "status": "KNOWN_AND_COVERED",
                "detail": f"strategy={strategy}, {len(include_groups)} include group(s), path exists",
            })

        elif strategy == "git_remote":
            if local_path and local_path.exists():
                stateful = check_stateful_data(local_path)
                if stateful:
                    findings.append({
                        "slug": slug,
                        "status": "STRATEGY_MISMATCH",
                        "detail": f"strategy=git_remote but contains stateful data: {', '.join(stateful)}",
                    })
                    continue

            findings.append({
                "slug": slug,
                "status": "KNOWN_GIT_REMOTE_ONLY",
                "detail": "strategy=git_remote, no file archive needed",
            })

        elif strategy == "database_dump":
            findings.append({
                "slug": slug,
                "status": "KNOWN_DATABASE_BACKUP",
                "detail": "strategy=database_dump, VPS-side PostgreSQL backup",
            })

        elif strategy == "regenerate":
            findings.append({
                "slug": slug,
                "status": "KNOWN_EXCLUDED",
                "detail": "strategy=regenerate, no backup needed",
            })

        else:
            findings.append({
                "slug": slug,
                "status": "POLICY_UNKNOWN",
                "detail": f"Unknown strategy: {strategy}",
            })

    # Check against last verified manifest for retirement candidates
    if last_manifest and last_manifest.exists():
        manifest_repos = read_manifest_repos(last_manifest)
        manifest_slugs = {r["slug"] for r in manifest_repos}
        retired = manifest_slugs - known_slugs
        for rs in sorted(retired):
            findings.append({
                "slug": rs,
                "status": "RETIREMENT_CANDIDATE",
                "detail": "Present in last verified manifest but not in current CONTROL.md policy",
            })

    # Scan for new candidates
    if scan_new:
        new_repos = discover_new_candidates()
        for nr in new_repos:
            findings.append({
                "slug": nr["slug"],
                "status": "NEW_CANDIDATE",
                "detail": f"Discovered git repo at {nr['path']} not in CONTROL.md",
            })

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Portfolio backup scope audit — required gate before every backup"
    )
    parser.add_argument(
        "--last-manifest", type=str, default=None,
        help="Path to last verified snapshot manifest.json",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Write audit results to file",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    parser.add_argument(
        "--no-scan", action="store_true",
        help="Skip ~/projects/ scan for new repos",
    )
    args = parser.parse_args()

    last_manifest = Path(args.last_manifest) if args.last_manifest else None
    findings = audit(last_manifest=last_manifest, scan_new=not args.no_scan)

    blocking = [f for f in findings if f["status"] in BLOCKING_STATUSES]
    status = "ALL_RESOLVED" if not blocking else "BLOCKERS_PRESENT"

    result: dict[str, Any] = {
        "audit_version": "1.0",
        "audited_at": iso_now(),
        "status": status,
        "blocking_count": len(blocking),
        "total_findings": len(findings),
        "findings": findings,
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2) + "\n")
        print(f"Scope audit written to {output_path}")

    if args.json:
        json.dump(result, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
    else:
        print("=" * 60)
        print("PORTFOLIO BACKUP SCOPE AUDIT")
        print(f"Audited at: {result['audited_at']}")
        print(f"Status: {result['status']} ({result['blocking_count']} blocker(s))")
        print()
        for f in findings:
            marker = "✗" if f["status"] in BLOCKING_STATUSES else " "
            print(f"  [{marker}] {f['slug']}: {f['status']}")
            print(f"         {f['detail']}")
        print()
        print(f"Total: {result['total_findings']} findings, {result['blocking_count']} blocking")

    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
