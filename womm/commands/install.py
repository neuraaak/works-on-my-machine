#!/usr/bin/env python3
"""
Installation commands for WOMM CLI.
Handles installation, uninstallation, and PATH management.
"""

import sys

import click

from ..utils.security import SECURITY_AVAILABLE, security_validator


def display_installation_result(result: dict) -> None:
    """Display installation results using specialized prints."""
    try:
        from shared.ui import (
            console,
            print_added,
            print_error,
            print_file,
            print_info,
            print_path,
            print_success,
            print_system,
            print_warn,
        )
        from shared.ui.tables import create_command_table

        # Display each action with appropriate print function
        for action in result["actions"]:
            action_name = action["action"]
            message = action["message"]

            if action["status"] == "success":
                if action_name == "copy_files":
                    print_added(message)
                elif action_name == "backup_path":
                    print_file(message)
                elif action_name == "create_executable":
                    print_system(message)
                elif action_name == "setup_path":
                    print_path(message)
                elif action_name == "verify_installation":
                    if action["status"] == "success":
                        print_success(message)
                    else:
                        print_error("VERIFY", message)
                    # Display verification checks
                    if "checks" in action:
                        for check in action["checks"]:
                            if check["success"]:
                                print_success(f"  ✓ {check.get('message', 'Check passed')}")
                            else:
                                print_error("VERIFY", f"  ✗ {check.get('error', 'Check failed')}")
                                # Debug: print more details
                                print_error("DEBUG", f"    Check details: {check}")
                else:
                    print_success(f"{action_name}: {message}")
            elif action["status"] == "warning":
                print_warn("INSTALL", f"{action_name}: {message}")
            elif action["status"] == "failed":
                print_error("INSTALL", f"{action_name}: {message}")
            else:
                print_info("INSTALL", f"{action_name}: {message}")

        if result["success"]:
            print_success("Installation completed successfully!")

            # Display available commands
            print_info("INSTALL", "Commands available after terminal restart:")
            print("\n")
            commands_table = create_command_table(result["commands_available"])
            console.print(commands_table)

        else:
            # Handle installation failure
            if result.get("requires_confirmation"):
                print_warn("INSTALL", "Installation requires confirmation")
                print_info(
                    "INSTALL", f"Directory {result['target_path']} already exists"
                )
                print_info(
                    "INSTALL", "Use --force to overwrite or confirm when prompted"
                )
            else:
                print_error("INSTALL", "Installation failed")
                for error in result["errors"]:
                    print_error("ERROR", error)

    except ImportError:
        # Fallback to basic console output
        # Display each action
        for action in result["actions"]:
            if action["status"] == "success":
                print(f"✅ {action['action']}: {action['message']}")
            elif action["status"] == "warning":
                print(f"⚠️  {action['action']}: {action['message']}")
            elif action["status"] == "failed":
                print(f"❌ {action['action']}: {action['message']}")
            else:
                print(f"ℹ️  {action['action']}: {action['message']}")

        if result["success"]:
            print("✅ Installation completed successfully!")

            # Platform instructions
            if result["platform"] == "Windows":
                print(f"\nTo use immediately: set PATH=%PATH%;{result['target_path']}")
            else:
                print(
                    f"\nTo use immediately: export PATH=\"$PATH:{result['target_path']}\""
                )
        else:
            if result.get("requires_confirmation"):
                print("⚠️  Installation requires confirmation")
                print(f"Directory {result['target_path']} already exists")
                print("Use --force to overwrite")
            else:
                print("❌ Installation failed")
                for error in result["errors"]:
                    print(f"Error: {error}")


