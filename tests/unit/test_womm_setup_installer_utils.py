#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST WOMM SETUP INSTALLER UTILS - Installation utilities coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for WOMM installation utilities."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.utils.womm_setup import installer_utils

# ///////////////////////////////////////////////////////////////
# SHOULD EXCLUDE FILE
# ///////////////////////////////////////////////////////////////


def test_should_exclude_file_rejects_none_paths(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        installer_utils.should_exclude_file(None, tmp_path)


def test_should_exclude_file_package_mode_never_excludes(tmp_path: Path) -> None:
    source = tmp_path / "womm"
    source.mkdir()
    (source / "anything.py").write_text("x")

    assert installer_utils.should_exclude_file(source / "anything.py", source) is False


# ///////////////////////////////////////////////////////////////
# PYPROJECT.TOML PATTERNS (DEV MODE)
# ///////////////////////////////////////////////////////////////


def test_check_pyproject_patterns_uses_setuptools_exclude(tmp_path: Path) -> None:
    source = tmp_path / "womm"
    source.mkdir()
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.setuptools.packages.find]\nexclude = ['tests*']\n")

    assert installer_utils.check_pyproject_patterns(
        source / "tests_helper.py", source, pyproject
    )
    assert not installer_utils.check_pyproject_patterns(
        source / "main.py", source, pyproject
    )


def test_check_pyproject_patterns_uses_womm_additional_exclude(
    tmp_path: Path,
) -> None:
    source = tmp_path / "womm"
    source.mkdir()
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "[tool.womm.installation]\nadditional-exclude = ['secret.txt']\n"
    )

    assert installer_utils.check_pyproject_patterns(
        source / "secret.txt", source, pyproject
    )


def test_check_pyproject_patterns_falls_back_when_file_missing(
    tmp_path: Path,
) -> None:
    source = tmp_path / "womm"
    source.mkdir()
    (source / "module.pyc").write_text("x")

    assert installer_utils.check_pyproject_patterns(
        source / "module.pyc", source, tmp_path / "missing-pyproject.toml"
    )


def test_check_pyproject_patterns_falls_back_on_invalid_toml(
    tmp_path: Path,
) -> None:
    source = tmp_path / "womm"
    source.mkdir()
    (source / "module.pyc").write_text("x")
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("not valid toml [[[")

    assert installer_utils.check_pyproject_patterns(
        source / "module.pyc", source, pyproject
    )


def test_should_exclude_file_dev_mode_delegates_to_pyproject(
    tmp_path: Path,
) -> None:
    source = tmp_path / "womm"
    source.mkdir()
    (tmp_path / "pyproject.toml").write_text(
        "[tool.setuptools.packages.find]\nexclude = ['ignored.py']\n"
    )

    assert installer_utils.should_exclude_file(source / "ignored.py", source) is True
    assert installer_utils.should_exclude_file(source / "kept.py", source) is False


# ///////////////////////////////////////////////////////////////
# DEFAULT PATTERNS
# ///////////////////////////////////////////////////////////////


def test_check_default_patterns_matches_wildcard_suffix(tmp_path: Path) -> None:
    (tmp_path / "module.pyc").write_text("x")

    assert installer_utils.check_default_patterns(tmp_path / "module.pyc", tmp_path)


def test_check_default_patterns_matches_wildcard_prefix(tmp_path: Path) -> None:
    (tmp_path / "test_module.py").write_text("x")

    assert installer_utils.check_default_patterns(tmp_path / "test_module.py", tmp_path)


def test_check_default_patterns_excludes_only_root_setup_py(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()

    assert installer_utils.check_default_patterns(tmp_path / "setup.py", tmp_path)
    assert not installer_utils.check_default_patterns(sub / "setup.py", tmp_path)


def test_check_default_patterns_matches_substring_pattern(tmp_path: Path) -> None:
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "pkg.js").write_text("x")

    assert installer_utils.check_default_patterns(node_modules / "pkg.js", tmp_path)


