#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST CONTEXT INTERFACES - Boundary tests for the exception->Result contract
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Boundary tests for the context menu interface.

These verify the exception-rework contract at the interface layer:
``ContextMenuInterface`` never raises and never imports ``ui`` — every public
method translates its collaborators' outcomes (service exceptions, Result
objects, plain booleans) into a typed Result. Fake services are injected
directly so the tests exercise only the interface's translation logic.
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
from womm.exceptions.context import ContextServiceError
from womm.interfaces.context.menu_interface import ContextMenuInterface
from womm.services.context import ContextParametersService
from womm.shared.results.context_results import (
    BackupDataResult,
    BackupFileResult,
    ContextBackupResult,
    ContextEntriesResult,
    ContextRegistryResult,
    ContextRestoreResult,
    ContextSetupResult,
    ContextStatusResult,
    ContextValidationResult,
    ScriptRegistrationResult,
    ScriptUnregistrationResult,
)

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


@pytest.fixture(autouse=True)
def _reset_context_parameters_singleton():
    """Reset the ContextParametersService singleton around each test.

    ContextParametersService.from_flags() builds on a process-wide singleton
    (__new__ always returns the same instance, context_types accumulates
    across calls instead of resetting) — a real, pre-existing bug outside the
    scope of this exception->Result rework. Without this reset, from_flags()
    calls in one test leak context_types into every later test in this file.
    """
    ContextParametersService._instance = None
    ContextParametersService._initialized = False
    yield
    ContextParametersService._instance = None
    ContextParametersService._initialized = False


# ///////////////////////////////////////////////////////////////
# FAKE SERVICES
# ///////////////////////////////////////////////////////////////


class _FakeValidationService:
    """Stand-in for ContextValidationService with a scriptable outcome."""

    def __init__(self, success: bool = True, error: str = ""):
        self._success = success
        self._error = error

    def validate_command_parameters(self, script_path, label, icon):
        return ContextValidationResult(success=self._success, error=self._error)


class _FakeIconManager:
    """Stand-in for ContextIconResolver."""

    def __init__(self, icon_path: str | None = "resolved.ico"):
        self._icon_path = icon_path

    def resolve_icon(self, icon, script_path):
        return self._icon_path


class _FakeRegistryService:
    """Stand-in for ContextRegistryService with scriptable outcomes."""

    def __init__(
        self,
        key_name: str = "demo_key",
        add_outcomes: list[bool | Exception] | None = None,
        remove_result: ContextRegistryResult | None = None,
        remove_error: Exception | None = None,
        list_results: dict[str, ContextRegistryResult] | None = None,
        list_errors: dict[str, Exception] | None = None,
        restore_result: ContextRegistryResult | None = None,
        restore_error: Exception | None = None,
        context_paths: dict[str, str] | None = None,
    ):
        self._key_name = key_name
        self._add_outcomes = list(add_outcomes) if add_outcomes else None
        self._remove_result = (
            remove_result
            if remove_result is not None
            else ContextRegistryResult(success=True)
        )
        self._remove_error = remove_error
        self._list_results = list_results or {}
        self._list_errors = list_errors or {}
        self._restore_result = (
            restore_result
            if restore_result is not None
            else ContextRegistryResult(success=True)
        )
        self._restore_error = restore_error
        self._context_paths = context_paths or {}

    def generate_registry_key_name(self, script_path: str) -> str:
        return self._key_name

    def add_context_menu_entry(self, registry_path, command, mui_verb, icon_path):
        outcome = self._add_outcomes.pop(0) if self._add_outcomes else True
        if isinstance(outcome, Exception):
            raise outcome
        return ContextRegistryResult(success=outcome)

    def remove_context_menu_entry(self, registry_path: str) -> ContextRegistryResult:
        if self._remove_error is not None:
            raise self._remove_error
        return self._remove_result

    def list_context_menu_entries(self, context_type: str) -> ContextRegistryResult:
        if context_type in self._list_errors:
            raise self._list_errors[context_type]
        return self._list_results.get(
            context_type, ContextRegistryResult(success=True, entries=[])
        )

    def restore_registry_entries(self, backup_data) -> ContextRegistryResult:
        if self._restore_error is not None:
            raise self._restore_error
        return self._restore_result

    def get_context_path(self, context_type: str) -> str | None:
        return self._context_paths.get(context_type, f"HKCU\\...\\{context_type}")


