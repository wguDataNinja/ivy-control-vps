#!/usr/bin/env python3
"""Read-only Hermes orchestration helpers.

These helpers intentionally do not dispatch executors or mutate Git state.
They provide the structured context, roadmap, task selection, packet, and
run-state artifacts needed for a supervised Hermes planning loop.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
UTC = timezone.utc
ACCEPTED_VALIDATION_DISPOSITIONS = {"COMPLETED", "COMPLETED_WITH_WARNINGS"}
TASK_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
INTAKE_BLOCKED_STATUSES = {"AUTHORITY_UNRESOLVED", "IDENTITY_CONFLICT", "RESTRICTED"}
RUN_ID_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-[A-Za-z0-9][A-Za-z0-9_.-]*$|^session-[0-9]+-[A-Za-z0-9][A-Za-z0-9_.-]*$")
BARE_SESSION_PATTERN = re.compile(r"^_internal/(inbox|outbox)/session-[0-9]+(?:/|$)")


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_git(repo: Path, *args: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": ["git", *args],
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def parse_status_porcelain(output: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for raw in output.splitlines():
        if not raw or raw.startswith("## "):
            continue
        if raw.startswith("?? "):
            entries.append({"path": raw[3:], "index": "?", "worktree": "?", "state": "untracked"})
            continue
        index = raw[0]
        worktree = raw[1]
        path = raw[3:]
        state = "modified"
        if index == "D" or worktree == "D":
            state = "deleted"
        elif index != " " and worktree == " ":
            state = "staged"
        elif index != " " and worktree != " ":
            state = "staged-and-modified"
        entries.append({"path": path, "index": index, "worktree": worktree, "state": state})
    return entries


def classify_path(path: str, status: str) -> dict[str, str]:
    private_prefixes = ("_internal/", "internal/", "_inbox/")
    generated_markers = ("/dist/", "/build/", ".pyc", "__pycache__", "node_modules/")
    if path.startswith(private_prefixes):
        disposition = "private-only"
        kind = "private"
    elif any(marker in path for marker in generated_markers):
        disposition = "review-before-publish"
        kind = "generated"
    elif path.startswith("agent/inbox/") or path.startswith("agent/reports/") or path.startswith("logs/"):
        disposition = "review-and-publish"
        kind = "evidence"
    elif path.endswith((".md", ".rst")):
        disposition = "review-and-publish"
        kind = "docs"
    elif path.endswith((".py", ".ts", ".tsx", ".js", ".json", ".yaml", ".yml", ".toml", ".sh")):
        disposition = "review-and-publish"
        kind = "source-or-config"
    else:
        disposition = "review-before-publish"
        kind = "unknown"
    return {
        "path": path,
        "status": status,
        "type": kind,
        "publishable": "no" if disposition == "private-only" else "needs-review",
        "recommended_disposition": disposition,
    }


def resolve_repository_context(repo: Path, slug: str | None = None, control_path: Path | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    git_root = run_git(repo, "rev-parse", "--show-toplevel")
    is_git = git_root["returncode"] == 0
    branch = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD") if is_git else {}
    head = run_git(repo, "rev-parse", "HEAD") if is_git else {}
    status = run_git(repo, "status", "--short", "--branch") if is_git else {}
    remotes = run_git(repo, "remote", "-v") if is_git else {}
    worktrees = run_git(repo, "worktree", "list", "--porcelain") if is_git else {}
    stash = run_git(repo, "stash", "list") if is_git else {}
    dirty = parse_status_porcelain(status.get("stdout", ""))
    classified = [classify_path(item["path"], item["state"]) for item in dirty]
    remote_names = sorted({line.split()[0] for line in remotes.get("stdout", "").splitlines() if line.strip()})
    default_ref = "origin/main" if "origin" in remote_names else ""
    divergence: dict[str, Any] = {"base": default_ref, "available": False}
    if default_ref:
        div = run_git(repo, "rev-list", "--left-right", "--count", f"HEAD...{default_ref}")
        divergence = {
            "base": default_ref,
            "available": div["returncode"] == 0,
            "ahead_behind": div["stdout"] if div["returncode"] == 0 else None,
            "error": div["stderr"] if div["returncode"] != 0 else "",
        }
    control: dict[str, Any] = {"path": str(control_path) if control_path else None, "exists": False}
    if control_path and control_path.exists():
        text = read_text(control_path)
        control = {
            "path": str(control_path),
            "exists": True,
            "sha256": sha256_text(text),
            "lifecycle": extract_bold_value(text, "Lifecycle state") or extract_yaml_value(text, "state"),
            "hermes_scope": extract_table_value(text, "Read-only inspection") or "",
            "current_blocker": extract_section(text, "Current Blocker").strip(),
            "next_authorized_work": extract_section(text, "Next Authorized Work").strip(),
        }
    lock_state = "locked" if dirty else "available-for-read-only-planning"
    return {
        "schema_version": "hermes.repository_context.v1",
        "generated_at": now_iso(),
        "repository": {"slug": slug or repo.name, "path": str(repo), "is_git_repository": is_git},
        "git": {
            "branch": branch.get("stdout", "") if is_git else "",
            "head": head.get("stdout", "") if is_git else "",
            "status_short_branch": status.get("stdout", "") if is_git else "",
            "remotes": remotes.get("stdout", "") if is_git else "",
            "divergence": divergence,
            "worktrees": worktrees.get("stdout", "") if is_git else "",
            "stash": stash.get("stdout", "") if is_git else "",
        },
        "dirty_state": classified,
        "lock_state": lock_state,
        "authority": control,
        "stop_reasons": derive_context_stop_reasons(classified, divergence, control),
    }


def extract_yaml_value(text: str, key: str) -> str:
    pattern = re.compile(rf"^\s*{re.escape(key)}:\s*['\"]?([^'\"\n]+)", re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def extract_bold_value(text: str, key: str) -> str:
    pattern = re.compile(rf"\*\*{re.escape(key)}:\*\*\s*`?([^`\n]+)`?", re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def extract_table_value(text: str, key: str) -> str:
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].lower() == key.lower():
            return cells[1]
    return ""


def extract_section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    return match.group(1) if match else ""


def extract_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    raw = text[4:end].strip()
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(raw) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return parse_simple_frontmatter(raw)


def parse_simple_frontmatter(raw: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, value = line.strip().split(":", 1)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        value = value.strip()
        if value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        elif value == "null":
            parent[key] = None
        elif value.startswith("[") and value.endswith("]"):
            parent[key] = [item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()]
        else:
            parent[key] = value.strip("\"'")
    return root


def nested_get(data: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def derive_context_stop_reasons(dirty: list[dict[str, str]], divergence: dict[str, Any], control: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if dirty:
        reasons.append("repository has dirty or untracked state; mutation requires preservation/disposition first")
    if divergence.get("available") is False and divergence.get("base"):
        reasons.append(f"cannot determine divergence from {divergence['base']}")
    blocker = (control.get("current_blocker") or "").lower()
    if blocker and "none" not in blocker:
        reasons.append("control record has a current blocker")
    return reasons


@dataclass
class RoadmapTask:
    task_id: str
    title: str
    outcome: str = ""
    dependencies: str = ""
    validation: str = ""
    human_gate: str = ""
    stop_conditions: str = ""
    completion_criteria: str = ""
    included_work: str = ""
    excluded_work: str = ""
    status: str = "unknown"

    def to_dict(self) -> dict[str, str]:
        return self.__dict__.copy()


def parse_roadmap(path: Path) -> dict[str, Any]:
    text = read_text(path)
    tasks: list[RoadmapTask] = []
    heading_re = re.compile(r"^###\s+([A-Z0-9]+(?:-[A-Z0-9]+)+)\s+[—-]\s+(.+)$", re.MULTILINE)
    matches = list(heading_re.finditer(text))
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[start:end]
        task = RoadmapTask(task_id=match.group(1), title=match.group(2).strip())
        for label, attr in [
            ("Outcome", "outcome"),
            ("Dependencies", "dependencies"),
            ("Validation", "validation"),
            ("Human gate", "human_gate"),
            ("Stop conditions", "stop_conditions"),
            ("Completion criteria", "completion_criteria"),
            ("Included work", "included_work"),
            ("Excluded work", "excluded_work"),
            ("Status", "status"),
        ]:
            value = extract_bold_field(block, label)
            if value:
                setattr(task, attr, value)
        tasks.append(task)
    return {
        "schema_version": "hermes.roadmap.v1",
        "generated_at": now_iso(),
        "roadmap_path": str(path.resolve()),
        "roadmap_sha256": sha256_text(text),
        "status": extract_bold_value(text, "Status") or "unknown",
        "approval_owner": extract_bold_value(text, "Approval owner") or "",
        "repository": extract_bold_value(text, "Repository") or "",
        "tasks": [task.to_dict() for task in tasks],
    }


def extract_bold_field(text: str, label: str) -> str:
    pattern = re.compile(rf"\*\*{re.escape(label)}:\*\*\s*(.*?)(?=\n\n|\n\*\*[A-Z]|\Z)", re.DOTALL)
    match = pattern.search(text)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def normalize_intent(intent: dict[str, Any]) -> dict[str, Any]:
    required = ["objective", "repositories", "authority_envelope", "duration_bound", "stop_conditions"]
    missing = [key for key in required if not intent.get(key)]
    normalized = {
        "schema_version": "hermes.user_intent.v1",
        "intent_id": intent.get("intent_id") or f"intent-{uuid.uuid4().hex[:12]}",
        "objective": intent.get("objective", ""),
        "repositories": intent.get("repositories", []),
        "authority_envelope": intent.get("authority_envelope", {}),
        "duration_bound": intent.get("duration_bound", {"max_tasks": 1}),
        "scope_boundary": intent.get("scope_boundary", {}),
        "stop_conditions": intent.get("stop_conditions", []),
        "created_at": intent.get("created_at") or now_iso(),
        "missing_required_fields": missing,
    }
    return normalized


def inspect_control_plane_candidate(slug: str, path: Path) -> dict[str, Any]:
    path = path.resolve()
    doc_names = ["AGENTS.md", "README.md", "ROADMAP.md"]
    docs: list[dict[str, Any]] = []
    claims: list[dict[str, str]] = []
    redirects: list[dict[str, str]] = []
    for name in doc_names:
        doc_path = path / name
        if not doc_path.exists():
            docs.append({"path": str(doc_path), "exists": False, "sha256": "", "claim_summary": "missing"})
            continue
        text = read_text(doc_path)
        summary = "authority document inspected"
        lower = text.lower()
        if "portfolio control plane" in lower or "local control plane" in lower or "control-plane repository" in lower:
            claims.append({
                "repository": slug,
                "document": str(doc_path),
                "claim_type": "control_plane_authority",
                "basis": "root authority document describes this repository as a control plane",
            })
            summary = "contains control-plane authority claim"
        for target in re.findall(
            r"(?:redirects?|delegates?|superseded by|governed by)\s+(?:governance\s+)?(?:to\s+)?([A-Za-z0-9_.-]+)",
            text,
            flags=re.IGNORECASE,
        ):
            redirects.append({
                "from": slug,
                "to": target.strip("`., "),
                "document": str(doc_path),
                "basis": "explicit redirect/delegation wording",
            })
        docs.append({
            "path": str(doc_path),
            "exists": True,
            "sha256": sha256_text(text),
            "claim_summary": summary,
        })
    registry_path = path / "registry" / "repos.yaml"
    registry_claim = None
    if registry_path.exists():
        registry_text = read_text(registry_path)
        registry_claim = {
            "repository": slug,
            "document": str(registry_path),
            "claim_type": "registry_taxonomy",
            "authority_use": "inventory_only",
            "basis": "registry membership does not establish governance authority",
            "sha256": sha256_text(registry_text),
        }
        claims.append(registry_claim)
    return {
        "slug": slug,
        "path": str(path),
        "documents_checked": docs,
        "authority_claims": claims,
        "delegation_or_redirect": redirects,
        "registry_taxonomy": registry_claim,
    }


def resolve_authority(candidates: list[dict[str, Any]], preferred_active: str | None = None) -> dict[str, Any]:
    inspected = [inspect_control_plane_candidate(item["slug"], Path(item["path"])) for item in candidates]
    candidate_slugs = {item["slug"] for item in inspected}
    all_docs = [doc for candidate in inspected for doc in candidate["documents_checked"]]
    all_claims = [claim for candidate in inspected for claim in candidate["authority_claims"]]
    redirects = [
        redir
        for candidate in inspected
        for redir in candidate["delegation_or_redirect"]
        if redir["to"] in candidate_slugs
    ]
    control_claims = [claim for claim in all_claims if claim["claim_type"] == "control_plane_authority"]
    registry_claims = [claim for claim in all_claims if claim["claim_type"] == "registry_taxonomy"]
    redirected_from = {item["from"] for item in redirects}
    redirected_to = {item["to"] for item in redirects}
    unresolved_claims = [claim for claim in control_claims if claim["repository"] not in redirected_from]
    unresolved_repositories = sorted({claim["repository"] for claim in unresolved_claims})
    status = "AUTHORITY_INSUFFICIENT_EVIDENCE"
    active: str | None = None
    conflicts: list[str] = []
    basis: list[str] = []

    if not any(doc["exists"] for doc in all_docs):
        basis.append("no authority documents were inspected")
    elif control_claims:
        if preferred_active:
            matching = preferred_active in unresolved_repositories
            competing = [repo for repo in unresolved_repositories if repo != preferred_active]
            if matching and not competing:
                active = preferred_active
                status = "AUTHORITY_RESOLVED"
                basis.append("preferred active control plane has explicit authority claim and no unresolved competing claim")
            elif matching and competing:
                status = "AUTHORITY_CONFLICT"
                conflicts.append("preferred active control plane has unresolved competing control-plane claim")
            else:
                status = "AUTHORITY_INSUFFICIENT_EVIDENCE"
                basis.append("preferred active control plane lacks an explicit authority claim")
        elif len(unresolved_repositories) == 1:
            active = unresolved_repositories[0]
            status = "AUTHORITY_RESOLVED"
            basis.append("exactly one unresolved explicit control-plane authority claim")
        elif len(unresolved_repositories) > 1:
            status = "AUTHORITY_CONFLICT"
            conflicts.append("multiple unresolved control-plane authority claims")
        elif redirected_to:
            active = sorted(redirected_to)[0]
            status = "AUTHORITY_RESOLVED"
            basis.append("all explicit control-plane claims redirect or delegate")
    elif registry_claims:
        status = "AUTHORITY_INSUFFICIENT_EVIDENCE"
        basis.append("registry taxonomy was present but is inventory only")
    else:
        basis.append("no explicit control-plane authority claim found")

    if status == "AUTHORITY_RESOLVED" and active:
        confidence = "high" if not conflicts else "low"
        resolution = f"Active control plane resolved to {active}."
        conflict_detected = False
    elif status == "AUTHORITY_CONFLICT":
        confidence = "low"
        resolution = "Stop: competing control-plane claims require human resolution."
        conflict_detected = True
    else:
        confidence = "low"
        resolution = "Stop: insufficient authority evidence to select an active control plane."
        conflict_detected = False

    return {
        "schema_version": "hermes.authority_resolution.v1",
        "generated_at": now_iso(),
        "status": status,
        "active_control_plane": active,
        "candidate_control_planes": inspected,
        "documents_checked": all_docs,
        "authority_claims": all_claims,
        "delegation_or_redirect": redirects,
        "registry_taxonomy_policy": "inventory_only_not_authority",
        "conflict_detected": conflict_detected,
        "conflicting_claims": conflicts,
        "resolution": resolution,
        "resolution_basis": basis,
        "confidence": confidence,
        "sufficient_to_continue": status == "AUTHORITY_RESOLVED",
    }


def validate_authority_resolution(authority: dict[str, Any] | None) -> tuple[bool, list[str], str]:
    if not authority:
        return False, ["no active control plane resolution supplied"], "AUTHORITY_INSUFFICIENT_EVIDENCE"
    status = authority.get("status", "AUTHORITY_INSUFFICIENT_EVIDENCE")
    errors: list[str] = []
    if status != "AUTHORITY_RESOLVED":
        errors.append(f"authority resolution status is {status}")
    if not authority.get("active_control_plane"):
        errors.append("active_control_plane is missing")
    if not authority.get("documents_checked"):
        errors.append("authority documents were not inspected")
    if authority.get("conflict_detected"):
        errors.append("competing control-plane claim exists without explicit resolution")
    claims = authority.get("authority_claims", [])
    non_registry = [claim for claim in claims if claim.get("claim_type") != "registry_taxonomy"]
    if claims and not non_registry:
        errors.append("registry entry is the sole basis for authority")
    return not errors, errors, status


def analyze_eligibility(intent: dict[str, Any], context: dict[str, Any], roadmap: dict[str, Any]) -> dict[str, Any]:
    tasks = roadmap.get("tasks", [])
    selected: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    for index, task in enumerate(tasks):
        reasons: list[str] = []
        eligible = True
        deps = task.get("dependencies", "").lower()
        if deps and deps not in {"none", "none, except fresh `git fetch`."} and "none" not in deps:
            eligible = False
            reasons.append(f"dependencies not proven satisfied: {task.get('dependencies')}")
        if selected is None and eligible:
            selected = task
            reasons.append("selected by roadmap order: first eligible package")
        elif eligible:
            reasons.append("eligible but lower roadmap order than selected task")
        rows.append({
            "task_id": task.get("task_id"),
            "title": task.get("title"),
            "eligible": eligible,
            "reasons": reasons,
            "roadmap_order": index + 1,
        })
    return {
        "schema_version": "hermes.task_eligibility.v1",
        "generated_at": now_iso(),
        "intent_id": intent.get("intent_id"),
        "repository": context.get("repository", {}),
        "context_stop_reasons": context.get("stop_reasons", []),
        "eligible_tasks": rows,
        "selected_task": selected,
        "selection_policy": "roadmap order after dependency and envelope filtering",
    }


def rank_repositories(intent: dict[str, Any], contexts: list[dict[str, Any]], authority: dict[str, Any]) -> dict[str, Any]:
    """Rank repository candidates before executor selection.

    Repository ownership and executor routing are deliberately separate:
    ivy-control-vps remains a candidate unless the intent or governance
    explicitly excludes it.
    """
    ok, errors, status = validate_authority_resolution(authority)
    if not ok:
        return {
            "schema_version": "hermes.repository_recommendation.v1",
            "generated_at": now_iso(),
            "intent_id": intent.get("intent_id"),
            "status": status,
            "errors": errors,
            "candidates": [],
            "recommended_repository": None,
            "selection_policy": "blocked before ranking because authority resolution failed",
        }
    scope = intent.get("scope_boundary", {})
    include = set(scope.get("include_repositories", []) or intent.get("repositories", []) or [])
    exclude = set(scope.get("exclude_repositories", []) or [])
    explicit_priority = list(scope.get("repository_priority", []) or [])
    rows: list[dict[str, Any]] = []
    for context in contexts:
        repo = context.get("repository", {})
        slug = repo.get("slug", "")
        repo_authority = context.get("authority", {})
        reasons: list[str] = []
        score = 0
        eligible = True
        if slug in exclude:
            eligible = False
            reasons.append("explicitly excluded by user intent")
        if include and "all" not in include and "portfolio" not in include and slug not in include:
            eligible = False
            reasons.append("outside user-intent repository scope")
        blocker = (repo_authority.get("current_blocker") or "").lower()
        if blocker and "none" not in blocker:
            score -= 40
            reasons.append("control record has current blocker")
        next_work = (repo_authority.get("next_authorized_work") or "").strip()
        if next_work:
            score += 20
            reasons.append("control record identifies next authorized work")
        if not context.get("dirty_state"):
            score += 10
            reasons.append("working tree has no dirty-state lock")
        else:
            score -= 5
            reasons.append("dirty state permits inspection but blocks mutation")
        if explicit_priority and slug in explicit_priority:
            score += 100 - explicit_priority.index(slug)
            reasons.append("listed in user-intent repository priority")
        if slug == "ivy-control-vps":
            reasons.append("control-plane repository is included unless governance explicitly excludes it")
        rows.append({
            "repository": slug,
            "path": repo.get("path", ""),
            "eligible": eligible,
            "priority_score": score if eligible else -1000,
            "reasons": reasons,
            "executor_selection": "not evaluated here",
        })
    rows.sort(key=lambda row: (-row["priority_score"], row["repository"]))
    selected = rows[0] if rows and rows[0]["eligible"] else None
    return {
        "schema_version": "hermes.repository_recommendation.v1",
        "generated_at": now_iso(),
        "status": "AUTHORITY_RESOLVED",
        "active_control_plane": authority.get("active_control_plane"),
        "intent_id": intent.get("intent_id"),
        "selection_policy": "evaluate repositories first; choose highest-priority eligible candidate; route executor later",
        "candidates": rows,
        "recommended_repository": selected,
    }


def author_packet(intent: dict[str, Any], context: dict[str, Any], roadmap: dict[str, Any], eligibility: dict[str, Any]) -> str:
    task = eligibility.get("selected_task") or {}
    repo = context.get("repository", {})
    dirty_paths = ", ".join(item["path"] for item in context.get("dirty_state", [])[:12]) or "none"
    stop_reasons = context.get("stop_reasons", [])
    title = task.get("title", "No eligible task")
    task_id = task.get("task_id", "NO-TASK")
    return f"""# {task_id} — {title}

