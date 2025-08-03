#!/usr/bin/env python3
"""
Uninstaller for Works On My Machine.
Removes WOMM from the system and cleans up PATH entries.
"""

import argparse
import os
import platform
import shutil
import sys
import winreg
from pathlib import Path
from typing import Dict, Optional

# Import CLI manager
try:
    from shared.core.cli_manager import run_command, run_silent
except ImportError:
    # Fallback if module not available
    import subprocess

    def run_command(cmd, **kwargs):
        """Run a command with logging."""
        result = subprocess.run(cmd, **kwargs)  # noqa: S603
        return type("obj", (object,), {"success": result.returncode == 0})()

    def run_silent(cmd, **kwargs):
        """Run a command silently."""
        return subprocess.run(cmd, capture_output=True, **kwargs)  # noqa: S603


# Import security validator if available
import importlib.util

SECURITY_AVAILABLE = (
    importlib.util.find_spec("shared.security.security_validator") is not None
)


class UninstallationManager:
    """Manages the uninstallation process for Works On My Machine."""

    def __init__(self, target: Optional[str] = None):
        """Initialize the uninstallation manager.

        Args:
            target: Custom target directory (default: ~/.womm)
        """
        if target:
            self.target_path = Path(target).expanduser().resolve()
        else:
            self.target_path = Path.home() / ".womm"

        # WOMM is installed directly in target_path, not in a bin subdirectory
        self.womm_path = str(self.target_path)
        self.actions = []
        self.platform = platform.system()

    def uninstall(self, force: bool = False) -> Dict:
        """Perform the uninstallation process.

        Args:
            force: Skip confirmation prompts

        Returns:
            Dictionary containing uninstallation results
        """
        result = {
            "success": False,
            "target_path": str(self.target_path),
            "platform": self.platform,
            "actions": [],
            "errors": [],
            "requires_confirmation": False,
        }

        # Check if WOMM is installed
        if not self.target_path.exists():
            result["errors"].append(
                "Works On My Machine is not installed at the specified location"
            )
            return result

        # Check if force is required
        if not force and self._needs_confirmation():
            result["requires_confirmation"] = True
            return result

        # Start uninstallation
        success = True

        # 1. Remove from PATH
        if self.platform == "Windows":
            path_result = self._remove_from_windows_path()
        else:
            path_result = self._remove_from_unix_path()

        if path_result["status"] == "failed":
            success = False
            result["errors"].extend(path_result["errors"])

        self.actions.append(path_result)

        # 2. Remove WOMM directory
        dir_result = self._remove_womm_directory()
        if dir_result["status"] == "failed":
            success = False
            result["errors"].extend(dir_result["errors"])

        self.actions.append(dir_result)

        result["success"] = success
        result["actions"] = self.actions

        return result

    def _needs_confirmation(self) -> bool:
        """Check if uninstallation requires user confirmation."""
        return self.target_path.exists()

    def _remove_from_windows_path(self) -> Dict:
        """Remove WOMM directory from Windows user PATH using backup/restore strategy."""
        action = {
            "action": "remove_path",
            "status": "failed",
            "message": "",
            "errors": [],
        }

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
            else:
                action["status"] = "warning"
                action["message"] = "PATH not found in registry"
                return action

            # Step 2: Vérifier si WOMM path est présent
            if self.womm_path not in backup_user_path:
                action["status"] = "warning"
                action["message"] = f"WOMM path {self.womm_path} not found in user PATH"
                return action

            # Step 3: Retirer le path du dossier .womm
            new_entries = [entry for entry in backup_user_path.split(";") if entry != self.womm_path]
            new_user_path = ";".join(new_entries)

            # Step 4: Écrire le nouveau PATH utilisateur
            result = run_silent([
                "reg", "add", "HKCU\\Environment", "/v", "PATH",
                "/t", "REG_SZ", "/d", new_user_path, "/f"
            ])

            if not result.success:
                action["errors"].append("Failed to update user PATH in registry")
                return action

            # Step 5: Vérifier que la suppression a réussi avec reg query
            verify_result = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])
            if not verify_result.success:
                # Si erreur, rétablir le PATH avec la variable de secours
                run_silent([
                    "reg", "add", "HKCU\\Environment", "/v", "PATH",
                    "/t", "REG_SZ", "/d", backup_user_path, "/f"
                ])
                action["errors"].append("Failed to verify PATH update - restored backup")
                return action

            # Step 6: Vérifier que le chemin WOMM n'est plus dans le registre
            verify_output = verify_result.stdout
            if isinstance(verify_output, bytes):
                verify_output = verify_output.decode("utf-8", errors="ignore")

            if self.womm_path in verify_output:
                # Si le chemin est encore dans le registre, restaurer
                run_silent([
                    "reg", "add", "HKCU\\Environment", "/v", "PATH",
                    "/t", "REG_SZ", "/d", backup_user_path, "/f"
                ])
                action["errors"].append("WOMM path still found in registry after removal")
                return action

            # Step 7: Mettre à jour la session courante
            current_full_path = os.environ.get("PATH", "")
            # Retirer de la session courante aussi
            current_entries = current_full_path.split(";")
            new_current_entries = [entry for entry in current_entries if entry != self.womm_path]
            os.environ["PATH"] = ";".join(new_current_entries)

            action["status"] = "success"
            action["message"] = f"Removed {self.womm_path} from user PATH - verified with registry"
            return action

        except Exception as e:
            # En cas d'exception, rétablir le PATH avec la variable de secours
            if 'backup_user_path' in locals() and backup_user_path:
                try:
                    run_silent([
                        "reg", "add", "HKCU\\Environment", "/v", "PATH",
                        "/t", "REG_SZ", "/d", backup_user_path, "/f"
                    ])
                except Exception:
                    pass  # Ignore les erreurs de restauration
            action["errors"].append(f"Windows user PATH removal error: {e}")
            return action

    def _remove_from_unix_path(self) -> Dict:
        """Remove WOMM bin directory from Unix PATH."""
        action = {
            "action": "remove_path",
            "status": "failed",
            "message": "",
            "errors": [],
        }

        try:
            bin_path_str = str(self.bin_path)
            shell_files = [
                Path.home() / ".bashrc",
                Path.home() / ".zshrc",
                Path.home() / ".profile",
                Path.home() / ".bash_profile",
            ]

            removed_from = []

            for shell_file in shell_files:
                if shell_file.exists():
                    content = shell_file.read_text()
                    path_line = f'export PATH="$PATH:{bin_path_str}"'

                    if path_line in content:
                        new_content = content.replace(path_line, "")
                        shell_file.write_text(new_content)
                        removed_from.append(shell_file.name)

            if removed_from:
                action["status"] = "success"
                action["message"] = f"Removed PATH entry from {', '.join(removed_from)}"
            else:
                action["status"] = "warning"
                action["message"] = f"{bin_path_str} not found in shell config files"

            return action

        except Exception as e:
            action["errors"].append(f"Error updating Unix PATH: {e}")
            return action

    def _remove_womm_directory(self) -> Dict:
        """Remove the WOMM directory."""
        action = {
            "action": "remove_directory",
            "status": "failed",
            "message": "",
            "errors": [],
        }

        try:
            if self.target_path.exists():
                shutil.rmtree(self.target_path)
                action["status"] = "success"
                action["message"] = f"WOMM directory removed: {self.target_path}"
            else:
                action["status"] = "warning"
                action["message"] = "WOMM directory not found"

            return action

        except Exception as e:
            action["errors"].append(f"Error removing WOMM directory: {e}")
            return action


def main():
    """Legacy main function - kept for backward compatibility."""
    parser = argparse.ArgumentParser(description="Uninstall Works On My Machine")
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force uninstallation without confirmation",
    )
    parser.add_argument(
        "--target", type=str, help="Custom target directory (default: ~/.womm)"
    )

    args = parser.parse_args()

    # Use UninstallationManager for actual uninstallation
    manager = UninstallationManager(target=args.target)
    result = manager.uninstall(force=args.force)

    # Simple console output for legacy compatibility
    if result["success"]:
        print("Uninstallation completed successfully")
    else:
        print("Uninstallation failed")
        for error in result["errors"]:
            print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
