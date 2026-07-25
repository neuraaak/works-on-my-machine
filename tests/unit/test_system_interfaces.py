#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SYSTEM INTERFACES - Boundary tests for the exception->Result contract
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Boundary tests for the system interfaces.

These verify the exception-rework contract at the interface layer: a service
raising its single exception is translated into a Result (never re-raised), and
the success path carries the service data through. Fake services are injected
directly so the tests exercise only the interface's translation logic.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import os
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.exceptions.system import SystemServiceError
from womm.interfaces.system.detector_interface import SystemDetectorInterface
from womm.interfaces.system.environment_interface import SystemEnvironmentInterface
from womm.interfaces.system.path_interface import SystemPathInterface
from womm.shared.results import (
    EnvironmentRefreshResult,
    EnvironmentVerificationResult,
    PathOperationResult,
    SystemDetectionResult,
)

# ///////////////////////////////////////////////////////////////
# FAKE SERVICES
# ///////////////////////////////////////////////////////////////


class _FakeDetectorService:
    """Stand-in for SystemDetectorService with a scriptable get_system_data."""

    def __init__(self, data: dict | None = None, error: Exception | None = None):
        self._data = data or {}
        self._error = error

    def get_system_data(self) -> dict:
        if self._error is not None:
            raise self._error
        return self._data


class _FakeEnvironmentService:
    """Stand-in for SystemEnvironmentService for refresh/verify."""

    def __init__(
        self,
        refresh: EnvironmentRefreshResult | None = None,
        verify: EnvironmentVerificationResult | None = None,
        error: Exception | None = None,
    ):
        self._refresh = refresh
        self._verify = verify
        self._error = error

    def refresh_environment(self) -> EnvironmentRefreshResult:
        if self._error is not None:
            raise self._error
        assert self._refresh is not None
        return self._refresh

    def verify_environment_refresh(self, command: str) -> EnvironmentVerificationResult:
        if self._error is not None:
            raise self._error
        assert self._verify is not None
        return self._verify


# ///////////////////////////////////////////////////////////////
# TESTS - DETECTOR INTERFACE
# ///////////////////////////////////////////////////////////////


class TestSystemDetectorInterface:
    """Boundary behaviour of SystemDetectorInterface.detect_system()."""

    def test_success_returns_result_with_data(self):
        """A service returning data yields a successful Result carrying it."""
        interface = SystemDetectorInterface()
        interface._detector = _FakeDetectorService(data={"system_info": {"x": 1}})

        result = interface.detect_system()

        assert isinstance(result, SystemDetectionResult)
        assert result.success is True
        assert result.system_data == {"system_info": {"x": 1}}

    def test_service_error_is_translated_to_failure_result(self):
        """A SystemServiceError becomes a failed Result, never re-raised."""
        interface = SystemDetectorInterface()
        interface._detector = _FakeDetectorService(
            error=SystemServiceError(
                operation="platform_info", reason="boom", details="ctx"
            )
        )

        result = interface.detect_system()

        assert isinstance(result, SystemDetectionResult)
        assert result.success is False
        assert "boom" in result.error
        assert result.system_data == {}


# ///////////////////////////////////////////////////////////////
# TESTS - ENVIRONMENT INTERFACE
# ///////////////////////////////////////////////////////////////


