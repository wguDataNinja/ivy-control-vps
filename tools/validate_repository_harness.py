#!/usr/bin/env python3
"""Validate the small, portable repository-harness orientation contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {"schema_version", "repository", "purpose", "authority_files", "active_task", "health_commands", "task_paths", "git"}

def validate(root: Path) -> list[str]:
    errors: list[str] = []
    manifest = root / "HARNESS.json"
    for name in ("README.md", "AGENTS.md", "ROADMAP.md", "HARNESS.json"):
        if not (root / name).is_file():
            errors.append(f"missing required harness entrypoint: {name}")
    if errors or not manifest.is_file():
        return errors
    try:
        data = json.loads(manifest.read_text())
    except json.JSONDecodeError as exc:
        return [f"HARNESS.json is invalid JSON: {exc.msg}"]
    missing = sorted(REQUIRED - set(data))
    if missing:
        errors.append("HARNESS.json missing fields: " + ", ".join(missing))
        return errors
    if data["schema_version"] != 1:
        errors.append("HARNESS.json schema_version must be 1")
    if not isinstance(data["authority_files"], list) or not data["authority_files"]:
        errors.append("authority_files must be a non-empty list")
    else:
        for name in data["authority_files"]:
            if not isinstance(name, str) or name.startswith("/") or ".." in Path(name).parts:
                errors.append(f"authority file is not a safe relative path: {name!r}")
            elif not (root / name).is_file():
                errors.append(f"declared authority file is missing: {name}")
    active = data["active_task"]
    if active is not None and (not isinstance(active, str) or not (root / active).is_file()):
        errors.append("active_task must be null or an existing relative file")
    if not isinstance(data["health_commands"], list) or not all(isinstance(c, str) and c.strip() for c in data["health_commands"]):
        errors.append("health_commands must be a non-empty list of commands")
    paths = data["task_paths"]
    if not isinstance(paths, dict) or set(paths) != {"packets", "reports", "journal"}:
        errors.append("task_paths must contain exactly packets, reports, and journal")
    elif any(not isinstance(v, str) or v.startswith("/") or ".." in Path(v).parts for v in paths.values()):
        errors.append("task_paths must be safe relative paths")
    git = data["git"]
    if not isinstance(git, dict) or not isinstance(git.get("writer"), str) or not isinstance(git.get("remote_mutation"), bool):
        errors.append("git must contain writer and boolean remote_mutation")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    errors = validate(args.repo.resolve())
    if errors:
        print("HARNESS_INVALID")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("HARNESS_VALID")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
