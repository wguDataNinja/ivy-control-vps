from __future__ import annotations

import dataclasses
import hashlib
from pathlib import Path
from typing import Any


@dataclasses.dataclass(frozen=True)
class RepositoryIdentity:
    path: str
    remote_url: str

    def digest(self) -> str:
        raw = f"{self.path}|{self.remote_url}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclasses.dataclass(frozen=True)
class ManifestSpec:
    include_globs: tuple[str, ...]
    exclude_globs: tuple[str, ...]
    max_file_size_bytes: int
    secret_scan_enabled: bool
    large_file_scan_enabled: bool


@dataclasses.dataclass(frozen=True)
class ApprovalState:
    push_approved: bool
    pr_approved: bool
    approved_by: str | None
    approval_ref: str | None


@dataclasses.dataclass(frozen=True)
class CredentialMechanism:
    mechanism: str  # "gh_cli", "pat", "none"


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
    approval: ApprovalState
    credentials: CredentialMechanism
    evidence_output_dir: str

    def validate_self(self) -> list[str]:
        errors: list[str] = []
        if not self.task_id:
            errors.append("task_id is required")
        if not self.repository.path:
            errors.append("repository.path is required")
        if not self.repository.remote_url:
            errors.append("repository.remote_url is required")
        if not self.expected_base_branch:
            errors.append("expected_base_branch is required")
        if not self.expected_base_sha:
            errors.append("expected_base_sha is required")
        if not self.candidate_branch:
            errors.append("candidate_branch is required")
        if not self.expected_candidate_head:
            errors.append("expected_candidate_head is required")
        return errors


@dataclasses.dataclass(frozen=True)
class BranchInfo:
    current_branch: str
    is_default: bool
    has_remote_tracking: bool
    remote_tracking_branch: str | None


@dataclasses.dataclass(frozen=True)
class FileFinding:
    path: str
    finding_type: str  # "protected_path", "oversized", "secret_like", "unexpected_tracked"
    detail: str
    size_bytes: int | None = None


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
    manifest_matches: bool | None = None
    no_secrets: bool | None = None
    no_large_files: bool | None = None
    not_default_branch: bool | None = None
    no_remote_tracking: bool | None = None
    push_approved: bool | None = None
    pr_approved: bool | None = None
    credential_ready: bool | None = None
    branch_info: BranchInfo | None = None
    findings: tuple[FileFinding, ...] = ()
    errors: tuple[str, ...] = ()
    actual_base_sha: str | None = None
    actual_head: str | None = None
    actual_remote: str | None = None
    file_count: int | None = None
    manifest_digest: str | None = None


@dataclasses.dataclass(frozen=True)
class DryRunResult:
    push_command: str | None
    pr_command: str | None
    pr_title: str | None
    pr_body: str | None
    rollback_command: str | None


@dataclasses.dataclass(frozen=True)
class StewardResult:
    validation: ValidationResult
    dry_run: DryRunResult | None
    mutation_status: str  # "none", "dry_run_only", "executed"
    stop_reason: str | None
    evidence_paths: tuple[str, ...]
    recommended_next_action: str


def parse_publication_manifest(data: dict[str, Any]) -> PublicationManifest:
    repo_data = data.get("repository", {})
    manifest_data = data.get("manifest", {})
    approval_data = data.get("approval", {})
    cred_data = data.get("credentials", {})

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
        approval=ApprovalState(
            push_approved=bool(approval_data.get("push_approved", False)),
            pr_approved=bool(approval_data.get("pr_approved", False)),
            approved_by=approval_data.get("approved_by"),
            approval_ref=approval_data.get("approval_ref"),
        ),
        credentials=CredentialMechanism(
            mechanism=cred_data.get("mechanism", "gh_cli"),
        ),
        evidence_output_dir=data.get("evidence", {}).get("output_dir", ""),
    )
