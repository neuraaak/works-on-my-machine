# ///////////////////////////////////////////////////////////////
# CONFTEST - Pytest configuration and fixtures
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Pytest configuration and shared fixtures for Works On My Machine tests.

This module provides common fixtures and pytest configuration used across
all test suites (unit, integration) for consistent test execution.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import tempfile
from collections.abc import Generator
from pathlib import Path

# Third-party imports
import pytest

# ///////////////////////////////////////////////////////////////
# FIXTURES - TEMPORARY RESOURCES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for tests.

    Automatically creates and cleans up a temporary directory for each test,
    ensuring isolation and cleanup between tests.

    Yields:
        Path: Temporary directory path (created and accessible during test)

    Example:
        >>> def test_with_temp_dir(temp_dir):
        ...     test_file = temp_dir / "test.txt"
        ...     test_file.write_text("content")
        ...     assert test_file.exists()
    """
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def temp_file(temp_dir: Path) -> Path:
    """
    Provide a temporary file path inside the temporary directory.

    The file path is created but the file itself is not created automatically.
    Tests can decide how to use the path (create the file, or just use the path).

    Args:
        temp_dir: Temporary directory fixture (injected by pytest)

    Returns:
        Path: Path to a temporary file (not yet created)

    Example:
        >>> def test_temp_file(temp_file):
        ...     # File doesn't exist yet
        ...     assert not temp_file.exists()
        ...     # Test can create it
        ...     temp_file.write_text("test")
        ...     assert temp_file.exists()
    """
    return temp_dir / "temp_file"


# ///////////////////////////////////////////////////////////////
# FIXTURES - PROJECT RESOURCES
# ///////////////////////////////////////////////////////////////


@pytest.fixture(scope="session")
def test_root() -> Path:
    """
    Root directory for all tests.

    Returns:
        Path: Path to tests directory
    """
    return Path(__file__).parent


@pytest.fixture(scope="session")
def project_root() -> Path:
    """
    Root directory of the project.

    Returns:
        Path: Path to project root directory
    """
    return Path(__file__).parent.parent


@pytest.fixture
def temp_project_dir(temp_dir: Path) -> Generator[Path, None, None]:
    """
    Create a temporary project directory with basic structure.

    Args:
        temp_dir: Temporary directory fixture

    Yields:
        Path: Temporary project directory path

    Example:
        >>> def test_project_structure(temp_project_dir):
        ...     assert (temp_project_dir / "src").exists()
        ...     assert (temp_project_dir / "tests").exists()
    """
    project_dir = temp_dir / "test-project"
    project_dir.mkdir()

    # Create basic project structure
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "docs").mkdir()

    # Create some test files
    (project_dir / "src" / "__init__.py").touch()
    (project_dir / "src" / "main.py").write_text("print('Hello, World!')")
    (project_dir / "tests" / "__init__.py").touch()
    (project_dir / "tests" / "test_main.py").write_text("def test_hello(): pass")

    yield project_dir


# ///////////////////////////////////////////////////////////////
# FIXTURES - SAMPLE PROJECTS
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def sample_python_project(temp_dir: Path) -> Generator[Path, None, None]:
    """
    Create a sample Python project for testing.

    Args:
        temp_dir: Temporary directory fixture

    Yields:
        Path: Sample Python project directory

    Example:
        >>> def test_python_setup(sample_python_project):
        ...     assert (sample_python_project / "pyproject.toml").exists()
    """
    project_dir = temp_dir / "sample-python-project"
    project_dir.mkdir()

    # Create project structure
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "docs").mkdir()

    # Create Python files
    (project_dir / "src" / "__init__.py").touch()
    (project_dir / "src" / "main.py").write_text("""
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
""")

    (project_dir / "tests" / "__init__.py").touch()
    (project_dir / "tests" / "test_main.py").write_text("""
import pytest
from src.main import hello_world

def test_hello_world():
    assert hello_world() == "Hello, World!"
""")

    # Create configuration files
    (project_dir / "pyproject.toml").write_text("""
[project]
name = "sample-python-project"
version = "0.1.0"
""")

    yield project_dir


@pytest.fixture
def sample_javascript_project(temp_dir: Path) -> Generator[Path, None, None]:
    """
    Create a sample JavaScript project for testing.

    Args:
        temp_dir: Temporary directory fixture

    Yields:
        Path: Sample JavaScript project directory

    Example:
        >>> def test_js_setup(sample_javascript_project):
        ...     assert (sample_javascript_project / "package.json").exists()
    """
    project_dir = temp_dir / "sample-js-project"
    project_dir.mkdir()

    # Create project structure
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()

    # Create JavaScript files
    (project_dir / "src" / "index.js").write_text("""
