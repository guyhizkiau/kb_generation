"""Unit tests for preview HTML transform."""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from preview_transform import (
    ensure_article_html,
    load_preview_html,
    load_preview_html_from_ref,
    patch_article_preview_html,
)


OLD_WIDGET_HTML = """<!doctype html>
<html><head><meta charset="utf-8"></head>
<body><main><p>Hello world</p></main>
<script src="/static/recogito.min.js"></script>
<script>
(function(){
  var SLUG = "01-test";
  function postAnnotation() { if (!N8N_WEBHOOK) return; }
  window.addEventListener("DOMContentLoaded", function() {
    Recogito.init({ content: document.querySelector("main") });
  });
})();
</script>
</body></html>"""


class PreviewTransformTests(unittest.TestCase):
    def test_strips_legacy_inline_widget(self):
        out = patch_article_preview_html(OLD_WIDGET_HTML, "01-test", "http://127.0.0.1:8767")
        self.assertNotIn("postAnnotation", out)
        self.assertIn("ghostwriter-annotate.js", out)
        self.assertIn('data-slug="01-test"', out)

    def test_injects_ghostwriter_config(self):
        out = patch_article_preview_html(OLD_WIDGET_HTML, "01-test", "http://127.0.0.1:8767")
        self.assertIn('window.__GHOSTWRITER__={"apiBase": "http://127.0.0.1:8767", "n8nWebhook": ""}', out)

    def test_adds_recogito_assets_when_missing(self):
        bare = "<html><head></head><body><main>x</main></body></html>"
        out = patch_article_preview_html(bare, "02-other", "http://localhost")
        self.assertIn("recogito.min.css", out)
        self.assertIn("recogito.min.js", out)

    def test_load_preview_html_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slug = "01-test"
            art = root / "articles" / slug
            art.mkdir(parents=True)
            (art / f"{slug}.html").write_text(
                "<html><head></head><body><main>hi</main></body></html>"
            )
            code, html = load_preview_html(root, slug, "http://127.0.0.1:8767")
            self.assertEqual(code, 200)
            self.assertIn("ghostwriter-annotate.js", html)

    def test_ensure_article_html_missing_without_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertIsNone(ensure_article_html(root, "99-nope"))

    def test_load_preview_html_from_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slug = "01-test"
            art = root / "articles" / slug
            art.mkdir(parents=True)
            (art / f"{slug}.html").write_text(
                "<html><head></head><body><main>from ref</main></body></html>"
            )
            import subprocess
            subprocess.run(["git", "init"], cwd=root, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "t@test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
            subprocess.run(["git", "add", "-A"], cwd=root, capture_output=True, check=True)
            subprocess.run(["git", "commit", "-m", "html"], cwd=root, capture_output=True, check=True)
            branch = f"article/{slug}"
            subprocess.run(["git", "branch", branch], cwd=root, check=True)
            code, html = load_preview_html_from_ref(root, slug, "http://127.0.0.1:8767", branch)
            self.assertEqual(code, 200)
            self.assertIn("from ref", html)
            self.assertIn("ghostwriter-annotate.js", html)

    def test_load_preview_html_from_ref_renders_draft(self):
        repo_root = Path(__file__).resolve().parent.parent.parent
        slug = "04-share-a-file"
        ref = "origin/article/04-share-a-file"
        check = subprocess.run(
            ["git", "rev-parse", "--verify", ref],
            cwd=repo_root,
            capture_output=True,
        )
        if check.returncode != 0:
            self.skipTest(f"{ref} not available locally")
        code, html = load_preview_html_from_ref(
            repo_root, slug, "http://127.0.0.1:8767", ref,
        )
        self.assertEqual(code, 200)
        self.assertIn("Securely share a file", html)
        self.assertIn("ghostwriter-annotate.js", html)


if __name__ == "__main__":
    unittest.main()
