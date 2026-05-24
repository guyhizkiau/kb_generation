#!/usr/bin/env python3
"""
build_kb.py — generates the SpecterX Zendesk-style KB pages from kb/articles.json.

Outputs:
  kb/categories/<cat-slug>.html   — 11 category landing pages
  kb/articles/<article-slug>.html — ~100 stub article pages (POC pages are hand-written, skipped)
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
KB   = ROOT / "kb"
DATA = KB / "articles.json"

# Articles handled by hand (not overwritten by this script)
HAND_WRITTEN = {
    "securely-share-a-file-from-the-web-platform",
    "configure-a-security-policy",
    "review-audit-logs-and-usage-dashboards",
}

ICONS = {
    "rocket": "🚀", "share": "📤", "inbox": "📥", "folder": "📁",
    "email": "✉️", "connect": "🔗", "shield": "🛡️", "org": "🏢",
    "integrations": "⚙️", "server": "🖥️", "book": "📚",
}

SUB_SECTION_LABELS = {
    "outlook-new":    "Outlook New Add-in",
    "outlook-classic":"Outlook Classic Add-in",
    "gmail":          "Gmail Extension",
    "share-in-place": "Share-in-place connectors",
    "messaging":      "Messaging connector",
    "salesforce":     "Salesforce",
    "identity":       "Identity integration",
    "storage":        "Storage integration",
    "security":       "Security & classification integration",
    "mail-protection":"Mail Protection service",
    "limits":         "Capability limits",
    "compliance":     "Compliance",
    "release-notes":  "Release notes",
}


def load():
    with open(DATA) as f:
        return json.load(f)


def topbar(active_href: str, up_one: bool = False) -> str:
    prefix = "../" if up_one else ""
    return f"""<nav class="kb-topbar">
  <div class="kb-topbar-inner">
    <a href="{prefix}../kb/index.html" class="kb-logo">
      <div class="kb-logo-mark">SX</div>
      SpecterX Help
    </a>
    <div class="kb-topbar-search">
      <input type="text" placeholder="Search help articles…" id="kb-search-input" autocomplete="off">
      <span class="kb-topbar-search-icon">🔍</span>
      <div class="kb-search-dropdown" id="kb-search-dropdown"></div>
    </div>
    <div class="kb-topbar-actions">
      <a href="#">Sign in</a>
      <a href="#" class="is-btn">Submit a request</a>
    </div>
  </div>
</nav>"""


def footer(depth: int = 1) -> str:
    prefix = "../" * depth
    return f"""<footer class="kb-footer">
  <div class="kb-footer-inner">
    <div>
      <h4>SpecterX Help</h4>
      <ul>
        <li><a href="{prefix}kb/index.html">Help Center Home</a></li>
        <li><a href="{prefix}kb/sitemap.html">Sitemap</a></li>
        <li><a href="{prefix}specterx.html">KB IA reference</a></li>
      </ul>
    </div>
    <div>
      <h4>Other ways to get help</h4>
      <ul>
        <li><a href="#">Community forums</a></li>
        <li><a href="#">Contact support</a></li>
        <li><a href="#">System status</a></li>
      </ul>
    </div>
    <div>
      <h4>Reference library</h4>
      <ul>
        <li><a href="{prefix}index.html">Overview</a></li>
        <li><a href="{prefix}sources/virtru/index.html">Virtru analysis</a></li>
        <li><a href="{prefix}compare.html">Compare KBs</a></li>
      </ul>
    </div>
  </div>
  <div class="kb-footer-bottom">
    <p>© 2026 SpecterX — Help Center preview</p>
    <p><a href="{prefix}kb/sitemap.html">Sitemap</a></p>
  </div>
