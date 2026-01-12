#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UTILS - Pure Utility Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for Works On My Machine.

This package contains stateless utility functions organized by domain.
Import utilities from the appropriate sub-package:

    from womm.utils.common import get_project_root, is_python_file
    from womm.utils.project import validate_project_name, create_python_structure
    from womm.utils.system import get_environment_info, refresh_path_from_registry
    from womm.utils.context import build_command_with_parameter, validate_label
    from womm.utils.cspell import format_spell_check_results
    from womm.utils.lint import parse_lint_output, validate_lint_result
    from womm.utils.dependencies import build_install_command, parse_version
    from womm.utils.security import validate_permission_command
    from womm.utils.womm_deployment import get_womm_installation_path

Available sub-packages:
- common: File scanning and path resolution utilities
- context: Context menu utilities
- cspell: Spell checking utilities
- dependencies: Package/runtime management utilities
- lint: Linting utilities
- project: Project creation and validation utilities
- security: Security validation utilities
- system: System path and environment utilities
- womm_deployment: WOMM installation utilities
"""

# ///////////////////////////////////////////////////////////////
# PUBLIC API - Sub-packages only
# ///////////////////////////////////////////////////////////////

__all__: list[str] = [
    "common",
    "context",
    "cspell",
    "dependencies",
    "lint",
    "project",
    "security",
    "system",
    "womm_deployment",
]
