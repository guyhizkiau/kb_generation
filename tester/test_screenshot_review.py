"""Unit tests for tester/screenshot_review.py."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import tester.screenshot_review as review


class ScreenshotReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.png = Path(self.tmp.name) / "shot.png"
        self.png.write_bytes(b"\x89PNG\r\n\x1a\n")
        review.set_review_impl(None)
        self._env = os.environ.copy()

    def tearDown(self):
        self.tmp.cleanup()
        review.set_review_impl(None)
        os.environ.clear()
        os.environ.update(self._env)

    def test_disabled_via_env(self):
        os.environ["SCREENSHOT_REVIEW"] = "off"
        result = review.review_screenshot(self.png, focus="dialog")
        self.assertTrue(result.ok)
        self.assertTrue(result.skipped)

    def test_missing_file_fails_open(self):
        result = review.review_screenshot(Path(self.tmp.name) / "missing.png")
        self.assertTrue(result.ok)
        self.assertTrue(result.skipped)

    def test_no_api_key_fails_open(self):
        os.environ.pop("ANTHROPIC_API_KEY", None)
        with mock.patch.object(review, "SECRETS_ENV_PATH", Path("/nonexistent/.env")):
            result = review.review_screenshot(self.png)
        self.assertTrue(result.ok)
        self.assertTrue(result.skipped)

    def test_parse_good_json(self):
        parsed = review._parse_review_json('{"ok": true, "reason": "dialog is stable"}')
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertTrue(parsed.ok)
        self.assertEqual(parsed.reason, "dialog is stable")

    def test_parse_bad_json_with_surrounding_text(self):
        parsed = review._parse_review_json(
            'Here is my verdict:\n{"ok": false, "reason": "spinner visible"}\nDone.'
        )
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertFalse(parsed.ok)
        self.assertEqual(parsed.reason, "spinner visible")

    def test_observation_suffix_bad_includes_attempts(self):
        result = review.ReviewResult(ok=False, reason="loader visible")
        self.assertIn("BAD", result.observation_suffix(attempts=3))
        self.assertIn("after 3 attempts", result.observation_suffix(attempts=3))

    def test_injectable_impl(self):
        def fake(_path, *, focus="", description=""):
            return review.ReviewResult(ok=False, reason="mock rejection")

        review.set_review_impl(fake)
        result = review.review_screenshot(self.png, focus="x")
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "mock rejection")

    def test_api_error_fails_open(self):
        os.environ["ANTHROPIC_API_KEY"] = "test-key"
        fake_client = mock.MagicMock()
        fake_client.messages.create.side_effect = RuntimeError("network down")
        fake_module = mock.MagicMock()
        fake_module.Anthropic.return_value = fake_client
        with mock.patch.dict("sys.modules", {"anthropic": fake_module}):
            result = review.review_screenshot(self.png)
        self.assertTrue(result.ok)
        self.assertTrue(result.skipped)

    def test_api_good_response(self):
        os.environ["ANTHROPIC_API_KEY"] = "test-key"
        block = mock.MagicMock()
        block.type = "text"
        block.text = '{"ok": true, "reason": "focus visible"}'
        fake_client = mock.MagicMock()
        fake_client.messages.create.return_value = mock.MagicMock(content=[block])
        fake_module = mock.MagicMock()
        fake_module.Anthropic.return_value = fake_client
        with mock.patch.dict("sys.modules", {"anthropic": fake_module}):
            result = review.review_screenshot(self.png, focus="Share dialog")
        self.assertTrue(result.ok)
        self.assertFalse(result.skipped)
        self.assertEqual(result.reason, "focus visible")

    def test_load_api_key_from_secrets_file(self):
        secrets = Path(self.tmp.name) / ".env"
        secrets.write_text('ANTHROPIC_API_KEY="from-file"\n', encoding="utf-8")
        with mock.patch.object(review, "SECRETS_ENV_PATH", secrets):
            self.assertEqual(review._load_api_key(), "from-file")
