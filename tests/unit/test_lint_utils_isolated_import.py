#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST LINT UTILS ISOLATED IMPORT - Import cycle guard
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Guard against the reappearance of the `utils.lint` ↔ `services.lint` cycle.

`womm.utils.lint` must be importable on its own. A fresh interpreter is used
because the pytest session has already imported `womm.services`, which would
hide a cycle by pre-populating `sys.modules`.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import subprocess
import sys

# ///////////////////////////////////////////////////////////////
# ISOLATED IMPORT
# ///////////////////////////////////////////////////////////////


def test_utils_lint_imports_without_preloading_services() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "import womm.utils.lint"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_utils_lint_does_not_pull_in_the_services_package() -> None:
    code = "import sys, womm.utils.lint; print('womm.services' in sys.modules)"
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False"
