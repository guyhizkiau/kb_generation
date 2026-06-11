"""Test resources config — users, credentials, and fixture file names.

Stored at ~/.config/specterx-kb/test-config.json (mode 600). Override path
with TEST_CONFIG_PATH. Passwords never leave this module unmasked except when
resolved at test-run time.

Each user role carries:
  - email — mailbox / SpecterX login address
  - email_password — Gmail/Workspace mailbox password (primary; enables resets)
  - specterx_password — optional SpecterX app password; empty triggers bootstrap
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
    "users.data_owner.email_password": (),
    "users.data_owner.specterx_password": ("SPECTERX_PASSWORD",),
    "users.data_owner.password": ("SPECTERX_PASSWORD",),
    "users.recipient.email": ("TEST_RECIPIENT_EMAIL",),
    "users.recipient.email_password": ("TEST_RECIPIENT_GMAIL_PASSWORD",),
    "users.recipient.specterx_password": ("TEST_RECIPIENT_GMAIL_PASSWORD",),
    "users.recipient.password": ("TEST_RECIPIENT_GMAIL_PASSWORD",),
}

_REF_ALIASES: dict[str, str] = {
    "users.data_owner.password": "users.data_owner.specterx_password",
    "users.recipient.password": "users.recipient.specterx_password",
}

_PASSWORD_REF_RE = re.compile(
    r"^users\.([a-zA-Z0-9_]+)\.(?:password|specterx_password)$"
)

_PLACEHOLDER_RE = re.compile(r"\{\{([^}]+)\}\}")

DEFAULT_USER_FIELDS: dict[str, str] = {
    "email": "",
    "email_password": "",
    "specterx_password": "",
}

DEFAULT_USERS: dict[str, dict[str, str]] = {
    "data_owner": dict(DEFAULT_USER_FIELDS),
    "recipient": dict(DEFAULT_USER_FIELDS),
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


def _normalize_user_fields(fields: dict[str, Any]) -> dict[str, str]:
    """Normalize one role to the canonical three-field shape."""
    out = dict(DEFAULT_USER_FIELDS)
    if not isinstance(fields, dict):
        return out
    email = fields.get("email", "")
    if isinstance(email, str):
        out["email"] = email.strip()
    for key in ("email_password", "specterx_password"):
        val = fields.get(key, "")
        if isinstance(val, str) and val.strip():
            out[key] = val.strip()
    legacy = fields.get("password", "")
    if isinstance(legacy, str) and legacy.strip() and not out["specterx_password"]:
        out["specterx_password"] = legacy.strip()
    return out


def _normalize_config(data: dict[str, Any]) -> None:
    """Migrate legacy shapes in place."""
    users = data.setdefault("users", {})
    if not isinstance(users, dict):
        data["users"] = copy.deepcopy(DEFAULT_USERS)
        return

    if "recipient_gmail" in users:
        rg = users.pop("recipient_gmail")
        if isinstance(rg, dict):
            recipient = users.setdefault("recipient", dict(DEFAULT_USER_FIELDS))
            if isinstance(recipient, dict):
                if not recipient.get("email") and rg.get("email"):
                    recipient["email"] = str(rg.get("email", "")).strip()
                rg_norm = _normalize_user_fields(rg)
                if not recipient.get("email_password") and rg_norm["email_password"]:
                    recipient["email_password"] = rg_norm["email_password"]
                if not recipient.get("specterx_password") and rg_norm["specterx_password"]:
                    recipient["specterx_password"] = rg_norm["specterx_password"]

    normalized: dict[str, dict[str, str]] = {}
    for role, fields in users.items():
        if isinstance(fields, dict):
            normalized[str(role)] = _normalize_user_fields(fields)
    data["users"] = normalized


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
    _normalize_config(data)
    if create and not path.is_file():
        save(data)
    return data


def save(config: dict[str, Any]) -> None:
    """Persist config with mode 600."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    to_save = copy.deepcopy(config)
    _normalize_config(to_save)
    path.write_text(json.dumps(to_save, indent=2) + "\n", encoding="utf-8")
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
    canonical = _REF_ALIASES.get(ref, ref)
    cfg = config if config is not None else load()
    value = _walk(cfg, canonical)
    if isinstance(value, str) and value.strip():
        return value.strip()
    for env_name in _ENV_FALLBACKS.get(canonical, _ENV_FALLBACKS.get(ref, ())):
        env_val = os.environ.get(env_name, "").strip()
        if env_val:
            return env_val
    return None


