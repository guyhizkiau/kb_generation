"""pipeline/render_html.py
Generic Markdown-to-HTML renderer for KB articles.

Usage:
    python3 pipeline/render_html.py articles/NN-slug/

Reads:   articles/NN-slug/final.md
Writes:  articles/NN-slug/NN-slug.html          (standalone preview)
         articles/NN-slug/NN-slug-zendesk.html  (body-only, inline-styled)

The output filename is derived from the directory name (the slug), so
every article gets a unique, recognisable filename instead of the generic
"article.html". Both files are written; run just this script and you have
everything you need.

See WORKFLOW.md §9.3 and §9.3b for the full spec.
"""

from __future__ import annotations

import base64
import html
import mimetypes
import re
import sys
from pathlib import Path


# ── Inline-style constants for the ZenDesk export ────────────────────────────

META_STYLE = (
    "font-size:0.875em;"
    "color:#57606a;"
    "margin:0.25rem 0 1.5rem;"
    "padding:0.5rem 0.75rem;"
    "background:#f6f8fa;"
    "border-radius:4px;"
    "border-left:3px solid #d0d7de;"
)
FIGURE_STYLE = "margin:1.5rem 0;padding:0;text-align:center;"
IMG_STYLE = (
    "max-width:100%;"
    "height:auto;"
    "border:1px solid #d0d7de;"
    "border-radius:6px;"
    "box-shadow:0 1px 4px rgba(0,0,0,.06);"
    "display:block;"
    "margin:0 auto;"
)
FIGCAPTION_STYLE = "font-size:0.85em;color:#57606a;margin-top:0.4rem;"
BLOCKQUOTE_STYLE = (
    "border-left:4px solid #d0d7de;"
    "margin:1rem 0;"
    "padding:0.25rem 1rem;"
    "color:#57606a;"
    "background:#f6f8fa;"
)
HR_STYLE = "border:none;border-top:1px solid #d0d7de;margin:2rem 0;"


# ── CSS for standalone preview ────────────────────────────────────────────────

CSS = """
  :root { color-scheme: light; }
  html, body { margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    color: #1f2328;
    background: #f6f8fa;
    line-height: 1.6;
    font-size: 16px;
  }
  main {
    max-width: 800px;
    margin: 0 auto;
    padding: 48px 32px 96px;
    background: #ffffff;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    min-height: 100vh;
  }
  h1 {
    font-size: 2rem;
    line-height: 1.2;
    margin: 0 0 0.5rem;
    border-bottom: 1px solid #d0d7de;
    padding-bottom: 0.4rem;
  }
  h2 {
    font-size: 1.4rem;
    margin: 2rem 0 0.75rem;
    border-bottom: 1px solid #eaeef2;
    padding-bottom: 0.3rem;
  }
  h3 { font-size: 1.15rem; margin: 1.6rem 0 0.5rem; }
  p { margin: 0.75rem 0; }
  ul { padding-left: 1.4rem; }
  li { margin: 0.25rem 0; }
  code {
    font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas,
                 "Liberation Mono", monospace;
    background: #f0f3f6;
    padding: 0.1em 0.35em;
    border-radius: 4px;
    font-size: 0.92em;
  }
  blockquote {
    border-left: 4px solid #d0d7de;
    margin: 1rem 0;
    padding: 0.25rem 1rem;
    color: #57606a;
    background: #f6f8fa;
  }
  figure.screenshot {
    margin: 1.25rem 0;
    padding: 0;
    text-align: center;
  }
  figure.screenshot img {
    max-width: 100%;
    height: auto;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .meta {
    font-size: 0.875em;
    color: #57606a;
    margin: 0.25rem 0 1.5rem;
    padding: 0.5rem 0.75rem;
    background: #f6f8fa;
    border-radius: 4px;
    border-left: 3px solid #d0d7de;
  }
  hr {
    border: none;
    border-top: 1px solid #d0d7de;
    margin: 2rem 0;
  }
"""


# ── Front-matter parser ───────────────────────────────────────────────────────

