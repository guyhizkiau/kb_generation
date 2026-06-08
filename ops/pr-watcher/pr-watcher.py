#!/usr/bin/env python3
"""
pr-watcher.py — autonomous PR comment resolver + article pipeline driver

Polls open PRs every 5 minutes. For each new review/issue comment from a
human, runs VM-Claude to resolve it, commits the fix, and posts a contextual
reply. Also monitors recently-merged article PRs and triggers the next article.
"""
import subprocess, json, os, pty, time, re, threading, tempfile, sys, urllib.parse
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
BOT_MARKER    = "<!-- pr-watcher-bot -->"
CLAUDE_BIN    = "/usr/local/bin/claude"
PREVIEW_BASE  = "http://18.192.122.48"   # nginx article browser (port 80)

# Timeouts for Claude invocations
TASK_TIMEOUT_SECS    = 3600  # 1-hour hard cap per Claude invocation
STEP_TIMEOUT_SECS    = 120   # kill if no output for 2 minutes AND claude is not in a tool call
TOOL_TIMEOUT_SECS    = 1800  # kill if a single tool call exceeds 30 minutes
INITIAL_TIMEOUT_SECS = 3600  # match task cap: first output may not arrive until E2E tool finishes
CONTROL_PORT      = 9191  # localhost-only HTTP control plane

# Prepend script directory so queue_store.py is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("KB_REPO_ROOT", str(REPO_PATH))
_vm_repo = "/home/ubuntu/kb_generation"
if os.environ.get("KB_REPO_ROOT") == _vm_repo and Path(_vm_repo).exists():
    os.environ.setdefault("GHOSTWRITER_FEEDBACK_DIR", "/home/ubuntu/ghostwriter-feedback")
try:
    import queue_store as _qs
    import feedback_store as _fb
    from preview_transform import patch_article_preview_html, load_preview_html, resolve_preview_html
    import gh_queue as _ghq
    _QUEUE_STORE_AVAILABLE = True
except ImportError:
    _qs = None  # type: ignore[assignment]
    _fb = None  # type: ignore[assignment]
    _ghq = None  # type: ignore[assignment]
    patch_article_preview_html = None  # type: ignore[assignment,misc]
    load_preview_html = None  # type: ignore[assignment,misc]
    resolve_preview_html = None  # type: ignore[assignment,misc]
    _QUEUE_STORE_AVAILABLE = False


def _load_resolution_checklist() -> list[dict]:
    for path in (
        REPO_PATH / "ops/pr-watcher/resolution_checklist.json",
        Path(__file__).resolve().parent / "resolution_checklist.json",
    ):
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError("resolution_checklist.json not found")


RESOLUTION_CHECKLIST: list[dict] = _load_resolution_checklist()


def build_resolution_checklist(
    active_phase: int,
    *,
    terminal: str | None = None,
) -> list[dict]:
    """Build checklist items with status: pending | active | done | failed."""
    phase = max(1, min(active_phase, len(RESOLUTION_CHECKLIST)))
    items: list[dict] = []
    for step in RESOLUTION_CHECKLIST:
        sid = step["id"]
        if terminal == "done":
            status = "done"
        elif terminal == "failed" and sid == phase:
            status = "failed"
        elif terminal == "failed" and sid < phase:
            status = "done"
        elif sid < phase:
            status = "done"
        elif sid == phase:
            status = "active"
        else:
            status = "pending"
        items.append({**step, "status": status})
    return items


# Event set by the control plane to trigger an immediate poll
_poll_now = threading.Event()

# Queue source of truth: clusters/queue.json (managed by queue_store)
# CLUSTER_1_ARTICLES removed — use queue_store.load_queue() instead

_queue_lock = threading.Lock()
_manual_trigger_set: list[dict] = []   # items: {slug, reason, issue}


# ── helpers ───────────────────────────────────────────────────────────────────

def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    # stdout is redirected to LOG_FILE via nohup; file write below is the only write
    with LOG_FILE.open("a") as fh:
        fh.write(line + "\n")


def gh_json(*args) -> list | dict:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed:\n{r.stderr.strip()}")
    return json.loads(r.stdout)


def gh_post(path: str, **fields) -> dict:
    cmd = ["gh", "api", path, "-X", "POST"]
    for k, v in fields.items():
        cmd += ["-f", f"{k}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gh api POST {path} failed:\n{r.stderr.strip()}")
    return json.loads(r.stdout)


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
    "current_task": None,   # {pr_number, comment_id, step, started_at}
    "last_poll_open_prs": [],
    "last_error": None,     # {message, at}
    "last_task_duration_secs": None,
}

# Cache of the latest write_status args so resolve_comment() can flush mid-task
_status_cache: dict = {}   # keys: state, iteration, next_poll_at

# Comment IDs to re-process even if already in state["handled"] (set by retry endpoint)
_retry_set: set = set()


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
        "open_prs": _runtime["last_poll_open_prs"],
        "current_task": _runtime["current_task"],
        "last_error": _runtime["last_error"],
        "last_task_duration_secs": _runtime["last_task_duration_secs"],
        "failed_comments": list(state.get("failed_comments", {}).values()),
        "counters": {
            "comments_resolved":  sum(1 for h in handled if h.startswith("issue-")),
            "articles_triggered": sum(1 for h in handled if h.startswith("article-triggered-")),
            "merges_handled":     sum(1 for h in handled if h.startswith("merge-handled-")),
            "previews_posted":    sum(1 for h in handled if h.startswith("preview-posted-")),
        },
        "recent_log": _tail_log(40),
    }
    dest = STATUS_DIR / "status.json"
    tmp = dest.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2))
    os.replace(tmp, dest)


def _record_failure(state: dict, cid: str, pr_number: int, body: str, status: str):
    state.setdefault("failed_comments", {})[cid] = {
        "comment_id": cid,
        "pr_number": pr_number,
        "body_preview": body[:200],
        "failure": status,
        "failed_at": _now_iso(),
    }


def _clear_failure(state: dict, cid: str):
    state.setdefault("failed_comments", {}).pop(cid, None)


def _tail_log(n: int) -> list[str]:
    try:
        lines = LOG_FILE.read_text(errors="replace").splitlines()
        return lines[-n:]
    except Exception:
        return []


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
    """Refresh remote refs for git show without checking out branches."""
    git("fetch", "--all", check=False)


def is_claude_running() -> bool:
    """Return True if a claude process is already running on the VM."""
    for pattern in (r"claude.*--dangerously", r"claude.*-p", r"run_claude_code\.py"):
        r = subprocess.run(["pgrep", "-f", pattern], capture_output=True)
        if r.returncode == 0:
            return True
    return False


