# Single-branch migration runbook

1. Stop the daemon: `systemctl stop pr-watcher`
2. Deploy code through T11 (status-driven path live alongside PR path).
3. Run: `python3 pipeline/migrate_to_single_branch.py --dry-run` then without `--dry-run`.
4. Push `main`.
5. Execute printed cleanup commands (close PRs, delete `article/*` branches).
6. Deploy T13+ code.
7. Start daemon: `systemctl start pr-watcher`
8. Supervise the first end-to-end article before leaving unattended.
