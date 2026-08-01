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
from womm import cli
from womm.cli import womm


def test_windows_console_configuration_uses_utf8(monkeypatch) -> None:
    configured_encodings: list[str] = []

    class Stream:
        def reconfigure(self, *, encoding: str) -> None:
            configured_encodings.append(encoding)

    monkeypatch.setattr(cli.sys, "platform", "win32")
    monkeypatch.setattr(cli.sys, "stdout", Stream())
    monkeypatch.setattr(cli.sys, "stderr", Stream())
    monkeypatch.setenv("PYTHONIOENCODING", "cp1252")

    cli._configure_windows_console()

    assert configured_encodings == ["utf-8", "utf-8"]
    assert cli.os.environ["PYTHONIOENCODING"] == "utf-8"


def test_help_registers_all_operational_command_groups() -> None:
    result = CliRunner().invoke(womm, ["--help"])

    assert result.exit_code == 0
    for command in (
        "doctor",
        "path",
        "create",
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
        "womm.interfaces.core.doctor_interface.DoctorInterface._context_menu_status",
        staticmethod(lambda: "0 entries"),
    )

    result = CliRunner().invoke(womm, ["doctor"])

    assert result.exit_code == 0
    assert not data_dir.exists()


def test_doctor_diagnose_reports_the_data_directory(tmp_path, monkeypatch) -> None:
    from womm.interfaces.core import DoctorInterface

    data_dir = tmp_path / "womm-home"
    monkeypatch.setenv("WOMM_HOME", str(data_dir))
    monkeypatch.setattr(
        "womm.interfaces.core.doctor_interface.DoctorInterface._context_menu_status",
        staticmethod(lambda: "0 entries"),
    )

    result = DoctorInterface().diagnose()

    assert result.success
    assert result.data_dir == str(data_dir)
    assert result.context_menu_status == "0 entries"
    assert not data_dir.exists()
