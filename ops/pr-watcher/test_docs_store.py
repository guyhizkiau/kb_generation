"""Unit tests for docs_store."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import docs_store


class DocsStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_list_docs_order_and_metadata(self):
        style_path = self.root / "editorial" / "STYLE_GUIDE.md"
        style_path.parent.mkdir(parents=True)
        style_path.write_text("# Style", encoding="utf-8")

        docs = docs_store.list_docs(self.root)
        self.assertEqual(len(docs), 8)
        self.assertEqual(docs[0]["id"], "articles-plan")
        self.assertEqual(docs[1]["id"], "style-guide")
        self.assertTrue(docs[1]["exists"])
        self.assertIsInstance(docs[1]["mtime"], float)
        self.assertFalse(docs[0]["exists"])
        self.assertIsNone(docs[0]["mtime"])

    def test_read_doc(self):
        path = self.root / "editorial" / "STYLE_GUIDE.md"
        path.parent.mkdir(parents=True)
        path.write_text("hello style", encoding="utf-8")
        self.assertEqual(docs_store.read_doc(self.root, "style-guide"), "hello style")
        self.assertIsNone(docs_store.read_doc(self.root, "missing-id"))

    def test_write_doc(self):
        self.assertTrue(docs_store.write_doc(self.root, "glossary", "x"))
        written = self.root / "canon" / "GLOSSARY.md"
        self.assertTrue(written.is_file())
        self.assertEqual(written.read_text(encoding="utf-8"), "x")
        self.assertFalse(docs_store.write_doc(self.root, "bad", "x"))
        self.assertFalse((self.root / "bad").exists())

    def test_doc_area_and_path(self):
        self.assertEqual(docs_store.doc_area("glossary"), "canon")
        self.assertEqual(docs_store.doc_area("style-guide"), "editorial")
        self.assertEqual(docs_store.doc_area("nope"), "")
        self.assertIsNone(docs_store.doc_path(self.root, "nope"))


if __name__ == "__main__":
    unittest.main()
