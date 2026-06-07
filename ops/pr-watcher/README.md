# pr-watcher — autonomous PR/article bot

The pr-watcher daemon is the long-running orchestrator that drives the
KB pipeline once a cluster is in flight. It:

- Polls open PRs for new review comments and resolves them by invoking
  Claude Code with the affected article checked out.
- Watches for merges and triggers the next article in the cluster.
- Streams Claude's live output to a dashboard so a human can see what
  the bot is doing in real time.
- Survives long-running tools (Playwright/Chrome runs of 10–30 min)
  without false-positive timeouts.

This document is the operational source of truth. **Read it end-to-end
before changing any of the files in this directory or before debugging
a stuck bot.** Every section below was written because something
broke or went silent during a real run — they are not theoretical.

---

## URLs (VM: 18.192.122.48)

| URL | Purpose |
|---|---|
| `http://18.192.122.48/` | Article browser (renders `articles/index.html`) |
| `http://18.192.122.48/status/` | Live dashboard (status.json + live task log) |
| `http://18.192.122.48/health` | `systemctl show` JSON, updated every 60 s |
| `http://18.192.122.48/log` | Full poll log (plain text) |
| `http://18.192.122.48/task-log` | Live Claude output for the current task (plain text, truncated at task start) |
| `http://18.192.122.48/poll-now` | `POST` — fire an immediate poll. Used by the dashboard's "Poll now" button. |
| `http://18.192.122.48/retry` | `POST {"comment_id": "issue-N"}` — re-process a comment that previously failed. Used by the dashboard's Retry button on the Failed Comments panel. |

`/poll-now` and `/retry` go through nginx to the localhost-only control
HTTP server inside the daemon (`CONTROL_PORT = 9191`).

---

## Architecture

```
systemd ─► start-pr-watcher.sh ─► pr-watcher.py ─► [forks per poll]
                                       │              │
                                       │              └── claude (in its own process group, via os.setpgrp)
                                       │                    │
                                       │                    └── tool subprocesses (bash → playwright → chrome)
                                       │
                                       └── 127.0.0.1:9191 control plane (poll-now, retry)

systemd timer (every 60 s) ─► pr-watcher-health.service ─► write_health.sh ─► /home/ubuntu/pr-watcher-web/health.json

nginx serves:
  - /home/ubuntu/kb_generation/articles/      (the published preview tree)
  - /home/ubuntu/pr-watcher-web/               (dashboard + status.json + health.json)
  - /home/ubuntu/pr-watcher.log                at /log
  - /home/ubuntu/pr-watcher-task.log           at /task-log
  - proxy_pass to 127.0.0.1:9191/{poll-now,retry}
```

### Files (canonical source in this directory)

| File | Role |
|---|---|
| `pr-watcher.py` | The daemon. Copy to `/home/ubuntu/pr-watcher.py` on deploy. |
| `pr-watcher.service` | systemd unit for the daemon. |
| `pr-watcher-health.service` + `pr-watcher-health.timer` | One-shot writer of `health.json`, fired every 60 s. |
| `write_health.sh` | The one-shot script. Reads `systemctl show pr-watcher` and writes JSON. |
| `dashboard/index.html` | Self-contained dark dashboard. Polls `status.json` every 5 s and `task-log` every 3 s when a task is active. |
| `dashboard/{health,status,task-log,prwatcher-fixture.log}.json` | Local fixtures so the dashboard can be previewed via `python -m http.server` without the VM. |
| `README.md` | This document. |

### Files on the VM only (not in git)

| Path | Purpose |
|---|---|
| `/home/ubuntu/pr-watcher.py` | Deployed copy of the daemon. |
| `/home/ubuntu/pr-watcher-state.json` | Handled comment/PR IDs + `failed_comments` map. |
| `/home/ubuntu/pr-watcher.log` | The full poll log (appends forever; cap with `logrotate` if it gets big). |
| `/home/ubuntu/pr-watcher-task.log` | Live Claude output. Truncated at the start of every task. |
| `/home/ubuntu/pr-watcher-web/status.json` | Dashboard data. Atomically written every poll AND on every task event. |
| `/home/ubuntu/pr-watcher-web/health.json` | systemd status snapshot, refreshed every 60 s. |
| `/home/ubuntu/start-pr-watcher.sh` | systemd `ExecStart`. Exports `HOME`, sources `.env`, launches the daemon. |
| `/home/ubuntu/.config/specterx-kb/.env` | All credentials. Mode 600. Never committed. |

---

## Deploy

The deploy mechanism is **AWS SSM `AWS-RunShellScript`**, *not* SSH.
SSM runs as root, so use `sudo -u ubuntu` for git/gh and any
HOME-sensitive command.

