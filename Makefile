# ///////////////////////////////////////////////////////////////
# MAKEFILE - Development Commands
# Project: works-on-my-machine
# Usage : make <target>
# ///////////////////////////////////////////////////////////////

.PHONY: help install install-dev format lint test clean setup-hooks check prepare

# ///////////////////////////////////////////////////////////////
# CONFIGURATION
# ///////////////////////////////////////////////////////////////

PYTHON := python
PIP := pip
PACKAGE := .

# ///////////////////////////////////////////////////////////////
# COLORS
# ///////////////////////////////////////////////////////////////

BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# ///////////////////////////////////////////////////////////////
# DEFAULT HELP TARGET
# ///////////////////////////////////////////////////////////////

help:
	@echo "$(BLUE)works-on-my-machine - Development Commands$(RESET)"
	@echo ""
	@echo "$(GREEN)Installation:$(RESET)"
	@echo "  install      - Install the package"
	@echo "  install-dev  - Install development dependencies"
	@echo ""
	@echo "$(GREEN)Formatting and quality:$(RESET)"
	@echo "  format       - Format code (black + isort)"
	@echo "  lint         - Check code quality"
	@echo "  fix          - Automatically fix issues"
	@echo ""
	@echo "$(GREEN)Tests:$(RESET)"
	@echo "  test         - Run all tests"
	@echo "  test-unit    - Unit tests only"
	@echo "  test-integration - Integration tests only"
	@echo "  test-security - Security tests only"
	@echo "  test-fast    - Fast tests (without slow tests)"
	@echo "  test-cov     - Tests with coverage"
	@echo "  test-parallel - Tests in parallel"
	@echo ""
	@echo "$(GREEN)Hooks and tools:$(RESET)"
	@echo "  setup-hooks  - Install pre-commit hooks"
	@echo "  pre-commit   - Run pre-commit checks"
	@echo ""
	@echo "$(GREEN)Cleanup:$(RESET)"
	@echo "  clean        - Remove temporary files"

# ///////////////////////////////////////////////////////////////
# INSTALLATION
# ///////////////////////////////////////////////////////////////
install:
	@echo "$(BLUE)Installing package...$(RESET)"
	$(PIP) install -e .

install-dev:
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(PIP) install -e ".[dev]"
	$(PIP) install pre-commit

# ///////////////////////////////////////////////////////////////
# FORMATTING
# ///////////////////////////////////////////////////////////////
format:
	@echo "$(BLUE)Formatting code with Black...$(RESET)"
	black shared languages womm.py .scripts/dev/lint.py setup.py
	@echo "$(BLUE)Organizing imports with isort...$(RESET)"
	isort shared languages womm.py .scripts/dev/lint.py setup.py

# ///////////////////////////////////////////////////////////////
# AUTO-FIX (LINT + FORMAT)
# ///////////////////////////////////////////////////////////////
fix: format
	@echo "$(BLUE)Automatic fixes with Ruff...$(RESET)"
	ruff check --fix shared languages womm.py .scripts/dev/lint.py setup.py
	@echo "$(GREEN)Code automatically fixed!$(RESET)"

# ///////////////////////////////////////////////////////////////
# LINTING ONLY
# ///////////////////////////////////////////////////////////////
lint:
	@echo "$(BLUE)Checking code quality with Ruff...$(RESET)"
	ruff check shared languages womm.py .scripts/dev/lint.py setup.py
	@echo "$(BLUE)Security check with Bandit...$(RESET)"
	bandit -r shared languages -f json -o bandit-report.json || true
	@echo "$(GREEN)Linting completed!$(RESET)"

# ///////////////////////////////////////////////////////////////
# TESTS
# ///////////////////////////////////////////////////////////////
test:
	@echo "$(BLUE)Running all tests...$(RESET)"
	pytest tests/ -v

test-unit:
	@echo "$(BLUE)Running unit tests...$(RESET)"
	pytest tests/unit/ -v

test-integration:
	@echo "$(BLUE)Running integration tests...$(RESET)"
	pytest tests/integration/ -v

test-security:
	@echo "$(BLUE)Running security tests...$(RESET)"
	pytest -m security -v

test-fast:
	@echo "$(BLUE)Running fast tests...$(RESET)"
	pytest tests/ -m "not slow" -v

test-cov:
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	pytest tests/ --cov=shared --cov=languages --cov-report=html --cov-report=term -v

test-parallel:
	@echo "$(BLUE)Tests in parallel...$(RESET)"
	pytest tests/ -n auto -v

# ///////////////////////////////////////////////////////////////
# PRE-COMMIT HOOKS
# ///////////////////////////////////////////////////////////////
setup-hooks:
	@echo "$(BLUE)Installing pre-commit hooks...$(RESET)"
	pre-commit install
	@echo "$(GREEN)Pre-commit hooks installed!$(RESET)"

pre-commit:
	@echo "$(BLUE)Running pre-commit checks...$(RESET)"
	pre-commit run --all-files

# ///////////////////////////////////////////////////////////////
# CLEANUP
# ///////////////////////////////////////////////////////////////
clean:
	@echo "$(BLUE)Cleaning temporary files...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ 2>/dev/null || true
	@echo "$(GREEN)Cleanup completed!$(RESET)"

# ///////////////////////////////////////////////////////////////
# AGGREGATE COMMANDS
# ///////////////////////////////////////////////////////////////
check: format lint test
	@echo "$(GREEN)All verifications completed!$(RESET)"

# Preparation for commit (format + lint)
prepare: format lint
	@echo "$(GREEN)Code ready for commit!$(RESET)"

# ///////////////////////////////////////////////////////////////
# DEMO
# ///////////////////////////////////////////////////////////////
demo:
	@echo "$(BLUE)Testing works-on-my-machine tools...$(RESET)"
	$(PYTHON) womm.py --help 2>/dev/null || echo "Run: python womm.py"
	@echo "$(GREEN)Demo completed!$(RESET)"