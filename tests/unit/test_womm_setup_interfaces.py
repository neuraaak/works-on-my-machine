#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST WOMM SETUP INTERFACES - Boundary tests for the exception->Result contract
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Boundary tests for the WOMM install/uninstall interfaces.

These verify the exception-rework contract at the interface layer:
``WommDeploymentServiceError``/``OSError`` raised while executing an install
or uninstall run is translated into a Result (never re-raised), the
planning phase (``precheck_install``/``plan_uninstall``) reports its own
failures without touching any progress UI, and the success path assembles
the final Result from real filesystem side effects.

Both interfaces are singletons; tests build a bare instance with
``object.__new__`` to bypass the singleton machinery and ``__init__``'s real
path resolution, then set only the attributes each test needs. PATH/registry
and command-accessibility steps are stubbed out (they belong to the
``system`` vertical and would otherwise touch the real environment); file
copy/removal run for real against ``tmp_path``.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import platform
from pathlib import Path

# Third-party imports
import pytest

# Local imports
from womm.exceptions.womm_deployment import WommDeploymentServiceError
from womm.interfaces.womm_setup.installer_interface import WommInstallerInterface
from womm.interfaces.womm_setup.uninstaller_interface import WommUninstallerInterface
from womm.shared.results import (
    InstallationResult,
    InstallPlanResult,
    UninstallationResult,
    UninstallPlanResult,
)

# ///////////////////////////////////////////////////////////////
# TEST HELPERS
# ///////////////////////////////////////////////////////////////


class _FakeReporter:
    """Records the progress calls made by execute_install/execute_uninstall."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def update_layer(
        self, layer_name: str, progress_value: int | None = None, message: str = ""
    ) -> None:
        self.calls.append(("update", layer_name, progress_value, message))

    def complete_layer(self, layer_name: str) -> None:
        self.calls.append(("complete", layer_name))

    def emergency_stop(self, message: str = "Operation stopped") -> None:
        self.calls.append(("stop", message))

    def stopped(self) -> bool:
        return any(call[0] == "stop" for call in self.calls)

    def completed(self, layer_name: str) -> bool:
        return ("complete", layer_name) in self.calls


def _bare_installer() -> WommInstallerInterface:
    """Build a WommInstallerInterface without the singleton __init__."""
    installer = object.__new__(WommInstallerInterface)
    installer._installation_service = None
    installer._command_runner = None
    installer.platform = platform.system()
    installer._path_backup_file = None
    installer._installed_files = []
    return installer


def _bare_uninstaller() -> WommUninstallerInterface:
    """Build a WommUninstallerInterface without the singleton __init__."""
    uninstaller = object.__new__(WommUninstallerInterface)
    uninstaller.platform = platform.system()
    uninstaller._uninstallation_service = None
    uninstaller._path_service = None
    return uninstaller


def _make_source_tree(root: Path) -> Path:
    """Build a minimal valid WOMM source tree under ``root``."""
    (root / "womm" / "bin").mkdir(parents=True)
    (root / "womm" / "assets").mkdir(parents=True)
    (root / "womm" / "bin" / "tool.txt").write_text("tool", encoding="utf-8")
    (root / "womm" / "assets" / "asset.txt").write_text("asset", encoding="utf-8")
    (root / "womm.py").write_text("# womm launcher", encoding="utf-8")
    (root / "womm.bat").write_text("@echo off", encoding="utf-8")
    return root


# ///////////////////////////////////////////////////////////////
# TESTS - PRECHECK_INSTALL
# ///////////////////////////////////////////////////////////////


class TestPrecheckInstall:
    """Boundary behaviour of WommInstallerInterface.precheck_install()."""

    def test_success_builds_plan_with_files(self, tmp_path: Path) -> None:
        """A valid source and an empty target yield a successful plan."""
        source = _make_source_tree(tmp_path / "source")
        target = tmp_path / "target"
        installer = _bare_installer()
        installer.source_path = source
        installer.target_path = target

        plan = installer.precheck_install()

        assert isinstance(plan, InstallPlanResult)
        assert plan.success is True
        assert plan.target_path == str(target)
        assert set(plan.files_to_copy or []) == {
            "womm.py",
            "womm.bat",
            str(Path("womm") / "bin" / "tool.txt"),
            str(Path("womm") / "assets" / "asset.txt"),
        }

    def test_missing_source_structure_fails(self, tmp_path: Path) -> None:
        """A source missing womm/assets fails the pre-check."""
        source = tmp_path / "source"
        (source / "womm" / "bin").mkdir(parents=True)
        (source / "womm.py").write_text("x", encoding="utf-8")
        (source / "womm.bat").write_text("x", encoding="utf-8")
        installer = _bare_installer()
        installer.source_path = source
        installer.target_path = tmp_path / "target"

        plan = installer.precheck_install()

        assert plan.success is False
        assert "Pre-check failed" in plan.error

    def test_existing_target_without_force_fails(self, tmp_path: Path) -> None:
        """A non-empty target without --force is reported as a failure."""
        source = _make_source_tree(tmp_path / "source")
        target = tmp_path / "target"
        target.mkdir()
        (target / "existing.txt").write_text("x", encoding="utf-8")
        installer = _bare_installer()
        installer.source_path = source
        installer.target_path = target

        plan = installer.precheck_install()

        assert plan.success is False
        assert plan.error == "Installation directory already exists"

    def test_existing_target_with_force_succeeds(self, tmp_path: Path) -> None:
        """--force allows planning over a non-empty target."""
        source = _make_source_tree(tmp_path / "source")
        target = tmp_path / "target"
        target.mkdir()
        (target / "existing.txt").write_text("x", encoding="utf-8")
        installer = _bare_installer()
        installer.source_path = source
        installer.target_path = target

        plan = installer.precheck_install(force=True)

        assert plan.success is True

    def test_target_argument_overrides_default(self, tmp_path: Path) -> None:
        """An explicit target overrides the interface's resolved target_path."""
        source = _make_source_tree(tmp_path / "source")
        other_target = tmp_path / "custom"
        installer = _bare_installer()
        installer.source_path = source
        installer.target_path = tmp_path / "default"

        plan = installer.precheck_install(target=str(other_target))

        assert installer.target_path == other_target
        assert plan.target_path == str(other_target)


