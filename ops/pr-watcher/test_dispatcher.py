"""Unit tests for dispatcher.py — fixture repo via KB_REPO_ROOT."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import dispatcher  # noqa: E402
from store.machine import current_phase  # noqa: E402
from store.state import read_state, write_state  # noqa: E402


class DispatcherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        (self.root / "clusters").mkdir()
        (self.root / "clusters" / "queue.json").write_text(json.dumps({
            "version": 1,
            "clusters": [{
                "id": "c1", "status": "active", "pause_after": False,
                "articles": [
                    {"slug": "01-a", "title": "A"},
                    {"slug": "02-b", "title": "B"},
                ],
            }],
        }))
        self.launches: list[tuple[str, str]] = []
        self.state: dict = {}

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def _mk_article(self, slug: str, phase: str, **extra: str) -> Path:
        d = self.root / "articles" / slug
        d.mkdir(parents=True, exist_ok=True)
        write_state(slug, {"PHASE": phase, **extra})
        return d

    def _launch_phase(self, slug: str, phase: str) -> None:
        self.launches.append((slug, phase))

    def _idle(self, reverify=lambda: False, running=lambda: False) -> None:
        dispatcher.dispatch_idle(
            launch_phase=self._launch_phase,
            queue_reverification=reverify,
            is_claude_running=running,
            state=self.state,
            save_state=lambda s: None,
            log=lambda m: None,
        )

    # -- first_queued_slug ------------------------------------------------

    def test_first_queued_prefers_queue_order(self):
        self._mk_article("01-a", "QUEUED")
        self._mk_article("02-b", "QUEUED")
        self.assertEqual(dispatcher.first_queued_slug(), ("01-a", "c1"))

    def test_missing_state_counts_as_queued(self):
        # Articles added to the queue have no STATE file until the
        # pipeline touches them — they must still be picked up.
        self._mk_article("01-a", "PUBLISHED")
        self.assertEqual(dispatcher.first_queued_slug(), ("02-b", "c1"))

    def test_nothing_queued(self):
        self._mk_article("01-a", "PUBLISHED")
        self._mk_article("02-b", "SKIPPED")
        self.assertIsNone(dispatcher.first_queued_slug())

    # -- dispatch_idle -----------------------------------------------------

    def test_idle_seeds_state_and_launches_research(self):
        self._mk_article("01-a", "PUBLISHED")
        self._idle()
        self.assertEqual(self.launches, [("02-b", "research")])
        fields = read_state("02-b")
        self.assertEqual(fields["PHASE"], "RESEARCHING")
        self.assertEqual(fields["CLUSTER"], "c1")

    def test_idle_defers_while_claude_running(self):
        self._mk_article("01-a", "QUEUED")
        self._idle(running=lambda: True)
        self.assertEqual(self.launches, [])

    def test_idle_reverification_outranks_new_work(self):
        self._mk_article("01-a", "QUEUED")
        self._idle(reverify=lambda: True)
        self.assertEqual(self.launches, [])

    # -- dispatch ----------------------------------------------------------

    def _dispatch(self, slug: str, *, running=lambda: False, retry=None) -> None:
        dispatcher.dispatch(
            slug,
            launch_phase=self._launch_phase,
            run_tester=lambda s: self.launches.append((s, "tester")),
            retry_publish=retry or (lambda s: self.launches.append((s, "publish"))),
            is_claude_running=running,
            state=self.state,
            save_state=lambda s: None,
            log=lambda m: None,
        )

    def test_dispatch_queued_launches_research(self):
        self._mk_article("01-a", "QUEUED")
        self._dispatch("01-a")
        self.assertEqual(self.launches, [("01-a", "research")])
        self.assertEqual(current_phase("01-a"), "RESEARCHING")

    def test_dispatch_dedupes(self):
        self._mk_article("01-a", "DRAFTING")
        self._dispatch("01-a")
        self._dispatch("01-a")
        self.assertEqual(self.launches, [("01-a", "draft")])

    def test_dispatch_testing_runs_test_plan_then_tester(self):
        d = self._mk_article("01-a", "TESTING")
        self._dispatch("01-a")
        self.assertEqual(self.launches, [("01-a", "test-plan")])
        (d / "test-plan.json").write_text("{}")
        self._dispatch("01-a")
        self.assertEqual(self.launches[-1], ("01-a", "tester"))

    def test_dispatch_approved_retries_publish(self):
        self._mk_article("01-a", "APPROVED")
        self._dispatch("01-a")
        self.assertEqual(self.launches, [("01-a", "publish")])

    def test_dispatch_in_review_waits(self):
        self._mk_article("01-a", "IN_REVIEW")
        self._dispatch("01-a")
        self.assertEqual(self.launches, [])

    def test_dispatch_revising_feedback_when_cycle_positive(self):
        self._mk_article("01-a", "REVISING", REVISION_CYCLE="1")
        self._dispatch("01-a")
        self.assertEqual(self.launches, [("01-a", "revise-from-feedback")])

    def test_dispatch_revising_from_test_by_default(self):
        self._mk_article("01-a", "REVISING")
        self._dispatch("01-a")
        self.assertEqual(self.launches, [("01-a", "revise-from-test")])


if __name__ == "__main__":
    unittest.main()