# ── resolution engine ─────────────────────────────────────────────────────────

RESOLUTION_PROMPT_TEMPLATE = """\
You are the KB pipeline bot resolving a PR review comment on the repository at
{worktree_path}. The branch {branch} is already checked out in this worktree
and up to date. The serving copy at {repo_path} stays on main — do NOT touch it.
Do NOT switch branches. Do NOT open PRs. Do NOT merge anything.

## Comment details

PR number : {pr_number}
File      : {path}
Line      : {line}
Comment   : {body}

## Phase markers (REQUIRED — dashboard checklist)

Before starting each numbered step (1–6) below, print exactly one line on its own:
  PHASE: <n>
where <n> is 1, 2, 3, 4, 5, or 6. Do not skip numbers. Granular STEP: lines
belong in tool output only; phase progress is tracked via PHASE lines.

## What you must do — FIX THE ROOT CAUSE FIRST (WORKFLOW.md §9.5)

Do NOT start by editing the article. Most review feedback reflects a rule
that should hold for EVERY future article. So you fix the canonical source
of truth first, then fix this article by APPLYING that updated source. This
makes the fix global, and turns this article into an immediate test of the
new rule.

1. Read the comment and the relevant article file carefully.

2. CLASSIFY the comment against this canonical-target map:
   | Comment is about…                                     | Fix-first file |
   |-------------------------------------------------------|----------------|
   | Voice / tone / wording / structure / anti-pattern     | editorial/STYLE_GUIDE.md |
   | A product term, definition, or canonical phrasing     | canon/GLOSSARY.md |
   | A component's name or category                        | product/COMPONENT_TAXONOMY.md |
   | Public-vs-internal scope, audience split              | editorial/PUBLIC_KB_SCOPE.md |
   | "We shouldn't document this / not shipped"            | canon/DO_NOT_DOCUMENT.md |
   | Article scope, topics-to-cover, sequencing            | editorial/ARTICLES_PLAN.md |
   | A process / pipeline-instruction gap                  | the relevant pipeline/prompts/*.md or WORKFLOW.md |
   | A one-off product fact, blurry screenshot, single fix | none — article-only, with a justification |

3. GENERALIZE WHEN APPLICABLE, ELSE JUSTIFY.
   - If a canonical file applies: edit THAT FILE FIRST. Then commit it alone:
       git add <canonical-file>
       git commit -m "docs(canon): resolve PR#{pr_number} feedback — <summary>"
       git push origin {branch}
     (use docs(style)/docs(taxonomy)/docs(scope) as appropriate)
   - If the comment is genuinely article-specific: do NOT invent a contrived
     canon edit. Record a one-line justification (you will put it in the reply)
     and proceed straight to the article fix.

4. APPLY TO THE ARTICLE FROM THE UPDATED CANON.
   Re-read the canonical file you just edited and fix the article FROM IT
   (not from memory). Typical article changes:
   - Reword a step for clarity or accuracy
   - Fix or expand competitor coverage (if the comment is about research gaps,
     scrape 2-4 competitor KBs using Playwright headless and update research files)
   - Add or correct a note, troubleshooting entry, or callout
   - Fix terminology using the canonical labels you just confirmed/added
   Then RE-RENDER the HTML previews (ALWAYS — even for prose-only changes):
       python3 pipeline/render_html.py articles/<NN-slug>/
   This writes <slug>.html AND <slug>-zendesk.html. Also regenerate the index:
       python3 pipeline/build_index.py
   Commit the article AND all rendered files together:
       git add articles/<NN-slug>/final.md articles/<NN-slug>/<slug>.html \
               articles/<NN-slug>/<slug>-zendesk.html articles/index.html
       git commit -m "fix(article): resolve PR#{pr_number} comment — <5-word summary>"
       git push origin {branch}

5. VALIDATE AGAINST THE ORIGINAL COMMENT (always — this is the closing step).
   Re-check the fix against what the reviewer actually asked. Quote the ask
   and point to the resolved text in the article.
   - If RESOLVED: continue to step 6.
   - If NOT resolved: diagnose WHY the generalized rule didn't carry the fix
     (too vague? wrong target file? rule right but mis-applied?). Then retry
     more directly — but the canonical edit must EXPAND the existing rule (add
     a clause, example, or precise label) while PRESERVING the general
     statement. NEVER delete the general rule and substitute an
     article-specific instruction — that forgoes generalization for an
     over-fit. Commit each expansion as its own amended docs(...) commit,
     re-apply to the article, and re-validate. Bound this loop to 2 retries.

6. On the LAST two lines of your output, print exactly:
   RESOLVED
   Context: <what canonical file you changed (or the justification for skipping),
   AND how applying it resolved the article; if the validate loop ran, what you
   expanded and why>

   Or if you could not resolve it within 2 retries:
   NEEDS_HUMAN
   Reason: <the diagnosis AND the current state of the expanded rule, so a human
   can improve the RULE — not just this one article>

## Competitor research rules (when a comment is about missing competitor coverage)

- Review AT LEAST 2 competitor articles on the topic, ideally 3-4.
- Vendor priority: Egnyte → Virtru → DocSend/Dropbox Help → Vera → HubSpot Knowledge Base
- Use Playwright headless (/opt/specterx-kb-venv/bin/python3) to navigate each vendor's
  help centre, search for the topic, and extract a coverage checklist.
- Only skip a vendor if you genuinely cannot find a relevant article after a real search.
- Save cached versions to references/competitors/<vendor>/<slug>.md with YAML front matter.
- Update references/competitors/INDEX.json with all new entries.

## Internal sources rules (when a comment is about missing internal coverage)

- Check references/internal/ AND product/ (especially product/COMPONENT_TAXONOMY.md
  and any files in component-records/).
- Also check editorial/ARTICLES_PLAN.md for the article's own "Topics to cover" section.

## Progress markers (REQUIRED — watcher monitors these)

Before every distinct action, print a STEP line on its own:
  STEP: read article file
  STEP: open SpecterX in browser
  STEP: navigate to Gmail
  STEP: search inbox for reset email
  STEP: git commit and push
  … (one STEP per logical action; keep labels short and descriptive)

The watcher uses stream-json events from your output to track progress.
Tool calls automatically extend the stall timer ({tool_timeout}s per
individual tool invocation), so long Bash/Playwright runs are fine.
When no tool is running, the stall timer is {step_timeout}s — print
a STEP line or any text periodically during pure-thinking pauses.
The task has a hard {task_timeout}s cap regardless.

## Playwright timeout rules (REQUIRED)

Every Playwright call must carry an explicit timeout. Never rely on defaults.
  page.goto(url, timeout=30_000)
  page.wait_for_selector(sel, timeout=15_000)
  page.wait_for_url(pattern, timeout=20_000)
  page.wait_for_load_state("networkidle", timeout=15_000)
  locator.click(timeout=10_000)

If a Playwright call raises TimeoutError, catch it, print:
  STEP_FAILED: <step name> — <brief reason>
Then either retry once or exit with NEEDS_HUMAN and a clear Reason.

## Style guide (REQUIRED for any prose change)

Before producing the final wording for any prose change, re-read the
relevant sections of `editorial/STYLE_GUIDE.md`:

- Section 2.4 — Contractions: default to "don't", "can't", "isn't",
  "you'll", "you've" in end-user articles. Uncontracted forms read
  AI-generated.
- Section 3 — Article openings: vary the opening pattern (situational,
  direct-action, or task-framing). Do NOT default to "Use this article
  to…" — that pattern is overused across the KB.
- Section 10 — Troubleshooting: headers state the symptom from the
  user's perspective, NOT the cause or the fix. The cause and the fix
  go in the body of the item.
- Section 13 / 13a — Words and punctuation: avoid "simply", "easily",
  "utilize", "in order to", "ensure that", em dashes.
- Section 14 — Anti-patterns: no meta-commentary about article
  structure, no summary-before-procedure, no internal QA / validation
  metadata (test-account emails, last-validated footers, capture-run
  identifiers) in `final.md`.

When a comment asks for a wording or structural change, FIRST check
whether the style guide already covers it. If the rule is MISSING or
TOO VAGUE to have prevented the issue, add or sharpen that rule in
`editorial/STYLE_GUIDE.md` (the docs commit in step 3) and then apply
it to the article (step 4). If the rule already exists and was simply
not followed, note that in your reply and just apply the existing rule
— no canon edit needed. If the comment itself asks for something the
style guide forbids, leave a brief reply explaining and ask for
confirmation before pushing the change.

## Hard rules (WORKFLOW.md §12)

- Never commit credentials or .env.
- Never paste source code into article drafts.
- Never invent UI labels — write [verify in test] if unsure.
- Screenshots with real customer data go to screenshots/_flagged/, not screenshots/.
"""