def test_check_default_patterns_keeps_regular_source_file(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("x")

    assert not installer_utils.check_default_patterns(tmp_path / "main.py", tmp_path)


# ///////////////////////////////////////////////////////////////
# GET FILES TO COPY
# ///////////////////////////////////////////////////////////////


def test_get_files_to_copy_raises_when_source_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Source path does not exist"):
        installer_utils.get_files_to_copy(tmp_path / "missing")


def test_get_files_to_copy_skips_files_that_error_during_processing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "womm"
    source.mkdir()
    (source / "ok.py").write_text("x")
    (source / "broken.py").write_text("x")

    def fake_should_exclude(file_path: Path, _source_path: Path) -> bool:
        if file_path.name == "broken.py":
            raise OSError("boom")
        return False

    monkeypatch.setattr(installer_utils, "should_exclude_file", fake_should_exclude)

    files = installer_utils.get_files_to_copy(source)

    assert files == ["ok.py"]


# ///////////////////////////////////////////////////////////////
# CREATE WOMM EXECUTABLE
# ///////////////////////////////////////////////////////////////


def test_create_womm_executable_rejects_none_target() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        installer_utils.create_womm_executable(None)


def test_create_womm_executable_raises_when_womm_py_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="womm.py not found"):
        installer_utils.create_womm_executable(tmp_path)


def test_create_womm_executable_raises_when_launcher_missing(
    tmp_path: Path,
) -> None:
    (tmp_path / "womm.py").write_text("print('hi')")

    with pytest.raises(FileNotFoundError, match="not found in target directory"):
        installer_utils.create_womm_executable(tmp_path)


def test_create_womm_executable_succeeds_on_windows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "womm.py").write_text("print('hi')")
    (tmp_path / "womm.bat").write_text("@echo off")
    monkeypatch.setattr(installer_utils.platform, "system", lambda: "Windows")

    result = installer_utils.create_womm_executable(tmp_path)

    assert result["success"] is True
    assert result["executable_path"] == str(tmp_path / "womm.bat")
    assert result["platform"] == "Windows"


def test_create_womm_executable_succeeds_on_unix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "womm.py").write_text("print('hi')")
    (tmp_path / "womm").write_text("#!/bin/sh")
    monkeypatch.setattr(installer_utils.platform, "system", lambda: "Linux")

    result = installer_utils.create_womm_executable(tmp_path)

    assert result["success"] is True
    assert result["executable_path"] == str(tmp_path / "womm")


# ///////////////////////////////////////////////////////////////
# VERIFY FILES COPIED
# ///////////////////////////////////////////////////////////////


def test_verify_files_copied_raises_when_source_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Source path does not exist"):
        installer_utils.verify_files_copied(tmp_path / "missing", tmp_path)


def test_verify_files_copied_raises_when_target_missing(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    with pytest.raises(FileNotFoundError, match="Target path does not exist"):
        installer_utils.verify_files_copied(source, tmp_path / "missing")


def test_verify_files_copied_raises_on_missing_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    target = tmp_path / "target"
    target.mkdir()

    with pytest.raises(FileNotFoundError, match="Missing 1 files"):
        installer_utils.verify_files_copied(source, target, ["missing.py"])


def test_verify_files_copied_raises_on_size_mismatch(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "file.py").write_text("short")
    target = tmp_path / "target"
    target.mkdir()
    (target / "file.py").write_text("a much longer content than source")

    with pytest.raises(OSError, match="Size mismatch"):
        installer_utils.verify_files_copied(source, target, ["file.py"])


def test_verify_files_copied_succeeds_using_auto_discovered_files(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "file.py").write_text("content")
    target = tmp_path / "target"
    target.mkdir()
    (target / "file.py").write_text("content")

    result = installer_utils.verify_files_copied(source, target)

    assert result == {
        "success": True,
        "total_files": 1,
        "missing_files": [],
        "size_mismatches": [],
    }


# ///////////////////////////////////////////////////////////////
# CREATE INSTALLATION PROOF
# ///////////////////////////////////////////////////////////////


def test_create_installation_proof_raises_when_womm_dir_missing(
    tmp_path: Path,
) -> None:
    with pytest.raises(NotADirectoryError, match="womm directory not found"):
        installer_utils.create_installation_proof(tmp_path)


def test_create_installation_proof_writes_metadata(tmp_path: Path) -> None:
    (tmp_path / "womm").mkdir()

    result = installer_utils.create_installation_proof(tmp_path)

    proof_path = Path(result["proof_file"])
    payload = json.loads(proof_path.read_text(encoding="utf-8"))
    assert payload["installation_type"] == "womm"
    assert payload["target_path"] == str(tmp_path)
