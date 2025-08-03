"""
Unit tests for secure CLI manager module.
"""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from shared.secure_cli_manager import (
    SecureCLIManager,
    SecureCommandResult,
    check_tool_secure,
    get_tool_version_secure,
    run_secure_command,
    run_secure_interactive,
    run_secure_silent,
)


class TestSecureCommandResult:
    """Test cases for SecureCommandResult class."""

    def test_init(self):
        """Test SecureCommandResult initialization."""
        result = SecureCommandResult(
            returncode=0,
            stdout="test output",
            stderr="test error",
            command=["test", "command"],
            cwd=Path("/test"),
            security_validated=True,
            execution_time=1.5,
        )

        assert result.returncode == 0
        assert result.stdout == "test output"
        assert result.stderr == "test error"
        assert result.command == ["test", "command"]
        assert result.cwd == Path("/test")
        assert result.success is True
        assert result.security_validated is True
        assert result.execution_time == 1.5

    def test_bool_representation(self):
        """Test boolean representation of SecureCommandResult."""
        # Successful and validated
        result = SecureCommandResult(0, security_validated=True)
        assert bool(result) is True

        # Successful but not validated
        result = SecureCommandResult(0, security_validated=False)
        assert bool(result) is False

        # Failed but validated
        result = SecureCommandResult(1, security_validated=True)
        assert bool(result) is False

        # Failed and not validated
        result = SecureCommandResult(1, security_validated=False)
        assert bool(result) is False

    def test_str_representation(self):
        """Test string representation of SecureCommandResult."""
        result = SecureCommandResult(
            returncode=0, security_validated=True, execution_time=1.23
        )

        str_repr = str(result)
        assert "SecureCommandResult" in str_repr
        assert "success=True" in str_repr
        assert "validated=True" in str_repr
        assert "time=1.23" in str_repr


