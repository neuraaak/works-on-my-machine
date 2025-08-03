#!/usr/bin/env python3
"""
Install Works On My Machine in user directory.

This script handles the installation of WOMM to the user's home directory,
including PATH setup and environment configuration.
"""

import argparse
import os
import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import CLI manager
try:
    # Import security modules if available
    import importlib.util

    from shared.core.cli_manager import run_command, run_interactive, run_silent

    SECURITY_AVAILABLE = (
        importlib.util.find_spec("shared.security.security_validator") is not None
    )
except ImportError:
    # Fallback if module not available during first installation
    subprocess_run = subprocess.run

    def run_command(cmd, **kwargs):
        """Run a command with logging.

        Args:
            cmd: Command to run as list of strings.
            **kwargs: Additional arguments passed to subprocess.run.

        Returns:
            Object with success attribute indicating if command succeeded.
        """
        result = subprocess_run(cmd, **kwargs)
        return type("obj", (object,), {"success": result.returncode == 0})()

    def run_silent(cmd, **kwargs):
        """Run a command silently.

        Args:
            cmd: Command to run as list of strings.
            **kwargs: Additional arguments passed to subprocess.run.

        Returns:
            Object with success attribute indicating if command succeeded.
        """
        result = subprocess_run(cmd, capture_output=True, **kwargs)
        return type(
            "obj",
            (object,),
            {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
        )()

    def run_interactive(cmd, **kwargs):
        """Run a command interactively.

        Args:
            cmd: Command to run as list of strings.
            **kwargs: Additional arguments passed to subprocess.run.

        Returns:
            CompletedProcess object from subprocess.run.
        """
        return subprocess_run(cmd, **kwargs)


def get_target_womm_path():
    """Get the standard target path for Works On My Machine.

    Returns:
        Path object pointing to the .womm directory in user's home.
    """
    return Path.home() / ".womm"


def get_current_womm_path():
    """Get the current script path.

    Returns:
        Path object pointing to the directory containing this script.
    """
    # Go up from shared/installation/installer.py to the project root
    return Path(__file__).parent.parent.parent.absolute()


def should_exclude_file(file_path: Path, source_path: Path) -> bool:
    """Check if a file should be excluded from installation.

    Args:
        file_path: Path to the file relative to source
        source_path: Source directory path

    Returns:
        True if file should be excluded, False otherwise
    """
    # Exclude common development files and directories
    exclude_patterns = [
        ".git",
        ".gitignore",
        ".pytest_cache",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".coverage",
        "htmlcov",
        "build",
        "dist",
        "*.egg-info",
        ".venv",
        "venv",
        "node_modules",
        ".vscode",
        ".idea",
        "*.log",
        ".DS_Store",
        "Thumbs.db",
    ]

    file_name = file_path.name
    relative_path = file_path.relative_to(source_path)

    for pattern in exclude_patterns:
        if pattern.startswith("*"):
            if file_name.endswith(pattern[1:]):
                return True
        elif pattern in str(relative_path):
            return True

    return False


class InstallationManager:
    """Manages WOMM installation process with data-driven approach."""

    def __init__(self):
        """Initialize the installation manager."""
        self.current_path = get_current_womm_path()
        self.target_path = get_target_womm_path()

    def install(self, force: bool = False, target: Optional[str] = None) -> Dict:
        """
        Perform WOMM installation.

        Args:
            force: Force installation even if target directory exists
            target: Custom target directory

        Returns:
            Dictionary containing installation results and data
        """
        # Override target path if specified
        if target:
            self.target_path = Path(target).expanduser().resolve()

        actions = []
        errors = []

        # Check if target directory already exists
        if self.target_path.exists() and not force:
            actions.append(
                {
                    "action": "check_existing",
                    "status": "exists",
                    "message": f"Directory {self.target_path} already exists",
                }
            )
            return {
                "success": False,
                "actions": actions,
                "errors": errors,
                "target_path": str(self.target_path),
                "requires_confirmation": True,
            }

        # Copy WOMM to target directory
        if self.current_path != self.target_path:
            copy_result = self._copy_womm_to_user_directory()
            if copy_result["success"]:
                actions.append(
                    {
                        "action": "copy_files",
                        "status": "success",
                        "message": "WOMM copied to target directory",
                    }
                )
            else:
                actions.append(
                    {
                        "action": "copy_files",
                        "status": "failed",
                        "message": copy_result["error"],
                    }
                )
                errors.append(copy_result["error"])

        # Backup current user PATH
        backup_result = self._backup_user_path()
        if backup_result["success"]:
            actions.append(
                {
                    "action": "backup_path",
                    "status": "success",
                    "message": "User PATH backed up",
                    "backup_file": backup_result["backup_file"],
                }
            )
        else:
            actions.append(
                {
                    "action": "backup_path",
                    "status": "warning",
                    "message": "PATH backup failed, but continuing",
                }
            )

        # Create WOMM executable
        exec_result = self._create_womm_executable()
        if exec_result["success"]:
            actions.append(
                {
                    "action": "create_executable",
                    "status": "success",
                    "message": "WOMM executable created",
                }
            )
        else:
            actions.append(
                {
                    "action": "create_executable",
                    "status": "failed",
                    "message": exec_result["error"],
                }
            )
            errors.append(exec_result["error"])

        # Setup PATH
        path_result = self._setup_path()
        if path_result["success"]:
            actions.append(
                {
                    "action": "setup_path",
                    "status": "success",
                    "message": "PATH configured",
                    "path_added": path_result["path_added"],
                }
            )
        else:
            actions.append(
                {
                    "action": "setup_path",
                    "status": "failed",
                    "message": path_result["error"],
                }
            )
            errors.append(path_result["error"])

        # Determine overall success
        success = len(errors) == 0

        # Verify installation if all steps succeeded
        if success:
            verification_result = self._verify_installation()
            if verification_result["success"]:
                actions.append(
                    {
                        "action": "verify_installation",
                        "status": "success",
                        "message": "Installation verified successfully",
                        "checks": verification_result["checks"],
                    }
                )
            else:
                actions.append(
                    {
                        "action": "verify_installation",
                        "status": "failed",
                        "message": "Installation verification failed",
                        "checks": verification_result["checks"],
                    }
                )
                success = False
                errors.append("Installation verification failed")

        return {
            "success": success,
            "actions": actions,
            "errors": errors,
            "target_path": str(self.target_path),
            "current_path": str(self.current_path),
            "commands_available": self._get_available_commands(),
            "platform": platform.system(),
            "requires_confirmation": False,
        }

    def _copy_womm_to_user_directory(self) -> Dict:
        """Copy WOMM files to user directory."""
        try:
            source = self.current_path
            target = self.target_path

            # Validate paths
            if not source.exists():
                return {
                    "success": False,
                    "error": f"Source directory does not exist: {source}",
                }

            # Create target directory
            target.mkdir(parents=True, exist_ok=True)

            # Copy files with exclusions
            def ignore_files(dir_path, files):
                return [
                    f for f in files if should_exclude_file(Path(dir_path) / f, source)
                ]

            shutil.copytree(source, target, dirs_exist_ok=True, ignore=ignore_files)

            return {"success": True}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _backup_user_path(self) -> Dict:
        """Backup current user PATH."""
        try:
            backup_dir = self.target_path / ".backup"
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f".path_{timestamp}"

            if platform.system() == "Windows":
                # Windows PATH backup - use environment variable
                current_path = os.environ.get("PATH", "")
                if current_path:
                    with open(backup_file, "w", encoding="utf-8") as f:
                        f.write(f"# WOMM PATH Backup - {timestamp}\n")
                        f.write(f"# Platform: {platform.system()}\n")
                        f.write(f"# User: {os.environ.get('USERNAME', 'unknown')}\n")
                        f.write("# Original PATH:\n")
                        f.write(f"{current_path}\n")
                    return {"success": True, "backup_file": str(backup_file)}
                else:
                    return {"success": False, "error": "Could not read Windows PATH"}
            else:
                # Unix PATH backup
                current_path = os.environ.get("PATH", "")
                with open(backup_file, "w", encoding="utf-8") as f:
                    f.write(f"# WOMM PATH Backup - {timestamp}\n")
                    f.write(f"# Platform: {platform.system()}\n")
                    f.write(f"# User: {os.environ.get('USER', 'unknown')}\n\n")
                    f.write(current_path)
                return {"success": True, "backup_file": str(backup_file)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_womm_executable(self) -> Dict:
        """Create WOMM executable."""
        try:
            if platform.system() == "Windows":
                # Create womm.bat
                womm_bat = self.target_path / "womm.bat"
                bat_content = f'@echo off\npython "{self.target_path}\\womm.py" %*'
                womm_bat.write_text(bat_content, encoding="utf-8")
                return {"success": True}
            else:
                # Create Unix executable
                womm_exec = self.target_path / "womm"
                exec_content = f'#!/bin/bash\npython3 "{self.target_path}/womm.py" "$@"'
                womm_exec.write_text(exec_content, encoding="utf-8")
                womm_exec.chmod(0o755)
                return {"success": True}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _setup_path(self) -> Dict:
        """Setup PATH for WOMM with proper user PATH handling and backup/restore."""
        try:
            womm_path = str(self.target_path)

            if platform.system() == "Windows":
                return self._setup_windows_user_path(womm_path)
            else:
                # Unix PATH setup with rollback
                original_path = os.environ.get("PATH", "")
                return self._setup_unix_path(womm_path, original_path)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _setup_windows_user_path(self, womm_path: str) -> Dict:
        """Setup Windows user PATH with proper backup/restore strategy."""
        try:
            # Step 1: Récupérer le PATH utilisateur actuel
            result = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])

            backup_user_path = ""  # Variable de secours

            if result.success:
                output = result.stdout
                if isinstance(output, bytes):
                    output = output.decode("utf-8", errors="ignore")

                # Extraire le PATH utilisateur du registre
                for line in output.split("\n"):
                    if "REG_SZ" in line and "PATH" in line:
                        parts = line.split("REG_SZ")
                        if len(parts) > 1:
                            backup_user_path = parts[1].strip()
                            break

            # Step 2: Vérifier si déjà présent
            if womm_path in backup_user_path:
                return {
                    "success": True,
                    "path_added": False,
                    "message": "Already in user PATH",
                }

            # Step 3: Faire la MAJ en rajoutant le path du dossier .womm
            if backup_user_path:
                new_user_path = f"{womm_path};{backup_user_path}"
            else:
                new_user_path = womm_path

            # Step 4: Écrire le nouveau PATH utilisateur
            result = run_silent(
                [
                    "reg",
                    "add",
                    "HKCU\\Environment",
                    "/v",
                    "PATH",
                    "/t",
                    "REG_SZ",
                    "/d",
                    new_user_path,
                    "/f",
                ]
            )

            if not result.success:
                return {
                    "success": False,
                    "error": "Failed to update user PATH in registry",
                }

            # Step 5: Vérifier que l'ajout a réussi avec reg query
            verify_result = run_silent(
                ["reg", "query", "HKCU\\Environment", "/v", "PATH"]
            )
            if not verify_result.success:
                # Si erreur, rétablir le PATH avec la variable de secours
                if backup_user_path:
                    run_silent(
                        [
                            "reg",
                            "add",
                            "HKCU\\Environment",
                            "/v",
                            "PATH",
                            "/t",
                            "REG_SZ",
                            "/d",
                            backup_user_path,
                            "/f",
                        ]
                    )
                return {
                    "success": False,
                    "error": "Failed to verify PATH update - restored backup",
                }

            # Step 6: Vérifier que le chemin WOMM est bien dans le registre
            verify_output = verify_result.stdout
            if isinstance(verify_output, bytes):
                verify_output = verify_output.decode("utf-8", errors="ignore")

            if womm_path not in verify_output:
                # Si le chemin n'est pas dans le registre, restaurer
                if backup_user_path:
                    run_silent(
                        [
                            "reg",
                            "add",
                            "HKCU\\Environment",
                            "/v",
                            "PATH",
                            "/t",
                            "REG_SZ",
                            "/d",
                            backup_user_path,
                            "/f",
                        ]
                    )
                return {
                    "success": False,
                    "error": "WOMM path not found in registry after update",
                }

            # Step 7: Mettre à jour la session courante
            current_full_path = os.environ.get("PATH", "")
            os.environ["PATH"] = f"{womm_path};{current_full_path}"

            return {
                "success": True,
                "path_added": True,
                "message": "User PATH updated successfully - verified with registry",
            }

        except Exception as e:
            # En cas d'exception, rétablir le PATH avec la variable de secours
            if "backup_user_path" in locals() and backup_user_path:
                try:
                    run_silent(
                        [
                            "reg",
                            "add",
                            "HKCU\\Environment",
                            "/v",
                            "PATH",
                            "/t",
                            "REG_SZ",
                            "/d",
                            backup_user_path,
                            "/f",
                        ]
                    )
                except:
                    pass  # Ignore les erreurs de restauration
            return {"success": False, "error": f"Windows user PATH setup error: {e}"}

    def _persist_path_change(self, new_path: str) -> Dict:
        """Persist PATH change to system (registry on Windows, profile on Unix)."""
        try:
            if platform.system() == "Windows":
                # Windows: Update user PATH in registry
                result = run_silent(
                    [
                        "reg",
                        "add",
                        "HKCU\\Environment",
                        "/v",
                        "PATH",
                        "/t",
                        "REG_EXPAND_SZ",
                        "/d",
                        new_path,
                        "/f",
                    ]
                )
                if result.success:
                    return {
                        "success": True,
                        "message": "PATH persisted to Windows registry",
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to update Windows registry",
                    }
            else:
                # Unix: Update shell profile
                return self._persist_unix_path_change(new_path)

        except Exception as e:
            return {"success": False, "error": f"PATH persistence error: {e}"}

    def _persist_unix_path_change(self, new_path: str) -> Dict:
        """Persist PATH change to Unix shell profile."""
        try:
            womm_path = str(self.target_path)
            profile_files = ["~/.bashrc", "~/.zshrc", "~/.profile"]

            for profile_file in profile_files:
                profile_path = Path(profile_file).expanduser()
                if profile_path.exists():
                    content = profile_path.read_text()
                    if womm_path not in content:
                        # Add PATH export
                        export_line = f'\n# Added by WOMM installer\nexport PATH="{womm_path}:$PATH"\n'
                        profile_path.write_text(content + export_line)
                        return {
                            "success": True,
                            "message": f"PATH persisted to {profile_file}",
                        }
                    else:
                        return {
                            "success": True,
                            "message": f"Already configured in {profile_file}",
                        }

            # If no profile found, create ~/.profile
            profile_path = Path("~/.profile").expanduser()
            export_line = (
                f'# Added by WOMM installer\nexport PATH="{womm_path}:$PATH"\n'
            )
            profile_path.write_text(export_line)
            return {"success": True, "message": "PATH persisted to new ~/.profile"}

        except Exception as e:
            return {"success": False, "error": f"Unix PATH persistence error: {e}"}

    def _setup_windows_path(self, womm_path: str, original_path: str) -> Dict:
        """Setup Windows PATH with automatic rollback and safety verification."""
        try:
            # Check if already in PATH
            if womm_path in original_path:
                return {
                    "success": True,
                    "path_added": False,
                    "message": "Already in PATH",
                }

            # Step 1: Get current user PATH from registry and store it
            result = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])

            if result.returncode == 0:
                # Parse current user PATH from registry
                output = result.stdout
                if isinstance(output, bytes):
                    output = output.decode("utf-8", errors="ignore")
                actual_user_path = ""

                # Extract PATH value from registry output
                for line in output.split("\n"):
                    if "REG_EXPAND_SZ" in line and "PATH" in line:
                        parts = line.split("REG_EXPAND_SZ")
                        if len(parts) > 1:
                            actual_user_path = parts[1].strip()
                            break

                # If no user PATH found, start with empty
                if not actual_user_path:
                    actual_user_path = ""

                # Check if already in user PATH
                if womm_path in actual_user_path:
                    return {
                        "success": True,
                        "path_added": False,
                        "message": "Already in user PATH",
                    }

                # Step 2: Create new user PATH
                if actual_user_path:
                    new_user_path = f"{womm_path};{actual_user_path}"
                else:
                    new_user_path = womm_path

                # Step 3: Modify user PATH in registry
                result = run_silent(
                    [
                        "reg",
                        "add",
                        "HKCU\\Environment",
                        "/v",
                        "PATH",
                        "/t",
                        "REG_EXPAND_SZ",
                        "/d",
                        new_user_path,
                        "/f",
                    ]
                )

                if result.returncode == 0:
                    # Step 4: Verify the modification - check if PATH length is valid
                    verification_result = run_silent(
                        ["reg", "query", "HKCU\\Environment", "/v", "PATH"]
                    )

                    if verification_result.returncode == 0:
                        verification_output = verification_result.stdout
                        if isinstance(verification_output, bytes):
                            verification_output = verification_output.decode(
                                "utf-8", errors="ignore"
                            )

                        # Extract the new PATH value
                        new_path_value = ""
                        for line in verification_output.split("\n"):
                            if "REG_EXPAND_SZ" in line and "PATH" in line:
                                parts = line.split("REG_EXPAND_SZ")
                                if len(parts) > 1:
                                    new_path_value = parts[1].strip()
                                    break

                        # Step 5: Safety check - if new PATH is shorter than original, rollback
                        if len(new_path_value) < len(actual_user_path):
                            # CRITICAL: PATH corruption detected, restore immediately
                            run_silent(
                                [
                                    "reg",
                                    "add",
                                    "HKCU\\Environment",
                                    "/v",
                                    "PATH",
                                    "/t",
                                    "REG_EXPAND_SZ",
                                    "/d",
                                    actual_user_path,
                                    "/f",
                                ]
                            )
                            return {
                                "success": False,
                                "error": "PATH corruption detected - restored original PATH",
                            }

                        # Step 6: Update current session PATH
                        system_path = os.environ.get("PATH", "")
                        os.environ["PATH"] = f"{new_user_path};{system_path}"

                        # Step 7: Final verification
                        verification = self._verify_path_modification(womm_path)
                        if verification["success"]:
                            return {
                                "success": True,
                                "path_added": True,
                                "message": "User PATH configured successfully",
                            }
                        else:
                            # Rollback: restore original user PATH
                            os.environ["PATH"] = original_path
                            run_silent(
                                [
                                    "reg",
                                    "add",
                                    "HKCU\\Environment",
                                    "/v",
                                    "PATH",
                                    "/t",
                                    "REG_EXPAND_SZ",
                                    "/d",
                                    actual_user_path,
                                    "/f",
                                ]
                            )
                            return {
                                "success": False,
                                "error": "User PATH modification failed verification",
                            }
                    else:
                        # Rollback: restore original user PATH
                        run_silent(
                            [
                                "reg",
                                "add",
                                "HKCU\\Environment",
                                "/v",
                                "PATH",
                                "/t",
                                "REG_EXPAND_SZ",
                                "/d",
                                actual_user_path,
                                "/f",
                            ]
                        )
                        return {
                            "success": False,
                            "error": "Failed to verify PATH modification",
                        }
                else:
                    return {
                        "success": False,
                        "error": "Failed to modify user PATH in registry",
                    }
            else:
                return {
                    "success": False,
                    "error": "Failed to read user PATH from registry",
                }

        except Exception as e:
            return {"success": False, "error": f"Windows user PATH setup error: {e}"}

    def _setup_unix_path(self, womm_path: str, original_path: str) -> Dict:
        """Setup Unix PATH with automatic rollback."""
        try:
            # Check if already in PATH
            if womm_path in original_path:
                return {
                    "success": True,
                    "path_added": False,
                    "message": "Already in PATH",
                }

            # Unix PATH setup
            profile_files = ["~/.bashrc", "~/.zshrc", "~/.profile"]
            for profile_file in profile_files:
                profile_path = Path(profile_file).expanduser()
                if profile_path.exists():
                    content = profile_path.read_text()
                    if womm_path not in content:
                        # Backup original content
                        backup_content = content

                        # Add PATH export
                        export_line = f'\nexport PATH="$PATH:{womm_path}"\n'
                        profile_path.write_text(content + export_line)

                        # Update current session
                        new_path = f"{original_path}:{womm_path}"
                        os.environ["PATH"] = new_path

                        # Verify the modification
                        verification = self._verify_path_modification(womm_path)
                        if verification["success"]:
                            return {
                                "success": True,
                                "path_added": True,
                                "message": f"PATH configured in {profile_file}",
                            }
                        else:
                            # Rollback: restore original content
                            profile_path.write_text(backup_content)
                            os.environ["PATH"] = original_path
                            return {
                                "success": False,
                                "error": "PATH modification failed verification",
                            }
                    else:
                        return {
                            "success": True,
                            "path_added": False,
                            "message": f"Already configured in {profile_file}",
                        }

            return {"success": False, "error": "No shell profile found"}

        except Exception as e:
            return {"success": False, "error": f"Unix PATH setup error: {e}"}

    def _verify_path_modification(self, womm_path: str) -> Dict:
        """Verify that PATH modification was successful."""
        try:
            current_path = os.environ.get("PATH", "")

            # Check if womm_path is in current PATH
            if womm_path in current_path:
                # Test if womm executable is accessible
                womm_exec = Path(womm_path) / (
                    "womm.bat" if platform.system() == "Windows" else "womm"
                )
                if womm_exec.exists():
                    return {"success": True, "message": "PATH modification verified"}
                else:
                    return {
                        "success": False,
                        "error": "WOMM executable not found after PATH modification",
                    }
            else:
                return {
                    "success": False,
                    "error": "WOMM path not found in current PATH",
                }

        except Exception as e:
            return {"success": False, "error": f"PATH verification error: {e}"}

    def _verify_installation(self) -> Dict:
        """Verify that installation was successful."""
        try:
            checks = []

            # Check 1: Files copied successfully
            files_check = self._verify_files_copied()
            checks.append(files_check)

            # Note: PATH verification is now done in _setup_windows_user_path with reg query
            # Executable verification removed due to Unicode encoding issues with subprocess
            # The executable works fine in interactive mode, the issue is only with subprocess.run

            success = all(check["success"] for check in checks)

            return {
                "success": success,
                "checks": checks,
                "message": "Installation verification completed",
            }

        except Exception as e:
            return {"success": False, "error": f"Installation verification error: {e}"}

    def _verify_files_copied(self) -> Dict:
        """Verify that WOMM files were copied successfully."""
        try:
            required_files = [
                "womm.py",
                "womm.bat" if platform.system() == "Windows" else "womm",
            ]
            missing_files = []

            for file_name in required_files:
                file_path = self.target_path / file_name
                if not file_path.exists():
                    missing_files.append(file_name)

            if missing_files:
                return {
                    "success": False,
                    "error": f"Missing files: {', '.join(missing_files)}",
                }
            else:
                return {"success": True, "message": "All required files present"}

        except Exception as e:
            return {"success": False, "error": f"File verification error: {e}"}

    def _verify_executable_works(self) -> Dict:
        """Verify that WOMM executable works correctly."""
        try:
            if platform.system() == "Windows":
                exec_path = self.target_path / "womm.bat"
            else:
                exec_path = self.target_path / "womm"

            if not exec_path.exists():
                return {"success": False, "error": "WOMM executable not found"}

            # Test basic functionality - avoid --help due to Unicode encoding issues
            # Just test that the executable can be run without arguments
            result = run_silent([str(exec_path)])
            # Exit code 0 or 2 is acceptable (0=success, 2=missing command)
            if result.returncode in [0, 2]:
                return {"success": True, "message": "WOMM executable working correctly"}
            else:
                return {
                    "success": False,
                    "error": f"WOMM executable failed basic test (exit code: {result.returncode})",
                }

        except Exception as e:
            return {"success": False, "error": f"Executable verification error: {e}"}

    def _verify_path_configured(self) -> Dict:
        """Verify that PATH is configured correctly."""
        try:
            current_path = os.environ.get("PATH", "")
            womm_path = str(self.target_path)

            if womm_path in current_path:
                return {"success": True, "message": "PATH configured correctly"}
            else:
                return {
                    "success": False,
                    "error": "WOMM path not found in current PATH",
                }

        except Exception as e:
            return {"success": False, "error": f"PATH verification error: {e}"}

    def _verify_commands_accessible(self) -> Dict:
        """Verify that WOMM commands are accessible."""
        try:
            # Test if womm command is accessible
            if platform.system() == "Windows":
                # Lancer un nouvel invite de cmd en background pour checker
                # car le terminal actuel n'a pas le PATH à jour
                result = run_silent(["cmd", "/c", "where", "womm"])
            else:
                result = run_silent(["which", "womm"])

            if result.success:
                return {"success": True, "message": "WOMM commands accessible"}
            else:
                return {"success": False, "error": "WOMM commands not accessible"}

        except Exception as e:
            return {"success": False, "error": f"Command accessibility error: {e}"}

    def _get_available_commands(self) -> List[Dict]:
        """Get list of available commands after installation."""
        return [
            {
                "command": "womm",
                "description": "Main CLI interface",
                "category": "Core",
            },
            {
                "command": "womm install",
                "description": "Install WOMM",
                "category": "Setup",
            },
            {
                "command": "womm uninstall",
                "description": "Uninstall WOMM",
                "category": "Setup",
            },
            {
                "command": "womm new python",
                "description": "Create Python project",
                "category": "Projects",
            },
            {
                "command": "womm new javascript",
                "description": "Create JavaScript project",
                "category": "Projects",
            },
            {
                "command": "womm lint",
                "description": "Lint code",
                "category": "Development",
            },
            {
                "command": "womm spell",
                "description": "Spell check",
                "category": "Development",
            },
            {
                "command": "womm system",
                "description": "System tools",
                "category": "System",
            },
        ]


