#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST CONTEXT BACKUP ENTRIES - Backup reading and path mapping
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Unit tests for the collaborators split out of ``ContextMenuInterface``.

``ContextBackupEntriesReader`` owns backup file reading and entry
normalization, ``context_type_from_registry_path`` owns registry path
interpretation, and ``format_entry_display`` owns the menu label.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
from pathlib import Path

# Local imports
from womm.services.context import ContextType, context_type_from_registry_path
from womm.services.context.backup_entries import ContextBackupEntriesReader
from womm.ui.context.menu_display import format_entry_display

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////


def _write_backup(backup_dir: Path, name: str, payload: dict) -> None:
    """Write a backup file with the given payload."""
    (backup_dir / name).write_text(json.dumps(payload), encoding="utf-8")


def _entry(key_name: str, **properties: str) -> dict:
    """Build a minimal backup entry."""
    return {"key_name": key_name, "properties": properties}


# ///////////////////////////////////////////////////////////////
# TESTS - COLLECT ENTRIES
# ///////////////////////////////////////////////////////////////


class TestCollectEntries:
    """Behaviour of ContextBackupEntriesReader.collect_entries()."""

    def test_collects_entries_across_context_types_with_metadata(self, tmp_path):
        _write_backup(
            tmp_path,
            "context_menu_backup_1.json",
            {
                "entries": {
                    "directory": [_entry("alpha")],
                    "background": [_entry("beta")],
                }
            },
        )

        entries = ContextBackupEntriesReader().collect_entries(tmp_path)

        by_key = {entry["key_name"]: entry for entry in entries}
        assert set(by_key) == {"alpha", "beta"}
        assert by_key["alpha"]["_context_type"] == "directory"
        assert by_key["beta"]["_source_backup"] == "context_menu_backup_1.json"

    def test_first_occurrence_of_a_key_wins(self, tmp_path):
        _write_backup(
            tmp_path,
            "context_menu_backup_1.json",
            {"entries": {"directory": [_entry("alpha", MUIVerb="first")]}},
        )
        _write_backup(
            tmp_path,
            "context_menu_backup_2.json",
            {"entries": {"directory": [_entry("alpha", MUIVerb="second")]}},
        )

        entries = ContextBackupEntriesReader().collect_entries(tmp_path)

        assert len(entries) == 1
        assert entries[0]["properties"]["MUIVerb"] == "first"

    def test_legacy_list_format_is_read_as_directory_entries(self, tmp_path):
        _write_backup(
            tmp_path, "context_menu_backup_1.json", {"entries": [_entry("alpha")]}
        )

        entries = ContextBackupEntriesReader().collect_entries(tmp_path)

        assert entries[0]["_context_type"] == "directory"

    def test_unreadable_file_is_skipped_not_fatal(self, tmp_path):
        (tmp_path / "context_menu_backup_broken.json").write_text(
            "{not json", encoding="utf-8"
        )
        _write_backup(
            tmp_path,
            "context_menu_backup_ok.json",
            {"entries": {"directory": [_entry("alpha")]}},
        )

        entries = ContextBackupEntriesReader().collect_entries(tmp_path)

        assert [entry["key_name"] for entry in entries] == ["alpha"]

    def test_unrelated_files_are_ignored(self, tmp_path):
        _write_backup(tmp_path, "other.json", {"entries": {"directory": [_entry("a")]}})

        assert ContextBackupEntriesReader().collect_entries(tmp_path) == []


# ///////////////////////////////////////////////////////////////
# TESTS - FILTER AND PARSE
# ///////////////////////////////////////////////////////////////


class TestFilterAndParse:
    """Behaviour of filter_available() and extract_script_path()."""

    def test_installed_and_keyless_entries_are_filtered_out(self):
        all_entries = [_entry("alpha"), _entry("beta"), {"properties": {}}]

        available = ContextBackupEntriesReader.filter_available(all_entries, {"alpha"})

        assert [entry["key_name"] for entry in available] == ["beta"]

    def test_extracts_the_quoted_path_when_it_exists(self, tmp_path):
        script = tmp_path / "demo.bat"
        script.write_text("@echo off", encoding="utf-8")

        extracted = ContextBackupEntriesReader.extract_script_path(f'"{script}" "%1"')

        assert extracted == str(script)

    def test_missing_or_unquoted_path_yields_none(self, tmp_path):
        assert ContextBackupEntriesReader.extract_script_path("womm.exe %1") is None
        assert (
            ContextBackupEntriesReader.extract_script_path(
                f'"{tmp_path / "gone.bat"}" "%1"'
            )
            is None
        )


# ///////////////////////////////////////////////////////////////
# TESTS - REGISTRY PATH MAPPING
# ///////////////////////////////////////////////////////////////


class TestContextTypeFromRegistryPath:
    """Behaviour of context_type_from_registry_path()."""

    def test_maps_each_known_pattern(self):
        assert (
            context_type_from_registry_path("Software\\Classes\\Directory\\shell")
            == ContextType.DIRECTORY
        )
        assert (
            context_type_from_registry_path(
                "Software\\Classes\\Directory\\background\\shell"
            )
            == ContextType.BACKGROUND
        )
        assert (
            context_type_from_registry_path("Software\\Classes\\Drive\\shell")
            == ContextType.ROOT
        )
        assert (
            context_type_from_registry_path("Software\\Classes\\*\\shell")
            == ContextType.FILE
        )

    def test_unknown_path_falls_back_to_directory(self):
        assert context_type_from_registry_path("nowhere") == ContextType.DIRECTORY


# ///////////////////////////////////////////////////////////////
# TESTS - DISPLAY FORMATTING
# ///////////////////////////////////////////////////////////////


class TestFormatEntryDisplay:
    """Behaviour of the UI-level entry label."""

    def test_uses_muiverb_and_executable_name(self):
        entry = _entry("demo_key", MUIVerb="Demo", Command='"C:\\tools\\womm.exe" "%1"')

        assert format_entry_display(entry) == "Demo (womm.exe) [key: demo_key]"

    def test_falls_back_to_key_name(self):
        assert format_entry_display(_entry("demo_key")) == "demo_key [key: demo_key]"
