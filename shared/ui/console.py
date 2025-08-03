#!/usr/bin/env python3
"""
Console utilities using Rich for beautiful terminal output.
"""

from enum import Enum

from rich.console import Console
from rich.text import Text

# Global console instance
console = Console()

# Niveaux de logging avec couleurs
class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"

# Niveau minimum configurable (par défaut INFO)
_min_log_level = LogLevel.INFO

def set_log_level(level: LogLevel):
    """Configure le niveau minimum de logging"""
    global _min_log_level
    _min_log_level = level

def get_log_level() -> LogLevel:
    """Retourne le niveau minimum de logging actuel"""
    return _min_log_level

def _should_print(level: LogLevel) -> bool:
    """Vérifie si un niveau doit être affiché selon le niveau minimum configuré"""
    # Ordre des niveaux de criticité (du moins au plus critique)
    level_order = {
        LogLevel.DEBUG: 0,
        LogLevel.INFO: 1,
        LogLevel.WARN: 2,
        LogLevel.ERROR: 3,
        LogLevel.CRITICAL: 4
    }

    return level_order.get(level, 0) >= level_order.get(_min_log_level, 1)

# Couleurs pour les niveaux de logging
LEVEL_COLORS = {
    LogLevel.DEBUG: "dim white",
    LogLevel.INFO: "blue",
    LogLevel.WARN: "yellow",
    LogLevel.ERROR: "red",
    LogLevel.CRITICAL: "bright_red"
}

# Couleurs pour les patterns contextuels - Inspirées de Symfony Console
PATTERN_COLORS = {
    # === PATTERNS PRINCIPAUX (Actions/États) ===
    "RUNNING": "bright_blue",      # 🔵 Action en cours (comme Symfony "Processing")
    "SUCCESS": "bright_green",     # 🟢 Succès (comme Symfony "OK")
    "FAILED": "bright_red",        # 🔴 Échec (comme Symfony "ERROR")
    "OK": "green",                 # 🟢 Validation (comme Symfony "OK")
    "TIP": "bright_magenta",       # 🟣 Conseil/Astuce (comme Symfony "Comment")
    "HINT": "bright_cyan",         # 🔵 Indice/Suggestion

    # === PATTERNS SYSTÈME (Infrastructure) ===
    "SYSTEM": "bright_blue",       # 🔵 Opérations système
    "INSTALL": "bright_green",     # 🟢 Installation/Setup
    "PATH": "cyan",                # 🔵 Gestion des chemins
    "SECURITY": "bright_red",      # 🔴 Sécurité (attention requise)
    "DETECT": "bright_blue",       # 🔵 Détection/Analyse
    "PROCESS": "blue",             # 🔵 Traitement

    # === PATTERNS FICHIERS (I/O) ===
    "FILE": "bright_blue",         # 🔵 Opérations fichiers
    "PREVIEW": "cyan",             # 🔵 Aperçu/Preview
    "ADDED": "green",              # 🟢 Fichier ajouté
    "WORDS": "bright_blue",        # 🔵 Contenu textuel

    # === PATTERNS VALIDATION (Vérification) ===
    "CHECK": "bright_yellow",      # 🟡 Vérification en cours
    "FIX": "bright_green",         # 🟢 Correction appliquée
    "EVAL": "bright_magenta",      # 🟣 Évaluation/Analyse
    "STATUS": "cyan",              # 🔵 État/Statut

    # === PATTERNS INTERACTION (Utilisateur) ===
    "CONFIRM": "bright_yellow",    # 🟡 Demande de confirmation
    "INTERACTIVE": "bright_magenta", # 🟣 Mode interactif

    # === PATTERNS FALLBACK (Récupération) ===
    "FALLBACK": "bright_yellow",   # 🟡 Mode de secours
    "PARTIAL": "bright_yellow",    # 🟡 Résultat partiel
    "UNKNOWN": "bright_yellow",    # 🟡 État inconnu

    # === PATTERNS RÉSUMÉ (Résultats) ===
    "SUMMARY": "bright_cyan",      # 🔵 Résumé/Total
}

def print_pattern(level: LogLevel, pattern: str, message: str, **kwargs):
    """
    Affiche un message avec le nouveau format: [$level] | [<pattern_color>$pattern</pattern_color>] :: $message

    Args:
        level: Niveau de logging (DEBUG, INFO, WARN, ERROR, CRITICAL)
        pattern: Pattern contextuel (FILE, SYSTEM, INSTALL, etc.)
        message: Message à afficher
        **kwargs: Arguments passés à console.print()
    """
    # Vérifier si le niveau doit être affiché
    if not _should_print(level):
        return

    level_color = LEVEL_COLORS.get(level, "black")
    pattern_color = PATTERN_COLORS.get(pattern, "black")

    # Construction du texte avec couleur uniquement pour le pattern
    text = Text()
    text.append(f"[{level.value.upper()}]", style=level_color)
    text.append(":", style="black")
    text.append(f"[{pattern}]", style=pattern_color)
    text.append(" :: ", style="black")
    text.append(message, style="black")

    console.print(text, **kwargs)

# Fonctions de base avec niveau INFO par défaut
def print_info(pattern: str, message: str, **kwargs):
    """Affiche un message de niveau INFO"""
    print_pattern(LogLevel.INFO, pattern, message, **kwargs)

def print_warn(pattern: str, message: str, **kwargs):
    """Affiche un message de niveau WARN"""
    print_pattern(LogLevel.WARN, pattern, message, **kwargs)

def print_error(pattern: str, message: str, **kwargs):
    """Affiche un message de niveau ERROR"""
    print_pattern(LogLevel.ERROR, pattern, message, **kwargs)