class _FakeBackupManager:
    """Stand-in for ContextRegistryInterface (backup file I/O).

    Mirrors the real contract: both methods return a Result and never raise.
    """

    def __init__(
        self,
        create_result: BackupFileResult | None = None,
        load_result: BackupDataResult | None = None,
        backup_dir: Path = Path("backups"),
    ):
        # NB: `or` would discard a failure Result — BaseResult.__bool__ is `success`
        self._create_result = (
            BackupFileResult(success=True, filepath="backup.json")
            if create_result is None
            else create_result
        )
        self._load_result = (
            BackupDataResult(success=True) if load_result is None else load_result
        )
        self._backup_dir = backup_dir

    def create_backup_file(self, entries, custom_filename, add_timestamp):
        return self._create_result

    def load_backup_file(self, backup_file):
        return self._load_result

    def get_backup_directory(self) -> Path:
        return self._backup_dir


def _interface(
    validation: _FakeValidationService | None = None,
    icon: _FakeIconManager | None = None,
    registry: _FakeRegistryService | None = None,
    backup: _FakeBackupManager | None = None,
) -> ContextMenuInterface:
    """Build an interface with the given collaborators faked out."""
    interface = ContextMenuInterface()
    interface._validation_service = validation or _FakeValidationService()
    interface._icon_manager = icon or _FakeIconManager()
    interface._registry_service = registry or _FakeRegistryService()
    interface._backup_manager = backup or _FakeBackupManager()
    return interface


# ///////////////////////////////////////////////////////////////
# TESTS - REGISTER SCRIPT
# ///////////////////////////////////////////////////////////////


class TestRegisterScript:
    """Boundary behaviour of ContextMenuInterface.register_script()."""

    def test_success_returns_registration_result(self):
        interface = _interface()
        context_params = ContextParametersService.from_flags(background=True)

        result = interface.register_script(
            "C:\\tools\\demo.bat", "Demo", None, False, context_params
        )

        assert isinstance(result, ScriptRegistrationResult)
        assert result.success is True
        assert result.registry_key == "demo_key"
        assert result.success_count == 1
        assert result.total_paths == 1

    def test_dry_run_does_not_touch_the_registry(self):
        def _boom(*_args, **_kwargs):
            raise AssertionError("must not write the registry in dry-run mode")

        registry = _FakeRegistryService()
        registry.add_context_menu_entry = _boom
        interface = _interface(registry=registry)
        context_params = ContextParametersService.from_flags(background=True)

        result = interface.register_script(
            "C:\\tools\\demo.bat", "Demo", None, True, context_params
        )

        assert result.success is True
        assert result.dry_run is True

    def test_missing_script_path_is_a_failure_result(self):
        interface = _interface()

        result = interface.register_script("", "Demo")

        assert result.success is False
        assert "Script path" in result.error

    def test_validation_failure_is_translated_to_failure_result(self):
        interface = _interface(
            validation=_FakeValidationService(success=False, error="bad params")
        )

        result = interface.register_script("C:\\tools\\demo.bat", "Demo")

        assert result.success is False
        assert "bad params" in result.error

    def test_partial_registry_failure_is_a_failure_result(self):
        registry = _FakeRegistryService(add_outcomes=[True, False])
        interface = _interface(registry=registry)
        context_params = ContextParametersService.from_flags()  # directory + background

        result = interface.register_script(
            "C:\\tools\\demo.bat", "Demo", None, False, context_params
        )

        assert result.success is False
        assert "1/2" in result.error

    def test_unexpected_registry_error_is_translated_not_reraised(self):
        registry = _FakeRegistryService(
            add_outcomes=[ContextServiceError("registry_entry", "boom")]
        )
        interface = _interface(registry=registry)
        context_params = ContextParametersService.from_flags(background=True)

        result = interface.register_script(
            "C:\\tools\\demo.bat", "Demo", None, False, context_params
        )

        assert result.success is False
        assert "0/1" in result.error


