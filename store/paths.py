"""Repository and article path resolution for the KB pipeline."""
from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    """Return the repository root (KB_REPO_ROOT override or derived from package location)."""
    env = os.environ.get("KB_REPO_ROOT")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent


def articles_root() -> Path:
    """Return the canonical articles/ directory."""
    return repo_root() / "articles"


def article_dir(slug: str) -> Path:
    """Resolve the article working directory with legacy fallback.

    Prefers ``articles/<slug>/``; falls back to ``workspace/articles/<slug>/``
    only when the canonical path is missing and the legacy path exists.
    """
    root = repo_root()
    canonical = root / "articles" / slug
    legacy = root / "workspace" / "articles" / slug
    if canonical.exists():
        return canonical
    if legacy.exists():
        return legacy
    return canonical


def _worktree_root() -> Path | None:
    """Return the git worktree path if it exists (KB_WORKTREE_ROOT or default)."""
    env = os.environ.get("KB_WORKTREE_ROOT")
    if env:
        return Path(env)
    default = Path("/home/ubuntu/kb_generation-work")
    return default if default.exists() else None


def state_path(slug: str) -> Path:
    """Return ``articles/<slug>/STATE``, preferring the worktree copy when present."""
    wt = _worktree_root()
    if wt:
        wt_path = wt / "articles" / slug / "STATE"
        if wt_path.exists():
            return wt_path
    return article_dir(slug) / "STATE"


def relative_to_repo(path: Path) -> str:
    """Return a repo-relative POSIX path for git show."""
    try:
        return path.relative_to(repo_root()).as_posix()
    except ValueError:
        pass
    wt = _worktree_root()
    if wt:
        try:
            return path.relative_to(wt).as_posix()
        except ValueError:
            pass
    raise ValueError(f"'{path}' is not in the subpath of '{repo_root()}'")
