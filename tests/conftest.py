"""
Pytest configuration and shared fixtures for Works On My Machine tests.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


@pytest.fixture(scope="session")
def test_root():
    """Root directory for all tests."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def project_root():
    """Root directory of the project."""
    return Path(__file__).parent.parent


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_project_dir(temp_dir):
    """Create a temporary project directory with basic structure."""
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


@pytest.fixture
def mock_cli_manager():
    """Mock CLI manager for testing."""
    with patch("shared.cli_manager.run_command") as mock_run:
        mock_run.return_value = Mock(
            success=True,
            returncode=0,
            stdout="Mock output",
            stderr="",
            command=["mock", "command"],
        )
        yield mock_run


@pytest.fixture
def mock_secure_cli_manager():
    """Mock secure CLI manager for testing."""
    with patch("shared.secure_cli_manager.run_secure_command") as mock_run:
        mock_run.return_value = Mock(
            success=True,
            security_validated=True,
            returncode=0,
            stdout="Mock secure output",
            stderr="",
            command=["mock", "secure", "command"],
            execution_time=0.1,
        )
        yield mock_run


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing command execution."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(
            returncode=0, stdout="Mock subprocess output", stderr=""
        )
        yield mock_run


@pytest.fixture
def mock_platform():
    """Mock platform for testing cross-platform functionality."""
    with patch("platform.system") as mock_system:
        mock_system.return_value = "Linux"
        yield mock_system


@pytest.fixture
def mock_shutil():
    """Mock shutil for testing file operations."""
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/bin/mock"
        yield mock_which


@pytest.fixture
def mock_pathlib():
    """Mock pathlib for testing path operations."""
    with patch("pathlib.Path") as mock_path:
        mock_path.return_value = Mock(
            exists=lambda: True,
            is_file=lambda: True,
            is_dir=lambda: False,
            parent=Mock(),
            name="mock_file.py",
            suffix=".py",
            resolve=lambda: Mock(),
        )
        yield mock_path


@pytest.fixture
def mock_click():
    """Mock click for testing CLI commands."""
    with patch("click.echo") as mock_echo:
        with patch("click.Context") as mock_context:
            mock_context.return_value = Mock()
            yield mock_echo


@pytest.fixture
def mock_winreg():
    """Mock winreg for testing Windows registry operations."""
    with patch("winreg.CreateKey") as mock_create:
        with patch("winreg.SetValueEx") as mock_set:
            with patch("winreg.DeleteKey") as mock_delete:
                mock_create.return_value = Mock()
                mock_set.return_value = None
                mock_delete.return_value = None
                yield {"create": mock_create, "set": mock_set, "delete": mock_delete}


@pytest.fixture
def mock_urllib():
    """Mock urllib for testing download operations."""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = Mock(
            read=lambda: b"Mock downloaded content", close=lambda: None
        )
        yield mock_urlopen


@pytest.fixture
def mock_json():
    """Mock json for testing JSON operations."""
    with patch("json.dump") as mock_dump:
        with patch("json.load") as mock_load:
            mock_dump.return_value = None
            mock_load.return_value = {"mock": "data"}
            yield {"dump": mock_dump, "load": mock_load}


@pytest.fixture
def mock_logging():
    """Mock logging for testing log operations."""
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger


@pytest.fixture
def sample_python_project(temp_dir):
    """Create a sample Python project for testing."""
    project_dir = temp_dir / "sample-python-project"
    project_dir.mkdir()

    # Create project structure
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "docs").mkdir()

    # Create Python files
    (project_dir / "src" / "__init__.py").touch()
    (project_dir / "src" / "main.py").write_text(
        """
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
"""
    )

    (project_dir / "tests" / "__init__.py").touch()
    (project_dir / "tests" / "test_main.py").write_text(
        """
import pytest
from src.main import hello_world

def test_hello_world():
    assert hello_world() == "Hello, World!"
"""
    )

    # Create configuration files
    (project_dir / "pyproject.toml").write_text(
        """
[project]
name = "sample-python-project"
version = "0.1.0"
"""
    )

    yield project_dir


@pytest.fixture
def sample_javascript_project(temp_dir):
    """Create a sample JavaScript project for testing."""
    project_dir = temp_dir / "sample-js-project"
    project_dir.mkdir()

    # Create project structure
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()

    # Create JavaScript files
    (project_dir / "src" / "index.js").write_text(
        """
function helloWorld() {
    return "Hello, World!";
}

module.exports = { helloWorld };
"""
    )

    (project_dir / "tests" / "index.test.js").write_text(
        """
const { helloWorld } = require('../src/index.js');

test('helloWorld returns correct string', () => {
    expect(helloWorld()).toBe('Hello, World!');
});
"""
    )

    # Create package.json
    (project_dir / "package.json").write_text(
        """
{
    "name": "sample-js-project",
    "version": "1.0.0",
    "main": "src/index.js",
    "scripts": {
        "test": "jest"
    }
}
"""
    )

    yield project_dir


