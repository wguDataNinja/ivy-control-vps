from __future__ import annotations

import fnmatch
import hashlib
import os
import re
import subprocess
from typing import Any

from .models import (
    BranchInfo,
    FileFinding,
    Gate1Result,
    Gate2Result,
    MutationCommand,
    OperationalMode,
    PublicationManifest,
    StewardResult,
    UpstreamInfo,
    ValidationResult,
    compute_manifest_digest_sha256,
    compute_tracked_file_digest_sha256,
    make_error,
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
    if not os.path.isdir(git_dir) and not os.path.isfile(git_dir):
        return None
    return path


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


def _is_large_file(filepath: str, max_bytes: int) -> tuple[bool, int]:
    try:
        size = os.path.getsize(filepath)
        return size > max_bytes, size
    except OSError:
        return False, 0


def validate(
    manifest: PublicationManifest,
    mode: str = OperationalMode.VALIDATE,
) -> StewardResult:
    errors: list[str] = []
    findings: list[FileFinding] = []
    repo_path = manifest.repository.path

    manifest_errors = manifest.validate_self()
    if manifest_errors:
        return StewardResult(
            validation=ValidationResult(
                passed=False, errors=tuple(manifest_errors)
            ),
            mutation_status="none",
            stop_reason="manifest validation failed",
            recommended_next_action="fix publication manifest",
        )

    if mode not in OperationalMode.ALL:
        return StewardResult(
            validation=ValidationResult(
                passed=False,
                mode=mode,
                errors=(make_error("ERR_INVALID_MODE", f"unknown mode: {mode}"),),
            ),
            mutation_status="none",
            stop_reason="invalid mode",
        )

    resolved = _resolve_repo_path(repo_path)
    if resolved is None:
        return StewardResult(
            validation=ValidationResult(
                passed=False,
                repository_identity_ok=False,
                mode=mode,
                errors=(
                    make_error(
                        "ERR_REPO_NOT_FOUND",
                        f"repository path not found or not a git repo: {repo_path}",
                    ),
                ),
            ),
            mutation_status="none",
            stop_reason="repository not found",
            recommended_next_action="verify repository path",
        )

    # Remote
    rc, stdout, _ = _run_git(resolved, "remote", "get-url", "origin")
    actual_remote = stdout.strip() if rc == 0 else None
    remote_matches = actual_remote == manifest.repository.remote_url
    if not remote_matches:
        errors.append(
            make_error(
                "ERR_REMOTE_MISMATCH",
                f"expected '{manifest.repository.remote_url}', got '{actual_remote}'",
            )
        )

    # Branch
    rc, stdout, _ = _run_git(resolved, "rev-parse", "--abbrev-ref", "HEAD")
    current_branch = stdout.strip() if rc == 0 else "unknown"
    branch_valid = current_branch == manifest.candidate_branch
    if not branch_valid:
        errors.append(
            make_error(
                "ERR_BRANCH_MISMATCH",
                f"expected '{manifest.candidate_branch}', on '{current_branch}'",
            )
        )

    # Default branch
    rc, stdout, _ = _run_git(resolved, "symbolic-ref", "refs/remotes/origin/HEAD")
    default_branch = ""
    if rc == 0:
        ref = stdout.strip()
        default_branch = ref.replace("refs/remotes/origin/", "")
    is_default = current_branch == default_branch
    if is_default:
        errors.append(
            make_error(
                "ERR_DEFAULT_BRANCH",
                f"candidate branch '{current_branch}' is the default branch",
            )
        )

    # Remote tracking / upstream
    rc, stdout, _ = _run_git(
        resolved,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        f"{current_branch}@{{upstream}}",
    )
    has_remote_tracking = rc == 0 and bool(stdout.strip())
    remote_tracking_branch = stdout.strip() if has_remote_tracking else None
    targets_main = bool(
        has_remote_tracking and remote_tracking_branch == "origin/main"
    )

    upstream_info = UpstreamInfo(
        has_upstream=has_remote_tracking,
        upstream_branch=remote_tracking_branch,
        targets_main=targets_main,
        warning=(
            "upstream targets 'origin/main'; bare `git push` would push to main, "
            "not to candidate branch"
        )
        if targets_main
        else None,
    )

    branch_info = BranchInfo(
        current_branch=current_branch,
        is_default=is_default,
        has_remote_tracking=has_remote_tracking,
        remote_tracking_branch=remote_tracking_branch,
    )

    if targets_main:
        findings.append(
            FileFinding(
                path="(branch config)",
                finding_type="upstream_warning",
                detail=(
                    f"upstream '{remote_tracking_branch}' targets main branch; "
                    f"a bare `git push` would push to main, not to candidate branch. "
                    f"Git Steward always uses an explicit refspec."
                ),
            )
        )

    # HEAD
    rc, stdout, _ = _run_git(resolved, "rev-parse", "HEAD")
    actual_head = stdout.strip() if rc == 0 else None
    head_valid = actual_head == manifest.expected_candidate_head
    if not head_valid:
        errors.append(
            make_error(
                "ERR_HEAD_MISMATCH",
                f"expected '{manifest.expected_candidate_head}', got '{actual_head}'",
            )
        )

    # Base SHA
    rc, stdout, _ = _run_git(resolved, "rev-parse", manifest.expected_base_sha)
    actual_base = stdout.strip() if rc == 0 else None
    base_found = rc == 0

    base_is_ancestor = False
    if base_found:
        rc, _, _ = _run_git(
            resolved,
            "merge-base",
            "--is-ancestor",
            manifest.expected_base_sha,
            "HEAD",
        )
        base_is_ancestor = rc == 0

    if not base_found:
        base_valid = False
        errors.append(
            make_error(
                "ERR_BASE_NOT_FOUND",
                f"base SHA not found: {manifest.expected_base_sha}",
            )
        )
    elif not base_is_ancestor:
        base_valid = False
        errors.append(
            make_error(
                "ERR_BASE_NOT_ANCESTOR",
                f"base SHA {manifest.expected_base_sha} is not an ancestor of HEAD",
            )
        )
    else:
        base_valid = True

    # Working tree
    rc, stdout, _ = _run_git(resolved, "status", "--porcelain")
    tree_lines = (
        [l for l in stdout.strip().split("\n") if l.strip()]
        if stdout.strip()
        else []
    )
    tree_clean = len(tree_lines) == 0
    if not tree_clean:
        errors.append(
            make_error(
                "ERR_DIRTY_TREE",
                f"working tree has {len(tree_lines)} dirty entries",
            )
        )

    untracked = [l for l in tree_lines if l.startswith("??")]
    no_untracked = len(untracked) == 0
    if not no_untracked:
        errors.append(
            make_error(
                "ERR_UNTRACKED_FILES",
                f"working tree has {len(untracked)} untracked files",
            )
        )

    # Tracked files
    rc, stdout, _ = _run_git(resolved, "ls-files")
    tracked_files = (
        sorted(stdout.strip().split("\n")) if rc == 0 and stdout.strip() else []
    )
    file_count = len(tracked_files)

    tracked_file_digest = compute_tracked_file_digest_sha256(resolved, tracked_files)
    manifest_digest = compute_manifest_digest_sha256(manifest)

    # Scan tracked files
    no_absolute_dev_paths = True
    if tracked_files:
        for tf in tracked_files:
            if _is_protected_path(tf):
                findings.append(
                    FileFinding(
                        path=tf,
                        finding_type="protected_path",
                        detail="path matches protected pattern",
                    )
                )

            abs_path = os.path.join(resolved, tf)
            if os.path.isfile(abs_path):
                if _has_absolute_dev_path(abs_path):
                    findings.append(
                        FileFinding(
                            path=tf,
                            finding_type="absolute_dev_path",
                            detail="contains absolute development environment path",
                        )
                    )

                if manifest.manifest.large_file_scan_enabled:
                    oversized, size = _is_large_file(
                        abs_path, manifest.manifest.max_file_size_bytes
                    )
                    if oversized:
                        findings.append(
                            FileFinding(
                                path=tf,
                                finding_type="oversized",
                                detail=f"size {size} exceeds max {manifest.manifest.max_file_size_bytes}",
                                size_bytes=size,
                            )
                        )

                if manifest.manifest.secret_scan_enabled:
                    if _has_secret_like_content(abs_path):
                        findings.append(
                            FileFinding(
                                path=tf,
                                finding_type="secret_like",
                                detail="file content matches secret-like pattern",
                            )
                        )

    # Excluded globs check
    excluded_globs = manifest.manifest.exclude_globs
    for tf in tracked_files:
        for pattern in excluded_globs:
            pat = pattern.rstrip("/") + ("/*" if pattern.endswith("/") else "")
            if fnmatch.fnmatch(tf, pat) or fnmatch.fnmatch(tf, pattern):
                findings.append(
                    FileFinding(
                        path=tf,
                        finding_type="protected_path",
                        detail=f"matches excluded pattern '{pattern}'",
                    )
                )

    # Promote findings to errors
    for ff in findings:
        if ff.finding_type == "protected_path":
            errors.append(
                make_error("ERR_PROTECTED_PATH", f"protected path: {ff.path}")
            )
        elif ff.finding_type == "secret_like":
            errors.append(
                make_error(
                    "ERR_SECRET_FOUND",
                    f"secret-like content in: {ff.path}",
                )
            )
        elif ff.finding_type == "oversized":
            errors.append(
                make_error(
                    "ERR_LARGE_FILE",
                    f"oversized file: {ff.path} ({ff.size_bytes} bytes)",
                )
            )
        elif ff.finding_type == "absolute_dev_path":
            errors.append(
                make_error(
                    "ERR_DEV_PATH",
                    f"absolute dev path in: {ff.path}",
                )
            )

    protected_findings = [f for f in findings if f.finding_type == "protected_path"]
    no_protected_paths = len(protected_findings) == 0
    secret_findings = [f for f in findings if f.finding_type == "secret_like"]
    no_secrets = len(secret_findings) == 0
    large_findings = [f for f in findings if f.finding_type == "oversized"]
    no_large_files = len(large_findings) == 0
    dev_path_findings = [f for f in findings if f.finding_type == "absolute_dev_path"]
    no_absolute_dev_paths = len(dev_path_findings) == 0

    not_default_branch = not is_default
    credential_ready = manifest.credentials.mechanism in ("gh_cli", "pat")

    # Gate checks (mode-dependent)
    gate1_approved: bool | None = None
    gate2_approved: bool | None = None

    if mode == OperationalMode.VALIDATE:
        pass
    elif mode == OperationalMode.PUBLISH_BRANCH:
        bp = manifest.approvals.branch_publication
        gate1_approved = bp.approved
        if not gate1_approved:
            errors.append(
                make_error(
                    "ERR_GATE1_NOT_APPROVED",
                    "branch_publication not approved",
                )
            )
        if bp.approved and not bp.approved_by:
            errors.append(
                make_error(
                    "ERR_GATE1_MISSING_APPROVER",
                    "branch_publication approved=true requires approved_by",
                )
            )
        if bp.approved and not bp.approval_ref:
            errors.append(
                make_error(
                    "ERR_GATE1_MISSING_REF",
                    "branch_publication approved=true requires approval_ref",
                )
            )
    elif mode == OperationalMode.CREATE_DRAFT_PR:
        dp = manifest.approvals.draft_pr_creation
        gate2_approved = dp.approved
        if not gate2_approved:
            errors.append(
                make_error(
                    "ERR_GATE2_NOT_APPROVED",
                    "draft_pr_creation not approved",
                )
            )
        if dp.approved and not dp.approved_by:
            errors.append(
                make_error(
                    "ERR_GATE2_MISSING_APPROVER",
                    "draft_pr_creation approved=true requires approved_by",
                )
            )
        if dp.approved and not dp.approval_ref:
            errors.append(
                make_error(
                    "ERR_GATE2_MISSING_REF",
                    "draft_pr_creation approved=true requires approval_ref",
                )
            )

    base_validation_passed = (
        remote_matches
        and branch_valid
        and base_valid
        and head_valid
        and tree_clean
        and no_untracked
        and no_protected_paths
        and no_secrets
        and no_large_files
        and not_default_branch
        and credential_ready
    )

    mode_gate_passed = True
    if mode == OperationalMode.PUBLISH_BRANCH:
        mode_gate_passed = bool(gate1_approved)
    elif mode == OperationalMode.CREATE_DRAFT_PR:
        mode_gate_passed = bool(gate2_approved)

    blocking_findings = [f for f in findings if f.finding_type != "upstream_warning"]
    overall_passed = base_validation_passed and mode_gate_passed and len(blocking_findings) == 0

    validation = ValidationResult(
        passed=overall_passed,
        repository_identity_ok=True,
        remote_matches=remote_matches,
        branch_valid=branch_valid,
        base_sha_valid=base_valid,
        head_valid=head_valid,
        tree_clean=tree_clean,
        no_untracked=no_untracked,
        no_protected_paths=no_protected_paths,
        no_secrets=no_secrets,
        no_large_files=no_large_files,
        not_default_branch=not_default_branch,
        no_absolute_dev_paths=no_absolute_dev_paths,
        gate1_approved=gate1_approved,
        gate2_approved=gate2_approved,
        credential_ready=credential_ready,
        mode=mode,
        branch_info=branch_info,
        upstream_info=upstream_info,
        findings=tuple(findings),
        errors=tuple(errors),
        actual_base_sha=actual_base or manifest.expected_base_sha,
        actual_head=actual_head or manifest.expected_candidate_head,
        actual_remote=actual_remote or "unknown",
        file_count=file_count,
        tracked_file_digest_sha256=tracked_file_digest,
        manifest_digest_sha256=manifest_digest,
    )

    gate1_result: Gate1Result | None = None
    gate2_result: Gate2Result | None = None

    if overall_passed:
        refspec = f"refs/heads/{manifest.candidate_branch}:refs/heads/{manifest.candidate_branch}"
        push_cmd = f"git push origin {refspec}"
        gate1_result = Gate1Result(
            push_command=MutationCommand(
                command=push_cmd, description="Push candidate branch to remote"
            ),
            rollback_command=f"git push origin --delete refs/heads/{manifest.candidate_branch}",
        )
        pr_title = _default_pr_title(manifest)
        pr_body = _default_pr_body(manifest)
        pr_cmd = (
            f"gh pr create --base {manifest.target_pr_base} "
            f"--head {manifest.candidate_branch} "
            f"--title \"{pr_title}\" "
            f"--body \"{pr_body}\" "
            f"--draft"
        )
        gate2_result = Gate2Result(
            pr_command=MutationCommand(
                command=pr_cmd, description="Create draft PR"
            ),
            pr_title=pr_title,
            pr_body=pr_body,
        )

    stop_reason = None
    if not overall_passed:
        reasons = [e for e in errors[:5]]
        stop_reason = "; ".join(reasons) if reasons else "validation failed"

    recommended = _recommend_next(validation, manifest)

    return StewardResult(
        validation=validation,
        gate1=gate1_result,
        gate2=gate2_result,
        mutation_status="dry_run_only" if overall_passed else "none",
        stop_reason=stop_reason,
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
        f"- **Expected candidate HEAD:** `{manifest.expected_candidate_head}`",
        f"- **Expected base SHA:** `{manifest.expected_base_sha}`",
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
        f"git push origin --delete refs/heads/{manifest.candidate_branch}",
        f"```",
    ]
    return "\n".join(lines)


def _recommend_next(
    validation: ValidationResult, manifest: PublicationManifest
) -> str:
    if validation.passed:
        return "ready for Gate 1 (branch_publication) or Gate 2 (draft_pr_creation) with explicit approval"
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
    if validation.gate1_approved is False:
        blockers.append("obtain branch_publication approval")
    if validation.gate2_approved is False:
        blockers.append("obtain draft_pr_creation approval")
    if not validation.credential_ready:
        blockers.append("configure credentials")
    return "blocked: " + ", ".join(blockers[:5]) if blockers else "unknown"