# ///////////////////////////////////////////////////////////////
# TESTS - UNREGISTER SCRIPT
# ///////////////////////////////////////////////////////////////


class TestUnregisterScript:
    """Boundary behaviour of ContextMenuInterface.unregister_script()."""

    def test_success_when_removed_from_any_context_type(self):
        interface = _interface(
            registry=_FakeRegistryService(
                remove_result=ContextRegistryResult(success=True)
            )
        )

        result = interface.unregister_script("demo_key")

        assert isinstance(result, ScriptUnregistrationResult)
        assert result.success is True
        assert result.key_name == "demo_key"

    def test_dry_run_reports_success_without_removing(self):
        interface = _interface(
            registry=_FakeRegistryService(remove_error=AssertionError("must not run"))
        )

        result = interface.unregister_script("demo_key", dry_run=True)

        assert result.success is True
        assert result.dry_run is True

    def test_missing_key_name_is_a_failure_result(self):
        interface = _interface()

        result = interface.unregister_script("")

        assert result.success is False
        assert "Registry key name" in result.error

    def test_not_found_in_any_type_is_a_failure_result(self):
        interface = _interface(
            registry=_FakeRegistryService(
                remove_result=ContextRegistryResult(success=False, error="not found")
            )
        )

        result = interface.unregister_script("demo_key")

        assert result.success is False
        assert result.error == "Entry not found in any context type"
        assert result.not_found_count > 0

    def test_permission_error_is_reported_distinctly(self):
        interface = _interface(
            registry=_FakeRegistryService(
                remove_error=ContextServiceError(
                    "registry_removal", "Access denied [WinError 5]"
                )
            )
        )

        result = interface.unregister_script("demo_key")

        assert result.success is False
        assert "Permission denied" in result.error
        assert result.permission_errors


# ///////////////////////////////////////////////////////////////
# TESTS - LIST ENTRIES / STATUS
# ///////////////////////////////////////////////////////////////


class TestListEntriesAndStatus:
    """Boundary behaviour of list_entries() and get_status()."""

    def test_list_entries_aggregates_by_context_type(self):
        interface = _interface(
            registry=_FakeRegistryService(
                list_results={
                    "directory": ContextRegistryResult(
                        success=True, entries=[{"key_name": "a"}]
                    ),
                    "background": ContextRegistryResult(
                        success=True, entries=[{"key_name": "b"}]
                    ),
                }
            )
        )

        result = interface.list_entries()

        assert isinstance(result, ContextEntriesResult)
        assert result.success is True
        assert result.entries["directory"] == [{"key_name": "a"}]
        assert result.entries["background"] == [{"key_name": "b"}]

    def test_list_entries_swallows_per_type_errors(self):
        interface = _interface(
            registry=_FakeRegistryService(
                list_errors={"directory": ContextServiceError("list", "boom")}
            )
        )

        result = interface.list_entries()

        assert result.success is True
        assert result.entries["directory"] == []

    def test_get_status_counts_directory_and_background_only(self):
        interface = _interface(
            registry=_FakeRegistryService(
                list_results={
                    "directory": ContextRegistryResult(
                        success=True, entries=[{"key_name": "a"}, {"key_name": "b"}]
                    ),
                    "background": ContextRegistryResult(
                        success=True, entries=[{"key_name": "c"}]
                    ),
                    "root": ContextRegistryResult(
                        success=True, entries=[{"key_name": "ignored"}]
                    ),
                }
            )
        )

        result = interface.get_status()

        assert isinstance(result, ContextStatusResult)
        assert result.success is True
        assert result.total_entries == 3
        assert result.entries_by_type == {"directory": 2, "background": 1}


# ///////////////////////////////////////////////////////////////
# TESTS - BACKUP / RESTORE
# ///////////////////////////////////////////////////////////////


