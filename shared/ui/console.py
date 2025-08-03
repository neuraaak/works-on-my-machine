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
        LogLevel.CRITICAL: 4,
    }

    return level_order.get(level, 0) >= level_order.get(_min_log_level, 1)


# Couleurs pour les niveaux de logging
LEVEL_COLORS = {
    LogLevel.DEBUG: "dim white",
    LogLevel.INFO: "blue",
    LogLevel.WARN: "yellow",
    LogLevel.ERROR: "red",
    LogLevel.CRITICAL: "bright_red",
}

# Couleurs pour les patterns contextuels - Inspirées de Symfony Console
PATTERN_COLORS = {
    # === PATTERNS PRINCIPAUX (Actions/États) ===
    "RUNNING": "bright_blue",  # 🔵 Action en cours (comme Symfony "Processing")
    "SUCCESS": "bright_green",  # 🟢 Succès (comme Symfony "OK")
    "FAILED": "bright_red",  # 🔴 Échec (comme Symfony "ERROR")
    "OK": "green",  # 🟢 Validation (comme Symfony "OK")
    "TIP": "bright_magenta",  # 🟣 Conseil/Astuce (comme Symfony "Comment")
    "HINT": "bright_cyan",  # 🔵 Indice/Suggestion
    # === PATTERNS SYSTÈME (Infrastructure) ===
    "SYSTEM": "bright_blue",  # 🔵 Opérations système
    "INSTALL": "bright_green",  # 🟢 Installation/Setup
    "PATH": "cyan",  # 🔵 Gestion des chemins
    "SECURITY": "bright_red",  # 🔴 Sécurité (attention requise)
    "DETECT": "bright_blue",  # 🔵 Détection/Analyse
    "PROCESS": "blue",  # 🔵 Traitement
    # === PATTERNS FICHIERS (I/O) ===
    "FILE": "bright_blue",  # 🔵 Opérations fichiers
    "PREVIEW": "cyan",  # 🔵 Aperçu/Preview
    "ADDED": "green",  # 🟢 Fichier ajouté
    "WORDS": "bright_blue",  # 🔵 Contenu textuel
    # === PATTERNS VALIDATION (Vérification) ===
    "CHECK": "bright_yellow",  # 🟡 Vérification en cours
    "FIX": "bright_green",  # 🟢 Correction appliquée
    "EVAL": "bright_magenta",  # 🟣 Évaluation/Analyse
    "STATUS": "cyan",  # 🔵 État/Statut
    # === PATTERNS INTERACTION (Utilisateur) ===
    "CONFIRM": "bright_yellow",  # 🟡 Demande de confirmation
    "INTERACTIVE": "bright_magenta",  # 🟣 Mode interactif
    # === PATTERNS FALLBACK (Récupération) ===
    "FALLBACK": "bright_yellow",  # 🟡 Mode de secours
    "PARTIAL": "bright_yellow",  # 🟡 Résultat partiel
    "UNKNOWN": "bright_yellow",  # 🟡 État inconnu
    # === PATTERNS RÉSUMÉ (Résultats) ===
    "SUMMARY": "bright_cyan",  # 🔵 Résumé/Total
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

    level_color = LEVEL_COLORS.get(level, "white")
    pattern_color = PATTERN_COLORS.get(pattern, "white")

    # Construction du texte avec couleur uniquement pour le pattern
    text = Text()
    text.append(f"[{level.value.upper()}]", style=level_color)
    text.append(":", style="dim white")
    text.append(f"[{pattern}]", style=pattern_color)
    text.append(" :: ", style="bold white")
    text.append(str(message), style="white")

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


# === NOUVELLES MÉTHODES UI SPÉCIALISÉES POUR LES RÉSULTATS ===


def print_dependency_check_result(result, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche le résultat d'une vérification de dépendances."""
    if result.all_available:
        print_success(
            f"All dependencies available: {', '.join(result.available)}",
            level,
            **kwargs,
        )
    else:
        print_warn(
            f"Missing dependencies: {', '.join(result.missing)}", level, **kwargs
        )
        if result.available:
            print_info(f"Available: {', '.join(result.available)}", level, **kwargs)


def print_installation_result(result, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche le résultat d'une installation de dépendances."""
    if result.success:
        if result.installed:
            print_success(f"Installed: {', '.join(result.installed)}", level, **kwargs)
        if result.skipped:
            print_info(f"Skipped: {', '.join(result.skipped)}", level, **kwargs)
        if result.installation_method:
            print_info(f"Method: {result.installation_method}", level, **kwargs)
    else:
        print_error(f"Installation failed: {result.error}", level, **kwargs)
        if result.failed:
            print_error(f"Failed: {', '.join(result.failed)}", level, **kwargs)


def print_setup_result(result, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche le résultat d'une configuration de projet."""
    if result.success:
        print_success(
            f"Project '{result.project_name}' setup completed", level, **kwargs
        )
        if result.project_path:
            print_path(f"Location: {result.project_path}", level, **kwargs)
        if result.files_created:
            print_file(f"Created {len(result.files_created)} files", level, **kwargs)
        if result.tools_configured:
            print_install(
                f"Configured: {', '.join(result.tools_configured)}", level, **kwargs
            )
        if result.warnings:
            for warning in result.warnings:
                print_warn(warning, level, **kwargs)
    else:
        print_error(f"Setup failed: {result.error}", level, **kwargs)


def print_validation_result(result, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche le résultat d'une validation."""
    if result.success:
        print_ok(f"Validation passed for {result.input_type}", level, **kwargs)
    else:
        print_error(
            f"Validation failed for {result.input_type}: {str(result.error)}",
            level,
            **kwargs,
        )


def print_security_result(result, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche le résultat d'une validation de sécurité."""
    if result.success:
        print_security(
            f"Security validation passed (level: {result.security_level})",
            level,
            **kwargs,
        )
    else:
        print_security(f"Security validation failed: {result.error}", level, **kwargs)
        if result.threats_detected:
            for threat in result.threats_detected:
                print_security(f"Threat: {threat}", level, **kwargs)
        if result.recommendations:
            for rec in result.recommendations:
                print_tip(f"Recommendation: {rec}", level, **kwargs)


def print_project_detection_result(result, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche le résultat d'une détection de projet."""
    if result.success:
        print_detect(
            f"Detected project type: {result.project_type} (confidence: {result.confidence:.1%})",
            level,
            **kwargs,
        )
        if result.detected_files:
            print_file(
                f"Detected files: {', '.join(result.detected_files)}", level, **kwargs
            )
    else:
        print_error(f"Project detection failed: {result.error}", level, **kwargs)


def print_file_operation_result(result, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche le résultat d'une opération sur fichier."""
    if result.success:
        print_file(
            f"{result.operation} completed in {result.operation_time:.2f}s",
            level,
            **kwargs,
        )
        if result.destination_path:
            print_path(f"Destination: {result.destination_path}", level, **kwargs)
    else:
        print_error(f"File operation failed: {result.error}", level, **kwargs)


def print_command_execution_result(result, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche le résultat d'une exécution de commande."""
    if result.success:
        print_success(
            f"Command executed successfully in {result.execution_time:.2f}s",
            level,
            **kwargs,
        )
        if result.security_validated:
            print_security("Command was security validated", level, **kwargs)
    else:
        print_error(f"Command execution failed: {result.error}", level, **kwargs)
        if result.stderr:
            print_error(f"Error output: {result.stderr}", level, **kwargs)


def print_configuration_result(result, level: LogLevel = LogLevel.INFO, **kwargs):
    """Affiche le résultat d'une configuration."""
    if result.success:
        print_install(f"{result.config_type} configuration completed", level, **kwargs)
        if result.config_files:
            print_file(
                f"Config files: {', '.join(result.config_files)}", level, **kwargs
            )
    else:
        print_error(f"Configuration failed: {result.error}", level, **kwargs)


# === MÉTHODES UTILITAIRES POUR LES ÉTAPES DE PROCESSUS ===


def print_process_step(
    step_name: str, description: str = "", level: LogLevel = LogLevel.INFO, **kwargs
):
    """Affiche une étape de processus."""
    message = f"Step: {step_name}"
    if description:
        message += f" - {description}"
    print_process(message, level, **kwargs)


def print_process_success(
    step_name: str, details: str = "", level: LogLevel = LogLevel.INFO, **kwargs
):
    """Affiche le succès d'une étape de processus."""
    message = f"Step '{step_name}' completed"
    if details:
        message += f" - {details}"
    print_success(message, level, **kwargs)


def print_process_error(
    step_name: str, error: str = "", level: LogLevel = LogLevel.ERROR, **kwargs
):
    """Affiche l'erreur d'une étape de processus."""
    message = f"Step '{step_name}' failed"
    if error:
        message += f" - {error}"
    print_error(message, level, **kwargs)


def print_process_warning(
    step_name: str, warning: str = "", level: LogLevel = LogLevel.WARN, **kwargs
):
    """Affiche un avertissement d'une étape de processus."""
    message = f"Step '{step_name}' warning"
    if warning:
        message += f" - {warning}"
    print_warn(message, level, **kwargs)


# === MÉTHODES SPÉCIALISÉES POUR LES COMMANDES NEW ===


def print_new_project_start(
    project_type: str, project_name: str, level: LogLevel = LogLevel.INFO, **kwargs
):
    """Affiche le début de création d'un nouveau projet."""
    print_header(f"Creating new {project_type} project: {project_name}")
    print_process(f"Starting {project_type} project setup", level, **kwargs)


def print_new_project_progress(
    step: str, details: str = "", level: LogLevel = LogLevel.INFO, **kwargs
):
    """Affiche le progrès de création d'un projet."""
    print_process_step(step, details, level, **kwargs)


def print_new_project_complete(
    project_type: str,
    project_name: str,
    project_path: str,
    level: LogLevel = LogLevel.INFO,
    **kwargs,
):
    """Affiche la completion de création d'un projet."""
    print_success(
        f"{project_type} project '{project_name}' created successfully!",
        level,
        **kwargs,
    )
    print_path(f"Project location: {project_path}", level, **kwargs)
    print_tip(
        "Next steps: cd into the project directory and start coding!", level, **kwargs
    )


def print_new_project_error(
    project_type: str,
    project_name: str,
    error: str,
    level: LogLevel = LogLevel.ERROR,
    **kwargs,
):
    """Affiche l'erreur de création d'un projet."""
    print_error(
        f"Failed to create {project_type} project '{project_name}'", level, **kwargs
    )
    print_error(f"Error: {error}", level, **kwargs)


# === FONCTIONS UTILITAIRES (inchangées) ===


def print_header(title: str, **kwargs):
    """Affiche un en-tête avec séparateurs"""
    console.print(f"{'=' * 80}", style="dim black", **kwargs)
    console.print(
        f"{' ' * (37 - len(title) // 2)} ** {title} ** {' ' * (37 - len(title) // 2)}",
        style="bold black",
        **kwargs,
    )
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


# === FONCTIONS UTILITAIRES POUR LA CONFIGURATION DU NIVEAU DE LOGGING ===


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
