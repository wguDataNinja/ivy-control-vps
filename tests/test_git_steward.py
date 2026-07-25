from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from tools.git_steward.models import (
    OperationalMode,
    PublicationManifest,
    compute_manifest_digest_sha256,
    compute_tracked_file_digest_sha256,
    parse_publication_manifest,
)
from tools.git_steward.validation import validate


def _git(*args: str, cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, cwd=cwd, check=False
    )


_TEST_REMOTE = "https://github.com/test/test.git"


@pytest.fixture
def temp_repo():
    """Create a temporary git repository with files and commits."""
    tmpdir = tempfile.mkdtemp()
    _git("init", cwd=tmpdir)
    _git("config", "user.email", "test@test.com", cwd=tmpdir)
    _git("config", "user.name", "Test", cwd=tmpdir)
    _git("checkout", "-b", "main", cwd=tmpdir)
    _git("remote", "add", "origin", _TEST_REMOTE, cwd=tmpdir)

    (Path(tmpdir) / "README.md").write_text("# Test")
    _git("add", "README.md", cwd=tmpdir)
    _git("commit", "-m", "initial", cwd=tmpdir)
    initial_sha = _git("rev-parse", "HEAD", cwd=tmpdir).stdout.strip()

    _git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main", cwd=tmpdir)

    (Path(tmpdir) / "pyproject.toml").write_text("[project]\nname = 'test'")
    _git("add", "pyproject.toml", cwd=tmpdir)
    _git("commit", "-m", "add pyproject", cwd=tmpdir)
    main_head = _git("rev-parse", "HEAD", cwd=tmpdir).stdout.strip()

    _git("checkout", "-b", "publish/test-v1", cwd=tmpdir)
    (Path(tmpdir) / "src").mkdir(exist_ok=True)
    (Path(tmpdir) / "src" / "main.py").write_text("print('hello')")
    _git("add", "src/main.py", cwd=tmpdir)
    _git("commit", "-m", "add main module", cwd=tmpdir)
    candidate_sha = _git("rev-parse", "HEAD", cwd=tmpdir).stdout.strip()

    yield {
        "path": tmpdir,
        "main_head": main_head,
        "initial_sha": initial_sha,
        "candidate_sha": candidate_sha,
    }

    shutil.rmtree(tmpdir)


def _make_manifest(repo_path: str, **overrides) -> PublicationManifest:
    base = {
        "task_id": "test-task",
        "session_id": 99,
        "repository": {
            "path": repo_path,
            "remote": _TEST_REMOTE,
        },
        "expected_base_branch": "main",
        "expected_base_sha": "ffff",
        "candidate_branch": "publish/test-v1",
        "expected_candidate_head": "ffff",
        "target_pr_base": "main",
        "manifest": {
            "include_globs": ["**/*"],
            "exclude_globs": ["_internal/"],
            "max_file_size_bytes": 1048576,
            "secret_scan": True,
            "large_file_scan": True,
        },
        "approvals": {
            "branch_publication": {
                "approved": False,
                "approved_by": None,
                "approval_ref": None,
            },
            "draft_pr_creation": {
                "approved": False,
                "approved_by": None,
                "approval_ref": None,
            },
        },
        "credentials": {
            "mechanism": "gh_cli",
        },
        "evidence": {
            "output_dir": "/tmp/steward-test-evidence",
        },
    }

    def _deep_merge(base, overrides):
        result = dict(base)
        for k, v in overrides.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = _deep_merge(result[k], v)
            else:
                result[k] = v
        return result

    merged = _deep_merge(base, overrides)
    return parse_publication_manifest(merged)


def _run_validation(repo_path: str, **overrides):
    manifest = _make_manifest(repo_path, **overrides)
    return validate(manifest)


# ─── 1. Validation succeeds with both approvals false ──────────────────────────


def test_validation_succeeds_with_approvals_false(temp_repo):
    """Validate mode must succeed even when both gates are false."""
    repo = temp_repo
    result = _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    assert result.validation.passed, f"Expected PASS, errors: {result.validation.errors}"
    assert result.validation.gate1_approved is None  # validate mode doesn't check
    assert result.validation.gate2_approved is None
    assert result.mutation_status == "dry_run_only"


