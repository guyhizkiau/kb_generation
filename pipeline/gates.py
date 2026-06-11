"""Deterministic pipeline gates."""
from __future__ import annotations

import re
from pathlib import Path

from store.paths import article_dir

# ── research gate contract ────────────────────────────────────────────────────

RESEARCH_SECTION_HEADING = "## Articles read"
RESEARCH_MIN_ENTRIES = 3

RESEARCH_CONTRACT = f"""\
competitor-coverage.md must contain a section whose heading starts with:

    ## Articles read

The heading is case-insensitive and may have additional words after it
(e.g. "## Articles read end to end" is accepted).

Immediately below that heading, list at least {RESEARCH_MIN_ENTRIES} sources using
bullet lines OR markdown table rows:

  Bullet format (preferred):
    - Vendor — "Article title" (source, date, ~N words)

  Table row format (also accepted):
    | Vendor | "Title" | ... |   ← data rows only; separator rows don't count

Do NOT put sources in a prose paragraph, a nested subsection, or under a
different heading. The gate stops counting at the next ## heading.

Minimum: {RESEARCH_MIN_ENTRIES} bullets or non-separator table rows.

Passing example:
  ## Articles read
  - Egnyte — "Folder Permissions" (cached 2026-06-01, ~1 200 words)
  - Virtru — "Secure Share" (cached 2026-06-01, ~800 words)
  - Dropbox — "Share with anyone" (cached 2026-06-01, ~950 words)
"""

_TABLE_SEPARATOR_RE = re.compile(r"^\|[\s\-|:]+\|$")


def check_research_gate(slug: str) -> tuple[bool, str]:
    """Verify competitor-coverage.md has ≥3 source entries under ## Articles read."""
    path = article_dir(slug) / "research" / "competitor-coverage.md"
    if not path.is_file():
        return False, "missing research/competitor-coverage.md"

    text = path.read_text(encoding="utf-8")

    # Accept heading with optional suffix, e.g. "## Articles read end to end"
    section_match = re.search(
        r"^## Articles read\b", text, re.MULTILINE | re.IGNORECASE,
    )
    if not section_match:
        return (
            False,
            f"missing '{RESEARCH_SECTION_HEADING}' section.\n{RESEARCH_CONTRACT}",
        )

    rest = text[section_match.end():]
    next_heading = re.search(r"^## ", rest, re.MULTILINE)
    section_body = rest[: next_heading.start()] if next_heading else rest

    count = 0
    for line in section_body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            count += 1
        elif (
            stripped.startswith("|")
            and stripped.endswith("|")
            and not _TABLE_SEPARATOR_RE.match(stripped)
        ):
            count += 1

    if count < RESEARCH_MIN_ENTRIES:
        return (
            False,
            (
                f"only {count} source entr{'y' if count == 1 else 'ies'} listed under "
                f"'{RESEARCH_SECTION_HEADING}' (need ≥{RESEARCH_MIN_ENTRIES}).\n"
                f"{RESEARCH_CONTRACT}"
            ),
        )
    return True, f"{count} articles read"
