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
# Third-party imports
from setuptools import setup

# ///////////////////////////////////////////////////////////////
# CONFIGURATION
# ///////////////////////////////////////////////////////////////

setup(
    name="works-on-my-machine",
    version="2.7.0",
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
