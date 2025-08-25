# Git Hooks

Ce projet utilise des hooks Git personnalisés pour automatiser les vérifications de qualité de code et la gestion des tags de version.

## Configuration

Les hooks Git sont configurés pour utiliser le dossier `.hooks` à la racine du projet :

```bash
git config core.hooksPath .hooks
```

## Hooks disponibles

### Pre-commit Hook

**Fichier :** `.hooks/pre-commit`

**Fonction :** Exécute les vérifications de qualité de code avant chaque commit.

**Actions :**
- Vérifie l'existence de `lint.py` et Python
- Exécute `python lint.py --check-only`
- Empêche le commit si des erreurs de linting sont détectées

**Messages d'aide :**
- Affiche les commandes pour corriger automatiquement les problèmes
- Fournit des instructions pour un output détaillé

### Post-commit Hook

**Fichier :** `.hooks/post-commit`

**Fonction :** Gère automatiquement les tags de version après chaque commit.

**Actions :**
- Lit la version depuis `pyproject.toml` (ou `setup.py` en fallback)
- Crée un tag de version exacte (`v{version}`)
- Crée un tag de version majeure (`v{major}-latest`)
- Déplace les tags existants si nécessaire
- Pousse les tags vers le remote

## Système de Tags Automatiques

### Tags de Version Exacte

Format : `v{version}`

Exemples :
- `v2.6.1`
- `v3.1.0`
- `v1.0.0`

**Comportement :**
- Créé automatiquement après chaque commit
- Si le tag existe déjà, il est déplacé vers le nouveau commit
- Permet de retrouver facilement le commit exact d'une version

### Tags de Version Majeure

Format : `v{major}-latest`

Exemples :
- `v2-latest`
- `v3-latest`
- `v1-latest`

**Comportement :**
- Créé automatiquement après chaque commit
- Toujours déplacé vers le dernier commit de la version majeure
- Permet de retrouver facilement le dernier commit d'une version majeure

## Exemples d'Utilisation

### Scénario 1 : Nouvelle Version

```bash
# Version actuelle : 2.6.1
git commit -m "feat: new feature"
# Résultat :
# - Tag v2.6.1 créé sur le commit
# - Tag v2-latest déplacé sur le commit
```

### Scénario 2 : Fix sans Changement de Version

```bash
# Version reste 2.6.1
git commit -m "fix: bug correction"
# Résultat :
# - Tag v2.6.1 déplacé sur le nouveau commit
# - Tag v2-latest déplacé sur le nouveau commit
```

### Scénario 3 : Nouvelle Version Majeure

```bash
# Version passe à 3.1.0
git commit -m "feat: major update"
# Résultat :
# - Tag v3.1.0 créé sur le commit
# - Tag v3-latest créé sur le commit
# - Tag v2-latest reste sur le dernier commit v2.x
```

## Compatibilité Multi-Plateforme

Le système détecte automatiquement la plateforme :

- **Windows :** Utilise PowerShell si disponible, sinon Bash
- **Unix/Linux/macOS :** Utilise Bash

### Fichiers de Scripts

#### Pre-commit Hooks
- `.hooks/pre-commit` : Script principal de détection de plateforme
- `.hooks/pre-commit.ps1` : Version PowerShell
- `.hooks/pre-commit.sh` : Version Bash

#### Post-commit Hooks
- `.hooks/post-commit` : Script principal de détection de plateforme
- `.hooks/post-commit.ps1` : Version PowerShell
- `.hooks/post-commit.sh` : Version Bash

## Gestion des Erreurs

### Pre-commit Hook

- **Erreur de linting :** Commit bloqué avec instructions de correction
- **Python manquant :** Commit bloqué
- **lint.py manquant :** Commit bloqué

### Post-commit Hook

- **Version introuvable :** Erreur affichée, pas de tag créé
- **Git non disponible :** Erreur affichée
- **Échec de push :** Avertissement affiché

## Personnalisation

### Désactiver Temporairement

```bash
# Désactiver pre-commit
git commit --no-verify -m "message"

# Désactiver post-commit
# Le hook s'exécute automatiquement, pas d'option pour le désactiver
```

### Modifier les Exclusions de Linting

Éditer `lint.py` pour modifier les dossiers exclus :

```python
exclude_dirs = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "*.egg-info",
    ".venv",
    "venv",
    "node_modules",
    ".hooks",  # Exclut les hooks Git
}
```

### Modifier le Format des Tags

Éditer les scripts dans `.hooks/` pour changer le format des tags :

- **Version exacte :** Modifier la variable `$versionTag`
- **Version majeure :** Modifier la variable `$majorTag`

## Dépannage

### Problèmes Courants

1. **Hooks non exécutés :**
   ```bash
   git config core.hooksPath .hooks
   ```

2. **Permissions refusées :**
   ```bash
   chmod +x .hooks/*
   ```

3. **Tags non créés :**
   - Vérifier que la version est dans `pyproject.toml`
   - Vérifier que Git est configuré avec un remote

4. **Erreurs PowerShell :**
   - Vérifier que PowerShell est installé
   - Vérifier les permissions d'exécution

### Logs et Debug

Les hooks affichent des messages détaillés avec des emojis pour faciliter le suivi :

- 🔍 : Début des vérifications
- 🔧 : Exécution d'un outil
- ✅ : Succès
- ❌ : Erreur
- ⚠️ : Avertissement
- 🔄 : Action en cours
- 📤 : Push vers remote
- 🏷️ : Gestion des tags
