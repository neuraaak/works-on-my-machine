#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST PROJECT ENV UTILS - Environment setup utilities coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for virtual environment and npm dependency utilities."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.services.common.command_runner_service import CommandRunnerService
from womm.services.project import env_utils
from womm.shared.results.base import CommandResult

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////


def _fake_venv_create(venv_path: Path, **_kwargs: object) -> None:
    venv_path.mkdir(parents=True)


def _make_windows_venv(venv_path: Path) -> None:
    scripts = venv_path / "Scripts"
    scripts.mkdir(parents=True)
    (scripts / "python.exe").touch()
    (scripts / "pip.exe").touch()


def _patch_command_runner(monkeypatch: pytest.MonkeyPatch, handler) -> None:
    """Patch the CommandRunnerService singleton instance's ``run`` method.

    Patched on the instance (not the class): the singleton persists across
    the whole test session, and other tests in the suite shadow ``run`` on
    that same instance, which would otherwise mask a class-level patch.
    """
    monkeypatch.setattr(CommandRunnerService(), "run", handler)


# ///////////////////////////////////////////////////////////////
# CREATE VIRTUAL ENVIRONMENT
# ///////////////////////////////////////////////////////////////


def test_create_virtual_environment_reports_existing_venv(tmp_path: Path) -> None:
    (tmp_path / "venv").mkdir()

    result = env_utils.create_virtual_environment(tmp_path)

    assert result == {
        "success": True,
        "venv_path": str(tmp_path / "venv"),
        "existing": True,
    }


def test_create_virtual_environment_creates_new_venv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(env_utils.venv, "create", _fake_venv_create)

    result = env_utils.create_virtual_environment(tmp_path, venv_name="myenv")

    assert result == {
        "success": True,
        "venv_path": str(tmp_path / "myenv"),
        "existing": False,
    }
    assert (tmp_path / "myenv").is_dir()


def test_create_virtual_environment_upgrades_pip_when_executables_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def create_with_executables(venv_path: Path, **_kwargs: object) -> None:
        _make_windows_venv(venv_path)

    monkeypatch.setattr(env_utils.venv, "create", create_with_executables)
    captured: dict[str, object] = {}

    def fake_run(command: list[str], **_kwargs: object):
        captured["command"] = command
        return CommandResult(returncode=0)

    _patch_command_runner(monkeypatch, fake_run)

    env_utils.create_virtual_environment(tmp_path)

    assert captured["command"][-4:] == ["-m", "pip", "install", "--upgrade", "pip"][-4:]
    assert "pip" in captured["command"][2]


# ///////////////////////////////////////////////////////////////
# FIND EXECUTABLES
# ///////////////////////////////////////////////////////////////


def test_find_pip_executable_returns_path_when_present(tmp_path: Path) -> None:
    _make_windows_venv(tmp_path)

    pip_exe = env_utils.find_pip_executable(tmp_path)

    assert pip_exe == tmp_path / "Scripts" / "pip.exe"


def test_find_pip_executable_raises_when_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="pip not found"):
        env_utils.find_pip_executable(tmp_path)


# ///////////////////////////////////////////////////////////////
# INSTALL PYTHON DEPENDENCIES
# ///////////////////////////////////////////////////////////////


def test_install_python_dependencies_raises_when_venv_missing(
    tmp_path: Path,
) -> None:
    with pytest.raises(FileNotFoundError, match="Virtual environment not found"):
        env_utils.install_python_dependencies(tmp_path)


def test_install_python_dependencies_skips_when_requirements_file_missing(
    tmp_path: Path,
) -> None:
    _make_windows_venv(tmp_path / "venv")

    result = env_utils.install_python_dependencies(tmp_path)

    assert result is True


def test_install_python_dependencies_installs_from_requirements_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_windows_venv(tmp_path / "venv")
    (tmp_path / "requirements-dev.txt").write_text("pytest\n")
    captured: dict[str, object] = {}

    def fake_run(command: list[str], **_kwargs: object):
        captured["command"] = command
        return CommandResult(returncode=0)

    _patch_command_runner(monkeypatch, fake_run)

    result = env_utils.install_python_dependencies(tmp_path)

    assert result is True
    assert captured["command"][1:] == ["install", "-r", "requirements-dev.txt"]


