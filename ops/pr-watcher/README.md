# pr-watcher ops

Autonomous PR comment resolver and article pipeline driver for the SpecterX KB project.

## URLs (VM: 18.192.122.48)

| URL | Description |
|---|---|
| `http://18.192.122.48/status/` | Live dashboard |
| `http://18.192.122.48/health` | Health JSON (machine-readable) |
| `http://18.192.122.48/log` | Full raw log (plain text) |
| `http://18.192.122.48/` | Article browser |

## Service commands

```bash
# Status
systemctl is-active pr-watcher
systemctl status pr-watcher
journalctl -u pr-watcher -n 50 --no-pager

# Start / stop / restart
systemctl start pr-watcher
systemctl stop pr-watcher
systemctl restart pr-watcher

# Health timer
systemctl status pr-watcher-health.timer
systemctl list-timers pr-watcher-health.timer
```

## Deploy (first time or after code change)

```bash
# Pull latest from git
cd /home/ubuntu/kb_generation && git pull

# Copy files into place
cp ops/pr-watcher/pr-watcher.py /home/ubuntu/pr-watcher.py
cp ops/pr-watcher/dashboard/index.html /home/ubuntu/pr-watcher-web/index.html
cp ops/pr-watcher/write_health.sh /home/ubuntu/write_health.sh
chmod +x /home/ubuntu/write_health.sh

# Install systemd units (first time only)
cp ops/pr-watcher/pr-watcher.service         /etc/systemd/system/
cp ops/pr-watcher/pr-watcher-health.service  /etc/systemd/system/
cp ops/pr-watcher/pr-watcher-health.timer    /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now pr-watcher
systemctl enable --now pr-watcher-health.timer

# Reload nginx after config change
nginx -t && systemctl reload nginx
```

## Cut over from nohup (one-time migration)

```bash
pkill -f pr-watcher.py || true
systemctl daemon-reload
systemctl enable --now pr-watcher
systemctl enable --now pr-watcher-health.timer
```

## Timeout behaviour

`STEP_TIMEOUT_SECS = 120` — if Claude produces no output for 2 minutes,
the watchdog kills the process and posts a `⏱️ Step timed out` reply.

`TASK_TIMEOUT_SECS = 3600` — 1-hour hard cap regardless of output activity.

Claude is required to print `STEP: <name>` before each discrete action,
resetting the step timer. All Playwright calls must carry explicit timeouts.

## Files

| File | Role |
|---|---|
| `pr-watcher.py` | The daemon (canonical source — overwrite VM copy on deploy) |
| `pr-watcher.service` | systemd service unit |
| `pr-watcher-health.service` | One-shot health writer (run by timer) |
| `pr-watcher-health.timer` | Fires health writer every 60s |
| `write_health.sh` | Reads `systemctl show`, writes `health.json` |
| `dashboard/index.html` | Self-contained status dashboard |

## State files (on VM, not in git)

| Path | Description |
|---|---|
| `/home/ubuntu/pr-watcher-state.json` | Handled comment/PR IDs |
| `/home/ubuntu/pr-watcher.log` | Full poll log |
| `/home/ubuntu/pr-watcher-web/status.json` | Written each poll |
| `/home/ubuntu/pr-watcher-web/health.json` | Written every 60s by timer |