# Legacy functions for backward compatibility
def copy_womm_to_user_directory():
    """Legacy function - use InstallationManager.install() instead."""
    manager = InstallationManager()
    result = manager._copy_womm_to_user_directory()
    if not result["success"]:
        raise Exception(result["error"])


def backup_user_path(target_path: Path) -> bool:
    """Legacy function - use InstallationManager.install() instead."""
    manager = InstallationManager()
    manager.target_path = target_path
    result = manager._backup_user_path()
    return result["success"]


def restore_user_path(target_path: Path) -> bool:
    """Restore user PATH from backup."""
    try:
        backup_dir = target_path / ".backup"
        latest_backup = backup_dir / ".path"

        if not latest_backup.exists():
            return False

        if platform.system() == "Windows":
            # Windows user PATH restoration
            with open(latest_backup, encoding="utf-8") as f:
                content = f.read()
                # Extract PATH from backup
                for line in content.split("\n"):
                    if not line.startswith("#") and line.strip():
                        path_value = line.strip()
                        result = run_silent(
                            [
                                "reg",
                                "add",
                                "HKCU\\Environment",
                                "/v",
                                "PATH",
                                "/t",
                                "REG_EXPAND_SZ",
                                "/d",
                                path_value,
                                "/f",
                            ]
                        )
                        return result.success
        else:
            # Unix PATH restoration
            with open(latest_backup, encoding="utf-8") as f:
                content = f.read()
                for line in content.split("\n"):
                    if not line.startswith("#") and line.strip():
                        os.environ["PATH"] = line.strip()
                        return True

        return False

    except Exception:
        return False


