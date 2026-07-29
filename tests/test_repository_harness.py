import json
from pathlib import Path
from tools.validate_repository_harness import validate

def make(root: Path, **overrides):
    root.mkdir()
    for name in ("README.md", "AGENTS.md", "ROADMAP.md", "tasks/one.md"):
        path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text("x")
    data = {"schema_version": 1, "repository": "demo", "purpose": "demo", "authority_files": ["README.md", "AGENTS.md", "ROADMAP.md"], "active_task": "tasks/one.md", "health_commands": ["git status --short --branch"], "task_paths": {"packets": "tasks", "reports": "reports", "journal": "JOURNAL.md"}, "git": {"writer": "Git Steward", "remote_mutation": False}}
    data.update(overrides)
    (root / "HARNESS.json").write_text(json.dumps(data))

def test_valid_harness(tmp_path):
    make(tmp_path / "repo")
    assert validate(tmp_path / "repo") == []

def test_harness_rejects_missing_active_task_and_unsafe_authority(tmp_path):
    root = tmp_path / "repo"; make(root, active_task="tasks/missing.md", authority_files=["../secret"])
    errors = validate(root)
    assert "active_task must be null or an existing relative file" in errors
    assert "authority file is not a safe relative path: '../secret'" in errors
