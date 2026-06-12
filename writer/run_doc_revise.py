#!/usr/bin/env python3
"""Revise a knowledge doc from Ghostwriter annotations.

Usage:
    python writer/run_doc_revise.py --doc style-guide
    python writer/run_doc_revise.py --doc glossary --dry-run

Exit codes:
    0 — success (including git nothing-to-commit)
    1 — failure
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from store.feedback import read_feedback  # noqa: E402

DOC_PATHS: dict[str, tuple[str, str]] = {
    "articles-plan": ("editorial/ARTICLES_PLAN.md", "editorial"),
    "style-guide": ("editorial/STYLE_GUIDE.md", "editorial"),
    "public-kb-scope": ("editorial/PUBLIC_KB_SCOPE.md", "editorial"),
    "glossary": ("canon/GLOSSARY.md", "canon"),
    "do-not-document": ("canon/DO_NOT_DOCUMENT.md", "canon"),
    "competitor-patterns": ("canon/COMPETITOR_PATTERNS.md", "canon"),
    "component-taxonomy": ("product/COMPONENT_TAXONOMY.md", "product"),
    "product-notes": ("product/notes.md", "product"),
}


def assemble_prompt(doc_id: str, rel_path: Path, annotations: list) -> str:
    prompt_path = REPO_ROOT / "pipeline" / "prompts" / "07-revise-doc.md"
    body = prompt_path.read_text(encoding="utf-8")
    area = DOC_PATHS[doc_id][1]
    content = rel_path.read_text(encoding="utf-8") if rel_path.is_file() else ""
    ann_block = json.dumps(annotations, indent=2)
    header = (
        f"# Doc revise run\n\n"
        f"You are revising knowledge doc `{doc_id}` (`{area}`).\n\n"
        f"Target file (edit only this file):\n\n"
        f"    {rel_path}\n\n"
        f"Relative path from repo root: `{DOC_PATHS[doc_id][0]}`\n\n"
        f"## Current document\n\n"
        f"```markdown\n{content}\n```\n\n"
        f"## Annotations to apply\n\n"
        f"```json\n{ann_block}\n```\n\n"
        f"Commit message when done: `docs({area}): revise {doc_id} from feedback`\n\n"
        f"---\n\n"
    )
    return header + body


def build_command(prompt: str, doc_path: Path, claude_bin: str, model: str | None) -> list[str]:
    allow = [
        "Read",
        "Write",
        "Edit",
        "Glob",
        "Grep",
        "Bash(git *)",
        "Bash(ls *)",
        "Bash(cat *)",
    ]
    cmd = [
        claude_bin,
        "-p",
        prompt,
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


def git_commit(doc_id: str, rel: str, area: str) -> int:
    msg = f"docs({area}): revise {doc_id} from feedback"
    subprocess.run(["git", "-C", str(REPO_ROOT), "add", rel], check=False)
    res = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "commit", "-m", msg, "--", rel],
        capture_output=True,
        text=True,
    )
    return res.returncode


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--doc", required=True, help="Knowledge doc id")
    p.add_argument("--claude-bin", default="claude", help="Claude CLI binary")
    p.add_argument("--model", default=os.environ.get("WRITER_MODEL", "sonnet"))
    p.add_argument("--dry-run", action="store_true", help="Print prompt only")
    args = p.parse_args(argv)

    doc_id = args.doc.strip()
    if doc_id not in DOC_PATHS:
        print(f"unknown doc: {doc_id}", file=sys.stderr)
        return 1

    pseudo = f"doc--{doc_id}"
    annotations = read_feedback(pseudo)
    if not annotations:
        print(f"no feedback for {pseudo}", file=sys.stderr)
        return 1

    rel, area = DOC_PATHS[doc_id]
    doc_path = REPO_ROOT / rel
    if not doc_path.is_file():
        print(f"doc file missing: {doc_path}", file=sys.stderr)
        return 1

    prompt = assemble_prompt(doc_id, doc_path, annotations)
    if args.dry_run:
        print(prompt)
        return 0

    cmd = build_command(prompt, doc_path, args.claude_bin, args.model)
    print(f"[run_doc_revise] launching claude for {doc_id}", flush=True)
    res = subprocess.run(cmd, cwd=REPO_ROOT)
    if res.returncode != 0:
        print(f"[run_doc_revise] claude exited {res.returncode}", file=sys.stderr)
        return 1

    git_commit(doc_id, rel, area)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
