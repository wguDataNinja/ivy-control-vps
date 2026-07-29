"""Validation for the human-facing durable task directory convention."""
from __future__ import annotations
from pathlib import Path
REQUIRED=("README.md","task.md","final-report.md","manifest.json")
def validate_task_directory(root: Path, cross_repository: bool=False)->list[str]:
    errors=[f"missing required artifact: {n}" for n in REQUIRED if not (root/n).is_file()]
    if errors:return errors
    index=(root/"README.md").read_text(); final=(root/"final-report.md").read_text()
    if "final-report.md" not in index:errors.append("task index does not link canonical final report")
    if "task.md" not in index:errors.append("task index does not link canonical task packet")
    if final.count("# Canonical Final Report")!=1:errors.append("final report must declare exactly one canonical result")
    if "## Detailed evidence" not in final:errors.append("final report lacks detailed evidence section")
    if cross_repository and "/Users/buddy/projects/" not in final:errors.append("cross-repository final report lacks repository-qualified absolute path")
    return errors
