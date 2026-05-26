"""Render final.md to a self-contained article.html.

- Strips YAML frontmatter
- Converts Markdown to HTML using a small built-in renderer (no extra deps)
- Embeds screenshot files referenced as ![](screenshots/...) as base64
  data URIs so the resulting HTML stands alone
"""

from __future__ import annotations

import base64
import html
import mimetypes
import re
from pathlib import Path

ARTICLE_DIR = Path(__file__).resolve().parent
DRAFT = ARTICLE_DIR / "final.md"
OUT = ARTICLE_DIR / "article.html"


# ---------- frontmatter ----------

def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_raw = text[4:end]
    body = text[end + 5 :]
    fm: dict[str, object] = {}
    cur_list_key: str | None = None
    for line in fm_raw.splitlines():
        if not line.strip():
            cur_list_key = None
            continue
        if line.startswith("  - ") and cur_list_key:
            fm.setdefault(cur_list_key, []).append(line[4:].strip())  # type: ignore[union-attr]
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


# ---------- inline markdown ----------

_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_EM_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def _embed_image(src: str) -> str:
    p = (ARTICLE_DIR / src).resolve()
    if not p.is_file():
        return src  # leave as-is if missing
    mime, _ = mimetypes.guess_type(str(p))
    mime = mime or "application/octet-stream"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def render_inline(text: str) -> str:
    # Image tokens first — they share `[...](...)` shape with links.
    placeholders: dict[str, str] = {}

    def img_sub(m: re.Match) -> str:
        alt = m.group(1).strip()
        src = m.group(2).strip()
        data = _embed_image(src)
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


# ---------- block parser ----------

def render_blocks(body: str) -> str:
    lines = body.splitlines()
    out: list[str] = []
    i = 0
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            joined = " ".join(paragraph).strip()
            if joined:
                out.append(f"<p>{render_inline(joined)}</p>")
            paragraph.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            i += 1
            continue

        h_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if h_match:
            flush_paragraph()
            level = len(h_match.group(1))
            text = h_match.group(2)
            out.append(f"<h{level}>{render_inline(text)}</h{level}>")
            i += 1
            continue

        # Image-only line — render as block
        if _IMG_RE.fullmatch(stripped):
            flush_paragraph()
            out.append(render_inline(stripped))
            i += 1
            continue

        # Unordered list
        if re.match(r"^[-*]\s+", stripped):
            flush_paragraph()
            items: list[str] = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                item_text = re.sub(r"^[-*]\s+", "", lines[i].strip())
                items.append(f"<li>{render_inline(item_text)}</li>")
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
            out.append("<blockquote>" + render_inline(" ".join(quote_lines)) + "</blockquote>")
            continue

        paragraph.append(stripped)
        i += 1

    flush_paragraph()
    return "\n".join(out)


# ---------- top-level ----------

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
  h3 {
    font-size: 1.15rem;
    margin: 1.6rem 0 0.5rem;
  }
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
    font-size: 0.9rem;
    color: #57606a;
    margin-bottom: 1.5rem;
  }
  .meta ul { list-style: none; padding: 0; margin: 0.25rem 0 0; }
  .meta li { margin: 0; }
"""


def render_meta(fm: dict) -> str:
    if not fm:
        return ""
    parts = ['<div class="meta">']
    aud = fm.get("audience")
    est = fm.get("estimated-reading-time")
    bits = []
    if aud:
        bits.append(f"Audience: <strong>{html.escape(str(aud))}</strong>")
    if est:
        bits.append(f"Reading time: <strong>{html.escape(str(est))}</strong>")
    if bits:
        parts.append("<p>" + " &middot; ".join(bits) + "</p>")
    prereqs = fm.get("prerequisites")
    if isinstance(prereqs, list) and prereqs:
        parts.append("<p><strong>Prerequisites</strong></p><ul>")
        for it in prereqs:
            parts.append(f"<li>{html.escape(str(it))}</li>")
        parts.append("</ul>")
    parts.append("</div>")
    return "\n".join(parts)


def main() -> int:
    md = DRAFT.read_text(encoding="utf-8")
    fm, body = split_frontmatter(md)
    title = str(fm.get("title", "Article"))

    body_html = render_blocks(body)
    meta_html = render_meta(fm)

    page = (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f"<style>{CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        "<main>\n"
        f"{meta_html}\n"
        f"{body_html}\n"
        "</main>\n"
        "</body>\n"
        "</html>\n"
    )
    OUT.write_text(page, encoding="utf-8")
    print(str(OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
