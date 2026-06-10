"""Queue I/O and article STATE enrichment for the KB pipeline."""
from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from store.machine import LEGACY_MAP
from store.paths import articles_root, repo_root, state_path
from store.state import read_state_fields, write_state_fields


def article_state_path(slug: str) -> Path:
    """Return canonical articles/<slug>/STATE path (alias for state_path)."""
    return state_path(slug)


def read_state(path: Path) -> str:
    """Read only the PHASE= line from a STATE file. Returns 'UNKNOWN' if absent."""
    if not path.exists():
        return "UNKNOWN"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("PHASE="):
            return line[6:].strip()
    return "UNKNOWN"


def article_state_fields(slug: str) -> dict[str, str]:
    """Read STATE for *slug* from the working tree."""
    return read_state_fields(article_state_path(slug))


def _queue_path() -> Path:
    return repo_root() / "clusters" / "queue.json"


def _worktree_root() -> Path | None:
    env = __import__("os").environ.get("KB_WORKTREE_ROOT")
    if env:
        return Path(env)
    default = Path("/home/ubuntu/kb_generation-work")
    return default if default.exists() else None


def load_queue() -> dict:
    """Load clusters/queue.json. Raises FileNotFoundError if missing."""
    return json.loads(_queue_path().read_text(encoding="utf-8"))


def strip_queue_for_save(q: dict) -> dict:
    """Remove API-enriched fields before persisting queue.json."""
    clusters = []
    for cluster in q.get("clusters", []):
        clusters.append({
            "id": cluster["id"],
            "title": cluster.get("title", ""),
            "mode": cluster.get("mode", "serial"),
            "status": cluster.get("status", "active"),
            "pause_after": cluster.get("pause_after", False),
            "articles": [
                {"slug": art["slug"], "title": art.get("title", art["slug"])}
                for art in cluster.get("articles", [])
            ],
        })
    return {"version": q.get("version", 1), "clusters": clusters}


def save_queue(q: dict) -> None:
    """Atomically write clusters/queue.json (tmp+os.replace pattern)."""
    q = strip_queue_for_save(q)
    path = _queue_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(q, indent=2, ensure_ascii=False)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(data)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def remove_article_from_queue(slug: str) -> bool:
    """Remove *slug* from every cluster in queue.json. Returns True if present."""
    q = load_queue()
    present = False
    for cluster in q.get("clusters", []):
        before = cluster.get("articles", [])
        after = [a for a in before if a.get("slug") != slug]
        if len(after) != len(before):
            present = True
        cluster["articles"] = after
    if present:
        save_queue(q)
    return present


def delete_article_dir(slug: str) -> bool:
    """Delete articles/<slug>/ from the main tree and worktree. Idempotent."""
    removed = False
    candidates = [articles_root() / slug]
    wt = _worktree_root()
    if wt:
        candidates.append(wt / "articles" / slug)
    for path in candidates:
        if path.exists():
            shutil.rmtree(path)
            removed = True
    return removed


def article_is_merged(slug: str) -> bool:
    """True when *slug*'s phase is terminal (published)."""
    fields = read_state_fields(article_state_path(slug))
    raw = fields.get("PHASE", "UNKNOWN")
    return raw in TERMINAL_PHASES or LEGACY_MAP.get(raw, raw) == "PUBLISHED"


SLUG_RE = re.compile(r"^\d{2}-[a-z0-9-]+$")
VALID_MODES = {"serial", "parallel"}
VALID_STATUSES = {"active", "paused", "done"}
TERMINAL_PHASES = {"PUBLISHED"}


