#!/usr/bin/env python3
"""Unit tests for context utility functions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from womm.utils.context import core_utils
from womm.utils.context.icon_utils import ContextIconResolver


@pytest.mark.parametrize(
    ("base", "parameter", "expected"),
    [("tool.exe", "%1", "tool.exe %1"), ('"tool.exe"', "%V", '"tool.exe %V"')],
)
def test_build_command_with_parameter(base: str, parameter: str, expected: str) -> None:
    assert core_utils.build_command_with_parameter(base, parameter) == expected


def test_context_string_helpers_validate_and_sanitize() -> None:
    assert core_utils.generate_registry_key_name("C:/tools/my-tool.exe") == "my-tool"
    assert core_utils.sanitize_registry_key('a/b:c*?"<>|') == "a_b_c______"
    assert core_utils.sanitize_label("  Hello\x00 world  ") == "Hello world"
    with pytest.raises(ValueError):
        core_utils.validate_label("---")
    with pytest.raises(ValueError):
        core_utils.validate_registry_key("invalid/key")


def test_context_help_and_file_types_are_exposed_without_mutating_config() -> None:
    assert "--background" in core_utils.get_context_type_help()
    assert "Custom extensions" in core_utils.get_file_type_help()
    types = core_utils.get_available_file_types()
    types.clear()
    assert core_utils.get_available_file_types()


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (None, "must be a dictionary"),
        ({}, "missing required keys"),
        (
            {"version": 1, "timestamp": "now", "entries": "bad", "metadata": {}},
            "Entries must be",
        ),
    ],
)
def test_validate_backup_data_rejects_invalid_shapes(data: Any, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        core_utils.validate_backup_data(data)


def test_validate_backup_data_accepts_required_structure() -> None:
    core_utils.validate_backup_data(
        {"version": 1, "timestamp": "now", "entries": [], "metadata": {}}
    )


def test_validate_icon_path_accepts_existing_supported_file(tmp_path: Path) -> None:
    icon = tmp_path / "icon.ico"
    icon.touch()
    core_utils.validate_icon_path(str(icon))
    unsupported_icon = tmp_path / "icon.txt"
    unsupported_icon.touch()
    with pytest.raises(ValueError, match="Unsupported"):
        core_utils.validate_icon_path(str(unsupported_icon))


@pytest.mark.parametrize("value", ["", 1])
def test_icon_lookup_rejects_invalid_values(value: Any) -> None:
    with pytest.raises(ValueError):
        ContextIconResolver.get_icon_for_extension(value)
    with pytest.raises(ValueError):
        ContextIconResolver.get_system_icon(value)


def test_icon_resolver_handles_extension_system_and_file_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ContextIconResolver, "EXTENSION_ICONS", {".py": "python.ico"})
    monkeypatch.setattr(ContextIconResolver, "SYSTEM_ICONS", {"folder": "folder.ico"})
    monkeypatch.setattr(ContextIconResolver, "SYSTEM_PATHS", [])
    monkeypatch.setattr(
        "womm.utils.context.icon_utils.os.path.exists",
        lambda path: path == "custom.ico",
    )

    assert ContextIconResolver.resolve_icon("auto", "module.py") == "python.ico"
    assert ContextIconResolver.resolve_icon("folder") == "folder.ico"
    assert ContextIconResolver.resolve_icon("custom.ico") == "custom.ico"
    assert ContextIconResolver.resolve_icon("missing.ico") is None


def test_icon_resolver_exposes_available_icons_and_path_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ContextIconResolver, "SYSTEM_ICONS", {"ok": "ok.ico", "none": None}
    )
    monkeypatch.setattr(ContextIconResolver, "EXTENSION_ICONS", {".py": "python.ico"})
    monkeypatch.setattr("shutil.which", lambda name: f"C:/icons/{name}")

    assert ContextIconResolver.get_available_icons() == {"ok": "ok.ico"}
    assert ContextIconResolver.get_supported_extensions() == [".py"]
    assert ContextIconResolver.find_icon_in_path("ok.ico") == "C:/icons/ok.ico"
