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

    def test_catastrophic_failure_blocks(self):
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
        self.assertEqual(rc, 0)
        self.assertEqual(read_state(self.slug)["PHASE"], "BLOCKED")

    def test_partial_failure_schedules_repair_on_attempt_one(self):
        steps = [
            {"id": "01", "description": "ok", "action": {}},
            {"id": "02", "description": "fail", "action": {}},
            {"id": "03", "description": "ok", "action": {}},
            {"id": "C1", "description": "cleanup", "action": {}},
        ]
        self._plan(steps)

        class MixedRunner:
            mode = "stub"
            def __init__(self, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def run_step(self, step):
                from tester.browser_runner import StepResult
                ok = str(step["id"]) != "02"
                return StepResult(str(step["id"]), ok, "ok" if ok else "fail")

        runner._browser_runner_cls = MixedRunner
        with mock.patch("tester.runner.classify", return_value="browser"):
            rc = runner.execute(self.slug)
        self.assertEqual(rc, 0)
        fields = read_state(self.slug)
        self.assertEqual(fields["PHASE"], "TESTING")
        self.assertEqual(fields["NEXT_ACTION"], "repair-test-plan")
        self.assertEqual(fields["TEST_ATTEMPT"], "1")
        self.assertFalse((self.root / "articles" / self.slug / "test-notes.md").exists())
        self.assertTrue(
            (self.root / "articles" / self.slug / "test-notes-attempt-1.md").is_file()
        )

    def test_second_attempt_partial_goes_to_revising(self):
        art = self.root / "articles" / self.slug
        (art / "STATE").write_text(
            "PHASE=TESTING\nCLUSTER=01-login\nTEST_ATTEMPT=1\n"
        )
        steps = [
            {"id": "01", "description": "ok", "action": {}},
            {"id": "02", "description": "fail", "action": {}},
            {"id": "03", "description": "ok", "action": {}},
            {"id": "C1", "description": "cleanup", "action": {}},
        ]
        self._plan(steps)

        class MixedRunner:
            mode = "stub"
            def __init__(self, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def run_step(self, step):
                from tester.browser_runner import StepResult
                ok = str(step["id"]) != "02"
                return StepResult(str(step["id"]), ok, "ok" if ok else "fail")

        runner._browser_runner_cls = MixedRunner
        with mock.patch("tester.runner.classify", return_value="browser"):
            rc = runner.execute(self.slug)
        self.assertEqual(rc, 0)
        fields = read_state(self.slug)
        self.assertEqual(fields["PHASE"], "REVISING")
        self.assertEqual(fields["VERIFY_GAPS"], "1")

    def test_cascade_abort_skips_remaining_steps(self):
        steps = [
            {"id": f"0{i}", "description": "fail", "action": {}}
            for i in range(1, 8)
        ] + [{"id": "C1", "description": "cleanup", "action": {}}]
        self._plan(steps)

        class FailRunner:
            mode = "stub"
            calls: list[str] = []
            def __init__(self, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def run_step(self, step):
                from tester.browser_runner import StepResult
                FailRunner.calls.append(str(step["id"]))
                return StepResult(str(step["id"]), False, "fail")

        runner._browser_runner_cls = FailRunner
        with mock.patch("tester.runner.classify", return_value="browser"):
            runner.execute(self.slug)
        # 5 failures then cascade skip for 06,07 plus cleanup C1
        self.assertIn("C1", FailRunner.calls)
        self.assertNotIn("07", FailRunner.calls)

    def test_desktop_step_blocks(self):
        self._plan([{"id": "1", "description": "desktop", "action": {}}])
        with mock.patch("tester.runner.classify", return_value="desktop"):
            rc = runner.execute(self.slug)
        self.assertEqual(rc, 1)
        self.assertIn("desktop", read_state(self.slug)["BLOCKED_REASON"])
