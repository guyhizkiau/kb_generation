"""AI vision review for tester screenshots.

After each capture, the tester can send the PNG to Claude with a quality
rubric (loaders, mid-animation, obscured focus). Review failures are
warnings only — they never flip step pass/fail.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

log = logging.getLogger("tester.screenshot_review")

DEFAULT_MODEL = "claude-3-5-haiku-20241022"
SECRETS_ENV_PATH = Path.home() / ".config" / "specterx-kb" / ".env"
SENSITIVE_TERMS_PATH = Path(__file__).resolve().parent / "sensitive-terms.txt"

RUBRIC = """You are reviewing a UI screenshot taken for a knowledge-base article.

Step description: {description}
Expected focus: {focus}

Reject the screenshot (ok=false) if ANY of these apply:
- Mid-animation or mid-transition (half-open dialog, sliding panel, fading overlay)
- Visible loader, spinner, skeleton screen, or blank/partially rendered content
- Tooltip, dropdown, toast, or unrelated dialog obscuring the stated focus
- The stated focus is not clearly visible in the frame
- Promotional/onboarding popups, spam banners, or unrelated browser chrome covering the focus
- Any of these sensitive values are clearly visible in the frame: {sensitive_terms}

Accept (ok=true) only when the frame is stable and the focus is clearly visible.

Reply with JSON only, no markdown:
{{"ok": true|false, "reason": "one short sentence"}}"""


@dataclass(frozen=True)
class ReviewResult:
    ok: bool
    reason: str
    skipped: bool = False

    def observation_suffix(self, *, attempts: int = 1) -> str:
        if self.skipped:
            return "screenshot-review=skipped"
        if self.ok:
            return "screenshot-review=ok"
        attempt_note = f" after {attempts} attempts" if attempts > 1 else ""
        return f"screenshot-review=BAD: {self.reason}{attempt_note}"


# Injectable override for tests.
_review_impl: Callable[..., ReviewResult] | None = None


def is_review_enabled() -> bool:
    return os.environ.get("SCREENSHOT_REVIEW", "on").strip().lower() not in {
        "0",
        "off",
        "false",
        "no",
    }


def _load_sensitive_terms() -> list[str]:
    terms: list[str] = []
    if SENSITIVE_TERMS_PATH.is_file():
        for line in SENSITIVE_TERMS_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                terms.append(line)
    try:
        from store.test_config import sensitive_emails

        for email in sensitive_emails():
            if email not in terms:
                terms.append(email)
    except Exception:
        pass
    return terms


def _load_api_key() -> str | None:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    if not SECRETS_ENV_PATH.is_file():
        return None
    try:
        for line in SECRETS_ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == "ANTHROPIC_API_KEY":
                return value.strip().strip('"').strip("'") or None
    except OSError as exc:
        log.warning("could not read secrets file %s: %s", SECRETS_ENV_PATH, exc)
    return None


def _parse_review_json(text: str) -> ReviewResult | None:
    text = text.strip()
    if not text:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    if not isinstance(data, dict):
        return None
    ok = data.get("ok")
    reason = data.get("reason")
    if not isinstance(ok, bool) or not isinstance(reason, str):
        return None
    return ReviewResult(ok=ok, reason=reason.strip() or ("acceptable" if ok else "unspecified issue"))


def _call_vision_api(png_path: Path, *, focus: str, description: str) -> ReviewResult:
    api_key = _load_api_key()
    if not api_key:
        log.warning("screenshot review skipped: no ANTHROPIC_API_KEY")
        return ReviewResult(ok=True, reason="review unavailable (no API key)", skipped=True)

    try:
        import anthropic
    except ImportError:
        log.warning("screenshot review skipped: anthropic package not installed")
        return ReviewResult(ok=True, reason="review unavailable (no anthropic SDK)", skipped=True)

    model = os.environ.get("SCREENSHOT_REVIEW_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    image_b64 = base64.standard_b64encode(png_path.read_bytes()).decode("ascii")
    sensitive = _load_sensitive_terms()
    sensitive_label = ", ".join(sensitive) if sensitive else "(none configured)"
    prompt = RUBRIC.format(
        description=description or "(not provided)",
        focus=focus or "(general UI state)",
        sensitive_terms=sensitive_label,
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=256,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
    except Exception as exc:
        log.warning("screenshot review API error for %s: %s", png_path.name, exc)
        return ReviewResult(ok=True, reason=f"review unavailable ({exc.__class__.__name__})", skipped=True)

    text_blocks = [
        block.text
        for block in message.content
        if getattr(block, "type", None) == "text" and getattr(block, "text", None)
    ]
    parsed = _parse_review_json("\n".join(text_blocks))
    if parsed is None:
        log.warning("screenshot review unparseable reply for %s", png_path.name)
        return ReviewResult(ok=True, reason="review unavailable (unparseable reply)", skipped=True)
    return parsed


def review_screenshot(
    png_path: str | Path,
    *,
    focus: str = "",
    description: str = "",
) -> ReviewResult:
    """Review a captured PNG. Fails open on outage or when review is disabled."""
    if _review_impl is not None:
        return _review_impl(png_path, focus=focus, description=description)

    if not is_review_enabled():
        return ReviewResult(ok=True, reason="review disabled", skipped=True)

    path = Path(png_path)
    if not path.is_file():
        log.warning("screenshot review skipped: file missing %s", path)
        return ReviewResult(ok=True, reason="review unavailable (missing file)", skipped=True)

    return _call_vision_api(path, focus=focus, description=description)


def set_review_impl(impl: Callable[..., ReviewResult] | None) -> None:
    """Replace the review implementation (tests only)."""
    global _review_impl
    _review_impl = impl