# ─── 2. Gate 1 true without approver fails ──────────────────────────────────────


def test_gate1_true_without_approver_fails(temp_repo):
    """approved=true without approved_by must be rejected by manifest validation."""
    repo = temp_repo
    result = validate(
        _make_manifest(
            repo["path"],
            expected_base_sha=repo["initial_sha"],
            expected_candidate_head=repo["candidate_sha"],
            approvals={
                "branch_publication": {
                    "approved": True,
                    "approved_by": None,
                    "approval_ref": "ref-1",
                },
            },
        ),
        mode=OperationalMode.PUBLISH_BRANCH,
    )
    assert not result.validation.passed
    manifest_errors = result.validation.errors
    assert any("approved_by" in e and "branch_publication" in e for e in manifest_errors)


# ─── 3. Gate 1 true without approval ref fails ──────────────────────────────────


def test_gate1_true_without_ref_fails(temp_repo):
    """approved=true without approval_ref must be rejected by manifest validation."""
    repo = temp_repo
    result = validate(
        _make_manifest(
            repo["path"],
            expected_base_sha=repo["initial_sha"],
            expected_candidate_head=repo["candidate_sha"],
            approvals={
                "branch_publication": {
                    "approved": True,
                    "approved_by": "Buddy",
                    "approval_ref": None,
                },
            },
        ),
        mode=OperationalMode.PUBLISH_BRANCH,
    )
    assert not result.validation.passed
    manifest_errors = result.validation.errors
    assert any("approval_ref" in e and "branch_publication" in e for e in manifest_errors)


# ─── 4. Gate 2 true without approver fails ──────────────────────────────────────


def test_gate2_true_without_approver_fails(temp_repo):
    """approved=true without approved_by must be rejected by manifest validation."""
    repo = temp_repo
    result = validate(
        _make_manifest(
            repo["path"],
            expected_base_sha=repo["initial_sha"],
            expected_candidate_head=repo["candidate_sha"],
            approvals={
                "draft_pr_creation": {
                    "approved": True,
                    "approved_by": None,
                    "approval_ref": "ref-2",
                },
            },
        ),
        mode=OperationalMode.CREATE_DRAFT_PR,
    )
    assert not result.validation.passed
    manifest_errors = result.validation.errors
    assert any("approved_by" in e and "draft_pr_creation" in e for e in manifest_errors)


# ─── 5. Gate 2 true without approval ref fails ──────────────────────────────────


def test_gate2_true_without_ref_fails(temp_repo):
    """approved=true without approval_ref must be rejected by manifest validation."""
    repo = temp_repo
    result = validate(
        _make_manifest(
            repo["path"],
            expected_base_sha=repo["initial_sha"],
            expected_candidate_head=repo["candidate_sha"],
            approvals={
                "draft_pr_creation": {
                    "approved": True,
                    "approved_by": "Buddy",
                    "approval_ref": None,
                },
            },
        ),
        mode=OperationalMode.CREATE_DRAFT_PR,
    )
    assert not result.validation.passed
    manifest_errors = result.validation.errors
    assert any("approval_ref" in e and "draft_pr_creation" in e for e in manifest_errors)


# ─── 6. Gate 1 does not imply Gate 2 ──────────────────────────────────────────


def test_gate1_does_not_imply_gate2(temp_repo):
    """With only Gate 1 approved, create-draft-pr mode must fail."""
    repo = temp_repo
    result = validate(
        _make_manifest(
            repo["path"],
            expected_base_sha=repo["initial_sha"],
            expected_candidate_head=repo["candidate_sha"],
            approvals={
                "branch_publication": {
                    "approved": True,
                    "approved_by": "Buddy",
                    "approval_ref": "session-99",
                },
                "draft_pr_creation": {
                    "approved": False,
                },
            },
        ),
        mode=OperationalMode.CREATE_DRAFT_PR,
    )
    assert not result.validation.passed
    assert any("ERR_GATE2_NOT_APPROVED" in e for e in result.validation.errors)


# ─── 7. Gate 2 does not imply Gate 1 ──────────────────────────────────────────


