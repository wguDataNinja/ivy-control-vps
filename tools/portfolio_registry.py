#!/usr/bin/env python3
"""Generate the portfolio registry from repository CONTROL.md records.

The registry is a derived/aggregated view — CONTROL.md is per-repo SOA.
Source data comes from YAML front matter (preferred) or Markdown extraction.
Repos without CONTROL.md appear as placeholders sourced from PORTFOLIO_BASELINE.md.

Usage:
    python tools/portfolio_registry.py --json
    python tools/portfolio_registry.py --table
    python tools/portfolio_registry.py --context --repo traderie
    python tools/portfolio_registry.py --validate
    python tools/portfolio_registry.py --repo traderie --json
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
REPOS_DIR = REPO_ROOT / "repos"
BASELINE_PATH = REPO_ROOT / "docs" / "PORTFOLIO_BASELINE.md"

UNKNOWN = "UNKNOWN"
MISSING = "MISSING"  # repo has no CONTROL.md at all
NA = "N/A"

REDACTION_PATTERNS = [
    (re.compile(r'/Users/[^/\s]+(?:/[^\s]*)*'), '<local-path>'),
    (re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'), '<ip>'),
    (re.compile(r'(?i)(?:api[_-]?key|token|secret|password|credential)\s*[=:]\s*\S+'), '<credential-redacted>'),
    (re.compile(r'(?i)(?:sk-[a-zA-Z0-9]{20,}|pk-[a-zA-Z0-9]{20,})'), '<key-redacted>'),
]

VALID_LIFECYCLES = {
    "pre-admission", "admission-pending", "admitted",
    "production-stabilizing", "production-degraded", "production-active",
    "production-complete", "archived", "decommissioned",
    "production-runtime",
    "source-only", "published",
    "browser-dependent", "downstream", "restricted", "batch",
}

VALID_GATES = {"1", "2", "3", "4", "5", "6", "UNKNOWN", "MISSING"}

HERMES_SCOPES = {"read-only", "read-write", "enabled", "none", "MISSING", "UNKNOWN", "N/A"}

# Baseline repos from PORTFOLIO_BASELINE.md §1A
BASELINE_REPOS: list[dict[str, str]] = [
    {"repo_id": "traderie", "display_name": "Traderie", "class": "Deterministic", "runtime_type": "Data pipeline"},
    {"repo_id": "sjc-intel", "display_name": "SJC Intel", "class": "Deterministic", "runtime_type": "Data collection"},
    {"repo_id": "ih-market-companion", "display_name": "IH Market Companion", "class": "Deterministic", "runtime_type": "Browser/API"},
    {"repo_id": "reddit-ops", "display_name": "Reddit Ops (WGU-Reddit)", "class": "Boundary unclear", "runtime_type": "Reddit-derived"},
    {"repo_id": "bsda-courses", "display_name": "BSDA Courses", "class": "LLM pipeline", "runtime_type": "Multi-stage LLM"},
    {"repo_id": "wgu-atlas", "display_name": "WGU Atlas", "class": "LLM pipeline", "runtime_type": "QA generation"},
    {"repo_id": "idlehacking-kb", "display_name": "Idle Hacking KB", "class": "LLM pipeline", "runtime_type": "Knowledge base"},
    {"repo_id": "reckless-ben", "display_name": "Reckless Ben", "class": "Restricted", "runtime_type": "NO_LAUNCH"},
    {"repo_id": "palworld-kb", "display_name": "Palworld KB", "class": "Unknown", "runtime_type": "Unknown"},
    {"repo_id": "wgu-catalog", "display_name": "WGU Catalog", "class": "Unknown", "runtime_type": "Unknown"},
]


def redact(text: str) -> str:
    for pattern, replacement in REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def parse_yaml_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Parse YAML front matter (--- ... ---) from CONTROL.md.

    Returns (metadata_dict, body_without_front_matter).
    Supports simple nested keys by tracking indentation — no external YAML dependency.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = 1
    while end < len(lines) and lines[end].strip() != "---":
        end += 1
    if end >= len(lines):
        return {}, text
    meta: dict[str, str] = {}
    prefix_stack: list[tuple[str, int]] = []
    for raw_line in lines[1:end]:
        if not raw_line.strip():
            continue
        stripped = raw_line.rstrip()
        content = stripped.lstrip()
        indent = len(stripped) - len(content)
        if ":" not in content:
            continue
        key, _, value = content.partition(":")
        leaf_key = key.strip().lower()
        value = value.strip()
        # Pop prefix stack until we find a parent at a lower indentation
        while prefix_stack and prefix_stack[-1][1] >= indent:
            prefix_stack.pop()
        if value:
            # This is a leaf key (has a value)
            prefix = ".".join(p[0] for p in prefix_stack)
            full_key = f"{prefix}.{leaf_key}" if prefix else leaf_key
            meta[full_key] = value.strip('"').strip("'")
        else:
            # This is a parent key (no value, children follow)
            prefix_stack.append((leaf_key, indent))
    body = "\n".join(lines[end + 1:])
    return meta, body


def extract_bold_fields(text: str) -> dict[str, str]:
    """Extract **Key:** Value pairs from Markdown text."""
    result: dict[str, str] = {}
    for match in re.finditer(r'\*\*([^*]+):\*\*\s*(.*?)(?:\n|$)', text):
        key = match.group(1).strip().lower()
        value = match.group(2).strip().strip('`').strip()
        result[key] = value
    return result


def extract_table(text: str) -> dict[str, str]:
    """Extract a Markdown table into a dict keyed by first column."""
    result: dict[str, str] = {}
    lines = text.split("\n")
    in_table = False
    for line in lines:
        if "|" not in line:
            in_table = False
            continue
        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c]
        if not cells:
            continue
        if re.match(r'^[\s\|:-]+$', line):
            in_table = True
            continue
        if not in_table:
            continue
        if len(cells) >= 2:
            result[cells[0].strip().lower()] = cells[1].strip()
    return result


def extract_heading(text: str, heading: str) -> str:
    """Extract content under a ## heading."""
    pattern = re.compile(
        rf'^##\s+{re.escape(heading)}\s*$.*?(?=^##\s|\Z)',
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(0) if match else ""


def parse_gate_from_lifecycle(lifecycle: str) -> str:
    lc = lifecycle.lower()
    if "decommissioned" in lc or "archived" in lc:
        return "6"
    if "complete" in lc:
        return "6"
    if "active" in lc:
        return "6"
    if "degraded" in lc or "stabilizing" in lc:
        return "5"
    if "admitted" in lc:
        return "2"
    if "admission" in lc or "pending" in lc:
        return "1"
    if "placeholder" in lc:
        return "1"
    return UNKNOWN


def extract_current_gate_from_table(text: str) -> str:
    """Read the Portfolio Admission State gate table and return the
    lowest gate number that has not yet passed."""
    section = extract_heading(text, "Portfolio Admission State")
    if not section:
        return UNKNOWN
    t = extract_table(section)
    gates_passed = 0
    for key in sorted(t.keys()):
        state = t[key].lower()
        if "pass" in state and "not" not in state and "block" not in state:
            gates_passed += 1
        else:
            break
    if gates_passed == 0:
        return "1"
    if gates_passed >= 6:
        return "6"
    return str(gates_passed + 1)


def display_name_from_title(title_line: str) -> str:
    m = re.match(r'^#\s+(.+?)\s*(?:[——-]|$)', title_line)
    return m.group(1).strip() if m else UNKNOWN


def extract_sha(text: str) -> str:
    m = re.search(r'\*\*Approved production SHA:\*\*\s*`?([a-f0-9]{7,40})`?', text)
    if m:
        return m.group(1)[:7]
    m = re.search(r'approved(?:[- ])?sha.*?`?([a-f0-9]{7,40})`?', text, re.IGNORECASE)
    if m:
        return m.group(1)[:7]
    return UNKNOWN


def extract_scheduler_state(table: dict[str, str], bold: dict[str, str]) -> str:
    raw = table.get("active scheduler", table.get("active timer", "")) or bold.get("active scheduler", "")
    if not raw:
        return UNKNOWN
    if "enabled" in raw.lower() and ("active" in raw.lower() or "waiting" in raw.lower()):
        return "active"
    if "disabled" in raw.lower() or "inactive" in raw.lower():
        return "inactive"
    return raw[:40] if raw else UNKNOWN


def extract_writer(table: dict[str, str]) -> str:
    raw = table.get("active writer", "")
    if raw:
        return raw[:60]
    return UNKNOWN


def extract_health(table: dict[str, str]) -> str:
    raw = table.get("health", "")
    if raw:
        return raw[:60]
    return UNKNOWN


def extract_database(table: dict[str, str]) -> str:
    raw = table.get("production database", table.get("storage backend", ""))
    if raw:
        return raw[:60]
    return UNKNOWN


def extract_lifecycle(text: str, bold: dict[str, str]) -> str:
    raw = bold.get("lifecycle state", "")
    if raw:
        raw = raw.replace("`", "").strip()
        for sep in (" — ", " —", "— ", " – ", " -- "):
            if sep in raw:
                raw = raw.split(sep)[0].strip()
        return raw
    admission_table = extract_table(extract_heading(text, "Portfolio Admission State"))
    for key in admission_table:
        if "not yet admitted" in admission_table[key].lower():
            return "pre-admission"
        if "admission" in key.lower() and "not yet" not in admission_table[key].lower():
            state = admission_table[key].lower()
            if "pass" in state:
                return "admitted"
    return UNKNOWN


def extract_vps_state(bold: dict[str, str]) -> str:
    return bold.get("vps path", UNKNOWN)


def extract_runtime(table: dict[str, str]) -> str:
    host = table.get("runtime host", "")
    user = table.get("runtime user", "")
    if host and user:
        return f"{host} ({user})"
    if host:
        return host
    if user:
        return user
    return UNKNOWN


def extract_archive(table: dict[str, str]) -> str:
    raw = table.get("archive", "")
    return raw[:60] if raw else UNKNOWN


def extract_blocker(text: str) -> str:
    section = extract_heading(text, "Current Blocker")
    if section:
        lines = [l.strip() for l in section.split("\n") if l.strip() and not l.startswith("#")]
        if lines:
            first = lines[0][:120]
            if first.lower().startswith("none"):
                return "none"
            return first
        return UNKNOWN
    return "none"


def extract_next_task(text: str) -> str:
    for heading in ("Next Authorized Work", "Next Authorized Phase"):
        section = extract_heading(text, heading)
        if section:
            lines = [l.strip() for l in section.split("\n") if l.strip() and not l.startswith("#")]
            if lines:
                return lines[0][:120]
    return UNKNOWN


def extract_hermes_scope(text: str, bold: dict[str, str], table: dict[str, str] | None = None) -> str:
    t = table or {}
    raw = t.get("hermes permission", t.get("hermes scope", ""))
    if raw:
        raw_lower = raw.lower()
        if "read-only" in raw_lower or "readonly" in raw_lower:
            return "read-only"
        if "admit" in raw_lower:
            return "read-only"
    if "hermes" in text.lower():
        m = re.search(r'(?i)hermes[^.]*?\b(read-?only|read-?write|enabled|disabled)\b', text)
        if m:
            return m.group(1).lower().replace(" ", "-")
    return NA


def github_visibility_from_baseline(repo_id: str) -> str:
    vis_map = {
        "traderie": "PRIVATE",
        "sjc-intel": "PRIVATE",
        "ih-market-companion": "PUBLIC",
        "reddit-ops": "PRIVATE",
        "idlehacking-kb": "PUBLIC",
        "palworld-kb": "PUBLIC",
        "bsda-courses": "PUBLIC",
        "wgu-atlas": "PUBLIC",
        "reckless-ben": "PRIVATE",
        "wgu-catalog": "PRIVATE",
    }
    return vis_map.get(repo_id, UNKNOWN)


def github_url_from_baseline(repo_id: str) -> str:
    url_map = {
        "traderie": "github.com/wguDataNinja/d2-market-helper",
        "reddit-ops": "github.com/wguDataNinja/WGU-Reddit-Feedback-Analyzer",
        "ih-market-companion": "github.com/wguDataNinja/ih-market-companion",
        "idlehacking-kb": "github.com/wguDataNinja/idlehacking-kb",
        "palworld-kb": "github.com/wguDataNinja/palworld-kb",
    }
    return url_map.get(repo_id, UNKNOWN)


def parse_control_md(
    repo_id: str,
    control_text: str,
    baseline_info: dict[str, str] | None = None,
) -> dict[str, str]:
    """Parse a single CONTROL.md into a registry record."""
    rec: dict[str, str] = {
        "repo_id": repo_id,
        "display_name": UNKNOWN,
        "purpose": UNKNOWN,
        "current_focus": UNKNOWN,
        "recent_milestone": UNKNOWN,
        "recent_reference": UNKNOWN,
        "long_horizon": UNKNOWN,
        "source": MISSING,
        "_yaml_present": "false",
        "lifecycle": UNKNOWN,
        "admission": UNKNOWN,
        "github_url": UNKNOWN,
        "default_branch": UNKNOWN,
        "github_visibility": UNKNOWN,
        "approved_sha": UNKNOWN,
        "vps_clone_state": UNKNOWN,
        "runtime": UNKNOWN,
        "scheduler_writer": UNKNOWN,
        "database": UNKNOWN,
        "health": UNKNOWN,
        "archive": UNKNOWN,
        "hermes_scope": NA,
        "blocker": UNKNOWN,
        "next_task": UNKNOWN,
        "gate": UNKNOWN,
        "last_verified": UNKNOWN,
        "warnings": "",
    }

    if baseline_info:
        rec["display_name"] = baseline_info.get("display_name", UNKNOWN)
        rec["github_visibility"] = github_visibility_from_baseline(repo_id)
        rec["github_url"] = github_url_from_baseline(repo_id)

    if not control_text:
        rec["source"] = MISSING
        rec["warnings"] = f"repo_id={repo_id} listed in PORTFOLIO_BASELINE but no CONTROL.md found"
        return rec

    rec["source"] = f"repos/{repo_id}/CONTROL.md"
    yaml_meta, body = parse_yaml_front_matter(control_text)

    if yaml_meta:
        rec["_yaml_present"] = "true"
        rec["repo_id"] = yaml_meta.get("repository.slug", repo_id)
        rec["purpose"] = yaml_meta.get("repository.purpose", UNKNOWN)
        rec["current_focus"] = yaml_meta.get("continuity.current_focus", UNKNOWN)
        rec["recent_milestone"] = yaml_meta.get("continuity.recent_milestone", UNKNOWN)
        rec["recent_reference"] = yaml_meta.get("continuity.recent_reference", UNKNOWN)
        rec["long_horizon"] = yaml_meta.get("continuity.long_horizon", UNKNOWN)
        body_title = next((line for line in body.splitlines() if line.startswith("# ")), "")
        rec["display_name"] = yaml_meta.get("display_name", yaml_meta.get("name",
            display_name_from_title(body_title)))
        if rec["display_name"] == UNKNOWN:
            rec["display_name"] = rec["purpose"]
        rec["lifecycle"] = yaml_meta.get("lifecycle.state",
            yaml_meta.get("lifecycle", yaml_meta.get("lifecycle_state", UNKNOWN)))
        rec["admission"] = yaml_meta.get("lifecycle.admission_gate",
            yaml_meta.get("admission", yaml_meta.get("admission_state", UNKNOWN)))
        rec["github_url"] = yaml_meta.get("repository.remote",
            yaml_meta.get("github_url", yaml_meta.get("canonical_remote", UNKNOWN)))
        rec["default_branch"] = yaml_meta.get("repository.default_branch",
            yaml_meta.get("default_branch", UNKNOWN))
        rec["github_visibility"] = yaml_meta.get("github.visibility",
            yaml_meta.get("github_visibility", rec["github_visibility"]))
        rec["approved_sha"] = yaml_meta.get("repository.approved_sha",
            yaml_meta.get("approved_sha", yaml_meta.get("approved_production_sha", UNKNOWN)))
        rec["vps_clone_state"] = yaml_meta.get("vps.clone_state",
            yaml_meta.get("vps_clone_state", yaml_meta.get("vps_path", UNKNOWN)))
        rec["runtime"] = yaml_meta.get("vps.runtime_location",
            yaml_meta.get("runtime", UNKNOWN))
        active = yaml_meta.get("scheduler.active", "")
        writer_val = yaml_meta.get("scheduler.writer", "")
        if active or writer_val:
            rec["scheduler_writer"] = (
                f"scheduler={active}; writer={writer_val}"
            )
        else:
            rec["scheduler_writer"] = yaml_meta.get("scheduler_writer",
                yaml_meta.get("scheduler", UNKNOWN))
        rec["database"] = yaml_meta.get("database.name",
            yaml_meta.get("database", UNKNOWN))
        rec["health"] = yaml_meta.get("health.state",
            yaml_meta.get("health", UNKNOWN))
        rec["archive"] = yaml_meta.get("data_locations.archive",
            yaml_meta.get("archive", UNKNOWN))
        rec["hermes_scope"] = yaml_meta.get("hermes.scope",
            yaml_meta.get("hermes_scope", NA))
        raw_blocker = yaml_meta.get("roadmap.blockers",
            yaml_meta.get("blocker", "none"))
        if raw_blocker and raw_blocker not in ("none", "[]", "", UNKNOWN):
            if raw_blocker.startswith("[") and raw_blocker.endswith("]"):
                try:
                    import ast
                    parsed = ast.literal_eval(raw_blocker)
                    if isinstance(parsed, list) and parsed:
                        rec["blocker"] = str(parsed[0])[:120]
                    elif isinstance(parsed, list):
                        rec["blocker"] = "none"
                    else:
                        rec["blocker"] = raw_blocker[:120]
                except (ValueError, SyntaxError):
                    rec["blocker"] = raw_blocker[:120]
            else:
                rec["blocker"] = raw_blocker[:120]
        else:
            rec["blocker"] = "none"
        rec["next_task"] = yaml_meta.get("roadmap.next_task",
            yaml_meta.get("next_task", UNKNOWN))
        raw_gate = yaml_meta.get("lifecycle.admission_gate",
            yaml_meta.get("gate", yaml_meta.get("current_gate", "")))
        if raw_gate and raw_gate not in (UNKNOWN, "", "null"):
            rec["gate"] = str(raw_gate)
        else:
            # Compute from roadmap gates list
            raw_rm_gates = yaml_meta.get("roadmap.gates", "[]")
            gates_passed = 0
            try:
                import ast
                parsed = ast.literal_eval(raw_rm_gates)
                if isinstance(parsed, list):
                    gates_passed = len(parsed)
            except (ValueError, SyntaxError):
                pass
            if gates_passed >= 6:
                rec["gate"] = "6"
            elif gates_passed > 0:
                rec["gate"] = str(min(gates_passed + 1, 6))
            else:
                rec["gate"] = parse_gate_from_lifecycle(rec["lifecycle"])
        rec["last_verified"] = yaml_meta.get("last_verified", UNKNOWN)
        return rec

    bold = extract_bold_fields(control_text)
    table = extract_table(control_text)

    rec["display_name"] = display_name_from_title(control_text.split("\n")[0]) if rec["display_name"] == UNKNOWN else rec["display_name"]
    rec["purpose"] = bold.get("purpose", UNKNOWN)
    rec["lifecycle"] = extract_lifecycle(control_text, bold)
    rec["github_url"] = bold.get("canonical remote", rec["github_url"])
    rec["default_branch"] = bold.get("default branch", UNKNOWN)
    rec["approved_sha"] = extract_sha(control_text)
    rec["vps_clone_state"] = extract_vps_state(bold)
    rec["runtime"] = extract_runtime(table)
    gate_from_table = extract_current_gate_from_table(control_text)
    rec["gate"] = gate_from_table if gate_from_table != UNKNOWN else parse_gate_from_lifecycle(rec["lifecycle"])
    rec["blocker"] = extract_blocker(control_text)
    rec["next_task"] = extract_next_task(control_text)
    rec["hermes_scope"] = extract_hermes_scope(control_text, bold, table)
    rec["scheduler_writer"] = f"scheduler={extract_scheduler_state(table, bold)}; writer={extract_writer(table)}"
    rec["database"] = extract_database(table)
    rec["health"] = extract_health(table)
    rec["archive"] = extract_archive(table)
    rec["last_verified"] = bold.get("last verified", UNKNOWN)

    return rec


def normalize_repo_id(dirname: str) -> str:
    return dirname.replace("_", "-")


def iter_existing_control_dirs() -> list[str]:
    if not REPOS_DIR.is_dir():
        return []
    return sorted(
        d.name for d in REPOS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def baseline_lookup(repo_id: str) -> dict[str, str] | None:
    for entry in BASELINE_REPOS:
        if entry["repo_id"] == repo_id:
            return entry
    return None


def build_registry(
    repo_filter: str | None = None,
    include_missing: bool = True,
) -> list[dict[str, str]]:
    existing = iter_existing_control_dirs()
    all_baseline_ids = {e["repo_id"] for e in BASELINE_REPOS}
    seen: set[str] = set()
    records: list[dict[str, str]] = []

    for dirname in existing:
        repo_id = normalize_repo_id(dirname)
        if repo_filter and repo_id != repo_filter:
            continue
        seen.add(repo_id)
        baseline = baseline_lookup(repo_id)
        ctrl_path = REPOS_DIR / dirname / "CONTROL.md"
        ctrl_text = read_file(ctrl_path)
        rec = parse_control_md(repo_id, ctrl_text, baseline)
        records.append(rec)

    if include_missing:
        for repo_id in sorted(all_baseline_ids):
            if repo_filter and repo_id != repo_filter:
                continue
            if repo_id in seen:
                continue
            baseline = baseline_lookup(repo_id)
            rec = parse_control_md(repo_id, "", baseline)
            records.append(rec)

    return records


def format_table(records: list[dict[str, str]], no_color: bool = False) -> str:
    headers = [
        "REPO_ID", "DISPLAY_NAME", "LIFECYCLE", "GATE",
        "APPROVED_SHA", "RUNTIME", "SCHEDULER/WRITER",
        "DATABASE", "CONTROL_HEALTH", "CONTROL_REVIEW", "BLOCKER", "NEXT_TASK",
    ]
    data = []
    for rec in records:
        data.append([
            rec["repo_id"],
            rec["display_name"][:20],
            rec["lifecycle"][:22],
            rec["gate"],
            rec["approved_sha"][:10],
            rec["runtime"][:20],
            rec["scheduler_writer"][:30],
            rec["database"][:20],
            rec["health"][:20],
            rec["last_verified"][:14],
            rec["blocker"][:40],
            rec["next_task"][:40],
        ])
    col_widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))
    buf = io.StringIO()
    header_line = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    buf.write(header_line)
    buf.write("\n")
    buf.write("  ".join("-" * w for w in col_widths))
    buf.write("\n")
    for row in data:
        line = "  ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
        buf.write(line)
        buf.write("\n")
    result = buf.getvalue()
    if no_color:
        return result
    return redact(result)


