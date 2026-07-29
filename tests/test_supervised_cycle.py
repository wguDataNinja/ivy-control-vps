import subprocess

from tools.hermes_orchestrator.supervised_cycle import (
    check_submission, claim_attempt, establish_baseline, new_cycle, reconcile,
    provision_worktree, seal_submission, validate_decision_packet,
)

AUTHORITY = {"permitted": ["bounded docs"]}
ACCEPTANCE = {"checks": ["pytest"]}
CONTRACT = {"base_sha": "abc", "allowed_paths": ["docs"], "denied_paths": ["secrets"], "authority": AUTHORITY, "acceptance": ACCEPTANCE}

def cycle():
    return new_cycle("run-1", "abc", ["docs"], ["secrets"], AUTHORITY, ACCEPTANCE, {"max_attempts": 2, "max_identical_failures": 1, "max_units": 5})

def ready():
    return claim_attempt(establish_baseline(cycle(), "repo", "abc", [], {"test": "pass"}), "maker", CONTRACT, 1)

def dispatched():
    state = ready()
    return __import__("tools.hermes_orchestrator.supervised_cycle", fromlist=["transition"]).transition(state, "dispatch_maker", "fixture")

def sealed():
    return seal_submission(dispatched(), "maker", ["docs/a.md"], {"ok": True})

def test_clean_baseline_and_immutable_contract_are_required():
    assert establish_baseline(cycle(), "repo", "wrong", [], {})["state"] == "stop_escalate"
    bad = dict(CONTRACT, base_sha="changed")
    assert claim_attempt(establish_baseline(cycle(), "repo", "abc", [], {}), "maker", bad)["state"] == "stop_escalate"

def test_dirty_and_denied_path_fail_closed():
    assert establish_baseline(cycle(), "repo", "abc", ["scratch"], {})["state"] == "stop_escalate"
    assert seal_submission(dispatched(), "maker", ["secrets/key"], {})["state"] == "stop_escalate"

def test_maker_cannot_check_and_stale_evidence_stops():
    assert check_submission(sealed(), "maker", {"paths": ["docs/a.md"], "evidence": {"ok": True}}, "pass")["state"] == "stop_escalate"
    assert check_submission(sealed(), "checker", {"wrong": True}, "pass")["state"] == "stop_escalate"

def test_checker_revision_retry_and_budget_stop():
    evidence = {"paths": ["docs/a.md"], "evidence": {"ok": True}}
    revision = check_submission(sealed(), "checker", evidence, "precise_revision", ["add a test"])
    assert revision["state"] == "precise_revision"
    exhausted = claim_attempt(establish_baseline(new_cycle("run-2", "abc", ["docs"], ["secrets"], AUTHORITY, ACCEPTANCE, {"max_attempts": 1}), "repo", "abc", [], {}), "maker", CONTRACT)
    retry_state = __import__("tools.hermes_orchestrator.supervised_cycle", fromlist=["transition"]).transition(exhausted, "precise_revision", "fixture")
    assert claim_attempt(retry_state, "maker", CONTRACT)["state"] == "stop_escalate"

def test_invalid_decision_and_restart_reconciliation():
    assert "invalid decision lifecycle state" in validate_decision_packet({"state": "nope"})
    evidence = {"paths": ["docs/a.md"], "evidence": {"ok": True}}
    passed = check_submission(sealed(), "checker", evidence, "pass")
    assert reconcile(passed, False, False, "abc")["state"] == "reconcile_clean_state"
    assert reconcile(passed, True, False, "abc")["state"] == "stop_escalate"

def test_worktree_lease_and_provisioning_are_isolated(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / "README.md").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, stdout=subprocess.PIPE)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
    state = new_cycle("run-worktree", head, ["docs"], [], AUTHORITY, ACCEPTANCE, {"max_attempts": 1})
    state = establish_baseline(state, str(repo), head, [], {})
    state = claim_attempt(state, "maker", {**CONTRACT, "base_sha": head, "denied_paths": []})
    result = provision_worktree(state, repo, tmp_path / "worktree", "ignored", tmp_path / "leases" / "run-worktree")
    assert result["state"] == "dispatch_maker"
    assert (tmp_path / "worktree").is_dir()
    assert provision_worktree(state, repo, tmp_path / "worktree", "ignored", tmp_path / "leases" / "run-worktree")["state"] == "stop_escalate"
