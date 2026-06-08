#!/usr/bin/env python3
"""
Ghostwriter local API shim — single entry point for Vite dev.

Listens on :8767 (default). Proxies /api/*, /poll-now, /retry to the pr-watcher
control server (:9191). Serves /status/* from the dashboard simulator. When the
control server is unreachable, queue routes are handled inline via queue_store.

Usage (from repo root):

    python ops/ghostwriter/dev_server.py

Then in ops/ghostwriter/.env.local:

    VITE_API_BASE=http://127.0.0.1:8767

Environment:
    GHOSTWRITER_SHIM_PORT  — shim listen port (default 8767)
    GHOSTWRITER_CONTROL    — control upstream URL (default http://127.0.0.1:9191)
    KB_REPO_ROOT           — repo root for inline queue fallback
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

GHOSTWRITER_DIR = Path(__file__).resolve().parent
REPO_ROOT = GHOSTWRITER_DIR.parent.parent
PR_WATCHER_DIR = REPO_ROOT / "ops" / "pr-watcher"
DASHBOARD_DIR = PR_WATCHER_DIR / "dashboard"

PORT = int(os.environ.get("GHOSTWRITER_SHIM_PORT", "8767"))
CONTROL_URL = os.environ.get("GHOSTWRITER_CONTROL", "http://127.0.0.1:9191").rstrip("/")
PROXY_TIMEOUT = float(os.environ.get("GHOSTWRITER_PROXY_TIMEOUT", "2.0"))


def _import_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_dashboard = _import_module("dash_dev", DASHBOARD_DIR / "dev_server.py")
SIM = _dashboard.Simulator()

os.environ.setdefault("KB_REPO_ROOT", str(REPO_ROOT))
sys.path.insert(0, str(PR_WATCHER_DIR))
_qs = _import_module("queue_store", PR_WATCHER_DIR / "queue_store.py")
_pt = _import_module("preview_transform", PR_WATCHER_DIR / "preview_transform.py")
_fb = _import_module("feedback_store", PR_WATCHER_DIR / "feedback_store.py")
_ghq = _import_module("gh_queue", PR_WATCHER_DIR / "gh_queue.py")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "guyhizkiau/kb_generation")


def control_reachable() -> bool:
    try:
        req = urllib.request.Request(f"{CONTROL_URL}/api/queue", method="GET")
        with urllib.request.urlopen(req, timeout=PROXY_TIMEOUT) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False


def proxy_request(method: str, path: str, body: bytes | None = None, query: str = "") -> tuple[int, bytes]:
    url = f"{CONTROL_URL}{path}"
    if query:
        url = f"{url}?{query}"
    headers: dict[str, str] = {}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read()


def _claude_running() -> bool:
    """True when a Claude pipeline process is active (VM or local writer)."""
    for pattern in (r"claude.*--dangerously", r"claude.*-p", r"run_claude_code\.py"):
        r = subprocess.run(["pgrep", "-f", pattern], capture_output=True)
        if r.returncode == 0:
            return True
    return False


def local_get_queue() -> dict:
    data = _qs.queue_with_states()
    data = _ghq.enrich_queue_with_open_prs(data, repo=GITHUB_REPO)
    data["claude_running"] = _claude_running()
    return data


def local_put_queue(payload: dict) -> tuple[int, dict]:
    errors = [e for e in _qs.validate_slugs(payload) if e["level"] == "error"]
    if errors:
        return 422, {"errors": errors}
    _qs.save_queue(payload)
    return 200, {"ok": True}


def local_trigger(payload: dict) -> tuple[int, dict]:
    slug = (payload.get("slug") or "").strip()
    reason = payload.get("reason", "manual")
    if not slug:
        return 400, {"ok": False, "error": "slug required"}

    if reason == "manual":
        return 200, {"ok": True, "reason": reason, "mock": True,
                      "note": "control server offline — trigger recorded locally only"}

    if reason == "feedback":
        state_path = _qs.article_state_path(slug)
        if not state_path.exists():
            return 400, {"ok": False, "error": f"no STATE file for {slug}"}
        fields = _qs.read_state_fields(state_path)
        try:
            rc = int(fields.get("REVISION_CYCLE", "0"))
        except ValueError:
            rc = 0
        _qs.write_state_fields(state_path, {
            "PHASE": "REVISING",
            "REVISION_CYCLE": str(rc + 1),
            "FEEDBACK_ISSUE": str(payload.get("issue", "")),
        })
        return 200, {
            "ok": True,
            "reason": reason,
            "mock": True,
            "phase": "revise-from-feedback",
            "revision_cycle": rc + 1,
        }

    return 400, {"ok": False, "error": f"unknown reason '{reason}'"}


def local_merge(payload: dict) -> tuple[int, dict]:
    slug = (payload.get("slug") or "").strip()
    if not slug:
        return 400, {"ok": False, "error": "slug required"}
    pr_number = payload.get("pr_number")
    if pr_number is not None:
        pr_number = int(pr_number)
    result = _ghq.merge_article_pr(slug, pr_number=pr_number, repo=GITHUB_REPO)
    code = 200 if result.get("ok") else 400
    return code, result


def local_feedback(slug: str) -> dict:
    return {"slug": slug, "annotations": _fb.read_feedback(slug)}


def local_article_preview(slug: str, origin: str) -> tuple[int, bytes, str]:
    code, html = _pt.resolve_preview_html(REPO_ROOT, slug, origin)
    if code != 200:
        return 404, b"", "application/json"
    return 200, html.encode("utf-8"), "text/html; charset=utf-8"


def local_append_feedback(payload: dict) -> tuple[int, dict]:
    slug = (payload.get("slug") or "").strip()
    if not slug:
        return 400, {"ok": False, "error": "slug required"}
    ann = {k: v for k, v in payload.items() if k != "slug"}
    result = _fb.append_feedback(slug, ann)
    code = 200 if result.get("ok") else 400
    return code, result


def _git_local(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(REPO_ROOT), capture_output=True, text=True,
    )


def local_delete_article(slug: str, remove_from_plan: bool) -> tuple[int, dict]:
    """Inline fallback for DELETE /api/articles/<slug> when control is offline."""
    slug = (slug or "").strip()
    if not _qs.SLUG_RE.match(slug):
        return 400, {"ok": False, "error": f"invalid slug '{slug}'"}

    merged = False
    try:
        merged = _qs.article_is_merged(slug)
    except Exception:
        pass

    try:
        res = _ghq.close_article_pr(slug, repo=GITHUB_REPO)
        if not res.get("ok"):
            print(f"[ghostwriter-shim] close PR for {slug} failed: {res.get('error')}")
    except Exception as exc:
        print(f"[ghostwriter-shim] close_article_pr({slug}) raised: {exc}")

    _git_local("branch", "-D", f"article/{slug}")
    _git_local("branch", "-rd", f"origin/article/{slug}")

    pushed = False
    push_failed = False
    push_error = ""
    if merged:
        _git_local("rm", "-r", "--quiet", f"articles/{slug}")
        _qs.delete_article_dir(slug)
        _git_local("commit", "-m", f"chore(article): delete {slug}")
        push = _git_local("push", "origin", "main")
        if push.returncode == 0:
            pushed = True
        else:
            push_failed = True
            push_error = (push.stderr or "git push failed").strip()
    else:
        _qs.delete_article_dir(slug)

    try:
        _fb.delete_feedback(slug)
    except Exception as exc:
        print(f"[ghostwriter-shim] delete feedback for {slug} failed: {exc}")

    removed_from_plan = False
    if remove_from_plan:
        try:
            removed_from_plan = _qs.remove_article_from_queue(slug)
        except Exception as exc:
            print(f"[ghostwriter-shim] remove {slug} from queue failed: {exc}")

    result = {
        "ok": True,
        "slug": slug,
        "merged": merged,
        "removed_from_plan": removed_from_plan,
        "pushed": pushed,
    }
    if push_failed:
        result["push_failed"] = True
        result["error"] = push_error
    return 200, result


def local_remove_feedback(slug: str, ann_id: str) -> tuple[int, dict]:
    if not slug:
        return 400, {"ok": False, "error": "slug required"}
    if not ann_id:
        return 400, {"ok": False, "error": "id required"}
    result = _fb.remove_feedback(slug, ann_id)
    if not result.get("ok"):
        code = 404 if result.get("error") == "annotation not found" else 400
        return code, result
    return 200, result


STATIC_DIR = GHOSTWRITER_DIR / "static"


class ShimHandler(BaseHTTPRequestHandler):
    simulator = SIM
    use_control: bool | None = None

    def log_message(self, fmt: str, *args) -> None:
        print(f"[ghostwriter-shim] {fmt % args}")

    @classmethod
    def _control_up(cls) -> bool:
        if cls.use_control is None:
            cls.use_control = control_reachable()
            mode = "proxy → control" if cls.use_control else "inline queue_store fallback"
            print(f"[ghostwriter-shim] API mode: {mode} ({CONTROL_URL})")
        return cls.use_control

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_bytes(self, code: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, obj: object, code: int = 200) -> None:
        self._send_bytes(code, json.dumps(obj).encode())

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/static/"):
            rel = path[len("/static/"):]
            file_path = (STATIC_DIR / rel).resolve()
            if not str(file_path).startswith(str(STATIC_DIR.resolve())) or not file_path.is_file():
                self._send_json({"error": "not found"}, 404)
                return
            ctype = "application/octet-stream"
            if file_path.suffix == ".css":
                ctype = "text/css; charset=utf-8"
            elif file_path.suffix == ".js":
                ctype = "application/javascript; charset=utf-8"
            self._send_bytes(200, file_path.read_bytes(), ctype)
            return

        if path == "/status/status.json":
            self._send_json(self.simulator.status_payload())
            return
        if path == "/status/health.json":
            self._send_json(self.simulator.health_payload())
            return

        if path.startswith("/api/"):
            # Preview is always served locally (read-only + auto-render from final.md).
            if path.startswith("/api/articles/") and path.endswith("/preview"):
                slug = path[len("/api/articles/"):-len("/preview")]
                origin = f"http://{self.headers.get('Host', f'127.0.0.1:{PORT}')}"
                code, body, ctype = local_article_preview(slug, origin)
                if code != 200:
                    self._send_json({"error": f"preview not available for {slug}"}, 404)
                    return
                self._send_bytes(code, body, ctype)
                return

            if self._control_up():
                try:
                    code, raw = proxy_request("GET", path, query=parsed.query)
                    self._send_bytes(code, raw)
                    return
                except urllib.error.HTTPError as exc:
                    self._send_bytes(exc.code, exc.read())
                    return
                except Exception as exc:
                    self._send_json({"error": str(exc)}, 502)
                    return

            if path == "/api/queue":
                try:
                    self._send_json(local_get_queue())
                except FileNotFoundError:
                    self._send_json({"error": "clusters/queue.json not found"}, 404)
                except Exception as exc:
                    self._send_json({"error": str(exc)}, 500)
                return
            if path == "/api/feedback":
                slug = parse_qs(parsed.query).get("slug", [""])[0]
                if not slug:
                    self._send_json({"error": "slug required"}, 400)
                    return
                self._send_json(local_feedback(slug))
                return
            self._send_json({"error": "not found"}, 404)
            return

        self._send_json({"error": "not found"}, 404)

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/queue":
            self._send_json({"error": "not found"}, 404)
            return

        body = self._read_body()
        if self._control_up():
            try:
                code, raw = proxy_request("PUT", parsed.path, body=body)
                self._send_bytes(code, raw)
                return
            except urllib.error.HTTPError as exc:
                self._send_bytes(exc.code, exc.read())
                return
            except Exception as exc:
                self._send_json({"error": str(exc)}, 502)
                return

        try:
            payload = json.loads(body or b"{}")
            code, result = local_put_queue(payload)
            self._send_json(result, code)
        except Exception as exc:
            self._send_json({"error": str(exc)}, 400)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_body()

        if path in ("/poll-now", "/retry", "/api/queue/trigger", "/api/queue/merge", "/api/feedback") and self._control_up():
            try:
                code, raw = proxy_request("POST", path, body=body or None)
                self._send_bytes(code, raw)
                return
            except urllib.error.HTTPError as exc:
                self._send_bytes(exc.code, exc.read())
                return
            except Exception as exc:
                if path not in ("/api/queue/trigger", "/api/feedback"):
                    self._send_json({"error": str(exc)}, 502)
                # fall through to local mock for trigger/feedback only

        if path == "/poll-now":
            self.simulator.poll_now()
            self._send_json({"ok": True, "mock": not self._control_up()})
            return

        if path == "/retry":
            data = json.loads(body or b"{}")
            cid = data.get("comment_id", "")
            if cid:
                self.simulator.retry_comment(cid)
            self._send_json({"ok": True, "comment_id": cid, "mock": not self._control_up()})
            return

        if path == "/api/queue/trigger":
            try:
                payload = json.loads(body or b"{}")
                code, result = local_trigger(payload)
                self._send_json(result, code)
            except Exception as exc:
                self._send_json({"error": str(exc)}, 400)
            return

        if path == "/api/queue/merge":
            try:
                payload = json.loads(body or b"{}")
                code, result = local_merge(payload)
                self._send_json(result, code)
            except Exception as exc:
                self._send_json({"error": str(exc)}, 400)
            return

        if path == "/api/feedback":
            try:
                payload = json.loads(body or b"{}")
                code, result = local_append_feedback(payload)
                self._send_json(result, code)
            except Exception as exc:
                self._send_json({"error": str(exc)}, 400)
            return

        if path == "/dev/scenario":
            qs = parse_qs(parsed.query)
            name = (qs.get("name") or [""])[0]
            try:
                autoplay = (qs.get("autoplay") or ["1"])[0] != "0"
                self.simulator.start_scenario(name, autoplay=autoplay)
                self._send_json({"ok": True, "scenario": name})
            except ValueError as exc:
                self._send_json({"ok": False, "error": str(exc)}, 400)
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
                self.simulator._reset_idle()
            self._send_json({"ok": True})
            return

        self._send_json({"error": "not found"}, 404)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/feedback" and self._control_up():
            try:
                code, raw = proxy_request("DELETE", path, query=parsed.query)
                if 200 <= code < 300:
                    self._send_bytes(code, raw)
                    return
            except urllib.error.HTTPError as exc:
                # Older control servers may not implement DELETE — handle locally.
                if exc.code not in (404, 405, 501):
                    self._send_bytes(exc.code, exc.read())
                    return
            except Exception:
                pass  # fall through to local handler

        if path.startswith("/api/articles/") and self._control_up():
            try:
                code, raw = proxy_request("DELETE", path, query=parsed.query)
                if 200 <= code < 300:
                    self._send_bytes(code, raw)
                    return
            except urllib.error.HTTPError as exc:
                if exc.code not in (404, 405, 501):
                    self._send_bytes(exc.code, exc.read())
                    return
            except Exception:
                pass  # fall through to local handler

        if path == "/api/feedback":
            qs = parse_qs(parsed.query)
            slug = qs.get("slug", [""])[0]
            ann_id = qs.get("id", [""])[0]
            code, result = local_remove_feedback(slug, ann_id)
            self._send_json(result, code)
            return

        if path.startswith("/api/articles/"):
            qs = parse_qs(parsed.query)
            slug = path[len("/api/articles/"):].strip("/")
            remove_from_plan = qs.get("remove_from_plan", ["false"])[0].lower() == "true"
            code, result = local_delete_article(slug, remove_from_plan)
            self._send_json(result, code)
            return

        self._send_json({"error": "not found"}, 404)


def main() -> None:
    demo = os.environ.get("GHOSTWRITER_AUTO_DEMO", "1") == "1"
    if demo:
        try:
            SIM.start_scenario("comment_resolution", autoplay=True)
            print("  Demo:    comment_resolution scenario (autoplay)")
        except Exception as exc:
            print(f"  Demo:    could not start scenario — {exc}")

    server = ThreadingHTTPServer(("127.0.0.1", PORT), ShimHandler)
    code, html = _pt.load_preview_html(REPO_ROOT, "01-log-in-to-specterx", f"http://127.0.0.1:{PORT}")
    preview_ok = code == 200 and "ghostwriter-annotate" in html
    print("SpecterX Ghostwriter — local API shim")
    print(f"  Listen:  http://127.0.0.1:{PORT}/")
    print(f"  Control: {CONTROL_URL} (proxy when reachable)")
    print(f"  Preview: /api/articles/{{slug}}/preview ({'ok' if preview_ok else 'FAILED'})")
    print(f"  Status:  /status/status.json  /status/health.json (simulator)")
    print(f"  Repo:    {REPO_ROOT}")
    print("  Vite dev: leave VITE_API_BASE unset in .env.local (proxy via :5173)")
    print("  Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        SIM.cancel_timer()


if __name__ == "__main__":
    main()
