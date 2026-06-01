# Lessons learned — durable knowledge for the KB pipeline

Each entry below was a real bug, blind spot, or "we discovered this the
hard way" moment during a real article run. They are recorded here so a
future session — human or autonomous — doesn't burn hours rediscovering
them.

Add new entries at the top. Keep each entry short, specific, and
actionable. Link to the file where the actual fix lives so the
reader can verify the canon hasn't drifted from this note.

---

## 2026-06-01 — Article 02 (Set or reset your password)

### L01. AI-tells leak through even with a thorough style guide

**Symptom.** Article 02 read as AI-generated despite an
otherwise-solid `editorial/STYLE_GUIDE.md`. Specific tells: every
article opened with "Use this article to…"; no contractions anywhere;
troubleshooting headers stated the *cause* or *fix*, not the
*symptom*; long parenthetical asides nobody writes by hand; an
internal QA footer with the test-recipient email leaked into the
published article.

**Fix.** `editorial/STYLE_GUIDE.md` Sections 2.4 (Contractions — now
"default to"), 3 (Article openings — three rotating patterns instead
of one canonical opener), 10 (Troubleshooting — new "Header rule"
sub-section requiring symptom-first headers), 14 (three new
anti-patterns: meta-commentary, summary-before-procedure, internal QA
metadata in customer copy). Plus a new pipeline phase
`pipeline/prompts/04a-voice-pass.md` that runs between
`revise-from-test` and the PR, rewrites prose against those rules,
and is forbidden from changing facts, screenshots, UI labels, or
structure.

**For future articles.** Run the voice pass (see
[`WORKFLOW.md`](../WORKFLOW.md) §9.2a) before opening a PR.
The article should hit at least the following objective markers:

- Opener does not start with "Use this article to…" unless the
  preceding articles in the KB used the situational or direct-action
  pattern.
- At least 5 contractions in the prose for an end-user article.
- Zero em dashes in prose (Section 13a).
- Every troubleshooting header phrased as a symptom (the user's
  observable experience), not a cause or fix.
- No `last-validated:` / `specterx-build:` in YAML front matter; no
  closing "Last validated…" footer; no test-account email anywhere.

### L02. Test recipients must be invited to the SpecterX tenant

**Symptom.** First attempt at the article-02 E2E reset capture: the
Playwright script reached `Reset password`, entered
`davidch@specterx.com`, the UI returned the same "we sent you an
email" response, but no email ever arrived in any folder of the
recipient mailbox. Hours of debugging Playwright, Gmail, and the
SpecterX UI followed before we realized SpecterX is no-enumeration:
unregistered addresses get the same silent UI as registered ones.

**Fix.** [`tester/TEST_RESOURCES.md`](../tester/TEST_RESOURCES.md)
now documents the provisioning prerequisite explicitly: a Google
Workspace mailbox is necessary but not sufficient; the same address
must also be invited as an active SpecterX user in the target tenant.

**For future articles.** Before any E2E run that depends on a
recipient mailbox, confirm the recipient is invited in the SpecterX
admin portal. If a future test produces zero reset emails AND the UI
looks normal, suspect provisioning first; don't debug Playwright.

### L03. Long bash tool calls are not stalls

**Symptom.** Every long Playwright run (10–30 min for a full Gmail +
SpecterX reset E2E) was killed by the watchdog at exactly 120 s with
no useful output. We thought Claude was hanging. It wasn't — Claude
was waiting for a perfectly healthy `bash` tool call to complete, and
between the `tool_use` event and the `tool_result` event there are no
intermediate `stream-json` events.

**Fix.** Three timeout dials in
[`ops/pr-watcher/pr-watcher.py`](../ops/pr-watcher/pr-watcher.py)
instead of one. `STEP_TIMEOUT_SECS = 120` only fires when Claude has
no in-flight tool. `TOOL_TIMEOUT_SECS = 1800` (30 min) applies once a
tool call is in flight. `TASK_TIMEOUT_SECS = 3600` (1 h) is the hard
cap. The reader thread switches between them based on whether the
most recent event was a `tool_use` or a `tool_result` / text.

**For future articles.** Don't reduce `TOOL_TIMEOUT_SECS` to "force
faster failures" — long Playwright runs are normal. If a tool
genuinely needs more than 30 min, raise `TOOL_TIMEOUT_SECS` and
`TASK_TIMEOUT_SECS` together. Both are at the top of `pr-watcher.py`.

### L04. Node.js block-buffers stdout when it isn't a TTY

**Symptom.** Claude's stdout was being routed to a regular file
(or `subprocess.PIPE`). For 18+ minutes the task log stayed at 0
bytes — then 1525 bytes appeared all at once at process exit. We
thought Claude was suppressing output. It wasn't — Node was
block-buffering it.