def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_raw = text[4:end]
    body = text[end + 5:]
    fm: dict[str, object] = {}
    cur_list_key: str | None = None
    for line in fm_raw.splitlines():
        if not line.strip():
            cur_list_key = None
            continue
        if line.startswith("  - ") and cur_list_key:
            fm.setdefault(cur_list_key, []).append(line[4:].strip())  # type: ignore
            continue
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            v = v.strip()
            if v == "":
                cur_list_key = k.strip()
                fm[cur_list_key] = []
            else:
                fm[k.strip()] = v
                cur_list_key = None
    return fm, body


# ── Inline Markdown renderer ──────────────────────────────────────────────────

_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_EM_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def _embed_image(article_dir: Path, src: str) -> str:
    p = (article_dir / src).resolve()
    if not p.is_file():
        return src
    mime, _ = mimetypes.guess_type(str(p))
    mime = mime or "application/octet-stream"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def render_inline(text: str, article_dir: Path) -> str:
    placeholders: dict[str, str] = {}

    def img_sub(m: re.Match) -> str:
        alt = m.group(1).strip()
        src = m.group(2).strip()
        data = _embed_image(article_dir, src)
        key = f"@@IMG{len(placeholders)}@@"
        placeholders[key] = (
            f'<figure class="screenshot">'
            f'<img src="{html.escape(data, quote=True)}" '
            f'alt="{html.escape(alt, quote=True)}">'
            f"</figure>"
        )
        return key

    text = _IMG_RE.sub(img_sub, text)

    def code_sub(m: re.Match) -> str:
        key = f"@@CODE{len(placeholders)}@@"
        placeholders[key] = f"<code>{html.escape(m.group(1))}</code>"
        return key

    text = _CODE_RE.sub(code_sub, text)
    text = html.escape(text, quote=False)
    text = _BOLD_RE.sub(lambda m: f"<strong>{m.group(1)}</strong>", text)
    text = _EM_RE.sub(lambda m: f"<em>{m.group(1)}</em>", text)

    def link_sub(m: re.Match) -> str:
        label = m.group(1)
        href = m.group(2)
        return f'<a href="{html.escape(href, quote=True)}">{label}</a>'

    text = _LINK_RE.sub(link_sub, text)

    for key, repl in placeholders.items():
        text = text.replace(html.escape(key, quote=False), repl).replace(key, repl)
    return text


# ── Block Markdown renderer ───────────────────────────────────────────────────

