"""Top-level tester: read test-plan.json, classify steps, execute, write notes.

Usage:
    python tester/runner.py --article 01-share-file-with-external-user
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from store.machine import block, transition  # noqa: E402
from store.paths import article_dir  # noqa: E402
from store.state import read_state, write_state  # noqa: E402
from store.test_config import load as load_test_config  # noqa: E402
from tester.browser_runner import BrowserRunner, StepResult
from tester.fixtures._generate import ensure_configured_fixtures
from tester.step_classifier import classify

log = logging.getLogger("tester.runner")

# Injectable for tests
_browser_runner_cls: type[BrowserRunner] = BrowserRunner

CASCADE_ABORT_AFTER = 5
CATASTROPHIC_FAIL_FRACTION = 0.5
MAX_TEST_ATTEMPTS = 2


def load_plan(slug: str) -> dict[str, Any]:
    path = article_dir(slug) / "test-plan.json"
    if not path.exists():
        raise FileNotFoundError(f"no test-plan.json at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _is_cleanup_step(step: dict[str, Any]) -> bool:
    sid = str(step.get("id", ""))
    return sid.startswith("C") or sid.lower().startswith("cleanup")


def _is_login_step(step_id: str) -> bool:
    return step_id.startswith("00-")


def _test_attempt(slug: str) -> int:
    try:
        return int(read_state(slug).get("TEST_ATTEMPT", "0"))
    except ValueError:
        return 0


def write_test_notes(
    slug: str,
    results: list[dict[str, Any]],
    *,
    first_failure: str | None = None,
    attempt: int | None = None,
) -> Path:
    out = article_dir(slug) / "test-notes.md"
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    lines: list[str] = []
    lines.append(f"# test-notes — {slug}")
    lines.append("")
    lines.append(f"Generated: {now}")
    if attempt is not None:
        lines.append(f"Test attempt: {attempt}")
    if first_failure:
        lines.append(f"First failure: {first_failure}")
    lines.append("")

    for r in results:
        status = "ok" if r["ok"] else ("skipped-cascade" if r.get("skipped_cascade") else "FAIL")
        lines.append(f"## Step {r['step_id']} — {status}")
        lines.append("")
        lines.append(f"- backend: `{r['backend']}`")
        lines.append(f"- observation: {r['observation']}")
        if r.get("screenshot"):
            lines.append(f"- screenshot: `{r['screenshot']}`")
        if "screenshot-review=BAD" in str(r.get("observation", "")):
            lines.append("- > ⚠ screenshot flagged by review — may need a retake")
        if r.get("error"):
            lines.append(f"- error: `{r['error']}`")
        if not r["ok"] and not r.get("skipped_cascade"):
            lines.append("- > ⚠ couldn't verify this step.")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def _archive_test_notes(slug: str, attempt: int) -> None:
    adir = article_dir(slug)
    src = adir / "test-notes.md"
    if not src.is_file():
        return
    dest = adir / f"test-notes-attempt-{attempt}.md"
    dest.write_text(src.read_text(encoding="utf-8"))
    src.unlink()


def _outcome_stats(results: list[dict[str, Any]]) -> dict[str, Any]:
    executed = [
        r for r in results
        if not r.get("skipped_cascade") and not _is_cleanup_step({"id": r["step_id"]})
    ]
    failed = [r for r in executed if not r["ok"]]
    passed = [r for r in executed if r["ok"]]
    login_failed = any(
        not r["ok"] and _is_login_step(str(r["step_id"]))
        for r in executed
    )
    first_failure = next((r["step_id"] for r in results if not r["ok"]), None)
    return {
        "executed": executed,
        "failed": failed,
        "passed": passed,
        "login_failed": login_failed,
        "first_failure": first_failure,
        "fail_count": len(failed),
        "executed_count": len(executed),
    }


def _is_catastrophic(stats: dict[str, Any]) -> bool:
    if stats["login_failed"]:
        return True
    if stats["executed_count"] == 0:
        return True
    if len(stats["passed"]) == 0:
        return True
    frac = stats["fail_count"] / stats["executed_count"]
    return frac > CATASTROPHIC_FAIL_FRACTION


def _block_reason(stats: dict[str, Any]) -> str:
    ff = stats["first_failure"] or "unknown"
    return (
        f"verification failed: {stats['fail_count']} of {stats['executed_count']} steps failed "
        f"(first failure: step {ff}) — see test-notes.md"
    )


def execute(slug: str) -> int:
    plan = load_plan(slug)
    steps = plan.get("steps", []) or []
    if not steps:
        log.warning("no steps in test-plan for %s; nothing to do", slug)
        return 0

    test_config = load_test_config()
    fixtures_dir = Path(os.environ.get("TEST_FIXTURES_DIR", str(REPO_ROOT / "tester" / "fixtures")))
    ensure_configured_fixtures(fixtures_dir, test_config)

    for s in steps:
        if classify(s) == "desktop":
            block(slug, "desktop steps present; desktop backend not implemented")
            return 1

    screenshots_dir = article_dir(slug) / "screenshots"
    results: list[dict[str, Any]] = []
    consecutive_failures = 0
    cascade_aborted = False

    browser_steps = [s for s in steps if classify(s) == "browser"]
    if browser_steps:
        with _browser_runner_cls(
            screenshots_dir=screenshots_dir,
            test_config=test_config,
        ) as runner:
            log.info("browser backend mode=%s", runner.mode)
            for s in steps:
                if classify(s) != "browser":
                    continue
                if cascade_aborted and not _is_cleanup_step(s):
                    results.append(_pack_skipped_cascade(s, backend="browser"))
                    continue
                res = runner.run_step(s)
                packed = _pack(s, res, backend="browser")
                results.append(packed)
                if res.ok:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= CASCADE_ABORT_AFTER:
                        cascade_aborted = True
                        log.warning(
                            "%s: cascade abort after %s consecutive failures",
                            slug,
                            CASCADE_ABORT_AFTER,
                        )
    else:
        for s in steps:
            results.append(_pack_skipped(s, backend="desktop"))

    attempt = _test_attempt(slug) + 1
    stats = _outcome_stats(results)
    notes_path = write_test_notes(
        slug,
        results,
        first_failure=stats["first_failure"],
        attempt=attempt,
    )
    log.info("wrote %s", notes_path)

    if not stats["failed"]:
        now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        transition(slug, "REVISING", extra={
            "VERIFIED_AS_OF": now,
            "NEXT_ACTION": "writer reconciles draft-1.md against test-notes.md",
            "TEST_ATTEMPT": str(attempt),
            "VERIFY_GAPS": "",
        })
        return 0

    catastrophic = _is_catastrophic(stats)
    current_attempt = _test_attempt(slug)

    if catastrophic or current_attempt >= MAX_TEST_ATTEMPTS - 1:
        if catastrophic:
            block(slug, _block_reason(stats))
        else:
            # Attempt 2 with partial failures — proceed to revise with gaps flagged.
            now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            transition(slug, "REVISING", extra={
                "VERIFIED_AS_OF": now,
                "NEXT_ACTION": "writer reconciles draft-1.md against test-notes.md",
                "TEST_ATTEMPT": str(attempt),
                "VERIFY_GAPS": str(stats["fail_count"]),
            })
            return 0

    # Attempt 1 (or 0): schedule cheap repair instead of blocking.
    _archive_test_notes(slug, attempt)
    write_state(slug, {
        "TEST_ATTEMPT": str(attempt),
        "NEXT_ACTION": "repair-test-plan",
    })
    log.info(
        "%s: %s failures — scheduling repair-test-plan (attempt %s)",
        slug,
        stats["fail_count"],
        attempt,
    )
    return 0


def _pack(step: dict[str, Any], res: StepResult, *, backend: str) -> dict[str, Any]:
    return {
        "step_id": res.step_id,
        "ok": res.ok,
        "backend": backend,
        "observation": res.observation,
        "screenshot": res.screenshot,
        "error": res.error,
        "description": step.get("description", ""),
        "skipped_cascade": False,
    }


def _pack_skipped_cascade(step: dict[str, Any], *, backend: str) -> dict[str, Any]:
    return {
        "step_id": str(step.get("id", "??")),
        "ok": False,
        "backend": backend,
        "observation": "skipped — cascade abort after consecutive failures",
        "screenshot": None,
        "error": None,
        "description": step.get("description", ""),
        "skipped_cascade": True,
    }


def _pack_skipped(step: dict[str, Any], *, backend: str) -> dict[str, Any]:
    return {
        "step_id": str(step.get("id", "??")),
        "ok": False,
        "backend": backend,
        "observation": "skipped — desktop backend not implemented",
        "screenshot": None,
        "error": None,
        "description": step.get("description", ""),
        "skipped_cascade": False,
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
