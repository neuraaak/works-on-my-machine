# Architecture des Exceptions - Projet WOMM

## 📋 **Vue d'Ensemble**

Le projet WOMM utilise un **système d'exceptions hiérarchisé et spécialisé** qui suit l'architecture des modules utilitaires (`@utils/`) pour assurer une **gestion d'erreurs cohérente** et **contextuelle**.

---

## 🏗️ **Structure de l'Architecture**

### **📁 Organisation des Exceptions**

```
womm/core/exceptions/
├── __init__.py                    # API publique centralisée
├── common_exceptions.py           # Exceptions communes
├── installation/                  # Exceptions d'installation
│   ├── __init__.py
│   ├── installation_exceptions.py
│   └── uninstallation_exceptions.py
├── system/                        # Exceptions système
│   ├── __init__.py
│   └── user_path_exceptions.py
├── spell/                         # Exceptions de spell checking
│   ├── __init__.py
│   └── spell_exceptions.py
├── project/                       # Exceptions de gestion de projets
│   ├── __init__.py
│   └── project_exceptions.py
├── lint/                          # Exceptions de linting
│   ├── __init__.py
│   └── lint_exceptions.py
├── security/                      # Exceptions de sécurité
│   ├── __init__.py
│   └── security_exceptions.py
├── cli/                           # Exceptions CLI
│   ├── __init__.py
│   └── cli_exceptions.py
└── file/                          # Exceptions de file scanning
    ├── __init__.py
    └── file_exceptions.py
```

---

## 🎯 **Principes de Design**

### **✅ Hiérarchie Logique**

- **Exceptions de base** pour chaque domaine
- **Exceptions spécialisées** pour des cas spécifiques
- **Héritage cohérent** et **contextualisé**

### **✅ Correspondance avec Utils**

- **Structure miroir** de `womm/core/utils/`
- **Exceptions spécialisées** par module utilitaire
- **Cohérence** entre utilitaires et exceptions

### **✅ Séparation des Responsabilités**

- **Exceptions utilitaires** : Erreurs de fonctions utilitaires
- **Exceptions de managers** : Erreurs de gestion de processus
- **Exceptions spécialisées** : Erreurs spécifiques au domaine

---

## 📊 **Types d'Exceptions par Domaine**

### **🔧 Installation (9 exceptions)**

```python
# Utilitaires
InstallationUtilityError
FileVerificationError
PathUtilityError
ExecutableVerificationError

# Managers
InstallationManagerError
InstallationFileError
InstallationPathError
InstallationVerificationError
InstallationSystemError
```

### **🗂️ Uninstallation (8 exceptions)**

```python
# Utilitaires
UninstallationUtilityError
FileScanError
DirectoryAccessError
UninstallationVerificationError

# Managers
UninstallationManagerError
UninstallationFileError
UninstallationPathError
UninstallationManagerVerificationError
```

### **💻 Système (3 exceptions)**

```python
UserPathError
RegistryError
FileSystemError
```

### **🔍 Spell Checking (5 exceptions)**

```python
# Utilitaires
SpellUtilityError
CSpellError
DictionaryError

# Managers
SpellManagerError
SpellValidationError
```

### **📁 Project Management (6 exceptions)**

```python
# Utilitaires
ProjectUtilityError
ProjectDetectionError
ProjectValidationError
TemplateError
VSCodeConfigError

# Managers
ProjectManagerError
```

### **🔧 Linting (5 exceptions)**

```python
# Utilitaires
LintUtilityError
ToolExecutionError
ToolAvailabilityError

# Managers
LintManagerError
LintValidationError
```

### **🛡️ Security (5 exceptions)**

```python
SecurityUtilityError
ValidationError
CommandValidationError
PathValidationError
FileValidationError
```

### **💻 CLI (4 exceptions)**

```python
CLIUtilityError
CommandExecutionError
CommandValidationError
TimeoutError
```

### **📄 File Scanning (4 exceptions)**

```python
FileUtilityError
FileScanError
FileAccessError
SecurityFilterError
```

### **🔧 Common (5 exceptions)**

```python
CommonUtilityError
ImportUtilityError
PathResolutionError
SecurityError
CommandExecutionError
```

---

## 🎯 **Patterns d'Utilisation**

### **✅ Import Centralisé**

```python
from womm.core.exceptions import (
    InstallationUtilityError,
    SpellUtilityError,
    ProjectValidationError,
    # ... autres exceptions selon le besoin
)
```

### **✅ Gestion Contextuelle**

```python
try:
    # Opération spécifique
    result = some_operation()
except SpellUtilityError as e:
    # Gestion spécifique aux erreurs de spell checking
    logger.error(f"Spell error: {e.message}")
    # Logique de récupération spécifique
except ProjectValidationError as e:
    # Gestion spécifique aux erreurs de validation de projet
    logger.error(f"Project validation error: {e.message}")
    # Logique de récupération spécifique
```

### **✅ Intégration avec le Système de Logging UI**

```python
from womm.core.exceptions import SpellUtilityError
from womm.core.ui.common.console import print_error

try:
    # Opération de spell checking
    spell_result = run_spellcheck(file_path)
except SpellUtilityError as e:
    print_error(f"Spell checking failed: {e.message}")
    if e.details:
        print_debug(f"Details: {e.details}")
```

---

## 🔧 **Avantages de cette Architecture**

### **✅ Cohérence**

- **Structure miroir** avec les utilitaires
- **Naming convention** cohérente
- **Patterns d'utilisation** standardisés

### **✅ Maintenabilité**

- **Exceptions spécialisées** par domaine
- **Séparation claire** des responsabilités
- **Documentation intégrée** dans chaque exception

### **✅ Extensibilité**

- **Ajout facile** de nouvelles exceptions
- **Structure modulaire** et **évolutive**
- **Intégration simple** avec de nouveaux modules

### **✅ Debugging**

- **Messages d'erreur** contextuels et informatifs
- **Détails techniques** pour le debugging
- **Traçabilité** des erreurs par domaine

---

## 🚀 **Utilisation Recommandée**

### **📋 Pour les Développeurs**

1. **Identifier le domaine** de l'opération
2. **Importer les exceptions** appropriées
3. **Utiliser des exceptions spécialisées** plutôt que génériques
4. **Fournir des messages contextuels** et des détails techniques
5. **Intégrer avec le système de logging UI** pour une UX cohérente

### **📋 Pour les Managers**

1. **Utiliser les exceptions de managers** pour les erreurs de processus
2. **Propager les exceptions utilitaires** avec du contexte
3. **Gérer les erreurs** de manière appropriée selon le contexte
4. **Logger les erreurs** avec le système UI

---

## 🎯 **Conclusion**

Cette architecture d'exceptions **complète et cohérente** assure une **gestion d'erreurs robuste** et **contextuelle** dans le projet WOMM, facilitant le **développement**, la **maintenance** et le **debugging** tout en offrant une **expérience utilisateur optimale**.