def test_install_python_dependencies_raises_on_command_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _make_windows_venv(tmp_path / "venv")
    (tmp_path / "requirements-dev.txt").write_text("pytest\n")
    _patch_command_runner(
        monkeypatch, lambda *_a, **_k: CommandResult(returncode=1, stderr="boom")
    )

    with pytest.raises(RuntimeError, match="Failed to install dependencies"):
        env_utils.install_python_dependencies(tmp_path)


def test_install_python_dependencies_uses_alt_venv_dir(tmp_path: Path) -> None:
    _make_windows_venv(tmp_path / ".venv")

    result = env_utils.install_python_dependencies(tmp_path)

    assert result is True


# ///////////////////////////////////////////////////////////////
# NPM AVAILABILITY
# ///////////////////////////////////////////////////////////////


def test_check_npm_available_reflects_shutil_which(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(env_utils.shutil, "which", lambda _name: "/usr/bin/npm")
    assert env_utils.check_npm_available() is True

    monkeypatch.setattr(env_utils.shutil, "which", lambda _name: None)
    assert env_utils.check_npm_available() is False


# ///////////////////////////////////////////////////////////////
# INSTALL NPM DEPENDENCIES
# ///////////////////////////////////////////////////////////////


def test_install_npm_dependencies_raises_when_npm_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(env_utils, "check_npm_available", lambda: False)

    with pytest.raises(FileNotFoundError, match="npm is not installed"):
        env_utils.install_npm_dependencies(tmp_path)


def test_install_npm_dependencies_runs_npm_install(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(env_utils, "check_npm_available", lambda: True)
    captured: dict[str, object] = {}

    def fake_run(command: list[str], **_kwargs: object):
        captured["command"] = command
        return CommandResult(returncode=0)

    _patch_command_runner(monkeypatch, fake_run)

    result = env_utils.install_npm_dependencies(tmp_path)

    assert result is True
    assert captured["command"] == ["npm", "install"]


def test_install_npm_dependencies_raises_on_command_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(env_utils, "check_npm_available", lambda: True)
    _patch_command_runner(
        monkeypatch, lambda *_a, **_k: CommandResult(returncode=1, stderr="boom")
    )

    with pytest.raises(RuntimeError, match="Failed to install dependencies"):
        env_utils.install_npm_dependencies(tmp_path)


# ///////////////////////////////////////////////////////////////
# INSTALL NPM DEV DEPENDENCIES
# ///////////////////////////////////////////////////////////////


def test_install_npm_dev_dependencies_skips_when_no_dependencies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(env_utils, "check_npm_available", lambda: True)

    result = env_utils.install_npm_dev_dependencies(tmp_path, [])

    assert result is True


def test_install_npm_dev_dependencies_raises_when_npm_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(env_utils, "check_npm_available", lambda: False)

    with pytest.raises(FileNotFoundError, match="npm is not installed"):
        env_utils.install_npm_dev_dependencies(tmp_path, ["eslint"])


def test_install_npm_dev_dependencies_installs_given_packages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(env_utils, "check_npm_available", lambda: True)
    captured: dict[str, object] = {}

    def fake_run(command: list[str], **_kwargs: object):
        captured["command"] = command
        return CommandResult(returncode=0)

    _patch_command_runner(monkeypatch, fake_run)

    result = env_utils.install_npm_dev_dependencies(tmp_path, ["eslint", "prettier"])

    assert result is True
    assert captured["command"] == [
        "npm",
        "install",
        "--save-dev",
        "eslint",
        "prettier",
    ]


def test_install_npm_dev_dependencies_raises_on_command_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(env_utils, "check_npm_available", lambda: True)
    _patch_command_runner(
        monkeypatch, lambda *_a, **_k: CommandResult(returncode=1, stderr="boom")
    )

    with pytest.raises(RuntimeError, match="Failed to install development tools"):
        env_utils.install_npm_dev_dependencies(tmp_path, ["eslint"])
