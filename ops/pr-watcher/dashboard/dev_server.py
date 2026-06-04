#!/usr/bin/env python3
"""
Local dev server for the pr-watcher status dashboard.

Serves the dashboard and simulates PR comment resolution so you can see
how the UI reacts (active task, live task-log, failed comments, poll-now, retry).

Usage (from repo root, venv optional — stdlib only):

    python ops/pr-watcher/dashboard/dev_server.py

Then open:
    http://127.0.0.1:8766/          — dashboard (same as production /status/)
    http://127.0.0.1:8766/dev.html  — scenario controls

Scenarios auto-advance on a timer; use the dev panel to start, pause, step, or reset.
"""

from __future__ import annotations

import json
import mimetypes
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DASHBOARD_DIR = Path(__file__).resolve().parent
CHECKLIST_PATH = DASHBOARD_DIR.parent / "resolution_checklist.json"
PORT = 8766
POLL_INTERVAL = 30  # short interval for local countdown demos

RESOLUTION_CHECKLIST: list[dict] = json.loads(
    CHECKLIST_PATH.read_text(encoding="utf-8")
)


def build_resolution_checklist(
    active_phase: int,
    *,
    terminal: str | None = None,
) -> list[dict]:
    phase = max(1, min(active_phase, len(RESOLUTION_CHECKLIST)))
    items: list[dict] = []
    for step in RESOLUTION_CHECKLIST:
        sid = step["id"]
        if terminal == "done":
            status = "done"
        elif terminal == "failed" and sid == phase:
            status = "failed"
        elif terminal == "failed" and sid < phase:
            status = "done"
        elif sid < phase:
            status = "done"
        elif sid == phase:
            status = "active"
        else:
            status = "pending"
        items.append({**step, "status": status})
    return items


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _iso_in(seconds: float) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


# ── simulation state ─────────────────────────────────────────────────────────

