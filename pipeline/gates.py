"""Deterministic pipeline gates."""
from __future__ import annotations

import re
from pathlib import Path

from store.paths import article_dir


def check_research_gate(slug: str) -> tuple[bool, str]:
    """Verify competitor-coverage.md lists ≥3 articles read."""
    path = article_dir(slug) / "research" / "competitor-coverage.md"
    if not path.is_file():
        return False, "missing research/competitor-coverage.md"

    text = path.read_text(encoding="utf-8")
    section_match = re.search(
        r"^## Articles read\s*$", text, re.MULTILINE | re.IGNORECASE,
    )
    if not section_match:
        return False, "missing ## Articles read section"

    rest = text[section_match.end():]
    next_heading = re.search(r"^## ", rest, re.MULTILINE)
    section_body = rest[: next_heading.start()] if next_heading else rest

    bullets = [
        line for line in section_body.splitlines()
        if line.strip().startswith("- ") or line.strip().startswith("* ")
    ]
    count = len(bullets)
    if count < 3:
        return False, f"only {count} competitor articles read (need ≥3)"
    return True, f"{count} articles read"
