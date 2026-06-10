# Deploy handoff — single-branch pipeline refactor

**Audience:** a Claude Code session with AWS SSM access to the pipeline VM.
**Goal:** finish deploying the single-branch refactor to the VM (runbook
steps 3–6), then hand back to Guy for the supervised first article (step 7).

Authoritative runbooks (read these first):
[`docs/VM_TESTING.md`](VM_TESTING.md) and
[`docs/MIGRATION_RUNBOOK.md`](MIGRATION_RUNBOOK.md). This file only adds
the live status and the exact remaining commands.

---

## 1. Background — what this refactor is

The KB article pipeline used to run one git branch + GitHub PR per
article; review meant merging the PR. PR #34 replaced that with a
status-driven model:

- All article work commits directly to `main`; the per-article STATE file
  (`articles/<slug>/STATE`) drives a state machine
  (`QUEUED → RESEARCHING → DRAFTING → TESTING → REVISING → FINALIZING →
  IN_REVIEW → APPROVED → PUBLISHED`), enforced by `store/machine.py`.
- The pr-watcher daemon no longer polls PRs; `ops/pr-watcher/dispatcher.py`
  scans STATE files and dispatches phases, strictly serial (one article in
  flight).
- Review/approve/publish are control-plane actions in the Ghostwriter SPA
  (Approve → publish adapter renders HTML + rebuilds the index). No merges.
- Feedback annotations live in `articles/<slug>/feedback.json` (the
  GitHub-issues/n8n mirror path is retired).
- `pipeline/migrate_to_single_branch.py` is a one-time, idempotent script
  that lands the legacy `article/*` branches onto `main`, maps legacy
  PHASE values (`DONE/MERGED→PUBLISHED`, `PR_OPEN→IN_REVIEW`, …), and
  seeds explicit `QUEUED` STATE for unstarted queue articles. It **prints**
  operator cleanup commands (close PRs, delete branches) but never runs
  them.

## 2. Current status (as of 2026-06-10)

