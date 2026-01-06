#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UPDATE_README_VERSION - Sync README badge with pyproject version
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Update the version badge in README.md from pyproject.toml.

This keeps the visible version in the README in sync with the
canonical [project].version value defined in pyproject.toml.
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
    """Read version from pyproject.toml [project].version."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text(encoding="utf-8")

    in_project_section = False
    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("[project]"):
            in_project_section = True
            continue

        if (
            in_project_section
            and stripped.startswith("[")
            and not stripped.startswith("[project]")
        ):
            # We left the [project] section without finding a version
            break

        if in_project_section and stripped.startswith("version"):
            match = re.match(r'version\s*=\s*["\']([^"\']+)["\']', stripped)
            if match:
                return match.group(1)

    raise RuntimeError(  # noqa: TRY003
        "Unable to find [project].version in pyproject.toml"
    )


def update_readme(version: str) -> None:
    """Replace version badge in README.md with the given version."""
    readme_path = Path("README.md")
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
        raise RuntimeError("Version badge not found in README.md")  # noqa: TRY003

    readme_path.write_text(new_content, encoding="utf-8")
    print(f"[VERSION] Updated README.md badge to version {version}")


def main() -> None:
    """Entry point."""
    version = read_version()
    update_readme(version)


# ///////////////////////////////////////////////////////////////
# MAIN
# ///////////////////////////////////////////////////////////////

if __name__ == "__main__":
    main()
