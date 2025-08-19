"""
Project management modules for Works On My Machine.

This package contains project detection and environment management functionality.
"""

from ...utils.project.project_detector import ProjectDetector
from ...utils.project.vscode_config import generate_vscode_config
from .environment_manager import EnvironmentManager

__all__ = [
    "ProjectDetector",
    "EnvironmentManager",
    "generate_vscode_config",
]
