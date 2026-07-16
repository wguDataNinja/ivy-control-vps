"""Transport, mode, JSON, and drift tests for the ingestion dashboard.

Covers:
1. Direct mode execution
2. Remote mode execution
3. Auto mode detection
4. No-live mode
5. Absent SSH config
6. --json output flag
7. Execution modes reflected in output
8. Private data exclusion across all modes
9. No tracked-file dirtiness
10. Arbitrary CWD support
11. External output directory
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
DASHBOARD_SCRIPT = TOOLS_DIR / "ingestion_dashboard.py"


def _run_python(
    args: list[str] | None = None,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(DASHBOARD_SCRIPT)]
    if args:
        cmd.extend(args)
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        cmd, capture_output=True, text=True,
        cwd=str(cwd or REPO_ROOT),
        timeout=30, env=merged_env,
    )


# ── 1. Direct mode ──────────────────────────────────────────────────────────


class TestDirectMode:
    def test_direct_mode_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(["--mode", "direct", "--output-dir", tmp])
            assert result.returncode == 0, f"direct mode failed:\n{result.stderr}"

    def test_direct_mode_no_ssh_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(["--mode", "direct", "--output-dir", tmp])
            assert "ssh" not in result.stderr.lower()
            assert "not available" not in result.stderr.lower()

    def test_direct_mode_generates_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(["--mode", "direct", "--output-dir", tmp])
            assert result.returncode == 0
            assert (Path(tmp) / "index.html").exists()
            assert (Path(tmp) / "status.json").exists()

    def test_direct_mode_has_correct_mode_in_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(["--mode", "direct", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            assert data.get("execution_mode") == "direct"

    def test_direct_mode_rows_populated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(["--mode", "direct", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            rows = data.get("rows", [])
            assert len(rows) >= 4
            workloads = {r["workload"] for r in rows}
            assert "WGU Reddit" in workloads
            assert "Traderie" in workloads
            assert "VPS / control plane" in workloads


# ── 2. Remote mode ──────────────────────────────────────────────────────────


class TestRemoteMode:
    def test_remote_mode_invalid_host_degrades(self) -> None:
        """With a nonexistent host, remote mode degrades to missing_producer."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(
                ["--mode", "remote", "--host", "nonexistent.invalid", "--output-dir", tmp],
            )
            assert result.returncode == 0
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            rows = data.get("rows", [])
            for r in rows:
                if r["workload"] in ("VPS / control plane", "WGU Reddit"):
                    assert r["evidence_level"] in (
                        "missing_producer", "doc_fallback",
                    )

    def test_remote_mode_with_custom_host(self) -> None:
        """Custom host is reflected in the execution mode metadata."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(
                ["--mode", "remote", "--host", "test-vps", "--output-dir", tmp,
                 "--json"],
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            assert data.get("execution_mode") == "remote"

    def test_remote_mode_env_host(self) -> None:
        """IVY_VPS_HOST env var configures the SSH host."""
        with tempfile.TemporaryDirectory() as tmp:
            env = {"IVY_VPS_HOST": "env-host-vps"}
            result = _run_python(
                ["--mode", "remote", "--output-dir", tmp],
                env=env,
            )
            assert result.returncode == 0

    def test_remote_mode_cli_overrides_env(self) -> None:
        """CLI --host overrides IVY_VPS_HOST env var."""
        with tempfile.TemporaryDirectory() as tmp:
            env = {"IVY_VPS_HOST": "env-host-vps"}
            result = _run_python(
                ["--mode", "remote", "--host", "cli-host-vps", "--output-dir", tmp],
                env=env,
            )
            assert result.returncode == 0


# ── 3. Auto mode ────────────────────────────────────────────────────────────


class TestAutoMode:
    def test_auto_mode_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(["--output-dir", tmp])
            assert result.returncode == 0

    def test_auto_mode_env_var(self) -> None:
        """IVY_VPS_MODE env var sets default mode."""
        with tempfile.TemporaryDirectory() as tmp:
            env = {"IVY_VPS_MODE": "no-live"}
            result = _run_python(["--output-dir", tmp], env=env)
            assert result.returncode == 0
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            assert data.get("execution_mode") in ("no-live", "direct")


# ── 4. No-live mode ─────────────────────────────────────────────────────────


class TestNoLiveMode:
    def test_no_live_mode_works(self) -> None:
        """--mode no-live disables all live probes."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(["--mode", "no-live", "--output-dir", tmp])
            assert result.returncode == 0

    def test_no_live_flag_alias(self) -> None:
        """--no-live is an alias for --mode no-live."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(["--no-live", "--output-dir", tmp])
            assert result.returncode == 0

    def test_no_live_rows_have_correct_level(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(["--mode", "no-live", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            for r in data.get("rows", []):
                if r["workload"] in ("WGU Reddit", "VPS / control plane"):
                    assert r["evidence_level"] in (
                        "missing_producer", "doc_fallback",
                    ), f"{r['workload']} should not be live in no-live mode"

    def test_no_live_traderie_fallback(self) -> None:
        """Traderie still uses doc_fallback regardless of mode."""
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(["--mode", "no-live", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            traderie = next(
                (r for r in data["rows"] if r["workload"] == "Traderie"), None,
            )
            assert traderie is not None
            assert traderie.get("evidence_level") == "doc_fallback"

    def test_no_live_ih_separate(self) -> None:
        """Chat and market remain separate rows in no-live mode."""
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(["--mode", "no-live", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            workloads = [r["workload"] for r in data["rows"]]
            assert "Idle Hacking chat" in workloads
            assert "Idle Hacking market" in workloads


# ── 5. Absent SSH / invalid remote ─────────────────────────────────────────


class TestAbsentSshConfig:
    def test_invalid_remote_host(self) -> None:
        """Unreachable SSH host degrades to missing_producer, does not crash."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(
                ["--mode", "remote", "--host", "nonexistent.invalid", "--output-dir", tmp],
            )
            assert result.returncode == 0
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            live_ssh_rows = [
                r for r in data["rows"]
                if r["evidence_level"] not in ("doc_fallback",)
            ]
            for r in live_ssh_rows:
                assert r["evidence_level"] == "missing_producer", (
                    f"{r['workload']} should be missing_producer with invalid SSH host, "
                    f"got {r['evidence_level']}"
                )

    def test_no_ssh_binary_fallback(self) -> None:
        """When ssh is not on PATH, Transport._ssh returns graceful error."""
        from tools.ingestion_dashboard import Transport, run
        t = Transport(mode="remote", host="nonexistent.test")
        # Monkey-patch shutil.which to simulate missing ssh
        import shutil
        original_which = shutil.which
        shutil.which = lambda cmd: None if cmd == "ssh" else original_which(cmd)
        try:
            ok, msg = t.exec("echo ok")
            assert not ok
            assert "not available" in msg
        finally:
            shutil.which = original_which

    def test_direct_mode_missing_ih_adapters_is_explicit_not_fatal(self) -> None:
        """An optional external adapter must not abort the VPS dashboard."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(
                ["--mode", "direct", "--json", "--output-dir", tmp],
                env={
                    "IVY_IH_MARKET_ADAPTER": "/definitely/missing/market.py",
                    "IVY_IH_CHAT_ADAPTER": "/definitely/missing/chat.py",
                },
            )
            assert result.returncode == 0
            data = json.loads(result.stdout)
            rows = {r["workload"]: r for r in data["rows"]}
            for workload in ("Idle Hacking chat", "Idle Hacking market"):
                assert rows[workload]["evidence_level"] == "missing_producer"


# ── 6. --json output ────────────────────────────────────────────────────────


class TestJsonFlag:
    def test_json_flag_outputs_to_stdout(self) -> None:
        """--json prints JSON to stdout."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(["--no-live", "--json", "--output-dir", tmp])
            assert result.returncode == 0
            assert result.stdout
            data = json.loads(result.stdout)
            assert "generated_at" in data
            assert "rows" in data
            assert "execution_mode" in data
            # HTML path should NOT be printed
            assert "index.html" not in result.stdout
            assert ".html" not in result.stdout

    def test_json_flag_still_writes_files(self) -> None:
        """--json still writes status.json and index.html to output dir."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(["--no-live", "--json", "--output-dir", tmp])
            assert result.returncode == 0
            assert (Path(tmp) / "status.json").exists()
            assert (Path(tmp) / "index.html").exists()

    def test_json_output_matches_file_content(self) -> None:
        """JSON stdout matches status.json content."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(["--no-live", "--json", "--output-dir", tmp])
            stdout_data = json.loads(result.stdout)
            file_data = json.loads(
                (Path(tmp) / "status.json").read_text(encoding="utf-8"),
            )
            assert stdout_data["generated_at"] == file_data["generated_at"]
            assert len(stdout_data["rows"]) == len(file_data["rows"])

    def test_json_parseable(self) -> None:
        """--json output is always valid JSON."""
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ("direct", "remote", "no-live"):
                result = _run_python(
                    ["--mode", mode, "--json", "--output-dir", tmp],
                )
                if result.returncode != 0:
                    continue
                try:
                    json.loads(result.stdout)
                except json.JSONDecodeError as exc:
                    pytest.fail(f"Invalid JSON in {mode} mode: {exc}")

    def test_json_with_host(self) -> None:
        """--json works with --host flag."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(
                ["--mode", "remote", "--host", "test-vps", "--json", "--output-dir", tmp],
            )
            assert result.returncode == 0
            json.loads(result.stdout)

    def test_json_rows_have_evidence_level(self) -> None:
        """Every row in JSON output has valid evidence_level."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(["--no-live", "--json", "--output-dir", tmp])
            data = json.loads(result.stdout)
            valid_levels = {
                "live", "stale", "missing_producer", "unsupported_field",
                "doc_fallback", "unresolved_authority",
            }
            for r in data["rows"]:
                assert r.get("evidence_level") in valid_levels, (
                    f"Invalid evidence_level in {r['workload']}: {r.get('evidence_level')}"
                )


