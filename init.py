#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize the dev-tools environment.

Detects if we are in the correct location (%USER%/.dev-tools) and if not,
copies and relaunches from the correct location.
"""
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


def get_target_devtools_path():
    """Get the standard target path for dev-tools.

    Returns:
        Path object pointing to the .dev-tools directory in user's home.
    """
    return Path.home() / ".dev-tools"


def get_current_devtools_path():
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
    current = get_current_devtools_path()
    target = get_target_devtools_path()

    try:
        # Resolve symbolic links and compare
        return current.resolve() == target.resolve()
    except Exception:
        return False


def copy_devtools_to_user_directory():
    """Copy dev-tools to %USER%/.dev-tools.

    Returns:
        Path object pointing to the new location of dev-tools.
    """
    source = get_current_devtools_path()
    target = get_target_devtools_path()

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
        target_path: Path object pointing to the new location of dev-tools.
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
                    f"cd {target_path} && python3 init.py && read -p 'Appuyez sur Entrée...'",
                ]
            )
        elif shutil.which("xterm"):
            subprocess.Popen(
                [
                    "xterm",
                    "-e",
                    f"cd {target_path} && python3 init.py && read -p 'Appuyez sur Entrée...'",
                ]
            )
        else:
            # Fallback: launch in current terminal
            subprocess.run([sys.executable, str(new_init)])
            return

    print("✅ New process launched")
    print("⚠️  Closing this terminal...")


def setup_path():
    """Configure PATH with the correct location.

    Adds the bin directory to the system PATH environment variable.
    """
    devtools_path = get_target_devtools_path()
    bin_path = devtools_path / "bin"

    print(f"🔧 Configuring PATH for: {bin_path}")

    if platform.system() == "Windows":
        setup_windows_path(str(bin_path))
    else:
        setup_unix_path(str(bin_path))


def setup_windows_path(bin_path):
    """Configure Windows PATH.

    Args:
        bin_path: Path to add to Windows PATH environment variable.
    """
    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS
        ) as key:
            try:
                current_path, _ = winreg.QueryValueEx(key, "PATH")
            except FileNotFoundError:
                current_path = ""

            # Normaliser les chemins pour la comparaison
            current_paths = [p.strip() for p in current_path.split(";") if p.strip()]
            bin_path_normalized = str(Path(bin_path).resolve())

            # Vérifier si déjà présent (chemins normalisés)
            path_exists = any(
                str(Path(p).resolve()) == bin_path_normalized
                for p in current_paths
                if Path(p).exists()
            )

            if not path_exists:
                # Add to beginning of PATH for priority
                new_path = f"{bin_path};{current_path}" if current_path else bin_path
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                print(f"✅ Added to Windows PATH: {bin_path}")
                print("⚠️  Restart your terminal for changes to take effect")

                # Notify system of the change
                try:
                    import win32con
                    import win32gui

                    win32gui.SendMessage(
                        win32con.HWND_BROADCAST,
                        win32con.WM_SETTINGCHANGE,
                        0,
                        "Environment",
                    )
                except ImportError:
                    pass  # win32gui not available, not critical
            else:
                print("✅ Already in Windows PATH")

    except ImportError:
        print("❌ Module winreg not available")
    except Exception as e:
        print(f"❌ Windows PATH error: {e}")


def setup_unix_path(bin_path):
    """Configure Unix/Linux/Mac PATH.

    Args:
        bin_path: Path to add to Unix PATH environment variable.
    """
    shell = os.environ.get("SHELL", "/bin/bash")

    # Determine possible configuration files
    possible_rc_files = []

    if "zsh" in shell:
        possible_rc_files = [".zshrc", ".zprofile"]
    elif "bash" in shell:
        possible_rc_files = [".bashrc", ".bash_profile", ".profile"]
    else:
        # Generic shell
        possible_rc_files = [".profile", ".bashrc"]

    export_line = f'export PATH="{bin_path}:$PATH"'
    comment_line = "# Dev Tools PATH"

    # Search in all existing files
    for rc_filename in possible_rc_files:
        rc_file = Path.home() / rc_filename
        if rc_file.exists():
            content = rc_file.read_text(encoding="utf-8", errors="ignore")
            if bin_path in content or comment_line in content:
                print(f"✅ Already in Unix PATH ({rc_file})")
                return

    # Choose main file to add
    primary_rc = Path.home() / possible_rc_files[0]

    # Create file if it doesn't exist
    if not primary_rc.exists():
        primary_rc.touch()
        print(f"📁 Creating {primary_rc}")

    # Add to configuration file
    with primary_rc.open("a", encoding="utf-8") as f:
        f.write(f"\n{comment_line}\n{export_line}\n")

    print(f"✅ Added to {primary_rc}")
    print(f"💡 Run: source {primary_rc}")

    # Suggestion for other shells
    if len(possible_rc_files) > 1:
        other_files = ", ".join(f"~/{f}" for f in possible_rc_files[1:])
        print(f"💡 Other possible files: {other_files}")


def create_bin_directory():
    """Create bin directory and wrapper scripts if needed.

    Creates the bin directory and populates it with wrapper scripts for all tools.
    """
    devtools_path = get_target_devtools_path()
    bin_path = devtools_path / "bin"

    if not bin_path.exists():
        bin_path.mkdir(parents=True)
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
devtools_path = Path(__file__).parent.parent
sys.path.insert(0, str(devtools_path))

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
devtools_path = Path(__file__).parent.parent
sys.path.insert(0, str(devtools_path))

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
    lint_content = """#!/usr/bin/env python3
