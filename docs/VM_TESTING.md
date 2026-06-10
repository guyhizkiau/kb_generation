# VM testing runbook — single-branch pipeline refactor

Branch: `pipeline/single-branch-refactor`

This branch replaces the branch-per-article / PR workflow with a
status-driven pipeline on `main`. Read this file before deploying to the
EC2 VM (`18.192.122.48`).

Related docs:

- [`docs/MIGRATION_RUNBOOK.md`](MIGRATION_RUNBOOK.md) — one-time migration from `article/*` branches
- [`ops/pr-watcher/README.md`](../ops/pr-watcher/README.md) — daemon architecture and deploy
- [`ops/ghostwriter/README.md`](../ops/ghostwriter/README.md) — Ghostwriter local/VM dev

---

## 1. Pre-deploy: verify locally (repo root, venv active)

```bash
source .venv/bin/activate

# Full automated suite
python3 -m unittest discover -s store -p 'test_*.py' -v
python3 -m unittest pipeline.test_gates pipeline.test_fixjournal pipeline.test_relint pipeline.test_reverify pipeline.test_migrate writer.test_run_claude_code tester.test_runner pipeline.publish.test_publish -v
(cd ops/pr-watcher && python3 -m unittest discover -p 'test_*.py' -v)
python3 -m unittest ops.ghostwriter.test_dev_shim -v
(cd ops/ghostwriter && npm test && npm run build)

# Migration plan (no writes)
python3 pipeline/migrate_to_single_branch.py --dry-run
```

All commands must exit 0 before deploying.

---

## 2. Deploy code to VM (before migration)

**Merge the `pipeline/single-branch-refactor` PR into `main` first.** The
migration script ends with the working tree on `main`, and the daemon
imports `store/` from the repo root — both require the refactor code to be
on `main` before anything runs on the VM.

Use AWS SSM (see `ops/pr-watcher/README.md` § Deploy). On the VM:

```bash
sudo systemctl stop pr-watcher

cd /home/ubuntu/kb_generation
sudo -u ubuntu git fetch origin main
sudo -u ubuntu git checkout main
sudo -u ubuntu git pull origin main

# Copy daemon + dashboard
cp ops/pr-watcher/pr-watcher.py /home/ubuntu/pr-watcher.py
cp ops/pr-watcher/dispatcher.py /home/ubuntu/dispatcher.py
cp ops/pr-watcher/dashboard/index.html /home/ubuntu/pr-watcher-web/index.html

# Rebuild Ghostwriter SPA
cd ops/ghostwriter && npm ci && npm run build
sudo rsync -a ../../dist/ghostwriter/ /home/ubuntu/pr-watcher-web/ghostwriter/

# Ensure repo packages are on PYTHONPATH (daemon adds repo root)
# No pip install needed — store/ is importable from repo root
```

**VM-local state the repo can't fix — check all three:**

```bash
# 1. Unset GHOSTWRITER_FEEDBACK_DIR everywhere it might be exported
#    (start-pr-watcher.sh, ~/.config/specterx-kb/.env, the systemd unit).
#    If it stays set, feedback silently keeps writing to
#    /home/ubuntu/ghostwriter-feedback/ instead of articles/<slug>/feedback.json
#    — restoring the two-sources-of-truth problem this refactor removes.
grep -rn GHOSTWRITER_FEEDBACK_DIR /home/ubuntu/start-pr-watcher.sh \
    /home/ubuntu/.config/specterx-kb/.env /etc/systemd/system/pr-watcher.service

# 2. Reset the worktree — it may still sit on a (soon-deleted) article branch
#    with dirty files; the phase launcher has no `set -e` and would carry on.
cd /home/ubuntu/kb_generation-work
sudo -u ubuntu git checkout -f main && sudo -u ubuntu git pull origin main

# 3. Disable the n8n annotation-intake workflow on the n8n instance.
#    Deleting ops/n8n/wf1-annotation-intake.json from the repo does not stop
#    the deployed workflow; if left running it will keep mirroring
#    annotations into GitHub issues that nothing reads anymore.
```

Do **not** start the daemon yet if you still have open `article/*` PRs —
run migration first (§3).

---

## 3. One-time migration (stop daemon → migrate → cleanup)

Follow [`docs/MIGRATION_RUNBOOK.md`](MIGRATION_RUNBOOK.md):

