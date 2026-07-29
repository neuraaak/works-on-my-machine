#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST CONTEXT REGISTRY INTERFACE - Boundary tests for the Result contract
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Boundary tests for the context backup and script-detection interfaces.

These verify the exception-rework contract: ``ContextRegistryInterface`` and
``ContextScriptDetectorInterface`` never raise — every public method returns a
typed Result, including on missing files, unreadable directories and malformed
JSON. Backups are written to ``tmp_path`` so no real WOMM install is touched.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
from datetime import datetime, timedelta
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.interfaces.context.registry_interface import ContextRegistryInterface
from womm.interfaces.context.script_detector_interface import (
    ContextScriptDetectorInterface,
    ScriptType,
)
from womm.shared.paths import WOMM_HOME_ENV, registry_backups_dir
from womm.shared.results import (
    BackupCleanupResult,
    BackupDataResult,
    BackupFileListResult,
    BackupFileResult,
    ScriptInfoResult,
)

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////

VALID_ENTRIES = {
    "directory": [{"key_name": "demo", "display_name": "Demo"}],
    "background": [],
    "file": [],
    "files": [],
    "root": [],
}


@pytest.fixture
def manager(tmp_path):
    """A backup manager rooted at a throwaway directory."""
    interface = ContextRegistryInterface()
    interface.backup_dir = tmp_path
    return interface


# ///////////////////////////////////////////////////////////////
# BACKUP DIRECTORY LOCATION
# ///////////////////////////////////////////////////////////////


def test_backup_directory_resolves_under_the_data_dir(tmp_path, monkeypatch):
    """Registry backups are data: they follow ``~/.womm``, not the code."""
    monkeypatch.setenv(WOMM_HOME_ENV, str(tmp_path))

    directory = ContextRegistryInterface().get_backup_directory()

    assert directory == tmp_path / "backups" / "registry"
    assert directory == registry_backups_dir()
    assert directory.is_dir()


def test_backup_directory_no_longer_depends_on_an_existing_install(
    tmp_path, monkeypatch
):
    """The old code fell back to the CWD when ``~/.womm`` was absent.

    The data directory is now created on demand, so a fresh machine gets a
    real backup location instead of scattering backups into whatever
    directory the user happened to run womm from.
    """
    fresh = tmp_path / "never-created"
    monkeypatch.setenv(WOMM_HOME_ENV, str(fresh))

    directory = ContextRegistryInterface().get_backup_directory()

    assert directory != Path(".")
    assert directory.is_dir()


def _write_backup(directory, name, entries=None, metadata=None):
    """Write a well-formed backup file and return its path."""
    payload = {
        "metadata": metadata
        if metadata is not None
        else {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "platform": "Windows",
            "total_entries": 1,
            "context_types": ["directory"],
        },
        "entries": entries if entries is not None else VALID_ENTRIES,
    }
    path = directory / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# ///////////////////////////////////////////////////////////////
# TESTS - CREATE BACKUP
# ///////////////////////////////////////////////////////////////


class TestCreateBackupFile:
    """Boundary behaviour of ContextRegistryInterface.create_backup_file()."""

    def test_success_returns_result_and_writes_the_file(self, manager, tmp_path):
        result = manager.create_backup_file(VALID_ENTRIES, "demo", add_timestamp=False)

        assert isinstance(result, BackupFileResult)
        assert result.success is True
        assert (tmp_path / "demo.json").exists()
        assert (result.metadata or {})["total_entries"] == 1

    def test_non_dict_entries_is_a_failure_result_not_a_raise(self, manager):
        result = manager.create_backup_file(["not", "a", "dict"])  # type: ignore[arg-type]

        assert result.success is False
        assert "must be a dictionary" in result.error

    def test_unwritable_target_is_a_failure_result(self, manager, tmp_path):
        # A directory where the backup file should go makes open() fail
        (tmp_path / "blocked.json").mkdir()

        result = manager.create_backup_file(
            VALID_ENTRIES, "blocked", add_timestamp=False
        )

        assert result.success is False
        assert "Failed to write backup file" in result.error


# ///////////////////////////////////////////////////////////////
# TESTS - LOAD BACKUP
# ///////////////////////////////////////////////////////////////


class TestLoadBackupFile:
    """Boundary behaviour of ContextRegistryInterface.load_backup_file()."""

    def test_success_returns_the_parsed_payload(self, manager, tmp_path):
        path = _write_backup(tmp_path, "context_menu_backup_1.json")

        result = manager.load_backup_file(str(path))

        assert isinstance(result, BackupDataResult)
        assert result.success is True
        assert (result.data or {})["entries"]["directory"][0]["key_name"] == "demo"

    def test_empty_filepath_is_a_failure_result(self, manager):
        result = manager.load_backup_file("")

        assert result.success is False
        assert "cannot be None or empty" in result.error

    def test_missing_file_is_a_failure_result_not_a_raise(self, manager, tmp_path):
        result = manager.load_backup_file(str(tmp_path / "nope.json"))

        assert result.success is False
        assert "not found" in result.error

    def test_malformed_json_is_a_failure_result_not_a_raise(self, manager, tmp_path):
        path = tmp_path / "broken.json"
        path.write_text("{ not json", encoding="utf-8")

        result = manager.load_backup_file(str(path))

        assert result.success is False
        assert "Could not read backup file" in result.error

    def test_schema_violation_is_a_failure_result_not_a_raise(self, manager, tmp_path):
        path = tmp_path / "incomplete.json"
        path.write_text(json.dumps({"metadata": {}}), encoding="utf-8")

        result = manager.load_backup_file(str(path))

        assert result.success is False
        assert "Invalid backup file" in result.error


