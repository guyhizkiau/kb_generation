#!/usr/bin/env python3
"""
Generate the navigation site (index.html + per-platform pages + compare page)
from the saved index.json files. Re-run after every scrape.

Usage:
    python tools/build_site.py
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────────────────────
# Platform metadata (curated; not derived from JSON)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Platform:
    slug: str
    name: str
    short_name: str
    tag: str
    relevance: str
    description: str
    accent_class: str
    key_takeaways: list[str]

PLATFORMS: list[Platform] = [
    Platform(
        slug="hubspot",
        name="HubSpot Knowledge Base",
        short_name="HubSpot",
        tag="Primary — connector playbook",
        relevance="Best-in-class documentation of host-app connectors (Chrome / Outlook / Office 365). Directly models SpecterX's Gmail and Outlook connectors.",
        description="17 pages spanning the full Sales Chrome extension lifecycle, both Outlook add-ins, SSO, and password reset.",
        accent_class="hubspot",
        key_takeaways=[
            "A repeatable connector lifecycle page set: landing → shared install hub → action-titled use pages → troubleshoot → uninstall. Apply directly to SpecterX Gmail + Outlook.",
            '"Before you get started" as the universal first H2: Requirements + Limitations + Permissions in one predictable place.',
            "Bold every UI label, every time. The most consistent formatting rule across all 17 saved pages.",
            "Cross-connector redirect in paragraph 2 of every landing page (\"If you're using the other connector, here's its guide…\").",
            "Multi-vendor / multi-IdP sections use H3-per-vendor inside one page (the SSO page: Okta / OneLogin / Entra ID / Google).",
            "Screenshot density splits clearly by page type: landings 4 images, task pages 22-76 images.",
        ],
    ),
    Platform(
        slug="egnyte",
        name="Egnyte Help Center",
        short_name="Egnyte",
        tag="Closest functional analog",
        relevance="Closest match to SpecterX's domain — secure content sharing, link permissions, classification/DLP, governance, admin.",
        description="15 pages across sharing workflows, link security, folder permissions, Secure & Govern (classification), admin roles, and the Outlook add-in.",
        accent_class="egnyte",
        key_takeaways=[
            "Audience-based splits: separate User Guide + Configuration Guide pages for the same feature (Outlook add-in is the canonical example).",
            "Explicit Prerequisites + Supported Configurations + Known Limitations sections on every installable component.",
            "Audience duplication in the IA — same article reachable from both the product-surface category AND the user-type category.",
            "Numbered list + inline screenshot per step is the workhorse pattern.",
            "Long, screenshot-dense feature manuals (one page has 88 images) live alongside short reference pages. Density follows page type.",
            "Avoid: mixed 2nd/3rd person ('users can…' / 'you can…' in same article); inconsistent UI-element formatting; promo banner on every page.",
        ],
    ),
    Platform(
        slug="docsend",
        name="Dropbox DocSend Help",
        short_name="DocSend",
        tag="Secure-share analog",
        relevance="Closest analog for SpecterX's secure-share use case — link-based external sharing, watermarks, viewer analytics, NDAs.",
        description="15 pages covering the DocSend category index plus link security (watermarks, allow/block, passcode, email auth, disable), Agreements, analytics, Spaces.",
        accent_class="docsend",
        key_takeaways=[
            "One feature, one outcome, one page — even when several controls share a UI panel. Watermarks, allow/block, passcode, email auth all get separate pages.",
            "Consistent page skeleton: plan-gate banner → 1-paragraph intro → auto-TOC (\"In this article\") → 2–6 task sections → 'Visitor experience' → 'Default options' → 'Related Articles'.",
            "A dedicated 'Visitor experience' H2 section on every share workflow — what the recipient sees, with its own screenshot.",
            "'Things to consider' section documents the limits, not just the happy path.",
            "Screenshots consistently inline above the step they illustrate, cropped tight to the UI region, no annotations.",
            "Second-person, present tense, contractions allowed, Title Case for product features, bold for UI button names, sparing 'Important:' / 'Note:' callouts.",
        ],
    ),
    Platform(
        slug="vera",
        name="Vera (Tricentis) Documentation",
        short_name="Vera",
        tag="Enterprise contrast point",
        relevance="Validation / approvals platform for regulated industries. Useful as a contrast — enterprise B2B style with very different choices.",
        description="12 pages covering the home, release notes, user guide (Web Portal workflows), the Tosca integration, and the admin guide top.",
        accent_class="vera",
        key_takeaways=[
            "Hard audience split at the guide level: User Guide vs Admin Guide vs Configuration Guide as separate top-level books.",
            "A dedicated 'Constraints' / 'Known Limitations' top-level section — regulated customers look there first.",
            "Section index pages are short, link-only orientation hubs; task pages are short and focused. Two distinct page types.",
            "Inline 'New in version X.Y' annotations flag version-specific behavior mid-content — readers don't have to dig into release notes.",
            "Sentence-case headings, formal/concise register suit admin/security pages.",
            "Avoid: over-splitting (Approve and Reject as separate pages); near-zero screenshots on end-user workflow pages; 3-level-deep URL hierarchy.",
        ],
    ),
]

PLATFORMS_BY_SLUG = {p.slug: p for p in PLATFORMS}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def esc(s: str | None) -> str:
    return html.escape(s or "", quote=True)


def fmt_thousands(n: int) -> str:
    return f"{n:,}"


def dir_size_kb(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for f in path.rglob("*"):
        if f.is_file():
            total += f.stat().st_size
    return total // 1024


def fmt_disk(kb: int) -> str:
    if kb >= 1024:
        return f"{kb / 1024:.1f} MB"
    return f"{kb} KB"


def read_index(slug: str) -> list[dict]:
    p = REPO_ROOT / "sources" / slug / "index.json"
    if not p.exists():
        return []
    return json.loads(p.read_text())


def topnav(active: str) -> str:
    items = [
        ("Overview", "/index.html", "home"),
        ("HubSpot", "/sources/hubspot/index.html", "hubspot"),
        ("Egnyte", "/sources/egnyte/index.html", "egnyte"),
        ("DocSend", "/sources/docsend/index.html", "docsend"),
        ("Vera", "/sources/vera/index.html", "vera"),
        ("Compare", "/compare.html", "compare"),
    ]
    links_html = "".join(
        f'<a class="{"is-active" if key == active else ""}" href="{esc(href)}">{esc(label)}</a>'
        for label, href, key in items
    )
    return f"""