def next_article(merged_slug: str, q: dict | None = None) -> dict:
    """Pure advance logic — no side effects."""
    if q is None:
        q = load_queue()

    for cluster in q.get("clusters", []):
        articles = cluster.get("articles", [])
        slugs = [a["slug"] for a in articles]
        if merged_slug not in slugs:
            continue

        cid = cluster["id"]

        state_path_val = article_state_path(merged_slug)
        fields = read_state_fields(state_path_val)
        try:
            rc = int(fields.get("REVISION_CYCLE", "0"))
        except ValueError:
            rc = 0
        if rc > 0:
            return {"action": "noop", "cluster_id": cid, "articles": [],
                    "pause_notice": "revision-cycle re-merge, not advancing cluster"}

        if cluster.get("status") == "paused":
            return {"action": "paused", "cluster_id": cid, "articles": [],
                    "pause_notice": f"cluster {cid} is paused"}

        idx = slugs.index(merged_slug)

        if idx >= len(articles) - 1:
            if cluster.get("pause_after"):
                return {"action": "pause", "cluster_id": cid, "articles": [],
                        "pause_notice": (
                            f"All articles in cluster {cid} merged. "
                            "Pausing for review before next cluster."
                        )}
            clusters = q.get("clusters", [])
            cidx = next((i for i, c in enumerate(clusters) if c["id"] == cid), -1)
            if cidx < 0 or cidx >= len(clusters) - 1:
                return {"action": "cluster_done", "cluster_id": cid, "articles": [],
                        "pause_notice": f"cluster {cid} complete, no next cluster"}
            next_cluster = clusters[cidx + 1]
            if next_cluster.get("status") == "paused":
                return {"action": "paused", "cluster_id": next_cluster["id"], "articles": [],
                        "pause_notice": f"next cluster {next_cluster['id']} is paused"}
            next_arts = next_cluster.get("articles", [])
            if not next_arts:
                return {"action": "cluster_done", "cluster_id": next_cluster["id"],
                        "articles": [], "pause_notice": "next cluster is empty"}
            art = next_arts[0]
            return {"action": "next_article", "cluster_id": next_cluster["id"],
                    "articles": [{"slug": art["slug"], "title": art["title"], "num": 1}],
                    "pause_notice": ""}

        next_art = articles[idx + 1]
        return {"action": "next_article", "cluster_id": cid,
                "articles": [{"slug": next_art["slug"], "title": next_art["title"],
                               "num": idx + 2}],
                "pause_notice": ""}

    return {"action": "unknown", "cluster_id": "", "articles": [],
            "pause_notice": f"merged slug '{merged_slug}' not found in any cluster"}


def queue_with_states(q: dict | None = None) -> dict:
    """Return queue enriched with live STATE data per article."""
    if q is None:
        q = load_queue()

    publish_stale: list[str] = []
    next_slug: str | None = None

    enriched_clusters = []
    for cluster in q.get("clusters", []):
        enriched_articles = []
        last_merged: str | None = None
        for art in cluster.get("articles", []):
            fields = article_state_fields(art["slug"])
            raw_phase = fields.get("PHASE", "UNKNOWN")
            phase = LEGACY_MAP.get(raw_phase, raw_phase)
            try:
                rc = int(fields.get("REVISION_CYCLE", "0"))
            except ValueError:
                rc = 0
            stale = fields.get("PUBLISH_STALE", "false").lower() == "true"
            if stale:
                publish_stale.append(art["slug"])
            if raw_phase in TERMINAL_PHASES or phase == "PUBLISHED":
                last_merged = art["slug"]
            enriched_articles.append({
                **art,
                "phase": phase,
                "revision_cycle": rc,
                "publish_stale": stale,
                "feedback_issue": fields.get("FEEDBACK_ISSUE", ""),
                "rework_reason": fields.get("REWORK_REASON", ""),
                "last_update": fields.get("LAST_UPDATE", ""),
            })
        enriched_clusters.append({**cluster, "articles": enriched_articles})
        if last_merged:
            plan = next_article(last_merged, q)
            if plan["action"] == "next_article" and plan["articles"]:
                next_slug = plan["articles"][0]["slug"]

    return {
        **q,
        "clusters": enriched_clusters,
        "next_slug": next_slug,
        "publish_stale": publish_stale,
    }


def validate_slugs(q: dict) -> list[dict]:
    """Validate the queue. Returns issues with level 'error' or 'warning'."""
    issues: list[dict] = []
    seen: set[str] = set()

    for cluster in q.get("clusters", []):
        cid = cluster.get("id", "?")
        mode = cluster.get("mode", "serial")
        status = cluster.get("status", "active")

        if mode not in VALID_MODES:
            issues.append({"level": "error",
                            "message": f"cluster {cid}: invalid mode '{mode}'"})
        if status not in VALID_STATUSES:
            issues.append({"level": "error",
                            "message": f"cluster {cid}: invalid status '{status}'"})

        for art in cluster.get("articles", []):
            slug = art.get("slug", "")
            if not SLUG_RE.match(slug):
                issues.append({"level": "error",
                                "message": f"cluster {cid}: slug '{slug}' doesn't match NN-name pattern"})
            if slug in seen:
                issues.append({"level": "error",
                                "message": f"duplicate slug '{slug}'"})
            seen.add(slug)
            if not article_state_path(slug).parent.exists():
                issues.append({"level": "warning",
                                "message": f"slug '{slug}': articles/{slug}/ does not exist yet"})

    return issues
