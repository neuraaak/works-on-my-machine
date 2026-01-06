#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# USER PATH UTILS - User PATH Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Utilities for PATH and registry operations (shared helpers).

Provides cross-platform utilities for managing PATH environment variables,
including Windows registry operations and Unix shell configuration files.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import os
import platform
from pathlib import Path

from ...exceptions.system import FileSystemError, RegistryError, UserPathError
from ..cli_utils import run_silent

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# UTILITY FUNCTIONS - PATH EXTRACTION
# ///////////////////////////////////////////////////////////////


def get_current_system_path() -> str:
    """
    Get current system PATH value.

    Returns:
        str: Current PATH string from system

    Raises:
        UserPathError: If PATH retrieval fails
        RegistryError: If registry operations fail
    """
    try:
        if platform.system() == "Windows":
            # Read PATH from user registry (HKCU), not from current session
            try:
                query = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])
            except Exception as e:
                raise RegistryError(
                    registry_key="HKCU\\Environment",
                    operation="query",
                    reason=f"Failed to execute registry query: {e}",
                    details=f"Exception type: {type(e).__name__}",
                ) from e

            if not query.success:
                raise RegistryError(
                    registry_key="HKCU\\Environment",
                    operation="query",
                    reason="Failed to query Windows user PATH from registry",
                    details=f"Return code: {query.returncode}",
                )

            try:
                current_path = extract_path_from_reg_output(query.stdout)
            except Exception as e:
                raise UserPathError(
                    message=f"Failed to extract PATH from registry output: {e}",
                    details=f"Registry query succeeded but PATH extraction failed. Output: {str(query.stdout)}",
                ) from e

            if not current_path:
                raise UserPathError(
                    message="No PATH value found in Windows user registry",
                    details=f"Registry query succeeded but no PATH value was extracted. Output: {str(query.stdout)}",
                )

            return current_path
        else:
            return os.environ.get("PATH", "")

    except (UserPathError, RegistryError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise UserPathError(
            message=f"Failed to get current system PATH: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def extract_path_from_reg_output(output: str | bytes) -> str:
    """
    Extract PATH value from `reg query` output, supporting REG_SZ and REG_EXPAND_SZ.

    Args:
        output: Raw stdout from `reg query` command

    Returns:
        str: Extracted PATH value or empty string if not found

    Raises:
        UserPathError: If registry output parsing fails
    """
    try:
        if not output:
            return ""

        if isinstance(output, (bytes, bytearray)):
            output = output.decode("utf-8", errors="ignore")

        for line in str(output).splitlines():
            if "PATH" in line and ("REG_SZ" in line or "REG_EXPAND_SZ" in line):
                if "REG_EXPAND_SZ" in line:
                    parts = line.split("REG_EXPAND_SZ")
                else:
                    parts = line.split("REG_SZ")
                if len(parts) > 1:
                    return parts[1].strip()

        return ""

    except Exception as e:
        # Wrap unexpected external exceptions
        raise UserPathError(
            message="Failed to parse registry output",
            details=f"Exception type: {type(e).__name__}, Output: {str(output)}",
        ) from e


def deduplicate_path_entries(path_value: str) -> str:
    """
    Deduplicate PATH entries preserving first occurrence and order.

    Comparison is done case-insensitively on expanded values with trailing
    slashes/backslashes trimmed. The original first textual form is kept.

    Args:
        path_value: Raw PATH string with semicolon-separated entries

    Returns:
        str: Deduplicated PATH string

    Raises:
        UserPathError: If PATH deduplication fails
    """
    try:
        if not path_value:
            return path_value

        seen: set[str] = set()
        result_parts: list[str] = []

        for raw_part in path_value.split(";"):
            part = raw_part.strip()
            if not part:
                continue
            try:
                key = os.path.expandvars(part).rstrip("/\\").lower()
                if key in seen:
                    continue
                seen.add(key)
                result_parts.append(part)
            except Exception as e:
                # Log but continue processing other entries
                logger.warning(f"Failed to process PATH entry '{part}': {e}")
                continue

        return ";".join(result_parts)

    except Exception as e:
        # Wrap unexpected external exceptions
        raise UserPathError(
            message="Failed to deduplicate PATH entries",
            details=f"Exception type: {type(e).__name__}, Path value: {path_value}",
        ) from e


# ///////////////////////////////////////////////////////////////
# WINDOWS PATH OPERATIONS
# ///////////////////////////////////////////////////////////////


def setup_windows_path(entry_path: str, original_path: str) -> dict[str, str | bool]:
    """
    Setup WOMM in Windows PATH environment variable.

    Args:
        entry_path: Path to WOMM installation directory
        original_path: Original PATH value for backup

    Returns:
        Dict: Dictionary with operation results

    Raises:
        UserPathError: If PATH setup fails
        RegistryError: If registry operations fail
    """
    try:
        # Input validation
        if not entry_path:
            raise UserPathError(
                message="Entry path cannot be empty",
                details="Empty entry path provided for Windows PATH setup",
            )

        if not original_path:
            raise UserPathError(
                message="Original path cannot be empty",
                details="Empty original path provided for Windows PATH setup",
            )

        # Query current user PATH from registry
        result = run_silent(
            [
                "reg",
                "query",
                "HKCU\\Environment",
                "/v",
                "PATH",
            ],
            capture_output=True,
        )

        if result.returncode != 0:
            # Handle stderr properly - check if it's bytes or str
            stderr_str = result.stderr
            if isinstance(stderr_str, bytes):
                stderr_str = stderr_str.decode()

            raise RegistryError(
                registry_key="HKCU\\Environment",
                operation="query",
                reason="Failed to query current PATH from registry",
                details=f"Return code: {result.returncode}, Stderr: {stderr_str}",
            )

        # Extract current PATH value - handle stdout properly
        stdout_str = result.stdout
        if isinstance(stdout_str, bytes):
            stdout_str = stdout_str.decode()

        current_path = extract_path_from_reg_output(stdout_str)

        # Normalize path separators and deduplicate
        def _normalize_list(path_str: str) -> list[str]:
            """Split PATH string and normalize separators."""
            try:
                entries = [p.strip() for p in path_str.split(";") if p.strip()]
                return [str(Path(p)) for p in entries]
            except Exception as e:
                raise UserPathError(
                    message="Failed to normalize PATH entries",
                    details=f"Exception type: {type(e).__name__}, Path string: {path_str}",
                ) from e

        # Parse current PATH entries
        current_entries = _normalize_list(current_path)
        normalized_womm = str(Path(entry_path))

        # Check if WOMM path is already in PATH
        if normalized_womm not in current_entries:
            # Add WOMM path to the beginning for priority
            updated_entries = current_entries + [normalized_womm]
            updated_path = ";".join(updated_entries)

            # Deduplicate entries to clean up PATH
            updated_path = deduplicate_path_entries(updated_path)

            # Update PATH in registry
            reg_result = run_silent(
                [
                    "reg",
                    "add",
                    "HKCU\\Environment",
                    "/v",
                    "PATH",
                    "/t",
                    "REG_EXPAND_SZ",
                    "/d",
                    updated_path,
                    "/f",
                ],
                capture_output=True,
            )

            if reg_result.returncode != 0:
                # Handle stderr properly
                stderr_str = reg_result.stderr
                if isinstance(stderr_str, bytes):
                    stderr_str = stderr_str.decode()

                raise RegistryError(
                    registry_key="HKCU\\Environment",
                    operation="update",
                    reason="Failed to update PATH in registry",
                    details=f"Return code: {reg_result.returncode}, Stderr: {stderr_str}",
                )

            return {
                "success": True,
                "action": "added",
                "entry_path": normalized_womm,
                "original_path": original_path,
                "updated_path": updated_path,
            }
        else:
            return {
                "success": True,
                "action": "already_present",
                "entry_path": normalized_womm,
                "current_path": current_path,
            }

    except (UserPathError, RegistryError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise UserPathError(
            message=f"Unexpected error during Windows PATH setup: {e}",
            details=f"Exception type: {type(e).__name__}, Entry path: {entry_path}, Original PATH: {original_path}",
        ) from e


def remove_from_windows_path(entry_path: str) -> dict[str, str | bool]:
    """
    Remove WOMM from Windows PATH environment variable.

    Args:
        entry_path: Path to WOMM installation directory

    Returns:
        Dict: Dictionary with operation results

    Raises:
        UserPathError: If PATH removal fails
        RegistryError: If registry operations fail
    """
    try:
        # Input validation
        if not entry_path:
            raise UserPathError(
                message="Entry path cannot be empty",
                details="Empty entry path provided for Windows PATH removal",
            )

        # Query current user PATH from registry
        result = run_silent(
            [
                "reg",
                "query",
                "HKCU\\Environment",
                "/v",
                "PATH",
            ],
            capture_output=True,
        )

        if result.returncode != 0:
            raise RegistryError(
                registry_key="HKCU\\Environment",
                operation="query",
                reason="Failed to query current PATH from registry",
                details=f"Return code: {result.returncode}",
            )

        # Extract and normalize current PATH - handle stdout properly
        stdout_str = result.stdout
        if isinstance(stdout_str, bytes):
            stdout_str = stdout_str.decode()

        current_path = extract_path_from_reg_output(stdout_str)

        def _norm(p: str) -> str:
            """Normalize path for comparison."""
            try:
                return str(Path(p).resolve()) if p else ""
            except Exception as e:
                # Log but continue with original path
                logger.warning(f"Failed to resolve path '{p}': {e}")
                return p

        path_entries = [p.strip() for p in current_path.split(";") if p.strip()]
        normalized_womm = _norm(entry_path)

        # Filter out WOMM paths
        updated_entries = []
        removed_paths = []

        for entry in path_entries:
            normalized_entry = _norm(entry)
            if normalized_entry and normalized_entry != normalized_womm:
                updated_entries.append(entry)
            elif normalized_entry == normalized_womm:
                removed_paths.append(entry)

        if removed_paths:
            # Update PATH in registry
            updated_path = ";".join(updated_entries)

            reg_result = run_silent(
                [
                    "reg",
                    "add",
                    "HKCU\\Environment",
                    "/v",
                    "PATH",
                    "/t",
                    "REG_EXPAND_SZ",
                    "/d",
                    updated_path,
                    "/f",
                ],
                capture_output=True,
            )

            if reg_result.returncode != 0:
                raise RegistryError(
                    registry_key="HKCU\\Environment",
                    operation="update",
                    reason="Failed to update PATH in registry",
                    details=f"Return code: {reg_result.returncode}",
                )

            return {
                "success": True,
                "action": "removed",
                "removed_paths": removed_paths,
                "updated_path": updated_path,
            }
        else:
            return {
                "success": True,
                "action": "not_found",
                "current_path": current_path,
            }

    except (UserPathError, RegistryError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise UserPathError(
            message=f"Unexpected error during Windows PATH removal: {e}",
            details=f"Exception type: {type(e).__name__}, Entry path: {entry_path}",
        ) from e


# ///////////////////////////////////////////////////////////////
# UNIX PATH OPERATIONS
# ///////////////////////////////////////////////////////////////


def setup_unix_path(entry_path: str, original_path: str) -> dict[str, str | bool]:
    """
    Setup WOMM in Unix PATH environment variable.

    Args:
        entry_path: Path to WOMM installation directory
        original_path: Original PATH value for backup

    Returns:
        Dict: Dictionary with operation results

    Raises:
        UserPathError: If PATH setup fails
        FileSystemError: If file system operations fail
    """
    try:
        # Input validation
        if not entry_path:
            raise UserPathError(
                message="Entry path cannot be empty",
                details="Empty entry path provided for Unix PATH setup",
            )

        if not original_path:
            raise UserPathError(
                message="Original path cannot be empty",
                details="Empty original path provided for Unix PATH setup",
            )

        shell_rc_files = [
            Path.home() / ".bashrc",
            Path.home() / ".zshrc",
            Path.home() / ".profile",
        ]

        # Find existing shell configuration file
        target_rc = None
        for rc_file in shell_rc_files:
            if rc_file.exists():
                target_rc = rc_file
                break

        # Default to .bashrc if none exist
        if target_rc is None:
            target_rc = Path.home() / ".bashrc"

        # Check if WOMM path is already in the RC file
        womm_export_line = f'export PATH="{entry_path}:$PATH"'
        womm_path_comment = "# Added by Works On My Machine installer"

        if target_rc.exists():
            try:
                with open(target_rc, encoding="utf-8") as f:
                    content = f.read()
                    if entry_path in content:
                        return {
                            "success": True,
                            "action": "already_present",
                            "rc_file": str(target_rc),
                            "entry_path": entry_path,
                        }
            except (PermissionError, OSError) as e:
                raise FileSystemError(
                    file_path=str(target_rc),
                    operation="read",
                    reason="Cannot read shell configuration file",
                    details=f"Error: {e}",
                ) from e

        # Add WOMM to PATH
        try:
            with open(target_rc, "a", encoding="utf-8") as f:
                f.write(f"\n{womm_path_comment}\n{womm_export_line}\n")
        except (PermissionError, OSError) as e:
            raise FileSystemError(
                file_path=str(target_rc),
                operation="write",
                reason="Cannot write to shell configuration file",
                details=f"Error: {e}",
            ) from e

        return {
            "success": True,
            "action": "added",
            "rc_file": str(target_rc),
            "entry_path": entry_path,
            "original_path": original_path,
        }

    except (UserPathError, FileSystemError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise UserPathError(
            message=f"Unexpected error during Unix PATH setup: {e}",
            details=f"Exception type: {type(e).__name__}, Entry path: {entry_path}, Original PATH: {original_path}",
        ) from e


def remove_from_unix_path(entry_path: str) -> dict[str, str | bool]:
    """
    Remove WOMM from Unix PATH environment variable.

    Args:
        entry_path: Path to WOMM installation directory

    Returns:
        Dict: Dictionary with operation results

    Raises:
        UserPathError: If PATH removal fails
        FileSystemError: If file system operations fail
    """
    try:
        # Input validation
        if not entry_path:
            raise UserPathError(
                message="Entry path cannot be empty",
                details="Empty entry path provided for Unix PATH removal",
            )

        shell_rc_files = [
            Path.home() / ".bashrc",
            Path.home() / ".zshrc",
            Path.home() / ".profile",
        ]

        removed_from_files = []

        for rc_file in shell_rc_files:
            if not rc_file.exists():
                continue

            try:
                with open(rc_file, encoding="utf-8") as f:
                    lines = f.readlines()
            except (PermissionError, OSError) as e:
                raise FileSystemError(
                    file_path=str(rc_file),
                    operation="read",
                    reason="Cannot read shell configuration file",
                    details=f"Error: {e}",
                ) from e

            # Filter out WOMM-related lines
            updated_lines = []
            removed_lines = []
            skip_next = False

            for _i, line in enumerate(lines):
                line_stripped = line.strip()

                # Skip WOMM comment lines
                if "Added by Works On My Machine installer" in line:
                    removed_lines.append(line_stripped)
                    skip_next = True
                    continue

                # Skip WOMM export lines
                elif skip_next and "export PATH=" in line and entry_path in line:
                    removed_lines.append(line_stripped)
                    skip_next = False
                    continue

                # Skip direct WOMM export lines without comment
                elif "export PATH=" in line and entry_path in line:
                    removed_lines.append(line_stripped)
                    continue

                else:
                    updated_lines.append(line)
                    skip_next = False

            # Write back if changes were made
            if removed_lines:
                try:
                    with open(rc_file, "w", encoding="utf-8") as f:
                        f.writelines(updated_lines)
                except (PermissionError, OSError) as e:
                    raise FileSystemError(
                        file_path=str(rc_file),
                        operation="write",
                        reason="Cannot write to shell configuration file",
                        details=f"Error: {e}",
                    ) from e

                removed_from_files.append(
                    {
                        "file": str(rc_file),
                        "removed_lines": removed_lines,
                    }
                )

        if removed_from_files:
            return {
                "success": True,
                "action": "removed",
                "removed_from_files": removed_from_files,
            }
        else:
            return {
                "success": True,
                "action": "not_found",
                "checked_files": [str(f) for f in shell_rc_files if f.exists()],
            }

    except (UserPathError, FileSystemError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise UserPathError(
            message=f"Unexpected error during Unix PATH removal: {e}",
            details=f"Exception type: {type(e).__name__}, Entry path: {entry_path}",
        ) from e


# ///////////////////////////////////////////////////////////////
# CROSS-PLATFORM OPERATIONS
# ///////////////////////////////////////////////////////////////


def remove_from_path(entry_path: str) -> dict[str, str | bool]:
    """
    Remove WOMM from PATH environment variable (cross-platform).

    Args:
        entry_path: Path to WOMM installation directory

    Returns:
        Dict: Dictionary with operation result and details

    Raises:
        UserPathError: If PATH removal fails
        RegistryError: If Windows registry operations fail
        FileSystemError: If Unix file system operations fail
    """
    try:
        # Input validation
        if not entry_path:
            raise UserPathError(
                message="Entry path cannot be empty",
                details="Empty entry path provided for PATH removal",
            )

        if platform.system() == "Windows":
            return remove_from_windows_path(entry_path)
        else:
            return remove_from_unix_path(entry_path)

    except (UserPathError, RegistryError, FileSystemError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise UserPathError(
            message=f"Unexpected error during PATH removal: {e}",
            details=f"Exception type: {type(e).__name__}, Entry path: {entry_path}, Platform: {platform.system()}",
        ) from e
