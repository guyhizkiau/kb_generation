"""Unit tests for preview HTML transform."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from preview_transform import (
    ensure_article_html,
    load_preview_html,
    patch_article_preview_html,
    resolve_preview_html,
    select_preview_source,
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

REPO_ROOT = Path(__file__).resolve().parents[2]


class PreviewTransformTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cache_dir = self.root / "preview-cache"
        os.environ["GHOSTWRITER_PREVIEW_CACHE"] = str(self.cache_dir)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("GHOSTWRITER_PREVIEW_CACHE", None)

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

    def test_load_preview_html_existing_in_tree(self):
        slug = "01-test"
        art = self.root / "articles" / slug
        art.mkdir(parents=True)
        (art / "final.md").write_text("# Title\n")
        html_file = art / f"{slug}.html"
        html_file.write_text(
            "<html><head></head><body><main>hi</main></body></html>"
        )
        os.utime(html_file, None)
        code, html = load_preview_html(self.root, slug, "http://127.0.0.1:8767")
        self.assertEqual(code, 200)
        self.assertIn("ghostwriter-annotate.js", html)

    def test_ensure_article_html_missing_without_source(self):
        self.assertIsNone(ensure_article_html(self.root, "99-nope"))

    def test_resolve_preview_html_uses_working_tree(self):
        slug = "01-test"
        art = self.root / "articles" / slug
        art.mkdir(parents=True)
        (art / "final.md").write_text("# Title\n")
        html_file = art / f"{slug}.html"
        html_file.write_text(
            "<html><head></head><body><main>working tree</main></body></html>"
        )
        os.utime(html_file, None)
        code, html = resolve_preview_html(self.root, slug, "http://127.0.0.1:8767")
        self.assertEqual(code, 200)
        self.assertIn("working tree", html)

    def test_preview_never_writes_final_md(self):
        slug = "02-draft-only"
        art = self.root / "articles" / slug
        art.mkdir(parents=True)
        (art / "draft-1.md").write_text("# Draft only\n\n> Screenshot: placeholder\n")
        before = {p.name for p in art.iterdir()}
        ensure_article_html(self.root, slug)
        after = {p.name for p in art.iterdir()}
        self.assertEqual(before, after)
        self.assertFalse((art / "final.md").exists())

    def test_select_preview_source_prefers_final_then_latest_draft(self):
        art = self.root / "articles" / "03-src"
        art.mkdir(parents=True)
        (art / "draft-1.md").write_text("# one\n")
        (art / "draft-2.md").write_text("# two\n")
        self.assertEqual(select_preview_source(art).name, "draft-2.md")
        (art / "final.md").write_text("# final\n")
        self.assertEqual(select_preview_source(art).name, "final.md")

    def test_preview_renders_to_cache_from_latest_draft(self):
        slug = "04-cache"
        art = self.root / "articles" / slug
        art.mkdir(parents=True)
        (art / "draft-1.md").write_text("# Cached preview\n\nBody text.\n")
        html_path = ensure_article_html(self.root, slug)
        self.assertIsNotNone(html_path)
        assert html_path is not None
        self.assertEqual(html_path.parent, self.cache_dir)
        self.assertIn("Cached preview", html_path.read_text(encoding="utf-8"))
        self.assertFalse((art / f"{slug}.html").exists())

    def test_stale_in_tree_html_preferred_over_rerender(self):
        slug = "06-in-tree"
        art = self.root / "articles" / slug
        art.mkdir(parents=True)
        final_md = art / "final.md"
        html_file = art / f"{slug}.html"
        html_file.write_text("<html><head></head><body><main>committed</main></body></html>")
        final_md.write_text("# Published\n")
        html_mtime = html_file.stat().st_mtime
        os.utime(final_md, (html_mtime + 0.001, html_mtime + 0.001))
        html_path = ensure_article_html(self.root, slug)
        self.assertEqual(html_path, html_file)
        self.assertIn("committed", html_path.read_text(encoding="utf-8"))

    def test_stale_cache_rerenders_when_source_changes(self):
        slug = "05-stale"
        art = self.root / "articles" / slug
        art.mkdir(parents=True)
        draft = art / "draft-1.md"
        draft.write_text("# Version 1\n")
        first = ensure_article_html(self.root, slug)
        assert first is not None
        self.assertIn("Version 1", first.read_text(encoding="utf-8"))

        time.sleep(0.05)
        draft.write_text("# Version 2\n")
        second = ensure_article_html(self.root, slug)
        assert second is not None
        self.assertIn("Version 2", second.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