def display_uninstallation_result(result: dict) -> None:
    """Display uninstallation results using specialized prints."""
    try:
        from shared.ui import (
            print_error,
            print_info,
            print_path,
            print_success,
            print_system,
            print_warn,
        )

        # Display each action with appropriate print function
        for action in result["actions"]:
            action_name = action["action"]
            message = action["message"]

            if action["status"] == "success":
                if action_name == "remove_path":
                    print_path(message)
                elif action_name == "remove_directory":
                    print_success(message)
                else:
                    print_success(f"{action_name}: {message}")
            elif action["status"] == "warning":
                print_warn("UNINSTALL", f"{action_name}: {message}")
            elif action["status"] == "skipped":
                print_info("UNINSTALL", f"{action_name}: {message}")
            elif action["status"] == "failed":
                print_error("UNINSTALL", f"{action_name}: {message}")
            else:
                print_info("UNINSTALL", f"{action_name}: {message}")

        if result["success"]:
            print_success("Uninstallation completed successfully!")
            print_info(
                "UNINSTALL",
                "You may need to restart your terminal for PATH changes to take effect",
            )

        else:
            # Handle uninstallation failure
            if result.get("requires_confirmation"):
                print_warn("UNINSTALL", "WOMM installation found")
                print_info("UNINSTALL", "Use --force to proceed without confirmation")
            else:
                print_error("UNINSTALL", "Uninstallation failed")
                for error in result["errors"]:
                    print_error("UNINSTALL", error)

    except ImportError:
        # Fallback to basic console output
        # Display each action
        for action in result["actions"]:
            if action["status"] == "success":
                print(f"✅ {action['action']}: {action['message']}")
            elif action["status"] == "warning":
                print(f"⚠️  {action['action']}: {action['message']}")
            elif action["status"] == "skipped":
                print(f"ℹ️  {action['action']}: {action['message']}")
            elif action["status"] == "failed":
                print(f"❌ {action['action']}: {action['message']}")
            else:
                print(f"ℹ️  {action['action']}: {action['message']}")

        if result["success"]:
            print("✅ Uninstallation completed successfully!")
            print(
                "💡 You may need to restart your terminal for PATH changes to take effect"
            )
        else:
            if result.get("requires_confirmation"):
                print("⚠️  Uninstallation requires confirmation")
                print("Use --force to proceed without confirmation")
            else:
                print("❌ Uninstallation failed")
                for error in result["errors"]:
                    print(f"Error: {error}")


def display_path_restore_result(result: dict) -> None:
    """Display PATH restore results using specialized prints."""
    try:
        from shared.ui import print_error, print_info, print_success

        if result["success"]:
            print_success("PATH restored successfully!")
            print_info("PATH", f"Restored from backup: {result['backup_used']}")
            print_info(
                "PATH",
                "You may need to restart your terminal for changes to take effect",
            )
        else:
            print_error("PATH", "Failed to restore PATH")
            for error in result["errors"]:
                print_error("PATH", error)

    except ImportError:
        # Fallback to basic console output
        if result["success"]:
            print("✅ PATH restored successfully!")
            print(f"📄 Restored from backup: {result['backup_used']}")
            print("💡 You may need to restart your terminal for changes to take effect")
        else:
            print("❌ Failed to restore PATH")
            for error in result["errors"]:
                print(f"Error: {error}")


def display_path_backup_result(result: dict) -> None:
    """Display PATH backup information using specialized prints."""
    try:
        from shared.ui import (
            console,
            print_error,
            print_info,
            print_success,
        )
        from shared.ui.tables import create_backup_table

        if result["success"]:
            print_success("PATH backup information retrieved successfully!")

            # Display backup location
            print_info("PATH", f"Backup location: {result['backup_location']}")

            # Display backup table
            if result["backups"]:
                print_info("PATH", f"Available backups ({len(result['backups'])}):")
                backup_table = create_backup_table(result["backups"])
                console.print(backup_table)
            else:
                print_info("PATH", "No backup files found")

        else:
            print_error("PATH", "Failed to retrieve backup information")
            for error in result["errors"]:
                print_error("PATH", error)

    except ImportError:
        # Fallback to basic console output
        if result["success"]:
            print("✅ PATH backup information retrieved successfully!")
            print(f"📁 Backup location: {result['backup_location']}")

            if result["backups"]:
                print(f"📚 Available backups ({len(result['backups'])}):")
                for backup in result["backups"]:
                    print(f"  - {backup['name']} ({backup['modified']})")
            else:
                print("ℹ️  No backup files found")
        else:
            print("❌ Failed to retrieve backup information")
            for error in result["errors"]:
                print(f"Error: {error}")


