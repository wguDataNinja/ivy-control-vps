import json
import subprocess
import sys
from pathlib import Path

import tools.hermes_orchestrator.core as hermes_core
from tools.hermes_orchestrator.core import (
    analyze_eligibility,
    archive_task_artifacts,
    build_artifact_manifest,
    create_run_state,
    intake_repository,
    parse_roadmap,
    rank_repositories,
    reconstruct_run_state,
    resolve_authority,
    resolve_repository_context,
    runtime_diagnostic,
    validate_artifact_destination,
)


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def init_repo(path: Path) -> None:
    path.mkdir()
    git(path, "init")
    git(path, "config", "user.email", "test@example.invalid")
    git(path, "config", "user.name", "Test")
    (path / "README.md").write_text("# Test\n", encoding="utf-8")
    git(path, "add", "README.md")
    git(path, "commit", "-m", "initial")


def make_candidate(tmp_path: Path, slug: str, readme: str = "", agents: str = "", roadmap: str = "", registry: bool = False) -> dict:
    root = tmp_path / slug
    root.mkdir()
    if readme:
        (root / "README.md").write_text(readme, encoding="utf-8")
    if agents:
        (root / "AGENTS.md").write_text(agents, encoding="utf-8")
    if roadmap:
        (root / "ROADMAP.md").write_text(roadmap, encoding="utf-8")
    if registry:
        (root / "registry").mkdir()
        (root / "registry" / "repos.yaml").write_text("repos:\n- name: ivy-control-vps\n", encoding="utf-8")
    return {"slug": slug, "path": str(root)}


def write_control(root: Path, slug: str, local_path: Path, hermes_scope: str = "read-only", remote: str | None = None) -> None:
    control_dir = root / "repos" / slug
    control_dir.mkdir(parents=True)
    remote_text = f'"{remote}"' if remote else "null"
    control_dir.joinpath("CONTROL.md").write_text(
        f"""---
repository:
  slug: {slug}
  remote: {remote_text}
  default_branch: main
  approved_sha: null
  local_path: "{local_path}"
hermes:
  scope: "{hermes_scope}"
roadmap:
  blockers: []
  next_task: "Perform read-only intake."
buddy_decisions: []
---

# {slug} Control

## Current Blocker

none
""",
        encoding="utf-8",
    )


def test_repository_context_classifies_dirty_paths(tmp_path):
    repo = tmp_path / "repo"
    init_repo(repo)
    (repo / "README.md").write_text("# Changed\n", encoding="utf-8")
    (repo / "_internal").mkdir()
    (repo / "_internal" / "note.md").write_text("private\n", encoding="utf-8")

    context = resolve_repository_context(repo, "test-repo")

    assert context["repository"]["is_git_repository"] is True
    paths = {item["path"]: item for item in context["dirty_state"]}
    assert paths["README.md"]["type"] == "docs"
    assert paths["_internal/"]["recommended_disposition"] == "private-only"
    assert context["lock_state"] == "locked"


def test_parse_roadmap_extracts_packages(tmp_path):
    roadmap = tmp_path / "ROADMAP.md"
    roadmap.write_text(
        """# Roadmap

**Status:** Approved execution authority

### PKB-FL-01 — First Task

**Outcome:** Do the first thing.

**Dependencies:** None.

**Validation:** `pytest`

**Human gate:** Buddy approves.

### PKB-FL-02 — Second Task

**Outcome:** Do the second thing.

**Dependencies:** PKB-FL-01.
""",
        encoding="utf-8",
    )

    parsed = parse_roadmap(roadmap)

    assert parsed["status"] == "Approved execution authority"
    assert [task["task_id"] for task in parsed["tasks"]] == ["PKB-FL-01", "PKB-FL-02"]
    assert parsed["tasks"][0]["validation"] == "`pytest`"


def test_eligibility_selects_first_dependency_free_task(tmp_path):
    roadmap = {
        "tasks": [
            {"task_id": "A-01", "title": "first", "dependencies": "None."},
            {"task_id": "A-02", "title": "second", "dependencies": "A-01."},
        ]
    }
    intent = {"intent_id": "intent-test"}
    context = {"repository": {"slug": "repo"}, "stop_reasons": []}

    result = analyze_eligibility(intent, context, roadmap)

    assert result["selected_task"]["task_id"] == "A-01"
    assert result["eligible_tasks"][1]["eligible"] is False


