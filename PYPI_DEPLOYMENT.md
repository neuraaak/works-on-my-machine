# 🚀 Guide de Déploiement PyPI

Ce guide explique comment déployer le projet "Works On My Machine" sur PyPI pour permettre l'installation via `pip install womm`.

## 📋 Prérequis

1. **Compte PyPI** : Créer un compte sur [PyPI](https://pypi.org/account/register/)
2. **Compte TestPyPI** : Créer un compte sur [TestPyPI](https://test.pypi.org/account/register/) pour les tests
3. **Outils de build** : Installer les outils nécessaires

```bash
pip install build twine
```

## 🔧 Configuration Actuelle

Le projet est configuré pour PyPI avec :

### ✅ Points d'Entrée CLI
- **Script principal** : `womm = "womm.cli:main"`
- **Fonction main()** : Ajoutée dans `womm/cli.py`
- **Imports compatibles** : Gestion des imports pour développement et PyPI

### ✅ Structure du Package
- **Modules inclus** : `shared`, `languages`, `womm`
- **Fichiers de données** : Templates, configs, scripts
- **MANIFEST.in** : Configuration des fichiers inclus

### ✅ Gestion des Imports
- **Module imports** : `womm/utils/imports.py` pour la compatibilité
- **Path manager** : Gestion des chemins pour PyPI et développement
- **Fallbacks** : Gestion des cas d'échec d'import

## 🧪 Tests de Compatibilité

### Test Local
```bash
python test_install.py
```

### Test de Build
```bash
python -m build
```

## 📦 Déploiement

### 1. Test sur TestPyPI

```bash
# Build du package
python -m build

# Upload sur TestPyPI
twine upload --repository testpypi dist/*

# Test d'installation
pip install --index-url https://test.pypi.org/simple/ womm
```

### 2. Déploiement sur PyPI

```bash
# Build du package
python -m build

# Upload sur PyPI
twine upload dist/*

# Test d'installation
pip install womm
```

## 🎯 Utilisation Après Installation

Une fois installé via PyPI, les utilisateurs pourront :

```bash
# Installation de WOMM
pip install womm

# Utilisation de la commande
womm --help
womm install
womm new python my-project
womm new javascript my-app
```

## 🔍 Vérifications Post-Déploiement

1. **Test d'installation** : `pip install womm`
2. **Test de commande** : `womm --help`
3. **Test de fonctionnalité** : `womm new python test-project`
4. **Test de désinstallation** : `pip uninstall womm`

## ⚠️ Points d'Attention

### Encodage
- ✅ Caractères Unicode remplacés par ASCII dans les commandes CLI
- ✅ Compatibilité Windows assurée

### Dépendances
- ✅ `click>=8.0.0` et `rich>=13.0.0` déclarées
- ✅ Python 3.8+ requis

### Structure
- ✅ Tous les modules nécessaires inclus
- ✅ Templates et configs préservés
- ✅ Scripts de setup fonctionnels

## 🚀 Prochaines Étapes

1. **Test sur TestPyPI** : Valider le déploiement
2. **Déploiement PyPI** : Publier la version stable
3. **Documentation** : Mettre à jour le README
4. **CI/CD** : Automatiser le déploiement

## 📝 Notes de Version

### Version 1.6.0
- ✅ Compatibilité PyPI complète
- ✅ Gestion des imports robuste
- ✅ Commandes CLI fonctionnelles
- ✅ Encodage Windows corrigé
- ✅ Structure de package optimisée 