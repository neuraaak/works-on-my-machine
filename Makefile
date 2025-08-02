# Makefile pour works-on-my-machine
# Usage: make <target>

.PHONY: help install install-dev format lint test clean setup-hooks check prepare

# Configuration
PYTHON := python
PIP := pip
PACKAGE := .

# Couleurs pour l'affichage
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Default help
help:
	@echo "$(BLUE)works-on-my-machine - Development Commands$(RESET)"
	@echo ""
	@echo "$(GREEN)Installation:$(RESET)"
	@echo "  install      - Installer le package"
	@echo "  install-dev  - Install development dependencies"
	@echo ""
	@echo "$(GREEN)Formatting and quality:$(RESET)"
@echo "  format       - Format code (black + isort)"
@echo "  lint         - Check code quality"
@echo "  fix          - Automatically fix issues"
	@echo ""
	@echo "$(GREEN)Tests:$(RESET)"
	@echo "  test         - Lancer tous les tests"
	@echo "  test-unit    - Tests unitaires uniquement"
	@echo "  test-integration - Integration tests only"
@echo "  test-security - Security tests only"
	@echo "  test-fast    - Tests rapides (sans tests lents)"
	@echo "  test-cov     - Tests avec couverture"
	@echo "  test-parallel - Tests in parallel"
	@echo ""
	@echo "$(GREEN)Hooks et outils:$(RESET)"
	@echo "  setup-hooks  - Installer les hooks pre-commit"
	@echo "  pre-commit   - Run pre-commit checks"
	@echo ""
	@echo "$(GREEN)Nettoyage:$(RESET)"
	@echo "  clean        - Nettoyer les fichiers temporaires"

# Installation
install:
	@echo "$(BLUE)Installation du package...$(RESET)"
	$(PIP) install -e .

install-dev:
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(PIP) install -e ".[dev]"
	$(PIP) install pre-commit

# Formatage automatique
format:
	@echo "$(BLUE)Formatage du code avec Black...$(RESET)"
	black shared languages womm.py lint.py setup.py
	@echo "$(BLUE)Organisation des imports avec isort...$(RESET)"
	isort shared languages womm.py lint.py setup.py

# Correction automatique
fix: format
	@echo "$(BLUE)Correction automatique avec Ruff...$(RESET)"
	ruff check --fix shared languages womm.py lint.py setup.py
	@echo "$(GREEN)Code automatically fixed!$(RESET)"

# Linting
lint:
	@echo "$(BLUE)Checking code quality with Ruff...$(RESET)"
	ruff check shared languages womm.py lint.py setup.py
	@echo "$(BLUE)Security check with Bandit...$(RESET)"
	bandit -r shared languages -f json -o bandit-report.json || true
	@echo "$(GREEN)Linting completed!$(RESET)"

# Tests
test:
	@echo "$(BLUE)Lancement de tous les tests...$(RESET)"
	pytest tests/ -v

test-unit:
	@echo "$(BLUE)Lancement des tests unitaires...$(RESET)"
	pytest tests/unit/ -v

test-integration:
	@echo "$(BLUE)Running integration tests...$(RESET)"
	pytest tests/integration/ -v

test-security:
	@echo "$(BLUE)Running security tests...$(RESET)"
	pytest -m security -v

test-fast:
	@echo "$(BLUE)Lancement des tests rapides...$(RESET)"
	pytest tests/ -m "not slow" -v

test-cov:
	@echo "$(BLUE)Tests avec couverture...$(RESET)"
	pytest tests/ --cov=shared --cov=languages --cov-report=html --cov-report=term -v

test-parallel:
	@echo "$(BLUE)Tests in parallel...$(RESET)"
	pytest tests/ -n auto -v

# Hooks pre-commit
setup-hooks:
	@echo "$(BLUE)Installation des hooks pre-commit...$(RESET)"
	pre-commit install
	@echo "$(GREEN)Pre-commit hooks installed!$(RESET)"

pre-commit:
	@echo "$(BLUE)Running pre-commit checks...$(RESET)"
	pre-commit run --all-files

# Nettoyage
clean:
	@echo "$(BLUE)Nettoyage des fichiers temporaires...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ 2>/dev/null || true
	@echo "$(GREEN)Cleanup completed!$(RESET)"

# Complete verification command
check: format lint test
	@echo "$(GREEN)All verifications completed!$(RESET)"

# Preparation for commit
prepare: format lint
	@echo "$(GREEN)Code ready for commit!$(RESET)"

# Test des outils dev-tools
demo:
	@echo "$(BLUE)Test des outils works-on-my-machine...$(RESET)"
	$(PYTHON) womm.py --help 2>/dev/null || echo "Lancez: python womm.py"
	@echo "$(GREEN)Demo completed!$(RESET)"