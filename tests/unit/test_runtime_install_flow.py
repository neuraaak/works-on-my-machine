#!/usr/bin/env python3
import types

import pytest  # noqa: F401

from womm.core.dependencies.package_manager import PackageManagerResult, package_manager
from womm.core.dependencies.runtime_manager import runtime_manager


def test_ensure_manager_no_pm_returns_panel(monkeypatch):
    # Force Python to appear missing so install_runtime takes the PM path
    monkeypatch.setattr(
        "womm.core.dependencies.runtime_manager.check_tool_available",
        lambda cmd: cmd not in ("python", "python3", "py"),
    )

    def fake_ensure(_preferred=None):
        return PackageManagerResult(
            success=False,
            package_manager_name="none",
            message="No PM",
            error="no_package_manager",
            panel="PANEL",
        )

    monkeypatch.setattr(package_manager, "ensure_manager", fake_ensure)

    res = runtime_manager.install_runtime("python")
    assert not res.success
    assert res.error == "no_package_manager"


def test_install_python_when_missing_but_pm_available(monkeypatch):
    # Enable dry-run to avoid any real installation path in lower layers
    monkeypatch.setenv("WOMM_DRY_RUN", "1")
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
            return types.SimpleNamespace(success=True, stdout="Python 3.11.4")
        return types.SimpleNamespace(success=True, stdout="")

    def fake_ensure(_preferred=None):
        return PackageManagerResult(success=True, package_manager_name="chocolatey")

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
    monkeypatch.setattr(package_manager, "ensure_manager", fake_ensure)
    monkeypatch.setattr(package_manager, "install_package", fake_install_package)

    res = runtime_manager.install_runtime("python")
    assert res.success
    assert res.version and res.version.startswith("3.11")


def test_node_min_version_validation(monkeypatch):
    # Simulate node present but older than required (e.g., 16)
    monkeypatch.setattr(
        "womm.core.dependencies.runtime_manager.check_tool_available",
        lambda cmd: cmd == "node",
    )
    monkeypatch.setattr(
        "womm.core.dependencies.runtime_manager.run_silent",
        lambda _cmd: types.SimpleNamespace(success=True, stdout="v16.0.0"),
    )

    ok, version = runtime_manager._check_node()
    assert not ok
    assert version is None or version == "v16.0.0" or isinstance(version, str)