<nav class="topnav">
  <div class="topnav-inner">
    <div class="topnav-brand">SpecterX Docs <small>· reference library</small></div>
    <div class="topnav-links">{links_html}</div>
    <div class="topnav-meta">Phase 1 — Prototype</div>
  </div>
</nav>
""".strip()


def html_doc(title: str, body: str, css_relative_path: str = "/site.css") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="{esc(css_relative_path)}">
</head>
<body>
{body}
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Master index.html
# ─────────────────────────────────────────────────────────────────────────────


def build_master() -> None:
    indices = {p.slug: read_index(p.slug) for p in PLATFORMS}
    total_pages = sum(len(rows) for rows in indices.values())
    total_assets = sum(int(r.get("asset_count", 0)) for rows in indices.values() for r in rows)
    total_kb = sum(dir_size_kb(REPO_ROOT / "sources" / p.slug) for p in PLATFORMS)

    cards_html = []
    for p in PLATFORMS:
        rows = indices[p.slug]
        pages = len(rows)
        assets = sum(int(r.get("asset_count", 0)) for r in rows)
        size = fmt_disk(dir_size_kb(REPO_ROOT / "sources" / p.slug))
        cards_html.append(f"""
<a class="card card-{p.accent_class}" href="sources/{p.slug}/index.html">
  <div class="card-head">
    <h3>{esc(p.name)}</h3>
    <span class="card-tag card-tag-{p.accent_class}">{esc(p.tag)}</span>
  </div>
  <div class="card-relevance">{esc(p.relevance)}</div>
  <p class="card-desc">{esc(p.description)}</p>
  <div class="card-stats">
    <span><strong>{pages}</strong> pages</span>
    <span><strong>{assets}</strong> assets</span>
    <span><strong>{size}</strong> on disk</span>
  </div>
