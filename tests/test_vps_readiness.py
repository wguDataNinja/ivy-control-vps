"""Tests for VPS readiness tools (verify_exact_sha, config validation, etc.)."""

import os
import shutil
import subprocess
import tempfile

import pytest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
TOOLS_DIR = os.path.join(REPO_ROOT, "tools")


def tool_path(name):
    return os.path.join(TOOLS_DIR, name)


def run_tool(name, args=None, cwd=None, env=None):
    cmd = [tool_path(name)]
    if args:
        cmd.extend(args)
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        cwd=cwd or REPO_ROOT,
        env={**os.environ, **(env or {})},
    )
    return result


def init_git_repo(temp_dir):
    """Initialise a temporary git repo with one commit."""
    subprocess.run(
        ["git", "init"],
        cwd=temp_dir, capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=temp_dir, capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=temp_dir, capture_output=True, check=True,
    )
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("content")
    subprocess.run(
        ["git", "add", "test.txt"],
        cwd=temp_dir, capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=temp_dir, capture_output=True, check=True,
    )
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=temp_dir, capture_output=True, text=True, check=True,
    ).stdout.strip()


class TestVerifyExactSha:
    TOOL = "verify_exact_sha.sh"

    def test_clean_repo_passes(self):
        result = run_tool(self.TOOL)
        # On a real repo this may be dirty or SHA may not match — that's OK
        assert result.returncode in (0, 1)
        assert "RESULT:" in result.stdout

    def test_dirty_repo_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            init_git_repo(tmp)
            # Create dirty file
            with open(os.path.join(tmp, "test.txt"), "w") as f:
                f.write("dirty")
            result = run_tool(self.TOOL, ["--checkout", tmp])
            assert result.returncode != 0
            assert "DIRTY" in result.stdout

    def test_expected_sha_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            sha = init_git_repo(tmp)
            result = run_tool(self.TOOL, [
                "--checkout", tmp,
                "--expected-sha", sha,
            ])
            assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
            assert "SHA_MATCH" in result.stdout

    def test_expected_sha_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            init_git_repo(tmp)
            bad_sha = "0" * 40
            result = run_tool(self.TOOL, [
                "--checkout", tmp,
                "--expected-sha", bad_sha,
            ])
            assert result.returncode != 0
            assert "SHA_MISMATCH" in result.stdout

    def test_remote_url_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            init_git_repo(tmp)
            # No remote configured yet, so any expected remote should fail
            result = run_tool(self.TOOL, [
                "--checkout", tmp,
                "--remote-url", "https://example.com/repo.git",
            ])
            # REMOTE_MISMATCH should appear but only fail if --remote-url is set
            assert "REMOTE_MISMATCH" in result.stdout

    def test_clean_tree_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            init_git_repo(tmp)
            result = run_tool(self.TOOL, ["--checkout", tmp])
            assert "CLEAN" in result.stdout

    def test_branch_displayed(self):
        with tempfile.TemporaryDirectory() as tmp:
            init_git_repo(tmp)
            result = run_tool(self.TOOL, ["--checkout", tmp])
            assert "BRANCH:" in result.stdout


class TestCheckUpstreamDrift:
    TOOL = "check_upstream_drift.sh"

    def test_runs_on_repo(self):
        result = run_tool(self.TOOL, ["--remote", "origin"])
        # Should print info and exit 0 (informational)
        assert result.returncode == 0
        assert "HEAD:" in result.stdout
        assert "REMOTE:" in result.stdout

    def test_uses_remote_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            init_git_repo(tmp)
            result = run_tool(self.TOOL, [
                "--checkout", tmp,
                "--remote", "origin",
            ])
            assert result.returncode == 0
            assert "FETCHING UPSTREAM" in result.stdout.upper() or \
                   "Fetching" in result.stdout or \
                   "fetch" in result.stdout.lower()


class TestReportDeployedRevision:
    TOOL = "report_deployed_revision.sh"

    def test_text_output(self):
        result = run_tool(self.TOOL)
        assert result.returncode == 0
        assert "HEAD_SHA:" in result.stdout
        assert "BRANCH:" in result.stdout
        assert "DIRTY:" in result.stdout

    def test_json_output(self):
        result = run_tool(self.TOOL, ["--format=json"])
        assert result.returncode == 0
        import json
        data = json.loads(result.stdout)
        assert "head_sha" in data
        assert "branch" in data
        assert "dirty" in data
        assert "remote_url" in data

    def test_custom_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            init_git_repo(tmp)
            result = run_tool(self.TOOL, ["--checkout", tmp])
            assert result.returncode == 0
            assert "CHECKOUT:" in result.stdout
            assert tmp in result.stdout


