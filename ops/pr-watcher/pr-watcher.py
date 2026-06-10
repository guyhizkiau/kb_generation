#!/usr/bin/env python3
"""
pr-watcher.py — article pipeline daemon + Ghostwriter control plane

Polls the queue on a fixed interval, dispatches pipeline phases via the
state machine, and serves the Ghostwriter HTTP API (approve, publish,
request-changes, feedback, preview).
"""
import subprocess, json, os, time, re, threading, tempfile, sys, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from datetime import datetime, timezone

REPO          = "guyhizkiau/kb_generation"
REPO_PATH     = Path("/home/ubuntu/kb_generation")
WORKTREE_PATH = Path("/home/ubuntu/kb_generation-work")
STATE_FILE    = Path("/home/ubuntu/pr-watcher-state.json")
LOG_FILE      = Path("/home/ubuntu/pr-watcher.log")
TASK_LOG_FILE = Path("/home/ubuntu/pr-watcher-task.log")   # live Claude output, overwritten per task
STATUS_DIR    = Path("/home/ubuntu/pr-watcher-web")
POLL_INTERVAL = 30    # seconds between polls
CLAUDE_BIN    = "/usr/local/bin/claude"
PREVIEW_BASE  = "http://18.192.122.48"   # nginx article browser (port 80)
CONTROL_PORT      = 9191  # localhost-only HTTP control plane

# Prepend script directory so queue_store.py is importable when deployed
# to /home/ubuntu/ (outside the repo tree).
_script_dir = Path(__file__).resolve().parent
_repo_root = REPO_PATH  # fixed: was _script_dir.parent.parent, broken when deployed outside repo tree
sys.path.insert(0, str(_script_dir))
if str(REPO_PATH) not in sys.path:
    sys.path.insert(0, str(REPO_PATH))
os.environ.setdefault("KB_REPO_ROOT", str(REPO_PATH))
_vm_repo = "/home/ubuntu/kb_generation"
if os.environ.get("KB_REPO_ROOT") == _vm_repo and Path(_vm_repo).exists():
    os.environ.setdefault("GHOSTWRITER_FEEDBACK_DIR", "/home/ubuntu/ghostwriter-feedback")
try:
    import queue_store as _qs
    import feedback_store as _fb
    from preview_transform import resolve_preview_html
    import dispatcher as _dispatcher
    from store import machine as _machine
    from pipeline import publish as _publish
    _QUEUE_STORE_AVAILABLE = True
except ImportError:
    _dispatcher = None  # type: ignore[assignment]
    _machine = None  # type: ignore[assignment]
    _publish = None  # type: ignore[assignment]
    _qs = None  # type: ignore[assignment]
    _fb = None  # type: ignore[assignment]
    resolve_preview_html = None  # type: ignore[assignment,misc]
    _QUEUE_STORE_AVAILABLE = False


# Event set by the control plane to trigger an immediate poll
_poll_now = threading.Event()

# Queue source of truth: clusters/queue.json (managed by queue_store)
# CLUSTER_1_ARTICLES removed — use queue_store.load_queue() instead

_queue_lock = threading.Lock()
_manual_trigger_set: list[dict] = []   # items: {slug, reason, issue}

# Slug of the article the daemon is currently writing (in-memory; reset each
# start). Drives the per-article live "running" indicator in the dashboard.
_active_article_slug: str | None = None
_active_article_since: float = 0.0


# ── helpers ───────────────────────────────────────────────────────────────────

def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    # stdout is redirected to LOG_FILE via nohup; file write below is the only write
    with LOG_FILE.open("a") as fh:
        fh.write(line + "\n")


def load_state() -> dict:
    if STATE_FILE.exists():
        d = json.loads(STATE_FILE.read_text())
        d.setdefault("failed_comments", {})
        return d
    return {"handled": [], "failed_comments": {}}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ── runtime state (in-memory, reset each start) ───────────────────────────────

_runtime: dict = {
    "started_at": None,
    "pid": os.getpid(),
    "current_task": None,
    "last_error": None,     # {message, at}
    "last_task_duration_secs": None,
}

