"""Unit tests for tester/runner.py."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import tester.runner as runner
from store.state import read_state


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        self.slug = "01-test-article"
        art = self.root / "articles" / self.slug
        art.mkdir(parents=True)
        (art / "STATE").write_text("PHASE=TESTING\nCLUSTER=01-login\nREVISION_CYCLE=1\n")

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)
        runner._browser_runner_cls = runner.BrowserRunner

    def _plan(self, steps: list) -> None:
        import json
        art = self.root / "articles" / self.slug
        (art / "test-plan.json").write_text(json.dumps({"steps": steps}))

    def test_all_pass_sets_verified_and_preserves_keys(self):
        self._plan([{"id": "1", "description": "click", "action": {"type": "noop"}}])

        class OkRunner:
            mode = "stub"
            def __init__(self, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def run_step(self, step):
                from tester.browser_runner import StepResult
                return StepResult(str(step["id"]), True, "ok")

        runner._browser_runner_cls = OkRunner
        with mock.patch("tester.runner.classify", return_value="browser"):
            rc = runner.execute(self.slug)
        self.assertEqual(rc, 0)
        fields = read_state(self.slug)
        self.assertEqual(fields["PHASE"], "REVISING")
        self.assertIn("VERIFIED_AS_OF", fields)
        self.assertEqual(fields["REVISION_CYCLE"], "1")

    def test_failure_blocks(self):
        self._plan([{"id": "1", "description": "fail", "action": {}}])

        class FailRunner:
            mode = "stub"
            def __init__(self, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def run_step(self, step):
                from tester.browser_runner import StepResult
                return StepResult(str(step["id"]), False, "fail")

        runner._browser_runner_cls = FailRunner
        with mock.patch("tester.runner.classify", return_value="browser"):
            rc = runner.execute(self.slug)
        self.assertEqual(rc, 1)
        self.assertEqual(read_state(self.slug)["PHASE"], "BLOCKED")

    def test_desktop_step_blocks(self):
        self._plan([{"id": "1", "description": "desktop", "action": {}}])
        with mock.patch("tester.runner.classify", return_value="desktop"):
            rc = runner.execute(self.slug)
        self.assertEqual(rc, 1)
        self.assertIn("desktop", read_state(self.slug)["BLOCKED_REASON"])