```python
# Standard SSM template
import boto3, time
s = boto3.client('ssm', region_name='eu-central-1')
r = s.send_command(
    InstanceIds=['i-089861af44af098a3'],
    DocumentName='AWS-RunShellScript',
    Parameters={'commands': ['sudo -u ubuntu bash -c "cd /home/ubuntu/kb_generation && git pull"']},
)
time.sleep(6)
o = s.get_command_invocation(CommandId=r['Command']['CommandId'], InstanceId='i-089861af44af098a3')
print(o['StandardOutputContent'])
```

Standard rolling deploy of a code change:

```bash
# 1. Pull the latest code on the VM
sudo -u ubuntu bash -c "cd /home/ubuntu/kb_generation && git fetch origin <branch> && git checkout origin/<branch> -- ops/pr-watcher/"

# 2. Copy files into place
cp /home/ubuntu/kb_generation/ops/pr-watcher/pr-watcher.py    /home/ubuntu/pr-watcher.py
cp /home/ubuntu/kb_generation/ops/pr-watcher/dashboard/index.html /home/ubuntu/pr-watcher-web/index.html
cp /home/ubuntu/kb_generation/ops/pr-watcher/write_health.sh  /home/ubuntu/write_health.sh
chmod +x /home/ubuntu/write_health.sh

# 3. Clear any stale lock files before restart (see "Failure modes" below)
find /home/ubuntu/.claude/tasks/ -name ".lock" -delete

# 4. Restart the daemon (systemd kills the entire cgroup — that includes
# any in-flight claude + chrome; preserve work first if needed)
systemctl restart pr-watcher

# 5. Verify
sleep 4
systemctl is-active pr-watcher    # → active
curl -s http://localhost/health | head -c 200    # ActiveState=active, NRestarts=0
```

First-time install (systemd units, nginx routes):

```bash
# Systemd units
cp ops/pr-watcher/pr-watcher.service        /etc/systemd/system/
cp ops/pr-watcher/pr-watcher-health.service /etc/systemd/system/
cp ops/pr-watcher/pr-watcher-health.timer   /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now pr-watcher
systemctl enable --now pr-watcher-health.timer

# Directory permissions
mkdir -p /home/ubuntu/pr-watcher-web
chown -R ubuntu:ubuntu /home/ubuntu/pr-watcher-web

# nginx location blocks (in /etc/nginx/sites-enabled/articles)
# location /status/    { alias /home/ubuntu/pr-watcher-web/; index index.html; }
# location = /health   { default_type application/json; alias /home/ubuntu/pr-watcher-web/health.json; }
# location = /log      { default_type text/plain;       alias /home/ubuntu/pr-watcher.log; }
# location = /task-log { default_type text/plain;       alias /home/ubuntu/pr-watcher-task.log; }
# location = /poll-now { proxy_pass http://127.0.0.1:9191/poll-now; proxy_read_timeout 10s; }
# location = /retry    { proxy_pass http://127.0.0.1:9191/retry;    proxy_read_timeout 10s; }
nginx -t && systemctl reload nginx
```

---

## How the daemon talks to Claude — the non-obvious bits

These are the design decisions inside `pr-watcher.py` that make the bot
work, all of which were arrived at by hitting a wall. **Do not revert
any of them without understanding why they exist.**

### 1. PTY for stdout (`pty.openpty()`)

Claude is Node.js. Node block-buffers `process.stdout` (~16 KB) when it
isn't connected to a TTY. If you pipe Claude's stdout to a file or
`subprocess.PIPE`, you see nothing for tens of minutes, then a single
flush at process exit. With `pty.openpty()` we give Claude a pseudo-TTY
slave fd; Node detects `isatty()=true` and line-buffers, so every `\n`
shows up immediately. We read from the master fd in a Python thread.

Safety env vars set when running under the PTY:

```python
TERM=dumb          # suppress curses-style updates
NO_COLOR=1         # no ANSI colour codes in the log
FORCE_COLOR=0     # belt-and-braces for chalk/picocolors
CI=1               # most CLIs suppress TUI when CI=1
```

### 2. `--output-format stream-json` for tool-level visibility

PTY alone isn't enough. Claude's `-p text` mode only emits text the
*model* produces — during long tool calls (a 25-min Playwright run),
the model is silent and the dashboard sees nothing. `stream-json`
emits one JSON event per assistant message delta, tool_use, and
tool_result, so the dashboard shows the active tool in real time
(`→ Bash: …`, `→ Read: <path>`, etc.) and the per-tool deadline
mechanism can do its job (see below).

