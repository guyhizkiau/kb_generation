"""Shared helpers for pr-watcher unit tests."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any
from unittest import mock


def load_pr_watcher_module(repo_root: Path | None = None):
    """Load pr-watcher.py as a module (hyphenated filename)."""
    script_dir = Path(__file__).resolve().parent
    if repo_root is not None:
        os.environ["KB_REPO_ROOT"] = str(repo_root)
    spec = importlib.util.spec_from_file_location(
        "pr_watcher",
        script_dir / "pr-watcher.py",
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pr_watcher"] = mod
    spec.loader.exec_module(mod)
    return mod


def make_fixture_repo() -> tuple[tempfile.TemporaryDirectory, Path]:
    """Create a temp repo with queue.json and one article STATE."""
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    q = {
        "version": 1,
        "clusters": [{
            "id": "01-login",
            "title": "Login",
            "mode": "serial",
            "status": "active",
            "pause_after": True,
            "articles": [
                {"slug": "01-log-in-to-specterx", "title": "Log in"},
                {"slug": "02-set-or-reset-password", "title": "Reset"},
            ],
        }],
    }
    (root / "clusters").mkdir(parents=True)
    (root / "clusters" / "queue.json").write_text(json.dumps(q))
    art = root / "articles" / "01-log-in-to-specterx"
    art.mkdir(parents=True)
    (art / "STATE").write_text("PHASE=MERGED\nREVISION_CYCLE=0\n")
    return tmp, root


def patch_vm_paths(pw: Any, root: Path) -> None:
    """Point pr-watcher VM paths at the temp fixture."""
    pw.REPO_PATH = root
    pw.STATE_FILE = root / "state.json"
    pw.LOG_FILE = root / "watcher.log"
    pw.TASK_LOG_FILE = root / "task.log"
    pw.STATUS_DIR = root / "status"
    pw.STATUS_DIR.mkdir(exist_ok=True)
    os.environ["KB_REPO_ROOT"] = str(root)
