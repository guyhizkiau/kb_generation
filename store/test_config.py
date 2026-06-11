"""Test resources config — users, credentials, and fixture file names.

Stored at ~/.config/specterx-kb/test-config.json (mode 600). Override path
with TEST_CONFIG_PATH. Passwords never leave this module unmasked except when
resolved at test-run time.
"""

from __future__ import annotations

import copy
import json
import os
import re
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "specterx-kb"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "test-config.json"

_ENV_FALLBACKS: dict[str, tuple[str, ...]] = {
    "users.data_owner.email": ("SPECTERX_USERNAME",),
    "users.data_owner.password": ("SPECTERX_PASSWORD",),
    "users.recipient.email": ("TEST_RECIPIENT_EMAIL",),
    "users.recipient.password": ("TEST_RECIPIENT_GMAIL_PASSWORD", "SPECTERX_PASSWORD"),
    "users.recipient_gmail.email": ("TEST_RECIPIENT_EMAIL",),
    "users.recipient_gmail.password": ("TEST_RECIPIENT_GMAIL_PASSWORD",),
}

_PLACEHOLDER_RE = re.compile(r"\{\{([^}]+)\}\}")

DEFAULT_USERS: dict[str, dict[str, str]] = {
    "data_owner": {"email": "", "password": ""},
    "recipient": {"email": "", "password": ""},
    "recipient_gmail": {"email": "", "password": ""},
}

DEFAULT_FILES: dict[str, Any] = {
    "default": "test-document.pdf",
    "list": [
        "test-document.pdf",
        "test-document-2.pdf",
        "test-document-3.pdf",
    ],
    "folder": "sample-folder",
    "folder_files": ["doc-a.pdf", "doc-b.pdf", "notes.txt"],
}


def config_path() -> Path:
    raw = os.environ.get("TEST_CONFIG_PATH", "").strip()
    return Path(raw) if raw else DEFAULT_CONFIG_PATH


def default_config() -> dict[str, Any]:
    return {
        "users": copy.deepcopy(DEFAULT_USERS),
        "files": copy.deepcopy(DEFAULT_FILES),
    }


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def load(*, create: bool = False) -> dict[str, Any]:
    """Load config from disk, merged with defaults. Optionally create the file."""
    path = config_path()
    data: dict[str, Any] = default_config()
    if path.is_file():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                data = _deep_merge(data, raw)
        except (OSError, json.JSONDecodeError):
            pass
    elif create:
        save(data)
    return data


