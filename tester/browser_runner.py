"""Browser-side test step executor.

Connects Playwright to a Chromium with `--remote-debugging-port=9222`.
Per the architecture doc, that Chromium runs on the Windows host of an
EC2 Windows VM and is reachable from WSL2 Ubuntu at the resolver's
nameserver IP. If no CDP endpoint is reachable, we fall back to
launching a local Chromium (headless by default) — useful for
smoke-testing the stack on a non-WSL2 Linux box.

This module is deliberately small: it exposes one class,
`BrowserRunner`, with a `run_step` method that takes a step descriptor
dict and returns a result dict. It's the browser leg of the wider
tester; the desktop leg is in `desktop_runner.py`.
"""

from __future__ import annotations

import contextlib
import dataclasses
import json
import logging
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any, Iterator

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

log = logging.getLogger("tester.browser")

CDP_DEFAULT_PORT = 9222
CDP_DEFAULT_TIMEOUT_S = 3
STEP_DEFAULT_TIMEOUT_MS = 15_000


def _wsl_host_ip() -> str | None:
    """Return the Windows host IP if this is WSL2, else None.

    On WSL2 the nameserver in /etc/resolv.conf is the Windows host
    gateway. On plain Linux it's 127.0.0.53 (systemd-resolved) or a
    real upstream resolver — those won't have a CDP endpoint, so we
    treat them as 'no WSL host'.
    """
    try:
        for line in Path("/etc/resolv.conf").read_text().splitlines():
            if line.startswith("nameserver "):
                ip = line.split()[1].strip()
                if ip.startswith("127."):
                    return None
                return ip
    except FileNotFoundError:
        return None
    return None


def _cdp_endpoint_reachable(host: str, port: int, timeout: float = CDP_DEFAULT_TIMEOUT_S) -> bool:
    url = f"http://{host}:{port}/json/version"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            resp.read(64)
            return resp.status == 200
    except Exception:
        return False


def _resolve_cdp_url() -> str | None:
    """Return a CDP ws/http URL if one is reachable, else None.

    Order:
      1. $PLAYWRIGHT_CDP_URL  (full URL, e.g. http://1.2.3.4:9222)
      2. WSL2 host on $PLAYWRIGHT_CDP_PORT or 9222
      3. localhost on $PLAYWRIGHT_CDP_PORT or 9222
    """
    env_url = os.environ.get("PLAYWRIGHT_CDP_URL")
    if env_url:
        return env_url
    port = int(os.environ.get("PLAYWRIGHT_CDP_PORT", CDP_DEFAULT_PORT))
    candidates: list[str] = []
    wsl_ip = _wsl_host_ip()
    if wsl_ip:
        candidates.append(wsl_ip)
    candidates.append("127.0.0.1")
    for host in candidates:
        if _cdp_endpoint_reachable(host, port):
            return f"http://{host}:{port}"
    return None


