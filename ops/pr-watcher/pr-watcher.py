#!/usr/bin/env python3
"""
pr-watcher.py — autonomous PR comment resolver + article pipeline driver

Polls open PRs every 5 minutes. For each new review/issue comment from a
human, runs VM-Claude to resolve it, commits the fix, and posts a contextual
reply. Also monitors recently-merged article PRs and triggers the next article.
"""
import subprocess, json, os, pty, time, re, threading, tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from datetime import datetime, timezone

REPO          = "guyhizkiau/kb_generation"
REPO_PATH     = Path("/home/ubuntu/kb_generation")
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

# Event set by the control plane to trigger an immediate poll
_poll_now = threading.Event()

# Cluster 1 article sequence (WORKFLOW.md §5.1 — one at a time, review pause after all 3)
CLUSTER_1_ARTICLES = [
    ("01-log-in-to-specterx",   "Log in to the SpecterX web platform"),
    ("02-set-or-reset-password", "Set or reset your password"),
    ("03-what-is-specterx",      "What is SpecterX?"),
]


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
    r = subprocess.run(
        ["sudo", "-u", "ubuntu", "git", *args],
        cwd=REPO_PATH, capture_output=True, text=True
    )
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{r.stderr.strip()}")
    return r.stdout.strip()


def is_claude_running() -> bool:
    """Return True if a claude process is already running on the VM."""
    r = subprocess.run(["pgrep", "-f", "claude.*--dangerously"], capture_output=True)
    return r.returncode == 0


# ── resolution engine ─────────────────────────────────────────────────────────

RESOLUTION_PROMPT_TEMPLATE = """\
You are the KB pipeline bot resolving a PR review comment on the repository at
/home/ubuntu/kb_generation. The branch {branch} is already checked out and
up to date. Do NOT switch branches. Do NOT open PRs. Do NOT merge anything.

## Comment details

PR number : {pr_number}
File      : {path}
Line      : {line}
Comment   : {body}

## What you must do

1. Read the file(s) relevant to the comment carefully.
2. Make exactly the changes needed to address the reviewer's feedback.
   Typical changes for KB articles:
   - Reword a step for clarity or accuracy
   - Fix or expand the competitor coverage (if the comment is about research gaps,
     scrape 2-4 competitor KBs using Playwright headless and update the research files)
   - Add or correct a note, troubleshooting entry, or callout
   - Fix terminology using canonical labels from ui-glossary.md
   - Expand the internal sources check: grep BOTH references/internal/ AND
     the product/ directory (product/COMPONENT_TAXONOMY.md, component-records/, etc.)
     for relevant content

3. `git add` only the changed file(s).
4. `git commit -m "fix(article): resolve PR#{pr_number} comment — <5-word summary>"`
5. `git push origin {branch}`
6. On the LAST two lines of your output, print exactly:
   RESOLVED
   Context: <1-3 sentences explaining specifically what was changed and why>

   Or if you cannot resolve the comment:
   NEEDS_HUMAN
   Reason: <explanation of what human action is needed>

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

When a comment asks for a wording or structural change, apply the
style guide rules to the change. If the comment itself asks for
something the style guide forbids, leave a brief reply explaining and
ask for confirmation before pushing the change.

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
        branch=branch, pr_number=pr_number, path=path, line=line, body=body,
        step_timeout=STEP_TIMEOUT_SECS, task_timeout=TASK_TIMEOUT_SECS,
        tool_timeout=TOOL_TIMEOUT_SECS,
    )

    output_lines: list[str] = []
    assistant_text_lines: list[str] = []   # only plain assistant text (for RESOLVED/NEEDS_HUMAN scan)
    kill_reason: list[str] = []   # mutable container so threads can write it
    current_step: list[str] = ["(starting)"]

    # Truncate task log. Reader thread will populate it.
    TASK_LOG_FILE.write_text("")

    # Track task in runtime state for dashboard
    task_started = time.time()
    _runtime["current_task"] = {
        "pr_number": pr_number,
        "comment_id": comment.get("id"),
        "step": current_step[0],
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
            env=claude_env, cwd=str(REPO_PATH),
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

    def _set_step(step: str):
        current_step[0] = step
        _runtime["current_task"] = {**_runtime["current_task"], "step": step}
        log(f"    → STEP: {step}")
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
                        if sub.startswith("STEP:"):
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
    _runtime["current_task"] = None
    _runtime["last_task_duration_secs"] = elapsed
    flush_status()  # clear active task from dashboard

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
            return "STEP_TIMEOUT", msg, ""
        else:
            msg = f"exceeded {TASK_TIMEOUT_SECS}s hard cap (last step: '{current_step[0]}')"
            log(f"    WATCHDOG: {msg}")
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
You are VM-Claude on /home/ubuntu/kb_generation (guyhizkiau/kb_generation, main branch).
Your task: write the next KB article in the pipeline, following WORKFLOW.md exactly.

Read WORKFLOW.md fully before starting. It is the authoritative spec.

## Article to write

Cluster : 01-login
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
    """After an article PR merges, determine and start the next article in the cluster."""
    slugs = [s for s, _ in CLUSTER_1_ARTICLES]
    titles = {s: t for s, t in CLUSTER_1_ARTICLES}

    if merged_slug not in slugs:
        log(f"  Merged slug '{merged_slug}' not in cluster 1 — no auto-trigger")
        return

    idx = slugs.index(merged_slug)
    if idx >= len(slugs) - 1:
        log("  All cluster 1 articles merged — awaiting style extraction review pause")
        reply_issue_to_anyone(
            "🎉 All cluster 1 articles merged. "
            "Per WORKFLOW.md §5.1, stopping now for style extraction and Guy's review "
            "before proceeding to cluster 2."
        )
        return

    next_slug = slugs[idx + 1]
    next_title = titles[next_slug]
    next_num = idx + 2  # 1-indexed

    trigger_key = f"article-triggered-{next_slug}"
    if trigger_key in state["handled"]:
        log(f"  Article {next_slug} already triggered")
        return

    if is_claude_running():
        log(f"  Claude already running — will retry next poll to trigger {next_slug}")
        return

    log(f"  Triggering next article: {next_slug} — {next_title}")

    handoff = NEXT_ARTICLE_HANDOFF.format(
        slug=next_slug, title=next_title, num=next_num
    )
    handoff_path = Path("/home/ubuntu/next-article-handoff.md")
    handoff_path.write_text(handoff)

    # Launch VM-Claude as ubuntu user, log to next-article.log
    launcher = f"""#!/bin/bash