class TestSystemEnvironmentInterface:
    """Boundary behaviour of SystemEnvironmentInterface."""

    def test_refresh_success_passes_result_through(self):
        """A successful service result is returned unchanged."""
        interface = SystemEnvironmentInterface()
        interface._environment_service = _FakeEnvironmentService(
            refresh=EnvironmentRefreshResult(success=True, refresh_method="registry")
        )

        result = interface.refresh_environment()

        assert isinstance(result, EnvironmentRefreshResult)
        assert result.success is True
        assert result.refresh_method == "registry"

    def test_refresh_service_error_is_translated_to_failure_result(self):
        """A SystemServiceError becomes a failed Result, never re-raised."""
        interface = SystemEnvironmentInterface()
        interface._environment_service = _FakeEnvironmentService(
            error=SystemServiceError(
                operation="refresh_windows_environment", reason="boom"
            )
        )

        result = interface.refresh_environment()

        assert isinstance(result, EnvironmentRefreshResult)
        assert result.success is False
        assert "boom" in result.error

    def test_verify_returns_true_when_accessible(self):
        """Verification returns True when the service reports the command reachable."""
        interface = SystemEnvironmentInterface()
        interface._environment_service = _FakeEnvironmentService(
            verify=EnvironmentVerificationResult(success=True, command_accessible=True)
        )

        assert interface.verify_environment_refresh("womm") is True

    def test_verify_service_error_returns_false(self):
        """Verification is best-effort: a service error yields False, not a raise."""
        interface = SystemEnvironmentInterface()
        interface._environment_service = _FakeEnvironmentService(
            error=SystemServiceError(operation="verify", reason="boom")
        )

        assert interface.verify_environment_refresh("womm") is False


# ///////////////////////////////////////////////////////////////
# FAKE SERVICES - PATH
# ///////////////////////////////////////////////////////////////


class _FakePathService:
    """Stand-in for SystemPathService with scriptable operations."""

    def __init__(
        self,
        current: PathOperationResult | None = None,
        setup: PathOperationResult | None = None,
        remove: PathOperationResult | None = None,
        error: Exception | None = None,
    ):
        self._current = current
        self._setup = setup
        self._remove = remove
        self._error = error

    def get_current_system_path(self) -> PathOperationResult:
        if self._error is not None:
            raise self._error
        assert self._current is not None
        return self._current

    def setup_windows_path(self, entry_path: str, original_path: str):
        return self._setup_result()

    def setup_unix_path(self, entry_path: str, original_path: str):
        return self._setup_result()

    def remove_from_windows_path(self, entry_path: str):
        return self._remove_result()

    def remove_from_unix_path(self, entry_path: str):
        return self._remove_result()

    def _setup_result(self) -> PathOperationResult:
        if self._error is not None:
            raise self._error
        assert self._setup is not None
        return self._setup

    def _remove_result(self) -> PathOperationResult:
        if self._error is not None:
            raise self._error
        assert self._remove is not None
        return self._remove


def _make_path_interface(tmp_path, platform: str = "Linux") -> SystemPathInterface:
    interface = SystemPathInterface(target=str(tmp_path))
    interface.platform = platform
    return interface


# ///////////////////////////////////////////////////////////////
# TESTS - PATH INTERFACE (ADD/REMOVE)
# ///////////////////////////////////////////////////////////////


class TestSystemPathInterfaceModify:
    """Boundary behaviour of add_to_path()/remove_from_path()."""

    def test_add_to_path_success_passes_result_through(self, tmp_path):
        """A successful service result is returned unchanged."""
        interface = _make_path_interface(tmp_path)
        interface._path_service = _FakePathService(
            current=PathOperationResult(success=True, path_entries=["/a"]),
            setup=PathOperationResult(
                success=True, path_modified=True, operation="add"
            ),
        )

        result = interface.add_to_path()

        assert isinstance(result, PathOperationResult)
        assert result.success is True
        assert result.path_modified is True

    def test_add_to_path_service_error_is_translated_to_failure_result(self, tmp_path):
        """A SystemServiceError from get_current_system_path becomes a failed Result."""
        interface = _make_path_interface(tmp_path)
        interface._path_service = _FakePathService(
            error=SystemServiceError(operation="path_get", reason="boom")
        )

        result = interface.add_to_path()

        assert isinstance(result, PathOperationResult)
        assert result.success is False
        assert "boom" in result.error
        assert result.operation == "add"

    def test_add_to_path_get_current_failure_short_circuits(self, tmp_path):
        """A failed get_current_system_path Result is surfaced as an add failure."""
        interface = _make_path_interface(tmp_path)
        interface._path_service = _FakePathService(
            current=PathOperationResult(success=False, message="registry unreadable")
        )

        result = interface.add_to_path()

        assert result.success is False
        assert result.message == "registry unreadable"
        assert result.operation == "add"

    def test_remove_from_path_success_passes_result_through(self, tmp_path):
        """A successful removal result is returned unchanged."""
        interface = _make_path_interface(tmp_path)
        interface._path_service = _FakePathService(
            remove=PathOperationResult(
                success=True, path_modified=True, operation="remove"
            )
        )

        result = interface.remove_from_path()

        assert result.success is True
        assert result.path_modified is True

    def test_remove_from_path_service_error_is_translated_to_failure_result(
        self, tmp_path
    ):
        """A service error during removal becomes a failed Result, never re-raised."""
        interface = _make_path_interface(tmp_path)
        interface._path_service = _FakePathService(
            error=SystemServiceError(operation="path_get", reason="boom")
        )

        result = interface.remove_from_path()

        assert result.success is False
        assert "boom" in result.error
        assert result.operation == "remove"


