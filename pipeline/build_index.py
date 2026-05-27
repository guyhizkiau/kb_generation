"""pipeline/build_index.py
Generate articles/index.html — the article browser overview page.

Usage:
    python3 pipeline/build_index.py

Reads every articles/NN-slug/ directory for:
    - final.md   (title, audience, reading-time from YAML front matter)
    - STATE      (PHASE= field)

Writes articles/index.html.

Run this after every article is merged (WORKFLOW.md §9.6).
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "articles"
OUT = ARTICLES_DIR / "index.html"

# Phase → human label + colour
PHASE_LABELS = {
    "PLANNED":    ("Planned",    "#8250df"),
    "DRAFTING":   ("Drafting",   "#0969da"),
    "TESTING":    ("Testing",    "#e36209"),
    "REVISING":   ("Revising",   "#e36209"),
    "FINALIZING": ("Finalizing", "#1a7f37"),
    "PR_OPEN":    ("PR open",    "#0969da"),
    "DONE":       ("Done",       "#1a7f37"),
}


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    fm: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def read_state(path: Path) -> str:
    if not path.exists():
        return "UNKNOWN"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("PHASE="):
            return line[6:].strip()
    return "UNKNOWN"


def collect_articles() -> list[dict]:
    articles = []
    if not ARTICLES_DIR.is_dir():
        return articles
    for slug_dir in sorted(ARTICLES_DIR.iterdir()):
        if not slug_dir.is_dir():
            continue
        slug = slug_dir.name
        # Skip hidden dirs and non-article dirs
        if slug.startswith(".") or not re.match(r"^\d+", slug):
            continue
        fm = read_frontmatter(slug_dir / "final.md") if (slug_dir / "final.md").exists() else {}
        state = read_state(slug_dir / "STATE")
        preview_file = slug_dir / f"{slug}.html"
        zendesk_file = slug_dir / f"{slug}-zendesk.html"
        articles.append({
            "slug": slug,
            "title": fm.get("title", slug),
            "audience": fm.get("audience", ""),
            "reading_time": fm.get("estimated-reading-time", ""),
            "phase": state,
            "has_preview": preview_file.exists(),
            "has_zendesk": zendesk_file.exists(),
        })
    return articles


def badge(label: str, color: str) -> str:
    return (
        f'<span style="display:inline-block;padding:0.15em 0.55em;'
        f'font-size:0.75em;font-weight:600;border-radius:2em;'
        f'background:{color}22;color:{color};border:1px solid {color}55;">'
        f"{html.escape(label)}</span>"
    )


def render_row(a: dict) -> str:
    slug = a["slug"]
    phase_label, phase_color = PHASE_LABELS.get(a["phase"], (a["phase"], "#57606a"))

    links = []
    if a["has_preview"]:
        links.append(
            f'<a href="{slug}/{slug}.html" '
            f'style="color:#0969da;text-decoration:none;font-size:0.85em;">Preview</a>'
        )
    if a["has_zendesk"]:
        links.append(
            f'<a href="{slug}/{slug}-zendesk.html" '
            f'style="color:#6e40c9;text-decoration:none;font-size:0.85em;">ZenDesk</a>'
        )
    link_cell = " &nbsp;·&nbsp; ".join(links) if links else '<span style="color:#bbb;font-size:0.85em;">—</span>'

    meta_parts = []
    if a["audience"]:
        meta_parts.append(html.escape(a["audience"]))
    if a["reading_time"]:
        meta_parts.append(html.escape(a["reading_time"]))
    meta = " · ".join(meta_parts)

    return (
        f"<tr>"
        f'<td style="padding:0.6rem 1rem 0.6rem 0;white-space:nowrap;color:#57606a;font-size:0.85em;">'
        f'{html.escape(slug[:2])}</td>'
        f'<td style="padding:0.6rem 1rem;">'
        f'<strong>{html.escape(a["title"])}</strong>'
        + (f'<br><span style="font-size:0.8em;color:#57606a;">{meta}</span>' if meta else "")
        + f"</td>"
        f'<td style="padding:0.6rem 1rem;">{badge(phase_label, phase_color)}</td>'
        f'<td style="padding:0.6rem 0;">{link_cell}</td>'
        f"</tr>\n"
    )


def build(articles: list[dict]) -> str:
    total = len(articles)
    done = sum(1 for a in articles if a["phase"] == "DONE")
    pr_open = sum(1 for a in articles if a["phase"] == "PR_OPEN")

    rows = "".join(render_row(a) for a in articles)

    stat_items = [
        f'<span style="margin-right:1.5rem;">'
        f'<strong style="font-size:1.5rem;">{done}</strong>'
        f'<span style="color:#57606a;font-size:0.9em;"> / {total} done</span></span>',
    ]
    if pr_open:
        stat_items.append(
            f'<span style="margin-right:1.5rem;">'
            f'<strong style="font-size:1.5rem;color:#0969da;">{pr_open}</strong>'
            f'<span style="color:#57606a;font-size:0.9em;"> in review</span></span>'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{ color-scheme: light; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    color: #1f2328;
    background: #f6f8fa;
    font-size: 16px;
    line-height: 1.5;
  }}
  .wrap {{
    max-width: 860px;
    margin: 0 auto;
    padding: 48px 32px 96px;
    background: #fff;
    min-height: 100vh;
    box-shadow: 0 1px 2px rgba(0,0,0,.04);
  }}
  h1 {{
    font-size: 1.6rem;
    margin: 0 0 0.25rem;
    border-bottom: 1px solid #d0d7de;
    padding-bottom: 0.4rem;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 1.5rem;
  }}
  tr + tr {{ border-top: 1px solid #eaeef2; }}
  th {{
    text-align: left;
    padding: 0.4rem 1rem 0.4rem 0;
    font-size: 0.8em;
    color: #57606a;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 2px solid #d0d7de;
  }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>SpecterX KB Articles</h1>
  <p style="color:#57606a;margin:0.5rem 0 0.25rem;">
    {"".join(stat_items)}
  </p>
  <table>
    <thead>
      <tr>
        <th style="padding:0.4rem 1rem 0.4rem 0;">#</th>
        <th style="padding:0.4rem 1rem;">Article</th>
        <th style="padding:0.4rem 1rem;">Status</th>
        <th style="padding:0.4rem 0;">Links</th>
      </tr>
    </thead>
    <tbody>
{rows}    </tbody>
  </table>
</div>
</body>
</html>
"""


def main() -> int:
    articles = collect_articles()
    if not articles:
        print("No articles found — nothing to index.")
        return 0
    page = build(articles)
    OUT.write_text(page, encoding="utf-8")
    print(f"Written: {OUT}  ({len(articles)} articles)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