def resolve_comment(pr_number: int, branch: str, comment: dict) -> tuple[str, str, str]:
    """
    Run VM-Claude to resolve a single comment.
    Returns (status, output, context) where:
      status  = RESOLVED | NEEDS_HUMAN | STEP_TIMEOUT | TOTAL_TIMEOUT | ERROR
      context = short explanation of what was done (from Claude's output)

    Two independent safety timers prevent hangs:
      STEP_TIMEOUT_SECS  — kills if no output for N seconds (stalled step)
      TASK_TIMEOUT_SECS  — 1-hour hard cap regardless of output activity
    """
    path = comment.get("path") or "(PR-level comment, no specific file)"
    line = comment.get("line") or comment.get("original_line") or "n/a"
    body = comment["body"]

    prompt = RESOLUTION_PROMPT_TEMPLATE.format(
        worktree_path=WORKTREE_PATH, repo_path=REPO_PATH,
        branch=branch, pr_number=pr_number, path=path, line=line, body=body,
        step_timeout=STEP_TIMEOUT_SECS, task_timeout=TASK_TIMEOUT_SECS,
        tool_timeout=TOOL_TIMEOUT_SECS,
    )

    output_lines: list[str] = []
    assistant_text_lines: list[str] = []   # only plain assistant text (for RESOLVED/NEEDS_HUMAN scan)
    kill_reason: list[str] = []   # mutable container so threads can write it
    current_step: list[str] = ["(starting)"]
    current_phase: list[int] = [1]

    # Truncate task log. Reader thread will populate it.
    TASK_LOG_FILE.write_text("")

    # Track task in runtime state for dashboard
    task_started = time.time()
    _runtime["current_task"] = {
        "pr_number": pr_number,
        "comment_id": comment.get("id"),
        "step": current_step[0],
        "phase": 1,
        "checklist": build_resolution_checklist(1),
        "started_at": _now_iso(),
    }
    flush_status()  # push to dashboard immediately so it shows active task

    # Allocate a PTY. Claude/Node sees its stdout as a TTY and switches to
    # line buffering, so each \n flushes immediately and we can stream
    # output to the dashboard. Without this, Node block-buffers ~16 KB and
    # we see nothing until process exit.
    master_fd, slave_fd = pty.openpty()

    # Env: keep ANTHROPIC_API_KEY etc, but suppress colors / animations
    # that would otherwise be triggered by the TTY detection.
    claude_env = os.environ.copy()
    claude_env["TERM"] = "dumb"
    claude_env["NO_COLOR"] = "1"
    claude_env["FORCE_COLOR"] = "0"
    claude_env["CI"] = "1"   # most CLIs suppress TUI when CI=1

    try:
        # --output-format=stream-json emits one JSON event per assistant
        # message delta, tool_use, and tool_result — in real time, as the
        # model produces them. --verbose is required by claude when -p +
        # stream-json are combined.
        proc = subprocess.Popen(
            [
                CLAUDE_BIN, "--dangerously-skip-permissions",
                "--output-format", "stream-json",
                "--verbose",
                "-p", prompt,
            ],
            stdout=slave_fd,
            stderr=slave_fd,
            stdin=subprocess.DEVNULL,
            env=claude_env, cwd=str(WORKTREE_PATH),
            preexec_fn=os.setpgrp, # new process group for killpg
            close_fds=True,
        )
    except Exception as exc:
        os.close(master_fd)
        os.close(slave_fd)
        _runtime["current_task"] = None
        return "ERROR", str(exc), ""

    # Parent no longer needs the slave end — close it so the master read
    # returns EOF when claude exits.
    os.close(slave_fd)

    # ── reader thread: stream PTY output → task log + dashboard ──────────────
    # Initial deadline is longer to allow for Claude cold-start; drops to
    # STEP_TIMEOUT_SECS after the first line of output arrives.
    step_deadline: list[float] = [time.time() + INITIAL_TIMEOUT_SECS]
    first_output = [False]

    def _set_phase(phase: int) -> None:
        phase = max(1, min(phase, len(RESOLUTION_CHECKLIST)))
        current_phase[0] = phase
        task = _runtime.get("current_task")
        if not task:
            return
        task["phase"] = phase
        task["checklist"] = build_resolution_checklist(phase)
        _runtime["current_task"] = task
        log(f"    → PHASE: {phase}")
        flush_status()

    def _set_step(step: str):
        current_step[0] = step
        task = _runtime.get("current_task")
        if not task:
            return
        task["step"] = step
        _runtime["current_task"] = task
        log(f"    → STEP: {step}")
        flush_status()

    def _finish_task_checklist(terminal: str) -> None:
        task = _runtime.get("current_task")
        if task:
            phase = task.get("phase", current_phase[0])
            if terminal == "done":
                task["checklist"] = build_resolution_checklist(
                    len(RESOLUTION_CHECKLIST), terminal="done"
                )
            else:
                task["checklist"] = build_resolution_checklist(
                    phase, terminal="failed"
                )
            _runtime["current_task"] = task
            flush_status()
        _runtime["current_task"] = None
        flush_status()

    def _format_event(evt: dict) -> list[str]:
        """Turn a stream-json event into human-readable log lines."""
        lines: list[str] = []
        et = evt.get("type")
        if et == "system" and evt.get("subtype") == "init":
            tools = evt.get("tools") or []
            lines.append(f"[system] init · {len(tools)} tools available")
        elif et == "assistant":
            for block in evt.get("message", {}).get("content", []):
                btype = block.get("type")
                if btype == "text":
                    text = (block.get("text") or "").rstrip()
                    if not text:
                        continue
                    for sub in text.splitlines():
                        lines.append(sub)
                        assistant_text_lines.append(sub)
                        phase_m = re.match(r"^PHASE:\s*(\d+)\s*$", sub.strip())
                        if phase_m:
                            _set_phase(int(phase_m.group(1)))
                        elif sub.startswith("STEP:"):
                            _set_step(sub[5:].strip())
                elif btype == "tool_use":
                    name = block.get("name", "?")
                    inp = block.get("input") or {}
                    summary = ""
                    if name == "Bash":
                        cmd = (inp.get("command") or "").splitlines()
                        summary = cmd[0][:200] if cmd else ""
                    elif name in ("Read", "Edit", "Write"):
                        summary = str(inp.get("file_path", ""))[:200]
                    elif name == "Grep":
                        summary = f"{inp.get('pattern','')!r} in {inp.get('path','.')}"
                    elif name == "Glob":
                        summary = inp.get("pattern", "")
                    else:
                        summary = json.dumps(inp)[:200]
                    lines.append(f"→ {name}: {summary}")
                    _set_step(f"{name}: {summary[:80]}")
        elif et == "user":
            # tool_result echo from previous tool_use
            for block in evt.get("message", {}).get("content", []):
                if block.get("type") == "tool_result":
                    content = block.get("content")
                    if isinstance(content, list):
                        content = "".join(
                            c.get("text", "") for c in content if c.get("type") == "text"
                        )
                    if not isinstance(content, str):
                        content = json.dumps(content)[:200]
                    tail = content.strip().splitlines()[-3:] if content else []
                    for t in tail:
                        lines.append(f"  {t[:240]}")
        elif et == "result":
            sub = evt.get("subtype", "")
            cost = evt.get("total_cost_usd")
            dur = evt.get("duration_ms")
            lines.append(f"[result] {sub} · {dur}ms · ${cost}")
        return lines

    def _process_line(raw: str):
        """Receive one line of PTY output (should be one JSON event)."""
        if not first_output[0]:
            first_output[0] = True
        if not raw.strip():
            return
        output_lines.append(raw)  # keep raw for RESOLVED/NEEDS_HUMAN parsing
        try:
            evt = json.loads(raw)
        except Exception:
            # Not JSON — pass through (claude warnings, login prompts, etc.)
            step_deadline[0] = time.time() + STEP_TIMEOUT_SECS
            with TASK_LOG_FILE.open("a") as fh:
                fh.write(raw + "\n")
            return

        # Adjust the watchdog deadline based on event type. The key insight:
        # between a tool_use event and its tool_result, no stream-json events
        # are produced — but claude is actively waiting on a real tool, not
        # hung. So when we see tool_use we extend the deadline to give the
        # tool time to run. tool_result and assistant text reset to normal.
        et = evt.get("type")
        contains_tool_use = False
        if et == "assistant":
            for block in evt.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    contains_tool_use = True
                    break
        if contains_tool_use:
            step_deadline[0] = time.time() + TOOL_TIMEOUT_SECS
        else:
            step_deadline[0] = time.time() + STEP_TIMEOUT_SECS

        formatted = _format_event(evt)
        if formatted:
            with TASK_LOG_FILE.open("a") as fh:
                for ln in formatted:
                    fh.write(ln + "\n")

    def _reader():
        buf = b""
        try:
            while True:
                try:
                    chunk = os.read(master_fd, 8192)
                except OSError:
                    break  # PTY closed (claude exited)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line, _, buf = buf.partition(b"\n")
                    _process_line(line.decode("utf-8", errors="replace").rstrip("\r"))
            if buf:
                _process_line(buf.decode("utf-8", errors="replace").rstrip("\r"))
        finally:
            try:
                os.close(master_fd)
            except OSError:
                pass

    reader = threading.Thread(target=_reader, daemon=True)
    reader.start()

    # ── watchdog thread: kill on step stall or total timeout ──────────────────
    task_deadline = time.time() + TASK_TIMEOUT_SECS

    def _kill_group():
        """Kill the entire process group to clean up claude + any child browsers."""
        try:
            import signal
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            proc.kill()  # fallback

    def _watchdog():
        while proc.poll() is None:
            now = time.time()
            if now > task_deadline:
                kill_reason.append("total_timeout")
                _kill_group()
                return
            if now > step_deadline[0]:
                kill_reason.append("step_timeout")
                _kill_group()
                return
            time.sleep(1)

    watchdog = threading.Thread(target=_watchdog, daemon=True)
    watchdog.start()

    proc.wait()
    reader.join(timeout=5)
    watchdog.join(timeout=2)

    elapsed = round(time.time() - task_started)
    _runtime["last_task_duration_secs"] = elapsed

    output = "\n".join(output_lines).strip()
    # Scan plain assistant text (not stream-json wrapper) for RESOLVED/NEEDS_HUMAN
    text_lines = assistant_text_lines

    # ── interpret kill reason ─────────────────────────────────────────────────
    if kill_reason:
        reason = kill_reason[0]
        if reason == "step_timeout":
            if not first_output[0]:
                msg = (f"no output within {INITIAL_TIMEOUT_SECS}s of launch "
                       f"(Claude cold-start timeout)")
            else:
                msg = (f"step stalled — no output for {STEP_TIMEOUT_SECS}s "
                       f"(last step: '{current_step[0]}')")
            log(f"    WATCHDOG: {msg}")
            _finish_task_checklist("failed")
            return "STEP_TIMEOUT", msg, ""
        else:
            msg = f"exceeded {TASK_TIMEOUT_SECS}s hard cap (last step: '{current_step[0]}')"
            log(f"    WATCHDOG: {msg}")
            _finish_task_checklist("failed")
            return "TOTAL_TIMEOUT", msg, ""

    # ── scan output for RESOLVED / NEEDS_HUMAN ────────────────────────────────
    status = "ERROR"
    context = ""
    for i, line_text in enumerate(text_lines[-20:], start=max(0, len(text_lines) - 20)):
        stripped = line_text.strip()
        if stripped == "RESOLVED":
            status = "RESOLVED"
            if i + 1 < len(text_lines) and text_lines[i + 1].startswith("Context:"):
                context = text_lines[i + 1][len("Context:"):].strip()
            break
        elif stripped == "NEEDS_HUMAN":
            status = "NEEDS_HUMAN"
            if i + 1 < len(text_lines) and text_lines[i + 1].startswith("Reason:"):
                context = text_lines[i + 1][len("Reason:"):].strip()
            break

    if status == "RESOLVED":
        _finish_task_checklist("done")
    else:
        _finish_task_checklist("failed")

    return status, output, context


