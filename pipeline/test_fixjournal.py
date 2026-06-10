"""Unit tests for pipeline/fixjournal.py."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from pipeline.fixjournal import close_journal, journal_path, open_journal, recover


class FixJournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        subprocess.run(["git", "init"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "t@test"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=self.root, check=True)
        (self.root / "README").write_text("init\n")
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=self.root, check=True)
        self.slug = "01-test"
        art = self.root / "articles" / self.slug
        art.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def test_open_and_close(self):
        open_journal(self.slug, ["ann-1"])
        (self.root / "editorial" / "STYLE_GUIDE.md").parent.mkdir(exist_ok=True)
        (self.root / "editorial" / "STYLE_GUIDE.md").write_text("# style\n")
        subprocess.run(["git", "add", "editorial"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "docs(canon): test"], cwd=self.root, check=True)
        (self.root / "articles" / self.slug / "final.md").write_text("# final\n")
        subprocess.run(["git", "add", f"articles/{self.slug}"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "fix(article): test"], cwd=self.root, check=True)
        close_journal(self.slug)
        self.assertFalse(journal_path(self.slug).exists())

    def test_recover_resets_partial(self):
        open_journal(self.slug, ["ann-1"])
        base = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.root, capture_output=True, text=True, check=True,
        ).stdout.strip()
        (self.root / "editorial").mkdir(exist_ok=True)
        (self.root / "editorial" / "STYLE_GUIDE.md").write_text("# only canon\n")
        subprocess.run(["git", "add", "editorial"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "docs only"], cwd=self.root, check=True)
        result = recover(self.slug)
        self.assertEqual(result, "reset")
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.root, capture_output=True, text=True, check=True,
        ).stdout.strip()
        self.assertEqual(head, base)
