#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST FILE SCANNER SERVICE - Direct common service coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for file discovery, filtering, and scan summaries."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.exceptions.common import SecurityServiceError
from womm.services.common.file_scanner_service import FileScannerService
from womm.shared.results import PathValidationResult

# ///////////////////////////////////////////////////////////////
# TEST DOUBLES
# ///////////////////////////////////////////////////////////////


class _PathValidator:
    """Configurable path validator used at the security boundary."""

    def __init__(self, *, is_valid: bool = True, error: Exception | None = None):
        self._is_valid = is_valid
        self._error = error

    def validate_file_path(self, file_path: str) -> PathValidationResult:
        if self._error is not None:
            raise self._error
        return PathValidationResult(
            success=self._is_valid,
            path=file_path,
            is_valid=self._is_valid,
            validation_reason="accepted" if self._is_valid else "rejected",
        )


def _scanner_with_validator(
    monkeypatch: pytest.MonkeyPatch, validator: _PathValidator
) -> FileScannerService:
    """Inject a validator without weakening the production attribute type."""
    scanner = FileScannerService()
    monkeypatch.setattr(scanner, "security_validator", validator)
    return scanner


# ///////////////////////////////////////////////////////////////
# FILE DISCOVERY
# ///////////////////////////////////////////////////////////////


def test_find_python_files_accepts_a_python_file(tmp_path: Path) -> None:
    source = tmp_path / "main.py"
    source.write_text("print('ok')", encoding="utf-8")

    result = FileScannerService().find_python_files(source)

    assert result.success
    assert result.files_found == [source]
    assert result.target_path == source


def test_find_python_files_ignores_a_non_python_file(tmp_path: Path) -> None:
    source = tmp_path / "README.md"
    source.write_text("# Demo", encoding="utf-8")

    result = FileScannerService().find_python_files(source)

    assert result.success
    assert result.files_found == []


def test_recursive_scan_filters_extensions_exclusions_and_sensitive_files(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "src"
    nested_dir = source_dir / "nested"
    excluded_dir = source_dir / ".venv"
    nested_dir.mkdir(parents=True)
    excluded_dir.mkdir()
    root_file = source_dir / "main.py"
    nested_file = nested_dir / "types.pyi"
    root_file.touch()
    nested_file.touch()
    (nested_dir / "notes.txt").touch()
    (excluded_dir / "hidden.py").touch()
    (source_dir / "api_token.py").touch()

    result = FileScannerService().find_python_files(source_dir)

    assert result.success
    assert result.files_found is not None
    assert set(result.files_found) == {root_file, nested_file}


def test_non_recursive_scan_does_not_descend_into_subdirectories(
    tmp_path: Path,
) -> None:
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    root_file = tmp_path / "root.py"
    root_file.touch()
    (nested_dir / "nested.py").touch()

    result = FileScannerService().find_python_files(tmp_path, recursive=False)

    assert result.success
    assert result.files_found == [root_file]
    assert result.recursive is False


def test_find_python_files_returns_failure_for_missing_path(tmp_path: Path) -> None:
    result = FileScannerService().find_python_files(tmp_path / "missing")

    assert not result.success
    assert result.files_found == []
    assert "Path does not exist" in result.error


def test_non_recursive_scan_translates_directory_access_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def deny_access(_path: Path):
        raise PermissionError("access denied")

    monkeypatch.setattr(Path, "iterdir", deny_access)

    result = FileScannerService().find_python_files(tmp_path, recursive=False)

    assert not result.success
    assert "access denied" in result.error


# ///////////////////////////////////////////////////////////////
# PROJECT SCANNING
# ///////////////////////////////////////////////////////////////


def test_get_project_python_files_discovers_sources_and_excludes_venv(
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "src"
    excluded_dir = tmp_path / "venv"
    source_dir.mkdir()
    excluded_dir.mkdir()
    source_file = source_dir / "app.py"
    stub_file = source_dir / "app.pyi"
    source_file.touch()
    stub_file.touch()
    (excluded_dir / "dependency.py").touch()

    result = FileScannerService().get_project_python_files(tmp_path)

    assert result.success
    assert result.files_found is not None
    assert set(result.files_found) == {source_file, stub_file}
    assert result.recursive is True


def test_get_project_python_files_rejects_a_file_as_project_root(
    tmp_path: Path,
) -> None:
    source = tmp_path / "main.py"
    source.touch()

    result = FileScannerService().get_project_python_files(source)

    assert not result.success
    assert "Invalid project root" in result.error


def test_get_project_python_files_translates_recursive_access_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def deny_access(_path: Path, _pattern: str):
        raise PermissionError("recursive access denied")

    monkeypatch.setattr(Path, "rglob", deny_access)

    result = FileScannerService().get_project_python_files(tmp_path)

    assert not result.success
    assert "recursive access denied" in result.error


# ///////////////////////////////////////////////////////////////
# SECURITY FILTERING
# ///////////////////////////////////////////////////////////////


def test_security_validator_rejection_excludes_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "main.py"
    source.touch()
    scanner = _scanner_with_validator(
        monkeypatch,
        _PathValidator(is_valid=False),
    )

    result = scanner.find_python_files(source)

    assert result.success
    assert result.files_found == []


def test_security_validator_error_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "main.py"
    source.touch()
    scanner = _scanner_with_validator(
        monkeypatch,
        _PathValidator(error=SecurityServiceError("validator unavailable")),
    )

    result = scanner.find_python_files(source)

    assert result.success
    assert result.files_found == []


# ///////////////////////////////////////////////////////////////
# SCAN SUMMARY
# ///////////////////////////////////////////////////////////////


def test_scan_summary_reports_previously_discovered_files(tmp_path: Path) -> None:
    files = [tmp_path / "one.py", tmp_path / "two.pyi"]

    result = FileScannerService().get_scan_summary(files)

    assert result.success
    assert result.target_path == tmp_path
    assert result.total_files == 2
    assert result.files_found == files
    assert result.file_extensions is not None
    assert result.excluded_dirs is not None
    assert ".py" in result.file_extensions
    assert ".venv" in result.excluded_dirs


def test_scan_summary_without_target_is_empty() -> None:
    result = FileScannerService().get_scan_summary()

    assert result.success
    assert result.target_path is None
    assert result.total_files == 0
    assert result.files_found == []
