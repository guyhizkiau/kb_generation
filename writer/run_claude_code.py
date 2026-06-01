#!/usr/bin/env python3
"""Wrap `claude -p` for a single pipeline phase against one article.

Usage:
    python writer/run_claude_code.py --article NN-slug --phase draft
    python writer/run_claude_code.py --article NN-slug --phase test-plan
    python writer/run_claude_code.py --article NN-slug --phase revise-from-test
    python writer/run_claude_code.py --article NN-slug --phase voice-pass
    python writer/run_claude_code.py --article NN-slug --phase revise-from-pr

Each phase corresponds to a prompt file under pipeline/prompts/ and a set of
expected outputs under workspace/articles/<slug>/. The wrapper assembles
the prompt, invokes Claude Code in non-interactive (--print) mode, and
streams output to stdout while also tee-ing it into a per-run log under
workspace/articles/<slug>/.writer-logs/.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shlex
import subprocess
import sys
from pathlib import Path

PHASE_TO_PROMPT = {
    "draft": "01-draft.md",
    "test-plan": "02-test-plan.md",
    "revise-from-test": "03-revise-from-test.md",
    "voice-pass": "04a-voice-pass.md",
    "revise-from-pr": "04-revise-from-pr-comments.md",
}

REPO_ROOT = Path(__file__).resolve().parent.parent


def article_dir(slug: str) -> Path:
    """Resolve the article working directory.

    Historically the pipeline used `workspace/articles/<slug>/` but the
    canonical location moved to `articles/<slug>/`. We prefer the
    canonical location if it exists; we fall back to the legacy path
    only if the canonical one is missing AND the legacy one is present.
    """
    canonical = REPO_ROOT / "articles" / slug
    legacy = REPO_ROOT / "workspace" / "articles" / slug
    if canonical.exists():
        return canonical
    if legacy.exists():
        return legacy
    return canonical  # create under the canonical path by default


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
        f"When you finish, update the `STATE` file in the working\n"
        f"directory as the prompt instructs, and then exit.\n\n"
        f"---\n\n"
    )
    return header + body


def build_command(slug: str, prompt: str, model: str | None, extra_allow: list[str]) -> list[str]:
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
    ] + extra_allow
    cmd = [
        "claude",
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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--article", required=True, help="Article slug, e.g. 01-share-file-with-external-user")
    p.add_argument("--phase", required=True, choices=list(PHASE_TO_PROMPT))
    p.add_argument(
        "--model",
        default=os.environ.get("WRITER_MODEL", "sonnet"),
        help="Claude model alias or full ID. Default: sonnet (set WRITER_MODEL to override).",
    )
    p.add_argument(
        "--allow",
        action="append",
        default=[],
        help="Extra tool allowance, e.g. 'Bash(gh *)'. Repeatable.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the assembled command without invoking Claude.",
    )
    args = p.parse_args(argv)

    slug = args.article
    adir = article_dir(slug)
    adir.mkdir(parents=True, exist_ok=True)
    log_dir = adir / ".writer-logs"
    log_dir.mkdir(exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = log_dir / f"{stamp}-{args.phase}.log"

    prompt = assemble_prompt(slug, args.phase)
    cmd = build_command(slug, prompt, args.model, args.allow)

    printable = " ".join(shlex.quote(c) for c in cmd[:2] + ["<prompt>"] + cmd[3:])
    print(f"[writer] article={slug} phase={args.phase} model={args.model}", flush=True)
    print(f"[writer] cmd: {printable}", flush=True)
    print(f"[writer] log: {log_path}", flush=True)

    if args.dry_run:
        return 0

    with log_path.open("w", encoding="utf-8") as log:
        log.write(f"# writer run {stamp}\n# article={slug} phase={args.phase} model={args.model}\n# cmd={printable}\n\n")
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
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
