#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST LOGGING CONFIG - Log location contract
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for ``LoggingConfig`` path resolution.

Logs are **user data**: they belong under the data directory, not next to
the installed code. These tests pin that contract via ``$WOMM_HOME``.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
import pytest

# Local imports
from womm.shared.configs.logging_config import LoggingConfig
from womm.shared.paths import WOMM_HOME_ENV, logs_dir

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def womm_home(tmp_path, monkeypatch):
    """Point ``$WOMM_HOME`` at an isolated directory for the test."""
    home = tmp_path / "womm-home"
    monkeypatch.setenv(WOMM_HOME_ENV, str(home))
    return home


# ///////////////////////////////////////////////////////////////
# TESTS
# ///////////////////////////////////////////////////////////////


def test_log_dir_resolves_under_the_data_directory(womm_home):
    assert LoggingConfig.get_log_dir() == womm_home / "logs"


@pytest.mark.usefixtures("womm_home")
def test_log_dir_is_the_shared_paths_authority():
    """No parallel resolution: the config must defer to ``logs_dir()``."""
    assert LoggingConfig.get_log_dir() == logs_dir()


def test_log_dir_is_created_on_access(womm_home):
    assert not womm_home.exists()

    assert LoggingConfig.get_log_dir().is_dir()


def test_log_file_sits_inside_the_log_dir(womm_home):
    log_file = LoggingConfig.get_log_file()

    assert log_file == womm_home / "logs" / LoggingConfig.LOG_FILE_NAME
    assert log_file.parent.is_dir()


def test_log_dir_follows_womm_home_override(tmp_path, monkeypatch):
    """The location tracks the data dir, never the installation path."""
    elsewhere = tmp_path / "elsewhere"
    monkeypatch.setenv(WOMM_HOME_ENV, str(elsewhere))

    assert LoggingConfig.get_log_dir() == elsewhere / "logs"
