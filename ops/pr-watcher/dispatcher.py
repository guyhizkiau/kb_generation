"""Status-driven phase dispatcher for the single-branch pipeline."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from store import feedback as fb  # noqa: E402
from store.machine import (  # noqa: E402
    LEGACY_MAP,
    current_phase,
    resume,
    transition,
)
from store.paths import article_dir
from store.queue import load_queue
from store.state import read_state, write_state


def map_phase(phase: str) -> str:
    return LEGACY_MAP.get(phase, phase)


def first_queued_slug() -> tuple[str, str] | None:
    """Return (slug, cluster_id) of the next QUEUED or unstarted article.

    Articles added to the queue have no STATE file until the pipeline
    touches them — treat a missing STATE as QUEUED, else the daemon
    idles forever once explicit QUEUED articles run out.
    """
    q = load_queue()
    for cluster in q.get("clusters", []):
        for art in cluster.get("articles", []):
            slug = art["slug"]
            if not (article_dir(slug) / "STATE").exists():
                return slug, cluster.get("id", "")
            if map_phase(current_phase(slug)) == "QUEUED":
                return slug, cluster.get("id", "")
    return None


def dispatch(
    slug: str,
    *,
    launch_phase,
    run_tester,
    retry_publish,
    is_claude_running,
    state: dict,
    save_state,
    log,
) -> None:
    """Dispatch the next action for the active article based on STATE."""
    phase = map_phase(current_phase(slug))
    adir = article_dir(slug)

    handlers = {
        "QUEUED": lambda: _launch(slug, "research", launch_phase, state, save_state, log, pre_transition=("RESEARCHING",)),
        "RESEARCHING": lambda: _relaunch_if_idle(slug, "research", launch_phase, is_claude_running, log),
        "DRAFTING": lambda: _launch(slug, "draft", launch_phase, state, save_state, log),
        "TESTING": lambda: _dispatch_testing(slug, adir, launch_phase, run_tester, is_claude_running, state, save_state, log),
        "REVISING": lambda: _dispatch_revising(slug, launch_phase, state, save_state, log),
        "FINALIZING": lambda: _launch(slug, "voice-pass", launch_phase, state, save_state, log),
        "APPROVED": lambda: retry_publish(slug),
    }

    handler = handlers.get(phase)
    if handler:
        handler()


def dispatch_idle(
    *,
    launch_phase,
    queue_reverification,
    is_claude_running,
    state: dict,
    save_state,
    log,
) -> None:
    """Pick up queued or stale work when no article is in flight."""
    if is_claude_running():
        return
    if queue_reverification():
        return
    picked = first_queued_slug()
    if picked:
        slug, cluster_id = picked
        if not (article_dir(slug) / "STATE").exists():
            write_state(slug, {"PHASE": "QUEUED", "CLUSTER": cluster_id, "NEXT_ACTION": ""})
        transition(slug, "RESEARCHING")
        _launch(slug, "research", launch_phase, state, save_state, log)


def _dedupe_key(slug: str, action: str) -> str:
    # LAST_UPDATE changes on every STATE write, so the key is fresh each
    # time the article (re-)enters a phase. Without it, a second feedback
    # cycle, a re-verification, or an unblock-retry of the same slug+phase
    # would be dedupe-blocked forever.
    stamp = read_state(slug).get("LAST_UPDATE", "")
    return f"phase-dispatch-{slug}-{action}-{stamp}"


def _launch(slug, phase, launch_phase, state, save_state, log, pre_transition=None):
    key = _dedupe_key(slug, phase)
    if key in state.get("handled", []):
        return
    if pre_transition:
        transition(slug, pre_transition[0])
    launch_phase(slug, phase)
    handled = state.setdefault("handled", [])
    handled.append(key)
    del handled[:-500]  # bound state-file growth
    save_state(state)
    log(f"  [{slug}] Dispatched phase {phase}")


def _relaunch_if_idle(slug, phase, launch_phase, is_claude_running, log):
    if is_claude_running():
        return
    relaunch = resume(slug)
    if relaunch:
        launch_phase(slug, phase)
        log(f"  [{slug}] Resuming phase {phase}")


def _dispatch_testing(slug, adir, launch_phase, run_tester, is_claude_running, state, save_state, log):
    if not (adir / "test-plan.json").is_file():
        _launch(slug, "test-plan", launch_phase, state, save_state, log)
    elif not (adir / "test-notes.md").is_file():
        if not is_claude_running():
            key = _dedupe_key(slug, "tester")
            if key not in state.get("handled", []):
                run_tester(slug)
                state.setdefault("handled", []).append(key)
                save_state(state)


def _dispatch_revising(slug, launch_phase, state, save_state, log):
    fields = read_state(slug)
    try:
        rc = int(fields.get("REVISION_CYCLE", "0"))
    except ValueError:
        rc = 0
    anns = fb.read_feedback(slug)
    phase = "revise-from-feedback" if rc > 0 or anns else "revise-from-test"
    _launch(slug, phase, launch_phase, state, save_state, log)
