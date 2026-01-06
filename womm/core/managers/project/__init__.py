#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# MANAGERS PROJECT - Project Management Modules
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project management modules for Works On My Machine.

This package contains project creation and management functionality
including project creators, language-specific managers, and template management.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .creation.javascript_project_manager import JavaScriptProjectManager
from .creation.project_creator import ProjectCreator
from .creation.python_project_manager import PythonProjectManager
from .project_manager import ProjectManager
from .templates.template_manager import TemplateManager

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ProjectManager",
    "ProjectCreator",
    "PythonProjectManager",
    "JavaScriptProjectManager",
    "TemplateManager",
]
