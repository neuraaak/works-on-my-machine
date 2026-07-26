#!/usr/bin/env python3
"""Boundary tests for the common service exception contract."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from womm.exceptions.common import (
    CommandExecutionError,
    CommandTimeoutError,
    CommandUtilityError,
    SecurityServiceError,
)
from womm.services.common.base_validation_service import BaseValidationService
from womm.services.common.command_runner_service import CommandRunnerService
from womm.services.common.file_scanner_service import FileScannerService
from womm.services.common.security_validator_service import SecurityValidatorService
from womm.shared.results import CommandAvailabilityResult, CommandResult


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


@pytest.mark.parametrize(
    ("command", "reason"),
    [
        ([], "Command cannot be empty"),
        ("echo", "Command must be a list"),
        (["echo", 1], "All command arguments must be strings"),
        (["rm", "file"], "not in allowed list"),
        (["echo", "hello; whoami"], "Dangerous argument"),
    ],
)
def test_security_validator_rejects_invalid_command_shapes(
    command: object, reason: str
) -> None:
    result = SecurityValidatorService().validate_command(command)  # type: ignore[arg-type]

    assert not result.success
    assert result.is_valid is False
    assert reason in result.validation_reason


def test_security_validator_accepts_whitelisted_safe_command() -> None:
    result = SecurityValidatorService().validate_command(["echo", "hello"])

    assert result.success
    assert result.is_valid is True
    assert result.command == "echo hello"


@pytest.mark.parametrize(
    ("path", "reason"),
    [
        ("", "cannot be empty"),
        ("../../../../secret", "dangerous patterns"),
        ("/etc/passwd", "dangerous patterns"),
    ],
)
def test_security_validator_rejects_unsafe_paths(path: str, reason: str) -> None:
    result = SecurityValidatorService().validate_file_path(path)

    assert not result.success
    assert result.is_valid is False
    assert reason in result.validation_reason


def test_security_validator_reports_all_checks_for_safe_command() -> None:
    result = SecurityValidatorService().get_security_report(["echo", "hello"])

    assert result.success
    assert result.is_safe is True
    assert result.base_command == "echo"
    assert result.arguments == ["hello"]
    assert len(result.checks_performed) == 3


def test_run_returns_subprocess_output_and_discards_unknown_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = CommandRunnerService()
    received: dict[str, object] = {}

    def complete(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        received["args"] = args
        received["kwargs"] = kwargs
        return subprocess.CompletedProcess(args[0], 0, "done", "")

    monkeypatch.setattr(
        "womm.services.common.command_runner_service.subprocess.run", complete
    )

    result = service.run(["echo", "done"], unsupported_option=True)

    assert result.returncode == 0
    assert result.stdout == "done"
    assert result.command == ["echo", "done"]
    assert received["args"] == (["echo", "done"],)
    assert received["kwargs"] == {
        "check": False,
        "cwd": service.default_cwd,
        "timeout": service.timeout,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "capture_output": True,
        "shell": False,
    }


def test_run_retries_timeout_then_returns_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = CommandRunnerService()
    original_retries, original_delay = service.max_retries, service.retry_delay
    attempts = 0

    def execute(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise subprocess.TimeoutExpired("echo", service.timeout)
        return subprocess.CompletedProcess(["echo"], 0, "done", "")

    monkeypatch.setattr(service, "_execute_command", execute)
    service.max_retries, service.retry_delay = 1, 0
    try:
        result = service.run(["echo", "done"])
    finally:
        service.max_retries, service.retry_delay = original_retries, original_delay

    assert result.stdout == "done"
    assert attempts == 2


def test_run_converts_final_timeout_to_domain_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = CommandRunnerService()
    original_retries = service.max_retries
    service.max_retries = 0
    monkeypatch.setattr(
        service,
        "_execute_command",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            subprocess.TimeoutExpired("echo", service.timeout)
        ),
    )
    try:
        with pytest.raises(CommandTimeoutError) as excinfo:
            service.run(["echo", "done"])
    finally:
        service.max_retries = original_retries

    assert excinfo.value.timeout_seconds == service.timeout


def test_run_secure_stops_before_execution_for_rejected_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = CommandRunnerService()
    monkeypatch.setattr(
        service,
        "_execute_command",
        lambda *_args, **_kwargs: pytest.fail("the command must not be executed"),
    )

    with pytest.raises(SecurityServiceError):
        service.run_secure(["rm", "file"])


def test_check_command_available_marks_existing_unapproved_command_unsecure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("shutil.which", lambda _command: "/usr/bin/rm")

    result = CommandRunnerService().check_command_available("rm")

    assert result.success
    assert result.is_available is True
    assert result.security_validated is False


def test_get_command_version_returns_first_output_line(
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
    monkeypatch.setattr(
        service,
        "run_silent",
        lambda *_args, **_kwargs: CommandResult(0, stdout="tool 1.2.3\nmore output"),
    )

    result = service.get_command_version("tool")

    assert result.success
    assert result.version == "tool 1.2.3"


def test_base_validation_converts_invalid_regex_to_failure_result() -> None:
    result = BaseValidationService.validate_string_pattern("value", "[")

    assert not result.success
    assert "Error validating value" in result.error