def test_gate2_does_not_imply_gate1(temp_repo):
    """With only Gate 2 approved, publish-branch mode must fail."""
    repo = temp_repo
    result = validate(
        _make_manifest(
            repo["path"],
            expected_base_sha=repo["initial_sha"],
            expected_candidate_head=repo["candidate_sha"],
            approvals={
                "branch_publication": {
                    "approved": False,
                },
                "draft_pr_creation": {
                    "approved": True,
                    "approved_by": "Buddy",
                    "approval_ref": "session-99",
                },
            },
        ),
        mode=OperationalMode.PUBLISH_BRANCH,
    )
    assert not result.validation.passed
    assert any("ERR_GATE1_NOT_APPROVED" in e for e in result.validation.errors)


# ─── 8. Publish mode fails without Gate 1 ──────────────────────────────────────


def test_publish_mode_fails_without_gate1(temp_repo):
    repo = temp_repo
    result = validate(
        _make_manifest(
            repo["path"],
            expected_base_sha=repo["initial_sha"],
            expected_candidate_head=repo["candidate_sha"],
        ),
        mode=OperationalMode.PUBLISH_BRANCH,
    )
    assert not result.validation.passed
    assert result.validation.gate1_approved is False
    assert any("ERR_GATE1_NOT_APPROVED" in e for e in result.validation.errors)


# ─── 9. Draft-PR mode fails without Gate 2 ──────────────────────────────────────


def test_draft_pr_mode_fails_without_gate2(temp_repo):
    repo = temp_repo
    result = validate(
        _make_manifest(
            repo["path"],
            expected_base_sha=repo["initial_sha"],
            expected_candidate_head=repo["candidate_sha"],
        ),
        mode=OperationalMode.CREATE_DRAFT_PR,
    )
    assert not result.validation.passed
    assert result.validation.gate2_approved is False
    assert any("ERR_GATE2_NOT_APPROVED" in e for e in result.validation.errors)


# ─── 10. Explicit full push refspec is generated ────────────────────────────────


def test_explicit_full_push_refspec(temp_repo):
    repo = temp_repo
    result = validate(
        _make_manifest(
            repo["path"],
            expected_base_sha=repo["initial_sha"],
            expected_candidate_head=repo["candidate_sha"],
            approvals={
                "branch_publication": {
                    "approved": True,
                    "approved_by": "Buddy",
                    "approval_ref": "session-99",
                },
            },
        ),
        mode=OperationalMode.PUBLISH_BRANCH,
    )
    assert result.validation.passed
    assert result.gate1 is not None
    cmd = result.gate1.push_command.command
    assert "refs/heads/" in cmd, f"expected refs/heads/ in push command, got: {cmd}"
    assert "--force" not in cmd
    assert "-f" not in cmd


# ─── 11. Upstream-to-main never determines push destination ─────────────────────


def test_upstream_to_main_does_not_affect_push(temp_repo):
    """Push command must use explicit refspec regardless of upstream."""
    repo = temp_repo
    _git("checkout", "publish/test-v1", cwd=repo["path"])
    _git(
        "config", "branch.publish/test-v1.remote", "origin", cwd=repo["path"]
    )
    _git(
        "config",
        "branch.publish/test-v1.merge",
        "refs/heads/main",
        cwd=repo["path"],
    )
    result = validate(
        _make_manifest(
            repo["path"],
            expected_base_sha=repo["initial_sha"],
            expected_candidate_head=repo["candidate_sha"],
            approvals={
                "branch_publication": {
                    "approved": True,
                    "approved_by": "Buddy",
                    "approval_ref": "session-99",
                },
            },
        ),
        mode=OperationalMode.PUBLISH_BRANCH,
    )
    assert result.validation.passed
    assert result.gate1 is not None
    cmd = result.gate1.push_command.command
    assert "refs/heads/publish/test-v1:refs/heads/publish/test-v1" in cmd
    assert ":refs/heads/main" not in cmd


# ─── 12. No bare push command is generated ──────────────────────────────────────


