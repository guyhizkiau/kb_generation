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

    def _run_git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def test_dry_run_succeeds(self):
        migrate(dry_run=True, root=self.root)

    def test_dry_run_writes_nothing(self):
        before = (self.root / "articles" / "01-a" / "STATE").read_text()
        migrate(dry_run=True, root=self.root)
        self.assertEqual(before, (self.root / "articles" / "01-a" / "STATE").read_text())
        out = subprocess.run(
            ["git", "status", "--porcelain"], cwd=self.root,
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(out.stdout.strip(), "")

    def test_resets_extra_in_flight(self):
        migrate(dry_run=False, root=self.root)
        phases = {read_state("01-a")["PHASE"], read_state("02-b")["PHASE"]}
        self.assertIn("QUEUED", phases)
        self.assertTrue(len([p for p in phases if p != "QUEUED"]) >= 1)

    def test_legacy_phases_normalized_without_crash(self):
        # DONE / PR_OPEN are legacy values; mapping them must not go through
        # transition() (PUBLISHED → PUBLISHED is not a lifecycle move).
        write_state("01-a", {"PHASE": "DONE"})
        write_state("02-b", {"PHASE": "PR_OPEN", "REVISION_CYCLE": "1"})
        self._run_git("add", "-A")
        self._run_git("commit", "-m", "legacy phases")
        migrate(dry_run=False, root=self.root)
        self.assertEqual(read_state("01-a")["PHASE"], "PUBLISHED")
        self.assertEqual(read_state("02-b")["PHASE"], "IN_REVIEW")
        # Published article gets VERIFIED_AS_OF backfilled.
        self.assertTrue(read_state("01-a").get("VERIFIED_AS_OF"))
        # REVISION_CYCLE survives the rewrite.
        self.assertEqual(read_state("02-b")["REVISION_CYCLE"], "1")

    def test_seeds_queued_state_for_unstarted_articles(self):
        # Queue articles without a STATE file get explicit PHASE=QUEUED.
        (self.root / "clusters" / "queue.json").write_text(
            '{"version":1,"clusters":[{"id":"c1","status":"active","pause_after":false,'
            '"articles":[{"slug":"01-a","title":"A"},{"slug":"02-b","title":"B"},'
            '{"slug":"03-c","title":"C"}]}]}'
        )
        self._run_git("add", "-A")
        self._run_git("commit", "-m", "queue with unstarted article")
        migrate(dry_run=False, root=self.root)
        self.assertEqual(read_state("03-c")["PHASE"], "QUEUED")
        self.assertEqual(read_state("03-c")["CLUSTER"], "c1")

    def test_merged_branch_not_landed(self):
        # A branch fully merged into main must not be landed: its stale
        # STATE (PR_OPEN) would regress the published article and re-queue it.
        write_state("01-a", {"PHASE": "DONE"})
        write_state("02-b", {"PHASE": "DONE"})
        self._run_git("add", "-A")
        self._run_git("commit", "-m", "both published")
        self._run_git("branch", "-M", "main")
        # Simulate a leftover, already-merged article branch with stale STATE.
        merged_sha = subprocess.run(
            ["git", "rev-parse", "HEAD~1"], cwd=self.root,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        self._run_git("update-ref", "refs/remotes/origin/article/01-a", merged_sha)
        migrate(dry_run=False, root=self.root)
        self.assertEqual(read_state("01-a")["PHASE"], "PUBLISHED")
        self.assertEqual(read_state("02-b")["PHASE"], "PUBLISHED")