def format_json(records: list[dict[str, str]]) -> str:
    payload = {
        "registry_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "record_count": len(records),
        "records": records,
    }
    return json.dumps(payload, indent=2)


def format_context(records: list[dict[str, str]]) -> str:
    """Render a generated orientation brief from CONTROL metadata.

    This output is intentionally routing-only: the referenced CONTROL record,
    ROADMAP, and dated evidence remain authoritative for any action or claim.
    """
    lines = [
        "Ivy Control repository context (generated from CONTROL.md)",
        "Confirm authority, evidence, and approval boundaries before acting.",
    ]
    for rec in records:
        lines.extend([
            "",
            f"## {rec['display_name']} ({rec['repo_id']})",
            f"Purpose: {rec['purpose']}",
            f"Lifecycle / control health: {rec['lifecycle']} / {rec['health']}",
            f"Current focus: {rec['current_focus']}",
            f"Recent milestone: {rec['recent_milestone']}",
            f"Recent reference: {rec['recent_reference']}",
            f"Short-term authorized work: {rec['next_task']}",
            f"Long horizon: {rec['long_horizon']}",
            f"Risk / blocker: {rec['blocker']}",
            f"Control review: {rec['last_verified']} (not current operational evidence)",
            f"Authority: {rec['source']}",
        ])
    return redact("\n".join(lines) + "\n")


