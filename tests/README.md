# Tests pour Works On My Machine

Ce répertoire contient tous les tests pour le projet "Works On My Machine", organisés de manière structurée pour assurer la qualité et la fiabilité du code.

## 📁 Structure des tests

```
tests/
├── __init__.py                 # Package Python
├── conftest.py                 # Configuration pytest et fixtures partagées
├── unit/                       # Tests unitaires
│   ├── test_security_validator.py    # Tests du validateur de sécurité
│   ├── test_secure_cli_manager.py    # Tests du gestionnaire CLI sécurisé
│   └── test_wom_cli.py               # Tests du CLI principal
├── integration/                # Tests d'intégration
│   └── test_project_creation.py      # Tests de création de projets
├── fixtures/                   # Données de test
│   ├── sample_projects/        # Projets d'exemple
│   └── test_data/              # Données de test
└── mocks/                      # Mocks et stubs
    ├── mock_cli_manager.py     # Mock du gestionnaire CLI
    └── mock_system.py          # Mock des appels système
```

## 🧪 Types de tests

### Tests unitaires (`tests/unit/`)

Les tests unitaires vérifient le comportement de composants individuels en isolation :

- **`test_security_validator.py`** : Tests du validateur de sécurité
  - Validation des noms de projets
  - Validation des chemins de fichiers
  - Validation des commandes
  - Validation des opérations de fichiers
  - Validation des opérations de registre Windows

- **`test_secure_cli_manager.py`** : Tests du gestionnaire CLI sécurisé
  - Exécution de commandes sécurisées
  - Gestion des erreurs et timeouts
  - Logique de retry
  - Validation de sécurité
  - Mesure du temps d'exécution

- **`test_wom_cli.py`** : Tests du CLI principal
  - Commandes de création de projets
  - Commandes de linting
  - Commandes de vérification orthographique
  - Commandes système
  - Gestion des erreurs

### Tests d'intégration (`tests/integration/`)

Les tests d'intégration vérifient l'interaction entre plusieurs composants :

- **`test_project_creation.py`** : Tests de création de projets
  - Structure des projets Python
  - Structure des projets JavaScript
  - Configuration des projets
  - Intégration Git
  - Configuration VSCode
  - Workflows complets

## 🏷️ Marqueurs de tests

Les tests utilisent des marqueurs pytest pour la catégorisation :

- `@pytest.mark.unit` : Tests unitaires
- `@pytest.mark.integration` : Tests d'intégration
- `@pytest.mark.security` : Tests de sécurité
- `@pytest.mark.slow` : Tests lents
- `@pytest.mark.windows` : Tests spécifiques Windows
- `@pytest.mark.linux` : Tests spécifiques Linux
- `@pytest.mark.macos` : Tests spécifiques macOS

## 🚀 Exécution des tests

### Script de lancement

Utilisez le script `run_tests.py` à la racine du projet :

```bash
# Tous les tests
python run_tests.py

# Tests unitaires uniquement
python run_tests.py --unit

# Tests d'intégration uniquement
python run_tests.py --integration

# Tests de sécurité uniquement
python run_tests.py --security

# Tests avec couverture
python run_tests.py --coverage

# Tests rapides (sans tests lents)
python run_tests.py --fast

# Tests en parallèle
python run_tests.py --parallel

# Mode debug
python run_tests.py --debug

# Vérifier les dépendances
python run_tests.py --check-deps

# Afficher le résumé
python run_tests.py --summary

# Test spécifique
python run_tests.py tests/unit/test_security_validator.py
```

### Commandes pytest directes

```bash
# Tous les tests
pytest tests/

# Tests unitaires
pytest tests/unit/

# Tests d'intégration
pytest tests/integration/

# Tests avec marqueur spécifique
pytest -m security
pytest -m "not slow"

# Tests avec couverture
pytest --cov=shared --cov=languages --cov-report=html

# Tests en parallèle
pytest -n auto

# Tests avec plus de détails
pytest -v --tb=long
```

## 🔧 Configuration

### pytest.ini

Le fichier `pytest.ini` configure pytest avec :

- Répertoires de tests : `tests/`
- Marqueurs personnalisés
- Options par défaut (verbose, couleurs, etc.)
- Filtres d'avertissements

### conftest.py

Le fichier `conftest.py` définit :

- **Fixtures partagées** : Répertoires temporaires, projets d'exemple
- **Mocks globaux** : CLI manager, subprocess, système de fichiers
- **Configuration automatique** : Marqueurs automatiques selon le nom de fichier
- **Données de test** : Noms de projets, chemins, commandes

## 📊 Couverture de code

La couverture de code est mesurée pour :

- `shared/` : Modules partagés (sécurité, CLI, etc.)
- `languages/` : Modules spécifiques aux langages
- `wom_secure.py` : CLI principal sécurisé

