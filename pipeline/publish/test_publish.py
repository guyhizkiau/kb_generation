"""Unit tests for pipeline/publish."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pipeline.publish import PublishResult, publish_article
from store.state import write_state


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        self.slug = "01-test-article"
        art = self.root / "articles" / self.slug
        art.mkdir(parents=True)
        (art / "final.md").write_text("---\ntitle: Test\n---\n\n# Test\n")

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def test_refuses_non_approved(self):
        write_state(self.slug, {"PHASE": "IN_REVIEW"})
        result = publish_article(self.slug)
        self.assertFalse(result.ok)
        self.assertEqual(result.error, "not approved")

    def test_publishes_approved(self):
        write_state(self.slug, {"PHASE": "APPROVED", "REVISION_CYCLE": "1"})
        with mock.patch("pipeline.publish.SaveAdapter.publish") as mock_pub:
            mock_pub.return_value = PublishResult(
                ok=True, adapter="save",
                outputs=[f"articles/{self.slug}/{self.slug}.html"],
            )
            from pipeline import publish as pub_mod
            orig = pub_mod.get_adapter
            pub_mod.get_adapter = lambda name=None: type("A", (), {
                "name": "save",
                "publish": mock_pub,
            })()
            result = publish_article(self.slug)
            pub_mod.get_adapter = orig
        self.assertTrue(result.ok)
