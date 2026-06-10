"""Unit tests for writer/run_claude_code.py."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
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
