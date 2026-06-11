"""Bootstrap SpecterX passwords via the reset-password flow."""

from __future__ import annotations

import logging
import re
import secrets
import string
import time
from typing import Any

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from store.test_config import (
    email_password_set,
    resolve,
    set_specterx_password,
    specterx_password_set,
)
from tester.browser_runner import BrowserRunner
from tester.gmail_reader import GmailAccessError, GmailChallengeError, read_verification_code

log = logging.getLogger("tester.password_bootstrap")

SPECTERX_APP = "https://app.specterx.com"
SPECIALS = "!@#$%^&*()_~-"


class BootstrapError(Exception):
    """SpecterX password bootstrap failed."""


def generate_specterx_password() -> str:
    """Return a random password that satisfies SpecterX Cognito rules."""
    lower = secrets.choice(string.ascii_lowercase)
    upper = secrets.choice(string.ascii_uppercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice(SPECIALS)
    rest = "".join(
        secrets.choice(string.ascii_letters + string.digits + SPECIALS)
        for _ in range(12)
    )
    chars = list(lower + upper + digit + special + rest)
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def _require_role_credentials(role: str, config: dict[str, Any]) -> tuple[str, str]:
    email = resolve(f"users.{role}.email", config)
    if not email:
        raise BootstrapError(
            f"users.{role}.email is not configured — set it in Ghostwriter Settings."
        )
    if not email_password_set(role, config):
        raise BootstrapError(
            f"users.{role}.email_password is not configured — set the mailbox password "
            f"in Ghostwriter Settings so the tester can read verification emails."
        )
    email_password = resolve(f"users.{role}.email_password", config)
    assert email_password is not None
    return email, email_password


def ensure_specterx_password(
    role: str,
    config: dict[str, Any],
    runner: BrowserRunner,
) -> str:
    """Ensure *role* has a SpecterX password; bootstrap via reset flow if missing."""
    if specterx_password_set(role, config):
        existing = resolve(f"users.{role}.specterx_password", config)
        assert existing is not None
        return existing

    email, email_password = _require_role_credentials(role, config)
    new_password = generate_specterx_password()
    page = runner.page
    timeout_ms = 30_000

    log.info("bootstrapping SpecterX password for role %s", role)
    page.goto(f"{SPECTERX_APP}/forgotPassword", timeout=timeout_ms, wait_until="domcontentloaded")

    page.get_by_placeholder("Enter your email").fill(email, timeout=timeout_ms)
    reset_sent_at = time.time()
    page.get_by_role("button", name="Reset").click(timeout=timeout_ms)

    try:
        page.get_by_text("Create New Password", exact=False).wait_for(
            state="visible",
            timeout=timeout_ms,
        )
    except PlaywrightTimeoutError as exc:
        raise BootstrapError(
            f"SpecterX reset flow for {role!r} did not reach Create New Password — "
            "confirm the account exists in the tenant."
        ) from exc

    try:
        code = read_verification_code(
            runner.context,
            email,
            email_password,
            sender_contains="verification",
            timeout_s=180,
        )
    except GmailChallengeError as exc:
        raise BootstrapError(
            f"Gmail access blocked while bootstrapping users.{role}.specterx_password: {exc}"
        ) from exc
    except GmailAccessError as exc:
        raise BootstrapError(
            f"Could not read verification email for users.{role}: {exc}"
        ) from exc

    log.info("reset code received for role %s (requested %.0fs ago)", role, time.time() - reset_sent_at)

    page.get_by_placeholder("Enter the code").fill(code, timeout=timeout_ms)
    password_field = page.get_by_placeholder("Create your password")
    password_field.fill(new_password, timeout=timeout_ms)
    page.get_by_role("button", name="Change Password").click(timeout=timeout_ms)

    try:
        page.wait_for_url(re.compile(r"/signIn"), timeout=timeout_ms)
    except PlaywrightTimeoutError:
        try:
            page.get_by_text("successfully changed", exact=False).wait_for(
                state="visible",
                timeout=10_000,
            )
        except PlaywrightTimeoutError as exc:
            raise BootstrapError(
                f"SpecterX password change for {role!r} did not confirm success."
            ) from exc

    updated = set_specterx_password(role, new_password, config)
    runner._test_config = updated
    log.info("persisted SpecterX password for role %s", role)
    return new_password


def bootstrap_roles(
    roles: list[str],
    config: dict[str, Any],
    runner: BrowserRunner,
) -> dict[str, Any]:
    """Bootstrap every role that lacks a SpecterX password."""
    current = config
    for role in roles:
        ensure_specterx_password(role, current, runner)
        current = runner._test_config
    return current