def test_no_bare_push_command(temp_repo):
    repo = temp_repo
    result = _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    assert result.validation.passed
    assert result.gate1 is not None
    cmd = result.gate1.push_command.command
    parts = cmd.split()
    assert len(parts) >= 4
    assert parts[0] == "git"
    assert parts[1] == "push"


# ─── 13. Explicit PR base and head are generated ────────────────────────────────


def test_explicit_pr_base_and_head(temp_repo):
    repo = temp_repo
    result = _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    assert result.validation.passed
    assert result.gate2 is not None
    cmd = result.gate2.pr_command.command
    assert "--base main" in cmd
    assert "--head publish/test-v1" in cmd
    assert "--draft" in cmd


# ─── 14. No merge mode exists ──────────────────────────────────────────────────


def test_no_merge_mode():
    """There must be no merge mode in OperationalMode."""
    assert "merge" not in OperationalMode.ALL
    assert "merge" not in str(OperationalMode.ALL)


# ─── 15. No generic ambiguous execution mode exists ─────────────────────────────


def test_no_ambiguous_execution_mode():
    """Every mode must be explicit."""
    assert OperationalMode.ALL == ("validate", "publish-branch", "create-draft-pr")


# ─── 16. Canonical SHA-256 digest is deterministic ──────────────────────────────


