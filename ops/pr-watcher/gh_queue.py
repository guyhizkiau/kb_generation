"""GitHub PR helpers for Ghostwriter queue enrichment and merge actions."""
from __future__ import annotations

import json
import os
import subprocess

DEFAULT_REPO = "guyhizkiau/kb_generation"


def github_repo() -> str:
    return os.environ.get("GITHUB_REPO", DEFAULT_REPO)


def open_prs_by_slug(repo: str | None = None) -> dict[str, int]:
    """Map article slug → open PR number for branches ``article/<slug>``."""
    repo = repo or github_repo()
    result = subprocess.run(
        ["gh", "pr", "list", "--repo", repo,
         "--json", "number,headRefName", "--state", "open"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gh pr list failed")
    by_slug: dict[str, int] = {}
    for pr in json.loads(result.stdout):
        branch = pr.get("headRefName", "")
        if not branch.startswith("article/"):
            continue
        slug = branch[len("article/"):].strip("/")
        if slug and "/" not in slug:
            by_slug[slug] = int(pr["number"])
    return by_slug


def enrich_queue_with_open_prs(data: dict, repo: str | None = None) -> dict:
    """Add ``pr_number`` to each queue article that has an open PR."""
    try:
        by_slug = open_prs_by_slug(repo)
    except Exception:
        by_slug = {}
    for cluster in data.get("clusters", []):
        for art in cluster.get("articles", []):
            num = by_slug.get(art.get("slug", ""))
            if num:
                art["pr_number"] = num
            else:
                art.pop("pr_number", None)
    return data


def merge_article_pr(
    slug: str,
    *,
    pr_number: int | None = None,
    repo: str | None = None,
) -> dict:
    """Merge the open PR for *slug* via ``gh pr merge --merge``."""
    repo = repo or github_repo()
    if not slug.strip():
        return {"ok": False, "error": "slug required"}
    slug = slug.strip()
    if pr_number is None:
        pr_number = open_prs_by_slug(repo).get(slug)
    if not pr_number:
        return {"ok": False, "error": f"no open PR for {slug}"}
    result = subprocess.run(
        ["gh", "pr", "merge", str(pr_number), "--repo", repo, "--merge"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "gh pr merge failed").strip()
        return {"ok": False, "error": err}
    return {"ok": True, "slug": slug, "pr_number": pr_number}