**Status:** DRAFT_NOT_APPROVED
**Generated:** {now_iso()}
**Intent:** {intent.get('intent_id')}

## Objective

{task.get('outcome') or intent.get('objective') or 'No objective available.'}

## Repository Context

- Repository: {repo.get('slug')} at `{repo.get('path')}`
- Branch: `{context.get('git', {}).get('branch', '')}`
- HEAD: `{context.get('git', {}).get('head', '')}`
- Dirty/untracked paths: {dirty_paths}
- Context stop reasons: {('; '.join(stop_reasons)) if stop_reasons else 'none for read-only planning'}

## Authoritative Sources

- `{roadmap.get('roadmap_path')}`
- repository AGENTS.md / control record when present
- `agents/HERMES_AGENT_CONTRACT.md`
- `docs/REPOSITORY_WORK_PROTOCOL.md`

## Scope

- Read-only inspection and evidence preparation only.
- Candidate package: `{task_id}`.
- Included work: {task.get('included_work') or 'See roadmap package.'}

## Do Not

- Do not stage, commit, push, merge, reset, clean, stash, delete, or publish.
- Do not modify production data, services, credentials, or branch protection.
- Do not resolve human gates without Buddy approval.

## Validation Requirements

{task.get('validation') or 'Run repository preflight and record evidence.'}