# ── reply helpers ─────────────────────────────────────────────────────────────

def reply_inline(pr_number: int, comment_id: int, body: str):
    try:
        gh_post(
            f"repos/{REPO}/pulls/{pr_number}/comments",
            body=f"{body}\n{BOT_MARKER}",
            in_reply_to=str(comment_id),
        )
    except Exception as exc:
        log(f"  WARNING: could not post inline reply — {exc}")


def reply_issue(pr_number: int, body: str):
    try:
        gh_post(
            f"repos/{REPO}/issues/{pr_number}/comments",
            body=f"{body}\n{BOT_MARKER}",
        )
    except Exception as exc:
        log(f"  WARNING: could not post issue reply — {exc}")


def build_reply(status: str, sha: str, context: str) -> str:
    """Build the reply comment body with context about what was done."""
    if status == "RESOLVED":
        base = f"✅ Resolved in `{sha}`."
        if context:
            base += f"\n\n{context}"
        return base
    elif status == "NEEDS_HUMAN":
        base = "🤔 Needs human review."
        if context:
            base += f"\n\n{context}"
        return base
    elif status == "STEP_TIMEOUT":
        base = f"⏱️ Step timed out ({STEP_TIMEOUT_SECS}s with no output)."
        if context:
            base += f"\n\n{context}"
        return base
    elif status == "TOTAL_TIMEOUT":
        base = f"⏱️ Task exceeded the {TASK_TIMEOUT_SECS // 3600}h hard cap."
        if context:
            base += f"\n\n{context}"
        return base
    return "⚠️ Resolution attempt failed — see bot log."