_status_cache: dict = {}   # keys: state, iteration, next_poll_at


def flush_status():
    """Write status.json immediately using the latest cached poll args."""
    if _status_cache:
        write_status(
            _status_cache["state"],
            _status_cache["iteration"],
            _status_cache["next_poll_at"],
        )


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_status(state: dict, iteration: int, next_poll_at: float) -> None:
    """Atomically write status.json to STATUS_DIR for the dashboard."""
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    handled = state.get("handled", [])
    payload = {
        "daemon": {
            "started_at": _runtime["started_at"],
            "pid": _runtime["pid"],
            "poll_interval": POLL_INTERVAL,
        },
        "last_poll_at": _now_iso(),
        "poll_number": iteration,
        "next_poll_at": datetime.fromtimestamp(next_poll_at, tz=timezone.utc)
                                .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "open_prs": [],
        "current_task": _runtime["current_task"],
        "last_error": _runtime["last_error"],
        "last_task_duration_secs": _runtime["last_task_duration_secs"],
        "failed_comments": [],
        "counters": {
            "comments_resolved": 0,
            "articles_triggered": sum(1 for h in handled if h.startswith("article-triggered-")),
            "merges_handled": 0,
            "previews_posted": 0,
        },
        "recent_log": _tail_log(200),
        "task_log": _tail_log_file(TASK_LOG_FILE, 200),
        **_latest_phase_log(300),
    }
    dest = STATUS_DIR / "status.json"
    tmp = dest.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2))
    os.replace(tmp, dest)


def _tail_log(n: int) -> list[str]:
    return _tail_log_file(LOG_FILE, n)


def _tail_log_file(path: Path, n: int) -> list[str]:
    try:
        lines = path.read_text(errors="replace").splitlines()
        return lines[-n:]
    except Exception:
        return []


def _latest_phase_log(n: int) -> dict:
    """Return the tail of the most recently modified <slug>-<phase>.log file.

    These are written by _launch_phase for each article phase run (e.g.
    04-share-a-file-revise-from-feedback.log).  The pr-watcher.log and
    pr-watcher-task.log files are excluded.
    """
    excluded = {LOG_FILE.name, TASK_LOG_FILE.name}
    import glob as _glob
    candidates = [
        Path(p) for p in _glob.glob("/home/ubuntu/*-*.log")
        if Path(p).name not in excluded
    ]
    if not candidates:
        return {"phase_log": [], "phase_log_source": ""}
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    return {
        "phase_log": _tail_log_file(latest, n),
        "phase_log_source": latest.name,
    }


def git(*args, check=True):
    """Run git in the serving tree (always on main)."""
    return _run_git(args, REPO_PATH, check=check)


def git_worktree(*args, check=True):
    """Run git in the daemon worktree (branch checkouts / commits)."""
    ensure_worktree()
    return _run_git(args, WORKTREE_PATH, check=check)


def _run_git(args, cwd: Path, check=True):
    cmd = ["git", *args]
    if os.environ.get("GHOSTWRITER_NO_SUDO") != "1":
        cmd = ["sudo", "-u", "ubuntu", *cmd]
    r = subprocess.run(
        cmd,
        cwd=str(cwd), capture_output=True, text=True,
    )
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{r.stderr.strip()}")
    return r.stdout.strip()


def ensure_worktree() -> Path:
    """Ensure WORKTREE_PATH exists as a git worktree rooted at main."""
    if (WORKTREE_PATH / ".git").exists():
        return WORKTREE_PATH
    WORKTREE_PATH.parent.mkdir(parents=True, exist_ok=True)
    git("worktree", "add", str(WORKTREE_PATH), "main")
    return WORKTREE_PATH


def _fetch_all_repos():
    """Refresh remote refs on main."""
    git("fetch", "--all", check=False)


def is_claude_running() -> bool:
    """Return True if a claude process is already running on the VM."""
    for pattern in (r"claude.*--dangerously", r"claude.*-p", r"run_claude_code\.py"):
        r = subprocess.run(["pgrep", "-f", pattern], capture_output=True)
        if r.returncode == 0:
            return True
    return False


