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
from womm.shared.paths import WOMM_HOME_ENV, path_backups_dir
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


@pytest.fixture(autouse=True)
def _isolated_womm_home(tmp_path, monkeypatch):
    """Keep PATH backups inside the test's own data directory."""
    monkeypatch.setenv(WOMM_HOME_ENV, str(tmp_path))


def _make_path_interface(platform: str = "Linux") -> SystemPathInterface:
    interface = SystemPathInterface()
    interface.platform = platform
    return interface


def test_path_backups_live_in_the_data_directory(tmp_path):
    """Backups are user data, independent from installation locations."""
    interface = _make_path_interface()

    assert interface.backup_dir == path_backups_dir()
    assert interface.backup_dir == tmp_path / "backups" / "path"
    assert interface.backup_dir.is_dir()


# ///////////////////////////////////////////////////////////////
# TESTS - PATH INTERFACE (ADD/REMOVE)
# ///////////////////////////////////////////////////////////////


def _bin_dir(tmp_path, name: str = "tools") -> Path:
    """Build a plausible PATH candidate: a directory holding an executable."""
    directory = tmp_path / name
    directory.mkdir()
    executable = directory / "thing.exe"
    executable.write_text("")
    executable.chmod(0o755)
    return directory


class TestSystemPathInterfaceModify:
    """Boundary behaviour of add_to_path()/remove_from_path()."""

    def test_add_to_path_success_passes_result_through(self, tmp_path):
        """A successful service result is returned unchanged."""
        interface = _make_path_interface()
        interface._path_service = _FakePathService(
            current=PathOperationResult(success=True, path_entries=["/a"]),
            setup=PathOperationResult(
                success=True, path_modified=True, operation="add"
            ),
        )

        result = interface.add_to_path(_bin_dir(tmp_path))

        assert isinstance(result, PathOperationResult)
        assert result.success is True
        assert result.path_modified is True

    def test_add_to_path_backs_the_current_path_up_before_writing(self, tmp_path):
        """The change must be undoable: a snapshot exists once add succeeded."""
        interface = _make_path_interface()
        interface._path_service = _FakePathService(
            current=PathOperationResult(success=True, path_entries=["/a"]),
            setup=PathOperationResult(
                success=True, path_modified=True, operation="add"
            ),
        )

        assert interface.list_backups().backups == []

        interface.add_to_path(_bin_dir(tmp_path))

        assert len(interface.list_backups().backups) == 1

    def test_add_to_path_refuses_a_missing_directory(self, tmp_path):
        """A path that does not exist is a typo, not an entry to write."""
        interface = _make_path_interface()
        interface._path_service = _FakePathService(
            current=PathOperationResult(success=True, path_entries=["/a"]),
            setup=PathOperationResult(success=True, operation="add"),
        )

        result = interface.add_to_path(tmp_path / "nope")

        assert result.success is False
        assert result.error == "Directory does not exist"
        assert interface.list_backups().backups == []

    def test_add_to_path_refuses_a_file(self, tmp_path):
        """PATH entries are directories; a file would never resolve anything."""
        interface = _make_path_interface()
        interface._path_service = _FakePathService(
            current=PathOperationResult(success=True, path_entries=["/a"]),
            setup=PathOperationResult(success=True, operation="add"),
        )
        target = tmp_path / "thing.exe"
        target.write_text("")

        result = interface.add_to_path(target)

        assert result.success is False
        assert result.error == "Not a directory"

    def test_add_to_path_refuses_a_directory_without_executable(self, tmp_path):
        """An entry resolving nothing is almost always the wrong nesting level."""
        interface = _make_path_interface()
        interface._path_service = _FakePathService(
            current=PathOperationResult(success=True, path_entries=["/a"]),
            setup=PathOperationResult(success=True, operation="add"),
        )
        empty = tmp_path / "empty"
        empty.mkdir()

        result = interface.add_to_path(empty)

        assert result.success is False
        assert "no executable" in result.error

    def test_add_to_path_refuses_to_write_when_the_backup_fails(self, tmp_path):
        """A PATH write we cannot undo is not one to attempt."""
        interface = _make_path_interface()
        interface._path_service = _FakePathService(
            current=PathOperationResult(success=False, message="registry unreadable"),
            setup=PathOperationResult(
                success=True, path_modified=True, operation="add"
            ),
        )

        result = interface.add_to_path(_bin_dir(tmp_path))

        assert result.success is False
        assert result.message == "Refused to modify PATH without a backup"
        assert result.operation == "add"

    def test_add_to_path_service_error_is_translated_to_failure_result(self, tmp_path):
        """A SystemServiceError from get_current_system_path becomes a failed Result."""
        interface = _make_path_interface()
        interface._path_service = _FakePathService(
            error=SystemServiceError(operation="path_get", reason="boom")
        )

        result = interface.add_to_path(_bin_dir(tmp_path))

        assert isinstance(result, PathOperationResult)
        assert result.success is False
        assert "boom" in result.error
        assert result.operation == "add"

    def test_remove_from_path_success_passes_result_through(self, tmp_path):
        """A successful removal result is returned unchanged."""
        interface = _make_path_interface()
        interface._path_service = _FakePathService(
            current=PathOperationResult(success=True, path_entries=["/a"]),
            remove=PathOperationResult(
                success=True, path_modified=True, operation="remove"
            ),
        )

        result = interface.remove_from_path(_bin_dir(tmp_path))

        assert result.success is True
        assert result.path_modified is True

    def test_remove_from_path_accepts_a_directory_that_no_longer_exists(self, tmp_path):
        """Dropping the entry of an uninstalled tool is the main use case."""
        interface = _make_path_interface()
        interface._path_service = _FakePathService(
            current=PathOperationResult(success=True, path_entries=["/a"]),
            remove=PathOperationResult(
                success=True, path_modified=True, operation="remove"
            ),
        )

        result = interface.remove_from_path(tmp_path / "uninstalled")

        assert result.success is True
        assert result.path_modified is True

    def test_remove_from_path_refuses_to_write_when_the_backup_fails(self, tmp_path):
        """Removal is a PATH write too, and needs the same safety net."""
        interface = _make_path_interface()
        interface._path_service = _FakePathService(
            current=PathOperationResult(success=False, message="registry unreadable"),
            remove=PathOperationResult(
                success=True, path_modified=True, operation="remove"
            ),
        )

        result = interface.remove_from_path(tmp_path / "uninstalled")

        assert result.success is False
        assert result.message == "Refused to modify PATH without a backup"
        assert result.operation == "remove"

    def test_remove_from_path_service_error_is_translated_to_failure_result(
        self, tmp_path
    ):
        """A service error during removal becomes a failed Result, never re-raised."""
        interface = _make_path_interface()
        interface._path_service = _FakePathService(
            error=SystemServiceError(operation="path_get", reason="boom")
        )

        result = interface.remove_from_path(tmp_path / "uninstalled")

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
        interface = _make_path_interface()

        result = interface.list_backups()

        assert result.success is True
        assert result.backups == []

    def test_list_backups_reads_valid_backup_files(self, tmp_path):
        """A valid backup JSON file is surfaced with its entry count."""
        interface = _make_path_interface()
        interface.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_file = interface.backup_dir / ".path_20260101_000000.json"
        backup_file.write_text(json.dumps({"entries": ["/a", "/b"]}), encoding="utf-8")

        result = interface.list_backups()

        assert result.success is True
        assert len(result.backups) == 1
        assert result.backups[0].path_entries == 2

    def test_list_backups_skips_corrupt_files(self, tmp_path):
        """A corrupt backup file is skipped rather than failing the whole listing."""
        interface = _make_path_interface()
        interface.backup_dir.mkdir(parents=True, exist_ok=True)
        (interface.backup_dir / ".path_bad.json").write_text(
            "not json", encoding="utf-8"
        )

        result = interface.list_backups()

        assert result.success is True
        assert result.backups == []

    def test_create_backup_success_writes_file(self, tmp_path):
        """A successful backup writes a JSON file and reports its path."""
        interface = _make_path_interface()
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
        interface = _make_path_interface()
        interface._path_service = _FakePathService(
            error=SystemServiceError(operation="path_get", reason="boom")
        )

        result = interface.create_backup()

        assert result.success is False
        assert "boom" in result.error

    def test_restore_backup_unix_updates_environment(self, tmp_path, monkeypatch):
        """Restoring on a non-Windows platform updates the process environment."""
        interface = _make_path_interface(platform="Linux")
        interface.backup_dir.mkdir(parents=True, exist_ok=True)
        (interface.backup_dir / ".path_backup.json").write_text(
            json.dumps(
                {"path_string": "/restored:/path", "entries": ["/restored", "/path"]}
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("PATH", "/old")

        result = interface.restore_backup(".path_backup.json")

        assert result.success is True
        assert result.path_modified is True
        assert os.environ["PATH"] == "/restored:/path"

    def test_restore_backup_corrupt_file_is_translated_to_failure_result(
        self, tmp_path
    ):
        """An unreadable backup file yields a failed Result, never a raise."""
        interface = _make_path_interface()
        interface.backup_dir.mkdir(parents=True, exist_ok=True)
        (interface.backup_dir / ".path_bad.json").write_text(
            "not json", encoding="utf-8"
        )

        result = interface.restore_backup(".path_bad.json")

        assert result.success is False
        assert result.operation == "restore"

    # ///////////////////////////////////////////////////////////////
    # CONTAINMENT OF THE RESTORE NAME
    # ///////////////////////////////////////////////////////////////
    #
    # restore_backup writes HKCU\Environment\PATH from whatever the backup
    # JSON says, so an attacker-chosen file reached through this name is a
    # user-PATH takeover, i.e. code execution on the next command launch.
    # Every hostile case below plants a *real, readable, valid* backup at the
    # end of the hostile path: without it the read would fail anyway and the
    # test would pass through a rejection path other than containment.

    @staticmethod
    def _plant_valid_backup(target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps({"path_string": "/evil", "entries": ["/evil"]}),
            encoding="utf-8",
        )

    def test_restore_backup_refuses_a_traversal_name(self, tmp_path, monkeypatch):
        """`../` must not reach a real backup planted outside the directory."""
        interface = _make_path_interface(platform="Linux")
        interface.backup_dir.mkdir(parents=True, exist_ok=True)
        self._plant_valid_backup(interface.backup_dir.parent / "evil.json")
        monkeypatch.setenv("PATH", "/old")

        result = interface.restore_backup("../evil.json")

        assert result.success is False
        assert os.environ["PATH"] == "/old"

    def test_restore_backup_refuses_an_absolute_name(self, tmp_path, monkeypatch):
        """An absolute path to a real backup must not be accepted as a name."""
        interface = _make_path_interface(platform="Linux")
        interface.backup_dir.mkdir(parents=True, exist_ok=True)
        outside = tmp_path / "outside" / "evil.json"
        self._plant_valid_backup(outside)
        monkeypatch.setenv("PATH", "/old")

        result = interface.restore_backup(str(outside))

        assert result.success is False
        assert os.environ["PATH"] == "/old"

    def test_restore_backup_refuses_a_separator_name(self, tmp_path, monkeypatch):
        """A relative name with a separator must not descend either."""
        interface = _make_path_interface(platform="Linux")
        self._plant_valid_backup(interface.backup_dir / "sub" / "evil.json")
        monkeypatch.setenv("PATH", "/old")

        result = interface.restore_backup("sub/evil.json")

        assert result.success is False
        assert os.environ["PATH"] == "/old"

    def test_restore_backup_rejection_does_not_disclose_the_resolved_path(
        self, tmp_path
    ):
        """The refusal quotes the supplied name only, never where it resolved."""
        interface = _make_path_interface(platform="Linux")
        interface.backup_dir.mkdir(parents=True, exist_ok=True)
        self._plant_valid_backup(interface.backup_dir.parent / "evil.json")

        result = interface.restore_backup("../evil.json")

        assert result.success is False
        assert str(interface.backup_dir.parent.resolve()) not in result.message
        assert str(interface.backup_dir.parent.resolve()) not in (result.error or "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
