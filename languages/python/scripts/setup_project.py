#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'initialisation d'environnement de développement Python.

Usage:
    python setup_project.py [nom_projet]
    python setup_project.py --current-dir

Fonctionnalités:
    - Copie les configurations de développement
    - Initialise Git avec .gitignore adapté
    - Configure les hooks pre-commit
    - Crée la structure de projet de base
    - Configure VSCode
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


class PythonProjectSetup:
    """Classe pour configurer un environnement de développement Python."""

    def __init__(self, project_path: Path, project_name: str):
        """Initialise le script de configuration du projet Python."""
        self.project_path = project_path
        self.project_name = project_name
        self.python_tools_path = Path(__file__).parent.parent
        self.devtools_path = self.python_tools_path.parent.parent

    def setup_all(self):
        """Configure tout l'environnement de développement."""
        print(f"🐍 Configuration de l'environnement Python pour '{self.project_name}'")
        print(f"📁 Répertoire: {self.project_path}")

        self.create_directory_structure()
        self.copy_configs()
        self.setup_git()
        self.setup_cspell()
        self.create_project_files()
        self.setup_vscode()
        self.setup_development_environment()
        self.install_hooks()

        print("\n✅ Configuration Python terminée !")
        self.print_next_steps()

    def create_directory_structure(self):
        """Crée la structure de répertoires de base."""
        print("\n📂 Création de la structure de répertoires...")

        directories = [
            self.project_path / self.project_name,
            self.project_path / "tests",
            self.project_path / "docs",
            self.project_path / ".vscode",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ {directory}")

    def copy_configs(self):
        """Copy configuration files."""
        print("\n⚙️ Copie des configurations Python...")

        configs = [
            ("configs/.flake8", ".flake8"),
            ("configs/.pre-commit-config.yaml", ".pre-commit-config.yaml"),
            ("templates/gitignore-python.txt", ".gitignore"),
            ("templates/Makefile.template", "Makefile"),
            ("templates/DEVELOPMENT.md.template", "docs/DEVELOPMENT.md"),
        ]

        for source, dest in configs:
            source_path = self.python_tools_path / source
            dest_path = self.project_path / dest

            if source_path.exists():
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Traiter les templates
                if source_path.suffix == ".template":
                    content = source_path.read_text(encoding="utf-8")
                    content = content.replace("{{PROJECT_NAME}}", self.project_name)
                    dest_path.write_text(content, encoding="utf-8")
                else:
                    shutil.copy2(source_path, dest_path)

                print(f"   ✓ {dest}")
            else:
                print(f"   ⚠️  Fichier manquant: {source}")

    def setup_git(self):
        """Initialise Git et configure .gitignore."""
        print("\n🔧 Configuration Git...")

        if not (self.project_path / ".git").exists():
            try:
                subprocess.run(
                    ["git", "init"],
                    cwd=self.project_path,
                    check=True,
                    capture_output=True,
                )
                print("   ✓ Repository Git initialisé")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("   ⚠️  Git non trouvé ou erreur d'initialisation")

    def setup_cspell(self):
        """Configure CSpell pour le projet."""
        print("📝 Configuration CSpell...")

        # Importer le gestionnaire CSpell
        devtools_path = Path.home() / ".dev-tools"
        sys.path.insert(0, str(devtools_path))

        try:
            from shared.cspell_manager import setup_project_cspell

            success = setup_project_cspell(
                self.project_path, "python", self.project_name
            )
            if success:
                print("   ✓ Configuration CSpell créée")
            else:
                print("   ⚠ Erreur lors de la configuration CSpell")
        except ImportError:
            print("   ⚠ Module cspell_manager non trouvé")

    def setup_development_environment(self):
        """Configure l'environnement de développement Python."""
        print("🛠️ Configuration de l'environnement de développement...")

        # Importer le gestionnaire d'environnement
        devtools_path = Path.home() / ".dev-tools"
        sys.path.insert(0, str(devtools_path))

        try:
            from shared.environment_manager import EnvironmentManager

            manager = EnvironmentManager(self.project_path, "python")

            if manager.prompt_install_tools():
                if manager.setup_python_environment():
                    manager.create_activation_scripts()
                    print("   ✓ Environnement de développement configuré")
                    return True
                else:
                    print("   ⚠ Erreur lors de la configuration de l'environnement")
                    return False
            else:
                print("   ⏭️ Configuration de l'environnement ignorée")
                return True

        except ImportError:
            print("   ⚠ Module environment_manager non trouvé")
            return False

    def create_project_files(self):
        """Crée les fichiers de base du projet."""
        print("\n📄 Création des fichiers de base...")

        # pyproject.toml
        pyproject_content = f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{self.project_name}"
version = "0.1.0"
description = "Description de votre projet Python"
readme = "README.md"
requires-python = ">=3.9"
license = {{text = "MIT"}}
authors = [{{name = "Votre Nom", email = "votre.email@example.com"}}]

dependencies = [
    # Ajoutez vos dépendances ici
]

[project.optional-dependencies]
dev = [
    "pytest>=6.2.5",
    "pytest-cov>=3.0.0",
    "coverage>=7.10.0",
    "flake8>=6.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "pre-commit>=3.0.0",
    "bandit>=1.7.0",
]

[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311', 'py312']

[tool.isort]
profile = "black"
line_length = 88
known_first_party = ["{self.project_name}"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--tb=short",
    "--cov={self.project_name}",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
]
"""

        (self.project_path / "pyproject.toml").write_text(
            pyproject_content, encoding="utf-8"
        )
        print("   ✓ pyproject.toml")

        # __init__.py
        init_content = f'''# -*- coding: utf-8 -*-
"""
{self.project_name} package.
"""
__version__ = "0.1.0"
'''
        (self.project_path / self.project_name / "__init__.py").write_text(
            init_content, encoding="utf-8"
        )
        print("   ✓ __init__.py")

        # README.md
        readme_content = f"""# {self.project_name}

Description de votre projet Python.

## 🚀 Installation

```bash
# Development mode installation
pip install -e ".[dev]"
```

## 🛠️ Development

```bash
# Code formatting
black .
isort .

# Quality check
flake8

# Tests
pytest
pytest --cov  # With coverage
```

## 📋 Make Commands

```bash
make help           # Help
make format         # Automatic formatting
make lint           # Quality check
make test           # Unit tests
make test-cov       # Tests with coverage
make clean          # Cleanup
```

## 📖 Documentation

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for complete development guide.
"""
        (self.project_path / "README.md").write_text(readme_content, encoding="utf-8")
        print("   ✓ README.md")

        # Test example
        test_content = f'''# -*- coding: utf-8 -*-
"""
Tests pour {self.project_name}.
"""
import pytest
from {self.project_name} import __version__


def test_version():
    """Test de la version du package."""
    assert __version__ == "0.1.0"


def test_import():
    """Test d'import du package."""
    import {self.project_name}
    assert {self.project_name} is not None
'''
        (self.project_path / "tests" / f"test_{self.project_name}.py").write_text(
            test_content, encoding="utf-8"
        )
        print("   ✓ test example")

    def setup_vscode(self):
        """Configure VSCode."""
        print("\n🔧 Configuration VSCode...")

        vscode_files = ["settings.json", "extensions.json"]

        for file in vscode_files:
            source = self.python_tools_path / "vscode" / file
            dest = self.project_path / ".vscode" / file

            if source.exists():
                shutil.copy2(source, dest)
                print(f"   ✓ .vscode/{file}")
            else:
                print(f"   ⚠️  Missing VSCode file: {file}")

    def install_hooks(self):
        """Installe les hooks pre-commit."""
        print("\n🔒 Installing pre-commit hooks...")

        try:
            # Vérifier si pre-commit est installé
            subprocess.run(
                ["pre-commit", "--version"],
                cwd=self.project_path,
                check=True,
                capture_output=True,
            )

            # Installer les hooks
            subprocess.run(
                ["pre-commit", "install"],
                cwd=self.project_path,
                check=True,
                capture_output=True,
            )
            print("   ✓ Pre-commit hooks installed")

        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   ⚠️  pre-commit not found. Install with: pip install pre-commit")

    def print_next_steps(self):
        """Affiche les prochaines étapes."""
        print(
            f"""
🎉 Python project '{self.project_name}' configured successfully!

📋 Next steps:
1. cd {self.project_path}
2. pip install -e ".[dev]"
3. pre-commit install  # If not already done
4. git add .
5. git commit -m "Initial commit with Python dev environment"

🛠️ Useful commands:
- make lint                    # Quality check
- make format                  # Automatic formatting
- make test                    # Tests
- black . && isort .           # Manual formatting
- pytest --cov                 # Tests with coverage

📚 Documentation:
- docs/DEVELOPMENT.md          # Development guide
- {self.python_tools_path}/PYTHON.md  # Complete Python documentation

🐍 Happy Python coding!
"""
        )


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Configure a Python development environment"
    )
    parser.add_argument(
        "project_name", nargs="?", help="Project name (optional if --current-dir)"
    )
    parser.add_argument(
        "--current-dir",
        action="store_true",
        help="Configure current directory instead of creating a new one",
    )

    args = parser.parse_args()

    if args.current_dir:
        project_path = Path.cwd()
        project_name = project_path.name
    elif args.project_name:
        project_name = args.project_name
        project_path = Path.cwd() / project_name
    else:
        project_name = input("Nom du projet Python: ").strip()
        if not project_name:
            print("❌ Nom de projet requis")
            return 1
        project_path = Path.cwd() / project_name

    # Confirmer avant de continuer
    if not args.current_dir:
        response = input(
            f"Créer le projet Python '{project_name}' dans {project_path}? (y/N): "
        )
        if response.lower() not in ("y", "yes", "o", "oui"):
            print("Annulé.")
            return 0

    setup = PythonProjectSetup(project_path, project_name)
    setup.setup_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())
