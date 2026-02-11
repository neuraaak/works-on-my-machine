#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# BASE VALIDATION SERVICE - Generic Validation Logic
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Base validation service providing common validation patterns.

This module provides a centralized, generic validation service that handles
common validation logic used across the application (path validation, config
validation, structure validation, etc.).

All specialized validation services should extend this base class to reuse
common functionality and maintain consistent validation behavior.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path
from typing import Any

# Local imports
from ...shared.result_models import ValidationResult

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class BaseValidationService:
    """
    Base validation service providing common validation patterns.

    This class provides reusable validation methods that can be used by
    specialized validation services. It handles common patterns like:
    - Path validation (existence, permissions, etc.)
    - Structure validation (keys, types, required fields)
    - Configuration validation (valid values, constraints)
    - String validation (non-empty, patterns, etc.)

    All methods return ValidationResult for consistent error handling.

    Note: This is a utility class with only static methods and should not be instantiated.
    """

    # ///////////////////////////////////////////////////////////////
    # PATH VALIDATION METHODS
    # ///////////////////////////////////////////////////////////////

    @staticmethod
    def validate_path_exists(
        path: str | Path, path_type: str = "file"
    ) -> ValidationResult:
        """
        Validate that a path exists.

        Args:
            path: Path to validate
            path_type: Type of path ("file", "directory", or "any")

        Returns:
            ValidationResult with success/failure status

        Note:
            - path_type="file" checks if file exists
            - path_type="directory" checks if directory exists
            - path_type="any" checks if either exists
        """
        try:
            path_obj = Path(path)

            if not path_obj.exists():
                return ValidationResult(
                    success=False,
                    error=f"{path_type.capitalize()} does not exist: {path}",
                )

            if path_type == "file" and not path_obj.is_file():
                return ValidationResult(
                    success=False,
                    error=f"Path is not a file: {path}",
                )

            if path_type == "directory" and not path_obj.is_dir():
                return ValidationResult(
                    success=False,
                    error=f"Path is not a directory: {path}",
                )

            return ValidationResult(success=True)

        except Exception as e:
            logger.error(f"Error validating path existence: {e}")
            return ValidationResult(
                success=False,
                error=f"Error validating path: {e!s}",
            )

    @staticmethod
    def validate_path_readable(path: str | Path) -> ValidationResult:
        """
        Validate that a path is readable.

        Args:
            path: Path to validate

        Returns:
            ValidationResult with success/failure status
        """
        try:
            path_obj = Path(path)

            if not path_obj.exists():
                return ValidationResult(
                    success=False,
                    error=f"Path does not exist: {path}",
                )

            if not path_obj.is_file():
                return ValidationResult(
                    success=False,
                    error=f"Path is not a file: {path}",
                )

            if not path_obj.stat().st_mode & 0o400:
                return ValidationResult(
                    success=False,
                    error=f"Path is not readable: {path}",
                )

            return ValidationResult(success=True)

        except Exception as e:
            logger.error(f"Error validating path readability: {e}")
            return ValidationResult(
                success=False,
                error=f"Error validating path: {e!s}",
            )

    @staticmethod
    def validate_path_writable(path: str | Path) -> ValidationResult:
        """
        Validate that a path is writable.

        Args:
            path: Path to validate

        Returns:
            ValidationResult with success/failure status
        """
        try:
            path_obj = Path(path)
            parent = path_obj.parent if path_obj.is_file() else path_obj

            if not parent.exists():
                return ValidationResult(
                    success=False,
                    error=f"Parent directory does not exist: {parent}",
                )

            if not parent.stat().st_mode & 0o200:
                return ValidationResult(
                    success=False,
                    error=f"Parent directory is not writable: {parent}",
                )

            return ValidationResult(success=True)

        except Exception as e:
            logger.error(f"Error validating path writeability: {e}")
            return ValidationResult(
                success=False,
                error=f"Error validating path: {e!s}",
            )

    # ///////////////////////////////////////////////////////////////
    # STRING VALIDATION METHODS
    # ///////////////////////////////////////////////////////////////

    @staticmethod
    def validate_non_empty_string(
        value: str, field_name: str = "value"
    ) -> ValidationResult:
        """
        Validate that a string is not empty.

        Args:
            value: String to validate
            field_name: Name of field for error messages

        Returns:
            ValidationResult with success/failure status
        """
        if not isinstance(value, str):
            return ValidationResult(
                success=False,
                error=f"{field_name} must be a string, got {type(value).__name__}",
            )

        if not value or not value.strip():
            return ValidationResult(
                success=False,
                error=f"{field_name} cannot be empty",
            )

        return ValidationResult(success=True)

    @staticmethod
    def validate_string_pattern(
        value: str, pattern: str, field_name: str = "value"
    ) -> ValidationResult:
        """
        Validate that a string matches a pattern.

        Args:
            value: String to validate
            pattern: Regex pattern to match
            field_name: Name of field for error messages

        Returns:
            ValidationResult with success/failure status
        """
        import re

        try:
            if not re.match(pattern, value):
                return ValidationResult(
                    success=False,
                    error=f"{field_name} does not match required pattern",
                )

            return ValidationResult(success=True)

        except Exception as e:
            logger.error(f"Error validating string pattern: {e}")
            return ValidationResult(
                success=False,
                error=f"Error validating {field_name}: {e!s}",
            )

    # ///////////////////////////////////////////////////////////////
    # STRUCTURE VALIDATION METHODS
    # ///////////////////////////////////////////////////////////////

    @staticmethod
    def validate_dict_structure(
        data: dict, required_keys: list[str], field_name: str = "data"
    ) -> ValidationResult:
        """
        Validate that a dictionary has required keys.

        Args:
            data: Dictionary to validate
            required_keys: List of required keys
            field_name: Name of field for error messages

        Returns:
            ValidationResult with success/failure status
        """
        if not isinstance(data, dict):
            return ValidationResult(
                success=False,
                error=f"{field_name} must be a dictionary",
            )

        missing_keys = [key for key in required_keys if key not in data]

        if missing_keys:
            return ValidationResult(
                success=False,
                error=f"Missing required keys in {field_name}: {', '.join(missing_keys)}",
            )

        return ValidationResult(success=True)

    @staticmethod
    def validate_dict_value_types(
        data: dict, type_schema: dict[str, type], field_name: str = "data"
    ) -> ValidationResult:
        """
        Validate that dictionary values have correct types.

        Args:
            data: Dictionary to validate
            type_schema: Dict mapping keys to expected types
            field_name: Name of field for error messages

        Returns:
            ValidationResult with success/failure status

        Example:
            schema = {"name": str, "age": int, "active": bool}
            result = validate_dict_value_types(data, schema)
        """
        if not isinstance(data, dict):
            return ValidationResult(
                success=False,
                error=f"{field_name} must be a dictionary",
            )

        for key, expected_type in type_schema.items():
            if key in data:
                value = data[key]
                if not isinstance(value, expected_type):
                    actual_type = type(value).__name__
                    expected_name = expected_type.__name__
                    return ValidationResult(
                        success=False,
                        error=(
                            f"Field '{key}' in {field_name} has type {actual_type}, expected {expected_name}"
                        ),
                    )

        return ValidationResult(success=True)

    # ///////////////////////////////////////////////////////////////
    # RANGE VALIDATION METHODS
    # ///////////////////////////////////////////////////////////////

    @staticmethod
    def validate_value_in_range(
        value: int | float,
        min_val: int | float | None,
        max_val: int | float | None,
        field_name: str = "value",
    ) -> ValidationResult:
        """
        Validate that a numeric value is within a range.

        Args:
            value: Value to validate
            min_val: Minimum allowed value (None for no minimum)
            max_val: Maximum allowed value (None for no maximum)
            field_name: Name of field for error messages

        Returns:
            ValidationResult with success/failure status
        """
        if min_val is not None and value < min_val:
            return ValidationResult(
                success=False,
                error=f"{field_name} must be >= {min_val}, got {value}",
            )

        if max_val is not None and value > max_val:
            return ValidationResult(
                success=False,
                error=f"{field_name} must be <= {max_val}, got {value}",
            )

        return ValidationResult(success=True)

    @staticmethod
    def validate_value_in_list(
        value: Any, allowed_values: list[Any], field_name: str = "value"
    ) -> ValidationResult:
        """
        Validate that a value is in allowed list.

        Args:
            value: Value to validate
            allowed_values: List of allowed values
            field_name: Name of field for error messages

        Returns:
            ValidationResult with success/failure status
        """
        if value not in allowed_values:
            return ValidationResult(
                success=False,
                error=f"{field_name} must be one of {allowed_values}, got {value}",
            )

        return ValidationResult(success=True)

    # ///////////////////////////////////////////////////////////////
    # COMBINATION VALIDATION METHODS
    # ///////////////////////////////////////////////////////////////

    @staticmethod
    def validate_all(
        validations: list[ValidationResult],
    ) -> ValidationResult:
        """
        Combine multiple validation results.

        Args:
            validations: List of ValidationResult objects

        Returns:
            ValidationResult with combined status and all error messages

        Note:
            Returns success only if ALL validations passed.
            Error messages are combined with newlines.
        """
        failed_validations = [v for v in validations if not v.success]

        if not failed_validations:
            return ValidationResult(success=True)

        error_messages = [v.error for v in failed_validations if v.error]
        combined_message = "\n".join(error_messages)

        return ValidationResult(
            success=False,
            error=combined_message,
        )

    @staticmethod
    def validate_any(
        validations: list[ValidationResult],
    ) -> ValidationResult:
        """
        Require at least one validation to pass.

        Args:
            validations: List of ValidationResult objects

        Returns:
            ValidationResult with combined status

        Note:
            Returns success if ANY validation passed.
        """
        passed_validations = [v for v in validations if v.success]

        if passed_validations:
            return ValidationResult(success=True)

        error_messages = [v.error for v in validations if v.error]
        combined_message = " OR ".join(error_messages)

        return ValidationResult(
            success=False,
            error=combined_message,
        )
