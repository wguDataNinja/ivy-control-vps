"""Local-only custody for one independently accepted manifest; no remote actions."""
from __future__ import annotations
import hashlib, json, subprocess
from dataclasses import dataclass
from pathlib import Path

def _digest(v: object) -> str: return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def _git(repo: Path, *args: str) -> tuple[int, str, str]:
    p = subprocess.run(["git", *args], cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return p.returncode, p.stdout, p.stderr.strip()

@dataclass(frozen=True)
class LocalCommitManifest:
    task_id: str; repository: str; base_sha: str; branch: str; allowed_paths: tuple[str, ...]; denied_paths: tuple[str, ...]; authority_digest: str; acceptance_digest: str; checker_disposition: str; archive_paths: tuple[str, ...]; commit_message: str

def validate_git_custody_permissions(v: object) -> list[str]:
    if not isinstance(v, dict): return ["git_custody must be an object"]
    needed={"inspect","local_commit","push_branch","create_pr","merge","update_approved_sha"}; errors=[f"git_custody missing {k}" for k in sorted(needed-v.keys())]
    for k in needed:
        if k in v and not isinstance(v[k], bool): errors.append(f"git_custody.{k} must be boolean")
    for k in {"push_branch","create_pr","merge","update_approved_sha"}:
        if v.get(k) is not False: errors.append(f"git_custody.{k} must be false in H4.1")
    return errors

def execute_local_commit(m: LocalCommitManifest, authority: object, acceptance: object) -> dict[str, object]:
    repo=Path(m.repository); errors=[]
    if m.checker_disposition not in {"COMPLETED","COMPLETED_WITH_WARNINGS","HERMES_ACCEPT","HERMES_ACCEPT_WITH_NOTE"}: errors.append("checker disposition is not accepted")
    if _digest(authority)!=m.authority_digest: errors.append("stale or contradictory authority digest")
    if _digest(acceptance)!=m.acceptance_digest: errors.append("stale or contradictory acceptance digest")
    if not m.task_id or not m.commit_message or not m.allowed_paths: errors.append("task_id, commit_message, and allowed_paths are required")
    if not all(Path(p).exists() for p in m.archive_paths): errors.append("required archive evidence is missing")
    code, head, _=_git(repo,"rev-parse","HEAD")
    if code or head.strip()!=m.base_sha: errors.append("pinned base SHA does not match repository HEAD")
    _, branch, _=_git(repo,"branch","--show-current")
    if not branch.strip() or branch.strip()!=m.branch: errors.append("repository is not on declared isolated branch")
    _, remotes, _=_git(repo,"remote")
    if remotes: errors.append("H4.1 local custody requires no configured remote")
    _, staged, _=_git(repo,"diff","--cached","--name-only")
    if staged.strip(): errors.append("pre-existing staged state is prohibited")
    _, status, _=_git(repo,"status","--porcelain"); paths=[line[3:] for line in status.splitlines() if line]
    invalid=[p for p in paths if p not in m.allowed_paths or p in m.denied_paths or p.startswith("_internal/")]
    if invalid: errors.append("manifest path violation: "+", ".join(sorted(invalid)))
    if errors: return {"status":"CUSTODY_BLOCKED","errors":errors,"head_before":head,"committed":False}
    rc,_,err=_git(repo,"add","--",*m.allowed_paths)
    if rc: return {"status":"CUSTODY_BLOCKED","errors":["git add failed: "+err],"head_before":head,"committed":False}
    rc,_,err=_git(repo,"commit","-m",m.commit_message)
    if rc: return {"status":"CUSTODY_STOPPED","errors":["git commit failed: "+err],"head_before":head,"committed":False}
    _,after,_=_git(repo,"rev-parse","HEAD"); _,residual,_=_git(repo,"status","--porcelain"); ok=after.strip()!=head.strip() and not residual.strip()
    return {"status":"CUSTODY_COMMITTED" if ok else "CUSTODY_STOPPED","errors":[] if ok else ["post-commit reconciliation failed"],"head_before":head,"head_after":after,"commit_evidence_digest":_digest({"manifest":m.__dict__,"head_before":head,"head_after":after}),"committed":ok}
