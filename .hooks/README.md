# Git Hooks

Ce dossier contient les hooks Git pour le projet WOMM.

## Hooks Disponibles

### `pre-commit`

- **Objectif** : Vérifications de qualité de code avant commit
- **Actions** :
  - Exécute `lint.py --check-only`
  - Bloque le commit si des erreurs sont détectées
  - Suggère d'exécuter `python lint.py --fix` pour corriger automatiquement

### `post-commit`

- **Objectif** : Actions après commit réussi
- **Actions** :
  - Affiche les informations du commit
  - Log le timestamp
  - Prêt pour extensions (notifications, CI/CD, etc.)

## Configuration

Pour activer ces hooks, configurez Git :

```bash
git config core.hooksPath .hooks
```

## Développement

### Ajouter un nouveau hook

1. Créez le fichier dans `.hooks/` (ex: `.hooks/pre-push`)
2. Rendez-le exécutable : `chmod +x .hooks/pre-push`
3. Documentez-le dans ce README

### Tests

Testez un hook manuellement :

```bash
# Test pre-commit
.hooks/pre-commit

# Test post-commit
.hooks/post-commit
```

## Extensions Futures

- `pre-push` : Tests avant push
- `commit-msg` : Validation du message de commit
- `post-merge` : Actions après merge
- `pre-rebase` : Vérifications avant rebase
