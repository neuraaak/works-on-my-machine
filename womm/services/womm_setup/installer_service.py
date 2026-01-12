#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INSTALLATION SERVICE - Installation Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Installation Service - Singleton service for installation operations.

Handles installation verification operations that require service dependencies:
- PATH configuration verification (uses SystemPathService)
- Command accessibility verification (uses CommandRunnerService)
- Executable verification (uses CommandRunnerService)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import platform
import tempfile
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.system import RegistryServiceError
from ...exceptions.womm_deployment import (
    ExeVerificationServiceError,
    PathUtilityError,
)
from ...shared.results import WOMMInstallerVerificationResult
from ..common.command_runner_service import CommandRunnerService
from ..system.path_service import SystemPathService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# INSTALLATION SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class WommInstallerService:
    """Singleton service for installation verification operations."""

    _instance: ClassVar[WommInstallerService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> WommInstallerService:
        """Create or return the singleton instance.

        Returns:
            InstallationService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize installation service (only once)."""
        if WommInstallerService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self._command_runner = CommandRunnerService()
        self._path_service = SystemPathService()
        WommInstallerService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def verify_path_configuration(
        self, entry_path: str
    ) -> WOMMInstallerVerificationResult:
        """
        Verify that WOMM is correctly configured in PATH.

        Args:
            entry_path: Path to WOMM installation directory

        Returns:
            InstallationVerificationResult: Verification result

        Raises:
            PathUtilityError: If PATH configuration verification fails
        """
        try:
            # Input validation
            if not entry_path:
                raise PathUtilityError(
                    operation="path_verification",
                    path="",
                    reason="Entry path cannot be empty",
                    details="Invalid entry path provided for PATH verification",
                )

            if platform.system() == "Windows":
                # Query Windows registry for PATH using SystemPathService
                try:
                    path_result = self._path_service.get_current_system_path()
                    if not path_result.success:
                        # Business logic error - return result
                        return WOMMInstallerVerificationResult(
                            success=False,
                            message=path_result.message or "Failed to get current PATH",
                            error=path_result.error or "",
                            entry_path=entry_path,
                            path_configured=False,
                            path_entries=[],
                        )
                    path_entries = path_result.path_entries or []

                except (RegistryServiceError, ValidationServiceError) as e:
                    # Critical error - raise exception
                    raise PathUtilityError(
                        operation="path_verification",
                        path=entry_path,
                        reason="Failed to query Windows registry",
                        details=f"Error: {e}",
                    ) from e

            else:
                # Check Unix shell configuration files
                shell_rc_files = [
                    Path.home() / ".bashrc",
                    Path.home() / ".zshrc",
                    Path.home() / ".profile",
                ]

                path_entries = []
                for rc_file in shell_rc_files:
                    try:
                        if rc_file.exists():
                            with open(rc_file, encoding="utf-8") as f:
                                content = f.read()
                                if entry_path in content:
                                    path_entries.append(str(rc_file))
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to check shell config {rc_file}: {e}"
                        )
                        continue

            # Normalize paths for comparison
            try:
                normalized_womm = str(Path(entry_path).resolve())
            except Exception as e:
                self.logger.warning(f"Failed to resolve entry path {entry_path}: {e}")
                normalized_womm = entry_path

            found_in_path = False

            if platform.system() == "Windows":
                try:
                    normalized_entries = [
                        str(Path(p).resolve()) for p in path_entries if p
                    ]
                    found_in_path = normalized_womm in normalized_entries
                except Exception as e:
                    self.logger.warning(
                        f"Failed to normalize Windows PATH entries: {e}"
                    )
                    found_in_path = entry_path in path_entries
            else:
                found_in_path = len(path_entries) > 0

            if not found_in_path:
                raise PathUtilityError(
                    operation="path_verification",
                    path=entry_path,
                    reason="WOMM path not found in system PATH",
                    details=f"Platform: {platform.system()}, Checked locations: {path_entries if platform.system() != 'Windows' else 'Registry'}",
                )

            return WOMMInstallerVerificationResult(
                success=True,
                message=f"PATH configuration verified successfully for: {entry_path}",
                entry_path=entry_path,
                path_configured=True,
                path_entries=path_entries if platform.system() == "Windows" else [],
            )

        except PathUtilityError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise PathUtilityError(
                operation="path_verification",
                path=entry_path,
                reason=f"Unexpected error during PATH verification: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def verify_commands_accessible(
        self, entry_path: str
    ) -> WOMMInstallerVerificationResult:
        """
        Verify that WOMM commands are accessible from PATH.

        Args:
            entry_path: Path to WOMM installation directory

        Returns:
            InstallationVerificationResult: Verification result

        Raises:
            ExecutableVerificationError: If executable is not accessible
        """
        try:
            # Input validation
            if not entry_path:
                raise ExeVerificationServiceError(
                    executable_name="womm",
                    reason="Entry path cannot be empty",
                    details="Invalid entry path provided for command verification",
                )

            # First test: Check if executable exists at the specified path
            if platform.system() == "Windows":
                local_executable = Path(entry_path) / "womm.bat"
                global_command = ["womm.bat", "--version"]
            else:
                local_executable = Path(entry_path) / "womm"
                global_command = ["womm", "--version"]

            # Test 1: Local executable exists and works
            if not local_executable.exists():
                raise ExeVerificationServiceError(
                    executable_name="womm",
                    reason=f"WOMM executable not found at {local_executable}",
                    details=f"Platform: {platform.system()}",
                )

            # Test local executable
            try:
                local_result = self._command_runner.run_silent(
                    [str(local_executable), "--version"], capture_output=True
                )
                local_works = local_result.returncode == 0
            except Exception as e:
                self.logger.warning(f"Failed to test local executable: {e}")
                local_works = False

            # Debug info for local test failure
            if not local_works:
                try:
                    # Clean stdout/stderr of problematic Unicode characters
                    stdout_clean = (
                        str(local_result.stdout)
                        .encode("ascii", "replace")
                        .decode("ascii")
                        if local_result.stdout
                        else "None"
                    )
                    stderr_clean = (
                        str(local_result.stderr)
                        .encode("ascii", "replace")
                        .decode("ascii")
                        if local_result.stderr
                        else "None"
                    )

                    debug_file = (
                        Path(tempfile.gettempdir()) / "womm_local_test_debug.txt"
                    )
                    with open(debug_file, "w", encoding="utf-8") as f:
                        f.write("Local executable test failed:\n")
                        f.write(f"Executable: {local_executable}\n")
                        f.write(f"Exists: {local_executable.exists()}\n")
                        f.write(f"Command: {[str(local_executable), '--version']}\n")
                        f.write(f"Return code: {local_result.returncode}\n")
                        f.write(f"Stdout: {stdout_clean}\n")
                        f.write(f"Stderr: {stderr_clean}\n")
                        if local_executable.exists():
                            f.write(f"File size: {local_executable.stat().st_size}\n")
                            try:
                                with open(
                                    local_executable, encoding="utf-8"
                                ) as exe_file:
                                    f.write(f"Content:\n{exe_file.read()}\n")
                            except Exception as e:
                                f.write(f"Could not read executable content: {e}\n")
                except Exception as e:
                    self.logger.warning(f"Failed to create debug file: {e}")

            # Test 2: Global accessibility via PATH
            try:
                global_result = self._command_runner.run_silent(
                    global_command, capture_output=True
                )
                global_works = global_result.returncode == 0
            except Exception as e:
                self.logger.warning(f"Failed to test global command: {e}")
                global_works = False

            # Logic for handling local vs global test results is handled below in unified way
            if local_works and global_works:
                # Handle stdout properly
                stdout_str = global_result.stdout
                if isinstance(stdout_str, bytes):
                    stdout_str = stdout_str.decode()

                return WOMMInstallerVerificationResult(
                    success=True,
                    message="WOMM commands are accessible both locally and globally",
                    entry_path=entry_path,
                    commands_accessible=True,
                    accessible_commands=["womm"],
                )
            elif local_works and not global_works:
                # Local works but global doesn't - this is common on Windows after fresh install
                return WOMMInstallerVerificationResult(
                    success=True,
                    message="WOMM executable works locally. Global command not yet accessible in current session (normal after fresh installation)",
                    entry_path=entry_path,
                    commands_accessible=True,
                    accessible_commands=["womm"],
                )
            else:
                # Both local and global failed - this is a real problem
                stderr_str = (
                    global_result.stderr if not global_works else local_result.stderr
                )
                if isinstance(stderr_str, bytes):
                    stderr_str = stderr_str.decode()

                # Clean stderr of problematic Unicode characters
                stderr_clean = (
                    stderr_str.encode("ascii", "replace").decode("ascii")
                    if stderr_str
                    else "None"
                )

                raise ExeVerificationServiceError(
                    executable_name="womm",
                    reason="WOMM command not accessible - both local and global tests failed",
                    details=f"Local: {local_works}, Global: {global_works}, stderr: {stderr_clean}",
                )

        except ExeVerificationServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            # Clean the error message of Unicode characters that can't be encoded
            error_msg = str(e).encode("ascii", "replace").decode("ascii")
            raise ExeVerificationServiceError(
                executable_name="womm",
                reason=f"Unexpected error during command verification: {error_msg}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def verify_executable_works(
        self, target_path: Path
    ) -> WOMMInstallerVerificationResult:
        """
        Verify that the WOMM executable works correctly.

        Args:
            target_path: Target installation directory

        Returns:
            InstallationVerificationResult: Verification result

        Raises:
            ExecutableVerificationError: If executable is missing or fails to work
        """
        try:
            # Input validation
            if not target_path or not target_path.exists():
                raise ExeVerificationServiceError(
                    executable_name="womm",
                    reason="Target path does not exist",
                    details=f"Target path: {target_path}",
                )

            if platform.system() == "Windows":
                executable_path = target_path / "womm.bat"
                test_command = [str(executable_path), "--version"]
            else:
                executable_path = target_path / "womm"
                test_command = [str(executable_path), "--version"]

            if not executable_path.exists():
                raise ExeVerificationServiceError(
                    executable_name="womm",
                    reason=f"Executable not found at {executable_path}",
                    details=f"Platform: {platform.system()}",
                )

            # Test the executable
            try:
                result = self._command_runner.run_silent(
                    test_command, capture_output=True
                )
            except Exception as e:
                raise ExeVerificationServiceError(
                    executable_name="womm",
                    reason=f"Failed to execute test command: {e}",
                    details=f"Command: {test_command}",
                ) from e

            if result.returncode == 0:
                # Handle stdout properly
                stdout_str = result.stdout
                if isinstance(stdout_str, bytes):
                    stdout_str = stdout_str.decode()

                return WOMMInstallerVerificationResult(
                    success=True,
                    message=f"WOMM executable verified successfully at {executable_path}",
                    entry_path=str(target_path),
                    executable_works=True,
                )
            else:
                # Handle stderr properly
                stderr_str = result.stderr
                if isinstance(stderr_str, bytes):
                    stderr_str = stderr_str.decode()

                raise ExeVerificationServiceError(
                    executable_name="womm",
                    reason=f"Executable test failed with code {result.returncode}",
                    details=f"stderr: {stderr_str}",
                )

        except ExeVerificationServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ExeVerificationServiceError(
                executable_name="womm",
                reason=f"Unexpected error during executable verification: {e}",
                details=f"Exception type: {type(e).__name__}, Target path: {target_path}",
            ) from e