class Simulator:
    """Drives status.json / task-log / health for dashboard dev."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.started_at = _iso_now()
        self.poll_number = 100
        self.recent_log: list[str] = []
        self.task_log: list[str] = []
        self.open_prs = [{"number": 4, "branch": "article/02-set-or-reset-password"}]
        self.current_task: dict | None = None
        self.failed_comments: list[dict] = []
        self.last_error: dict | None = None
        self.last_task_duration_secs: int | None = None
        self.counters = {
            "comments_resolved": 12,
            "articles_triggered": 2,
            "merges_handled": 2,
            "previews_posted": 3,
        }
        self._scenario: str | None = None
        self._scenario_frames: list[dict] = []
        self._frame_idx = 0
        self._timer: threading.Timer | None = None
        self._paused = False
        self._comment_id = "issue-dev-9001"
        self._pr = 4
        self._body_preview = (
            "Please rerun the reset password flow end-to-end, including fetching "
            "the reset code from the mailbox."
        )
        self._phase = 1
        self._reset_idle()

    def _task_payload(self, step: str, phase: int) -> dict:
        return {
            "pr_number": self._pr,
            "comment_id": self._comment_id,
            "step": step,
            "phase": phase,
            "checklist": build_resolution_checklist(phase),
            "started_at": _iso_now(),
        }

    def _log(self, line: str) -> None:
        ts = _iso_now()
        self.recent_log.append(f"[{ts}] {line}")
        self.recent_log = self.recent_log[-40:]

    def _reset_idle(self) -> None:
        self.current_task = None
        self.task_log = []
        self.last_error = None
        self._log("--- Poll #%d ---" % self.poll_number)
        self._log("Open PRs: [%d]" % self._pr)
        self._log("  Checking PR#%d (branch: article/02-set-or-reset-password)" % self._pr)

    def status_payload(self) -> dict:
        with self.lock:
            return {
                "daemon": {
                    "started_at": self.started_at,
                    "pid": 99999,
                    "poll_interval": POLL_INTERVAL,
                },
                "last_poll_at": _iso_now(),
                "poll_number": self.poll_number,
                "next_poll_at": _iso_in(POLL_INTERVAL),
                "open_prs": list(self.open_prs),
                "current_task": self.current_task,
                "failed_comments": list(self.failed_comments),
                "last_error": self.last_error,
                "last_task_duration_secs": self.last_task_duration_secs,
                "counters": dict(self.counters),
                "recent_log": list(self.recent_log),
            }

    def health_payload(self) -> dict:
        return {
            "generated_at": _iso_now(),
            "ActiveState": "active",
            "SubState": "running",
            "MainPID": "99999",
            "NRestarts": "0",
            "ExecMainStartTimestamp": datetime.now(timezone.utc).strftime(
                "%a %Y-%m-%d %H:%M:%S UTC"
            ),
        }

    def full_log_text(self) -> str:
        fixture = DASHBOARD_DIR / "prwatcher-fixture.log"
        base = fixture.read_text() if fixture.exists() else ""
        with self.lock:
            tail = "\n".join(self.recent_log)
        return (base + "\n" + tail).strip() + "\n"

    def task_log_text(self) -> str:
        with self.lock:
            return "\n".join(self.task_log) + ("\n" if self.task_log else "")

    def cancel_timer(self) -> None:
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def schedule_next(self, delay: float = 2.5) -> None:
        self.cancel_timer()
        if self._paused or not self._scenario:
            return

        def tick() -> None:
            with self.lock:
                if self._frame_idx < len(self._scenario_frames):
                    self._apply_frame(self._scenario_frames[self._frame_idx])
                    self._frame_idx += 1
            if self._frame_idx < len(self._scenario_frames):
                self.schedule_next(delay)
            else:
                with self.lock:
                    self._scenario = None

        self._timer = threading.Timer(delay, tick)
        self._timer.daemon = True
        self._timer.start()

    def start_scenario(self, name: str, *, autoplay: bool = True) -> None:
        frames = SCENARIOS.get(name)
        if not frames:
            raise ValueError(f"Unknown scenario: {name}")
        with self.lock:
            self.cancel_timer()
            self._scenario = name
            self._scenario_frames = frames
            self._frame_idx = 0
            self._paused = False
            if name == "idle":
                self.failed_comments = []
                self._reset_idle()
                self._scenario = None
                return
            self._apply_frame(frames[0])
            self._frame_idx = 1
        if autoplay and len(frames) > 1:
            self.schedule_next()

    def pause(self) -> None:
        with self.lock:
            self._paused = True
        self.cancel_timer()

    def resume(self) -> None:
        with self.lock:
            self._paused = False
        if self._scenario and self._frame_idx < len(self._scenario_frames):
            self.schedule_next()

    def step(self) -> None:
        with self.lock:
            if self._frame_idx >= len(self._scenario_frames):
                return
            self._apply_frame(self._scenario_frames[self._frame_idx])
            self._frame_idx += 1

    def poll_now(self) -> None:
        with self.lock:
            self.poll_number += 1
            self._log("--- Poll #%d (manual) ---" % self.poll_number)
            self._log("Open PRs: [%d]" % self._pr)
            if not self.current_task:
                self._log("  Checking PR#%d (branch: article/02-set-or-reset-password)" % self._pr)

    def retry_comment(self, comment_id: str) -> None:
        with self.lock:
            self.failed_comments = [
                f for f in self.failed_comments if f["comment_id"] != comment_id
            ]
            self._phase = 1
            self.current_task = self._task_payload(
                "retry — loading article branch", 1
            )
            self.task_log = [
                "PHASE: 1",
                "STEP: retry — loading article branch",
                f"Re-queued comment {comment_id}",
            ]
            self._log("  Retry requested for %s" % comment_id)

    def _apply_frame(self, frame: dict) -> None:
        action = frame.get("action")
        if action == "poll":
            self.poll_number += 1
            for line in frame.get("log", []):
                self._log(line)
        elif action == "set_phase":
            self._phase = frame["phase"]
            if self.current_task:
                self.current_task = self._task_payload(
                    self.current_task.get("step", "…"), self._phase
                )
            self.task_log.append(f"PHASE: {self._phase}")
            self._log(f"    → PHASE: {self._phase}")
        elif action == "task_start":
            self._phase = frame.get("phase", 1)
            self.current_task = self._task_payload(frame["step"], self._phase)
            self.task_log = [f"PHASE: {self._phase}", f"STEP: {frame['step']}"]
            self._log(f"    → PHASE: {self._phase}")
            self._log(f"    → STEP: {frame['step']}")
        elif action == "task_step":
            step = frame["step"]
            phase = frame.get("phase", self._phase)
            self._phase = phase
            self.current_task = self._task_payload(step, phase)
            self._log(f"    → STEP: {step}")
            if frame.get("phase"):
                self._log(f"    → PHASE: {phase}")
                self.task_log.append(f"PHASE: {phase}")
            for line in frame.get("task_lines", []):
                self.task_log.append(line)
            self.task_log.append(f"STEP: {step}")
        elif action == "task_resolve":
            for line in frame.get("task_lines", []):
                self.task_log.append(line)
            self.task_log.extend(["PHASE: 6", "RESOLVED"])
            self._log("    RESOLVED comment %s" % self._comment_id.replace("issue-", ""))
            self.last_task_duration_secs = frame.get("duration_secs", 95)
            self.current_task = self._task_payload("RESOLVED", 6)
            self.current_task["checklist"] = build_resolution_checklist(6, terminal="done")
            self.counters["comments_resolved"] += 1
            self.failed_comments = []
            self.current_task = None
        elif action == "task_fail":
            for line in frame.get("task_lines", []):
                self.task_log.append(line)
            self._log("    STEP_TIMEOUT on %s" % self._comment_id)
            self.last_task_duration_secs = frame.get("duration_secs", 180)
            fail_task = self._task_payload(self.current_task.get("step", "…") if self.current_task else "…", self._phase)
            fail_task["checklist"] = build_resolution_checklist(self._phase, terminal="failed")
            self.current_task = None
            self.failed_comments = [
                {
                    "comment_id": self._comment_id,
                    "pr_number": self._pr,
                    "body_preview": self._body_preview,
                    "failure": frame.get("failure", "STEP_TIMEOUT"),
                    "failed_at": _iso_now(),
                }
            ]
        elif action == "error":
            self.last_error = {"message": frame["message"], "at": _iso_now()}
            self._log("ERROR in poll loop: " + frame["message"])
        elif action == "clear_error":
            self.last_error = None


SIM = Simulator()

# Each frame: {action, ...} — applied in order when scenario runs
SCENARIOS: dict[str, list[dict]] = {
    "idle": [{"action": "poll", "log": []}],
    "comment_resolution": [
        {
            "action": "poll",
            "log": [
                "--- Poll #101 ---",
                "Open PRs: [4]",
                "  Checking PR#4 (branch: article/02-set-or-reset-password)",
                "  New issue comment 9001 from reviewer",
                "    Body: Please rerun the reset password flow end-to-end...",
            ],
        },
        {
            "action": "task_start",
            "phase": 1,
            "step": "Read: article draft and PR comment",
        },
        {"action": "set_phase", "phase": 2},
        {
            "action": "task_step",
            "phase": 2,
            "step": "Classify: article-only (test-plan gap)",
            "task_lines": ["→ Read: articles/02-set-or-reset-password/draft.md"],
        },
        {"action": "set_phase", "phase": 3},
        {
            "action": "task_step",
            "phase": 3,
            "step": "Bash: docs(test-plan) — expand mailbox step",
            "task_lines": [
                "→ Bash: git commit -m 'docs(test-plan): require mailbox fetch in reset flow'",
            ],
        },
        {"action": "set_phase", "phase": 4},
        {
            "action": "task_step",
            "phase": 4,
            "step": "open SpecterX in browser",
            "task_lines": ["Navigating to https://app.specterx.com/login"],
        },
        {
            "action": "task_step",
            "phase": 4,
            "step": "navigate to reset password page",
            "task_lines": ['Tool: browser_navigate(url="https://app.specterx.com/login")'],
        },
        {
            "action": "task_step",
            "phase": 4,
            "step": "fill email and submit",
            "task_lines": ['Tool: browser_click(selector="Send reset link")'],
        },
        {
            "action": "task_step",
            "phase": 4,
            "step": "open Gmail inbox",
            "task_lines": ['Tool: browser_navigate(url="https://mail.google.com")'],
        },
        {
            "action": "task_step",
            "phase": 4,
            "step": "search Gmail inbox for reset email",
            "task_lines": ["Waiting for results..."],
        },
        {
            "action": "task_step",
            "phase": 4,
            "step": "Bash: fix(article) — commit test notes and screenshots",
            "task_lines": [
                "→ Bash: git commit -m 'fix(article): resolve PR#4 — reset flow with mailbox'",
            ],
        },
        {"action": "set_phase", "phase": 5},
        {
            "action": "task_step",
            "phase": 5,
            "step": "Validate: comment ask vs article text",
            "task_lines": ["Quoted reviewer ask; matched new test-plan step 4."],
        },
        {"action": "set_phase", "phase": 6},
        {
            "action": "task_resolve",
            "task_lines": [
                "Context: test-plan expanded; article re-tested end-to-end with mailbox.",
            ],
            "duration_secs": 142,
        },
        {
            "action": "poll",
            "log": [
                "--- Poll #102 ---",
                "Open PRs: [4]",
                "  Checking PR#4 (branch: article/02-set-or-reset-password)",
            ],
        },
    ],
    "step_timeout": [
        {
            "action": "poll",
            "log": [
                "--- Poll #201 ---",
                "Open PRs: [4]",
                "  New issue comment 9001 from reviewer",
            ],
        },
        {"action": "task_start", "phase": 1, "step": "Read: article draft and PR comment"},
        {"action": "set_phase", "phase": 4},
        {
            "action": "task_step",
            "phase": 4,
            "step": "search Gmail inbox for reset email",
            "task_lines": ["Waiting for results...", "(no matching email after 5 min)"],
        },
        {"action": "set_phase", "phase": 5},
        {"action": "task_fail", "failure": "STEP_TIMEOUT", "duration_secs": 300},
        {
            "action": "poll",
            "log": [
                "--- Poll #202 ---",
                "Open PRs: [4]",
                "  Failed comment still queued for human retry",
            ],
        },
    ],
    "stale_daemon": [
        {
            "action": "poll",
            "log": ["--- Poll #50 ---", "Open PRs: [4]"],
        },
    ],
}


class DevHandler(BaseHTTPRequestHandler):
    simulator = SIM

    def log_message(self, fmt: str, *args) -> None:
        pass  # quiet by default

    def _send_json(self, obj: object, code: int = 200) -> None:
        body = json.dumps(obj, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, code: int = 200) -> None:
        body = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        return json.loads(self.rfile.read(length))

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path in ("/status.json", "/health.json"):
            if path == "/status.json":
                self._send_json(self.simulator.status_payload())
            else:
                self._send_json(self.simulator.health_payload())
            return

        if path == "/health":
            self._send_json(self.simulator.health_payload())
            return

        if path == "/log":
            self._send_text(self.simulator.full_log_text())
            return

        if path == "/task-log":
            self._send_text(self.simulator.task_log_text())
            return

        if path == "/dev/state":
            with self.simulator.lock:
                state = {
                    "scenario": self.simulator._scenario,
                    "frame": self.simulator._frame_idx,
                    "frames": len(self.simulator._scenario_frames),
                    "paused": self.simulator._paused,
                }
            self._send_json(state)
            return

        # static files from dashboard dir
        rel = path.lstrip("/") or "index.html"
        file_path = (DASHBOARD_DIR / rel).resolve()
        if not str(file_path).startswith(str(DASHBOARD_DIR)) or not file_path.is_file():
            self.send_error(404)
            return
        content = file_path.read_bytes()
        ctype = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path == "/poll-now":
            self.simulator.poll_now()
            self._send_json({"ok": True})
            return

        if path == "/retry":
            body = self._read_json_body()
            cid = body.get("comment_id", "")
            if cid:
                self.simulator.retry_comment(cid)
            self._send_json({"ok": True, "comment_id": cid})
            return

        if path == "/dev/scenario":
            qs = parse_qs(urlparse(self.path).query)
            name = (qs.get("name") or [""])[0]
            try:
                autoplay = (qs.get("autoplay") or ["1"])[0] != "0"
                self.simulator.start_scenario(name, autoplay=autoplay)
                self._send_json({"ok": True, "scenario": name})
            except ValueError as e:
                self._send_json({"ok": False, "error": str(e)}, code=400)
            return

        if path == "/dev/pause":
            self.simulator.pause()
            self._send_json({"ok": True})
            return

        if path == "/dev/resume":
            self.simulator.resume()
            self._send_json({"ok": True})
            return

        if path == "/dev/step":
            self.simulator.step()
            self._send_json({"ok": True})
            return

        if path == "/dev/reset":
            self.simulator.cancel_timer()
            with self.simulator.lock:
                self.simulator._scenario = None
                self.simulator._scenario_frames = []
                self.simulator._frame_idx = 0
                self.simulator._paused = False
                self.simulator.failed_comments = []
                self.simulator.poll_number = 100
                self.simulator.counters["comments_resolved"] = 12
                self.simulator._reset_idle()
            self._send_json({"ok": True})
            return

        self.send_error(404)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), DevHandler)
    print(f"pr-watcher dashboard dev server")
    print(f"  Dashboard:  http://127.0.0.1:{PORT}/")
    print(f"  Controls:   http://127.0.0.1:{PORT}/dev.html")
    print(f"  Scenarios:  comment_resolution | step_timeout | idle")
    print(f"  Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        SIM.cancel_timer()


if __name__ == "__main__":
    main()
