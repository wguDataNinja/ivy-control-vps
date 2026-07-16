"""Tests for VPS path class definitions (vps_paths.sh)."""

import os
import shutil
import subprocess
import tempfile

import pytest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
VPS_PATHS_SCRIPT = os.path.join(REPO_ROOT, "tools", "vps_paths.sh")


def source_vps_paths(env_overrides=None):
    """Source vps_paths.sh and return the PATH variables it exports."""
    cmd = ". {} && vps_print_paths".format(shlex_quote(VPS_PATHS_SCRIPT))
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    result = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, env=env, cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        pytest.fail(f"vps_paths.sh failed: {result.stderr}")
    paths = {}
    for line in result.stdout.strip().splitlines():
        if "=" in line:
            key, val = line.split("=", 1)
            paths[key.strip()] = val.strip()
    return paths


def shlex_quote(s):
    return "'" + s.replace("'", "'\\''") + "'"


class TestVPSSourced:
    def test_can_source(self):
        paths = source_vps_paths()
        assert "VPS_REPO_ROOT" in paths
        assert "VPS_STATE_DIR" in paths
        assert "VPS_GENERATED_DIR" in paths
        assert "VPS_CONFIG_DIR" in paths
        assert "VPS_DATA_DIR" in paths
        assert "VPS_LOG_DIR" in paths
        assert "VPS_BACKUP_DIR" in paths
        assert "VPS_SHA_REGISTRY" in paths

    def test_generated_dir_outside_repo_root(self):
        paths = source_vps_paths()
        repo_root = paths["VPS_REPO_ROOT"]
        generated = paths["VPS_GENERATED_DIR"]
        assert not generated.startswith(repo_root + "/"), \
            f"VPS_GENERATED_DIR {generated} should not be under {repo_root}"

    def test_config_dir_outside_repo_root(self):
        paths = source_vps_paths()
        repo_root = paths["VPS_REPO_ROOT"]
        cfg = paths["VPS_CONFIG_DIR"]
        assert not cfg.startswith(repo_root + "/"), \
            f"VPS_CONFIG_DIR {cfg} should not be under {repo_root}"

    def test_data_dir_outside_repo_root(self):
        paths = source_vps_paths()
        repo_root = paths["VPS_REPO_ROOT"]
        data = paths["VPS_DATA_DIR"]
        assert not data.startswith(repo_root + "/"), \
            f"VPS_DATA_DIR {data} should not be under {repo_root}"

    def test_log_dir_outside_repo_root(self):
        paths = source_vps_paths()
        repo_root = paths["VPS_REPO_ROOT"]
        log = paths["VPS_LOG_DIR"]
        assert not log.startswith(repo_root + "/"), \
            f"VPS_LOG_DIR {log} should not be under {repo_root}"

    def test_backup_dir_outside_repo_root(self):
        paths = source_vps_paths()
        repo_root = paths["VPS_REPO_ROOT"]
        backup = paths["VPS_BACKUP_DIR"]
        assert not backup.startswith(repo_root + "/"), \
            f"VPS_BACKUP_DIR {backup} should not be under {repo_root}"

    def test_default_state_dir_is_home_dot_ivy(self):
        paths = source_vps_paths()
        home = os.path.expanduser("~")
        expected = os.path.join(home, ".ivy-control-vps")
        assert paths["VPS_STATE_DIR"] == expected

    def test_env_overrides_state_dir(self):
        paths = source_vps_paths({"VPS_STATE_DIR": "/tmp/test-vps-state"})
        assert paths["VPS_STATE_DIR"] == "/tmp/test-vps-state"
        assert paths["VPS_GENERATED_DIR"].startswith("/tmp/test-vps-state")

    def test_env_overrides_all(self):
        overrides = {
            "VPS_STATE_DIR": "/custom/state",
            "VPS_GENERATED_DIR": "/custom/gen",
            "VPS_CONFIG_DIR": "/custom/cfg",
            "VPS_DATA_DIR": "/custom/data",
            "VPS_LOG_DIR": "/custom/logs",
            "VPS_BACKUP_DIR": "/custom/backups",
            "VPS_SHA_REGISTRY": "/custom/shas.json",
        }
        paths = source_vps_paths(overrides)
        for key, val in overrides.items():
            assert paths[key] == val, f"{key}: expected {val}, got {paths[key]}"

    def test_ensure_dirs_creates_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            overrides = {
                "VPS_STATE_DIR": tmp,
                "HOME": tmp,
            }
            paths = source_vps_paths(overrides)
            cmd = ". {} && vps_ensure_dirs".format(shlex_quote(VPS_PATHS_SCRIPT))
            result = subprocess.run(
                ["bash", "-c", cmd],
                capture_output=True, text=True,
                env={**os.environ, **overrides},
                cwd=REPO_ROOT,
            )
            assert result.returncode == 0, f"vps_ensure_dirs failed: {result.stderr}"
            for d in [paths["VPS_GENERATED_DIR"], paths["VPS_CONFIG_DIR"],
                      paths["VPS_DATA_DIR"], paths["VPS_LOG_DIR"],
                      paths["VPS_BACKUP_DIR"]]:
                assert os.path.isdir(d), f"Directory not created: {d}"

    def test_check_paths_reports_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            overrides = {"VPS_STATE_DIR": os.path.join(tmp, "state")}
            cmd = ". {} && vps_check_paths".format(shlex_quote(VPS_PATHS_SCRIPT))
            result = subprocess.run(
                ["bash", "-c", cmd],
                capture_output=True, text=True,
                env={**os.environ, **overrides},
                cwd=REPO_ROOT,
            )
            assert result.returncode != 0, "Should fail when dirs missing"
            assert "MISSING" in result.stderr

    def test_check_paths_passes_when_dirs_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            overrides = {"VPS_STATE_DIR": tmp}
            cmd = ". {} && vps_ensure_dirs && vps_check_paths".format(
                shlex_quote(VPS_PATHS_SCRIPT))
            result = subprocess.run(
                ["bash", "-c", cmd],
                capture_output=True, text=True,
                env={**os.environ, **overrides},
                cwd=REPO_ROOT,
            )
            assert result.returncode == 0, f"check_paths failed: {result.stderr}"


class TestScriptExecutable:
    def test_vps_paths_is_readable(self):
        assert os.path.isfile(VPS_PATHS_SCRIPT)

    def test_vps_paths_is_shell_script(self):
        with open(VPS_PATHS_SCRIPT) as f:
            first = f.readline().strip()
            assert first.startswith("#!/bin/sh"), f"Bad shebang: {first}"


class TestPortability:
    def test_no_hardcoded_mac_paths(self):
        with open(VPS_PATHS_SCRIPT) as f:
            content = f.read()
        assert "/Users/" not in content, "Hardcoded Mac path found"

    def test_no_open_command(self):
        with open(VPS_PATHS_SCRIPT) as f:
            content = f.read()
        assert "open " not in content, "Mac-only open command found"

    def test_shellcheck_clean(self):
        """Verify shellcheck passes (best-effort, tool may not exist)."""
        if not shutil.which("shellcheck"):
            pytest.skip("shellcheck not installed")
        result = subprocess.run(
            ["shellcheck", VPS_PATHS_SCRIPT],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            pytest.fail(f"shellcheck issues:\n{result.stdout}\n{result.stderr}")
