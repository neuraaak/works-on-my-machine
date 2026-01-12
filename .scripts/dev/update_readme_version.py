#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UPDATE_README_VERSION - Sync README badge and pyproject.toml with __init__.py version
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Update the version badge in README.md and pyproject.toml from womm/__init__.py.

This keeps the visible version in sync with the canonical __version__ value
defined in womm/__init__.py, which is the single source of truth.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports

from __future__ import annotations

import re
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# PUBLIC METHODS
# ///////////////////////////////////////////////////////////////


def read_version() -> str:
    """Read version from womm/__init__.py __version__.

    This is the canonical source of truth for the package version.
    """
    # Project root is the parent of the .scripts/dev directory
    project_root = Path(__file__).resolve().parents[2]
    womm_init_path = project_root / "womm" / "__init__.py"
    content = womm_init_path.read_text(encoding="utf-8")

    # Match __version__ = "X.Y.Z"
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)

    raise RuntimeError("Unable to find __version__ in womm/__init__.py")


def update_pyproject(version: str) -> None:
    """Update version in pyproject.toml [project].version."""
    project_root = Path(__file__).resolve().parents[2]
    pyproject_path = project_root / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")

    # Match version = "X.Y.Z" in [project] section
    in_project_section = False
    lines = content.splitlines()
    new_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("[project]"):
            in_project_section = True
            new_lines.append(line)
            continue

        if (
            in_project_section
            and stripped.startswith("[")
            and not stripped.startswith("[project]")
        ):
            in_project_section = False

        if in_project_section and stripped.startswith("version"):
            # Replace the version line
            match = re.match(r'version\s*=\s*["\']([^"\']+)["\']', stripped)
            if match:
                # Preserve the original formatting (quotes style)
                quote_char = '"' if '"' in stripped else "'"
                indent = len(line) - len(line.lstrip())
                new_lines.append(
                    f"{indent * ' '}version = {quote_char}{version}{quote_char}"
                )
                continue

        new_lines.append(line)

    pyproject_path.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"[VERSION] Updated pyproject.toml version to {version}")


def update_readme(version: str) -> None:
    """Replace version badge in README.md with the given version."""
    project_root = Path(__file__).resolve().parents[2]
    readme_path = project_root / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    # Match shields.io badge: Version-X.Y.Z-orange.svg?style=for-the-badge
    pattern = r"(Version-)(\d+\.\d+\.\d+)(-orange\.svg\?style=for-the-badge\))"
    new_content, count = re.subn(
        pattern,
        rf"\g<1>{version}\g<3>",
        content,
        count=1,
    )

    if count == 0:
        raise RuntimeError("Version badge not found in README.md")

    readme_path.write_text(new_content, encoding="utf-8")
    print(f"[VERSION] Updated README.md badge to version {version}")


def main() -> None:
    """Entry point."""
    version = read_version()
    update_pyproject(version)
    update_readme(version)


# ///////////////////////////////////////////////////////////////
# MAIN
# ///////////////////////////////////////////////////////////////

if __name__ == "__main__":
    main()
