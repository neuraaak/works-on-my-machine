#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST LINT SERVICES - Boundary tests for the utils/services contract
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Boundary tests for the lint utils and services.

These verify the two lower layers of the exception-rework contract: the utils
raise stdlib exceptions only, and the services collapse every failure into the
single ``LintServiceError`` discriminated by its ``operation`` field. The
command runner is faked so nothing is executed on the machine.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import subprocess
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.exceptions.common import TimeoutError as CommandTimeoutError
from womm.exceptions.lint import LintServiceError
from womm.services.lint.core_service import LintService
from womm.services.lint.python_lint_service import PythonLintService
from womm.shared.results.base import CommandResult
from womm.utils.lint import get_tool_version

# ///////////////////////////////////////////////////////////////
# FAKES & FIXTURES
# ///////////////////////////////////////////////////////////////


class _FakeCommandRunner:
    """Stand-in for CommandRunnerService with a scriptable run_silent."""

    def __init__(
        self, result: CommandResult | None = None, error: Exception | None = None
    ):
        self._result = result
        self._error = error

    def run_silent(self, command, **kwargs) -> CommandResult:
        if self._error is not None:
            raise self._error
        assert self._result is not None
        return self._result


@pytest.fixture
def lint_service():
    """Yield the LintService singleton with its command runner restored after."""
    service = LintService()
    original = service.command_runner
    yield service
    service.command_runner = original


# ///////////////////////////////////////////////////////////////
# TESTS - UTILS RAISE STDLIB ONLY
# ///////////////////////////////////////////////////////////////


class TestGetToolVersionUtil:
    """The util layer normalizes failures into stdlib exceptions."""

    def test_empty_tool_name_raises_value_error(self):
        """An empty tool name is a plain ValueError, not a project exception."""
        with pytest.raises(ValueError, match="Tool name cannot be empty"):
            get_tool_version("", _FakeCommandRunner())

    def test_failed_command_raises_called_process_error(self):
        """A non-zero return code surfaces as subprocess.CalledProcessError."""
        runner = _FakeCommandRunner(
            CommandResult(returncode=2, stdout="", stderr="not found")
        )

        with pytest.raises(subprocess.CalledProcessError) as excinfo:
            get_tool_version("ruff", runner)

        assert excinfo.value.returncode == 2
        assert excinfo.value.stderr == "not found"

    def test_version_is_taken_from_the_first_line(self):
        """The default extraction keeps the first output line."""
        runner = _FakeCommandRunner(
            CommandResult(returncode=0, stdout="ruff 0.16.0\nextra\n")
        )

        assert get_tool_version("ruff", runner) == "ruff 0.16.0"

    def test_isort_version_is_found_behind_its_ascii_art(self):
        """isort prints a banner, so the VERSION line is searched for."""
        runner = _FakeCommandRunner(
            CommandResult(returncode=0, stdout="  _ _\n banner\nVERSION 7.0.0\n")
        )

        assert get_tool_version("isort", runner) == "VERSION 7.0.0"

    def test_silent_tool_returns_empty_version(self):
        """A tool printing nothing yields an empty version, not an error."""
        runner = _FakeCommandRunner(CommandResult(returncode=0, stdout="   "))

        assert get_tool_version("ruff", runner) == ""


# ///////////////////////////////////////////////////////////////
# TESTS - LINT SERVICE COLLAPSES INTO ONE EXCEPTION
# ///////////////////////////////////////////////////////////////


class TestLintServiceErrors:
    """Every LintService failure is one exception discriminated by operation."""

    def test_empty_tool_name_is_reported_with_the_operation(self, lint_service):
        """Input validation raises LintServiceError carrying the failing step."""
        with pytest.raises(LintServiceError) as excinfo:
            lint_service.run_tool_check("", [], ["src"], Path("."))

        assert excinfo.value.operation == "run_tool_check"
        assert excinfo.value.reason == "Tool name cannot be empty"

    def test_empty_targets_are_reported_with_the_operation(self, lint_service):
        """The fix path reports its own operation on the same exception type."""
        with pytest.raises(LintServiceError) as excinfo:
            lint_service.run_tool_fix("ruff", [], [], Path("."))

        assert excinfo.value.operation == "run_tool_fix"
        assert excinfo.value.reason == "Target directories cannot be empty"

    def test_timeout_is_normalized_into_the_service_exception(self, lint_service):
        """A command timeout no longer escapes as a command-layer exception."""
        lint_service.command_runner = _FakeCommandRunner(
            error=CommandTimeoutError(command="ruff", timeout_seconds=300)
        )

        with pytest.raises(LintServiceError) as excinfo:
            lint_service.run_tool_check("ruff", [], ["src"], Path("."))

        assert excinfo.value.operation == "run_tool_check"
        assert "timed out" in excinfo.value.reason

    def test_malformed_json_output_is_reported_as_a_service_error(self, lint_service):
        """Undecodable JSON is chained into LintServiceError, not raised raw."""
        lint_service.command_runner = _FakeCommandRunner(
            CommandResult(returncode=0, stdout="{not json")
        )

        with pytest.raises(LintServiceError) as excinfo:
            lint_service.run_tool_check(
                "bandit", [], ["src"], Path("."), json_output=True
            )

        assert excinfo.value.operation == "run_tool_check"
        assert "Failed to parse bandit JSON output" in excinfo.value.reason
        assert isinstance(excinfo.value.__cause__, ValueError)

    def test_json_payload_is_extracted_behind_log_lines(self, lint_service):
        """Tools prefixing their JSON with logs still get their issues counted.

        The payload starts at the first line opening a JSON document, so a log
        line must not itself start with ``{`` or ``[``.
        """
        lint_service.command_runner = _FakeCommandRunner(
            CommandResult(returncode=1, stdout='INFO starting\n[{"a": 1}, {"b": 2}]')
        )

        result = lint_service.run_tool_check(
            "bandit", [], ["src"], Path("."), json_output=True
        )

        assert result.issues_found == 2

    def test_no_json_at_all_is_treated_as_no_issue(self, lint_service):
        """Output without any JSON document is not an error."""
        lint_service.command_runner = _FakeCommandRunner(
            CommandResult(returncode=0, stdout="nothing to report")
        )

        result = lint_service.run_tool_check(
            "bandit", [], ["src"], Path("."), json_output=True
        )

        assert result.success is True
        assert result.issues_found == 0


# ///////////////////////////////////////////////////////////////
# TESTS - PYTHON LINT SERVICE VALIDATION
# ///////////////////////////////////////////////////////////////


class TestPythonLintServiceValidation:
    """PythonLintService reports its input failures on the same exception."""

    def test_empty_targets_are_rejected(self):
        """Both entry points share the validation helper and its exception."""
        with pytest.raises(LintServiceError) as excinfo:
            PythonLintService().check_python_code([], Path("."))

        assert excinfo.value.operation == "check_python_code"
        assert excinfo.value.reason == "Target directories cannot be empty"

    def test_missing_working_directory_is_rejected(self, tmp_path):
        """A working directory that does not exist fails before any tool runs."""
        missing = tmp_path / "does-not-exist"

        with pytest.raises(LintServiceError) as excinfo:
            PythonLintService().fix_python_code(["src"], missing)

        assert excinfo.value.operation == "fix_python_code"
        assert excinfo.value.reason == "Working directory does not exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