</a>""")

    body = f"""
{topnav("home")}
<main class="page">
  <header class="hero">
    <h1>SpecterX Documentation reference library</h1>
    <p class="hero-lede">
      A curated, offline snapshot of four product knowledge bases (HubSpot, Egnyte, Dropbox DocSend, Vera/Tricentis) with per-platform analyses of how they structure documentation. The synthesis output of this research will become SpecterX's house standard for writing new documentation.
    </p>
    <div class="hero-status">Phase 1 prototype — {total_pages} pages saved · ready for checkpoint review</div>
  </header>

  <section class="stats">
    <div class="stat"><div class="stat-num">{total_pages}</div><div class="stat-label">pages saved (full HTML + images)</div></div>
    <div class="stat"><div class="stat-num">{fmt_thousands(total_assets)}</div><div class="stat-label">assets downloaded</div></div>
    <div class="stat"><div class="stat-num">4</div><div class="stat-label">platforms analyzed</div></div>
    <div class="stat"><div class="stat-num">{fmt_disk(total_kb)}</div><div class="stat-label">total on disk</div></div>
  </section>

  <h2>Platforms</h2>
  <p class="muted">Each card opens the platform's index page: stats, key takeaways, and a sortable table of every saved page.</p>
  <div class="cards">
    {''.join(cards_html)}
  </div>

  <h2>Quick comparison</h2>
  <p class="muted">Top-line answers to the seven questions. Open each platform page for evidence and citations.</p>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Question</th>
          <th>HubSpot</th>
          <th>Egnyte</th>
          <th>DocSend</th>
          <th>Vera</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Hierarchy depth</strong></td>
          <td>2 levels (topic → article)</td>
          <td>2 levels + audience duplication</td>
          <td>2 levels under product landing</td>
          <td>3 levels (guide → section → page)</td>
        </tr>
        <tr>
          <td><strong>Page-skeleton signal</strong></td>
          <td>"Before you get started" H2 always first</td>
          <td>Prerequisites / Supported OS first when relevant</td>
          <td>"In this article" auto-TOC always</td>
          <td>1-line orientation, then sub-features</td>
        </tr>
        <tr>
          <td><strong>Page-scope rule</strong></td>
          <td>One verb per page</td>
          <td>Audience-based split + concept split</td>
          <td>One feature, one outcome, one page</td>
          <td>One menu entry per page (very granular)</td>
        </tr>
        <tr>
          <td><strong>Cross-refs</strong></td>
          <td>Inline + cross-connector redirects + FAQs in-page</td>
          <td>Inline + "Additional Resources" footer</td>
          <td>Inline + "Related Articles" cards (4 siblings)</td>
          <td>IA-driven, minimal inline</td>
        </tr>
        <tr>
          <td><strong>Screenshot density (task pages)</strong></td>
          <td>20–76 per page</td>
          <td>11–88 per page (variable)</td>
          <td>~7 per page (uniform)</td>
          <td>0–3 per page</td>
        </tr>
        <tr>
          <td><strong>Voice / person</strong></td>
          <td>Strict 2nd person</td>
          <td>Mixed 2nd / 3rd</td>
          <td>Strict 2nd, contractions OK</td>
          <td>Strict 2nd, formal register</td>
        </tr>
        <tr>
          <td><strong>Headings case</strong></td>
          <td>Sentence case</td>
          <td>Title Case</td>
          <td>Sentence case (mostly)</td>
          <td>Sentence case</td>
        </tr>
        <tr>
          <td><strong>UI label formatting</strong></td>
          <td><strong>Bold</strong> (consistent)</td>
          <td>Inconsistent (bold/italic/quoted)</td>
          <td><strong>Bold</strong> (consistent)</td>
          <td>Inline plain (no special)</td>
        </tr>
        <tr>
          <td><strong>"Recipient/visitor" perspective</strong></td>
          <td>N/A (CRM tool)</td>
          <td>Inline mentions</td>
          <td>Dedicated H2 section per page</td>
          <td>N/A (closed system)</td>
        </tr>
        <tr>
          <td><strong>Lifecycle / status callouts</strong></td>
          <td>Inline ("maintenance mode") in paragraph 2</td>
          <td>"Known Limitations" H2</td>
          <td>Plan-gate banner at top</td>
          <td>"Constraints" top-level section + "New in vX.Y"</td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2>How to use this site</h2>
  <ul class="takeaways">
    <li>Read [<strong>HubSpot first</strong>](sources/hubspot/index.html) — it carries the strongest signal because the connector lifecycle pattern (§0 of its README) maps directly to SpecterX's Gmail and Outlook connectors.</li>
    <li>Use the platform pages to <strong>jump straight to any saved page</strong>. Each row has a "View offline" link that opens the saved HTML with all original images intact.</li>
    <li>Open [<strong>Compare</strong>](compare.html) for side-by-side voice samples and structural patterns across all four platforms.</li>
    <li>The per-platform <strong>README.md</strong> is the long-form analysis. The platform pages excerpt the key takeaways.</li>
  </ul>

  <h2>Phase status</h2>
  <p class="muted">Phase 1 (this site) is the prototype output. Phase 2 (post-checkpoint) will expand the crawl to ~80–150 pages per platform and produce the synthesis guidelines (<code>STYLE_GUIDE.md</code>, <code>PAGE_TEMPLATE.md</code>, <code>SCREENSHOT_GUIDELINES.md</code>, <code>INFORMATION_ARCHITECTURE.md</code>).</p>
