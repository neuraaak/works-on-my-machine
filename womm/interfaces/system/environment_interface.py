#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM ENVIRONMENT INTERFACE - Environment Manager Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Environment Manager Interface for Works On My Machine.

Handles environment variable refresh and management with integrated UI.
Provides cross-platform environment management capabilities.

This interface orchestrates SystemEnvironmentService and converts service
exceptions to interface exceptions following the MEF pattern.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import platform
from time import sleep

# Local imports
from ...exceptions.system import (
    EnvironmentInterfaceError,
    EnvironmentServiceError,
)
from ...services import SystemEnvironmentService
from ...shared.results.system_results import EnvironmentRefreshResult
from ...ui.common.ezpl_bridge import (
    ezlogger,
    ezprinter,
)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class SystemEnvironmentInterface:
    """Manages environment variable refresh and management with integrated UI.

    This interface orchestrates SystemEnvironmentService and converts service
    exceptions to interface exceptions following the MEF pattern.
    """

    def __init__(self) -> None:
        """Initialize the EnvironmentManagerInterface."""
        # Lazy initialization to avoid slow startup
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
            EnvironmentRefreshResult: Result of the environment refresh operation

        Raises:
            EnvironmentManagerInterfaceError: If environment refresh fails
        """
        try:
            result = self.environment_service.refresh_environment()
            return result
        except EnvironmentServiceError as e:
            ezlogger.error(f"Service error in refresh_environment: {e}")
            raise EnvironmentInterfaceError(
                message=f"Environment refresh failed: {e}",
                operation="refresh_environment",
                details=f"Service exception: {type(e).__name__}",
            ) from e
        except Exception as e:
            ezlogger.error(f"Unexpected error in refresh_environment: {e}")
            raise EnvironmentInterfaceError(
                message=f"Environment refresh failed: {e}",
                operation="refresh_environment",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def verify_environment_refresh(self, command: str = "womm") -> bool:
        """
        Verify that environment refresh was successful by testing command accessibility.

        Args:
            command: Command to test (default: "womm")

        Returns:
            bool: True if command is accessible, False otherwise

        Raises:
            EnvironmentManagerInterfaceError: If verification fails critically
        """
        try:
            result = self.environment_service.verify_environment_refresh(command)
            return result.success and result.command_accessible
        except EnvironmentServiceError as e:
            ezlogger.error(f"Service error in verify_environment_refresh: {e}")
            raise EnvironmentInterfaceError(
                message=f"Environment verification failed: {e}",
                operation="verify_environment_refresh",
                details=f"Service exception: {type(e).__name__}",
            ) from e
        except Exception as e:
            ezlogger.warning(f"Could not verify environment refresh: {e}")
            return False

    def get_environment_info(self) -> dict[str, str]:
        """
        Get current environment information.

        Returns:
            Dict[str, str]: Dictionary of environment information
        """
        return self.environment_service.get_environment_info()

    def refresh_environment_with_ui(self) -> bool:
        """
        Refresh environment variables with user interface feedback.

        Returns:
            bool: True if refresh was successful, False otherwise
        """
        with ezprinter.create_spinner_with_status(
            "Refreshing environment variables..."
        ) as (progress, task):
            progress.update(
                task,
                description="Refreshing environment variables...",
                status="Initializing...",
            )
            sleep(1)
            progress.update(task, status="Reading registry/system configuration...")
            sleep(2)
            try:
                success = self.refresh_environment()
                if success:
                    progress.update(task, status="Environment refreshed successfully!")
            except EnvironmentInterfaceError as e:
                ezlogger.error(f"Environment refresh failed: {e}")
                progress.update(task, status="Environment refresh failed.")
                success = False

        if success:
            # Verify the refresh worked
            if self.verify_environment_refresh():
                ezprinter.info("WOMM should now be accessible in the current session")
            else:
                ezprinter.warning(
                    "Environment refreshed but WOMM may not be accessible in current session"
                )
                ezprinter.info(
                    "Solution: Restart your terminal or open a new command prompt"
                )
        else:
            ezprinter.error("Environment refresh failed")
            ezprinter.info(
                "This means WOMM may not be accessible in the current session"
            )
            ezprinter.info(
                "Solution: Restart your terminal or run 'refreshenv' manually"
            )

        return success


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["SystemEnvironmentInterface"]
