#!/usr/bin/env python3
"""Unit tests for common and system utility functions."""

from __future__ import annotations

from pathlib import Path

import pytest

from womm.utils.common import path_resolver_utils
from womm.utils.system import detector_utils, environment_utils, path_utils


@pytest.mark.parametrize(
    ("relative_path", "expected_base", "expected_suffix"),
    [
        ("languages/python/template.py", "assets", "languages/python/template.py"),
        ("bin/womm", "bin", "womm"),
        ("assets/icon.svg", "assets", "icon.svg"),
        ("README.md", "root", "README.md"),
    ],
)
def test_resolve_script_path_uses_expected_base(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    relative_path: str,
    expected_base: str,
    expected_suffix: str,
) -> None:
    bases = {
        "assets": tmp_path / "assets",
        "bin": tmp_path / "bin",
        "root": tmp_path / "root",
    }
    monkeypatch.setattr(
        path_resolver_utils, "get_assets_module_path", lambda: bases["assets"]
    )
    monkeypatch.setattr(
        path_resolver_utils, "get_bin_module_path", lambda: bases["bin"]
    )
    monkeypatch.setattr(path_resolver_utils, "get_project_root", lambda: bases["root"])

    assert (
        path_resolver_utils.resolve_script_path(relative_path)
        == bases[expected_base] / expected_suffix
    )


def test_validate_script_exists_accepts_regular_file_only(tmp_path: Path) -> None:
    file_path = tmp_path / "script.py"
    file_path.write_text("print('ok')")

    assert path_resolver_utils.validate_script_exists(file_path)
    assert not path_resolver_utils.validate_script_exists(tmp_path)
    assert not path_resolver_utils.validate_script_exists(tmp_path / "missing.py")


@pytest.mark.parametrize(
    ("module_path", "git_exists", "expected"),
    [
        (Path("/site-packages/womm/assets"), False, True),
        (Path("/workspace/womm/assets"), True, False),
        (Path("/workspace/womm/assets"), False, True),
    ],
)
def test_is_pip_installation_uses_location_and_git_marker(
    monkeypatch: pytest.MonkeyPatch,
    module_path: Path,
    git_exists: bool,
    expected: bool,
) -> None:
    monkeypatch.setattr(
        path_resolver_utils, "get_assets_module_path", lambda: module_path
    )
    original_exists = Path.exists

    def exists(path: Path) -> bool:
        if path.name == ".git":
            return git_exists
        return original_exists(path)

    monkeypatch.setattr(Path, "exists", exists)

    assert path_resolver_utils.is_pip_installation() is expected


@pytest.mark.parametrize(
    ("stdout", "fallback", "expected"),
    [
        (None, "unknown", "unknown"),
        ("  1.2.3  ", "unknown", "1.2.3"),
        ("1.2.3\nmetadata", "unknown", "1.2.3"),
        ("   ", "missing", "missing"),
    ],
)
def test_extract_version_from_stdout(
    stdout: str | None, fallback: str, expected: str
) -> None:
    assert detector_utils.extract_version_from_stdout(stdout, fallback) == expected


def test_detector_helpers_build_normalized_entries() -> None:
    manager = detector_utils.create_package_manager_entry(
        "pip", "", {"command": "pip", "priority": 2}
    )

    assert manager == {
        "available": True,
        "version": None,
        "command": "pip",
        "description": "",
        "install_cmd": "",
        "priority": 2,
    }
    assert detector_utils.create_editor_entry("code", "VS Code")["available"]
    assert detector_utils.create_shell_entry("bash", "Bash")["type"] == "shell"


@pytest.mark.parametrize(
    ("managers", "expected"),
    [
        ({}, None),
        ({"a": {"available": False}}, None),
        (
            {
                "slow": {"available": True, "priority": 9},
                "fast": {"available": True, "priority": 1},
            },
            "fast",
        ),
    ],
)
def test_get_best_package_manager_selects_lowest_available_priority(
    managers: dict[str, dict[str, object]], expected: str | None
) -> None:
    assert detector_utils.get_best_package_manager(managers) == expected