## Human Gate

{task.get('human_gate') or 'None recorded in selected roadmap package.'}

## Stop Conditions

{task.get('stop_conditions') or 'Use repository global stop rules.'}

## Result Report Requirements

Stable task ID: `{task_id}`. Use this same ID in the packet, execution report,
validation report, execution log, and archive manifest.

Write the execution report to the target repository's declared `agent/reports/`
path if this packet is later dispatched. Treat the report as a claim requiring
independent Hermes verification.

After Hermes validation accepts the completed task, archive the active artifacts
under `_internal/orchestration/repos/{repo.get('slug')}/tasks/{task_id}/` or the
cross-repo archive namespace when the task spans multiple repositories.

## Approval Boundary

This draft does not create a session/task artifact in the target repository and
does not authorize dispatch. Create the durable task packet only after explicit
approval unless repository policy explicitly authorizes pre-creation.
"""


def create_run_state(intent: dict[str, Any], state: str, artifacts: dict[str, str], dispatch: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": "hermes.run_state.v1",
        "run_id": f"run-{uuid.uuid4().hex[:12]}",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "state": state,
        "intent": intent,
        "artifacts": artifacts,
        "completed_tasks": [],
        "in_flight_dispatch": dispatch,
        "next_action": derive_next_action(state, dispatch),
    }


def derive_next_action(state: str, dispatch: dict[str, Any] | None) -> str:
    if state == "DISPATCH" and dispatch:
        return "monitor for the exact result report path before re-dispatching"
    if state == "VERIFY":
        return "run verification against packet, report, and repository state"
    if state == "STOP":
        return "present final state to Buddy"
    return "continue state-machine transition from recorded state"


def reconstruct_run_state(path: Path) -> dict[str, Any]:
    state = json.loads(read_text(path))
    return {
        "schema_version": "hermes.restart_reconstruction.v1",
        "reconstructed_at": now_iso(),
        "run_id": state.get("run_id"),
        "state": state.get("state"),
        "intent": state.get("intent"),
        "completed_tasks": state.get("completed_tasks", []),
        "in_flight_dispatch": state.get("in_flight_dispatch"),
        "next_action": derive_next_action(state.get("state", ""), state.get("in_flight_dispatch")),
        "source_path": str(path.resolve()),
        "source_sha256": sha256_text(json.dumps(state, sort_keys=True)),
    }


def memory_status(source: Path, live: Path) -> dict[str, Any]:
    source_text = read_text(source) if source.exists() else ""
    live_text = read_text(live) if live.exists() else ""
    return {
        "schema_version": "hermes.memory_status.v1",
        "generated_at": now_iso(),
        "source": {
            "path": str(source),
            "exists": source.exists(),
            "sha256": sha256_text(source_text) if source_text else "",
            "line_count": len(source_text.splitlines()) if source_text else 0,
        },
        "live": {
            "path": str(live),
            "exists": live.exists(),
            "sha256": sha256_text(live_text) if live_text else "",
            "line_count": len(live_text.splitlines()) if live_text else 0,
        },
        "drift": bool(source_text and live_text and source_text.strip() != live_text.strip()),
        "authoritative_copy": "repository_source",
    }


def run_command(command: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout_first_line": proc.stdout.splitlines()[0] if proc.stdout.splitlines() else "",
        "stderr_first_line": proc.stderr.splitlines()[0] if proc.stderr.splitlines() else "",
    }


def describe_executable(path: Path) -> dict[str, Any]:
    path = path.expanduser()
    exists = path.exists()
    text = ""
    if exists and path.is_file():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = ""
    target = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("exec "):
            parts = shlex.split(stripped)
            if len(parts) >= 2:
                target = parts[1]
            break
    return {
        "path": str(path),
        "exists": exists,
        "resolved_path": str(path.resolve()) if exists else "",
        "sha256": sha256_text(text) if text else "",
        "first_line": text.splitlines()[0] if text.splitlines() else "",
        "exec_target": target,
        "help_check": run_command([str(path), "--help"]) if exists else {"returncode": 127},
    }


def runtime_diagnostic(
    source: Path,
    live: Path,
    canonical: Path,
    alternate: Path,
    backup: Path | None = None,
) -> dict[str, Any]:
    mem = memory_status(source, live)
    canonical_info = describe_executable(canonical)
    alternate_info = describe_executable(alternate)
    backup_info: dict[str, Any] = {"path": str(backup) if backup else "", "exists": False}
    if backup and backup.exists():
        backup_text = read_text(backup)
        backup_info = {
            "path": str(backup),
            "exists": True,
            "sha256": sha256_text(backup_text),
            "line_count": len(backup_text.splitlines()),
            "restore_command": f"cp -p {backup} {live}",
        }
    ambiguity: list[str] = []
    if canonical_info["help_check"].get("returncode") != 0:
        ambiguity.append("canonical executable help check failed")
    if alternate_info["help_check"].get("returncode") != 0:
        ambiguity.append("alternate executable help check failed")
    if canonical_info.get("sha256") != alternate_info.get("sha256"):
        ambiguity.append("canonical and alternate launcher content differs")
    if mem.get("drift"):
        ambiguity.append("repository and live memory differ")
    return {
        "schema_version": "hermes.runtime_diagnostic.v1",
        "generated_at": now_iso(),
        "canonical_executable": canonical_info,
        "alternate_executable": alternate_info,
        "memory": mem,
        "backup": backup_info,
        "entrypoint_ambiguity": ambiguity,
        "status": "PASS" if not ambiguity else "REVIEW_REQUIRED",
    }


def verify_report(packet_path: Path, report_path: Path, repo: Path, allowed_paths: list[str]) -> dict[str, Any]:
    status = resolve_repository_context(repo)
    changed = [item["path"] for item in status.get("dirty_state", [])]
    violations = [path for path in changed if allowed_paths and not any(path == allowed or path.startswith(allowed.rstrip("/") + "/") for allowed in allowed_paths)]
    return {
        "schema_version": "hermes.verification.v1",
        "generated_at": now_iso(),
        "packet_path": str(packet_path),
        "report_path": str(report_path),
        "packet_exists": packet_path.exists(),
        "report_exists": report_path.exists(),
        "changed_paths": changed,
        "allowed_paths": allowed_paths,
        "scope_violations": violations,
        "verified_disposition": "HUMAN_DECISION_REQUIRED" if violations else "COMPLETED_WITH_WARNINGS",
    }


def artifact_namespace(repositories: list[str]) -> tuple[str, str]:
    unique = sorted({repo for repo in repositories if repo})
    if not unique:
        raise ValueError("at least one repository is required")
    if len(unique) == 1:
        return "repository", f"repos/{unique[0]}"
    return "cross_repository", "cross-repo"


def artifact_archive_name(role: str, source: Path) -> str:
    if role == "task_packet":
        return "task-packet.md"
    if role == "execution_report":
        return "execution-report.md"
    if role == "execution_log":
        return "execution-log.md"
    suffix = source.suffix or ".md"
    return f"validation-report{suffix}"


def normalize_artifact_path(path: Path) -> str:
    try:
        relative = path.resolve().relative_to(REPO_ROOT.resolve())
        return relative.as_posix()
    except ValueError:
        return path.as_posix().lstrip("./")


def validate_artifact_destination(path: Path) -> dict[str, Any]:
    """Validate one proposed artifact destination.

    This validates new destinations. It intentionally does not scan or condemn
    legacy session directories that already exist for historical auditability.
    """
    rel = normalize_artifact_path(path)
    errors: list[str] = []
    accepted_location = ""

    if BARE_SESSION_PATTERN.match(rel):
        errors.append("bare session-N inbox/outbox destinations are ambiguous; use runs/<run-id> or repos/<repo>/<task-id>")

    parts = rel.split("/")
    if len(parts) >= 4 and parts[:3] in (["_internal", "inbox", "runs"], ["_internal", "outbox", "runs"]):
        run_id = parts[3]
        if RUN_ID_PATTERN.match(run_id):
            accepted_location = "active_run_queue"
        else:
            errors.append("run id must be globally distinguishable: YYYY-MM-DD-<slug> or session-<N>-<slug>")
    elif len(parts) >= 5 and parts[:3] in (["_internal", "inbox", "repos"], ["_internal", "outbox", "repos"]):
        repo = parts[3]
        task_id = parts[4]
        if not TASK_ID_PATTERN.match(repo):
            errors.append("repo queue segment must use a stable repository slug")
        if not TASK_ID_PATTERN.match(task_id):
            errors.append("repo queue task id must be stable and collision-resistant")
        if not errors:
            accepted_location = "active_repository_queue"
    elif len(parts) >= 6 and parts[:3] == ["_internal", "orchestration", "repos"] and parts[4] == "tasks":
        repo = parts[3]
        task_id = parts[5]
        if not TASK_ID_PATTERN.match(repo):
            errors.append("durable repository archive requires a stable repository slug")
        if not TASK_ID_PATTERN.match(task_id):
            errors.append("durable repository archive requires a stable task id")
        if not errors:
            accepted_location = "durable_repository_archive"
    elif len(parts) >= 6 and parts[:5] == ["_internal", "orchestration", "cross-repo", "tasks", parts[4]]:
        task_id = parts[4]
        if not TASK_ID_PATTERN.match(task_id):
            errors.append("durable cross-repo archive requires a stable task id")
        if not errors:
            accepted_location = "durable_cross_repo_archive"
    elif len(parts) >= 5 and parts[:3] == ["_internal", "logs", "agents"]:
        accepted_location = "agent_execution_log"
    else:
        errors.append("destination is not an accepted Hermes artifact location")

    return {
        "schema_version": "hermes.artifact_destination.v1",
        "generated_at": now_iso(),
        "path": str(path),
        "relative_path": rel,
        "status": "ARTIFACT_DESTINATION_ACCEPTED" if not errors else "ARTIFACT_DESTINATION_REJECTED",
        "accepted_location": accepted_location,
        "errors": errors,
    }


def build_artifact_manifest(
    task_id: str,
    repositories: list[str],
    archive_root: Path,
    copied_files: list[dict[str, str]] | None = None,
    validation_disposition: str = "",
) -> dict[str, Any]:
    namespace_kind, namespace_path = artifact_namespace(repositories)
    task_root = archive_root / namespace_path / "tasks" / task_id
    return {
        "schema_version": "hermes.artifact_manifest.v1",
        "generated_at": now_iso(),
        "task_id": task_id,
        "repositories": sorted({repo for repo in repositories if repo}),
        "namespace": namespace_kind,
        "archive_root": str(archive_root),
        "task_root": str(task_root),
        "active_queue_semantics": "copied_not_moved",
        "validation_disposition": validation_disposition,
        "artifacts": copied_files or [],
    }


def validation_disposition(validation_path: Path) -> str:
    if not validation_path.exists():
        return ""
    if validation_path.suffix == ".json":
        try:
            data = json.loads(read_text(validation_path))
        except json.JSONDecodeError:
            return ""
        return data.get("verified_disposition") or data.get("status") or ""
    text = read_text(validation_path)
    match = re.search(r"verified[_ -]disposition\s*:\s*`?([A-Z_]+)`?", text, re.IGNORECASE)
    return match.group(1).upper() if match else ""


def archive_task_artifacts(
    task_id: str,
    repositories: list[str],
    packet_path: Path,
    report_path: Path,
    validation_path: Path,
    archive_root: Path,
    log_path: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    errors: list[str] = []
    if not TASK_ID_PATTERN.match(task_id):
        errors.append("task_id must be stable and contain only letters, numbers, dots, underscores, or hyphens")
    for role, path in {
        "task_packet": packet_path,
        "execution_report": report_path,
        "validation_report": validation_path,
        **({"execution_log": log_path} if log_path else {}),
    }.items():
        if path and not path.exists():
            errors.append(f"{role} does not exist: {path}")
    disposition = validation_disposition(validation_path)
    if disposition not in ACCEPTED_VALIDATION_DISPOSITIONS:
        errors.append(f"validation disposition is not archivable: {disposition or 'UNKNOWN'}")
    try:
        manifest = build_artifact_manifest(task_id, repositories, archive_root, validation_disposition=disposition)
    except ValueError as exc:
        errors.append(str(exc))
        manifest = {
            "schema_version": "hermes.artifact_manifest.v1",
            "generated_at": now_iso(),
            "task_id": task_id,
            "repositories": repositories,
            "artifacts": [],
        }
    task_root = Path(manifest.get("task_root", archive_root / "invalid"))
    manifest_path = task_root / "manifest.json"
    if task_root.exists() and not dry_run:
        errors.append(f"archive task root already exists: {task_root}")
    if errors:
        manifest.update({
            "status": "ARCHIVE_BLOCKED",
            "errors": errors,
            "files_copied": [],
            "manifest_path": str(manifest_path),
        })
        return manifest

    sources = [
        ("task_packet", packet_path),
        ("execution_report", report_path),
        ("validation_report", validation_path),
    ]
    if log_path:
        sources.append(("execution_log", log_path))
    copied: list[dict[str, str]] = []
    for role, source in sources:
        destination = task_root / artifact_archive_name(role, source)
        copied.append({
            "role": role,
            "source": str(source),
            "destination": str(destination),
            "sha256": sha256_file(source),
        })
    manifest = build_artifact_manifest(task_id, repositories, archive_root, copied, disposition)
    manifest.update({
        "status": "ARCHIVE_DRY_RUN" if dry_run else "ARCHIVED",
        "manifest_path": str(manifest_path),
        "files_copied": [] if dry_run else [item["destination"] for item in copied] + [str(manifest_path)],
    })
    if not dry_run:
        task_root.mkdir(parents=True, exist_ok=False)
        for item in copied:
            shutil.copy2(item["source"], item["destination"])
        task_alias = task_root / "task.md"
        shutil.copy2(packet_path, task_alias)
        final_path = task_root / "final-report.md"
        final_path.write_text(
            "# Canonical Final Report\n\n"
            f"**Task:** `{task_id}`  \n"
            f"**Disposition:** `{disposition}`  \n"
            f"**Repository scope:** `{', '.join(sorted(set(repositories)))}`\n\n"
            "## Summary\n\n"
            "This durable entrypoint preserves the completed task's sealed evidence. "
            "The execution report remains the detailed executor account; the validation "
            "report is the independent disposition.\n\n"
            "## Detailed evidence\n\n"
            f"- Task packet source: `{packet_path.resolve()}`\n"
            f"- Execution report source: `{report_path.resolve()}`\n"
            f"- Validation source: `{validation_path.resolve()}`\n"
            + (f"- Execution log source: `{log_path.resolve()}`\n" if log_path else "")
            + "- Archived copies: `task.md`, `execution-report.md`, `validation-report.*`, "
              "and `execution-log.*` when present.\n"
        )
        (task_root / "README.md").write_text(
            f"# Task index — {task_id}\n\n"
            "- [Canonical final report](final-report.md)\n"
            "- [Task packet](task.md)\n"
            "- [Execution report](execution-report.md)\n"
            "- [Archive manifest](manifest.json)\n",
            encoding="utf-8",
        )
        write_json(manifest_path, manifest)
    return manifest


def canonical_repo_slug(value: str) -> str:
    return value.strip().replace("_", "-")


def control_record_for_slug(slug: str) -> tuple[Path, dict[str, Any], str]:
    canonical = canonical_repo_slug(slug)
    control_path = Path(REPO_ROOT) / "repos" / canonical / "CONTROL.md"
    if not control_path.exists():
        return control_path, {}, ""
    text = read_text(control_path)
    return control_path, extract_frontmatter(text), text


def summarize_git_state(repo: Path) -> dict[str, Any]:
    context = resolve_repository_context(repo)
    upstream = run_git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    upstream_name = upstream["stdout"] if upstream["returncode"] == 0 else ""
    upstream_counts = run_git(repo, "rev-list", "--left-right", "--count", f"HEAD...{upstream_name}") if upstream_name else {"returncode": 1, "stdout": "", "stderr": ""}
    status_text = context.get("git", {}).get("status_short_branch", "")
    dirty = context.get("dirty_state", [])
    staged = [item for item in dirty if item.get("status") == "staged" or item.get("status") == "staged-and-modified"]
    unstaged = [item for item in dirty if item.get("status") in {"modified", "deleted", "staged-and-modified"}]
    untracked = [item for item in dirty if item.get("status") == "untracked"]
    return {
        "branch": context.get("git", {}).get("branch", ""),
        "head": context.get("git", {}).get("head", ""),
        "remotes": context.get("git", {}).get("remotes", ""),
        "upstream": upstream_name,
        "tracking_state": "tracking" if upstream_name else "no_upstream",
        "ahead_behind_upstream": upstream_counts["stdout"] if upstream_counts["returncode"] == 0 else None,
        "divergence": context.get("git", {}).get("divergence", {}),
        "status_short_branch": status_text,
        "clean": not dirty,
        "dirty_count": len(dirty),
        "staged_count": len(staged),
        "unstaged_count": len(unstaged),
        "untracked_count": len(untracked),
        "dirty_state": dirty,
        "observed_changes_assessment": (
            "pre_existing_or_operator_work; intake is read-only and did not create or modify target repository files"
            if dirty
            else "no tracked or untracked changes observed during intake"
        ),
    }


def document_record(repo: Path, relative_path: str, role: str, authoritative_if_present: bool = False) -> dict[str, Any]:
    path = repo / relative_path
    exists = path.exists()
    record: dict[str, Any] = {
        "role": role,
        "relative_path": relative_path,
        "exists": exists,
        "authority": "candidate" if exists and authoritative_if_present else "evidence_only",
    }
    if exists and path.is_file():
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            text = ""
        record.update({
            "sha256": sha256_text(text) if text else "",
            "line_count": len(text.splitlines()) if text else 0,
            "status_markers": status_markers(text),
        })
    return record


def status_markers(text: str) -> list[str]:
    markers = []
    lowered = text.lower()
    for label, needles in {
        "blocked": ["blocked", "blocker", "stop condition"],
        "todo": ["todo", "next task", "next authorized"],
        "roadmap": ["roadmap", "milestone", "phase"],
        "handoff": ["handoff", "session", "journal"],
        "deployment": ["deploy", "systemd", "vps"],
        "recovery": ["backup", "restore", "rollback", "recovery"],
        "human_decision": ["buddy decides", "pending", "human gate", "requires buddy"],
    }.items():
        if any(needle in lowered for needle in needles):
            markers.append(label)
    return sorted(set(markers))


def discover_repository_documents(repo: Path) -> dict[str, Any]:
    core_docs = [
        document_record(repo, "CONTROL.md", "repository_local_control", True),
        document_record(repo, "ROADMAP.md", "roadmap", True),
        document_record(repo, "TODO.md", "todo", False),
        document_record(repo, "README.md", "readme", True),
        document_record(repo, "AGENTS.md", "agent_instructions", True),
        document_record(repo, "_internal/README.md", "internal_readme", False),
        document_record(repo, "internal/README.md", "legacy_internal_readme", False),
    ]
    patterns = [
        ("operating", "OPERATING"),
        ("deployment", "DEPLOY"),
        ("recovery", "RECOVER"),
        ("handoff", "HANDOFF"),
        ("status", "STATUS"),
        ("session", "SESSION"),
    ]
    discovered: list[dict[str, Any]] = []
    for path in list(repo.glob("*.md")) + list((repo / "docs").glob("*.md")) if (repo / "docs").exists() else list(repo.glob("*.md")):
        try:
            rel = str(path.relative_to(repo))
        except ValueError:
            continue
        upper = path.name.upper()
        for role, needle in patterns:
            if needle in upper and rel not in {doc["relative_path"] for doc in core_docs}:
                discovered.append(document_record(repo, rel, role, False))
                break
    return {
        "core_documents": core_docs,
        "operational_documents": sorted(discovered, key=lambda item: item["relative_path"]),
    }


def derive_intake_findings(control: dict[str, Any], control_text: str, docs: dict[str, Any], git_state: dict[str, Any], identity_errors: list[str]) -> dict[str, Any]:
    hermes_scope = nested_get(control, ["hermes", "scope"], "")
    blockers = nested_get(control, ["roadmap", "blockers"], []) or []
    buddy_decisions = nested_get(control, ["buddy_decisions"], []) or []
    next_task = nested_get(control, ["roadmap", "next_task"], "") or extract_section(control_text, "Next Authorized Work").strip()
    docs_by_role = {doc["role"]: doc for doc in docs["core_documents"]}
    continuation_blockers: list[str] = []
    if identity_errors:
        continuation_blockers.extend(identity_errors)
    if hermes_scope == "none":
        continuation_blockers.append("control record declares Hermes scope none")
    if blockers:
        continuation_blockers.extend([str(item) for item in blockers])
    if git_state.get("dirty_count"):
        continuation_blockers.append("dirty or untracked state protects repository from write work until disposition")
    if not docs.get("inspection_skipped") and not docs_by_role.get("roadmap", {}).get("exists"):
        continuation_blockers.append("roadmap missing; do not infer implementation direction")
    suitability = {
        "read_only_analysis": "no" if hermes_scope == "none" or identity_errors else "yes",
        "bounded_documentation_work": "requires_human_authorization" if hermes_scope != "none" and not identity_errors else "no",
        "delegated_implementation": "no" if continuation_blockers else "requires_new_task_packet_and_clean_write_boundary",
        "vps_onboarding_or_deployment": "no_without_gate",
    }
    recommended: list[str] = []
    if identity_errors:
        recommended.append("resolve repository identity/control-record mismatch before any intake-dependent work")
    if hermes_scope == "none":
        recommended.append("do not inspect or delegate until Buddy changes Hermes scope")
    if buddy_decisions:
        recommended.append("collect Buddy decision for pending control-record decisions")
    if next_task:
        recommended.append(f"review control-record next task: {next_task}")
    if git_state.get("dirty_count"):
        recommended.append("classify dirty, staged, unstaged, and untracked files before any write task")
    return {
        "roadmap_status": "present" if docs_by_role.get("roadmap", {}).get("exists") else "missing",
        "todo_status": "present_evidence_only" if docs_by_role.get("todo", {}).get("exists") else "missing",
        "unresolved_human_decisions": buddy_decisions,
        "obvious_blockers": continuation_blockers,
        "suitability": suitability,
        "recommended_next_bounded_tasks": recommended,
        "missing_or_contradictory_evidence": missing_or_contradictory_evidence(control, docs, git_state),
    }


def missing_or_contradictory_evidence(control: dict[str, Any], docs: dict[str, Any], git_state: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if docs.get("inspection_skipped"):
        issues.append("repository documents were not inspected because intake stopped at control-record boundary")
        return issues
    docs_by_role = {doc["role"]: doc for doc in docs["core_documents"]}
    if not docs_by_role.get("readme", {}).get("exists"):
        issues.append("README.md missing")
    if not docs_by_role.get("agent_instructions", {}).get("exists"):
        issues.append("AGENTS.md missing")
    if not docs_by_role.get("roadmap", {}).get("exists"):
        issues.append("ROADMAP.md missing")
    expected_remote = nested_get(control, ["repository", "remote"])
    if expected_remote and expected_remote not in (git_state.get("remotes") or ""):
        issues.append("configured remotes do not include control-record remote")
    if nested_get(control, ["repository", "remote"]) is None:
        issues.append("control record has no canonical remote")
    if git_state.get("untracked_count"):
        issues.append("untracked files exist and may contain important unreviewed work")
    return issues


def render_intake_report(intake: dict[str, Any]) -> str:
    repo = intake.get("repository", {})
    findings = intake.get("findings", {})
    git_state = intake.get("git_state", {})
    docs = intake.get("documents", {})
    lines = [
        f"# Repository Intake Report — {repo.get('slug')}",
        "",
        f"- **Status:** {intake.get('status')}",
        f"- **Task ID:** {intake.get('task_id')}",
        f"- **Path:** `{repo.get('path') or 'not inspected'}`",
        f"- **Control record:** `{repo.get('control_record', {}).get('path')}`",
        f"- **Branch:** `{git_state.get('branch', '')}`",
        f"- **HEAD:** `{git_state.get('head', '')}`",
        f"- **Clean:** {git_state.get('clean')}",
        f"- **Dirty/staged/unstaged/untracked:** {git_state.get('dirty_count', 0)} / {git_state.get('staged_count', 0)} / {git_state.get('unstaged_count', 0)} / {git_state.get('untracked_count', 0)}",
        "",
        "## What Hermes Knows",
        "",
        f"- Registry/control record match: {repo.get('control_record', {}).get('match_status')}",
        f"- Hermes scope: {repo.get('hermes_scope') or 'unknown'}",
        f"- Roadmap status: {findings.get('roadmap_status')}",
        f"- TODO status: {findings.get('todo_status')}",
        "",
        "## Documents Checked",
        "",
    ]
    for doc in docs.get("core_documents", []):
        lines.append(f"- `{doc['relative_path']}`: {'present' if doc['exists'] else 'missing'} ({doc['role']})")
    for doc in docs.get("operational_documents", []):
        lines.append(f"- `{doc['relative_path']}`: present ({doc['role']})")
    lines.extend(["", "## Blockers And Decisions", ""])
    for item in findings.get("obvious_blockers", []) or ["none identified for read-only intake"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Missing Or Contradictory Evidence", ""])
    for item in findings.get("missing_or_contradictory_evidence", []) or ["none identified"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Suitability", ""])
    for key, value in findings.get("suitability", {}).items():
        lines.append(f"- **{key}:** {value}")
    lines.extend(["", "## Recommended Next Bounded Tasks", ""])
    for item in findings.get("recommended_next_bounded_tasks", []) or ["none"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def intake_repository(repo_arg: str | None, path_arg: str | None, task_id: str | None = None, archive_root: Path | None = None) -> dict[str, Any]:
    if not repo_arg and not path_arg:
        raise ValueError("provide --repo, --path, or both")
    inferred_slug = canonical_repo_slug(repo_arg) if repo_arg else canonical_repo_slug(Path(path_arg or "").name)
    control_path, control, control_text = control_record_for_slug(inferred_slug)
    errors: list[str] = []
    if not control:
        errors.append("control record not found in active control plane")
    control_slug = nested_get(control, ["repository", "slug"], inferred_slug) if control else inferred_slug
    slug = canonical_repo_slug(str(control_slug))
    expected_path = nested_get(control, ["repository", "local_path"]) if control else None
    selected_path = Path(path_arg or expected_path or "").expanduser() if (path_arg or expected_path) else None
    hermes_scope = nested_get(control, ["hermes", "scope"], "") if control else ""
    identity_errors: list[str] = []
    if control and slug != inferred_slug:
        identity_errors.append(f"requested slug {inferred_slug} differs from control-record slug {slug}")
    if control and path_arg and expected_path and Path(path_arg).expanduser().resolve() != Path(expected_path).expanduser().resolve():
        identity_errors.append("provided path differs from control-record local_path")
    if identity_errors:
        errors.extend(identity_errors)
    blocked_before_repo = bool(errors) or hermes_scope == "none"
    path_exists = bool(selected_path and selected_path.exists())
    if selected_path and not path_exists and hermes_scope != "none":
        errors.append("repository path does not exist")
        blocked_before_repo = True
    git_state: dict[str, Any] = {
        "branch": "",
        "head": "",
        "remotes": "",
        "divergence": {},
        "status_short_branch": "",
        "clean": None,
        "dirty_count": 0,
        "staged_count": 0,
        "unstaged_count": 0,
        "untracked_count": 0,
        "dirty_state": [],
        "observed_changes_assessment": "not inspected because intake blocked before repository access",
    }
    docs: dict[str, Any] = {"core_documents": [], "operational_documents": [], "inspection_skipped": blocked_before_repo}
    if not blocked_before_repo and selected_path:
        git_state = summarize_git_state(selected_path)
        docs = discover_repository_documents(selected_path)
        docs["inspection_skipped"] = False
    findings = derive_intake_findings(control, control_text, docs, git_state, identity_errors)
    status = "INTAKE_COMPLETE"
    if hermes_scope == "none":
        status = "RESTRICTED"
    elif errors:
        status = "AUTHORITY_UNRESOLVED" if "control record not found in active control plane" in errors else "IDENTITY_CONFLICT"
    result = {
        "schema_version": "hermes.repository_intake.v1",
        "generated_at": now_iso(),
        "task_id": task_id,
        "status": status,
        "mode": "read_only",
        "repository": {
            "requested": repo_arg,
            "slug": slug,
            "path": str(selected_path) if selected_path else "",
            "path_exists": path_exists,
            "control_record": {
                "path": str(control_path),
                "exists": bool(control),
                "match_status": "matched" if control and not identity_errors else "unresolved",
                "sha256": sha256_text(control_text) if control_text else "",
            },
            "control_remote": nested_get(control, ["repository", "remote"]),
            "control_default_branch": nested_get(control, ["repository", "default_branch"]),
            "control_approved_sha": nested_get(control, ["repository", "approved_sha"]),
            "hermes_scope": hermes_scope,
        },
        "git_state": git_state,
        "documents": docs,
        "findings": findings,
        "errors": errors,
        "write_actions_performed": [],
    }
    result["human_report"] = render_intake_report(result)
    if archive_root and task_id:
        result["archive"] = write_intake_archive(result, archive_root)
    return result


def write_intake_archive(intake: dict[str, Any], archive_root: Path) -> dict[str, Any]:
    task_id = intake.get("task_id")
    if not task_id or not TASK_ID_PATTERN.match(task_id):
        return {"status": "ARCHIVE_BLOCKED", "errors": ["valid stable task_id is required for intake archive"], "files_written": []}
    repo_slug = intake.get("repository", {}).get("slug", "")
    manifest = build_artifact_manifest(task_id, [repo_slug], archive_root)
    task_root = Path(manifest["task_root"])
    if task_root.exists():
        return {"status": "ARCHIVE_BLOCKED", "errors": [f"archive task root already exists: {task_root}"], "files_written": []}
    task_root.mkdir(parents=True, exist_ok=False)
    json_path = task_root / "intake.json"
    report_path = task_root / "intake-report.md"
    report_text = intake.get("human_report", "")
    json_payload = dict(intake)
    json_payload.pop("archive", None)
    write_json(json_path, json_payload)
    report_path.write_text(report_text, encoding="utf-8")
    artifacts = [
        {"role": "intake_json", "source": "generated", "destination": str(json_path), "sha256": sha256_file(json_path)},
        {"role": "intake_report", "source": "generated", "destination": str(report_path), "sha256": sha256_file(report_path)},
    ]
    archive_manifest = build_artifact_manifest(task_id, [repo_slug], archive_root, artifacts, intake.get("status", ""))
    archive_manifest.update({
        "status": "ARCHIVED",
        "manifest_path": str(task_root / "manifest.json"),
        "files_copied": [str(json_path), str(report_path), str(task_root / "manifest.json")],
    })
    write_json(task_root / "manifest.json", archive_manifest)
    return archive_manifest


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hermes orchestration planning tools")
    sub = parser.add_subparsers(dest="command", required=True)

    ctx = sub.add_parser("context")
    ctx.add_argument("--repo", required=True)
    ctx.add_argument("--slug")
    ctx.add_argument("--control")
    ctx.add_argument("--out")

    rm = sub.add_parser("roadmap")
    rm.add_argument("--roadmap", required=True)
    rm.add_argument("--out")

    plan = sub.add_parser("plan")
    plan.add_argument("--intent", required=True)
    plan.add_argument("--context", required=True)
    plan.add_argument("--roadmap", required=True)
    plan.add_argument("--authority-resolution", required=True)
    plan.add_argument("--out-dir")
    plan.add_argument("--dry-run", action="store_true", help="Print draft packet and eligibility without writing files")

    auth = sub.add_parser("authority-resolve")
    auth.add_argument("--candidate", action="append", required=True, help="Candidate as slug=path")
    auth.add_argument("--preferred-active")
    auth.add_argument("--out")

    rank = sub.add_parser("rank-repositories")
    rank.add_argument("--intent", required=True)
    rank.add_argument("--context", action="append", required=True)
    rank.add_argument("--authority-resolution", required=True)
    rank.add_argument("--out")

    rs = sub.add_parser("run-state")
    rs.add_argument("--intent", required=True)
    rs.add_argument("--state", default="DISPATCH")
    rs.add_argument("--artifact", action="append", default=[])
    rs.add_argument("--dispatch-task")
    rs.add_argument("--dispatch-report")
    rs.add_argument("--out", required=True)

    rec = sub.add_parser("reconstruct")
    rec.add_argument("--run-state", required=True)
    rec.add_argument("--out")

    mem = sub.add_parser("memory-status")
    mem.add_argument("--source", required=True)
    mem.add_argument("--live", required=True)
    mem.add_argument("--out")

    diag = sub.add_parser("runtime-diagnostic")
    diag.add_argument("--source", default=str(Path(REPO_ROOT) / "agents" / "hermes-memory" / "MEMORY.md"))
    diag.add_argument("--live", default=str(Path.home() / ".hermes" / "memories" / "MEMORY.md"))
    diag.add_argument("--canonical", default=str(Path.home() / ".local" / "bin" / "hermes"))
    diag.add_argument("--alternate", default=str(Path.home() / ".hermes" / "hermes-agent" / "hermes"))
    diag.add_argument("--backup")
    diag.add_argument("--out")

    ver = sub.add_parser("verify")
    ver.add_argument("--packet", required=True)
    ver.add_argument("--report", required=True)
    ver.add_argument("--repo", required=True)
    ver.add_argument("--allowed-path", action="append", default=[])
    ver.add_argument("--out")

    archive = sub.add_parser("archive-task")
    archive.add_argument("--task-id", required=True)
    archive.add_argument("--repo", action="append", required=True, help="Managed repository slug; repeat for cross-repo tasks")
    archive.add_argument("--packet", required=True)
    archive.add_argument("--report", required=True)
    archive.add_argument("--validation", required=True)
    archive.add_argument("--log")
    archive.add_argument("--archive-root", default=str(Path(REPO_ROOT) / "_internal" / "orchestration"))
    archive.add_argument("--dry-run", action="store_true")
    archive.add_argument("--out")

    dest = sub.add_parser("validate-artifact-destination")
    dest.add_argument("--path", required=True)
    dest.add_argument("--out")

    intake = sub.add_parser("intake-repository")
    intake.add_argument("--repo", help="Managed repository slug")
    intake.add_argument("--path", help="Repository checkout path")
    intake.add_argument("--task-id", help="Stable intake task identifier; required with --archive-root")
    intake.add_argument("--archive-root", help="Durable archive root for intake bundle")
    intake.add_argument("--json-out")
    intake.add_argument("--report-out")
    return parser


def emit(data: dict[str, Any], out: str | None) -> None:
    if out:
        write_json(Path(out), data)
    print(json.dumps(data, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "context":
        emit(resolve_repository_context(Path(args.repo), args.slug, Path(args.control) if args.control else None), args.out)
    elif args.command == "roadmap":
        emit(parse_roadmap(Path(args.roadmap)), args.out)
    elif args.command == "plan":
        intent = normalize_intent(load_json(Path(args.intent)))
        context = load_json(Path(args.context))
        roadmap = load_json(Path(args.roadmap))
        authority = load_json(Path(args.authority_resolution))
        ok, errors, status = validate_authority_resolution(authority)
        if not ok:
            emit(
                {
                    "schema_version": "hermes.plan.v1",
                    "generated_at": now_iso(),
                    "status": status,
                    "errors": errors,
                    "files_written": [],
                },
                None,
            )
            return 2
        eligibility = analyze_eligibility(intent, context, roadmap)
        packet = author_packet(intent, context, roadmap, eligibility)
        if args.dry_run:
            emit(
                {
                    "schema_version": "hermes.plan.v1",
                    "generated_at": now_iso(),
                    "status": "AUTHORITY_RESOLVED",
                    "active_control_plane": authority.get("active_control_plane"),
                    "intent": intent,
                    "eligibility": eligibility,
                    "draft_packet": packet,
                    "files_written": [],
                },
                None,
            )
        else:
            if not args.out_dir:
                raise SystemExit("--out-dir is required unless --dry-run is used")
            out_dir = Path(args.out_dir)
            write_json(out_dir / "intent.normalized.json", intent)
            write_json(out_dir / "eligibility.json", eligibility)
            (out_dir / "packet.md").write_text(packet, encoding="utf-8")
            emit(
                {
                    "schema_version": "hermes.plan.v1",
                    "generated_at": now_iso(),
                    "status": "AUTHORITY_RESOLVED",
                    "active_control_plane": authority.get("active_control_plane"),
                    "intent": intent,
                    "eligibility": eligibility,
                    "packet": str((out_dir / "packet.md").resolve()),
                },
                None,
            )
    elif args.command == "authority-resolve":
        candidates = []
        for item in args.candidate:
            if "=" not in item:
                raise SystemExit("--candidate must use slug=path")
            slug, path = item.split("=", 1)
            candidates.append({"slug": slug, "path": path})
        emit(resolve_authority(candidates, args.preferred_active), args.out)
    elif args.command == "rank-repositories":
        intent = normalize_intent(load_json(Path(args.intent)))
        contexts = [load_json(Path(path)) for path in args.context]
        authority = load_json(Path(args.authority_resolution))
        result = rank_repositories(intent, contexts, authority)
        emit(result, args.out)
        if result.get("status") != "AUTHORITY_RESOLVED":
            return 2
    elif args.command == "run-state":
        intent = normalize_intent(load_json(Path(args.intent)))
        artifacts = dict(item.split("=", 1) for item in args.artifact)
        dispatch = None
        if args.dispatch_task or args.dispatch_report:
            dispatch = {"task_packet": args.dispatch_task, "expected_report": args.dispatch_report, "recorded_at": now_iso()}
        emit(create_run_state(intent, args.state, artifacts, dispatch), args.out)
    elif args.command == "reconstruct":
        emit(reconstruct_run_state(Path(args.run_state)), args.out)
    elif args.command == "memory-status":
        emit(memory_status(Path(args.source), Path(args.live)), args.out)
    elif args.command == "runtime-diagnostic":
        emit(
            runtime_diagnostic(
                Path(args.source),
                Path(args.live),
                Path(args.canonical),
                Path(args.alternate),
                Path(args.backup) if args.backup else None,
            ),
            args.out,
        )
    elif args.command == "verify":
        emit(verify_report(Path(args.packet), Path(args.report), Path(args.repo), args.allowed_path), args.out)
    elif args.command == "archive-task":
        result = archive_task_artifacts(
            args.task_id,
            args.repo,
            Path(args.packet),
            Path(args.report),
            Path(args.validation),
            Path(args.archive_root),
            Path(args.log) if args.log else None,
            args.dry_run,
        )
        emit(result, args.out)
        if result.get("status") == "ARCHIVE_BLOCKED":
            return 2
    elif args.command == "validate-artifact-destination":
        result = validate_artifact_destination(Path(args.path))
        emit(result, args.out)
        if result.get("status") == "ARTIFACT_DESTINATION_REJECTED":
            return 2
    elif args.command == "intake-repository":
        if args.archive_root and not args.task_id:
            print(json.dumps({
                "schema_version": "hermes.repository_intake.v1",
                "generated_at": now_iso(),
                "status": "AUTHORITY_UNRESOLVED",
                "errors": ["--task-id is required when --archive-root is supplied"],
            }, indent=2, sort_keys=True))
            return 2
        result = intake_repository(
            args.repo,
            args.path,
            args.task_id,
            Path(args.archive_root) if args.archive_root else None,
        )
        if args.json_out:
            write_json(Path(args.json_out), result)
        if args.report_out:
            report_path = Path(args.report_out)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(result.get("human_report", ""), encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        if result.get("status") in INTAKE_BLOCKED_STATUSES:
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
