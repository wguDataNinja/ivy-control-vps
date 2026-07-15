"""Tests for portfolio_phase0_status.py — Phase 0 operator status CLI."""

import json
import os
import subprocess
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.portfolio_phase0_status import (
    REDACTION_PATTERNS,
    Row,
    build_rows,
    build_traderie_row,
    build_reddit_ops_row,
    build_sjc_intel_placeholder,
    build_wgu_catalog_placeholder,
    format_table,
    format_json,
    redact,
    extract_heading_text,
    parse_table_from_markdown,
)


TRADERIE_CTRL_DEGRADED = """# Traderie — Repository Control

**Lifecycle state:** `production-stabilizing` / `PRODUCTION_DEGRADED`
**Approved production SHA:** `e5ebd0f6dd41bcb4e1d8a88f272be89b225cfd40`

## Production Authority

| Component | Current state |
|---|---|
| Active scheduler | `traderie-ingest-snapshot.timer` enabled, active, waiting |
| Active writer | VPS systemd service path only |
| Health | DB-backed `health.health_runs` exists |
| Backup | Latest known dump: `traderie_20260709T090253Z.dump` |

## Current Blocker

The first genuine natural scheduled generation after segmented cutover partially failed on 2026-07-11 at 18:01:46 UTC. Segments `pc_sc_nl`, `pc_sc_l`, and `pc_hc_l` completed; `pc_hc_nl` reached its 480-second bound and timed out. Overall service exit was `1`.
"""

TRADERIE_CTRL_OK = """# Traderie — Repository Control

**Lifecycle state:** `production-complete`
**Approved production SHA:** `e5ebd0f6dd41bcb4e1d8a88f272be89b225cfd40`

## Production Authority

| Component | Current state |
|---|---|
| Active scheduler | `traderie-ingest-snapshot.timer` enabled, active, waiting |
| Active writer | VPS systemd service path only |
| Health | DB-backed `health.health_runs` exists |
| Backup | Latest known dump ok |
"""

REDDITOPS_CTRL = """# Reddit Ops — Repository Control

**Lifecycle state:** `production-stabilizing`

## Production Authority

| Component | State |
|---|---|
| Active timer | `wgu-reddit-postgres-run.timer` — enabled, active, waiting (07:00 UTC daily) |
| Active service | `wgu-reddit-postgres-run.service` |
| Runtime user | `scraper` |

## Deployment Status

| Item | Status |
|---|---|
| Deployed SHA | `7047400` — local WGU-Reddit commit. Pending clean Git publication because local history contains credential-bearing commit `e4acae0`. |
| Drift detection | Checksum comparison via `sha256sum` |
"""

REDDITOPS_CTRL_OK = """# Reddit Ops — Repository Control

**Lifecycle state:** `production-complete`

## Production Authority

| Component | State |
|---|---|
| Active timer | `wgu-reddit-postgres-run.timer` — enabled, active, waiting |
| Active service | `wgu-reddit-postgres-run.service` |

## Deployment Status

| Item | Status |
|---|---|
| Deployed SHA | `7047400` |
| Drift detection | Checksum comparison |
"""


class TestRedaction:
    def test_local_path_redacted(self):
        assert redact('path /Users/buddy/secret/file.txt') == 'path <local-path>'

    def test_ip_redacted(self):
        assert redact('server 192.168.1.1 is up') == 'server <ip> is up'

    def test_credential_redacted(self):
        assert '<credential-redacted>' in redact('api_key=sk-live-abc123def456')

    def test_no_false_positive_on_source(self):
        result = redact('repos/traderie/CONTROL.md')
        assert 'repos/traderie/CONTROL.md' in result


class TestParseTable:
    def test_parse_simple_table(self):
        text = """| Key | Value |
|---|---|
| Name | Test |
| SHA | abc123 |
"""
        result = parse_table_from_markdown(text)
        assert result.get('Name') == 'Test'
        assert result.get('SHA') == 'abc123'


class TestExtractHeading:
    def test_extract_current_blocker(self):
        text = """# Title

## Current Blocker

The first natural scheduled generation partially failed.

## Next Authorized Work

Fix it.
"""
        result = extract_heading_text(text, 'Current Blocker')
        assert 'partially failed' in result
        assert 'Fix it' not in result


class TestBuildTraderieRow:
    def test_degraded_parsing(self):
        row = build_traderie_row(TRADERIE_CTRL_DEGRADED)
        assert row.classification == 'production_degraded'
        assert row.current_failure == 'pc_hc_nl_timeout'
        assert row.incident_or_approval == 'incident:degraded'
        assert row.deployed_revision == 'e5ebd0f'
        assert row.scheduler_state == 'active'

    def test_missing_control_sheet(self):
        row = build_traderie_row('')
        assert row.classification == 'production_degraded'
        assert row.current_failure == 'missing_authority'

    def test_ok_state(self):
        row = build_traderie_row(TRADERIE_CTRL_OK)
        assert row.classification == 'production'
        assert row.current_failure == 'none'


