#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST WOMM SETUP COMMON UTILS - Installation path resolution coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for WOMM installation path resolution utilities."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.utils.womm_setup import common_utils

# ///////////////////////////////////////////////////////////////
# DEFAULT PATH
# ///////////////////////////////////////////////////////////////


def test_get_default_womm_path_uses_home_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(common_utils.Path, "home", classmethod(lambda _cls: tmp_path))

    assert common_utils.get_default_womm_path() == tmp_path / ".womm"


# ///////////////////////////////////////////////////////////////
# CURRENT WOMM PATH
# ///////////////////////////////////////////////////////////////


def test_get_current_womm_path_finds_package_under_project_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    womm_dir = tmp_path / "womm"
    womm_dir.mkdir()
    (womm_dir / "__main__.py").touch()
    monkeypatch.setattr(common_utils, "get_project_root", lambda: tmp_path)

    assert common_utils.get_current_womm_path() == womm_dir


def test_get_current_womm_path_falls_back_to_sys_path_scan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(common_utils, "get_project_root", lambda: tmp_path / "empty")
    monkeypatch.setitem(sys.modules, "womm.__main__", None)

    scan_root = tmp_path / "scan_root"
    womm_dir = scan_root / "womm"
    womm_dir.mkdir(parents=True)
    (womm_dir / "__main__.py").touch()
    monkeypatch.setattr(sys, "path", [str(scan_root)])

    assert common_utils.get_current_womm_path() == womm_dir


def test_get_current_womm_path_falls_back_to_parent_walk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(common_utils, "get_project_root", lambda: tmp_path / "empty")
    monkeypatch.setitem(sys.modules, "womm.__main__", None)
    monkeypatch.setattr(sys, "path", [])

    fake_module_dir = tmp_path / "frozen" / "internal"
    fake_module_dir.mkdir(parents=True)
    (tmp_path / "frozen" / "__main__.py").touch()
    fake_file = fake_module_dir / "common_utils.py"
    fake_file.touch()
    monkeypatch.setattr(common_utils, "__file__", str(fake_file))

    assert common_utils.get_current_womm_path() == tmp_path / "frozen"


def test_get_current_womm_path_raises_when_nothing_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(common_utils, "get_project_root", lambda: tmp_path / "empty")
    monkeypatch.setitem(sys.modules, "womm.__main__", None)
    monkeypatch.setattr(sys, "path", [])

    isolated_dir = tmp_path / "isolated"
    isolated_dir.mkdir()
    fake_file = isolated_dir / "common_utils.py"
    fake_file.touch()
    monkeypatch.setattr(common_utils, "__file__", str(fake_file))

    with pytest.raises(RuntimeError, match="Could not find womm package directory"):
        common_utils.get_current_womm_path()


# ///////////////////////////////////////////////////////////////
# WOMM INSTALLATION PATH
# ///////////////////////////////////////////////////////////////


def test_get_womm_installation_path_detects_development_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        common_utils, "get_current_womm_path", lambda: tmp_path / "womm"
    )
    monkeypatch.setattr(common_utils, "get_project_root", lambda: tmp_path)
    default_path = tmp_path / "default" / ".womm"
    monkeypatch.setattr(common_utils, "get_default_womm_path", lambda: default_path)

    assert common_utils.get_womm_installation_path() == default_path


def test_get_womm_installation_path_detects_installation_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    install_dir = tmp_path / "install"
    womm_dir = install_dir / "womm"
    womm_dir.mkdir(parents=True)
    (womm_dir / "__main__.py").touch()
    monkeypatch.setattr(common_utils, "get_current_womm_path", lambda: womm_dir)
    monkeypatch.setattr(common_utils, "get_project_root", lambda: tmp_path / "other")

    assert common_utils.get_womm_installation_path() == install_dir


def test_get_womm_installation_path_uses_parent_for_custom_installation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    install_dir = tmp_path / "custom"
    womm_dir = install_dir / "womm"
    womm_dir.mkdir(parents=True)
    monkeypatch.setattr(common_utils, "get_current_womm_path", lambda: womm_dir)
    monkeypatch.setattr(common_utils, "get_project_root", lambda: tmp_path / "other")

    assert common_utils.get_womm_installation_path() == install_dir


def test_get_womm_installation_path_falls_back_when_current_path_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail() -> Path:
        raise RuntimeError("not found")

    monkeypatch.setattr(common_utils, "get_current_womm_path", fail)
    default_path = tmp_path / "default" / ".womm"
    monkeypatch.setattr(common_utils, "get_default_womm_path", lambda: default_path)

    assert common_utils.get_womm_installation_path() == default_path


# ///////////////////////////////////////////////////////////////
# VALID WOMM INSTALLATION
# ///////////////////////////////////////////////////////////////


def test_is_valid_womm_installation_uses_detected_path_when_none_given(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    womm_dir = tmp_path / "womm"
    womm_dir.mkdir()
    (womm_dir / "__main__.py").touch()
    (womm_dir / ".proof").touch()
    monkeypatch.setattr(common_utils, "get_womm_installation_path", lambda: tmp_path)

    assert common_utils.is_valid_womm_installation() is True


def test_is_valid_womm_installation_rejects_missing_womm_directory(
    tmp_path: Path,
) -> None:
    assert common_utils.is_valid_womm_installation(tmp_path) is False


def test_is_valid_womm_installation_rejects_missing_main_file(
    tmp_path: Path,
) -> None:
    (tmp_path / "womm").mkdir()

    assert common_utils.is_valid_womm_installation(tmp_path) is False


def test_is_valid_womm_installation_rejects_missing_proof_file(
    tmp_path: Path,
) -> None:
    womm_dir = tmp_path / "womm"
    womm_dir.mkdir()
    (womm_dir / "__main__.py").touch()

    assert common_utils.is_valid_womm_installation(tmp_path) is False


def test_is_valid_womm_installation_accepts_complete_installation(
    tmp_path: Path,
) -> None:
    womm_dir = tmp_path / "womm"
    womm_dir.mkdir()
    (womm_dir / "__main__.py").touch()
    (womm_dir / ".proof").touch()

    assert common_utils.is_valid_womm_installation(tmp_path) is True


def test_is_valid_womm_installation_returns_false_on_os_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_is_dir(_self: Path) -> bool:
        raise OSError("boom")

    monkeypatch.setattr(Path, "is_dir", fail_is_dir)

    assert common_utils.is_valid_womm_installation(tmp_path) is False
