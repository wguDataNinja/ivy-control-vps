#!/usr/bin/env python3
"""Phase 0 operator status report — read-only CLI for portfolio health visibility."""

import argparse
import csv
import io
import json
import os
import re
import sys
import textwrap


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REDACTION_PATTERNS = [
    (re.compile(r'/Users/[^/\s]+(?:/[^\s]*)*'), '<local-path>'),
    (re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'), '<ip>'),
    (re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+(?:com|org|net|edu|gov|io|dev|app|co|uk|de|jp|fr|au|ca|info|biz|me|tv)(?:\:[0-9]+)?(?:\/[^\s]*)?'), '<host>'),
    (re.compile(r'(?i)(?:api[_-]?key|token|secret|password|credential)\s*[=:]\s*\S+'), '<credential-redacted>'),
    (re.compile(r'(?i)(?:sk-[a-zA-Z0-9]{20,}|pk-[a-zA-Z0-9]{20,})'), '<key-redacted>'),
]


OUTPUT_REDACTION_PATTERNS = [
    (re.compile(r'/Users/[^/\s]+(?:/[^\s]*)*'), '<local-path>'),
    (re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'), '<ip>'),
    (re.compile(r'(?i)(?:api[_-]?key|token|secret|password|credential)\s*[=:]\s*\S+'), '<credential-redacted>'),
    (re.compile(r'(?i)(?:sk-[a-zA-Z0-9]{20,}|pk-[a-zA-Z0-9]{20,})'), '<key-redacted>'),
    (re.compile(r'\b[\w.-]+\.(?:com|org|net|edu|gov|io|dev|app|co|uk|de|jp|fr|au|ca|info|biz|me|tv)\b'), '<host>'),
]


def redact(text):
    for pattern, replacement in OUTPUT_REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def parse_table_from_markdown(text, header_col=None):
    """Parse a markdown table into a dict keyed by the first column."""
    result = {}
    lines = text.split('\n')
    in_table = False
    headers = []
    for line in lines:
        if '|' not in line:
            in_table = False
            continue
        cells = [c.strip() for c in line.split('|')]
        cells = [c for c in cells if c]
        if not cells:
            continue
        if '---' in line:
            in_table = True
            continue
        if not in_table:
            if header_col is not None and cells[0].lower().replace(' ', '_') == header_col.lower().replace(' ', '_'):
                in_table = True
            continue
        if len(cells) >= 2:
            result[cells[0].strip()] = cells[1].strip()
    return result


def extract_heading_text(text, heading):
    """Extract a block of text under a markdown heading."""
    pattern = re.compile(
        rf'^##\s+{re.escape(heading)}\s*$.*?(?=^##\s|\Z)',
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if match:
        return match.group(0)
    return ''


def read_file(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ''
    except Exception:
        return ''


class Row:
    def __init__(self):
        self.workload_id = 'unknown'
        self.repository = 'unknown'
        self.workflow = 'unknown'
        self.classification = 'unknown'
        self.last_attempt_at = 'unknown'
        self.last_success_at = 'unknown'
        self.freshness_state = 'unknown'
        self.scheduler_state = 'unknown'
        self.writer_authority = 'unknown'
        self.deployed_revision = 'unknown'
        self.backup_age = 'unknown'
        self.current_failure = 'none'
        self.drift_state = 'unknown'
        self.incident_or_approval = 'none'
        self.source = 'unknown'

    def to_dict(self):
        return {
            'workload_id': self.workload_id,
            'repository': self.repository,
            'workflow': self.workflow,
            'classification': self.classification,
            'last_attempt_at': self.last_attempt_at,
            'last_success_at': self.last_success_at,
            'freshness_state': self.freshness_state,
            'scheduler_state': self.scheduler_state,
            'writer_authority': self.writer_authority,
            'deployed_revision': self.deployed_revision,
            'backup_age': self.backup_age,
            'current_failure': self.current_failure,
            'drift_state': self.drift_state,
            'incident_or_approval': self.incident_or_approval,
            'source': self.source,
        }


def build_traderie_row(control_text, evidence_dir=None):
    row = Row()
    row.workload_id = 'traderie/ingest_snapshot'
    row.repository = 'traderie'
    row.workflow = 'ingest_snapshot'

    if not control_text:
        row.classification = 'production_degraded'
        row.current_failure = 'missing_authority'
        return row

    lifecycle_match = re.search(r'\*\*Lifecycle state:\*\*\s*(.+?)(?:\n|$)', control_text)
    lifecycle = lifecycle_match.group(1).strip() if lifecycle_match else ''
    classification = 'production'
    if 'degraded' in lifecycle.lower() and 'production' in lifecycle.lower():
        classification = 'production_degraded'
    row.classification = classification

    table = parse_table_from_markdown(control_text)
    row.writer_authority = table.get('Active writer', 'unknown')
    row.scheduler_state = 'active' if 'enabled' in table.get(
        'Active scheduler', ''
    ).lower() and 'timer' in table.get('Active scheduler', '').lower() else 'unknown'

    sha_match = re.search(r'\*\*Approved production SHA:\*\*\s*`?([a-f0-9]+)`?', control_text)
    if sha_match:
        row.deployed_revision = sha_match.group(1)[:7]
    else:
        sha_table = parse_table_from_markdown(control_text)
        health_text = sha_table.get('Health', '')
        sha_in_table = re.search(r'[a-f0-9]{7,40}', health_text)
        row.deployed_revision = sha_in_table.group(0)[:7] if sha_in_table else 'unknown'

    blocker_section = extract_heading_text(control_text, 'Current Blocker')
    if 'pc_hc_nl' in blocker_section.lower() and ('timeout' in blocker_section.lower() or 'timed out' in blocker_section.lower()):
        row.freshness_state = 'fail'
        row.current_failure = 'pc_hc_nl_timeout'
        row.incident_or_approval = 'incident:degraded'
    else:
        row.freshness_state = 'unknown'

    backup_table = parse_table_from_markdown(control_text)
    backup_text = backup_table.get('Backup', '')
    if 'stale' in backup_text.lower():
        row.backup_age = 'stale'
    elif 'ok' in backup_text.lower() or 'pass' in backup_text.lower():
        row.backup_age = 'ok'
    else:
        row.backup_age = 'unknown'

    row.drift_state = 'not_evaluated'
    row.source = 'repos/traderie/CONTROL.md'
    return row


def build_reddit_ops_row(control_text, evidence_dir=None):
    row = Row()
    row.workload_id = 'reddit_ops/daily_wgu_collection'
    row.repository = 'reddit_ops'
    row.workflow = 'daily_wgu_collection'

    if not control_text:
        row.classification = 'production'
        row.current_failure = 'missing_authority'
        return row

    lifecycle_match = re.search(r'\*\*Lifecycle state:\*\*\s*(.+?)(?:\n|$)', control_text)
    lifecycle = lifecycle_match.group(1).strip() if lifecycle_match else ''
    row.classification = 'production'

    table = parse_table_from_markdown(control_text)
    row.writer_authority = 'vps'
    row.scheduler_state = 'active' if 'enabled' in table.get(
        'Active timer', ''
    ).lower() else 'unknown'

    deploy_table_text = extract_heading_text(control_text, 'Deployment Status')
    deploy_table = parse_table_from_markdown(deploy_table_text)
    sha = deploy_table.get('Deployed SHA', '')
    if 'pending' in sha.lower():
        row.deployed_revision = 'pending-pub'
        row.current_failure = 'publication_blocker'
        row.incident_or_approval = 'approval:publication'
    elif sha:
        row.deployed_revision = sha[:7]
    else:
        row.deployed_revision = 'unknown'

    row.backup_age = 'unknown'
    row.drift_state = 'unknown'
    row.source = 'repos/reddit-ops/CONTROL.md'
    return row


def build_sjc_intel_placeholder():
    row = Row()
    row.workload_id = 'sjc_intel/ingestion_readiness'
    row.repository = 'sjc_intel'
    row.workflow = 'ingestion_readiness'
    row.classification = 'readiness_placeholder'
    row.last_attempt_at = 'not_applicable'
    row.last_success_at = 'not_applicable'
    row.freshness_state = 'unknown'
    row.scheduler_state = 'unmanaged'
    row.writer_authority = 'none'
    row.deployed_revision = 'unknown'
    row.backup_age = 'unknown'
    row.current_failure = 'readiness_pending'
    row.drift_state = 'not_evaluated'
    row.incident_or_approval = 'approval:cutover'
    row.source = 'placeholder'
    return row


def build_wgu_catalog_placeholder():
    row = Row()
    row.workload_id = 'wgu_catalog/catalog_release_batch'
    row.repository = 'wgu_catalog'
    row.workflow = 'catalog_release_batch'
    row.classification = 'batch_placeholder'
    row.last_attempt_at = 'not_applicable'
    row.last_success_at = 'not_applicable'
    row.freshness_state = 'unknown'
    row.scheduler_state = 'manual'
    row.writer_authority = 'file-export'
    row.deployed_revision = 'unknown'
    row.backup_age = 'not_app'
    row.current_failure = 'activation_mode'
    row.drift_state = 'not_evaluated'
    row.incident_or_approval = 'approval:activation-mode'
    row.source = 'placeholder'
    return row


def build_rows(repo_filter=None, include_placeholders=True, evidence_dir=None):
    rows = []

    ctrl_dir = os.path.join(REPO_ROOT, 'repos')

    traderie_ctrl = read_file(os.path.join(ctrl_dir, 'traderie', 'CONTROL.md'))
    if not repo_filter or repo_filter == 'traderie':
        rows.append(build_traderie_row(traderie_ctrl, evidence_dir))

    reddit_ctrl = read_file(os.path.join(ctrl_dir, 'reddit-ops', 'CONTROL.md'))
    if not repo_filter or repo_filter == 'reddit-ops' or repo_filter == 'reddit_ops':
        rows.append(build_reddit_ops_row(reddit_ctrl, evidence_dir))

    if include_placeholders:
        if not repo_filter or repo_filter == 'sjc-intel' or repo_filter == 'sjc_intel':
            rows.append(build_sjc_intel_placeholder())
        if not repo_filter or repo_filter == 'wgu-catalog' or repo_filter == 'wgu_catalog':
            rows.append(build_wgu_catalog_placeholder())

    return rows


HEADER_LABELS = [
    'WORKLOAD', 'WORKFLOW', 'LAST_ATTEMPT', 'LAST_SUCCESS',
    'FRESHNESS', 'SCHEDULER', 'WRITER', 'REVISION',
    'BACKUP_AGE', 'FAILURE', 'DRIFT', 'INCIDENT/APPROVAL',
]


def format_table(rows, no_color=False):
    data = []
    for r in rows:
        d = r.to_dict()
        data.append([
            d['workload_id'].split('/')[0] if '/' in d['workload_id'] else d['repository'],
            d['workflow'],
            d['last_attempt_at'],
            d['last_success_at'],
            d['freshness_state'],
            d['scheduler_state'],
            d['writer_authority'],
            d['deployed_revision'],
            d['backup_age'],
            d['current_failure'],
            d['drift_state'],
            d['incident_or_approval'],
        ])

    col_widths = [len(h) for h in HEADER_LABELS]
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    buf = io.StringIO()
    header_line = '  '.join(h.ljust(col_widths[i]) for i, h in enumerate(HEADER_LABELS))
    buf.write(header_line)
    buf.write('\n')
    buf.write('  '.join('-' * w for w in col_widths))
    buf.write('\n')
    for row in data:
        line = '  '.join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
        buf.write(line)
        buf.write('\n')

    result = buf.getvalue()
    return redact(result) if not no_color else result


def format_json(rows):
    output = {'rows': [r.to_dict() for r in rows]}
    raw = json.dumps(output, indent=2)
    return redact(raw)


def main():
    parser = argparse.ArgumentParser(description='Phase 0 portfolio health status')
    parser.add_argument('--format', choices=['table', 'json'], default='table')
    parser.add_argument('--repo', type=str, default=None, help='Filter by repo slug')
    parser.add_argument('--evidence-dir', type=str, default=None, help='Directory with sanitized evidence snapshots')
    parser.add_argument('--include-placeholders', action='store_true', default=True)
    parser.add_argument('--no-placeholders', dest='include_placeholders', action='store_false')
    parser.add_argument('--strict', action='store_true', help='Exit non-zero on contradictory authority')
    parser.add_argument('--no-color', action='store_true', help='Disable color (deterministic output)')
    args = parser.parse_args()

    rows = build_rows(
        repo_filter=args.repo,
        include_placeholders=args.include_placeholders,
        evidence_dir=args.evidence_dir,
    )

    if not rows:
        print('No matching workloads found.')
        sys.exit(0)

    if args.format == 'json':
        output = format_json(rows)
    else:
        output = format_table(rows, no_color=args.no_color)

    sys.stdout.write(output)
    if not output.endswith('\n'):
        sys.stdout.write('\n')

    if args.strict:
        for r in rows:
            if r.current_failure == 'contradictory_authority':
                sys.exit(1)


if __name__ == '__main__':
    main()