**Fix.** Allocate a pseudo-terminal with `pty.openpty()`, hand the
slave fd to `subprocess.Popen` as `stdout`/`stderr`, read from the
master fd in a thread. Node detects `isatty()=true`, switches to
line-buffering, and flushes on every `\n`. See
[`ops/pr-watcher/README.md`](../ops/pr-watcher/README.md) section
"How the daemon talks to Claude — the non-obvious bits".

**For future articles.** Don't replace the PTY with a pipe or a file
"to simplify". The dashboard's Live output panel depends on it.

### L05. `--output-format stream-json` is required for tool-level live updates

**Symptom.** Even with the PTY working, the live output panel was
empty during the entire Playwright phase of a task. Claude in `-p
text` mode emits text the *model* produces — not tool output, not tool
identifiers, nothing during long tool calls.

**Fix.** Run Claude with `--output-format stream-json --verbose`. The
reader thread parses each NDJSON event and formats it into a
human-readable line (`→ Bash: <cmd>`, `→ Read: <path>`, indented tool
result tail). Plain assistant text events are still captured for the
`RESOLVED` / `NEEDS_HUMAN` final-status scan.

**For future articles.** If a future Claude release changes the
`stream-json` event schema, the parser is in `_format_event()` near
the top of `resolve_comment()` in `pr-watcher.py`. Extend, don't
rewrite — the parser ignores unknown event types so partial coverage
still works.

### L06. SIGKILL leaves Claude lock files behind

**Symptom.** Every watchdog kill left a `.lock` file in
`~/.claude/tasks/<uuid>/`. New Claude invocations hung indefinitely on
those stale locks. We thought Claude was hung; it was waiting on a
file lock owned by a PID that no longer existed.

**Fix.**

1. `preexec_fn=os.setpgrp` + `os.killpg()` so the entire process tree
   (claude + bash + node + chrome) dies together. Reduces lock-file
   leakage by killing claude cleanly when possible.
2. Standard deploy template now runs
   `find /home/ubuntu/.claude/tasks/ -name ".lock" -delete` before
   every `systemctl restart pr-watcher`. Always.

**For future articles.** If the bot is "running but produces no
output, ever", the first thing to check is stale `.lock` files. See
the runbook's "Failure modes A" entry.

### L07. Status writes had to be flushed mid-task, not just per poll

**Symptom.** The dashboard's Active Task widget showed "(starting)"
for the entire duration of a Claude run, then jumped to the next
state when the poll loop returned. `status.json` was only written
once per poll (~5 min apart).

**Fix.** Module-level `_status_cache` + `flush_status()` helper, plus
explicit `flush_status()` calls on task start, every `tool_use` event,
every `STEP:` line, and task end. The dashboard now sees updates in
real time.

**For future articles.** When adding new daemon state that the
dashboard should see, route it through `_runtime[…]` + `flush_status()`,
not directly into `status.json`.

### L08. Retry endpoints must mutate in-memory state, not just disk

**Symptom.** The `/retry` endpoint cleared the comment ID from
`state.json` on disk, but the running daemon already had `state`
loaded into memory. The next poll iteration still saw the comment as
"handled" and skipped it. Clicking Retry felt like it did nothing.

**Fix.** Module-level `_retry_set: set` populated by the `/retry`
handler. The comment-processing loops check it before honoring the
`handled` skip.

**For future articles.** Any new "force re-process" controls (e.g.
re-trigger an article, re-open a merged PR) need the same
on-disk-PLUS-in-memory pattern.

### L09. Screenshot capture has its own pre-flight list

**Symptom.** Article 02's first screenshot pass produced frames with
Gmail's "Start a chat" tour bubble, "Why is this message in spam?"
banners, message threads that collated with prior test runs, and
generally too much chrome around the relevant element. The reader's
eye had to hunt for the SpecterX content inside Gmail UI noise.

**Fix.** [`editorial/STYLE_GUIDE.md`](../editorial/STYLE_GUIDE.md)
§9 now has a "Pre-capture cleanup checklist" sub-section and a
"Special cases — screenshots that almost always need a tight crop"
list (inbox listings, message bodies, toast notifications).

**For future articles.** Walk the checklist before pressing the
shutter. If a screenshot is committed with visible Gmail/Outlook
chrome, the PR review will catch it; better to catch it during the
test run.

---

## How to read this file

- Entries are dated `YYYY-MM-DD` plus the article slug or topic.
- "Symptom" explains what we observed.
- "Fix" cites the file that actually implements the fix.
- "For future articles" is the durable rule a future session should
  apply *before* hitting the same wall.
