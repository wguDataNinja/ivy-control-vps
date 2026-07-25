#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
import time
from pathlib import Path

from .models import parse_publication_manifest
from .validation import validate


def _serialize(obj):
    if dataclasses.is_dataclass(obj):
        d = {}
        for field in dataclasses.fields(obj):
            val = getattr(obj, field.name)
            d[field.name] = _serialize(val)
        return d
    if isinstance(obj, (list, tuple)):
        return [_serialize(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    return obj


def _resolve_manifest_path(raw: str) -> str | None:
    candidates = [
        raw,
        os.path.abspath(os.path.expanduser(raw)),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def _load_yaml(path: str) -> dict:
    try:
        import yaml
    except ImportError:
        print("error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    with open(path, "r") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        print(f"error: manifest must be a YAML mapping, got {type(data).__name__}", file=sys.stderr)
        sys.exit(1)
    return data


def _load_json(path: str) -> dict:
    with open(path, "r") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        print(f"error: manifest must be a JSON object, got {type(data).__name__}", file=sys.stderr)
        sys.exit(1)
    return data


def _write_evidence(
    output_dir: str, manifest_path: str, result: object
) -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    dirpath = os.path.abspath(os.path.expanduser(output_dir))
    os.makedirs(dirpath, exist_ok=True)

    evidence_path = os.path.join(dirpath, f"steward-result-{ts}.json")
    with open(evidence_path, "w") as f:
        json.dump(_serialize(result), f, indent=2, default=str)
    return evidence_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Git Steward MVP — publication candidate validation"
    )
    parser.add_argument(
        "manifest",
        help="Path to publication manifest (YAML or JSON)",
    )
    parser.add_argument(
        "--format",
        choices=["yaml", "json", "auto"],
        default="auto",
        help="Manifest format (default: auto-detect from extension)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit result as JSON",
    )
    parser.add_argument(
        "--evidence-dir",
        help="Override evidence output directory",
    )
    args = parser.parse_args()

    # Resolve manifest
    manifest_path = _resolve_manifest_path(args.manifest)
    if manifest_path is None:
        print(f"error: manifest file not found: {args.manifest}", file=sys.stderr)
        return 1

    # Determine format
    fmt = args.format
    if fmt == "auto":
        ext = os.path.splitext(manifest_path)[1].lower()
        if ext in (".yaml", ".yml"):
            fmt = "yaml"
        elif ext == ".json":
            fmt = "json"
        else:
            print(f"error: cannot determine format for {manifest_path}; use --format", file=sys.stderr)
            return 1

    # Load manifest
    if fmt == "yaml":
        data = _load_yaml(manifest_path)
    else:
        data = _load_json(manifest_path)

    manifest = parse_publication_manifest(data)

    # Override evidence dir from CLI
    if args.evidence_dir:
        object.__setattr__(manifest, "evidence_output_dir", args.evidence_dir)

    # Run validation
    result = validate(manifest)

    # Write evidence
    evidence_dir = manifest.evidence_output_dir or "_internal/evidence"
    evidence_path = _write_evidence(evidence_dir, manifest_path, result)
    evidence_abspath = os.path.abspath(evidence_path)

    # Update evidence paths in result
    object.__setattr__(
        result, "evidence_paths", (evidence_abspath,)
    )

    result_dict = _serialize(result)

    if args.json:
        print(json.dumps(result_dict, indent=2, default=str))
    else:
        v = result.validation
        status = "PASSED" if v.passed else "FAILED"
        print(f"\n{'='*60}")
        print(f"  Git Steward MVP — {status}")
        print(f"{'='*60}")
        print(f"  Repository:    {manifest.repository.path}")
        print(f"  Candidate:     {manifest.candidate_branch} @ {manifest.expected_candidate_head[:12]}")
        print(f"  Base:          {manifest.expected_base_sha[:12]}")
        print(f"  Remote:        {v.remote_matches}")
        print(f"  Branch:        {v.branch_valid}")
        print(f"  HEAD:          {v.head_valid}")
        print(f"  Base SHA:      {v.base_sha_valid}")
        print(f"  Clean tree:    {v.tree_clean}")
        print(f"  No protected:  {v.no_protected_paths}")
        print(f"  No secrets:    {v.no_secrets}")
        print(f"  No large:      {v.no_large_files}")
        print(f"  Not default:   {v.not_default_branch}")
        print(f"  No tracking:   {v.no_remote_tracking}")
        print(f"  Push approved: {v.push_approved}")
        print(f"  PR approved:   {v.pr_approved}")
        print(f"  Files:         {v.file_count}")
        print(f"  Manifest hash: {v.manifest_digest}")
        if v.errors:
            print(f"\n  Errors ({len(v.errors)}):")
            for e in v.errors[:10]:
                print(f"    - {e}")
        if v.findings:
            print(f"\n  Findings ({len(v.findings)}):")
            for f_item in v.findings[:10]:
                print(f"    - [{f_item.finding_type}] {f_item.path}: {f_item.detail}")
        if result.dry_run and v.passed:
            print(f"\n  Dry-run commands:")
            print(f"    Push: {result.dry_run.push_command}")
            print(f"    PR:   {result.dry_run.pr_command}")
        if result.stop_reason:
            print(f"\n  Stop: {result.stop_reason}")
        print(f"\n  Evidence: {evidence_abspath}")
        print(f"  Next: {result.recommended_next_action}")
        print()

    return 0 if result.validation.passed else 1


if __name__ == "__main__":
    sys.exit(main())
