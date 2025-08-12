#!/usr/bin/env python3
from click.testing import CliRunner

from womm.cli import womm


def test_cli_install_invokes_manager(monkeypatch):
    class DummyManager:
        def install(self, force=False, target=None):
            # Simule une installation qui ne lève pas d'exception
            return None

    monkeypatch.setattr(
        "womm.core.installation.installer.InstallationManager", DummyManager
    )

    runner = CliRunner()
    result = runner.invoke(womm, ["install", "--force"])  # minimal path
    assert result.exit_code == 0


def test_cli_uninstall_invokes_manager(monkeypatch):
    class DummyManager:
        def __init__(self, target=None):
            self.target = target

        def uninstall(self, force=False):
            return None

    monkeypatch.setattr(
        "womm.core.installation.uninstaller.UninstallationManager", DummyManager
    )

    runner = CliRunner()
    result = runner.invoke(womm, ["uninstall", "--force"])  # minimal path
    assert result.exit_code == 0


def test_cli_backup_path_list(monkeypatch):
    class DummyPathManager:
        def __init__(self, target=None):
            self.target = target

        def list_backup(self):
            return None

    monkeypatch.setattr(
        "womm.core.installation.path_manager.PathManager", DummyPathManager
    )

    runner = CliRunner()
    result = runner.invoke(womm, ["backup-path", "--list"])  # just list
    assert result.exit_code == 0


def test_cli_backup_path_create(monkeypatch):
    class DummyPathManager:
        def __init__(self, target=None):
            self.target = target

        def backup_path(self):
            return None

    monkeypatch.setattr(
        "womm.core.installation.path_manager.PathManager", DummyPathManager
    )

    runner = CliRunner()
    result = runner.invoke(womm, ["backup-path"])  # create new backup
    assert result.exit_code == 0


def test_cli_restore_path_list(monkeypatch):
    class DummyPathManager:
        def __init__(self, target=None):
            self.target = target

        def list_backup(self):
            return None

    monkeypatch.setattr(
        "womm.core.installation.path_manager.PathManager", DummyPathManager
    )

    runner = CliRunner()
    result = runner.invoke(womm, ["restore-path", "--list"])  # list
    assert result.exit_code == 0


def test_cli_restore_path_restore(monkeypatch):
    class DummyPathManager:
        def __init__(self, target=None):
            self.target = target

        def restore_path(self):
            return None

    monkeypatch.setattr(
        "womm.core.installation.path_manager.PathManager", DummyPathManager
    )

    runner = CliRunner()
    result = runner.invoke(womm, ["restore-path"])  # restore
    assert result.exit_code == 0
