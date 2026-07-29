import json
from tools.hermes_orchestrator.task_directory import validate_task_directory
def make(root, final="# Canonical Final Report\n\n## Detailed evidence\n\n/Users/buddy/projects/example/report.md\n", index="[task](task.md) [final](final-report.md)\n"):
    root.mkdir(); (root/"README.md").write_text(index); (root/"task.md").write_text("task"); (root/"final-report.md").write_text(final); (root/"manifest.json").write_text(json.dumps({}))
def test_task_directory_accepts_one_human_entrypoint(tmp_path):
    root=tmp_path/"task"; make(root); assert validate_task_directory(root,True)==[]
def test_task_directory_fails_missing_final_link_or_ambiguous_final(tmp_path):
    root=tmp_path/"task"; make(root,index="[task](task.md)"); assert "task index does not link canonical final report" in validate_task_directory(root)
    root2=tmp_path/"task2"; make(root2,final="# Canonical Final Report\n# Canonical Final Report\n## Detailed evidence\n"); assert "final report must declare exactly one canonical result" in validate_task_directory(root2)
