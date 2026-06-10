"""Pluggable publish adapters — save adapter renders HTML and rebuilds index."""
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from store.machine import current_phase, transition  # noqa: E402
from store.paths import article_dir, repo_root  # noqa: E402
from store.state import read_state  # noqa: E402


@dataclass
class PublishResult:
    ok: bool
    adapter: str
    outputs: list[str] = field(default_factory=list)
    error: str | None = None


class PublishAdapter(Protocol):
    name: str

    def publish(self, slug: str, article_dir: Path) -> PublishResult: ...


class SaveAdapter:
    """Render final.md and rebuild articles/index.html."""

    name = "save"

    def publish(self, slug: str, adir: Path) -> PublishResult:
        outputs: list[str] = []
        try:
            subprocess.run(
                [sys.executable, str(REPO_ROOT / "pipeline" / "render_html.py"), str(adir)],
                cwd=str(repo_root()),
                check=True,
                capture_output=True,
                text=True,
            )
            outputs.append(f"articles/{slug}/{slug}.html")
            outputs.append(f"articles/{slug}/{slug}-zendesk.html")

            subprocess.run(
                [sys.executable, str(REPO_ROOT / "pipeline" / "build_index.py")],
                cwd=str(repo_root()),
                check=True,
                capture_output=True,
                text=True,
            )
            outputs.append("articles/index.html")
        except subprocess.CalledProcessError as exc:
            return PublishResult(
                ok=False, adapter=self.name, error=exc.stderr or str(exc),
            )
        return PublishResult(ok=True, adapter=self.name, outputs=outputs)


_ADAPTERS: dict[str, type[SaveAdapter]] = {
    "save": SaveAdapter,
}


def get_adapter(name: str | None = None) -> PublishAdapter:
    adapter_name = name or os.environ.get("KB_PUBLISH_ADAPTER", "save")
    cls = _ADAPTERS.get(adapter_name)
    if cls is None:
        raise ValueError(f"unknown publish adapter: {adapter_name}")
    return cls()


def publish_article(slug: str) -> PublishResult:
    """Publish an approved article via the configured adapter."""
    if current_phase(slug) != "APPROVED":
        return PublishResult(ok=False, adapter="none", error="not approved")

    adir = article_dir(slug)
    adapter = get_adapter()
    result = adapter.publish(slug, adir)
    if not result.ok:
        return result

    fields = read_state(slug)
    extra: dict[str, str] = {"NEXT_ACTION": ""}
    try:
        rc = int(fields.get("REVISION_CYCLE", "0"))
    except ValueError:
        rc = 0
    if rc > 0:
        extra["PUBLISH_STALE"] = "true"

    transition(slug, "PUBLISHED", extra=extra)
    return result