</footer>"""


def search_js(depth: int = 1) -> str:
    prefix = "../" * depth
    return f"""<script src="{prefix}kb/kb.js"></script>"""


def badge(status: str) -> str:
    if status == "poc":
        return '<span class="kb-badge is-poc">Live</span>'
    return '<span class="kb-badge is-planned">Planned</span>'


def article_path(slug: str) -> str:
    return f"../articles/{slug}.html"


# ──────────────────────────────────────────────────────────────────────────────
# Category pages
# ──────────────────────────────────────────────────────────────────────────────

def build_category(cat: dict, articles: list[dict]) -> str:
    cat_articles = [a for a in articles if a["category"] == cat["slug"]]
    # Group by sub_section preserving order
    seen_subs: list[str | None] = []
    for a in cat_articles:
        sub = a.get("sub_section")
        if sub not in seen_subs:
            seen_subs.append(sub)

    sections_html = ""
    for sub in seen_subs:
        group = [a for a in cat_articles if a.get("sub_section") == sub]
        label = SUB_SECTION_LABELS.get(sub, "") if sub else ""
        if label:
            sections_html += f'<div class="kb-subsection"><div class="kb-subsection-title">{label}</div>\n'
        else:
            sections_html += '<div class="kb-subsection">\n'
        sections_html += '<ul class="kb-article-list">\n'
        for a in group:
            sections_html += f"""  <li>
    <a href="../articles/{a['slug']}.html" class="kb-article-list-link">
      <span class="kb-article-list-icon">📄</span>
      <div class="kb-article-list-body">
        <div class="kb-article-list-title">{a['title']}</div>
        <div class="kb-article-list-intro">{a['intro']}</div>
      </div>
      <div class="kb-article-list-badge">{badge(a['status'])}</div>
    </a>
  </li>\n"""
        sections_html += "</ul></div>\n"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{cat['title']} — SpecterX Help</title>
  <link rel="stylesheet" href="../kb.css">
</head>
<body>
{topbar(f"categories/{cat['slug']}.html", up_one=False)}
<div class="kb-category-page">
  <nav class="kb-breadcrumb">
    <a href="../../kb/index.html">Help Center</a>
    <span class="kb-breadcrumb-sep">›</span>
    {cat['title']}
  </nav>
  <div class="kb-category-header">
    <h1>{cat['icon'] and ICONS.get(cat['icon'], '')} {cat['title']}</h1>
    <p>{cat['description']}</p>
  </div>
  {sections_html}
</div>
{footer(depth=2)}
{search_js(depth=2)}
</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────────────
# Stub article pages
# ──────────────────────────────────────────────────────────────────────────────

def build_stub(article: dict, cat: dict, all_articles: list[dict]) -> str:
    cat_siblings = [
        a for a in all_articles
        if a["category"] == article["category"] and a["slug"] != article["slug"]
    ][:6]

    sidebar_html = '<div class="kb-sidebar-card"><h3>Articles in this section</h3><ul class="kb-sidebar-list">'
    for sib in cat_siblings:
        sidebar_html += f'<li><a href="{sib["slug"]}.html">{sib["title"]}</a></li>'
    sidebar_html += "</ul></div>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{article['title']} — SpecterX Help</title>
  <link rel="stylesheet" href="../kb.css">
</head>
<body>
{topbar(f"articles/{article['slug']}.html", up_one=False)}
<div class="kb-article-layout">
  <main class="kb-article-main">
    <nav class="kb-breadcrumb">
      <a href="../../kb/index.html">Help Center</a>
      <span class="kb-breadcrumb-sep">›</span>
      <a href="../categories/{cat['slug']}.html">{cat['title']}</a>
      <span class="kb-breadcrumb-sep">›</span>
      {article['title']}
    </nav>
    <div class="kb-article-header">
      <h1>{article['title']}</h1>
      <div class="kb-article-meta">
        <span>Planned</span>
        <button class="kb-article-meta-follow">Follow</button>
      </div>
    </div>
    <article class="kb-article-body">
      <div class="kb-planned-banner">
        <div class="kb-planned-banner-icon">📋</div>
        <div>
          <h2>This article is planned</h2>
          <p>{article['intro']} This article has been mapped in the SpecterX KB information architecture and will be written in a future sprint.</p>
        </div>
      </div>
      <p>In the meantime, you may find the articles in the sidebar helpful, or you can <a href="#">contact support</a> with your question.</p>
    </article>
    <div class="kb-article-vote">
      <p>Was this article helpful?</p>
      <button class="kb-vote-btn">Yes</button>
      <button class="kb-vote-btn">No</button>
    </div>
  </main>
  <aside class="kb-article-sidebar">
    {sidebar_html}
  </aside>
</div>
{footer(depth=2)}
{search_js(depth=2)}
</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────────────
# Home page
# ──────────────────────────────────────────────────────────────────────────────

def build_home(data: dict) -> str:
    cats = data["categories"]
    articles = data["articles"]
    art_by_slug = {a["slug"]: a for a in articles}

    # Category cards
    cards_html = ""
    for cat in cats:
        cat_arts = [a for a in articles if a["category"] == cat["slug"]][:3]
        links = "".join(f'<li><a href="categories/{cat["slug"]}.html#{a["slug"]}">{a["title"]}</a></li>' for a in cat_arts)
        count = len([a for a in articles if a["category"] == cat["slug"]])
        cards_html += f"""<a href="categories/{cat['slug']}.html" class="kb-cat-card">
  <div class="kb-cat-icon">{ICONS.get(cat['icon'], '📄')}</div>
  <h3>{cat['title']}</h3>
  <p>{cat['description']}</p>
  <ul class="kb-cat-articles">
    {links}
    <li class="more"><a href="categories/{cat['slug']}.html">See all {count} articles →</a></li>
  </ul>
