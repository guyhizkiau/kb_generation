#!/usr/bin/env python3
"""
SpecterX documentation reference crawler.

Reads a per-platform YAML config (tools/platforms/<name>.yml), fetches each
seed URL with a headless Chromium browser (so JS-rendered help centres work),
downloads referenced images/assets, rewrites the HTML so the page renders
offline, and writes an index.json catalog for later analysis.

Usage:
    python tools/scrape.py <platform>             # incremental
    python tools/scrape.py <platform> --force     # ignore state, re-fetch all
    python tools/scrape.py <platform> --list      # show what will be fetched

This is research tooling: it is intentionally simple, single-threaded, polite,
and deterministic. It does NOT follow links beyond the seed list in Phase 1.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.robotparser
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

import httpx
import yaml
from bs4 import BeautifulSoup
from playwright.sync_api import Page, sync_playwright
from tenacity import retry, stop_after_attempt, wait_exponential


REPO_ROOT = Path(__file__).resolve().parent.parent
PLATFORMS_DIR = REPO_ROOT / "tools" / "platforms"
STATE_DIR = REPO_ROOT / ".scrape-state"


# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PlatformConfig:
    name: str
    display_name: str
    base_url: str
    output_dir: Path
    phase: int
    max_pages: int
    request_delay_seconds: float
    asset_delay_seconds: float
    user_agent: str
    allowed_asset_hosts: list[str]
    asset_deny_substrings: list[str]
    seeds: list[str]
    respect_robots_txt: bool

    @classmethod
    def load(cls, name: str) -> "PlatformConfig":
        path = PLATFORMS_DIR / f"{name}.yml"
        if not path.exists():
            raise FileNotFoundError(f"No config at {path}")
        data = yaml.safe_load(path.read_text())
        return cls(
            name=data["name"],
            display_name=data["display_name"],
            base_url=data["base_url"].rstrip("/"),
            output_dir=REPO_ROOT / data["output_dir"],
            phase=int(data.get("phase", 1)),
            max_pages=int(data["max_pages"]),
            request_delay_seconds=float(data.get("request_delay_seconds", 1.5)),
            asset_delay_seconds=float(data.get("asset_delay_seconds", 0.3)),
            user_agent=data["user_agent"],
            allowed_asset_hosts=list(data.get("allowed_asset_hosts", [])),
            asset_deny_substrings=list(data.get("asset_deny_substrings", [])),
            seeds=list(data["seeds"]),
            respect_robots_txt=bool(data.get("respect_robots_txt", True)),
        )


# ─────────────────────────────────────────────────────────────────────────────
# State (resume-from-state)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class CrawlState:
    platform: str
    fetched: dict[str, str] = field(default_factory=dict)  # url -> local html path
    errors: dict[str, str] = field(default_factory=dict)   # url -> last error

    @classmethod
    def load(cls, platform: str) -> "CrawlState":
        STATE_DIR.mkdir(exist_ok=True)
        path = STATE_DIR / f"{platform}.json"
        if not path.exists():
            return cls(platform=platform)
        data = json.loads(path.read_text())
        return cls(
            platform=platform,
            fetched=data.get("fetched", {}),
            errors=data.get("errors", {}),
        )

    def save(self) -> None:
        STATE_DIR.mkdir(exist_ok=True)
        path = STATE_DIR / f"{self.platform}.json"
        path.write_text(json.dumps(
            {"fetched": self.fetched, "errors": self.errors},
            indent=2,
            sort_keys=True,
        ))


# ─────────────────────────────────────────────────────────────────────────────
# URL → filesystem slugs
# ─────────────────────────────────────────────────────────────────────────────


_SAFE = re.compile(r"[^a-z0-9._-]+")


def url_to_slug(url: str) -> str:
    """Stable, human-readable filename for a URL."""
    parsed = urlparse(url)
    parts = [parsed.netloc] + [p for p in parsed.path.split("/") if p]
    raw = "_".join(parts).lower()
    raw = _SAFE.sub("-", raw)
    raw = raw.strip("-_") or "index"
    return raw[:120]


def asset_filename(url: str, content_type: str | None, body: bytes) -> str:
    """Content-hashed asset filename. Extension preferred from URL path, then content-type."""
    digest = hashlib.sha1(body).hexdigest()[:16]
    ext = Path(urlparse(url).path).suffix.lower()
    if not ext and content_type:
        ct = content_type.split(";")[0].strip().lower()
        ext = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/webp": ".webp",
            "image/avif": ".avif",
            "image/gif": ".gif",
            "image/svg+xml": ".svg",
        }.get(ct, "")
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".svg"}:
        ext = ".bin"
    return f"{digest}{ext}"


# ─────────────────────────────────────────────────────────────────────────────
# Politeness
# ─────────────────────────────────────────────────────────────────────────────


def robots_allows(url: str, user_agent: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        return True  # if robots.txt is unreachable, do not block research fetches
    return rp.can_fetch(user_agent, url)


# ─────────────────────────────────────────────────────────────────────────────
# Page fetching (Playwright)
# ─────────────────────────────────────────────────────────────────────────────


def fetch_rendered_page(page: Page, url: str) -> tuple[str, dict[str, str]]:
    """Navigate, wait for content, scroll to load lazy images, return HTML + metadata."""
    page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception:
        pass  # some sites keep beacons open; HTML is still usable
    # Scroll to bottom in steps so lazy-loaded images request themselves
    page.evaluate(
        """async () => {
            await new Promise((resolve) => {
                let total = 0;
                const step = 600;
                const timer = setInterval(() => {
                    window.scrollBy(0, step);
                    total += step;
                    if (total >= document.body.scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 150);
            });
        }"""
    )
    page.wait_for_timeout(800)
    html = page.content()
    meta = {
        "final_url": page.url,
        "title": page.title() or "",
    }
    return html, meta


# ─────────────────────────────────────────────────────────────────────────────
# Asset extraction + download
# ─────────────────────────────────────────────────────────────────────────────


_SRCSET_RE = re.compile(r"\s*,\s*")


def _srcset_candidates(value: str) -> list[tuple[str, str]]:
    """Parse `srcset` into [(url, descriptor)] pairs."""
    out: list[tuple[str, str]] = []
    for part in _SRCSET_RE.split(value.strip()):
        if not part:
            continue
        bits = part.strip().split(None, 1)
        if not bits:
            continue
        url = bits[0]
        descriptor = bits[1] if len(bits) > 1 else ""
        out.append((url, descriptor))
    return out


def collect_image_urls(soup: BeautifulSoup, base_url: str) -> set[str]:
    urls: set[str] = set()
    for img in soup.find_all("img"):
        for attr in ("src", "data-src", "data-lazy-src", "data-original"):
            v = img.get(attr)
            if v:
                urls.add(urljoin(base_url, v))
        for attr in ("srcset", "data-srcset"):
            v = img.get(attr)
            if v:
                for u, _ in _srcset_candidates(v):
                    urls.add(urljoin(base_url, u))
    for source in soup.find_all("source"):
        v = source.get("srcset")
        if v:
            for u, _ in _srcset_candidates(v):
                urls.add(urljoin(base_url, u))
    return urls


def asset_url_allowed(url: str, cfg: PlatformConfig) -> bool:
    if url.startswith("data:"):
        return False
    host = urlparse(url).netloc.lower()
    if not host:
        return False
    if cfg.allowed_asset_hosts and not any(
        host == h or host.endswith("." + h) for h in cfg.allowed_asset_hosts
    ):
        return False
    return not any(needle in url for needle in cfg.asset_deny_substrings)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def _http_get(client: httpx.Client, url: str) -> httpx.Response:
    r = client.get(url, follow_redirects=True, timeout=30.0)
    r.raise_for_status()
    return r


def download_assets(
    urls: Iterable[str],
    assets_dir: Path,
    cfg: PlatformConfig,
    client: httpx.Client,
) -> dict[str, str]:
    """Download each URL and return {original_url: local_relative_path}."""
    assets_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = assets_dir / "_manifest.json"
    manifest: dict[str, dict[str, str | int]] = (
        json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    )
    url_to_local: dict[str, str] = {}
    for url in sorted(urls):
        if url in manifest and (assets_dir / manifest[url]["local"]).exists():
            url_to_local[url] = manifest[url]["local"]  # type: ignore[assignment]
            continue
        if not asset_url_allowed(url, cfg):
            continue
        try:
            resp = _http_get(client, url)
        except Exception as exc:  # noqa: BLE001
            print(f"    ! asset failed: {url} ({exc})", file=sys.stderr)
            continue
        body = resp.content
        if not body:
            continue
        name = asset_filename(url, resp.headers.get("content-type"), body)
        (assets_dir / name).write_bytes(body)
        manifest[url] = {
            "local": name,
            "content_type": resp.headers.get("content-type", ""),
            "bytes": len(body),
        }
        url_to_local[url] = name
        time.sleep(cfg.asset_delay_seconds)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return url_to_local


# ─────────────────────────────────────────────────────────────────────────────
# HTML rewriting (point image URLs at local files)
# ─────────────────────────────────────────────────────────────────────────────


def rewrite_html(
    soup: BeautifulSoup, base_url: str, url_to_local: dict[str, str], slug: str
) -> None:
    """Mutate the soup so img/source point at `assets/<slug>/<file>`."""

    def localize(remote_url: str) -> str | None:
        absolute = urljoin(base_url, remote_url)
        local = url_to_local.get(absolute)
        if local is None:
            return None
        return f"assets/{slug}/{local}"

    for img in soup.find_all("img"):
        for attr in ("src", "data-src", "data-lazy-src", "data-original"):
            v = img.get(attr)
            if v:
                rewritten = localize(v)
                if rewritten:
                    img[attr] = rewritten
        for attr in ("srcset", "data-srcset"):
            v = img.get(attr)
            if v:
                new_parts: list[str] = []
                for u, descriptor in _srcset_candidates(v):
                    rewritten = localize(u)
                    if rewritten:
                        new_parts.append(
                            f"{rewritten} {descriptor}".strip()
                        )
                if new_parts:
                    img[attr] = ", ".join(new_parts)
    for source in soup.find_all("source"):
        v = source.get("srcset")
        if v:
            new_parts = []
            for u, descriptor in _srcset_candidates(v):
                rewritten = localize(u)
                if rewritten:
                    new_parts.append(f"{rewritten} {descriptor}".strip())
            if new_parts:
                source["srcset"] = ", ".join(new_parts)

    # Annotate page so it is obvious it's an offline mirror
    head = soup.find("head")
    if head is not None:
        marker = soup.new_tag(
            "meta",
            attrs={"name": "specterx-mirror", "content": "true"},
        )
        head.append(marker)


# ─────────────────────────────────────────────────────────────────────────────
# Breadcrumb extraction (best-effort, heuristic)
# ─────────────────────────────────────────────────────────────────────────────


def extract_breadcrumbs(soup: BeautifulSoup) -> list[str]:
    selectors = [
        '[itemtype*="BreadcrumbList"] [itemprop="name"]',
        'nav[aria-label*="readcrumb"] a',
        '.breadcrumbs a',
        '.breadcrumb a',
        '.MicroBreadcrumbs a',
        '[data-test="breadcrumb"] a',
    ]
    for sel in selectors:
        nodes = soup.select(sel)
        if nodes:
            return [n.get_text(strip=True) for n in nodes if n.get_text(strip=True)]
    return []


# ─────────────────────────────────────────────────────────────────────────────
# Main crawl loop
# ─────────────────────────────────────────────────────────────────────────────


def crawl(cfg: PlatformConfig, force: bool) -> None:
    state = CrawlState.load(cfg.name)
    pages_dir = cfg.output_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    index_path = cfg.output_dir / "index.json"
    index: list[dict] = (
        json.loads(index_path.read_text()) if index_path.exists() else []
    )
    index_by_url = {row["url"]: row for row in index}

    seeds = cfg.seeds[: cfg.max_pages]
    print(f"[{cfg.name}] Phase {cfg.phase}: {len(seeds)} seed(s), output={cfg.output_dir}")

    # robots.txt check — one check per host. Can be disabled per-platform
    # in YAML (`respect_robots_txt: false`) when the host's robots.txt is
    # known-malformed and Python's parser misreads it.
    if cfg.respect_robots_txt:
        seen_hosts: set[str] = set()
        for url in seeds:
            host = urlparse(url).netloc
            if host in seen_hosts:
                continue
            seen_hosts.add(host)
            if not robots_allows(url, cfg.user_agent):
                print(f"  ! robots.txt disallows {host} — skipping host", file=sys.stderr)
                return
    else:
        print(f"  (robots.txt check skipped per platform config)", file=sys.stderr)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=cfg.user_agent,
            viewport={"width": 1366, "height": 900},
        )
        page = context.new_page()
        http = httpx.Client(headers={"User-Agent": cfg.user_agent})
        try:
            for i, url in enumerate(seeds, 1):
                if not force and url in state.fetched and Path(state.fetched[url]).exists():
                    print(f"  [{i}/{len(seeds)}] SKIP (cached) {url}")
                    continue
                print(f"  [{i}/{len(seeds)}] GET {url}")
                slug = url_to_slug(url)
                try:
                    html, meta = fetch_rendered_page(page, url)
                except Exception as exc:  # noqa: BLE001
                    print(f"    ! page failed: {exc}", file=sys.stderr)
                    state.errors[url] = str(exc)
                    state.save()
                    time.sleep(cfg.request_delay_seconds)
                    continue

                soup = BeautifulSoup(html, "html.parser")
                image_urls = collect_image_urls(soup, base_url=meta["final_url"])
                assets_dir = pages_dir / "assets" / slug
                url_to_local = download_assets(image_urls, assets_dir, cfg, http)
                rewrite_html(soup, base_url=meta["final_url"], url_to_local=url_to_local, slug=slug)

                html_out = soup.prettify()
                html_path = pages_dir / f"{slug}.html"
                html_path.write_text(html_out)

                index_by_url[url] = {
                    "url": url,
                    "final_url": meta["final_url"],
                    "title": meta["title"],
                    "h1": (soup.h1.get_text(strip=True) if soup.h1 else ""),
                    "breadcrumbs": extract_breadcrumbs(soup),
                    "local_path": str(html_path.relative_to(REPO_ROOT)),
                    "asset_count": len(url_to_local),
                    "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }
                state.fetched[url] = str(html_path)
                state.errors.pop(url, None)
                state.save()

                # Persist index incrementally so a crash mid-crawl leaves usable data
                index_rows = sorted(index_by_url.values(), key=lambda r: r["url"])
                index_path.write_text(json.dumps(index_rows, indent=2))

                time.sleep(cfg.request_delay_seconds)
        finally:
            http.close()
            context.close()
            browser.close()

    print(f"[{cfg.name}] done. fetched={len(state.fetched)} errors={len(state.errors)}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("platform", help="config name under tools/platforms/<name>.yml")
    p.add_argument("--force", action="store_true", help="ignore cached state")
    p.add_argument("--list", action="store_true", help="list seeds and exit")
    args = p.parse_args()

    cfg = PlatformConfig.load(args.platform)
    if args.list:
        print(f"{cfg.display_name} — {len(cfg.seeds)} seeds (max_pages={cfg.max_pages})")
        for s in cfg.seeds[: cfg.max_pages]:
            print(f"  - {s}")
        return 0

    crawl(cfg, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
