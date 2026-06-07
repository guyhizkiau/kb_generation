"""Unit tests for queue_store.py — uses a temp fixture repo via KB_REPO_ROOT."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import queue_store as qs


def _seed_queue(root: Path) -> dict:
    q = {
        "version": 1,
        "clusters": [
            {
                "id": "01-login",
                "title": "Login cluster",
                "mode": "serial",
                "status": "active",
                "pause_after": True,
                "articles": [
                    {"slug": "01-log-in-to-specterx", "title": "Log in"},
                    {"slug": "02-set-or-reset-password", "title": "Reset password"},
                    {"slug": "03-what-is-specterx", "title": "What is SpecterX"},
                ],
            },
            {
                "id": "02-sharing",
                "title": "Sharing cluster",
                "mode": "serial",
                "status": "active",
                "pause_after": False,
                "articles": [
                    {"slug": "04-share-file", "title": "Share a file"},
                ],
            },
        ],
    }
    (root / "clusters").mkdir(parents=True, exist_ok=True)
    (root / "clusters" / "queue.json").write_text(json.dumps(q, indent=2))
    return q


def _write_state(root: Path, slug: str, fields: dict[str, str]) -> None:
    d = root / "articles" / slug
    d.mkdir(parents=True, exist_ok=True)
    lines = [f"{k}={v}" for k, v in fields.items()]
    (d / "STATE").write_text("\n".join(lines) + "\n")


class QueueStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        _seed_queue(self.root)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def test_next_article_serial_advance(self):
        plan = qs.next_article("01-log-in-to-specterx")
        self.assertEqual(plan["action"], "next_article")
        self.assertEqual(plan["articles"][0]["slug"], "02-set-or-reset-password")
        self.assertEqual(plan["articles"][0]["num"], 2)

    def test_next_article_revision_cycle_noop(self):
        _write_state(self.root, "01-log-in-to-specterx", {
            "PHASE": "MERGED", "REVISION_CYCLE": "1",
        })
        plan = qs.next_article("01-log-in-to-specterx")
        self.assertEqual(plan["action"], "noop")

    def test_next_article_pause_after_last(self):
        plan = qs.next_article("03-what-is-specterx")
        self.assertEqual(plan["action"], "pause")

    def test_next_article_rollover_to_next_cluster(self):
        q = qs.load_queue()
        q["clusters"][0]["pause_after"] = False
        qs.save_queue(q)
        plan = qs.next_article("03-what-is-specterx", q)
        self.assertEqual(plan["action"], "next_article")
        self.assertEqual(plan["cluster_id"], "02-sharing")
        self.assertEqual(plan["articles"][0]["slug"], "04-share-file")

    def test_next_article_paused_cluster(self):
        q = qs.load_queue()
        q["clusters"][0]["status"] = "paused"
        qs.save_queue(q)
        plan = qs.next_article("01-log-in-to-specterx", q)
        self.assertEqual(plan["action"], "paused")

    def test_next_article_parallel_eligible(self):
        q = qs.load_queue()
        q["clusters"][0]["mode"] = "parallel"
        qs.save_queue(q)
        plan = qs.next_article("01-log-in-to-specterx", q)
        self.assertEqual(plan["action"], "next_article")
        slugs = {a["slug"] for a in plan["articles"]}
        self.assertIn("02-set-or-reset-password", slugs)
        self.assertIn("03-what-is-specterx", slugs)

    def test_next_article_unknown_slug(self):
        plan = qs.next_article("99-nonexistent")
        self.assertEqual(plan["action"], "unknown")

    def test_validate_slugs_errors_and_warnings(self):
        q = qs.load_queue()
        q["clusters"][0]["mode"] = "invalid"
        q["clusters"][0]["articles"].append(
            {"slug": "01-log-in-to-specterx", "title": "dup"},
        )
        q["clusters"][0]["articles"].append(
            {"slug": "bad slug", "title": "bad"},
        )
        q["clusters"][0]["articles"].append(
            {"slug": "99-new-article", "title": "new"},
        )
        issues = qs.validate_slugs(q)
        levels = {i["level"] for i in issues}
        self.assertIn("error", levels)
        self.assertIn("warning", levels)

    def test_write_state_fields_round_trip(self):
        path = qs.article_state_path("01-log-in-to-specterx")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("PHASE=DRAFTING\nREVISION_CYCLE=0\n")
        qs.write_state_fields(path, {"PHASE": "REVISING", "FEEDBACK_ISSUE": "42"})
        fields = qs.read_state_fields(path)
        self.assertEqual(fields["PHASE"], "REVISING")
        self.assertEqual(fields["FEEDBACK_ISSUE"], "42")
        self.assertEqual(fields["REVISION_CYCLE"], "0")
        self.assertIn("LAST_UPDATE", fields)

    def test_queue_with_states_next_slug_and_publish_stale(self):
        _write_state(self.root, "01-log-in-to-specterx", {"PHASE": "MERGED"})
        _write_state(self.root, "02-set-or-reset-password", {
            "PHASE": "REVISING", "PUBLISH_STALE": "true",
        })
        data = qs.queue_with_states()
        self.assertEqual(data["next_slug"], "02-set-or-reset-password")
        self.assertIn("02-set-or-reset-password", data["publish_stale"])

    def test_strip_queue_for_save_removes_enriched_fields(self):
        enriched = qs.queue_with_states()
        stripped = qs.strip_queue_for_save(enriched)
        art = stripped["clusters"][0]["articles"][0]
        self.assertEqual(set(art.keys()), {"slug", "title"})
        self.assertNotIn("next_slug", stripped)
        self.assertNotIn("publish_stale", stripped)

    def _init_git(self, root: Path) -> None:
        subprocess.run(["git", "init"], cwd=root, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "t@test"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
        subprocess.run(["git", "add", "-A"], cwd=root, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=root, capture_output=True, check=True)

    def test_article_ref_detects_local_branch(self):
        self._init_git(self.root)
        slug = "02-set-or-reset-password"
        branch = f"article/{slug}"
        subprocess.run(["git", "branch", branch], cwd=self.root, check=True)
        self.assertEqual(qs.article_ref(slug), branch)

    def test_queue_with_states_reads_phase_from_branch_ref(self):
        self._init_git(self.root)
        slug = "02-set-or-reset-password"
        branch = f"article/{slug}"
        art_dir = self.root / "articles" / slug
        art_dir.mkdir(parents=True, exist_ok=True)
        (art_dir / "STATE").write_text("PHASE=PR_OPEN\nREVISION_CYCLE=0\n")
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "branch state"], cwd=self.root, check=True)
        subprocess.run(["git", "branch", branch], cwd=self.root, check=True)
        # main tree has no STATE for slug 02 — ref should supply PR_OPEN
        data = qs.queue_with_states()
        art = next(
            a for c in data["clusters"] for a in c["articles"] if a["slug"] == slug
        )
        self.assertEqual(art["phase"], "PR_OPEN")


if __name__ == "__main__":
    unittest.main()