@click.command()
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force installation even if .womm directory exists",
)
@click.option(
    "--target", type=click.Path(), help="Custom target directory (default: ~/.womm)"
)
def install(force, target):
    """Install Works On My Machine in user directory."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"❌ Invalid target path: {error}", err=True)
            sys.exit(1)

    try:
        from shared.installation.installer import InstallationManager
        from shared.ui import print_header

        print_header("W.O.M.M Installation")

        # Use InstallationManager for installation
        manager = InstallationManager()
        result = manager.install(force=force, target=target)

        # Display results
        display_installation_result(result)

        # Exit with appropriate code
        if result["success"]:
            sys.exit(0)
        elif result.get("requires_confirmation"):
            # Ask for confirmation if needed
            response = click.prompt(
                "Do you want to continue and overwrite the existing directory?",
                type=click.Choice(["y", "n"]),
                default="n",
            )
            if response == "y":
                # Retry with force
                result = manager.install(force=True, target=target)

                display_installation_result(result)
                sys.exit(0 if result["success"] else 1)
            else:
                click.echo("Installation cancelled")
                sys.exit(0)
        else:
            sys.exit(1)

    except ImportError as e:
        click.echo(f"❌ Error importing installer: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error during installation: {e}", err=True)
        sys.exit(1)


@click.command()
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force uninstallation without confirmation",
)
@click.option(
    "--target", type=click.Path(), help="Custom target directory (default: ~/.womm)"
)
def uninstall(force, target):
    """Uninstall Works On My Machine from user directory."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"❌ Invalid target path: {error}", err=True)
            sys.exit(1)

    try:
        from shared.installation.uninstaller import UninstallationManager
        from shared.ui import print_header

        print_header("W.O.M.M Uninstallation")

        # Use UninstallationManager for uninstallation
        manager = UninstallationManager(target=target)
        result = manager.uninstall(force=force)

        # Display results
        display_uninstallation_result(result)

        # Exit with appropriate code
        if result["success"]:
            sys.exit(0)
        elif result.get("requires_confirmation"):
            # Ask for confirmation if needed
            response = click.prompt(
                "Do you want to continue and remove WOMM completely?",
                type=click.Choice(["y", "n"]),
                default="n",
            )
            if response == "y":
                # Retry with force
                result = manager.uninstall(force=True)

                display_uninstallation_result(result)
                sys.exit(0 if result["success"] else 1)
            else:
                click.echo("Uninstallation cancelled")
                sys.exit(0)
        else:
            sys.exit(1)

    except ImportError as e:
        click.echo(f"❌ Error importing uninstaller: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error during uninstallation: {e}", err=True)
        sys.exit(1)


@click.command()
@click.option(
    "--target", type=click.Path(), help="Custom target directory (default: ~/.womm)"
)
def restore_path(target):
    """Restore user PATH from backup created during installation."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"❌ Invalid target path: {error}", err=True)
            sys.exit(1)

    try:
        from shared.installation.installer import PathManager
        from shared.ui import print_header

        print_header("W.O.M.M PATH Restoration")

        # Use PathManager for restoration
        manager = PathManager(target=target)
        result = manager.restore_path()

        # Display results
        display_path_restore_result(result)

        # Exit with appropriate code
        if result["success"]:
            sys.exit(0)
        else:
            sys.exit(1)

    except ImportError as e:
        click.echo(f"❌ Error importing path manager: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error during PATH restoration: {e}", err=True)
        sys.exit(1)


@click.command()
@click.option(
    "--target", type=click.Path(), help="Custom target directory (default: ~/.womm)"
)
def backup_path(target):
    """Show information about PATH backup."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"❌ Invalid target path: {error}", err=True)
            sys.exit(1)

    try:
        from shared.installation.installer import PathManager
        from shared.ui import print_header

        print_header("W.O.M.M PATH Backup Information")

        # Use PathManager for backup listing
        manager = PathManager(target=target)
        result = manager.list_backups()

        # Display results
        display_path_backup_result(result)

        # Exit with appropriate code
        if result["success"]:
            sys.exit(0)
        else:
            sys.exit(1)

    except ImportError as e:
        click.echo(f"❌ Error importing path manager: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error reading backup info: {e}", err=True)
        sys.exit(1)
