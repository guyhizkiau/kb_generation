"""Unit tests for store.feedback."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from store.feedback import append_feedback, read_feedback, remove_feedback


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        os.environ["GHOSTWRITER_FEEDBACK_DIR"] = str(self.root / "feedback")

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)
        os.environ.pop("GHOSTWRITER_FEEDBACK_DIR", None)

    def test_append_and_read(self):
        slug = "01-test"
        result = append_feedback(slug, {"id": "ann-1", "text": "fix typo"})
        self.assertTrue(result["ok"])
        anns = read_feedback(slug)
        self.assertEqual(len(anns), 1)
        self.assertEqual(anns[0]["id"], "ann-1")

    def test_dedupe_by_id(self):
        slug = "02-dedupe"
        append_feedback(slug, {"id": "ann-1", "text": "first"})
        result = append_feedback(slug, {"id": "ann-1", "text": "duplicate"})
        self.assertTrue(result.get("deduped"))
        self.assertEqual(len(read_feedback(slug)), 1)

    def test_remove_feedback(self):
        slug = "03-remove"
        append_feedback(slug, {"id": "ann-1", "text": "note"})
        result = remove_feedback(slug, "ann-1")
        self.assertTrue(result["ok"])
        self.assertEqual(read_feedback(slug), [])

    def test_default_feedback_path_under_article_dir(self):
        os.environ.pop("GHOSTWRITER_FEEDBACK_DIR", None)
        from store.feedback import feedback_path

        slug = "04-default-path"
        self.assertEqual(
            feedback_path(slug),
            self.root / "articles" / slug / "feedback.json",
        )

    def test_default_path_under_article_dir(self):
        os.environ.pop("GHOSTWRITER_FEEDBACK_DIR", None)
        slug = "04-default-path"
        append_feedback(slug, {"id": "ann-1", "text": "note"})
        expected = self.root / "articles" / slug / "feedback.json"
        self.assertTrue(expected.exists())
