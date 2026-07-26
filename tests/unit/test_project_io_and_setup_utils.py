"""Unit tests for project asset and WOMM setup utility functions."""

from __future__ import annotations

from pathlib import Path

import pytest

from womm.utils.project import asset_utils, env_utils
from womm.utils.womm_setup import common_utils, uninstaller_utils


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


def test_uninstaller_scans_and_verifies_paths(tmp_path: Path) -> None:
    target = tmp_path / "install"
    (target / "nested").mkdir(parents=True)
    (target / "nested" / "file.txt").touch()
    assert uninstaller_utils.get_files_to_remove(target) == [
        str(Path("nested") / "file.txt"),
        "nested/",
    ]
    with pytest.raises(FileExistsError):
        uninstaller_utils.verify_directory_removed(target)
    missing = tmp_path / "removed"
    assert uninstaller_utils.verify_files_removed(missing)["success"] is True


def test_valid_womm_installation_requires_package_and_proof(tmp_path: Path) -> None:
    root = tmp_path / "install"
    package = root / "womm"
    package.mkdir(parents=True)
    (package / "__main__.py").touch()
    assert not common_utils.is_valid_womm_installation(root)
    (package / ".proof").touch()
    assert common_utils.is_valid_womm_installation(root)
