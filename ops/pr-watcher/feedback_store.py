"""Thin shim — implementation lives in store/."""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from store.feedback import (  # noqa: F401
    append_feedback,
    delete_feedback,
    feedback_dir,
    feedback_path,
    merge_feedback,
    read_feedback,
    remove_feedback,
    write_feedback,
)
