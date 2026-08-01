#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST CONTEXT COMMAND - CLI surface
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for the ``womm context`` CLI surface.

These assert the shape of the command tree and the containment of the
backup name arguments. Registry-touching behaviour is covered by the
interface tests.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from unittest.mock import MagicMock

# Third-party imports
import pytest
from click.testing import CliRunner

# Local imports
from womm.commands.system.context import context_group
from womm.shared.results import (
    BackupFileInfo,
    BackupFileListResult,
    ContextRestoreResult,
)

# ///////////////////////////////////////////////////////////////
# COMMAND TREE
# ///////////////////////////////////////////////////////////////


def test_context_without_subcommand_shows_help():
    result = CliRunner().invoke(context_group, [])

    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_backup_without_subcommand_shows_help():
    result = CliRunner().invoke(context_group, ["backup"])

    assert result.exit_code == 0
    assert "Usage:" in result.output


@pytest.mark.parametrize(
    "argv",
    [
        ["list"],
        ["register"],
        ["unregister"],
        ["quick-setup"],
        ["backup", "create"],
        ["backup", "list"],
        ["backup", "show"],
        ["backup", "restore"],
        ["backup", "cherry-pick"],
    ],
)
def test_every_subcommand_is_reachable(argv):
    result = CliRunner().invoke(context_group, [*argv, "--help"])

    assert result.exit_code == 0
    assert "Usage:" in result.output


@pytest.mark.parametrize(
    "argv", [["status"], ["restore"], ["cherry-pick"], ["backup", "--output", "x.json"]]
)
def test_the_old_surface_is_gone(argv):
    result = CliRunner().invoke(context_group, argv)

    assert result.exit_code != 0


# ///////////////////////////////////////////////////////////////
# BACKUP NAME CONTAINMENT
# ///////////////////////////////////////////////////////////////


_SAFE_NAME = "context_menu_backup_20260101_000000.json"
_SAFE_PATH = f"C:/backups/{_SAFE_NAME}"


def _listing_with_one_backup() -> BackupFileListResult:
    """Build a non-empty backup listing.

    A populated listing matters: with an empty one, ``restore`` would exit 1
    on its own and the containment assertions would pass vacuously.

    Returns:
        A successful listing holding a single known backup.
    """
    return BackupFileListResult(
        success=True,
        backup_directory="C:/backups",
        backups=[BackupFileInfo(filename=_SAFE_NAME, filepath=_SAFE_PATH)],
    )


@pytest.mark.parametrize("hostile_name", ["../evil.json", "..\\evil.json", "/etc/x"])
def test_restore_never_reaches_the_registry_with_an_unsafe_name(
    monkeypatch, hostile_name
):
    """The point of the containment: a rejected name must not restore.

    A failed ``show`` only costs a message; a failed ``restore`` writes to
    the Windows registry. This asserts the write is never attempted, and
    that the refusal comes from ``resolve_backup_path`` rather than from an
    accidentally empty listing.
    """
    from womm.commands.system.context import backup as backup_module

    manager = MagicMock()
    manager.is_windows.return_value = True
    manager.list_backups.return_value = _listing_with_one_backup()
    manager.resolve_backup_path.return_value = None
    monkeypatch.setattr(
        backup_module, "ContextMenuInterface", MagicMock(return_value=manager)
    )

    result = CliRunner().invoke(context_group, ["backup", "restore", hostile_name])

    assert result.exit_code == 1
    manager.resolve_backup_path.assert_called_once_with(hostile_name)
    manager.restore_entries.assert_not_called()


def test_restore_reaches_the_registry_with_a_resolved_name(monkeypatch):
    """The positive control: the guard discriminates, it does not block all.

    Paired with the hostile-name test, this proves the containment lets a
    resolved name through to the registry write.
    """
    from womm.commands.system.context import backup as backup_module

    manager = MagicMock()
    manager.is_windows.return_value = True
    manager.list_backups.return_value = _listing_with_one_backup()
    manager.resolve_backup_path.return_value = Path(_SAFE_PATH)
    manager.restore_entries.return_value = ContextRestoreResult(
        success=True, backup_file=_SAFE_PATH, entry_count=1
    )
    monkeypatch.setattr(
        backup_module, "ContextMenuInterface", MagicMock(return_value=manager)
    )
    monkeypatch.setattr(
        backup_module.ContextMenuUI,
        "confirm_restore_operation",
        staticmethod(lambda _backup: True),
    )

    result = CliRunner().invoke(context_group, ["backup", "restore", _SAFE_NAME])

    assert result.exit_code == 0
    manager.resolve_backup_path.assert_called_once_with(_SAFE_NAME)
    manager.restore_entries.assert_called_once_with(_SAFE_PATH)


def test_show_rejects_an_unsafe_name(monkeypatch):
    from womm.commands.system.context import backup as backup_module
    from womm.shared.results import BackupDataResult

    manager = MagicMock()
    manager.is_windows.return_value = True
    manager.read_backup.return_value = BackupDataResult(
        success=False, error="No readable backup named '../evil.json'"
    )
    monkeypatch.setattr(
        backup_module, "ContextMenuInterface", MagicMock(return_value=manager)
    )

    result = CliRunner().invoke(context_group, ["backup", "show", "../evil.json"])

    assert result.exit_code == 1
