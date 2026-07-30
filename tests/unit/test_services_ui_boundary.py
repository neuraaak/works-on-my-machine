#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SERVICES UI BOUNDARY - Layer guard
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Guard the rule that services never reach for the UI layer.

Services hold policy and must stay usable without a terminal; prompting and
rendering belong to the command/UI layer. The check reads the source rather
than the imported modules so that deferred, in-function imports are caught too.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import ast
from pathlib import Path

# Local imports
import womm.services

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////

SERVICES_ROOT = Path(womm.services.__file__).parent


def _ui_imports(source: str, depth: int) -> list[str]:
    """List the UI imports found in a module's source.

    Args:
        source: Python source code of a service module
        depth: Depth of that module inside `womm`, i.e. how many leading dots a
            relative import needs to reach the package root

    Returns:
        list[str]: Human-readable description of each offending import
    """
    offenders: list[str] = []

    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            reaches_root = node.level == depth
            if (reaches_root and module.startswith("ui")) or module.startswith(
                ("womm.ui", "ui.")
            ):
                offenders.append(f"from {'.' * node.level}{module}")
        elif isinstance(node, ast.Import):
            offenders.extend(
                f"import {alias.name}"
                for alias in node.names
                if alias.name.startswith("womm.ui")
            )

    return offenders


# ///////////////////////////////////////////////////////////////
# UI BOUNDARY
# ///////////////////////////////////////////////////////////////


def test_no_service_module_imports_the_ui_layer() -> None:
    offenders: list[str] = []

    for path in SERVICES_ROOT.rglob("*.py"):
        depth = len(path.relative_to(SERVICES_ROOT.parent).parts) - 1
        offenders += [
            f"{path.name}: {found}"
            for found in _ui_imports(path.read_text(encoding="utf-8"), depth)
        ]

    assert offenders == [], f"services must not import the UI layer: {offenders}"


def test_the_guard_detects_the_import_it_was_written_for() -> None:
    # Depth 3: womm/services/<domain>/<module>.py, the shape of the module that
    # used to prompt from within the service layer.
    found = _ui_imports("from ...ui.common.prompts import confirm\n", depth=3)

    assert found == ["from ...ui.common.prompts"]
