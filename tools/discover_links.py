#!/usr/bin/env python3
"""
One-off helper: fetch a category/index page and print every internal link
whose path matches a given prefix. Used to build accurate seed lists when
guessed URL slugs return 404s.

Example:
    python tools/discover_links.py https://help.dropbox.com/docsend \\
        --include /share/dropbox-docsend
"""

from __future__ import annotations

import argparse
import sys
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("url", help="Category/index page URL to inspect")
    p.add_argument(
        "--include",
        action="append",
        default=[],
        help="Only print links whose path contains this substring (repeatable)",
    )
    p.add_argument("--user-agent", default="SpecterX-DocsResearch/0.1")
    args = p.parse_args()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=args.user_agent)
        page = ctx.new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=60_000)
        try:
            page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:
            pass
        page.evaluate(
            """async () => {
                await new Promise((r) => {
                    let t = 0; const s = 600;
                    const i = setInterval(() => {
                        window.scrollBy(0, s); t += s;
                        if (t >= document.body.scrollHeight) { clearInterval(i); r(); }
                    }, 100);
                });
            }"""
        )
        html = page.content()
        ctx.close()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    needles = args.include or [""]
    for a in soup.find_all("a"):
        href = a.get("href")
        if not href:
            continue
        absolute = urljoin(args.url, href)
        path = urlparse(absolute).path
        if not any(n in path for n in needles):
            continue
        normalized = absolute.split("#")[0].split("?")[0]
        seen.add(normalized)

    for url in sorted(seen):
        print(url)
    print(f"\n[{len(seen)} unique links]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
