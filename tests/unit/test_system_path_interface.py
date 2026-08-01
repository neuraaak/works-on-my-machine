#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SYSTEM PATH INTERFACE - Backup reading and containment
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for ``SystemPathInterface`` backup reading.

The containment tests are the point of this file: ``read_backup`` takes a
user-supplied name, so it must never reach outside the backup directory.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
from unittest.mock import MagicMock

# Third-party imports
import pytest

# Local imports
from womm.interfaces.system.path_interface import SystemPathInterface
from womm.shared.results import PathOperationResult

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def interface(tmp_path, monkeypatch):
    """A SystemPathInterface whose backup_dir is an empty tmp directory."""
    monkeypatch.setattr(
        "womm.interfaces.system.path_interface.path_backups_dir",
        lambda: tmp_path / "backups",
    )
    instance = SystemPathInterface()
    instance.backup_dir.mkdir(parents=True, exist_ok=True)
    return instance


def _write_backup(interface, name: str, entries: list[str]) -> None:
    """Write a well-formed backup file into the interface's backup dir."""
    payload = {
        "type": "womm_path_backup",
        "version": 1,
        "timestamp": "20260801_120000",
        "platform": "Windows",
        "separator": ";",
        "path_string": ";".join(entries),
        "entries": entries,
        "length": len(";".join(entries)),
    }
    (interface.backup_dir / name).write_text(json.dumps(payload), encoding="utf-8")


# ///////////////////////////////////////////////////////////////
# READ BACKUP - NOMINAL
# ///////////////////////////////////////////////////////////////


def test_read_backup_returns_the_backup_content(interface):
    _write_backup(interface, ".path_20260801_120000.json", ["C:/a", "C:/b"])

    result = interface.read_backup(".path_20260801_120000.json")

    assert result.success is True
    assert result.name == ".path_20260801_120000.json"
    assert result.entries == ["C:/a", "C:/b"]
    assert result.timestamp == "20260801_120000"
    assert result.platform == "Windows"
    assert result.separator == ";"
    assert result.length == len("C:/a;C:/b")


def test_read_backup_reports_a_missing_file(interface):
    result = interface.read_backup(".path_nope.json")

    assert result.success is False
    assert ".path_nope.json" in result.message


def test_read_backup_reports_corrupted_json(interface):
    (interface.backup_dir / ".path_bad.json").write_text("{not json", encoding="utf-8")

    result = interface.read_backup(".path_bad.json")

    assert result.success is False
    assert result.error


# ///////////////////////////////////////////////////////////////
# READ BACKUP - CONTAINMENT
# ///////////////////////////////////////////////////////////////


@pytest.mark.parametrize(
    "hostile_name",
    [
        "../evil.json",
        "../../evil.json",
        "..\\evil.json",
        "sub/evil.json",
        "sub\\evil.json",
        "..",
        "",
        "C:/Windows/System32/evil.json",
        "/etc/passwd",
    ],
)
def test_read_backup_rejects_names_escaping_the_backup_dir(
    interface, tmp_path, hostile_name
):
    """No name containing a separator, a parent ref, or a root may resolve."""
    outside = tmp_path / "evil.json"
    outside.write_text(
        json.dumps({"entries": ["pwned"], "timestamp": "x"}), encoding="utf-8"
    )

    result = interface.read_backup(hostile_name)

    assert result.success is False
    assert result.entries in (None, [])
    # The rejection message must not leak a resolved filesystem path.
    assert str(tmp_path) not in (result.message or "")
    assert str(tmp_path) not in (result.error or "")


def test_read_backup_rejects_a_directory(interface):
    (interface.backup_dir / "adir").mkdir()

    result = interface.read_backup("adir")

    assert result.success is False


def test_read_backup_rejects_a_symlink_escaping_the_backup_dir(interface, tmp_path):
    """Syntax filtering cannot see symlinks; the resolved-path check must."""
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps({"entries": ["pwned"]}), encoding="utf-8")
    link = interface.backup_dir / "link.json"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted on this platform")

    result = interface.read_backup("link.json")

    assert result.success is False


# ///////////////////////////////////////////////////////////////
# LIST PATH ENTRIES
# ///////////////////////////////////////////////////////////////


def test_list_path_entries_passes_the_service_result_through(interface):
    service = MagicMock()
    service.get_current_system_path.return_value = PathOperationResult(
        success=True, message="ok", path_entries=["C:/a", "C:/b"]
    )
    interface._path_service = service

    result = interface.list_path_entries()

    assert result.success is True
    assert result.path_entries == ["C:/a", "C:/b"]


def test_list_path_entries_converts_a_service_exception(interface):
    from womm.exceptions.system import SystemServiceError

    service = MagicMock()
    service.get_current_system_path.side_effect = SystemServiceError("list", "boom")
    interface._path_service = service

    result = interface.list_path_entries()

    assert result.success is False
    assert "boom" in (result.error or "")