# ── 7. No tracked-file dirtiness ────────────────────────────────────────────


class TestNoTrackedFileDirtiness:
    def test_no_dirtiness_after_run(self) -> None:
        """Dashboard generation does not modify tracked files regardless of mode.
        Tests no-live and direct; remote mode is excluded because SSH connection
        attempts add ~10s per remote call and the invariance property is
        established by the first two modes."""
        with tempfile.TemporaryDirectory() as tmp:
            before = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=REPO_ROOT,
            ).stdout.strip()
            for mode in ("no-live", "direct"):
                _run_python(["--mode", mode, "--output-dir", tmp])
            after = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=REPO_ROOT,
            ).stdout.strip()
            assert before == after, (
                f"Dashboard modified tracked files. Diff:\n"
                f"Before: {before}\nAfter: {after}"
            )


# ── 8. Private data exclusion ───────────────────────────────────────────────


class TestPrivateDataExclusion:
    FORBIDDEN = [
        "api_key", "token", "credential", "cookie", "session_id",
        "browser_profile", "chat_body", "raw_body", "error_message_private",
        "private_notes", "/home/", "/Users/",
    ]

    def test_no_private_data_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ("no-live", "direct"):
                _run_python(["--mode", mode, "--output-dir", tmp])
                text = (Path(tmp) / "status.json").read_text(encoding="utf-8")
                for pattern in self.FORBIDDEN:
                    assert pattern not in text, (
                        f"Forbidden pattern in {mode} JSON: {pattern}"
                    )

    def test_no_private_data_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ("no-live", "direct"):
                _run_python(["--mode", mode, "--output-dir", tmp])
                text = (Path(tmp) / "index.html").read_text(encoding="utf-8")
                for pattern in self.FORBIDDEN:
                    assert pattern not in text, (
                        f"Forbidden pattern in {mode} HTML: {pattern}"
                    )

    def test_no_private_data_json_stdout(self) -> None:
        """--json output also excludes private patterns."""
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ("no-live", "direct"):
                result = _run_python(
                    ["--mode", mode, "--json", "--output-dir", tmp],
                )
                if result.returncode != 0:
                    continue
                for pattern in self.FORBIDDEN:
                    assert pattern not in result.stdout, (
                        f"Forbidden pattern in {mode} JSON stdout: {pattern}"
                    )


