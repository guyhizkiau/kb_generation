"""Validated article state machine — single choke point for PHASE transitions."""
from __future__ import annotations

from store.paths import article_dir, articles_root
from store.state import read_state, write_state

PHASES = frozenset({
    "QUEUED", "RESEARCHING", "DRAFTING", "TESTING", "REVISING", "FINALIZING",
    "IN_REVIEW", "APPROVED", "PUBLISHED", "BLOCKED", "SKIPPED",
})

LEGACY_MAP: dict[str, str] = {
    "PLANNED": "QUEUED",
    "PR_OPEN": "IN_REVIEW",
    "PR_REVISION_NEEDED": "REVISING",
    "MERGED": "PUBLISHED",
    "DONE": "PUBLISHED",
}

TRANSITIONS: dict[str, frozenset[str]] = {
    "QUEUED": frozenset({"RESEARCHING", "SKIPPED"}),
    "RESEARCHING": frozenset({"DRAFTING"}),
    "DRAFTING": frozenset({"TESTING"}),
    "TESTING": frozenset({"REVISING"}),
    "REVISING": frozenset({"FINALIZING"}),
    "FINALIZING": frozenset({"IN_REVIEW"}),
    "IN_REVIEW": frozenset({"APPROVED", "REVISING"}),
    "APPROVED": frozenset({"PUBLISHED"}),
    "PUBLISHED": frozenset({"REVISING", "TESTING"}),
    "BLOCKED": frozenset(),  # handled specially via RESUME_PHASE
    "SKIPPED": frozenset({"RESEARCHING"}),
}

ACTIVE_PHASES = frozenset({
    "RESEARCHING", "DRAFTING", "TESTING", "REVISING", "FINALIZING",
    "IN_REVIEW", "APPROVED", "BLOCKED",
})

PHASE_ARTIFACTS: dict[str, str] = {
    "RESEARCHING": "research/competitor-coverage.md",
    "DRAFTING": "draft-1.md",
    "TESTING": "test-notes.md",
    "REVISING": "draft-2.md",
    "FINALIZING": "final.md",
}


class InvalidTransition(Exception):
    """Raised when a PHASE transition is not allowed."""

    def __init__(self, slug: str, from_phase: str, to_phase: str):
        self.slug = slug
        self.from_phase = from_phase
        self.to_phase = to_phase
        super().__init__(f"{slug}: {from_phase} → {to_phase} not allowed")


def current_phase(slug: str) -> str:
    """Return the current phase for *slug*, mapping legacy values."""
    fields = read_state(slug)
    raw = fields.get("PHASE", "UNKNOWN")
    return LEGACY_MAP.get(raw, raw)


def normalize_legacy(slug: str) -> str:
    """Rewrite a legacy PHASE value to its new-set equivalent.

    Administrative rename, not a lifecycle move — bypasses TRANSITIONS on
    purpose (PUBLISHED → PUBLISHED is not a transition). No-op for
    new-set values.
    """
    raw = read_state(slug).get("PHASE", "")
    mapped = LEGACY_MAP.get(raw)
    if mapped is None:
        return raw
    write_state(slug, {"PHASE": mapped})
    return mapped


def transition(slug: str, to_phase: str, *, extra: dict[str, str] | None = None) -> dict[str, str]:
    """Validate and apply a PHASE transition; return resulting STATE fields."""
    fields = read_state(slug)
    cur = LEGACY_MAP.get(fields.get("PHASE", ""), fields.get("PHASE", "UNKNOWN"))
    extra = dict(extra or {})

    if to_phase == "BLOCKED":
        if cur in {"PUBLISHED", "SKIPPED"}:
            raise InvalidTransition(slug, cur, to_phase)
        extra["RESUME_PHASE"] = cur
    elif cur == "BLOCKED":
        resume = fields.get("RESUME_PHASE", "")
        if to_phase != resume:
            raise InvalidTransition(slug, cur, to_phase)
        extra["RESUME_PHASE"] = ""
        extra["BLOCKED_REASON"] = ""
    else:
        allowed = TRANSITIONS.get(cur, frozenset())
        if to_phase not in allowed:
            raise InvalidTransition(slug, cur, to_phase)

    updates = {"PHASE": to_phase, **extra}
    return write_state(slug, updates)


def block(slug: str, reason: str) -> dict[str, str]:
    """Block an article, recording RESUME_PHASE and BLOCKED_REASON."""
    return transition(slug, "BLOCKED", extra={"BLOCKED_REASON": reason})


def unblock(slug: str) -> dict[str, str]:
    """Return a blocked article to its RESUME_PHASE."""
    fields = read_state(slug)
    resume = fields.get("RESUME_PHASE", "")
    if not resume:
        raise InvalidTransition(slug, "BLOCKED", "?")
    return transition(slug, resume)


def active_article() -> str | None:
    """Return the slug of the article currently in-flight, or None."""
    root = articles_root()
    if not root.exists():
        return None
    for art_dir in sorted(root.iterdir()):
        if not art_dir.is_dir():
            continue
        state_file = art_dir / "STATE"
        if not state_file.exists():
            continue
        slug = art_dir.name
        if current_phase(slug) in ACTIVE_PHASES:
            return slug
    return None


def artifact_exists(slug: str, relpath: str) -> bool:
    """Return True when the phase artifact exists in the article directory."""
    return (article_dir(slug) / relpath).is_file()


def resume(slug: str) -> str | None:
    """Return the phase to relaunch after a crash, or None if idle/complete."""
    cur = current_phase(slug)
    if cur not in PHASE_ARTIFACTS:
        return None
    artifact = PHASE_ARTIFACTS[cur]
    if artifact_exists(slug, artifact):
        return None
    return cur
