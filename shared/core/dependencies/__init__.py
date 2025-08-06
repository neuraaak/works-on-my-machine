"""
Core modules for Works On My Machine.

This package contains dependencies utilities and base functionality.
"""

from .dependency_manager import dependency_manager
from .runtime_manager import runtime_manager

# Note: system_detector functions are not exported at module level
# Note: template_helpers functions are not exported at module level

__all__ = [
    "dependency_manager",
    "runtime_manager",
]
