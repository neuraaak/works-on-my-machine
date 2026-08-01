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
from unittest.mock import MagicMock

# Third-party imports
import pytest
from click.testing import CliRunner

# Local imports
from womm.commands.system.context import context_group

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


@pytest.mark.parametrize("hostile_name", ["../evil.json", "..\\evil.json", "/etc/x"])
def test_restore_never_reaches_the_registry_with_an_unsafe_name(
    monkeypatch, hostile_name
):
    """The point of the containment: a rejected name must not restore.

    A failed ``show`` only costs a message; a failed ``restore`` writes to
    the Windows registry. This asserts the write is never attempted.
    """
    from womm.commands.system.context import backup as backup_module

    manager = MagicMock()
    manager.is_windows.return_value = True
    manager.resolve_backup_path.return_value = None
    monkeypatch.setattr(
        backup_module, "ContextMenuInterface", MagicMock(return_value=manager)
    )

    result = CliRunner().invoke(context_group, ["backup", "restore", hostile_name])

    assert result.exit_code == 1
    manager.restore_entries.assert_not_called()


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
