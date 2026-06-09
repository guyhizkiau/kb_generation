"""Unit tests for trigger_next_article, _handle_trigger, check_merged_prs."""
from __future__ import annotations

import json
import os
import unittest
from pathlib import Path
from unittest import mock

from test_helpers import load_pr_watcher_module, make_fixture_repo, patch_vm_paths


class TriggerTests(unittest.TestCase):
    def setUp(self):
        self.tmp, self.root = make_fixture_repo()
        self.pw = load_pr_watcher_module(self.root)
        patch_vm_paths(self.pw, self.root)
        self.state = {"handled": [], "failed_comments": {}}

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def test_trigger_next_article_dispatches_next(self):
        with mock.patch.object(self.pw, "_launch_next_article", return_value=True) as launch:
            self.pw.trigger_next_article("01-log-in-to-specterx", self.state)
            launch.assert_called_once()
            args = launch.call_args[0]
            self.assertEqual(args[0], "02-set-or-reset-password")

    def test_trigger_next_article_noop_on_revision_cycle(self):
        state_path = self.root / "articles" / "01-log-in-to-specterx" / "STATE"
        state_path.write_text("PHASE=MERGED\nREVISION_CYCLE=1\n")
        with mock.patch.object(self.pw, "_launch_next_article") as launch:
            self.pw.trigger_next_article("01-log-in-to-specterx", self.state)
            launch.assert_not_called()

    def test_handle_trigger_manual_queues_slug(self):
        result = self.pw._handle_trigger({"slug": "02-set-or-reset-password", "reason": "manual"})
        self.assertTrue(result["ok"])
        self.assertEqual(len(self.pw._manual_trigger_set), 1)
        self.assertEqual(self.pw._manual_trigger_set[0]["slug"], "02-set-or-reset-password")

    def test_handle_trigger_feedback_writes_state_and_feedback(self):
        slug = "01-log-in-to-specterx"
        self.pw.WORKTREE_PATH.mkdir(parents=True, exist_ok=True)
        issue_body = 'Review comment\n```json\n{"id":"anno-1","body":[{"value":"fix this"}]}\n```'
        with mock.patch.object(self.pw, "is_claude_running", return_value=False), \
             mock.patch.object(self.pw, "_launch_phase") as launch, \
             mock.patch.object(self.pw, "ensure_worktree"), \
             mock.patch.object(self.pw, "git_worktree"), \
             mock.patch("subprocess.run") as run:
            run.return_value = mock.Mock(returncode=0, stdout=json.dumps([
                {"body": issue_body},
            ]))
            result = self.pw._handle_trigger({
                "slug": slug, "reason": "feedback", "issue": "99",
            })
        self.assertTrue(result["ok"])
        self.assertEqual(result["revision_cycle"], 1)
        self.assertEqual(result["annotation_count"], 1)
        import feedback_store as fb
        fb_data = fb.read_feedback(slug)
        self.assertEqual(len(fb_data), 1)
        fields = self.pw._qs.read_state_fields(
            self.pw.WORKTREE_PATH / "articles" / slug / "STATE",
        )
        self.assertEqual(fields["PHASE"], "REVISING")
        self.assertEqual(fields["REVISION_CYCLE"], "1")
        self.assertEqual(fields["FEEDBACK_ISSUE"], "99")
        launch.assert_called_once_with(slug, "revise-from-feedback")

    def test_handle_trigger_feedback_preserves_inline_annotations_no_issue(self):
        """Inline comments are not wiped when no GitHub issue is provided."""
        import feedback_store as fb
        slug = "01-log-in-to-specterx"
        self.pw.WORKTREE_PATH.mkdir(parents=True, exist_ok=True)
        fb.write_feedback(slug, [{"id": "inline-1", "body": [{"value": "clarify step 2"}]}])

        with mock.patch.object(self.pw, "is_claude_running", return_value=False), \
             mock.patch.object(self.pw, "_launch_phase") as launch, \
             mock.patch.object(self.pw, "ensure_worktree"), \
             mock.patch.object(self.pw, "git_worktree"):
            result = self.pw._handle_trigger({
                "slug": slug, "reason": "feedback", "issue": "",
            })

        self.assertTrue(result["ok"])
        self.assertEqual(result["annotation_count"], 1)
        stored = fb.read_feedback(slug)
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["id"], "inline-1")
        launch.assert_called_once_with(slug, "revise-from-feedback")
        fields = self.pw._qs.read_state_fields(
            self.pw.WORKTREE_PATH / "articles" / slug / "STATE",
        )
        self.assertEqual(fields["PHASE"], "REVISING")

    def test_handle_trigger_feedback_empty_store_returns_error(self):
        """Trigger with an empty feedback store and no issue returns ok=False,
        does not modify STATE, and does not launch Claude."""
        import feedback_store as fb
        slug = "01-log-in-to-specterx"
        self.pw.WORKTREE_PATH.mkdir(parents=True, exist_ok=True)
        fb.write_feedback(slug, [])

        with mock.patch.object(self.pw, "is_claude_running", return_value=False), \
             mock.patch.object(self.pw, "_launch_phase") as launch, \
             mock.patch.object(self.pw, "ensure_worktree"), \
             mock.patch.object(self.pw, "git_worktree"):
            result = self.pw._handle_trigger({
                "slug": slug, "reason": "feedback", "issue": "",
            })

        self.assertFalse(result["ok"])
        self.assertIn("No feedback", result.get("error", ""))
        launch.assert_not_called()
        # STATE must not have been updated to REVISING.
        state_path = self.pw.WORKTREE_PATH / "articles" / slug / "STATE"
        if state_path.exists():
            fields = self.pw._qs.read_state_fields(state_path)
            self.assertNotEqual(fields.get("PHASE"), "REVISING")

    def test_handle_trigger_feedback_dedup_already_queued(self):
        """A second trigger while a feedback-launch is already queued returns
        ok=False without duplicating the queue entry."""
        import feedback_store as fb
        slug = "01-log-in-to-specterx"
        self.pw.WORKTREE_PATH.mkdir(parents=True, exist_ok=True)
        fb.write_feedback(slug, [{"id": "inline-1", "body": [{"value": "fix typo"}]}])
        # Pre-load the queue with a pending feedback-launch for this slug.
        self.pw._manual_trigger_set.append({"slug": slug, "reason": "feedback-launch", "issue": ""})

        with mock.patch.object(self.pw, "is_claude_running", return_value=True), \
             mock.patch.object(self.pw, "_launch_phase") as launch, \
             mock.patch.object(self.pw, "ensure_worktree"), \
             mock.patch.object(self.pw, "git_worktree"):
            result = self.pw._handle_trigger({
                "slug": slug, "reason": "feedback", "issue": "",
            })

        self.assertFalse(result["ok"])
        self.assertIn("already queued", result.get("error", "").lower())
        launch.assert_not_called()
        # Must not have added a second entry for this slug.
        queued = [t for t in self.pw._manual_trigger_set
                  if t.get("slug") == slug and t.get("reason") == "feedback-launch"]
        self.assertEqual(len(queued), 1)

    def test_merge_feedback_dedup_by_id(self):
        """merge_feedback never loses existing annotations and dedupes by id."""
        import feedback_store as fb
        slug = "01-log-in-to-specterx"
        fb.write_feedback(slug, [
            {"id": "existing-1", "body": [{"value": "first comment"}]},
        ])
        merged = fb.merge_feedback(slug, [
            {"id": "existing-1", "body": [{"value": "should be ignored"}]},
            {"id": "new-2", "body": [{"value": "new comment"}]},
        ])
        self.assertEqual(len(merged), 2)
        ids = {a["id"] for a in merged}
        self.assertIn("existing-1", ids)
        self.assertIn("new-2", ids)
        # The original value of existing-1 must be preserved (not overwritten).
        orig = next(a for a in merged if a["id"] == "existing-1")
        self.assertEqual(orig["body"][0]["value"], "first comment")

        # Calling again with only known ids should be idempotent.
        merged2 = fb.merge_feedback(slug, [{"id": "existing-1"}, {"id": "new-2"}])
        self.assertEqual(len(merged2), 2)

    def test_manual_drain_launches_selected_slug(self):
        self.pw._manual_trigger_set.append({
            "slug": "02-set-or-reset-password", "reason": "manual", "issue": "",
        })
        with mock.patch.object(self.pw, "is_claude_running", return_value=False), \
             mock.patch.object(self.pw, "_launch_next_article", return_value=True) as launch:
            trig = self.pw._manual_trigger_set[0]
            if self.pw.is_claude_running():
                pass
            else:
                q = self.pw._qs.load_queue()
                art = self.pw._article_from_queue(trig["slug"], q)
                self.pw._launch_next_article(
                    art["slug"], art["title"], art["num"], art["cluster_id"], self.state,
                )
                self.pw._manual_trigger_set.pop(0)
        launch.assert_called_once()
        self.assertEqual(launch.call_args[0][0], "02-set-or-reset-password")

    def test_check_merged_prs_sets_publish_stale(self):
        state_path = self.root / "articles" / "01-log-in-to-specterx" / "STATE"
        state_path.write_text("PHASE=MERGED\nREVISION_CYCLE=2\n")
        merged_pr = [{
            "number": 5,
            "headRefName": "article/01-log-in-to-specterx",
            "mergedAt": "2026-06-01T00:00:00Z",
        }]
        with mock.patch.object(self.pw, "gh_json", return_value=merged_pr), \
             mock.patch.object(self.pw, "git"), \
             mock.patch.object(self.pw, "trigger_next_article"):
            self.pw.check_merged_prs(self.state)
        fields = self.pw._qs.read_state_fields(state_path)
        self.assertEqual(fields.get("PUBLISH_STALE"), "true")


if __name__ == "__main__":
    unittest.main()
