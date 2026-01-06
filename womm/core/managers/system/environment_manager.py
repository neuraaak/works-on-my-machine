#!/usr/bin/env python3
"""
Environment Manager for Works On My Machine.

Handles environment variable refresh and management with integrated UI.
Provides cross-platform environment management capabilities.

Author: WOMM Team
"""

# =============================================================================
# IMPORTS
# =============================================================================
# Standard library imports
import logging
import os
import platform
from typing import Dict

# Third-party imports
# (None for this file)
# Local imports
from ...exceptions.system import EnvironmentRefreshError
from ...ui.common.console import print_error, print_info, print_success, print_warn
from ...utils.cli_utils import run_silent

# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# MAIN CLASS
# =============================================================================


class EnvironmentManager:
    """Manages environment variable refresh and management with integrated UI."""

    def __init__(self):
        """Initialize the EnvironmentManager."""
        self.platform = platform.system().lower()

    def refresh_environment(self) -> bool:
        """
        Refresh environment variables from registry/system.

        Returns:
            bool: True if refresh was successful, False otherwise

        Raises:
            EnvironmentRefreshError: If environment refresh fails
        """
        try:
            if self.platform == "windows":
                return self._refresh_windows_environment()
            else:
                return self._refresh_unix_environment()
        except Exception as e:
            raise EnvironmentRefreshError(
                operation="environment_refresh",
                reason=f"Environment refresh failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _refresh_windows_environment(self) -> bool:
        """
        Refresh Windows environment variables from registry.

        Returns:
            bool: True if refresh was successful, False otherwise
        """
        try:
            import winreg

            # Read PATH from both HKLM and HKCU
            hklm_path = ""
            hkcu_path = ""

            try:
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"System\CurrentControlSet\Control\Session Manager\Environment",
                ) as key:
                    hklm_path = winreg.QueryValueEx(key, "Path")[0]
            except (FileNotFoundError, OSError):
                logger.warning("Could not read HKLM PATH from registry")

            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                    hkcu_path = winreg.QueryValueEx(key, "Path")[0]
            except (FileNotFoundError, OSError):
                logger.warning("Could not read HKCU PATH from registry")

            # Combine paths
            if hklm_path and hkcu_path:
                combined_path = f"{hklm_path};{hkcu_path}"
            elif hklm_path:
                combined_path = hklm_path
            elif hkcu_path:
                combined_path = hkcu_path
            else:
                logger.warning("Could not read PATH from registry")
                return False

            # Update current process environment
            os.environ["PATH"] = combined_path

            logger.info("Environment variables refreshed from registry")
            return True

        except Exception as e:
            logger.error(f"Windows environment refresh failed: {e}")
            return False

    def _refresh_unix_environment(self) -> bool:
        """
        Refresh Unix environment variables.

        Returns:
            bool: True if refresh was successful, False otherwise
        """
        # On Unix systems, environment refresh is typically handled by the shell
        # We can try to reload shell configuration files
        try:
            # Try to reload common shell configuration files
            shell_configs = [
                os.path.expanduser("~/.bashrc"),
                os.path.expanduser("~/.zshrc"),
                os.path.expanduser("~/.profile"),
            ]

            for config_file in shell_configs:
                if os.path.exists(config_file):
                    # Try to reload shell configuration using bash
                    # Use run_silent which is already optimized for the project
                    try:
                        import shutil

                        # Find bash executable safely
                        bash_path = shutil.which("bash")
                        if not bash_path:
                            continue

                        # Use run_silent instead of subprocess.run directly
                        result = run_silent([bash_path, "-c", f"source {config_file}"])
                        if result.success:
                            logger.info(f"Reloaded shell configuration: {config_file}")
                            return True
                    except Exception as e:
                        # Bash not available or other error, continue to next config
                        logger.debug(f"Could not reload {config_file}: {e}")
                        continue

            logger.info("Unix environment refresh completed")
            return True

        except Exception as e:
            logger.error(f"Unix environment refresh failed: {e}")
            return False

    def verify_environment_refresh(self, command: str = "womm") -> bool:
        """
        Verify that environment refresh was successful by testing command accessibility.

        Args:
            command: Command to test (default: "womm")

        Returns:
            bool: True if command is accessible, False otherwise
        """
        try:
            result = run_silent([command, "--version"], capture_output=True)
            if result.success:
                logger.info(
                    f"Environment refresh verification successful - {command} is accessible"
                )
                return True
            else:
                logger.warning(
                    f"Environment refresh completed but {command} not yet accessible in current session"
                )
                return False
        except Exception as e:
            logger.warning(f"Could not verify environment refresh: {e}")
            return False

    def get_environment_info(self) -> Dict[str, str]:
        """
        Get current environment information.

        Returns:
            Dict[str, str]: Dictionary of environment information
        """
        return {
            "platform": self.platform,
            "path": os.environ.get("PATH", ""),
            "home": os.environ.get("HOME", os.environ.get("USERPROFILE", "")),
            "shell": os.environ.get("SHELL", os.environ.get("COMSPEC", "")),
        }

    def refresh_environment_with_ui(self) -> bool:
        """
        Refresh environment variables with user interface feedback.

        Returns:
            bool: True if refresh was successful, False otherwise
        """
        print_info("🔄 Refreshing environment variables...")

        success = self.refresh_environment()

        if success:
            print_success("✅ Environment variables refreshed successfully")

            # Verify the refresh worked
            if self.verify_environment_refresh():
                print_info("🎉 WOMM should now be accessible in the current session")
            else:
                print_warn(
                    "⚠️ Environment refreshed but WOMM may not be accessible in current session"
                )
                print_info(
                    "💡 Solution: Restart your terminal or open a new command prompt"
                )
        else:
            print_error("❌ Environment refresh failed")
            print_info(
                "💡 This means WOMM may not be accessible in the current session"
            )
            print_info(
                "🔧 Solution: Restart your terminal or run 'refreshenv' manually"
            )

        return success
