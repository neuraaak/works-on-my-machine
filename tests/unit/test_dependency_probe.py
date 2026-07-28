#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST DEPENDENCY PROBE - Executable detection primitive
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for ``probe()``.

``CommandRunnerService`` is a singleton; per this repo's established
pattern (see the ``env_utils``/``installer_utils`` coverage campaign),
patch methods on the singleton *instance*, not the class, to avoid
leaking class-level patches into unrelated tests.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import shutil

# Local imports
from womm.services.common.command_runner_service import CommandRunnerService
from womm.shared.results.command_results import (
    CommandAvailabilityResult,
    CommandVersionResult,
)
from womm.utils.dependencies.probe import probe

# ///////////////////////////////////////////////////////////////
# TESTS
# ///////////////////////////////////////////////////////////////


def test_probe_unavailable_command_returns_unavailable_result(monkeypatch):
    runner = CommandRunnerService()
    monkeypatch.setattr(
        runner,
        "check_command_available",
        lambda _command: CommandAvailabilityResult(success=False, is_available=False),
    )

    result = probe("ghost-tool")

    assert result.available is False
    assert result.name == "ghost-tool"
    assert result.path is None
    assert result.version is None
    assert result.success is False


def test_probe_available_command_detects_version_and_path(monkeypatch, tmp_path):
    fake_exe = tmp_path / "ruff.exe"
    fake_exe.write_text("")

    runner = CommandRunnerService()
    monkeypatch.setattr(
        runner,
        "check_command_available",
        lambda _command: CommandAvailabilityResult(success=True, is_available=True),
    )
    monkeypatch.setattr(
        runner,
        "get_command_version",
        lambda _command, _flag: CommandVersionResult(success=True, version="0.5.0"),
    )
    monkeypatch.setattr(shutil, "which", lambda _cmd: str(fake_exe))

    result = probe("ruff")

    assert result.available is True
    assert result.version == "0.5.0"
    assert result.path == str(fake_exe)
    assert result.success is True


def test_probe_available_command_without_version_detection_skips_lookup(
    monkeypatch,
):
    runner = CommandRunnerService()
    monkeypatch.setattr(
        runner,
        "check_command_available",
        lambda _command: CommandAvailabilityResult(success=True, is_available=True),
    )

    def _fail_if_called(*_args, **_kwargs):
        raise AssertionError("get_command_version should not be called")

    monkeypatch.setattr(runner, "get_command_version", _fail_if_called)
    monkeypatch.setattr(shutil, "which", lambda _cmd: None)

    result = probe("ruff", detect_version=False)

    assert result.available is True
    assert result.version is None


def test_probe_available_command_with_failed_version_lookup_leaves_version_none(
    monkeypatch,
):
    runner = CommandRunnerService()
    monkeypatch.setattr(
        runner,
        "check_command_available",
        lambda _command: CommandAvailabilityResult(success=True, is_available=True),
    )
    monkeypatch.setattr(
        runner,
        "get_command_version",
        lambda _command, _flag: CommandVersionResult(success=False, version=""),
    )
    monkeypatch.setattr(shutil, "which", lambda _cmd: None)

    result = probe("ruff")

    assert result.version is None
