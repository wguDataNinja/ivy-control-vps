from __future__ import annotations

import fnmatch
import hashlib
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from .models import (
    BranchInfo,
    DryRunResult,
    FileFinding,
    PublicationManifest,
    StewardResult,
    ValidationResult,
)


def _run_git(
    repo_path: str, *args: str, timeout: int = 30
) -> tuple[int, str, str]:
    try:
        r = subprocess.run(
            ["git", "-C", repo_path, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return r.returncode, r.stdout, r.stderr
    except FileNotFoundError:
        return -2, "", "git not found"
    except subprocess.TimeoutExpired:
        return -1, "", "git command timed out"


def _resolve_repo_path(raw: str) -> str | None:
    path = os.path.abspath(os.path.expanduser(raw))
    if not os.path.isdir(path):
        return None
    git_dir = os.path.join(path, ".git")
    # .git may be a directory (normal repo) or a file (worktree)
    if not os.path.isdir(git_dir) and not os.path.isfile(git_dir):
        return None
    return path


def _compute_manifest_digest(repo_path: str, manifest: PublicationManifest) -> str:
    tracked = _run_git(repo_path, "ls-files")
    if tracked[0] != 0:
        return ""
    files = sorted(tracked[1].strip().split("\n")) if tracked[1].strip() else []
    raw = "\n".join(files)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


# Patterns that suggest secrets in committed files
_SECRET_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?i)(?:api[_-]?key|apikey)\s*[:=]\s*[\"'][^\"']{16,}[\"']"),
    re.compile(r"(?i)(?:secret|token)\s*[:=]\s*[\"'][^\"']{16,}[\"']"),
    re.compile(r"(?i)password\s*[:=]\s*[\"'][^\"']+[\"']"),
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    re.compile(r"gho_[a-zA-Z0-9]{36}"),
    re.compile(r"github_pat_[a-zA-Z0-9]{36}"),
    re.compile(r"sk-[a-zA-Z0-9]{32,}"),
    re.compile(r"(?i)-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
]

# Path patterns that are typically excluded from publication
_PROTECTED_PATH_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?:^|/)_internal/"),
    re.compile(r"(?:^|/)internal/"),
    re.compile(r"(?:^|/)logs/"),
    re.compile(r"(?:^|/)\.env$"),
    re.compile(r"(?:^|/)\.env\.local$"),
    re.compile(r"(?:^|/)\.env\.production$"),
    re.compile(r"(?:^|/)\.env\.development$"),
    re.compile(r"(?:^|/)\.env\.staging$"),
    re.compile(r"(?:^|/)TODO\.md$"),
    re.compile(r"(?:^|/)agent/"),
    re.compile(r"(?:^|/)agent-reports/"),
    re.compile(r"(?:^|/)generated/"),
    re.compile(r"(?:^|/)__pycache__/"),
    re.compile(r"\.pytest_cache/"),
    re.compile(r"\.venv/"),
    re.compile(r"node_modules/"),
    re.compile(r"\.DS_Store$"),
    re.compile(r"credentials\.json$"),
    re.compile(r"tokens\.json$"),
    re.compile(r"client_secret.+\.json$"),
]

# Absolute path patterns from the development environment
_ABSOLUTE_PATH_PATTERNS: list[re.Pattern] = [
    re.compile(r"/Users/buddy/"),
    re.compile(r"/home/buddy/"),
]


def _is_protected_path(path: str) -> bool:
    for pat in _PROTECTED_PATH_PATTERNS:
        if pat.search(path):
            return True
    return False


def _has_secret_like_content(filepath: str) -> bool:
    try:
        with open(filepath, "r", errors="replace") as f:
            content = f.read(50000)
        for pat in _SECRET_PATTERNS:
            if pat.search(content):
                return True
    except Exception:
        pass
    return False


def _has_absolute_dev_path(filepath: str) -> bool:
    try:
        with open(filepath, "r", errors="replace") as f:
            content = f.read(50000)
        for pat in _ABSOLUTE_PATH_PATTERNS:
            if pat.search(content):
                return True
    except Exception:
        pass
    return False


def _is_large_file(filepath: str, max_bytes: int) -> bool:
    try:
        size = os.path.getsize(filepath)
        return size > max_bytes, size
    except OSError:
        return False, 0