class TestBackupEntries:
    """Boundary behaviour of ContextMenuInterface.backup_entries()."""

    def test_success_returns_backup_result(self):
        interface = _interface(
            backup=_FakeBackupManager(
                create_result=BackupFileResult(
                    success=True,
                    filepath="backup.json",
                    metadata={"total_entries": 5},
                )
            )
        )

        result = interface.backup_entries("backup.json")

        assert isinstance(result, ContextBackupResult)
        assert result.success is True
        assert result.backup_file == "backup.json"
        assert result.entry_count == 5

    def test_missing_backup_file_is_a_failure_result(self):
        interface = _interface()

        result = interface.backup_entries("")

        assert result.success is False
        assert "Backup file path" in result.error

    def test_backup_manager_error_is_surfaced_not_reraised(self):
        interface = _interface(
            backup=_FakeBackupManager(
                create_result=BackupFileResult(success=False, error="disk full")
            )
        )

        result = interface.backup_entries("backup.json")

        assert result.success is False
        assert "disk full" in result.error

    def test_backup_creation_failure_is_reported(self):
        interface = _interface(
            backup=_FakeBackupManager(
                create_result=BackupFileResult(success=False, error="error detail")
            )
        )

        result = interface.backup_entries("backup.json")

        assert result.success is False
        assert "error detail" in result.error


class TestRestoreEntries:
    """Boundary behaviour of ContextMenuInterface.restore_entries()."""

    def test_success_returns_restore_result(self):
        interface = _interface(
            backup=_FakeBackupManager(
                load_result=BackupDataResult(
                    success=True, data={"metadata": {"total_entries": 4}}
                )
            ),
            registry=_FakeRegistryService(
                restore_result=ContextRegistryResult(success=True)
            ),
        )

        result = interface.restore_entries("backup.json")

        assert isinstance(result, ContextRestoreResult)
        assert result.success is True
        assert result.entry_count == 4

    def test_missing_backup_file_is_a_failure_result(self):
        interface = _interface()

        result = interface.restore_entries("")

        assert result.success is False
        assert "Backup file path" in result.error

    def test_load_failure_is_surfaced_not_reraised(self):
        interface = _interface(
            backup=_FakeBackupManager(
                load_result=BackupDataResult(success=False, error="missing")
            )
        )

        result = interface.restore_entries("backup.json")

        assert result.success is False
        assert "missing" in result.error

    def test_registry_restore_failure_is_reported(self):
        interface = _interface(
            registry=_FakeRegistryService(
                restore_result=ContextRegistryResult(success=False)
            )
        )

        result = interface.restore_entries("backup.json")

        assert result.success is False
        assert result.error == "Registry restoration failed"


# ///////////////////////////////////////////////////////////////
# TESTS - QUICK SETUP
# ///////////////////////////////////////////////////////////////


class TestQuickSetupTools:
    """Boundary behaviour of ContextMenuInterface.quick_setup_tools()."""

    def test_womm_executable_not_found_is_a_failure_result(self, monkeypatch, tmp_path):
        monkeypatch.setattr(
            "womm.interfaces.context.menu_interface.get_womm_executable",
            lambda: tmp_path / "womm.exe",
        )
        interface = _interface()

        result = interface.quick_setup_tools()

        assert isinstance(result, ContextSetupResult)
        assert result.success is False
        assert "executable" in result.error

    def test_location_error_is_translated_not_reraised(self, monkeypatch):
        def _boom():
            raise OSError("cannot resolve path")

        monkeypatch.setattr(
            "womm.interfaces.context.menu_interface.get_womm_executable", _boom
        )
        interface = _interface()

        result = interface.quick_setup_tools()

        assert result.success is False
        assert "cannot resolve path" in result.error

    def test_success_registers_the_womm_cli_tool(self, monkeypatch, tmp_path):
        executable = tmp_path / "womm.exe"
        executable.write_text("entrypoint")
        monkeypatch.setattr(
            "womm.interfaces.context.menu_interface.get_womm_executable",
            lambda: executable,
        )
        interface = _interface()

        result = interface.quick_setup_tools()

        assert isinstance(result, ContextSetupResult)
        assert result.success is True
        assert result.success_count == 1
        assert result.tools_registered == ["WOMM CLI"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
