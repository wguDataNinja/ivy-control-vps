"""Regression tests for backup planner command generation."""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

from tools.backup_planner import (
    BASE_RSYNC_FLAGS,
    VERIFY_RSYNC_FLAGS,
    build_execution_packet,
    EXCLUDE_GROUPS,
)


def test_base_flags_have_dot_underscore_and_ds_store() -> None:
    """._* and .DS_Store must be in both BASE and VERIFY flag sets."""
    flags_str = " ".join(BASE_RSYNC_FLAGS)
    assert "--exclude ._*" in flags_str, "BASE missing ._* exclusion"
    assert "--exclude .DS_Store" in flags_str, "BASE missing .DS_Store exclusion"

    vflags_str = " ".join(VERIFY_RSYNC_FLAGS)
    assert "--exclude ._*" in vflags_str, "VERIFY missing ._* exclusion"
    assert "--exclude .DS_Store" in vflags_str, "VERIFY missing .DS_Store exclusion"


def _make_test_repos(src_root: Path) -> list[dict]:
    """Build a realistic two-repo mock matching the real portfolio structure."""
    for p in ["capture", "data/kb", "data/chat", "data/derived", "data/imports"]:
        (src_root / p).mkdir(parents=True)
        (src_root / p / "test.json").write_text("{}")
    (src_root / "_internal").mkdir()
    (src_root / "_outbox").mkdir()
    (src_root / "_internal" / "t.txt").write_text("t")

    # Same exclude pattern list that resolve_paths produces for idlehacking-kb
    idle_excludes = [
        "__pycache__/", ".pytest_cache/", ".next/", ".ipynb_checkpoints/",
        ".venv/", "node_modules/", ".opencode/",
        "out/", "site/", "public/", "dist/", "build/",
        "reports/", "notebook/", "logs/", "bench_llm/results/",
        ".git/objects/",
    ]
    ih_excludes = [
        "__pycache__/", ".pytest_cache/", ".next/", ".ipynb_checkpoints/",
        ".venv/", "node_modules/", ".opencode/",
        "out/", "site/", "public/", "dist/", "build/",
        ".git/objects/",
    ]

    return [
        {
            "slug": "idlehacking-kb",
            "policy": {
                "importance": "critical", "sensitivity": "private",
                "strategy": "file_archive", "priority": "P0",
            },
            "local_path": src_root,
            "local_path_exists": True,
            "include_groups": ["raw_corpus", "derived_irreplaceable"],
            "exclude_groups": [
                "cache", "virtualenv", "build_output",
                "regenerable_output", "git_objects",
            ],
            "resolved_includes": [
                src_root / "capture",
                src_root / "data/kb",
                src_root / "data/chat",
                src_root / "data/derived",
                src_root / "data/imports",
            ],
            "resolved_exclude_patterns": idle_excludes,
            "estimated": {"bytes": 1000, "files": 5},
            "skipped_reason": None,
        },
        {
            "slug": "ih-market-companion",
            "policy": {
                "importance": "important", "sensitivity": "private",
                "strategy": "file_archive", "priority": "P1",
            },
            "local_path": src_root,
            "local_path_exists": True,
            "include_groups": ["private_state"],
            "exclude_groups": ["cache", "virtualenv", "build_output", "git_objects"],
            "resolved_includes": [src_root / "_internal", src_root / "_outbox"],
            "resolved_exclude_patterns": ih_excludes,
            "estimated": {"bytes": 500, "files": 2},
            "skipped_reason": None,
        },
    ]


def _check_command_integrity(
    cmd_str: str,
    label: str,
    collected_issues: list[str],
) -> None:
    """Validate a single rsync command string for all known defect patterns."""
    parts = cmd_str.split()

    # Defect 1: every --exclude must have a space before its value
    for p in parts:
        if p.startswith("--exclude") and p != "--exclude" and "=" not in p:
            collected_issues.append(
                f"[{label}] MALFORMED EXCLUDE: {p!r} (no space after --exclude)"
            )

    # Defect 2: no path concatenation (two paths without separator)
    # Check for patterns like /path/chat//Volumes
    for m in re.finditer(r"/[^\s]*/[^\s]*//[^\s]*/", cmd_str):
        collected_issues.append(
            f"[{label}] CONCATENATED PATHS: ...{m.group()[:80]}..."
        )

    # Each token should be well-formed
    for i, p in enumerate(parts):
        # Check for multi-source flattening (more than one absolute source path)
        pass  # This is structural, checked at the packet level

    # Check that --delete is never present
    if "--delete" in parts:
        collected_issues.append(f"[{label}] --delete FLAG PRESENT (forbidden)")


