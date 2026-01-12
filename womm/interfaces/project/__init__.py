#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INTERFACES PROJECT - Project Interfaces
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project interfaces for Works On My Machine.

This package contains project interface modules that orchestrate services
for project creation, language-specific operations, and template management.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .create_interface import ProjectCreateInterface
from .detection_interface import ProjectDetectionInterface
from .manager_interface import ProjectManagerInterface
from .setup_interface import ProjectSetupInterface
from .template_interface import TemplateInterface

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ProjectCreateInterface",
    "ProjectDetectionInterface",
    "ProjectManagerInterface",
    "ProjectSetupInterface",
    "TemplateInterface",
]
