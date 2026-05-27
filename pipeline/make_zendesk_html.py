"""
pipeline/make_zendesk_html.py
Convert {slug}.html → {slug}-zendesk.html (body-only, inline-styled).

ZenDesk strips <head> and <style> blocks on import, so articles need a
second export that carries all styling via inline style= attributes.

Usage:
    python3 pipeline/make_zendesk_html.py articles/NN-slug/
    # reads  articles/NN-slug/NN-slug.html
    # writes articles/NN-slug/NN-slug-zendesk.html

NOTE: pipeline/render_html.py generates both files in one step.
This script exists for standalone re-export when only the ZenDesk
file needs to be regenerated.

See WORKFLOW.md §9.3b for the full specification.
"""
import re, sys, os


# ── Inline style values ────────────────────────────────────────────────────

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


def make_zendesk(article_dir: str) -> None:
    slug = os.path.basename(os.path.normpath(article_dir))
    src  = os.path.join(article_dir, f"{slug}.html")
    dest = os.path.join(article_dir, f"{slug}-zendesk.html")

    with open(src, "r", encoding="utf-8") as f:
        raw = f.read()

    # 1. Extract content inside <main>…</main>
    m = re.search(r"<main[^>]*>(.*?)</main>", raw, re.DOTALL)
    if not m:
        raise ValueError(f"No <main> tag found in {src}")
    body = m.group(1).strip()

    # 2. .meta div → inline style
    body = re.sub(r'<div\s+class="meta">', f'<div style="{META_STYLE}">', body)

    # 3. figure.screenshot → inline style
    body = re.sub(r'<figure\s+class="screenshot">', f'<figure style="{FIGURE_STYLE}">', body)

    # 4. All <img> tags get border/shadow style
    body = re.sub(r'<img\b', f'<img style="{IMG_STYLE}"', body)

    # 5. <figcaption> inline style
    body = re.sub(r'<figcaption>', f'<figcaption style="{FIGCAPTION_STYLE}">', body)

    # 6. <blockquote> inline style
    body = re.sub(r'<blockquote>', f'<blockquote style="{BLOCKQUOTE_STYLE}">', body)

    # 7. <p>---</p> → <hr>
    body = re.sub(r'<p>\s*---\s*</p>', f'<hr style="{HR_STYLE}">', body)

    # 8. Strip any remaining class="…" attributes (safety net)
    body = re.sub(r'\s*class="[^"]*"', "", body)

    with open(dest, "w", encoding="utf-8") as f:
        f.write(body)
        f.write("\n")

    size_kb = len(body) // 1024
    print(f"Written: {dest}  ({size_kb} KB)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    make_zendesk(sys.argv[1])
