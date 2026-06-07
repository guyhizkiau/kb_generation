"""queue_store.py — queue-as-data helpers for the KB article pipeline.

Importable by pr-watcher.py and runnable standalone for tests.
Root resolves via KB_REPO_ROOT env (daemon sets it to REPO_PATH);
defaults to repo root derived from __file__.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

# ── repo root resolution ──────────────────────────────────────────────────────

def _repo_root() -> Path:
    env = os.environ.get("KB_REPO_ROOT")
    if env:
        return Path(env)
    # __file__ is ops/pr-watcher/queue_store.py -> go up 2 levels
    return Path(__file__).resolve().parent.parent.parent


def _queue_path() -> Path:
    return _repo_root() / "clusters" / "queue.json"


def _articles_root() -> Path:
    return _repo_root() / "articles"


def _relative_to_repo(path: Path) -> str:
    """Return a repo-relative POSIX path for git show."""
    return path.relative_to(_repo_root()).as_posix()


# ── git ref helpers ───────────────────────────────────────────────────────────

def read_file_at_ref(ref: str, relpath: str) -> str | None:
    """Read file contents at ``ref:relpath`` without checking out the branch."""
    result = subprocess.run(
        ["git", "show", f"{ref}:{relpath}"],
        cwd=_repo_root(),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def article_ref(slug: str) -> str | None:
    """Return a git ref for ``article/<slug>`` when the branch exists locally or on origin."""
    branch = f"article/{slug}"
    for candidate in (f"origin/{branch}", branch):
        result = subprocess.run(
            ["git", "rev-parse", "--verify", candidate],
            cwd=_repo_root(),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return candidate
    return None


def article_state_fields(slug: str) -> dict[str, str]:
    """Read STATE for *slug* from main when merged, else from the article branch ref."""
    sp = article_state_path(slug)
    main_fields = read_state_fields(sp)
    if main_fields.get("PHASE", "UNKNOWN") in TERMINAL_PHASES:
        return main_fields
    ref = article_ref(slug)
    if ref:
        ref_fields = read_state_fields(sp, ref=ref)
        if ref_fields:
            return ref_fields
    return main_fields


# ── queue I/O ─────────────────────────────────────────────────────────────────

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


# ── STATE file helpers ────────────────────────────────────────────────────────

def article_state_path(slug: str) -> Path:
    """Return canonical articles/<slug>/STATE path."""
    return _articles_root() / slug / "STATE"


def read_state(path: Path) -> str:
    """Read only the PHASE= line from a STATE file. Returns 'UNKNOWN' if absent."""
    if not path.exists():
        return "UNKNOWN"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("PHASE="):
            return line[6:].strip()
    return "UNKNOWN"


def read_state_fields(path: Path, *, ref: str | None = None) -> dict[str, str]:
    """Parse ALL KEY=VALUE lines from a STATE file (filesystem or git ref)."""
    if ref:
        content = read_file_at_ref(ref, _relative_to_repo(path))
        if content is None:
            return {}
        lines = content.splitlines()
    elif not path.exists():
        return {}
    else:
        lines = path.read_text(encoding="utf-8").splitlines()
    result: dict[str, str] = {}
    for line in lines:
        if "=" in line and not line.startswith(" ") and not line.startswith("#"):
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip()
    return result


def write_state_fields(path: Path, updates: dict[str, str]) -> None:
    """Read-modify-write STATE preserving key order; atomic; refreshes LAST_UPDATE."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    updates = dict(updates)
    updates["LAST_UPDATE"] = now

    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    else:
        lines = []
        path.parent.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        if "=" in line and not line.startswith(" ") and not line.startswith("#"):
            k = line.partition("=")[0].strip()
            if k in updates:
                out.append(f"{k}={updates[k]}\n")
                seen.add(k)
            else:
                out.append(line if line.endswith("\n") else line + "\n")
        else:
            out.append(line if line.endswith("\n") else line + "\n")

    for k, v in updates.items():
        if k not in seen:
            out.append(f"{k}={v}\n")

    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text("".join(out), encoding="utf-8")
    os.replace(tmp_path, path)


# ── next-article advance logic ────────────────────────────────────────────────

SLUG_RE = re.compile(r"^\d{2}-[a-z0-9-]+$")
VALID_MODES = {"serial", "parallel"}
VALID_STATUSES = {"active", "paused", "done"}
TERMINAL_PHASES = {"MERGED", "DONE"}


def next_article(merged_slug: str, q: dict | None = None) -> dict:
    """
    Pure advance logic — no side effects.

    Returns a plan dict::

        {
          "action": "next_article"|"noop"|"pause"|"cluster_done"|"paused"|"unknown",
          "cluster_id": str,
          "articles": [{"slug": str, "title": str, "num": int}],
          "pause_notice": str,
        }
    """
    if q is None:
        q = load_queue()

    for cluster in q.get("clusters", []):
        articles = cluster.get("articles", [])
        slugs = [a["slug"] for a in articles]
        if merged_slug not in slugs:
            continue

        cid = cluster["id"]
        mode = cluster.get("mode", "serial")

        # Revision-cycle guard: if REVISION_CYCLE > 0 this is a feedback
        # re-merge — do NOT advance the cluster.
        state_path = article_state_path(merged_slug)
        fields = read_state_fields(state_path)
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

        if mode == "parallel":
            eligible = []
            for i, art in enumerate(articles):
                sp = article_state_path(art["slug"])
                phase = read_state(sp)
                if phase in TERMINAL_PHASES:
                    continue
                if phase != "UNKNOWN":
                    continue  # already in-progress
                eligible.append({"slug": art["slug"], "title": art["title"], "num": i + 1})
            if not eligible:
                return {"action": "cluster_done", "cluster_id": cid, "articles": [],
                        "pause_notice": f"all articles in cluster {cid} done"}
            return {"action": "next_article", "cluster_id": cid, "articles": eligible,
                    "pause_notice": ""}

        # serial mode
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


# ── queue + live states for the API ──────────────────────────────────────────

def queue_with_states(q: dict | None = None) -> dict:
    """Return queue enriched with live STATE data per article.

    Adds per-article: phase, revision_cycle, publish_stale, feedback_issue.
    Adds top-level: next_slug, publish_stale (list).
    """
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
            phase = fields.get("PHASE", "UNKNOWN")
            try:
                rc = int(fields.get("REVISION_CYCLE", "0"))
            except ValueError:
                rc = 0
            stale = fields.get("PUBLISH_STALE", "false").lower() == "true"
            if stale:
                publish_stale.append(art["slug"])
            if phase in TERMINAL_PHASES:
                last_merged = art["slug"]
            enriched_articles.append({
                **art,
                "phase": phase,
                "revision_cycle": rc,
                "publish_stale": stale,
                "feedback_issue": fields.get("FEEDBACK_ISSUE", ""),
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


# ── validation ────────────────────────────────────────────────────────────────

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
