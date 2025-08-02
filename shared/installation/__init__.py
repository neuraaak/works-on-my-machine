"""
Installation modules for Works On My Machine.

This package contains all installation and deployment related functionality.
"""

from .installer import (
    copy_womm_to_user_directory,
    create_bin_directory,
    get_current_womm_path,
    get_target_womm_path,
    setup_path,
)
from .prerequisite_installer import (
    PrerequisiteInstaller,
)
from .uninstaller import (
    remove_context_menu,
    remove_from_unix_path,
    remove_from_windows_path,
    remove_womm_directory,
)

# Note: deploy-devtools.py is a script, not a module
# Functions can be imported directly if needed

__all__ = [
    "setup_path",
    "create_bin_directory",
    "copy_womm_to_user_directory",
    "get_target_womm_path",
    "get_current_womm_path",
    "remove_from_windows_path",
    "remove_from_unix_path",
    "remove_context_menu",
    "remove_womm_directory",
    "PrerequisiteInstaller",
]
