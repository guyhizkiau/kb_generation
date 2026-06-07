"""HTTP control-plane API tests — hits _ControlHandler on an ephemeral port."""
from __future__ import annotations

import json
import os
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer
from pathlib import Path
from unittest import mock

from test_helpers import load_pr_watcher_module, make_fixture_repo, patch_vm_paths


class ControlApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp, cls.root = make_fixture_repo()
        cls.pw = load_pr_watcher_module(cls.root)
        patch_vm_paths(cls.pw, cls.root)
        cls.pw._manual_trigger_set.clear()
        cls.server = HTTPServer(("127.0.0.1", 0), cls.pw._ControlHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def _req(self, method: str, path: str, body: dict | None = None) -> tuple[int, dict, dict]:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"} if data else {},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                headers = dict(resp.headers)
                payload = json.loads(resp.read().decode())
                return resp.status, payload, headers
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode())
            return exc.code, payload, dict(exc.headers)

    def test_get_api_queue(self):
        code, payload, _ = self._req("GET", "/api/queue")
        self.assertEqual(code, 200)
        self.assertIn("clusters", payload)
        self.assertIn("next_slug", payload)

    def test_options_cors_methods(self):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/queue",
            method="OPTIONS",
        )
        with urllib.request.urlopen(req) as resp:
            methods = resp.headers.get("Access-Control-Allow-Methods", "")
            self.assertIn("GET", methods)
            self.assertIn("PUT", methods)
            self.assertIn("POST", methods)

    def test_put_api_queue_valid(self):
        q = json.loads((self.root / "clusters" / "queue.json").read_text())
        code, payload, _ = self._req("PUT", "/api/queue", q)
        self.assertEqual(code, 200)
        self.assertTrue(payload["ok"])

    def test_put_api_queue_duplicate_slug_422(self):
        q = json.loads((self.root / "clusters" / "queue.json").read_text())
        q["clusters"][0]["articles"].append(
            {"slug": "01-log-in-to-specterx", "title": "dup"},
        )
        code, payload, _ = self._req("PUT", "/api/queue", q)
        self.assertEqual(code, 422)
        self.assertIn("errors", payload)

    def test_post_trigger_feedback(self):
        with mock.patch.object(self.pw, "is_claude_running", return_value=True), \
             mock.patch.object(self.pw, "_launch_phase"):
            code, payload, _ = self._req("POST", "/api/queue/trigger", {
                "slug": "01-log-in-to-specterx",
                "reason": "feedback",
                "issue": "42",
            })
        self.assertEqual(code, 200)
        self.assertTrue(payload["ok"])
        fields = self.pw._qs.read_state_fields(
            self.root / "articles" / "01-log-in-to-specterx" / "STATE",
        )
        self.assertEqual(fields["PHASE"], "REVISING")
        self.assertEqual(fields["REVISION_CYCLE"], "1")

    def test_get_api_feedback(self):
        fb_path = self.root / "articles" / "01-log-in-to-specterx" / "feedback.json"
        fb_path.write_text(json.dumps([{"id": "a1"}]))
        code, payload, _ = self._req("GET", "/api/feedback?slug=01-log-in-to-specterx")
        self.assertEqual(code, 200)
        self.assertEqual(payload["slug"], "01-log-in-to-specterx")
        self.assertEqual(len(payload["annotations"]), 1)

    def test_get_article_preview(self):
        slug = "01-log-in-to-specterx"
        html_path = self.root / "articles" / slug / f"{slug}.html"
        html_path.write_text("<html><head></head><body>preview</body></html>")
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/articles/{slug}/preview",
            method="GET",
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            body = resp.read().decode()
            self.assertIn("preview", body)
            self.assertIn("__GHOSTWRITER__", body)
            self.assertIn("ghostwriter-annotate.js", body)
            self.assertNotIn("if (!N8N_WEBHOOK) return", body)

    def test_post_api_feedback_append(self):
        fb_path = self.root / "articles" / "01-log-in-to-specterx" / "feedback.json"
        fb_path.write_text("[]")
        code, payload, _ = self._req("POST", "/api/feedback", {
            "slug": "01-log-in-to-specterx",
            "id": "anno-new",
            "body": [{"value": "fix typo"}],
        })
        self.assertEqual(code, 200)
        self.assertTrue(payload["ok"])
        fb_path = self.root / "articles" / "01-log-in-to-specterx" / "feedback.json"
        stored = json.loads(fb_path.read_text())
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["id"], "anno-new")

        code2, payload2, _ = self._req("POST", "/api/feedback", {
            "slug": "01-log-in-to-specterx",
            "id": "anno-new",
            "body": [{"value": "fix typo"}],
        })
        self.assertTrue(payload2.get("deduped"))

    def test_poll_now_and_retry_regression(self):
        code, payload, _ = self._req("POST", "/poll-now")
        self.assertEqual(code, 200)
        self.assertTrue(payload["ok"])
        state_path = self.root / "state.json"
        self.pw.STATE_FILE = state_path
        state_path.write_text(json.dumps({"handled": ["issue-1"], "failed_comments": {}}))
        code2, payload2, _ = self._req("POST", "/retry", {"comment_id": "issue-1"})
        self.assertEqual(code2, 200)
        self.assertTrue(payload2["ok"])


if __name__ == "__main__":
    unittest.main()