def validate_registry(records: list[dict[str, str]]) -> list[dict[str, str]]:
    """Run validation rules against the registry. Returns list of issues."""
    issues: list[dict[str, str]] = []
    seen_ids: dict[str, int] = {}

    REQUIRED_YAML_FIELDS = {"repository.slug", "lifecycle.state"}

    for i, rec in enumerate(records):
        rid = rec["repo_id"]

        if rid in seen_ids:
            issues.append({
                "severity": "error",
                "rule": "duplicate_id",
                "repo_id": rid,
                "message": f"Duplicate repo_id={rid} at records {seen_ids[rid]} and {i}",
            })
        seen_ids[rid] = i

        if rec["source"] == MISSING:
            issues.append({
                "severity": "warning",
                "rule": "missing_control_md",
                "repo_id": rid,
                "message": f"repo_id={rid} has no CONTROL.md (source=MISSING)",
            })

        if rec["approved_sha"] in (UNKNOWN, MISSING, "unknown"):
            issues.append({
                "severity": "warning",
                "rule": "missing_approved_sha",
                "repo_id": rid,
                "message": f"repo_id={rid} missing approved_sha",
            })
        elif rec["approved_sha"] == "null" and rec["source"] == MISSING:
            issues.append({
                "severity": "warning",
                "rule": "missing_approved_sha",
                "repo_id": rid,
                "message": f"repo_id={rid} missing approved_sha",
            })

        if rec["lifecycle"] not in VALID_LIFECYCLES and rec["lifecycle"] not in (UNKNOWN, MISSING):
            issues.append({
                "severity": "warning",
                "rule": "invalid_lifecycle",
                "repo_id": rid,
                "message": f"repo_id={rid} lifecycle={rec['lifecycle']} not in valid set",
            })

        if rec["gate"] not in VALID_GATES:
            issues.append({
                "severity": "warning",
                "rule": "invalid_gate",
                "repo_id": rid,
                "message": f"repo_id={rid} gate={rec['gate']} not in valid gate set",
            })

        lifecycle = rec["lifecycle"].lower()
        is_active_production = any(t in lifecycle for t in ["production", "active", "stabilizing", "degraded"])

        if is_active_production and rec["source"] != MISSING:
            scheduler_writer = rec.get("scheduler_writer", "").lower()
            if "scheduler=unknown" in scheduler_writer or "scheduler=unknown" in scheduler_writer:
                issues.append({
                    "severity": "warning",
                    "rule": "active_runtime_no_scheduler",
                    "repo_id": rid,
                    "message": f"Active runtime lifecycle={rec['lifecycle']} but scheduler is UNKNOWN",
                })
            if "writer=unknown" in scheduler_writer:
                issues.append({
                    "severity": "warning",
                    "rule": "active_runtime_no_writer",
                    "repo_id": rid,
                    "message": f"Active runtime lifecycle={rec['lifecycle']} but writer is UNKNOWN",
                })

        if is_active_production and rec["database"] not in (UNKNOWN, MISSING, NA, "none") and rec["source"] != MISSING:
            if "backup" not in rec.get("health", "").lower() and rec["health"] != UNKNOWN:
                pass

        if rec["_yaml_present"] == "true":
            if rec["source"] != MISSING:
                ctrl_text = read_file(REPOS_DIR / rid / "CONTROL.md")
                yaml_meta, _ = parse_yaml_front_matter(ctrl_text)
                missing = REQUIRED_YAML_FIELDS - set(yaml_meta.keys())
                if missing:
                    issues.append({
                        "severity": "warning",
                        "rule": "yaml_missing_required_fields",
                        "repo_id": rid,
                        "message": f"YAML front matter present but missing required fields: {', '.join(sorted(missing))}",
                    })

        if is_active_production and rec["hermes_scope"] in (NA, UNKNOWN, MISSING):
            issues.append({
                "severity": "warning",
                "rule": "active_repo_no_hermes_scope",
                "repo_id": rid,
                "message": f"Active lifecycle={rec['lifecycle']} but hermes_scope is {rec['hermes_scope']}",
            })

        if rec["hermes_scope"] not in (NA, UNKNOWN, MISSING) and rec["hermes_scope"]:
            if rec["hermes_scope"] not in HERMES_SCOPES:
                issues.append({
                    "severity": "warning",
                    "rule": "invalid_hermes_scope",
                    "repo_id": rid,
                    "message": f"repo_id={rid} hermes_scope={rec['hermes_scope']} not in valid set",
                })

        if rec["last_verified"] not in (UNKNOWN, MISSING, NA, ""):
            try:
                lv_date = date.fromisoformat(rec["last_verified"])
                days_old = (date.today() - lv_date).days
                if days_old > 30:
                    issues.append({
                        "severity": "warning",
                        "rule": "stale_last_verified",
                        "repo_id": rid,
                        "message": f"last_verified={rec['last_verified']} is {days_old} days old (>30 day threshold)",
                    })
            except (ValueError, TypeError):
                issues.append({
                    "severity": "warning",
                    "rule": "stale_date",
                    "repo_id": rid,
                    "message": f"repo_id={rid} last_verified={rec['last_verified']} is not a valid ISO date",
                })

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Portfolio registry — generate, display, validate"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON (default: table)")
    parser.add_argument("--table", action="store_true", help="Output as human-readable table")
    parser.add_argument("--context", action="store_true",
                        help="Output generated repository continuity/orientation context")
    parser.add_argument("--validate", action="store_true", help="Run validation and exit")
    parser.add_argument("--repo", type=str, default=None, help="Filter by repo_id")
    parser.add_argument("--no-placeholders", dest="placeholders", action="store_false", default=True)
    parser.add_argument("--no-color", action="store_true", help="Suppress redaction")
    parser.add_argument("--output", type=Path, default=None, help="Write JSON to file")
    args = parser.parse_args()

    records = build_registry(
        repo_filter=args.repo,
        include_missing=args.placeholders,
    )

    if not records:
        print("No matching records found.")
        return 0

    if args.validate:
        issues = validate_registry(records)
        if issues:
            print(f"Validation: {len(issues)} issue(s) found\n")
            for issue in issues:
                tag = "[ERROR]" if issue["severity"] == "error" else "[WARN]"
                print(f"  {tag} {issue['rule']}: {issue['message']}")
            return 1 if any(i["severity"] == "error" for i in issues) else 0
        else:
            print("Validation: 0 issues found — all records clean.")
            return 0

    if args.context:
        if args.output:
            parser.error("--context cannot be combined with --output")
        sys.stdout.write(format_context(records))
        return 0

    want_json = args.json or (args.output is not None)
    if want_json:
        output = format_json(records)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output + "\n", encoding="utf-8")
            print(args.output)
        else:
            sys.stdout.write(output)
            sys.stdout.write("\n")
    else:
        output = format_table(records, no_color=args.no_color)
        sys.stdout.write(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
