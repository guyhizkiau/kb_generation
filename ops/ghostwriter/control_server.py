#!/usr/bin/env python3
"""
Standalone pr-watcher control plane for local Ghostwriter development.

Starts only the REST control handler from pr-watcher.py on port 9191 — no
GitHub polling, no Claude launches. Queue reads/writes use the real repo
clusters/queue.json and articles/*/STATE. Annotations live in
.ghostwriter/feedback/<slug>.json (branch-independent).

Usage (from repo root):

    python ops/ghostwriter/control_server.py

Environment:
    KB_REPO_ROOT              — repo root (defaults to auto-detected)
    GHOSTWRITER_FEEDBACK_DIR  — annotation store (default .ghostwriter/feedback/)
    CONTROL_PORT              — listen port (default 9191)
"""

from __future__ import annotations

import importlib.util
import os
import sys
import threading
from http.server import HTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PR_WATCHER_SCRIPT = REPO_ROOT / "ops" / "pr-watcher" / "pr-watcher.py"
DEFAULT_PORT = 9191


def _load_pr_watcher():
    os.environ.setdefault("KB_REPO_ROOT", str(REPO_ROOT))
    os.environ.setdefault("GHOSTWRITER_NO_SUDO", "1")
    os.environ.setdefault(
        "GHOSTWRITER_FEEDBACK_DIR",
        str(REPO_ROOT / ".ghostwriter" / "feedback"),
    )
    spec = importlib.util.spec_from_file_location("pr_watcher", PR_WATCHER_SCRIPT)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot load {PR_WATCHER_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pr_watcher"] = mod
    spec.loader.exec_module(mod)
    mod.REPO_PATH = REPO_ROOT
    mod.WORKTREE_PATH = REPO_ROOT / ".ghostwriter" / "worktree"
    mod.STATE_FILE = REPO_ROOT / ".ghostwriter-local-state.json"
    mod.LOG_FILE = REPO_ROOT / ".ghostwriter-local-watcher.log"
    mod.TASK_LOG_FILE = REPO_ROOT / ".ghostwriter-local-task.log"
    mod.STATUS_DIR = REPO_ROOT / ".ghostwriter-local-status"
    mod.STATUS_DIR.mkdir(exist_ok=True)
    if not mod.STATE_FILE.exists():
        mod.STATE_FILE.write_text('{"handled":[],"failed_comments":{}}', encoding="utf-8")
    return mod


def main() -> None:
    pw = _load_pr_watcher()
    pw._start_fetch_thread()
    port = int(os.environ.get("CONTROL_PORT", str(DEFAULT_PORT)))
    server = HTTPServer(("127.0.0.1", port), pw._ControlHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print("Ghostwriter control server (queue API only — no daemon poll loop)")
    print(f"  Repo:     {REPO_ROOT}")
    print(f"  Feedback: {os.environ.get('GHOSTWRITER_FEEDBACK_DIR')}")
    print(f"  Worktree: {pw.WORKTREE_PATH} (lazy — created on first daemon edit)")
    print(f"  Listen:   http://127.0.0.1:{port}/")
    print("  Routes: GET/PUT /api/queue  POST /api/queue/trigger  POST /api/queue/merge")
    print("          GET /api/feedback  POST /api/feedback")
    print("          GET /api/articles/{slug}/preview")
    print("          POST /poll-now  POST /retry")
    print("  Press Ctrl+C to stop.")
    try:
        thread.join()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
