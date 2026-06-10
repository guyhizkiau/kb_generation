"""Unit tests for pipeline/migrate_to_single_branch.py."""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from pipeline.migrate_to_single_branch import migrate
from store.state import read_state, write_state


class MigrateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        subprocess.run(["git", "init"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "t@test"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=self.root, check=True)
        (self.root / "clusters").mkdir()
        (self.root / "clusters" / "queue.json").write_text(
            '{"version":1,"clusters":[{"id":"c1","status":"active","pause_after":false,'
            '"articles":[{"slug":"01-a","title":"A"},{"slug":"02-b","title":"B"}]}]}'
        )
        for slug, phase in [("01-a", "TESTING"), ("02-b", "DRAFTING")]:
            d = self.root / "articles" / slug
            d.mkdir(parents=True)
            write_state(slug, {"PHASE": phase})
            (d / "draft-1.md").write_text("# draft\n")
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=self.root, check=True)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def test_dry_run_succeeds(self):
        migrate(dry_run=True, root=self.root)

    def test_resets_extra_in_flight(self):
        migrate(dry_run=False, root=self.root)
        phases = {read_state("01-a")["PHASE"], read_state("02-b")["PHASE"]}
        self.assertIn("QUEUED", phases)
        self.assertTrue(len([p for p in phases if p != "QUEUED"]) >= 1)
