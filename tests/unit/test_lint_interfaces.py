#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST LINT INTERFACES - Boundary tests for the exception->Result contract
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Boundary tests for the Python lint interface.

These verify the exception-rework contract at the interface layer: the lint
service raising its single exception is translated into a Result (never
re-raised), the scanner's result-based failures are carried through, and the
success path aggregates the service data. Fake services are injected directly
so the tests exercise only the interface's translation logic.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.exceptions.lint import LintServiceError
from womm.interfaces.lint.python_lint_interface import PythonLintInterface
from womm.shared.results.file_results import FileScanResult, FileSearchResult
from womm.shared.results.lint_results import (
    LintSummaryResult,
    ToolResult,
    ToolStatusResult,
)

# ///////////////////////////////////////////////////////////////
# FAKE SERVICES
# ///////////////////////////////////////////////////////////////


class _FakeFileScanner:
    """Stand-in for FileScannerService, which never raises."""

    def __init__(self, files: list[Path] | None = None, error: str = ""):
        self._files = files or []
        self._error = error

    def get_project_python_files(self, project_root: Path) -> FileSearchResult:
        return self._search_result()

    def find_python_files(self, path: Path, recursive: bool = True) -> FileSearchResult:
        return self._search_result()

    def get_scan_summary(self, files: list[Path]) -> FileScanResult:
        return FileScanResult(success=True, total_files=len(files))

    def _search_result(self) -> FileSearchResult:
        if self._error:
            return FileSearchResult(success=False, error=self._error, files_found=[])
        return FileSearchResult(success=True, files_found=list(self._files))


class _FakeLintService:
    """Stand-in for PythonLintService with scriptable check/fix outcomes."""

    def __init__(
        self,
        results: dict[str, ToolResult] | None = None,
        error: Exception | None = None,
        summary: dict[str, str] | None = None,
    ):
        self._results = results or {}
        self._error = error
        self._summary = summary or {}

    def check_python_code(self, target_dirs, cwd, tools=None) -> dict[str, ToolResult]:
        return self._run()

    def fix_python_code(self, target_dirs, cwd, tools=None) -> dict[str, ToolResult]:
        return self._run()

    def get_tool_summary(self) -> dict[str, str]:
        return self._summary

    def _run(self) -> dict[str, ToolResult]:
        if self._error is not None:
            raise self._error
        return self._results


def _interface(
    scanner: _FakeFileScanner, service: _FakeLintService
) -> PythonLintInterface:
    """Build an interface with both services faked out."""
    interface = PythonLintInterface(project_root=Path("."))
    interface._file_scanner = scanner
    interface._python_lint_service = service
    return interface


# ///////////////////////////////////////////////////////////////
# TESTS - CHECK MODE
# ///////////////////////////////////////////////////////////////


class TestCheckPythonCode:
    """Boundary behaviour of PythonLintInterface.check_python_code()."""

    def test_success_aggregates_tool_results(self):
        """Successful tool runs yield a successful Result carrying the totals."""
        interface = _interface(
            _FakeFileScanner(files=[Path("a.py"), Path("b.py")]),
            _FakeLintService(
                results={
                    "ruff": ToolResult(
                        success=True, tool_name="ruff", files_checked=2, issues_found=0
                    )
                }
            ),
        )

        result = interface.check_python_code()

        assert isinstance(result, LintSummaryResult)
        assert result.success is True
        assert result.total_files == 2
        assert result.total_issues == 0
        assert "Checked 2 files with 1 tools" in result.message

    def test_failing_tool_yields_failed_result_with_data(self):
        """A tool reporting issues fails the summary but keeps its results."""
        interface = _interface(
            _FakeFileScanner(files=[Path("a.py")]),
            _FakeLintService(
                results={
                    "ruff": ToolResult(
                        success=False, tool_name="ruff", files_checked=1, issues_found=3
                    )
                }
            ),
        )

        result = interface.check_python_code()

        assert result.success is False
        assert result.total_issues == 3
        assert result.tool_results is not None
        assert "ruff" in result.tool_results

    def test_service_error_is_translated_to_failure_result(self):
        """A LintServiceError becomes a failed Result, never re-raised."""
        interface = _interface(
            _FakeFileScanner(files=[Path("a.py")]),
            _FakeLintService(
                error=LintServiceError(
                    operation="check_python_code", reason="boom", details="ctx"
                )
            ),
        )

        result = interface.check_python_code()

        assert isinstance(result, LintSummaryResult)
        assert result.success is False
        assert "boom" in result.error
        assert not result.tool_results

    def test_scan_failure_is_reported_without_running_tools(self):
        """The scanner's result-based failure short-circuits into a failed Result."""
        interface = _interface(
            _FakeFileScanner(error="permission denied"),
            _FakeLintService(error=AssertionError("tools must not run")),
        )

        result = interface.check_python_code()

        assert result.success is False
        assert "permission denied" in result.error

    def test_no_python_file_yields_failure_result(self):
        """An empty scan is a failure, reported with the mode in the message."""
        interface = _interface(_FakeFileScanner(files=[]), _FakeLintService())

        result = interface.check_python_code()

        assert result.success is False
        assert result.error == "No Python files found to check"


# ///////////////////////////////////////////////////////////////
# TESTS - FIX MODE
# ///////////////////////////////////////////////////////////////


class TestFixPythonCode:
    """Boundary behaviour of PythonLintInterface.fix_python_code()."""

    def test_success_reports_fixed_issues(self):
        """Fix mode aggregates the fixed count and uses its own wording."""
        interface = _interface(
            _FakeFileScanner(files=[Path("a.py")]),
            _FakeLintService(
                results={
                    "black": ToolResult(
                        success=True, tool_name="black", files_checked=1, fixed_issues=4
                    )
                }
            ),
        )

        result = interface.fix_python_code()

        assert result.success is True
        assert result.total_fixed == 4
        assert "Processed 1 files with 1 tools" in result.message

    def test_service_error_is_translated_to_failure_result(self):
        """A LintServiceError becomes a failed Result, never re-raised."""
        interface = _interface(
            _FakeFileScanner(files=[Path("a.py")]),
            _FakeLintService(
                error=LintServiceError(operation="fix_python_code", reason="boom")
            ),
        )

        result = interface.fix_python_code()

        assert result.success is False
        assert "boom" in result.error

    def test_no_python_file_yields_failure_result(self):
        """The empty-scan message reflects the fix mode."""
        interface = _interface(_FakeFileScanner(files=[]), _FakeLintService())

        result = interface.fix_python_code()

        assert result.error == "No Python files found to fix"


# ///////////////////////////////////////////////////////////////
# TESTS - TOOL STATUS
# ///////////////////////////////////////////////////////////////


class TestGetToolStatus:
    """Boundary behaviour of PythonLintInterface.get_tool_status()."""

    def test_success_carries_the_tool_summary(self):
        """The service summary is passed through on a successful Result."""
        interface = _interface(
            _FakeFileScanner(),
            _FakeLintService(summary={"ruff": "Available: ruff 0.16.0"}),
        )

        result = interface.get_tool_status()

        assert isinstance(result, ToolStatusResult)
        assert result.success is True
        assert result.tool_summary == {"ruff": "Available: ruff 0.16.0"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