class TestCommandGeneration:
    """Comprehensive command-generation regression tests."""

    def _make_packet(self) -> tuple[dict, Path, Path]:
        """Build a packet with mock repos and a realistic target path."""
        src_root = Path(tempfile.mkdtemp(prefix="test-plan-src-"))
        dest_root = Path(tempfile.mkdtemp(prefix="test-plan-dst-"))
        repos = _make_test_repos(src_root)
        packet = build_execution_packet(repos, dest_root, [])
        return packet, src_root, dest_root

    def test_every_copy_command_has_valid_syntax(self) -> None:
        """No malformed --exclude, no concatenated paths, no --delete."""
        packet, src_root, dest_root = self._make_packet()
        issues: list[str] = []
        for c in packet.get("copy_commands", []):
            _check_command_integrity(
                c["command"],
                f"COPY {c['repo_slug']} {c['relative_path']}",
                issues,
            )
        assert not issues, "Copy command defects:\n" + "\n".join(issues)

    def test_every_verify_command_has_valid_syntax(self) -> None:
        """Verify commands must also pass the integrity check."""
        packet, src_root, dest_root = self._make_packet()
        issues: list[str] = []
        for c in packet.get("verify_commands", []):
            _check_command_integrity(
                c["command"],
                f"VERIFY {c['repo_slug']} {c['relative_path']}",
                issues,
            )
        assert not issues, "Verify command defects:\n" + "\n".join(issues)

    def test_one_command_per_source_path(self) -> None:
        """Each resolved include gets its own rsync command."""
        packet, src_root, dest_root = self._make_packet()
        cmds = packet.get("copy_commands", [])
        # idlehacking-kb: 5 paths, ih-market-companion: 2 paths = 7
        assert len(cmds) == 7, f"Expected 7 commands, got {len(cmds)}"

    def test_hierarchy_preserved(self) -> None:
        """capture/ and data/ go to separate destinations."""
        packet, src_root, dest_root = self._make_packet()
        cmds = packet.get("copy_commands", [])
        capture_cmds = [c for c in cmds if c["relative_path"] == "capture"]
        data_cmds = [c for c in cmds if "data/" in c["relative_path"]]
        assert len(capture_cmds) == 1
        assert len(data_cmds) == 4
        # Verify capture goes to a path ending in /capture
        assert "repos/idlehacking-kb/capture" in capture_cmds[0]["dest"]
        # Verify data paths preserve their subdirectory
        data_chat = [c for c in data_cmds if c["relative_path"] == "data/chat"]
        assert len(data_chat) == 1
        assert "repos/idlehacking-kb/data/chat" in data_chat[0]["dest"]

    def test_copy_and_verify_exclusion_parity(self) -> None:
        """Copy and verify commands must use IDENTICAL exclusion lists."""
        packet, src_root, dest_root = self._make_packet()

        def extract_excludes(cmds: list[dict]) -> set[str]:
            excludes: set[str] = set()
            for c in cmds:
                parts = c["command"].split()
                for i, p in enumerate(parts):
                    if p == "--exclude" and i + 1 < len(parts):
                        excludes.add(parts[i + 1])
            return excludes

        copy_excludes = extract_excludes(packet.get("copy_commands", []))
        verify_excludes = extract_excludes(packet.get("verify_commands", []))

        only_in_copy = copy_excludes - verify_excludes
        only_in_verify = verify_excludes - copy_excludes

        assert not only_in_copy, (
            f"Exclusions in copy but NOT in verify: {sorted(only_in_copy)}"
        )
        assert not only_in_verify, (
            f"Exclusions in verify but NOT in copy: {sorted(only_in_verify)}"
        )

    def test_snapshot_naming(self) -> None:
        """Destination paths must use snapshot-YYYY-MM-DD/ naming."""
        packet, src_root, dest_root = self._make_packet()
        snapshot_name = packet.get("snapshot_name", "")
        assert snapshot_name.startswith("snapshot-"), (
            f"Snapshot name doesn't use snapshot- prefix: {snapshot_name}"
        )
        for c in packet.get("copy_commands", []):
            assert f"/{snapshot_name}/" in c["dest"], (
                f"Command dest missing snapshot path: {c['dest']}"
            )

    def test_manifest_destination(self) -> None:
        """Manifest should live inside the snapshot directory."""
        packet, src_root, dest_root = self._make_packet()
        manifest = packet.get("manifest_destination", "")
        snapshot = packet.get("snapshot_name", "")
        assert snapshot in manifest, (
            f"Manifest {manifest} not inside snapshot {snapshot}"
        )
        assert manifest.endswith("manifest.json")

    def test_no_delete_flag(self) -> None:
        """No command should contain --delete."""
        packet, src_root, dest_root = self._make_packet()
        for c in packet.get("copy_commands", []):
            assert "--delete" not in c["command"], (
                f"--delete found in {c['repo_slug']} {c['relative_path']}"
            )

    def test_commands_executable_as_is(self) -> None:
        """Every emitted command should pass `bash -n` syntax check."""
        packet, src_root, dest_root = self._make_packet()
        for c in packet.get("copy_commands", []):
            cmd = c["command"]
            # Split and rebuild as a shell-safe check
            # We can't run the actual rsync, but we can verify the shell syntax
            result = subprocess.run(
                ["bash", "-n", "-c", cmd],
                capture_output=True, text=True, timeout=10,
            )
            assert result.returncode == 0, (
                f"Shell syntax error in command for {c['repo_slug']} {c['relative_path']}: "
                f"{result.stderr}"
            )

    def test_each_command_has_single_source(self) -> None:
        """No command should have multiple source paths (no flattening)."""
        packet, src_root, dest_root = self._make_packet()
        for c in packet.get("copy_commands", []):
            parts = c["command"].split()
            # Count tokens that look like absolute source paths (end with /)
            source_count = sum(
                1 for p in parts
                if p.startswith("/") and (p.endswith("/") or "src" in p)
            )
            # Should have exactly 1 source + 1 dest = 2 path tokens
            # dest doesn't end with /
            path_tokens = [p for p in parts if p.startswith("/")]
            assert len(path_tokens) == 2, (
                f"Expected 2 path tokens (source + dest), got {len(path_tokens)} "
                f"in {c['command'][:150]}"
            )

    def test_exclude_groups_comprehensive(self) -> None:
        """All EXCLUDE_GROUPS patterns should be representable as valid --exclude args."""
        for group_name, group in EXCLUDE_GROUPS.items():
            for pattern in group["patterns"]:
                assert isinstance(pattern, str)
                assert len(pattern) > 0
                # Pattern should be a valid glob, not a flag
                assert not pattern.startswith("-"), (
                    f"Exclude group {group_name} has flag-like pattern: {pattern}"
                )
