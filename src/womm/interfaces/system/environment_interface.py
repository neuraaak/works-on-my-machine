#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM ENVIRONMENT INTERFACE - Environment Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System Environment Interface for Works On My Machine.

Orchestrates SystemEnvironmentService and translates its exception into a Result.
This interface carries no UI: it does not print, log, or drive spinners — the
command layer owns presentation (spinner + renderer). It never re-raises; the
single service exception is converted into a Result (or a best-effort bool for
verification).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import platform

# Local imports
from ...exceptions.system import EnvironmentServiceError
from ...services import SystemEnvironmentService
from ...shared.results import EnvironmentRefreshResult

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class SystemEnvironmentInterface:
    """Orchestrates SystemEnvironmentService and returns a Result.

    Pure orchestration: no UI, no re-raise. The service's
    ``EnvironmentServiceError`` is translated into an ``EnvironmentRefreshResult``
    (the single exception→Result conversion point). Unexpected errors are not
    swallowed — they propagate.
    """

    def __init__(self) -> None:
        """Initialize the interface (service is created lazily)."""
        self.platform = platform.system().lower()
        self._environment_service: SystemEnvironmentService | None = None

    @property
    def environment_service(self) -> SystemEnvironmentService:
        """Lazy load SystemEnvironmentService when needed."""
        if self._environment_service is None:
            self._environment_service = SystemEnvironmentService()
        return self._environment_service

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def refresh_environment(self) -> EnvironmentRefreshResult:
        """
        Refresh environment variables from registry/system.

        Returns:
            EnvironmentRefreshResult: success/failure; failure carries the error.
        """
        try:
            return self.environment_service.refresh_environment()
        except EnvironmentServiceError as e:
            return EnvironmentRefreshResult(
                success=False,
                message="Environment refresh failed",
                error=str(e),
                platform=self.platform,
            )

    def verify_environment_refresh(self, command: str = "womm") -> bool:
        """
        Verify that environment refresh worked by testing command accessibility.

        This is best-effort: any service failure yields ``False`` rather than
        propagating.

        Args:
            command: Command to test (default: "womm")

        Returns:
            bool: True if the command is accessible, False otherwise.
        """
        try:
            result = self.environment_service.verify_environment_refresh(command)
            return result.success and result.command_accessible
        except EnvironmentServiceError:
            return False

    def get_environment_info(self) -> dict[str, str]:
        """
        Get current environment information.

        Returns:
            Dict[str, str]: Dictionary of environment information
        """
        return self.environment_service.get_environment_info()


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["SystemEnvironmentInterface"]
