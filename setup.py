#!/usr/bin/env python3
"""
Setup script for WOMM project.
Allows installation with both 'works-on-my-machine' and 'womm' package names.
"""

# Read the version from pyproject.toml
import re

from setuptools import setup

with open("pyproject.toml", encoding="utf-8") as f:
    content = f.read()
    version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
    version = version_match.group(1) if version_match else "0.0.0"

# Read README
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="womm",  # Short name for pip install womm
    version=version,
    description="Universal development tools for Python and JavaScript",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Neuraaak",
    maintainer="Neuraaak",
    url="https://github.com/neuraaak/works-on-my-machine",
    project_urls={
        "Homepage": "https://github.com/neuraaak/works-on-my-machine",
        "Repository": "https://github.com/neuraaak/works-on-my-machine",
        "Bug Tracker": "https://github.com/neuraaak/works-on-my-machine/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "development-tools",
        "python",
        "javascript",
        "automation",
        "project-setup",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "questionary>=2.0.0",
        "InquirerPy>=0.3.4",
    ],
    extras_require={
        "dev": [
            "black>=23.0.0",
            "isort>=5.12.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "bandit>=1.7.0",
            "cryptography>=41.0.0",
            "psutil>=5.9.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "pytest-xdist>=3.0.0",
            "build>=1.0.0",
            "twine>=4.0.0",
            "pyinstaller>=5.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "pytest-xdist>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "womm=womm.cli:main",
        ],
    },
    packages=["womm"],
    include_package_data=True,
    zip_safe=False,
)
