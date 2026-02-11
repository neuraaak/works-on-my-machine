#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UNINSTALLATION SERVICE - Uninstallation Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Uninstallation Service - Singleton service for uninstallation operations.

Handles uninstallation verification operations that require service dependencies:
- Complete uninstallation verification (uses CommandRunnerService)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.womm_deployment import VerificationServiceError
from ...shared.result_models import WOMMInstallerVerificationResult
from ..common.command_runner_service import CommandRunnerService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# UNINSTALLATION SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class WommUninstallerService:
    """Singleton service for uninstallation verification operations."""

    _instance: ClassVar[WommUninstallerService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> WommUninstallerService:
        """Create or return the singleton instance.

        Returns:
            UninstallationService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize uninstallation service (only once)."""
        if WommUninstallerService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self._command_runner = CommandRunnerService()
        WommUninstallerService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def verify_uninstallation_complete(
        self, target_path: Path
    ) -> WOMMInstallerVerificationResult:
        """
        Verify that uninstallation completed successfully.

        Args:
            target_path: Target installation directory

        Returns:
            InstallationVerificationResult: Result with success status and details

        Raises:
            UninstallationVerificationError: If uninstallation verification fails
        """
        try:
            # Input validation
            if not target_path:
                raise VerificationServiceError(
                    verification_type="completion_verification",
                    target_path="",
                    reason="Target path cannot be empty",
                    details="Invalid target path provided for completion verification",
                )

            # Check that target directory is gone (handled by utils)
            # This service only handles command verification

            # Simple check that womm command is no longer accessible
            try:
                cmd_result = self._command_runner.run_silent(
                    ["womm", "--version"], timeout=10
                )
            except Exception as e:
                # If command execution fails, that's actually success (command not found)
                self.logger.info(f"Command execution failed (expected): {e}")
                return WOMMInstallerVerificationResult(
                    success=True,
                    message="WOMM command no longer accessible (execution failed)",
                    entry_path=str(target_path),
                    executable_works=False,
                )

            # If command is not found (exit code 9009 on Windows), that's success
            if cmd_result.returncode == 9009:  # Command not found on Windows
                return WOMMInstallerVerificationResult(
                    success=True,
                    message="WOMM command no longer accessible",
                    entry_path=str(target_path),
                    executable_works=False,
                )
            else:
                # Command still found, but this might be from another installation
                return WOMMInstallerVerificationResult(
                    success=True,  # Don't fail uninstallation for this
                    message="WOMM command still accessible (may be from another installation)",
                    entry_path=str(target_path),
                    executable_works=True,
                )

        except VerificationServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"verify_uninstallation_complete failed: {e}")
            # Wrap unexpected external exceptions
            raise VerificationServiceError(
                message=f"Uninstallation verification error: {e}",
                verification_type="unexpected_error",
                target_path=str(target_path),
                details=f"Exception type: {type(e).__name__}",
            ) from e
