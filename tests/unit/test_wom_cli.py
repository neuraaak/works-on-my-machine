"""
Unit tests for WOM CLI module.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

# Import the CLI modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestWOMCLI:
    """Test cases for WOM CLI commands."""

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

    def test_wom_help(self, cli_runner):
        """Test WOM CLI help command."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['--help'])
        
        assert result.exit_code == 0
        assert "Universal development tools" in result.output
        assert "new" in result.output
        assert "lint" in result.output
        assert "spell" in result.output

    def test_wom_version(self, cli_runner):
        """Test WOM CLI version command."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['--version'])
        
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_new_python_project_valid(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test creating a new Python project with valid name."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['new', 'python', 'test-project'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()
        
        # Check that the command was called with correct arguments
        call_args = mock_secure_cli_manager.call_args
        assert 'python' in call_args[0][0]
        assert 'test-project' in call_args[0][0]

    def test_new_python_project_invalid_name(self, cli_runner, mock_security_validator):
        """Test creating a new Python project with invalid name."""
        from wom_secure import wom
        
        # Mock validation to fail
        mock_security_validator['validate_user_input'].return_value = (False, "Invalid project name")
        
        result = cli_runner.invoke(wom, ['new', 'python', 'invalid;project'])
        
        assert result.exit_code == 1
        assert "Invalid project name" in result.output

    def test_new_python_project_current_dir(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test creating a Python project in current directory."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['new', 'python', '--current-dir'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()
        
        # Check that --current-dir was passed
        call_args = mock_secure_cli_manager.call_args
        assert '--current-dir' in call_args[0][0]

    def test_new_javascript_project_valid(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test creating a new JavaScript project with valid name."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['new', 'javascript', 'test-js-project'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()
        
        # Check that the command was called with correct arguments
        call_args = mock_secure_cli_manager.call_args
        assert 'javascript' in call_args[0][0]
        assert 'test-js-project' in call_args[0][0]

    def test_new_javascript_project_with_type(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test creating a new JavaScript project with specific type."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['new', 'javascript', 'test-react', '--type', 'react'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()
        
        # Check that --type react was passed
        call_args = mock_secure_cli_manager.call_args
        assert '--type' in call_args[0][0]
        assert 'react' in call_args[0][0]

    def test_new_detect_project(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test auto-detecting project type."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['new', 'detect', 'test-project'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_lint_python_valid(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test linting Python code with valid path."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['lint', 'python', '.'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_lint_python_with_fix(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test linting Python code with fix option."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['lint', 'python', '.', '--fix'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()
        
        # Check that --fix was passed
        call_args = mock_secure_cli_manager.call_args
        assert '--fix' in call_args[0][0]

    def test_lint_all_valid(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test linting all code types."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['lint', 'all', '.'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_spell_install(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test installing CSpell."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['spell', 'install'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_spell_setup_valid(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test setting up CSpell for project."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['spell', 'setup', 'test-project'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_spell_setup_invalid_name(self, cli_runner, mock_security_validator):
        """Test setting up CSpell with invalid project name."""
        from wom_secure import wom
        
        # Mock validation to fail
        mock_security_validator['validate_user_input'].return_value = (False, "Invalid project name")
        
        result = cli_runner.invoke(wom, ['spell', 'setup', 'invalid;project'])
        
        assert result.exit_code == 1
        assert "Invalid project name" in result.output

    def test_spell_check_valid(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test spell checking with valid path."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['spell', 'check', '.'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_spell_check_with_fix(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test spell checking with fix option."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['spell', 'check', '.', '--fix'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_system_detect(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test system detection."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['system', 'detect'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_system_detect_with_export(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test system detection with export option."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['system', 'detect', '--export', 'report.json'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_system_install_check(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test system prerequisites check."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['system', 'install', '--check'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_system_install_tools(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test installing specific tools."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['system', 'install', 'python', 'node'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_deploy_tools(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test deploying tools."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['deploy', 'tools'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_deploy_tools_with_target(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test deploying tools with custom target."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['deploy', 'tools', '--target', '/custom/path'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    def test_deploy_tools_global(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test deploying tools with global option."""
        from wom_secure import wom
        
        result = cli_runner.invoke(wom, ['deploy', 'tools', '--global'])
        
        assert result.exit_code == 0
        mock_secure_cli_manager.assert_called_once()

    @pytest.mark.windows
    def test_context_register_windows(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test registering context menu on Windows."""
        from wom_secure import wom
        
        with patch('platform.system', return_value="Windows"):
            result = cli_runner.invoke(wom, ['context', 'register'])
            
            assert result.exit_code == 0
            mock_secure_cli_manager.assert_called_once()

    @pytest.mark.windows
    def test_context_register_with_backup(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test registering context menu with backup."""
        from wom_secure import wom
        
        with patch('platform.system', return_value="Windows"):
            result = cli_runner.invoke(wom, ['context', 'register', '--backup'])
            
            assert result.exit_code == 0
            mock_secure_cli_manager.assert_called_once()

    @pytest.mark.windows
    def test_context_unregister_windows(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test unregistering context menu on Windows."""
        from wom_secure import wom
        
        with patch('platform.system', return_value="Windows"):
            result = cli_runner.invoke(wom, ['context', 'unregister'])
            
            assert result.exit_code == 0
            mock_secure_cli_manager.assert_called_once()

    @pytest.mark.windows
    def test_context_list_windows(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test listing context menu entries on Windows."""
        from wom_secure import wom
        
        with patch('platform.system', return_value="Windows"):
            result = cli_runner.invoke(wom, ['context', 'list'])
            
            assert result.exit_code == 0
            mock_secure_cli_manager.assert_called_once()

    def test_context_commands_non_windows(self, cli_runner):
        """Test context commands on non-Windows systems."""
        from wom_secure import wom
        
        with patch('platform.system', return_value="Linux"):
            # Test register
            result = cli_runner.invoke(wom, ['context', 'register'])
            assert result.exit_code == 1
            assert "only supported on Windows" in result.output
            
            # Test unregister
            result = cli_runner.invoke(wom, ['context', 'unregister'])
            assert result.exit_code == 1
            assert "only supported on Windows" in result.output
            
            # Test list
            result = cli_runner.invoke(wom, ['context', 'list'])
            assert result.exit_code == 1
            assert "only supported on Windows" in result.output


class TestWOMCLIErrorHandling:
    """Test error handling in WOM CLI."""

    @pytest.fixture
    def cli_runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    def test_script_validation_failure(self, cli_runner, mock_security_validator):
        """Test handling of script validation failure."""
        from wom_secure import wom
        
        # Mock script validation to fail
        mock_security_validator['security_validator'].validate_script_execution.return_value = (
            False, "Script validation failed"
        )
        
        result = cli_runner.invoke(wom, ['new', 'python', 'test-project'])
        
        assert result.exit_code == 1
        assert "Script validation failed" in result.output

    def test_command_execution_failure(self, cli_runner, mock_security_validator):
        """Test handling of command execution failure."""
        from wom_secure import wom
        
        with patch('shared.secure_cli_manager.run_secure_command') as mock_run:
            mock_run.return_value = Mock(
                success=False,
                security_validated=True,
                returncode=1,
                stdout="",
                stderr="Command failed"
            )
            
            result = cli_runner.invoke(wom, ['new', 'python', 'test-project'])
            
            assert result.exit_code == 1

    def test_security_validation_failure(self, cli_runner, mock_security_validator):
        """Test handling of security validation failure."""
        from wom_secure import wom
        
        with patch('shared.secure_cli_manager.run_secure_command') as mock_run:
            mock_run.return_value = Mock(
                success=True,
                security_validated=False,
                returncode=0,
                stdout="",
                stderr="Security validation failed"
            )
            
            result = cli_runner.invoke(wom, ['new', 'python', 'test-project'])
            
            assert result.exit_code == 1

    def test_path_validation_failure(self, cli_runner, mock_security_validator):
        """Test handling of path validation failure."""
        from wom_secure import wom
        
        # Mock path validation to fail
        mock_security_validator['validate_user_input'].return_value = (False, "Invalid path")
        
        result = cli_runner.invoke(wom, ['lint', 'python', 'invalid/path'])
        
        assert result.exit_code == 1
        assert "Invalid path" in result.output


class TestWOMCLIArgumentValidation:
    """Test argument validation in WOM CLI."""

    @pytest.fixture
    def cli_runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    def test_javascript_project_type_validation(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test JavaScript project type validation."""
        from wom_secure import wom
        
        # Test valid types
        valid_types = ['node', 'react', 'vue', 'express']
        for project_type in valid_types:
            result = cli_runner.invoke(wom, ['new', 'javascript', 'test-project', '--type', project_type])
            assert result.exit_code == 0
        
        # Test invalid type
        result = cli_runner.invoke(wom, ['new', 'javascript', 'test-project', '--type', 'invalid'])
        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_spell_project_type_validation(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test spell project type validation."""
        from wom_secure import wom
        
        # Test valid types
        valid_types = ['python', 'javascript']
        for project_type in valid_types:
            result = cli_runner.invoke(wom, ['spell', 'setup', 'test-project', '--type', project_type])
            assert result.exit_code == 0
        
        # Test invalid type
        result = cli_runner.invoke(wom, ['spell', 'setup', 'test-project', '--type', 'invalid'])
        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_system_install_tools_validation(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test system install tools validation."""
        from wom_secure import wom
        
        # Test valid tools
        valid_tools = ['python', 'node', 'git', 'all']
        for tool in valid_tools:
            result = cli_runner.invoke(wom, ['system', 'install', tool])
            assert result.exit_code == 0
        
        # Test invalid tool
        result = cli_runner.invoke(wom, ['system', 'install', 'invalid'])
        assert result.exit_code != 0
        assert "Invalid value" in result.output


class TestWOMCLIIntegration:
    """Integration tests for WOM CLI."""

    @pytest.fixture
    def cli_runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    def test_complete_workflow_python(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test complete workflow for Python project."""
        from wom_secure import wom
        
        # Create project
        result = cli_runner.invoke(wom, ['new', 'python', 'test-project'])
        assert result.exit_code == 0
        
        # Lint project
        result = cli_runner.invoke(wom, ['lint', 'python', '.'])
        assert result.exit_code == 0
        
        # Setup spell checking
        result = cli_runner.invoke(wom, ['spell', 'setup', 'test-project'])
        assert result.exit_code == 0
        
        # Check spelling
        result = cli_runner.invoke(wom, ['spell', 'check', '.'])
        assert result.exit_code == 0

    def test_complete_workflow_javascript(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test complete workflow for JavaScript project."""
        from wom_secure import wom
        
        # Create project
        result = cli_runner.invoke(wom, ['new', 'javascript', 'test-js-project', '--type', 'react'])
        assert result.exit_code == 0
        
        # Lint all code
        result = cli_runner.invoke(wom, ['lint', 'all', '.'])
        assert result.exit_code == 0
        
        # Setup spell checking
        result = cli_runner.invoke(wom, ['spell', 'setup', 'test-js-project', '--type', 'javascript'])
        assert result.exit_code == 0

    def test_system_workflow(self, cli_runner, mock_secure_cli_manager, mock_security_validator):
        """Test complete system workflow."""
        from wom_secure import wom
        
        # Detect system
        result = cli_runner.invoke(wom, ['system', 'detect'])
        assert result.exit_code == 0
        
        # Check prerequisites
        result = cli_runner.invoke(wom, ['system', 'install', '--check'])
        assert result.exit_code == 0
        
        # Install tools
        result = cli_runner.invoke(wom, ['system', 'install', 'python', 'node'])
        assert result.exit_code == 0
        
        # Deploy tools
        result = cli_runner.invoke(wom, ['deploy', 'tools', '--global'])
        assert result.exit_code == 0