The reader thread parses each event and writes a human-readable line
to the task log. The raw stream is kept in memory for the
`RESOLVED`/`NEEDS_HUMAN` parser.

### 3. Process group + `killpg`, not session

We use `preexec_fn=os.setpgrp` (NOT `start_new_session=True`).
`setsid()` makes Claude a session leader with no controlling terminal,
which causes Claude Code to suppress its own output entirely. A new
process *group* (without a new session) keeps the PTY working AND
lets us kill the whole tree on watchdog timeout:

```python
os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
```

This SIGKILLs claude + bash + node + every chrome subprocess — without
it, watchdog kills leave hundreds of orphan chrome processes per run.

### 4. `stdin=subprocess.DEVNULL`

If Claude is launched unauthenticated and stdin is anything other than
DEVNULL, it can block waiting for `/login` input. DEVNULL guarantees
the read returns EOF immediately and the process either prints
`Not logged in · Please run /login` or proceeds.

### 5. Three timeout dials, not one

| Constant | Value | Triggers on |
|---|---|---|
| `INITIAL_TIMEOUT_SECS` | 3600 | No output at all since launch (cold start). Effectively disabled (matches task cap) because `stream-json init` arrives within seconds in practice. |
| `STEP_TIMEOUT_SECS` | 120 | No event for 2 minutes AND claude is not in a tool call. This is the "real hang" detector. |
| `TOOL_TIMEOUT_SECS` | 1800 | A single tool call has been running for more than 30 min. This is the "tool stuck" detector. |
| `TASK_TIMEOUT_SECS` | 3600 | Whole task has been running for an hour. The hard cap. |

The reader extends the per-step deadline to `TOOL_TIMEOUT_SECS` when
it sees a `tool_use` event and resets to `STEP_TIMEOUT_SECS` on any
`tool_result` or assistant text. This is what lets Playwright runs of
20+ minutes survive while still killing genuinely hung claude
sessions.

### 6. Status flush on every event (`flush_status()`)

`write_status()` previously ran only at the end of the poll loop.
That meant `status.json` was stale for the entire duration of a Claude
run, and the dashboard's Active Task widget always read "(starting)".
We now call `flush_status()` on task start, every STEP, every tool
call, and task end. The dashboard updates in real time.

### 7. The `_retry_set` for retry semantics

The `/retry` endpoint mutates `state.json` on disk (removes the
comment from `handled`, clears it from `failed_comments`). But the
daemon's in-memory `state` dict was already loaded — without a
secondary flag, the next poll skips the comment again because it's
still in the in-memory `handled`. `_retry_set` is a module-level
`set()` populated by the endpoint; the comment loops check it before
honoring the `handled` skip.

### 8. Lock file cleanup as a deploy step

Every SIGKILL'd Claude leaves a stale `.lock` file in
`~/.claude/tasks/<uuid>/`. New Claude invocations hang on those locks.
The deploy template above runs `find ... -name ".lock" -delete` before
restarting. The process-group kill (item 3) reduces but does not
eliminate this — keep the cleanup step.

---

## Failure modes and what to check

When the bot stops making progress, work down this list in order.

### A — "Claude task log is empty for minutes"

1. **Check the active task.** `curl -s http://localhost/status/status.json | jq .current_task`. If it's `null` the bot isn't running anything. If it shows a step, see B.
2. **Check the dashboard's Live output panel.** If it's empty AND status shows an active task, check the PTY (next).
3. **Verify Claude's stdout is going to the PTY.** `ls -la /proc/$(pgrep -f "claude.*--dangerously" | head -1)/fd/{0,1,2}`. Expected: fd 0 → `/dev/null`, fd 1 and fd 2 → `/dev/pts/N`. If fd 1 points to a file or a pipe, somebody changed `pty.openpty()`. Revert.
4. **Check stale lock files.** `find /home/ubuntu/.claude/tasks/ -name ".lock"`. If any exist while the bot is also running, claude is hung on them. Delete and restart.

### B — "Task hits TOTAL_TIMEOUT at exactly 3600 s with no useful output"

Means Claude got into a state where it never emitted a `tool_use`
event (or the very first one stalled), so the step deadline never
extended. In practice this has been caused by:

- **Stale lock files** (see A.4). Most common.
- **`Not logged in · Please run /login`** if the env wasn't sourced.
  Check `cat /proc/$(pgrep pr-watcher.py | head -1)/environ | tr '\0' '\n' | grep ANTHROPIC_API_KEY` — if missing, `start-pr-watcher.sh` failed to source `.env`.
