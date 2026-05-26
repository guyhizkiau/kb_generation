# Windows VM — Deferred Execution Plan

> Status: **PARKED**. The Linux-first pipeline ships first. Wire in the
> Windows VM when you hit an article that genuinely requires a Windows
> desktop app (Outlook plugin, SpecterX desktop client, file-explorer
> integration).

## What the Windows VM is for

Workflows that cannot be driven from a browser:
- SpecterX Outlook plugin (compose / protect email)
- SpecterX Windows desktop client / file-explorer integration
- Any flow where the article must show a Windows Explorer window
- Any flow that involves dragging files between Windows apps

Everything else (web UI, file uploads) stays on Linux using Playwright +
`set_input_files()`.

## Existing Windows VM

| Field | Value |
|---|---|
| Instance ID | `i-084f9aa7c6bf5e6a5` |
| Region | eu-central-1 |
| Type | t3.large, Windows Server 2022 |
| Public IP | `63.178.246.68` (elastic? check before use) |
| Security group | `sg-0e8194d2861cf9016` (specterx-kb-sg) |
| Key pair | `specterx_frankfurt` (PEM at `~/.ssh/specterx_frankfurt.pem`) |
| Phase 1 bootstrap | Complete (Chocolatey, WSL features enabled, Chrome, Git, Node, Python, AWS CLI, gh installed) |
| Phase 2 bootstrap | Not complete — WSL/Ubuntu install was abandoned when architecture changed |

## What still needs to happen on the Windows VM before it's usable

1. **Install SpecterX desktop client + Outlook plugin** — Guy does this manually (license required)
2. **Install Microsoft Office / Outlook** — Guy does this manually (M365 license)
3. **Install Adobe Acrobat** — if needed for any articles
4. **Deploy `win-action-server.py`** — a small Flask server on localhost:9100 that receives click/type/screenshot actions from the Linux VM and executes them via `pyautogui`. Run as a Windows service via NSSM.
5. **Launch Chrome with CDP** — `chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\specterx-kb\.chrome-profile`. See `vm-bootstrap/start-chrome.ps1` in the bootstrap package.
6. **Open security group ports from Linux VM SG** — ports 9222 (Chrome CDP) and 9100 (win-action-server). The Linux SG (`specterx-kb-linux-sg`) must be created first.

## Connection architecture (Linux → Windows)

```
Linux EC2 (Claude Code)
    │
    ├─ Playwright CDP → Windows:9222  (Chrome remote debugging)
    │   Used for: any browser step that needs to look like Windows
    │   (see GTK theme note in project_kb_pipeline_arch.md)
    │
    └─ HTTP → Windows:9100            (win-action-server.py)
        Used for: click, type, scroll, screenshot actions on Windows desktop
        Actions executed via pyautogui on Windows side
```

## win-action-server.py spec

Minimal Flask app on the Windows VM. Endpoints:

```
POST /click        { x, y }
POST /type         { text }
POST /scroll       { x, y, direction, amount }
POST /screenshot   → returns PNG bytes
POST /key          { key }  (e.g. "enter", "ctrl+s")
GET  /health       → 200 OK
```

Claude Code on Linux calls these via `requests`. The tester's
`desktop_runner.py` wraps them with the Anthropic computer-use loop.

## Step classifier (Linux side)

When the orchestrator processes an article step, classify it:

| Keywords in step | Backend |
|---|---|
| "Outlook", "email plugin", "protect email" | Windows desktop |
| "file explorer", "drag file", "right-click file" | Windows desktop |
| "SpecterX app", "desktop client" | Windows desktop |
| everything else | Linux Playwright |

## When to activate

Open `editorial/ARTICLES_PLAN.md`, find the first article that requires Outlook
or the desktop client, and tackle the Windows wiring then. Until that
point, keep the Windows VM **stopped** to avoid cost.

Stop it now if not already stopped:
```bash
python3 -c "
import boto3
ec2 = boto3.client('ec2', region_name='eu-central-1')
ec2.stop_instances(InstanceIds=['i-084f9aa7c6bf5e6a5'])
print('Windows VM stopping...')
"
```
