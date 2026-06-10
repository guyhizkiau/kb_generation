"""STATE file read/write helpers."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from store.paths import repo_root, state_path


def read_state_fields(path: Path) -> dict[str, str]:
    """Parse ALL KEY=VALUE lines from a STATE file on disk."""
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    result: dict[str, str] = {}
    for line in lines:
        if "=" in line and not line.startswith(" ") and not line.startswith("#"):
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip()
    return result


def write_state_fields(path: Path, updates: dict[str, str]) -> None:
    """Read-modify-write STATE preserving key order; atomic; refreshes LAST_UPDATE."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    updates = dict(updates)
    updates["LAST_UPDATE"] = now

    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    else:
        lines = []
        path.parent.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        if "=" in line and not line.startswith(" ") and not line.startswith("#"):
            k = line.partition("=")[0].strip()
            if k in updates:
                out.append(f"{k}={updates[k]}\n")
                seen.add(k)
            else:
                out.append(line if line.endswith("\n") else line + "\n")
        else:
            out.append(line if line.endswith("\n") else line + "\n")

    for k, v in updates.items():
        if k not in seen:
            out.append(f"{k}={v}\n")

    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text("".join(out), encoding="utf-8")
    os.replace(tmp_path, path)


def read_state(slug: str) -> dict[str, str]:
    """Read all STATE fields for *slug* from the filesystem."""
    return read_state_fields(state_path(slug))


def write_state(slug: str, updates: dict[str, str]) -> dict[str, str]:
    """Apply *updates* to STATE for *slug*; return the resulting fields."""
    path = state_path(slug)
    write_state_fields(path, updates)
    return read_state_fields(path)
