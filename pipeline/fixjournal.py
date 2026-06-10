"""Atomic feedback-fix journal for assets-first then article commits."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from store.paths import article_dir, repo_root

CANON_PREFIXES = ("editorial/", "canon/", "product/", "pipeline/prompts/")


def journal_path(slug: str) -> Path:
    return article_dir(slug) / ".fix-journal.json"


def open_journal(slug: str, annotation_ids: list[str]) -> Path:
    """Record base SHA before a feedback-fix begins."""
    path = journal_path(slug)
    if path.exists():
        raise RuntimeError(f"fix journal already open for {slug}")
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root(), capture_output=True, text=True, check=True,
    ).stdout.strip()
    data = {
        "slug": slug,
        "base_sha": base,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "annotation_ids": annotation_ids,
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def close_journal(slug: str) -> None:
    """Validate two commits since base_sha and delete the journal."""
    path = journal_path(slug)
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    base = data["base_sha"]
    log_out = subprocess.run(
        ["git", "log", f"{base}..HEAD", "--name-only", "--pretty=format:%H"],
        cwd=repo_root(), capture_output=True, text=True, check=True,
    ).stdout
    commits = [c for c in log_out.split("\n\n") if c.strip()]
    if len(commits) < 2:
        raise RuntimeError(f"expected ≥2 commits since {base}, got {len(commits)}")
    path.unlink()


def recover(slug: str) -> str | None:
    """Reset to base_sha if journal is open with incomplete commits."""
    path = journal_path(slug)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    base = data["base_sha"]
    count = subprocess.run(
        ["git", "rev-list", "--count", f"{base}..HEAD"],
        cwd=repo_root(), capture_output=True, text=True, check=True,
    ).stdout.strip()
    if int(count) >= 2:
        path.unlink()
        return None
    subprocess.run(["git", "reset", "--hard", base], cwd=repo_root(), check=True)
    path.unlink()
    return "reset"
