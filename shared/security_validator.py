#!/usr/bin/env python3
"""
Security validation module for Works On My Machine CLI.
Provides comprehensive validation for all user inputs and system operations.
"""

import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Union
import platform


class SecurityValidator:
    """Security validation for CLI operations."""

    # Patterns dangereux à rejeter
    DANGEROUS_PATTERNS = [
        r'[;&|`$(){}[\]]',  # Caractères de commande shell
        r'\.\./',  # Path traversal
        r'\.\.\\',  # Path traversal Windows
        r'[<>]',  # Redirection
        r'\\x[0-9a-fA-F]{2}',  # Encoded characters
        r'%[0-9a-fA-F]{2}',  # URL encoding
    ]

    # Extensions de fichiers autorisées
    ALLOWED_EXTENSIONS = {
        '.py', '.pyw', '.js', '.jsx', '.ts', '.tsx', '.json', '.yaml', '.yml',
        '.md', '.txt', '.toml', '.ini', '.cfg', '.conf', '.bat', '.cmd', '.ps1',
        '.sh', '.bash', '.zsh', '.fish'
    }

    # Commandes autorisées
    ALLOWED_COMMANDS = {
        'python', 'python3', 'py', 'node', 'npm', 'npx', 'git', 'pip', 'pip3',
        'black', 'isort', 'flake8', 'pytest', 'pre-commit', 'cspell', 'eslint',
        'prettier', 'jest', 'husky', 'lint-staged'
    }

    def __init__(self):
        """Initialize security validator."""
        self.system = platform.system()
        self.max_path_length = 260 if self.system == "Windows" else 4096

    def validate_project_name(self, name: str) -> Tuple[bool, str]:
        """
        Validate project name for security.
        
        Args:
            name: Project name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "Project name cannot be empty"
        
        if len(name) > 50:
            return False, "Project name too long (max 50 characters)"
        
        # Vérifier les caractères dangereux
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, name):
                return False, f"Project name contains dangerous characters: {pattern}"
        
        # Vérifier les caractères autorisés
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return False, "Project name can only contain letters, numbers, underscores, and hyphens"
        
        # Vérifier les noms réservés
        reserved_names = {
            'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5',
            'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4',
            'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'
        }
        if name.lower() in reserved_names:
            return False, f"Project name '{name}' is reserved by the system"
        
        return True, ""

    def validate_path(self, path: Union[str, Path], must_exist: bool = False) -> Tuple[bool, str]:
        """
        Validate file or directory path.
        
        Args:
            path: Path to validate
            must_exist: Whether the path must exist
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path_obj = Path(path).resolve()
        except (OSError, RuntimeError) as e:
            return False, f"Invalid path: {e}"
        
        # Vérifier la longueur
        if len(str(path_obj)) > self.max_path_length:
            return False, f"Path too long (max {self.max_path_length} characters)"
        
        # Vérifier les caractères dangereux
        path_str = str(path_obj)
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, path_str):
                return False, f"Path contains dangerous characters: {pattern}"
        
        # Vérifier l'existence si demandé
        if must_exist and not path_obj.exists():
            return False, f"Path does not exist: {path_obj}"
        
        return True, ""

    def validate_command(self, command: Union[str, List[str]]) -> Tuple[bool, str]:
        """
        Validate command for security.
        
        Args:
            command: Command to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if isinstance(command, str):
            cmd_parts = command.split()
        else:
            cmd_parts = list(command)
        
        if not cmd_parts:
            return False, "Empty command"
        
        # Vérifier la commande principale
        main_cmd = cmd_parts[0].lower()
        if main_cmd not in self.ALLOWED_COMMANDS:
            return False, f"Command '{main_cmd}' is not allowed"
        
        # Vérifier les arguments
        for arg in cmd_parts[1:]:
            if not self._validate_argument(arg):
                return False, f"Invalid argument: {arg}"
        
        return True, ""

    def _validate_argument(self, arg: str) -> bool:
        """Validate command argument."""
        # Vérifier les caractères dangereux
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, arg):
                return False
        
        # Vérifier la longueur
        if len(arg) > 1000:
            return False
        
        return True

    def validate_file_operation(self, source: Path, destination: Path, operation: str) -> Tuple[bool, str]:
        """
        Validate file operation (copy, move, etc.).
        
        Args:
            source: Source path
            destination: Destination path
            operation: Operation type ('copy', 'move', 'delete')
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Valider les chemins
        for path, name in [(source, "source"), (destination, "destination")]:
            is_valid, error = self.validate_path(path, must_exist=(name == "source"))
            if not is_valid:
                return False, f"Invalid {name} path: {error}"
        
        # Vérifier les permissions
        if operation in ['copy', 'move']:
            if not os.access(source, os.R_OK):
                return False, f"Cannot read source: {source}"
            
            dest_parent = destination.parent
            if not os.access(dest_parent, os.W_OK):
                return False, f"Cannot write to destination directory: {dest_parent}"
        
        # Vérifier l'espace disque pour les copies
        if operation == 'copy' and source.is_file():
            try:
                free_space = shutil.disk_usage(destination.parent).free
                file_size = source.stat().st_size
                if file_size > free_space:
                    return False, f"Insufficient disk space for copy operation"
            except OSError:
                pass  # Ignorer les erreurs de stat
        
        return True, ""

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe use.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remplacer les caractères dangereux
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Supprimer les espaces en début/fin
        sanitized = sanitized.strip()
        
        # Limiter la longueur
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext
        
        return sanitized

    def validate_script_execution(self, script_path: Path) -> Tuple[bool, str]:
        """
        Validate script for execution.
        
        Args:
            script_path: Path to script
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Vérifier que le fichier existe
        if not script_path.exists():
            return False, f"Script does not exist: {script_path}"
        
        # Vérifier que c'est un fichier
        if not script_path.is_file():
            return False, f"Path is not a file: {script_path}"
        
        # Vérifier l'extension
        if script_path.suffix not in self.ALLOWED_EXTENSIONS:
            return False, f"File extension not allowed: {script_path.suffix}"
        
        # Vérifier les permissions de lecture
        if not os.access(script_path, os.R_OK):
            return False, f"Cannot read script: {script_path}"
        
        # Vérifier que le script est dans un répertoire autorisé
        allowed_dirs = [
            Path(__file__).parent.parent / "languages",
            Path(__file__).parent.parent / "shared",
            Path(__file__).parent.parent
        ]
        
        script_in_allowed_dir = any(
            script_path.is_relative_to(allowed_dir) for allowed_dir in allowed_dirs
        )
        
        if not script_in_allowed_dir:
            return False, f"Script not in allowed directory: {script_path}"
        
        return True, ""

    def validate_registry_operation(self, key_path: str, operation: str) -> Tuple[bool, str]:
        """
        Validate registry operation (Windows only).
        
        Args:
            key_path: Registry key path
            operation: Operation type ('read', 'write', 'delete')
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.system != "Windows":
            return False, "Registry operations only supported on Windows"
        
        # Vérifier le format de la clé
        if not re.match(r'^[A-Za-z0-9_\\]+$', key_path):
            return False, f"Invalid registry key format: {key_path}"
        
        # Vérifier les clés autorisées
        allowed_prefixes = [
            r'Software\\WorksOnMyMachine',
            r'Software\\Classes\\Directory\\Background\\shell',
            r'Software\\Classes\\Directory\\shell'
        ]
        
        key_allowed = any(
            re.match(prefix, key_path, re.IGNORECASE) for prefix in allowed_prefixes
        )
        
        if not key_allowed:
            return False, f"Registry key not allowed: {key_path}"
        
        return True, ""


# Instance globale pour utilisation simple
security_validator = SecurityValidator()


def validate_user_input(input_value: str, input_type: str) -> Tuple[bool, str]:
    """
    Validate user input based on type.
    
    Args:
        input_value: User input to validate
        input_type: Type of input ('project_name', 'path', 'command')
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if input_type == 'project_name':
        return security_validator.validate_project_name(input_value)
    elif input_type == 'path':
        return security_validator.validate_path(input_value)
    elif input_type == 'command':
        return security_validator.validate_command(input_value)
    else:
        return False, f"Unknown input type: {input_type}"


def safe_command_execution(command: List[str], description: str = "") -> Tuple[bool, str]:
    """
    Safely execute a command with validation.
    
    Args:
        command: Command to execute
        description: Description for logging
        
    Returns:
        Tuple of (success, error_message)
    """
    # Valider la commande
    is_valid, error = security_validator.validate_command(command)
    if not is_valid:
        return False, f"Command validation failed: {error}"
    
    # Exécuter avec le gestionnaire CLI sécurisé
    try:
        from shared.cli_manager import run_command
        result = run_command(command, description)
        return result.success, result.stderr if not result.success else ""
    except Exception as e:
        return False, f"Command execution failed: {e}"