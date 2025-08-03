"""
Project management modules for Works On My Machine.

This package contains project detection and environment management functionality.
"""

from .environment_manager import EnvironmentManager
from .project_detector import ProjectDetector
from .vscode_config import generate_vscode_config

__all__ = [
    "ProjectDetector",
    "EnvironmentManager",
    "generate_vscode_config",
]
