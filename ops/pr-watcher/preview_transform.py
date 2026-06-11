"""Transform stored article HTML for Ghostwriter preview + inline commenting."""
from __future__ import annotations

import os
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

_DRAFT_RE = re.compile(r"^draft-(\d+)\.md$")
_TOOLING_ROOT = Path(__file__).resolve().parents[2]


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


def _preview_cache_dir(repo_root: Path) -> Path:
    env = os.environ.get("GHOSTWRITER_PREVIEW_CACHE")
    if env:
        return Path(env)
    return Path.home() / ".cache" / "ghostwriter-preview"


def select_preview_source(article_dir: Path) -> Path | None:
    """Pick markdown source for preview: final.md, else latest draft-N.md."""
    final_md = article_dir / "final.md"
    if final_md.is_file():
        return final_md

    drafts: list[tuple[int, Path]] = []
    for path in article_dir.iterdir():
        if not path.is_file():
            continue
        match = _DRAFT_RE.match(path.name)
        if match:
            drafts.append((int(match.group(1)), path))
    if not drafts:
        return None
    drafts.sort(key=lambda item: item[0], reverse=True)
    return drafts[0][1]


def _is_fresh(html_path: Path, source_md: Path) -> bool:
    return html_path.is_file() and html_path.stat().st_mtime >= source_md.stat().st_mtime


def _run_render_to_cache(
    repo_root: Path,
    article_dir: Path,
    source_md: Path,
    cache_dir: Path,
    slug: str,
) -> Path | None:
    import subprocess

    render_script = _TOOLING_ROOT / "pipeline" / "render_html.py"
    if not render_script.exists():
        return None

    cache_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            sys.executable,
            str(render_script),
            str(article_dir),
            "--source",
            str(source_md),
            "--out-dir",
            str(cache_dir),
        ],
        cwd=_TOOLING_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None

    html_path = cache_dir / f"{slug}.html"
    return html_path if html_path.is_file() else None


def ensure_article_html(repo_root: Path, slug: str) -> Path | None:
    """Return preview HTML path without writing inside the article directory."""
    article_dir = repo_root / "articles" / slug
    if not article_dir.is_dir():
        return None

    in_tree_html = article_dir / f"{slug}.html"
    if in_tree_html.is_file():
        return in_tree_html

    source_md = select_preview_source(article_dir)
    if source_md is None:
        return None

    cache_dir = _preview_cache_dir(repo_root)
    cached_html = cache_dir / f"{slug}.html"
    if _is_fresh(cached_html, source_md):
        return cached_html

    return _run_render_to_cache(repo_root, article_dir, source_md, cache_dir, slug)


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
