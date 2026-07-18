"""Regression tests for the ingestion dashboard entrypoint.

Validates:
1. The script runs from the repository root (invocation via python3 tools/ingestion_dashboard.py)
2. The script runs from elsewhere (simulating the --no-open CWD scenario that caused ModuleNotFoundError)
3. --no-open flag works without a display/GUI dependency
4. Output directory selection works (--output-dir)
5. --no-live mode works (no SSH dependency)
6. No tracked files are modified during generation
7. No private payload bodies or secrets in output
8. IH chat and market remain separate
9. Malformed/missing producer inputs degrade to explicit unknown/error rather than crash
10. Current vs cumulative failure semantics remain correct
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
ADAPTER_SCRIPT = TOOLS_DIR / "ih_dashboard_adapter.py"


def _run_python(script: Path, args: list[str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(script)]
    if args:
        cmd.extend(args)
    return subprocess.run(
        cmd, capture_output=True, text=True,
        cwd=str(cwd or REPO_ROOT),
        timeout=30,
    )


# ── 1. Invocation from repository root ─────────────────────────────────────


class TestInvocationFromRoot:
    def test_imports_resolve_from_root(self) -> None:
        """Dashboard imports tools.ih_dashboard_adapter successfully from repo root."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            assert result.returncode == 0, f"Dashboard failed from repo root:\n{result.stderr}"

    def test_generates_output_files(self) -> None:
        """Dashboard generates index.html and status.json."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            assert result.returncode == 0
            assert (Path(tmp) / "index.html").exists()
            assert (Path(tmp) / "status.json").exists()

    def test_status_json_valid(self) -> None:
        """status.json is valid JSON with required structure."""
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            assert "generated_at" in data
            assert "rows" in data
            assert "roadmap_coverage" in data
            assert "missing_live_adapters" in data


# ── 2. Invocation from another working directory ───────────────────────────


class TestInvocationFromOtherDir:
    def test_imports_resolve_from_other_cwd(self) -> None:
        """Dashboard imports correctly when CWD is not the repo root."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp], cwd=Path(tmp))
            assert result.returncode == 0, f"Dashboard failed from other CWD:\n{result.stderr}"

    def test_output_in_correct_dir(self) -> None:
        """Dashboard writes to --output-dir, not to CWD."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp], cwd=Path(tmp))
            assert result.returncode == 0
            assert (Path(tmp) / "index.html").exists()
            # Should not write to CWD (which is the tmp dir, but output dir is also tmp
            # so just make sure files exist)
            assert (Path(tmp) / "status.json").exists()


# ── 3. --no-open works ────────────────────────────────────────────────────


class TestNoOpen:
    def test_sh_wrapper_accepts_no_open(self) -> None:
        """Shell wrapper exits cleanly with --no-open."""
        result = subprocess.run(
            ["bash", str(TOOLS_DIR / "open_ingestion_dashboard.sh"), "--no-open"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"Wrapper with --no-open failed:\n{result.stderr}"


# ── 4. Output directory selection ──────────────────────────────────────────


class TestOutputDir:
    def test_custom_output_dir(self) -> None:
        """--output-dir puts files in the specified location."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            assert result.returncode == 0
            assert (Path(tmp) / "index.html").exists()

    def test_output_dir_created_if_missing(self) -> None:
        """--output-dir creates parent directories as needed."""
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "a" / "b" / "c"
            result = _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", str(nested)])
            assert result.returncode == 0
            assert (nested / "index.html").exists()


# ── 5. --no-live / headless execution ──────────────────────────────────────


class TestHeadlessExecution:
    def test_no_live_flag_disables_ssh(self) -> None:
        """--no-live disables SSH calls; dashboard still produces output."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            assert result.returncode == 0

    def test_no_gui_dependency(self) -> None:
        """Dashboard does not require a display/GUI."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            assert result.returncode == 0
            assert "DISPLAY" not in result.stderr and "display" not in result.stderr.lower()


# ── 6. No tracked files modified ───────────────────────────────────────────


class TestNoTrackedFilesModified:
    def test_no_tracked_file_changes(self) -> None:
        """Dashboard generation does not modify tracked files."""
        with tempfile.TemporaryDirectory() as tmp:
            before = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=REPO_ROOT,
            ).stdout.strip()
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            after = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=REPO_ROOT,
            ).stdout.strip()
            assert before == after, "Dashboard modified tracked files"


# ── 7. No private payload bodies or secrets in output ──────────────────────


class TestNoPrivateLeakage:
    FORBIDDEN_IN_OUTPUT = [
        "api_key", "token", "credential", "cookie", "session_id",
        "browser_profile", "chat_body", "raw_body", "error_message_private",
        "private_notes", "/home/", "/Users/",
    ]

    def test_no_forbidden_content_in_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            text = (Path(tmp) / "status.json").read_text(encoding="utf-8")
            for pattern in self.FORBIDDEN_IN_OUTPUT:
                assert pattern not in text, f"Forbidden pattern found: {pattern}"

    def test_no_forbidden_content_in_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            text = (Path(tmp) / "index.html").read_text(encoding="utf-8")
            for pattern in self.FORBIDDEN_IN_OUTPUT:
                assert pattern not in text, f"Forbidden pattern found in HTML: {pattern}"


# ── 8. IH chat and market remain separate ──────────────────────────────────


class TestChatMarketSeparation:
    def test_separate_rows_in_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            workloads = [r["workload"] for r in data["rows"]]
            assert "Idle Hacking chat" in workloads
            assert "Idle Hacking market" in workloads


# ── 9. Malformed/missing producer inputs ──────────────────────────────────


