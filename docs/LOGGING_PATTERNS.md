# Patterns de Logging Normalisés

## Design définitif

Tous les patterns de logging utilisent le format : `[<color>$pattern</color>] :: $message`

## Patterns principaux (conservés)

| Pattern | Couleur | Usage | Exemple |
|---------|---------|-------|---------|
| `[RUN]` | cyan | Exécution de commandes | `[RUN] :: Installing dependencies...` |
| `[ERROR]` | red | Erreurs critiques | `[ERROR] :: File not found` |
| `[WARN]` | yellow | Avertissements | `[WARN] :: Directory already exists` |
| `[INFO]` | blue | Informations générales | `[INFO] :: Current location: /path` |
| `[OK]` | green | Succès simple | `[OK] :: File copied successfully` |
| `[SUCCESS]` | bright_green | Succès majeur | `[SUCCESS] :: Installation complete!` |
| `[FAILED]` | bright_red | Échec d'opération | `[FAILED] :: Installation failed` |
| `[TIP]` | magenta | Conseils généraux | `[TIP] :: Add .txt files with one word per line` |
| `[HINT]` | cyan | Indices spécifiques | `[HINT] :: Try running with administrator privileges` |

## Patterns regroupés (Option A)

### `[FILE]` (remplace `[COPY]`, `[BACKUP]`, `[RESTORE]`)
- **Couleur** : blue
- **Usage** : Opérations de fichiers
- **Exemples** :
  - `[FILE] :: Copying from: /source`
  - `[FILE] :: Backing up old version to: /backup`
  - `[FILE] :: Restoring PATH from backup...`

### `[SYSTEM]` (remplace `[BAT]`, `[EXEC]`, `[WINDOWS]`, `[REGISTER]`)
- **Couleur** : blue
- **Usage** : Opérations système Windows
- **Exemples** :
  - `[SYSTEM] :: Created main womm.bat: /path`
  - `[SYSTEM] :: Created Unix womm executable: /path`
  - `[SYSTEM] :: Adding to Windows context menu...`

### `[INSTALL]` (remplace `[INSTALL]`, `[DICT]`)
- **Couleur** : green
- **Usage** : Installation et configuration
- **Exemples** :
  - `[INSTALL] :: Installing CSpell and dictionaries...`
  - `[INSTALL] :: Installing dictionaries...`

## Patterns spécialisés (conservés)

| Pattern | Couleur | Usage | Exemple |
|---------|---------|-------|---------|
| `[SECURITY]` | red | Problèmes de sécurité | `[SECURITY] :: Command validation failed` |
| `[FALLBACK]` | yellow | Mode de repli | `[FALLBACK] :: Trying with npx...` |
| `[STATUS]` | cyan | Statut général | `[STATUS] :: CSPELL PROJECT STATUS` |
| `[DETECT]` | blue | Détection automatique | `[DETECT] :: Project type detected: python` |
| `[UNKNOWN]` | yellow | État inconnu | `[UNKNOWN] :: Project type not detected` |
| `[EVAL]` | magenta | Évaluation | `[EVAL] :: Will add 5 dictionaries to CSpell configuration` |
| `[CONFIRM]` | yellow | Demande de confirmation | `[CONFIRM] :: Continue? (y/N):` |
| `[PROCESS]` | blue | Traitement en cours | `[PROCESS] :: Adding dictionary: words.txt` |
| `[SUMMARY]` | cyan | Résumé | `[SUMMARY] :: Process completed: 3/5 dictionaries added` |
| `[PARTIAL]` | yellow | Résultat partiel | `[PARTIAL] :: Some dictionaries added successfully` |
| `[INTERACTIVE]` | magenta | Mode interactif | `[INTERACTIVE] :: Interactive word addition mode` |
| `[PREVIEW]` | blue | Aperçu | `[PREVIEW] :: Words to add: word1, word2, word3` |
| `[ADDED]` | green | Élément ajouté | `[ADDED] :: 'newword' added to list` |
| `[WORDS]` | blue | Mots/dictionnaire | `[WORDS] :: Custom words: 15` |
| `[CHECK]` | yellow | Vérification | `[CHECK] :: Checking: file.txt` |
| `[FIX]` | green | Correction | `[FIX] :: Interactive mode - Fixing: file.txt` |
| `[PATH]` | cyan | Configuration PATH | `[PATH] :: Setting up Windows USER PATH (safe mode)...` |

## Migration depuis l'ancien format

### Avant (ancien format)
```python
print("[COPY] Copying from: /source")
print("[BAT] Created main womm.bat: /path")
print("[ERROR] File not found")
```

### Après (nouveau format)
```python
from shared.ui.console import print_file, print_system, print_error

print_file("Copying from: /source")
print_system("Created main womm.bat: /path")
print_error("File not found")
```

## Utilisation

### Import des fonctions
```python
from shared.ui.console import (
    print_run, print_error, print_warning, print_info,
    print_file, print_system, print_install,
    print_security, print_fallback, print_status
)
```

### Utilisation directe
```python
print_run("Executing command...")
print_error("Something went wrong")
print_file("Copying files...")
```

### Fonction générique
```python
from shared.ui.console import print_pattern

print_pattern("CUSTOM", "Custom message")  # Pattern personnalisé
```

## Couleurs par catégorie

- **🔴 Rouge** : Erreurs critiques, sécurité
- **🟢 Vert** : Succès, installations, corrections
- **🟡 Jaune** : Avertissements, états intermédiaires, confirmations
- **🔵 Bleu** : Informations, opérations système, traitements
- **🟣 Magenta** : Conseils, interactions, évaluations
- **🔵 Cyan** : Actions actives, résumés, détection 