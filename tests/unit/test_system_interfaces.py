#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SYSTEM INTERFACES - Boundary tests for the exception->Result contract
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Boundary tests for the system interfaces.

These verify the exception-rework contract at the interface layer: a service
raising its single exception is translated into a Result (never re-raised), and
the success path carries the service data through. Fake services are injected
directly so the tests exercise only the interface's translation logic.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
import pytest

# Local imports
from womm.exceptions.system import DetectorServiceError, EnvironmentServiceError
from womm.interfaces.system.detector_interface import SystemDetectorInterface
from womm.interfaces.system.environment_interface import SystemEnvironmentInterface
from womm.shared.results import (
    EnvironmentRefreshResult,
    EnvironmentVerificationResult,
    SystemDetectionResult,
)

# ///////////////////////////////////////////////////////////////
# FAKE SERVICES
# ///////////////////////////////////////////////////////////////


class _FakeDetectorService:
    """Stand-in for SystemDetectorService with a scriptable get_system_data."""

    def __init__(self, data: dict | None = None, error: Exception | None = None):
        self._data = data or {}
        self._error = error

    def get_system_data(self) -> dict:
        if self._error is not None:
            raise self._error
        return self._data


class _FakeEnvironmentService:
    """Stand-in for SystemEnvironmentService for refresh/verify."""

    def __init__(
        self,
        refresh: EnvironmentRefreshResult | None = None,
        verify: EnvironmentVerificationResult | None = None,
        error: Exception | None = None,
    ):
        self._refresh = refresh
        self._verify = verify
        self._error = error

    def refresh_environment(self) -> EnvironmentRefreshResult:
        if self._error is not None:
            raise self._error
        assert self._refresh is not None
        return self._refresh

    def verify_environment_refresh(self, command: str) -> EnvironmentVerificationResult:
        if self._error is not None:
            raise self._error
        assert self._verify is not None
        return self._verify


# ///////////////////////////////////////////////////////////////
# TESTS - DETECTOR INTERFACE
# ///////////////////////////////////////////////////////////////


class TestSystemDetectorInterface:
    """Boundary behaviour of SystemDetectorInterface.detect_system()."""

    def test_success_returns_result_with_data(self):
        """A service returning data yields a successful Result carrying it."""
        interface = SystemDetectorInterface()
        interface._detector = _FakeDetectorService(data={"system_info": {"x": 1}})

        result = interface.detect_system()

        assert isinstance(result, SystemDetectionResult)
        assert result.success is True
        assert result.system_data == {"system_info": {"x": 1}}

    def test_service_error_is_translated_to_failure_result(self):
        """A DetectorServiceError becomes a failed Result, never re-raised."""
        interface = SystemDetectorInterface()
        interface._detector = _FakeDetectorService(
            error=DetectorServiceError(
                operation="platform_info", reason="boom", details="ctx"
            )
        )

        result = interface.detect_system()

        assert isinstance(result, SystemDetectionResult)
        assert result.success is False
        assert "boom" in result.error
        assert result.system_data == {}


# ///////////////////////////////////////////////////////////////
# TESTS - ENVIRONMENT INTERFACE
# ///////////////////////////////////////////////////////////////


class TestSystemEnvironmentInterface:
    """Boundary behaviour of SystemEnvironmentInterface."""

    def test_refresh_success_passes_result_through(self):
        """A successful service result is returned unchanged."""
        interface = SystemEnvironmentInterface()
        interface._environment_service = _FakeEnvironmentService(
            refresh=EnvironmentRefreshResult(success=True, refresh_method="registry")
        )

        result = interface.refresh_environment()

        assert isinstance(result, EnvironmentRefreshResult)
        assert result.success is True
        assert result.refresh_method == "registry"

    def test_refresh_service_error_is_translated_to_failure_result(self):
        """An EnvironmentServiceError becomes a failed Result, never re-raised."""
        interface = SystemEnvironmentInterface()
        interface._environment_service = _FakeEnvironmentService(
            error=EnvironmentServiceError(
                operation="refresh_windows_environment", reason="boom"
            )
        )

        result = interface.refresh_environment()

        assert isinstance(result, EnvironmentRefreshResult)
        assert result.success is False
        assert "boom" in result.error

    def test_verify_returns_true_when_accessible(self):
        """Verification returns True when the service reports the command reachable."""
        interface = SystemEnvironmentInterface()
        interface._environment_service = _FakeEnvironmentService(
            verify=EnvironmentVerificationResult(success=True, command_accessible=True)
        )

        assert interface.verify_environment_refresh("womm") is True

    def test_verify_service_error_returns_false(self):
        """Verification is best-effort: a service error yields False, not a raise."""
        interface = SystemEnvironmentInterface()
        interface._environment_service = _FakeEnvironmentService(
            error=EnvironmentServiceError(operation="verify", reason="boom")
        )

        assert interface.verify_environment_refresh("womm") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