| Item | State |
|---|---|
| Refactor PR | **#34 merged.** `main` is at `02b4f75c…` with the full refactor |
| Rollback point | Pre-merge main SHA: `c8ef31c702eb6a45ba7e945d8899ce734244e83f` (also recorded in the PR #34 body) |
| VM (`18.192.122.48`) | **NOT updated.** Still running the old PR-polling daemon against old `main` |
| Migration | **Not run.** Legacy branches `article/02-set-or-reset-password` and `article/04-share-a-file` still exist on the remote |
| Local test suites | All green at merge time (store, pipeline, writer, tester, pr-watcher incl. dispatcher, ghostwriter shim + SPA) |

Guy has explicitly approved: closing the article/02 PR, and losing any
post-upgrade work if a rollback is needed.

## 3. Remaining steps (run via SSM)

Deploy via **AWS SSM `AWS-RunShellScript`** — not SSH. SSM runs as root;
use `sudo -u ubuntu` for git/HOME-sensitive commands. Find the instance ID
by its IP if you don't have it:

```bash
aws ec2 describe-instances \
  --filters "Name=ip-address,Values=18.192.122.48" \
  --query "Reservations[].Instances[].InstanceId" --output text
```

### Step 3a — stop daemon, pull main, deploy daemon files, rebuild SPA

```bash
systemctl stop pr-watcher

cd /home/ubuntu/kb_generation
sudo -u ubuntu git fetch origin main
sudo -u ubuntu git checkout main
sudo -u ubuntu git pull origin main

cp ops/pr-watcher/pr-watcher.py            /home/ubuntu/pr-watcher.py
cp ops/pr-watcher/dispatcher.py            /home/ubuntu/dispatcher.py
cp ops/pr-watcher/dashboard/index.html     /home/ubuntu/pr-watcher-web/index.html

cd ops/ghostwriter && npm ci && npm run build
rsync -a ../../dist/ghostwriter/ /home/ubuntu/pr-watcher-web/ghostwriter/
```

### Step 4 — VM-local state checks (all three)

```bash
# 4.1 GHOSTWRITER_FEEDBACK_DIR must NOT be exported anywhere.
#     If found, remove the export line (and `systemctl daemon-reload` if it
#     was in the unit). Left set, feedback silently keeps writing to
#     /home/ubuntu/ghostwriter-feedback/ instead of articles/<slug>/feedback.json.
grep -rn GHOSTWRITER_FEEDBACK_DIR \
    /home/ubuntu/start-pr-watcher.sh \
    /home/ubuntu/.config/specterx-kb/.env \
    /etc/systemd/system/pr-watcher.service || echo FEEDBACK_DIR_CLEAN

# 4.2 Reset the daemon worktree — it may sit on a soon-deleted article branch.
cd /home/ubuntu/kb_generation-work
sudo -u ubuntu git checkout -f main && sudo -u ubuntu git pull origin main

# 4.3 MANUAL (Guy, in the n8n UI): deactivate the wf1-annotation-intake
#     workflow. Deleting its JSON from the repo does not stop the deployed
#     copy; left running it mirrors annotations into GitHub issues nothing
#     reads anymore.
```

If any existing annotations live in `/home/ubuntu/ghostwriter-feedback/`,
copy them into the repo:

```bash
for f in /home/ubuntu/ghostwriter-feedback/*.json; do
  [ -e "$f" ] || continue
  slug=$(basename "$f" .json)
  cp "$f" "/home/ubuntu/kb_generation/articles/$slug/feedback.json"
done
```

### Step 5 — migration (dry-run, REVIEW OUTPUT, then real)

```bash
cd /home/ubuntu/kb_generation
/opt/specterx-kb-venv/bin/python3 pipeline/migrate_to_single_branch.py --dry-run
```

**Stop and read the dry-run output.** Expected shape:

- `article/04-share-a-file` is already merged into main → **skipped**, not landed
- `article/02-set-or-reset-password` is landed onto main; its `PR_OPEN`
  STATE maps to `IN_REVIEW`
- Articles 05–10 (unstarted queue entries) get seeded `PHASE=QUEUED`
- Dry-run writes **nothing** — if it claims it would and you see actual
  STATE diffs afterwards, abort and report

If the plan matches, run it for real and push:

```bash
/opt/specterx-kb-venv/bin/python3 pipeline/migrate_to_single_branch.py
sudo -u ubuntu git push origin main
```

The script prints operator **cleanup commands** (close article/02 PR,
delete both `article/*` remote branches). **Save them; do not run them
yet** — they are step 8, after the first supervised article succeeds.

### Step 6 — start daemon and smoke-test

```bash
find /home/ubuntu/.claude/tasks/ -name .lock -delete
systemctl start pr-watcher
sleep 4
systemctl is-active pr-watcher
curl -s http://localhost/health | head -c 200
curl -s http://localhost/status/status.json | python3 -m json.tool | head -30
curl -s http://127.0.0.1:9191/api/queue | python3 -m json.tool | head -20
```

Pass criteria: unit `active`; `/health` OK; `status.json` shows new-set
phases (`PUBLISHED`, `IN_REVIEW`, `QUEUED`, …); `/api/queue` lists the
queue with migrated phases. Then open
`http://18.192.122.48/ghostwriter/` and confirm the article list loads.

## 4. Step 7 — supervised first article (Guy drives, session watches)

Do **not** leave the daemon unattended until one article completes
end-to-end:

1. The dispatcher should pick the first QUEUED slug (expected: `05-…`)
   and launch research on its own — watch `/status/` and
   `/home/ubuntu/pr-watcher-task.log`.
2. Confirm commits land on `main` under `articles/<slug>/` (never on an
   `article/*` branch).
3. If it goes `BLOCKED` after research: the competitor gate requires ≥3
   bullets under `## Articles read` in `research/competitor-coverage.md`.
4. At `IN_REVIEW`, Guy approves in Ghostwriter → expect `PHASE=PUBLISHED`,
   rendered HTML + index on disk.

## 5. Step 8 — operator cleanup (ONLY after step 7 succeeds)

Run the cleanup commands the migration printed: close the
`article/02-set-or-reset-password` PR, delete both `article/*` remote
branches.

## 6. Rollback

`main` already IS the refactor — roll back by SHA, not branch:

```bash
systemctl stop pr-watcher
cd /home/ubuntu/kb_generation
sudo -u ubuntu git checkout c8ef31c702eb6a45ba7e945d8899ce734244e83f
cp ops/pr-watcher/pr-watcher.py /home/ubuntu/pr-watcher.py
systemctl start pr-watcher
```

A botched migration commit on `main` is reverted with
`git revert <migration-sha>` (the migration is a single commit). Article
branches/PRs survive until step 8, so rollback before that point loses
nothing. Guy has accepted losing post-upgrade work in a rollback.

## 7. Troubleshooting quick refs

| Symptom | Check |
|---|---|
| Daemon won't start | `journalctl -u pr-watcher -n 50`; `store/` import errors |
| Phase stuck | `articles/<slug>/STATE`; `current_task` in `/status/status.json` |
| Approve returns 409 | Phase must be `IN_REVIEW` |
| Approve 500, stays `APPROVED` | Retry `POST /api/queue/publish` |
| `pipeline busy` (exit 3) | Another article in an active phase; wait or fix STATE |

Logs: `/home/ubuntu/pr-watcher.log`, `/home/ubuntu/pr-watcher-task.log`.
Secrets: `/home/ubuntu/.config/specterx-kb/.env` (mode 600) — never cat
into logs or commits.
