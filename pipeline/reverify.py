"""Re-verification triggers for stale published articles."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from store.machine import current_phase, transition
from store.paths import articles_root, repo_root
from store.state import read_state

RELEASE_FILE = repo_root() / "product" / "CURRENT_RELEASE"
STALE_DAYS = 90


def _parse_release() -> dict[str, str]:
    if not RELEASE_FILE.is_file():
        return {}
    result: dict[str, str] = {}
    for line in RELEASE_FILE.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip()
    return result


def find_stale_articles(now: datetime | None = None) -> list[tuple[str, str]]:
    """Return (slug, reason) for PUBLISHED articles needing re-verification."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=STALE_DAYS)
    release = _parse_release()
    released_at = release.get("RELEASED_AT", "")
    stale: list[tuple[str, str]] = []
    if not articles_root().exists():
        return stale
    for art_dir in sorted(articles_root().iterdir()):
        if not art_dir.is_dir():
            continue
        slug = art_dir.name
        if current_phase(slug) != "PUBLISHED":
            continue
        fields = read_state(slug)
        verified = fields.get("VERIFIED_AS_OF", "")
        if not verified:
            stale.append((slug, "missing VERIFIED_AS_OF"))
            continue
        try:
            vdt = datetime.fromisoformat(verified.replace("Z", "+00:00"))
        except ValueError:
            stale.append((slug, "invalid VERIFIED_AS_OF"))
            continue
        if vdt < cutoff:
            stale.append((slug, f"verified {STALE_DAYS}+ days ago"))
            continue
        if released_at:
            try:
                rdt = datetime.fromisoformat(released_at.replace("Z", "+00:00"))
                if vdt < rdt:
                    stale.append((slug, f"product release {released_at} newer than verification"))
            except ValueError:
                pass
    return stale


def queue_reverification(slug: str, reason: str) -> None:
    """Transition a published article back to TESTING for re-verification."""
    transition(slug, "TESTING", extra={
        "REWORK_REASON": reason,
        "NEXT_ACTION": "re-verification: run tester",
    })
