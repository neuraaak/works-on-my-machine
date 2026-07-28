#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST CONTEXT CORE UTILS EXTRA - Error branches and registry lookup
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Additional coverage for context core utils: error branches and winreg lookup."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import winreg

# Third-party imports
import pytest

# Local imports
from womm.utils.context import core_utils

# ///////////////////////////////////////////////////////////////
# EMPTY-INPUT VALIDATION
# ///////////////////////////////////////////////////////////////


def test_build_command_with_parameter_rejects_empty_base() -> None:
    with pytest.raises(ValueError, match="Base command cannot be empty"):
        core_utils.build_command_with_parameter("", "%1")


def test_generate_registry_key_name_rejects_empty_path() -> None:
    with pytest.raises(ValueError, match="File path cannot be empty"):
        core_utils.generate_registry_key_name("")


def test_generate_registry_key_name_rejects_path_without_stem() -> None:
    with pytest.raises(ValueError, match="Could not generate valid key name"):
        core_utils.generate_registry_key_name(".")


def test_sanitize_registry_key_rejects_empty_key() -> None:
    with pytest.raises(ValueError, match="Registry key cannot be empty"):
        core_utils.sanitize_registry_key("")


def test_sanitize_label_rejects_empty_label() -> None:
    with pytest.raises(ValueError, match="Label cannot be empty"):
        core_utils.sanitize_label("")


def test_validate_label_rejects_empty_label() -> None:
    with pytest.raises(ValueError, match="Label cannot be empty"):
        core_utils.validate_label("")


def test_validate_label_rejects_label_too_long() -> None:
    with pytest.raises(ValueError, match="too long"):
        core_utils.validate_label("a" * 101)


def test_validate_label_accepts_valid_label() -> None:
    core_utils.validate_label("My Tool")


def test_validate_registry_key_rejects_empty_key() -> None:
    with pytest.raises(ValueError, match="Registry key cannot be empty"):
        core_utils.validate_registry_key("")


def test_validate_registry_key_rejects_key_too_long() -> None:
    with pytest.raises(ValueError, match="too long"):
        core_utils.validate_registry_key("a" * 256)


def test_validate_registry_key_accepts_valid_key() -> None:
    core_utils.validate_registry_key("MyTool")


def test_validate_icon_path_accepts_auto() -> None:
    core_utils.validate_icon_path("auto")


def test_validate_icon_path_accepts_empty() -> None:
    core_utils.validate_icon_path("")


def test_validate_icon_path_rejects_missing_file() -> None:
    with pytest.raises(ValueError, match="does not exist"):
        core_utils.validate_icon_path("C:/does/not/exist.ico")


# ///////////////////////////////////////////////////////////////
# REGISTRY ENTRY INFO
# ///////////////////////////////////////////////////////////////


def test_get_registry_entry_info_reads_display_name_icon_and_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeCommandKey:
        def __enter__(self) -> FakeCommandKey:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    class FakeKey:
        def __enter__(self) -> FakeKey:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    def fake_open_key(_hive: object, path: str) -> FakeKey | FakeCommandKey:
        if path == "command":
            return FakeCommandKey()
        return FakeKey()

    def fake_query_value(_key: object, name: str) -> tuple[str, int]:
        values = {
            "MUIVerb": ("My Tool", 1),
            "Icon": ("tool.ico", 1),
            "": ("tool.exe %1", 1),
        }
        return values[name]

    monkeypatch.setattr(winreg, "OpenKey", fake_open_key)
    monkeypatch.setattr(winreg, "QueryValueEx", fake_query_value)

    info = core_utils.get_registry_entry_info("HKCU\\Base", "MyTool")

    assert info["key_name"] == "MyTool"
    assert info["registry_path"] == "HKCU\\Base\\MyTool"
    assert info["display_name"] == "My Tool"
    assert info["icon"] == "tool.ico"
    assert info["command"] == "tool.exe %1"


def test_get_registry_entry_info_defaults_when_values_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeKey:
        def __enter__(self) -> FakeKey:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    def fake_open_key(_hive: object, path: str) -> FakeKey:
        if path == "command":
            raise OSError("no command subkey")
        return FakeKey()

    def fake_query_value(_key: object, _name: str) -> tuple[str, int]:
        raise OSError("value not set")

    monkeypatch.setattr(winreg, "OpenKey", fake_open_key)
    monkeypatch.setattr(winreg, "QueryValueEx", fake_query_value)

    info = core_utils.get_registry_entry_info("HKCU\\Base", "MyTool")

    assert info["display_name"] == "MyTool"
    assert info["icon"] is None
    assert info["command"] is None