@pytest.mark.parametrize(
    ("best", "installable", "expected_template"),
    [
        ("winget", None, "package_manager_use"),
        (None, "brew", "package_manager_install"),
        (None, None, "package_manager_none"),
    ],
)
def test_generate_package_manager_recommendation_selects_template(
    best: str | None, installable: str | None, expected_template: str
) -> None:
    result = detector_utils.generate_package_manager_recommendation(best, installable)

    assert result == detector_utils.SystemDetectorConfig.RECOMMENDATION_TEMPLATES[
        expected_template
    ].format(manager=best or installable)


@pytest.mark.parametrize(
    ("environments", "template"),
    [
        ({"code": {}}, "editor_vscode"),
        ({"nvim": {}}, "editor_cli"),
        ({}, "editor_install"),
    ],
)
def test_generate_editor_recommendation_selects_expected_template(
    environments: dict[str, dict[str, object]], template: str
) -> None:
    assert (
        detector_utils.generate_editor_recommendation(environments)
        == detector_utils.SystemDetectorConfig.RECOMMENDATION_TEMPLATES[template]
    )


@pytest.mark.parametrize(
    ("machine_path", "user_path", "expected"),
    [
        ("machine", "user", "machine;user"),
        ("machine", None, "machine"),
        (None, "user", "user"),
        (None, None, ""),
    ],
)
def test_combine_paths(
    machine_path: str | None, user_path: str | None, expected: str
) -> None:
    assert environment_utils.combine_paths(machine_path, user_path) == expected


def test_read_windows_registry_path_rejects_non_windows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(environment_utils.platform, "system", lambda: "Linux")

    with pytest.raises(OSError, match="only available on Windows"):
        environment_utils.read_windows_registry_path()


def test_refresh_path_from_registry_updates_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        environment_utils, "read_windows_registry_path", lambda: ("machine", "user")
    )
    monkeypatch.delenv("PATH", raising=False)

    assert environment_utils.refresh_path_from_registry()
    assert environment_utils.os.environ["PATH"] == "machine;user"


def test_refresh_path_from_registry_returns_false_on_registry_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        environment_utils,
        "read_windows_registry_path",
        lambda: (_ for _ in ()).throw(OSError("unavailable")),
    )

    assert not environment_utils.refresh_path_from_registry()


def test_get_shell_config_files_returns_existing_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / ".bashrc").touch()
    (tmp_path / ".profile").touch()
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert environment_utils.get_shell_config_files() == [
        tmp_path / ".bashrc",
        tmp_path / ".profile",
    ]


def test_get_environment_info_uses_environment_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(environment_utils.platform, "system", lambda: "Linux")
    monkeypatch.setenv("PATH", "bin")
    monkeypatch.setenv("HOME", "home")
    monkeypatch.setenv("SHELL", "bash")
    monkeypatch.setenv("USER", "alice")
    monkeypatch.setenv("TEMP", "tmp")

    assert environment_utils.get_environment_info() == {
        "platform": "linux",
        "path": "bin",
        "home": "home",
        "shell": "bash",
        "user": "alice",
        "temp": "tmp",
    }


@pytest.mark.parametrize(
    ("output", "expected"),
    [
        ("Path    REG_SZ    C:\\Tools", "C:\\Tools"),
        (b"Path    REG_EXPAND_SZ    %USERPROFILE%\\bin", "%USERPROFILE%\\bin"),
        ("Other REG_SZ value", ""),
        ("", ""),
    ],
)
def test_extract_path_from_reg_output(output: str | bytes, expected: str) -> None:
    assert path_utils.extract_path_from_reg_output(output) == expected


def test_deduplicate_path_entries_preserves_first_normalized_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        path_utils.os.path,
        "expandvars",
        lambda value: value.replace("%ROOT%", "C:/Tools"),
    )

    result = path_utils.deduplicate_path_entries(" C:/Tools/ ;%ROOT%\\;D:/Bin;;d:/bin/")

    assert result == "C:/Tools/;D:/Bin"
