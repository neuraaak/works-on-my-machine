#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Main CLI Entry Point.
Universal development tools for Python and JavaScript projects.
Enhanced with comprehensive security validation.
"""

import sys
from pathlib import Path

import click

from shared.core.cli_manager import run_command

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent / "shared"))

# Import security modules
try:
    from shared.security.secure_cli_manager import run_secure_command
    from shared.security.security_validator import (
        security_validator,
        validate_user_input,
    )

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

    # Fallback functions if security modules are not available
    def validate_user_input(_value, _input_type):
        """Fallback validation function when security modules are not available."""
        return True, ""

    def run_secure_command(cmd, description):
        """Fallback secure command execution when security modules are not available."""
        return run_command(cmd, description)


@click.group()
@click.version_option(version="1.0.0")
def womm():
    """🛠️ Works On My Machine - Universal development tools.

    Automatic installation, cross-platform configuration, global commands
    for Python and JavaScript projects.

    🔒 Enhanced with comprehensive security validation.
    """


@womm.command("install")
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force installation even if .womm directory exists",
)
@click.option(
    "--no-prerequisites", is_flag=True, help="Skip prerequisites installation"
)
@click.option(
    "--no-context-menu", is_flag=True, help="Skip Windows context menu integration"
)
@click.option(
    "--target", type=click.Path(), help="Custom target directory (default: ~/.womm)"
)
def install(force, no_prerequisites, no_context_menu, target):
    """Install Works On My Machine in user directory."""
    # Security validation for target path
    if target and SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            click.echo(f"❌ Invalid target path: {error}", err=True)
            sys.exit(1)

    script_path = Path(__file__).parent / "shared" / "installation" / "installer.py"

    cmd = [sys.executable, str(script_path)]

    if force:
        cmd.append("--force")
    if no_prerequisites:
        cmd.append("--no-prerequisites")
    if no_context_menu:
        cmd.append("--no-context-menu")
    if target:
        cmd.extend(["--target", target])

    # Use secure command execution if available
    if SECURITY_AVAILABLE:
        result = run_secure_command(cmd, "Installing Works On My Machine")
    else:
        result = run_command(cmd, "Installing Works On My Machine")

    sys.exit(0 if result.success else 1)


@womm.command("uninstall")
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

    script_path = Path(__file__).parent / "shared" / "installation" / "uninstaller.py"

    cmd = [sys.executable, str(script_path)]

    if force:
        cmd.append("--force")
    if target:
        cmd.extend(["--target", target])

    # Use secure command execution if available
    if SECURITY_AVAILABLE:
        result = run_secure_command(cmd, "Uninstalling Works On My Machine")
    else:
        result = run_command(cmd, "Uninstalling Works On My Machine")

    sys.exit(0 if result.success else 1)


@womm.group()
def new():
    """🆕 Create new projects."""


@new.command("python")
@click.argument("project_name", required=False)
@click.option(
    "--current-dir",
    is_flag=True,
    help="Configure current directory instead of creating new one",
)
def new_python(project_name, current_dir):
    """Create a new Python project with full development environment."""
    # Security validation for project name
    if project_name and SECURITY_AVAILABLE:
        is_valid, error = validate_user_input(project_name, "project_name")
        if not is_valid:
            click.echo(f"❌ Invalid project name: {error}", err=True)
            sys.exit(1)

    script_path = (
        Path(__file__).parent / "languages" / "python" / "scripts" / "setup_project.py"
    )

    # Security validation for script execution
    if SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_script_execution(script_path)
        if not is_valid:
            click.echo(f"❌ Script validation failed: {error}", err=True)
            sys.exit(1)

    cmd = [sys.executable, str(script_path)]
    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)

    # Use secure command execution if available
    if SECURITY_AVAILABLE:
        result = run_secure_command(cmd, "Setting up Python project")
    else:
        result = run_command(cmd, "Setting up Python project")

    sys.exit(0 if result.success else 1)


@new.command("javascript")
@click.argument("project_name", required=False)
@click.option(
    "--current-dir",
    is_flag=True,
    help="Configure current directory instead of creating new one",
)
@click.option(
    "--type",
    "project_type",
    type=click.Choice(["node", "react", "vue", "express"]),
    default="node",
    help="JavaScript project type",
)
def new_javascript(project_name, current_dir, project_type):
    """Create a new JavaScript/Node.js project with development tools."""
    # Security validation for project name
    if project_name and SECURITY_AVAILABLE:
        is_valid, error = validate_user_input(project_name, "project_name")
        if not is_valid:
            click.echo(f"❌ Invalid project name: {error}", err=True)
            sys.exit(1)

    script_path = (
        Path(__file__).parent
        / "languages"
        / "javascript"
        / "scripts"
        / "setup_project.py"
    )

    # Security validation for script execution
    if SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_script_execution(script_path)
        if not is_valid:
            click.echo(f"❌ Script validation failed: {error}", err=True)
            sys.exit(1)

    cmd = [sys.executable, str(script_path)]
    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)

    cmd.extend(["--type", project_type])

    # Use secure command execution if available
    if SECURITY_AVAILABLE:
        result = run_secure_command(cmd, f"Setting up {project_type} project")
    else:
        result = run_command(cmd, f"Setting up {project_type} project")

    sys.exit(0 if result.success else 1)


@new.command("detect")
@click.argument("project_name", required=False)
@click.option("--current-dir", is_flag=True, help="Configure current directory")
def new_detect(project_name, current_dir):
    """Auto-detect project type and create appropriate setup."""
    script_path = Path(__file__).parent / "shared" / "project" / "project_detector.py"

    cmd = [sys.executable, str(script_path)]
    if current_dir:
        cmd.append("--current-dir")
    elif project_name:
        cmd.append(project_name)

    result = run_command(cmd, "Auto-detecting and setting up project")
    sys.exit(0 if result.success else 1)


@womm.group()
def lint():
    """🎨 Code quality and linting tools."""


@lint.command("python")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Automatically fix code issues")
def lint_python(path, fix):
    """Lint Python code with flake8, black, and isort."""
    script_path = Path(__file__).parent / "languages" / "python" / "scripts" / "lint.py"

    cmd = [sys.executable, str(script_path), path]
    if fix:
        cmd.append("--fix")

    result = run_command(cmd, f"Linting Python code in {path}")
    sys.exit(0 if result.success else 1)


@lint.command("all")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Automatically fix code issues")
def lint_all(path, fix):
    """Lint all supported code in project."""
    script_path = Path(__file__).parent / "lint.py"

    cmd = [sys.executable, str(script_path), path]
    if fix:
        cmd.append("--fix")

    result = run_command(cmd, f"Linting all code in {path}")
    sys.exit(0 if result.success else 1)


@womm.group()
def spell():
    """📝 Spell checking with CSpell."""


@spell.command("install")
def spell_install():
    """Install CSpell and dictionaries globally."""
    script_path = Path(__file__).parent / "shared" / "tools" / "cspell_manager.py"

    cmd = [sys.executable, str(script_path), "--install"]
    result = run_command(cmd, "Installing CSpell globally")
    sys.exit(0 if result.success else 1)


@spell.command("setup")
@click.argument("project_name")
@click.option(
    "--type",
    "project_type",
    type=click.Choice(["python", "javascript"]),
    help="Force project type",
)
def spell_setup(project_name, project_type):
    """Set CSpell for current project."""
    script_path = Path(__file__).parent / "shared" / "tools" / "cspell_manager.py"

    cmd = [sys.executable, str(script_path), "--setup-project", project_name]
    if project_type:
        cmd.extend(["--type", project_type])

    result = run_command(cmd, f"Setting up CSpell for {project_name}")
    sys.exit(0 if result.success else 1)


@spell.command("status")
def spell_status():
    """Display CSpell project status."""
    script_path = Path(__file__).parent / "shared" / "tools" / "cspell_manager.py"

    cmd = [sys.executable, str(script_path), "--status"]
    result = run_command(cmd, "Displaying CSpell status")
    sys.exit(0 if result.success else 1)


@spell.command("add")
@click.argument("words", nargs=-1, required=False)
@click.option(
    "--file", "file_path", type=click.Path(exists=True), help="Add words from file"
)
@click.option("--interactive", is_flag=True, help="Interactive mode")
def spell_add(words, file_path, interactive):
    """Add words to CSpell configuration."""
    script_path = Path(__file__).parent / "shared" / "tools" / "cspell_manager.py"

    if interactive:
        cmd = [sys.executable, str(script_path), "--add-interactive"]
    elif file_path:
        cmd = [sys.executable, str(script_path), "--add-file", file_path]
    elif words:
        cmd = [sys.executable, str(script_path), "--add"] + list(words)
    else:
        click.echo("Error: Specify words, --file, or --interactive", err=True)
        sys.exit(1)

    result = run_command(cmd, "Adding words to CSpell configuration")
    sys.exit(0 if result.success else 1)


@spell.command("add-all")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def spell_add_all(force):
    """Add all dictionaries from .cspell-dict/ to CSpell configuration."""
    from shared.tools.dictionary_manager import add_all_dictionaries

    # Override input function to skip confirmation if --force
    if force:
        import builtins

        original_input = builtins.input
        builtins.input = lambda _prompt: "y"

    try:
        success = add_all_dictionaries()
        sys.exit(0 if success else 1)
    finally:
        if force:
            builtins.input = original_input


@spell.command("list-dicts")
def spell_list_dicts():
    """List available dictionaries in .cspell-dict/."""
    from shared.tools.dictionary_manager import get_dictionary_info

    info = get_dictionary_info()

    if not info["directory_exists"]:
        click.echo("❌ .cspell-dict directory not found")
        click.echo("💡 Create the directory and add dictionary files (.txt)")
        sys.exit(1)

    if info["total_files"] == 0:
        click.echo("📁 .cspell-dict directory is empty")
        click.echo("💡 Add .txt files with one word per line")
        sys.exit(0)

    click.echo(f"📚 Found {info['total_files']} dictionary files:")
    for file_path in info["files"]:
        file_name = Path(file_path).name
        click.echo(f"   - {file_name}")

    click.echo(f"\n📊 Total words available: {info['total_words']}")


@spell.command("check")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Interactive fix mode")
def spell_check(path, fix):
    """Check spelling in files."""
    script_path = Path(__file__).parent / "shared" / "tools" / "cspell_manager.py"

    if fix:
        cmd = [sys.executable, str(script_path), "--fix", path]
    else:
        cmd = [sys.executable, str(script_path), "--check", path]

    result = run_command(cmd, f"Spell checking {path}")
    sys.exit(0 if result.success else 1)


@womm.group()
def system():
    """🔧 System detection and prerequisites."""


@system.command("detect")
@click.option("--export", type=click.Path(), help="Export report to file")
def system_detect(export):
    """Detect system information and available tools."""
    script_path = Path(__file__).parent / "shared" / "core" / "system_detector.py"

    cmd = [sys.executable, str(script_path)]
    if export:
        cmd.extend(["--export", export])

    result = run_command(cmd, "Detecting system information")
    sys.exit(0 if result.success else 1)


@system.command("install")
@click.option("--check", is_flag=True, help="Only check prerequisites")
@click.option("--interactive", is_flag=True, help="Interactive installation mode")
@click.argument(
    "tools", nargs=-1, type=click.Choice(["python", "node", "git", "npm", "all"])
)
def system_install(check, interactive, tools):
    """Install system prerequisites."""
    script_path = (
        Path(__file__).parent / "shared" / "installation" / "prerequisite_installer.py"
    )

    cmd = [sys.executable, str(script_path)]
    if check:
        cmd.append("--check")
    if interactive:
        cmd.append("--interactive")
    if tools:
        cmd.extend(["--install"] + list(tools))

    result = run_command(cmd, "Managing system prerequisites")
    sys.exit(0 if result.success else 1)


@womm.group()
def deploy():
    """📦 Deployment and distribution tools."""


@deploy.command("tools")
@click.option(
    "--target",
    type=click.Path(),
    default="~/.womm",
    help="Target directory for deployment",
)
@click.option("--global", "create_global", is_flag=True, help="Create global commands")
def deploy_tools(target, create_global):
    """Deploy development tools to global directory."""
    script_path = (
        Path(__file__).parent / "shared" / "installation" / "deploy-devtools.py"
    )

    cmd = [sys.executable, str(script_path), "--target", target]
    if create_global:
        cmd.append("--install-global")

    result = run_command(cmd, f"Deploying tools to {target}")
    sys.exit(0 if result.success else 1)


@womm.group()
def context():
    """🖱️ Windows context menu management."""


@context.command("register")
@click.option("--backup", is_flag=True, help="Create backup before registration")
def context_register(backup):
    """Register WOMM tools in Windows context menu."""
    script_path = Path(__file__).parent / "shared" / "system" / "register_wom_tools.py"

    cmd = [sys.executable, str(script_path), "--register"]
    if backup:
        cmd.append("--backup")

    result = run_command(cmd, "Registering context menu tools")
    sys.exit(0 if result.success else 1)


@context.command("unregister")
def context_unregister():
    """Unregister WOMM tools from Windows context menu."""
    script_path = Path(__file__).parent / "shared" / "system" / "register_wom_tools.py"

    cmd = [sys.executable, str(script_path), "--unregister"]
    result = run_command(cmd, "Unregistering context menu tools")
    sys.exit(0 if result.success else 1)


@context.command("list")
def context_list():
    """List registered context menu entries."""
    script_path = Path(__file__).parent / "shared" / "system" / "registrator.py"

    cmd = [sys.executable, str(script_path), "--list"]
    result = run_command(cmd, "Listing context menu entries")
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    womm()
