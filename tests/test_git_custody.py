import subprocess
from pathlib import Path
from tools.git_steward.custody import LocalCommitManifest, execute_local_commit, validate_git_custody_permissions, _digest

def git(repo, *args): return subprocess.run(["git", *args], cwd=repo, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
def setup(tmp_path):
    repo=tmp_path/"repo"; repo.mkdir(); git(repo,"init"); git(repo,"config","user.email","t@example.invalid"); git(repo,"config","user.name","T"); (repo/"base.txt").write_text("base"); git(repo,"add","base.txt"); git(repo,"commit","-m","base"); base=git(repo,"rev-parse","HEAD"); git(repo,"switch","-c","custody/task"); (repo/"change.txt").write_text("change"); archive=tmp_path/"archive"; archive.write_text("accepted"); return repo,base,archive
def manifest(repo,base,archive,**overrides):
    auth={"task":"ok"}; acceptance={"checker":"accept"}; d=dict(task_id="t-1",repository=str(repo),base_sha=base,branch="custody/task",allowed_paths=("change.txt",),denied_paths=("_internal/x",),authority_digest=_digest(auth),acceptance_digest=_digest(acceptance),checker_disposition="HERMES_ACCEPT",archive_paths=(str(archive),),commit_message="test: custody")
    d.update(overrides); return LocalCommitManifest(**d),auth,acceptance
def test_local_custody_commits_exact_accepted_manifest(tmp_path):
    repo,base,archive=setup(tmp_path); m,a,c=manifest(repo,base,archive); result=execute_local_commit(m,a,c)
    assert result["status"]=="CUSTODY_COMMITTED" and result["committed"] is True
    assert git(repo,"status","--porcelain")==""
def test_custody_blocks_stale_authority_missing_archive_and_denied_path(tmp_path):
    repo,base,archive=setup(tmp_path); m,a,c=manifest(repo,base,archive,authority_digest="bad")
    assert execute_local_commit(m,a,c)["status"]=="CUSTODY_BLOCKED"
    m,a,c=manifest(repo,base,tmp_path/"missing"); assert execute_local_commit(m,a,c)["status"]=="CUSTODY_BLOCKED"
    (repo/"_internal").mkdir(); (repo/"_internal"/"x").write_text("no"); m,a,c=manifest(repo,base,archive); assert execute_local_commit(m,a,c)["status"]=="CUSTODY_BLOCKED"
def test_custody_blocks_checker_branch_and_remote(tmp_path):
    repo,base,archive=setup(tmp_path); m,a,c=manifest(repo,base,archive,checker_disposition="HERMES_REJECT"); assert execute_local_commit(m,a,c)["status"]=="CUSTODY_BLOCKED"
    m,a,c=manifest(repo,base,archive,branch="main"); assert execute_local_commit(m,a,c)["status"]=="CUSTODY_BLOCKED"
    git(repo,"remote","add","origin","https://example.invalid/x.git"); m,a,c=manifest(repo,base,archive); assert execute_local_commit(m,a,c)["status"]=="CUSTODY_BLOCKED"
def test_git_custody_permissions_fail_closed():
    assert validate_git_custody_permissions({"inspect":True,"local_commit":False,"push_branch":False,"create_pr":False,"merge":False,"update_approved_sha":False})==[]
    assert validate_git_custody_permissions({"inspect":True,"local_commit":True,"push_branch":True,"create_pr":False,"merge":False,"update_approved_sha":False})
