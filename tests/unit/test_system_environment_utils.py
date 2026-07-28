#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SYSTEM ENVIRONMENT UTILS - Environment utilities coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for cross-platform environment variable utilities."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import shutil
import winreg
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.utils.system import environment_utils

# ///////////////////////////////////////////////////////////////
# WINDOWS REGISTRY READ
# ///////////////////////////////////////////////////////////////


def test_read_windows_registry_path_rejects_non_windows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(environment_utils.platform, "system", lambda: "Linux")

    with pytest.raises(OSError, match="only available on Windows"):
        environment_utils.read_windows_registry_path()


def test_read_windows_registry_path_returns_both_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(environment_utils.platform, "system", lambda: "Windows")

    class FakeKey:
        def __enter__(self) -> FakeKey:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    def fake_open_key(_hive: int, _subkey: str) -> FakeKey:
        return FakeKey()

    def fake_query_value(_key: FakeKey, _name: str) -> tuple[str, int]:
        return ("C:\\hklm\\path", 1)

    monkeypatch.setattr(winreg, "OpenKey", fake_open_key)
    monkeypatch.setattr(winreg, "QueryValueEx", fake_query_value)

    hklm, hkcu = environment_utils.read_windows_registry_path()

    assert hklm == "C:\\hklm\\path"
    assert hkcu == "C:\\hklm\\path"


def test_read_windows_registry_path_returns_none_when_key_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(environment_utils.platform, "system", lambda: "Windows")

    def fail_open_key(_hive: int, _subkey: str) -> None:
        raise OSError("key not found")

    monkeypatch.setattr(winreg, "OpenKey", fail_open_key)

    hklm, hkcu = environment_utils.read_windows_registry_path()

    assert hklm is None
    assert hkcu is None


# ///////////////////////////////////////////////////////////////
# COMBINE PATHS
# ///////////////////////////////////////////////////////////////


@pytest.mark.parametrize(
    ("hklm_path", "hkcu_path", "expected"),
    [
        ("C:\\a", "C:\\b", "C:\\a;C:\\b"),
        ("C:\\a", None, "C:\\a"),
        (None, "C:\\b", "C:\\b"),
        (None, None, ""),
    ],
)
def test_combine_paths(
    hklm_path: str | None, hkcu_path: str | None, expected: str
) -> None:
    assert environment_utils.combine_paths(hklm_path, hkcu_path) == expected


# ///////////////////////////////////////////////////////////////
# REFRESH PATH FROM REGISTRY
# ///////////////////////////////////////////////////////////////


def test_refresh_path_from_registry_sets_environ_on_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        environment_utils,
        "read_windows_registry_path",
        lambda: ("C:\\a", "C:\\b"),
    )
    monkeypatch.delenv("PATH", raising=False)

    assert environment_utils.refresh_path_from_registry() is True
    assert environment_utils.os.environ["PATH"] == "C:\\a;C:\\b"


def test_refresh_path_from_registry_returns_false_when_combined_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        environment_utils, "read_windows_registry_path", lambda: (None, None)
    )

    assert environment_utils.refresh_path_from_registry() is False


@pytest.mark.parametrize("error", [OSError("boom"), ImportError("no winreg")])
def test_refresh_path_from_registry_returns_false_on_error(
    monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    def fail() -> tuple[str | None, str | None]:
        raise error

    monkeypatch.setattr(environment_utils, "read_windows_registry_path", fail)

    assert environment_utils.refresh_path_from_registry() is False


# ///////////////////////////////////////////////////////////////
# SHELL CONFIG FILES
# ///////////////////////////////////////////////////////////////


def test_get_shell_config_files_returns_only_existing_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        environment_utils.Path, "home", classmethod(lambda _cls: tmp_path)
    )
    (tmp_path / ".bashrc").touch()
    (tmp_path / ".zprofile").touch()

    result = environment_utils.get_shell_config_files()

    assert result == [tmp_path / ".bashrc", tmp_path / ".zprofile"]


def test_get_shell_config_files_returns_empty_list_when_none_exist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        environment_utils.Path, "home", classmethod(lambda _cls: tmp_path)
    )

    assert environment_utils.get_shell_config_files() == []


# ///////////////////////////////////////////////////////////////
# ENVIRONMENT INFO
# ///////////////////////////////////////////////////////////////


def test_get_environment_info_reads_from_os_environ(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(environment_utils.platform, "system", lambda: "Linux")
    monkeypatch.setenv("PATH", "/usr/bin")
    monkeypatch.setenv("HOME", "/home/demo")
    monkeypatch.setenv("SHELL", "/bin/bash")
    monkeypatch.setenv("USER", "demo")
    monkeypatch.setenv("TEMP", "/scratch")

    info = environment_utils.get_environment_info()

    assert info == {
        "platform": "linux",
        "path": "/usr/bin",
        "home": "/home/demo",
        "shell": "/bin/bash",
        "user": "demo",
        "temp": "/scratch",
    }


# ///////////////////////////////////////////////////////////////
# COMMAND ACCESSIBILITY
# ///////////////////////////////////////////////////////////////


def test_is_command_accessible_reflects_shutil_which(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(shutil, "which", lambda _cmd: "/usr/bin/git")
    assert environment_utils.is_command_accessible("git") is True

    monkeypatch.setattr(shutil, "which", lambda _cmd: None)
    assert environment_utils.is_command_accessible("git") is False
