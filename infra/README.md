# infra/

Operational glue.

- `systemd/specterx-kb.service` — runs `orchestrator/main.py` as a
  service.
- `cron/wake-and-check.sh` — wake-up hook called by EventBridge.
- `sensitive-terms.txt` — list of names/phrases the PII checker should
  flag in screenshots. Initially empty; populate as needed.