@dataclasses.dataclass
class StepResult:
    step_id: str
    ok: bool
    observation: str
    screenshot: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class BrowserRunner:
    """A tiny wrapper over a Playwright `Page` plus a screenshots dir.

    Usage:
        with BrowserRunner(screenshots_dir=...) as r:
            r.run_step({"id": "01", "description": "...",
                        "action": {"type": "goto", "url": "..."},
                        "screenshot": {"after": True, "filename": "01-home.png"}})
    """

    def __init__(
        self,
        screenshots_dir: Path,
        *,
        cdp_url: str | None = None,
        headless: bool | None = None,
        viewport: tuple[int, int] = (1280, 800),
    ) -> None:
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self._cdp_url = cdp_url if cdp_url is not None else _resolve_cdp_url()
        if headless is None:
            headless = os.environ.get("PLAYWRIGHT_HEADLESS", "1") != "0"
        self._headless = headless
        self._viewport = viewport
        self._pw: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._mode: str = "uninitialized"

    # ---- lifecycle ----------------------------------------------------------

    def __enter__(self) -> "BrowserRunner":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop()

    def start(self) -> None:
        self._pw = sync_playwright().start()
        if self._cdp_url:
            log.info("browser_runner: connecting to CDP at %s", self._cdp_url)
            self._browser = self._pw.chromium.connect_over_cdp(self._cdp_url)
            self._mode = "cdp"
            ctxs = self._browser.contexts
            self._context = ctxs[0] if ctxs else self._browser.new_context(viewport={"width": self._viewport[0], "height": self._viewport[1]})
            pages = self._context.pages
            self._page = pages[0] if pages else self._context.new_page()
        else:
            log.info("browser_runner: no CDP endpoint; launching local Chromium (headless=%s)", self._headless)
            self._browser = self._pw.chromium.launch(headless=self._headless)
            self._mode = "local"
            self._context = self._browser.new_context(viewport={"width": self._viewport[0], "height": self._viewport[1]})
            self._page = self._context.new_page()

    def stop(self) -> None:
        with contextlib.suppress(Exception):
            if self._mode == "local" and self._context is not None:
                self._context.close()
        with contextlib.suppress(Exception):
            if self._browser is not None and self._mode == "local":
                self._browser.close()
        with contextlib.suppress(Exception):
            if self._pw is not None:
                self._pw.stop()
        self._pw = self._browser = self._context = self._page = None

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("BrowserRunner not started")
        return self._page

    # ---- step execution -----------------------------------------------------

    def run_step(self, step: dict[str, Any]) -> StepResult:
        step_id = str(step.get("id", "??"))
        desc = str(step.get("description", ""))
        action = step.get("action") or {}
        timeout = int(step.get("timeout_ms") or STEP_DEFAULT_TIMEOUT_MS)
        screenshot_spec = step.get("screenshot") or {}
        try:
            self._dispatch_action(action, timeout=timeout)
        except PlaywrightTimeoutError as exc:
            return StepResult(step_id, False, f"timed out: {desc}", error=str(exc))
        except Exception as exc:
            return StepResult(step_id, False, f"error: {desc}", error=repr(exc))

        observation = self._observe(step)
        screenshot_path: str | None = None
        if screenshot_spec.get("after"):
            screenshot_path = self._capture(step_id, screenshot_spec)

        return StepResult(step_id, True, observation, screenshot=screenshot_path)

    # ---- actions ------------------------------------------------------------

    def _dispatch_action(self, action: dict[str, Any], *, timeout: int) -> None:
        kind = action.get("type")
        page = self.page
        if kind == "goto":
            url = action["url"]
            page.goto(url, timeout=timeout, wait_until=action.get("wait_until", "load"))
        elif kind == "click":
            target = self._locate(action, timeout=timeout)
            target.click(timeout=timeout)
        elif kind == "fill":
            target = self._locate(action, timeout=timeout)
            value = action.get("value")
            if value is None and action.get("value_env"):
                env_name = action["value_env"]
                value = os.environ.get(env_name)
                if value is None:
                    raise ValueError(
                        f"fill: env var {env_name!r} not set; export it before running"
                    )
            if value is None:
                raise ValueError("fill action requires 'value' or 'value_env'")
            target.fill(value, timeout=timeout)
        elif kind == "press":
            page.keyboard.press(action["key"])
        elif kind == "wait_for":
            target = self._locate(action, timeout=timeout)
            target.wait_for(state=action.get("state", "visible"), timeout=timeout)
        elif kind == "noop":
            return
        else:
            raise ValueError(f"unknown action type: {kind!r}")

    def _locate(self, action: dict[str, Any], *, timeout: int):
        page = self.page
        if "selector" in action:
            return page.locator(action["selector"]).first
        hint = action.get("selector_hint") or ""
        role = action.get("role")
        name = action.get("name") or _name_from_hint(hint)
        if role and name:
            return page.get_by_role(role, name=name).first
        if name:
            return page.get_by_text(name, exact=False).first
        if action.get("placeholder"):
            return page.get_by_placeholder(action["placeholder"]).first
        if action.get("label"):
            return page.get_by_label(action["label"]).first
        raise ValueError(
            f"could not derive a locator from action; provide 'selector', 'role'+'name', "
            f"'placeholder', or 'label'. action={action!r}"
        )

    # ---- observation + screenshots -----------------------------------------

    def _observe(self, step: dict[str, Any]) -> str:
        verify = step.get("verify")
        page = self.page
        title = page.title()
        url = page.url
        parts = [f"title={title!r}", f"url={url}"]
        if verify:
            try:
                hit = page.get_by_text(verify, exact=False).first
                visible = hit.is_visible(timeout=1500)
                parts.append(f"verify({verify!r})={'ok' if visible else 'not-visible'}")
            except Exception as exc:
                parts.append(f"verify({verify!r})=error:{exc.__class__.__name__}")
        return "; ".join(parts)

    def _capture(self, step_id: str, spec: dict[str, Any]) -> str:
        filename = spec.get("filename") or f"{step_id}-after.png"
        out = self.screenshots_dir / filename
        try:
            self.page.screenshot(path=str(out), full_page=bool(spec.get("full_page", False)))
        except Exception as exc:
            log.warning("screenshot failed for step %s: %s", step_id, exc)
            return ""
        return str(out.relative_to(self.screenshots_dir.parent)) if out.is_relative_to(self.screenshots_dir.parent) else str(out)


def _name_from_hint(hint: str) -> str | None:
    if not hint:
        return None
    m = re.search(r"['\"]([^'\"]+)['\"]", hint)
    if m:
        return m.group(1)
    return hint[:60].strip()


def smoke(url: str, screenshots_dir: Path) -> dict[str, Any]:
    """Tiny end-to-end smoke: navigate, screenshot, return JSON-ish result."""
    steps = [
        {
            "id": "smoke-01",
            "description": f"navigate to {url}",
            "action": {"type": "goto", "url": url, "wait_until": "domcontentloaded"},
            "screenshot": {"after": True, "filename": "smoke-01-loaded.png"},
        }
    ]
    with BrowserRunner(screenshots_dir=screenshots_dir) as r:
        results = [r.run_step(s) for s in steps]
        return {"mode": r.mode, "steps": [x.to_dict() for x in results]}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://app.specterx.com")
    parser.add_argument("--out", default="workspace/articles/00-test/screenshots")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    result = smoke(args.url, Path(args.out))
    print(json.dumps(result, indent=2))
