from __future__ import annotations

import dataclasses
import hashlib
import json
from typing import Any


class OperationalMode:
    VALIDATE = "validate"
    PUBLISH_BRANCH = "publish-branch"
    CREATE_DRAFT_PR = "create-draft-pr"

    ALL = (VALIDATE, PUBLISH_BRANCH, CREATE_DRAFT_PR)


@dataclasses.dataclass(frozen=True)
class RepositoryIdentity:
    path: str
    remote_url: str


@dataclasses.dataclass(frozen=True)
class ManifestSpec:
    include_globs: tuple[str, ...]
    exclude_globs: tuple[str, ...]
    max_file_size_bytes: int
    secret_scan_enabled: bool
    large_file_scan_enabled: bool


@dataclasses.dataclass(frozen=True)
class GateApproval:
    approved: bool
    approved_by: str | None = None
    approval_ref: str | None = None

    def validate(self, gate_name: str) -> list[str]:
        errors: list[str] = []
        if self.approved:
            if not self.approved_by:
                errors.append(f"{gate_name}: approved=true requires approved_by")
            if not self.approval_ref:
                errors.append(f"{gate_name}: approved=true requires approval_ref")
        return errors


@dataclasses.dataclass(frozen=True)
class Approvals:
    branch_publication: GateApproval
    draft_pr_creation: GateApproval

    def validate(self) -> list[str]:
        return (
            self.branch_publication.validate("branch_publication")
            + self.draft_pr_creation.validate("draft_pr_creation")
        )


@dataclasses.dataclass(frozen=True)
class CredentialMechanism:
    mechanism: str


@dataclasses.dataclass(frozen=True)
class PublicationManifest:
    task_id: str
    session_id: int
    repository: RepositoryIdentity
    expected_base_branch: str
    expected_base_sha: str
    candidate_branch: str
    expected_candidate_head: str
    target_pr_base: str
    manifest: ManifestSpec
    approvals: Approvals
    credentials: CredentialMechanism
    evidence_output_dir: str

    def validate_self(self) -> list[str]:
        errors: list[str] = []
        if not self.task_id:
            errors.append("ERR_MISSING_TASK_ID: task_id is required")
        if not self.repository.path:
            errors.append("ERR_MISSING_REPO_PATH: repository.path is required")
        if not self.repository.remote_url:
            errors.append("ERR_MISSING_REMOTE_URL: repository.remote_url is required")
        if not self.expected_base_branch:
            errors.append("ERR_MISSING_BASE_BRANCH: expected_base_branch is required")
        if not self.expected_base_sha:
            errors.append("ERR_MISSING_BASE_SHA: expected_base_sha is required")
        if not self.candidate_branch:
            errors.append("ERR_MISSING_CANDIDATE_BRANCH: candidate_branch is required")
        if not self.expected_candidate_head:
            errors.append("ERR_MISSING_CANDIDATE_HEAD: expected_candidate_head is required")
        errors.extend(self.approvals.validate())
        return errors


@dataclasses.dataclass(frozen=True)
class BranchInfo:
    current_branch: str
    is_default: bool
    has_remote_tracking: bool
    remote_tracking_branch: str | None


@dataclasses.dataclass(frozen=True)
class UpstreamInfo:
    has_upstream: bool
    upstream_branch: str | None
    targets_main: bool
    warning: str | None = None


@dataclasses.dataclass(frozen=True)
class FileFinding:
    path: str
    finding_type: str
    detail: str
    size_bytes: int | None = None


_ERR_PREFIXES = [
    "ERR_REPO_NOT_FOUND",
    "ERR_REMOTE_MISMATCH",
    "ERR_BRANCH_MISMATCH",
    "ERR_HEAD_MISMATCH",
    "ERR_BASE_NOT_FOUND",
    "ERR_BASE_NOT_ANCESTOR",
    "ERR_DIRTY_TREE",
    "ERR_UNTRACKED_FILES",
    "ERR_PROTECTED_PATH",
    "ERR_SECRET_FOUND",
    "ERR_LARGE_FILE",
    "ERR_DEFAULT_BRANCH",
    "ERR_GATE1_NOT_APPROVED",
    "ERR_GATE1_MISSING_APPROVER",
    "ERR_GATE1_MISSING_REF",
    "ERR_GATE2_NOT_APPROVED",
    "ERR_GATE2_MISSING_APPROVER",
    "ERR_GATE2_MISSING_REF",
    "ERR_MODE_NOT_AUTHORIZED",
    "ERR_REMOTE_BRANCH_EXISTS",
    "ERR_REMOTE_SHA_MISMATCH",
]


def make_error(error_id: str, message: str) -> str:
    return f"{error_id}: {message}"