def test_deterministic_sha256_digest(temp_repo):
    repo = temp_repo
    manifest = _make_manifest(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    digest1 = compute_manifest_digest_sha256(manifest)
    digest2 = compute_manifest_digest_sha256(manifest)
    assert digest1 == digest2
    assert len(digest1) == 64
    assert all(c in "0123456789abcdef" for c in digest1)


# ─── 17. Key ordering does not change canonical digest ──────────────────────────


def test_key_ordering_does_not_affect_digest():
    """Two manifests with same data but different key order must produce same digest."""
    data1 = {
        "task_id": "test",
        "session_id": 1,
        "repository": {"path": "/a", "remote": "https://r.com"},
        "expected_base_branch": "main",
        "expected_base_sha": "a" * 40,
        "candidate_branch": "pub/v1",
        "expected_candidate_head": "b" * 40,
        "target_pr_base": "main",
        "manifest": {
            "include_globs": ["**/*"],
            "exclude_globs": ["_internal/"],
            "max_file_size_bytes": 1048576,
            "secret_scan": True,
            "large_file_scan": True,
        },
        "approvals": {
            "branch_publication": {"approved": False},
            "draft_pr_creation": {"approved": False},
        },
        "credentials": {"mechanism": "gh_cli"},
        "evidence": {"output_dir": "/tmp"},
    }
    data2 = dict(data1)
    data2["task_id"] = "test"
    del data2["task_id"]
    data2["task_id"] = "test"

    m1 = parse_publication_manifest(data1)
    m2 = parse_publication_manifest(data2)
    assert compute_manifest_digest_sha256(m1) == compute_manifest_digest_sha256(m2)


# ─── 18. Manifest changes alter the digest ──────────────────────────────────────


def test_manifest_changes_alter_digest(temp_repo):
    repo = temp_repo
    m1 = _make_manifest(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    m2 = _make_manifest(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
        manifest={"max_file_size_bytes": 999},
    )
    d1 = compute_manifest_digest_sha256(m1)
    d2 = compute_manifest_digest_sha256(m2)
    assert d1 != d2


# ─── 19. Tracked-file changes alter the digest ──────────────────────────────────


def test_tracked_file_changes_alter_digest(temp_repo):
    repo = temp_repo
    files1 = ["a.md", "b.md"]
    files2 = ["a.md", "b.md", "c.md"]
    d1 = compute_tracked_file_digest_sha256(repo["path"], files1)
    d2 = compute_tracked_file_digest_sha256(repo["path"], files2)
    assert d1 != d2
    assert len(d1) == 64


# ─── 20. Approval changes alter execution evidence ──────────────────────────────


def test_approval_changes_alter_evidence(temp_repo):
    """Approval state changes must be reflected in PUBLISH_BRANCH mode."""
    repo = temp_repo
    manifest1 = _make_manifest(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    result1 = validate(manifest1, mode=OperationalMode.PUBLISH_BRANCH)

    manifest2 = _make_manifest(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
        approvals={
            "branch_publication": {
                "approved": True,
                "approved_by": "Buddy",
                "approval_ref": "ref",
            },
        },
    )
    result2 = validate(manifest2, mode=OperationalMode.PUBLISH_BRANCH)
    assert result1.validation.gate1_approved is False
    assert result2.validation.gate1_approved is True


# ─── 21. Secret values absent from evidence ─────────────────────────────────────


def test_secret_values_absent_from_evidence(temp_repo):
    """Evidence must not contain raw token values."""
    repo = temp_repo
    evidence_dir = tempfile.mkdtemp()
    manifest = _make_manifest(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
        evidence={"output_dir": evidence_dir},
    )
    result = validate(manifest)
    from tools.git_steward.steward import _write_evidence
    ep = _write_evidence(evidence_dir, "/tmp/test.yaml", result)
    with open(ep) as f:
        content = f.read()
    for token in ["ghp_", "gho_", "github_pat_", "sk-"]:
        assert token not in content, f"evidence contains token pattern: {token}"
    shutil.rmtree(evidence_dir)


# ─── 22. All validation occurs before mutation ──────────────────────────────────


def test_validation_before_mutation(temp_repo):
    """Validate() must not mutate the repository."""
    repo = temp_repo
    sha_before = _git("rev-parse", "HEAD", cwd=repo["path"]).stdout.strip()
    _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    sha_after = _git("rev-parse", "HEAD", cwd=repo["path"]).stdout.strip()
    assert sha_before == sha_after, "validate() mutated the repository"


# ─── 23. Stable error identifiers are emitted ───────────────────────────────────


def test_stable_error_identifiers(temp_repo):
    """Errors must start with stable identifiers like ERR_*."""
    repo = temp_repo
    result = _run_validation(
        repo["path"],
        expected_base_sha="0000000000000000000000000000000000000000",
        expected_candidate_head="0000000000000000000000000000000000000000",
    )
    for e in result.validation.errors:
        assert "ERR_" in e, f"error lacks stable identifier: {e}"


# ─── 24. Evidence is deterministic except for run metadata ──────────────────────


def test_evidence_is_deterministic(temp_repo):
    """Repeated validation with same manifest produces same validation result."""
    repo = temp_repo
    manifest = _make_manifest(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    r1 = validate(manifest)
    r2 = validate(manifest)
    assert r1.validation.passed == r2.validation.passed
    assert r1.validation.errors == r2.validation.errors
    assert r1.validation.file_count == r2.validation.file_count
    assert (
        r1.validation.manifest_digest_sha256 == r2.validation.manifest_digest_sha256
    )
    assert (
        r1.validation.tracked_file_digest_sha256
        == r2.validation.tracked_file_digest_sha256
    )


# ─── 25. Default branch rejected ────────────────────────────────────────────────


def test_default_branch_rejected(temp_repo):
    repo = temp_repo
    _git("checkout", "main", cwd=repo["path"])
    sha = _git("rev-parse", "HEAD", cwd=repo["path"]).stdout.strip()
    manifest = _make_manifest(
        repo["path"],
        candidate_branch="main",
        expected_candidate_head=sha,
        expected_base_sha=repo["initial_sha"],
    )
    result = validate(manifest)
    assert not result.validation.passed
    assert any("ERR_DEFAULT_BRANCH" in e for e in result.validation.errors)


# ─── 26. Wrong repository identity rejected ────────────────────────────────────


def test_wrong_repository_identity():
    result = _run_validation("/nonexistent/path")
    assert not result.validation.passed
    assert any("ERR_REPO_NOT_FOUND" in e for e in result.validation.errors)


# ─── 27. Wrong candidate SHA rejected ──────────────────────────────────────────


def test_wrong_candidate_sha(temp_repo):
    repo = temp_repo
    result = _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head="0000000000000000000000000000000000000000",
    )
    assert not result.validation.passed
    assert any("ERR_HEAD_MISMATCH" in e for e in result.validation.errors)


# ─── 28. Dirty state rejected ──────────────────────────────────────────────────


def test_dirty_state_rejected(temp_repo):
    repo = temp_repo
    (Path(repo["path"]) / "uncommitted.txt").write_text("dirty")
    result = _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    assert not result.validation.passed
    assert any("ERR_DIRTY_TREE" in e for e in result.validation.errors)


# ─── 29. Untracked files rejected ──────────────────────────────────────────────


def test_untracked_files_rejected(temp_repo):
    repo = temp_repo
    (Path(repo["path"]) / "untracked.yaml").write_text("key: value")
    result = _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    assert not result.validation.passed
    assert any("ERR_UNTRACKED_FILES" in e for e in result.validation.errors)


# ─── 30. Protected paths rejected ──────────────────────────────────────────────


def test_protected_paths_rejected(temp_repo):
    repo = temp_repo
    (Path(repo["path"]) / "_internal").mkdir(exist_ok=True)
    (Path(repo["path"]) / "_internal" / "notes.md").write_text("private")
    _git("add", "_internal/notes.md", cwd=repo["path"])
    _git("commit", "-m", "add protected", cwd=repo["path"])
    sha = _git("rev-parse", "HEAD", cwd=repo["path"]).stdout.strip()
    result = _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=sha,
    )
    assert not result.validation.passed
    assert any("ERR_PROTECTED_PATH" in e for e in result.validation.errors)


# ─── 31. Oversized files rejected ──────────────────────────────────────────────


def test_oversized_files_rejected(temp_repo):
    repo = temp_repo
    big_path = Path(repo["path"]) / "big_file.bin"
    big_path.write_bytes(b"x" * (2 * 1024 * 1024))
    _git("add", "big_file.bin", cwd=repo["path"])
    _git("commit", "-m", "add big file", cwd=repo["path"])
    sha = _git("rev-parse", "HEAD", cwd=repo["path"]).stdout.strip()
    result = _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=sha,
        manifest={"max_file_size_bytes": 1024},
    )
    assert not result.validation.passed
    assert any("ERR_LARGE_FILE" in e for e in result.validation.errors)


# ─── 32. Secret-like content rejected ──────────────────────────────────────────


def test_secret_like_content_rejected(temp_repo):
    repo = temp_repo
    (Path(repo["path"]) / "config.py").write_text(
        'API_KEY = "sk-1234567890123456789012345678901234567890123"\n'
    )
    _git("add", "config.py", cwd=repo["path"])
    _git("commit", "-m", "add config", cwd=repo["path"])
    sha = _git("rev-parse", "HEAD", cwd=repo["path"]).stdout.strip()
    result = _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=sha,
    )
    assert not result.validation.passed
    assert any("ERR_SECRET_FOUND" in e for e in result.validation.errors)


