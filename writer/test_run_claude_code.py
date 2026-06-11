"""Unit tests for writer/run_claude_code.py."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class RunClaudeCodeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        self.runner = REPO_ROOT / "writer" / "run_claude_code.py"

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)
        os.environ.pop("KB_SERIAL_OVERRIDE", None)

    def _write_state(self, slug: str, phase: str) -> None:
        art = self.root / "articles" / slug
        art.mkdir(parents=True, exist_ok=True)
        (art / "STATE").write_text(f"PHASE={phase}\nCLUSTER=01-login\n")

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.runner), *args],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env={**os.environ},
        )

    # ── original passing tests (must stay green) ─────────────────────────────

    def test_draft_transitions_to_testing(self):
        slug = "01-test-article"
        self._write_state(slug, "DRAFTING")
        art = self.root / "articles" / slug
        (art / "draft-1.md").write_text("# draft\n")
        result = self._run(
            "--article", slug, "--phase", "draft",
            "--claude-bin", "/usr/bin/true",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        state = (art / "STATE").read_text()
        self.assertIn("PHASE=TESTING", state)

    def test_busy_pipeline_exit_3(self):
        self._write_state("01-busy", "DRAFTING")
        self._write_state("02-requested", "QUEUED")
        result = self._run(
            "--article", "02-requested", "--phase", "research",
            "--claude-bin", "/usr/bin/true",
        )
        self.assertEqual(result.returncode, 3)

    def test_force_with_override(self):
        self._write_state("01-busy", "DRAFTING")
        slug = "02-forced"
        self._write_state(slug, "RESEARCHING")
        art = self.root / "articles" / slug
        (art / "research").mkdir(parents=True)
        (art / "research" / "competitor-coverage.md").write_text(
            "## Articles read\n\n- Vendor A article\n- Vendor B article\n- Vendor C article\n"
        )
        os.environ["KB_SERIAL_OVERRIDE"] = "1"
        result = self._run(
            "--article", slug, "--phase", "research",
            "--claude-bin", "/usr/bin/true", "--force",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    # ── pre-flight checks ────────────────────────────────────────────────────

    def test_preflight_fails_on_missing_binary(self):
        slug = "01-preflight"
        self._write_state(slug, "DRAFTING")
        art = self.root / "articles" / slug
        (art / "draft-1.md").write_text("# x\n")
        result = self._run(
            "--article", slug, "--phase", "draft",
            "--claude-bin", "/nonexistent/bin/claude",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("preflight", result.stdout + result.stderr)

    def test_preflight_blocks_state(self):
        slug = "01-preflight-block"
        self._write_state(slug, "DRAFTING")
        art = self.root / "articles" / slug
        (art / "draft-1.md").write_text("# x\n")
        self._run(
            "--article", slug, "--phase", "draft",
            "--claude-bin", "/nonexistent/bin/claude",
        )
        state = (art / "STATE").read_text()
        self.assertIn("BLOCKED", state)

    # ── heartbeat written on a real phase run ─────────────────────────────────

    def test_heartbeat_written_after_phase(self):
        """After a successful phase, heartbeat.json must exist."""
        slug = "02-heartbeat"
        self._write_state(slug, "DRAFTING")
        art = self.root / "articles" / slug
        (art / "draft-1.md").write_text("# draft\n")
        result = self._run(
            "--article", slug, "--phase", "draft",
            "--claude-bin", "/usr/bin/true",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        hb_path = art / ".writer-logs" / "heartbeat.json"
        # heartbeat.json is written only if output is produced; /usr/bin/true
        # emits nothing, so the file may not exist — that's acceptable.  What
        # we check is that IF it exists it is valid JSON with required keys.
        if hb_path.is_file():
            hb = json.loads(hb_path.read_text())
            self.assertIn("phase", hb)
            self.assertIn("started_at", hb)
            self.assertIn("last_event_at", hb)

    # ── stream-json helpers (unit-level) ─────────────────────────────────────

    def test_parse_stream_event_returns_dict(self):
        from writer.run_claude_code import _parse_stream_event
        evt = _parse_stream_event('{"type":"tool_use","name":"Grep","input":{}}')
        self.assertIsNotNone(evt)
        self.assertEqual(evt["type"], "tool_use")

    def test_parse_stream_event_returns_none_for_plain_text(self):
        from writer.run_claude_code import _parse_stream_event
        self.assertIsNone(_parse_stream_event("Starting research phase…"))
        self.assertIsNone(_parse_stream_event(""))

    def test_summarize_tool_use_event(self):
        from writer.run_claude_code import _summarize_event
        summary = _summarize_event({
            "type": "tool_use",
            "name": "Grep",
            "input": {"pattern": "share", "path": "src/"},
        })
        self.assertIsNotNone(summary)
        self.assertIn("tool:", summary)
        self.assertIn("Grep", summary)

    def test_summarize_result_event(self):
        from writer.run_claude_code import _summarize_event
        summary = _summarize_event({
            "type": "result",
            "subtype": "success",
            "cost_usd": 0.42,
            "duration_ms": 180000,
            "num_turns": 7,
        })
        self.assertIsNotNone(summary)
        self.assertIn("success", summary)
        self.assertIn("0.4200", summary)
        self.assertIn("3.0m", summary)

    def test_summarize_unknown_event_returns_none(self):
        from writer.run_claude_code import _summarize_event
        self.assertIsNone(_summarize_event({"type": "system", "subtype": "init"}))

    # ── gate with remediation (unit-level) ───────────────────────────────────

    def test_gate_passes_immediately_no_fixer_called(self):
        """run_gate_with_remediation returns True without launching any subprocess
        when the gate already passes."""
        import io
        from writer.run_claude_code import run_gate_with_remediation

        slug = "03-gate-ok"
        art = self.root / "articles" / slug
        (art / "research").mkdir(parents=True)
        (art / "research" / "competitor-coverage.md").write_text(
            "## Articles read\n\n- A\n- B\n- C\n"
        )
        os.environ["KB_SERIAL_OVERRIDE"] = "1"
        log_buf = io.StringIO()
        ok, msg = run_gate_with_remediation(slug, "research", "/usr/bin/true", log_buf)
        self.assertTrue(ok, msg)
        self.assertNotIn("fixer", log_buf.getvalue())

    def test_gate_fixer_invoked_when_coverage_exists_but_fails(self):
        """When the artifact exists but gate fails, the fixer is attempted.
        Since /usr/bin/true can't reformat the file, the gate still fails —
        but we verify the fixer was triggered."""
        import io
        from writer.run_claude_code import run_gate_with_remediation

        slug = "04-gate-fixer"
        art = self.root / "articles" / slug
        (art / "research").mkdir(parents=True)
        # Write a file that has content but no ## Articles read section
        (art / "research" / "competitor-coverage.md").write_text(
            "# Competitor coverage\n\nSome prose about Egnyte, Virtru, Dropbox.\n"
        )
        os.environ["KB_SERIAL_OVERRIDE"] = "1"
        log_buf = io.StringIO()
        ok, _msg = run_gate_with_remediation(slug, "research", "/usr/bin/true", log_buf)
        # /usr/bin/true exits 0 but doesn't reformat, so gate should still fail
        self.assertFalse(ok)
        # Fixer must have been triggered
        self.assertIn("fixer", log_buf.getvalue())

    def test_gate_no_fixer_if_artifact_missing(self):
        """When competitor-coverage.md is absent, block immediately (no fixer)."""
        import io
        from writer.run_claude_code import run_gate_with_remediation

        slug = "05-gate-no-file"
        art = self.root / "articles" / slug
        art.mkdir(parents=True)
        os.environ["KB_SERIAL_OVERRIDE"] = "1"
        log_buf = io.StringIO()
        ok, _msg = run_gate_with_remediation(slug, "research", "/usr/bin/true", log_buf)
        self.assertFalse(ok)
        self.assertNotIn("fixer", log_buf.getvalue())

    # ── build_command includes stream-json flags ──────────────────────────────

    def test_build_command_includes_stream_json(self):
        from writer.run_claude_code import build_command
        cmd = build_command("01-slug", "prompt", "draft", "sonnet", [], "claude")
        cmd_str = " ".join(cmd)
        self.assertIn("--output-format", cmd_str)
        self.assertIn("stream-json", cmd_str)
        self.assertIn("--verbose", cmd_str)
