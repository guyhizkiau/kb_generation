"""Unit tests for _handle_trigger and feedback helpers."""
from __future__ import annotations

import os
import unittest
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

    def test_handle_trigger_manual_queues_slug(self):
        result = self.pw._handle_trigger({"slug": "02-set-or-reset-password", "reason": "manual"})
        self.assertTrue(result["ok"])
        self.assertEqual(len(self.pw._manual_trigger_set), 1)
        self.assertEqual(self.pw._manual_trigger_set[0]["slug"], "02-set-or-reset-password")

    def test_handle_trigger_feedback_writes_state_and_feedback(self):
        import feedback_store as fb
        slug = "01-log-in-to-specterx"
        fb.write_feedback(slug, [{"id": "anno-1", "body": [{"value": "fix this"}]}])
        with mock.patch.object(self.pw, "is_claude_running", return_value=False), \
             mock.patch.object(self.pw, "_launch_phase") as launch:
            result = self.pw._handle_trigger({
                "slug": slug, "reason": "feedback",
            })
        self.assertTrue(result["ok"])
        self.assertEqual(result["revision_cycle"], 1)
        self.assertEqual(result["annotation_count"], 1)
        fields = self.pw._qs.read_state_fields(
            self.root / "articles" / slug / "STATE",
        )
        self.assertEqual(fields["PHASE"], "REVISING")
        self.assertEqual(fields["REVISION_CYCLE"], "1")
        launch.assert_called_once_with(slug, "revise-from-feedback")

    def test_handle_trigger_feedback_preserves_inline_annotations_no_issue(self):
        """Inline comments are not wiped when no GitHub issue is provided."""
        import feedback_store as fb
        slug = "01-log-in-to-specterx"
        self.pw.WORKTREE_PATH.mkdir(parents=True, exist_ok=True)
        fb.write_feedback(slug, [{"id": "inline-1", "body": [{"value": "clarify step 2"}]}])

        with mock.patch.object(self.pw, "is_claude_running", return_value=False), \
             mock.patch.object(self.pw, "_launch_phase") as launch:
            result = self.pw._handle_trigger({
                "slug": slug, "reason": "feedback",
            })

        self.assertTrue(result["ok"])
        self.assertEqual(result["annotation_count"], 1)
        stored = fb.read_feedback(slug)
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["id"], "inline-1")
        launch.assert_called_once_with(slug, "revise-from-feedback")
        fields = self.pw._qs.read_state_fields(
            self.root / "articles" / slug / "STATE",
        )
        self.assertEqual(fields["PHASE"], "REVISING")

    def test_handle_trigger_feedback_empty_store_returns_error(self):
        import feedback_store as fb
        slug = "01-log-in-to-specterx"
        self.pw.WORKTREE_PATH.mkdir(parents=True, exist_ok=True)
        fb.write_feedback(slug, [])

        with mock.patch.object(self.pw, "is_claude_running", return_value=False), \
             mock.patch.object(self.pw, "_launch_phase") as launch:
            result = self.pw._handle_trigger({
                "slug": slug, "reason": "feedback", "issue": "",
            })

        self.assertFalse(result["ok"])
        self.assertIn("No feedback", result.get("error", ""))
        launch.assert_not_called()
        state_path = self.pw.WORKTREE_PATH / "articles" / slug / "STATE"
        if state_path.exists():
            fields = self.pw._qs.read_state_fields(state_path)
            self.assertNotEqual(fields.get("PHASE"), "REVISING")

    def test_handle_trigger_feedback_dedup_already_queued(self):
        import feedback_store as fb
        slug = "01-log-in-to-specterx"
        self.pw.WORKTREE_PATH.mkdir(parents=True, exist_ok=True)
        fb.write_feedback(slug, [{"id": "inline-1", "body": [{"value": "fix typo"}]}])
        self.pw._manual_trigger_set.append({"slug": slug, "reason": "feedback-launch", "issue": ""})

        with mock.patch.object(self.pw, "is_claude_running", return_value=True), \
             mock.patch.object(self.pw, "_launch_phase") as launch:
            result = self.pw._handle_trigger({
                "slug": slug, "reason": "feedback", "issue": "",
            })

        self.assertFalse(result["ok"])
        self.assertIn("already queued", result.get("error", "").lower())
        launch.assert_not_called()
        queued = [t for t in self.pw._manual_trigger_set
                  if t.get("slug") == slug and t.get("reason") == "feedback-launch"]
        self.assertEqual(len(queued), 1)

    def test_merge_feedback_dedup_by_id(self):
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
        orig = next(a for a in merged if a["id"] == "existing-1")
        self.assertEqual(orig["body"][0]["value"], "first comment")

        merged2 = fb.merge_feedback(slug, [{"id": "existing-1"}, {"id": "new-2"}])
        self.assertEqual(len(merged2), 2)

    def test_prepare_manual_research_seeds_missing_state(self):
        slug = "02-set-or-reset-password"
        self.assertFalse((self.root / "articles" / slug / "STATE").exists())
        self.assertTrue(self.pw._prepare_manual_research(slug))
        fields = self.pw._qs.read_state_fields(self.root / "articles" / slug / "STATE")
        self.assertEqual(fields["PHASE"], "QUEUED")
        self.assertEqual(fields["CLUSTER"], "01-login")

    def test_prepare_manual_research_from_skipped(self):
        from store.state import write_state
        slug = "02-set-or-reset-password"
        write_state(slug, {"PHASE": "SKIPPED", "CLUSTER": "01-login"})
        self.assertTrue(self.pw._prepare_manual_research(slug))
        fields = self.pw._qs.read_state_fields(self.root / "articles" / slug / "STATE")
        self.assertEqual(fields["PHASE"], "SKIPPED")

    def test_manual_drain_launches_research(self):
        self.pw._manual_trigger_set.append({
            "slug": "02-set-or-reset-password", "reason": "manual", "issue": "",
        })
        with mock.patch.object(self.pw, "is_claude_running", return_value=False), \
             mock.patch.object(self.pw, "_prepare_manual_research", return_value=True), \
             mock.patch.object(self.pw, "_launch_phase") as launch:
            slug = "02-set-or-reset-password"
            self.pw._manual_trigger_set.pop(0)
            self.pw._launch_phase(slug, "research")
        launch.assert_called_once_with("02-set-or-reset-password", "research")


if __name__ == "__main__":
    unittest.main()
