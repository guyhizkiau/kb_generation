"""Unit tests for pipeline/reverify.py."""
from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline.reverify import find_stale_articles, queue_reverification
from store.state import read_state, write_state


class ReverifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        self.slug = "01-old"
        art = self.root / "articles" / self.slug
        art.mkdir(parents=True)
        (self.root / "product").mkdir(exist_ok=True)
        (self.root / "product" / "CURRENT_RELEASE").write_text(
            "BUILD=test\nRELEASED_AT=2026-06-01T00:00:00Z\n"
        )

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def test_stale_when_old_verified(self):
        old = (datetime.now(timezone.utc) - timedelta(days=91)).strftime("%Y-%m-%dT%H:%M:%SZ")
        write_state(self.slug, {"PHASE": "PUBLISHED", "VERIFIED_AS_OF": old})
        stale = find_stale_articles()
        slugs = [s for s, _ in stale]
        self.assertIn(self.slug, slugs)

    def test_queue_reverification(self):
        write_state(self.slug, {"PHASE": "PUBLISHED", "VERIFIED_AS_OF": "2020-01-01T00:00:00Z"})
        queue_reverification(self.slug, "test stale")
        self.assertEqual(read_state(self.slug)["PHASE"], "TESTING")