def post_preview_link(pr_number: int, branch: str, state: dict):
    """Post a preview URL comment once per PR (first time we see it)."""
    key = f"preview-posted-{pr_number}"
    if key in state["handled"]:
        return
    slug = branch.replace("article/", "").strip("/")
    if not slug or "/" in slug:
        return
    url = f"{PREVIEW_BASE}/{slug}/"
    body = (
        f"📄 **Preview:** [{url}]({url})\n\n"
        f"Renders the article directly — no download needed. "
        f"Updates automatically after each resolved comment."
    )
    reply_issue(pr_number, body)
    state["handled"].append(key)
    save_state(state)
    log(f"  Posted preview link for PR#{pr_number}: {url}")


# ── next-article trigger ──────────────────────────────────────────────────────

NEXT_ARTICLE_HANDOFF = """\
You are VM-Claude on {worktree_path} (guyhizkiau/kb_generation).
The serving copy at {repo_path} stays on main — do all work in this worktree.
Your task: write the next KB article in the pipeline, following WORKFLOW.md exactly.

Read WORKFLOW.md fully before starting. It is the authoritative spec.

## Article to write

Cluster : {cluster}
Slug    : {slug}
Title   : {title}
Branch  : article/{slug}

Find the full plan entry in editorial/ARTICLES_PLAN.md (search for the title).

## Mandatory rules from prior feedback

### Competitor research (ALWAYS do this — no exceptions)

Review AT LEAST 2 competitor articles on this topic, ideally 3-4.
Vendor priority: Egnyte → Virtru → DocSend/Dropbox → Vera → HubSpot.
Only skip a vendor if you genuinely cannot find a relevant article after searching.

For each vendor:
1. Open the vendor's KB in Playwright headless (/opt/specterx-kb-venv/bin/python3)
2. Search for the topic
3. Navigate to the most relevant article
4. Extract a coverage checklist (what they covered, NOT their wording)
5. Save to references/competitors/<vendor>/<slug>.md with YAML front matter
6. Update references/competitors/INDEX.json

### Internal sources (check BOTH locations)

When doing the internal sources research step, grep BOTH:
- references/internal/
- product/  (especially product/COMPONENT_TAXONOMY.md and component-records/)

These product records and PRDs count as internal sources.

### Writing style

Follow editorial/STYLE_GUIDE.md at all times. Key rules:
- No em dashes (—) in article prose. Break into two sentences instead.
- Run python3 pipeline/render_html.py articles/{slug}/ — writes {slug}.html AND
  {slug}-zendesk.html (body-only, inline styles). Commit both files in the PR.
- No <title> tag (renderer omits it; ZenDesk re-injects it).
- HTML layout: <h1> first, meta bar (audience + reading time) second.
- After rendering, run python3 pipeline/build_index.py and commit articles/index.html.

### Codebase

Use ~/specterx-codebase/web-client/ and ~/specterx-codebase/admin-web-client/
for UI strings, feature flags, and error messages. These are now available.

## Pipeline phases

Follow the same 6-phase structure as the previous article:
1. Initialize structure if not already done (canon/, clusters/, etc.)
2. Research (competitor coverage 2-4 vendors, internal sources incl. product/, UI recon)
2a. Cross-linking pass (WORKFLOW.md §7.2):
    - Scan all approved articles/*/final.md for back-link opportunities.
    - Add this new article to Related articles sections where relevant.
    - Hyperlink the first mention of this article's topic in previous article bodies.
    - Re-render affected article.html files. Commit with prefix 'cross-link:'.
3. Draft (articles/{slug}/draft-1.md)
4. Test via Playwright
5. Revise to draft-2.md, then run the voice pass to produce final.md:
   Run: python3 writer/run_claude_code.py --article {slug} --phase voice-pass
   The voice pass (pipeline/prompts/04a-voice-pass.md) enforces
   editorial/STYLE_GUIDE.md §2.4, §3, §10, §13, §13a, §14 — it
   varies the opener, applies contractions, fixes troubleshooting
   headers to be symptom-first, and strips internal QA metadata.
   Do NOT add `last-validated:` to YAML front matter or a
   `*Last validated against …*` footer — the style guide bans them
   from customer copy.
6. Render HTML and open PR (WORKFLOW.md §9.3a + §9.3b):
   Run: python3 pipeline/render_html.py articles/{slug}/
   This produces TWO files:
     - articles/{slug}/{slug}.html         (standalone preview)
     - articles/{slug}/{slug}-zendesk.html (body-only, inline-styled for ZenDesk)
   Rules enforced by the renderer:
   - No <title> tag (ZenDesk re-injects it)
   - <h1> first inside <main>, meta bar (audience + reading time) second
   - No em dashes (—) in prose (editorial/STYLE_GUIDE.md §13a)
   After rendering, regenerate the overview:
     python3 pipeline/build_index.py

Commit {slug}.html, {slug}-zendesk.html, and articles/index.html on branch article/{slug}.
PR title: "Article {num}: {title}"
PR body per WORKFLOW.md §9.4 template.

Print "DONE. PR: <url>" as the final line.
"""


