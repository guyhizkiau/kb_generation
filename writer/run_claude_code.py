#!/usr/bin/env python3
"""Wrap `claude -p` for a single pipeline phase against one article.

Usage:
    python writer/run_claude_code.py --article NN-slug --phase draft
    python writer/run_claude_code.py --article NN-slug --phase research
    python writer/run_claude_code.py --article NN-slug --phase test-plan
    python writer/run_claude_code.py --article NN-slug --phase revise-from-test
    python writer/run_claude_code.py --article NN-slug --phase voice-pass
    python writer/run_claude_code.py --article NN-slug --phase revise-from-feedback

Exit codes:
    0 — phase completed successfully
    1 — phase failed (subprocess error or missing artifact)
    3 — pipeline busy (another article is in-flight; use --force with KB_SERIAL_OVERRIDE=1)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json as _json
import os
import select
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

try:
    import pty as _pty
    _HAS_PTY = True
except ImportError:  # pragma: no cover — Windows fallback
    _HAS_PTY = False

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from store.machine import active_article, block, current_phase, transition  # noqa: E402
from store.paths import article_dir  # noqa: E402

# ── phase maps ───────────────────────────────────────────────────────────────

PHASE_TO_PROMPT = {
    "research": "02-research.md",
    "draft": "01-draft.md",
    "test-plan": "02-test-plan.md",
    "revise-from-test": "03-revise-from-test.md",
    "voice-pass": "04a-voice-pass.md",
    "revise-from-feedback": "06-revise-from-feedback.md",
}

PHASE_ARTIFACTS: dict[str, str] = {
    "research": "research/competitor-coverage.md",
    "draft": "draft-1.md",
    "test-plan": "test-plan.json",
    "revise-from-test": "draft-2.md",
    "voice-pass": "final.md",
    "revise-from-feedback": "final.md",
}

PHASE_TRANSITIONS: dict[str, tuple[str, str]] = {
    "research": ("RESEARCHING", "DRAFTING"),
    "draft": ("DRAFTING", "TESTING"),
    "revise-from-test": ("REVISING", "FINALIZING"),
    "voice-pass": ("FINALIZING", "IN_REVIEW"),
    "revise-from-feedback": ("REVISING", "FINALIZING"),
}

PHASE_EXTRA_ALLOW: dict[str, list[str]] = {
    "research": [
        "Bash(python3 *)",
        "Bash(python *)",
    ],
    "revise-from-feedback": [
        "Bash(python3 *)",
        "Bash(python *)",
        "Bash(git *)",
    ],
}

# ── timing knobs ─────────────────────────────────────────────────────────────

# Hard-kill if no output for this many seconds (default 40 min).
WRITER_PHASE_TIMEOUT_SECS = int(os.environ.get("WRITER_PHASE_TIMEOUT_SECS", "2400"))
# Warn in log after this many seconds of silence (5 min).
WRITER_STALL_WARN_SECS = 300
# Retry once if the subprocess exits nonzero within this many seconds (2 min).
WRITER_FAST_FAIL_SECS = 120
# Model to use for the cheap gate-fixer pass.
WRITER_FIXER_MODEL = os.environ.get("WRITER_FIXER_MODEL", "haiku")


# ── prompt / command assembly ─────────────────────────────────────────────────

def assemble_prompt(slug: str, phase: str) -> str:
    """Read the phase prompt and prepend article-specific context."""
    prompt_path = REPO_ROOT / "pipeline" / "prompts" / PHASE_TO_PROMPT[phase]
    body = prompt_path.read_text(encoding="utf-8")
    article_path = article_dir(slug)
    header = (
        f"# Pipeline run\n\n"
        f"You are running the `{phase}` phase for article `{slug}`.\n\n"
        f"The article working directory is:\n\n"
        f"    {article_path}\n\n"
        f"All file paths in the prompt below that use placeholders like\n"
        f"`articles/<NN-slug>/...` or `articles/{slug}/...` refer to this\n"
        f"working directory.\n\n"
        f"Do not edit the STATE file — the pipeline runner updates it.\n\n"
        f"---\n\n"
    )
    return header + body


def build_command(
    slug: str,
    prompt: str,
    phase: str,
    model: str | None,
    extra_allow: list[str],
    claude_bin: str,
) -> list[str]:
    allow = [
        "Read",
        "Write",
        "Edit",
        "Glob",
        "Grep",
        "Bash(ls *)",
        "Bash(cat *)",
        "Bash(date *)",
        "Bash(mkdir *)",
    ] + PHASE_EXTRA_ALLOW.get(phase, []) + extra_allow
    cmd = [
        claude_bin,
        "-p",
        prompt,
        "--add-dir",
        str(article_dir(slug)),
        "--add-dir",
        str(REPO_ROOT),
        "--allowedTools",
        " ".join(allow),
        "--permission-mode",
        "acceptEdits",
        "--output-format",
        "stream-json",
        "--verbose",
    ]
    if model:
        cmd.extend(["--model", model])
    return cmd


# ── stream-json helpers ───────────────────────────────────────────────────────

def _parse_stream_event(raw: str) -> dict | None:
    """Try to parse a stream-json event line. Return None if not a JSON object."""
    line = raw.strip().lstrip("\r")
    if not line.startswith("{"):
        return None
    try:
        return _json.loads(line)
    except _json.JSONDecodeError:
        return None


def _summarize_event(evt: dict) -> str | None:
    """Return a one-line human-readable summary of a stream-json event, or None to skip."""
    etype = evt.get("type", "")

    if etype == "tool_use":
        name = evt.get("name", "?")
        inp = evt.get("input", {})
        summary = _json.dumps(inp, separators=(",", ":"))[:100]
        return f"tool: {name} {summary}"

    if etype == "tool_result":
        is_err = evt.get("is_error", False)
        content = evt.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                c.get("text", "") for c in content if isinstance(c, dict)
            )
        preview = str(content)[:100].replace("\n", " ")
        tag = "error" if is_err else "ok"
        return f"tool_result({tag}): {preview}"

    if etype == "assistant":
        msg = evt.get("message", {})
        for chunk in msg.get("content", []):
            if isinstance(chunk, dict) and chunk.get("type") == "text":
                text = chunk.get("text", "")[:120].replace("\n", " ")
                if text.strip():
                    return f"text: {text}"
        return None

    if etype == "result":
        sub = evt.get("subtype", "?")
        cost = evt.get("cost_usd", 0.0)
        dur_ms = evt.get("duration_ms", 0)
        turns = evt.get("num_turns", "?")
        dur_s = dur_ms / 1000
        dur_str = f"{dur_s / 60:.1f}m" if dur_s >= 60 else f"{dur_s:.1f}s"
        return f"result: {sub} (cost: ${cost:.4f}, duration: {dur_str}, turns: {turns})"

    return None


# ── heartbeat ─────────────────────────────────────────────────────────────────

def _update_heartbeat(
    adir: Path,
    phase: str,
    started_at: float,
    last_tool: str,
    event_count: int,
) -> None:
    """Atomically write a heartbeat.json so the daemon can show live progress."""
    hb_dir = adir / ".writer-logs"
    hb_dir.mkdir(exist_ok=True)
    payload = {
        "phase": phase,
        "started_at": dt.datetime.fromtimestamp(started_at, dt.timezone.utc).isoformat(),
        "last_event_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "last_tool": last_tool,
        "event_count": event_count,
    }
    tmp = hb_dir / "heartbeat.tmp"
    tmp.write_text(_json.dumps(payload))
    tmp.replace(hb_dir / "heartbeat.json")


# ── pre-flight ────────────────────────────────────────────────────────────────

def _preflight(slug: str, phase: str, claude_bin: str) -> None:
    """Raise RuntimeError with a precise message on any pre-launch problem."""
    if not shutil.which(claude_bin) and not os.path.isfile(claude_bin):
        raise RuntimeError(f"claude binary not found or not executable: {claude_bin!r}")

    prompt_file = REPO_ROOT / "pipeline" / "prompts" / PHASE_TO_PROMPT.get(phase, "")
    if not prompt_file.is_file():
        raise RuntimeError(f"prompt file missing: {prompt_file}")

    adir = article_dir(slug)
    try:
        test_file = adir / ".preflight-test"
        test_file.write_text("")
        test_file.unlink()
    except OSError as exc:
        raise RuntimeError(f"article dir not writable ({adir}): {exc}") from exc


# ── PTY subprocess runner ─────────────────────────────────────────────────────

def _run_with_pty(
    slug: str,
    phase: str,
    cmd: list[str],
    log_handle,
    started_at: float,
) -> int:
    """Run cmd under a PTY, streaming parsed events to log_handle. Returns exit code."""
    adir = article_dir(slug)

    last_event_time: list[float] = [time.time()]
    last_tool: list[str] = ["(none)"]
    event_count: list[int] = [0]

    if _HAS_PTY:
        master_fd, slave_fd = _pty.openpty()
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(REPO_ROOT),
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                close_fds=True,
                preexec_fn=os.setpgrp,
            )
        except Exception:
            os.close(master_fd)
            os.close(slave_fd)
            raise
        os.close(slave_fd)
    else:
        # Fallback for systems without PTY (keeps the function usable)
        proc = subprocess.Popen(
            cmd,
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            preexec_fn=os.setpgrp,
        )
        master_fd = None

    # ── watchdog thread ───────────────────────────────────────────────────────

    def _watchdog() -> None:
        warned = False
        while proc.poll() is None:
            time.sleep(10)
            idle = time.time() - last_event_time[0]
            if idle > WRITER_PHASE_TIMEOUT_SECS:
                ts = dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S")
                msg = (
                    f"[{ts}] [watchdog] HARD TIMEOUT: no output for {idle:.0f}s "
                    f"(last tool: {last_tool[0]}) — killing process group\n"
                )
                log_handle.write(msg)
                log_handle.flush()
                sys.stdout.write(msg)
                sys.stdout.flush()
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
                return
            if idle > WRITER_STALL_WARN_SECS and not warned:
                warned = True
                ts = dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S")
                msg = (
                    f"[{ts}] [watchdog] STALL WARNING: no output for {idle:.0f}s "
                    f"(last tool: {last_tool[0]})\n"
                )
                log_handle.write(msg)
                log_handle.flush()
                sys.stdout.write(msg)
                sys.stdout.flush()

    wdog = threading.Thread(target=_watchdog, daemon=True)
    wdog.start()

    # ── event handler (called for every output line) ──────────────────────────

    def _handle_line(raw_bytes: bytes) -> None:
        raw = raw_bytes.decode("utf-8", errors="replace").rstrip("\r\n")
        if not raw:
            return

        last_event_time[0] = time.time()
        event_count[0] += 1
        ts = dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S")

        evt = _parse_stream_event(raw)
        if evt is not None:
            if evt.get("type") == "tool_use":
                last_tool[0] = evt.get("name", last_tool[0])
            summary = _summarize_event(evt)
            if summary:
                line_out = f"[{ts}] {summary}\n"
                log_handle.write(line_out)
                log_handle.flush()
                sys.stdout.write(line_out)
                sys.stdout.flush()
            # Raw JSON is not written to the log — only the human-readable summary.
        else:
            # Plain text (e.g. during startup before stream-json kicks in).
            prefix = f"[{ts}] " if not raw.startswith("[") else ""
            line_out = f"{prefix}{raw}\n"
            log_handle.write(line_out)
            log_handle.flush()
            sys.stdout.write(line_out)
            sys.stdout.flush()

        try:
            _update_heartbeat(adir, phase, started_at, last_tool[0], event_count[0])
        except Exception:
            pass

    # ── read loop ─────────────────────────────────────────────────────────────

    if _HAS_PTY and master_fd is not None:
        buf = b""
        while True:
            try:
                r, _, _ = select.select([master_fd], [], [], 1.0)
            except (select.error, ValueError):
                break
            if r:
                try:
                    chunk = os.read(master_fd, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    line_bytes, buf = buf.split(b"\n", 1)
                    _handle_line(line_bytes)

            if proc.poll() is not None:
                # Drain any remaining data after the process exits.
                try:
                    while True:
                        r2, _, _ = select.select([master_fd], [], [], 0.1)
                        if not r2:
                            break
                        chunk = os.read(master_fd, 4096)
                        if not chunk:
                            break
                        buf += chunk
                except OSError:
                    pass
                if buf:
                    _handle_line(buf)
                break

        try:
            os.close(master_fd)
        except OSError:
            pass
    else:
        # Pipe fallback: iterate lines from stdout
        assert proc.stdout is not None
        for line in proc.stdout:
            _handle_line(line.encode())

    rc = proc.wait()
    wdog.join(timeout=2)
    return rc


# ── gate fixer ────────────────────────────────────────────────────────────────

def _run_gate_fixer(
    slug: str,
    coverage_path: Path,
    gate_error: str,
    claude_bin: str,
    log_handle,
) -> bool:
    """Run a cheap haiku one-shot to reformat competitor-coverage.md.

    Returns True if the research gate passes after the fix.
    """
    from pipeline.gates import RESEARCH_CONTRACT, check_research_gate

    fixer_prompt = (
        f"The file `{coverage_path}` failed the pipeline quality gate.\n\n"
        f"Gate error:\n{gate_error}\n\n"
        "TASK: Reformat the EXISTING content of the file to satisfy the "
        "gate contract shown above. Do NOT invent new sources. Do NOT "
        "remove any information already in the file. Only restructure the "
        "format so the gate passes.\n\n"
        f"Required format:\n{RESEARCH_CONTRACT}\n\n"
        "Steps:\n"
        "1. Read the current file.\n"
        "2. Identify all competitor articles/sources already described.\n"
        "3. Ensure the file contains a section headed `## Articles read` "
        "with one bullet per source (minimum 3).\n"
        "4. Write the updated file.\n"
    )

    fixer_cmd = [
        claude_bin,
        "-p",
        fixer_prompt,
        "--add-dir",
        str(article_dir(slug)),
        "--allowedTools",
        "Read Write Edit",
        "--permission-mode",
        "acceptEdits",
        "--model",
        WRITER_FIXER_MODEL,
    ]

    ts = dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S")
    msg = (
        f"[{ts}] [fixer] gate failed; launching haiku one-shot to reformat "
        f"competitor-coverage.md (model: {WRITER_FIXER_MODEL})\n"
    )
    log_handle.write(msg)
    log_handle.flush()
    sys.stdout.write(msg)
    sys.stdout.flush()

    try:
        result = subprocess.run(
            fixer_cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=180,
        )
        ts = dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S")
        exit_line = f"[{ts}] [fixer] exit={result.returncode}\n"
        log_handle.write(exit_line)
        log_handle.flush()
        sys.stdout.write(exit_line)
        sys.stdout.flush()
        if result.stdout.strip():
            preview = result.stdout.strip()[:300].replace("\n", " ")
            log_handle.write(f"[{ts}] [fixer] output: {preview}\n")
            log_handle.flush()
    except subprocess.TimeoutExpired:
        ts = dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S")
        msg = f"[{ts}] [fixer] TIMEOUT after 180s — skipping remediation\n"
        log_handle.write(msg)
        log_handle.flush()
        sys.stdout.write(msg)
        sys.stdout.flush()
        return False
    except Exception as exc:
        ts = dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S")
        msg = f"[{ts}] [fixer] ERROR: {exc}\n"
        log_handle.write(msg)
        log_handle.flush()
        sys.stdout.write(msg)
        sys.stdout.flush()
        return False

    ok, msg2 = check_research_gate(slug)
    ts = dt.datetime.now(dt.timezone.utc).strftime("%H:%M:%S")
    if ok:
        log_handle.write(f"[{ts}] [fixer] gate passed after fix: {msg2}\n")
        log_handle.flush()
        sys.stdout.write(f"[{ts}] [fixer] gate passed: {msg2}\n")
        sys.stdout.flush()
        return True

    log_handle.write(f"[{ts}] [fixer] gate still failed after fix: {msg2}\n")
    log_handle.flush()
    sys.stdout.write(f"[{ts}] [fixer] gate still failed: {msg2}\n")
    sys.stdout.flush()
    return False


def run_gate_with_remediation(
    slug: str,
    phase: str,
    claude_bin: str,
    log_handle,
) -> tuple[bool, str]:
    """Check the research gate; attempt cheap remediation if it fails with the artifact present.

    Returns (ok, message).  Currently only implemented for the research phase.
    """
    if phase != "research":
        return True, "no gate for this phase"

    from pipeline.gates import check_research_gate

    ok, msg = check_research_gate(slug)
    if ok:
        return True, msg

    # Cheap fix path: only attempt if the artifact already exists.
    coverage_path = article_dir(slug) / "research" / "competitor-coverage.md"
    if coverage_path.is_file():
        fixed = _run_gate_fixer(slug, coverage_path, msg, claude_bin, log_handle)
        if fixed:
            ok2, msg2 = check_research_gate(slug)
            return ok2, msg2

    return False, msg


# ── state transitions ─────────────────────────────────────────────────────────

def apply_phase_transition(slug: str, phase: str) -> None:
    """Transition STATE after a successful phase completion."""
    spec = PHASE_TRANSITIONS.get(phase)
    if spec is None:
        return
    expected_from, to_phase = spec
    cur = current_phase(slug)
    if cur != expected_from:
        block(slug, f"{phase} completed but phase is {cur}, expected {expected_from}")
        raise RuntimeError(f"phase mismatch: {cur} != {expected_from}")
    transition(slug, to_phase)


# ── main ──────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--article", required=True, help="Article slug")
    p.add_argument("--phase", required=True, choices=list(PHASE_TO_PROMPT))
    p.add_argument(
        "--model",
        default=os.environ.get("WRITER_MODEL", "sonnet"),
        help="Claude model alias or full ID.",
    )
    p.add_argument("--allow", action="append", default=[], help="Extra tool allowance.")
    p.add_argument("--dry-run", action="store_true", help="Print command without invoking.")
    p.add_argument(
        "--claude-bin",
        default="claude",
        help="Claude CLI binary (default: claude).",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Bypass serial guard (requires KB_SERIAL_OVERRIDE=1).",
    )
    args = p.parse_args(argv)

    slug = args.article

    if not args.force or os.environ.get("KB_SERIAL_OVERRIDE") != "1":
        active = active_article()
        if active is not None and active != slug:
            print(
                f"[writer] pipeline busy: article '{active}' is in-flight "
                f"(requested '{slug}')",
                flush=True,
            )
            return 3

    adir = article_dir(slug)
    adir.mkdir(parents=True, exist_ok=True)
    log_dir = adir / ".writer-logs"
    log_dir.mkdir(exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = log_dir / f"{stamp}-{args.phase}.log"

    # ── pre-flight ────────────────────────────────────────────────────────────
    try:
        _preflight(slug, args.phase, args.claude_bin)
    except RuntimeError as exc:
        block(slug, f"preflight failed: {exc}")
        print(f"[writer] preflight failed: {exc}", flush=True)
        return 1

    prompt = assemble_prompt(slug, args.phase)
    cmd = build_command(slug, prompt, args.phase, args.model, args.allow, args.claude_bin)

    printable = f"claude -p <prompt> {' '.join(cmd[3:])}"
    print(f"[writer] article={slug} phase={args.phase} model={args.model}", flush=True)
    print(f"[writer] cmd: {printable}", flush=True)
    print(f"[writer] log: {log_path}", flush=True)

    if args.dry_run:
        return 0

    with log_path.open("w", encoding="utf-8") as log:
        log.write(
            f"# writer run {stamp}\n"
            f"# article={slug} phase={args.phase} model={args.model}\n"
            f"# cmd={printable}\n\n"
        )
        log.flush()

        started_at = time.time()
        rc = _run_with_pty(slug, args.phase, cmd, log, started_at)
        elapsed = time.time() - started_at

        print(f"[writer] exit={rc} elapsed={elapsed:.0f}s", flush=True)
        log.write(f"\n# exit={rc} elapsed={elapsed:.0f}s\n")
        log.flush()

        # ── fast-failure retry ────────────────────────────────────────────────
        # If the process failed very quickly it was likely a transient startup
        # error (auth hiccup, binary temporarily unavailable).  Retry once and
        # only once; long-running failures block immediately.
        if rc != 0 and elapsed < WRITER_FAST_FAIL_SECS:
            msg = (
                f"[writer] phase exited {rc} after {elapsed:.0f}s "
                f"(within {WRITER_FAST_FAIL_SECS}s fast-fail window) — retrying once\n"
            )
            print(msg, end="", flush=True)
            log.write(msg)
            log.flush()
            started_at = time.time()
            rc = _run_with_pty(slug, args.phase, cmd, log, started_at)
            elapsed2 = time.time() - started_at
            print(f"[writer] retry exit={rc} elapsed={elapsed2:.0f}s", flush=True)
            log.write(f"# retry exit={rc} elapsed={elapsed2:.0f}s\n")
            log.flush()

    # ── outcome checks ────────────────────────────────────────────────────────
    if rc != 0:
        block(slug, f"{args.phase} failed: subprocess exit {rc}")
        return 1

    artifact = PHASE_ARTIFACTS.get(args.phase)
    if artifact and not (adir / artifact).is_file():
        block(slug, f"{args.phase} failed: missing artifact {artifact}")
        return 1

    if args.phase == "research":
        with log_path.open("a", encoding="utf-8") as log:
            ok, gate_msg = run_gate_with_remediation(
                slug, args.phase, args.claude_bin, log
            )
        if not ok:
            block(slug, f"research gate: {gate_msg}")
            return 1

    try:
        apply_phase_transition(slug, args.phase)
    except Exception as exc:
        block(slug, f"{args.phase} transition failed: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