def specterx_password_set(role: str, config: dict[str, Any] | None = None) -> bool:
    return bool(resolve(f"users.{role}.specterx_password", config))


def email_password_set(role: str, config: dict[str, Any] | None = None) -> bool:
    return bool(resolve(f"users.{role}.email_password", config))


def set_specterx_password(role: str, password: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Persist a SpecterX password for *role* and return the updated config."""
    cfg = copy.deepcopy(config if config is not None else load())
    users = cfg.setdefault("users", {})
    role_fields = users.setdefault(role, dict(DEFAULT_USER_FIELDS))
    if not isinstance(role_fields, dict):
        role_fields = dict(DEFAULT_USER_FIELDS)
        users[role] = role_fields
    role_fields["specterx_password"] = password.strip()
    role_fields.pop("password", None)
    save(cfg)
    return cfg


def roles_referenced_for_specterx_login(plan: dict[str, Any]) -> list[str]:
    """Roles whose SpecterX password is referenced by value_ref in the plan."""
    roles: set[str] = set()
    for step in plan.get("steps") or []:
        action = step.get("action") or {}
        ref = str(action.get("value_ref", "")).strip()
        match = _PASSWORD_REF_RE.match(ref)
        if match:
            roles.add(match.group(1))
    return sorted(roles)


def roles_needing_specterx_bootstrap(plan: dict[str, Any], config: dict[str, Any] | None = None) -> list[str]:
    """Roles referenced in the plan whose SpecterX password is not yet set."""
    cfg = config if config is not None else load()
    return [r for r in roles_referenced_for_specterx_login(plan) if not specterx_password_set(r, cfg)]


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
    """Return a copy safe for HTTP GET — passwords replaced with has_* flags."""
    out = copy.deepcopy(config)
    _normalize_config(out)
    users = out.get("users")
    if isinstance(users, dict):
        for role, fields in users.items():
            if not isinstance(fields, dict):
                continue
            email_pwd = fields.get("email_password", "")
            sx_pwd = fields.get("specterx_password", "")
            fields["email_password"] = ""
            fields["specterx_password"] = ""
            fields.pop("password", None)
            fields["has_email_password"] = bool(isinstance(email_pwd, str) and email_pwd.strip())
            fields["has_specterx_password"] = bool(isinstance(sx_pwd, str) and sx_pwd.strip())
            fields.pop("has_password", None)
    return out


def merge_update(payload: dict[str, Any], existing: dict[str, Any] | None = None) -> dict[str, Any]:
    """Merge a PUT payload; empty password fields mean keep existing."""
    base = existing if existing is not None else load()
    merged = _deep_merge(base, payload)
    _normalize_config(merged)

    incoming_users = payload.get("users")
    if isinstance(incoming_users, dict):
        for role, fields in incoming_users.items():
            if not isinstance(fields, dict):
                continue
            prev = base.get("users", {}).get(role, {})
            if not isinstance(prev, dict):
                prev = {}
            dest = merged.setdefault("users", {}).setdefault(role, dict(DEFAULT_USER_FIELDS))
            for pwd_key in ("email_password", "specterx_password"):
                new_val = fields.get(pwd_key, "")
                if not isinstance(new_val, str) or not new_val.strip():
                    if isinstance(prev.get(pwd_key), str) and prev.get(pwd_key, "").strip():
                        dest[pwd_key] = prev[pwd_key]
            dest.pop("password", None)

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
