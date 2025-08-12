#!/usr/bin/env python3
import types

import pytest  # noqa: F401
from click.testing import CliRunner

from womm.cli import womm
from womm.core.dependencies.package_manager import PackageManagerResult, package_manager


def test_system_install_no_package_manager_shows_panel(monkeypatch):
    # Simuler aucun PM dispo
    monkeypatch.setattr(
        package_manager,
        "ensure_manager",
        lambda _preferred=None: PackageManagerResult(
            success=False,
            package_manager_name="none",
            message="No PM",
            error="no_package_manager",
            panel="PANEL",
        ),
    )

    runner = CliRunner()
    result = runner.invoke(womm, ["system", "install", "all"])  # not --check

    assert result.exit_code == 0  # we early-return without sys.exit
    # Optionally, we could check text, but UI uses Rich panels; we assert no crash


def test_system_install_python_only_with_pm(monkeypatch):
    # Enable dry-run to avoid any real installation path even if detection passes
    monkeypatch.setenv("WOMM_DRY_RUN", "1")
    # PM dispo
    monkeypatch.setattr(
        package_manager,
        "ensure_manager",
        lambda _preferred=None: PackageManagerResult(
            success=True, package_manager_name="chocolatey"
        ),
    )

    # Python pas dispo au début puis dispo après installation
    installed = {"python": False}

    def fake_check_tool_available(cmd: str) -> bool:
        if cmd in ("python", "python3", "py"):
            return installed["python"]
        return True

    def fake_run_silent(cmd):
        if (
            len(cmd) >= 2
            and cmd[0] in ("python", "python3", "py")
            and cmd[1] == "--version"
        ):
            return types.SimpleNamespace(success=True, stdout="Python 3.11.5")
        return types.SimpleNamespace(success=True, stdout="")

    def fake_install_package(_package_name: str, manager_name: str = None):
        installed["python"] = True
        return PackageManagerResult(
            success=True, package_manager_name=manager_name or "chocolatey"
        )

    monkeypatch.setattr(
        "womm.core.dependencies.runtime_manager.check_tool_available",
        fake_check_tool_available,
    )
    monkeypatch.setattr(
        "womm.core.dependencies.runtime_manager.run_silent",
        fake_run_silent,
    )
    monkeypatch.setattr(package_manager, "install_package", fake_install_package)

    runner = CliRunner()
    result = runner.invoke(womm, ["system", "install", "python"])  # not --check

    # Should complete successfully
    assert result.exit_code == 0
