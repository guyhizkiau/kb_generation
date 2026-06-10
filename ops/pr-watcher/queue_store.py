"""Thin shim — implementation lives in store/."""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from store.queue import (  # noqa: F401
    SLUG_RE,
    TERMINAL_PHASES,
    VALID_MODES,
    VALID_STATUSES,
    article_is_merged,
    article_state_fields,
    article_state_path,
    delete_article_dir,
    load_queue,
    next_article,
    queue_with_states,
    read_state,
    remove_article_from_queue,
    save_queue,
    strip_queue_for_save,
    validate_slugs,
)
from store.state import read_state_fields, write_state_fields  # noqa: F401