def validate(manifest: PublicationManifest) -> StewardResult:
    errors: list[str] = []
    findings: list[FileFinding] = []
    repo_path = manifest.repository.path

    # Validate manifest self-consistency
    manifest_errors = manifest.validate_self()
    if manifest_errors:
        return StewardResult(
            validation=ValidationResult(
                passed=False, errors=tuple(manifest_errors)
            ),
            dry_run=None,
            mutation_status="none",
            stop_reason="manifest validation failed",
            evidence_paths=(),
            recommended_next_action="fix publication manifest",
        )

    # Resolve and verify repository
    resolved = _resolve_repo_path(repo_path)
    if resolved is None:
        return StewardResult(
            validation=ValidationResult(
                passed=False,
                repository_identity_ok=False,
                errors=(f"repository path not found or not a git repo: {repo_path}",),
            ),
            dry_run=None,
            mutation_status="none",
            stop_reason="repository not found",
            evidence_paths=(),
            recommended_next_action="verify repository path",
        )

    # Remote
    rc, stdout, _ = _run_git(resolved, "remote", "get-url", "origin")
    actual_remote = stdout.strip() if rc == 0 else None
    remote_matches = actual_remote == manifest.repository.remote_url

    if not remote_matches:
        errors.append(
            f"remote mismatch: expected '{manifest.repository.remote_url}', got '{actual_remote}'"
        )

    # Branch
    rc, stdout, _ = _run_git(resolved, "rev-parse", "--abbrev-ref", "HEAD")
    current_branch = stdout.strip() if rc == 0 else "unknown"
    branch_valid = current_branch == manifest.candidate_branch
    if not branch_valid:
        errors.append(
            f"branch mismatch: expected '{manifest.candidate_branch}', on '{current_branch}'"
        )

    # Default branch check
    rc, stdout, _ = _run_git(resolved, "symbolic-ref", "refs/remotes/origin/HEAD")
    default_branch = ""
    if rc == 0:
        ref = stdout.strip()
        default_branch = ref.replace("refs/remotes/origin/", "")
    is_default = current_branch == default_branch

    # Remote tracking
    rc, stdout, _ = _run_git(
        resolved, "rev-parse", "--abbrev-ref", "--symbolic-full-name", f"{current_branch}@{{upstream}}"
    )
    has_remote_tracking = rc == 0 and bool(stdout.strip())
    remote_tracking_branch = stdout.strip() if has_remote_tracking else None

    branch_info = BranchInfo(
        current_branch=current_branch,
        is_default=is_default,
        has_remote_tracking=has_remote_tracking,
        remote_tracking_branch=remote_tracking_branch,
    )

    # HEAD
    rc, stdout, _ = _run_git(resolved, "rev-parse", "HEAD")
    actual_head = stdout.strip() if rc == 0 else None
    head_valid = actual_head == manifest.expected_candidate_head
    if not head_valid:
        errors.append(
            f"HEAD mismatch: expected '{manifest.expected_candidate_head}', got '{actual_head}'"
        )

    # Base SHA
    rc, stdout, _ = _run_git(resolved, "rev-parse", manifest.expected_base_sha)
    actual_base = stdout.strip() if rc == 0 else None
    base_found = rc == 0

    # Verify base is ancestor of HEAD
    base_is_ancestor = False
    if base_found:
        rc, _, _ = _run_git(
            resolved, "merge-base", "--is-ancestor", manifest.expected_base_sha, "HEAD"
        )
        base_is_ancestor = rc == 0

    if not base_found or not base_is_ancestor:
        base_valid = False
        if not base_found:
            errors.append(f"base SHA not found in repository: {manifest.expected_base_sha}")
        else:
            errors.append(
                f"base SHA {manifest.expected_base_sha} is not an ancestor of HEAD"
            )
    else:
        base_valid = True

    # Working tree
    rc, stdout, _ = _run_git(resolved, "status", "--porcelain")
    tree_dirty_lines = [l for l in stdout.strip().split("\n") if l.strip()] if stdout.strip() else []
    tree_clean = len(tree_dirty_lines) == 0
    if not tree_clean:
        errors.append(f"working tree has {len(tree_dirty_lines)} dirty entries")

    # Untracked files
    untracked = [l for l in tree_dirty_lines if l.startswith("??")]
    no_untracked = len(untracked) == 0
    if not no_untracked:
        errors.append(f"working tree has {len(untracked)} untracked files")

    # Tracked file list
    rc, stdout, _ = _run_git(resolved, "ls-files")
    tracked_files = sorted(stdout.strip().split("\n")) if rc == 0 and stdout.strip() else []
    file_count = len(tracked_files)

    # Manifest digest
    manifest_digest = _compute_manifest_digest(resolved, manifest)

    # Scan tracked files for protected paths, secrets, large files
    if tracked_files:
        for tf in tracked_files:
            # Protected/excluded path check
            if _is_protected_path(tf):
                findings.append(
                    FileFinding(
                        path=tf,
                        finding_type="protected_path",
                        detail=f"path matches protected pattern",
                    )
                )

            # Absolute development path check
            abs_path = os.path.join(resolved, tf)
            if os.path.isfile(abs_path):
                if _has_absolute_dev_path(abs_path):
                    findings.append(
                        FileFinding(
                            path=tf,
                            finding_type="secret_like",
                            detail="contains absolute development environment path",
                        )
                    )

                # Large file check
                if manifest.manifest.large_file_scan_enabled:
                    oversized, size = _is_large_file(abs_path, manifest.manifest.max_file_size_bytes)
                    if oversized:
                        findings.append(
                            FileFinding(
                                path=tf,
                                finding_type="oversized",
                                detail=f"file size {size} exceeds max {manifest.manifest.max_file_size_bytes}",
                                size_bytes=size,
                            )
                        )

                # Secret scan
                if manifest.manifest.secret_scan_enabled:
                    if _has_secret_like_content(abs_path):
                        findings.append(
                            FileFinding(
                                path=tf,
                                finding_type="secret_like",
                                detail="file content matches secret-like pattern",
                            )
                        )

    # Protected path gate
    protected_findings = [f for f in findings if f.finding_type == "protected_path"]
    no_protected_paths = len(protected_findings) == 0
    if not no_protected_paths:
        for pf in protected_findings:
            errors.append(f"protected path found in tracked files: {pf.path}")

    # Secret findings
    secret_findings = [f for f in findings if f.finding_type == "secret_like"]
    no_secrets = len(secret_findings) == 0

    # Large file findings
    large_findings = [f for f in findings if f.finding_type == "oversized"]
    no_large_files = len(large_findings) == 0

    # Not default branch
    not_default_branch = not is_default
    if is_default:
        errors.append(
            f"candidate branch '{current_branch}' is the default branch; publication candidates must not be the default branch"
        )

    # No remote tracking — warn if upstream targets main
    no_remote_tracking = not has_remote_tracking
    if has_remote_tracking and remote_tracking_branch == "origin/main":
        findings.append(
            FileFinding(
                path="(branch config)",
                finding_type="protected_path",
                detail=f"upstream '{remote_tracking_branch}' targets main branch; a bare `git push` would push to main, not to candidate branch",
            )
        )

    # Push approval
    push_approved = manifest.approval.push_approved
    if not push_approved:
        errors.append("push not approved")

    # PR approval
    pr_approved = manifest.approval.pr_approved
    if not pr_approved:
        errors.append("PR creation not approved")

    # Credential readiness
    credential_ready = manifest.credentials.mechanism in ("gh_cli", "pat")

    # Verify excluded paths don't exist in candidate
    excluded_globs = manifest.manifest.exclude_globs
    for tf in tracked_files:
        for pattern in excluded_globs:
            # Support directory-only patterns: "internal/" matches "internal/foo"
            pat = pattern.rstrip("/") + ("/*" if pattern.endswith("/") else "")
            if fnmatch.fnmatch(tf, pat) or fnmatch.fnmatch(tf, pattern):
                findings.append(
                    FileFinding(
                        path=tf,
                        finding_type="protected_path",
                        detail=f"path matches excluded pattern '{pattern}'",
                    )
                )

    validation = ValidationResult(
        passed=len(errors) == 0 and len(findings) == 0,
        repository_identity_ok=True,
        remote_matches=remote_matches,
        branch_valid=branch_valid,
        base_sha_valid=base_valid,
        head_valid=head_valid,
        tree_clean=tree_clean,
        no_untracked=no_untracked,
        no_protected_paths=no_protected_paths,
        manifest_matches=True,
        no_secrets=no_secrets,
        no_large_files=no_large_files,
        not_default_branch=not_default_branch,
        no_remote_tracking=no_remote_tracking,
        push_approved=push_approved,
        pr_approved=pr_approved,
        credential_ready=credential_ready,
        branch_info=branch_info,
        findings=tuple(findings),
        errors=tuple(errors),
        actual_base_sha=actual_base or manifest.expected_base_sha,
        actual_head=actual_head or manifest.expected_candidate_head,
        actual_remote=actual_remote or "unknown",
        file_count=file_count,
        manifest_digest=manifest_digest,
    )

    passed = validation.passed

    # Dry run commands
    if passed:
        remote_name = "origin"
        push_cmd = f"git push {remote_name} {manifest.candidate_branch}:{manifest.candidate_branch}"
        pr_cmd = (
            f"gh pr create --base {manifest.target_pr_base} "
            f"--head {manifest.candidate_branch} "
            f"--title \"{_default_pr_title(manifest)}\" "
            f"--body \"{_default_pr_body(manifest)}\" "
            f"--draft"
        )
        rollback_cmd = f"git push {remote_name} --delete {manifest.candidate_branch}"
    else:
        push_cmd = None
        pr_cmd = None
        rollback_cmd = None

    dry_run = DryRunResult(
        push_command=push_cmd,
        pr_command=pr_cmd,
        pr_title=_default_pr_title(manifest) if passed else None,
        pr_body=_default_pr_body(manifest) if passed else None,
        rollback_command=rollback_cmd,
    )

    stop_reason = None
    if not passed:
        stop_reason = "; ".join(errors[:5]) if errors else "validation failed"

    recommended = _recommend_next(validation, manifest)

    return StewardResult(
        validation=validation,
        dry_run=dry_run,
        mutation_status="dry_run_only",
        stop_reason=stop_reason,
        evidence_paths=(),
        recommended_next_action=recommended,
    )