def test_restart_reconstruction_preserves_dispatch(tmp_path):
    intent = {"intent_id": "intent-test", "objective": "plan only"}
    state = create_run_state(
        intent,
        "DISPATCH",
        {"packet": "packet.md"},
        {"task_packet": "packet.md", "expected_report": "report.md"},
    )
    path = tmp_path / "run-state.json"
    path.write_text(json.dumps(state), encoding="utf-8")

    reconstructed = reconstruct_run_state(path)

    assert reconstructed["run_id"] == state["run_id"]
    assert reconstructed["in_flight_dispatch"]["expected_report"] == "report.md"
    assert "monitor" in reconstructed["next_action"]


def test_cli_context_outputs_json(tmp_path):
    repo = tmp_path / "repo"
    init_repo(repo)

    proc = subprocess.run(
        [sys.executable, "-m", "tools.hermes_orchestrator", "context", "--repo", str(repo)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    data = json.loads(proc.stdout)
    assert data["schema_version"] == "hermes.repository_context.v1"


def test_runtime_diagnostic_reports_matching_memory_and_entrypoints(tmp_path):
    source = tmp_path / "MEMORY.source.md"
    live = tmp_path / "MEMORY.live.md"
    backup = tmp_path / "MEMORY.live.md.bak"
    source.write_text("memory\n", encoding="utf-8")
    live.write_text("memory\n", encoding="utf-8")
    backup.write_text("old memory\n", encoding="utf-8")
    canonical = tmp_path / "hermes"
    alternate = tmp_path / "hermes-alt"
    script = "#!/usr/bin/env sh\nprintf 'usage: hermes\\n'\n"
    canonical.write_text(script, encoding="utf-8")
    alternate.write_text(script, encoding="utf-8")
    canonical.chmod(0o755)
    alternate.chmod(0o755)

    result = runtime_diagnostic(source, live, canonical, alternate, backup)

    assert result["status"] == "PASS"
    assert result["memory"]["drift"] is False
    assert result["backup"]["restore_command"].endswith(str(live))
    assert result["canonical_executable"]["help_check"]["returncode"] == 0


def test_authority_resolves_single_unambiguous_control_plane(tmp_path):
    candidate = make_candidate(tmp_path, "ivy-control-vps", readme="IvyControlVPS is the portfolio control plane.\n")

    result = resolve_authority([candidate])

    assert result["status"] == "AUTHORITY_RESOLVED"
    assert result["active_control_plane"] == "ivy-control-vps"
    assert result["sufficient_to_continue"] is True


def test_authority_detects_ivy_control_and_vps_conflict(tmp_path):
    old = make_candidate(tmp_path, "ivy-control", readme="IVY Control is Buddy's local control plane.\n", registry=True)
    new = make_candidate(tmp_path, "ivy-control-vps", readme="IvyControlVPS is the portfolio control plane.\n")

    result = resolve_authority([old, new])

    assert result["status"] == "AUTHORITY_CONFLICT"
    assert result["conflict_detected"] is True


def test_registry_taxonomy_alone_is_insufficient_authority(tmp_path):
    candidate = make_candidate(tmp_path, "ivy-control", registry=True)

    result = resolve_authority([candidate])

    assert result["status"] == "AUTHORITY_INSUFFICIENT_EVIDENCE"
    assert result["registry_taxonomy_policy"] == "inventory_only_not_authority"


def test_explicit_redirect_resolves_to_target_control_plane(tmp_path):
    old = make_candidate(
        tmp_path,
        "ivy-control",
        readme="IVY Control is Buddy's local control plane. This repository redirects governance to ivy-control-vps.\n",
        registry=True,
    )
    new = make_candidate(tmp_path, "ivy-control-vps", readme="IvyControlVPS is the portfolio control plane.\n")

    result = resolve_authority([old, new])

    assert result["status"] == "AUTHORITY_RESOLVED"
    assert result["active_control_plane"] == "ivy-control-vps"
    assert result["delegation_or_redirect"][0]["from"] == "ivy-control"


def test_conflicting_authority_claims_cause_safe_stop(tmp_path):
    first = make_candidate(tmp_path, "control-a", readme="Control A is the portfolio control plane.\n")
    second = make_candidate(tmp_path, "control-b", readme="Control B is the portfolio control plane.\n")

    result = resolve_authority([first, second])

    assert result["status"] == "AUTHORITY_CONFLICT"
    assert result["sufficient_to_continue"] is False


def test_artifact_manifest_uses_repository_namespace(tmp_path):
    result = build_artifact_manifest("PKB-FL-01", ["palworld-kb"], tmp_path / "orchestration")

    assert result["namespace"] == "repository"
    assert result["task_id"] == "PKB-FL-01"
    assert result["task_root"].endswith("orchestration/repos/palworld-kb/tasks/PKB-FL-01")


def test_artifact_manifest_uses_cross_repo_namespace(tmp_path):
    result = build_artifact_manifest("portfolio-01", ["palworld-kb", "ivy-control-vps"], tmp_path / "orchestration")

    assert result["namespace"] == "cross_repository"
    assert result["repositories"] == ["ivy-control-vps", "palworld-kb"]
    assert result["task_root"].endswith("orchestration/cross-repo/tasks/portfolio-01")


def test_archive_task_artifacts_copies_validated_task_without_moving_active_queue(tmp_path):
    active = tmp_path / "active"
    active.mkdir()
    packet = active / "packet.md"
    report = active / "report.md"
    validation = active / "validation.json"
    log = active / "log.md"
    packet.write_text("packet\n", encoding="utf-8")
    report.write_text("report\n", encoding="utf-8")
    validation.write_text(json.dumps({"verified_disposition": "COMPLETED_WITH_WARNINGS"}), encoding="utf-8")
    log.write_text("log\n", encoding="utf-8")

    result = archive_task_artifacts(
        "PKB-FL-01",
        ["palworld-kb"],
        packet,
        report,
        validation,
        tmp_path / "orchestration",
        log,
    )

    assert result["status"] == "ARCHIVED"
    assert packet.exists()
    assert report.exists()
    task_root = tmp_path / "orchestration" / "repos" / "palworld-kb" / "tasks" / "PKB-FL-01"
    assert (task_root / "task-packet.md").read_text(encoding="utf-8") == "packet\n"
    assert (task_root / "execution-report.md").read_text(encoding="utf-8") == "report\n"
    assert (task_root / "validation-report.json").exists()
    assert (task_root / "execution-log.md").exists()
    assert (task_root / "README.md").exists()
    assert (task_root / "task.md").exists()
    assert (task_root / "final-report.md").exists()
    manifest = json.loads((task_root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["active_queue_semantics"] == "copied_not_moved"


def test_archive_task_artifacts_blocks_unaccepted_validation_without_writes(tmp_path):
    packet = tmp_path / "packet.md"
    report = tmp_path / "report.md"
    validation = tmp_path / "validation.json"
    packet.write_text("packet\n", encoding="utf-8")
    report.write_text("report\n", encoding="utf-8")
    validation.write_text(json.dumps({"verified_disposition": "HUMAN_DECISION_REQUIRED"}), encoding="utf-8")

    result = archive_task_artifacts(
        "PKB-FL-01",
        ["palworld-kb"],
        packet,
        report,
        validation,
        tmp_path / "orchestration",
    )

    assert result["status"] == "ARCHIVE_BLOCKED"
    assert result["files_copied"] == []
    assert not (tmp_path / "orchestration").exists()


def test_artifact_destination_accepts_canonical_run_and_archive_paths():
    inbox = validate_artifact_destination(Path("_internal/inbox/runs/2026-07-28-portfolio-readiness/task-packet.md"))
    outbox = validate_artifact_destination(Path("_internal/outbox/runs/session-14-palworld-kb/result-report.md"))
    repo_archive = validate_artifact_destination(Path("_internal/orchestration/repos/wgu-catalog/tasks/2026-07-28-readiness/manifest.json"))
    cross_archive = validate_artifact_destination(Path("_internal/orchestration/cross-repo/tasks/2026-07-28-portfolio-readiness/manifest.json"))

    assert inbox["status"] == "ARTIFACT_DESTINATION_ACCEPTED"
    assert outbox["accepted_location"] == "active_run_queue"
    assert repo_archive["accepted_location"] == "durable_repository_archive"
    assert cross_archive["accepted_location"] == "durable_cross_repo_archive"


def test_artifact_destination_rejects_new_bare_session_paths():
    inbox = validate_artifact_destination(Path("_internal/inbox/session-14/task.md"))
    outbox = validate_artifact_destination(Path("_internal/outbox/session-1/03-gpt-assistant-context-packet.md"))

    assert inbox["status"] == "ARTIFACT_DESTINATION_REJECTED"
    assert outbox["status"] == "ARTIFACT_DESTINATION_REJECTED"
    assert "bare session-N" in inbox["errors"][0]


def test_cli_validate_artifact_destination_rejects_bare_session_path():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.hermes_orchestrator",
            "validate-artifact-destination",
            "--path",
            "_internal/outbox/session-1/new-report.md",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    result = json.loads(proc.stdout)
    assert proc.returncode == 2
    assert result["status"] == "ARTIFACT_DESTINATION_REJECTED"


def test_intake_repository_reports_git_docs_and_archive(tmp_path, monkeypatch):
    control_root = tmp_path / "control"
    repo = tmp_path / "target"
    init_repo(repo)
    (repo / "ROADMAP.md").write_text("# Roadmap\n\nNext task pending.\n", encoding="utf-8")
    (repo / "TODO.md").write_text("# TODO\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs" / "DEPLOYMENT.md").write_text("# Deployment\n", encoding="utf-8")
    (repo / "scratch.txt").write_text("important untracked work\n", encoding="utf-8")
    write_control(control_root, "sample-repo", repo)
    monkeypatch.setattr(hermes_core, "REPO_ROOT", control_root)

    result = intake_repository("sample-repo", str(repo), "sample-intake-01", tmp_path / "archive")

    assert result["status"] == "INTAKE_COMPLETE"
    assert result["mode"] == "read_only"
    assert result["repository"]["control_record"]["match_status"] == "matched"
    assert result["git_state"]["tracking_state"] in {"tracking", "no_upstream"}
    assert result["git_state"]["untracked_count"] >= 1
    assert result["findings"]["suitability"]["read_only_analysis"] == "yes"
    assert any(doc["relative_path"] == "docs/DEPLOYMENT.md" for doc in result["documents"]["operational_documents"])
    assert result["write_actions_performed"] == []
    archive = result["archive"]
    assert archive["status"] == "ARCHIVED"
    assert archive["namespace"] == "repository"
    assert (tmp_path / "archive" / "repos" / "sample-repo" / "tasks" / "sample-intake-01" / "intake-report.md").exists()


def test_intake_repository_restricted_scope_blocks_repo_inspection(tmp_path, monkeypatch):
    control_root = tmp_path / "control"
    repo = tmp_path / "restricted"
    init_repo(repo)
    write_control(control_root, "restricted-repo", repo, hermes_scope="none")
    monkeypatch.setattr(hermes_core, "REPO_ROOT", control_root)

    result = intake_repository("restricted-repo", str(repo), "restricted-intake-01")

    assert result["status"] == "RESTRICTED"
    assert result["git_state"]["observed_changes_assessment"] == "not inspected because intake blocked before repository access"
    assert result["findings"]["suitability"]["read_only_analysis"] == "no"


def test_cli_intake_repository_writes_json_and_report(tmp_path):
    control_root = tmp_path / "control"
    repo = tmp_path / "target"
    init_repo(repo)
    write_control(control_root, "sample-repo", repo)
    script = (
        "import sys, tools.hermes_orchestrator.core as c; "
        f"c.REPO_ROOT = {str(control_root)!r}; "
        "raise SystemExit(c.main(sys.argv[1:]))"
    )
    json_out = tmp_path / "intake.json"
    report_out = tmp_path / "intake.md"

    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            "intake-repository",
            "--repo",
            "sample-repo",
            "--path",
            str(repo),
            "--json-out",
            str(json_out),
            "--report-out",
            str(report_out),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    result = json.loads(proc.stdout)
    assert result["status"] == "INTAKE_COMPLETE"
    assert json.loads(json_out.read_text(encoding="utf-8"))["status"] == "INTAKE_COMPLETE"
    assert "Repository Intake Report" in report_out.read_text(encoding="utf-8")


def test_repository_ranking_includes_control_plane_by_default():
    intent = {
        "intent_id": "intent-test",
        "repositories": ["all"],
        "scope_boundary": {"repository_priority": ["ivy-control-vps", "palworld-kb"]},
    }
    contexts = [
        {
            "repository": {"slug": "ivy-control-vps", "path": "/repo/control"},
            "dirty_state": [],
            "authority": {"next_authorized_work": "orchestration policy refinement", "current_blocker": "none"},
        },
        {
            "repository": {"slug": "palworld-kb", "path": "/repo/palworld"},
            "dirty_state": [{"path": "docs/x.md"}],
            "authority": {"next_authorized_work": "footprint review", "current_blocker": "none"},
        },
    ]

    authority = {
        "status": "AUTHORITY_RESOLVED",
        "active_control_plane": "ivy-control-vps",
        "documents_checked": [{"path": "README.md", "exists": True}],
        "authority_claims": [{"claim_type": "control_plane_authority", "repository": "ivy-control-vps"}],
        "conflict_detected": False,
    }

    result = rank_repositories(intent, contexts, authority)

    assert result["active_control_plane"] == "ivy-control-vps"
    assert [row["repository"] for row in result["candidates"]] == ["ivy-control-vps", "palworld-kb"]
    assert result["recommended_repository"]["repository"] == "ivy-control-vps"
    assert result["recommended_repository"]["executor_selection"] == "not evaluated here"


def test_ranking_cannot_proceed_before_authority_resolution():
    intent = {"intent_id": "intent-test", "repositories": ["all"]}
    contexts = [{"repository": {"slug": "ivy-control-vps"}, "dirty_state": [], "authority": {}}]
    authority = {"status": "AUTHORITY_INSUFFICIENT_EVIDENCE", "authority_claims": [], "documents_checked": []}

    result = rank_repositories(intent, contexts, authority)

    assert result["status"] == "AUTHORITY_INSUFFICIENT_EVIDENCE"
    assert result["recommended_repository"] is None


def test_cli_plan_dry_run_writes_no_files(tmp_path):
    intent = tmp_path / "intent.json"
    context = tmp_path / "context.json"
    roadmap = tmp_path / "roadmap.json"
    authority = tmp_path / "authority.json"
    intent.write_text(
        json.dumps({"intent_id": "intent-test", "objective": "draft only", "repositories": ["repo"]}),
        encoding="utf-8",
    )
    context.write_text(json.dumps({"repository": {"slug": "repo"}, "stop_reasons": []}), encoding="utf-8")
    roadmap.write_text(
        json.dumps({"roadmap_path": "ROADMAP.md", "tasks": [{"task_id": "A-01", "title": "First", "dependencies": "None."}]}),
        encoding="utf-8",
    )
    authority.write_text(
        json.dumps({
            "status": "AUTHORITY_RESOLVED",
            "active_control_plane": "ivy-control-vps",
            "documents_checked": [{"path": "README.md", "exists": True}],
            "authority_claims": [{"claim_type": "control_plane_authority", "repository": "ivy-control-vps"}],
            "conflict_detected": False,
        }),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.hermes_orchestrator",
            "plan",
            "--intent",
            str(intent),
            "--context",
            str(context),
            "--roadmap",
            str(roadmap),
            "--authority-resolution",
            str(authority),
            "--dry-run",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    result = json.loads(proc.stdout)
    assert result["active_control_plane"] == "ivy-control-vps"
    assert result["files_written"] == []
    assert "**Status:** DRAFT_NOT_APPROVED" in result["draft_packet"]


def test_cli_plan_dry_run_writes_no_files_when_authority_unresolved(tmp_path):
    intent = tmp_path / "intent.json"
    context = tmp_path / "context.json"
    roadmap = tmp_path / "roadmap.json"
    authority = tmp_path / "authority.json"
    out_dir = tmp_path / "should-not-exist"
    intent.write_text(json.dumps({"intent_id": "intent-test", "objective": "draft only", "repositories": ["repo"]}), encoding="utf-8")
    context.write_text(json.dumps({"repository": {"slug": "repo"}, "stop_reasons": []}), encoding="utf-8")
    roadmap.write_text(json.dumps({"roadmap_path": "ROADMAP.md", "tasks": [{"task_id": "A-01", "title": "First"}]}), encoding="utf-8")
    authority.write_text(
        json.dumps({"status": "AUTHORITY_CONFLICT", "active_control_plane": None, "documents_checked": [{"exists": True}], "authority_claims": [], "conflict_detected": True}),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.hermes_orchestrator",
            "plan",
            "--intent",
            str(intent),
            "--context",
            str(context),
            "--roadmap",
            str(roadmap),
            "--authority-resolution",
            str(authority),
            "--out-dir",
            str(out_dir),
            "--dry-run",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    result = json.loads(proc.stdout)
    assert proc.returncode == 2
    assert result["status"] == "AUTHORITY_CONFLICT"
    assert result["files_written"] == []
    assert not out_dir.exists()
