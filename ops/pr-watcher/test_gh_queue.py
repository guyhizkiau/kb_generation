"""Tests for gh_queue.py."""
from __future__ import annotations

import json
import os
import unittest
from unittest import mock

import gh_queue as gq


class GhQueueTests(unittest.TestCase):
    def test_enrich_queue_with_open_prs(self):
        queue = {
            "clusters": [{
                "articles": [
                    {"slug": "04-share-a-file", "title": "Share"},
                    {"slug": "05-share-a-folder", "title": "Folder"},
                ],
            }],
        }
        with mock.patch.object(gq, "open_prs_by_slug", return_value={"04-share-a-file": 8}):
            out = gq.enrich_queue_with_open_prs(queue)
        arts = out["clusters"][0]["articles"]
        self.assertEqual(arts[0]["pr_number"], 8)
        self.assertNotIn("pr_number", arts[1])

    def test_merge_article_pr_success(self):
        with mock.patch.object(gq, "open_prs_by_slug", return_value={"04-share-a-file": 8}), \
             mock.patch("gh_queue.subprocess.run") as run:
            run.return_value = mock.Mock(returncode=0, stdout="", stderr="")
            result = gq.merge_article_pr("04-share-a-file")
        self.assertTrue(result["ok"])
        self.assertEqual(result["pr_number"], 8)
        args = run.call_args[0][0]
        self.assertIn("merge", args)
        self.assertIn("8", args)


if __name__ == "__main__":
    unittest.main()
