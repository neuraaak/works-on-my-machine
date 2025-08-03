#!/usr/bin/env python3
"""
Path management utilities for WOMM CLI.
Provides path resolution and validation functions.
"""

import sys
from pathlib import Path

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent

def get_shared_path() -> Path:
    """Get the shared modules path."""
    return get_project_root() / "shared"

def resolve_script_path(relative_path: str) -> Path:
    """Resolve a script path relative to the project root."""
    return get_project_root() / relative_path

def validate_script_exists(script_path: Path) -> bool:
    """Validate that a script file exists and is executable."""
    return script_path.exists() and script_path.is_file()

# Export path functions
__all__ = [
    "get_project_root",
    "get_shared_path",
    "resolve_script_path",
    "validate_script_exists",
]
