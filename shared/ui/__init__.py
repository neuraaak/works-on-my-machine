#!/usr/bin/env python3
"""
User Interface module using Rich for beautiful terminal output.
"""

# Import and expose common Rich utilities
from .console import (
    LogLevel,
    console,
    get_log_level,
    print_added,
    print_check,
    print_command,
    print_confirm,
    print_critical,
    print_debug,
    print_detect,
    print_error,
    print_eval,
    print_failed,
    print_fallback,
    # Patterns regroupés (Option A)
    print_file,  # Remplace COPY, BACKUP, RESTORE
    print_fix,
    print_header,
    print_hint,
    print_info,
    print_install,  # Remplace INSTALL, DICT
    print_interactive,
    print_ok,
    print_partial,
    print_path,
    # Fonction générique
    print_pattern,
    print_preview,
    print_process,
    print_result,
    # Patterns principaux
    print_run,
    # Patterns spécialisés
    print_security,
    print_separator,
    print_status,
    print_success,
    print_summary,
    print_system,  # Remplace BAT, EXEC, WINDOWS, REGISTER
    print_tip,
    print_unknown,
    print_warn,
    print_words,
    set_critical_level,
    set_debug_level,
    set_error_level,
    set_info_level,
    # Fonctions de configuration du niveau de logging
    set_log_level,
    set_warn_level,
)
from .panels import (
    create_error_panel,
    create_info_panel,
    create_installation_panel,
    create_panel,
    create_success_panel,
    create_warning_panel,
)
from .progress import (
    create_download_progress,
    create_progress,
    create_spinner,
    track_installation_steps,
)
from .prompts import (
    confirm,
    prompt_choice,
    prompt_path,
    prompt_text,
    show_error_panel,
    show_info_panel,
    show_warning_panel,
)
from .tables import (
    create_command_table,
    create_dependency_table,
    create_status_table,
    create_table,
)

__all__ = [
    "console",
    "LogLevel",
    "print_success",
    "print_error",
    "print_warn",
    "print_info",
    "print_debug",
    "print_critical",
    "create_table",
    "create_status_table",
    "create_panel",
    "create_info_panel",
    "create_progress",
    "confirm",
    "prompt_choice",
    # Fonctions de configuration du niveau de logging
    "set_log_level",
    "get_log_level",
    "set_debug_level",
    "set_info_level",
    "set_warn_level",
    "set_error_level",
    "set_critical_level",
]
