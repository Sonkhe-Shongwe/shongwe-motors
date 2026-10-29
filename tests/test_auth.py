"""Tests for the safe first-run credential store, independent of PyQt5."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import auth


def test_first_run_and_authentication(tmp_path: Path):
    file = tmp_path / "config" / "admin.json"
    assert not auth.has_admin(file)
    auth.create_admin("administrator", "correct-horse-stable-password", file)
    assert auth.has_admin(file)
    assert auth.verify_admin("administrator", "correct-horse-stable-password", file)
    assert auth.verify_admin("ADMINISTRATOR", "correct-horse-stable-password", file)
    assert not auth.verify_admin("administrator", "incorrect-password", file)
    assert not auth.verify_admin("someone-else", "correct-horse-stable-password", file)
    content = file.read_text(encoding="utf-8")
    assert "correct-horse-stable-password" not in content
    record = json.loads(content)
    assert record["algorithm"] == "pbkdf2_sha256" and record["iterations"] >= 600_000


def test_credentials_not_overwritten(tmp_path: Path):
    file = tmp_path / "admin.json"
    auth.create_admin("firstuser", "correct-horse-stable-password", file)
    with pytest.raises(auth.AuthStoreError):
        auth.create_admin("seconduser", "totally-different-password", file)
    assert auth.verify_admin("firstuser", "correct-horse-stable-password", file)


@pytest.mark.parametrize("name,password", [
    ("ab", "correct-horse-stable-password"),
    ("bad name", "correct-horse-stable-password"),
    ("administrator", "too-short"),
])
def test_rejects_invalid_setup(tmp_path: Path, name: str, password: str):
    with pytest.raises(ValueError):
        auth.create_admin(name, password, tmp_path / "admin.json")
    assert not (tmp_path / "admin.json").exists()


def test_corrupt_records_fail_closed(tmp_path: Path):
    file = tmp_path / "admin.json"
    file.write_text('{"format_version":2}', encoding="utf-8")
    with pytest.raises(auth.AuthStoreError):
        auth.verify_admin("admin", "anything", file)


def test_password_not_embedded_in_gui_code():
    source = (Path(__file__).resolve().parents[1] / "main.py").read_text(encoding="utf-8")
    assert "VALID_PASSWORD" not in source
    assert "VALID_USERNAME" not in source
    assert "auth.verify_admin(" in source
    assert "auth.create_admin(" in source