# ///////////////////////////////////////////////////////////////
# TESTS - LIST AND CLEANUP
# ///////////////////////////////////////////////////////////////


class TestListBackupFiles:
    """Boundary behaviour of ContextRegistryInterface.list_backup_files()."""

    def test_empty_directory_is_a_successful_empty_listing(self, manager):
        result = manager.list_backup_files()

        assert isinstance(result, BackupFileListResult)
        assert result.success is True
        assert result.backups == []

    def test_unreadable_metadata_still_lists_the_file(self, manager, tmp_path):
        """A corrupt backup is reported, not silently dropped."""
        (tmp_path / "context_menu_backup_bad.json").write_text(
            "{ not json", encoding="utf-8"
        )

        result = manager.list_backup_files(include_metadata=True)

        assert result.success is True
        assert len(result.backups or []) == 1
        assert (result.backups or [])[0].entry_count == 0
        assert (result.backups or [])[0].backup_version == "unknown"


class TestCleanupOldBackups:
    """Boundary behaviour of ContextRegistryInterface.cleanup_old_backups()."""

    def test_invalid_max_files_is_a_failure_result_not_a_raise(self, manager):
        result = manager.cleanup_old_backups(max_files=-1)

        assert isinstance(result, BackupCleanupResult)
        assert result.success is False
        assert "max_files" in result.error

    def test_invalid_retention_days_is_a_failure_result_not_a_raise(self, manager):
        result = manager.cleanup_old_backups(retention_days=-5)

        assert result.success is False
        assert "retention_days" in result.error

    def test_expired_backups_are_deleted(self, manager, tmp_path):
        path = _write_backup(tmp_path, "context_menu_backup_old.json")
        stale = (datetime.now() - timedelta(days=90)).timestamp()
        import os

        os.utime(path, (stale, stale))

        result = manager.cleanup_old_backups(retention_days=30)

        assert result.success is True
        assert result.deleted_count == 1
        assert not path.exists()

    def test_recent_backups_are_kept(self, manager, tmp_path):
        path = _write_backup(tmp_path, "context_menu_backup_new.json")

        result = manager.cleanup_old_backups(retention_days=30)

        assert result.success is True
        assert result.kept_count == 1
        assert path.exists()


# ///////////////////////////////////////////////////////////////
# TESTS - COPY AND MERGE
# ///////////////////////////////////////////////////////////////


class TestCopyAndMerge:
    """Boundary behaviour of the copy and merge operations."""

    def test_copy_missing_source_is_a_failure_result(self, manager, tmp_path):
        result = manager.create_backup_copy(
            str(tmp_path / "nope.json"), str(tmp_path / "dest.json")
        )

        assert result.success is False
        assert "Source file not found" in result.error

    def test_copy_empty_paths_are_failure_results(self, manager):
        assert manager.create_backup_copy("", "dest.json").success is False
        assert manager.create_backup_copy("src.json", "").success is False

    def test_merge_empty_list_is_a_failure_result(self, manager):
        result = manager.merge_backups([], "out")

        assert result.success is False
        assert "cannot be empty" in result.error

    def test_merge_propagates_a_bad_source_as_failure(self, manager, tmp_path):
        result = manager.merge_backups([str(tmp_path / "nope.json")], "out")

        assert result.success is False
        assert "Could not merge" in result.error

    def test_merge_deduplicates_by_key_name(self, manager, tmp_path):
        a = _write_backup(tmp_path, "context_menu_backup_a.json")
        b = _write_backup(tmp_path, "context_menu_backup_b.json")

        result = manager.merge_backups([str(a), str(b)], "merged")

        assert result.success is True
        merged = json.loads((tmp_path / "merged.json").read_text(encoding="utf-8"))
        assert len(merged["entries"]["directory"]) == 1


# ///////////////////////////////////////////////////////////////
# TESTS - SCRIPT DETECTOR
# ///////////////////////////////////////////////////////////////


class TestScriptDetector:
    """Boundary behaviour of ContextScriptDetectorInterface."""

    def test_get_script_info_returns_a_typed_result(self):
        result = ContextScriptDetectorInterface.get_script_info("demo.py")

        assert isinstance(result, ScriptInfoResult)
        assert result.success is True
        assert result.script_type == ScriptType.PYTHON
        assert result.extension == ".py"
        assert result.command

    def test_empty_path_is_a_failure_result_not_a_raise(self):
        result = ContextScriptDetectorInterface.get_script_info("")

        assert result.success is False
        assert "cannot be None or empty" in result.error

    def test_unknown_extension_is_still_a_success(self):
        """An unrecognized script is a finding, not a failure of detection."""
        result = ContextScriptDetectorInterface.get_script_info("notes.xyz")

        assert result.success is True
        assert result.script_type == ScriptType.UNKNOWN

    def test_lookup_helpers_are_total_functions(self):
        """The helpers must not raise on empty or unknown input."""
        assert ContextScriptDetectorInterface.detect_type("") == ScriptType.UNKNOWN
        assert ContextScriptDetectorInterface.get_default_icon("nope") is None
        assert ContextScriptDetectorInterface.get_context_params("nope") == "%V"
