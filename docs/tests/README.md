# Tests for Works On My Machine

[🏠 Main](../README.md) > [🧪 Tests](README.md)

[← Back to Main Documentation](../README.md)

This directory contains all tests for the "Works On My Machine" project, organized in a structured manner to ensure code quality and reliability.

## Table of Contents
- [Test Structure](#-test-structure)
- [Test Types](#-test-types)
- [Test Markers](#️-test-markers)
- [Test Execution](#-test-execution)
- [Test Configuration](#-test-configuration)
- [Test Data](#-test-data)
- [Test Utilities](#-test-utilities)

## Related Documentation
- [Main README](../README.md) - Project overview
- [Python Tools](../languages/python/PYTHON.md) - Python development tools
- [JavaScript Tools](../languages/javascript/JAVASCRIPT.md) - JavaScript development tools

## 📁 Test Structure

```
tests/
├── __init__.py                 # Package Python
├── conftest.py                 # Pytest configuration and shared fixtures
├── unit/                       # Tests unitaires
│   ├── test_security_validator.py    # Security validator tests
│   ├── test_secure_cli_manager.py    # Secure CLI manager tests
│   └── test_wom_cli.py               # Tests du CLI principal
├── integration/                # Integration tests
│   └── test_project_creation.py      # Project creation tests
├── fixtures/                   # Test data
│   ├── sample_projects/        # Sample projects
│   └── test_data/              # Test data
└── mocks/                      # Mocks et stubs
    ├── mock_cli_manager.py     # Mock du gestionnaire CLI
    └── mock_system.py          # System calls mock
```

## 🧪 Test Types

### Unit Tests (`tests/unit/`)

Unit tests verify the behavior of individual components in isolation:

- **`test_security_validator.py`** : Security validator tests
  - Project name validation
  - File path validation
  - Command validation
  - File operation validation
  - Windows registry operation validation

- **`test_secure_cli_manager.py`** : Secure CLI manager tests
  - Secure command execution
  - Error and timeout handling
  - Retry logic
  - Security validation
  - Execution time measurement

- **`test_wom_cli.py`** : Main CLI tests
  - Project creation commands
  - Linting commands
  - Spell checking commands
  - System commands
  - Error handling

### Integration Tests (`tests/integration/`)

Integration tests verify the interaction between multiple components:

- **`test_project_creation.py`** : Project creation tests
  - Python project structure
  - JavaScript project structure
  - Project configuration
  - Git integration
  - VSCode configuration
  - Complete workflows

## 🏷️ Test Markers

Tests use pytest markers for categorization:

- `@pytest.mark.unit` : Unit tests
- `@pytest.mark.integration` : Integration tests
- `@pytest.mark.security` : Security tests
- `@pytest.mark.slow` : Slow tests
- `@pytest.mark.windows` : Windows-specific tests
- `@pytest.mark.linux` : Linux-specific tests
- `@pytest.mark.macos` : macOS-specific tests

## 🚀 Test Execution

### Launch Script

Use the `run_tests.py` script at the project root:

```bash
# All tests
python run_tests.py

# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# Security tests only
python run_tests.py --security

# Tests with coverage
python run_tests.py --coverage

# Fast tests (without slow tests)
python run_tests.py --fast

# Parallel tests
python run_tests.py --parallel

# Debug mode
python run_tests.py --debug

# Check dependencies
python run_tests.py --check-deps

# Show summary
python run_tests.py --summary

# Specific test
python run_tests.py tests/unit/test_security_validator.py
```

### Direct pytest commands

```bash
# All tests
pytest tests/

# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Tests with specific marker
pytest -m security
pytest -m "not slow"

# Tests with coverage
pytest --cov=shared --cov=languages --cov-report=html

# Parallel tests
pytest -n auto

# Tests with more details
pytest -v --tb=long
```

## 🔧 Configuration

### pytest.ini

The `pytest.ini` file configures pytest with:

- Test directories: `tests/`
- Custom markers
- Default options (verbose, colors, etc.)
- Warning filters

### conftest.py

The `conftest.py` file defines:

- **Shared fixtures**: Temporary directories, sample projects
- **Global mocks**: CLI manager, subprocess, file system
- **Automatic configuration**: Automatic markers based on file name
- **Test data**: Project names, paths, commands

## 📊 Code Coverage

Code coverage is measured for:

- `shared/`: Shared modules (security, CLI, etc.)
- `languages/`: Language-specific modules
- `wom_secure.py`: Secure main CLI

To generate a coverage report:

```bash
python run_tests.py --coverage
```

The HTML report will be generated in `htmlcov/`.

## 🛡️ Security Tests

Security tests verify:

1. **Input validation**: Project names, paths, commands
2. **Injection prevention**: Dangerous commands, special characters
3. **Directory traversal**: Dangerous relative paths
4. **File operations**: Permissions, disk space
5. **Script execution**: Script validation before execution

## 🔄 Development Workflow

### Adding a new test

1. **Identify the type**: unit or integration
2. **Choose the location**: `tests/unit/` or `tests/integration/`
3. **Name the file**: `test_<module>_<feature>.py`
4. **Use fixtures**: Reuse existing fixtures
5. **Add markers**: Mark with appropriate markers

### Unit test example

```python
import pytest
from shared.security_validator import SecurityValidator

class TestSecurityValidator:
    """Tests for the security validator."""
    
    def test_validate_project_name_valid(self):
        """Test validation of valid project name."""
        validator = SecurityValidator()
        is_valid, error = validator.validate_project_name("my-project")
        assert is_valid
        assert error == ""
    
    def test_validate_project_name_invalid(self):
        """Test validation of invalid project name."""
        validator = SecurityValidator()
        is_valid, error = validator.validate_project_name("invalid;project")
        assert not is_valid
        assert "dangerous characters" in error
```

### Integration test example

```python
import pytest
from pathlib import Path

class TestProjectCreation:
    """Integration tests for project creation."""
    
    def test_create_python_project_structure(self, temp_dir):
        """Test that Python project creation generates the correct structure."""
        project_name = "test-project"
        project_path = temp_dir / project_name
        
        # Simulate project creation
        project_path.mkdir()
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        
        # Verify structure
        assert project_path.exists()
        assert (project_path / "src").exists()
        assert (project_path / "tests").exists()
```

## 🐛 Test Debugging

### Debug mode

```bash
python run_tests.py --debug
```

### Specific tests

```bash
# Specific test with more details
pytest tests/unit/test_security_validator.py::TestSecurityValidator::test_validate_project_name_valid -v -s

# Failed tests only
pytest --lf

# Failed tests and dependencies
pytest --lf --ff
```

### Logs and traces

```bash
# Show logs
pytest --log-cli-level=DEBUG

# Complete traceback
pytest --tb=long

# Stop at first failure
pytest -x
```

## 📈 Quality Metrics

### Coverage targets

- **Global coverage**: ≥ 90%
- **Critical modules**: ≥ 95% (security, CLI)
- **New features**: ≥ 95%

### Performance

- **Unit tests**: < 1 second per test
- **Integration tests**: < 5 seconds per test
- **Complete suite**: < 30 seconds

### Reliability

- **Flaky tests**: 0%
- **Dependent tests**: Avoid dependencies between tests
- **Isolation**: Each test must be independent

## 🔍 Best Practices

### Writing tests

1. **Clear naming**: Descriptive names for tests and classes
2. **Documentation**: Docstrings to explain test purpose
3. **Arrange-Act-Assert**: Clear test structure
4. **Fixtures**: Reuse existing fixtures
5. **Appropriate mocks**: Mock external dependencies

### Maintenance

1. **Up-to-date tests**: Maintain tests with code
2. **Refactoring**: Refactor tests when necessary
3. **Performance**: Monitor execution time
4. **Coverage**: Maintain high coverage

### Continuous Integration

1. **Automatic execution**: Tests on each commit
2. **Reports**: Generate coverage reports
3. **Thresholds**: Define coverage thresholds
4. **Notifications**: Alert on failure

## 🆘 Troubleshooting

### Common issues

1. **Import errors**: Check PYTHONPATH
2. **Missing fixtures**: Check conftest.py
3. **Slow tests**: Use `@pytest.mark.slow` markers
4. **Flaky tests**: Add retries or mocks

### Support

For test issues:

1. Check pytest documentation
2. Consult existing examples
3. Use debug mode
4. Check dependencies with `--check-deps`