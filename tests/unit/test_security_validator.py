"""
Unit tests for security validator module.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from shared.security_validator import (
    SecurityValidator,
    safe_command_execution,
    validate_user_input,
)


class TestSecurityValidator:
    """Test cases for SecurityValidator class."""

    def test_init(self):
        """Test SecurityValidator initialization."""
        validator = SecurityValidator()

        assert validator.system in ["Windows", "Linux", "Darwin"]
        assert validator.max_path_length in [260, 4096]  # Windows vs Unix
        assert hasattr(validator, 'DANGEROUS_PATTERNS')
        assert hasattr(validator, 'ALLOWED_EXTENSIONS')
        assert hasattr(validator, 'ALLOWED_COMMANDS')

    @pytest.mark.parametrize("name", [
        "valid-project",
        "valid_project",
        "ValidProject",
        "project123",
        "a" * 50,  # Max length
    ])
    def test_validate_project_name_valid(self, name):
        """Test valid project name validation."""
        validator = SecurityValidator()
        is_valid, error = validator.validate_project_name(name)

        assert is_valid, f"Valid name '{name}' was rejected: {error}"
        assert error == ""

    @pytest.mark.parametrize("name,expected_error", [
        ("", "Project name cannot be empty"),
        ("a" * 51, "Project name too long"),
        ("invalid;project", "Project name contains dangerous characters"),
        ("invalid..project", "Project name contains dangerous characters"),
        ("invalid<project", "Project name contains dangerous characters"),
        ("con", "Project name 'con' is reserved by the system"),
        ("prn", "Project name 'prn' is reserved by the system"),
        ("invalid project", "Project name can only contain letters"),
        ("invalid/project", "Project name can only contain letters"),
        ("invalid\\project", "Project name can only contain letters"),
    ])
    def test_validate_project_name_invalid(self, name, expected_error):
        """Test invalid project name validation."""
        validator = SecurityValidator()
        is_valid, error = validator.validate_project_name(name)

        assert not is_valid, f"Invalid name '{name}' was accepted"
        assert expected_error in error

    @pytest.mark.parametrize("path", [
        "/home/user/project",
        "C:\\Users\\user\\project",
        "./relative/path",
        "project",
        "src/main.py",
    ])
    def test_validate_path_valid(self, path):
        """Test valid path validation."""
        validator = SecurityValidator()
        is_valid, error = validator.validate_path(path)

        assert is_valid, f"Valid path '{path}' was rejected: {error}"
        assert error == ""

    @pytest.mark.parametrize("path", [
        "path/../dangerous",
        "path\\..\\dangerous",
        "path;dangerous",
        "path|dangerous",
        "path`dangerous",
        "path$(dangerous)",
        "path<dangerous",
        "path>dangerous",
    ])
    def test_validate_path_invalid(self, path):
        """Test invalid path validation."""
        validator = SecurityValidator()
        is_valid, error = validator.validate_path(path)

        assert not is_valid, f"Invalid path '{path}' was accepted"
        assert "dangerous characters" in error

    def test_validate_path_too_long(self):
        """Test path length validation."""
        validator = SecurityValidator()
        long_path = "a" * (validator.max_path_length + 1)

        is_valid, error = validator.validate_path(long_path)

        assert not is_valid
        assert "too long" in error

    def test_validate_path_must_exist(self, temp_dir):
        """Test path existence validation."""
        validator = SecurityValidator()
        non_existent_path = temp_dir / "non_existent_file"

        is_valid, error = validator.validate_path(non_existent_path, must_exist=True)

        assert not is_valid
        assert "does not exist" in error

    @pytest.mark.parametrize("command", [
        ["python", "--version"],
        ["git", "status"],
        ["npm", "install"],
        ["black", "src/"],
        ["flake8", "project"],
    ])
    def test_validate_command_valid(self, command):
        """Test valid command validation."""
        validator = SecurityValidator()
        is_valid, error = validator.validate_command(command)

        assert is_valid, f"Valid command {command} was rejected: {error}"
        assert error == ""

    @pytest.mark.parametrize("command", [
        ["rm", "-rf", "/"],
        ["sudo", "rm", "-rf", "/"],
        ["python", ";", "rm", "-rf", "/"],
        ["python", "&&", "rm", "-rf", "/"],
        ["python", "|", "rm", "-rf", "/"],
        ["python", "`rm -rf /`"],
        ["python", "$(rm -rf /)"],
    ])
    def test_validate_command_invalid(self, command):
        """Test invalid command validation."""
        validator = SecurityValidator()
        is_valid, error = validator.validate_command(command)

        assert not is_valid, f"Invalid command {command} was accepted"
        assert "not allowed" in error or "Invalid argument" in error

    def test_validate_command_empty(self):
        """Test empty command validation."""
        validator = SecurityValidator()
        is_valid, error = validator.validate_command([])

        assert not is_valid
        assert "Empty command" in error

    def test_validate_argument(self):
        """Test argument validation."""
        validator = SecurityValidator()

        # Valid arguments
        assert validator._validate_argument("normal_arg")
        assert validator._validate_argument("arg_with_123")
        assert validator._validate_argument("arg-with-dashes")

        # Invalid arguments
        assert not validator._validate_argument("arg;with;semicolon")
        assert not validator._validate_argument("arg|with|pipe")
        assert not validator._validate_argument("arg`with`backtick")
        assert not validator._validate_argument("arg$(with)subshell")
        assert not validator._validate_argument("a" * 1001)  # Too long

    def test_validate_file_operation(self, temp_dir):
        """Test file operation validation."""
        validator = SecurityValidator()

        # Create test files
        source_file = temp_dir / "source.txt"
        dest_file = temp_dir / "dest.txt"
        source_file.write_text("test content")

        # Valid operation
        is_valid, error = validator.validate_file_operation(
            source_file, dest_file, "copy"
        )
        assert is_valid, f"Valid file operation was rejected: {error}"

        # Invalid source
        non_existent = temp_dir / "non_existent.txt"
        is_valid, error = validator.validate_file_operation(
            non_existent, dest_file, "copy"
        )
        assert not is_valid
        assert "does not exist" in error

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        validator = SecurityValidator()

        # Test dangerous characters
        sanitized = validator.sanitize_filename("file<>:\"/\\|?*.txt")
        assert sanitized == "file_______.txt"

        # Test spaces
        sanitized = validator.sanitize_filename("  file with spaces  ")
        assert sanitized == "file with spaces"

        # Test length limit
        long_name = "a" * 300
        sanitized = validator.sanitize_filename(long_name)
        assert len(sanitized) <= 255

    def test_validate_script_execution(self, temp_dir):
        """Test script execution validation."""
        validator = SecurityValidator()

        # Create a valid script
        valid_script = temp_dir / "test_script.py"
        valid_script.write_text("print('Hello')")

        # Valid script
        is_valid, error = validator.validate_script_execution(valid_script)
        assert is_valid, f"Valid script was rejected: {error}"

        # Non-existent script
        non_existent = temp_dir / "non_existent.py"
        is_valid, error = validator.validate_script_execution(non_existent)
        assert not is_valid
        assert "does not exist" in error

        # Invalid extension
        invalid_ext = temp_dir / "script.exe"
        invalid_ext.write_text("binary content")
        is_valid, error = validator.validate_script_execution(invalid_ext)
        assert not is_valid
        assert "extension not allowed" in error

    @pytest.mark.parametrize("key_path,operation,expected", [
        ("Software\\WorksOnMyMachine\\Test", "write", True),
        ("Software\\Classes\\Directory\\shell\\Test", "write", True),
        ("Software\\Classes\\Directory\\Background\\shell\\Test", "write", True),
        ("Software\\Malicious\\Key", "write", False),
        ("System\\CurrentControlSet\\Services", "write", False),
    ])
    def test_validate_registry_operation(self, key_path, operation, expected):
        """Test registry operation validation."""
        validator = SecurityValidator()

        with patch('platform.system', return_value="Windows"):
            is_valid, error = validator.validate_registry_operation(key_path, operation)
            assert is_valid == expected, f"Registry validation failed for {key_path}: {error}"

        # Test non-Windows system
        with patch('platform.system', return_value="Linux"):
            is_valid, error = validator.validate_registry_operation(key_path, operation)
            assert not is_valid
            assert "only supported on Windows" in error


class TestValidateUserInput:
    """Test cases for validate_user_input function."""

    def test_validate_project_name(self):
        """Test project name validation through function."""
        # Valid name
        is_valid, error = validate_user_input("valid-project", "project_name")
        assert is_valid
        assert error == ""

        # Invalid name
        is_valid, error = validate_user_input("invalid;project", "project_name")
        assert not is_valid
        assert "dangerous characters" in error

    def test_validate_path(self):
        """Test path validation through function."""
        # Valid path
        is_valid, error = validate_user_input("/home/user/project", "path")
        assert is_valid
        assert error == ""

        # Invalid path
        is_valid, error = validate_user_input("path/../dangerous", "path")
        assert not is_valid
        assert "dangerous characters" in error

    def test_validate_command(self):
        """Test command validation through function."""
        # Valid command
        is_valid, error = validate_user_input("python --version", "command")
        assert is_valid
        assert error == ""

        # Invalid command
        is_valid, error = validate_user_input("rm -rf /", "command")
        assert not is_valid
        assert "not allowed" in error

    def test_unknown_input_type(self):
        """Test unknown input type handling."""
        is_valid, error = validate_user_input("test", "unknown_type")
        assert not is_valid
        assert "Unknown input type" in error


class TestSafeCommandExecution:
    """Test cases for safe_command_execution function."""

    def test_safe_command_execution_valid(self, mock_secure_cli_manager):
        """Test safe command execution with valid command."""
        success, error = safe_command_execution(["python", "--version"], "Test command")

        assert success
        assert error == ""
        mock_secure_cli_manager.assert_called_once()

    def test_safe_command_execution_invalid(self):
        """Test safe command execution with invalid command."""
        success, error = safe_command_execution(["invalid_command"], "Test command")

        assert not success
        assert "Command validation failed" in error

    def test_safe_command_execution_exception(self, mock_secure_cli_manager):
        """Test safe command execution with exception."""
        mock_secure_cli_manager.side_effect = Exception("Test exception")

        success, error = safe_command_execution(["python", "--version"], "Test command")

        assert not success
        assert "Command execution failed" in error


class TestSecurityValidatorEdgeCases:
    """Test edge cases for SecurityValidator."""

    def test_dangerous_patterns_comprehensive(self):
        """Test all dangerous patterns are detected."""
        validator = SecurityValidator()

        dangerous_inputs = [
            "test;command",
            "test|command",
            "test`command",
            "test$(command)",
            "test{command}",
            "test[command]",
            "test..command",
            "test\\..command",
            "test<command",
            "test>command",
            "test\\x00command",
            "test%00command",
        ]

        for dangerous_input in dangerous_inputs:
            is_valid, error = validator.validate_project_name(dangerous_input)
            assert not is_valid, f"Dangerous input '{dangerous_input}' was accepted"
            assert "dangerous characters" in error

    def test_allowed_extensions_comprehensive(self):
        """Test all allowed extensions are accepted."""
        validator = SecurityValidator()

        allowed_extensions = [
            ".py", ".pyw", ".js", ".jsx", ".ts", ".tsx",
            ".json", ".yaml", ".yml", ".md", ".txt",
            ".toml", ".ini", ".cfg", ".conf",
            ".bat", ".cmd", ".ps1", ".sh", ".bash", ".zsh", ".fish"
        ]

        for ext in allowed_extensions:
            test_file = Path(f"test{ext}")
            is_valid, error = validator.validate_script_execution(test_file)
            # Note: This will fail because file doesn't exist, but extension should be allowed
            # We're just checking that the extension is in the allowed list
            assert ext in validator.ALLOWED_EXTENSIONS

    def test_allowed_commands_comprehensive(self):
        """Test all allowed commands are accepted."""
        validator = SecurityValidator()

        allowed_commands = [
            "python", "python3", "py", "node", "npm", "npx",
            "git", "pip", "pip3", "black", "isort", "flake8",
            "pytest", "pre-commit", "cspell", "eslint",
            "prettier", "jest", "husky", "lint-staged"
        ]

        for cmd in allowed_commands:
            is_valid, error = validator.validate_command([cmd])
            assert is_valid, f"Allowed command '{cmd}' was rejected: {error}"

    def test_cross_platform_path_validation(self):
        """Test path validation works across platforms."""
        validator = SecurityValidator()

        # Test Windows paths on Windows
        with patch('platform.system', return_value="Windows"):
            validator.max_path_length = 260
            is_valid, error = validator.validate_path("C:\\Users\\user\\project")
            assert is_valid, f"Windows path was rejected: {error}"

        # Test Unix paths on Linux
        with patch('platform.system', return_value="Linux"):
            validator.max_path_length = 4096
            is_valid, error = validator.validate_path("/home/user/project")
            assert is_valid, f"Unix path was rejected: {error}"

    def test_reserved_names_comprehensive(self):
        """Test all reserved Windows names are blocked."""
        validator = SecurityValidator()

        reserved_names = [
            'con', 'prn', 'aux', 'nul',
            'com1', 'com2', 'com3', 'com4', 'com5',
            'com6', 'com7', 'com8', 'com9',
            'lpt1', 'lpt2', 'lpt3', 'lpt4',
            'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'
        ]

        for name in reserved_names:
            is_valid, error = validator.validate_project_name(name)
            assert not is_valid, f"Reserved name '{name}' was accepted"
            assert "reserved by the system" in error
