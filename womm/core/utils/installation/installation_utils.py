#!/usr/bin/env python3
"""
Installation utilities for Works On My Machine.

This module provides pure utility functions for WOMM installation operations.
All functions here are stateless and can be used independently.
"""

# IMPORTS
########################################################
# Standard library imports
import platform
import stat
from pathlib import Path
from time import sleep
from typing import Dict, List

from ...exceptions.installation_exceptions import (
    ExecutableVerificationError,
    FileVerificationError,
)
from ...exceptions.uninstallation_exceptions import (
    FileRemovalVerificationError,
    UninstallationDirectoryAccessError,
    UninstallationFileListError,
    UninstallationPermissionError,
    UninstallationVerificationUtilityError,
)

# Local imports
from ..cli_utils import run_silent

# CONSTANTS
########################################################
# Configuration constants
DEFAULT_EXCLUDE_PATTERNS = [
    ".git",
    ".gitignore",
    ".pytest_cache",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "Thumbs.db",
    "*.tmp",
    "*.bak",
    "*.swp",
    "*.swo",
    "coverage.xml",
    "htmlcov",
    ".coverage",
    ".tox",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "*.egg-info",
    ".mypy_cache",
    ".ruff_cache",
    "tests",
    "test_*",
    "*_test.py",
    "ignore-install.txt",
    "womm.bat",  # Generated dynamically, should not be copied
    "womm-installed.py",  # Avoid copying previous installation artifacts
]

# FUNCTIONS
########################################################
# Path management utilities


def get_target_womm_path() -> Path:
    """Get the standard target path for Works On My Machine.

    Returns:
        Path object pointing to the .womm directory in user's home.
    """
    return Path.home() / ".womm"


def get_current_womm_path() -> Path:
    """Get the current script path.

    Returns:
        Path object pointing to the directory containing this script.
    """
    # Go up from womm/core/utils/installation/installation_utils.py to the project root
    # womm/core/utils/installation/installation_utils.py -> womm/core/utils/installation/ -> womm/core/utils/ -> womm/core/ -> womm/ -> project_root
    current_path = Path(__file__).parent.parent.parent.parent.parent.absolute()

    # Verify we're at the project root by checking for key files
    if not (current_path / "pyproject.toml").exists():
        raise RuntimeError(
            f"Could not find project root. Expected pyproject.toml at {current_path}"
        )

    return current_path


