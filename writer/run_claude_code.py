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
import os
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from store.machine import active_article, block, current_phase, transition  # noqa: E402
from store.paths import article_dir  # noqa: E402

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
    # Research scrapes competitor KBs and does UI recon via Playwright
    # (venv python) — without these the competitor gate can never pass.
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
    ]
    if model:
        cmd.extend(["--model", model])
    return cmd


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

    prompt = assemble_prompt(slug, args.phase)
    cmd = build_command(slug, prompt, args.phase, args.model, args.allow, args.claude_bin)

    printable = " ".join(shlex.quote(c) for c in cmd[:2] + ["<prompt>"] + cmd[3:])
    print(f"[writer] article={slug} phase={args.phase} model={args.model}", flush=True)
    print(f"[writer] cmd: {printable}", flush=True)
    print(f"[writer] log: {log_path}", flush=True)

    if args.dry_run:
        return 0

    with log_path.open("w", encoding="utf-8") as log:
        log.write(
            f"# writer run {stamp}\n# article={slug} phase={args.phase}\n"
            f"# cmd={printable}\n\n"
        )
        log.flush()
        proc = subprocess.Popen(
            cmd,
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            log.write(line)
        rc = proc.wait()

    print(f"[writer] exit={rc}", flush=True)

    if rc != 0:
        block(slug, f"{args.phase} failed: subprocess exit {rc}")
        return 1

    artifact = PHASE_ARTIFACTS.get(args.phase)
    if artifact and not (adir / artifact).is_file():
        block(slug, f"{args.phase} failed: missing artifact {artifact}")
        return 1

    if args.phase == "research":
        from pipeline.gates import check_research_gate
        ok, msg = check_research_gate(slug)
        if not ok:
            block(slug, f"research gate: {msg}")
            return 1

    try:
        apply_phase_transition(slug, args.phase)
    except Exception as exc:
        block(slug, f"{args.phase} transition failed: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