def trigger_next_article(merged_slug: str, state: dict):
    """After an article PR merges, determine and start the next article."""
    if not _QUEUE_STORE_AVAILABLE:
        log("  WARNING: queue_store not available — auto-trigger disabled")
        return
    try:
        q = _qs.load_queue()
    except FileNotFoundError:
        log("  WARNING: clusters/queue.json missing — auto-trigger disabled")
        return
    except Exception as exc:
        log(f"  ERROR loading queue: {exc}")
        return

    plan = _qs.next_article(merged_slug, q)
    action = plan["action"]
    cid = plan.get("cluster_id", "")

    if action == "unknown":
        log(f"  Merged slug '{merged_slug}' not in queue — no auto-trigger")
        return
    if action == "noop":
        log(f"  Revision-cycle re-merge for {merged_slug} — not advancing cluster")
        return
    if action == "paused":
        log(f"  Cluster {cid} is paused — not advancing")
        return
    if action in ("pause", "cluster_done"):
        notice = plan.get("pause_notice", "")
        log(f"  {notice}")
        reply_issue_to_anyone(f"\U0001f389 {notice}")
        return

    # action == "next_article"
    for art in plan["articles"]:
        _launch_next_article(art["slug"], art["title"], art["num"], cid, state)


def _article_from_queue(slug: str, q: dict | None = None) -> dict | None:
    """Look up slug in queue.json; return {slug, title, num, cluster_id} or None."""
    if q is None:
        q = _qs.load_queue()
    for cluster in q.get("clusters", []):
        for i, art in enumerate(cluster.get("articles", [])):
            if art.get("slug") == slug:
                return {
                    "slug": slug,
                    "title": art.get("title", slug),
                    "num": i + 1,
                    "cluster_id": cluster.get("id", ""),
                }
    return None


