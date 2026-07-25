#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST DEPENDENCIES INTERFACES - Boundary tests for the Result contract
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Boundary tests for the dependencies interface.

These verify the exception-rework contract at the interface layer:
``DepsInterface`` never raises and never renders — every public method returns
a typed Result, and presentation is left to the ``ui`` layer. The ``probe``
primitive is patched so the tests exercise only the interface's own logic.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import inspect

# Third-party imports
import pytest

# Local imports
from womm.interfaces.dependencies import deps_interface as deps_module
from womm.interfaces.dependencies.deps_interface import DepsInterface
from womm.shared.results import (
    DependencyCheckResult,
    DependencyInventoryResult,
    DependencyStatusResult,
)
from womm.utils.dependencies import ProbeResult

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def all_available(monkeypatch):
    """Patch probe() so every executable looks installed."""

    def _probe(executable, *, version_flag="--version", detect_version=True):  # noqa: ARG001
        return ProbeResult(
            name=executable,
            available=True,
            path=f"/usr/bin/{executable}",
            version="1.2.3" if detect_version else None,
        )

    monkeypatch.setattr(deps_module, "probe", _probe)
    return _probe


@pytest.fixture
def none_available(monkeypatch):
    """Patch probe() so nothing looks installed."""

    def _probe(executable, *, version_flag="--version", detect_version=True):  # noqa: ARG001
        return ProbeResult(name=executable, available=False)

    monkeypatch.setattr(deps_module, "probe", _probe)
    return _probe


# ///////////////////////////////////////////////////////////////
# TESTS - ZERO-UI CONTRACT
# ///////////////////////////////////////////////////////////////


class TestZeroUiContract:
    """The interface must not reach into the ui layer."""

    def test_module_never_imports_ui(self):
        """Rendering belongs to the caller, not to the interface."""
        source = inspect.getsource(deps_module)

        assert "ui.system" not in source
        assert "ui.common" not in source
        assert "ezprinter" not in source


# ///////////////////////////////////////////////////////////////
# TESTS - CHECK ALL
# ///////////////////////////////////////////////////////////////


class TestCheckAll:
    """Boundary behaviour of DepsInterface.check_all()."""

    def test_returns_a_typed_result(self, all_available):
        result = DepsInterface().check_all()

        assert isinstance(result, DependencyCheckResult)
        assert result.success is True
        assert result.runtime, "runtimes are configured, so they must be reported"

    def test_missing_dependencies_are_data_not_failure(self, none_available):
        """A missing tool is a finding; the check itself still succeeded."""
        result = DepsInterface().check_all()

        assert result.success is True
        assert result.system_ok is False
        assert result.runtime_ok is False
        assert all(entry.available is False for entry in result.tools)

    def test_availability_flags_reflect_the_probes(self, all_available):
        result = DepsInterface().check_all()

        assert result.system_ok is True
        assert result.runtime_ok is True

    def test_versions_only_resolved_when_requested(self, all_available):
        without = DepsInterface().check_all(detect_versions=False)
        with_versions = DepsInterface().check_all(detect_versions=True)

        assert all(entry.version is None for entry in without.system)
        assert all(entry.version == "1.2.3" for entry in with_versions.system)


# ///////////////////////////////////////////////////////////////
# TESTS - SHOW STATUS
# ///////////////////////////////////////////////////////////////


class TestShowStatus:
    """Boundary behaviour of DepsInterface.show_status()."""

    def test_returns_a_typed_result(self, all_available):
        result = DepsInterface().show_status()

        assert isinstance(result, DependencyStatusResult)
        assert result.success is True

    def test_reports_managers_unsupported_on_this_platform(self, all_available):
        """Unlike check_all(), status covers every configured manager."""
        result = DepsInterface().show_status()

        assert any(not m.supported_on_current_platform for m in result.system), (
            "at least one configured manager targets another platform"
        )
        for manager in result.system:
            if not manager.supported_on_current_platform:
                assert manager.available is False
                assert manager.version is None


# ///////////////////////////////////////////////////////////////
# TESTS - LIST ALL
# ///////////////////////////////////////////////////////////////


class TestListAll:
    """Boundary behaviour of DepsInterface.list_all()."""

    def test_returns_a_typed_result_without_probing(self, monkeypatch):
        """The inventory is static: it must not touch probe() at all."""

        def _explode(*args, **kwargs):  # noqa: ARG001
            raise AssertionError("list_all() must not probe the machine")

        monkeypatch.setattr(deps_module, "probe", _explode)

        result = DepsInterface().list_all()

        assert isinstance(result, DependencyInventoryResult)
        assert result.success is True
        assert result.platform in {"windows", "darwin", "linux"}
        assert result.runtime, "runtimes are configured, so they must be listed"
        assert result.tools, "dev tools are configured, so they must be listed"
