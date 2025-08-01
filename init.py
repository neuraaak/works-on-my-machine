#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize the Works On My Machine environment.

Detects if we are in the correct location (%USER%/.womm) and if not,
copies and relaunches from the correct location.
"""
import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Importer le gestionnaire CLI
try:
    from shared.cli_manager import run_command, run_interactive, run_silent
except ImportError:
    # Fallback si le module n'est pas encore disponible lors de la première installation
    subprocess_run = subprocess.run

    def run_command(cmd, desc, **kwargs):
        """Run a command with logging.

        Args:
            cmd: Command to run as list of strings.
            desc: Description of the command for logging.
            **kwargs: Additional arguments passed to subprocess.run.

        Returns:
            Object with success attribute indicating if command succeeded.
        """
        print(f"\n🔍 {desc}...")
        print(f"Command: {' '.join(cmd)}")
        result = subprocess_run(cmd, **kwargs)
        return type("obj", (object,), {"success": result.returncode == 0})()

    def run_silent(cmd, **kwargs):
        """Run a command silently.

        Args:
            cmd: Command to run as list of strings.
            **kwargs: Additional arguments passed to subprocess.run.

        Returns:
            CompletedProcess object from subprocess.run.
        """
        return subprocess_run(cmd, capture_output=True, **kwargs)

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
    return Path(__file__).parent.absolute()


def is_in_correct_location():
    """Check if we are in the correct location.

    Returns:
        bool: True if the script is in the target location, False otherwise.
    """
    current = get_current_womm_path()
    target = get_target_womm_path()

    try:
        # Resolve symbolic links and compare
        return current.resolve() == target.resolve()
    except Exception:
        return False


def copy_womm_to_user_directory():
    """Copy Works On My Machine to %USER%/.womm.

    Returns:
        Path object pointing to the new location of Works On My Machine.
    """
    source = get_current_womm_path()
    target = get_target_womm_path()

    print(f"📦 Copying from: {source}")
    print(f"📁 To: {target}")

    # Save old version if exists
    if target.exists():
        backup = target.with_suffix(".backup")
        if backup.exists():
            shutil.rmtree(backup)

        print(f"💾 Backing up old version to: {backup}")
        target.rename(backup)

    # Copy
    shutil.copytree(source, target)
    print("✅ Copy completed")

    return target


def launch_relocated_init(target_path):
    """Launch the new init from the correct location.

    Args:
        target_path: Path object pointing to the new location of Works On My Machine.
    """
    new_init = target_path / "init.py"

    print(f"🚀 Launching new init from: {new_init}")
    print("🔄 A new terminal window will open...")

    if platform.system() == "Windows":
        # Launch in a new cmd window
        subprocess.Popen(
            ["cmd", "/c", f"cd /d {target_path} && python init.py && pause"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    else:
        # Launch in a new terminal (Linux/Mac)
        if shutil.which("gnome-terminal"):
            subprocess.Popen(
                [
                    "gnome-terminal",
                    "--",
                    "bash",
                    "-c",
                    f"cd {target_path} && python3 init.py && read -p 'Press Enter to continue...'",
                ]
            )
        elif shutil.which("xterm"):
            subprocess.Popen(
                [
                    "xterm",
                    "-e",
                    f"cd {target_path} && python3 init.py && read -p 'Press Enter to continue...'",
                ]
            )
        else:
            # Fallback: just run in current terminal
            print("⚠️  No suitable terminal found, running in current terminal...")
            subprocess.run([sys.executable, str(new_init)])


def setup_path():
    """Set up PATH environment variable."""
    bin_path = get_target_womm_path() / "bin"

    if platform.system() == "Windows":
        setup_windows_path(bin_path)
    else:
        setup_unix_path(bin_path)


def setup_windows_path(bin_path):
    """Set up PATH for Windows."""
    print("🔧 Setting up Windows PATH...")

    # Get current user PATH
    try:
        result = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])
        if result.returncode == 0:
            # Parse current PATH
            output = result.stdout.decode("utf-8", errors="ignore")
            for line in output.split("\n"):
                if "PATH" in line and "REG_EXPAND_SZ" in line:
                    current_path = line.split("REG_EXPAND_SZ")[1].strip()
                    break
            else:
                current_path = ""
        else:
            current_path = ""
    except Exception:
        current_path = ""

    # Check if our path is already in PATH
    if str(bin_path) not in current_path:
        # Add to PATH
        new_path = f"{bin_path};{current_path}" if current_path else str(bin_path)

        try:
            # Set PATH for current user
            result = run_command(
                ["reg", "add", "HKCU\\Environment", "/v", "PATH", "/t", "REG_EXPAND_SZ", "/d", new_path, "/f"],
                "Setting Windows PATH",
                capture_output=True,
                text=True,
            )

            if result.success:
                print("✅ Windows PATH updated successfully")
                print("🔄 Restart your terminal or run 'refreshenv' to apply changes")
            else:
                print("⚠️  Failed to update Windows PATH automatically")
                print("💡 You can add it manually:")
                print(f"   setx PATH \"{bin_path};%PATH%\"")
        except Exception as e:
            print(f"⚠️  Error updating Windows PATH: {e}")
            print("💡 You can add it manually:")
            print(f"   setx PATH \"{bin_path};%PATH%\"")
    else:
        print("✅ PATH already configured")


def setup_unix_path(bin_path):
    """Set up PATH for Unix-like systems."""
    print("🔧 Setting up Unix PATH...")

    # Determine shell profile file
    shell = os.environ.get("SHELL", "")
    home = Path.home()

    if "zsh" in shell:
        profile_file = home / ".zshrc"
    elif "bash" in shell:
        profile_file = home / ".bashrc"
    else:
        profile_file = home / ".profile"

    # Check if our path is already in profile
    if profile_file.exists():
        with open(profile_file, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = ""

    path_line = f'export PATH="{bin_path}:$PATH"'
    if path_line not in content:
        # Add to profile
        with open(profile_file, "a", encoding="utf-8") as f:
            f.write(f"\n# Works On My Machine\nexport PATH=\"{bin_path}:$PATH\"\n")

        print(f"✅ Added to {profile_file}")
        print("🔄 Restart your terminal or run 'source ~/.bashrc' to apply changes")
    else:
        print("✅ PATH already configured")


def create_bin_directory():
    """Create the bin directory and wrapper scripts."""
    bin_path = get_target_womm_path() / "bin"
    bin_path.mkdir(exist_ok=True)

    print(f"📁 Bin directory created: {bin_path}")

    # Create main wrapper scripts
    create_wrapper_scripts(bin_path)


def create_wrapper_scripts(bin_path):
    """Create wrapper scripts in /bin.

    Args:
        bin_path: Path to the bin directory where scripts will be created.
    """

    # Main new-project script (uses existing project_detector)
    new_project_py = bin_path / "new-project.py"
    new_project_content = """#!/usr/bin/env python3
