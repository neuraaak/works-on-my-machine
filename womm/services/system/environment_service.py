#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM ENVIRONMENT SERVICE - System Environment Service (Singleton)
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
SystemEnvironmentService - Service for environment refresh and management.

Provides cross-platform environment refresh capabilities, including:
- Windows registry-based refresh
- Unix shell configuration reload
- Environment verification
- Environment information retrieval
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import contextlib
import logging
import os
import platform
import tempfile
import time
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.system import EnvironmentServiceError
from ...shared.configs.system.system_environment_config import SystemEnvironmentConfig
from ...shared.results.system_results import (
    EnvironmentRefreshResult,
    EnvironmentVerificationResult,
)
from ...utils.system import (
    combine_paths,
    get_environment_info,
    get_shell_config_files,
    read_windows_registry_path,
)
from ...utils.womm_setup import get_default_womm_path
from ..common.command_runner_service import CommandRunnerService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)
_command_runner = CommandRunnerService()


# ///////////////////////////////////////////////////////////////
# SYSTEM ENVIRONMENT SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class SystemEnvironmentService:
    """Cross-platform environment refresh service (singleton)."""

    _instance: ClassVar[SystemEnvironmentService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> SystemEnvironmentService:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the system environment service once."""
        if SystemEnvironmentService._initialized:
            return
        SystemEnvironmentService._initialized = True
        self.platform = platform.system().lower()

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def refresh_environment(self) -> EnvironmentRefreshResult:
        """
        Refresh environment variables from registry/system.

        Returns:
            EnvironmentRefreshResult: Result of the refresh operation

        Raises:
            EnvironmentRefreshError: If environment refresh fails
        """
        start_time = time.time()
        try:
            if self.platform == "windows":
                return self._refresh_windows_environment(start_time)
            else:
                return self._refresh_unix_environment(start_time)
        except EnvironmentServiceError:
            raise
        except Exception as e:
            raise EnvironmentServiceError(
                operation="refresh_environment",
                reason=f"Unexpected error during environment refresh: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def verify_environment_refresh(
        self, command: str | None = None
    ) -> EnvironmentVerificationResult:
        """
        Verify that environment refresh was successful by testing command accessibility.

        On Windows, this executes RefreshEnv.cmd in a new cmd.exe session and tests
        the command in that same session to ensure the PATH is updated.

        Args:
            command: Command to test (default: SystemEnvironmentConfig.DEFAULT_VERIFICATION_COMMAND)

        Returns:
            EnvironmentVerificationResult: Result of the verification operation

        Raises:
            EnvironmentRefreshError: If verification fails critically
        """
        start_time = time.time()
        if command is None:
            command = SystemEnvironmentConfig.DEFAULT_VERIFICATION_COMMAND

        try:
            if self.platform == "windows":
                return self._verify_windows_environment(command, start_time)
            else:
                return self._verify_unix_environment(command, start_time)
        except EnvironmentServiceError:
            raise
        except Exception as e:
            logger.warning(f"Could not verify environment refresh: {e}")
            return EnvironmentVerificationResult(
                success=False,
                message=f"Verification failed: {e}",
                error=str(e),
                command=command,
                command_accessible=False,
                verification_method="unknown",
                verification_time=time.time() - start_time,
            )

    def get_environment_info(self) -> dict[str, str]:
        """
        Get current environment information.

        Returns:
            Dict[str, str]: Dictionary of environment information
        """
        return get_environment_info()

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS - WINDOWS
    # ///////////////////////////////////////////////////////////////

    def _refresh_windows_environment(
        self, start_time: float
    ) -> EnvironmentRefreshResult:
        """
        Refresh Windows environment variables from registry.

        Args:
            start_time: Start time of the refresh operation

        Returns:
            EnvironmentRefreshResult: Result of the refresh operation

        Raises:
            EnvironmentRefreshError: If registry access fails critically
        """
        try:
            hklm_path, hkcu_path = read_windows_registry_path()
            combined_path = combine_paths(hklm_path, hkcu_path)

            # Business logic: PATH empty - return result with success=False
            if not combined_path:
                return EnvironmentRefreshResult(
                    success=False,
                    message="Could not read PATH from registry",
                    error="Both HKLM and HKCU PATH values were empty or None",
                    platform=self.platform,
                    refresh_method="registry",
                    path_refreshed=False,
                    environment_info=get_environment_info(),
                    refresh_time=time.time() - start_time,
                )

            # Update current process environment
            os.environ["PATH"] = combined_path

            logger.info("Environment variables refreshed from registry")
            return EnvironmentRefreshResult(
                success=True,
                message="Environment variables refreshed from registry",
                platform=self.platform,
                refresh_method="registry",
                path_refreshed=True,
                environment_info=get_environment_info(),
                refresh_time=time.time() - start_time,
            )

        except (OSError, PermissionError) as e:
            # Critical system errors - raise exception
            raise EnvironmentServiceError(
                operation="refresh_windows_environment",
                reason=f"Windows environment refresh failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e
        except Exception as e:
            # Wrap unexpected external exceptions - critical error
            raise EnvironmentServiceError(
                operation="refresh_windows_environment",
                reason=f"Windows environment refresh failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _verify_windows_environment(
        self, command: str, start_time: float
    ) -> EnvironmentVerificationResult:
        """
        Verify Windows environment refresh using RefreshEnv.cmd.

        Args:
            command: Command to test
            start_time: Start time of the verification operation

        Returns:
            EnvironmentVerificationResult: Result of the verification operation
        """
        try:
            # Get RefreshEnv.cmd path from installed location
            # Files are installed in target_path/womm/bin/ (not target_path/bin/)
            target_path = get_default_womm_path()
            refresh_env_cmd = (
                target_path
                / "womm"
                / "bin"
                / SystemEnvironmentConfig.REFRESH_ENV_SCRIPT_NAME
            )

            if not refresh_env_cmd.exists() or not refresh_env_cmd.is_file():
                logger.warning(
                    f"RefreshEnv.cmd not found at {refresh_env_cmd}, falling back to direct test"
                )
                return self._verify_direct_command(command, start_time)

            # Resolve path for security
            refresh_env_cmd = refresh_env_cmd.resolve()

            # Create a temporary batch script that:
            # 1. Calls RefreshEnv.cmd to refresh environment
            # 2. Tests command --version in the same session
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".bat",
                delete=False,
                encoding="utf-8",
            ) as temp_script:
                temp_script_path = Path(temp_script.name).resolve()
                # Write script that calls RefreshEnv then tests command
                temp_script.write("@echo off\n")
                temp_script.write(f'call "{refresh_env_cmd}"\n')
                temp_script.write(
                    f"{command} {' '.join(SystemEnvironmentConfig.VERIFICATION_COMMAND_ARGS)}\n"
                )
                temp_script.write("if errorlevel 1 exit /b 1\n")
                temp_script.write("exit /b 0\n")

            try:
                # Execute in a new cmd.exe session
                cmd_exe = Path(
                    os.environ.get("COMSPEC", "C:\\Windows\\System32\\cmd.exe")
                )
                if not cmd_exe.is_file():
                    logger.warning(f"cmd.exe not found: {cmd_exe}")
                    return EnvironmentVerificationResult(
                        success=False,
                        message=f"cmd.exe not found: {cmd_exe}",
                        error="cmd.exe not found",
                        command=command,
                        command_accessible=False,
                        verification_method="refresh_env_cmd",
                        verification_time=time.time() - start_time,
                        temp_script_path=str(temp_script_path),
                    )

                result = _command_runner.run_silent(
                    [str(cmd_exe), "/c", str(temp_script_path)],
                    timeout=SystemEnvironmentConfig.VERIFICATION_TIMEOUT,
                    encoding="utf-8",
                    errors="replace",
                )

                if result.returncode == 0:
                    logger.info(
                        f"Environment refresh verification successful - {command} is accessible"
                    )
                    return EnvironmentVerificationResult(
                        success=True,
                        message=f"Environment refresh verification successful - {command} is accessible",
                        command=command,
                        command_accessible=True,
                        verification_method="refresh_env_cmd",
                        verification_time=time.time() - start_time,
                        temp_script_path=str(temp_script_path),
                    )
                else:
                    logger.warning(
                        f"Environment refresh completed but {command} verification failed"
                    )
                    return EnvironmentVerificationResult(
                        success=False,
                        message=f"Environment refresh completed but {command} verification failed",
                        error=f"Command returned exit code {result.returncode}",
                        command=command,
                        command_accessible=False,
                        verification_method="refresh_env_cmd",
                        verification_time=time.time() - start_time,
                        temp_script_path=str(temp_script_path),
                    )
            finally:
                # Clean up temp script
                with contextlib.suppress(Exception):
                    temp_script_path.unlink()

        except Exception as e:
            logger.warning(
                f"Could not verify environment refresh with RefreshEnv.cmd: {e}"
            )
            # Fallback to direct test
            return self._verify_direct_command(command, start_time)

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS - UNIX
    # ///////////////////////////////////////////////////////////////

    def _refresh_unix_environment(self, start_time: float) -> EnvironmentRefreshResult:
        """
        Refresh Unix environment variables.

        Args:
            start_time: Start time of the refresh operation

        Returns:
            EnvironmentRefreshResult: Result of the refresh operation

        Raises:
            EnvironmentRefreshError: If shell configuration reload fails
        """
        try:
            # On Unix systems, environment refresh is typically handled by the shell
            # We can try to reload shell configuration files
            shell_configs = get_shell_config_files()

            if not shell_configs:
                logger.info(
                    "No shell configuration files found, environment refresh skipped"
                )
                return EnvironmentRefreshResult(
                    success=True,
                    message="No shell configuration files found, environment refresh skipped",
                    platform=self.platform,
                    refresh_method="none",
                    path_refreshed=False,
                    environment_info=get_environment_info(),
                    refresh_time=time.time() - start_time,
                )

            # Try to reload shell configuration using bash
            import shutil

            bash_path = shutil.which("bash")
            if not bash_path:
                logger.info("bash not available, environment refresh skipped")
                return EnvironmentRefreshResult(
                    success=True,
                    message="bash not available, environment refresh skipped",
                    platform=self.platform,
                    refresh_method="none",
                    path_refreshed=False,
                    environment_info=get_environment_info(),
                    refresh_time=time.time() - start_time,
                )

            # Try to source each config file
            for config_file in shell_configs:
                try:
                    result = _command_runner.run_silent(
                        [bash_path, "-c", f"source {config_file}"]
                    )
                    if result.returncode == 0:
                        logger.info(f"Reloaded shell configuration: {config_file}")
                        return EnvironmentRefreshResult(
                            success=True,
                            message=f"Reloaded shell configuration: {config_file}",
                            platform=self.platform,
                            refresh_method="shell_config",
                            path_refreshed=True,
                            environment_info=get_environment_info(),
                            refresh_time=time.time() - start_time,
                        )
                except Exception as e:
                    logger.debug(f"Could not reload {config_file}: {e}")
                    continue

            logger.info("Unix environment refresh completed (no configs reloaded)")
            return EnvironmentRefreshResult(
                success=True,
                message="Unix environment refresh completed",
                platform=self.platform,
                refresh_method="shell_config",
                path_refreshed=False,
                environment_info=get_environment_info(),
                refresh_time=time.time() - start_time,
            )

        except Exception as e:
            raise EnvironmentServiceError(
                operation="refresh_unix_environment",
                reason=f"Unix environment refresh failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _verify_unix_environment(
        self, command: str, start_time: float
    ) -> EnvironmentVerificationResult:
        """
        Verify Unix environment refresh using direct command test.

        Args:
            command: Command to test
            start_time: Start time of the verification operation

        Returns:
            EnvironmentVerificationResult: Result of the verification operation
        """
        return self._verify_direct_command(command, start_time)

    def _verify_direct_command(
        self, command: str, start_time: float
    ) -> EnvironmentVerificationResult:
        """
        Verify command accessibility using direct test.

        Args:
            command: Command to test
            start_time: Start time of the verification operation

        Returns:
            EnvironmentVerificationResult: Result of the verification operation
        """
        try:
            result = _command_runner.run_silent(
                [command, *SystemEnvironmentConfig.VERIFICATION_COMMAND_ARGS]
            )
            if result.returncode == 0:
                logger.info(
                    f"Environment refresh verification successful - {command} is accessible"
                )
                return EnvironmentVerificationResult(
                    success=True,
                    message=f"Environment refresh verification successful - {command} is accessible",
                    command=command,
                    command_accessible=True,
                    verification_method="direct_test",
                    verification_time=time.time() - start_time,
                )
            else:
                logger.warning(
                    f"Environment refresh completed but {command} not yet accessible in current session"
                )
                return EnvironmentVerificationResult(
                    success=False,
                    message=f"Environment refresh completed but {command} not yet accessible in current session",
                    error=f"Command returned exit code {result.returncode}",
                    command=command,
                    command_accessible=False,
                    verification_method="direct_test",
                    verification_time=time.time() - start_time,
                )
        except Exception as e:
            logger.warning(f"Could not verify command {command}: {e}")
            return EnvironmentVerificationResult(
                success=False,
                message=f"Could not verify command {command}: {e}",
                error=str(e),
                command=command,
                command_accessible=False,
                verification_method="direct_test",
                verification_time=time.time() - start_time,
            )