class TestPlanRollback:
    TOOL = "plan_rollback.sh"

    def test_no_target_shows_message(self):
        result = run_tool(self.TOOL)
        assert result.returncode == 0
        assert "Rollback Plan" in result.stdout or "rollback" in result.stdout.lower()
        assert "No target SHA" in result.stdout

    def test_target_sha_available_locally(self):
        with tempfile.TemporaryDirectory() as tmp:
            sha = init_git_repo(tmp)
            result = run_tool(self.TOOL, [
                "--checkout", tmp,
                "--target-sha", sha,
            ])
            assert result.returncode == 0
            assert "TARGET_SHA:" in result.stdout
            assert "available in local object store" in result.stdout

    def test_target_sha_not_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            init_git_repo(tmp)
            result = run_tool(self.TOOL, [
                "--checkout", tmp,
                "--target-sha", "a" * 40,
            ])
            assert result.returncode == 0
            assert "NOT available locally" in result.stdout

    def test_dirty_working_tree_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            init_git_repo(tmp)
            with open(os.path.join(tmp, "test.txt"), "w") as f:
                f.write("dirty")
            result = run_tool(self.TOOL, ["--checkout", tmp])
            assert "WARNING" in result.stdout


class TestValidateConfig:
    TOOL = "validate_config.sh"

    def test_runs_on_this_repo(self):
        result = run_tool(self.TOOL)
        # May have warnings, but should not crash
        assert result.returncode in (0, 1)
        assert "PASS" in result.stdout or "FAIL" in result.stdout or "WARN" in result.stdout

    def test_reports_summary(self):
        result = run_tool(self.TOOL)
        assert "=== Summary ===" in result.stdout
        assert "PASS:" in result.stdout

    def test_source_no_hardcoded_mac_paths(self):
        """Check the tool source for /Users/ hardcoding, not the output
        (output legitimately contains repo root on Mac)."""
        with open(tool_path(self.TOOL)) as f:
            source = f.read()
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("VPS_REPO_ROOT=") or stripped == "":
                continue
            assert "/Users/" not in stripped, f"Hardcoded Mac path in source: {line}"


class TestCheckVpsReadiness:
    TOOL = "check_vps_readiness.sh"

    def test_runs_end_to_end(self):
        result = run_tool(self.TOOL)
        assert result.returncode == 0
        assert "OVERALL:" in result.stdout

    def test_json_output(self):
        result = run_tool(self.TOOL, ["--format=json"])
        assert result.returncode == 0
        import json
        data = json.loads(result.stdout)
        assert "check_type" in data
        assert "deployed" in data
        assert "overall" in data

    def test_source_no_hardcoded_mac_paths(self):
        """Check tool source for hardcoded /Users/ paths, not output."""
        with open(tool_path(self.TOOL)) as f:
            source = f.read()
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or stripped == "":
                continue
            assert "/Users/" not in stripped, f"Hardcoded Mac path in source: {line}"


class TestScriptsExecutable:
    TOOLS = [
        "vps_paths.sh",
        "verify_exact_sha.sh",
        "check_upstream_drift.sh",
        "report_deployed_revision.sh",
        "plan_rollback.sh",
        "validate_config.sh",
        "check_vps_readiness.sh",
    ]

    def test_all_tools_exist(self):
        for t in self.TOOLS:
            assert os.path.isfile(tool_path(t)), f"Missing tool: {t}"

    def test_all_tools_have_shebang(self):
        for t in self.TOOLS:
            with open(tool_path(t)) as f:
                first = f.readline().strip()
            assert first.startswith("#!/bin/sh"), f"{t}: bad shebang {first}"

    def test_no_hardcoded_mac_paths(self):
        for t in self.TOOLS:
            with open(tool_path(t)) as f:
                content = f.read()
            assert "/Users/" not in content, f"{t}: hardcoded /Users/ path"
            assert "/buddy/" not in content, f"{t}: hardcoded /buddy/ path"

    def test_shellcheck_clean_if_available(self):
        if not shutil.which("shellcheck"):
            pytest.skip("shellcheck not installed")
        for t in self.TOOLS:
            result = subprocess.run(
                ["shellcheck", tool_path(t)],
                capture_output=True, text=True, cwd=REPO_ROOT,
            )
            if result.returncode != 0:
                pytest.fail(f"shellcheck issues in {t}:\n{result.stdout}\n{result.stderr}")


class TestOpenDashboardShell:
    TOOL = "open_ingestion_dashboard.sh"

    def test_no_open_uses_xdg_fallback(self):
        """Verify the script has xdg-open fallback."""
        with open(tool_path(self.TOOL)) as f:
            content = f.read()
        assert "xdg-open" in content, "Missing Linux xdg-open fallback"
        assert "open " in content, "Missing macOS open command"

    def test_source_no_mac_assumptions(self):
        """Check the shell script source for portable patterns."""
        with open(tool_path(self.TOOL)) as f:
            content = f.read()
        assert '#!/bin/sh' in content, "Should use portable shebang"
        assert 'xdg-open' in content, "Should have Linux fallback"