def print_debug(pattern: str, message: str, **kwargs):
    """Affiche un message de niveau DEBUG"""
    print_pattern(LogLevel.DEBUG, pattern, message, **kwargs)

def print_critical(pattern: str, message: str, **kwargs):
    """Affiche un message de niveau CRITICAL"""
    print_pattern(LogLevel.CRITICAL, pattern, message, **kwargs)

# Fonctions spécialisées pour compatibilité (utilisent INFO par défaut)
def print_run(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [RUNNING] :: $message"""
    print_pattern(level, "RUNNING", message, **kwargs)

def print_success(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [SUCCESS] :: $message"""
    print_pattern(level, "SUCCESS", message, **kwargs)

def print_failed(message: str, level: LogLevel = LogLevel.ERROR, **kwargs):
    """Affiche un message [level] | [FAILED] :: $message"""
    print_pattern(level, "FAILED", message, **kwargs)

def print_ok(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [OK] :: $message"""
    print_pattern(level, "OK", message, **kwargs)

def print_tip(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [TIP] :: $message"""
    print_pattern(level, "TIP", message, **kwargs)

def print_hint(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [HINT] :: $message"""
    print_pattern(level, "HINT", message, **kwargs)

# Fonctions contextuelles (utilisent INFO par défaut)
def print_file(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [FILE] :: $message"""
    print_pattern(level, "FILE", message, **kwargs)

def print_system(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [SYSTEM] :: $message"""
    print_pattern(level, "SYSTEM", message, **kwargs)

def print_install(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [INSTALL] :: $message"""
    print_pattern(level, "INSTALL", message, **kwargs)

def print_path(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [PATH] :: $message"""
    print_pattern(level, "PATH", message, **kwargs)

def print_security(message: str, level: LogLevel = LogLevel.WARN, **kwargs):
    """Affiche un message [level] | [SECURITY] :: $message"""
    print_pattern(level, "SECURITY", message, **kwargs)

def print_fallback(message: str, level: LogLevel = LogLevel.WARN, **kwargs):
    """Affiche un message [level] | [FALLBACK] :: $message"""
    print_pattern(level, "FALLBACK", message, **kwargs)

def print_status(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [STATUS] :: $message"""
    print_pattern(level, "STATUS", message, **kwargs)

def print_detect(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [DETECT] :: $message"""
    print_pattern(level, "DETECT", message, **kwargs)

def print_unknown(message: str, level: LogLevel = LogLevel.WARN, **kwargs):
    """Affiche un message [level] | [UNKNOWN] :: $message"""
    print_pattern(level, "UNKNOWN", message, **kwargs)

def print_eval(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [EVAL] :: $message"""
    print_pattern(level, "EVAL", message, **kwargs)

def print_confirm(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [CONFIRM] :: $message"""
    print_pattern(level, "CONFIRM", message, **kwargs)

def print_process(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [PROCESS] :: $message"""
    print_pattern(level, "PROCESS", message, **kwargs)

def print_summary(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [SUMMARY] :: $message"""
    print_pattern(level, "SUMMARY", message, **kwargs)

def print_partial(message: str, level: LogLevel = LogLevel.WARN, **kwargs):
    """Affiche un message [level] | [PARTIAL] :: $message"""
    print_pattern(level, "PARTIAL", message, **kwargs)

def print_interactive(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [INTERACTIVE] :: $message"""
    print_pattern(level, "INTERACTIVE", message, **kwargs)

def print_preview(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [PREVIEW] :: $message"""
    print_pattern(level, "PREVIEW", message, **kwargs)

def print_added(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [ADDED] :: $message"""
    print_pattern(level, "ADDED", message, **kwargs)

def print_words(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [WORDS] :: $message"""
    print_pattern(level, "WORDS", message, **kwargs)

def print_check(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [CHECK] :: $message"""
    print_pattern(level, "CHECK", message, **kwargs)

def print_fix(message: str, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche un message [level] | [FIX] :: $message"""
    print_pattern(level, "FIX", message, **kwargs)

# Fonctions utilitaires (inchangées)
def print_header(title: str, **kwargs):
    """Affiche un en-tête avec séparateurs"""
    console.print(f"{'=' * 80}", style="dim black", **kwargs)
    console.print(f"{' ' * (37 - len(title) // 2)} ** {title} ** {' ' * (37 - len(title) // 2)}", style="bold black", **kwargs)
    console.print(f"{'=' * 80}", style="dim black", **kwargs)
    print("\n")

def print_separator(**kwargs):
    """Affiche une ligne de séparation"""
    console.print("-" * 80, style="dim white", **kwargs)

def print_command(command: str, **kwargs):
    """Affiche une commande exécutée"""
    console.print(f"$ {command}", style="bold cyan", **kwargs)

def print_result(result: str, success: bool = True, **kwargs):
    """Affiche le résultat d'une opération"""
    style = "bold green" if success else "bold red"
    console.print(result, style=style, **kwargs)

# Fonctions utilitaires pour la configuration du niveau de logging
def set_debug_level():
    """Configure le niveau de logging à DEBUG (affiche tout)"""
    set_log_level(LogLevel.DEBUG)

def set_info_level():
    """Configure le niveau de logging à INFO (affiche INFO et plus critique)"""
    set_log_level(LogLevel.INFO)

def set_warn_level():
    """Configure le niveau de logging à WARN (affiche WARN et plus critique)"""
    set_log_level(LogLevel.WARN)

def set_error_level():
    """Configure le niveau de logging à ERROR (affiche ERROR et plus critique)"""
    set_log_level(LogLevel.ERROR)

def set_critical_level():
    """Configure le niveau de logging à CRITICAL (affiche seulement CRITICAL)"""
    set_log_level(LogLevel.CRITICAL)