# ///////////////////////////////////////////////////////////////
# TESTS - EXECUTE_INSTALL
# ///////////////////////////////////////////////////////////////


class TestExecuteInstall:
    """Boundary behaviour of WommInstallerInterface.execute_install()."""

    def _planned_installer(
        self, tmp_path: Path
    ) -> tuple[WommInstallerInterface, InstallPlanResult]:
        source = _make_source_tree(tmp_path / "source")
        target = tmp_path / "target"
        installer = _bare_installer()
        installer.source_path = source
        installer.target_path = target
        plan = installer.precheck_install()
        assert plan.success is True
        return installer, plan

    def test_success_copies_files_and_returns_result(self, tmp_path: Path) -> None:
        """A full run (PATH steps stubbed) copies files and completes the stages."""
        installer, plan = self._planned_installer(tmp_path)
        installer._backup_path = lambda: True
        installer._setup_path = lambda _reporter: None
        installer._verify_installation_with_progress = lambda _reporter: None
        reporter = _FakeReporter()

        result = installer.execute_install(plan, reporter)

        assert isinstance(result, InstallationResult)
        assert result.success is True
        assert result.files_copied == len(plan.files_to_copy or [])
        assert (Path(plan.target_path) / "womm.py").exists()
        assert reporter.completed("main_installation")
        assert not reporter.stopped()

    def test_file_copy_failure_is_translated_to_failure_result(
        self, tmp_path: Path
    ) -> None:
        """A missing source file surfaces as a failed Result, never re-raised."""
        source = _make_source_tree(tmp_path / "source")
        target = tmp_path / "target"
        installer = _bare_installer()
        installer.source_path = source
        installer.target_path = target
        plan = InstallPlanResult(
            success=True,
            source_path=str(source),
            target_path=str(target),
            files_to_copy=["does_not_exist.py"],
        )
        reporter = _FakeReporter()

        result = installer.execute_install(plan, reporter)

        assert result.success is False
        assert "file_copy" in result.error or "does_not_exist" in result.error
        assert reporter.stopped()

    def test_path_setup_failure_is_translated_to_failure_result(
        self, tmp_path: Path
    ) -> None:
        """A WommDeploymentServiceError from PATH setup becomes a failed Result."""
        installer, plan = self._planned_installer(tmp_path)
        installer._backup_path = lambda: True

        def _raise_setup(_reporter) -> None:
            raise WommDeploymentServiceError(
                operation="path_setup", reason="registry busy"
            )

        installer._setup_path = _raise_setup
        reporter = _FakeReporter()

        result = installer.execute_install(plan, reporter)

        assert result.success is False
        assert "registry busy" in result.error
        assert reporter.stopped()
        assert not reporter.completed("main_installation")


