#!/usr/bin/env python3
"""
Import utilities for WOMM CLI.
Handles imports for both development and PyPI installation.
"""

import sys
from pathlib import Path
from typing import Any


def import_shared_module(module_name: str) -> Any:
    """
    Import a shared module, handling both development and PyPI installation.
    
    Args:
        module_name: Name of the module to import (e.g., 'ui', 'core.results')
        
    Returns:
        The imported module
        
    Raises:
        ImportError: If the module cannot be imported
    """
    try:
        # Try direct import first (PyPI installation)
        return __import__(f"shared.{module_name}", fromlist=[module_name.split('.')[-1]])
    except ImportError:
        # Fallback to path insertion (development)
        shared_path = Path(__file__).parent.parent.parent / "shared"
        if shared_path not in sys.path:
            sys.path.insert(0, str(shared_path))
        
        # Try import again
        try:
            return __import__(f"shared.{module_name}", fromlist=[module_name.split('.')[-1]])
        except ImportError as e:
            raise ImportError(f"Cannot import shared.{module_name}: {e}")


def get_shared_module_path() -> Path:
    """
    Get the path to the shared module, handling both development and PyPI installation.
    
    Returns:
        Path to the shared module
    """
    try:
        import shared
        return Path(shared.__file__).parent
    except ImportError:
        # Fallback to development path
        return Path(__file__).parent.parent.parent / "shared"


def get_languages_module_path() -> Path:
    """
    Get the path to the languages module, handling both development and PyPI installation.
    
    Returns:
        Path to the languages module
    """
    try:
        import languages
        return Path(languages.__file__).parent
    except ImportError:
        # Fallback to development path
        return Path(__file__).parent.parent.parent / "languages" 