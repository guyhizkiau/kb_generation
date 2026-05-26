"""Top-level tester: read test-plan.json, classify steps, execute, write notes.

Usage:
    python tester/runner.py --article 01-share-file-with-external-user

Reads:
    workspace/articles/<slug>/test-plan.json

Writes:
    workspace/articles/<slug>/test-notes.md
    workspace/articles/<slug>/screenshots/<step>-*.png
    workspace/articles/<slug>/STATE  (advanced to REVISING on success)

The browser backend is wired up (`tester/browser_runner.py`). The
desktop backend is a Phase D deliverable; for now, any step classified
as `desktop` is logged as `couldn't verify (no desktop backend yet)`
in test-notes and the runner moves on. That matches the architecture
doc's "couldn't verify" handling.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import sys
from pathlib import Path
from typing import Any

from tester.browser_runner import BrowserRunner, StepResult
from tester.step_classifier import classify

REPO_ROOT = Path(__file__).resolve().parent.parent
log = logging.getLogger("tester.runner")


def article_dir(slug: str) -> Path:
    return REPO_ROOT / "workspace" / "articles" / slug


def load_plan(slug: str) -> dict[str, Any]:
    path = article_dir(slug) / "test-plan.json"
    if not path.exists():
        raise FileNotFoundError(f"no test-plan.json at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_test_notes(slug: str, results: list[dict[str, Any]]) -> Path:
    out = article_dir(slug) / "test-notes.md"
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    lines: list[str] = []
    lines.append(f"# test-notes — {slug}")
    lines.append("")
    lines.append(f"Generated: {now}")
    lines.append("")
    for r in results:
        lines.append(f"## Step {r['step_id']} — {'ok' if r['ok'] else 'FAIL'}")
        lines.append("")
        lines.append(f"- backend: `{r['backend']}`")
        lines.append(f"- observation: {r['observation']}")
        if r.get("screenshot"):
            lines.append(f"- screenshot: `{r['screenshot']}`")
        if r.get("error"):
            lines.append(f"- error: `{r['error']}`")
        if not r["ok"]:
            lines.append(f"- > ⚠ couldn't verify this step.")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def advance_state(slug: str, next_phase: str) -> None:
    state = article_dir(slug) / "STATE"
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    state.write_text(
        f"PHASE={next_phase}\n"
        f"LAST_UPDATE={now}\n"
        f"NEXT_ACTION=writer reconciles draft-1.md against test-notes.md\n",
        encoding="utf-8",
    )


def execute(slug: str) -> int:
    plan = load_plan(slug)
    steps = plan.get("steps", []) or []
    if not steps:
        log.warning("no steps in test-plan for %s; nothing to do", slug)
        return 0

    screenshots_dir = article_dir(slug) / "screenshots"
    results: list[dict[str, Any]] = []

    desktop_steps: list[dict[str, Any]] = []
    browser_steps: list[dict[str, Any]] = []
    for s in steps:
        backend = classify(s)
        s_with = dict(s)
        s_with["backend"] = backend
        if backend == "browser":
            browser_steps.append(s_with)
        else:
            desktop_steps.append(s_with)

    # Execute browser steps in declared order, in a single browser session.
    if browser_steps:
        with BrowserRunner(screenshots_dir=screenshots_dir) as runner:
            log.info("browser backend mode=%s", runner.mode)
            for s in steps:
                if classify(s) == "browser":
                    res = runner.run_step(s)
                    results.append(_pack(s, res, backend="browser"))
                else:
                    results.append(_pack_skipped(s, backend="desktop"))
    else:
        for s in steps:
            results.append(_pack_skipped(s, backend="desktop"))

    notes_path = write_test_notes(slug, results)
    log.info("wrote %s", notes_path)
    advance_state(slug, "REVISING")

    any_fail = any(not r["ok"] for r in results)
    return 1 if any_fail else 0


def _pack(step: dict[str, Any], res: StepResult, *, backend: str) -> dict[str, Any]:
    return {
        "step_id": res.step_id,
        "ok": res.ok,
        "backend": backend,
        "observation": res.observation,
        "screenshot": res.screenshot,
        "error": res.error,
        "description": step.get("description", ""),
    }


def _pack_skipped(step: dict[str, Any], *, backend: str) -> dict[str, Any]:
    return {
        "step_id": str(step.get("id", "??")),
        "ok": False,
        "backend": backend,
        "observation": "skipped — desktop backend not implemented (Phase D)",
        "screenshot": None,
        "error": None,
        "description": step.get("description", ""),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--article", required=True)
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    return execute(args.article)


if __name__ == "__main__":
    sys.exit(main())
