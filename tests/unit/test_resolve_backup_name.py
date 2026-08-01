#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST RESOLVE BACKUP NAME - Shared containment helper
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for ``resolve_backup_name``.

This helper is the single gate between a user-supplied backup name and a
real filesystem path, for both the ``path`` and ``context`` verticals. Its
containment clauses are the point of this file.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys

# Third-party imports
import pytest

# Local imports
from womm.utils.security import resolve_backup_name

# ///////////////////////////////////////////////////////////////
# NOMINAL RESOLUTION
# ///////////////////////////////////////////////////////////////


def test_resolves_a_regular_file_inside_the_directory(tmp_path):
    backup = tmp_path / "backup_1.json"
    backup.write_text("{}", encoding="utf-8")

    resolved = resolve_backup_name(tmp_path, "backup_1.json")

    assert resolved == backup.resolve()


def test_returns_none_for_a_missing_file(tmp_path):
    assert resolve_backup_name(tmp_path, "absent.json") is None


def test_returns_none_for_a_directory(tmp_path):
    (tmp_path / "adir").mkdir()

    assert resolve_backup_name(tmp_path, "adir") is None


# ///////////////////////////////////////////////////////////////
# CONTAINMENT
# ///////////////////////////////////////////////////////////////


@pytest.mark.parametrize(
    "hostile_name",
    [
        "",
        "..",
        "../evil.json",
        "..\\evil.json",
        "sub/evil.json",
        "sub\\evil.json",
        "/etc/passwd",
        "C:\\Windows\\System32\\evil.json",
        "real.json:ads",
    ],
)
def test_rejects_names_escaping_the_directory(tmp_path, hostile_name):
    (tmp_path / "real.json").write_text("{}", encoding="utf-8")

    assert resolve_backup_name(tmp_path, hostile_name) is None


@pytest.mark.skipif(sys.platform == "win32", reason="symlink creation needs privileges")
def test_rejects_a_symlink_pointing_outside(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = outside / "secret.json"
    secret.write_text("{}", encoding="utf-8")

    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    (backup_dir / "link.json").symlink_to(secret)

    assert resolve_backup_name(backup_dir, "link.json") is None