import sys
from pathlib import Path
womm_path = Path(__file__).parent.parent
sys.path.insert(0, str(womm_path))

from shared.project_detector import main
if __name__ == "__main__":
    main()
"""
    new_project_py.write_text(new_project_content, encoding="utf-8")

    # Specific scripts (existing modules only)
    scripts = [
        ("new-python-project.py", "languages.python.scripts.setup_project", "main"),
        ("new-js-project.py", "languages.javascript.scripts.setup_project", "main"),
        ("vscode-config.py", "shared.vscode_config", "main"),
        ("template-helpers.py", "shared.template_helpers", "main"),
        ("spellcheck.py", "shared.cspell_manager", "main"),
        ("dev-tools-install.py", "shared.prerequisite_installer", "main"),
        ("setup-dev-env.py", "shared.environment_manager", "main"),
        ("context-menu.py", "shared.system.register_wom_tools", "main"),
        ("registrator.py", "shared.system.registrator", "main"),
    ]

    for script_name, module_path, func_name in scripts:
        script_file = bin_path / script_name
        script_content = f"""#!/usr/bin/env python3
import sys
from pathlib import Path
womm_path = Path(__file__).parent.parent
sys.path.insert(0, str(womm_path))

try:
    from {module_path} import {func_name}
    if __name__ == "__main__":
        {func_name}()
except ImportError as e:
    print(f"❌ Module not found: {{e}}")
    print(f"📁 Check that module {module_path} exists")
    sys.exit(1)
"""
        script_file.write_text(script_content, encoding="utf-8")

    # Create a simple lint-project script that detects project type
    lint_project_py = bin_path / "lint-project.py"
    lint_project_content = """#!/usr/bin/env python3
import sys
from pathlib import Path
womm_path = Path(__file__).parent.parent
sys.path.insert(0, str(womm_path))

from shared.project_detector import detect_project_type
from languages.python.scripts.lint import main as python_lint
from languages.javascript.scripts.lint import main as js_lint

def main():
    project_type = detect_project_type(Path.cwd())
    
    if project_type == "python":
        python_lint()
    elif project_type == "javascript":
        js_lint()
    else:
        print("❌ No supported project type detected")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    lint_project_py.write_text(lint_project_content, encoding="utf-8")

    # Make scripts executable on Unix
    if platform.system() != "Windows":
        for script_file in bin_path.glob("*.py"):
            script_file.chmod(0o755)

    # Create batch files for Windows
    if platform.system() == "Windows":
        for script_file in bin_path.glob("*.py"):
            batch_file = script_file.with_suffix(".bat")
            batch_content = f"""@echo off
python "{script_file}" %*
"""
            batch_file.write_text(batch_content, encoding="utf-8")

    print("✅ Wrapper scripts created")


