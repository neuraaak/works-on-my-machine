# TODO - Works On My Machine

## 🚀 Fonctionnalités à implémenter

### 📝 Spell Checking - Auto-correction

#### `womm spell fix` - Correction automatique des erreurs orthographiques

**Objectif** : Implémenter une commande de correction automatique des erreurs orthographiques détectées par CSpell.

**Fonctionnalités** :

1. **Mode interactif** : `womm spell fix [path]`
   - Détecte les erreurs avec `cspell lint`
   - Pour chaque erreur :
     - Affiche le contexte (ligne, fichier, mot)
     - Propose les suggestions via `cspell suggestions`
     - Interface utilisateur pour choisir l'action :
       - ✅ Accepter la suggestion
       - 📚 Ajouter au dictionnaire
       - 🙈 Ignorer (ajouter à la liste d'ignore)
       - ⏭️ Passer au suivant

2. **Mode automatique** : `womm spell fix --auto [path]`
   - Applique automatiquement la première suggestion
   - Ajoute les mots non corrigés au dictionnaire projet
   - Option `--backup` pour créer une sauvegarde avant modification

3. **Fonctionnalités avancées** :
   - **Backup automatique** : Sauvegarde des fichiers avant modification
   - **Prévisualisation** : Afficher les changements avant application
   - **Undo/Redo** : Possibilité d'annuler les corrections
   - **Batch processing** : Traitement de plusieurs fichiers
   - **Rapport détaillé** : Résumé des corrections appliquées

**Implémentation technique** :

```python
# Nouvelle commande dans womm/commands/spell.py
@spell_group.command("fix")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--auto", is_flag=True, help="Mode automatique")
@click.option("--backup", is_flag=True, help="Créer une sauvegarde")
@click.option("--preview", is_flag=True, help="Prévisualiser les changements")
def spell_fix(path, auto, backup, preview):
    """🔧 Corriger automatiquement les erreurs orthographiques."""
```

**Fichiers à modifier/créer** :
- `womm/commands/spell.py` : Ajouter la commande `fix`
- `womm/core/utils/spell_manager.py` : Implémenter `perform_spell_fix()`
- `womm/core/tools/cspell_utils.py` : Ajouter `get_spell_suggestions()`
- `womm/core/ui/interactive.py` : Interface utilisateur interactive
- `docs/diagrams/flow-spell.md` : Mettre à jour le diagramme

**Avantages** :
- ✅ Correction automatique des erreurs courantes
- ✅ Interface utilisateur intuitive
- ✅ Intégration parfaite avec l'écosystème WOMM
- ✅ Compatible avec les dictionnaires existants
- ✅ Sécurisé avec backup automatique

**Priorité** : 🔥 Haute - Améliore significativement l'expérience utilisateur

---

## 📋 Autres améliorations potentielles

### 🔍 Linting avancé
- Intégration avec d'autres outils de linting
- Règles personnalisables par projet

### 🎨 Interface utilisateur
- Mode sombre/clair
- Personnalisation des couleurs
- Barres de progression améliorées

### 🔧 Configuration
- Templates de configuration par langage
- Migration automatique des anciennes configs