def save(config: dict[str, Any]) -> None:
    """Persist config with mode 600."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def _walk(config: dict[str, Any], ref: str) -> Any:
    node: Any = config
    for part in ref.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def resolve(ref: str, config: dict[str, Any] | None = None) -> str | None:
    """Resolve a dotted ref like ``users.data_owner.email``."""
    ref = ref.strip()
    if not ref:
        return None
    cfg = config if config is not None else load()
    value = _walk(cfg, ref)
    if isinstance(value, str) and value.strip():
        return value.strip()
    for env_name in _ENV_FALLBACKS.get(ref, ()):
        env_val = os.environ.get(env_name, "").strip()
        if env_val:
            return env_val
    return None


def substitute(text: str, config: dict[str, Any] | None = None) -> str:
    """Replace ``{{dotted.ref}}`` placeholders with resolved values."""
    if not text or "{{" not in text:
        return text
    cfg = config if config is not None else load()

    def repl(match: re.Match[str]) -> str:
        ref = match.group(1).strip()
        resolved = resolve(ref, cfg)
        return resolved if resolved is not None else match.group(0)

    return _PLACEHOLDER_RE.sub(repl, text)


def resolve_action_value(action: dict[str, Any], config: dict[str, Any] | None = None) -> str | None:
    """Resolve fill/type value from value_ref, value_env, or inline value."""
    cfg = config if config is not None else load()
    if action.get("value_ref"):
        return resolve(str(action["value_ref"]), cfg)
    if action.get("value_env"):
        env_name = str(action["value_env"])
        env_val = os.environ.get(env_name, "").strip()
        if env_val:
            return env_val
    raw = action.get("value")
    if raw is None:
        return None
    if isinstance(raw, str):
        return substitute(raw, cfg)
    return str(raw)


def mask_for_api(config: dict[str, Any]) -> dict[str, Any]:
    """Return a copy safe for HTTP GET — passwords replaced with has_password flags."""
    out = copy.deepcopy(config)
    users = out.get("users")
    if isinstance(users, dict):
        for role, fields in users.items():
            if not isinstance(fields, dict):
                continue
            pwd = fields.get("password", "")
            fields["password"] = ""
            fields["has_password"] = bool(isinstance(pwd, str) and pwd.strip())
    return out


def merge_update(payload: dict[str, Any], existing: dict[str, Any] | None = None) -> dict[str, Any]:
    """Merge a PUT payload into existing config; empty password means keep existing."""
    base = existing if existing is not None else load()
    merged = _deep_merge(base, payload)

    incoming_users = payload.get("users")
    if isinstance(incoming_users, dict):
        for role, fields in incoming_users.items():
            if not isinstance(fields, dict):
                continue
            new_pwd = fields.get("password", "")
            if not isinstance(new_pwd, str) or not new_pwd.strip():
                prev = base.get("users", {}).get(role, {})
                if isinstance(prev, dict) and prev.get("password"):
                    merged.setdefault("users", {}).setdefault(role, {})["password"] = prev["password"]

    return merged


def configured_file_names(config: dict[str, Any] | None = None) -> list[str]:
    """All fixture file names referenced by the files section."""
    cfg = config if config is not None else load()
    files = cfg.get("files") or {}
    names: list[str] = []
    default = files.get("default")
    if isinstance(default, str) and default.strip():
        names.append(default.strip())
    lst = files.get("list")
    if isinstance(lst, list):
        names.extend(str(x).strip() for x in lst if str(x).strip())
    folder_files = files.get("folder_files")
    if isinstance(folder_files, list):
        names.extend(str(x).strip() for x in folder_files if str(x).strip())
    seen: set[str] = set()
    out: list[str] = []
    for name in names:
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def configured_folder_name(config: dict[str, Any] | None = None) -> str | None:
    cfg = config if config is not None else load()
    folder = (cfg.get("files") or {}).get("folder")
    if isinstance(folder, str) and folder.strip():
        return folder.strip()
    return None


def _substitute_list(items: list[Any], config: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for item in items:
        if isinstance(item, str):
            out.append(substitute(item, config))
        else:
            out.append(str(item))
    return out


def prepare_step(step: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Deep-copy a plan step with ``{{...}}`` placeholders resolved."""
    cfg = config if config is not None else load()
    out = copy.deepcopy(step)

    if isinstance(out.get("description"), str):
        out["description"] = substitute(out["description"], cfg)
    if isinstance(out.get("verify"), str):
        out["verify"] = substitute(out["verify"], cfg)

    action = out.get("action")
    if isinstance(action, dict):
        if isinstance(action.get("value"), str):
            action["value"] = substitute(action["value"], cfg)
        if isinstance(action.get("filename"), str):
            action["filename"] = substitute(action["filename"], cfg)
        if isinstance(action.get("folder"), str):
            action["folder"] = substitute(action["folder"], cfg)
        if isinstance(action.get("save_as"), str):
            action["save_as"] = substitute(action["save_as"], cfg)
        if isinstance(action.get("filenames"), list):
            action["filenames"] = _substitute_list(action["filenames"], cfg)

    screenshot = out.get("screenshot")
    if isinstance(screenshot, dict):
        if isinstance(screenshot.get("filename"), str):
            screenshot["filename"] = substitute(screenshot["filename"], cfg)
        if isinstance(screenshot.get("focus"), str):
            screenshot["focus"] = substitute(screenshot["focus"], cfg)

    return out


def sensitive_emails(config: dict[str, Any] | None = None) -> list[str]:
    """Collect configured user emails for PII redaction checks."""
    cfg = config if config is not None else load()
    emails: list[str] = []
    users = cfg.get("users")
    if isinstance(users, dict):
        for fields in users.values():
            if isinstance(fields, dict):
                email = fields.get("email", "")
                if isinstance(email, str) and email.strip():
                    emails.append(email.strip())
    for ref in _ENV_FALLBACKS:
        if ref.endswith(".email"):
            val = resolve(ref, cfg)
            if val and val not in emails:
                emails.append(val)
    return emails
