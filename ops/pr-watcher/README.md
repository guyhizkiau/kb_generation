# pr-watcher — status-driven pipeline daemon

The pr-watcher daemon is the long-running orchestrator for the KB
article pipeline on the EC2 VM. It:

- Polls `articles/*/STATE` on a fixed interval and **dispatches** the
  next automated phase for the active article (`dispatcher.py`).
- Serves the Ghostwriter control-plane HTTP API (approve, publish,
  request-changes, feedback, article preview).
- Streams Claude's live output to a dashboard so a human can see what
  the bot is doing in real time.
- Survives long-running tools (Playwright/Chrome runs of 10–30 min)
  without false-positive timeouts.

All article work lives on **`main`** — there is no GitHub PR polling.

> **Historical note:** Earlier versions polled open `article/<slug>` PRs
> for review comments and advanced the queue on merge. That flow is
> retired; review is `IN_REVIEW` → approve/publish on `main`.

This document is the operational source of truth. **Read it end-to-end
before changing any of the files in this directory or before debugging
a stuck bot.**

---

## URLs (VM: 18.192.122.48)

| URL | Purpose |
|---|---|
| `http://18.192.122.48/` | Article browser (renders `articles/index.html`) |
| `http://18.192.122.48/ghostwriter/` | Ghostwriter SPA (queue, review, feedback) |
| `http://18.192.122.48/status/` | Live dashboard (`status.json` + live task log) |
| `http://18.192.122.48/health` | `systemctl show` JSON, updated every 60 s |
| `http://18.192.122.48/log` | Full poll log (plain text) |
| `http://18.192.122.48/task-log` | Live Claude output for the current task (plain text, truncated at task start) |
| `http://18.192.122.48/poll-now` | `POST` — wake the poll loop immediately |

Control-plane routes (`/api/*`) are proxied to the localhost HTTP server
inside the daemon (`CONTROL_PORT = 9191`).

---

## Architecture

```
systemd ─► start-pr-watcher.sh ─► pr-watcher.py
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
              poll loop          dispatcher.py      127.0.0.1:9191
           (every 30 s)         (phase dispatch)    control plane
                    │                  │                  │
                    │                  ├── writer/run_claude_code.py
                    │                  ├── tester/runner.py
                    │                  └── pipeline/publish (on approve)
                    │
                    └── claude (PTY, own process group)

nginx serves:
  - /home/ubuntu/kb_generation/articles/     (preview tree on main)
  - /home/ubuntu/pr-watcher-web/              (dashboard + Ghostwriter build)
  - proxy_pass to 127.0.0.1:9191              (control API)
```

### Single branch on `main`

The repo checkout at `/home/ubuntu/kb_generation` stays on **`main`**.
Pipeline phases commit article files directly to `main` via a git
worktree at `/home/ubuntu/kb_generation-work` (same branch, isolated
working tree for daemon edits).

Reviewer annotations default to `articles/<slug>/feedback.json` in the
repo; on the VM, `GHOSTWRITER_FEEDBACK_DIR=/home/ubuntu/ghostwriter-feedback`
stores them outside the serving tree.

### Dispatcher (`dispatcher.py`)

Each poll iteration (when Claude is not already running):

1. **`active_article()`** — if a slug is in an active `PHASE`, dispatch
   the next step for that slug only.
2. **`dispatch_idle()`** — if nothing is active: optionally queue
   re-verification for a stale `PUBLISHED` article, else transition the
   next `QUEUED` slug from `clusters/queue.json` to `RESEARCHING`.

| `PHASE` | Dispatcher action |
|---|---|
| `QUEUED` | Launch `research` |
| `RESEARCHING` | Resume `research` if artifact missing |
| `DRAFTING` | Launch `draft` |
| `TESTING` | Launch `test-plan`, then `tester/runner.py` |
| `REVISING` | Launch `revise-from-test` or `revise-from-feedback` |
| `FINALIZING` | Launch `voice-pass` → `IN_REVIEW` |
| `APPROVED` | Retry publish adapter |
| `IN_REVIEW` | *(human review — no auto step)* |