def should_exclude_file(file_path: Path, source_path: Path) -> bool:
    """Check if a file should be excluded from installation.

    Args:
        file_path: Path to the file relative to source
        source_path: Source directory path

    Returns:
        True if file should be excluded, False otherwise
    """
    # Load exclude patterns from ignore-install.txt if available
    exclude_patterns = []
    ignore_file = source_path / "ignore-install.txt"

    if ignore_file.exists():
        try:
            with open(ignore_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith("#"):
                        exclude_patterns.append(line)
        except Exception as e:
            # Fall back to default patterns if file can't be read
            # Log the error for debugging but continue with defaults
            print(f"Warning: Could not read ignore-install.txt: {e}")

    # Fallback to default patterns if no ignore-install.txt or empty
    if not exclude_patterns:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

    file_name = file_path.name
    relative_path = file_path.relative_to(source_path)

    for pattern in exclude_patterns:
        if pattern.startswith("*"):
            if file_name.endswith(pattern[1:]):
                return True
        elif pattern in str(relative_path):
            return True

    return False


def create_womm_executable(target_path: Path) -> Dict:
    """Create the womm executable script.

    Args:
        target_path: Path where WOMM is installed

    Returns:
        Dictionary with success status and details
    """
    try:
        # Create executable script content
        if platform.system() == "Windows":
            # Windows batch file
            executable_path = target_path / "womm.bat"
            script_content = f'@echo off\npython "{target_path / "womm.py"}" %*\n'
        else:
            # Unix shell script
            executable_path = target_path / "womm"
            script_content = f'#!/bin/bash\npython3 "{target_path / "womm.py"}" "$@"\n'

        # Write the executable
        with open(executable_path, "w", encoding="utf-8") as f:
            f.write(script_content)
            sleep(0.5)

        # Make executable on Unix systems
        if platform.system() != "Windows":
            executable_path.chmod(executable_path.stat().st_mode | stat.S_IEXEC)

        return {
            "success": True,
            "executable_path": str(executable_path),
            "platform": platform.system(),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "platform": platform.system(),
        }


def get_files_to_copy(source_path: Path) -> List[str]:
    """Get list of files to copy during installation.

    Args:
        source_path: Source directory path

    Returns:
        List of file paths relative to source
    """
    files_to_copy = []

    for file_path in source_path.rglob("*"):
        if file_path.is_file() and not should_exclude_file(file_path, source_path):
            relative_path = file_path.relative_to(source_path)
            files_to_copy.append(str(relative_path))

    return files_to_copy


def verify_files_copied(source_path: Path, target_path: Path) -> Dict:
    """Verify that all required files were copied correctly.

    Args:
        source_path: Original source directory
        target_path: Target installation directory

    Returns:
        Dictionary with verification results

    Raises:
        FileVerificationError: If files are missing or corrupted
    """
    try:
        files_to_check = get_files_to_copy(source_path)
        missing_files = []
        size_mismatches = []

        for relative_file in files_to_check:
            source_file = source_path / relative_file
            target_file = target_path / relative_file

            if not target_file.exists():
                missing_files.append(str(relative_file))
            elif source_file.stat().st_size != target_file.stat().st_size:
                size_mismatches.append(str(relative_file))

        # If there are issues, raise appropriate exceptions
        if missing_files:
            raise FileVerificationError(
                verification_type="copy_verification",
                file_path=str(missing_files[0]),  # First missing file
                reason=f"Missing {len(missing_files)} files",
                details=f"Missing files: {missing_files[:5]}{'...' if len(missing_files) > 5 else ''}",
            )

        if size_mismatches:
            raise FileVerificationError(
                verification_type="copy_verification",
                file_path=str(size_mismatches[0]),  # First mismatched file
                reason=f"Size mismatch in {len(size_mismatches)} files",
                details=f"Size mismatches: {size_mismatches[:5]}{'...' if len(size_mismatches) > 5 else ''}",
            )

        # All files verified successfully
        return {
            "success": True,
            "total_files": len(files_to_check),
            "missing_files": [],
            "size_mismatches": [],
        }

    except FileVerificationError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise FileVerificationError(
            verification_type="copy_verification",
            file_path=str(target_path),
            reason=f"Unexpected error during file verification: {e}",
            details="This is an unexpected error that should be reported",
        ) from e


def verify_executable_works(target_path: Path) -> Dict:
    """Verify that the WOMM executable works correctly.

    Args:
        target_path: Target installation directory

    Returns:
        Dictionary with verification results

    Raises:
        ExecutableVerificationError: If executable is missing or fails to work
    """
    try:
        if platform.system() == "Windows":
            executable_path = target_path / "womm.bat"
            test_command = [str(executable_path), "--version"]
        else:
            executable_path = target_path / "womm"
            test_command = [str(executable_path), "--version"]

        if not executable_path.exists():
            raise ExecutableVerificationError(
                executable_name="womm",
                reason=f"Executable not found at {executable_path}",
                details=f"Platform: {platform.system()}",
            )

        # Test the executable
        result = run_silent(test_command, capture_output=True)

        if result.returncode == 0:
            # Handle stdout properly
            stdout_str = result.stdout
            if isinstance(stdout_str, bytes):
                stdout_str = stdout_str.decode()

            return {
                "success": True,
                "executable_path": str(executable_path),
                "output": stdout_str,
            }
        else:
            # Handle stderr properly
            stderr_str = result.stderr
            if isinstance(stderr_str, bytes):
                stderr_str = stderr_str.decode()

            raise ExecutableVerificationError(
                executable_name="womm",
                reason=f"Executable test failed with code {result.returncode}",
                details=f"stderr: {stderr_str}",
            )

    except ExecutableVerificationError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise ExecutableVerificationError(
            executable_name="womm",
            reason=f"Unexpected error during executable verification: {e}",
            details="This is an unexpected error that should be reported",
        ) from e


# UNINSTALLATION UTILITIES
########################################################
# Functions for uninstallation operations


def get_files_to_remove(target_path: Path) -> List[str]:
    """Get list of files and directories to remove for progress tracking.

    Args:
        target_path: Target installation directory

    Returns:
        List of relative file and directory paths to remove

    Raises:
        UninstallationFileListError: If file list generation fails
        UninstallationDirectoryAccessError: If directory access fails
        UninstallationPermissionError: If permission issues occur
    """
    files_to_remove = []

    if not target_path.exists():
        return files_to_remove

    try:
        # Check if we have permission to access the directory
        if not target_path.is_dir():
            raise UninstallationDirectoryAccessError(
                directory_path=str(target_path),
                operation="list_generation",
                reason="Target path is not a directory",
                details=f"Path exists but is not a directory: {target_path}",
            )

        # Get all files and directories recursively
        for item_path in target_path.rglob("*"):
            try:
                if item_path.is_file():
                    # Add file with relative path
                    relative_path = item_path.relative_to(target_path)
                    files_to_remove.append(str(relative_path))
                elif item_path.is_dir():
                    # Add directory with relative path (keep trailing slash for directories)
                    relative_path = item_path.relative_to(target_path)
                    files_to_remove.append(f"{relative_path}/")
            except PermissionError as e:
                raise UninstallationPermissionError(
                    target_path=str(item_path),
                    operation="file_scanning",
                    reason=f"Permission denied: {e}",
                    details=f"Cannot access file/directory: {item_path}",
                ) from e

        # Sort to ensure files are removed before their parent directories
        # Files first, then directories (reverse alphabetical for nested dirs)
        files_to_remove.sort(key=lambda x: (x.endswith("/"), x))

        return files_to_remove

    except (UninstallationDirectoryAccessError, UninstallationPermissionError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise UninstallationFileListError(
            target_path=str(target_path),
            reason=f"Unexpected error during file list generation: {e}",
            details="This is an unexpected error that should be reported",
        ) from e


def verify_files_removed(target_path: Path) -> Dict:
    """Verify that WOMM files were removed successfully.

    Args:
        target_path: Target installation directory

    Returns:
        Dictionary with success status and details

    Raises:
        FileRemovalVerificationError: If files were not removed successfully
        UninstallationDirectoryAccessError: If directory access fails during verification
    """
    try:
        # Check if we can access the directory for verification
        if target_path.exists():
            try:
                # Try to access the directory to see if it's accessible
                target_path.stat()
            except PermissionError as e:
                raise UninstallationDirectoryAccessError(
                    directory_path=str(target_path),
                    operation="verification",
                    reason=f"Permission denied during verification: {e}",
                    details=f"Cannot access directory for verification: {target_path}",
                ) from e

            # Directory exists and is accessible
            raise FileRemovalVerificationError(
                verification_type="removal_verification",
                file_path=str(target_path),
                reason="WOMM directory still exists after removal",
                details=f"Directory path: {target_path}",
            )
        else:
            return {"success": True, "message": "All WOMM files removed successfully"}

    except (FileRemovalVerificationError, UninstallationDirectoryAccessError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise FileRemovalVerificationError(
            verification_type="removal_verification",
            file_path=str(target_path),
            reason=f"File removal verification error: {e}",
            details="This is an unexpected error that should be reported",
        ) from e


def verify_uninstallation_complete(target_path: Path) -> Dict:
    """Verify that uninstallation completed successfully.

    Args:
        target_path: Target installation directory

    Returns:
        Dictionary with success status and details

    Raises:
        UninstallationVerificationUtilityError: If uninstallation verification fails
        UninstallationDirectoryAccessError: If directory access fails during verification
    """
    try:
        # Check that target directory is gone
        if target_path.exists():
            try:
                # Try to access the directory to see if it's accessible
                target_path.stat()
            except PermissionError as e:
                raise UninstallationDirectoryAccessError(
                    directory_path=str(target_path),
                    operation="verification",
                    reason=f"Permission denied during verification: {e}",
                    details=f"Cannot access directory for verification: {target_path}",
                ) from e

            # Directory exists and is accessible
            raise UninstallationVerificationUtilityError(
                verification_step="directory_removal",
                reason=f"Installation directory still exists: {target_path}",
                details="The target directory was not removed during uninstallation",
            )

        # Simple check that womm command is no longer accessible
        from ....common.security import run_silent

        try:
            cmd_result = run_silent("womm --version", timeout=10)
        except Exception:
            # If command execution fails, that's actually success (command not found)
            return {
                "success": True,
                "message": "WOMM command no longer accessible (execution failed)",
            }

        # If command is not found (exit code 9009 on Windows), that's success
        if cmd_result.returncode == 9009:  # Command not found on Windows
            return {"success": True, "message": "WOMM command no longer accessible"}
        else:
            # Command still found, but this might be from another installation
            return {
                "success": True,  # Don't fail uninstallation for this
                "message": "WOMM command still accessible (may be from another installation)",
            }

    except (UninstallationVerificationUtilityError, UninstallationDirectoryAccessError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise UninstallationVerificationUtilityError(
            verification_step="unexpected_error",
            reason=f"Uninstallation verification error: {e}",
            details="This is an unexpected error that should be reported",
        ) from e
