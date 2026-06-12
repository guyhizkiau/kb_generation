"""Unit tests for doc-- feedback path routing."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from store.feedback import feedback_path


class FeedbackDocsTests(unittest.TestCase):
    def test_doc_slug_routes_to_docs_feedback(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GHOSTWRITER_FEEDBACK_DIR", None)
            path = feedback_path("doc--glossary")
            self.assertTrue(str(path).endswith("docs-feedback/doc--glossary.json"))
            self.assertEqual(path.parent.name, "docs-feedback")

    def test_article_slug_unchanged(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GHOSTWRITER_FEEDBACK_DIR", None)
            path = feedback_path("05-share-a-folder")
            self.assertTrue(str(path).endswith("articles/05-share-a-folder/feedback.json"))

    def test_env_override_for_doc_slug(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {"GHOSTWRITER_FEEDBACK_DIR": tmp}, clear=False):
                path = feedback_path("doc--glossary")
                self.assertEqual(path, Path(tmp) / "doc--glossary.json")


if __name__ == "__main__":
    unittest.main()
