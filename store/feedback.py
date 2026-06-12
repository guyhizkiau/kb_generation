"""Ghostwriter annotation store — per-article feedback.json by default."""
from __future__ import annotations

import json
import os
from pathlib import Path

from store.paths import repo_root


def feedback_path(slug: str) -> Path:
    """Per-slug annotation JSON — articles/<slug>/feedback.json unless overridden."""
    env = os.environ.get("GHOSTWRITER_FEEDBACK_DIR")
    if env:
        return Path(env) / f"{slug}.json"
    if slug.startswith("doc--"):
        return repo_root() / "docs-feedback" / f"{slug}.json"
    return repo_root() / "articles" / slug / "feedback.json"


def feedback_dir() -> Path:
    """Resolve the feedback directory (override via GHOSTWRITER_FEEDBACK_DIR)."""
    env = os.environ.get("GHOSTWRITER_FEEDBACK_DIR")
    if env:
        return Path(env)
    return repo_root() / "articles"


def read_feedback(slug: str) -> list:
    """Return stored annotations for *slug*, or an empty list."""
    fp = feedback_path(slug)
    if not fp.exists():
        return []
    return json.loads(fp.read_text(encoding="utf-8"))


def write_feedback(slug: str, annotations: list) -> None:
    """Replace all annotations for *slug*."""
    fp = feedback_path(slug)
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps(annotations, indent=2) + "\n", encoding="utf-8")


def append_feedback(slug: str, annotation: dict) -> dict:
    """Append one annotation; dedupe by ``id``."""
    ann_id = annotation.get("id")
    if not ann_id:
        return {"ok": False, "error": "annotation id required"}
    annotations = read_feedback(slug)
    if any(a.get("id") == ann_id for a in annotations):
        return {"ok": True, "annotation": annotation, "deduped": True}
    annotations.append(annotation)
    write_feedback(slug, annotations)
    return {"ok": True, "annotation": annotation}


def delete_feedback(slug: str) -> bool:
    """Delete the entire annotation file for *slug*. Returns True if removed."""
    fp = feedback_path(slug)
    if fp.exists():
        fp.unlink()
        return True
    return False


def merge_feedback(slug: str, new_annotations: list) -> list:
    """Merge *new_annotations* into the existing store for *slug*."""
    existing = read_feedback(slug)
    existing_ids = {a.get("id") for a in existing}
    merged = existing + [a for a in new_annotations if a.get("id") not in existing_ids]
    write_feedback(slug, merged)
    return merged


def remove_feedback(slug: str, ann_id: str) -> dict:
    """Remove one annotation by ``id``."""
    if not ann_id:
        return {"ok": False, "error": "id required"}
    annotations = read_feedback(slug)
    kept = [a for a in annotations if a.get("id") != ann_id]
    if len(kept) == len(annotations):
        return {"ok": False, "error": "annotation not found"}
    write_feedback(slug, kept)
    return {"ok": True, "id": ann_id}
