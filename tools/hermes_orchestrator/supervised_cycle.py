"""Fail-closed state helpers for one supervised maker/checker cycle.

This module never publishes, merges, deploys, or grants authority.  Callers
persist each returned state before the corresponding external side effect.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import os
import subprocess

STATES = {"initialize", "establish_baseline", "claim", "provision_isolated_worktree", "dispatch_maker", "seal_submission", "run_independent_checker", "pass", "precise_revision", "stop_escalate", "integrate", "suspend", "reconcile_clean_state"}
DECISION_STATES = {"identified", "preparation_required", "preparation_in_progress", "ready_for_review", "under_review", "supplemental_evidence_required", "decided", "deferred", "superseded", "invalidated"}

def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def new_cycle(run_id: str, base_sha: str, allowed_paths: list[str], denied_paths: list[str], authority: Any, acceptance: Any, budget: dict[str, int]) -> dict[str, Any]:
    if not run_id or not base_sha or not allowed_paths or budget.get("max_attempts", 0) < 1:
        raise ValueError("run_id, base_sha, allowed_paths, and positive max_attempts are required")
    state = {"schema_version": "hermes.supervised_cycle.v1", "run_id": run_id, "state": "initialize", "immutable_contract": {"base_sha": base_sha, "allowed_paths": sorted(set(allowed_paths)), "denied_paths": sorted(set(denied_paths)), "authority_digest": digest(authority), "acceptance_digest": digest(acceptance)}, "baseline": {}, "attempts": [], "budget": {"max_attempts": budget["max_attempts"], "max_identical_failures": budget.get("max_identical_failures", 1), "max_units": budget.get("max_units", 0), "used_units": 0}, "events": []}
    return transition(state, "initialize", "cycle created")

def transition(state: dict[str, Any], target: str, reason: str, **data: Any) -> dict[str, Any]:
    if target not in STATES: raise ValueError("invalid cycle state")
    out = deepcopy(state); out["state"] = target
    out["events"].append({"at": now(), "state": target, "reason": reason, "data": data, "digest": digest({"target": target, "reason": reason, "data": data, "prior": digest(state.get("events", []))})})
    return out

def establish_baseline(state: dict[str, Any], repository: str, head: str, dirty_paths: list[str], evidence: Any) -> dict[str, Any]:
    if state["state"] not in {"initialize", "establish_baseline"}: raise ValueError("baseline is not currently permitted")
    if head != state["immutable_contract"]["base_sha"] or dirty_paths: return transition(state, "stop_escalate", "baseline contradicts pinned clean base", head=head, dirty_paths=dirty_paths)
    out = deepcopy(state); out["baseline"] = {"repository": repository, "head": head, "dirty_paths": [], "evidence_digest": digest(evidence)}
    return transition(out, "claim", "clean pinned baseline recorded")

def claim_attempt(state: dict[str, Any], maker: str, contract: dict[str, Any], units: int = 0) -> dict[str, Any]:
    if state["state"] not in {"claim", "precise_revision"}: raise ValueError("attempt claim is not currently permitted")
    if digest(contract.get("authority")) != state["immutable_contract"]["authority_digest"] or digest(contract.get("acceptance")) != state["immutable_contract"]["acceptance_digest"] or contract.get("base_sha") != state["immutable_contract"]["base_sha"] or sorted(contract.get("allowed_paths", [])) != state["immutable_contract"]["allowed_paths"] or sorted(contract.get("denied_paths", [])) != state["immutable_contract"]["denied_paths"]: return transition(state, "stop_escalate", "immutable contract changed")
    budget = state["budget"]
    if len(state["attempts"]) >= budget["max_attempts"] or (budget["max_units"] and budget["used_units"] + units > budget["max_units"]): return transition(state, "stop_escalate", "attempt or budget limit exhausted")
    out = deepcopy(state); out["budget"]["used_units"] += units; out["attempts"].append({"attempt": len(out["attempts"]) + 1, "maker": maker, "submission_digest": None, "checker": None, "result": "claimed"})
    return transition(out, "provision_isolated_worktree", "attempt claimed", maker=maker)

def seal_submission(state: dict[str, Any], maker: str, changed_paths: list[str], evidence: Any) -> dict[str, Any]:
    if state["state"] not in {"dispatch_maker", "seal_submission"}: raise ValueError("submission is not currently permitted")
    if not state["attempts"] or state["attempts"][-1]["maker"] != maker: return transition(state, "stop_escalate", "unknown maker submission")
    allowed, denied = state["immutable_contract"]["allowed_paths"], state["immutable_contract"]["denied_paths"]
    invalid = [p for p in changed_paths if p in denied or not any(p == root or p.startswith(root.rstrip("/") + "/") for root in allowed)]
    if invalid: return transition(state, "stop_escalate", "path manifest violation", paths=invalid)
    out = deepcopy(state); out["attempts"][-1].update({"submission_digest": digest({"paths": sorted(changed_paths), "evidence": evidence}), "changed_paths": sorted(changed_paths), "result": "sealed"})
    return transition(out, "run_independent_checker", "maker submission sealed")

def provision_worktree(state: dict[str, Any], repository: Path, worktree: Path, branch: str, lease: Path) -> dict[str, Any]:
    """Provision one isolated worktree after persisting the claim.

    The lease is exclusive and is deliberately never removed by this helper;
    reconciliation owns release after a terminal recorded state.
    """
    if state["state"] != "provision_isolated_worktree": raise ValueError("worktree is not currently permitted")
    if lease.exists() or worktree.exists(): return transition(state, "stop_escalate", "worktree or task lease already exists")
    try:
        lease.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(lease, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, digest({"run": state["run_id"], "base": state["immutable_contract"]["base_sha"]}).encode()); os.close(fd)
        proc = subprocess.run(["git", "worktree", "add", "--detach", str(worktree), state["immutable_contract"]["base_sha"]], cwd=repository, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except OSError as exc:
        return transition(state, "stop_escalate", "unable to acquire task lease", error=str(exc))
    if proc.returncode:
        return transition(state, "stop_escalate", "worktree provisioning failed", error=proc.stderr.strip())
    return transition(state, "dispatch_maker", "isolated worktree provisioned", worktree=str(worktree), branch=branch, lease=str(lease))

def reconcile(state: dict[str, Any], worktree_exists: bool, lease_exists: bool, repository_head: str) -> dict[str, Any]:
    """Fail closed if the recorded terminal outcome cannot be reconciled."""
    if state["state"] not in {"pass", "stop_escalate", "integrate", "suspend", "reconcile_clean_state"}: raise ValueError("reconciliation requires a terminal or integration state")
    if repository_head != state["immutable_contract"]["base_sha"] or worktree_exists or lease_exists:
        return transition(state, "stop_escalate", "clean-state reconciliation failed", worktree_exists=worktree_exists, lease_exists=lease_exists, repository_head=repository_head)
    return transition(state, "reconcile_clean_state", "repository, worktree, lease, and base reconciled")

def check_submission(state: dict[str, Any], checker: str, evidence: Any, disposition: str, revision: list[str] | None = None) -> dict[str, Any]:
    if state["state"] != "run_independent_checker": raise ValueError("checker is not currently permitted")
    attempt = state["attempts"][-1]
    if checker == attempt["maker"]: return transition(state, "stop_escalate", "maker cannot approve own result")
    if not attempt.get("submission_digest") or digest(evidence) != attempt["submission_digest"]: return transition(state, "stop_escalate", "missing, stale, or contradictory evidence")
    if disposition not in {"pass", "precise_revision", "stop_escalate"}: return transition(state, "stop_escalate", "invalid checker disposition")
    out = deepcopy(state); out["attempts"][-1].update({"checker": checker, "result": disposition, "revision": revision or []})
    if disposition == "precise_revision":
        prior = [a for a in out["attempts"] if a.get("result") == "precise_revision" and a.get("revision") == (revision or [])]
        if len(prior) > out["budget"]["max_identical_failures"]: return transition(out, "stop_escalate", "repeated identical checker failure", revision=revision or [])
    return transition(out, disposition, "independent checker disposition", checker=checker, revision=revision or [])

def validate_decision_packet(packet: dict[str, Any]) -> list[str]:
    required = {"decision_id", "decision_type", "required_authority", "bounded_question", "reason_required", "governing_references", "affected_tasks", "state", "evidence", "options", "recommended_disposition", "safe_default", "required_response_format", "downstream_state_changes"}
    errors = [f"missing {key}" for key in sorted(required - packet.keys())]
    if packet.get("state") not in DECISION_STATES: errors.append("invalid decision lifecycle state")
    if packet.get("required_authority") not in {"buddy", "gpt", "strong_codex"}: errors.append("invalid decision authority")
    evidence = packet.get("evidence", {})
    for key in {"repository", "runtime", "semantic", "representative_samples", "high_risk_samples", "counterexamples", "uncertainties"}:
        if key not in evidence: errors.append(f"missing evidence.{key}")
    return errors
