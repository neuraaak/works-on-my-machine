#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# MANAGERS PROJECT CREATION - Project Creation Modules
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project creation modules for Works On My Machine.

This package contains project creation functionality for different languages.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .javascript_project_manager import JavaScriptProjectManager
from .project_creator import ProjectCreator
from .python_project_manager import PythonProjectManager

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ProjectCreator",
    "PythonProjectManager",
    "JavaScriptProjectManager",
]
