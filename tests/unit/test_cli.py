#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST CLI - Command Registration
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Regression tests for the unconditional CLI command surface."""

from __future__ import annotations

# Third-party imports
from click.testing import CliRunner

# Local imports
from womm.cli import womm


def test_help_registers_all_operational_command_groups() -> None:
    result = CliRunner().invoke(womm, ["--help"])

    assert result.exit_code == 0
    for command in (
        "path",
        "create",
        "lint",
        "system",
        "context",
        "setup",
        "template",
        "deps",
    ):
        assert command in result.output


def test_help_does_not_expose_removed_self_installation_commands() -> None:
    result = CliRunner().invoke(womm, ["--help"])

    assert result.exit_code == 0
    assert "install" not in result.output
    assert "uninstall" not in result.output
