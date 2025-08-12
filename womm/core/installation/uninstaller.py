#!/usr/bin/env python3
"""
Uninstaller for Works On My Machine.
Removes WOMM from the system and cleans up PATH entries.
"""

# IMPORTS
########################################################
# Standard library imports
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

from womm.core.installation.path_manager_utils import (
    extract_path_from_reg_output,
)

# Third-party imports
# (None for this file)
# Local imports
from womm.core.utils.cli_manager import run_silent

# Security is assumed available; remove conditional availability


# MAIN CLASS
########################################################
# Core uninstallation manager class


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

    # PUBLIC METHODS
    ########################################################
    # Main interface methods for uninstallation

    def uninstall(
        self,
        force: bool = False,
        target: Optional[str] = None,
    ) -> None:
        """
        Perform WOMM uninstallation with integrated UI.

        Args:
            force: Force uninstallation without confirmation
            target: Custom target directory
        """
        # Override target path if specified
        if target:
            self.target_path = Path(target).expanduser().resolve()

        # Import UI modules (assumed available)
        from womm.core.ui.console import (
            console,
            print_error,
            print_header,
            print_install,
            print_success,
            print_system,
        )
        from womm.core.ui.panels import create_panel
        from womm.core.ui.progress import (
            create_file_copy_progress,
            create_spinner_with_status,
            create_step_progress,
        )
        from womm.core.ui.prompts import confirm, show_warning_panel

        print_header("W.O.M.M Uninstallation")

        # Check target directory existence
        with create_spinner_with_status("Checking target directory...") as (
            progress,
            task,
        ):
            # Check if WOMM is installed
            if not self.target_path.exists():
                progress.update(
                    task, status="Following path not found: {self.target_path}"
                )
                print_error(
                    "Works On My Machine is not installed at the specified location"
                )
                raise RuntimeError("WOMM not installed at target path")
            else:
                progress.update(
                    task, status=f"Found installation at : {self.target_path}"
                )

        # Check if force is required
        if not force and self._needs_confirmation():
            # Show warning panel for uninstallation
            console.print("")
            show_warning_panel(
                "Uninstallation Confirmation",
                f"This will completely remove WOMM from {self.target_path}.\n\n"
                "This action cannot be undone.",
            )

            # Ask for confirmation
            if not confirm(
                "Do you want to continue and remove WOMM completely?",
                default=False,
            ):
                console.print("❌ Uninstallation cancelled", style="red")
                raise RuntimeError("Uninstallation cancelled by user")

            console.print("")
            print_system("Proceeding with uninstallation...")

        # Remove from PATH with spinner
        print("")
        with create_spinner_with_status("Removing from PATH...") as (
            progress,
            task,
        ):
            path_result = self._remove_from_path()
            # Treat 'already clean' as non-fatal and continue
            if not path_result.get("success") and not path_result.get("warning"):
                progress.update(task, status="Failed to remove from PATH")
                progress.stop()
                print_error(
                    f"Failed to remove from PATH: {path_result.get('error', 'unknown error')}"
                )
                sys.exit(1)

            # Status feedback
            if path_result.get("warning") and not path_result.get(
                "path_deleted", False
            ):
                progress.update(task, status="PATH already clean")
            else:
                progress.update(task, status="PATH updated")

        # Remove WOMM directory with spinner
        print("")
        # Get list of files to remove for progress bar
        files_to_remove = self._get_files_to_remove()
        with create_file_copy_progress(files_to_remove, "Removing WOMM files...") as (
            progress,
            task,
            files,
        ):
            # Iterate through each file and update progress
            for file_path in files:
                # Update progress bar with current file
                filename = os.path.basename(file_path)
                progress.update(task, current_file=filename)

                # Remove each file individually
                try:
                    import time

                    target_file = self.target_path / file_path.rstrip("/")

                    if target_file.is_file():
                        # Remove single file
                        target_file.unlink()
                        time.sleep(0.1)
                    elif target_file.is_dir():
                        # Remove directory
                        shutil.rmtree(target_file)
                        time.sleep(0.3)

                    # Advance progress bar
                    progress.advance(task)
                except Exception as e:
                    print_error(f"Failed to remove {file_path}: {e}")
                    raise

        # Remove the root directory itself
        try:
            if self.target_path.exists():
                shutil.rmtree(self.target_path)
        except Exception as e:
            print_error(f"Failed to remove root directory {self.target_path}: {e}")
            raise

        # Verify uninstallation with step progress
        try:
            print("")
            print_system("Verifying uninstallation...")
            verification_steps = ["Files", "PATH", "Registry"]
            with create_step_progress(
                verification_steps, "Verifying uninstallation..."
            ) as (
                progress,
                task,
                steps,
            ):
                # Perform verification for each step
                verification_results = []
                for i, step in enumerate(steps):
                    # Update progress bar with current step and step number
                    progress.update(
                        task,
                        description=f"[bold blue]{step}",
                        current_step=step,
                        step=i + 1,
                    )

                    # Perform specific verification for each step
                    if step == "Files":
                        result = self._verify_files_removed()
                    elif step == "PATH":
                        result = self._verify_path_cleaned()
                    elif step == "Registry":
                        result = self._verify_registry_cleaned()
                    else:
                        result = {
                            "success": False,
                            "error": f"Unknown verification step: {step}",
                        }

                    verification_results.append(result)

                    if not result["success"]:
                        raise Exception(
                            f"Verification failed for {step}: {result.get('error', 'Check failed')}"
                        )

                    # Advance progress bar
                    progress.advance(task)

            # Show verification details
            for result in verification_results:
                if result["success"]:
                    print_success(f"✓ {result.get('message', 'Check passed')}")
                else:
                    print_error(f"✗ {result.get('error', 'Check failed')}")

        except Exception as e:
            print("")
            print_error(f"Error during verification: {e}")
            raise

        # Uninstallation success
        print("")
        print_install("🎉 Uninstallation completed successfully!")

        # Show completion panel
        completion_content = (
            "WOMM has been successfully removed from your system.\n\n"
            "To complete the cleanup:\n"
            "• Restart your terminal for PATH changes to take effect\n"
            "• Remove any remaining WOMM references from your shell config files\n\n"
            "Thank you for using Works On My Machine!"
        )

        completion_panel = create_panel(
            completion_content,
            title="✅ Uninstallation Complete",
            style="bright_green",
            border_style="bright_green",
            padding=(1, 1),
        )
        print("")
        console.print(completion_panel)

        return None

    # PRIVATE METHODS
    ########################################################
    # Internal methods for uninstallation process

    def _needs_confirmation(self) -> bool:
        """Check if uninstallation requires user confirmation."""
        return self.target_path.exists()

    def _remove_from_path(self) -> Dict:
        """Remove WOMM from PATH based on platform."""
        if self.platform == "Windows":
            return self._remove_from_windows_path()
        else:
            return self._remove_from_unix_path()

    def _remove_from_windows_path(self) -> Dict:
        """Remove WOMM directory from Windows user PATH using backup/restore strategy."""
        result_dict = {
            "success": False,
            "message": "",
            "error": "",
        }

        # Import UI modules
        try:
            # Step 1: Récupérer le PATH utilisateur actuel (accepter REG_SZ ou REG_EXPAND_SZ)
            query_result = run_silent(
                ["reg", "query", "HKCU\\Environment", "/v", "PATH"]
            )

            backup_user_path = ""  # Variable de secours

            if query_result.success:
                backup_user_path = extract_path_from_reg_output(query_result.stdout)

            # Normalisation pour comparaison robuste (insensible à la casse, sans slash final)
            import os as _os

            def _norm(p: str) -> str:
                return _os.path.expandvars(p).rstrip("/\\").lower()

            womm_norm = _norm(self.womm_path)

            # Step 2: Vérifier si WOMM path est présent (comparaison normalisée)
            has_womm = any(_norm(e) == womm_norm for e in backup_user_path.split(";"))
            if not has_womm:
                result_dict["warning"] = True
                result_dict["path_deleted"] = False
                result_dict["success"] = True
                result_dict["message"] = (
                    f"WOMM path {self.womm_path} not found in user PATH"
                )
                return result_dict

            # Step 3: Retirer le path du dossier .womm (comparaison normalisée)
            from womm.core.installation.path_manager_utils import (
                deduplicate_path_entries,
            )

            new_entries = []
            for entry in backup_user_path.split(";"):
                part = entry.strip()
                if not part:
                    continue
                if _norm(part) == womm_norm:
                    # skip WOMM entry
                    continue
                new_entries.append(part)
            new_user_path = deduplicate_path_entries(";".join(new_entries))

            # Step 4: Écrire le nouveau PATH utilisateur (toujours REG_EXPAND_SZ)
            update_result = run_silent(
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

            if not update_result.success:
                result_dict["error"] = "Failed to update user PATH in registry"
                return result_dict

            # Step 5: Vérifier que la suppression a réussi avec reg query
            verify_result = run_silent(
                ["reg", "query", "HKCU\\Environment", "/v", "PATH"]
            )
            if not verify_result.success:
                result_dict["error"] = "Failed to verify PATH update"
                return result_dict

            # Step 6: Vérifier que le chemin WOMM n'est plus dans le registre (comparaison normalisée)
            current_user_path = extract_path_from_reg_output(verify_result.stdout)
            still_has_womm = any(
                _norm(e) == womm_norm for e in current_user_path.split(";")
            )
            if still_has_womm:
                result_dict["error"] = "WOMM path still found in registry after removal"
                return result_dict

            # Step 7: Mettre à jour la session courante
            current_full_path = os.environ.get("PATH", "")
            # Retirer de la session courante aussi (comparaison normalisée)
            current_entries = [e for e in current_full_path.split(";") if e]
            new_current_entries = []
            for entry in current_entries:
                if _norm(entry) == womm_norm:
                    continue
                new_current_entries.append(entry)
            os.environ["PATH"] = ";".join(new_current_entries)

            result_dict["success"] = True
            result_dict["message"] = (
                f"Removed {self.womm_path} from user PATH - verified with registry"
            )
            return result_dict

        except Exception as e:
            result_dict["error"] = f"Windows user PATH removal error: {e}"
            return result_dict

    def _remove_from_unix_path(self) -> Dict:
        """Remove WOMM bin directory from Unix PATH."""
        result = {
            "success": False,
            "message": "",
            "error": "",
        }

        try:
            womm_path_str = str(self.womm_path)
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
                    path_line = f'export PATH="$PATH:{womm_path_str}"'

                    if path_line in content:
                        new_content = content.replace(path_line, "")
                        shell_file.write_text(new_content)
                        removed_from.append(shell_file.name)

            if removed_from:
                result["success"] = True
                result["message"] = f"Removed PATH entry from {', '.join(removed_from)}"
            else:
                result["warning"] = True
                result["message"] = f"{womm_path_str} not found in shell config files"

            return result

        except Exception as e:
            result["error"] = f"Error updating Unix PATH: {e}"
            return result

    def _get_files_to_remove(self) -> List[str]:
        """Get list of files and directories to remove for progress bar."""
        files_to_remove = []
        target = self.target_path

        if not target.exists():
            return files_to_remove

        # Add main files and directories
        for item in target.iterdir():
            if item.is_file():
                files_to_remove.append(str(item.name))
            elif item.is_dir():
                files_to_remove.append(f"{item.name}/")

        return files_to_remove

    def _verify_files_removed(self) -> Dict:
        """Verify that WOMM files were removed successfully."""
        result_dict = {
            "success": False,
            "message": "",
            "error": "",
        }

        try:
            if not self.target_path.exists():
                result_dict["success"] = True
                result_dict["message"] = "All WOMM files removed successfully"
                return result_dict
            else:
                result_dict["error"] = (
                    f"WOMM directory still exists: {self.target_path}"
                )
                return result_dict

        except Exception as e:
            result_dict["error"] = f"File removal verification error: {e}"
            return result_dict

    def _verify_path_cleaned(self) -> Dict:
        """Verify that PATH was cleaned successfully."""
        result_dict = {
            "success": False,
            "message": "",
            "error": "",
        }

        try:
            current_path = os.environ.get("PATH", "")
            womm_path = str(self.target_path)

            if womm_path not in current_path:
                result_dict["success"] = True
                result_dict["message"] = "PATH cleaned successfully"
                return result_dict
            else:
                result_dict["error"] = "WOMM path still found in current PATH"
                return result_dict

        except Exception as e:
            result_dict["error"] = f"PATH verification error: {e}"
            return result_dict

    def _verify_registry_cleaned(self) -> Dict:
        """Verify that Windows registry was cleaned successfully."""
        result_dict = {
            "success": False,
            "message": "",
            "error": "",
        }

        try:
            if self.platform != "Windows":
                result_dict["success"] = True
                result_dict["message"] = "Registry check skipped (not Windows)"
                return result_dict

            # Check Windows registry
            query_result = run_silent(
                ["reg", "query", "HKCU\\Environment", "/v", "PATH"]
            )

            if not query_result.success:
                result_dict["error"] = "Could not query Windows registry"
                return result_dict

            output = query_result.stdout
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="ignore")

            womm_path = str(self.target_path)
            if womm_path not in output:
                result_dict["success"] = True
                result_dict["message"] = "Windows registry cleaned successfully"
                return result_dict
            else:
                result_dict["error"] = "WOMM path still found in Windows registry"
                return result_dict

        except Exception as e:
            result_dict["error"] = f"Registry verification error: {e}"
            return result_dict
