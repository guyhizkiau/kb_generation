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
        self.assertIn("claude_running", payload)
        self.assertIsInstance(payload["claude_running"], bool)

    def test_get_api_queue_claude_running_mocked(self):
        with mock.patch.object(self.pw, "is_claude_running", return_value=True):
            code, payload, _ = self._req("GET", "/api/queue")
        self.assertEqual(code, 200)
        self.assertTrue(payload["claude_running"])

    def test_post_queue_approve_wrong_phase(self):
        code, payload, _ = self._req("POST", "/api/queue/approve", {
            "slug": "01-log-in-to-specterx",
            "reviewer": "guy",
        })
        self.assertEqual(code, 409)
        self.assertFalse(payload["ok"])

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
            self.assertIn("DELETE", methods)

    def test_delete_api_feedback(self):
        import feedback_store as fb
        fb.write_feedback("01-log-in-to-specterx", [{"id": "a1"}, {"id": "a2"}])
        code, payload, _ = self._req(
            "DELETE", "/api/feedback?slug=01-log-in-to-specterx&id=a1",
        )
        self.assertEqual(code, 200)
        self.assertTrue(payload["ok"])
        stored = fb.read_feedback("01-log-in-to-specterx")
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["id"], "a2")

        code2, payload2, _ = self._req(
            "DELETE", "/api/feedback?slug=01-log-in-to-specterx&id=missing",
        )
        self.assertEqual(code2, 404)
        self.assertFalse(payload2["ok"])

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
        import feedback_store as fb
        slug = "01-log-in-to-specterx"
        # Pre-seed the store so the empty-feedback guard does not block the trigger.
        fb.write_feedback(slug, [{"id": "inline-1", "body": [{"value": "fix intro"}]}])
        self.addCleanup(lambda: fb.write_feedback(slug, []))
        # Clear any stale feedback-launch entries from prior tests.
        self.pw._manual_trigger_set[:] = [
            t for t in self.pw._manual_trigger_set
            if not (t.get("slug") == slug and t.get("reason") == "feedback-launch")
        ]

        self.pw.WORKTREE_PATH.mkdir(parents=True, exist_ok=True)
        with mock.patch.object(self.pw, "is_claude_running", return_value=True), \
             mock.patch.object(self.pw, "_launch_phase"), \
             mock.patch.object(self.pw, "ensure_worktree"), \
             mock.patch.object(self.pw, "git_worktree"):
            code, payload, _ = self._req("POST", "/api/queue/trigger", {
                "slug": slug,
                "reason": "feedback",
                "issue": "42",
            })
        self.assertEqual(code, 200)
        self.assertTrue(payload["ok"])
        self.assertGreaterEqual(payload.get("annotation_count", 0), 1)
        fields = self.pw._qs.read_state_fields(
            self.root / "articles" / slug / "STATE",
        )
        self.assertEqual(fields["PHASE"], "REVISING")
        self.assertEqual(fields["REVISION_CYCLE"], "1")

    def test_get_api_feedback(self):
        import feedback_store as fb
        fb.write_feedback("01-log-in-to-specterx", [{"id": "a1"}])
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
        import feedback_store as fb
        fb.write_feedback("01-log-in-to-specterx", [])
        code, payload, _ = self._req("POST", "/api/feedback", {
            "slug": "01-log-in-to-specterx",
            "id": "anno-new",
            "body": [{"value": "fix typo"}],
        })
        self.assertEqual(code, 200)
        self.assertTrue(payload["ok"])
        stored = fb.read_feedback("01-log-in-to-specterx")
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["id"], "anno-new")

        code2, payload2, _ = self._req("POST", "/api/feedback", {
            "slug": "01-log-in-to-specterx",
            "id": "anno-new",
            "body": [{"value": "fix typo"}],
        })
        self.assertTrue(payload2.get("deduped"))

    def _restore_queue(self):
        original = json.loads((self.root / "clusters" / "queue.json").read_text())

        def restore():
            (self.root / "clusters" / "queue.json").write_text(json.dumps(original))

        self.addCleanup(restore)

    @staticmethod
    def _git_side_effect(slug: str, tracked: bool):
        """Mock git: ls-files reflects tracking; other commands no-op."""
        prefix = f"articles/{slug}"

        def side_effect(*args, **kwargs):
            if args[:2] == ("ls-files", prefix):
                return f"{prefix}/STATE\n" if tracked else ""
            return ""

        return side_effect

    def test_delete_article_non_merged_keeps_plan(self):
        self._restore_queue()
        import feedback_store as fb
        slug = "02-set-or-reset-password"
        fb.write_feedback(slug, [{"id": "x1"}])
        self.assertTrue(fb.feedback_path(slug).exists())
        with mock.patch.object(
            self.pw, "git", side_effect=self._git_side_effect(slug, tracked=False),
        ):
            code, payload, _ = self._req("DELETE", f"/api/articles/{slug}")
        self.assertEqual(code, 200)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["merged"])
        self.assertFalse(payload["pushed"])
        self.assertFalse(payload["removed_from_plan"])
        q = json.loads((self.root / "clusters" / "queue.json").read_text())
        slugs = [a["slug"] for c in q["clusters"] for a in c["articles"]]
        self.assertIn(slug, slugs)
        self.assertFalse(fb.feedback_path(slug).exists())
        state_path = self.root / "articles" / slug / "STATE"
        self.assertTrue(state_path.is_file())
        self.assertIn("PHASE=SKIPPED", state_path.read_text())

    def test_delete_article_remove_from_plan(self):
        self._restore_queue()
        slug = "02-set-or-reset-password"
        with mock.patch.object(
            self.pw, "git", side_effect=self._git_side_effect(slug, tracked=True),
        ) as git:
            code, payload, _ = self._req(
                "DELETE", f"/api/articles/{slug}?remove_from_plan=true",
            )
        self.assertEqual(code, 200)
        self.assertTrue(payload["removed_from_plan"])
        self.assertTrue(payload["pushed"])
        called = [c.args for c in git.call_args_list]
        self.assertIn(("add", "--", "clusters/queue.json"), called)
        q = json.loads((self.root / "clusters" / "queue.json").read_text())
        slugs = [a["slug"] for c in q["clusters"] for a in c["articles"]]
        self.assertNotIn(slug, slugs)
        self.assertFalse((self.root / "articles" / slug / "STATE").exists())

    def test_delete_merged_article_commits_to_main(self):
        self._restore_queue()
        slug = "01-log-in-to-specterx"
        art_dir = self.root / "articles" / slug
        state = (art_dir / "STATE").read_text()

        def restore_dir():
            art_dir.mkdir(parents=True, exist_ok=True)
            (art_dir / "STATE").write_text(state)

        self.addCleanup(restore_dir)

        with mock.patch.object(
            self.pw, "git", side_effect=self._git_side_effect(slug, tracked=True),
        ) as git:
            code, payload, _ = self._req("DELETE", f"/api/articles/{slug}")
        self.assertEqual(code, 200)
        self.assertTrue(payload["merged"])
        self.assertTrue(payload["pushed"])
        called = [c.args for c in git.call_args_list]
        self.assertIn(("ls-files", f"articles/{slug}"), called)
        self.assertIn(("add", "-A", "--", f"articles/{slug}"), called)
        self.assertTrue(any(a[:1] == ("commit",) for a in called), called)
        self.assertIn(("push", "origin", "main"), called)
        self.assertFalse(art_dir.exists())

    def test_delete_blocked_tracked_article_commits_to_main(self):
        self._restore_queue()
        slug = "05-share-a-folder"
        art_dir = self.root / "articles" / slug
        art_dir.mkdir(parents=True, exist_ok=True)
        (art_dir / "STATE").write_text(
            "PHASE=BLOCKED\nRESUME_PHASE=RESEARCHING\nBLOCKED_REASON=test\n",
        )

        def restore_dir():
            if not art_dir.exists():
                art_dir.mkdir(parents=True, exist_ok=True)
                (art_dir / "STATE").write_text(
                    "PHASE=BLOCKED\nRESUME_PHASE=RESEARCHING\nBLOCKED_REASON=test\n",
                )

        self.addCleanup(restore_dir)

        with mock.patch.object(
            self.pw, "git", side_effect=self._git_side_effect(slug, tracked=True),
        ) as git:
            code, payload, _ = self._req("DELETE", f"/api/articles/{slug}")
        self.assertEqual(code, 200)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["merged"])
        self.assertTrue(payload["pushed"])
        called = [c.args for c in git.call_args_list]
        self.assertIn(("ls-files", f"articles/{slug}"), called)
        self.assertIn(("add", "-A", "--", f"articles/{slug}"), called)
        self.assertTrue(any(a[:1] == ("commit",) for a in called), called)
        self.assertIn(("push", "origin", "main"), called)
        self.assertFalse(art_dir.exists())

    def test_delete_article_invalid_slug(self):
        with mock.patch.object(self.pw, "git", return_value=""):
            code, payload, _ = self._req("DELETE", "/api/articles/bad_slug")
        self.assertEqual(code, 400)
        self.assertFalse(payload["ok"])

    def test_resolve_blocked_unblocks_and_schedules_repair(self):
        slug = "02-set-or-reset-password"
        art = self.root / "articles" / slug
        art.mkdir(parents=True, exist_ok=True)
        (art / "STATE").write_text(
            "PHASE=BLOCKED\nRESUME_PHASE=TESTING\nBLOCKED_REASON=test failure\n"
        )
        (art / "test-notes.md").write_text("# test-notes\n\nfailures\n")
        code, payload, _ = self._req("POST", "/api/queue/resolve-blocked", {
            "slug": slug,
            "instructions": "Click Share a folder not Share files",
        })
        self.assertEqual(code, 200)
        self.assertTrue(payload["ok"])
        fields = self.pw._qs.read_state_fields(art / "STATE")
        self.assertEqual(fields["PHASE"], "TESTING")
        self.assertEqual(fields["NEXT_ACTION"], "repair-test-plan")
        self.assertEqual(fields["TEST_ATTEMPT"], "0")
        self.assertFalse((art / "test-notes.md").exists())
        self.assertTrue((art / "operator-instructions.md").is_file())

    def test_get_article_test_notes(self):
        slug = "02-set-or-reset-password"
        art = self.root / "articles" / slug
        art.mkdir(parents=True, exist_ok=True)
        (art / "test-notes.md").write_text("# notes\n\nstep failed\n")
        code, payload, _ = self._req("GET", f"/api/articles/{slug}/test-notes")
        self.assertEqual(code, 200)
        self.assertIn("step failed", payload["content"])

    def test_poll_now_regression(self):
        code, payload, _ = self._req("POST", "/poll-now")
        self.assertEqual(code, 200)
        self.assertTrue(payload["ok"])

    def test_get_api_docs(self):
        code, payload, _ = self._req("GET", "/api/docs")
        self.assertEqual(code, 200)
        self.assertEqual(len(payload["docs"]), 8)
        self.assertEqual(payload["docs"][0]["id"], "articles-plan")

    def test_get_api_doc_by_id(self):
        glossary = self.root / "canon" / "GLOSSARY.md"
        glossary.parent.mkdir(parents=True, exist_ok=True)
        glossary.write_text("# Glossary\n", encoding="utf-8")
        code, payload, _ = self._req("GET", "/api/docs/glossary")
        self.assertEqual(code, 200)
        self.assertEqual(payload["id"], "glossary")
        self.assertIn("Glossary", payload["content"])

    def test_get_api_doc_not_found(self):
        code, payload, _ = self._req("GET", "/api/docs/bad-id")
        self.assertEqual(code, 404)
        self.assertEqual(payload["error"], "doc not found")

    def test_put_api_doc(self):
        with mock.patch.object(self.pw.subprocess, "run") as git_run:
            git_run.return_value.returncode = 0
            code, payload, _ = self._req("PUT", "/api/docs/glossary", {"content": "hello"})
        self.assertEqual(code, 200)
        self.assertTrue(payload["ok"])
        written = self.root / "canon" / "GLOSSARY.md"
        self.assertEqual(written.read_text(encoding="utf-8"), "hello")
        commit_calls = [
            c.args[0] for c in git_run.call_args_list
            if c.args and isinstance(c.args[0], list) and "commit" in c.args[0]
        ]
        self.assertTrue(commit_calls)
        self.assertIn("docs(canon): update glossary via ghostwriter", commit_calls[0])

    def test_put_api_doc_unknown(self):
        with mock.patch.object(self.pw.subprocess, "run"):
            code, payload, _ = self._req("PUT", "/api/docs/bad-id", {"content": "x"})
        self.assertEqual(code, 404)
        self.assertEqual(payload["error"], "unknown doc")

    def test_put_api_doc_missing_content(self):
        with mock.patch.object(self.pw.subprocess, "run"):
            code, payload, _ = self._req("PUT", "/api/docs/glossary", {})
        self.assertEqual(code, 400)
        self.assertEqual(payload["error"], "content required")

    def test_get_doc_preview(self):
        glossary = self.root / "canon" / "GLOSSARY.md"
        glossary.parent.mkdir(parents=True, exist_ok=True)
        glossary.write_text("# Glossary\n\nhello", encoding="utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/docs/glossary/preview",
            method="GET",
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertTrue(resp.headers.get("Content-Type", "").startswith("text/html"))
            body = resp.read().decode()
            self.assertIn("ghostwriter-annotate.js", body)
            self.assertIn('data-slug="doc--glossary"', body)

    def test_get_doc_preview_not_found(self):
        try:
            urllib.request.urlopen(
                f"http://127.0.0.1:{self.port}/api/docs/bad-id/preview",
            )
            self.fail("expected HTTPError")
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 404)
            payload = json.loads(exc.read().decode())
            self.assertIn("doc preview not found", payload["error"])

    def test_get_article_research(self):
        slug = "02-set-or-reset-password"
        research = self.root / "articles" / slug / "research"
        research.mkdir(parents=True, exist_ok=True)
        (research / "competitor-coverage.md").write_text("# coverage\n", encoding="utf-8")
        snap = research / "ui-snapshot"
        snap.mkdir()
        (snap / "ui-glossary.md").write_text("# glossary\n", encoding="utf-8")
        (snap / "a.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        code, payload, _ = self._req("GET", f"/api/articles/{slug}/research")
        self.assertEqual(code, 200)
        self.assertEqual(payload["slug"], slug)
        self.assertEqual(len(payload["files"]), 2)
        self.assertEqual(payload["files"][0]["name"], "competitor-coverage.md")
        self.assertEqual(payload["files"][1]["name"], "ui-snapshot/ui-glossary.md")
        self.assertEqual(payload["images"], ["a.png"])

    def test_get_article_research_empty(self):
        slug = "99-no-research"
        code, payload, _ = self._req("GET", f"/api/articles/{slug}/research")
        self.assertEqual(code, 200)
        self.assertEqual(payload["files"], [])
        self.assertEqual(payload["images"], [])

    def test_get_research_asset_png(self):
        slug = "02-set-or-reset-password"
        snap = self.root / "articles" / slug / "research" / "ui-snapshot"
        snap.mkdir(parents=True, exist_ok=True)
        (snap / "a.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/articles/{slug}/research/asset/a.png",
            method="GET",
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers.get("Content-Type"), "image/png")

    def test_get_research_asset_bad_name(self):
        slug = "02-set-or-reset-password"
        code, payload, _ = self._req(
            "GET", f"/api/articles/{slug}/research/asset/../STATE",
        )
        self.assertEqual(code, 400)
        self.assertEqual(payload["error"], "bad asset name")

    def test_get_research_asset_missing(self):
        slug = "02-set-or-reset-password"
        code, payload, _ = self._req(
            "GET", f"/api/articles/{slug}/research/asset/missing.png",
        )
        self.assertEqual(code, 404)
        self.assertEqual(payload["error"], "asset not found")

    def test_post_doc_revise_no_feedback(self):
        code, payload, _ = self._req("POST", "/api/docs/glossary/revise", {})
        self.assertEqual(code, 400)
        self.assertEqual(payload["error"], "no doc feedback")

    def test_post_doc_revise_launches(self):
        import feedback_store as fb
        fb.write_feedback("doc--glossary", [{"id": "a1", "body": [{"value": "fix term"}]}])
        with mock.patch.object(self.pw, "is_claude_running", return_value=False):
            with mock.patch.object(self.pw, "_launch_doc_revise") as launch:
                code, payload, _ = self._req("POST", "/api/docs/glossary/revise", {})
        self.assertEqual(code, 200)
        self.assertTrue(payload["launched"])
        launch.assert_called_once_with("doc--glossary")

    def test_post_doc_revise_queues_when_busy(self):
        import feedback_store as fb
        fb.write_feedback("doc--glossary", [{"id": "a2", "body": [{"value": "fix"}]}])
        with mock.patch.object(self.pw, "is_claude_running", return_value=True):
            code, payload, _ = self._req("POST", "/api/docs/glossary/revise", {})
        self.assertEqual(code, 200)
        self.assertFalse(payload["launched"])
        self.assertTrue(
            any(t.get("reason") == "doc-revise-launch" for t in self.pw._manual_trigger_set),
        )

    def test_post_doc_revise_unknown(self):
        code, payload, _ = self._req("POST", "/api/docs/bad-id/revise", {})
        self.assertEqual(code, 404)
        self.assertEqual(payload["error"], "unknown doc")


if __name__ == "__main__":
    unittest.main()
