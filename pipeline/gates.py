"""Deterministic pipeline gates."""
from __future__ import annotations

import json
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


# ── test-plan gate contract ───────────────────────────────────────────────────

VALID_ACTION_TYPES = frozenset({
    "goto", "click", "fill", "type", "select", "file_upload", "clear",
    "hover", "navigate", "press", "wait_for", "download",
})

TEST_PLAN_CONTRACT = """\
test-plan.json must be valid JSON with a "steps" array. Each step needs:
  - "id" (string)
  - "backend" ("browser" or "desktop")
  - "action" with "type" in the allowed set
  - a locator (role+name, placeholder, label, selector, or selector_hint)
    for actions that target elements

Rules:
  - Login block: at least one step with id starting "00-"; use value_ref users.data_owner.specterx_password for password fill
  - selector_hint must be a short quoted label (e.g. "'Share files'"), not prose
  - If steps create state (upload/share/create), include cleanup steps (id "C*")
"""

_SELECTOR_HINT_PROSE_RE = re.compile(r"^[^{'\"].{40,}")


def check_test_plan_gate(slug: str) -> tuple[bool, str]:
    """Verify test-plan.json structure before the tester runs."""
    path = article_dir(slug) / "test-plan.json"
    if not path.is_file():
        return False, "missing test-plan.json"

    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON in test-plan.json: {exc}\n{TEST_PLAN_CONTRACT}"

    steps = plan.get("steps")
    if not isinstance(steps, list) or not steps:
        return False, f"missing or empty steps array.\n{TEST_PLAN_CONTRACT}"

    has_login = False
    has_state_creating = False
    has_cleanup = False
    locatorless_types = frozenset({"goto", "press"})

    for i, step in enumerate(steps):
        sid = step.get("id")
        if not sid:
            return False, f"step[{i}] missing id.\n{TEST_PLAN_CONTRACT}"
        if str(sid).startswith("00-"):
            has_login = True
        if str(sid).startswith("C"):
            has_cleanup = True
        if step.get("backend") not in ("browser", "desktop"):
            return False, f"step {sid}: invalid backend.\n{TEST_PLAN_CONTRACT}"

        action = step.get("action") or {}
        atype = action.get("type")
        if atype not in VALID_ACTION_TYPES:
            return False, f"step {sid}: invalid action type {atype!r}.\n{TEST_PLAN_CONTRACT}"

        if atype == "goto":
            if not action.get("url"):
                return False, f"step {sid}: goto missing url.\n{TEST_PLAN_CONTRACT}"
        elif atype not in locatorless_types:
            has_locator = any(
                action.get(k)
                for k in ("role", "name", "placeholder", "label", "selector", "selector_hint")
            ) or (atype == "file_upload" and (
                action.get("selector") or action.get("folder") or action.get("filename")
            ))
            if not has_locator:
                return False, f"step {sid}: action missing locator.\n{TEST_PLAN_CONTRACT}"

        hint = action.get("selector_hint", "")
        if hint and _SELECTOR_HINT_PROSE_RE.match(str(hint).strip()):
            return False, (
                f"step {sid}: selector_hint looks like prose, not a quoted label: {hint!r}.\n"
                f"{TEST_PLAN_CONTRACT}"
            )

        desc = (step.get("description") or "").lower()
        if any(kw in desc for kw in ("upload", "create", "share", "folder")):
            if not str(sid).startswith("C") and not str(sid).startswith("00-"):
                has_state_creating = True

    if not has_login:
        return False, f"missing login steps (00-*).\n{TEST_PLAN_CONTRACT}"

    if has_state_creating and not has_cleanup:
        return False, f"steps create state but no cleanup steps (C*).\n{TEST_PLAN_CONTRACT}"

    return True, f"{len(steps)} steps validated"


# ── final / draft markdown gate contract ─────────────────────────────────────

FINAL_CONTRACT = """\
final.md must be ready for publish and preview:

  - No screenshot placeholders (lines starting with "> Screenshot")
  - Every markdown image reference ![alt](path) must point to an existing file
    relative to the article directory

Replace placeholders with real embeds during revise-from-test, e.g.:
  ![The Share button](screenshots/04-share-files-button.png)
"""

_SCREENSHOT_PLACEHOLDER_RE = re.compile(r"^>\s*Screenshot\b", re.MULTILINE | re.IGNORECASE)
_MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def _check_markdown_images(article_path: Path, rel_path: str) -> tuple[bool, str]:
    """Shared gate for draft-2.md and final.md."""
    path = article_path / rel_path
    if not path.is_file():
        return False, f"missing {rel_path}"

    text = path.read_text(encoding="utf-8")

    if _SCREENSHOT_PLACEHOLDER_RE.search(text):
        placeholders = len(_SCREENSHOT_PLACEHOLDER_RE.findall(text))
        return (
            False,
            (
                f"{rel_path} still contains {placeholders} screenshot placeholder"
                f"{'s' if placeholders != 1 else ''} (> Screenshot …).\n"
                f"{FINAL_CONTRACT}"
            ),
        )

    missing: list[str] = []
    for match in _MD_IMAGE_RE.finditer(text):
        src = match.group(1).strip()
        if src.startswith(("http://", "https://", "data:")):
            continue
        image_path = (article_path / src).resolve()
        if not image_path.is_file():
            missing.append(src)

    if missing:
        shown = ", ".join(missing[:5])
        extra = f" (+{len(missing) - 5} more)" if len(missing) > 5 else ""
        return (
            False,
            (
                f"{rel_path} references missing image file(s): {shown}{extra}.\n"
                f"{FINAL_CONTRACT}"
            ),
        )

    image_count = len(_MD_IMAGE_RE.findall(text))
    return True, f"{rel_path} validated ({image_count} image embeds)"


def check_draft2_gate(slug: str) -> tuple[bool, str]:
    """Verify draft-2.md has real screenshot embeds before voice-pass."""
    return _check_markdown_images(article_dir(slug), "draft-2.md")


def check_final_gate(slug: str) -> tuple[bool, str]:
    """Verify final.md has no placeholders and all images exist."""
    return _check_markdown_images(article_dir(slug), "final.md")
