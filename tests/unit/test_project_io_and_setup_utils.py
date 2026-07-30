"""Unit tests for project asset and environment utility functions."""

from __future__ import annotations

from pathlib import Path

import pytest

from womm.services.project import env_utils
from womm.utils.project import asset_utils


def test_copy_asset_file_and_directory_honor_overwrite_and_exclusions(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "keep.txt").write_text("new")
    (source / "skip.pyc").write_text("skip")
    target = tmp_path / "target"
    copied = asset_utils.copy_assets_directory(
        source, target, exclude_patterns=["*.pyc"]
    )
    assert copied == [target / "keep.txt"]
    assert (target / "keep.txt").read_text() == "new"
    (target / "keep.txt").write_text("old")
    asset_utils.copy_asset_file(source / "keep.txt", target / "keep.txt")
    assert (target / "keep.txt").read_text() == "old"
    asset_utils.copy_asset_file(
        source / "keep.txt", target / "keep.txt", overwrite=True
    )
    assert (target / "keep.txt").read_text() == "new"


def test_asset_path_and_copy_type_handle_validation_and_missing_source(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        asset_utils, "get_assets_module_path", lambda: tmp_path / "assets"
    )
    with pytest.raises(ValueError):
        asset_utils.get_assets_path("unknown")
    monkeypatch.setattr(
        asset_utils, "get_assets_path", lambda *_args: tmp_path / "missing"
    )
    assert (
        asset_utils.copy_asset_type("python", "basic", "templates", tmp_path / "out")
        == []
    )


def test_environment_helpers_find_executables_and_npm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    venv = tmp_path / "venv"
    executable = venv / "bin" / "pip"
    executable.parent.mkdir(parents=True)
    executable.touch()
    assert env_utils.find_pip_executable(venv) == executable
    monkeypatch.setattr(
        env_utils.shutil, "which", lambda name: "/bin/npm" if name == "npm" else None
    )
    assert env_utils.check_npm_available()