function helloWorld() {
    return "Hello, World!";
}

module.exports = { helloWorld };
""")

    (project_dir / "tests" / "index.test.js").write_text("""
const { helloWorld } = require('../src/index.js');

test('helloWorld returns correct string', () => {
    expect(helloWorld()).toBe('Hello, World!');
});
""")

    # Create package.json
    (project_dir / "package.json").write_text("""
{
    "name": "sample-js-project",
    "version": "1.0.0",
    "main": "src/index.js",
    "scripts": {
        "test": "jest"
    }
}
""")

    yield project_dir


# ///////////////////////////////////////////////////////////////
# FIXTURES - TEST DATA
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def sample_project_names() -> list[str]:
    """
    Sample valid project names for testing validation.

    Returns:
        list[str]: List of valid project names
    """
    return [
        "valid-project",
        "valid_project",
        "ValidProject",
        "project123",
        "a" * 50,  # Max length
    ]


@pytest.fixture
def invalid_project_names() -> list[str]:
    """
    Invalid project names for testing validation.

    Returns:
        list[str]: List of invalid project names
    """
    return [
        "",  # Empty
        "a" * 51,  # Too long
        "invalid;project",
        "invalid..project",
        "invalid<project",
        "con",  # Reserved Windows name
        "prn",  # Reserved Windows name
        "invalid project",  # Space
        "invalid/project",  # Slash
        "invalid\\project",  # Backslash
    ]


@pytest.fixture
def sample_paths() -> list[str]:
    """
    Sample paths for testing validation.

    Returns:
        list[str]: List of sample paths
    """
    return [
        "/home/user/project",
        "C:\\Users\\user\\project",
        "./relative/path",
        "project",
        "src/main.py",
        "tests/test_file.py",
    ]


@pytest.fixture
def dangerous_paths() -> list[str]:
    """
    Dangerous paths for testing validation.

    Returns:
        list[str]: List of dangerous paths
    """
    return [
        "path/../dangerous",
        "path\\..\\dangerous",
        "path;dangerous",
        "path|dangerous",
        "path`dangerous",
        "path$(dangerous)",
        "path<dangerous",
        "path>dangerous",
        "path\\x00dangerous",
        "path%00dangerous",
    ]


@pytest.fixture
def valid_commands() -> list[list[str]]:
    """
    Valid commands for testing validation.

    Returns:
        list[list[str]]: List of valid commands
    """
    return [
        ["python", "--version"],
        ["git", "status"],
        ["npm", "install"],
        ["black", "src/"],
        ["flake8", "project"],
        ["eslint", "."],
        ["prettier", "--write", "src/"],
    ]


@pytest.fixture
def dangerous_commands() -> list[list[str]]:
    """
    Dangerous commands for testing validation.

    Returns:
        list[list[str]]: List of dangerous commands
    """
    return [
        ["rm", "-rf", "/"],
        ["sudo", "rm", "-rf", "/"],
        ["python", ";", "rm", "-rf", "/"],
        ["python", "&&", "rm", "-rf", "/"],
        ["python", "|", "rm", "-rf", "/"],
        ["python", "`rm -rf /`"],
        ["python", "$(rm -rf /)"],
        ["cmd", "/c", "del", "C:\\Windows\\System32\\*"],
    ]


# ///////////////////////////////////////////////////////////////
# PYTEST HOOKS
# ///////////////////////////////////////////////////////////////


def pytest_configure(config: pytest.Config) -> None:
    """
    Configure pytest with custom markers.

    Args:
        config: Pytest configuration object
    """
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "robustness: mark test as a robustness test")
    config.addinivalue_line("markers", "security: mark test as a security test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "windows: mark test as Windows specific")
    config.addinivalue_line("markers", "linux: mark test as Linux specific")
    config.addinivalue_line("markers", "macos: mark test as macOS specific")


def pytest_collection_modifyitems(
    config: pytest.Config,  # noqa: ARG001
    items: list[pytest.Item],
) -> None:
    """
    Modify test collection to add markers based on test names.

    Args:
        config: Pytest configuration object (required by pytest hook signature)
        items: List of collected test items
    """
    for item in items:
        # Add unit marker to tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add integration marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add robustness marker to tests in robustness directory
        if "robustness" in str(item.fspath):
            item.add_marker(pytest.mark.robustness)

        # Add security marker to security-related tests
        if "security" in item.name.lower():
            item.add_marker(pytest.mark.security)

        # Add slow marker to tests that might be slow
        if any(
            slow_indicator in item.name.lower()
            for slow_indicator in ["download", "install", "build", "deploy"]
        ):
            item.add_marker(pytest.mark.slow)
