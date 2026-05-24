# SpecterX Documentation — Reference Library & Guidelines

This repository is the source-of-truth for SpecterX documentation standards. It contains:

1. A curated, offline reference library of four well-regarded product knowledge bases (HubSpot, Egnyte, Dropbox DocSend, Vera/Tricentis).
2. Per-platform analyses extracting how each one structures hierarchy, page anatomy, cross-references, screenshots, voice, and scope decisions.
3. SpecterX house guidelines synthesized from those analyses.

The end goal is a small, opinionated set of rules and templates that anyone at SpecterX can use to write a new documentation page that feels consistent with the rest.

## Status

**Phase 1 — Prototype: complete, ready for checkpoint review.**

| Platform | Pages | Assets | Disk | Analysis |
| --- | --- | --- | --- | --- |
| HubSpot (primary — connectors) | 17 | 482 | 25M | [`sources/hubspot/README.md`](sources/hubspot/README.md) |
| Egnyte | 15 | 207 | 24M | [`sources/egnyte/README.md`](sources/egnyte/README.md) |
| Dropbox DocSend | 15 | 147 | 12M | [`sources/docsend/README.md`](sources/docsend/README.md) |
| Vera / Tricentis | 12 | 27 | 828K | [`sources/vera/README.md`](sources/vera/README.md) |
| **Total** | **59** | **863** | **62M** | |

**Phase 2 — Full crawl + synthesis (pending Phase 1 checkpoint).** Expands the crawl to ~80–150 pages per platform and produces the synthesis guidelines (`guidelines/STYLE_GUIDE.md`, `PAGE_TEMPLATE.md`, `SCREENSHOT_GUIDELINES.md`, `INFORMATION_ARCHITECTURE.md`).

## Repository layout

```
sources/
  hubspot/      # PRIMARY: connector / integration documentation playbook
  egnyte/       # Secure content collaboration
  docsend/      # Secure document sharing + viewer analytics
  vera/         # Validation management platform
  <platform>/
    pages/              # Saved HTML, one file per source page
    pages/assets/       # Per-page images (PNG/JPG/WebP/AVIF/GIF, content-SVG)
    index.json          # url → local file, title, breadcrumb, asset count
    README.md           # Analysis of this platform's documentation patterns

guidelines/             # Phase 2 deliverable — SpecterX house rules
  STYLE_GUIDE.md
  PAGE_TEMPLATE.md
  SCREENSHOT_GUIDELINES.md
  INFORMATION_ARCHITECTURE.md

tools/
  scrape.py             # Playwright-based crawler (shared across platforms)
  platforms/*.yml       # Per-platform crawl config: seeds, allow/deny, max pages
```

## How to run the scraper

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

python tools/scrape.py egnyte
python tools/scrape.py docsend
python tools/scrape.py hubspot
python tools/scrape.py vera
```

Each platform has a YAML config under `tools/platforms/`. The crawler is incremental — already-fetched URLs are skipped unless you pass `--force`. To discover real article URLs for a platform (used to build seed lists before scraping), use `tools/discover_links.py`.

## How to browse this library

There's a generated navigation site at the repo root (`index.html`, `compare.html`, and per-platform `sources/<slug>/index.html`). Because browsers block image loads from `file://` URLs for security reasons, serve the directory with a local HTTP server:

```bash
cd "/Users/hizki/Workspace/SpecterX Documentation"
python3 -m http.server 8765
# then open http://localhost:8765/index.html
```

From the master page you can:
- Open any of the four platform pages — each shows stats, key takeaways, and a sortable table of every saved page with "View offline" and "Live ↗" links per row.
- Open `compare.html` for side-by-side voice samples, page-anatomy comparison, screenshot-density table, and cross-reference patterns.
- Open any saved knowledge-base page — they render with full original layout, styling, and screenshots.

To regenerate the site after a new crawl: `python tools/build_site.py`.

## Why these four platforms

| Platform | Why it's in the set |
| --- | --- |
| **HubSpot** | Best-in-class documentation of product connectors that live inside Gmail, Outlook, and Chrome — a direct model for SpecterX's Gmail and Outlook connectors. |
| **Egnyte** | Closest functional analog to SpecterX: secure content collaboration with permissions, governance, classification, and admin tooling. |
| **Dropbox DocSend** | Closest analog for SpecterX's secure-share use case (link-based sharing, watermarks, viewer analytics, NDAs). |
| **Vera (Tricentis)** | Enterprise, policy-heavy admin documentation — useful as a contrast point to the consumer-friendlier style of the other three. |

## Disclaimer

The contents of `sources/` are downloaded copies of public help-center pages, stored locally for research and reference only. They are not republished. Each saved page records the original URL it came from in `index.json` so it can always be cited back to the source.
