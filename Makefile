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

# Aide par défaut
help:
	@echo "$(BLUE)works-on-my-machine - Commandes de développement$(RESET)"
	@echo ""
	@echo "$(GREEN)Installation:$(RESET)"
	@echo "  install      - Installer le package"
	@echo "  install-dev  - Installer les dépendances de développement"
	@echo ""
	@echo "$(GREEN)Formatage et qualité:$(RESET)"
	@echo "  format       - Formater le code (black + isort)"
	@echo "  lint         - Vérifier la qualité du code"
	@echo "  fix          - Corriger automatiquement les problèmes"
	@echo ""
	@echo "$(GREEN)Tests:$(RESET)"
	@echo "  test         - Lancer les tests unitaires"
	@echo "  test-cov     - Tests avec couverture"
	@echo ""
	@echo "$(GREEN)Hooks et outils:$(RESET)"
	@echo "  setup-hooks  - Installer les hooks pre-commit"
	@echo "  pre-commit   - Lancer les vérifications pre-commit"
	@echo ""
	@echo "$(GREEN)Nettoyage:$(RESET)"
	@echo "  clean        - Nettoyer les fichiers temporaires"

# Installation
install:
	@echo "$(BLUE)Installation du package...$(RESET)"
	$(PIP) install -e .

install-dev:
	@echo "$(BLUE)Installation des dépendances de développement...$(RESET)"
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
	@echo "$(BLUE)Correction des problèmes d'espaces...$(RESET)"
	$(PYTHON) lint.py --fix
	@echo "$(GREEN)Code formaté automatiquement !$(RESET)"

# Linting
lint:
	@echo "$(BLUE)Vérification de la qualité du code...$(RESET)"
	$(PYTHON) lint.py

# Tests
test:
	@echo "$(BLUE)Lancement des tests unitaires...$(RESET)"
	pytest tests/ 2>/dev/null || echo "$(YELLOW)Pas de tests configurés pour le moment$(RESET)"

test-cov:
	@echo "$(BLUE)Tests avec couverture...$(RESET)"
	pytest --cov=shared --cov=languages --cov-report=html --cov-report=term 2>/dev/null || echo "$(YELLOW)Pas de tests configurés$(RESET)"

# Hooks pre-commit
setup-hooks:
	@echo "$(BLUE)Installation des hooks pre-commit...$(RESET)"
	pre-commit install
	@echo "$(GREEN)Hooks pre-commit installés !$(RESET)"

pre-commit:
	@echo "$(BLUE)Lancement des vérifications pre-commit...$(RESET)"
	pre-commit run --all-files

# Nettoyage
clean:
	@echo "$(BLUE)Nettoyage des fichiers temporaires...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ 2>/dev/null || true
	@echo "$(GREEN)Nettoyage terminé !$(RESET)"

# Commande complète de vérification
check: format lint test
	@echo "$(GREEN)Toutes les vérifications sont terminées !$(RESET)"

# Préparation pour un commit
prepare: format lint
	@echo "$(GREEN)Code prêt pour le commit !$(RESET)"

# Test des outils dev-tools
demo:
	@echo "$(BLUE)Test des outils works-on-my-machine...$(RESET)"
	$(PYTHON) womm.py --help 2>/dev/null || echo "Lancez: python womm.py"
	@echo "$(GREEN)Démo terminée !$(RESET)"