Pour générer un rapport de couverture :

```bash
python run_tests.py --coverage
```

Le rapport HTML sera généré dans `htmlcov/`.

## 🛡️ Tests de sécurité

Les tests de sécurité vérifient :

1. **Validation des entrées** : Noms de projets, chemins, commandes
2. **Prévention d'injection** : Commandes dangereuses, caractères spéciaux
3. **Traversée de répertoires** : Chemins relatifs dangereux
4. **Opérations de fichiers** : Permissions, espace disque
5. **Exécution de scripts** : Validation des scripts avant exécution

## 🔄 Workflow de développement

### Ajouter un nouveau test

1. **Identifier le type** : unitaire ou intégration
2. **Choisir l'emplacement** : `tests/unit/` ou `tests/integration/`
3. **Nommer le fichier** : `test_<module>_<fonctionnalité>.py`
4. **Utiliser les fixtures** : Réutiliser les fixtures existantes
5. **Ajouter les marqueurs** : Marquer avec les marqueurs appropriés

### Exemple de test unitaire

```python
import pytest
from shared.security_validator import SecurityValidator

class TestSecurityValidator:
    """Tests pour le validateur de sécurité."""
    
    def test_validate_project_name_valid(self):
        """Test validation de nom de projet valide."""
        validator = SecurityValidator()
        is_valid, error = validator.validate_project_name("my-project")
        assert is_valid
        assert error == ""
    
    def test_validate_project_name_invalid(self):
        """Test validation de nom de projet invalide."""
        validator = SecurityValidator()
        is_valid, error = validator.validate_project_name("invalid;project")
        assert not is_valid
        assert "dangerous characters" in error
```

### Exemple de test d'intégration

```python
import pytest
from pathlib import Path

class TestProjectCreation:
    """Tests d'intégration pour la création de projets."""
    
    def test_create_python_project_structure(self, temp_dir):
        """Test que la création de projet Python génère la bonne structure."""
        project_name = "test-project"
        project_path = temp_dir / project_name
        
        # Simuler la création de projet
        project_path.mkdir()
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        
        # Vérifier la structure
        assert project_path.exists()
        assert (project_path / "src").exists()
        assert (project_path / "tests").exists()
```

## 🐛 Débogage des tests

### Mode debug

```bash
python run_tests.py --debug
```

### Tests spécifiques

```bash
# Test spécifique avec plus de détails
pytest tests/unit/test_security_validator.py::TestSecurityValidator::test_validate_project_name_valid -v -s

# Tests avec échec uniquement
pytest --lf

# Tests avec échec et dépendances
pytest --lf --ff
```

### Logs et traces

```bash
# Afficher les logs
pytest --log-cli-level=DEBUG

# Traceback complet
pytest --tb=long

# Arrêter au premier échec
pytest -x
```

## 📈 Métriques de qualité

### Couverture cible

- **Couverture globale** : ≥ 90%
- **Modules critiques** : ≥ 95% (sécurité, CLI)
- **Nouvelles fonctionnalités** : ≥ 95%

### Performance

- **Tests unitaires** : < 1 seconde par test
- **Tests d'intégration** : < 5 secondes par test
- **Suite complète** : < 30 secondes

### Fiabilité

- **Tests flaky** : 0%
- **Tests dépendants** : Éviter les dépendances entre tests
- **Isolation** : Chaque test doit être indépendant

## 🔍 Bonnes pratiques

### Écriture de tests

1. **Nommage clair** : Noms descriptifs pour les tests et classes
2. **Documentation** : Docstrings pour expliquer le but du test
3. **Arrange-Act-Assert** : Structure claire des tests
4. **Fixtures** : Réutiliser les fixtures existantes
5. **Mocks appropriés** : Mocker les dépendances externes

### Maintenance

1. **Tests à jour** : Maintenir les tests avec le code
2. **Refactoring** : Refactorer les tests quand nécessaire
3. **Performance** : Surveiller le temps d'exécution
4. **Couverture** : Maintenir une couverture élevée

### Intégration continue

1. **Exécution automatique** : Tests sur chaque commit
2. **Rapports** : Générer des rapports de couverture
3. **Seuils** : Définir des seuils de couverture
4. **Notifications** : Alerter en cas d'échec

## 🆘 Dépannage

### Problèmes courants

1. **Import errors** : Vérifier le PYTHONPATH
2. **Fixtures manquantes** : Vérifier conftest.py
3. **Tests lents** : Utiliser les marqueurs `@pytest.mark.slow`
4. **Tests flaky** : Ajouter des retries ou mocks

### Support

Pour les problèmes de tests :

1. Vérifier la documentation pytest
2. Consulter les exemples existants
3. Utiliser le mode debug
4. Vérifier les dépendances avec `--check-deps`