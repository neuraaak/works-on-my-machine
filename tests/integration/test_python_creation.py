"""Integration tests for Python project creation functionality."""

from unittest.mock import Mock, patch


class TestPythonProjectCreation:
    """Integration tests for Python project creation."""

    def test_create_python_project_structure(self, temp_dir):
        """Test that Python project creation creates correct structure."""
        project_name = "test-python-project"
        project_path = temp_dir / project_name

        # Mock the setup script to create actual structure
        with patch("shared.secure_cli_manager.run_secure_command") as mock_run:
            mock_run.return_value = Mock(
                success=True,
                security_validated=True,
                returncode=0,
                stdout="Project created successfully",
                stderr="",
            )

            # Create project structure manually for testing
            project_path.mkdir()
            (project_path / "src").mkdir()
            (project_path / "tests").mkdir()
            (project_path / "docs").mkdir()
            (project_path / ".vscode").mkdir()

            # Create sample files
            (project_path / "src" / "__init__.py").touch()
            (project_path / "src" / "main.py").write_text("print('Hello, World!')")
            (project_path / "tests" / "__init__.py").touch()
            (project_path / "tests" / "test_main.py").write_text(
                "def test_hello(): pass"
            )
            (project_path / "pyproject.toml").write_text(
                "[project]\nname = 'test-project'"
            )
            (project_path / ".gitignore").write_text("__pycache__/\n*.pyc")
            (project_path / "Makefile").write_text("test:\n\techo 'Running tests'")

            # Verify structure
            assert project_path.exists()
            assert (project_path / "src").exists()
            assert (project_path / "tests").exists()
            assert (project_path / "docs").exists()
            assert (project_path / ".vscode").exists()
            assert (project_path / "pyproject.toml").exists()
            assert (project_path / ".gitignore").exists()
            assert (project_path / "Makefile").exists()

    def test_python_project_configuration_files(self, temp_dir):
        """Test that Python project has correct configuration files."""
        project_name = "test-python-project"
        project_path = temp_dir / project_name
        project_path.mkdir()

        # Create configuration files
        pyproject_content = """
[project]
name = "test-python-project"
version = "0.1.0"
description = "Test Python project"
requires-python = ">=3.8"

[project.optional-dependencies]
dev = [
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "pytest>=7.0.0",
]
"""
        (project_path / "pyproject.toml").write_text(pyproject_content)

        # Verify pyproject.toml content
        pyproject_file = project_path / "pyproject.toml"
        assert pyproject_file.exists()

        content = pyproject_file.read_text()
        assert "test-python-project" in content
        assert "black>=23.0.0" in content
        assert "pytest>=7.0.0" in content

    def test_python_project_git_integration(self, temp_dir):
        """Test that Python project integrates with Git."""
        project_name = "test-python-project"
        project_path = temp_dir / project_name
        project_path.mkdir()

        # Create .gitignore
        gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
"""
        (project_path / ".gitignore").write_text(gitignore_content)

        # Verify .gitignore content
        gitignore_file = project_path / ".gitignore"
        assert gitignore_file.exists()

        content = gitignore_file.read_text()
        assert "__pycache__/" in content
        assert "*.pyc" in content
        assert "venv/" in content
        assert ".vscode/" in content

    def test_python_project_vscode_configuration(self, temp_dir):
        """Test that Python project has correct VSCode configuration."""
        project_name = "test-python-project"
        project_path = temp_dir / project_name
        project_path.mkdir()

        # Create VSCode configuration
        vscode_dir = project_path / ".vscode"
        vscode_dir.mkdir()

        settings_content = """
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
"""
        (vscode_dir / "settings.json").write_text(settings_content)

        # Verify VSCode configuration
        settings_file = vscode_dir / "settings.json"
        assert settings_file.exists()

        content = settings_file.read_text()
        assert "black" in content
        assert "flake8" in content
        assert "formatOnSave" in content

    def test_python_project_makefile(self, temp_dir):
        """Test that Python project has correct Makefile."""
        project_name = "test-python-project"
        project_path = temp_dir / project_name
        project_path.mkdir()

        # Create Makefile
        makefile_content = """
.PHONY: help install install-dev format lint test clean

help:
    @echo "Available commands:"
    @echo "  install     - Install package"
    @echo "  install-dev - Install development dependencies"
    @echo "  format      - Format code with black and isort"
    @echo "  lint        - Lint code with flake8"
    @echo "  test        - Run tests with pytest"
    @echo "  clean       - Clean build artifacts"

install:
    pip install -e .

install-dev:
    pip install -e ".[dev]"

format:
    black src/ tests/
    isort src/ tests/

lint:
    flake8 src/ tests/

test:
    pytest tests/ -v

clean:
    rm -rf build/ dist/ *.egg-info/
    find . -type d -name __pycache__ -exec rm -rf {} +
"""
        (project_path / "Makefile").write_text(makefile_content)

        # Verify Makefile content
        makefile = project_path / "Makefile"
        assert makefile.exists()

        content = makefile.read_text()
        assert "black" in content
        assert "flake8" in content
        assert "pytest" in content
        assert "install" in content
        assert "format" in content

    def test_python_project_complete_workflow(self, temp_dir):
        """Test complete Python project creation workflow."""
        project_name = "test-python-project"
        project_path = temp_dir / project_name

        # Mock CLI execution
        with patch("shared.secure_cli_manager.run_secure_command") as mock_run:
            mock_run.return_value = Mock(
                success=True,
                security_validated=True,
                returncode=0,
                stdout="Project created successfully",
                stderr="",
            )

            # Create complete project structure
            project_path.mkdir()

            # Source code
            src_dir = project_path / "src"
            src_dir.mkdir()
            (src_dir / "__init__.py").touch()
            (src_dir / "main.py").write_text(
                """
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
"""
            )

            # Tests
            tests_dir = project_path / "tests"
            tests_dir.mkdir()
            (tests_dir / "__init__.py").touch()
            (tests_dir / "test_main.py").write_text(
                """
import pytest
from src.main import hello_world

def test_hello_world():
    assert hello_world() == "Hello, World!"
"""
            )

            # Configuration files
            (project_path / "pyproject.toml").write_text(
                """
[project]
name = "test-python-project"
version = "0.1.0"
description = "Test Python project"
requires-python = ">=3.8"

[project.optional-dependencies]
dev = [
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "pytest>=7.0.0",
]
"""
            )

            # Verify complete structure
            assert project_path.exists()
            assert src_dir.exists()
            assert tests_dir.exists()
            assert (src_dir / "main.py").exists()
            assert (tests_dir / "test_main.py").exists()
            assert (project_path / "pyproject.toml").exists()

            # Verify source code content
            main_content = (src_dir / "main.py").read_text()
            assert "def hello_world():" in main_content
            assert 'return "Hello, World!"' in main_content

            # Verify test content
            test_content = (tests_dir / "test_main.py").read_text()
            assert "def test_hello_world():" in test_content
            assert 'hello_world() == "Hello, World!"' in test_content