@pytest.fixture
def mock_environment():
    """Mock environment variables for testing."""
    original_env = os.environ.copy()

    # Set test environment variables
    test_env = {
        "HOME": "/home/testuser",
        "USER": "testuser",
        "PATH": "/usr/bin:/usr/local/bin",
        "PYTHONPATH": "/usr/lib/python3.8",
        "NODE_PATH": "/usr/lib/node_modules",
    }

    os.environ.update(test_env)

    yield test_env

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_file_system(temp_dir):
    """Mock file system operations for testing."""
    with patch("pathlib.Path.exists") as mock_exists:
        with patch("pathlib.Path.is_file") as mock_is_file:
            with patch("pathlib.Path.is_dir") as mock_is_dir:
                with patch("pathlib.Path.mkdir") as mock_mkdir:
                    with patch("pathlib.Path.write_text") as mock_write:
                        with patch("pathlib.Path.read_text") as mock_read:
                            mock_exists.return_value = True
                            mock_is_file.return_value = True
                            mock_is_dir.return_value = False
                            mock_mkdir.return_value = None
                            mock_write.return_value = None
                            mock_read.return_value = "Mock file content"

                            yield {
                                "exists": mock_exists,
                                "is_file": mock_is_file,
                                "is_dir": mock_is_dir,
                                "mkdir": mock_mkdir,
                                "write_text": mock_write,
                                "read_text": mock_read,
                            }


@pytest.fixture
def mock_tools():
    """Mock development tools for testing."""
    tools = {
        "python": "/usr/bin/python3",
        "node": "/usr/bin/node",
        "npm": "/usr/bin/npm",
        "git": "/usr/bin/git",
        "black": "/usr/local/bin/black",
        "flake8": "/usr/local/bin/flake8",
        "eslint": "/usr/local/bin/eslint",
        "prettier": "/usr/local/bin/prettier",
    }

    with patch("shutil.which") as mock_which:

        def which_side_effect(tool):
            return tools.get(tool)

        mock_which.side_effect = which_side_effect
        yield tools


@pytest.fixture
def mock_versions():
    """Mock tool versions for testing."""
    versions = {
        "python": "Python 3.8.10",
        "node": "v16.14.0",
        "npm": "8.3.1",
        "git": "git version 2.34.1",
        "black": "black, version 22.3.0",
        "flake8": "4.0.1",
        "eslint": "v8.15.0",
        "prettier": "2.6.2",
    }

    yield versions


@pytest.fixture
def mock_package_managers():
    """Mock package managers for testing."""
    managers = {
        "apt": "/usr/bin/apt",
        "yum": "/usr/bin/yum",
        "dnf": "/usr/bin/dnf",
        "pacman": "/usr/bin/pacman",
        "brew": "/usr/local/bin/brew",
        "choco": "C:\\ProgramData\\chocolatey\\bin\\choco.exe",
        "winget": "C:\\Program Files\\WindowsApps\\Microsoft.Winget.Source_8wekyb3d8bbwe\\winget.exe",
    }

    with patch("shutil.which") as mock_which:

        def which_side_effect(manager):
            return managers.get(manager)

        mock_which.side_effect = which_side_effect
        yield managers


# Test data fixtures
@pytest.fixture
def sample_project_names():
    """Sample project names for testing validation."""
    return [
        "valid-project",
        "valid_project",
        "ValidProject",
        "project123",
        "a" * 50,  # Max length
    ]


@pytest.fixture
def invalid_project_names():
    """Invalid project names for testing validation."""
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
def sample_paths():
    """Sample paths for testing validation."""
    return [
        "/home/user/project",
        "C:\\Users\\user\\project",
        "./relative/path",
        "project",
        "src/main.py",
        "tests/test_file.py",
    ]


@pytest.fixture
def dangerous_paths():
    """Dangerous paths for testing validation."""
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
def valid_commands():
    """Valid commands for testing validation."""
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
def dangerous_commands():
    """Dangerous commands for testing validation."""
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


# Configuration for pytest
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "security: mark test as a security test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "windows: mark test as Windows specific")
    config.addinivalue_line("markers", "linux: mark test as Linux specific")
    config.addinivalue_line("markers", "macos: mark test as macOS specific")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit marker to tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add integration marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add security marker to security-related tests
        if "security" in item.name.lower():
            item.add_marker(pytest.mark.security)

        # Add slow marker to tests that might be slow
        if any(
            slow_indicator in item.name.lower()
            for slow_indicator in ["download", "install", "build", "deploy"]
        ):
            item.add_marker(pytest.mark.slow)