# ///////////////////////////////////////////////////////////////
# TESTS - PLAN_UNINSTALL
# ///////////////////////////////////////////////////////////////


class TestPlanUninstall:
    """Boundary behaviour of WommUninstallerInterface.plan_uninstall()."""

    def test_missing_target_fails(self, tmp_path: Path) -> None:
        """A target that doesn't exist is reported as 'not found'."""
        uninstaller = _bare_uninstaller()
        uninstaller.target_path = tmp_path / "missing"

        plan = uninstaller.plan_uninstall()

        assert isinstance(plan, UninstallPlanResult)
        assert plan.success is False
        assert plan.error == "WOMM installation not found"

    def test_success_lists_files(self, tmp_path: Path) -> None:
        """An existing target yields the removal manifest."""
        target = tmp_path / "target"
        (target / "womm").mkdir(parents=True)
        (target / "womm" / "app.py").write_text("x", encoding="utf-8")
        uninstaller = _bare_uninstaller()
        uninstaller.target_path = target

        plan = uninstaller.plan_uninstall()

        assert plan.success is True
        assert str(Path("womm") / "app.py") in (plan.files_to_remove or [])

    def test_scan_failure_is_translated_to_failure_result(self, tmp_path: Path) -> None:
        """A target that is a file, not a directory, fails the scan cleanly."""
        target = tmp_path / "target"
        target.write_text("not a directory", encoding="utf-8")
        uninstaller = _bare_uninstaller()
        uninstaller.target_path = target

        plan = uninstaller.plan_uninstall()

        assert plan.success is False
        assert "Failed to scan installation directory" in plan.error


# ///////////////////////////////////////////////////////////////
# TESTS - EXECUTE_UNINSTALL
# ///////////////////////////////////////////////////////////////


class TestExecuteUninstall:
    """Boundary behaviour of WommUninstallerInterface.execute_uninstall()."""

    def _planned_uninstaller(
        self, tmp_path: Path
    ) -> tuple[WommUninstallerInterface, UninstallPlanResult]:
        target = tmp_path / "target"
        (target / "womm").mkdir(parents=True)
        (target / "womm" / "app.py").write_text("x", encoding="utf-8")
        uninstaller = _bare_uninstaller()
        uninstaller.target_path = target
        plan = uninstaller.plan_uninstall()
        assert plan.success is True
        return uninstaller, plan

    def test_success_removes_files_and_returns_result(self, tmp_path: Path) -> None:
        """A full run (PATH/verification steps stubbed) removes the target."""
        uninstaller, plan = self._planned_uninstaller(tmp_path)
        uninstaller._cleanup_path = lambda: None
        uninstaller._verify_uninstallation_with_progress = lambda _reporter: None
        reporter = _FakeReporter()

        result = uninstaller.execute_uninstall(plan, reporter)

        assert isinstance(result, UninstallationResult)
        assert result.success is True
        assert result.files_removed == len(plan.files_to_remove or [])
        assert not Path(plan.target_path).exists()
        assert reporter.completed("main_uninstallation")
        assert not reporter.stopped()

    def test_cleanup_failure_is_translated_to_failure_result(
        self, tmp_path: Path
    ) -> None:
        """A WommDeploymentServiceError from PATH cleanup becomes a failed Result."""
        uninstaller, plan = self._planned_uninstaller(tmp_path)

        def _raise_cleanup() -> None:
            raise WommDeploymentServiceError(
                operation="cleanup", reason="registry busy"
            )

        uninstaller._cleanup_path = _raise_cleanup
        reporter = _FakeReporter()

        result = uninstaller.execute_uninstall(plan, reporter)

        assert result.success is False
        assert "registry busy" in result.error
        assert reporter.stopped()
        # Cleanup failed before any file was removed.
        assert Path(plan.target_path).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