def _launch_next_article(slug: str, title: str, num: int, cluster: str, state: dict) -> bool:
    """Launch the article pipeline for one slug (detached, as ubuntu user).

    Returns True if launched, False if blocked (deduped or Claude busy).
    """
    trigger_key = f"article-triggered-{slug}"
    if trigger_key in state["handled"]:
        log(f"  Article {slug} already triggered")
        return False
    if is_claude_running():
        log(f"  Claude already running — will retry next poll to trigger {slug}")
        return False

    log(f"  Triggering next article: {slug} — {title}")

    ensure_worktree()
    handoff = NEXT_ARTICLE_HANDOFF.format(
        worktree_path=WORKTREE_PATH, repo_path=REPO_PATH,
        slug=slug, title=title, num=num, cluster=cluster,
    )
    handoff_path = Path("/home/ubuntu/next-article-handoff.md")
    handoff_path.write_text(handoff)

    launcher = (
        "#!/bin/bash\n"
        "export HOME=/home/ubuntu\n"
        'export PATH="/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin"\n'
        "set -a; source /home/ubuntu/.config/specterx-kb/.env; set +a\n"
        f"cd {WORKTREE_PATH}\n"
        "sudo -u ubuntu git checkout main\n"
        "sudo -u ubuntu git pull origin main\n"
        "PROMPT=$(cat /home/ubuntu/next-article-handoff.md)\n"
        '/usr/local/bin/claude --dangerously-skip-permissions -p "$PROMPT"'
        " >> /home/ubuntu/next-article.log 2>&1\n"
        'echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] article pipeline exited $?"'
        " >> /home/ubuntu/next-article.log\n"
    )
    launcher_path = Path("/home/ubuntu/run-next-article.sh")
    launcher_path.write_text(launcher)
    launcher_path.chmod(0o755)

    subprocess.Popen(
        ["bash", str(launcher_path)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    state["handled"].append(trigger_key)
    save_state(state)
    log(f"  ✅ Article pipeline launched for {slug}")
    return True


# ── phase auto-advancement ────────────────────────────────────────────────────
#
# Rules checked on every poll for each open article PR:
#
#   TESTING   + draft-1.md   present, test-plan.json absent  → test-plan
#   REVISING  + test-notes.md present, draft-2.md absent     → revise-from-test
#   FINALIZING+ draft-2.md   present, final.md absent        → voice-pass
#
# Each rule fires at most once per article per phase (deduped via state
# ["handled"] key "phase-auto-{slug}-{phase}").  If Claude is already
# running the launch is deferred to the next poll.

_PHASE_AUTO_RULES: list[tuple[str, str, str, str]] = [
    # (required_STATE_phase, must_exist, must_not_exist, phase_to_launch)
    ("TESTING",    "draft-1.md",    "test-plan.json", "test-plan"),
    ("REVISING",   "test-notes.md", "draft-2.md",     "revise-from-test"),
    ("FINALIZING", "draft-2.md",    "final.md",        "voice-pass"),
]


def _maybe_advance_phase(branch: str, state: dict) -> None:
    """Auto-launch the next pipeline phase for an article branch if warranted."""
    if not branch.startswith("article/"):
        return
    slug = branch[len("article/"):]

    article_dir = WORKTREE_PATH / "articles" / slug
    state_path = article_dir / "STATE"
    if not state_path.exists():
        return

    fields: dict[str, str] = {}
    for line in state_path.read_text().splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            fields[k.strip()] = v.strip()

    current_phase = fields.get("PHASE", "")

    for req_phase, req_file, blocking_file, next_phase in _PHASE_AUTO_RULES:
        if current_phase != req_phase:
            continue
        if not (article_dir / req_file).exists():
            continue
        if (article_dir / blocking_file).exists():
            continue

        trigger_key = f"phase-auto-{slug}-{next_phase}"
        if trigger_key in state["handled"]:
            continue  # already launched this phase for this article

        if is_claude_running():
            log(f"  [{slug}] Auto-advance to {next_phase} deferred — Claude busy")
            return  # retry next poll

        log(f"  [{slug}] Auto-advancing: STATE={req_phase} → launching phase {next_phase}")
        _launch_phase(slug, next_phase)
        state["handled"].append(trigger_key)
        save_state(state)
        return  # one phase at a time; re-evaluate on next poll


def _launch_phase(slug: str, phase: str):
    """Launch a specific pipeline phase for an article (detached)."""
    ensure_worktree()
    launcher = (
        "#!/bin/bash\n"
        "export HOME=/home/ubuntu\n"
        'export PATH="/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin"\n'
        "set -a; source /home/ubuntu/.config/specterx-kb/.env; set +a\n"
        f"cd {WORKTREE_PATH}\n"
        f"sudo -u ubuntu git checkout article/{slug} 2>/dev/null || "
        f"sudo -u ubuntu git checkout -b article/{slug}\n"
        f"sudo -u ubuntu git pull origin article/{slug} 2>/dev/null || true\n"
        f"/opt/specterx-kb-venv/bin/python3 writer/run_claude_code.py"
        f" --article {slug} --phase {phase}"
        f" >> /home/ubuntu/{slug}-{phase}.log 2>&1\n"
        f'echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] phase {phase} exited $?"'
        f" >> /home/ubuntu/{slug}-{phase}.log\n"
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
        fields = _qs.article_state_fields(slug)
        if not fields:
            return {"ok": False, "error": f"no STATE file for {slug}"}

        annotations: list = []
        if issue:
            try:
                r = subprocess.run(
                    ["gh", "api", f"repos/{REPO}/issues/{issue}/comments"],
                    capture_output=True, text=True,
                )
                if r.returncode == 0:
                    comments = json.loads(r.stdout)
                    for c in comments:
                        body_text = c.get("body", "")
                        m = re.search(r"```json\n(.*?)\n```", body_text, re.DOTALL)
                        if m:
                            try:
                                annotations.append(json.loads(m.group(1)))
                            except json.JSONDecodeError:
                                pass
            except Exception as exc:
                log(f"  WARNING: could not fetch issue {issue} annotations: {exc}")

        _fb.write_feedback(slug, annotations)

        ensure_worktree()
        branch = f"article/{slug}"
        git_worktree("checkout", branch, check=False)
        git_worktree("pull", "origin", branch, check=False)

        state_path = WORKTREE_PATH / "articles" / slug / "STATE"
        try:
            rc = int(fields.get("REVISION_CYCLE", "0"))
        except ValueError:
            rc = 0

        _qs.write_state_fields(state_path, {
            "PHASE": "REVISING",
            "REVISION_CYCLE": str(rc + 1),
            "FEEDBACK_ISSUE": issue,
        })

        if not is_claude_running():
            _launch_phase(slug, "revise-from-feedback")
        else:
            log(f"  Claude running — queued feedback launch for {slug}")
            _manual_trigger_set.append({"slug": slug, "reason": "feedback-launch", "issue": issue})

        return {"ok": True, "reason": reason,
                "phase": "revise-from-feedback",
                "revision_cycle": rc + 1}

    return {"ok": False, "error": f"unknown reason '{reason}'"}


def _handle_merge(data: dict) -> dict:
    """Merge the open article PR for *slug* and refresh the serving tree."""
    if not _ghq:
        return {"ok": False, "error": "gh_queue not available"}
    slug = (data.get("slug") or "").strip()
    pr_number = data.get("pr_number")
    if pr_number is not None:
        pr_number = int(pr_number)
    result = _ghq.merge_article_pr(slug, pr_number=pr_number, repo=REPO)
    if not result.get("ok"):
        return result

    log(f"  Ghostwriter merged PR#{result['pr_number']} for {slug}")
    try:
        git("pull", "origin", "main", check=False)
        ensure_worktree()
        git_worktree("checkout", "main", check=False)
        git_worktree("pull", "origin", "main", check=False)
    except Exception as exc:
        log(f"  WARNING: post-merge git pull failed: {exc}")

    state = load_state()
    try:
        check_merged_prs(state)
    except Exception as exc:
        log(f"  WARNING: post-merge check_merged_prs failed: {exc}")
    _poll_now.set()
    return result


def reply_issue_to_anyone(body: str):
    """Post a general notice on the most recent open/merged article PR."""
    try:
        prs = gh_json("pr", "list", "--repo", REPO,
                      "--json", "number", "--state", "all", "--limit", "3")
        if prs:
            reply_issue(prs[0]["number"], body)
    except Exception as exc:
        log(f"  WARNING: could not post general notice — {exc}")


# ── merged PR monitoring ──────────────────────────────────────────────────────

def check_merged_prs(state: dict):
    """Detect recently merged article PRs and trigger the next article."""
    try:
        merged = gh_json(
            "pr", "list", "--repo", REPO,
            "--json", "number,headRefName,mergedAt",
            "--state", "merged", "--limit", "10"
        )
    except Exception as exc:
        log(f"  ERROR fetching merged PRs: {exc}")
        return

    for pr in merged:
        branch = pr["headRefName"]
        if not branch.startswith("article/"):
            continue

        slug = branch.replace("article/", "").strip("/")
        merge_key = f"merge-handled-{pr['number']}"

        if merge_key in state["handled"]:
            continue

        log(f"  Detected merged article PR#{pr['number']}: {branch}")
        state["handled"].append(merge_key)
        save_state(state)

        # Refresh serving tree (main) and reset worktree after merge
        try:
            git("pull", "origin", "main", check=False)
            ensure_worktree()
            git_worktree("checkout", "main", check=False)
            git_worktree("pull", "origin", "main", check=False)
        except Exception:
            pass

        # If REVISION_CYCLE > 0 this is a feedback re-merge: mark PUBLISH_STALE
        if _QUEUE_STORE_AVAILABLE:
            try:
                sp = _qs.article_state_path(slug)
                fields = _qs.read_state_fields(sp)
                rc = int(fields.get("REVISION_CYCLE", "0"))
                if rc > 0:
                    _qs.write_state_fields(sp, {"PUBLISH_STALE": "true"})
                    log(f"  Marked {slug} PUBLISH_STALE (revision cycle {rc})")
            except Exception as exc:
                log(f"  WARNING: could not check REVISION_CYCLE for {slug}: {exc}")

        trigger_next_article(slug, state)


# ── open PR processing ────────────────────────────────────────────────────────

def process_pr(pr_number: int, branch: str, state: dict):
    """Fetch and process all new comments on one open PR."""
    log(f"  Checking PR#{pr_number} (branch: {branch})")

    try:
        ensure_worktree()
        git_worktree("checkout", branch)
        git_worktree("pull", "origin", branch)
    except RuntimeError as exc:
        log(f"  ERROR checking out {branch} in worktree: {exc}")
        return

    post_preview_link(pr_number, branch, state)
    _maybe_advance_phase(branch, state)

    # ── inline review comments ────────────────────────────────────────────
    try:
        inline = gh_json("api", f"repos/{REPO}/pulls/{pr_number}/comments")
    except Exception as exc:
        log(f"  ERROR fetching inline comments: {exc}")
        inline = []

    for c in inline:
        cid = f"inline-{c['id']}"
        if cid in state["handled"] and cid not in _retry_set:
            continue
        _retry_set.discard(cid)
        if BOT_MARKER in c["body"]:
            state["handled"].append(cid)
            save_state(state)
            continue

        log(f"  New inline comment {c['id']} on {c.get('path','?')}:{c.get('line','?')}")
        log(f"    Body: {c['body'][:120]}")

        status, output, context = resolve_comment(pr_number, branch, c)
        log(f"    Status: {status}  Context: {context[:80]}")

        try:
            sha = git_worktree("rev-parse", "--short", "HEAD")
        except Exception:
            sha = "unknown"

        reply_inline(pr_number, c["id"], build_reply(status, sha, context))

        if status in ("STEP_TIMEOUT", "TOTAL_TIMEOUT", "ERROR"):
            log(f"    Output tail: {output[-400:]}")
            _record_failure(state, cid, pr_number, c["body"], status)
        else:
            _clear_failure(state, cid)

        state["handled"].append(cid)
        save_state(state)

    # ── issue-level (PR) comments ─────────────────────────────────────────
    try:
        issue_comments = gh_json("api", f"repos/{REPO}/issues/{pr_number}/comments")
    except Exception as exc:
        log(f"  ERROR fetching issue comments: {exc}")
        issue_comments = []

    for c in issue_comments:
        cid = f"issue-{c['id']}"
        if cid in state["handled"] and cid not in _retry_set:
            continue
        _retry_set.discard(cid)
        if BOT_MARKER in c["body"]:
            state["handled"].append(cid)
            save_state(state)
            continue

        log(f"  New issue comment {c['id']} from {c['user']['login']}")
        log(f"    Body: {c['body'][:120]}")

        c_enriched = dict(c)
        c_enriched.setdefault("path", None)
        c_enriched.setdefault("line", None)

        status, output, context = resolve_comment(pr_number, branch, c_enriched)
        log(f"    Status: {status}  Context: {context[:80]}")

        try:
            sha = git_worktree("rev-parse", "--short", "HEAD")
        except Exception:
            sha = "unknown"

        reply_issue(pr_number, build_reply(status, sha, context))

        if status in ("STEP_TIMEOUT", "TOTAL_TIMEOUT", "ERROR"):
            log(f"    Output tail: {output[-400:]}")
            _record_failure(state, cid, pr_number, c["body"], status)
        else:
            _clear_failure(state, cid)

        state["handled"].append(cid)
        save_state(state)


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
                if _ghq:
                    data = _ghq.enrich_queue_with_open_prs(data, repo=REPO)
                data["claude_running"] = is_claude_running()
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
        elif path == "/retry":
            try:
                data = self._read_json()
                cid = data["comment_id"]
                state = load_state()
                if cid in state["handled"]:
                    state["handled"].remove(cid)
                _clear_failure(state, cid)
                save_state(state)
                _retry_set.add(cid)   # also bypass in-memory handled check
                _poll_now.set()
                log(f"Control: retry requested for {cid}")
                self._respond(200, '{"ok":true}')
            except Exception as exc:
                self._respond(400, json.dumps({"error": str(exc)}))
        elif path == "/api/queue/trigger":
            try:
                data = self._read_json()
                result = _handle_trigger(data)
                code = 200 if result.get("ok") else 400
                self._respond(code, json.dumps(result))
            except Exception as exc:
                self._respond(400, json.dumps({"error": str(exc)}))
        elif path == "/api/queue/merge":
            try:
                data = self._read_json()
                result = _handle_merge(data)
                code = 200 if result.get("ok") else 400
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
    """Background git fetch so branch refs stay fresh for git show serving."""

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
    _runtime["started_at"] = _now_iso()
    _runtime["pid"] = os.getpid()

    log("=" * 60)
    log("pr-watcher daemon starting")
    log(f"Repo   : {REPO}")
    log(f"Polling: every {POLL_INTERVAL}s")
    log(f"Timeouts: step={STEP_TIMEOUT_SECS}s  task={TASK_TIMEOUT_SECS}s")
    log("=" * 60)

    _start_control_server()
    git("fetch", "--all", check=False)
    state = load_state()
    iteration = 0

    while True:
        iteration += 1
        log(f"--- Poll #{iteration} ---")
        next_poll_at = time.time() + POLL_INTERVAL
        _status_cache.update({"state": state, "iteration": iteration, "next_poll_at": next_poll_at})
        try:
            # Check merged PRs first (triggers next article)
            check_merged_prs(state)

            # Drain manual triggers queued by the control plane
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
                    if not _QUEUE_STORE_AVAILABLE:
                        _manual_trigger_set.pop(0)
                        continue
                    try:
                        q = _qs.load_queue()
                        art = _article_from_queue(slug, q)
                        if not art:
                            log(f"  Manual trigger: slug '{slug}' not in queue")
                            _manual_trigger_set.pop(0)
                            continue
                        if _launch_next_article(
                            art["slug"], art["title"], art["num"],
                            art["cluster_id"], state,
                        ):
                            _manual_trigger_set.pop(0)
                    except Exception as exc:
                        log(f"  ERROR in manual trigger for {slug}: {exc}")
                        _manual_trigger_set.pop(0)
                else:
                    _manual_trigger_set.pop(0)

            # Then process open PRs
            prs = gh_json("pr", "list", "--repo", REPO,
                          "--json", "number,headRefName", "--state", "open")
            log(f"Open PRs: {[p['number'] for p in prs]}")
            _runtime["last_poll_open_prs"] = [
                {"number": p["number"], "branch": p["headRefName"]} for p in prs
            ]

            for pr in prs:
                process_pr(pr["number"], pr["headRefName"], state)

            _runtime["last_error"] = None

        except Exception as exc:
            log(f"ERROR in poll loop: {exc}")
            _runtime["last_error"] = {"message": str(exc), "at": _now_iso()}

        write_status(state, iteration, next_poll_at)
        triggered = _poll_now.wait(timeout=POLL_INTERVAL)
        _poll_now.clear()
        if triggered:
            log("Poll triggered on demand — skipping scheduled wait")


if __name__ == "__main__":
    main()