```bash
sudo systemctl stop pr-watcher
cd /home/ubuntu/kb_generation
source /opt/specterx-kb-venv/bin/activate

python3 pipeline/migrate_to_single_branch.py --dry-run
python3 pipeline/migrate_to_single_branch.py

sudo -u ubuntu git push origin main
```

Execute the **printed cleanup commands** (close article PRs, delete
`article/*` remote branches) — the script does not run these automatically.

Copy VM feedback dir into repo if needed:

```bash
# If annotations live outside the repo today:
for f in /home/ubuntu/ghostwriter-feedback/*.json; do
  slug=$(basename "$f" .json)
  cp "$f" "articles/$slug/feedback.json"
done
```

---

## 4. Start daemon and smoke-test

```bash
sudo systemctl start pr-watcher
sleep 4
systemctl is-active pr-watcher
curl -s http://localhost/health | head -c 200
curl -s http://localhost/status/status.json | python3 -m json.tool | head -30
```

### Ghostwriter (browser)

Open `http://18.192.122.48/ghostwriter/`

| Check | Expected |
|-------|----------|
| Articles queue loads | Phases show new values (`PUBLISHED`, `IN_REVIEW`, …) |
| `04-share-a-file` row | Phase reflects migrated STATE |
| Review article 01 | Preview HTML loads |
| Add annotation | Persists to feedback store |
| Approve (if `IN_REVIEW`) | STATE → `PUBLISHED`, HTML/index rebuilt |

### Control API (from VM)

```bash
curl -s http://127.0.0.1:9191/api/queue | python3 -m json.tool | head -20
curl -s -X POST http://127.0.0.1:9191/poll-now
```

### First supervised article

Do **not** leave the daemon unattended until one article completes
end-to-end under the new model:

1. Pick next `QUEUED` slug from `clusters/queue.json`
2. Watch `/status/` dashboard and `/task-log` during phase runs
3. Confirm commits land on `main` (not `article/<slug>`)
4. Approve via Ghostwriter when `IN_REVIEW`
5. Confirm `PHASE=PUBLISHED` and rendered HTML on disk

---

## 5. Rollback

If migration or first article fails (after the PR is merged, `main` IS the
refactor code — roll back by SHA, not by branch):

```bash
sudo systemctl stop pr-watcher
cd /home/ubuntu/kb_generation
# <pre-merge-sha> = last main commit before the refactor merge
sudo -u ubuntu git checkout <pre-merge-sha>
cp ops/pr-watcher/pr-watcher.py /home/ubuntu/pr-watcher.py
sudo systemctl start pr-watcher
```

Article branches/PRs are only deleted by the operator cleanup commands, so
they still exist until you ran those — do not run cleanup until the first
supervised article has completed end-to-end. A botched migration commit on
`main` is reverted with `git revert <migration-sha>` (one commit per phase
convention: the migration is a single commit).

---

## 6. Key behaviour changes (quick reference)

| Before | After |
|--------|-------|
| Review = merge PR | Review = Ghostwriter **Approve** → publish adapter |
| STATE on `article/<slug>` branch | STATE on `main` only |
| Parallel cluster mode | Strictly serial (one article in flight) |
| `PHASE=DONE/MERGED/PR_OPEN` | `PUBLISHED/IN_REVIEW/…` (+ legacy read mapping) |
| Feedback via GitHub issues (n8n) | Feedback via `/api/feedback` → store only |
| Daemon polls open PRs | Daemon dispatches from STATE scan (`dispatcher.py`) |

---

## 7. Troubleshooting

| Symptom | Check |
|---------|-------|
| Daemon won't start | `journalctl -u pr-watcher -n 50`; import errors for `store/` |
| Phase stuck | `articles/<slug>/STATE`; `/status/status.json` `current_task` |
| Approve 409 | Phase must be `IN_REVIEW` |
| Approve 500, stays APPROVED | Retry `POST /api/queue/publish` |
| Pipeline busy (exit 3) | Another article in `ACTIVE_PHASES`; wait or fix STATE |
| BLOCKED after research | `research/competitor-coverage.md` needs ≥3 bullets under `## Articles read` |

Log paths on VM: `/home/ubuntu/pr-watcher.log`, `/home/ubuntu/pr-watcher-task.log`
