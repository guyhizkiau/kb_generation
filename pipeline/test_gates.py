"""Unit tests for pipeline/gates.py."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from pipeline.gates import check_research_gate


class GatesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        self.slug = "01-test"
        self.coverage = self.root / "articles" / self.slug / "research"
        self.coverage.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def _write(self, bullets: list[str]) -> None:
        body = "## Articles read\n\n" + "\n".join(f"- {b}" for b in bullets)
        (self.coverage / "competitor-coverage.md").write_text(body)

    def test_passes_with_three(self):
        self._write(["A", "B", "C"])
        ok, msg = check_research_gate(self.slug)
        self.assertTrue(ok)

    def test_fails_with_two(self):
        self._write(["A", "B"])
        ok, msg = check_research_gate(self.slug)
        self.assertFalse(ok)
        self.assertIn("2", msg)

    def test_missing_file(self):
        ok, msg = check_research_gate(self.slug)
        self.assertFalse(ok)
