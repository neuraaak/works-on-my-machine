#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT UTILS - Pure Project Utility Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for project operations.

This package contains stateless utility functions for:
- Asset management (path resolution, copying)
- Project detection
- Project validation
- Template processing
- Platform-specific utilities
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .asset_utils import (
    copy_asset_file,
    copy_asset_type,
    copy_assets_directory,
    get_assets_path,
)
from .core_utils import (
    analyze_csharp_config,
    analyze_go_config,
    analyze_java_config,
    analyze_javascript_config,
    analyze_python_config,
    analyze_rust_config,
    categorize_directory,
    create_common_structure,
    create_javascript_config_files,
    create_javascript_structure,
    create_python_dev_config_files,
    create_python_requirements_files,
    create_python_structure,
    matches_project_type,
)
from .env_utils import (
    check_npm_available,
    create_virtual_environment,
    find_pip_executable,
    install_npm_dependencies,
    install_npm_dev_dependencies,
    install_python_dependencies,
)
from .file_utils import (
    create_javascript_source_files,
    create_node_main_files,
    create_python_main_files,
    create_python_test_file,
    create_react_main_files,
    create_vue_main_files,
)
from .platform_utils import (
    get_node_paths,
    get_platform_info,
    get_python_paths,
    get_shell_commands,
)
from .template_utils import (
    generate_cross_platform_template,
    replace_platform_placeholders,
    validate_template_placeholders,
)
from .validation_utils import (
    check_project_name,
    get_validation_summary,
    suggest_project_name,
    validate_project_config,
    validate_project_name,
    validate_project_path,
    validate_project_type,
)
from .variant_detection_utils import VariantDetectionUtils

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "VariantDetectionUtils",
    "analyze_csharp_config",
    "analyze_go_config",
    "analyze_java_config",
    "analyze_javascript_config",
    "analyze_python_config",
    "analyze_rust_config",
    "categorize_directory",
    "check_npm_available",
    "check_project_name",
    "copy_asset_file",
    "copy_asset_type",
    "copy_assets_directory",
    "create_common_structure",
    "create_javascript_config_files",
    "create_javascript_source_files",
    "create_javascript_structure",
    "create_node_main_files",
    "create_python_dev_config_files",
    "create_python_main_files",
    "create_python_requirements_files",
    "create_python_structure",
    "create_python_test_file",
    "create_react_main_files",
    "create_virtual_environment",
    "create_vue_main_files",
    "find_pip_executable",
    "generate_cross_platform_template",
    "get_assets_path",
    "get_node_paths",
    "get_platform_info",
    "get_python_paths",
    "get_shell_commands",
    "get_validation_summary",
    "install_npm_dependencies",
    "install_npm_dev_dependencies",
    "install_python_dependencies",
    "matches_project_type",
    "replace_platform_placeholders",
    "suggest_project_name",
    "validate_project_config",
    "validate_project_name",
    "validate_project_path",
    "validate_project_type",
    "validate_template_placeholders",
]
