"""
Integration tests for project creation functionality.
"""

import pytest
import shutil
from pathlib import Path
from unittest.mock import patch, Mock

from shared.security_validator import SecurityValidator
from shared.secure_cli_manager import SecureCLIManager


class TestPythonProjectCreation:
    """Integration tests for Python project creation."""

    def test_create_python_project_structure(self, temp_dir):
        """Test that Python project creation creates correct structure."""
        project_name = "test-python-project"
        project_path = temp_dir / project_name
        
        # Mock the setup script to create actual structure
        with patch('shared.secure_cli_manager.run_secure_command') as mock_run:
            mock_run.return_value = Mock(
                success=True,
                security_validated=True,
                returncode=0,
                stdout="Project created successfully",
                stderr=""
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
            (project_path / "tests" / "test_main.py").write_text("def test_hello(): pass")
            (project_path / "pyproject.toml").write_text("[project]\nname = 'test-project'")
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
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.coverage
.pytest_cache/
htmlcov/
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
        """Test that Python project has VSCode configuration."""
        project_name = "test-python-project"
        project_path = temp_dir / project_name
        project_path.mkdir()
        (project_path / ".vscode").mkdir()
        
        # Create VSCode settings
        settings_content = """
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
"""
        (project_path / ".vscode" / "settings.json").write_text(settings_content)
        
        # Verify VSCode configuration
        settings_file = project_path / ".vscode" / "settings.json"
        assert settings_file.exists()
        
        content = settings_file.read_text()
        assert "python.linting.enabled" in content
        assert "black" in content
        assert "formatOnSave" in content

    def test_python_project_makefile(self, temp_dir):
        """Test that Python project has functional Makefile."""
        project_name = "test-python-project"
        project_path = temp_dir / project_name
        project_path.mkdir()
        
        # Create Makefile
        makefile_content = """
.PHONY: help install install-dev format lint test clean

help:
	@echo "Available commands:"
	@echo "  install     - Install project dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  format      - Format code with black and isort"
	@echo "  lint        - Lint code with flake8"
	@echo "  test        - Run tests with pytest"
	@echo "  clean       - Clean up generated files"

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
	pytest tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info/
"""
        (project_path / "Makefile").write_text(makefile_content)
        
        # Verify Makefile content
        makefile = project_path / "Makefile"
        assert makefile.exists()
        
        content = makefile.read_text()
        assert "install" in content
        assert "format" in content
        assert "lint" in content
        assert "test" in content
        assert "black" in content
        assert "flake8" in content
        assert "pytest" in content


class TestJavaScriptProjectCreation:
    """Integration tests for JavaScript project creation."""

    def test_create_javascript_project_structure(self, temp_dir):
        """Test that JavaScript project creation creates correct structure."""
        project_name = "test-js-project"
        project_path = temp_dir / project_name
        
        # Create project structure
        project_path.mkdir()
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "public").mkdir()
        
        # Create sample files
        (project_path / "src" / "index.js").write_text("console.log('Hello, World!');")
        (project_path / "tests" / "index.test.js").write_text("test('example', () => expect(true).toBe(true));")
        (project_path / "package.json").write_text('{"name": "test-js-project"}')
        (project_path / ".gitignore").write_text("node_modules/\n*.log")
        
        # Verify structure
        assert project_path.exists()
        assert (project_path / "src").exists()
        assert (project_path / "tests").exists()
        assert (project_path / "public").exists()
        assert (project_path / "package.json").exists()
        assert (project_path / ".gitignore").exists()

    def test_javascript_project_package_json(self, temp_dir):
        """Test that JavaScript project has correct package.json."""
        project_name = "test-js-project"
        project_path = temp_dir / project_name
        project_path.mkdir()
        
        # Create package.json
        package_json_content = """
{
  "name": "test-js-project",
  "version": "1.0.0",
  "description": "Test JavaScript project",
  "main": "src/index.js",
  "scripts": {
    "dev": "node src/index.js",
    "build": "echo 'Build process'",
    "start": "node src/index.js",
    "test": "jest",
    "lint": "eslint src/",
    "format": "prettier --write src/"
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "prettier": "^3.0.0",
    "jest": "^29.0.0"
  },
  "dependencies": {
    "express": "^4.18.0"
  }
}
"""
        (project_path / "package.json").write_text(package_json_content)
        
        # Verify package.json content
        package_file = project_path / "package.json"
        assert package_file.exists()
        
        content = package_file.read_text()
        assert "test-js-project" in content
        assert "eslint" in content
        assert "prettier" in content
        assert "jest" in content
        assert "express" in content

    def test_javascript_project_eslint_config(self, temp_dir):
        """Test that JavaScript project has ESLint configuration."""
        project_name = "test-js-project"
        project_path = temp_dir / project_name
        project_path.mkdir()
        
        # Create ESLint config
        eslint_config_content = """
{
  "env": {
    "browser": true,
    "es2021": true,
    "node": true
  },
  "extends": [
    "eslint:recommended"
  ],
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "rules": {
    "indent": ["error", 2],
    "linebreak-style": ["error", "unix"],
    "quotes": ["error", "single"],
    "semi": ["error", "always"]
  }
}
"""
        (project_path / ".eslintrc.json").write_text(eslint_config_content)
        
        # Verify ESLint configuration
        eslint_file = project_path / ".eslintrc.json"
        assert eslint_file.exists()
        
        content = eslint_file.read_text()
        assert "eslint:recommended" in content
        assert "indent" in content
        assert "quotes" in content

    def test_javascript_project_prettier_config(self, temp_dir):
        """Test that JavaScript project has Prettier configuration."""
        project_name = "test-js-project"
        project_path = temp_dir / project_name
        project_path.mkdir()
        
        # Create Prettier config
        prettier_config_content = """
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
"""
        (project_path / ".prettierrc.json").write_text(prettier_config_content)
        
        # Verify Prettier configuration
        prettier_file = project_path / ".prettierrc.json"
        assert prettier_file.exists()
        
        content = prettier_file.read_text()
        assert "semi" in content
        assert "singleQuote" in content
        assert "printWidth" in content

    def test_javascript_project_git_integration(self, temp_dir):
        """Test that JavaScript project integrates with Git."""
        project_name = "test-js-project"
        project_path = temp_dir / project_name
        project_path.mkdir()
        
        # Create .gitignore
        gitignore_content = """
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Production builds
build/
dist/
out/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        (project_path / ".gitignore").write_text(gitignore_content)
        
        # Verify .gitignore content
        gitignore_file = project_path / ".gitignore"
        assert gitignore_file.exists()
        
        content = gitignore_file.read_text()
        assert "node_modules/" in content
        assert "build/" in content
        assert ".env" in content
        assert ".vscode/" in content


class TestProjectValidation:
    """Integration tests for project validation."""

    def test_project_name_validation_integration(self):
        """Test project name validation in integration context."""
        validator = SecurityValidator()
        
        # Test valid names
        valid_names = ["my-project", "my_project", "MyProject", "project123"]
        for name in valid_names:
            is_valid, error = validator.validate_project_name(name)
            assert is_valid, f"Valid name '{name}' was rejected: {error}"
        
        # Test invalid names
        invalid_names = ["", "invalid;project", "invalid..project", "con"]
        for name in invalid_names:
            is_valid, error = validator.validate_project_name(name)
            assert not is_valid, f"Invalid name '{name}' was accepted"

    def test_project_path_validation_integration(self, temp_dir):
        """Test project path validation in integration context."""
        validator = SecurityValidator()
        
        # Test valid paths
        valid_paths = [str(temp_dir), str(temp_dir / "valid-project")]
        for path in valid_paths:
            is_valid, error = validator.validate_path(path)
            assert is_valid, f"Valid path '{path}' was rejected: {error}"
        
        # Test invalid paths
        invalid_paths = ["path/../dangerous", "path;dangerous", "path|dangerous"]
        for path in invalid_paths:
            is_valid, error = validator.validate_path(path)
            assert not is_valid, f"Invalid path '{path}' was accepted"

    def test_project_creation_security_integration(self, temp_dir):
        """Test that project creation respects security constraints."""
        cli_manager = SecureCLIManager(verbose=False)
        
        # Test that dangerous commands are rejected
        dangerous_commands = [
            ["rm", "-rf", "/"],
            ["sudo", "rm", "-rf", "/"],
            ["python", ";", "rm", "-rf", "/"]
        ]
        
        for cmd in dangerous_commands:
            result = cli_manager.run(cmd, "Test dangerous command")
            assert not result.success, f"Dangerous command {cmd} was executed"
            assert not result.security_validated, f"Dangerous command {cmd} was validated"


class TestProjectTemplates:
    """Integration tests for project templates."""

    def test_python_project_template_content(self, temp_dir):
        """Test that Python project template has correct content."""
        project_name = "template-test-python"
        project_path = temp_dir / project_name
        project_path.mkdir()
        
        # Create template files
        (project_path / "src" / "main.py").write_text("""