def _default_pr_title(manifest: PublicationManifest) -> str:
    return f"[{manifest.task_id}] Publish {manifest.repository.path} baseline"


def _default_pr_body(manifest: PublicationManifest) -> str:
    lines = [
        "## Publication Baseline",
        "",
        "This pull request proposes a reconstructed clean publication baseline.",
        "",
        "### Details",
        f"- **Task:** {manifest.task_id}",
        f"- **Session:** {manifest.session_id}",
        f"- **Candidate branch:** `{manifest.candidate_branch}`",
        f"- **Target base:** `{manifest.target_pr_base}`",
        f"- **Expected candidate HEAD:** `{manifest.expected_candidate_head[:12]}`",
        f"- **Expected base SHA:** `{manifest.expected_base_sha[:12]}`",
        "",
        "### Validation",
        "All local safety gates passed.",
        "",
        "### Notes",
        "- Private and generated paths are removed prospectively.",
        "- Prior public history may still contain those paths.",
        "- No merge is requested.",
        "- Review is required before any integration.",
        "",
        "### Rollback",
        "Delete the remote branch after rejection or consolidation:",
        f"```",
        f"git push origin --delete {manifest.candidate_branch}",
        f"```",
    ]
    return "\n".join(lines)


def _recommend_next(validation: ValidationResult, manifest: PublicationManifest) -> str:
    if validation.passed:
        return "execute push after push_approved; then create draft PR after pr_approved"
    blockers = []
    if not validation.remote_matches:
        blockers.append("fix remote")
    if not validation.branch_valid:
        blockers.append("switch to candidate branch")
    if not validation.head_valid:
        blockers.append("correct HEAD")
    if not validation.base_sha_valid:
        blockers.append("correct base SHA")
    if not validation.tree_clean:
        blockers.append("clean working tree")
    if not validation.no_protected_paths:
        blockers.append("remove protected paths")
    if not validation.no_secrets:
        blockers.append("resolve secret findings")
    if not validation.no_large_files:
        blockers.append("resolve large file findings")
    if not validation.not_default_branch:
        blockers.append("use non-default branch")
    if not validation.push_approved:
        blockers.append("obtain push approval")
    if not validation.pr_approved:
        blockers.append("obtain PR approval")
    if not validation.credential_ready:
        blockers.append("configure credentials")
    return "blocked: " + ", ".join(blockers[:5]) if blockers else "unknown"
