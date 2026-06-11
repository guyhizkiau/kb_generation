"""Unit tests for store.queue — uses a temp fixture repo via KB_REPO_ROOT."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from store import queue as qs
from store.state import write_state_fields


def _seed_queue(root: Path) -> dict:
    q = {
        "version": 1,
        "clusters": [
            {
                "id": "01-login",
                "title": "Login cluster",
                "articles": [
                    {"slug": "01-log-in-to-specterx", "title": "Log in"},
                    {"slug": "02-set-or-reset-password", "title": "Reset password"},
                    {"slug": "03-what-is-specterx", "title": "What is SpecterX"},
                ],
            },
            {
                "id": "02-sharing",
                "title": "Sharing cluster",
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

    def test_next_article_revision_cycle_noop(self):
        _write_state(self.root, "01-log-in-to-specterx", {
            "PHASE": "MERGED", "REVISION_CYCLE": "1",
        })
        plan = qs.next_article("01-log-in-to-specterx")
        self.assertEqual(plan["action"], "noop")

    def test_next_article_rollover_to_next_cluster(self):
        plan = qs.next_article("03-what-is-specterx")
        self.assertEqual(plan["action"], "next_article")
        self.assertEqual(plan["cluster_id"], "02-sharing")
        self.assertEqual(plan["articles"][0]["slug"], "04-share-file")

    def test_write_state_fields_round_trip(self):
        path = qs.article_state_path("01-log-in-to-specterx")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("PHASE=DRAFTING\nREVISION_CYCLE=0\n")
        write_state_fields(path, {"PHASE": "REVISING", "FEEDBACK_ISSUE": "42"})
        from store.state import read_state_fields
        fields = read_state_fields(path)
        self.assertEqual(fields["PHASE"], "REVISING")
        self.assertEqual(fields["REVISION_CYCLE"], "0")

    def test_article_state_fields_reads_working_tree(self):
        slug = "02-set-or-reset-password"
        _write_state(self.root, slug, {"PHASE": "IN_REVIEW", "REVISION_CYCLE": "0"})
        fields = qs.article_state_fields(slug)
        self.assertEqual(fields["PHASE"], "IN_REVIEW")