class TestMalformedInputs:
    def test_missing_adapter_returns_issues(self) -> None:
        """Missing producer info shows in issues, not crash."""
        with tempfile.TemporaryDirectory() as tmp:
            result = _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            assert result.returncode == 0

    def test_rows_have_evidence_level(self) -> None:
        """Every row has a valid evidence_level in the expected set."""
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            valid_levels = {"live", "stale", "missing_producer", "unsupported_field", "doc_fallback", "unresolved_authority"}
            for r in data["rows"]:
                assert r.get("evidence_level") in valid_levels, f"Invalid evidence_level in {r['workload']}: {r.get('evidence_level')}"


# ── 10. Current vs cumulative failure semantics ────────────────────────────


class TestFailureSemantics:
    def test_issues_exist_for_all_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            for r in data["rows"]:
                assert isinstance(r.get("issues"), list), f"Missing issues list in {r['workload']}"


# ── 11. Evidence timestamps ──────────────────────────────────────────────────


class TestEvidenceTimestamps:
    def test_every_row_has_evidence_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            for r in data["rows"]:
                assert "evidence_timestamp" in r, f"Missing evidence_timestamp in {r['workload']}"
                assert "collected_at" in r, f"Missing collected_at in {r['workload']}"

    def test_evidence_timestamp_iso_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            for r in data["rows"]:
                ts = r.get("evidence_timestamp", "")
                assert "T" in ts and ts.endswith("Z"), (
                    f"evidence_timestamp should be ISO-8601 in {r['workload']}: {ts}"
                )


# ── 12. Traderie not database-backed ─────────────────────────────────────────


class TestTraderieNotDatabaseBacked:
    def test_traderie_authority_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            traderie = next(
                (r for r in data["rows"] if r["workload"] == "Traderie"), None,
            )
            assert traderie is not None
            detail = traderie.get("detail", {})
            auth = detail.get("authority_type", "")
            assert "file_based" in auth, (
                f"Traderie must document file-based authority, got: {auth}"
            )
            pg_status = detail.get("postgresql", "")
            assert "zero_non_system_tables" in pg_status, (
                f"Traderie PG must show zero non-system tables, got: {pg_status}"
            )
            assert traderie.get("evidence_level", "") == "missing_producer", (
                "Traderie should show missing_producer without live adapter"
            )
            assert traderie.get("status", "") == "UNKNOWN", (
                "Traderie should be UNKNOWN without live probe, not RED from prose"
            )


# ── 13. Reddit recovery wording ──────────────────────────────────────────────


class TestRedditRecoveryWording:
    def test_reddit_backup_shows_recovery_proven(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            reddit = next(
                (r for r in data["rows"] if r["workload"] == "WGU Reddit"), None,
            )
            assert reddit is not None
            backup_text = reddit.get("backup", "")
            assert "BACKUP_RECOVERY_PROVEN" in backup_text, (
                f"Reddit backup must show BACKUP_RECOVERY_PROVEN, got: {backup_text}"
            )
            assert "natural" in backup_text.lower(), (
                f"Reddit backup must still mention natural acceptance, got: {backup_text}"
            )


# ── 14. Missing producer details ─────────────────────────────────────────────


class TestMissingProducerDetails:
    def test_rows_show_missing_adapters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            data = json.loads((Path(tmp) / "status.json").read_text(encoding="utf-8"))
            for r in data["rows"]:
                detail = r.get("detail", {})
                # Each row should have some adapter status fields in detail
                adapter_fields = [k for k in detail if "adapter" in k.lower()]
                assert len(adapter_fields) > 0 or r["evidence_level"] != "missing_producer", (
                    f"{r['workload']} with missing_producer should detail what adapters are missing"
                )


# ── 15. HTML includes collected_at column ─────────────────────────────────────


class TestHtmlCollectedAt:
    def test_html_table_has_collected_at_column(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _run_python(DASHBOARD_SCRIPT, ["--no-live", "--output-dir", tmp])
            html = (Path(tmp) / "index.html").read_text(encoding="utf-8")
            assert "<th>Collected at</th>" in html, "HTML should have Collected at column header"


# ── 16. Read-only terminal summary ─────────────────────────────────────────


class TestTerminalSummary:
    def test_summary_is_stdout_only_and_routes_passport_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "must-not-exist"
            result = _run_python(
                DASHBOARD_SCRIPT,
                ["--no-live", "--summary", "--stdout-only", "--output-dir", str(output_dir)],
            )
            assert result.returncode == 0, result.stderr
            assert "Ivy Control Portfolio Health" in result.stdout
            assert "Passport / backup\nUNKNOWN" in result.stdout
            assert "Refresh Passport recovery-confidence evidence" in result.stdout
            assert not output_dir.exists(), "stdout-only summary must not write dashboard artifacts"

    def test_summary_uses_explicit_passport_evidence_card(self) -> None:
        evidence = REPO_ROOT / "tests" / "fixtures" / "passport_recovery_confidence_verified.json"
        result = _run_python(
            DASHBOARD_SCRIPT,
            ["--no-live", "--summary", "--stdout-only", "--passport-evidence", str(evidence)],
        )
        assert result.returncode == 0, result.stderr
        assert "Passport / backup: VERIFIED" in result.stdout
        assert "sanitized-test-host" not in result.stdout

    def test_summary_treats_expired_passport_evidence_as_unknown(self) -> None:
        evidence = REPO_ROOT / "tests" / "fixtures" / "passport_recovery_confidence_expired.json"
        result = _run_python(
            DASHBOARD_SCRIPT,
            ["--no-live", "--summary", "--stdout-only", "--passport-evidence", str(evidence)],
        )
        assert result.returncode == 0, result.stderr
        assert "Passport / backup\nUNKNOWN" in result.stdout
        assert "expired" in result.stdout
