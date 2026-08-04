"""Unit tests for pure project platform, template and validation helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from womm.utils.project import platform_utils, validation_utils


@pytest.mark.parametrize(
    ("system", "python", "npm", "shell"),
    [("Windows", "python.exe", "npm.cmd", "cmd"), ("Linux", "python3", "npm", "bash")],
)
def test_platform_helpers_select_expected_commands(
    monkeypatch: pytest.MonkeyPatch, system: str, python: str, npm: str, shell: str
) -> None:
    monkeypatch.setattr(platform_utils.platform, "system", lambda: system)

    assert platform_utils.get_platform_info()["system"] == system
    assert platform_utils.get_python_paths()["python_executable"] == python
    assert platform_utils.get_node_paths()["npm_executable"] == npm
    assert platform_utils.get_shell_commands()["shell"] == shell


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("", "my-project"),
        ("My project!!", "my-project"),
        ("123 app", "project-123-app"),
    ],
)
def test_suggest_project_name_normalizes_input(raw: str, expected: str) -> None:
    assert validation_utils.suggest_project_name(raw) == expected


@pytest.mark.parametrize("name", ["", ".hidden", "bad/name", "CON"])
def test_validate_project_name_rejects_invalid_inputs(name: str) -> None:
    with pytest.raises(ValueError):
        validation_utils.validate_project_name(name)


def test_validate_project_config_and_summary(tmp_path: Path) -> None:
    config = {"project_name": "demo", "project_type": "python"}
    validation_utils.validate_project_config(config)
    assert validation_utils.check_project_name("bad/name")[0] is False
    summary = validation_utils.get_validation_summary(
        "demo", tmp_path / "new", "python"
    )
    assert summary == {"project_name": True, "project_path": True, "project_type": True}