@dataclasses.dataclass(frozen=True)
class ValidationResult:
    passed: bool
    repository_identity_ok: bool | None = None
    remote_matches: bool | None = None
    branch_valid: bool | None = None
    base_sha_valid: bool | None = None
    head_valid: bool | None = None
    tree_clean: bool | None = None
    no_untracked: bool | None = None
    no_protected_paths: bool | None = None
    no_secrets: bool | None = None
    no_large_files: bool | None = None
    not_default_branch: bool | None = None
    no_absolute_dev_paths: bool | None = None
    gate1_approved: bool | None = None
    gate2_approved: bool | None = None
    credential_ready: bool | None = None
    mode: str | None = None
    branch_info: BranchInfo | None = None
    upstream_info: UpstreamInfo | None = None
    findings: tuple[FileFinding, ...] = ()
    errors: tuple[str, ...] = ()
    actual_base_sha: str | None = None
    actual_head: str | None = None
    actual_remote: str | None = None
    file_count: int | None = None
    tracked_file_digest_sha256: str | None = None
    manifest_digest_sha256: str | None = None


@dataclasses.dataclass(frozen=True)
class MutationCommand:
    command: str
    description: str


@dataclasses.dataclass(frozen=True)
class Gate1Result:
    push_command: MutationCommand | None = None
    rollback_command: str | None = None


@dataclasses.dataclass(frozen=True)
class Gate2Result:
    pr_command: MutationCommand | None = None
    pr_title: str | None = None
    pr_body: str | None = None


@dataclasses.dataclass(frozen=True)
class StewardResult:
    validation: ValidationResult
    gate1: Gate1Result | None = None
    gate2: Gate2Result | None = None
    mutation_status: str = "none"
    stop_reason: str | None = None
    evidence_paths: tuple[str, ...] = ()
    recommended_next_action: str = ""


def _stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)


def compute_manifest_digest_sha256(manifest: PublicationManifest) -> str:
    canonical = {
        "task_id": manifest.task_id,
        "session_id": manifest.session_id,
        "repository_path": manifest.repository.path,
        "repository_remote": manifest.repository.remote_url,
        "expected_base_branch": manifest.expected_base_branch,
        "expected_base_sha": manifest.expected_base_sha,
        "candidate_branch": manifest.candidate_branch,
        "expected_candidate_head": manifest.expected_candidate_head,
        "target_pr_base": manifest.target_pr_base,
        "manifest": {
            "max_file_size_bytes": manifest.manifest.max_file_size_bytes,
            "secret_scan_enabled": manifest.manifest.secret_scan_enabled,
            "large_file_scan_enabled": manifest.manifest.large_file_scan_enabled,
            "exclude_globs": sorted(manifest.manifest.exclude_globs),
            "include_globs": sorted(manifest.manifest.include_globs),
        },
    }
    raw = _stable_json(canonical)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def compute_tracked_file_digest_sha256(repo_path: str, tracked_files: list[str]) -> str:
    if not tracked_files:
        return hashlib.sha256(b"").hexdigest()
    canonical = "\n".join(sorted(tracked_files)) + "\n"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def parse_publication_manifest(data: dict[str, Any]) -> PublicationManifest:
    repo_data = data.get("repository", {})
    manifest_data = data.get("manifest", {})
    approvals_data = data.get("approvals", {})
    cred_data = data.get("credentials", {})

    bp = approvals_data.get("branch_publication", {})
    dp = approvals_data.get("draft_pr_creation", {})

    return PublicationManifest(
        task_id=data.get("task_id", ""),
        session_id=int(data.get("session_id", 0)),
        repository=RepositoryIdentity(
            path=repo_data.get("path", ""),
            remote_url=repo_data.get("remote", ""),
        ),
        expected_base_branch=data.get("expected_base_branch", ""),
        expected_base_sha=data.get("expected_base_sha", ""),
        candidate_branch=data.get("candidate_branch", ""),
        expected_candidate_head=data.get("expected_candidate_head", ""),
        target_pr_base=data.get("target_pr_base", ""),
        manifest=ManifestSpec(
            include_globs=tuple(manifest_data.get("include_globs", [])),
            exclude_globs=tuple(manifest_data.get("exclude_globs", [])),
            max_file_size_bytes=int(manifest_data.get("max_file_size_bytes", 1048576)),
            secret_scan_enabled=bool(manifest_data.get("secret_scan", True)),
            large_file_scan_enabled=bool(manifest_data.get("large_file_scan", True)),
        ),
        approvals=Approvals(
            branch_publication=GateApproval(
                approved=bool(bp.get("approved", False)),
                approved_by=bp.get("approved_by"),
                approval_ref=bp.get("approval_ref"),
            ),
            draft_pr_creation=GateApproval(
                approved=bool(dp.get("approved", False)),
                approved_by=dp.get("approved_by"),
                approval_ref=dp.get("approval_ref"),
            ),
        ),
        credentials=CredentialMechanism(
            mechanism=cred_data.get("mechanism", "gh_cli"),
        ),
        evidence_output_dir=data.get("evidence", {}).get("output_dir", ""),
    )