# ─── 33. Absolute dev paths rejected ──────────────────────────────────────────


def test_absolute_dev_paths_rejected(temp_repo):
    repo = temp_repo
    (Path(repo["path"]) / "config.yaml").write_text(
        "path: /Users/buddy/projects/something\n"
    )
    _git("add", "config.yaml", cwd=repo["path"])
    _git("commit", "-m", "add config", cwd=repo["path"])
    sha = _git("rev-parse", "HEAD", cwd=repo["path"]).stdout.strip()
    result = _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=sha,
    )
    assert not result.validation.passed


# ─── 34. Wrong remote rejected ──────────────────────────────────────────────────


def test_wrong_remote_rejected(temp_repo):
    repo = temp_repo
    result = _run_validation(
        repo["path"],
        repository={"remote": "https://github.com/wrong/wrong.git"},
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    assert not result.validation.passed
    assert any("ERR_REMOTE_MISMATCH" in e for e in result.validation.errors)


# ─── 35. Wrong branch rejected ─────────────────────────────────────────────────


def test_wrong_branch_rejected(temp_repo):
    repo = temp_repo
    _git("checkout", "main", cwd=repo["path"])
    result = _run_validation(
        repo["path"],
        candidate_branch="publish/test-v1",
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    assert not result.validation.passed
    assert any("ERR_BRANCH_MISMATCH" in e for e in result.validation.errors)


# ─── 36. Upstream info recorded ────────────────────────────────────────────────


def test_upstream_info_recorded(temp_repo):
    """Upstream tracking to main must be detected and recorded."""
    repo = temp_repo
    _git("checkout", "publish/test-v1", cwd=repo["path"])
    _git("config", "branch.publish/test-v1.remote", "origin", cwd=repo["path"])
    _git("config", "branch.publish/test-v1.merge", "refs/heads/main", cwd=repo["path"])
    # Create the remote tracking ref so @{upstream} resolves
    main_sha = _git("rev-parse", "main", cwd=repo["path"]).stdout.strip()
    _git("update-ref", "refs/remotes/origin/main", main_sha, cwd=repo["path"])
    result = _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    assert result.validation.passed, f"validation errors: {result.validation.errors}"
    ui = result.validation.upstream_info
    assert ui is not None
    assert ui.has_upstream is True, f"expected has_upstream=True, got {ui}"
    assert ui.targets_main is True
    assert ui.warning is not None


# ─── 37. Full 64-char SHA-256 in output ──────────────────────────────────────


def test_full_64_char_sha256(temp_repo):
    repo = temp_repo
    result = _run_validation(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
    )
    if result.validation.tracked_file_digest_sha256:
        assert len(result.validation.tracked_file_digest_sha256) == 64
    if result.validation.manifest_digest_sha256:
        assert len(result.validation.manifest_digest_sha256) == 64


# ─── 38. Manifest self-validation errors have stable IDs ──────────────────────


def test_manifest_self_validation_stable_errors():
    data = {
        "task_id": "",
        "session_id": 0,
        "repository": {"path": "", "remote": ""},
        "expected_base_branch": "",
        "expected_base_sha": "",
        "candidate_branch": "",
        "expected_candidate_head": "",
        "target_pr_base": "",
        "manifest": {},
        "approvals": {
            "branch_publication": {"approved": False},
            "draft_pr_creation": {"approved": False},
        },
        "credentials": {},
        "evidence": {},
    }
    manifest = parse_publication_manifest(data)
    errors = manifest.validate_self()
    for e in errors:
        assert "ERR_" in e, f"error lacks stable identifier: {e}"
    assert len(errors) >= 5


# ─── 39. Validate mode accepts any approval state ─────────────────────────────


def test_validate_mode_accepts_any_approval_state(temp_repo):
    """validate mode must not check gates regardless of approval state."""
    repo = temp_repo
    manifest = _make_manifest(
        repo["path"],
        expected_base_sha=repo["initial_sha"],
        expected_candidate_head=repo["candidate_sha"],
        approvals={
            "branch_publication": {"approved": True, "approved_by": "Buddy", "approval_ref": "r"},
            "draft_pr_creation": {"approved": True, "approved_by": "Buddy", "approval_ref": "r"},
        },
    )
    result = validate(manifest, mode=OperationalMode.VALIDATE)
    assert result.validation.passed
    assert result.validation.gate1_approved is None
    assert result.validation.gate2_approved is None


# ─── 40. Publish-branch mode requires only Gate 1 ──────────────────────────────


def test_publish_requires_only_gate1(temp_repo):
    repo = temp_repo
    result = validate(
        _make_manifest(
            repo["path"],
            expected_base_sha=repo["initial_sha"],
            expected_candidate_head=repo["candidate_sha"],
            approvals={
                "branch_publication": {
                    "approved": True,
                    "approved_by": "Buddy",
                    "approval_ref": "session-99",
                },
                "draft_pr_creation": {"approved": False},
            },
        ),
        mode=OperationalMode.PUBLISH_BRANCH,
    )
    assert result.validation.passed, f"publish-branch failed: {result.validation.errors}"
    assert result.gate1 is not None
    assert result.gate2 is not None  # commands generated but won't be executed
    cmd = result.gate1.push_command.command
    assert "refs/heads/" in cmd


# ─── 41. Empty tracked file digest ────────────────────────────────────────────


def test_empty_tracked_file_digest():
    d = compute_tracked_file_digest_sha256("/tmp", [])
    assert len(d) == 64
    assert d == hashlib.sha256(b"").hexdigest()