</main>
""".strip()

    # Render markdown-style links in body manually (since we wrote them in markdown shape).
    body = body.replace("[<strong>HubSpot first</strong>](sources/hubspot/index.html)",
                        '<a href="sources/hubspot/index.html"><strong>HubSpot first</strong></a>')
    body = body.replace("[<strong>Compare</strong>](compare.html)",
                        '<a href="compare.html"><strong>Compare</strong></a>')

    (REPO_ROOT / "index.html").write_text(html_doc("SpecterX Docs — reference library", body, css_relative_path="site.css"))


# ─────────────────────────────────────────────────────────────────────────────
# Per-platform page
# ─────────────────────────────────────────────────────────────────────────────


def build_platform(p: Platform) -> None:
    rows = read_index(p.slug)
    pages_count = len(rows)
    assets_total = sum(int(r.get("asset_count", 0)) for r in rows)
    size_label = fmt_disk(dir_size_kb(REPO_ROOT / "sources" / p.slug))

    # Sort rows: highest asset count first so screenshot-heavy pages bubble up
    rows_sorted = sorted(rows, key=lambda r: (-int(r.get("asset_count", 0)), r.get("title", "")))

    row_html: list[str] = []
    for r in rows_sorted:
        url = r.get("url", "")
        final_url = r.get("final_url", url)
        local_path = r.get("local_path", "")
        title = r.get("title", "") or r.get("h1", "")
        # Trim the boilerplate site suffix from the displayed title for compactness.
        for suffix in [" - Dropbox Help", " | Knowledge Base", " – Egnyte"]:
            if title.endswith(suffix):
                title = title[: -len(suffix)]
        breadcrumbs = r.get("breadcrumbs") or []
        crumb_html = ""
        if breadcrumbs:
            crumb_html = '<div class="crumb">' + '<span class="crumb-arrow">›</span>'.join(esc(b) for b in breadcrumbs) + "</div>"
        slug_short = url.rsplit("/", 1)[-1][:60]
        # Local viewer link is the saved HTML — relative from sources/<slug>/index.html.
        local_relative = local_path.replace(f"sources/{p.slug}/", "") if local_path else ""
        assets = int(r.get("asset_count", 0))
        row_html.append(f"""