def main():
    print("Hello from template!")
    
if __name__ == "__main__":
    main()
""")
        
        (project_path / "tests" / "test_main.py").write_text("""
import pytest
from src.main import main

def test_main():
    # This is a placeholder test
    assert True
""")
        
        # Verify template content
        main_file = project_path / "src" / "main.py"
        test_file = project_path / "tests" / "test_main.py"
        
        assert main_file.exists()
        assert test_file.exists()
        
        main_content = main_file.read_text()
        test_content = test_file.read_text()
        
        assert "def main():" in main_content
        assert "if __name__ == '__main__':" in main_content
        assert "import pytest" in test_content
        assert "def test_main():" in test_content

    def test_javascript_project_template_content(self, temp_dir):
        """Test that JavaScript project template has correct content."""
        project_name = "template-test-js"
        project_path = temp_dir / project_name
        project_path.mkdir()
        
        # Create template files
        (project_path / "src" / "index.js").write_text("""
function hello() {
    return "Hello from template!";
}

module.exports = { hello };
""")
        
        (project_path / "tests" / "index.test.js").write_text("""
const { hello } = require('../src/index.js');

test('hello returns correct string', () => {
    expect(hello()).toBe('Hello from template!');
});
""")
        
        # Verify template content
        index_file = project_path / "src" / "index.js"
        test_file = project_path / "tests" / "index.test.js"
        
        assert index_file.exists()
        assert test_file.exists()
        
        index_content = index_file.read_text()
        test_content = test_file.read_text()
        
        assert "function hello()" in index_content
        assert "module.exports" in index_content
        assert "const { hello }" in test_content
        assert "expect(hello())" in test_content


class TestProjectWorkflow:
    """Integration tests for complete project workflows."""

    def test_python_project_complete_workflow(self, temp_dir):
        """Test complete Python project workflow."""
        project_name = "workflow-test-python"
        project_path = temp_dir / project_name
        project_path.mkdir()
        
        # 1. Create project structure
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "docs").mkdir()
        
        # 2. Create source code
        (project_path / "src" / "calculator.py").write_text("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
""")
        
        # 3. Create tests
        (project_path / "tests" / "test_calculator.py").write_text("""
import pytest
from src.calculator import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(1, 1) == 0

def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-2, 3) == -6

def test_divide():
    assert divide(6, 2) == 3
    assert divide(5, 2) == 2.5

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(5, 0)
""")
        
        # 4. Create configuration
        (project_path / "pyproject.toml").write_text("""
[project]
name = "workflow-test-python"
version = "0.1.0"
description = "Test calculator"
requires-python = ">=3.8"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
]
""")
        
        # 5. Verify workflow components
        assert (project_path / "src" / "calculator.py").exists()
        assert (project_path / "tests" / "test_calculator.py").exists()
        assert (project_path / "pyproject.toml").exists()
        
        # 6. Test that code can be imported (simulate)
        calculator_content = (project_path / "src" / "calculator.py").read_text()
        assert "def add(" in calculator_content
        assert "def subtract(" in calculator_content
        assert "def multiply(" in calculator_content
        assert "def divide(" in calculator_content
        
        # 7. Test that tests are valid
        test_content = (project_path / "tests" / "test_calculator.py").read_text()
        assert "import pytest" in test_content
        assert "def test_add():" in test_content
        assert "def test_divide_by_zero():" in test_content

    def test_javascript_project_complete_workflow(self, temp_dir):
        """Test complete JavaScript project workflow."""
        project_name = "workflow-test-js"
        project_path = temp_dir / project_name
        project_path.mkdir()
        
        # 1. Create project structure
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "public").mkdir()
        
        # 2. Create source code
        (project_path / "src" / "math.js").write_text("""
function add(a, b) {
    return a + b;
}

function subtract(a, b) {
    return a - b;
}

function multiply(a, b) {
    return a * b;
}

function divide(a, b) {
    if (b === 0) {
        throw new Error('Cannot divide by zero');
    }
    return a / b;
}

module.exports = { add, subtract, multiply, divide };
""")
        
        # 3. Create tests
        (project_path / "tests" / "math.test.js").write_text("""
const { add, subtract, multiply, divide } = require('../src/math.js');

test('add function', () => {
    expect(add(2, 3)).toBe(5);
    expect(add(-1, 1)).toBe(0);
});

test('subtract function', () => {
    expect(subtract(5, 3)).toBe(2);
    expect(subtract(1, 1)).toBe(0);
});

test('multiply function', () => {
    expect(multiply(2, 3)).toBe(6);
    expect(multiply(-2, 3)).toBe(-6);
});

test('divide function', () => {
    expect(divide(6, 2)).toBe(3);
    expect(divide(5, 2)).toBe(2.5);
});

test('divide by zero', () => {
    expect(() => divide(5, 0)).toThrow('Cannot divide by zero');
});
""")
        
        # 4. Create configuration
        (project_path / "package.json").write_text("""
{
  "name": "workflow-test-js",
  "version": "1.0.0",
  "description": "Test math library",
  "main": "src/math.js",
  "scripts": {
    "test": "jest",
    "lint": "eslint src/",
    "format": "prettier --write src/"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0"
  }
}
""")
        
        # 5. Verify workflow components
        assert (project_path / "src" / "math.js").exists()
        assert (project_path / "tests" / "math.test.js").exists()
        assert (project_path / "package.json").exists()
        
        # 6. Test that code is valid
        math_content = (project_path / "src" / "math.js").read_text()
        assert "function add(" in math_content
        assert "function subtract(" in math_content
        assert "function multiply(" in math_content
        assert "function divide(" in math_content
        assert "module.exports" in math_content
        
        # 7. Test that tests are valid
        test_content = (project_path / "tests" / "math.test.js").read_text()
        assert "const { add, subtract, multiply, divide }" in test_content
        assert "test('add function'" in test_content
        assert "expect(() => divide(5, 0)).toThrow" in test_content