"""Unit tests for pipeline/relint.py."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from pipeline.relint import apply_rework_flags, diff_touches_assets, lint_article, relint_catalog
from store.state import write_state


class RelintTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        self.slug = "01-published"
        art = self.root / "articles" / self.slug
        art.mkdir(parents=True)
        write_state(self.slug, {"PHASE": "PUBLISHED"})
        rules = {
            "version": 1,
            "banned_phrases": [{"pattern": "simply", "rule": "test"}],
            "glossary_terms": [],
        }
        (self.root / "editorial").mkdir(exist_ok=True)
        (self.root / "editorial" / "lint_rules.json").write_text(json.dumps(rules))

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def test_lint_finds_banned_phrase(self):
        (self.root / "articles" / self.slug / "final.md").write_text("# Title\n\nSimply click here.\n")
        rules = json.loads((self.root / "editorial" / "lint_rules.json").read_text())
        v = lint_article(self.slug, rules)
        self.assertEqual(len(v), 1)

    def test_diff_touches_assets(self):
        self.assertTrue(diff_touches_assets("editorial/STYLE_GUIDE.md\n"))
        self.assertFalse(diff_touches_assets("articles/foo/final.md\n"))

    def test_apply_rework_flags(self):
        from pipeline.relint import Violation
        results = {self.slug: [Violation("f", 1, "r", "x")]}
        apply_rework_flags(results)
        from store.state import read_state
        self.assertIn("re-lint", read_state(self.slug)["REWORK_REASON"])