export HOME=/home/ubuntu
export PATH="/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin"
set -a; source /home/ubuntu/.config/specterx-kb/.env; set +a
cd /home/ubuntu/kb_generation
sudo -u ubuntu git checkout main
sudo -u ubuntu git pull origin main
PROMPT=$(cat /home/ubuntu/next-article-handoff.md)
/usr/local/bin/claude --dangerously-skip-permissions -p "$PROMPT" >> /home/ubuntu/next-article.log 2>&1
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] article pipeline exited $?" >> /home/ubuntu/next-article.log
"""
    launcher_path = Path("/home/ubuntu/run-next-article.sh")
    launcher_path.write_text(launcher)
    launcher_path.chmod(0o755)

    subprocess.Popen(
        ["bash", str(launcher_path)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True
    )

    state["handled"].append(trigger_key)
    save_state(state)
    log(f"  ✅ Article pipeline launched for {next_slug}")


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

        # Switch back to main after the merge
        try:
            git("checkout", "main", check=False)
            git("pull", "origin", "main", check=False)
        except Exception:
            pass

        trigger_next_article(slug, state)


# ── open PR processing ────────────────────────────────────────────────────────

def process_pr(pr_number: int, branch: str, state: dict):
    """Fetch and process all new comments on one open PR."""
    log(f"  Checking PR#{pr_number} (branch: {branch})")

    try:
        git("checkout", branch)
        git("pull", "origin", branch)
    except RuntimeError as exc:
        log(f"  ERROR checking out {branch}: {exc}")
        return

    post_preview_link(pr_number, branch, state)

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
            sha = git("rev-parse", "--short", "HEAD")
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
            sha = git("rev-parse", "--short", "HEAD")
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

class _ControlHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # silence default access log

    def do_POST(self):
        if self.path == "/poll-now":
            _poll_now.set()
            log("Control: poll-now requested via HTTP")
            self._respond(200, '{"ok":true}')
        elif self.path == "/retry":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b""
            try:
                data = json.loads(body)
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
        else:
            self._respond(404, '{"error":"not found"}')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, code, body):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(data)


def _start_control_server():
    srv = HTTPServer(("127.0.0.1", CONTROL_PORT), _ControlHandler)
    t = threading.Thread(target=srv.serve_forever, daemon=True, name="control-http")
    t.start()
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