# ── phase launcher ────────────────────────────────────────────────────────────


def _launch_phase(slug: str, phase: str):
    """Launch a specific pipeline phase for an article (detached)."""
    # Extra bash tool allowances beyond run_claude_code.py's global baseline.
    # revise-from-feedback needs git to commit its changes.  We pass these here
    # so the shell script carries the right permissions regardless of which
    # version of run_claude_code.py is checked out in the worktree.
    PHASE_EXTRA_ALLOW: dict[str, list[str]] = {
        # Research needs Playwright (venv python) for competitor scraping
        # and UI recon — without it the three-competitor gate blocks.
        "research": [
            "Bash(python3 *)",
            "Bash(python *)",
        ],
        "revise-from-feedback": [
            "Bash(python3 *)",
            "Bash(python *)",
            "Bash(git *)",
        ],
    }
    extra_allow_flags = " ".join(
        f"--allow '{a}'" for a in PHASE_EXTRA_ALLOW.get(phase, [])
    )

    fb_path = str(_fb.feedback_path(slug)) if _fb else f"articles/{slug}/feedback.json"

    # Pre-launch shell commands that run BEFORE Claude, after the worktree is
    # ready.  For revise-from-feedback: snapshot the annotation IDs currently
    # in the store so the post-success step can do a selective clear rather
    # than wiping the whole store (which would destroy annotations added while
    # Claude was running).
    PHASE_PRE_LAUNCH: dict[str, str] = {
        "revise-from-feedback": (
            f"python3 << 'PYEOF'\n"
            f"import json, pathlib\n"
            f"p = pathlib.Path('{fb_path}')\n"
            f"ids = [a.get('id','') for a in (json.loads(p.read_text()) if p.exists() else []) if a.get('id')]\n"
            f"pathlib.Path('/home/ubuntu/.{slug}-fb-snapshot.json').write_text(json.dumps(ids))\n"
            f"PYEOF\n"
        ),
    }
    pre_launch = PHASE_PRE_LAUNCH.get(phase, "")

    # Post-success shell commands appended after the phase exits 0.
    # For revise-from-feedback: selectively clear only the annotations that
    # were present at launch (preserving any added during the run), then push
    # Claude's commit(s) to the remote branch.
    PHASE_POST_SUCCESS: dict[str, str] = {
        "revise-from-feedback": (
            f'echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] clearing handled feedback"'
            f" >> /home/ubuntu/{slug}-{phase}.log\n"
            f"python3 << 'PYEOF'\n"
            f"import json, pathlib\n"
            f"fb = pathlib.Path('{fb_path}')\n"
            f"snap_file = pathlib.Path('/home/ubuntu/.{slug}-fb-snapshot.json')\n"
            f"snap = set(json.loads(snap_file.read_text())) if snap_file.exists() else set()\n"
            f"anns = json.loads(fb.read_text()) if fb.exists() else []\n"
            f"remaining = [a for a in anns if a.get('id','') not in snap]\n"
            f"fb.write_text(json.dumps(remaining))\n"
            f"PYEOF\n"
            f"rm -f '/home/ubuntu/.{slug}-fb-snapshot.json'\n"
        ),
    }
    post_success = PHASE_POST_SUCCESS.get(phase, "")

    ensure_worktree()
    venv_python = "/opt/specterx-kb-venv/bin/python3"
    launcher = (
        "#!/bin/bash\n"
        "export HOME=/home/ubuntu\n"
        'export PATH="/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin"\n'
        "set -a; source /home/ubuntu/.config/specterx-kb/.env; set +a\n"
        f"cd {WORKTREE_PATH}\n"
        f"sudo -u ubuntu git checkout main\n"
        f"sudo -u ubuntu git pull origin main\n"
        + (pre_launch if pre_launch else "")
        + f"{venv_python} {_repo_root}/writer/run_claude_code.py"
        f" --article {slug} --phase {phase}"
        + (f" {extra_allow_flags}" if extra_allow_flags else "")
        + f" >> /home/ubuntu/{slug}-{phase}.log 2>&1\n"
        f"_PHASE_EXIT=$?\n"
        f'echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] phase {phase} exited $_PHASE_EXIT"'
        f" >> /home/ubuntu/{slug}-{phase}.log\n"
        + (
            "if [ \"$_PHASE_EXIT\" -eq 0 ]; then\n"
            f"  sudo -u ubuntu git add articles/{slug}/\n"
            f"  sudo -u ubuntu git commit -m 'feat(article): {slug} — {phase}' || true\n"
            "  for _try in 1 2 3 4; do\n"
            "    sudo -u ubuntu git push origin main && break\n"
            "    sleep $((2 ** _try))\n"
            "  done\n"
            + (post_success if post_success else "")
            + "fi\n"
        )
    )
    lpath = Path(f"/home/ubuntu/run-{slug}-{phase}.sh")
    lpath.write_text(launcher)
    lpath.chmod(0o755)
    subprocess.Popen(
        ["bash", str(lpath)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    log(f"  Launched phase {phase} for {slug}")


def _handle_trigger(data: dict) -> dict:
    """Handle a manual or feedback trigger from the control plane API."""
    slug = data.get("slug", "").strip()
    reason = data.get("reason", "manual")
    issue = str(data.get("issue", ""))

    if not slug:
        return {"ok": False, "error": "slug required"}
    if not _QUEUE_STORE_AVAILABLE:
        return {"ok": False, "error": "queue_store not available"}

    state = load_state()

    if reason == "manual":
        trigger_key = f"article-triggered-{slug}"
        if trigger_key in state["handled"]:
            state["handled"].remove(trigger_key)
            save_state(state)
        _manual_trigger_set.append({"slug": slug, "reason": reason, "issue": issue})
        _poll_now.set()
        return {"ok": True, "reason": reason}

    if reason == "feedback":
        annotations = _fb.read_feedback(slug)
        if not annotations:
            return {"ok": False, "error": f"No feedback to revise for {slug}"}

        already_queued = any(
            t.get("slug") == slug and t.get("reason") == "feedback-launch"
            for t in _manual_trigger_set
        )
        if already_queued:
            return {"ok": False, "error": f"Revision already queued for {slug}"}

        fields = _qs.article_state_fields(slug)
        try:
            rc = int(fields.get("REVISION_CYCLE", "0"))
        except ValueError:
            rc = 0

        if _machine:
            _machine.transition(slug, "REVISING", extra={
                "REVISION_CYCLE": str(rc + 1),
                "NEXT_ACTION": "revise from reviewer feedback",
            })

        if not is_claude_running():
            _launch_phase(slug, "revise-from-feedback")
        else:
            log(f"  Claude running — queued feedback launch for {slug}")
            _manual_trigger_set.append({"slug": slug, "reason": "feedback-launch", "issue": issue})

        _poll_now.set()
        return {"ok": True, "reason": reason,
                "phase": "REVISING",
                "revision_cycle": rc + 1,
                "annotation_count": len(annotations)}

    return {"ok": False, "error": f"unknown reason '{reason}'"}


def _git_commit_push(message: str, *paths: str) -> None:
    """Commit and push to main with retry backoff."""
    ensure_worktree()
    git_worktree("checkout", "main", check=False)
    if paths:
        for p in paths:
            git_worktree("add", p, check=False)
    else:
        git_worktree("add", "-A", check=False)
    git_worktree("commit", "-m", message, check=False)
    for delay in (2, 4, 8, 16):
        r = subprocess.run(
            ["sudo", "-u", "ubuntu", "git", "push", "origin", "main"],
            cwd=str(WORKTREE_PATH), capture_output=True,
        ) if os.environ.get("GHOSTWRITER_NO_SUDO") != "1" else subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=str(WORKTREE_PATH), capture_output=True,
        )
        if r.returncode == 0:
            return
        time.sleep(delay)


def _handle_approve(data: dict) -> dict:
    """Approve an IN_REVIEW article and publish."""
    if not _machine or not _publish:
        return {"ok": False, "error": "pipeline modules not available"}
    slug = (data.get("slug") or "").strip()
    reviewer = (data.get("reviewer") or "reviewer").strip()
    phase = _machine.current_phase(slug)
    if phase != "IN_REVIEW":
        return {"ok": False, "error": f"phase is {phase}"}
    _machine.transition(slug, "APPROVED", extra={
        "APPROVED_BY": reviewer,
        "APPROVED_AT": _now_iso(),
    })
    _git_commit_push(f"feat(article): {slug} — approved by {reviewer}",
                     f"articles/{slug}/STATE")
    result = _publish.publish_article(slug)
    if not result.ok:
        return {"ok": False, "slug": slug, "phase": "APPROVED", "error": result.error}
    paths = list(result.outputs) + [f"articles/{slug}/STATE"]
    _git_commit_push(f"feat(article): {slug} — published ({result.adapter} adapter)", *paths)
    return {"ok": True, "slug": slug, "phase": "PUBLISHED", "outputs": result.outputs}


def _handle_publish_retry(data: dict) -> dict:
    """Retry publish for an APPROVED article."""
    if not _machine or not _publish:
        return {"ok": False, "error": "pipeline modules not available"}
    slug = (data.get("slug") or "").strip()
    if _machine.current_phase(slug) != "APPROVED":
        return {"ok": False, "error": f"phase is {_machine.current_phase(slug)}"}
    result = _publish.publish_article(slug)
    if not result.ok:
        return {"ok": False, "slug": slug, "phase": "APPROVED", "error": result.error}
    _git_commit_push(f"feat(article): {slug} — published ({result.adapter} adapter)",
                     *result.outputs, f"articles/{slug}/STATE")
    return {"ok": True, "slug": slug, "phase": "PUBLISHED", "outputs": result.outputs}


def _handle_request_changes(data: dict) -> dict:
    """Send an article back to REVISING."""
    if not _machine:
        return {"ok": False, "error": "pipeline modules not available"}
    slug = (data.get("slug") or "").strip()
    reason = (data.get("reason") or "reviewer requested changes").strip()
    phase = _machine.current_phase(slug)
    if phase not in ("IN_REVIEW", "PUBLISHED"):
        return {"ok": False, "error": f"phase is {phase}"}
    fields = _qs.article_state_fields(slug)
    try:
        rc = int(fields.get("REVISION_CYCLE", "0"))
    except ValueError:
        rc = 0
    if phase == "PUBLISHED":
        rc += 1
    _machine.transition(slug, "REVISING", extra={
        "REVISION_CYCLE": str(rc),
        "NEXT_ACTION": reason,
    })
    _poll_now.set()
    return {"ok": True, "slug": slug, "phase": "REVISING"}


def _run_tester(slug: str) -> None:
    """Run the Playwright tester for *slug*."""
    venv_python = "/opt/specterx-kb-venv/bin/python3"
    if not Path(venv_python).exists():
        venv_python = "python3"
    subprocess.Popen(
        [venv_python, str(_repo_root / "tester" / "runner.py"), "--article", slug],
        cwd=str(_repo_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    log(f"  Launched tester for {slug}")


def _queue_reverification(state: dict, save_state) -> bool:
    """Queue the oldest stale article for re-verification. Returns True if queued."""
    if not _machine:
        return False
    try:
        from pipeline.reverify import find_stale_articles, queue_reverification
        stale = find_stale_articles()
        if not stale:
            return False
        slug, reason = stale[0]
        key = f"reverify-{slug}"
        if key in state.get("handled", []):
            return False
        queue_reverification(slug, reason)
        state.setdefault("handled", []).append(key)
        save_state(state)
        log(f"  Queued re-verification for {slug}: {reason}")
        return True
    except Exception as exc:
        log(f"  WARNING: re-verification scan failed: {exc}")
        return False


def _handle_delete_article(slug: str, remove_from_plan: bool) -> dict:
    """Delete an article's files and optionally drop it from the queue."""
    if not _QUEUE_STORE_AVAILABLE:
        return {"ok": False, "error": "queue_store not available"}
    slug = (slug or "").strip()
    if not _qs.SLUG_RE.match(slug):
        return {"ok": False, "error": f"invalid slug '{slug}'"}

    merged = False
    try:
        merged = _qs.article_is_merged(slug)
    except Exception as exc:
        log(f"  WARNING: could not determine merged state for {slug}: {exc}")

    pushed = False
    push_failed = False
    push_error = ""
    if merged:
        git("rm", "-r", "--quiet", f"articles/{slug}", check=False)
        _qs.delete_article_dir(slug)
        git("commit", "-m", f"chore(article): delete {slug}", check=False)
        try:
            git("push", "origin", "main")
            pushed = True
        except Exception as exc:
            push_failed = True
            push_error = str(exc)
            log(f"  WARNING: push of {slug} deletion to main failed: {exc}")
    else:
        _qs.delete_article_dir(slug)

    if _fb:
        try:
            _fb.delete_feedback(slug)
        except Exception as exc:
            log(f"  WARNING: delete feedback for {slug} failed: {exc}")

    removed_from_plan = False
    if remove_from_plan:
        try:
            with _queue_lock:
                removed_from_plan = _qs.remove_article_from_queue(slug)
            _poll_now.set()
        except Exception as exc:
            log(f"  WARNING: remove {slug} from queue failed: {exc}")

    log(f"  Ghostwriter deleted article {slug} "
        f"(merged={merged}, removed_from_plan={removed_from_plan})")
    result = {
        "ok": True,
        "slug": slug,
        "merged": merged,
        "removed_from_plan": removed_from_plan,
        "pushed": pushed,
    }
    if push_failed:
        result["push_failed"] = True
        result["error"] = push_error
    return result


# ── control plane (localhost:9191) ────────────────────────────────────────────

def _request_origin(handler: BaseHTTPRequestHandler) -> str:
    host = handler.headers.get("Host", f"127.0.0.1:{CONTROL_PORT}")
    return f"http://{host}"


def _article_preview_html(slug: str, origin: str) -> tuple[int, str]:
    return resolve_preview_html(REPO_PATH, slug, origin)


def _append_feedback(slug: str, payload: dict) -> dict:
    if not slug:
        return {"ok": False, "error": "slug required"}
    ann = {k: v for k, v in payload.items() if k != "slug"}
    return _fb.append_feedback(slug, ann)


def _remove_feedback(slug: str, ann_id: str) -> dict:
    if not slug:
        return {"ok": False, "error": "slug required"}
    return _fb.remove_feedback(slug, ann_id)


class _ControlHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # silence default access log

    def _route(self):
        parsed = urllib.parse.urlparse(self.path)
        return parsed.path, urllib.parse.parse_qs(parsed.query)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        return json.loads(body)

    def do_GET(self):
        path, qs = self._route()
        if path == "/api/queue":
            if not _QUEUE_STORE_AVAILABLE:
                self._respond(503, json.dumps({"error": "queue_store not available"}))
                return
            try:
                data = _qs.queue_with_states()
                data["claude_running"] = is_claude_running()
                data["active_article"] = _active_article_slug
                self._respond(200, json.dumps(data))
            except FileNotFoundError:
                self._respond(404, json.dumps({"error": "clusters/queue.json not found"}))
            except Exception as exc:
                self._respond(500, json.dumps({"error": str(exc)}))
        elif path == "/api/feedback":
            slug = qs.get("slug", [""])[0]
            if not slug:
                self._respond(400, json.dumps({"error": "slug required"}))
                return
            annotations = _fb.read_feedback(slug)
            self._respond(200, json.dumps({"slug": slug, "annotations": annotations}))
        elif path.startswith("/api/articles/") and path.endswith("/preview"):
            slug = path[len("/api/articles/"):-len("/preview")]
            if not slug:
                self._respond(400, json.dumps({"error": "slug required"}))
                return
            code, html = _article_preview_html(slug, _request_origin(self))
            if code != 200:
                self._respond(404, json.dumps({"error": f"preview not found for {slug}"}))
                return
            self._respond_html(200, html)
        else:
            self._respond(404, json.dumps({"error": "not found"}))

    def do_PUT(self):
        path, _ = self._route()
        if path == "/api/queue":
            if not _QUEUE_STORE_AVAILABLE:
                self._respond(503, json.dumps({"error": "queue_store not available"}))
                return
            try:
                q = self._read_json()
                errors = [e for e in _qs.validate_slugs(q) if e["level"] == "error"]
                if errors:
                    self._respond(422, json.dumps({"errors": errors}))
                    return
                with _queue_lock:
                    _qs.save_queue(q)
                _poll_now.set()
                self._respond(200, json.dumps({"ok": True}))
            except Exception as exc:
                self._respond(400, json.dumps({"error": str(exc)}))
        else:
            self._respond(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        path, _ = self._route()
        if path == "/poll-now":
            _poll_now.set()
            log("Control: poll-now requested via HTTP")
            self._respond(200, '{"ok":true}')
        elif path == "/api/queue/trigger":
            try:
                data = self._read_json()
                result = _handle_trigger(data)
                code = 200 if result.get("ok") else 400
                self._respond(code, json.dumps(result))
            except Exception as exc:
                self._respond(400, json.dumps({"error": str(exc)}))
        elif path == "/api/queue/approve":
            try:
                data = self._read_json()
                result = _handle_approve(data)
                code = 200 if result.get("ok") else (409 if "phase is" in result.get("error", "") else 500)
                self._respond(code, json.dumps(result))
            except Exception as exc:
                self._respond(400, json.dumps({"error": str(exc)}))
        elif path == "/api/queue/publish":
            try:
                data = self._read_json()
                result = _handle_publish_retry(data)
                code = 200 if result.get("ok") else 409
                self._respond(code, json.dumps(result))
            except Exception as exc:
                self._respond(400, json.dumps({"error": str(exc)}))
        elif path == "/api/queue/request-changes":
            try:
                data = self._read_json()
                result = _handle_request_changes(data)
                code = 200 if result.get("ok") else 409
                self._respond(code, json.dumps(result))
            except Exception as exc:
                self._respond(400, json.dumps({"error": str(exc)}))
        elif path == "/api/feedback":
            try:
                data = self._read_json()
                slug = (data.get("slug") or "").strip()
                result = _append_feedback(slug, data)
                code = 200 if result.get("ok") else 400
                self._respond(code, json.dumps(result))
            except Exception as exc:
                self._respond(400, json.dumps({"error": str(exc)}))
        else:
            self._respond(404, json.dumps({"error": "not found"}))

    def do_DELETE(self):
        path, qs = self._route()
        if path == "/api/feedback":
            slug = qs.get("slug", [""])[0]
            ann_id = qs.get("id", [""])[0]
            if not slug:
                self._respond(400, json.dumps({"error": "slug required"}))
                return
            if not ann_id:
                self._respond(400, json.dumps({"error": "id required"}))
                return
            result = _remove_feedback(slug, ann_id)
            if not result.get("ok"):
                code = 404 if result.get("error") == "annotation not found" else 400
                self._respond(code, json.dumps(result))
                return
            self._respond(200, json.dumps(result))
        elif path.startswith("/api/articles/"):
            slug = path[len("/api/articles/"):].strip("/")
            remove_from_plan = qs.get("remove_from_plan", ["false"])[0].lower() == "true"
            try:
                result = _handle_delete_article(slug, remove_from_plan)
                code = 200 if result.get("ok") else 400
                self._respond(code, json.dumps(result))
            except Exception as exc:
                self._respond(400, json.dumps({"error": str(exc)}))
        else:
            self._respond(404, json.dumps({"error": "not found"}))

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, code, body):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(data)

    def _respond_html(self, code, body: str):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(data)


def _start_fetch_thread(interval: int = 60):
    """Background git fetch to keep main up to date."""

    def _loop():
        while True:
            try:
                _fetch_all_repos()
            except Exception as exc:
                log(f"Background fetch failed: {exc}")
            time.sleep(interval)

    t = threading.Thread(target=_loop, daemon=True, name="git-fetch")
    t.start()


def _start_control_server():
    srv = HTTPServer(("127.0.0.1", CONTROL_PORT), _ControlHandler)
    t = threading.Thread(target=srv.serve_forever, daemon=True, name="control-http")
    t.start()
    _start_fetch_thread()
    log(f"Control plane listening on 127.0.0.1:{CONTROL_PORT}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    global _active_article_slug, _active_article_since
    _runtime["started_at"] = _now_iso()
    _runtime["pid"] = os.getpid()

    log("=" * 60)
    log("pr-watcher daemon starting")
    log(f"Repo   : {REPO}")
    log(f"Polling: every {POLL_INTERVAL}s")
    log("=" * 60)

    _start_control_server()
    git("fetch", "--all", check=False)
    state = load_state()
    iteration = 0

    if _machine and _dispatcher:
        active = _machine.active_article()
        if active:
            relaunch = _machine.resume(active)
            if relaunch:
                log(f"Startup resume: {active} phase {relaunch}")

    while True:
        iteration += 1
        log(f"--- Poll #{iteration} ---")
        next_poll_at = time.time() + POLL_INTERVAL
        _status_cache.update({"state": state, "iteration": iteration, "next_poll_at": next_poll_at})
        try:
            while _manual_trigger_set:
                trig = _manual_trigger_set[0]
                if trig.get("reason") == "feedback-launch":
                    if not is_claude_running():
                        _manual_trigger_set.pop(0)
                        _launch_phase(trig["slug"], "revise-from-feedback")
                    else:
                        break
                elif trig.get("reason") == "manual":
                    if is_claude_running():
                        break
                    slug = trig["slug"]
                    _manual_trigger_set.pop(0)
                    if _machine:
                        try:
                            _machine.transition(slug, "RESEARCHING")
                        except Exception as exc:
                            log(f"  Manual trigger: could not transition {slug}: {exc}")
                    _launch_phase(slug, "research")
                    state.setdefault("handled", []).append(f"article-triggered-{slug}")
                    save_state(state)
                    _active_article_slug = slug
                    _active_article_since = time.time()
                else:
                    _manual_trigger_set.pop(0)

            if _machine and _dispatcher and not is_claude_running():
                active = _machine.active_article()
                if active:
                    _dispatcher.dispatch(
                        active,
                        launch_phase=_launch_phase,
                        run_tester=_run_tester,
                        retry_publish=lambda s: _handle_publish_retry({"slug": s}),
                        is_claude_running=is_claude_running,
                        state=state,
                        save_state=save_state,
                        log=log,
                    )
                else:
                    _dispatcher.dispatch_idle(
                        launch_phase=_launch_phase,
                        queue_reverification=lambda: _queue_reverification(state, save_state),
                        is_claude_running=is_claude_running,
                        state=state,
                        save_state=save_state,
                        log=log,
                    )

            _runtime["last_error"] = None

        except Exception as exc:
            log(f"ERROR in poll loop: {exc}")
            _runtime["last_error"] = {"message": str(exc), "at": _now_iso()}

        # Clear the active-article marker once Claude is no longer running.
        # Guarded by a grace window because the launcher runs `git pull` before
        # `claude` starts, so is_claude_running() is briefly False after launch.
        if (
            _active_article_slug
            and time.time() - _active_article_since > max(POLL_INTERVAL, 120)
            and not is_claude_running()
        ):
            _active_article_slug = None

        write_status(state, iteration, next_poll_at)
        triggered = _poll_now.wait(timeout=POLL_INTERVAL)
        _poll_now.clear()
        if triggered:
            log("Poll triggered on demand — skipping scheduled wait")


if __name__ == "__main__":
    main()
