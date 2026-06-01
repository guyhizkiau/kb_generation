#!/bin/bash
# write_health.sh — emit health.json from systemctl show
# Run by pr-watcher-health.timer every 60s.
set -euo pipefail

DEST=/home/ubuntu/pr-watcher-web/health.json
TMP="${DEST}.tmp"
mkdir -p "$(dirname "$DEST")"

# Collect systemctl properties as key=value pairs
eval "$(systemctl show pr-watcher \
  --property=ActiveState,SubState,MainPID,NRestarts,ExecMainStartTimestamp \
  | sed 's/=/="/' | sed 's/$/"/')"

GENERATED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$TMP" <<EOF
{
  "generated_at": "${GENERATED_AT}",
  "ActiveState": "${ActiveState:-unknown}",
  "SubState": "${SubState:-unknown}",
  "MainPID": "${MainPID:-0}",
  "NRestarts": "${NRestarts:-0}",
  "ExecMainStartTimestamp": "${ExecMainStartTimestamp:-}"
}
EOF

mv "$TMP" "$DEST"
chown ubuntu:ubuntu "$DEST"
