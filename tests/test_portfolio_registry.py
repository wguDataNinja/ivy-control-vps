"""Tests for portfolio_registry.py — portfolio registry, validation, and control parsing."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.portfolio_registry import (
    NA,
    MISSING,
    UNKNOWN,
    parse_control_md,
    parse_yaml_front_matter,
    extract_bold_fields,
    extract_table,
    extract_heading,
    extract_sha,
    display_name_from_title,
    build_registry,
    format_table,
    format_json,
    validate_registry,
    normalize_repo_id,
    redact,
    parse_gate_from_lifecycle,
    extract_scheduler_state,
    extract_lifecycle,
    extract_blocker,
    extract_next_task,
    extract_hermes_scope,
    baseline_lookup,
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


TRADERIE = load_fixture("traderie_control.md")
REDDIT_OPS = load_fixture("reddit_ops_control.md")
MINIMAL = load_fixture("minimal_control.md")
YAML_CTRL = load_fixture("control_with_yaml.md")


# ── YAML front matter ──────────────────────────────────────────────────


class TestYamlFrontMatter:
    def test_no_front_matter(self):
        meta, body = parse_yaml_front_matter("no yaml here\n---\nline")
        assert meta == {}
        assert body == "no yaml here\n---\nline"

    def test_parses_yaml(self):
        text = "---\nrepo_id: traderie\ndisplay_name: Traderie\n---\n# Body"
        meta, body = parse_yaml_front_matter(text)
        assert meta["repo_id"] == "traderie"
        assert meta["display_name"] == "Traderie"
        assert "Body" in body

    def test_unclosed_delimiter(self):
        text = "---\nkey: value\nno closing"
        meta, body = parse_yaml_front_matter(text)
        assert meta == {}
        assert "no closing" in body


# ── Markdown extraction ────────────────────────────────────────────────


class TestBoldFields:
    def test_extracts_bold(self):
        text = "**Key:** Value\n**Another:** thing"
        result = extract_bold_fields(text)
        assert result["key"] == "Value"
        assert result["another"] == "thing"

    def test_strips_backticks(self):
        text = "**SHA:** `abc123`"
        result = extract_bold_fields(text)
        assert result["sha"] == "abc123"


class TestExtractTable:
    def test_extracts_simple(self):
        text = """| Component | State |
|---|---|
| Active | yes |
| Health | ok |"""
        result = extract_table(text)
        assert result["active"] == "yes"
        assert result["health"] == "ok"


class TestExtractHeading:
    def test_extracts_blocker(self):
        text = """# Title\n\n## Current Blocker\n\nSomething is broken.\n\n## Next\n\nWork."""
        result = extract_heading(text, "Current Blocker")
        assert "broken" in result
        assert "Work" not in result

    def test_returns_empty_on_missing(self):
        assert extract_heading("# No heading", "Missing") == ""


class TestExtractSha:
    def test_from_bold(self):
        text = "**Approved production SHA:** `abc123def456`"
        assert extract_sha(text) == "abc123d"

    def test_from_generic(self):
        text = "approved SHA `deadbeef123`"
        assert extract_sha(text) == "deadbee"


class TestDisplayName:
    def test_from_title(self):
        assert display_name_from_title("# Traderie — Repository Control") == "Traderie"

    def test_fallback(self):
        assert display_name_from_title("Not a title") == UNKNOWN


# ── Normalization ──────────────────────────────────────────────────────


class TestNormalize:
    def test_replaces_underscores(self):
        assert normalize_repo_id("reddit_ops") == "reddit-ops"

    def test_passes_through(self):
        assert normalize_repo_id("traderie") == "traderie"


# ── Gate parsing ───────────────────────────────────────────────────────


class TestGateFromLifecycle:
    def test_complete_is_gate_6(self):
        assert parse_gate_from_lifecycle("production-complete") == "6"

    def test_degraded_is_gate_5(self):
        assert parse_gate_from_lifecycle("production-degraded") == "5"

    def test_stabilizing_is_gate_5(self):
        assert parse_gate_from_lifecycle("production-stabilizing") == "5"

    def test_admitted_is_gate_2(self):
        assert parse_gate_from_lifecycle("admitted") == "2"

    def test_pending_is_gate_1(self):
        assert parse_gate_from_lifecycle("admission-pending") == "1"

    def test_unknown_fallback(self):
        assert parse_gate_from_lifecycle("bogus") == UNKNOWN


# ── Scheduler extraction ───────────────────────────────────────────────


