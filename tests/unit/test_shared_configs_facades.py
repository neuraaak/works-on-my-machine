#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SHARED CONFIGS FACADES - Remaining thin classmethod coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for the remaining thin config helpers: ``ProjectVariantConfig`` (a
backward-compat facade delegating to ``VariantMappingsConfig``/
``VariantUIConfig``), ``PythonProjectConfig``'s static formatters, and
and ``PythonProjectConfig``'s static formatters.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from womm.shared.configs.project.project_variant_config import ProjectVariantConfig
from womm.shared.configs.project.python_project_config import PythonProjectConfig

# ///////////////////////////////////////////////////////////////
# PROJECT VARIANT CONFIG (FACADE)
# ///////////////////////////////////////////////////////////////


def test_get_variants_for_ui_delegates_to_variant_ui_config():
    variants = ProjectVariantConfig.get_variants_for_ui("python")

    assert variants[0][0] == "py"


def test_get_javascript_project_type_choices_for_ui_delegates():
    choices = ProjectVariantConfig.get_javascript_project_type_choices_for_ui()

    assert any(value == "node" for value, _ in choices)


def test_get_variant_assets_path_delegates_to_variant_mappings_config():
    assert ProjectVariantConfig.get_variant_assets_path("python", "py") == "python/py"


def test_validate_variant_delegates_to_variant_mappings_config():
    assert ProjectVariantConfig.validate_variant("javascript", "vue") is True
    assert ProjectVariantConfig.validate_variant("python", "flask") is False


# ///////////////////////////////////////////////////////////////
# PYTHON PROJECT CONFIG
# ///////////////////////////////////////////////////////////////


def test_get_dev_requirements_content_returns_template():
    assert (
        PythonProjectConfig.get_dev_requirements_content()
        == PythonProjectConfig.DEV_REQUIREMENTS_TEMPLATE
    )


def test_get_requirements_content_returns_template():
    assert (
        PythonProjectConfig.get_requirements_content()
        == PythonProjectConfig.REQUIREMENTS_TEMPLATE
    )


def test_format_dependency_joins_name_and_version():
    assert PythonProjectConfig.format_dependency("ruff", ">=0.5.0") == "ruff>=0.5.0"
