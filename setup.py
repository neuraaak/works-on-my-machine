#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SETUP - Package Setup Script
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Setup script for works-on-my-machine package.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from __future__ import annotations

import re
from pathlib import Path

from setuptools import setup

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////


def read_version() -> str:
    """Read project version from womm/__init__.py.

    This reads the canonical version defined in the package itself.
    """
    womm_init_path = Path(__file__).parent / "womm" / "__init__.py"
    content = womm_init_path.read_text(encoding="utf-8")

    # Match __version__ = "X.Y.Z"
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)

    raise RuntimeError("Unable to find __version__ in womm/__init__.py")


# ///////////////////////////////////////////////////////////////
# CONFIGURATION
# ///////////////////////////////////////////////////////////////

setup(
    name="works-on-my-machine",
    version=read_version(),
    description="Universal development tools for Python and JavaScript",
    author="Neuraaak",
    url="https://github.com/neuraaak/works-on-my-machine",
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "InquirerPy>=0.3.4",
        "tomli>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "womm=womm.cli:main",
        ],
    },
    packages=["womm"],
    include_package_data=True,
    zip_safe=False,
)