</a>"""

    # Promoted articles (3 POCs)
    pocs = [a for a in articles if a["status"] == "poc"]
    prom_html = ""
    for a in pocs:
        prom_html += f"""<a href="articles/{a['slug']}.html" class="kb-promoted-item">
  <div class="kb-promoted-item-badge is-poc">Live article</div>
  <h4>{a['title']}</h4>
  <p>{a['intro']}</p>
</a>"""

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SpecterX Help Center</title>
  <link rel="stylesheet" href="kb.css">
</head>
<body>
<nav class="kb-topbar">
  <div class="kb-topbar-inner">
    <a href="index.html" class="kb-logo">
      <div class="kb-logo-mark">SX</div>
      SpecterX Help
    </a>
    <div class="kb-topbar-search">
      <input type="text" placeholder="Search help articles…" id="kb-search-input" autocomplete="off">
      <span class="kb-topbar-search-icon">🔍</span>
      <div class="kb-search-dropdown" id="kb-search-dropdown"></div>
    </div>
    <div class="kb-topbar-actions">
      <a href="#">Sign in</a>
      <a href="#" class="is-btn">Submit a request</a>
    </div>
  </div>
</nav>

<div class="kb-hero">
  <h1>How can we help?</h1>
  <div class="kb-hero-search">
    <input type="text" placeholder="Search help articles…" id="kb-hero-search-input" autocomplete="off">
    <span class="kb-hero-search-icon">🔍</span>
    <div class="kb-search-dropdown" id="kb-hero-search-dropdown"></div>
  </div>
</div>

<div class="kb-main">
  <div class="kb-section-label">Browse by category</div>
  <div class="kb-category-grid">
    {cards_html}
  </div>

  <div class="kb-promoted">
    <h2>Featured articles</h2>
    <div class="kb-promoted-list">
      {prom_html}
    </div>
  </div>
</div>

<footer class="kb-footer">
  <div class="kb-footer-inner">
    <div>
      <h4>SpecterX Help</h4>
      <ul>
        <li><a href="index.html">Help Center Home</a></li>
        <li><a href="sitemap.html">Sitemap</a></li>
        <li><a href="../specterx.html">KB IA reference</a></li>
      </ul>
    </div>
    <div>
      <h4>Other ways to get help</h4>
      <ul>
        <li><a href="#">Community forums</a></li>
        <li><a href="#">Contact support</a></li>
        <li><a href="#">System status</a></li>
      </ul>
    </div>
    <div>
      <h4>Reference library</h4>
      <ul>
        <li><a href="../index.html">Overview</a></li>
        <li><a href="../sources/virtru/index.html">Virtru analysis</a></li>
        <li><a href="../compare.html">Compare KBs</a></li>
      </ul>
    </div>
  </div>
  <div class="kb-footer-bottom">
    <p>© 2026 SpecterX — Help Center preview</p>
    <p><a href="sitemap.html">Sitemap</a></p>
  </div>
</footer>
<script src="kb.js"></script>
</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────────────
# Sitemap
# ──────────────────────────────────────────────────────────────────────────────

def build_sitemap(data: dict) -> str:
    cats = {c["slug"]: c for c in data["categories"]}
    articles = data["articles"]

    sections_html = ""
    for cat in data["categories"]:
        cat_arts = [a for a in articles if a["category"] == cat["slug"]]
        items_html = ""
        for a in cat_arts:
            items_html += f"""  <li class="kb-sitemap-row" data-title="{a['title'].lower()}">
    <a href="articles/{a['slug']}.html">{a['title']}</a>
    {badge(a['status'])}
  </li>"""
        sections_html += f"""<div class="kb-sitemap-section" id="{cat['slug']}">
  <h2>{ICONS.get(cat['icon'], '')} {cat['title']}</h2>
  <ul class="kb-sitemap-list">{items_html}</ul>
