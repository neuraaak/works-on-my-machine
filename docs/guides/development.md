# Development Guide

Contributing to WOMM - development setup, code standards, testing, and release process.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Code editor (VSCode recommended)

### Clone Repository

```bash
git clone https://github.com/neuraaak/works-on-my-machine.git
cd works-on-my-machine
```

### Install Dependencies

```bash
# Install in development mode
pip install -e ".[dev]"

# This installs:
# - Runtime dependencies
# - Development tools (pytest, black, mypy, ruff)
# - Documentation tools (mkdocs, mkdocstrings)
```

### Verify Installation

```bash
# Run WOMM from source
python -m womm --version

# Run tests
pytest

# Run linting
ruff check .
black --check .
mypy womm/
```

## Project Structure

```text
works-on-my-machine/
├── womm/                      # Main package
│   ├── cli/                   # CLI commands
│   ├── core/                  # Core logic
│   │   ├── managers/          # Business logic managers
│   │   ├── ui/                # UI components
│   │   ├── utils/             # Utilities
│   │   └── exceptions/        # Exception hierarchy
│   └── __main__.py            # Entry point
├── tests/                     # Test suite
├── docs/                      # Documentation
├── .github/                   # GitHub workflows
├── .scripts/                  # Build scripts
├── pyproject.toml             # Project configuration
└── README.md                  # Main README
```

## Code Standards

### Python Style (PEP 8)

- Use **Black** for formatting (line length: 88)
- Use **type hints** for all functions
- Use **Google-style docstrings**
- Follow **PEP 8** conventions

**Example:**

```python
from pathlib import Path
from typing import Optional

def create_project(name: str, path: Optional[Path] = None) -> Path:
    """Create a new project.

    Args:
        name: Project name
        path: Optional output path

    Returns:
        Path: Created project directory

    Raises:
        ValueError: If name is invalid
    """
    if not name:
        raise ValueError("Project name cannot be empty")

    output_path = path or Path.cwd() / name
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path
```

### Type Hints

Use type hints consistently:

```python
# Good
def process_data(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Bad
def process_data(items):
    return {item: len(item) for item in items}
```

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
    """
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_project_manager.py

# Run with coverage
pytest --cov=womm --cov-report=html

# Run verbose
pytest -v --tb=short
```

### Writing Tests

```python
import pytest
from womm.core.managers.project_manager import ProjectManager

def test_create_project_success():
    """Test successful project creation."""
    manager = ProjectManager()
    result = manager.create_project("test-project", "python")
    assert result.exists()
    assert (result / "src").exists()

def test_create_project_invalid_name():
    """Test project creation with invalid name."""
    manager = ProjectManager()
    with pytest.raises(ValueError):
        manager.create_project("", "python")
```

### Test Organization

```text
tests/
├── conftest.py                # Shared fixtures
├── test_cli/                  # CLI tests
├── test_managers/             # Manager tests
└── test_utils/                # Utility tests
```

## Linting and Formatting

### Black (Formatting)

```bash
# Format code
black womm/ tests/

# Check formatting
black --check womm/ tests/
```

### Ruff (Linting)

```bash
# Lint code
ruff check womm/ tests/

# Auto-fix issues
ruff check --fix womm/ tests/
```

### Mypy (Type Checking)

```bash
# Type check
mypy womm/

# Strict mode
mypy --strict womm/
```

## Documentation

### Building Documentation

```bash
# Install docs dependencies
pip install -e ".[dev]"

# Serve docs locally
mkdocs serve

# Build docs
mkdocs build

# Visit http://127.0.0.1:8000
```

### Writing Documentation

**Documentation Standards:**

- **Language**: All documentation MUST be in English
- **Format**: Markdown files in `docs/` directory
- **Style**: Clear, concise, professional
- **Code blocks**: Always specify language
- **Links**: Use relative links for internal pages

**Example:**

````markdown
# Page Title

Description of the page.

## Section

Content with [link](../other-page.md).

```python
# Code example
def example():
    pass
```

### API Documentation

Use mkdocstrings for API docs:

```markdown
# Module Documentation

::: womm.core.managers.project_manager
options:
show_source: true
members: true
```
````

## Contributing Workflow

### 1. Create Branch

```bash
# Create feature branch
git checkout -b feature/my-feature

# Or bug fix branch
git checkout -b fix/my-bug
```

### 2. Make Changes

```bash
# Make your changes
# Edit files...

# Run tests
pytest

# Run linting
ruff check --fix .
black .
mypy womm/
```

### 3. Commit Changes

Use conventional commits:

```bash
# Feature
git commit -m "feat: add new template system"

# Bug fix
git commit -m "fix: resolve PATH issue on Windows"

# Documentation
git commit -m "docs: update installation guide"

# Refactor
git commit -m "refactor: improve project manager structure"
```

**Commit Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### 4. Push and Create PR

```bash
# Push branch
git push origin feature/my-feature

# Create Pull Request on GitHub
# Fill out PR template
# Wait for review
```

## Code Review Guidelines

### For Contributors

- Write clear PR descriptions
- Include tests for new features
- Update documentation
- Respond to feedback promptly
- Keep PRs focused and small

### For Reviewers

- Be constructive and respectful
- Check code quality and tests
- Verify documentation updates
- Test changes locally
- Approve when ready

## Release Process

### Versioning

Follow Semantic Versioning (SemVer):

- **MAJOR** (3.0.0): Breaking changes
- **MINOR** (3.1.0): New features (backward compatible)
- **PATCH** (3.1.1): Bug fixes

### Creating Release

```bash
# 1. Update version in pyproject.toml
version = "3.2.0"

# 2. Update CHANGELOG.md
## [3.2.0] - 2026-02-11
### Added
- New template system
### Fixed
- PATH issue on Windows

# 3. Commit and tag
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 3.2.0"
git tag v3.2.0
git push origin main --tags

# 4. GitHub Actions will:
#    - Run tests
#    - Build package
#    - Publish to PyPI
#    - Create GitHub release
```

## Best Practices

### Code Quality

1. **Write Tests First** - TDD approach
2. **Keep Functions Small** - Single responsibility
3. **Use Type Hints** - Better IDE support
4. **Document Public APIs** - Clear docstrings
5. **Handle Errors** - Proper exception handling

### Git Workflow

1. **Small Commits** - One logical change per commit
2. **Descriptive Messages** - Follow conventional commits
3. **Keep PRs Focused** - One feature/fix per PR
4. **Update from Main** - Rebase frequently
5. **Review Your Code** - Before pushing

### Documentation Standards

1. **Update Docs** - With code changes
2. **Add Examples** - For new features
3. **Keep It Current** - Remove outdated info
4. **Link Pages** - Cross-reference related docs
5. **Test Docs** - Build and review locally

## Troubleshooting

### Import Errors

```bash
# Reinstall in development mode
pip install -e ".[dev]"
```

### Test Failures

```bash
# Run specific test with verbose output
pytest -v tests/test_file.py::test_function

# Check test coverage
pytest --cov=womm --cov-report=term-missing
```

### Type Check Errors

```bash
# Run mypy with verbose output
mypy --show-error-codes womm/

# Ignore specific error
# type: ignore[error-code]
```

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/neuraaak/works-on-my-machine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/neuraaak/works-on-my-machine/discussions)
- **Email**: Contact maintainers

## See Also

- [Getting Started](../getting-started.md)
- [Configuration Guide](configuration.md)
- [API Reference](../api/index.md)
- [Examples](../examples/index.md)

---

Thank you for contributing to WOMM! 🚀
