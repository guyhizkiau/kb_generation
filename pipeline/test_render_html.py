"""Unit tests for pipeline/render_html.py."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class RenderHtmlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.slug = "01-test"
        self.art = self.root / "articles" / self.slug
        self.art.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *extra: str) -> subprocess.CompletedProcess:
        script = REPO_ROOT / "pipeline" / "render_html.py"
        return subprocess.run(
            [sys.executable, str(script), str(self.art), *extra],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )

    def test_missing_image_exits_nonzero(self):
        (self.art / "final.md").write_text("# Title\n\n![missing](screenshots/nope.png)\n")
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing image", result.stderr.lower())

    def test_renders_with_existing_image(self):
        shots = self.art / "screenshots"
        shots.mkdir()
        (shots / "01.png").write_bytes(b"png")
        (self.art / "final.md").write_text("# Title\n\n![ok](screenshots/01.png)\n")
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stderr)
        html = self.art / f"{self.slug}.html"
        self.assertTrue(html.is_file())
        self.assertIn("data:image", html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
