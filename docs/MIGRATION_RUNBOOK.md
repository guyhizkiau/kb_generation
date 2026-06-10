# Single-branch migration runbook

> Order matters: the migration script and `store/` live on the refactor
> branch, and the script leaves the working tree on `main` — so `main`
> must already contain the refactor code when migration runs.

1. Merge the `pipeline/single-branch-refactor` PR into `main`.
2. Stop the daemon: `sudo systemctl stop pr-watcher`
3. On the VM: `cd /home/ubuntu/kb_generation && sudo -u ubuntu git checkout main && sudo -u ubuntu git pull origin main`
4. Deploy daemon files + SPA per `docs/VM_TESTING.md` §2 (copy
   `pr-watcher.py`/`dispatcher.py`, rebuild Ghostwriter).
5. Run: `python3 pipeline/migrate_to_single_branch.py --dry-run`, review
   the plan (landed branches, keeper, mappings), then run without
   `--dry-run`. Branches already merged into `main` are skipped — only
   genuinely in-flight work is landed.
6. Push `main`: `sudo -u ubuntu git push origin main`
7. Execute the printed cleanup commands (close still-open article PRs,
   delete `article/*` remote branches). These are operator actions; the
   script never runs them.
8. Copy any VM feedback files into the repo
   (`/home/ubuntu/ghostwriter-feedback/*.json` → `articles/<slug>/feedback.json`),
   commit, push.
9. Start the daemon: `sudo systemctl start pr-watcher`
10. Supervise the first end-to-end article before leaving it unattended.