def render_blocks(body: str, article_dir: Path) -> str:
    lines = body.splitlines()
    out: list[str] = []
    i = 0
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            joined = " ".join(paragraph).strip()
            if joined:
                out.append(f"<p>{render_inline(joined, article_dir)}</p>")
            paragraph.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            i += 1
            continue

        # Headings
        h_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if h_match:
            flush_paragraph()
            level = len(h_match.group(1))
            text = h_match.group(2)
            out.append(f"<h{level}>{render_inline(text, article_dir)}</h{level}>")
            i += 1
            continue

        # Horizontal rule --- (bare, not in a paragraph)
        if stripped == "---":
            flush_paragraph()
            out.append("<hr>")
            i += 1
            continue

        # Image-only line → block figure
        if _IMG_RE.fullmatch(stripped):
            flush_paragraph()
            out.append(render_inline(stripped, article_dir))
            i += 1
            continue

        # Unordered list
        if re.match(r"^[-*]\s+", stripped):
            flush_paragraph()
            items: list[str] = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                item_text = re.sub(r"^[-*]\s+", "", lines[i].strip())
                items.append(f"<li>{render_inline(item_text, article_dir)}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue

        # Blockquote
        if stripped.startswith(">"):
            flush_paragraph()
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            out.append(
                "<blockquote>"
                + render_inline(" ".join(quote_lines), article_dir)
                + "</blockquote>"
            )
            continue

        paragraph.append(stripped)
        i += 1

    flush_paragraph()
    return "\n".join(out)


# ── Meta bar ──────────────────────────────────────────────────────────────────

def render_meta(fm: dict) -> str:
    """Render audience + reading-time meta bar.
    Prerequisites are NOT included here — they live in the article body only.
    """
    aud = fm.get("audience")
    est = fm.get("estimated-reading-time")
    bits = []
    if aud:
        bits.append(f"Audience: <strong>{html.escape(str(aud))}</strong>")
    if est:
        bits.append(f"Reading time: <strong>{html.escape(str(est))}</strong>")
    if not bits:
        return ""
    return '<div class="meta"><p>' + " &middot; ".join(bits) + "</p></div>"


# ── ZenDesk export ────────────────────────────────────────────────────────────

def make_zendesk_body(main_html: str) -> str:
    """Convert the <main> inner HTML to ZenDesk-compatible body-only HTML.

    Replaces CSS classes with inline style= attributes and strips the
    <head>/<style> wrapper so ZenDesk can import it without losing styling.
    """
    body = main_html

    body = re.sub(r'<div\s+class="meta">', f'<div style="{META_STYLE}">', body)
    body = re.sub(r'<figure\s+class="screenshot">', f'<figure style="{FIGURE_STYLE}">', body)
    body = re.sub(r'<img\b', f'<img style="{IMG_STYLE}"', body)
    body = re.sub(r'<figcaption>', f'<figcaption style="{FIGCAPTION_STYLE}">', body)
    body = re.sub(r'<blockquote>', f'<blockquote style="{BLOCKQUOTE_STYLE}">', body)
    body = re.sub(r'<p>\s*---\s*</p>', f'<hr style="{HR_STYLE}">', body)
    body = re.sub(r'<hr>', f'<hr style="{HR_STYLE}">', body)
    # Strip any remaining class= attributes
    body = re.sub(r'\s*class="[^"]*"', "", body)
    return body


# ── Top-level render ──────────────────────────────────────────────────────────

def render(article_dir: Path) -> tuple[Path, Path]:
    """Render final.md → {slug}.html and {slug}-zendesk.html.

    Returns the paths of both output files.
    """
    slug = article_dir.name
    src = article_dir / "final.md"
    out_preview = article_dir / f"{slug}.html"
    out_zendesk = article_dir / f"{slug}-zendesk.html"

    md = src.read_text(encoding="utf-8")
    fm, body = split_frontmatter(md)
    title = str(fm.get("title", slug))

    body_html = render_blocks(body, article_dir)
    meta_html = render_meta(fm)

    # Layout order: h1 FIRST, then meta bar, then body (WORKFLOW.md §9.3a)
    # The body already contains <h1> as the first element from Markdown.
    # Strip it from body_html and render it explicitly so we control the order.
    h1_match = re.match(r"^<h1>.*?</h1>\n?", body_html)
    if h1_match:
        h1_tag = h1_match.group(0).rstrip("\n")
        body_remainder = body_html[h1_match.end():]
    else:
        h1_tag = f"<h1>{html.escape(title)}</h1>"
        body_remainder = body_html

    main_inner = f"{h1_tag}\n{meta_html}\n{body_remainder}"

    # ── Standalone preview ────────────────────────────────────────────────────
    preview_page = (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        # No <title> — ZenDesk and other CMS platforms re-inject it (WORKFLOW.md §9.3a)
        f"<style>{CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        "<main>\n"
        f"{main_inner}\n"
        "</main>\n"
        "</body>\n"
        "</html>\n"
    )
    out_preview.write_text(preview_page, encoding="utf-8")
    print(f"Preview : {out_preview}  ({len(preview_page) // 1024} KB)")

    # ── ZenDesk export ────────────────────────────────────────────────────────
    zendesk_body = make_zendesk_body(main_inner)
    out_zendesk.write_text(zendesk_body + "\n", encoding="utf-8")
    print(f"ZenDesk : {out_zendesk}  ({len(zendesk_body) // 1024} KB)")

    return out_preview, out_zendesk


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    article_dir = Path(sys.argv[1]).resolve()
    if not article_dir.is_dir():
        print(f"ERROR: {article_dir} is not a directory", file=sys.stderr)
        return 1
    if not (article_dir / "final.md").exists():
        print(f"ERROR: {article_dir}/final.md not found", file=sys.stderr)
        return 1
    render(article_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
