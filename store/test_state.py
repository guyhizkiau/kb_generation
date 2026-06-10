"""Unit tests for store.state."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from store.state import read_state, write_state


class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def test_write_state_preserves_unknown_keys(self):
        slug = "01-test-article"
        art_dir = self.root / "articles" / slug
        art_dir.mkdir(parents=True)
        (art_dir / "STATE").write_text("PHASE=DRAFTING\nCLUSTER=01-login\nREVISION_CYCLE=2\n")

        result = write_state(slug, {"PHASE": "TESTING"})
        self.assertEqual(result["PHASE"], "TESTING")
        self.assertEqual(result["CLUSTER"], "01-login")
        self.assertEqual(result["REVISION_CYCLE"], "2")
        self.assertIn("LAST_UPDATE", result)

    def test_read_state_round_trip(self):
        slug = "02-another-article"
        write_state(slug, {"PHASE": "QUEUED", "CLUSTER": "02-share"})
        fields = read_state(slug)
        self.assertEqual(fields["PHASE"], "QUEUED")
        self.assertEqual(fields["CLUSTER"], "02-share")

    def test_last_update_auto_stamps(self):
        slug = "03-stamp-test"
        write_state(slug, {"PHASE": "DRAFTING"})
        fields = read_state(slug)
        self.assertIn("LAST_UPDATE", fields)
        self.assertRegex(fields["LAST_UPDATE"], r"^\d{4}-\d{2}-\d{2}T")
