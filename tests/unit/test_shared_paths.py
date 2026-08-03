#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SHARED PATHS - Data/code path contract
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for ``womm.shared.paths``.

This module is the single authority on *where things live*. It answers two
questions that the legacy self-installer used to conflate:
where the mutable user data lives (``~/.womm``, overridable via
``$WOMM_HOME``) and where the immutable packaged assets live (the package
itself, read through ``importlib.resources``).

Every test isolates ``$WOMM_HOME`` onto ``tmp_path`` — no test may touch the
real ``~/.womm``.
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
from womm.shared.paths import (
    WOMM_HOME_ENV,
    config_file,
    logs_dir,
    packaged_assets,
    path_backups_dir,
    registry_backups_dir,
    state_file,
    user_templates_dir,
    womm_data_dir,
    womm_data_path,
)

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def womm_home(tmp_path, monkeypatch):
    """Point ``$WOMM_HOME`` at an isolated directory for the test."""
    home = tmp_path / "womm-home"
    monkeypatch.setenv(WOMM_HOME_ENV, str(home))
    return home


# ///////////////////////////////////////////////////////////////
# TESTS - DATA ROOT
# ///////////////////////////////////////////////////////////////


def test_data_dir_defaults_to_dot_womm_in_home(tmp_path, monkeypatch):
    monkeypatch.delenv(WOMM_HOME_ENV, raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda _cls: tmp_path))

    assert womm_data_dir() == tmp_path / ".womm"


def test_data_dir_honors_womm_home_override(womm_home):
    assert womm_data_dir() == womm_home


def test_data_path_does_not_create_the_data_directory(womm_home):
    assert womm_data_path() == womm_home
    assert not womm_home.exists()


def test_data_dir_is_created_on_access(womm_home):
    assert not womm_home.exists()

    result = womm_data_dir()

    assert result.is_dir()


def test_data_dir_is_idempotent_when_already_present(womm_home):
    womm_data_dir()
    marker = womm_home / "keep.txt"
    marker.write_text("data", encoding="utf-8")

    womm_data_dir()

    assert marker.read_text(encoding="utf-8") == "data"


def test_blank_womm_home_falls_back_to_default(tmp_path, monkeypatch):
    monkeypatch.setenv(WOMM_HOME_ENV, "   ")
    monkeypatch.setattr(Path, "home", classmethod(lambda _cls: tmp_path))

    assert womm_data_dir() == tmp_path / ".womm"


def test_womm_home_expands_user_and_resolves(tmp_path, monkeypatch):
    """``~`` in the override is expanded.

    ``Path.expanduser()`` reads the environment (``$USERPROFILE`` on Windows,
    ``$HOME`` elsewhere), *not* ``Path.home()`` — patching the latter would
    let the test write into the developer's real home directory.
    """
    for var in ("USERPROFILE", "HOME"):
        monkeypatch.setenv(var, str(tmp_path))
    monkeypatch.setenv(WOMM_HOME_ENV, "~/custom-womm")

    assert womm_data_dir() == (tmp_path / "custom-womm").resolve()


# ///////////////////////////////////////////////////////////////
# TESTS - SUBDIRECTORIES
# ///////////////////////////////////////////////////////////////


@pytest.mark.parametrize(
    ("accessor", "relative"),
    [
        (logs_dir, "logs"),
        (user_templates_dir, "templates"),
        (path_backups_dir, "backups/path"),
        (registry_backups_dir, "backups/registry"),
    ],
)
def test_subdirectories_resolve_under_data_dir_and_are_created(
    womm_home, accessor, relative
):
    result = accessor()

    assert result == womm_home.joinpath(*relative.split("/"))
    assert result.is_dir()


@pytest.mark.usefixtures("womm_home")
def test_path_and_registry_backups_are_distinct():
    assert path_backups_dir() != registry_backups_dir()


# ///////////////////////////////////////////////////////////////
# TESTS - FILES
# ///////////////////////////////////////////////////////////////


@pytest.mark.parametrize(
    ("accessor", "filename"),
    [
        (config_file, "config.toml"),
        (state_file, "state.json"),
    ],
)
def test_files_resolve_under_data_dir_without_being_created(
    womm_home, accessor, filename
):
    result = accessor()

    assert result == womm_home / filename
    assert result.parent.is_dir()
    assert not result.exists()


# ///////////////////////////////////////////////////////////////
# TESTS - PACKAGED ASSETS
# ///////////////////////////////////////////////////////////////


def test_packaged_assets_points_at_the_shipped_assets_tree():
    assets = packaged_assets()

    assert assets.is_dir()
    assert {entry.name for entry in assets.iterdir()} >= {"languages"}


def test_packaged_assets_is_independent_of_womm_home(womm_home):
    """Code location must never follow the data location."""
    assets = packaged_assets()

    assert not str(assets).startswith(str(womm_home))


def test_packaged_copier_official_contains_language_dirs():
    from womm.shared.paths import packaged_copier_official

    official = packaged_copier_official()
    names = {entry.name for entry in official.iterdir()}
    assert "python" in names


def test_template_catalog_file_is_under_womm_home(tmp_path, monkeypatch):
    monkeypatch.setenv("WOMM_HOME", str(tmp_path))
    from womm.shared.paths import template_catalog_file

    catalog = template_catalog_file()
    assert catalog.parent == tmp_path / "templates"
    assert catalog.name == "catalog.json"
    assert not catalog.exists()


def test_packaged_copier_meta_exists():
    from womm.shared.paths import packaged_copier_meta

    assert packaged_copier_meta().name == "meta"