</div>"""

    total = len(articles)
    poc_count = sum(1 for a in articles if a["status"] == "poc")
    planned_count = total - poc_count

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sitemap — SpecterX Help</title>
  <link rel="stylesheet" href="kb.css">
</head>
<body>
<div class="kb-editorial-banner">
  📋 <strong>Editorial view</strong> — This sitemap is for documentation planning and is not part of the published help center.
</div>
<nav class="kb-topbar">
  <div class="kb-topbar-inner">
    <a href="index.html" class="kb-logo">
      <div class="kb-logo-mark">SX</div>
      SpecterX Help
    </a>
    <div class="kb-topbar-actions" style="margin-left:auto;">
      <a href="index.html">← Help Center</a>
      <a href="../specterx.html">KB IA reference</a>
    </div>
  </div>
</nav>
<div class="kb-main">
  <h1 style="margin-bottom:6px;">Article sitemap</h1>
  <p style="color:var(--z-muted);margin-bottom:24px;">
    {total} articles total &mdash;
    <span class="kb-badge is-poc">Live</span> {poc_count} &nbsp;
    <span class="kb-badge is-planned">Planned</span> {planned_count}
  </p>
  <input type="text" class="kb-sitemap-filter" placeholder="Filter articles by title…" id="kb-sitemap-filter">
  {sections_html}
</div>
{footer(depth=1)}
<script>
const filter = document.getElementById('kb-sitemap-filter');
filter.addEventListener('input', () => {{
  const q = filter.value.toLowerCase().trim();
  document.querySelectorAll('.kb-sitemap-row').forEach(row => {{
    const match = !q || row.dataset.title.includes(q);
    row.classList.toggle('kb-sitemap-hide', !match);
  }});
  // Hide section headings if all children hidden
  document.querySelectorAll('.kb-sitemap-section').forEach(sec => {{
    const visible = sec.querySelectorAll('.kb-sitemap-row:not(.kb-sitemap-hide)').length > 0;
    sec.style.display = visible ? '' : 'none';
  }});
}});
</script>
</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    data = load()
    cats_by_slug = {c["slug"]: c for c in data["categories"]}
    articles = data["articles"]

    os.makedirs(KB / "categories", exist_ok=True)
    os.makedirs(KB / "articles", exist_ok=True)

    # Home page
    home_html = build_home(data)
    (KB / "index.html").write_text(home_html)
    print("✓ kb/index.html")

    # Sitemap
    sitemap_html = build_sitemap(data)
    (KB / "sitemap.html").write_text(sitemap_html)
    print("✓ kb/sitemap.html")

    # Category pages
    for cat in data["categories"]:
        html = build_category(cat, articles)
        path = KB / "categories" / f"{cat['slug']}.html"
        path.write_text(html)
        print(f"✓ kb/categories/{cat['slug']}.html")

    # Stub article pages
    written = 0
    skipped = 0
    for a in articles:
        if a["slug"] in HAND_WRITTEN:
            print(f"  (skip hand-written) kb/articles/{a['slug']}.html")
            skipped += 1
            continue
        cat = cats_by_slug[a["category"]]
        html = build_stub(a, cat, articles)
        path = KB / "articles" / f"{a['slug']}.html"
        path.write_text(html)
        written += 1

    print(f"\n✓ {written} stub articles written, {skipped} hand-written articles skipped")
    print(f"✓ Total: {len(articles)} articles, {len(data['categories'])} categories")


if __name__ == "__main__":
    main()
