#!/usr/bin/env python3
"""
Setup script for works-on-my-machine package.
"""

from setuptools import setup

setup(
    name="works-on-my-machine",
    version="2.6.8",
    description="Universal development tools for Python and JavaScript",
    author="Neuraaak",
    url="https://github.com/neuraaak/works-on-my-machine",
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "questionary>=2.0.0",
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
