#!/usr/bin/env python3
"""Migrate article branches onto main for the single-branch pipeline."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from store.machine import LEGACY_MAP, current_phase, transition  # noqa: E402
from store.paths import article_dir, repo_root  # noqa: E402
from store.queue import load_queue  # noqa: E402
from store.state import read_state, write_state  # noqa: E402


def _git(*args: str, cwd: Path | None = None) -> str:
    r = subprocess.run(
        ["git", *args],
        cwd=str(cwd or repo_root()),
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()


def _article_refs() -> list[tuple[str, str]]:
    out = _git("branch", "-r")
    refs = []
    for line in out.splitlines():
        ref = line.strip().lstrip("* ").strip()
        if ref.startswith("origin/article/"):
            slug = ref.split("origin/article/", 1)[1]
            refs.append((slug, ref))
    return refs


def _backfill_verified(slug: str) -> None:
    fields = read_state(slug)
    if current_phase(slug) != "PUBLISHED":
        return
    if fields.get("VERIFIED_AS_OF"):
        return
    notes = article_dir(slug) / "test-notes.md"
    if notes.is_file():
        for line in notes.read_text(encoding="utf-8").splitlines():
            if line.startswith("Generated:"):
                write_state(slug, {"VERIFIED_AS_OF": line.split(":", 1)[1].strip()})
                return
    write_state(slug, {"VERIFIED_AS_OF": fields.get("LAST_UPDATE", "")})


def migrate(*, dry_run: bool = False, root: Path | None = None) -> None:
    if root:
        import os
        os.environ["KB_REPO_ROOT"] = str(root)
    if not dry_run:
        try:
            _git("fetch", "origin")
        except RuntimeError:
            pass
    refs = _article_refs()
    print(f"Found {len(refs)} article branch refs")
    for slug, ref in refs:
        print(f"  land {slug} from {ref}")
        if not dry_run:
            _git("checkout", "main")
            _git("checkout", ref, "--", f"articles/{slug}/")

    in_flight: list[str] = []
    q = load_queue()
    for cluster in q.get("clusters", []):
        for art in cluster.get("articles", []):
            slug = art["slug"]
            if not (article_dir(slug) / "STATE").exists():
                continue
            phase = current_phase(slug)
            if phase not in ("PUBLISHED", "SKIPPED"):
                in_flight.append(slug)

    keeper = in_flight[0] if in_flight else None
    print(f"In-flight keeper: {keeper}")
    for slug in in_flight:
        if slug == keeper:
            continue
        print(f"  reset {slug} → QUEUED")
        if not dry_run:
            write_state(slug, {"PHASE": "QUEUED", "NEXT_ACTION": ""})

    for cluster in q.get("clusters", []):
        for art in cluster.get("articles", []):
            slug = art["slug"]
            if not (article_dir(slug) / "STATE").exists():
                continue
            fields = read_state(slug)
            raw = fields.get("PHASE", "")
            mapped = LEGACY_MAP.get(raw, raw)
            if mapped != raw:
                print(f"  map {slug} {raw} → {mapped}")
                if not dry_run:
                    transition(slug, mapped)
            _backfill_verified(slug)

    fb_dir = root / ".ghostwriter" / "feedback" if root else repo_root() / ".ghostwriter" / "feedback"
    if fb_dir.exists():
        for fp in fb_dir.glob("*.json"):
            slug = fp.stem
            dest = article_dir(slug) / "feedback.json"
            print(f"  copy feedback {slug}")
            if not dry_run:
                shutil.copy2(fp, dest)

    if dry_run:
        print("Dry run — no commit")
    else:
        _git("add", "-A")
        status = _git("status", "--porcelain")
        if status.strip():
            _git("commit", "-m", "chore(pipeline): migrate article branches to single-branch model")
            print("Committed migration")
        else:
            print("No changes to commit")

    print("\nOperator cleanup (not executed):")
    for slug, _ in refs:
        print(f"  gh pr close --comment 'superseded by single-branch pipeline'  # article/{slug}")
        print(f"  git push origin --delete article/{slug}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--repo", type=Path, default=None)
    args = p.parse_args()
    migrate(dry_run=args.dry_run, root=args.repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
