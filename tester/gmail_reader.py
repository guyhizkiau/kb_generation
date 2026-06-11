"""Read SpecterX verification codes from Gmail via Playwright."""

from __future__ import annotations

import contextlib
import logging
import re
import time

from playwright.sync_api import BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

log = logging.getLogger("tester.gmail")

DEFAULT_TIMEOUT_S = 180
POLL_INTERVAL_S = 5
CODE_REGEX = re.compile(
    r"(?:verification code is|code is|Your verification code)[^\d]{0,40}(\d{6})",
    re.IGNORECASE,
)
FALLBACK_CODE_REGEX = re.compile(r"\b(\d{6})\b")


class GmailAccessError(Exception):
    """Gmail login or inbox read failed."""


class GmailChallengeError(GmailAccessError):
    """Google blocked or challenged automated login."""


def _page_text(page: Page) -> str:
    try:
        return page.inner_text("body")
    except Exception:
        return ""


def _looks_like_google_challenge(page: Page) -> bool:
    url = page.url.lower()
    text = _page_text(page).lower()
    if "challenge" in url or "signin/rejected" in url:
        return True
    markers = (
        "couldn't sign you in",
        "unusual activity",
        "verify it's you",
        "confirm you're not a robot",
        "account has been disabled",
    )
    return any(m in text for m in markers)


def _sign_in_to_gmail(page: Page, email: str, email_password: str, *, timeout_ms: int) -> None:
    page.goto("https://accounts.google.com/signin/v2/identifier?service=mail", timeout=timeout_ms)
    page.wait_for_load_state("domcontentloaded")

    if _looks_like_google_challenge(page):
        raise GmailChallengeError(
            "Google sign-in was blocked or challenged — log into Gmail manually once "
            "in the VM browser profile, or fill the SpecterX password in Settings."
        )

    if "mail.google.com" in page.url and "inbox" in page.url.lower():
        return

    email_input = page.locator('input[type="email"]').first
    try:
        email_input.wait_for(state="visible", timeout=timeout_ms)
        email_input.fill(email, timeout=timeout_ms)
        page.locator("#identifierNext button, button:has-text('Next')").first.click(timeout=timeout_ms)
    except PlaywrightTimeoutError as exc:
        if "mail.google.com" in page.url:
            return
        raise GmailAccessError(f"Gmail email step failed: {exc}") from exc

    page.wait_for_timeout(1500)
    if _looks_like_google_challenge(page):
        raise GmailChallengeError(
            "Google challenged the mailbox login after entering email."
        )

    password_input = page.locator('input[type="password"]').first
    try:
        password_input.wait_for(state="visible", timeout=timeout_ms)
        password_input.fill(email_password, timeout=timeout_ms)
        page.locator("#passwordNext button, button:has-text('Next')").first.click(timeout=timeout_ms)
    except PlaywrightTimeoutError as exc:
        raise GmailAccessError(f"Gmail password step failed: {exc}") from exc

    try:
        page.wait_for_url(re.compile(r"mail\.google\.com"), timeout=timeout_ms)
    except PlaywrightTimeoutError:
        if _looks_like_google_challenge(page):
            raise GmailChallengeError(
                "Google did not reach Gmail inbox — likely a bot challenge. "
                "Log into Gmail manually once or fill the SpecterX password in Settings."
            )
        raise GmailAccessError("Gmail sign-in did not reach the inbox.")


def _extract_code_from_text(text: str, *, sender_contains: str | None) -> str | None:
    if sender_contains and sender_contains.lower() not in text.lower():
        return None
    match = CODE_REGEX.search(text)
    if match:
        return match.group(1)
    match = FALLBACK_CODE_REGEX.search(text)
    if match:
        return match.group(1)
    return None


def _scan_mailbox_page(page: Page, *, sender_contains: str | None) -> str | None:
    rows = page.locator("tr.zA, div.Cp tbody tr, div[role='main'] tr")
    count = min(rows.count(), 20)
    for i in range(count):
        row = rows.nth(i)
        try:
            text = row.inner_text(timeout=2000)
        except Exception:
            continue
        code = _extract_code_from_text(text, sender_contains=sender_contains)
        if code:
            return code
    body = _page_text(page)
    return _extract_code_from_text(body, sender_contains=sender_contains)


def read_verification_code(
    context: BrowserContext,
    email: str,
    email_password: str,
    *,
    sender_contains: str | None = "verification",
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> str:
    """Sign into Gmail and poll inbox/spam for a 6-digit verification code."""
    deadline = time.monotonic() + timeout_s
    timeout_ms = min(int(timeout_s * 1000), 60_000)
    page = context.new_page()
    try:
        _sign_in_to_gmail(page, email, email_password, timeout_ms=timeout_ms)
        while time.monotonic() < deadline:
            for fragment in ("#inbox", "#spam"):
                page.goto(f"https://mail.google.com/mail/u/0/{fragment}", timeout=timeout_ms)
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(2000)
                code = _scan_mailbox_page(page, sender_contains=sender_contains)
                if code:
                    log.info("verification code found in Gmail (%s)", fragment)
                    return code
            page.wait_for_timeout(int(POLL_INTERVAL_S * 1000))
        raise GmailAccessError(
            f"No verification email with a 6-digit code arrived within {int(timeout_s)}s."
        )
    finally:
        with contextlib.suppress(Exception):
            page.close()
