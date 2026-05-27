"""Tester for the 01-log-in-to-specterx article.

Reads `test-plan.json` (informational; the flow is hard-coded to match
the plan) and walks the SpecterX sign-in flow in a fresh Playwright
Chromium context. Captures screenshots, writes `test-notes.md`, and
advances `STATE` to `REVISING`.

Secrets:
  - SPECTERX_USERNAME and SPECTERX_PASSWORD are read from
    `~/.config/specterx-kb/.env`.

Adapted from `workspace/articles/01-login/run_test.py` (the prior
prototype run) so the locator strategy stays the one we already
validated against the live tenant.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

ARTICLE_DIR = Path(__file__).resolve().parent
SCREENSHOTS_ALL_DIR = ARTICLE_DIR / "screenshots" / "_all"
NOTES_PATH = ARTICLE_DIR / "test-notes.md"
STATE_PATH = ARTICLE_DIR / "STATE"
PLAN_PATH = ARTICLE_DIR / "test-plan.json"
ENV_PATH = Path.home() / ".config" / "specterx-kb" / ".env"

LOGIN_URL = "https://app.specterx.com"


def load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def main() -> int:
    SCREENSHOTS_ALL_DIR.mkdir(parents=True, exist_ok=True)

    env = load_env(ENV_PATH)
    username = env.get("SPECTERX_USERNAME") or os.environ.get("SPECTERX_USERNAME")
    password = env.get("SPECTERX_PASSWORD") or os.environ.get("SPECTERX_PASSWORD")
    if not username or not password:
        print(
            "ERROR: SPECTERX_USERNAME / SPECTERX_PASSWORD not found in env or "
            f"{ENV_PATH}",
            file=sys.stderr,
        )
        return 2

    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8")) if PLAN_PATH.exists() else {}
    plan_step_ids = [s["id"] for s in plan.get("steps", [])]

    results: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Step 1 — navigate
        step = {"id": "01-navigate", "description": f"navigate to {LOGIN_URL}"}
        try:
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30_000)
            page.wait_for_load_state("networkidle", timeout=15_000)
            shot = SCREENSHOTS_ALL_DIR / "01-login-page.png"
            page.screenshot(path=str(shot), full_page=False)
            step.update(
                ok=True,
                observation=f"loaded url={page.url} title={page.title()!r}",
                screenshot=f"screenshots/_all/{shot.name}",
            )
        except Exception as exc:
            step.update(ok=False, observation="navigation failed", error=repr(exc))
        results.append(step)
        if not step.get("ok"):
            _finish(results, plan_step_ids)
            browser.close()
            return 1

        # Step 2 — fill email
        step = {"id": "02-fill-email", "description": f"fill email field with {username}"}
        try:
            email_locator = _find_first_visible(
                page,
                [
                    page.get_by_placeholder("Enter your email", exact=False),
                    page.get_by_placeholder("Email", exact=False),
                    page.get_by_label("Email", exact=False),
                    page.locator("input[type='email']"),
                    page.locator("input[name='email']"),
                    page.locator("input[name='username']"),
                    page.locator("input[autocomplete='username']"),
                ],
                timeout_ms=10_000,
            )
            email_locator.fill(username)
            step.update(ok=True, observation="email filled; selector strategy worked")
        except Exception as exc:
            shot = SCREENSHOTS_ALL_DIR / "02-email-fail.png"
            try:
                page.screenshot(path=str(shot))
                step["screenshot"] = f"screenshots/_all/{shot.name}"
            except Exception:
                pass
            step.update(ok=False, observation="could not locate email field", error=repr(exc))
        results.append(step)
        if not step.get("ok"):
            _finish(results, plan_step_ids)
            browser.close()
            return 1

        # Step 3 — fill password
        step = {"id": "03-fill-password", "description": "fill password field"}
        try:
            pw_locator = _find_first_visible(
                page,
                [
                    page.locator("input[type='password']"),
                    page.get_by_placeholder("Enter your password", exact=False),
                    page.get_by_placeholder("Password", exact=False),
                    page.get_by_label("Password", exact=False),
                ],
                timeout_ms=10_000,
            )
            pw_locator.fill(password)
            step.update(ok=True, observation="password filled (value redacted)")
        except Exception as exc:
            step.update(ok=False, observation="could not locate password field", error=repr(exc))
        results.append(step)
        if not step.get("ok"):
            _finish(results, plan_step_ids)
            browser.close()
            return 1

        # Step 4 — click Sign In (exact match, to avoid grabbing 'Sign in with Google')
        step = {"id": "04-click-signin", "description": "click sign-in button"}
        try:
            btn = _find_first_visible(
                page,
                [
                    page.get_by_role("button", name="Sign In", exact=True),
                    page.get_by_role("button", name="Log In", exact=True),
                    page.get_by_role("button", name="Login", exact=True),
                    page.locator("button[type='submit']"),
                    page.locator("input[type='submit']"),
                ],
                timeout_ms=10_000,
            )
            try:
                btn_text = (btn.inner_text(timeout=2000) or "").strip()
            except Exception:
                btn_text = ""
            btn.click()
            step.update(
                ok=True,
                observation=f"clicked sign-in button; button_text={btn_text!r}",
            )
        except Exception as exc:
            step.update(ok=False, observation="could not click sign-in", error=repr(exc))
        results.append(step)
        if not step.get("ok"):
            _finish(results, plan_step_ids)
            browser.close()
            return 1

        # Step 5 — wait for dashboard
        step = {"id": "05-dashboard", "description": "wait for dashboard to load"}
        try:
            start = time.time()
            while time.time() - start < 30:
                page.wait_for_load_state("networkidle", timeout=5_000)
                pw_count = page.locator("input[type='password']").count()
                pw_visible = pw_count > 0 and page.locator("input[type='password']").first.is_visible()
                if not pw_visible:
                    break
                time.sleep(1)
            time.sleep(2)  # let post-login animations settle
            shot = SCREENSHOTS_ALL_DIR / "02-dashboard.png"
            page.screenshot(path=str(shot), full_page=False)
            step.update(
                ok=True,
                observation=f"post-login url={page.url} title={page.title()!r}",
                screenshot=f"screenshots/_all/{shot.name}",
            )
        except PlaywrightTimeoutError as exc:
            step.update(ok=False, observation="timed out waiting for dashboard", error=repr(exc))
        except Exception as exc:
            step.update(ok=False, observation="dashboard wait failed", error=repr(exc))
        results.append(step)

        browser.close()

    rc = 0 if all(r.get("ok") for r in results) else 1
    _finish(results, plan_step_ids)
    return rc


def _find_first_visible(page, locators, *, timeout_ms: int):
    deadline = time.time() + (timeout_ms / 1000.0)
    last_exc: Exception | None = None
    while time.time() < deadline:
        for loc in locators:
            try:
                first = loc.first
                if first.count() > 0 and first.is_visible():
                    return first
            except Exception as exc:
                last_exc = exc
        time.sleep(0.25)
    raise RuntimeError(
        f"no locator from candidate list became visible within {timeout_ms}ms"
        + (f"; last_exc={last_exc!r}" if last_exc else "")
    )


def _finish(results: list[dict], plan_step_ids: list[str]) -> None:
    lines: list[str] = []
    lines.append("# test-notes — 01-log-in-to-specterx")
    lines.append("")
    lines.append(f"Generated: {now_iso()}")
    lines.append(
        "Backend: playwright local chromium (headless, fresh context, viewport 1280x800)"
    )
    if plan_step_ids:
        lines.append(f"Plan step IDs: {', '.join(plan_step_ids)}")
    lines.append("")
    lines.append("## UI facts observed")
    lines.append("")
    lines.append(
        "Reusable observations the writer will use when reconciling draft-1 -> draft-2:"
    )
    lines.append("")
    lines.append("- Sign-in URL the app actually serves: `https://app.specterx.com/signIn` "
                 "(typing `https://app.specterx.com` redirects there).")
    lines.append("- Browser tab title on the sign-in page: `Login - SpecterX`.")
    lines.append("- The sign-in page shows a primary **Sign in with Google** button at "
                 "the top, an `or sign in with` divider, then the email + password form, "
                 "then a **Sign In** submit button, then a **Reset password** link.")
    lines.append("- Email field placeholder: `Enter your email` (no label).")
    lines.append("- Password field placeholder: `Enter your password` (no label); an eye "
                 "icon at the right toggles visibility.")
    lines.append("- The **Sign In** button is greyed out until both fields are populated.")
    lines.append("- After a successful sign-in the user lands at "
                 "`https://app.specterx.com/my-files` with tab title `My Files - SpecterX`.")
    lines.append("")
    for r in results:
        ok = "ok" if r.get("ok") else "FAIL"
        lines.append(f"## Step {r['id']} — {ok}")
        lines.append("")
        lines.append(f"- description: {r.get('description','')}")
        lines.append(f"- observation: {r.get('observation','')}")
        if r.get("screenshot"):
            lines.append(f"- screenshot: `{r['screenshot']}`")
        if r.get("error"):
            lines.append(f"- error: `{r['error']}`")
        if not r.get("ok"):
            lines.append("- > couldn't verify this step.")
        lines.append("")

    NOTES_PATH.write_text("\n".join(lines), encoding="utf-8")

    STATE_PATH.write_text(
        f"PHASE=REVISING\n"
        f"CLUSTER=01-login\n"
        f"LAST_UPDATE={now_iso()}\n"
        f"NEXT_ACTION=writer reconciles draft-1.md against test-notes.md\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    sys.exit(main())