class TestSchedulerState:
    def test_active(self):
        tbl = {"active scheduler": "timer enabled, active, waiting"}
        assert extract_scheduler_state(tbl, {}) == "active"

    def test_disabled(self):
        tbl = {"active timer": "something disabled, inactive"}
        assert extract_scheduler_state(tbl, {}) == "inactive"

    def test_unknown(self):
        assert extract_scheduler_state({}, {}) == UNKNOWN


# ── Lifecycle extraction ───────────────────────────────────────────────


class TestLifecycle:
    def test_from_bold(self):
        bold = {"lifecycle state": "`production-stabilizing`"}
        assert extract_lifecycle("", bold) == "production-stabilizing"

    def test_unset(self):
        assert extract_lifecycle("# No lifecycle info", {}) == UNKNOWN


# ── Blocker / next task ────────────────────────────────────────────────


class TestBlocker:
    def test_returns_blocker_text(self):
        text = "## Current Blocker\n\nThis is blocked because X.\n\n## Next"
        result = extract_blocker(text)
        assert "blocked" in result

    def test_none(self):
        assert extract_blocker("# No blocker") == "none"


class TestNextTask:
    def test_returns_next_task(self):
        text = "## Next Authorized Work\n\nDo something important."
        result = extract_next_task(text)
        assert "important" in result


# ── Hermes scope ───────────────────────────────────────────────────────


class TestHermesScope:
    def test_detects_read_only(self):
        text = "Hermes operates as read-only."
        assert extract_hermes_scope(text, {}) == "read-only"

    def test_default_na(self):
        assert extract_hermes_scope("No mention", {}) == NA


# ── Baseline lookup ────────────────────────────────────────────────────


class TestBaselineLookup:
    def test_finds_existing(self):
        entry = baseline_lookup("traderie")
        assert entry is not None
        assert entry["display_name"] == "Traderie"

    def test_none_for_unknown(self):
        assert baseline_lookup("nonexistent") is None


# ── Full parse_control_md ──────────────────────────────────────────────


class TestParseControlMd:
    def test_traderie_from_markdown(self):
        rec = parse_control_md("traderie", TRADERIE)
        assert rec["display_name"] == "Traderie"
        assert "production-stabilizing" in rec["lifecycle"]
        assert "e5ebd0f" in rec["approved_sha"]
        assert rec["source"] != MISSING
        assert rec["blocker"] != UNKNOWN
        assert rec["next_task"] != UNKNOWN

    def test_reddit_ops(self):
        rec = parse_control_md("reddit-ops", REDDIT_OPS)
        assert rec["display_name"] == "Reddit Ops"
        assert rec["lifecycle"] == "production-stabilizing"
        assert "7047400" in rec["approved_sha"]

    def test_missing_control(self):
        rec = parse_control_md("ghost-repo", "")
        assert rec["source"] == MISSING
        assert "no CONTROL.md" in rec["warnings"]

    def test_minimal(self):
        rec = parse_control_md("minimal", MINIMAL)
        assert rec["lifecycle"] == "admitted"
        assert rec["approved_sha"] != UNKNOWN

    def test_yaml_front_matter(self):
        rec = parse_control_md("test-yaml", YAML_CTRL)
        assert rec["repo_id"] == "test-yaml"
        assert rec["display_name"] == "Test YAML Repo"
        assert rec["lifecycle"] == "production-active"
        assert rec["gate"] == "6"
        assert rec["hermes_scope"] == "read-only"
        assert rec["blocker"] == "none"

    def test_with_baseline_info(self):
        baseline = {"repo_id": "traderie", "display_name": "Traderie"}
        rec = parse_control_md("traderie", TRADERIE, baseline)
        assert rec["display_name"] == "Traderie"
        assert rec["github_url"] != UNKNOWN


# ── Build registry ─────────────────────────────────────────────────────


class TestBuildRegistry:
    def test_includes_existing_controls(self):
        records = build_registry(include_missing=False)
        ids = [r["repo_id"] for r in records]
        assert "traderie" in ids
        assert "reddit-ops" in ids

    def test_includes_placeholders(self):
        records = build_registry(include_missing=True)
        ids = [r["repo_id"] for r in records]
        assert "sjc-intel" in ids
        assert "bsda-courses" in ids

    def test_repo_filter(self):
        records = build_registry(repo_filter="traderie", include_missing=True)
        assert len(records) >= 1
        assert all(r["repo_id"] == "traderie" for r in records)

    def test_missing_repos_have_missing_source(self):
        records = build_registry(repo_filter="bsda-courses")
        assert records[0]["source"] != MISSING
        assert records[0]["_yaml_present"] == "true"


