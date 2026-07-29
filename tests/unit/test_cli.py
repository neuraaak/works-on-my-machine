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
        "doctor",
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
    assert "install" not in womm.commands
    assert "uninstall" not in womm.commands


def test_doctor_reports_runtime_without_creating_data_directory(
    tmp_path, monkeypatch
) -> None:
    data_dir = tmp_path / "womm-home"
    monkeypatch.setenv("WOMM_HOME", str(data_dir))
    monkeypatch.setattr(
        "womm.commands.core.doctor._context_menu_status", lambda: "0 entries"
    )

    result = CliRunner().invoke(womm, ["doctor"])

    assert result.exit_code == 0
    assert "Runtime channel:" in result.output
    assert f"Data directory: {data_dir}" in result.output
    assert "Context menu: 0 entries" in result.output
    assert not data_dir.exists()
