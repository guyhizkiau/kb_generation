"""Transform stored article HTML for Ghostwriter preview + inline commenting."""
from __future__ import annotations

import re
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
    import json

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
    """Return preview HTML path, rendering from final.md on demand if needed."""
    article_dir = repo_root / "articles" / slug
    html_path = article_dir / f"{slug}.html"
    if html_path.exists():
        return html_path
    if not article_dir.is_dir():
        return None

    if not _prepare_final_md_for_render(article_dir):
        return None

    return _run_render(repo_root, article_dir, html_path)


def _prepare_final_md_for_render(article_dir: Path) -> bool:
    """Ensure article_dir/final.md exists (copy latest draft if needed)."""
    final_md = article_dir / "final.md"
    if final_md.exists():
        return True
    slug = article_dir.name
    draft_re = re.compile(rf"^draft-(\d+)\.md$")
    drafts: list[tuple[int, Path]] = []
    for path in article_dir.iterdir():
        if not path.is_file():
            continue
        m = draft_re.match(path.name)
        if m:
            drafts.append((int(m.group(1)), path))
    if not drafts:
        return False
    drafts.sort(key=lambda item: item[0], reverse=True)
    final_md.write_bytes(drafts[0][1].read_bytes())
    return True


def _run_render(repo_root: Path, article_dir: Path, html_path: Path) -> Path | None:
    import subprocess

    render_script = repo_root / "pipeline" / "render_html.py"
    if not render_script.exists():
        return None
    result = subprocess.run(
        [sys.executable, str(render_script), str(article_dir)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
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


def resolve_preview_html(repo_root: Path, slug: str, origin: str) -> tuple[int, str]:
    """Serve preview from the working tree."""
    return load_preview_html(repo_root, slug, origin)