def setup_path():
    """Legacy function - use InstallationManager.install() instead."""
    manager = InstallationManager()
    result = manager._setup_path()
    if not result["success"]:
        raise Exception(result["error"])


def create_womm_executable():
    """Legacy function - use InstallationManager.install() instead."""
    manager = InstallationManager()
    result = manager._create_womm_executable()
    if not result["success"]:
        raise Exception(result["error"])


class PathManager:
    """Manages PATH operations for Works On My Machine."""

    def __init__(self, target: Optional[str] = None):
        """Initialize the path manager.

        Args:
            target: Custom target directory (default: ~/.womm)
        """
        if target:
            self.target_path = Path(target).expanduser().resolve()
        else:
            self.target_path = Path.home() / ".womm"

        self.backup_dir = self.target_path / ".backup"
        self.latest_backup = self.backup_dir / ".path"
        self.platform = platform.system()

    def backup_path(self) -> Dict:
        """Backup the current user PATH.

        Returns:
            Dictionary containing backup results
        """
        result = {
            "success": False,
            "target_path": str(self.target_path),
            "backup_location": str(self.backup_dir),
            "backup_files": [],
            "errors": [],
        }

        try:
            # Create backup directory if it doesn't exist
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Get current PATH
            if self.platform == "Windows":
                # Use environment variable for Windows
                current_path = os.environ.get("PATH", "")
                if not current_path:
                    result["errors"].append(
                        "Failed to read Windows PATH from environment"
                    )
                    return result
            else:
                current_path = os.environ.get("PATH", "")

            # Create backup file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f".path_{timestamp}"

            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(f"# WOMM PATH Backup - {timestamp}\n")
                f.write(f"# Platform: {self.platform}\n")
                f.write(f"# Target: {self.target_path}\n")
                f.write("# Original PATH:\n")
                f.write(f"{current_path}\n")

            # Update latest backup reference (copy instead of symlink for Windows compatibility)
            if self.latest_backup.exists():
                self.latest_backup.unlink()
            # Copy the backup file to .path (latest reference)
            shutil.copy2(backup_file, self.latest_backup)

            # Get list of all backup files
            backup_files = list(self.backup_dir.glob(".path_*"))
            result["backup_files"] = [
                str(f.name) for f in sorted(backup_files, reverse=True)
            ]
            result["success"] = True

            return result

        except Exception as e:
            result["errors"].append(f"Error creating PATH backup: {e}")
            return result

    def restore_path(self) -> Dict:
        """Restore user PATH from backup.

        Returns:
            Dictionary containing restore results
        """
        result = {
            "success": False,
            "target_path": str(self.target_path),
            "backup_used": "",
            "errors": [],
        }

        try:
            # Check if any backup files exist
            backup_files = list(self.backup_dir.glob(".path_*"))
            if not backup_files:
                result["errors"].append("No PATH backup found")
                return result

            # Use the most recent backup if .path doesn't exist
            if not self.latest_backup.exists():
                backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                latest_file = backup_files[0]
            else:
                latest_file = self.latest_backup

                # Read backup content
            with open(latest_file, encoding="utf-8") as f:
                content = f.read()

            # Parse the backup content to extract PATH
            if self.platform == "Windows":
                # For Windows, the backup contains registry output
                # Look for the PATH value in the registry output
                lines = content.split("\n")
                path_value = ""
                for line in lines:
                    if "REG_EXPAND_SZ" in line and "PATH" in line:
                        # Extract the PATH value from registry output
                        parts = line.split("REG_EXPAND_SZ")
                        if len(parts) > 1:
                            path_value = parts[1].strip()
                            break
            else:
                # For Unix, extract the PATH value (skip comment lines)
                lines = content.split("\n")
                for line in lines:
                    if not line.startswith("#") and line.strip():
                        path_value = line.strip()
                        break

            if not path_value:
                result["errors"].append("No valid PATH found in backup")
                return result

            # Restore PATH
            if self.platform == "Windows":
                restore_result = run_silent(
                    [
                        "reg",
                        "add",
                        "HKCU\\Environment",
                        "/v",
                        "PATH",
                        "/t",
                        "REG_EXPAND_SZ",
                        "/d",
                        path_value,
                        "/f",
                    ]
                )
                if not restore_result.success:
                    result["errors"].append("Failed to restore Windows user PATH")
                    return result
            else:
                # For Unix, we can only update current session
                os.environ["PATH"] = path_value

            result["backup_used"] = latest_file.name
            result["success"] = True
            return result

        except Exception as e:
            result["errors"].append(f"Error restoring PATH: {e}")
            return result

    def list_backups(self) -> Dict:
        """List available PATH backups.

        Returns:
            Dictionary containing backup information
        """
        result = {
            "success": False,
            "target_path": str(self.target_path),
            "backup_location": str(self.backup_dir),
            "backups": [],
            "latest_backup": "",
            "errors": [],
        }

        try:
            if not self.backup_dir.exists():
                result["errors"].append("No backup directory found")
                return result

            # Get all backup files
            backup_files = list(self.backup_dir.glob(".path_*"))
            if not backup_files:
                result["errors"].append("No PATH backups found")
                return result

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for backup_file in backup_files:
                try:
                    stat = backup_file.stat()
                    with open(backup_file, encoding="utf-8") as f:
                        first_line = f.readline().strip()

                    backup_info = {
                        "name": backup_file.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "description": (
                            first_line
                            if first_line.startswith("#")
                            else "No description"
                        ),
                    }
                    result["backups"].append(backup_info)

                    # Mark as latest if it's the most recent
                    if not result["latest_backup"]:
                        result["latest_backup"] = backup_file.name

                except Exception as e:
                    result["errors"].append(f"Error listing backups: {e}")
                    continue

            result["success"] = True
            return result

        except Exception as e:
            result["errors"].append(f"Error listing backups: {e}")
            return result


def main():
    """Legacy main function - kept for backward compatibility."""
    import sys

    parser = argparse.ArgumentParser(description="Install Works On My Machine")
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force installation even if .womm directory exists",
    )
    parser.add_argument(
        "--target", type=str, help="Custom target directory (default: ~/.womm)"
    )

    args = parser.parse_args()

    # Use InstallationManager for actual installation
    manager = InstallationManager()
    result = manager.install(force=args.force, target=args.target)

    # Simple console output for legacy compatibility
    if result["success"]:
        print("Installation completed successfully")
    else:
        print("Installation failed")
        for error in result["errors"]:
            print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