def check_and_install_prerequisites() -> bool:
    """Check and install prerequisites if needed."""
    try:
        from shared.prerequisite_installer import PrerequisiteInstaller

        installer = PrerequisiteInstaller()
        should_install, missing, custom_path = installer.prompt_installation()

        if should_install and missing:
            return installer.install_missing_prerequisites(missing, custom_path)
        elif not missing:
            print("✅ All prerequisites are already installed!")
            return True
        else:
            print("⏭️  Installation cancelled by user")
            return False

    except ImportError:
        print("⚠️  Prerequisites installer not available")
        return True

    except Exception as e:
        print(f"⚠️  Error checking prerequisites: {e}")
        return True


def main():
    """Run the initialization process.

    Checks location, installs prerequisites, and sets up the environment.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Initialize Works On My Machine")
    parser.add_argument("--force", "-f", action="store_true", help="Force initialization even if .womm directory exists")
    parser.add_argument("--no-prerequisites", action="store_true", help="Skip prerequisites installation")
    parser.add_argument("--no-context-menu", action="store_true", help="Skip Windows context menu integration")
    parser.add_argument("--target", type=str, help="Custom target directory (default: ~/.womm)")
    
    args = parser.parse_args()

    print("🔧 Smart Init - Works On My Machine")
    print("=" * 50)

    # Use custom target if specified
    if args.target:
        global get_target_womm_path
        custom_target = Path(args.target).expanduser().resolve()

        def get_target_womm_path():
            return custom_target

    current_path = get_current_womm_path()
    target_path = get_target_womm_path()

    print(f"📍 Current location: {current_path}")
    print(f"🎯 Target location: {target_path}")

    # Check if target directory already exists
    if target_path.exists() and not args.force:
        print(f"⚠️  Directory {target_path} already exists")
        response = input("Do you want to continue and overwrite it? (y/N): ").lower()
        if response not in ["y", "yes", "o", "oui"]:
            print("⏭️  Initialization cancelled")
            return

    if is_in_correct_location():
        print("✅ Already in the correct location!")

        # Prerequisites check
        if not args.no_prerequisites and not check_and_install_prerequisites():
            print("❌ Prerequisites installation cancelled or failed")
            print("💡 You can restart the installation with: womm system install")
            return

        # Normal configuration
        create_bin_directory()
        setup_path()

        print("\n🎉 Initialization complete!")
        print("📋 Commands available after terminal restart:")
        print("  - womm")
        print("  - womm init")
        print("  - womm new python")
        print("  - womm new javascript")
        print("  - womm lint")
        print("  - womm spell")
        print("  - womm system")

        # Offer to add to Windows context menu
        if platform.system() == "Windows" and not args.no_context_menu:
            print("\n🔧 Windows System Integration")
            response = input(
                "Do you want to add Works On My Machine to the context menu? (y/N): "
            ).lower()
            if response in ["o", "oui", "y", "yes"]:
                try:
                    register_script = (
                        target_path / "shared" / "system" / "register_wom_tools.py"
                    )
                    if register_script.exists():
                        print("📝 Adding to Windows context menu...")
                        result = run_command(
                            [
                                sys.executable,
                                str(register_script),
                                "--register",
                                "--no-backup",
                            ],
                            "Registering context menu",
                        )

                        if result.success:
                            print("✅ Works On My Machine added to context menu!")
                            print("💡 Right-click on a folder to see WOMM options")
                        else:
                            print("⚠️  Error adding to context menu")
                            print("💡 You can do it manually later with:")
                            print("   womm context register")
                    else:
                        print("⚠️  Registry script not found")
                except Exception as e:
                    print(f"⚠️  Error adding to context menu: {e}")
            else:
                print("💡 You can add WOMM to the context menu later with:")
                print("   womm context register")

        # OS-specific instructions
        bin_path = target_path / "bin"
        if platform.system() == "Windows":
            print("\n💡 To use immediately (without restart):")
            print(f"    set PATH={bin_path};%PATH%")
            print("    womm --help")
        else:
            print("\n💡 To use immediately (without restart):")
            print(f'    export PATH="{bin_path}:$PATH"')
            print("    womm --help")

    else:
        print("⚠️  Not in the correct location, relocation needed...")

        # Copy and relaunch
        new_target = copy_womm_to_user_directory()
        launch_relocated_init(new_target)

        print("✅ Relocation process started")
        print("⏳ Wait for the new window to complete initialization...")


if __name__ == "__main__":
    main()