class TestBuildRedditOpsRow:
    def test_publication_blocked(self):
        row = build_reddit_ops_row(REDDITOPS_CTRL)
        assert row.deployed_revision == 'pending-pub'
        assert row.current_failure == 'publication_blocker'
        assert row.incident_or_approval == 'approval:publication'
        assert row.scheduler_state == 'active'

    def test_missing_control_sheet(self):
        row = build_reddit_ops_row('')
        assert row.classification == 'production'
        assert row.current_failure == 'missing_authority'

    def ok_state(self):
        row = build_reddit_ops_row(REDDITOPS_CTRL_OK)
        assert row.deployed_revision == '7047400'
        assert row.current_failure == 'none'


class TestPlaceholders:
    def test_sjc_intel(self):
        row = build_sjc_intel_placeholder()
        assert row.classification == 'readiness_placeholder'
        assert row.current_failure == 'readiness_pending'
        assert row.scheduler_state == 'unmanaged'
        assert row.writer_authority == 'none'
        assert row.incident_or_approval == 'approval:cutover'

    def test_wgu_catalog(self):
        row = build_wgu_catalog_placeholder()
        assert row.classification == 'batch_placeholder'
        assert row.current_failure == 'activation_mode'
        assert row.scheduler_state == 'manual'


class TestBuildRows:
    def test_all_rows_included(self):
        rows = build_rows(include_placeholders=True)
        ids = [r.workload_id for r in rows]
        assert 'traderie/ingest_snapshot' in ids
        assert 'reddit_ops/daily_wgu_collection' in ids
        assert 'sjc_intel/ingestion_readiness' in ids
        assert 'wgu_catalog/catalog_release_batch' in ids

    def test_no_placeholders(self):
        rows = build_rows(include_placeholders=False)
        ids = [r.workload_id for r in rows]
        assert 'traderie/ingest_snapshot' in ids
        assert 'reddit_ops/daily_wgu_collection' in ids
        assert 'sjc_intel/ingestion_readiness' not in ids
        assert 'wgu_catalog/catalog_release_batch' not in ids

    def test_filter_by_repo(self):
        rows = build_rows(repo_filter='traderie')
        ids = [r.workload_id for r in rows]
        assert 'traderie/ingest_snapshot' in ids
        assert 'reddit_ops/daily_wgu_collection' not in ids


class TestFormat:
    def test_table_includes_headers(self):
        rows = build_rows(include_placeholders=True)
        output = format_table(rows, no_color=True)
        assert 'WORKLOAD' in output
        assert 'FRESHNESS' in output
        assert 'INCIDENT/APPROVAL' in output
        assert 'traderie' in output
        assert 'reddit_ops' in output
        assert 'sjc_intel' in output
        assert 'wgu_catalog' in output

    def test_placeholders_visibly_marked(self):
        rows = build_rows(include_placeholders=True)
        output = format_table(rows, no_color=True)
        assert 'readiness_pending' in output
        assert 'activation_mode' in output

    def test_json_output(self):
        rows = build_rows(include_placeholders=True)
        output = format_json(rows)
        parsed = json.loads(output)
        assert 'rows' in parsed
        assert len(parsed['rows']) == 4


class TestCli:
    def test_cli_table(self):
        result = subprocess.run(
            [sys.executable, 'tools/portfolio_phase0_status.py', '--format', 'table', '--no-color'],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..'),
        )
        assert result.returncode == 0
        assert 'traderie' in result.stdout
        assert 'pc_hc_nl_timeout' in result.stdout
        assert 'readiness_pending' in result.stdout
        assert 'activation_mode' in result.stdout

    def test_cli_json(self):
        result = subprocess.run(
            [sys.executable, 'tools/portfolio_phase0_status.py', '--format', 'json'],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..'),
        )
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert len(parsed['rows']) == 4

    def test_cli_repo_filter(self):
        result = subprocess.run(
            [sys.executable, 'tools/portfolio_phase0_status.py', '--repo', 'traderie', '--format', 'table', '--no-color'],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..'),
        )
        assert 'traderie' in result.stdout
        assert 'reddit_ops' not in result.stdout

    def test_cli_no_placeholders(self):
        result = subprocess.run(
            [sys.executable, 'tools/portfolio_phase0_status.py', '--no-placeholders', '--format', 'table', '--no-color'],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..'),
        )
        assert 'sjc_intel' not in result.stdout
        assert 'wgu_catalog' not in result.stdout

    def test_no_secrets_in_output(self):
        result = subprocess.run(
            [sys.executable, 'tools/portfolio_phase0_status.py', '--format', 'table', '--no-color'],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..'),
        )
        assert '/Users/' not in result.stdout
        import re
        assert re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', result.stdout) is None
