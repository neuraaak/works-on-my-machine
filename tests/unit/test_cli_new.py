"""Unit tests for WOM CLI 'new' commands."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

# Import the CLI modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestCLINewCommands:
    """Test cases for WOM CLI 'new' commands."""

    @pytest.fixture
    def cli_runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    @pytest.fixture
    def mock_secure_cli_manager(self):
        """Mock secure CLI manager."""
        with patch('shared.secure_cli_manager.run_secure_command') as mock_run:
            mock_run.return_value = Mock(
                success=True,
                security_validated=True,
                returncode=0,
                stdout="Mock output",
                stderr=""
            )
            yield mock_run

    @pytest.fixture
    def mock_security_validator(self):
        """Mock security validator."""
        with patch('shared.security_validator.validate_user_input') as mock_validate:
            with patch('shared.security_validator.security_validator') as mock_validator:
                mock_validate.return_value = (True, "")
                mock_validator.validate_script_execution.return_value = (True, "")
                yield {
                    'validate_user_input': mock_validate,
                    'security_validator': mock_validator
                }

    def test_new_python_project_valid(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test creating a new Python project with valid name."""
        from womm import womm as cli

        result = cli_runner.invoke(cli, ['new', 'python', 'test-project'])

        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

        # Check that the command was called with correct arguments
        call_args = mock_secure_cli_manager.call_args
        assert 'python' in call_args[0][0]
        assert 'test-project' in call_args[0][0]

    def test_new_python_project_invalid_name(self, cli_runner, mock_security_validator):
        """Test creating a new Python project with invalid name."""
        from womm import womm as cli

        # Mock validation to fail
        mock_security_validator['validate_user_input'].return_value = (False, "Invalid project name")

        result = cli_runner.invoke(cli, ['new', 'python', 'invalid;project'])

        assert result.exit_code == 1
        assert "Invalid project name" in result.output

    def test_new_python_project_current_dir(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test creating a Python project in current directory."""
        from womm import womm

        result = cli_runner.invoke(womm, ['new', 'python', '--current-dir'])

        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

        # Check that the command was called with --current-dir
        call_args = mock_secure_cli_manager.call_args
        assert '--current-dir' in call_args[0][0]

    def test_new_javascript_project_valid(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test creating a new JavaScript project with valid name."""
        from womm import womm

        result = cli_runner.invoke(womm, ['new', 'javascript', 'test-js-project'])

        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

        # Check that the command was called with correct arguments
        call_args = mock_secure_cli_manager.call_args
        assert 'javascript' in call_args[0][0]
        assert 'test-js-project' in call_args[0][0]

    def test_new_javascript_project_with_type(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test creating a new JavaScript project with specific type."""
        from womm import womm

        result = cli_runner.invoke(womm, ['new', 'javascript', 'test-react-project', '--type', 'react'])

        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

        # Check that the command was called with type argument
        call_args = mock_secure_cli_manager.call_args
        assert '--type' in call_args[0][0]
        assert 'react' in call_args[0][0]

    def test_new_detect_project(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test creating a project with auto-detection."""
        from womm import womm

        result = cli_runner.invoke(womm, ['new', 'detect', 'test-project'])

        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

        # Check that the command was called with detect
        call_args = mock_secure_cli_manager.call_args
        assert 'detect' in call_args[0][0]

    def test_new_detect_project_current_dir(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test auto-detection in current directory."""
        from womm import womm

        result = cli_runner.invoke(womm, ['new', 'detect', '--current-dir'])

        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

        # Check that the command was called with --current-dir
        call_args = mock_secure_cli_manager.call_args
        assert '--current-dir' in call_args[0][0]


class TestCLINewErrorHandling:
    """Test error handling for 'new' commands."""

    @pytest.fixture
    def cli_runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    @pytest.fixture
    def mock_security_validator(self):
        """Mock security validator."""
        with patch('shared.security_validator.validate_user_input') as mock_validate:
            with patch('shared.security_validator.security_validator') as mock_validator:
                mock_validate.return_value = (True, "")
                mock_validator.validate_script_execution.return_value = (True, "")
                yield {
                    'validate_user_input': mock_validate,
                    'security_validator': mock_validator
                }

    def test_new_project_script_validation_failure(self, cli_runner, mock_security_validator):
        """Test handling of script validation failure."""
        from womm import womm

        # Mock script validation to fail
        mock_security_validator['security_validator'].validate_script_execution.return_value = (
            False, "Script validation failed"
        )

        result = cli_runner.invoke(womm, ['new', 'python', 'test-project'])

        assert result.exit_code == 1
        assert "Script validation failed" in result.output

    def test_new_project_command_execution_failure(self, cli_runner, mock_security_validator):
        """Test handling of command execution failure."""
        from womm import womm

        with patch('shared.secure_cli_manager.run_secure_command') as mock_run:
            mock_run.return_value = Mock(
                success=False,
                security_validated=True,
                returncode=1,
                stdout="",
                stderr="Command failed"
            )

            result = cli_runner.invoke(womm, ['new', 'python', 'test-project'])

            assert result.exit_code == 1

    def test_new_project_security_validation_failure(self, cli_runner, mock_security_validator):
        """Test handling of security validation failure."""
        from womm import womm

        with patch('shared.secure_cli_manager.run_secure_command') as mock_run:
            mock_run.return_value = Mock(
                success=True,
                security_validated=False,
                returncode=0,
                stdout="",
                stderr="Security validation failed"
            )

            result = cli_runner.invoke(womm, ['new', 'python', 'test-project'])

            assert result.exit_code == 1


class TestCLINewArgumentValidation:
    """Test argument validation for 'new' commands."""

    @pytest.fixture
    def cli_runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    @pytest.fixture
    def mock_secure_cli_manager(self):
        """Mock secure CLI manager."""
        with patch('shared.secure_cli_manager.run_secure_command') as mock_run:
            mock_run.return_value = Mock(
                success=True,
                security_validated=True,
                returncode=0,
                stdout="Mock output",
                stderr=""
            )
            yield mock_run

    @pytest.fixture
    def mock_security_validator(self):
        """Mock security validator."""
        with patch('shared.security_validator.validate_user_input') as mock_validate:
            with patch('shared.security_validator.security_validator') as mock_validator:
                mock_validate.return_value = (True, "")
                mock_validator.validate_script_execution.return_value = (True, "")
                yield {
                    'validate_user_input': mock_validate,
                    'security_validator': mock_validator
                }

    def test_javascript_project_type_validation(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test JavaScript project type validation."""
        from womm import womm

        # Test valid types
        valid_types = ['node', 'react', 'vue', 'express']
        for project_type in valid_types:
            result = cli_runner.invoke(womm, ['new', 'javascript', 'test-project', '--type', project_type])
            assert result.exit_code == 0

        # Test invalid type
        result = cli_runner.invoke(womm, ['new', 'javascript', 'test-project', '--type', 'invalid'])
        assert result.exit_code != 0

    def test_new_command_missing_project_name(self, cli_runner):
        """Test new command without project name."""
        from womm import womm

        # Python without project name should work with --current-dir
        result = cli_runner.invoke(womm, ['new', 'python', '--current-dir'])
        assert result.exit_code == 0

        # JavaScript without project name should work with --current-dir
        result = cli_runner.invoke(womm, ['new', 'javascript', '--current-dir'])
        assert result.exit_code == 0

        # Detect without project name should work with --current-dir
        result = cli_runner.invoke(womm, ['new', 'detect', '--current-dir'])
        assert result.exit_code == 0
