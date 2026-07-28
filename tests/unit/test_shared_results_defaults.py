#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SHARED RESULTS DEFAULTS - __post_init__/__str__/__bool__ coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for the mutable-default normalization (``__post_init__``) and dunder
methods (``__str__``/``__bool__``) on the ``Result`` dataclasses.

Each ``__post_init__`` here follows the same pattern: replace a ``None``
default with an empty ``list``/``dict`` (the standard dataclass workaround
for not being able to use mutable defaults directly) — worth a one-line
assertion per field since a typo in the field name silently breaks it.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from womm.shared.results.base import BaseResult, CommandResult
from womm.shared.results.file_results import FileSearchResult
from womm.shared.results.installation_results import WOMMInstallerVerificationResult
from womm.shared.results.project_results import (
    ProjectDetectionResult,
    SetupResult,
)
from womm.shared.results.security_results import (
    SecurityReportResult,
    SecurityResult,
    ValidationResult,
)
from womm.shared.results.system_results import (
    EnvironmentRefreshResult,
    PathOperationResult,
    PrerequisitesCheckResult,
    PrerequisitesInstallResult,
)

# ///////////////////////////////////////////////////////////////
# BASE RESULT
# ///////////////////////////////////////////////////////////////


def test_base_result_bool_reflects_success():
    assert bool(BaseResult(success=True)) is True
    assert bool(BaseResult(success=False)) is False


def test_base_result_str_success_shows_message():
    assert str(BaseResult(success=True, message="done")) == "Success: done"


def test_base_result_str_failure_shows_error():
    assert str(BaseResult(success=False, error="boom")) == "Failed: boom"


def test_command_result_post_init_defaults_command_to_empty_list():
    result = CommandResult(returncode=0, command=None)

    assert result.command == []


def test_command_result_bool_reflects_returncode():
    assert bool(CommandResult(returncode=0)) is True
    assert bool(CommandResult(returncode=1)) is False


def test_command_result_str_includes_validation_and_time():
    result = CommandResult(returncode=0, security_validated=True, execution_time=1.5)

    assert str(result) == "CommandResult(success=True, validated=True, time=1.50s)"


# ///////////////////////////////////////////////////////////////
# FILE RESULTS
# ///////////////////////////////////////////////////////////////


def test_file_search_result_post_init_defaults_files_found_to_empty_list():
    result = FileSearchResult(success=True, files_found=None)

    assert result.files_found == []


# ///////////////////////////////////////////////////////////////
# INSTALLATION RESULTS
# ///////////////////////////////////////////////////////////////


def test_womm_installer_verification_result_post_init_defaults():
    result = WOMMInstallerVerificationResult(success=True)

    assert result.path_entries == []
    assert result.accessible_commands == []


# ///////////////////////////////////////////////////////////////
# PROJECT RESULTS
# ///////////////////////////////////////////////////////////////


def test_setup_result_post_init_defaults_all_lists():
    result = SetupResult(success=True)

    assert result.files_created == []
    assert result.tools_configured == []
    assert result.warnings == []


def test_project_detection_result_post_init_defaults():
    result = ProjectDetectionResult(success=True)

    assert result.detected_files == []
    assert result.configuration_files == {}


# ///////////////////////////////////////////////////////////////
# SECURITY RESULTS
# ///////////////////////////////////////////////////////////////


def test_validation_result_post_init_defaults_validation_rules():
    result = ValidationResult(success=True)

    assert result.validation_rules == []


def test_security_result_post_init_defaults_both_lists():
    result = SecurityResult(success=True)

    assert result.threats_detected == []
    assert result.recommendations == []


def test_security_report_result_post_init_defaults_both_lists():
    result = SecurityReportResult(success=True)

    assert result.arguments == []
    assert result.checks_performed == []


# ///////////////////////////////////////////////////////////////
# SYSTEM RESULTS
# ///////////////////////////////////////////////////////////////


def test_path_operation_result_post_init_defaults_path_entries():
    result = PathOperationResult(success=True)

    assert result.path_entries == []


def test_environment_refresh_result_post_init_defaults_environment_info():
    result = EnvironmentRefreshResult(success=True)

    assert result.environment_info == {}


def test_prerequisites_check_result_post_init_defaults():
    result = PrerequisitesCheckResult(success=True)

    assert result.checked_tools == []
    assert result.results == {}
    assert result.missing_tools == []


def test_prerequisites_install_result_post_init_defaults():
    result = PrerequisitesInstallResult(success=True)

    assert result.selected_tools == []
    assert result.installation_results == {}
    assert result.failed_installations == []
