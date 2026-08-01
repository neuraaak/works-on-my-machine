#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PATH COMMAND - CLI surface of the path group
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for the ``womm path`` command group.

These assert the CLI surface only: which subcommands exist, that the removed
flags are gone, and that each subcommand reaches its interface method.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from unittest.mock import MagicMock

# Third-party imports
import pytest
from click.testing import CliRunner

# Local imports
from womm.commands.core.path import path_group
from womm.shared.results import (
    PathBackupContentResult,
    PathBackupListResult,
    PathBackupResult,
    PathOperationResult,
)

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def manager(monkeypatch):
    """Patch SystemPathInterface with a mock and hand it back."""
    instance = MagicMock()
    monkeypatch.setattr("womm.commands.core.path.SystemPathInterface", lambda: instance)
    return instance


# ///////////////////////////////////////////////////////////////
# GROUP SURFACE
# ///////////////////////////////////////////////////////////////


def test_path_without_subcommand_shows_help():
    result = CliRunner().invoke(path_group, [])

    assert result.exit_code == 0
    assert "Usage" in result.output


def test_path_group_exposes_the_expected_subcommands():
    assert set(path_group.commands) == {"list", "backup"}
    backup_group = path_group.commands["backup"]
    assert set(backup_group.commands) == {"create", "list", "show", "restore"}


@pytest.mark.parametrize("removed_flag", ["-b", "-r", "-l"])
def test_removed_action_flags_are_rejected(removed_flag):
    result = CliRunner().invoke(path_group, [removed_flag])

    assert result.exit_code != 0


# ///////////////////////////////////////////////////////////////
# SUBCOMMANDS
# ///////////////////////////////////////////////////////////////


def test_path_list_calls_the_interface(manager):
    manager.list_path_entries.return_value = PathOperationResult(
        success=True, message="ok", path_entries=["C:/a"]
    )

    result = CliRunner().invoke(path_group, ["list"])

    assert result.exit_code == 0
    manager.list_path_entries.assert_called_once()


def test_path_list_exits_non_zero_on_failure(manager):
    manager.list_path_entries.return_value = PathOperationResult(
        success=False, error="nope"
    )

    result = CliRunner().invoke(path_group, ["list"])

    assert result.exit_code == 1


def test_backup_create_calls_the_interface(manager):
    manager.create_backup.return_value = PathBackupResult(
        success=True, backup_location="C:/b", backup_file="C:/b/a.json"
    )

    result = CliRunner().invoke(path_group, ["backup", "create"])

    assert result.exit_code == 0
    manager.create_backup.assert_called_once()


def test_backup_list_calls_the_interface(manager):
    manager.list_backups.return_value = PathBackupListResult(success=True, backups=[])

    result = CliRunner().invoke(path_group, ["backup", "list"])

    assert result.exit_code == 0
    manager.list_backups.assert_called_once()


def test_backup_show_passes_the_name_through(manager):
    manager.read_backup.return_value = PathBackupContentResult(
        success=True, name="a.json", entries=["C:/a"]
    )

    result = CliRunner().invoke(path_group, ["backup", "show", "a.json"])

    assert result.exit_code == 0
    manager.read_backup.assert_called_once_with("a.json")


def test_backup_show_requires_a_name():
    result = CliRunner().invoke(path_group, ["backup", "show"])

    assert result.exit_code != 0


def test_backup_show_exits_non_zero_when_the_name_is_rejected(manager):
    manager.read_backup.return_value = PathBackupContentResult(
        success=False, message="No readable backup named '../evil.json'"
    )

    result = CliRunner().invoke(path_group, ["backup", "show", "../evil.json"])

    assert result.exit_code == 1
    manager.read_backup.assert_called_once_with("../evil.json")