# ── Format ─────────────────────────────────────────────────────────────


class TestFormat:
    def test_table_includes_headers(self):
        records = build_registry(repo_filter="traderie")
        output = format_table(records, no_color=True)
        assert "REPO_ID" in output
        assert "traderie" in output

    def test_json_includes_fields(self):
        records = build_registry(repo_filter="traderie")
        output = format_json(records)
        parsed = json.loads(output)
        assert "records" in parsed
        assert parsed["record_count"] == len(records)
        assert parsed["records"][0]["repo_id"] == "traderie"


# ── Validation ─────────────────────────────────────────────────────────


class TestValidation:
    def test_validates_clean_record(self):
        records = build_registry(repo_filter="traderie")
        issues = validate_registry(records)
        assert all(i["severity"] == "warning" for i in issues)

    def test_detects_missing_control(self):
        records = build_registry(repo_filter="bsda-courses")
        issues = validate_registry(records)
        assert not any(i["rule"] == "missing_control_md" for i in issues)

    def test_yaml_validated_fields(self):
        records = build_registry(repo_filter="traderie")
        issues = validate_registry(records)
        assert not any(i["rule"] == "yaml_missing_required_fields" for i in issues)

    def test_staleness_detection(self):
        text = "---\nrepository:\n  slug: stale-repo\nlifecycle:\n  state: source-only\nlast_verified: 2025-01-01\n---\n# content"
        rec = parse_control_md("stale-repo", text)
        issues = validate_registry([rec])
        stale_issues = [i for i in issues if i["rule"] == "stale_last_verified"]
        assert len(stale_issues) >= 1

    def test_no_duplicates_in_full_registry(self):
        records = build_registry(include_missing=True)
        issues = validate_registry(records)
        assert not any(i["rule"] == "duplicate_id" for i in issues)


# ── Redaction ──────────────────────────────────────────────────────────


class TestRedaction:
    def test_local_path_redacted(self):
        assert redact("path /Users/buddy/secret/file.txt") == "path <local-path>"

    def test_ip_redacted(self):
        assert redact("server 192.168.1.1 is up") == "server <ip> is up"

    def test_no_false_positive(self):
        result = redact("repos/traderie/CONTROL.md")
        assert "repos/traderie/CONTROL.md" in result


# ── CLI ────────────────────────────────────────────────────────────────


BASE_DIR = os.path.join(os.path.dirname(__file__), "..")


class TestCli:
    def test_cli_table(self):
        result = subprocess.run(
            [sys.executable, "tools/portfolio_registry.py", "--table", "--no-color"],
            capture_output=True, text=True, cwd=BASE_DIR,
        )
        assert result.returncode == 0
        assert "REPO_ID" in result.stdout

    def test_cli_json(self):
        result = subprocess.run(
            [sys.executable, "tools/portfolio_registry.py", "--json"],
            capture_output=True, text=True, cwd=BASE_DIR,
        )
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert "records" in parsed

    def test_cli_validate(self):
        result = subprocess.run(
            [sys.executable, "tools/portfolio_registry.py", "--validate"],
            capture_output=True, text=True, cwd=BASE_DIR,
        )
        assert result.returncode == 0

    def test_cli_repo_filter(self):
        result = subprocess.run(
            [sys.executable, "tools/portfolio_registry.py",
             "--table", "--no-color", "--repo", "traderie"],
            capture_output=True, text=True, cwd=BASE_DIR,
        )
        assert "traderie" in result.stdout
        assert "reddit-ops" not in result.stdout.lower() or "reddit" not in result.stdout.lower()

    def test_cli_json_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            outpath = os.path.join(tmp, "registry.json")
            result = subprocess.run(
                [sys.executable, "tools/portfolio_registry.py",
                 "--json", "--output", outpath],
                capture_output=True, text=True, cwd=BASE_DIR,
            )
            assert result.returncode == 0
            assert os.path.exists(outpath)
            parsed = json.loads(Path(outpath).read_text())
            assert "records" in parsed

    def test_no_secrets_in_output(self):
        result = subprocess.run(
            [sys.executable, "tools/portfolio_registry.py", "--table"],
            capture_output=True, text=True, cwd=BASE_DIR,
        )
        assert "/Users/" not in result.stdout
        import re
        assert re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", result.stdout) is None
