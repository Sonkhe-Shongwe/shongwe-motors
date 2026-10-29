"""Single-user local administrator credentials for the Shongwe Motors desktop UI.

This login protects accidental access via the GUI, not against an attacker who
can modify this user's executable code or SQLite files. The OS user account and
filesystem permissions remain the primary local security boundary.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
from pathlib import Path

ITERATIONS = 600_000
SALT_BYTES = 16


class AuthStoreError(RuntimeError):
    """Credentials are missing, damaged or have an unsupported format."""


def account_path() -> Path:
    """Return an account-file location outside the checked-in source tree."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
        return base / "ShongweMotors" / "admin.json"
    base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "shongwe-motors" / "admin.json"


def has_admin(path: Path | None = None) -> bool:
    return (path or account_path()).exists()


def _validate_username(username: str) -> str:
    username = username.strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,64}", username):
        raise ValueError("Use a 3-64 character username with letters, digits, dots, underscores or hyphens.")
    return username


def create_admin(username: str, password: str, path: Path | None = None) -> Path:
    """Create a one-time admin account, refusing to overwrite an existing one."""
    username = _validate_username(username)
    if len(password) < 12 or len(password) > 1024:
        raise ValueError("Choose a password between 12 and 1024 characters.")
    target = path or account_path()
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    record = {
        "format_version": 1,
        "username": username,
        "algorithm": "pbkdf2_sha256",
        "iterations": ITERATIONS,
        "salt_hex": salt.hex(),
        "digest_hex": digest.hex(),
    }
    # Exclusive creation prevents silently resetting accounts on restart.
    try:
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise AuthStoreError("An administrator account already exists.") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    return target


def verify_admin(username: str, password: str, path: Path | None = None) -> bool:
    target = path or account_path()
    try:
        record = json.loads(target.read_text(encoding="utf-8"))
        if record["format_version"] != 1 or record["algorithm"] != "pbkdf2_sha256":
            raise ValueError("Unsupported credential format")
        iterations = int(record["iterations"])
        if iterations != ITERATIONS:
            raise ValueError("Unexpected credential work factor")
        salt = bytes.fromhex(record["salt_hex"])
        digest = bytes.fromhex(record["digest_hex"])
        if len(salt) != SALT_BYTES or len(digest) != 32:
            raise ValueError("Corrupt credential data")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise AuthStoreError("The local administrator record is missing or invalid.") from exc
    computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(username.strip().casefold(), str(record["username"]).casefold()) and hmac.compare_digest(computed, digest)