<tr class="row-{p.accent_class}">
  <td>
    <div><strong>{esc(title)}</strong></div>
    {crumb_html}
    <div class="crumb" style="margin-top: 4px;"><code>{esc(slug_short)}</code></div>
  </td>
  <td class="num">{assets}</td>
  <td class="tight">
    <a href="{esc(local_relative)}">View offline</a>
    <br>
    <a class="subtle" href="{esc(final_url)}" target="_blank" rel="noopener">Live ↗</a>
  </td>
</tr>""")

    takeaways_html = "\n".join(f"<li>{esc(t)}</li>" for t in p.key_takeaways)

    body = f"""
{topnav(p.slug)}
<main class="page">
  <header class="hero">
    <div class="card-tag card-tag-{p.accent_class}" style="margin-bottom: 12px;">{esc(p.tag)}</div>
    <h1>{esc(p.name)}</h1>
    <p class="hero-lede">{esc(p.relevance)}</p>
  </header>

  <section class="stats">
    <div class="stat"><div class="stat-num">{pages_count}</div><div class="stat-label">pages saved</div></div>
    <div class="stat"><div class="stat-num">{fmt_thousands(assets_total)}</div><div class="stat-label">assets</div></div>
    <div class="stat"><div class="stat-num">{size_label}</div><div class="stat-label">on disk</div></div>
    <div class="stat"><div class="stat-num"><a href="README.md">README ↗</a></div><div class="stat-label">full analysis (markdown)</div></div>
  </section>

  <h2>Key takeaways</h2>
  <ul class="takeaways">
    {takeaways_html}
  </ul>

  <h2>Saved pages</h2>
  <p class="muted">Sorted by asset count (proxy for screenshot density). Click <strong>View offline</strong> to open the saved HTML with original images, or <strong>Live ↗</strong> to compare against the current online version.</p>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Title / breadcrumb / slug</th>
          <th class="right">Assets</th>
          <th>Open</th>
        </tr>
      </thead>
      <tbody>
        {''.join(row_html)}
      </tbody>
    </table>
  </div>

  <div class="callout">
    <strong>Tip:</strong> if "View offline" links don't load images in your browser, you're opening files via <code>file://</code> instead of HTTP. Run <code>python3 -m http.server 8765</code> from the repo root and use <a href="http://localhost:8765/sources/{p.slug}/index.html">http://localhost:8765/sources/{p.slug}/index.html</a> instead.
  </div>
</main>
""".strip()

    out = REPO_ROOT / "sources" / p.slug / "index.html"
    out.write_text(html_doc(f"{p.short_name} — SpecterX Docs", body, css_relative_path="../../site.css"))


# ─────────────────────────────────────────────────────────────────────────────
# compare.html
# ─────────────────────────────────────────────────────────────────────────────


VOICE_SAMPLES = {
    "hubspot": {
        "label": "HubSpot",
        "quote": "Use the <strong>Track and Log</strong> features of the HubSpot Sales Chrome extension to monitor and keep a record of your contacts' engagement with your emails.",
        "from": "Track and log emails with the HubSpot Sales Chrome extension",
        "notes": "Strict 2nd person. Bold every UI label. Action-titled. Conversational but precise.",
    },
    "egnyte": {
        "label": "Egnyte",
        "quote": "Egnyte makes it easy to keep links secure. <em>Users can</em> make the link public (accessible by anyone) or private (only accessible by people who are users in the Egnyte domain), add a password, and more.",
        "from": "How Do I Make File and Folder Links More Secure?",
        "notes": "Mixed 2nd / 3rd person. <em>Users can</em> for capability statements; <em>you</em> for direct instruction.",
    },
    "docsend": {
        "label": "DocSend",
        "quote": "Stay in control; restrict access to a specific set of recipients by leveraging either our <strong>Allow Viewers</strong> or <strong>Block Viewers</strong> features. While it's difficult to control whether visitors forward links, the ability to restrict access helps ensure that only your intended viewers have access to your shared content.",
        "from": "Allow or block viewers in Dropbox DocSend",
        "notes": "Strict 2nd person. Contractions OK. Acknowledges limits up front (\"While it's difficult to control…\").",
    },
    "vera": {
        "label": "Vera",
        "quote": "When you sign into the Tricentis Vera Web Portal, all the pending tasks are displayed in the Approval Queue page.",
        "from": "Approval queue",
        "notes": "Strict 2nd person but formal register. Spells out full product name. No contractions.",
    },
}


def build_compare() -> None:
    voice_html = []
    for slug in ("hubspot", "egnyte", "docsend", "vera"):
        s = VOICE_SAMPLES[slug]
        voice_html.append(f"""
