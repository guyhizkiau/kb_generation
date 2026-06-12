"""Pure registry and read/write helpers for Ghostwriter knowledge docs."""
from __future__ import annotations

from pathlib import Path

DOC_REGISTRY: list[dict] = [
    {
        "id": "articles-plan",
        "title": "Articles plan",
        "group": "Editorial",
        "path": "editorial/ARTICLES_PLAN.md",
    },
    {
        "id": "style-guide",
        "title": "Style guide",
        "group": "Editorial",
        "path": "editorial/STYLE_GUIDE.md",
    },
    {
        "id": "public-kb-scope",
        "title": "Public KB scope",
        "group": "Editorial",
        "path": "editorial/PUBLIC_KB_SCOPE.md",
    },
    {
        "id": "glossary",
        "title": "Glossary",
        "group": "Canon",
        "path": "canon/GLOSSARY.md",
    },
    {
        "id": "do-not-document",
        "title": "Do not document",
        "group": "Canon",
        "path": "canon/DO_NOT_DOCUMENT.md",
    },
    {
        "id": "competitor-patterns",
        "title": "Competitor patterns",
        "group": "Canon",
        "path": "canon/COMPETITOR_PATTERNS.md",
    },
    {
        "id": "component-taxonomy",
        "title": "Component taxonomy",
        "group": "Product",
        "path": "product/COMPONENT_TAXONOMY.md",
    },
    {
        "id": "product-notes",
        "title": "Product notes",
        "group": "Product",
        "path": "product/notes.md",
    },
]


def doc_entry(doc_id: str) -> dict | None:
    """Return registry entry for *doc_id*, or ``None`` if unknown."""
    for entry in DOC_REGISTRY:
        if entry["id"] == doc_id:
            return entry
    return None


def doc_path(repo_root: Path, doc_id: str) -> Path | None:
    """Return absolute path for *doc_id*, or ``None`` if unknown."""
    entry = doc_entry(doc_id)
    if entry is None:
        return None
    return repo_root / entry["path"]


def doc_area(doc_id: str) -> str:
    """Return first path segment (editorial, canon, product) or empty string."""
    entry = doc_entry(doc_id)
    if entry is None:
        return ""
    return entry["path"].split("/", 1)[0]


def list_docs(repo_root: Path) -> list[dict]:
    """Return registry entries enriched with exists/mtime."""
    out: list[dict] = []
    for entry in DOC_REGISTRY:
        path = repo_root / entry["path"]
        exists = path.is_file()
        mtime = path.stat().st_mtime if exists else None
        out.append({
            "id": entry["id"],
            "title": entry["title"],
            "group": entry["group"],
            "path": entry["path"],
            "exists": exists,
            "mtime": mtime,
        })
    return out


def read_doc(repo_root: Path, doc_id: str) -> str | None:
    """Return file text for *doc_id*, or ``None`` if unknown or missing."""
    path = doc_path(repo_root, doc_id)
    if path is None or not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def write_doc(repo_root: Path, doc_id: str, text: str) -> bool:
    """Write utf-8 text for *doc_id*. Returns ``False`` if id unknown."""
    path = doc_path(repo_root, doc_id)
    if path is None:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True
