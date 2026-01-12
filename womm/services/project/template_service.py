#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEMPLATE SERVICE - Template Generation Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Template Service - Singleton service for template operations.

Handles cross-platform template generation and placeholder replacement.
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
from ...shared.results.project_results import TemplateResult
from ...utils.project import (
    generate_cross_platform_template,
    replace_platform_placeholders,
    validate_template_placeholders,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# TEMPLATE SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class TemplateService:
    """Singleton service for template operations."""

    _instance: ClassVar[TemplateService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> TemplateService:
        """Create or return the singleton instance.

        Returns:
            TemplateService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize template service (only once)."""
        if TemplateService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        TemplateService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def replace_placeholders(self, text: str, **extra_vars: str) -> str:
        """Replace platform-specific placeholders in a text.

        Args:
            text: Text containing placeholders to replace
            **extra_vars: Additional variables for replacement

        Returns:
            str: Text with placeholders replaced

        Raises:
            ProjectServiceError: If placeholder replacement fails
        """
        return replace_platform_placeholders(text, **extra_vars)

    def generate_template(
        self,
        template_path: Path,
        output_path: Path,
        template_vars: dict[str, str] | None = None,
    ) -> None:
        """Generate a file from a template by replacing placeholders.

        Args:
            template_path: Path to the template to use
            output_path: Path to the output file
            template_vars: Variables to replace in the template

        Raises:
            TemplateError: If template generation fails
        """
        generate_cross_platform_template(template_path, output_path, template_vars)

    def validate_template(self, template_path: Path) -> TemplateResult:
        """Validate placeholders in a template and return statistics.

        Args:
            template_path: Path to the template to validate

        Returns:
            TemplateResult: A result object containing validation statistics

        Raises:
            TemplateError: If template validation fails
        """
        try:
            stats = validate_template_placeholders(template_path)
            return TemplateResult(
                success=True,
                message="Template validation completed successfully",
                template_path=template_path,
                validation_stats=stats,
            )
        except Exception as e:
            logger.error(f"validate_template failed: {e}")
            return TemplateResult(
                success=False,
                message=f"Template validation failed: {e}",
                template_path=template_path,
                error=str(e),
            )