<div class="quote quote-{slug}">
  <div class="quote-label">{esc(s['label'])}</div>
  <div class="quote-text">{s['quote']}</div>
  <div class="crumb" style="margin-top: 10px;">from <em>{esc(s['from'])}</em></div>
  <div class="muted" style="margin-top: 8px; font-size: 13px;">{s['notes']}</div>
</div>""")

    body = f"""
{topnav("compare")}
<main class="page">
  <header class="hero">
    <h1>Side-by-side comparison</h1>
    <p class="hero-lede">Cross-platform views on voice, page anatomy, screenshots, and cross-references — distilled from the per-platform READMEs.</p>
  </header>

  <h2>Voice samples</h2>
  <p class="muted">One representative paragraph from each platform on the same kind of content (a security-feature explanation).</p>
  <div class="split split-4">
    {''.join(voice_html)}
  </div>

  <h2>Page anatomy at a glance</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Section</th>
          <th>HubSpot</th>
          <th>Egnyte</th>
          <th>DocSend</th>
          <th>Vera</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Pre-content banner</strong></td>
          <td>—</td>
          <td>Community promo banner (every page)</td>
          <td>Plan-gate banner ("Available on DocSend Advanced…")</td>
          <td>—</td>
        </tr>
        <tr>
          <td><strong>Intro paragraph</strong></td>
          <td>Product description + cross-connector redirect</td>
          <td>"&lt;Feature&gt; in Egnyte allow/provides…"</td>
          <td>1 paragraph: what + why</td>
          <td>1–2 sentences orienting to the UI</td>
        </tr>
        <tr>
          <td><strong>Universal first H2</strong></td>
          <td><strong>Before you get started</strong> (Requirements / Limitations / Permissions)</td>
          <td>Prerequisites (when installable)</td>
          <td><strong>In this article</strong> (auto-TOC)</td>
          <td>—</td>
        </tr>
        <tr>
          <td><strong>Body sections</strong></td>
          <td>Configure → primary task → secondary task → "View in HubSpot"</td>
          <td>Numbered tasks, each ending with screenshot</td>
          <td>2–6 task H2s</td>
          <td>1–4 sub-feature H2s</td>
        </tr>
        <tr>
          <td><strong>Recipient view</strong></td>
          <td>N/A</td>
          <td>—</td>
          <td>Dedicated <strong>Visitor experience</strong> H2 (every share page)</td>
          <td>N/A</td>
        </tr>
        <tr>
          <td><strong>Limits / caveats section</strong></td>
          <td>Inside "Before you get started"</td>
          <td>"Known Limitations" H2</td>
          <td>"Things to consider" H2</td>
          <td>Inline parentheticals + a top-level "Constraints" section</td>
        </tr>
        <tr>
          <td><strong>Trailing nav</strong></td>
          <td>None inline</td>
          <td>"Additional Resources" link list</td>
          <td>"Related Articles" cards (4 siblings)</td>
          <td>None inline</td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2>Screenshot density (per task page)</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Platform</th>
          <th>Landing pages</th>
          <th>Short reference</th>
          <th>Standard task page</th>
          <th>Long feature manual</th>
        </tr>
      </thead>
      <tbody>
        <tr class="row-hubspot"><td><strong>HubSpot</strong></td><td>4</td><td>4–22</td><td>28–52</td><td>76 (troubleshoot)</td></tr>
        <tr class="row-egnyte"><td><strong>Egnyte</strong></td><td>3</td><td>5–11</td><td>17–20</td><td>88 (long guide)</td></tr>
        <tr class="row-docsend"><td><strong>DocSend</strong></td><td>—</td><td>7 (uniform)</td><td>7 (uniform)</td><td>7 (uniform)</td></tr>
        <tr class="row-vera"><td><strong>Vera</strong></td><td>1–13</td><td>1</td><td>1–3</td><td>(not in sample)</td></tr>
      </tbody>
    </table>
  </div>
  <p class="muted">HubSpot and Egnyte scale density with content. DocSend enforces a near-uniform ~7 images per page. Vera uses screenshots sparingly even on workflow pages — an enterprise B2B convention.</p>

  <h2>Cross-reference patterns</h2>
  <div class="split">
    <div class="quote quote-hubspot">
      <div class="quote-label">HubSpot</div>
      <div class="quote-text">Inline links to dependency concepts. <strong>Cross-connector redirects</strong> in paragraph 2 of every connector landing. FAQs bundled into the parent setup page as a final H2. No "Related articles" footer.</div>
    </div>
    <div class="quote quote-egnyte">
      <div class="quote-label">Egnyte</div>
      <div class="quote-text">Inline links to dependency articles in the intro paragraph. <strong>"Additional Resources"</strong> footer = plain bulleted link list, hand-curated. No callouts wrapping cross-refs.</div>
    </div>
    <div class="quote quote-docsend">
      <div class="quote-label">DocSend</div>
      <div class="quote-text">Inline links throughout. <strong>"Related Articles"</strong> footer = 4 cards (heading + snippet) of sibling articles in the same H2 group on the product index. Lateral discovery, not next-step.</div>
    </div>
    <div class="quote quote-vera">
      <div class="quote-label">Vera</div>
      <div class="quote-text">IA-driven. Section index pages are the table of contents. <strong>"New in Vera X.Y"</strong> inline annotations point to release notes for version-specific behavior. Minimal lateral linking.</div>
    </div>
  </div>

  <h2>Page-scope (split) rules</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Platform</th>
          <th>Inferred rule</th>
          <th>Example</th>
        </tr>
      </thead>
      <tbody>
        <tr class="row-hubspot">
          <td><strong>HubSpot</strong></td>
          <td>One user-visible verb per page</td>
          <td>Install / Customize / Track / Log / Use sales tools / Manage meetings / Troubleshoot / Uninstall — all separate</td>
        </tr>
        <tr class="row-egnyte">
          <td><strong>Egnyte</strong></td>
          <td>Audience-based + concept-based split</td>
          <td>Outlook add-in has a User Guide and a Configuration Guide as separate pages</td>
        </tr>
        <tr class="row-docsend">
          <td><strong>DocSend</strong></td>
          <td>One feature + one outcome = one page</td>
          <td>Watermarks, allow/block, passcode, email auth, email validation — all separate, despite sharing the link-settings panel</td>
        </tr>
        <tr class="row-vera">
          <td><strong>Vera</strong></td>
          <td>One UI menu entry per page (very granular)</td>
          <td>Approve records and Reject records are sibling pages, not sections of one page</td>
        </tr>
      </tbody>
    </table>
  </div>
</main>
""".strip()

    (REPO_ROOT / "compare.html").write_text(html_doc("Compare — SpecterX Docs", body, css_relative_path="site.css"))


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    build_master()
    for p in PLATFORMS:
        build_platform(p)
    build_compare()
    print("Built:")
    print("  index.html")
    print("  compare.html")
    for p in PLATFORMS:
        print(f"  sources/{p.slug}/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
