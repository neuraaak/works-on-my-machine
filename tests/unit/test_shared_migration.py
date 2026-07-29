#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SHARED MIGRATION - Legacy data layout migration
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for ``womm.shared.migration``.

The data directory changed shape: dot-prefixed directories written by the
old self-installer (``.logs``, ``.templates``, ``.backup``) become plain
ones (``logs``, ``templates``, ``backups/{path,registry}``). Existing users
must keep their templates and backups across that change.

The migration is destructive by nature (it moves files), so these tests pin
the safety properties as tightly as the happy path: never overwrite, never
delete user data, never run twice.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json

# Third-party imports
import pytest

# Local imports
from womm.shared.migration import DATA_VERSION, migrate_legacy_data_layout
from womm.shared.paths import (
    WOMM_HOME_ENV,
    logs_dir,
    path_backups_dir,
    registry_backups_dir,
    state_file,
    user_templates_dir,
    womm_data_dir,
)

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def legacy_home(tmp_path, monkeypatch):
    """A data directory in the pre-migration shape."""
    home = tmp_path / "womm-home"
    monkeypatch.setenv(WOMM_HOME_ENV, str(home))

    (home / ".logs").mkdir(parents=True)
    (home / ".logs" / "womm.log").write_text("old log", encoding="utf-8")

    (home / ".templates" / "demo").mkdir(parents=True)
    (home / ".templates" / "demo" / "template.json").write_text(
        '{"name": "demo"}', encoding="utf-8"
    )

    (home / ".backup").mkdir(parents=True)
    (home / ".backup" / ".path.json").write_text("{}", encoding="utf-8")
    (home / ".backup" / ".path_20251005_050735.json").write_text("{}", encoding="utf-8")
    (home / ".backup" / "context_menu").mkdir()
    (home / ".backup" / "context_menu" / "context_menu_backup_1.json").write_text(
        "{}", encoding="utf-8"
    )

    return home


# ///////////////////////////////////////////////////////////////
# TESTS - HAPPY PATH
# ///////////////////////////////////////////////////////////////


def test_templates_are_preserved(legacy_home):
    """The regression that matters most: users keep their templates."""
    migrate_legacy_data_layout()

    migrated = user_templates_dir() / "demo" / "template.json"
    assert migrated.read_text(encoding="utf-8") == '{"name": "demo"}'
    assert not (legacy_home / ".templates" / "demo").exists()


def test_logs_are_moved(legacy_home):
    migrate_legacy_data_layout()

    assert (logs_dir() / "womm.log").read_text(encoding="utf-8") == "old log"
    assert not (legacy_home / ".logs" / "womm.log").exists()


def test_path_backups_are_moved(legacy_home):  # noqa: ARG001
    migrate_legacy_data_layout()

    moved = {entry.name for entry in path_backups_dir().iterdir()}
    assert moved == {".path.json", ".path_20251005_050735.json"}


def test_registry_backups_are_moved(legacy_home):  # noqa: ARG001
    migrate_legacy_data_layout()

    moved = {entry.name for entry in registry_backups_dir().iterdir()}
    assert moved == {"context_menu_backup_1.json"}


def test_report_lists_what_moved(legacy_home):  # noqa: ARG001
    report = migrate_legacy_data_layout()

    assert report.performed is True
    assert report.moved_count == 5


# ///////////////////////////////////////////////////////////////
# TESTS - SAFETY
# ///////////////////////////////////////////////////////////////


def test_existing_destination_is_never_overwritten(legacy_home):
    """A file already present in the new layout wins; nothing is clobbered."""
    user_templates_dir().joinpath("demo").mkdir(parents=True)
    kept = user_templates_dir() / "demo" / "template.json"
    kept.write_text('{"name": "already-here"}', encoding="utf-8")

    report = migrate_legacy_data_layout()

    assert kept.read_text(encoding="utf-8") == '{"name": "already-here"}'
    assert (legacy_home / ".templates" / "demo" / "template.json").exists()
    assert report.skipped_count == 1


def test_migration_runs_only_once(legacy_home):
    """A second call is a no-op, even if legacy directories reappear."""
    migrate_legacy_data_layout()
    (legacy_home / ".logs").mkdir(exist_ok=True)
    (legacy_home / ".logs" / "late.log").write_text("late", encoding="utf-8")

    report = migrate_legacy_data_layout()

    assert report.performed is False
    assert (legacy_home / ".logs" / "late.log").exists()


def test_state_file_records_the_data_version(legacy_home):  # noqa: ARG001
    migrate_legacy_data_layout()

    state = json.loads(state_file().read_text(encoding="utf-8"))
    assert state["data_version"] == DATA_VERSION


def test_nothing_to_migrate_is_not_an_error(tmp_path, monkeypatch):
    """A fresh install has no legacy layout; the migration still marks state."""
    monkeypatch.setenv(WOMM_HOME_ENV, str(tmp_path / "fresh"))

    report = migrate_legacy_data_layout()

    assert report.performed is True
    assert report.moved_count == 0
    assert state_file().exists()


def test_code_residue_is_left_untouched(legacy_home):
    """Legacy code in ``~/.womm`` is out of scope: reported, never deleted."""
    (legacy_home / "womm").mkdir()
    (legacy_home / "womm" / "__main__.py").write_text("", encoding="utf-8")
    (legacy_home / "womm.bat").write_text("", encoding="utf-8")

    report = migrate_legacy_data_layout()

    assert (legacy_home / "womm" / "__main__.py").exists()
    assert (legacy_home / "womm.bat").exists()
    assert report.code_residue is True


def test_migration_never_raises_on_unreadable_source(legacy_home, monkeypatch):
    """A failed move degrades into a report entry, not a crash at startup."""

    def _boom(*_args, **_kwargs):
        raise OSError("device busy")

    monkeypatch.setattr("womm.shared.migration.shutil.move", _boom)

    report = migrate_legacy_data_layout()

    assert report.failed_count > 0
    assert womm_data_dir() == legacy_home
    assert not state_file().exists()


def test_migration_never_raises_when_data_directory_is_unavailable(monkeypatch):
    def _boom():
        raise OSError("access denied")

    monkeypatch.setattr("womm.shared.migration._already_migrated", _boom)

    report = migrate_legacy_data_layout()

    assert report.performed is True
    assert report.failed_count == 1
    assert report.errors == ["access denied"]