class TestSecureCLIManager:
    """Test cases for SecureCLIManager class."""

    def test_init(self):
        """Test SecureCLIManager initialization."""
        manager = SecureCLIManager(
            default_cwd="/test/cwd",
            verbose=False,
            capture_output=False,
            check=True,
            timeout=30,
            max_retries=5,
            retry_delay=2.0,
        )

        assert manager.default_cwd == Path("/test/cwd")
        assert manager.verbose is False
        assert manager.capture_output is False
        assert manager.check is True
        assert manager.timeout == 30
        assert manager.max_retries == 5
        assert manager.retry_delay == 2.0
        assert hasattr(manager, "security_validator")
        assert hasattr(manager, "logger")

    def test_setup_logging(self):
        """Test logging setup."""
        manager = SecureCLIManager()

        assert hasattr(manager, "logger")
        assert manager.logger.name == "secure_cli_manager"
        assert manager.logger.level == 20  # INFO level

    @patch("shared.secure_cli_manager.subprocess.run")
    def test_run_success(self, mock_subprocess):
        """Test successful command execution."""
        mock_subprocess.return_value = Mock(
            returncode=0, stdout="Success output", stderr=""
        )

        manager = SecureCLIManager(verbose=False)
        result = manager.run(["python", "--version"], "Test command")

        assert result.success is True
        assert result.security_validated is True
        assert result.stdout == "Success output"
        assert result.stderr == ""
        assert result.returncode == 0
        assert result.execution_time > 0

    @patch("shared.secure_cli_manager.subprocess.run")
    def test_run_failure(self, mock_subprocess):
        """Test failed command execution."""
        mock_subprocess.return_value = Mock(
            returncode=1, stdout="", stderr="Command failed"
        )

        manager = SecureCLIManager(verbose=False)
        result = manager.run(["invalid", "command"], "Test command")

        assert result.success is False
        assert result.security_validated is True
        assert result.stdout == ""
        assert result.stderr == "Command failed"
        assert result.returncode == 1

    def test_run_invalid_command(self):
        """Test execution with invalid command."""
        manager = SecureCLIManager(verbose=False)
        result = manager.run(["rm", "-rf", "/"], "Dangerous command")

        assert result.success is False
        assert result.security_validated is False
        assert "not allowed" in result.stderr

    @patch("shared.secure_cli_manager.subprocess.run")
    def test_run_with_retry_success(self, mock_subprocess):
        """Test command execution with retry on success."""
        # First call fails, second succeeds
        mock_subprocess.side_effect = [
            Mock(returncode=1, stdout="", stderr="First attempt failed"),
            Mock(returncode=0, stdout="Success", stderr=""),
        ]

        manager = SecureCLIManager(verbose=False, max_retries=2)
        result = manager.run(["python", "--version"], "Test command")

        assert result.success is True
        assert mock_subprocess.call_count == 2

    @patch("shared.secure_cli_manager.subprocess.run")
    def test_run_with_retry_all_fail(self, mock_subprocess):
        """Test command execution with all retries failing."""
        mock_subprocess.side_effect = subprocess.TimeoutExpired(
            cmd=["python", "--version"], timeout=30
        )

        manager = SecureCLIManager(verbose=False, max_retries=3)
        result = manager.run(["python", "--version"], "Test command")

        assert result.success is False
        assert "All 3 attempts failed" in result.stderr
        assert mock_subprocess.call_count == 3

    @patch("shared.secure_cli_manager.subprocess.run")
    def test_run_timeout(self, mock_subprocess):
        """Test command execution with timeout."""
        mock_subprocess.side_effect = subprocess.TimeoutExpired(
            cmd=["python", "--version"], timeout=5
        )

        manager = SecureCLIManager(verbose=False, timeout=5)
        result = manager.run(["python", "--version"], "Test command")

        assert result.success is False
        assert "Timeout" in result.stderr

    def test_run_invalid_working_directory(self):
        """Test execution with invalid working directory."""
        manager = SecureCLIManager(verbose=False)
        result = manager.run(
            ["python", "--version"], "Test command", cwd="/non/existent/path"
        )

        assert result.success is False
        assert "Invalid working directory" in result.stderr

    def test_run_silent(self):
        """Test silent command execution."""
        with patch.object(SecureCLIManager, "run") as mock_run:
            mock_run.return_value = Mock(success=True, security_validated=True)

            manager = SecureCLIManager()
            result = manager.run_silent(["python", "--version"])

            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[1]["verbose"] is False
            assert call_args[1]["capture_output"] is True

    def test_run_interactive(self):
        """Test interactive command execution."""
        with patch.object(SecureCLIManager, "run") as mock_run:
            mock_run.return_value = Mock(success=True, security_validated=True)

            manager = SecureCLIManager()
            result = manager.run_interactive(["python", "--version"])

            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[1]["capture_output"] is False

    def test_run_with_validation(self):
        """Test command execution with strict validation."""
        with patch.object(SecureCLIManager, "run") as mock_run:
            mock_run.return_value = Mock(success=True, security_validated=True)

            manager = SecureCLIManager()
            result = manager.run_with_validation(["python", "--version"], "Test")

            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[1]["validate_security"] is True

    def test_check_command_available(self):
        """Test command availability check."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/python"

            manager = SecureCLIManager()
            result = manager.check_command_available("python")

            assert result is True
            mock_which.assert_called_once_with("python")

    def test_check_command_available_not_found(self):
        """Test command availability check when not found."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None

            manager = SecureCLIManager()
            result = manager.check_command_available("nonexistent")

            assert result is False

    def test_check_command_available_invalid(self):
        """Test command availability check with invalid command."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/rm"

            manager = SecureCLIManager()
            result = manager.check_command_available("rm")

            assert result is False  # rm is not in allowed commands

    @patch("shared.secure_cli_manager.subprocess.run")
    def test_get_command_version(self, mock_subprocess):
        """Test getting command version."""
        mock_subprocess.return_value = Mock(
            returncode=0, stdout="Python 3.8.10\n", stderr=""
        )

        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/python"

            manager = SecureCLIManager(verbose=False)
            version = manager.get_command_version("python")

            assert version == "Python 3.8.10"

    def test_get_command_version_not_available(self):
        """Test getting version of unavailable command."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None

            manager = SecureCLIManager()
            version = manager.get_command_version("nonexistent")

            assert version is None

    def test_find_executable(self):
        """Test finding first available executable."""
        with patch("shutil.which") as mock_which:

            def which_side_effect(cmd):
                return "/usr/bin/python" if cmd == "python" else None

            mock_which.side_effect = which_side_effect

            manager = SecureCLIManager()
            result = manager.find_executable(["python", "python3", "py"])

            assert result == "/usr/bin/python"

    def test_find_executable_none_found(self):
        """Test finding executable when none are available."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None

            manager = SecureCLIManager()
            result = manager.find_executable(["nonexistent1", "nonexistent2"])

            assert result is None

    def test_create_shell_command(self, temp_dir):
        """Test creating temporary shell script."""
        manager = SecureCLIManager()
        script_content = "#!/bin/bash\necho 'Hello, World!'"

        script_path = manager.create_shell_command(script_content)

        assert script_path.exists()
        assert script_path.read_text() == script_content

        # Clean up
        script_path.unlink()

    def test_create_shell_command_too_large(self):
        """Test creating shell script with content too large."""
        manager = SecureCLIManager()
        large_content = "a" * 10001  # Larger than 10000 limit

        with pytest.raises(ValueError, match="Script content too large"):
            manager.create_shell_command(large_content)

    def test_create_shell_command_dangerous_content(self):
        """Test creating shell script with dangerous content."""
        manager = SecureCLIManager()
        dangerous_content = "echo 'test'; rm -rf /"

        with pytest.raises(ValueError, match="Script contains dangerous pattern"):
            manager.create_shell_command(dangerous_content)


class TestGlobalFunctions:
    """Test cases for global functions."""

    @patch("shared.secure_cli_manager.default_secure_cli")
    def test_run_secure_command(self, mock_default_cli):
        """Test run_secure_command function."""
        mock_result = Mock(success=True, security_validated=True)
        mock_default_cli.run.return_value = mock_result

        result = run_secure_command(["python", "--version"], "Test command")

        assert result == mock_result
        mock_default_cli.run.assert_called_once_with(
            ["python", "--version"], "Test command"
        )

    @patch("shared.secure_cli_manager.default_secure_cli")
    def test_run_secure_silent(self, mock_default_cli):
        """Test run_secure_silent function."""
        mock_result = Mock(success=True, security_validated=True)
        mock_default_cli.run_silent.return_value = mock_result

        result = run_secure_silent(["python", "--version"])

        assert result == mock_result
        mock_default_cli.run_silent.assert_called_once_with(["python", "--version"])

    @patch("shared.secure_cli_manager.default_secure_cli")
    def test_run_secure_interactive(self, mock_default_cli):
        """Test run_secure_interactive function."""
        mock_result = Mock(success=True, security_validated=True)
        mock_default_cli.run_interactive.return_value = mock_result

        result = run_secure_interactive(["python", "--version"])

        assert result == mock_result
        mock_default_cli.run_interactive.assert_called_once_with(
            ["python", "--version"]
        )

    @patch("shared.secure_cli_manager.default_secure_cli")
    def test_check_tool_secure(self, mock_default_cli):
        """Test check_tool_secure function."""
        mock_default_cli.check_command_available.return_value = True

        result = check_tool_secure("python")

        assert result is True
        mock_default_cli.check_command_available.assert_called_once_with("python")

    @patch("shared.secure_cli_manager.default_secure_cli")
    def test_get_tool_version_secure(self, mock_default_cli):
        """Test get_tool_version_secure function."""
        mock_default_cli.get_command_version.return_value = "Python 3.8.10"

        version = get_tool_version_secure("python")

        assert version == "Python 3.8.10"
        mock_default_cli.get_command_version.assert_called_once_with(
            "python", "--version"
        )


class TestSecureCLIManagerEdgeCases:
    """Test edge cases for SecureCLIManager."""

    def test_run_with_shell_true(self):
        """Test running command with shell=True."""
        with patch("shared.secure_cli_manager.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

            manager = SecureCLIManager(verbose=False)
            result = manager.run("echo 'test'", shell=True)

            mock_subprocess.assert_called_once()
            call_args = mock_subprocess.call_args
            assert call_args[1]["shell"] is True

    def test_run_with_input_data(self):
        """Test running command with input data."""
        with patch("shared.secure_cli_manager.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

            manager = SecureCLIManager(verbose=False)
            result = manager.run(["python"], input_data="print('hello')")

            mock_subprocess.assert_called_once()
            call_args = mock_subprocess.call_args
            assert call_args[1]["input"] == "print('hello')"

    def test_run_with_environment(self):
        """Test running command with custom environment."""
        with patch("shared.secure_cli_manager.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

            manager = SecureCLIManager(verbose=False)
            custom_env = {"TEST_VAR": "test_value"}
            result = manager.run(["python", "--version"], env=custom_env)

            mock_subprocess.assert_called_once()
            call_args = mock_subprocess.call_args
            assert call_args[1]["env"] == custom_env

    def test_run_with_check_true(self):
        """Test running command with check=True raises exception on failure."""
        with patch("shared.secure_cli_manager.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=1, stdout="", stderr="Error")

            manager = SecureCLIManager(verbose=False, check=True)

            with pytest.raises(subprocess.CalledProcessError):
                manager.run(["invalid", "command"])

    def test_run_with_validate_security_false(self):
        """Test running command with security validation disabled."""
        with patch("shared.secure_cli_manager.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

            manager = SecureCLIManager(verbose=False)
            result = manager.run(["rm", "-rf", "/"], validate_security=False)

            assert result.success is True
            assert result.security_validated is False

    def test_run_with_custom_timeout(self):
        """Test running command with custom timeout."""
        with patch("shared.secure_cli_manager.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

            manager = SecureCLIManager(verbose=False)
            result = manager.run(["python", "--version"], timeout=60)

            mock_subprocess.assert_called_once()
            call_args = mock_subprocess.call_args
            assert call_args[1]["timeout"] == 60

    def test_run_with_custom_cwd(self):
        """Test running command with custom working directory."""
        with patch("shared.secure_cli_manager.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

            manager = SecureCLIManager(verbose=False)
            custom_cwd = Path("/custom/path")
            result = manager.run(["python", "--version"], cwd=custom_cwd)

            mock_subprocess.assert_called_once()
            call_args = mock_subprocess.call_args
            assert call_args[1]["cwd"] == custom_cwd

    def test_logging_of_security_events(self):
        """Test that security events are logged."""
        with patch("shared.secure_cli_manager.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

            manager = SecureCLIManager(verbose=False)
            with patch.object(manager.logger, "info") as mock_logger:
                manager.run(["python", "--version"], "Test command")

                mock_logger.assert_called()
                log_call = mock_logger.call_args[0][0]
                assert "Command executed" in log_call
                assert "python --version" in log_call
                assert "Success: True" in log_call
                assert "Validated: True" in log_call

    def test_logging_of_security_failures(self):
        """Test that security failures are logged."""
        manager = SecureCLIManager(verbose=False)
        with patch.object(manager.logger, "warning") as mock_logger:
            manager.run(["rm", "-rf", "/"], "Dangerous command")

            mock_logger.assert_called()
            log_call = mock_logger.call_args[0][0]
            assert "Command validation failed" in log_call

    def test_execution_time_measurement(self):
        """Test that execution time is measured correctly."""
        with patch("shared.secure_cli_manager.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

            manager = SecureCLIManager(verbose=False)
            result = manager.run(["python", "--version"])

            assert result.execution_time > 0
            assert isinstance(result.execution_time, float)
