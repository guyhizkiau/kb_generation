"""Transform stored article HTML for Ghostwriter preview + inline commenting."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

_LEGACY_WIDGET_MARKERS = ("postAnnotation", "Recogito.init", "ghostwriter-annotate.js")

_ANNOTATION_HEAD = (
    '<link rel="stylesheet" href="/static/recogito.min.css">\n'
    '<link rel="stylesheet" href="/static/annotorious.min.css">\n'
)

_ANNOTATION_SCRIPTS = (
    '<script src="/static/recogito.min.js"></script>\n'
    '<script src="/static/annotorious.min.js"></script>\n'
)


def strip_legacy_widget_scripts(html: str) -> str:
    """Remove inline annotation widget scripts from stored HTML."""

    def _maybe_strip(match: re.Match[str]) -> str:
        block = match.group(0)
        if any(marker in block for marker in _LEGACY_WIDGET_MARKERS):
            return ""
        return block

    return re.sub(
        r"<script\b[^>]*>.*?</script>",
        _maybe_strip,
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )


def inject_ghostwriter_config(html: str, origin: str) -> str:
    """Inject or replace window.__GHOSTWRITER__ before </head>."""
    cfg = json.dumps({"apiBase": origin, "n8nWebhook": ""})
    script = f"<script>window.__GHOSTWRITER__={cfg};</script>"
    html = re.sub(
        r"<script>window\.__GHOSTWRITER__=.*?</script>\s*",
        "",
        html,
        flags=re.DOTALL,
    )
    if "</head>" in html:
        return html.replace("</head>", f"{script}\n</head>", 1)
    return f"{script}\n{html}"


def ensure_annotation_assets(html: str, slug: str) -> str:
    """Ensure CSS/JS assets and canonical ghostwriter-annotate.js are present."""
    if "recogito.min.css" not in html and "</head>" in html:
        html = html.replace("</head>", f"{_ANNOTATION_HEAD}</head>", 1)

    # Drop stale ghostwriter-annotate tag so slug stays correct.
    html = re.sub(
        r'<script\b[^>]*src="/static/ghostwriter-annotate\.js"[^>]*>\s*</script>\s*',
        "",
        html,
        flags=re.IGNORECASE,
    )

    widget = f'<script src="/static/ghostwriter-annotate.js" data-slug="{slug}"></script>\n'
    body_scripts = _ANNOTATION_SCRIPTS if "recogito.min.js" not in html else ""
    tail = body_scripts + widget

    if "</body>" in html:
        return html.replace("</body>", f"{tail}</body>", 1)
    return html + tail


def patch_article_preview_html(html: str, slug: str, origin: str) -> str:
    """Return HTML ready for iframe preview with working inline commenting."""
    html = strip_legacy_widget_scripts(html)
    html = inject_ghostwriter_config(html, origin)
    return ensure_annotation_assets(html, slug)


def ensure_article_html(repo_root: Path, slug: str) -> Path | None:
    """Return preview HTML path, rendering on demand if needed.

    Source priority: final.md > draft-2.md > draft-1.md.  This allows the
    Ghostwriter to preview articles at any pipeline stage, not just after the
    voice pass.
    """
    article_dir = repo_root / "articles" / slug
    html_path = article_dir / f"{slug}.html"
    if html_path.exists():
        return html_path

    # Find the best available Markdown source.
    source_candidates = ["final.md", "draft-2.md", "draft-1.md"]
    source_md: Path | None = None
    for candidate in source_candidates:
        p = article_dir / candidate
        if p.exists():
            source_md = p
            break

    if source_md is None:
        return None

    render_script = repo_root / "pipeline" / "render_html.py"
    if not render_script.exists():
        return None

    # render_html.py reads final.md; symlink the best source so it can render.
    final_md = article_dir / "final.md"
    created_symlink = False
    if not final_md.exists() and source_md != final_md:
        final_md.symlink_to(source_md.name)
        created_symlink = True

    try:
        result = subprocess.run(
            [sys.executable, str(render_script), str(article_dir)],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
    finally:
        if created_symlink and final_md.is_symlink():
            final_md.unlink()

    if result.returncode != 0:
        return None
    return html_path if html_path.exists() else None


def load_preview_html(repo_root: Path, slug: str, origin: str) -> tuple[int, str]:
    """Ensure HTML exists (auto-render if needed) and return patched preview."""
    html_path = ensure_article_html(repo_root, slug)
    if not html_path:
        return 404, ""
    html = html_path.read_text(encoding="utf-8")
    return 200, patch_article_preview_html(html, slug, origin)
