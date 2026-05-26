"""Decide which backend (browser vs desktop) should execute a step.

This is v1: a naive keyword scan over the step's description and any
action hints. The classifier defaults to `browser` when uncertain,
matching the rule in `docs/01-ARCHITECTURE.md` ("anything else →
browser") — because most SpecterX article steps are web flows, and the
desktop backend (Phase D) is expensive to invoke.

Note: `prompts/02-test-plan.md` tells the *writer* to default to
desktop when unsure, which is the right rail for the prompt that
generates plans (be cautious; flag ambiguous steps as desktop so a
human can adjust). This module is consumed by the *runner*, where the
practical default is the cheaper, more common backend.

This file has no Playwright or Anthropic dependencies — it is pure
string matching and can be unit-tested without any network.
"""

from __future__ import annotations

import re
from typing import Any, Literal

Backend = Literal["browser", "desktop"]

# Tokens that strongly imply the step needs the Windows desktop.
# Match as whole words so substrings inside a URL or sentence don't
# trigger false positives (e.g. "outlook.com" mentioned in an article
# about web shouldn't force desktop if the actual action is a click in
# the SpecterX web UI).
_DESKTOP_TOKENS = {
    "outlook",
    "word",
    "excel",
    "powerpoint",
    "acrobat",
    "explorer",     # File Explorer
    "taskbar",
    "tray",
    "desktop",
    "drag",         # drag-from-OS is a desktop interaction
    "drop",
    "right-click",  # context menu only really exists on desktop here
    "context",
    "shortcut",
    "pyautogui",
    "win+",
    "shortcuts",
}

# Tokens that strongly imply browser. These override desktop when both
# are present (e.g. "Drag from your Files page to the Share dialog" is
# browser even though it says drag).
_BROWSER_OVERRIDE_TOKENS = {
    "app.specterx.com",
    "web ui",
    "web app",
    "browser tab",
    "address bar",
    "url bar",
    "https://",
}

_WORD = re.compile(r"[A-Za-z0-9+\-.]+")


def _tokens(text: str) -> set[str]:
    return {w.lower() for w in _WORD.findall(text or "")}


def classify(step: dict[str, Any]) -> Backend:
    """Pick a backend for a single test-plan step.

    Honors an explicit `backend` field on the step (writer often sets
    this directly), and only falls back to keyword detection when the
    field is missing or empty.
    """
    explicit = (step.get("backend") or "").strip().lower()
    if explicit in ("browser", "desktop"):
        return explicit  # type: ignore[return-value]

    blob_parts: list[str] = [step.get("description", "")]
    action = step.get("action") or {}
    for key in ("type", "selector_hint", "from", "to_hint", "url", "value"):
        v = action.get(key)
        if isinstance(v, str):
            blob_parts.append(v)
    text = " ".join(blob_parts).lower()
    toks = _tokens(text)

    if any(ovr in text for ovr in _BROWSER_OVERRIDE_TOKENS):
        return "browser"
    if toks & _DESKTOP_TOKENS:
        return "desktop"
    return "browser"


def annotate(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return new list with `backend` filled in on every step."""
    out: list[dict[str, Any]] = []
    for s in steps:
        s2 = dict(s)
        s2["backend"] = classify(s)
        out.append(s2)
    return out


if __name__ == "__main__":
    import json
    import sys
    plan = json.load(sys.stdin)
    plan["steps"] = annotate(plan.get("steps", []))
    json.dump(plan, sys.stdout, indent=2)