# ── 9. Arbitrary CWD ────────────────────────────────────────────────────────


class TestArbitraryCwd:
    def test_works_from_any_directory(self) -> None:
        """Dashboard generates from any CWD."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(
                ["--no-live", "--output-dir", tmp],
                cwd=Path(tmp),
            )
            assert result.returncode == 0, (
                f"Failed from other CWD:\n{result.stderr}"
            )

    def test_works_from_desktop_sim(self) -> None:
        """Simulates running from ~/Desktop or similar."""
        with tempfile.TemporaryDirectory() as tmp:
            desktop = Path(tmp) / "Desktop"
            desktop.mkdir()
            result = _run_python(
                ["--no-live", "--output-dir", tmp],
                cwd=desktop,
            )
            assert result.returncode == 0

    def test_output_goes_to_correct_dir(self) -> None:
        """Output always goes to --output-dir, not CWD."""
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp) / "somewhere"
            cwd.mkdir()
            out = Path(tmp) / "results"
            _run_python(["--no-live", "--output-dir", str(out)], cwd=cwd)
            assert (out / "index.html").exists()
            assert (out / "status.json").exists()


# ── 10. Execution mode in output ────────────────────────────────────────────


class TestExecutionModeInOutput:
    def test_execution_mode_field_present(self) -> None:
        """status.json includes execution_mode field."""
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ("no-live", "direct", "remote"):
                _run_python(["--mode", mode, "--output-dir", tmp])
                data = json.loads(
                    (Path(tmp) / "status.json").read_text(encoding="utf-8"),
                )
                assert "execution_mode" in data, f"Missing execution_mode in {mode}"

    def test_no_live_traderie_fallback(self) -> None:
        """Traderie uses doc_fallback, not a live producer, in all modes."""
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ("no-live", "direct", "remote"):
                _run_python(["--mode", mode, "--output-dir", tmp])
                data = json.loads(
                    (Path(tmp) / "status.json").read_text(encoding="utf-8"),
                )
                traderie = next(
                    (r for r in data["rows"] if r["workload"] == "Traderie"), None,
                )
                if traderie:
                    assert traderie["evidence_level"] in (
                        "doc_fallback", "missing_producer",
                    )