# ///////////////////////////////////////////////////////////////
# TESTS - PATH INTERFACE (BACKUPS)
# ///////////////////////////////////////////////////////////////


class TestSystemPathInterfaceBackups:
    """Boundary behaviour of list_backups()/create_backup()/restore_backup()."""

    def test_list_backups_empty_when_no_backup_dir(self, tmp_path):
        """No backup directory is a normal empty state, not a failure."""
        interface = _make_path_interface(tmp_path)

        result = interface.list_backups()

        assert result.success is True
        assert result.backups == []

    def test_list_backups_reads_valid_backup_files(self, tmp_path):
        """A valid backup JSON file is surfaced with its entry count."""
        interface = _make_path_interface(tmp_path)
        interface.backup_dir.mkdir(parents=True)
        backup_file = interface.backup_dir / ".path_20260101_000000.json"
        backup_file.write_text(json.dumps({"entries": ["/a", "/b"]}), encoding="utf-8")

        result = interface.list_backups()

        assert result.success is True
        assert len(result.backups) == 1
        assert result.backups[0].path_entries == 2

    def test_list_backups_skips_corrupt_files(self, tmp_path):
        """A corrupt backup file is skipped rather than failing the whole listing."""
        interface = _make_path_interface(tmp_path)
        interface.backup_dir.mkdir(parents=True)
        (interface.backup_dir / ".path_bad.json").write_text(
            "not json", encoding="utf-8"
        )

        result = interface.list_backups()

        assert result.success is True
        assert result.backups == []

    def test_create_backup_success_writes_file(self, tmp_path):
        """A successful backup writes a JSON file and reports its path."""
        interface = _make_path_interface(tmp_path)
        interface._path_service = _FakePathService(
            current=PathOperationResult(success=True, path_entries=["/a", "/b"])
        )

        result = interface.create_backup()

        assert result.success is True
        assert result.entries_count == 2
        assert Path(result.backup_file).exists()

    def test_create_backup_service_error_is_translated_to_failure_result(
        self, tmp_path
    ):
        """A service error during backup creation becomes a failed Result."""
        interface = _make_path_interface(tmp_path)
        interface._path_service = _FakePathService(
            error=SystemServiceError(operation="path_get", reason="boom")
        )

        result = interface.create_backup()

        assert result.success is False
        assert "boom" in result.error

    def test_restore_backup_unix_updates_environment(self, tmp_path, monkeypatch):
        """Restoring on a non-Windows platform updates the process environment."""
        interface = _make_path_interface(tmp_path, platform="Linux")
        backup_file = tmp_path / ".path_backup.json"
        backup_file.write_text(
            json.dumps(
                {"path_string": "/restored:/path", "entries": ["/restored", "/path"]}
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("PATH", "/old")

        result = interface.restore_backup(backup_file)

        assert result.success is True
        assert result.path_modified is True
        assert os.environ["PATH"] == "/restored:/path"

    def test_restore_backup_corrupt_file_is_translated_to_failure_result(
        self, tmp_path
    ):
        """An unreadable backup file yields a failed Result, never a raise."""
        interface = _make_path_interface(tmp_path)
        backup_file = tmp_path / ".path_bad.json"
        backup_file.write_text("not json", encoding="utf-8")

        result = interface.restore_backup(backup_file)

        assert result.success is False
        assert result.operation == "restore"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
