#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SECURITY PATTERNS CONFIG - Security & File Scanner Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Centralized security and file scanning configuration for Works On My Machine.

This config module exposes constants used by security and file scanning utilities:
- File scanner patterns (extensions, excluded directories)
- Security-sensitive patterns
- Dangerous commands and arguments
- Whitelisted commands
- Permission validation patterns
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# FILE SCANNER CONFIG CLASS
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class FileScannerConfig:
    """File scanner-related configuration (static, read-only).

    Contains patterns for file scanning operations:
    - File extensions to scan
    - Directories to exclude
    - Security-sensitive file patterns
    """

    # ///////////////////////////////////////////////////////////
    # PYTHON FILE EXTENSIONS
    # ///////////////////////////////////////////////////////////

    PYTHON_EXTENSIONS: ClassVar[set[str]] = {".py", ".pyi"}

    # ///////////////////////////////////////////////////////////
    # EXCLUDED DIRECTORIES
    # ///////////////////////////////////////////////////////////

    EXCLUDED_DIRS: ClassVar[set[str]] = {
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        ".venv",
        "venv",
        "env",
        ".env",
        "build",
        "dist",
        "*.egg-info",
    }

    # ///////////////////////////////////////////////////////////
    # SECURITY-SENSITIVE FILE PATTERNS
    # ///////////////////////////////////////////////////////////

    SECURITY_SENSITIVE_PATTERNS: ClassVar[list[str]] = [
        "password",
        "secret",
        "key",
        "credential",
        "token",
    ]


# ///////////////////////////////////////////////////////////////
# SECURITY PATTERNS CONFIG CLASS
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class SecurityPatternsConfig:
    """Security-related pattern configuration (static, read-only).

    Contains patterns for security validation:
    - Dangerous commands and arguments
    - Dangerous file/path patterns
    - Allowed commands whitelist
    - Shell injection patterns
    - Permission validation patterns
    """

    # ///////////////////////////////////////////////////////////
    # DANGEROUS COMMAND PATTERNS
    # ///////////////////////////////////////////////////////////

    DANGEROUS_COMMANDS: ClassVar[dict[str, list[str]]] = {
        "rm": ["-rf", "--recursive", "--force"],
        "del": ["/s", "/q", "/f"],
        "format": ["c:", "d:", "/q", "/u"],
        "shutdown": ["/s", "/t", "0"],
        "taskkill": ["/f", "/im", "*"],
        "kill": ["-9", "-f"],
        "chmod": ["777", "000"],
        "chown": ["root:", "sudo:"],
    }

    # ///////////////////////////////////////////////////////////
    # DANGEROUS FILE PATTERNS
    # ///////////////////////////////////////////////////////////

    DANGEROUS_FILE_PATTERNS: ClassVar[list[str]] = [
        r"\.\./\.\./",  # Directory traversal
        r"~/.ssh/",  # SSH keys
        r"/etc/",  # System files
        r"/var/log/",  # Log files
        r"/proc/",  # Process files
        r"/sys/",  # System files
        r"C:\\Windows\\",  # Windows system files
        r"C:\\System32\\",  # Windows system files
    ]

    # ///////////////////////////////////////////////////////////
    # ALLOWED COMMANDS (WHITELIST)
    # ///////////////////////////////////////////////////////////

    ALLOWED_COMMANDS: ClassVar[set[str]] = {
        "python",
        "python3",
        "pip",
        "pip3",
        "node",
        "npm",
        "npx",
        "yarn",
        "git",
        "git-*",
        "ruff",
        "black",
        "isort",
        "mypy",
        "eslint",
        "prettier",
        "cspell",
        "spellcheck",
        "echo",
        "cat",
        "ls",
        "dir",
        "mkdir",
        "rmdir",
        "cp",
        "copy",
        "mv",
        "move",
        "grep",
        "find",
        "sort",
        "uniq",
        "head",
        "tail",
        "wc",
        "curl",
        "wget",
        "tar",
        "zip",
        "unzip",
        "chmod",
        "chown",  # With restrictions
    }

    # ///////////////////////////////////////////////////////////
    # DANGEROUS COMMAND REGEX PATTERNS
    # ///////////////////////////////////////////////////////////

    DANGEROUS_COMMAND_PATTERNS: ClassVar[list[str]] = [
        r"rm\s*-rf",  # Recursive force remove
        r"del\s*/[sqf]",  # Windows delete with dangerous flags
        r"format\s*[cd]:",  # Format drives
        r"shutdown\s*/s",  # Shutdown system
        r"taskkill\s*/f",  # Force kill processes
        r"kill\s*-[9f]",  # Force kill
        r"chmod\s*[07]{3}",  # Dangerous permissions
        r"chown\s*root:",  # Change to root
    ]

    # ///////////////////////////////////////////////////////////
    # SHELL INJECTION PATTERNS
    # ///////////////////////////////////////////////////////////

    SHELL_INJECTION_PATTERNS: ClassVar[list[str]] = [
        r"[;&|`$()]",  # Shell operators
        r"\.\./",  # Directory traversal
        r"~/.ssh/",  # SSH keys
        r"/etc/",  # System files
        r"C:\\Windows\\",  # Windows system files
    ]

    # ///////////////////////////////////////////////////////////
    # SYSTEM DIRECTORY PATHS
    # ///////////////////////////////////////////////////////////

    SYSTEM_DIRECTORIES: ClassVar[list[str]] = [
        "/",  # Root
        "/bin",
        "/sbin",
        "/usr/bin",
        "/usr/sbin",
        "/etc",
        "/var",
        "/proc",
        "/sys",
        "C:\\",
        "C:\\Windows",
        "C:\\System32",
    ]

    # ///////////////////////////////////////////////////////////
    # PERMISSION VALIDATION PATTERNS
    # ///////////////////////////////////////////////////////////

    # Chmod permission patterns
    CHMOD_ALLOWED_PATTERNS: ClassVar[list[str]] = [
        r"^[0-7]{3,4}$",  # Octal permissions
        r"^[ugoa]*[+-=][rwxXst]*$",  # Symbolic permissions
    ]

    # Chown owner patterns
    CHOWN_ALLOWED_PATTERNS: ClassVar[list[str]] = [
        r"^[a-zA-Z_][a-zA-Z0-9_]*$",  # Username
        r"^[a-zA-Z_][a-zA-Z0-9_]*:[a-zA-Z_][a-zA-Z0-9_]*$",  # user:group
    ]


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["FileScannerConfig", "SecurityPatternsConfig"]
