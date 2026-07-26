#!/usr/bin/env python3
"""Boundary tests for the common service exception contract."""

from __future__ import annotations

from pathlib import Path

import pytest

from womm.exceptions.common import CommandExecutionError, CommandUtilityError
from womm.services.common.base_validation_service import BaseValidationService
from womm.services.common.command_runner_service import CommandRunnerService
from womm.services.common.file_scanner_service import FileScannerService
from womm.services.common.security_validator_service import SecurityValidatorService
from womm.shared.results import CommandAvailabilityResult


def test_execute_command_wraps_os_error_as_command_utility_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = CommandRunnerService()

    def raise_os_error(*_args, **_kwargs):
        raise OSError("executable unavailable")

    monkeypatch.setattr(
        "womm.services.common.command_runner_service.subprocess.run", raise_os_error
    )

    with pytest.raises(CommandUtilityError) as excinfo:
        service._execute_command(["missing-tool"], Path.cwd())

    assert "executable unavailable" in excinfo.value.message
    assert isinstance(excinfo.value.__cause__, OSError)


def test_run_normalizes_os_error_as_command_execution_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = CommandRunnerService()
    original_retries = service.max_retries
    service.max_retries = 0

    def raise_os_error(*_args, **_kwargs):
        raise OSError("process launch failed")

    monkeypatch.setattr(service, "_execute_command", raise_os_error)
    try:
        with pytest.raises(CommandExecutionError) as excinfo:
            service.run(["missing-tool"])
    finally:
        service.max_retries = original_retries

    assert excinfo.value.return_code == -1
    assert "process launch failed" in excinfo.value.stderr


def test_get_command_version_translates_command_error_to_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = CommandRunnerService()
    monkeypatch.setattr(
        service,
        "check_command_available",
        lambda _command: CommandAvailabilityResult(
            success=True,
            command_name="tool",
            is_available=True,
            security_validated=True,
        ),
    )

    def raise_command_error(*_args, **_kwargs):
        raise CommandExecutionError(command="tool", return_code=1, stderr="failed")

    monkeypatch.setattr(service, "run_silent", raise_command_error)

    result = service.get_command_version("tool")

    assert not result.success
    assert result.error == "Command execution failed (code 1): tool"


def test_file_scanner_translates_invalid_path_to_failure_result(tmp_path: Path) -> None:
    result = FileScannerService().find_python_files(tmp_path / "missing")

    assert not result.success
    assert "Path does not exist" in result.error


def test_security_validator_rejects_dangerous_command_without_raising() -> None:
    result = SecurityValidatorService().validate_command(["rm", "-rf", "/"])

    assert not result.success
    assert result.is_valid is False


def test_base_validation_converts_invalid_regex_to_failure_result() -> None:
    result = BaseValidationService.validate_string_pattern("value", "[")

    assert not result.success
    assert "Error validating value" in result.error
