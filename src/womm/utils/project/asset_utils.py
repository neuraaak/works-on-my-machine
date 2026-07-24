#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# ASSET UTILS - Asset Path Resolution and Copying
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for asset management.

This module provides stateless functions for:
- Resolving asset paths by language and variant
- Copying individual asset files
- Copying asset directories recursively
- Copying specific asset types (templates, vscode, configs, scripts)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import shutil
from pathlib import Path

# Local imports
from ...exceptions.project import ProjectServiceError
from ...shared.configs.project import ProjectVariantConfig
from ..common.path_resolver_utils import get_assets_module_path

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# ASSET PATH RESOLUTION
# ///////////////////////////////////////////////////////////////


def get_assets_path(
    language: str, variant: str | None = None, asset_type: str | None = None
) -> Path:
    """Get the path to assets for a given language and variant.

    Args:
        language: Project language (python, javascript)
        variant: Project variant (py, js, react, vue, etc.). If None, uses default.
        asset_type: Optional asset type subdirectory (templates, vscode, configs, scripts)

    Returns:
        Path: Path to the assets directory

    Raises:
        ProjectServiceError: If language or variant is invalid
    """
    try:
        assets_base = get_assets_module_path() / "languages"

        # Validate language
        if language not in ProjectVariantConfig.SUPPORTED_VARIANTS:
            raise ProjectServiceError(
                message=f"Unsupported language: {language}",
                operation="get_assets_path",
                details=f"Supported languages: {list(ProjectVariantConfig.SUPPORTED_VARIANTS.keys())}",
            )

        # Get variant (use default if not specified)
        if variant is None:
            variant = ProjectVariantConfig.DEFAULT_VARIANTS.get(language)
            if variant is None:
                raise ProjectServiceError(
                    message=f"No default variant for language: {language}",
                    operation="get_assets_path",
                    details="Please specify a variant explicitly",
                )

        # Validate variant
        if variant not in ProjectVariantConfig.SUPPORTED_VARIANTS[language]:
            raise ProjectServiceError(
                message=f"Unsupported variant '{variant}' for language '{language}'",
                operation="get_assets_path",
                details=f"Supported variants: {ProjectVariantConfig.SUPPORTED_VARIANTS[language]}",
            )

        # Get assets subdirectory
        assets_subdir = ProjectVariantConfig.VARIANT_TO_ASSETS.get(variant, variant)
        assets_path = assets_base / language / assets_subdir

        # Add asset type subdirectory if specified
        if asset_type:
            assets_path = assets_path / asset_type

        return assets_path

    except ProjectServiceError:
        raise
    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to resolve assets path: {e}",
            operation="get_assets_path",
            details=f"Language: {language}, Variant: {variant}, Asset type: {asset_type}",
        ) from e


# ///////////////////////////////////////////////////////////////
# ASSET FILE OPERATIONS
# ///////////////////////////////////////////////////////////////


def copy_asset_file(
    source: Path,
    target: Path,
    overwrite: bool = False,
    create_parents: bool = True,
) -> Path:
    """Copy a single asset file to target location.

    Args:
        source: Source file path
        target: Target file path
        overwrite: If True, overwrite existing files. If False, skip if exists.
        create_parents: If True, create parent directories if they don't exist

    Returns:
        Path: Path to the copied file (or existing file if skipped)

    Raises:
        ProjectServiceError: If copy operation fails
    """
    try:
        # Validate source
        if not source.exists():
            raise ProjectServiceError(
                message="Source file does not exist",
                operation="copy_asset_file",
                details=f"Source: {source}",
            )

        if not source.is_file():
            raise ProjectServiceError(
                message="Source path is not a file",
                operation="copy_asset_file",
                details=f"Source: {source}",
            )

        # Check if target exists
        if target.exists() and not overwrite:
            logger.debug(f"Skipping {target} (already exists, overwrite=False)")
            return target

        # Create parent directories if needed
        if create_parents:
            target.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file
        shutil.copy2(source, target)
        logger.debug(f"Copied {source} to {target}")

        return target

    except ProjectServiceError:
        raise
    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to copy asset file: {e}",
            operation="copy_asset_file",
            details=f"Source: {source}, Target: {target}",
        ) from e


def copy_assets_directory(
    source: Path,
    target: Path,
    overwrite: bool = False,
    exclude_patterns: list[str] | None = None,
) -> list[Path]:
    """Copy an asset directory recursively to target location.

    Args:
        source: Source directory path
        target: Target directory path
        overwrite: If True, overwrite existing files. If False, skip if exists.
        exclude_patterns: Optional list of glob patterns to exclude

    Returns:
        list[Path]: List of copied file paths (relative to target)

    Raises:
        ProjectServiceError: If copy operation fails
    """
    try:
        # Validate source
        if not source.exists():
            raise ProjectServiceError(
                message="Source directory does not exist",
                operation="copy_assets_directory",
                details=f"Source: {source}",
            )

        if not source.is_dir():
            raise ProjectServiceError(
                message="Source path is not a directory",
                operation="copy_assets_directory",
                details=f"Source: {source}",
            )

        copied_files = []
        exclude_patterns = exclude_patterns or []

        # Create target directory
        target.mkdir(parents=True, exist_ok=True)

        # Copy files recursively
        for item in source.rglob("*"):
            if item.is_file():
                # Check exclude patterns
                relative_path = item.relative_to(source)
                if any(relative_path.match(pattern) for pattern in exclude_patterns):
                    logger.debug(f"Excluding {relative_path} (matches pattern)")
                    continue

                # Determine target file path
                target_file = target / relative_path

                # Skip if exists and overwrite is False
                if target_file.exists() and not overwrite:
                    logger.debug(
                        f"Skipping {target_file} (already exists, overwrite=False)"
                    )
                    continue

                # Create parent directories
                target_file.parent.mkdir(parents=True, exist_ok=True)

                # Copy the file
                shutil.copy2(item, target_file)
                copied_files.append(target_file)
                logger.debug(f"Copied {item} to {target_file}")

        logger.info(f"Copied {len(copied_files)} files from {source} to {target}")
        return copied_files

    except ProjectServiceError:
        raise
    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to copy assets directory: {e}",
            operation="copy_assets_directory",
            details=f"Source: {source}, Target: {target}",
        ) from e


def copy_asset_type(
    language: str,
    variant: str | None,
    asset_type: str,
    target: Path,
    overwrite: bool = False,
) -> list[Path]:
    """Copy a specific asset type (templates, vscode, configs, scripts) to target.

    Args:
        language: Project language (python, javascript)
        variant: Project variant (py, js, react, vue, etc.)
        asset_type: Asset type subdirectory (templates, vscode, configs, scripts)
        target: Target directory path
        overwrite: If True, overwrite existing files

    Returns:
        list[Path]: List of copied file paths

    Raises:
        ProjectServiceError: If copy operation fails
    """
    try:
        # Get source path
        source = get_assets_path(language, variant, asset_type)

        if not source.exists():
            logger.warning(
                f"Asset type '{asset_type}' not found for {language}/{variant} at {source}"
            )
            return []

        # Copy the directory
        return copy_assets_directory(source, target, overwrite=overwrite)

    except ProjectServiceError:
        raise
    except Exception as e:
        raise ProjectServiceError(
            message=f"Failed to copy asset type: {e}",
            operation="copy_asset_type",
            details=f"Language: {language}, Variant: {variant}, Asset type: {asset_type}",
        ) from e


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "copy_asset_file",
    "copy_asset_type",
    "copy_assets_directory",
    "get_assets_path",
]