import sys
from pathlib import Path
import subprocess

def detect_project_type():
    current_dir = Path.cwd()

    # Python detection
    if any((current_dir / f).exists() for f in ["setup.py", "pyproject.toml", "requirements.txt"]):
        return "python"

    # JavaScript detection
    if any((current_dir / f).exists() for f in ["package.json", "node_modules"]):
        return "javascript"

    return None

def main():
    project_type = detect_project_type()

    if project_type == "python":
        print("🐍 Python project detected - Starting linting...")
        try:
            subprocess.run(["flake8", "."], check=False)
            subprocess.run(["black", "--check", "."], check=False)
            subprocess.run(["isort", "--check-only", "."], check=False)
            # Spell checking
            subprocess.run(["cspell", "."], check=False)
        except FileNotFoundError as e:
            print(f"❌ Tool not found: {e}")

    elif project_type == "javascript":
        print("🟨 JavaScript project detected - Starting linting...")
        try:
            run_silent(["npm", "run", "lint"])
            # Spell checking
            run_silent(["cspell", "."])
        except FileNotFoundError:
            print("❌ npm not found or lint script not configured")

    else:
        print("❓ Project type not detected")
        print("💡 Navigate to a folder containing a Python or JavaScript project")

if __name__ == "__main__":
    main()
"""
    lint_project_py.write_text(lint_content, encoding="utf-8")

    # Permissions Unix
    if platform.system() != "Windows":
        import stat

        for script_file in bin_path.glob("*.py"):
            script_file.chmod(
                stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
            )

    # Wrapper Windows
    if platform.system() == "Windows":
        all_scripts = (
            [("new-project.py", "", "")] + scripts + [("lint-project.py", "", "")]
        )
        for script_name, _, _ in all_scripts:
            bat_name = script_name.replace(".py", ".bat")
            bat_file = bin_path / bat_name
            bat_content = f'@echo off\npython "%~dp0{script_name}" %*\n'
            bat_file.write_text(bat_content, encoding="utf-8")

    print("✅ Wrapper scripts created with appropriate permissions")


def check_and_install_prerequisites() -> bool:
    """Check and offer to install prerequisites.

    Returns:
        bool: True if prerequisites are installed or skipped, False if installation failed.
    """
    try:
        # Import the prerequisites manager
        devtools_path = get_target_devtools_path()
        sys.path.insert(0, str(devtools_path))

        from shared.prerequisite_installer import PrerequisiteInstaller

        installer = PrerequisiteInstaller()
        should_install, missing, custom_path = installer.prompt_installation()

        if missing and should_install:
            return installer.install_missing_prerequisites(missing, custom_path)
        elif missing and not should_install:
            print(
                "⚠️  Some prerequisites are missing - dev-tools may not work correctly"
            )
            return True  # Continue anyway
        else:
            return True  # All installed

    except ImportError:
        print("⚠️  Module prerequisite_installer not found - check skipped")
        return True
    except Exception as e:
        print(f"⚠️  Error checking prerequisites: {e}")
        return True


def main():
    """Run the initialization process.

    Checks location, installs prerequisites, and sets up the environment.
    """
    print("🔧 Smart Init - Dev Tools")
    print("=" * 50)

    current_path = get_current_devtools_path()
    target_path = get_target_devtools_path()

    print(f"📍 Current location: {current_path}")
    print(f"🎯 Target location: {target_path}")

    if is_in_correct_location():
        print("✅ Already in the correct location!")

        # Prerequisites check
        if not check_and_install_prerequisites():
            print("❌ Prerequisites installation cancelled or failed")
            print("💡 You can restart the installation with: dev-tools-install")
            return

        # Normal configuration
        create_bin_directory()
        setup_path()

        print("\n🎉 Initialization complete!")
        print("📋 Commands available after terminal restart:")
        print("  - new-project")
        print("  - new-python-project")
        print("  - new-js-project")
        print("  - lint-project")
        print("  - vscode-config")
        print("  - template-helpers")
        print("  - spellcheck")
        print("  - dev-tools-install")
        print("  - setup-dev-env")

        # Offer to add to Windows context menu
        if platform.system() == "Windows":
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
                            capture_output=True,
                            text=True,
                        )

                        if result.returncode == 0:
                            print("✅ Works On My Machine added to context menu!")
                            print("💡 Right-click on a folder to see WOM options")
                        else:
                            print("⚠️  Error adding to context menu")
                            print("💡 You can do it manually later with:")
                            print(f"   python {register_script} --register")
                    else:
                        print("⚠️  Registry script not found")
                except Exception as e:
                    print(f"⚠️  Error adding to context menu: {e}")
            else:
                print("💡 You can add WOM to the context menu later with:")
                register_script = (
                    target_path / "shared" / "system" / "register_wom_tools.py"
                )
                print(f"   python {register_script} --register")

        # OS-specific instructions
        bin_path = target_path / "bin"
        if platform.system() == "Windows":
            print("\n💡 To use immediately (without restart):")
            print(f"    set PATH={bin_path};%PATH%")
            print("    new-project.bat --help")
        else:
            print("\n💡 To use immediately (without restart):")
            print(f'    export PATH="{bin_path}:$PATH"')
            print("    new-project.py --help")

    else:
        print("⚠️  Not in the correct location, relocation needed...")

        # Copy and relaunch
        new_target = copy_devtools_to_user_directory()
        launch_relocated_init(new_target)

        print("✅ Relocation process started")
        print("⏳ Wait for the new window to complete initialization...")


if __name__ == "__main__":
    main()
