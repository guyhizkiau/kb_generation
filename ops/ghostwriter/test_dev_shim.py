"""Smoke tests for the Ghostwriter local API shim."""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

SHIM_PATH = Path(__file__).resolve().parent / "dev_server.py"


def _load_shim():
    spec = importlib.util.spec_from_file_location("ghostwriter_dev_server", SHIM_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class DevShimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Isolate feedback writes — without this, POST /api/feedback lands
        # in the real repo's articles/<slug>/feedback.json.
        cls._fb_tmp = tempfile.TemporaryDirectory()
        os.environ["GHOSTWRITER_FEEDBACK_DIR"] = cls._fb_tmp.name
        cls.shim = _load_shim()
        cls.shim.ShimHandler.use_control = False
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), cls.shim.ShimHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.shim.SIM.cancel_timer()
        os.environ.pop("GHOSTWRITER_FEEDBACK_DIR", None)
        cls._fb_tmp.cleanup()

    def _get_json(self, path: str) -> dict:
        with urllib.request.urlopen(f"{self.base}{path}") as resp:
            self.assertEqual(resp.status, 200)
            return json.loads(resp.read().decode())

    def test_status_json(self):
        data = self._get_json("/status/status.json")
        self.assertIn("daemon", data)
        self.assertIn("counters", data)

    def test_health_json(self):
        data = self._get_json("/status/health.json")
        self.assertIn("ActiveState", data)

    def test_queue_fallback(self):
        data = self._get_json("/api/queue")
        self.assertIn("clusters", data)
        self.assertIn("next_slug", data)
        self.assertTrue(data["clusters"])

    def test_poll_now_mock(self):
        req = urllib.request.Request(
            f"{self.base}/poll-now",
            data=b"{}",
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            payload = json.loads(resp.read().decode())
        self.assertTrue(payload["ok"])

    def test_cors_options(self):
        req = urllib.request.Request(f"{self.base}/api/queue", method="OPTIONS")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 204)
            self.assertIn("*", resp.headers.get("Access-Control-Allow-Origin", ""))

    def test_proxy_mode_when_control_up(self):
        fake_queue = {"clusters": [], "next_slug": None, "version": 1, "publish_stale": []}
        with mock.patch.object(self.shim, "control_reachable", return_value=True), \
             mock.patch.object(self.shim, "proxy_request", return_value=(200, json.dumps(fake_queue).encode())):
            self.shim.ShimHandler.use_control = True
            data = self._get_json("/api/queue")
            self.assertEqual(data["clusters"], [])
            self.shim.ShimHandler.use_control = False

    def test_static_served(self):
        req = urllib.request.Request(f"{self.base}/static/recogito.min.css")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("text/css", resp.headers.get("Content-Type", ""))

    def test_ghostwriter_annotate_js(self):
        req = urllib.request.Request(f"{self.base}/static/ghostwriter-annotate.js")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            body = resp.read().decode()
            self.assertIn("ghostwriter:annotation-created", body)

    def test_post_feedback_fallback(self):
        payload = json.dumps({
            "slug": "01-log-in-to-specterx",
            "id": "shim-anno",
            "body": [{"value": "note"}],
        }).encode()
        req = urllib.request.Request(
            f"{self.base}/api/feedback",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
