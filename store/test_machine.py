"""Unit tests for store.machine."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from store.machine import (
    ACTIVE_PHASES,
    InvalidTransition,
    active_article,
    block,
    current_phase,
    normalize_legacy,
    resume,
    transition,
    unblock,
)
from store.state import write_state


class MachineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def _slug(self, name: str = "01-test-article") -> str:
        return name

    def _init(self, slug: str, phase: str, **extra: str) -> None:
        write_state(slug, {"PHASE": phase, "CLUSTER": "01-login", **extra})

    def test_legacy_map_on_read(self):
        self._init(self._slug(), "DONE")
        self.assertEqual(current_phase(self._slug()), "PUBLISHED")

    def test_allowed_transition(self):
        self._init(self._slug(), "QUEUED")
        result = transition(self._slug(), "RESEARCHING")
        self.assertEqual(result["PHASE"], "RESEARCHING")

    def test_rejected_transition(self):
        self._init(self._slug(), "QUEUED")
        with self.assertRaises(InvalidTransition):
            transition(self._slug(), "DRAFTING")

    def test_block_and_unblock_round_trip(self):
        self._init(self._slug(), "DRAFTING")
        block(self._slug(), "test failure")
        self.assertEqual(current_phase(self._slug()), "BLOCKED")
        unblock(self._slug())
        self.assertEqual(current_phase(self._slug()), "DRAFTING")

    def test_active_article_none_when_idle(self):
        self._init(self._slug(), "PUBLISHED")
        self.assertIsNone(active_article())

    def test_active_article_detects_in_flight(self):
        self._init(self._slug(), "DRAFTING")
        self.assertEqual(active_article(), self._slug())

    def test_resume_mid_phase(self):
        self._init(self._slug(), "DRAFTING")
        self.assertEqual(resume(self._slug()), "DRAFTING")

    def test_resume_finished_artifact(self):
        slug = self._slug()
        self._init(slug, "DRAFTING")
        art = self.root / "articles" / slug
        art.mkdir(parents=True, exist_ok=True)
        (art / "draft-1.md").write_text("# draft\n")
        self.assertIsNone(resume(slug))

    def test_published_to_revising(self):
        self._init(self._slug(), "PUBLISHED")
        result = transition(self._slug(), "REVISING")
        self.assertEqual(result["PHASE"], "REVISING")

    def test_in_review_to_approved(self):
        self._init(self._slug(), "IN_REVIEW")
        result = transition(self._slug(), "APPROVED", extra={
            "APPROVED_BY": "guy", "APPROVED_AT": "2026-06-01T00:00:00Z",
        })
        self.assertEqual(result["APPROVED_BY"], "guy")

    def test_skipped_to_researching(self):
        self._init(self._slug(), "SKIPPED")
        result = transition(self._slug(), "RESEARCHING")
        self.assertEqual(result["PHASE"], "RESEARCHING")

    def test_normalize_legacy_rewrites_value(self):
        self._init(self._slug(), "DONE")
        self.assertEqual(normalize_legacy(self._slug()), "PUBLISHED")
        self.assertEqual(current_phase(self._slug()), "PUBLISHED")

    def test_normalize_legacy_noop_for_new_set(self):
        self._init(self._slug(), "TESTING")
        self.assertEqual(normalize_legacy(self._slug()), "TESTING")

    def test_transition_rejects_identity_move(self):
        self._init(self._slug(), "PUBLISHED")
        with self.assertRaises(InvalidTransition):
            transition(self._slug(), "PUBLISHED")