- **Anthropic API rate limit / outage.** Visible as 4xx/5xx in
  `journalctl -u pr-watcher --since "1h ago" | grep -i error`.

### C — "Watchdog kills a tool that was working fine"

Means a `tool_use` event didn't extend the deadline as expected.
Check the relevant section of `pr-watcher.py` (`_format_event`):
`contains_tool_use` must be True for the deadline extension to fire.
If a tool produces output without first emitting a `tool_use` (rare),
the per-step 120 s timeout still applies.

### D — "Dashboard says HEALTHY but no tasks are running"

The dashboard reads `status.json`. `last_poll_at` should advance every
~300 s. If it stops, the daemon is alive but stuck inside the poll
loop. Check `journalctl -u pr-watcher -n 100 --no-pager`.

### E — "Retry button doesn't seem to do anything"

The endpoint returns `{"ok":true}` even when nothing happens. Two
common reasons:

1. The daemon is already mid-task. The retry only takes effect on the
   *next* poll iteration. The Poll now button has the same caveat.
2. `_retry_set` wasn't updated because the daemon process restarted
   between disk-update and next poll. Check
   `/home/ubuntu/pr-watcher.log` for `Control: retry requested for …`.

---

## Maintenance

### Weekly

- Rotate `/home/ubuntu/pr-watcher.log` if it's larger than ~50 MB. The
  `_tail_log()` function in the daemon reads only the last 40 lines, so
  size is purely a disk concern.
- Sanity-check `/home/ubuntu/pr-watcher-state.json`. If `failed_comments`
  has entries older than a week, decide whether to retry or to
  `_clear_failure()` them manually (the latter is just JSON editing).

### Monthly

- `find /home/ubuntu/.claude/tasks/ -type d -mtime +30 -exec rm -rf {} +` to
  garbage-collect old Claude session directories.

### After every Claude version bump

- `--output-format=stream-json` is documented but the event schema can
  evolve. If `_format_event()` starts emitting `{json.dumps(input)[:200]}`
  blobs for tool_use cases the parser doesn't recognize, extend the
  parser.
- PTY behaviour can change too. Cross-check by tailing
  `pr-watcher-task.log` during the next task — if it lights up within
  10 s of task start, PTY is working.

---

## See also

- `WORKFLOW.md` §9 — what the pipeline expects this bot to do during
  Stage 5 (revise → voice-pass → PR → review → merge).
- `editorial/STYLE_GUIDE.md` — the canon the bot enforces when it
  applies PR review comments.
- `pipeline/prompts/04a-voice-pass.md` — the prompt the bot runs at
  phase 5 to humanize draft prose.
- `tester/TEST_RESOURCES.md` — credentials and provisioning notes for
  test accounts used during E2E captures.

---

## Ghostwriter SPA

### Build

```bash
cd ops/ghostwriter
npm install
npm run build
# Output: ../../dist/ghostwriter/
```

### Deploy to VM

```bash
# Copy build output to the VM
rsync -avz dist/ghostwriter/ ubuntu@18.192.122.48:/home/ubuntu/pr-watcher-web/ghostwriter/

# Copy annotation libraries (one-time setup):
# Download recogito.min.js + recogito.min.css from @recogito/recogito-js
# Download annotorious.min.js + annotorious.min.css from @recogito/annotorious
# Then:
rsync -avz ops/ghostwriter/static/ ubuntu@18.192.122.48:/home/ubuntu/pr-watcher-web/static/
```

Or via AWS SSM (same procedure as the daemon — see "Deploying via AWS SSM" above):

```bash
aws ssm send-command \
  --instance-ids <INSTANCE_ID> \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /home/ubuntu/kb_generation && git pull origin main && cd ops/ghostwriter && npm ci && npm run build && rsync -a ../../dist/ghostwriter/ /home/ubuntu/pr-watcher-web/ghostwriter/"]'
```

### nginx config

Add the location blocks from `ops/ghostwriter/nginx-ghostwriter.conf` to the VM's nginx server block
(usually `/etc/nginx/sites-available/default`), then reload:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

The SPA will then be available at `http://18.192.122.48/ghostwriter/`.

### Environment

Create `ops/ghostwriter/.env.local` (git-ignored, never commit):

```
VITE_API_BASE=http://18.192.122.48
VITE_N8N_WEBHOOK=http://18.192.122.48/n8n/webhook/annotation-intake
```

### queue.json first deploy

Commit `clusters/queue.json` before enabling auto-advance. The daemon degrades gracefully
if it is missing (logs "auto-trigger disabled") — no crash.

```bash
git add clusters/queue.json
git commit -m "chore: seed clusters/queue.json for daemon queue-as-data"
git push origin main
```