Serial rule: only one article may be in `ACTIVE_PHASES` at a time.

### Control-plane API (`127.0.0.1:9191`)

| Method | Path | Body | Effect |
|---|---|---|---|
| `POST` | `/poll-now` | — | Wake poll loop |
| `POST` | `/api/queue/trigger` | `{"reason":"feedback"\|"manual", "slug":"…"}` | Start feedback revision or manual research |
| `POST` | `/api/queue/approve` | `{"slug":"…", "reviewer":"guy"}` | `IN_REVIEW` → `APPROVED` → publish → `PUBLISHED` |
| `POST` | `/api/queue/publish` | `{"slug":"…"}` | Retry publish for `APPROVED` article |
| `POST` | `/api/queue/request-changes` | `{"slug":"…", "reason":"…"}` | `IN_REVIEW` or `PUBLISHED` → `REVISING` |
| `POST` | `/api/feedback` | annotation JSON + `slug` | Append Ghostwriter annotation |
| `DELETE` | `/api/feedback?slug=…&id=…` | — | Remove one annotation |
| `GET` | `/api/articles/<slug>/preview` | — | HTML preview for Ghostwriter reader |
| `GET`/`PUT` | `/api/queue` | queue JSON | Read/write `clusters/queue.json` |

**Approve flow** (`_handle_approve`):

1. `transition(slug, "APPROVED", {APPROVED_BY, APPROVED_AT})`
2. Commit STATE on `main`
3. `pipeline.publish.publish_article(slug)` — render HTML, rebuild index,
   `transition(slug, "PUBLISHED")`
4. Commit rendered outputs on `main`

If publish fails, the article stays at `APPROVED`; retry with
`/api/queue/publish`.

### Files (canonical source in this directory)

| File | Role |
|---|---|
| `pr-watcher.py` | Daemon + control plane. Deploy to `/home/ubuntu/pr-watcher.py`. |
| `dispatcher.py` | Status-driven phase dispatch |
| `queue_store.py` | Queue I/O, STATE helpers |
| `feedback_store.py` | Ghostwriter annotation store wrapper |
| `preview_transform.py` | HTML preview patching for Ghostwriter |
| `pr-watcher.service` | systemd unit |
| `dashboard/index.html` | Live status dashboard |
| `README.md` | This document |

### Files on the VM only (not in git)

| Path | Purpose |
|---|---|
| `/home/ubuntu/pr-watcher.py` | Deployed daemon copy |
| `/home/ubuntu/kb_generation-work/` | Git worktree for daemon commits on `main` |
| `/home/ubuntu/ghostwriter-feedback/` | Optional annotation store override |
| `/home/ubuntu/pr-watcher-state.json` | Dispatcher dedupe keys (`handled`, etc.) |
| `/home/ubuntu/pr-watcher.log` | Full poll log |
| `/home/ubuntu/pr-watcher-task.log` | Live Claude output (truncated per task) |
| `/home/ubuntu/pr-watcher-web/status.json` | Dashboard data |
| `/home/ubuntu/.config/specterx-kb/.env` | Credentials (mode 600, never committed) |

---

## Deploy

Deploy via **AWS SSM `AWS-RunShellScript`**, not SSH. SSM runs as root —
use `sudo -u ubuntu` for git and HOME-sensitive commands.

Standard rolling deploy:

```bash
# 1. Pull latest on VM
sudo -u ubuntu bash -c "cd /home/ubuntu/kb_generation && git fetch origin <branch> && git checkout origin/<branch> -- ops/pr-watcher/ store/ pipeline/ writer/ tester/"

# 2. Copy daemon + dashboard into place
cp /home/ubuntu/kb_generation/ops/pr-watcher/pr-watcher.py    /home/ubuntu/pr-watcher.py
cp /home/ubuntu/kb_generation/ops/pr-watcher/dashboard/index.html /home/ubuntu/pr-watcher-web/index.html

# 3. Clear stale Claude lock files
find /home/ubuntu/.claude/tasks/ -name ".lock" -delete

# 4. Restart
systemctl restart pr-watcher

# 5. Verify
sleep 4
systemctl is-active pr-watcher
curl -s http://localhost/health | head -c 200
```

First-time install: copy `pr-watcher.service`, enable the health timer,
configure nginx (`/status/`, `/health`, `/log`, `/task-log`, proxy to
`:9191`). See historical deploy blocks in git history if needed.

---

## How the daemon talks to Claude

These design choices inside `pr-watcher.py` are load-bearing — do not
revert without understanding why they exist.

### 1. PTY for stdout (`pty.openpty()`)

Node block-buffers stdout without a TTY. A pseudo-TTY gives line-buffered
output so the dashboard updates during long runs.

### 2. `--output-format stream-json`

Emits per-tool events so the dashboard shows active tools and the
per-tool deadline can extend during Playwright runs.

### 3. Process group + `killpg`

`preexec_fn=os.setpgrp` (not `start_new_session`) keeps the PTY working
while allowing `killpg` to tear down claude + chrome on watchdog timeout.

### 4. Three timeout dials

| Constant | Value | Triggers on |
|---|---|---|
| `STEP_TIMEOUT_SECS` | 120 | No event for 2 min outside a tool call |
| `TOOL_TIMEOUT_SECS` | 1800 | Single tool call > 30 min |
| `TASK_TIMEOUT_SECS` | 3600 | Whole task > 1 hour |

### 5. `flush_status()` on every event

Keeps `status.json` current during long Claude runs.

---

## Failure modes

Work down this list when the bot stops making progress.

### A — Task log empty for minutes

1. `curl -s http://localhost/status/status.json | jq .current_task`
2. Check PTY: `ls -la /proc/$(pgrep -f "claude.*--dangerously" | head -1)/fd/{0,1,2}`
3. Clear stale locks: `find /home/ubuntu/.claude/tasks/ -name ".lock" -delete`

### B — Article stuck at `BLOCKED`

Read `articles/<slug>/STATE` → `BLOCKED_REASON`. Fix the underlying issue
(research gate, missing artifact, phase failure) then unblock via
`store.machine.unblock()` or manual STATE edit with care.

### C — Approve returned 409

Article must be `IN_REVIEW`. Check `PHASE` in STATE and Ghostwriter queue.

### D — Publish failed, stuck at `APPROVED`

`POST /api/queue/publish {"slug":"…"}` or wait for dispatcher retry on
next poll.

### E — `poll-now` / approve seem no-op

Daemon may be mid-Claude-task. Actions take effect when `is_claude_running()`
returns false.

---

## Maintenance

- Rotate `/home/ubuntu/pr-watcher.log` if > ~50 MB.
- Monthly: garbage-collect old `~/.claude/tasks/` directories.
- After Claude version bumps: verify `stream-json` event parsing still
  works (`pr-watcher-task.log` should show output within ~10 s of task start).

---

## See also

- [WORKFLOW.md](../../WORKFLOW.md) §9–§14 — review, approve, publish, state machine
- [CLAUDE.md](../../CLAUDE.md) — session rules for manual runs
- `store/machine.py` — authoritative `PHASE` transition table
- `editorial/STYLE_GUIDE.md` — canon enforced during voice-pass and feedback revision

---

## Ghostwriter SPA

Build and deploy: see `ops/ghostwriter/README.md`. The SPA calls the
control-plane endpoints above (`/api/queue/approve`, `/api/queue/request-changes`,
`/api/feedback`, etc.) — it does not talk to GitHub for article review.

`clusters/queue.json` must exist on `main` before auto-advance works;
without it the daemon logs "auto-trigger disabled" and does not crash.
